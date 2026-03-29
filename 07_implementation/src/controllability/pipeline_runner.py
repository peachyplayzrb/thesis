from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from shared_utils.io_utils import canonical_json_hash, format_utc_iso, sha256_of_text
from shared_utils.parsing import parse_float

from controllability.reporting import csv_text, merge_stage_maps, json_text
from controllability.weights import (
    candidate_labels,
    candidate_weight_pairs,
    normalize_component_weight_keys,
    normalize_weight_map,
    normalized_weights_with_override,
    numeric_similarity,
    sorted_weight_map,
    weighted_overlap,
)


def _decision_reason(is_seed_track: bool, semantic_score: int, numeric_pass_count: int, kept: bool) -> str:
    if is_seed_track:
        return "reject: seed track excluded from retrieval output"
    if kept:
        return f"keep: semantic_score={semantic_score}, numeric_pass_count={numeric_pass_count}"
    return (
        f"reject: semantic_score={semantic_score}, "
        f"numeric_pass_count={numeric_pass_count} below keep threshold"
    )


def execute_profile_stage(
    events: list[dict[str, object]],
    candidate_rows_by_id: dict[str, dict[str, str]],
    scenario: dict[str, object],
    root: Path,
    input_artifacts: dict[str, str],
) -> dict[str, object]:
    profile_config = scenario["profile"]
    include_interaction_types = set(profile_config["include_interaction_types"])
    selected_events = [event for event in events if str(event["interaction_type"]) in include_interaction_types]
    if not selected_events:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} selected no events for BL-004")

    numeric_columns = profile_config["numeric_feature_columns"]
    numeric_sums = {column: 0.0 for column in numeric_columns}
    numeric_weights = {column: 0.0 for column in numeric_columns}
    tag_weights: dict[str, float] = {}
    genre_weights: dict[str, float] = {}
    lead_genre_weights: dict[str, float] = {}
    seed_trace_rows: list[dict[str, object]] = []
    missing_track_ids: list[str] = []
    counts_by_type = {"history": 0, "influence": 0}
    weight_by_type = {"history": 0.0, "influence": 0.0}

    user_ids = {str(event["user_id"]) for event in selected_events}
    if len(user_ids) != 1:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} expected one user_id, got {sorted(user_ids)}")
    user_id = next(iter(user_ids))

    for event in selected_events:
        track_id = str(event["track_id"])
        candidate = candidate_rows_by_id.get(track_id)
        if candidate is None:
            missing_track_ids.append(track_id)
            continue

        interaction_type = str(event["interaction_type"])
        preference_weight = float(event["preference_weight"])
        effective_weight = preference_weight

        counts_by_type[interaction_type] = counts_by_type.get(interaction_type, 0) + 1
        weight_by_type[interaction_type] = weight_by_type.get(interaction_type, 0.0) + effective_weight

        for column in numeric_columns:
            value = parse_float(candidate.get(column, ""))
            if value is None:
                continue
            numeric_sums[column] += value * effective_weight
            numeric_weights[column] += effective_weight

        for tag, score in candidate_weight_pairs(candidate, "tags"):
            tag_weights[tag] = tag_weights.get(tag, 0.0) + (effective_weight * score)

        for genre, score in candidate_weight_pairs(candidate, "genres"):
            genre_weights[genre] = genre_weights.get(genre, 0.0) + (effective_weight * score)

        lead_genre = str(event.get("lead_genre", "")).strip()
        if lead_genre:
            lead_genre_weights[lead_genre] = lead_genre_weights.get(lead_genre, 0.0) + effective_weight

        seed_trace_rows.append(
            {
                "event_id": str(event["event_id"]),
                "track_id": track_id,
                "interaction_type": interaction_type,
                "signal_source": str(event["signal_source"]),
                "seed_rank": int(event["seed_rank"]),
                "interaction_count": int(event["interaction_count"]),
                "preference_weight": round(preference_weight, 6),
                "effective_weight": round(effective_weight, 6),
                "lead_genre": lead_genre,
                "top_tag": str(event.get("top_tag", "")),
                "candidate_playcount_sum": int(float(candidate.get("playcount_sum") or "0")),
                "candidate_listener_rows": int(float(candidate.get("listener_rows") or "0")),
            }
        )

    if missing_track_ids:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} missing candidate rows for track_ids: {missing_track_ids}")

    seed_trace_rows.sort(key=lambda row: int(row["seed_rank"]))
    numeric_profile: dict[str, float] = {}
    for column in numeric_columns:
        if numeric_weights[column] > 0:
            numeric_profile[column] = round(numeric_sums[column] / numeric_weights[column], 6)

    total_effective_weight = round(sum(weight_by_type.values()), 6)
    run_timestamp = datetime.now(timezone.utc)
    run_id = f"BL011-{scenario['scenario_id'].upper()}-BL004-{run_timestamp.strftime('%Y%m%d-%H%M%S-%f')}"

    profile = {
        "run_id": run_id,
        "task": "BL-004",
        "generated_at_utc": format_utc_iso(run_timestamp),
        "user_id": user_id,
        "scenario_id": scenario["scenario_id"],
        "input_artifacts": {
            "aligned_events_path": input_artifacts["aligned_events_path"],
            "candidate_stub_path": input_artifacts["candidate_stub_path"],
        },
        "config": {
            "effective_weight_rule": profile_config["effective_weight_rule"],
            "numeric_feature_columns": profile_config["numeric_feature_columns"],
            "top_tag_limit": profile_config["top_tag_limit"],
            "top_genre_limit": profile_config["top_genre_limit"],
            "top_lead_genre_limit": profile_config["top_lead_genre_limit"],
            "aggregation_rules": profile_config["aggregation_rules"],
            "include_interaction_types": list(profile_config["include_interaction_types"]),
        },
        "diagnostics": {
            "events_total": len(selected_events),
            "matched_seed_count": len(seed_trace_rows),
            "missing_seed_count": len(missing_track_ids),
            "missing_track_ids": missing_track_ids,
            "candidate_rows_total": len(candidate_rows_by_id),
            "total_effective_weight": total_effective_weight,
            "weight_by_interaction_type": {key: round(value, 6) for key, value in weight_by_type.items() if value > 0},
        },
        "seed_summary": {
            "counts_by_interaction_type": {key: value for key, value in counts_by_type.items() if value > 0},
            "matched_track_ids": [row["track_id"] for row in seed_trace_rows],
        },
        "numeric_feature_profile": numeric_profile,
        "semantic_profile": {
            "top_tags": sorted_weight_map(tag_weights, int(profile_config["top_tag_limit"])),
            "top_genres": sorted_weight_map(genre_weights, int(profile_config["top_genre_limit"])),
            "top_lead_genres": sorted_weight_map(lead_genre_weights, int(profile_config["top_lead_genre_limit"])),
        },
    }

    summary = {
        "run_id": run_id,
        "scenario_id": scenario["scenario_id"],
        "matched_seed_count": len(seed_trace_rows),
        "total_effective_weight": total_effective_weight,
        "dominant_lead_genres": [item["label"] for item in profile["semantic_profile"]["top_lead_genres"][:5]],
        "dominant_tags": [item["label"] for item in profile["semantic_profile"]["top_tags"][:5]],
        "dominant_genres": [item["label"] for item in profile["semantic_profile"]["top_genres"][:5]],
        "feature_centers": {
            key: numeric_profile[key]
            for key in [
                "rhythm.bpm",
                "rhythm.danceability",
                "lowlevel.loudness_ebu128.integrated",
                "V_mean",
                "A_mean",
                "D_mean",
            ]
            if key in numeric_profile
        },
    }

    seed_trace_fields = list(seed_trace_rows[0].keys())
    profile_text = json_text(profile)
    summary_text = json_text(summary)
    seed_trace_text = csv_text(seed_trace_fields, seed_trace_rows)

    return {
        "profile": profile,
        "summary": summary,
        "seed_trace_rows": seed_trace_rows,
        "texts": {
            "bl004_preference_profile.json": profile_text,
            "profile_summary.json": summary_text,
            "bl004_seed_trace.csv": seed_trace_text,
        },
        "stable_hashes": {
            "profile_semantic_hash": canonical_json_hash(
                {
                    "user_id": profile["user_id"],
                    "config": profile["config"],
                    "diagnostics": {
                        "events_total": profile["diagnostics"]["events_total"],
                        "matched_seed_count": profile["diagnostics"]["matched_seed_count"],
                        "missing_seed_count": profile["diagnostics"]["missing_seed_count"],
                        "candidate_rows_total": profile["diagnostics"]["candidate_rows_total"],
                        "total_effective_weight": profile["diagnostics"]["total_effective_weight"],
                        "weight_by_interaction_type": profile["diagnostics"]["weight_by_interaction_type"],
                    },
                    "seed_summary": profile["seed_summary"],
                    "numeric_feature_profile": profile["numeric_feature_profile"],
                    "semantic_profile": profile["semantic_profile"],
                    "summary": {
                        "matched_seed_count": summary["matched_seed_count"],
                        "total_effective_weight": summary["total_effective_weight"],
                        "dominant_lead_genres": summary["dominant_lead_genres"],
                        "dominant_tags": summary["dominant_tags"],
                        "dominant_genres": summary["dominant_genres"],
                        "feature_centers": summary["feature_centers"],
                    },
                }
            ),
            "seed_trace_hash": sha256_of_text(seed_trace_text),
        },
    }


