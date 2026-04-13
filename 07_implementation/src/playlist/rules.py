"""Rule engine for BL-007 playlist assembly."""

from __future__ import annotations

from collections import Counter, deque

from shared_utils.parsing import safe_float, safe_int


def last_n_genres(playlist: list[dict[str, object]], n: int) -> list[str]:
    """Return assembly genres for the last n playlist entries."""
    return [str(track.get("_assembly_genre") or track.get("lead_genre", "")) for track in playlist[-n:]]


def decide_candidate(
    *,
    playlist: list[dict[str, object]],
    assembly_genre: str,
    target_size: int,
    max_per_genre: int,
    max_consecutive: int,
    rule_hits: Counter,
    ignore_genre_cap: bool = False,
    ignore_consecutive: bool = False,
) -> tuple[str, str]:
    """Apply BL-007 diversity rules (R2, R3, R4) and return decision plus exclusion reason.

    R1 (score threshold) is enforced upstream in assemble_bucketed before candidates
    reach this function and is not re-checked here.
    """
    if len(playlist) >= target_size:
        rule_hits["R4_length_cap"] += 1
        return "excluded", "length_cap_reached"

    if not ignore_genre_cap:
        if sum(
            1
            for track in playlist
            if str(track.get("_assembly_genre", track.get("lead_genre", ""))) == assembly_genre
        ) >= max_per_genre:
            rule_hits["R2_genre_cap"] += 1
            return "excluded", "genre_cap_exceeded"

    if not ignore_consecutive:
        if len(playlist) >= max_consecutive and all(
            genre == assembly_genre for genre in last_n_genres(playlist, max_consecutive)
        ):
            rule_hits["R3_consecutive_run"] += 1
            return "excluded", "consecutive_genre_run"

    return "included", ""


def _derive_assembly_genre(candidate: dict[str, object], strategy: str) -> str:
    lead_genre = str(candidate.get("lead_genre", "")).strip()
    if lead_genre:
        return lead_genre
    if strategy != "semantic_component_proxy":
        return ""

    lead_score = safe_float(candidate.get("lead_genre_contribution"), 0.0)
    genre_score = safe_float(candidate.get("genre_overlap_contribution"), 0.0)
    tag_score = safe_float(candidate.get("tag_overlap_contribution"), 0.0)
    strongest = max(lead_score, genre_score, tag_score)
    if strongest <= 0:
        return "__unknown__"
    if strongest == genre_score:
        return "__semantic_genre__"
    if strongest == tag_score:
        return "__semantic_tag__"
    return "__semantic_lead__"


def _normalize_candidates(
    candidates: list[dict[str, object]],
    *,
    lead_genre_fallback_strategy: str,
) -> list[dict[str, object]]:
    normalized_candidates: list[dict[str, object]] = []
    for cand in candidates:
        semantic_strength = (
            safe_float(cand.get("lead_genre_contribution"), 0.0)
            + safe_float(cand.get("genre_overlap_contribution"), 0.0)
            + safe_float(cand.get("tag_overlap_contribution"), 0.0)
        )
        numeric_strength = (
            safe_float(cand.get("danceability_contribution"), 0.0)
            + safe_float(cand.get("energy_contribution"), 0.0)
            + safe_float(cand.get("valence_contribution"), 0.0)
            + safe_float(cand.get("tempo_contribution"), 0.0)
            + safe_float(cand.get("duration_ms_contribution"), 0.0)
            + safe_float(cand.get("popularity_contribution"), 0.0)
            + safe_float(cand.get("key_contribution"), 0.0)
            + safe_float(cand.get("mode_contribution"), 0.0)
        )
        lead_genre = str(cand.get("lead_genre", ""))
        assembly_genre = _derive_assembly_genre(cand, lead_genre_fallback_strategy)
        normalized_candidates.append(
            {
                "track_id": str(cand.get("track_id", "")),
                "lead_genre": lead_genre,
                "assembly_genre": assembly_genre,
                "final_score": round(safe_float(cand.get("final_score"), 0.0), 6),
                "score_rank": safe_int(cand.get("rank"), 0),
                "semantic_strength": round(semantic_strength, 6),
                "component_strength": round(semantic_strength + numeric_strength, 6),
            }
        )
    normalized_candidates.sort(key=lambda row: (safe_int(row["score_rank"], 0), str(row["track_id"])))
    return normalized_candidates


