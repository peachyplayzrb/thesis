"""BL-004 profile stage executor for BL-011 controllability scenarios."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from controllability.reporting import csv_text, json_text
from controllability.weights import candidate_weight_pairs, sorted_weight_map
from shared_utils.io_utils import canonical_json_hash, format_utc_iso, sha256_of_text
from shared_utils.parsing import parse_float


def _selected_events(
    events: list[dict[str, object]],
    include_interaction_types: set[str],
    scenario_id: str,
) -> list[dict[str, object]]:
    selected = [event for event in events if str(event["interaction_type"]) in include_interaction_types]
    if not selected:
        raise RuntimeError(f"Scenario {scenario_id} selected no events for BL-004")
    return selected


def _resolve_user_id(selected_events: list[dict[str, object]], scenario_id: str) -> str:
    user_ids = {str(event["user_id"]) for event in selected_events}
    if len(user_ids) != 1:
        raise RuntimeError(f"Scenario {scenario_id} expected one user_id, got {sorted(user_ids)}")
    return next(iter(user_ids))


def _accumulate_numeric_values(
    *,
    numeric_columns: list[str],
    candidate: dict[str, str],
    effective_weight: float,
    numeric_sums: dict[str, float],
    numeric_weights: dict[str, float],
) -> None:
    for column in numeric_columns:
        value = parse_float(candidate.get(column, ""))
        if value is None:
            continue
        numeric_sums[column] += value * effective_weight
        numeric_weights[column] += effective_weight


def _accumulate_semantic_weights(
    *,
    candidate: dict[str, str],
    effective_weight: float,
    lead_genre: str,
    tag_weights: dict[str, float],
    genre_weights: dict[str, float],
    lead_genre_weights: dict[str, float],
) -> None:
    for tag, score in candidate_weight_pairs(candidate, "tags"):
        tag_weights[tag] = tag_weights.get(tag, 0.0) + (effective_weight * score)

    for genre, score in candidate_weight_pairs(candidate, "genres"):
        genre_weights[genre] = genre_weights.get(genre, 0.0) + (effective_weight * score)

    if lead_genre:
        lead_genre_weights[lead_genre] = lead_genre_weights.get(lead_genre, 0.0) + effective_weight


def _build_seed_trace_row(
    *,
    event: dict[str, object],
    track_id: str,
    interaction_type: str,
    preference_weight: float,
    effective_weight: float,
    lead_genre: str,
    candidate: dict[str, str],
) -> dict[str, object]:
    return {
        "event_id": str(event["event_id"]),
        "track_id": track_id,
        "interaction_type": interaction_type,
        "signal_source": str(event["signal_source"]),
        "seed_rank": int(cast(Any, event["seed_rank"])),
        "interaction_count": int(cast(Any, event["interaction_count"])),
        "preference_weight": round(preference_weight, 6),
        "effective_weight": round(effective_weight, 6),
        "lead_genre": lead_genre,
        "top_tag": str(event.get("top_tag", "")),
        "candidate_playcount_sum": int(float(candidate.get("playcount_sum") or "0")),
        "candidate_listener_rows": int(float(candidate.get("listener_rows") or "0")),
    }


def _compute_numeric_profile(
    numeric_columns: list[str],
    numeric_sums: dict[str, float],
    numeric_weights: dict[str, float],
) -> dict[str, float]:
    numeric_profile: dict[str, float] = {}
    for column in numeric_columns:
        if numeric_weights[column] > 0:
            numeric_profile[column] = round(numeric_sums[column] / numeric_weights[column], 6)
    return numeric_profile


def _build_profile_payload(
    *,
    run_id: str,
    run_timestamp: datetime,
    user_id: str,
    scenario_id: str,
    input_artifacts: dict[str, str],
    profile_config: dict[str, Any],
    selected_events: list[dict[str, object]],
    seed_trace_rows: list[dict[str, object]],
    missing_track_ids: list[str],
    blank_track_id_row_count: int,
    candidate_rows_total: int,
    total_effective_weight: float,
    weight_by_type: dict[str, float],
    counts_by_type: dict[str, int],
    numeric_profile: dict[str, float],
    tag_weights: dict[str, float],
    genre_weights: dict[str, float],
    lead_genre_weights: dict[str, float],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "task": "BL-004",
        "generated_at_utc": format_utc_iso(run_timestamp),
        "user_id": user_id,
        "scenario_id": scenario_id,
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
            "missing_candidate_track_count": len(missing_track_ids),
            "missing_candidate_track_ids": missing_track_ids,
            "blank_track_id_rows": blank_track_id_row_count,
            "candidate_rows_total": candidate_rows_total,
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


def _build_summary(
    *,
    run_id: str,
    scenario_id: str,
    seed_trace_rows: list[dict[str, object]],
    total_effective_weight: float,
    semantic_profile: dict[str, Any],
    numeric_profile: dict[str, float],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "scenario_id": scenario_id,
        "matched_seed_count": len(seed_trace_rows),
        "total_effective_weight": total_effective_weight,
        "dominant_lead_genres": [item["label"] for item in cast(list[dict[str, Any]], semantic_profile["top_lead_genres"])[:5]],
        "dominant_tags": [item["label"] for item in cast(list[dict[str, Any]], semantic_profile["top_tags"])[:5]],
        "dominant_genres": [item["label"] for item in cast(list[dict[str, Any]], semantic_profile["top_genres"])[:5]],
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


def _profile_semantic_hash_payload(
    *,
    profile: dict[str, Any],
    diagnostics: dict[str, Any],
    semantic_profile: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "user_id": profile["user_id"],
        "config": profile["config"],
        "diagnostics": {
            "events_total": diagnostics["events_total"],
            "matched_seed_count": diagnostics["matched_seed_count"],
            "missing_candidate_track_count": diagnostics["missing_candidate_track_count"],
            "candidate_rows_total": diagnostics["candidate_rows_total"],
            "total_effective_weight": diagnostics["total_effective_weight"],
            "weight_by_interaction_type": diagnostics["weight_by_interaction_type"],
        },
        "seed_summary": profile["seed_summary"],
        "numeric_feature_profile": profile["numeric_feature_profile"],
        "semantic_profile": semantic_profile,
        "summary": {
            "matched_seed_count": summary["matched_seed_count"],
            "total_effective_weight": summary["total_effective_weight"],
            "dominant_lead_genres": summary["dominant_lead_genres"],
            "dominant_tags": summary["dominant_tags"],
            "dominant_genres": summary["dominant_genres"],
            "feature_centers": summary["feature_centers"],
        },
    }


def execute_profile_stage(
    events: list[dict[str, object]],
    candidate_rows_by_id: dict[str, dict[str, str]],
    scenario: dict[str, object],
    root: Path,
    input_artifacts: dict[str, str],
) -> dict[str, object]:
    scenario_id = str(scenario["scenario_id"])
    profile_config = cast(dict[str, Any], scenario["profile"])
    include_interaction_types = set(cast(list[str], profile_config["include_interaction_types"]))
    selected_events = _selected_events(events, include_interaction_types, scenario_id)

    numeric_columns = cast(list[str], profile_config["numeric_feature_columns"])
    numeric_sums = {column: 0.0 for column in numeric_columns}
    numeric_weights = {column: 0.0 for column in numeric_columns}
    tag_weights: dict[str, float] = {}
    genre_weights: dict[str, float] = {}
    lead_genre_weights: dict[str, float] = {}
    seed_trace_rows: list[dict[str, object]] = []
    missing_track_ids: list[str] = []
    blank_track_id_row_count = 0
    counts_by_type = {"history": 0, "influence": 0}
    weight_by_type = {"history": 0.0, "influence": 0.0}

    user_id = _resolve_user_id(selected_events, scenario_id)

    for event in selected_events:
        track_id = str(event["track_id"]).strip()
        if not track_id:
            blank_track_id_row_count += 1
            continue
        candidate = candidate_rows_by_id.get(track_id)
        if candidate is None:
            missing_track_ids.append(track_id)
            continue

        interaction_type = str(event["interaction_type"])
        preference_weight = float(cast(Any, event["preference_weight"]))
        effective_weight = preference_weight

        counts_by_type[interaction_type] = counts_by_type.get(interaction_type, 0) + 1
        weight_by_type[interaction_type] = weight_by_type.get(interaction_type, 0.0) + effective_weight

        lead_genre = str(event.get("lead_genre", "")).strip()
        _accumulate_numeric_values(
            numeric_columns=numeric_columns,
            candidate=candidate,
            effective_weight=effective_weight,
            numeric_sums=numeric_sums,
            numeric_weights=numeric_weights,
        )
        _accumulate_semantic_weights(
            candidate=candidate,
            effective_weight=effective_weight,
            lead_genre=lead_genre,
            tag_weights=tag_weights,
            genre_weights=genre_weights,
            lead_genre_weights=lead_genre_weights,
        )
        seed_trace_rows.append(
            _build_seed_trace_row(
                event=event,
                track_id=track_id,
                interaction_type=interaction_type,
                preference_weight=preference_weight,
                effective_weight=effective_weight,
                lead_genre=lead_genre,
                candidate=candidate,
            )
        )

    # Permit partial/zero seed coverage so BL-011 can still evaluate controllability
    # behavior under sparse upstream candidate joins, while preserving diagnostics.

    seed_trace_rows.sort(key=lambda row: int(cast(Any, row["seed_rank"])))
    numeric_profile = _compute_numeric_profile(numeric_columns, numeric_sums, numeric_weights)

    total_effective_weight = round(sum(weight_by_type.values()), 6)
    run_timestamp = datetime.now(UTC)
    run_id = f"BL011-{scenario_id.upper()}-BL004-{run_timestamp.strftime('%Y%m%d-%H%M%S-%f')}"

    profile = _build_profile_payload(
        run_id=run_id,
        run_timestamp=run_timestamp,
        user_id=user_id,
        scenario_id=scenario_id,
        input_artifacts=input_artifacts,
        profile_config=profile_config,
        selected_events=selected_events,
        seed_trace_rows=seed_trace_rows,
        missing_track_ids=missing_track_ids,
        blank_track_id_row_count=blank_track_id_row_count,
        candidate_rows_total=len(candidate_rows_by_id),
        total_effective_weight=total_effective_weight,
        weight_by_type=weight_by_type,
        counts_by_type=counts_by_type,
        numeric_profile=numeric_profile,
        tag_weights=tag_weights,
        genre_weights=genre_weights,
        lead_genre_weights=lead_genre_weights,
    )

    semantic_profile = cast(dict[str, Any], profile["semantic_profile"])
    diagnostics = cast(dict[str, Any], profile["diagnostics"])
    summary = _build_summary(
        run_id=run_id,
        scenario_id=scenario_id,
        seed_trace_rows=seed_trace_rows,
        total_effective_weight=total_effective_weight,
        semantic_profile=semantic_profile,
        numeric_profile=numeric_profile,
    )

    seed_trace_fields = [
        "event_id",
        "track_id",
        "interaction_type",
        "signal_source",
        "seed_rank",
        "interaction_count",
        "preference_weight",
        "effective_weight",
        "lead_genre",
        "top_tag",
        "candidate_playcount_sum",
        "candidate_listener_rows",
    ]
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
                _profile_semantic_hash_payload(
                    profile=profile,
                    diagnostics=diagnostics,
                    semantic_profile=semantic_profile,
                    summary=summary,
                )
            ),
            "seed_trace_hash": sha256_of_text(seed_trace_text),
        },
    }