def execute_retrieval_stage(
    profile_stage: dict[str, object],
    candidate_rows: list[dict[str, str]],
    scenario: dict[str, object],
) -> dict[str, object]:
    retrieval_config = scenario["retrieval"]
    profile = profile_stage["profile"]
    seed_trace_rows = profile_stage["seed_trace_rows"]

    seed_track_ids = {str(row["track_id"]) for row in seed_trace_rows}
    top_lead_genres = {
        item["label"]
        for item in profile["semantic_profile"]["top_lead_genres"][
            : int(retrieval_config["top_lead_genre_limit"])
        ]
    }
    top_tags = {
        item["label"]
        for item in profile["semantic_profile"]["top_tags"][: int(retrieval_config["top_tag_limit"])]
    }
    top_genres = {
        item["label"]
        for item in profile["semantic_profile"]["top_genres"][: int(retrieval_config["top_genre_limit"])]
    }

    scaled_thresholds = {
        key: round(float(value) * float(retrieval_config["threshold_scale"]), 6)
        for key, value in retrieval_config["numeric_thresholds"].items()
    }
    numeric_centers = {
        key: float(value)
        for key, value in profile["numeric_feature_profile"].items()
        if key in scaled_thresholds
    }
    keep_rule = str(retrieval_config.get("keep_rule", "")).lower()

    decisions: list[dict[str, object]] = []
    kept_rows: list[dict[str, str]] = []
    decision_counts = {"seed_excluded": 0, "semantic_and_numeric_keep": 0, "rejected_threshold": 0}
    semantic_rule_hits = {"lead_genre_match": 0, "genre_overlap": 0, "tag_overlap": 0}
    numeric_rule_hits = {key: 0 for key in scaled_thresholds}

    for row in candidate_rows:
        track_id = row["track_id"]
        is_seed_track = track_id in seed_track_ids
        candidate_genres = candidate_labels(row, "genres")
        candidate_tags = candidate_labels(row, "tags")
        lead_genre = candidate_genres[0] if candidate_genres else (candidate_tags[0] if candidate_tags else "")

        lead_genre_match = lead_genre in top_lead_genres if lead_genre else False
        genre_overlap = len(top_genres.intersection(candidate_genres))
        tag_overlap = len(top_tags.intersection(candidate_tags))

        if lead_genre_match:
            semantic_rule_hits["lead_genre_match"] += 1
        if genre_overlap > 0:
            semantic_rule_hits["genre_overlap"] += 1
        if tag_overlap > 0:
            semantic_rule_hits["tag_overlap"] += 1

        semantic_score = (1 if lead_genre_match else 0) + (1 if genre_overlap > 0 else 0) + (1 if tag_overlap > 0 else 0)

        numeric_pass_count = 0
        numeric_distances: dict[str, float | None] = {}
        for column, threshold in scaled_thresholds.items():
            value = parse_float(row.get(column, ""))
            if value is None:
                numeric_distances[column] = None
                continue
            center = numeric_centers.get(column)
            if center is None:
                numeric_distances[column] = None
                continue
            if column == "key":
                raw_diff = abs(value - center)
                distance = min(raw_diff, 12.0 - raw_diff)
            else:
                distance = abs(value - center)
            numeric_distances[column] = round(distance, 6)
            if distance <= threshold:
                numeric_pass_count += 1
                numeric_rule_hits[column] += 1

        kept = False
        if not is_seed_track:
            if "semantic_score >= 2 or" in keep_rule:
                kept = semantic_score >= 2 or (semantic_score >= 1 and numeric_pass_count >= 1)
            else:
                kept = ((semantic_score >= 2 and numeric_pass_count >= 4) or (semantic_score == 3 and numeric_pass_count >= 3))

        if is_seed_track:
            decision_counts["seed_excluded"] += 1
        elif kept:
            decision_counts["semantic_and_numeric_keep"] += 1
        else:
            decision_counts["rejected_threshold"] += 1

        decision_row = {
            "track_id": track_id,
            "is_seed_track": int(is_seed_track),
            "lead_genre": lead_genre,
            "semantic_score": semantic_score,
            "lead_genre_match": int(lead_genre_match),
            "genre_overlap_count": genre_overlap,
            "tag_overlap_count": tag_overlap,
            "numeric_pass_count": numeric_pass_count,
            "decision": "keep" if kept else "reject",
            "decision_reason": _decision_reason(is_seed_track, semantic_score, numeric_pass_count, kept),
        }
        for column in sorted(scaled_thresholds):
            decision_row[f"{column}_distance"] = numeric_distances.get(column)
        decisions.append(decision_row)
        if kept:
            kept_rows.append(row)

    diagnostics = {
        "run_id": f"BL011-{scenario['scenario_id'].upper()}-BL005-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-005",
        "scenario_id": scenario["scenario_id"],
        "config": {
            "top_lead_genre_limit": retrieval_config["top_lead_genre_limit"],
            "top_tag_limit": retrieval_config["top_tag_limit"],
            "top_genre_limit": retrieval_config["top_genre_limit"],
            "threshold_scale": retrieval_config["threshold_scale"],
            "numeric_thresholds": scaled_thresholds,
            "keep_rule": retrieval_config["keep_rule"],
        },
        "counts": {
            "candidate_rows_total": len(candidate_rows),
            "seed_tracks_excluded": decision_counts["seed_excluded"],
            "kept_candidates": len(kept_rows),
            "rejected_non_seed_candidates": decision_counts["rejected_threshold"],
        },
        "rule_hits": {
            "semantic_rule_hits": semantic_rule_hits,
            "numeric_rule_hits": numeric_rule_hits,
        },
        "top_kept_track_ids": [row["track_id"] for row in kept_rows[:15]],
    }

    filtered_fields = list(candidate_rows[0].keys())
    decisions_fields = list(decisions[0].keys())
    filtered_text = csv_text(filtered_fields, kept_rows)
    decisions_text = csv_text(decisions_fields, decisions)
    diagnostics_text = json_text(diagnostics)

    return {
        "kept_rows": kept_rows,
        "decisions": decisions,
        "diagnostics": diagnostics,
        "texts": {
            "bl005_filtered_candidates.csv": filtered_text,
            "bl005_candidate_decisions.csv": decisions_text,
            "bl005_candidate_diagnostics.json": diagnostics_text,
        },
        "stable_hashes": {
            "filtered_candidates_hash": sha256_of_text(filtered_text),
            "candidate_decisions_hash": sha256_of_text(decisions_text),
        },
    }