def _compute_effective_max_per_genre(
    candidates: list[dict[str, object]],
    base_max_per_genre: int,
    *,
    adaptive_limits: dict[str, object],
) -> int:
    if not bool(adaptive_limits.get("enabled", False)):
        return base_max_per_genre

    top_k = max(1, safe_int(adaptive_limits.get("reference_top_k"), 100))
    sample = candidates[:top_k]
    if not sample:
        return base_max_per_genre

    counts: Counter[str] = Counter(str(cand.get("assembly_genre", "")) for cand in sample)
    dominant_count = max(counts.values()) if counts else 0
    if dominant_count <= 0:
        return base_max_per_genre

    dominant_share = float(dominant_count) / float(len(sample))
    uniform_share = 1.0 / float(max(1, len(counts)))
    pressure = max(0.0, dominant_share - uniform_share)
    scale = 1.0 + pressure
    scale_min = max(0.0, safe_float(adaptive_limits.get("max_per_genre_scale_min"), 0.75))
    scale_max = max(scale_min, safe_float(adaptive_limits.get("max_per_genre_scale_max"), 1.25))
    scale = min(scale_max, max(scale_min, scale))
    return max(1, int(round(float(base_max_per_genre) * scale)))


def _apply_relaxation_round(
    *,
    current_max_per_genre: int,
    current_max_consecutive: int,
    base_max_consecutive: int,
    round_index: int,
    controlled_relaxation: dict[str, object],
) -> tuple[int, int]:
    relax_consecutive_first = bool(controlled_relaxation.get("relax_consecutive_first", True))
    increment = max(1, safe_int(controlled_relaxation.get("max_per_genre_increment"), 1))

    next_max_per_genre = current_max_per_genre
    next_max_consecutive = current_max_consecutive
    if relax_consecutive_first and round_index == 1:
        next_max_consecutive = max(current_max_consecutive, base_max_consecutive + 1)
    else:
        next_max_per_genre = current_max_per_genre + increment
    return next_max_per_genre, next_max_consecutive


def _candidate_utility(
    candidate: dict[str, object],
    *,
    playlist: list[dict[str, object]],
    utility_decay_factor: float,
    utility_weights: dict[str, float],
    use_component_contributions_for_tiebreak: bool,
    use_semantic_strength_for_tiebreak: bool,
) -> float:
    score_weight = safe_float(utility_weights.get("score_weight"), 1.0)
    novelty_weight = safe_float(utility_weights.get("novelty_weight"), 0.0)
    repetition_penalty_weight = safe_float(utility_weights.get("repetition_penalty_weight"), 0.0)

    assembly_genre = str(candidate.get("assembly_genre", ""))
    genre_count = sum(
        1
        for track in playlist
        if str(track.get("_assembly_genre", track.get("lead_genre", ""))) == assembly_genre
    )
    novelty = 1.0 / float(1 + genre_count)
    repetition_penalty = 0.0
    if playlist:
        last_genre = str(playlist[-1].get("_assembly_genre", playlist[-1].get("lead_genre", "")))
        repetition_penalty = 1.0 if last_genre == assembly_genre else 0.0

    rank_position = max(1, safe_int(candidate.get("score_rank"), 1))
    rank_decay = 1.0 / (1.0 + max(0.0, utility_decay_factor) * float(rank_position - 1))

    utility = (
        score_weight * safe_float(candidate.get("final_score"), 0.0)
        + novelty_weight * novelty
        - repetition_penalty_weight * repetition_penalty
    ) * rank_decay
    if use_component_contributions_for_tiebreak:
        utility += safe_float(candidate.get("component_strength"), 0.0) * 0.0001
    if use_semantic_strength_for_tiebreak:
        utility += safe_float(candidate.get("semantic_strength"), 0.0) * 0.0001
    return round(utility, 9)


