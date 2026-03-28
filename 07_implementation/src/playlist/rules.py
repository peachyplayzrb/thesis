"""Rule engine for BL-007 playlist assembly."""

from __future__ import annotations

from collections import Counter, deque

from shared_utils.parsing import safe_float, safe_int


def last_n_genres(playlist: list[dict[str, object]], n: int) -> list[str]:
    """Return lead genres for the last n playlist entries."""
    return [str(track["lead_genre"]) for track in playlist[-n:]]


def decide_candidate(
    *,
    playlist: list[dict[str, object]],
    lead_genre: str,
    final_score: float,
    target_size: int,
    min_score_threshold: float,
    max_per_genre: int,
    max_consecutive: int,
    rule_hits: Counter,
) -> tuple[str, str]:
    """Apply BL-007 rules in fixed order and return decision plus exclusion reason."""
    if len(playlist) >= target_size:
        rule_hits["R4_length_cap"] += 1
        return "excluded", "length_cap_reached"

    if final_score < min_score_threshold:
        rule_hits["R1_score_threshold"] += 1
        return "excluded", "below_score_threshold"

    if sum(1 for track in playlist if track["lead_genre"] == lead_genre) >= max_per_genre:
        rule_hits["R2_genre_cap"] += 1
        return "excluded", "genre_cap_exceeded"

    if len(playlist) >= max_consecutive and all(
        genre == lead_genre for genre in last_n_genres(playlist, max_consecutive)
    ):
        rule_hits["R3_consecutive_run"] += 1
        return "excluded", "consecutive_genre_run"

    return "included", ""


def assemble_bucketed(
    *,
    candidates: list[dict[str, object]],
    target_size: int,
    min_score_threshold: float,
    max_per_genre: int,
    max_consecutive: int,
    rule_hits: Counter,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Assemble playlist by round-robin across genre buckets to avoid deep-rank cliffs."""
    normalized_candidates: list[dict[str, object]] = []
    for cand in candidates:
        normalized_candidates.append(
            {
                "track_id": str(cand.get("track_id", "")),
                "lead_genre": str(cand.get("lead_genre", "")),
                "final_score": round(safe_float(cand.get("final_score"), 0.0), 6),
                "score_rank": safe_int(cand.get("rank"), 0),
            }
        )

    # Keep rank ordering stable for deterministic bucket ordering and trace output.
    normalized_candidates.sort(
        key=lambda row: (safe_int(row["score_rank"], 0), str(row["track_id"]))
    )

    playlist: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []

    # Apply threshold upfront and keep explicit exclusion rows.
    eligible_by_rank: list[dict[str, object]] = []
    for cand in normalized_candidates:
        if safe_float(cand["final_score"], 0.0) < min_score_threshold:
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
                }
            )
            continue
        eligible_by_rank.append(cand)

    genre_buckets: dict[str, deque[dict[str, object]]] = {}
    for cand in eligible_by_rank:
        genre = str(cand["lead_genre"])
        genre_buckets.setdefault(genre, deque()).append(cand)

    genre_order = sorted(
        genre_buckets.keys(),
        key=lambda genre: (
            safe_int(genre_buckets[genre][0]["score_rank"], 0),
            genre,
        ),
    )

    processed_ids: set[str] = set()

    while len(playlist) < target_size and any(genre_buckets.values()):
        progressed = False
        for genre in genre_order:
            bucket = genre_buckets.get(genre)
            if not bucket:
                continue

            cand = bucket.popleft()
            processed_ids.add(str(cand["track_id"]))

            decision, exclusion_reason = decide_candidate(
                playlist=playlist,
                lead_genre=str(cand["lead_genre"]),
                final_score=safe_float(cand["final_score"], 0.0),
                target_size=target_size,
                min_score_threshold=min_score_threshold,
                max_per_genre=max_per_genre,
                max_consecutive=max_consecutive,
                rule_hits=rule_hits,
            )

            playlist_position: int | str = ""
            if decision == "included":
                progressed = True
                playlist_position = len(playlist) + 1
                playlist.append(
                    {
                        "playlist_position": playlist_position,
                        "track_id": cand["track_id"],
                        "lead_genre": cand["lead_genre"],
                        "final_score": cand["final_score"],
                        "score_rank": cand["score_rank"],
                    }
                )

            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": cand["track_id"],
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": decision,
                    "playlist_position": playlist_position,
                    "exclusion_reason": exclusion_reason,
                }
            )

            if len(playlist) >= target_size:
                break

        if not progressed:
            # No further candidates can pass active diversity constraints.
            break

    # Preserve full-trace semantics by marking unprocessed eligible candidates as length-capped
    # once target size is reached.
    if len(playlist) >= target_size:
        for cand in eligible_by_rank:
            track_id = str(cand["track_id"])
            if track_id in processed_ids:
                continue
            rule_hits["R4_length_cap"] += 1
            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": cand["track_id"],
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": "excluded",
                    "playlist_position": "",
                    "exclusion_reason": "length_cap_reached",
                }
            )

    trace_rows.sort(key=lambda row: (safe_int(row["score_rank"], 0), str(row["track_id"])))
    return playlist, trace_rows