def execute_scoring_stage(
    profile_stage: dict[str, object], retrieval_stage: dict[str, object], scenario: dict[str, object]
) -> dict[str, object]:
    scoring_config = scenario["scoring"]
    profile = profile_stage["profile"]
    candidates = retrieval_stage["kept_rows"]
    if not candidates:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} has no BL-005 candidates for BL-006")

    raw_component_weights = (
        scoring_config.get("component_weights")
        or scoring_config.get("active_component_weights")
        or scoring_config.get("base_component_weights")
        or {}
    )
    component_weights = normalize_component_weight_keys(
        {key: float(value) for key, value in raw_component_weights.items()}
    )
    if not component_weights:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} has no scoring component weights")
    if abs(sum(component_weights.values()) - 1.0) > 1e-4:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} scoring weights must sum to 1.0")

    numeric_thresholds = {key: float(value) for key, value in scoring_config["numeric_thresholds"].items()}
    numeric_components = [key for key in numeric_thresholds if key in component_weights]
    profile_lead_map, profile_lead_total = normalize_weight_map(
        profile["semantic_profile"]["top_lead_genres"], top_k=6
    )
    profile_genre_map, profile_genre_total = normalize_weight_map(
        profile["semantic_profile"]["top_genres"], top_k=8
    )
    profile_tag_map, profile_tag_total = normalize_weight_map(
        profile["semantic_profile"]["top_tags"], top_k=10
    )

    scored_rows: list[dict[str, object]] = []
    component_totals = {component: 0.0 for component in component_weights}

    for row in candidates:
        lead_genres = candidate_labels(row, "genres")
        candidate_tags = candidate_labels(row, "tags")
        lead_genre = lead_genres[0] if lead_genres else (candidate_tags[0] if candidate_tags else "")

        component_similarity: dict[str, float] = {}
        component_contribution: dict[str, float] = {}

        for column in numeric_components:
            threshold = float(numeric_thresholds[column])
            value = parse_float(row.get(column, ""))
            center = float(profile["numeric_feature_profile"][column])
            if column == "key" and value is not None:
                raw_diff = abs(value - center)
                circular_distance = min(raw_diff, 12.0 - raw_diff)
                similarity = max(0.0, min(1.0, round(1.0 - (circular_distance / threshold), 6)))
            else:
                similarity = numeric_similarity(value, center, threshold)
            component_similarity[column] = similarity
            component_contribution[column] = round(similarity * component_weights[column], 6)

        lead_genre_similarity = 0.0
        if lead_genre and lead_genre in profile_lead_map and profile_lead_total > 0:
            lead_genre_similarity = round(profile_lead_map[lead_genre] / max(profile_lead_map.values()), 6)
        component_similarity["lead_genre"] = lead_genre_similarity
        component_contribution["lead_genre"] = round(
            lead_genre_similarity * component_weights.get("lead_genre", 0.0),
            6,
        )

        genre_overlap_similarity, matched_genres = weighted_overlap(
            lead_genres, profile_genre_map, profile_genre_total
        )
        tag_overlap_similarity, matched_tags = weighted_overlap(
            candidate_tags, profile_tag_map, profile_tag_total
        )
        component_similarity["genre_overlap"] = genre_overlap_similarity
        component_contribution["genre_overlap"] = round(
            genre_overlap_similarity * component_weights.get("genre_overlap", 0.0),
            6,
        )
        component_similarity["tag_overlap"] = tag_overlap_similarity
        component_contribution["tag_overlap"] = round(
            tag_overlap_similarity * component_weights.get("tag_overlap", 0.0),
            6,
        )

        final_score = round(sum(component_contribution.values()), 6)
        for key, value in component_contribution.items():
            if key in component_totals:
                component_totals[key] += value

        row_payload: dict[str, object] = {
            "track_id": row["track_id"],
            "lead_genre": lead_genre,
            "matched_genres": "|".join(matched_genres),
            "matched_tags": "|".join(matched_tags),
            "final_score": final_score,
        }
        ordered_components = list(numeric_components) + [
            component
            for component in ["lead_genre", "genre_overlap", "tag_overlap"]
            if component in component_weights
        ]
        for component in ordered_components:
            row_payload[f"{component}_similarity"] = component_similarity.get(component, 0.0)
            row_payload[f"{component}_contribution"] = component_contribution.get(component, 0.0)
        scored_rows.append(row_payload)

    scored_rows.sort(key=lambda item: (-float(item["final_score"]), str(item["track_id"])))
    for index, row in enumerate(scored_rows, start=1):
        row["rank"] = index

    top_candidates = [
        {
            "rank": row["rank"],
            "track_id": row["track_id"],
            "lead_genre": row["lead_genre"],
            "final_score": row["final_score"],
            "matched_genres": row["matched_genres"],
            "matched_tags": row["matched_tags"],
        }
        for row in scored_rows[:10]
    ]
    score_values = [float(row["final_score"]) for row in scored_rows]
    summary = {
        "run_id": f"BL011-{scenario['scenario_id'].upper()}-BL006-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-006",
        "scenario_id": scenario["scenario_id"],
        "config": {
            "numeric_thresholds": numeric_thresholds,
            "component_weights": component_weights,
            "weight_override_component": scoring_config["weight_override_component"],
            "raw_override_value": scoring_config["raw_override_value"],
        },
        "counts": {
            "candidates_scored": len(scored_rows),
            "score_max": round(max(score_values), 6),
            "score_min": round(min(score_values), 6),
        },
        "top_candidates": top_candidates,
        "mean_component_contributions": {
            key: round(component_totals[key] / len(scored_rows), 6) for key in component_totals
        },
    }

    scored_fields = list(scored_rows[0].keys())
    if "rank" in scored_fields:
        scored_fields.remove("rank")
        scored_fields.insert(0, "rank")
    scored_text = csv_text(scored_fields, scored_rows)
    summary_text = json_text(summary)

    return {
        "scored_rows": scored_rows,
        "summary": summary,
        "texts": {
            "bl006_scored_candidates.csv": scored_text,
            "bl006_score_summary.json": summary_text,
        },
        "stable_hashes": {
            "ranked_output_hash": sha256_of_text(scored_text),
        },
    }