def _select_rank_round_robin_order(
    candidates: list[dict[str, object]],
    *,
    use_component_contributions_for_tiebreak: bool,
    use_semantic_strength_for_tiebreak: bool,
) -> list[dict[str, object]]:
    genre_buckets: dict[str, deque[dict[str, object]]] = {}
    for cand in candidates:
        genre = str(cand.get("assembly_genre", ""))
        genre_buckets.setdefault(genre, deque()).append(cand)

    for bucket in genre_buckets.values():
        sorted_rows = sorted(
            list(bucket),
            key=lambda row: (
                safe_int(row["score_rank"], 0),
                -safe_float(row.get("component_strength"), 0.0)
                if use_component_contributions_for_tiebreak
                else 0.0,
                -safe_float(row.get("semantic_strength"), 0.0)
                if use_semantic_strength_for_tiebreak
                else 0.0,
                str(row["track_id"]),
            ),
        )
        bucket.clear()
        bucket.extend(sorted_rows)

    genre_order = sorted(
        genre_buckets.keys(),
        key=lambda genre: (
            safe_int(genre_buckets[genre][0]["score_rank"], 0),
            str(genre),
        ),
    )
    ordered: list[dict[str, object]] = []
    while any(genre_buckets.values()):
        for genre in genre_order:
            bucket = genre_buckets.get(genre)
            if not bucket:
                continue
            ordered.append(bucket.popleft())
    return ordered