def execute_playlist_stage(scoring_stage: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    assembly_config = scenario["assembly"]
    candidates = scoring_stage["scored_rows"]

    playlist: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []
    rule_hits = {"R1_score_threshold": 0, "R2_genre_cap": 0, "R3_consecutive_run": 0, "R4_length_cap": 0}

    for cand in candidates:
        track_id = str(cand["track_id"])
        lead_genre = str(cand["lead_genre"])
        final_score = float(cand["final_score"])
        score_rank = int(cand["rank"])
        decision = "included"
        exclusion_reason = ""

        if len(playlist) >= int(assembly_config["target_size"]):
            decision = "excluded"
            exclusion_reason = "length_cap_reached"
            rule_hits["R4_length_cap"] += 1
        elif final_score < float(assembly_config["min_score_threshold"]):
            decision = "excluded"
            exclusion_reason = "below_score_threshold"
            rule_hits["R1_score_threshold"] += 1
        elif sum(1 for track in playlist if track["lead_genre"] == lead_genre) >= int(
            assembly_config["max_per_genre"]
        ):
            decision = "excluded"
            exclusion_reason = "genre_cap_exceeded"
            rule_hits["R2_genre_cap"] += 1
        elif len(playlist) >= int(assembly_config["max_consecutive"]) and all(
            track["lead_genre"] == lead_genre
            for track in playlist[-int(assembly_config["max_consecutive"]):]
        ):
            decision = "excluded"
            exclusion_reason = "consecutive_genre_run"
            rule_hits["R3_consecutive_run"] += 1

        playlist_position: int | str = ""
        if decision == "included":
            playlist_position = len(playlist) + 1
            playlist.append(
                {
                    "playlist_position": playlist_position,
                    "track_id": track_id,
                    "lead_genre": lead_genre,
                    "final_score": round(final_score, 6),
                    "score_rank": score_rank,
                }
            )

        trace_rows.append(
            {
                "score_rank": score_rank,
                "track_id": track_id,
                "lead_genre": lead_genre,
                "final_score": round(final_score, 6),
                "decision": decision,
                "playlist_position": playlist_position,
                "exclusion_reason": exclusion_reason,
            }
        )

    playlist_obj = {
        "run_id": f"BL011-{scenario['scenario_id'].upper()}-BL007-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-007",
        "scenario_id": scenario["scenario_id"],
        "config": dict(assembly_config),
        "playlist_length": len(playlist),
        "tracks": playlist,
    }
    report = {
        "run_id": playlist_obj["run_id"],
        "task": "BL-007",
        "scenario_id": scenario["scenario_id"],
        "config": dict(assembly_config),
        "counts": {
            "candidates_evaluated": len(candidates),
            "tracks_included": len(playlist),
            "tracks_excluded": len(trace_rows) - len(playlist),
        },
        "rule_hits": rule_hits,
        "playlist_genre_mix": {
            genre: sum(1 for track in playlist if track["lead_genre"] == genre)
            for genre in sorted({track["lead_genre"] for track in playlist})
        },
        "playlist_score_range": {
            "max": round(max(float(track["final_score"]) for track in playlist), 6) if playlist else 0.0,
            "min": round(min(float(track["final_score"]) for track in playlist), 6) if playlist else 0.0,
        },
    }

    playlist_text = json_text(playlist_obj)
    trace_text = csv_text(
        [
            "score_rank",
            "track_id",
            "lead_genre",
            "final_score",
            "decision",
            "playlist_position",
            "exclusion_reason",
        ],
        trace_rows,
    )
    report_text = json_text(report)

    return {
        "playlist": playlist_obj,
        "trace_rows": trace_rows,
        "report": report,
        "texts": {
            "playlist.json": playlist_text,
            "bl007_assembly_trace.csv": trace_text,
            "bl007_assembly_report.json": report_text,
        },
        "stable_hashes": {
            "assembly_trace_hash": sha256_of_text(trace_text),
            "playlist_output_hash": canonical_json_hash(playlist_obj["tracks"]),
        },
    }


def execute_scenario(
    scenario: dict[str, object],
    events: list[dict[str, object]],
    candidate_rows: list[dict[str, str]],
    candidate_rows_by_id: dict[str, dict[str, str]],
    root: Path,
    input_artifacts: dict[str, str],
) -> dict[str, object]:
    profile_stage = execute_profile_stage(events, candidate_rows_by_id, scenario, root, input_artifacts)
    retrieval_stage = execute_retrieval_stage(profile_stage, candidate_rows, scenario)
    scoring_stage = execute_scoring_stage(profile_stage, retrieval_stage, scenario)
    playlist_stage = execute_playlist_stage(scoring_stage, scenario)

    ranked_rows = scoring_stage["scored_rows"]
    playlist_tracks = playlist_stage["playlist"]["tracks"]
    rank_map = {str(row["track_id"]): int(row["rank"]) for row in ranked_rows}
    top10_ids = [str(row["track_id"]) for row in ranked_rows[:10]]
    playlist_ids = [str(track["track_id"]) for track in playlist_tracks]

    effective_config = {
        "scenario_id": scenario["scenario_id"],
        "test_id": scenario["test_id"],
        "control_surface": scenario["control_surface"],
        "description": scenario["description"],
        "expected_effect": scenario["expected_effect"],
        "alignment_seed_controls": dict(scenario.get("alignment_seed_controls") or {}),
        "profile": profile_stage["profile"]["config"],
        "retrieval": retrieval_stage["diagnostics"]["config"],
        "scoring": scoring_stage["summary"]["config"],
        "assembly": playlist_stage["playlist"]["config"],
    }

    texts = merge_stage_maps(
        profile_stage["texts"],
        retrieval_stage["texts"],
        scoring_stage["texts"],
        playlist_stage["texts"],
    )

    stable_hashes = merge_stage_maps(
        profile_stage["stable_hashes"],
        retrieval_stage["stable_hashes"],
        scoring_stage["stable_hashes"],
        playlist_stage["stable_hashes"],
    )

    return {
        "scenario_id": scenario["scenario_id"],
        "test_id": scenario["test_id"],
        "control_surface": scenario["control_surface"],
        "description": scenario["description"],
        "expected_effect": scenario["expected_effect"],
        "effective_config": effective_config,
        "config_hash": canonical_json_hash(effective_config),
        "texts": texts,
        "stable_hashes": stable_hashes,
        "metrics": {
            "selected_event_count": profile_stage["profile"]["diagnostics"]["events_total"],
            "matched_seed_count": profile_stage["profile"]["diagnostics"]["matched_seed_count"],
            "candidate_pool_size": retrieval_stage["diagnostics"]["counts"]["kept_candidates"],
            "scored_candidate_count": scoring_stage["summary"]["counts"]["candidates_scored"],
            "playlist_length": playlist_stage["playlist"]["playlist_length"],
            "top10_track_ids": top10_ids,
            "playlist_track_ids": playlist_ids,
            "dominant_lead_genres": profile_stage["summary"]["dominant_lead_genres"],
            "dominant_tags": profile_stage["summary"]["dominant_tags"],
            "mean_component_contributions": scoring_stage["summary"]["mean_component_contributions"],
            "playlist_genre_mix": playlist_stage["report"]["playlist_genre_mix"],
            "rank_map": rank_map,
        },
    }


def build_active_seed_events(seed_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for idx, row in enumerate(seed_rows, start=1):
        events.append(
            {
                "event_id": str(row.get("event_id") or f"seed_event_{idx:06d}"),
                "track_id": str(row.get("track_id", "")),
                "interaction_type": str(row.get("interaction_type") or "history"),
                "signal_source": str(row.get("signal_source") or "seed_trace"),
                "seed_rank": int(float(row.get("interaction_count") or idx)),
                "interaction_count": int(float(row.get("interaction_count") or 1)),
                "preference_weight": float(row.get("preference_weight") or row.get("effective_weight") or 1.0),
                "user_id": str(row.get("user_id") or "active_user"),
                "lead_genre": str(row.get("lead_genre") or ""),
                "top_tag": str(row.get("top_tag") or ""),
            }
        )
    return events