def assemble_bucketed(
    *,
    candidates: list[dict[str, object]],
    target_size: int,
    min_score_threshold: float,
    max_per_genre: int,
    max_consecutive: int,
    rule_hits: Counter,
    utility_strategy: str = "rank_round_robin",
    utility_decay_factor: float = 0.0,
    utility_weights: dict[str, float] | None = None,
    adaptive_limits: dict[str, object] | None = None,
    controlled_relaxation: dict[str, object] | None = None,
    lead_genre_fallback_strategy: str = "none",
    use_component_contributions_for_tiebreak: bool = False,
    use_semantic_strength_for_tiebreak: bool = False,
    influence_enabled: bool = False,
    influence_track_ids: set[str] | None = None,
    influence_policy_mode: str = "competitive",
    influence_reserved_slots: int = 0,
    influence_allow_genre_cap_override: bool = False,
    influence_allow_consecutive_override: bool = False,
    influence_allow_score_threshold_override: bool = False,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Assemble playlist by round-robin across genre buckets to avoid deep-rank cliffs."""
    utility_weights = utility_weights or {}
    adaptive_limits = adaptive_limits or {}
    controlled_relaxation = controlled_relaxation or {}
    influence_track_ids = influence_track_ids or set()

    if influence_policy_mode not in {"competitive", "reserved_slots", "hybrid_override"}:
        influence_policy_mode = "competitive"

    policy_active = bool(influence_enabled) and bool(influence_track_ids)
    reserved_slot_target = 0
    if policy_active and influence_policy_mode in {"reserved_slots", "hybrid_override"}:
        reserved_slot_target = min(target_size, max(0, int(influence_reserved_slots)))

    normalized_candidates = _normalize_candidates(
        candidates,
        lead_genre_fallback_strategy=lead_genre_fallback_strategy,
    )

    playlist: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []

    # Apply threshold upfront and keep explicit exclusion rows.
    eligible_by_rank: list[dict[str, object]] = []
    for cand in normalized_candidates:
        is_influence_requested = str(cand.get("track_id", "")) in influence_track_ids
        score_override_allowed = (
            policy_active
            and influence_policy_mode in {"reserved_slots", "hybrid_override"}
            and influence_allow_score_threshold_override
            and is_influence_requested
        )
        if safe_float(cand["final_score"], 0.0) < min_score_threshold and not score_override_allowed:
            rule_hits["R1_score_threshold"] += 1
            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": cand["track_id"],
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": "excluded",
                    "playlist_position": "",
                    "exclusion_reason": "below_score_threshold",
                    "influence_requested": is_influence_requested,
                    "inclusion_path": "",
                }
            )
            continue
        eligible_by_rank.append(cand)

    remaining: list[dict[str, object]] = list(eligible_by_rank)
    finalized_ids: set[str] = set()

    effective_max_per_genre = _compute_effective_max_per_genre(
        remaining,
        max_per_genre,
        adaptive_limits=adaptive_limits,
    )
    effective_max_consecutive = max_consecutive

    relaxation_enabled = bool(controlled_relaxation.get("enabled", False))
    max_relaxation_rounds = max(1, safe_int(controlled_relaxation.get("max_relaxation_rounds"), 2))
    relaxation_round = 0

    if reserved_slot_target > 0:
        influence_ranked = [
            cand for cand in remaining if str(cand.get("track_id", "")) in influence_track_ids
        ]
        influence_ranked.sort(key=lambda row: (safe_int(row["score_rank"], 0), str(row["track_id"])))
        for cand in influence_ranked:
            if len(playlist) >= reserved_slot_target or len(playlist) >= target_size:
                break
            if cand not in remaining:
                continue

            decision, exclusion_reason = decide_candidate(
                playlist=playlist,
                assembly_genre=str(cand["assembly_genre"]),
                target_size=target_size,
                max_per_genre=effective_max_per_genre,
                max_consecutive=effective_max_consecutive,
                rule_hits=rule_hits,
                ignore_genre_cap=influence_allow_genre_cap_override,
                ignore_consecutive=influence_allow_consecutive_override,
            )
            if decision != "included":
                continue

            playlist_position = len(playlist) + 1
            playlist.append(
                {
                    "playlist_position": playlist_position,
                    "track_id": cand["track_id"],
                    "lead_genre": cand["lead_genre"],
                    "_assembly_genre": cand["assembly_genre"],
                    "final_score": cand["final_score"],
                    "score_rank": cand["score_rank"],
                }
            )
            finalized_ids.add(str(cand["track_id"]))
            remaining.remove(cand)
            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": cand["track_id"],
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": "included",
                    "playlist_position": playlist_position,
                    "exclusion_reason": "",
                    "influence_requested": True,
                    "inclusion_path": "reserved_slot",
                }
            )

    while len(playlist) < target_size and remaining:
        deferred: list[dict[str, object]] = []
        progressed = False

        if utility_strategy == "utility_greedy":
            ordered_candidates = sorted(
                remaining,
                key=lambda cand: (
                    -_candidate_utility(
                        cand,
                        playlist=playlist,
                        utility_decay_factor=utility_decay_factor,
                        utility_weights=utility_weights,
                        use_component_contributions_for_tiebreak=use_component_contributions_for_tiebreak,
                        use_semantic_strength_for_tiebreak=use_semantic_strength_for_tiebreak,
                    ),
                    safe_int(cand["score_rank"], 0),
                    str(cand["track_id"]),
                ),
            )
        else:
            ordered_candidates = _select_rank_round_robin_order(
                remaining,
                use_component_contributions_for_tiebreak=use_component_contributions_for_tiebreak,
                use_semantic_strength_for_tiebreak=use_semantic_strength_for_tiebreak,
            )

        for cand in ordered_candidates:
            if cand not in remaining:
                continue

            track_id = str(cand.get("track_id", ""))
            is_influence_requested = track_id in influence_track_ids
            can_override = (
                policy_active
                and influence_policy_mode in {"reserved_slots", "hybrid_override"}
                and is_influence_requested
            )

            ignore_genre_cap = bool(can_override and influence_allow_genre_cap_override)
            ignore_consecutive = bool(can_override and influence_allow_consecutive_override)

            decision, exclusion_reason = decide_candidate(
                playlist=playlist,
                assembly_genre=str(cand["assembly_genre"]),
                target_size=target_size,
                max_per_genre=effective_max_per_genre,
                max_consecutive=effective_max_consecutive,
                rule_hits=rule_hits,
                ignore_genre_cap=ignore_genre_cap,
                ignore_consecutive=ignore_consecutive,
            )

            inclusion_path = ""
            if decision == "included":
                inclusion_path = "competitive"
                if can_override and (ignore_genre_cap or ignore_consecutive):
                    baseline_decision, _ = decide_candidate(
                        playlist=playlist,
                        assembly_genre=str(cand["assembly_genre"]),
                        target_size=target_size,
                        max_per_genre=effective_max_per_genre,
                        max_consecutive=effective_max_consecutive,
                        rule_hits=Counter(),
                    )
                    if baseline_decision == "excluded":
                        inclusion_path = "policy_override"

            relaxable_exclusion = exclusion_reason in {"genre_cap_exceeded", "consecutive_genre_run"}
            if decision == "excluded" and relaxable_exclusion and relaxation_enabled and relaxation_round < max_relaxation_rounds:
                deferred.append(cand)
                continue

            playlist_position: int | str = ""
            if decision == "included":
                progressed = True
                playlist_position = len(playlist) + 1
                playlist.append(
                    {
                        "playlist_position": playlist_position,
                        "track_id": cand["track_id"],
                        "lead_genre": cand["lead_genre"],
                        "_assembly_genre": cand["assembly_genre"],
                        "final_score": cand["final_score"],
                        "score_rank": cand["score_rank"],
                    }
                )
                finalized_ids.add(str(cand["track_id"]))
                remaining.remove(cand)
            else:
                finalized_ids.add(str(cand["track_id"]))
                remaining.remove(cand)

            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": cand["track_id"],
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": decision,
                    "playlist_position": playlist_position,
                    "exclusion_reason": exclusion_reason,
                    "influence_requested": is_influence_requested,
                    "inclusion_path": inclusion_path,
                }
            )

            if len(playlist) >= target_size:
                break

        if not progressed:
            if deferred and relaxation_enabled and relaxation_round < max_relaxation_rounds:
                relaxation_round += 1
                effective_max_per_genre, effective_max_consecutive = _apply_relaxation_round(
                    current_max_per_genre=effective_max_per_genre,
                    current_max_consecutive=effective_max_consecutive,
                    base_max_consecutive=max_consecutive,
                    round_index=relaxation_round,
                    controlled_relaxation=controlled_relaxation,
                )
                continue

            # Finalize deferred rows when no further relaxation rounds are available.
            for cand in deferred:
                if cand not in remaining:
                    continue
                _, final_reason = decide_candidate(
                    playlist=playlist,
                    assembly_genre=str(cand["assembly_genre"]),
                    target_size=target_size,
                    max_per_genre=effective_max_per_genre,
                    max_consecutive=effective_max_consecutive,
                    rule_hits=rule_hits,
                )
                finalized_ids.add(str(cand["track_id"]))
                remaining.remove(cand)
                trace_rows.append(
                    {
                        "score_rank": cand["score_rank"],
                        "track_id": cand["track_id"],
                        "lead_genre": cand["lead_genre"],
                        "final_score": cand["final_score"],
                        "decision": "excluded",
                        "playlist_position": "",
                        "exclusion_reason": final_reason,
                        "influence_requested": str(cand.get("track_id", "")) in influence_track_ids,
                        "inclusion_path": "",
                    }
                )

            # No further candidates can pass active diversity constraints.
            break

    # Preserve full-trace semantics by marking unprocessed eligible candidates
    # once target size is reached.
    if len(playlist) >= target_size:
        for cand in remaining:
            track_id = str(cand["track_id"])
            if track_id in finalized_ids:
                continue
            finalized_ids.add(track_id)
            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": cand["track_id"],
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": "excluded",
                    "playlist_position": "",
                    "exclusion_reason": "post_fill_unprocessed",
                    "influence_requested": str(cand.get("track_id", "")) in influence_track_ids,
                    "inclusion_path": "",
                }
            )

    for track in playlist:
        track.pop("_assembly_genre", None)

    trace_rows.sort(key=lambda row: (safe_int(row["score_rank"], 0), str(row["track_id"])))
    return playlist, trace_rows
