"""BL-011 scenario pipeline orchestrator."""
from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from controllability.reporting import merge_stage_maps
from controllability.stage_playlist import execute_playlist_stage
from controllability.stage_profile import execute_profile_stage
from controllability.stage_retrieval import execute_retrieval_stage
from controllability.stage_scoring import execute_scoring_stage
from shared_utils.io_utils import canonical_json_hash


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

    profile = cast(dict[str, Any], profile_stage["profile"])
    profile_summary = cast(dict[str, Any], profile_stage["summary"])
    retrieval_diagnostics = cast(dict[str, Any], retrieval_stage["diagnostics"])
    retrieval_counts = cast(dict[str, Any], retrieval_diagnostics["counts"])
    scoring_summary = cast(dict[str, Any], scoring_stage["summary"])
    scoring_counts = cast(dict[str, Any], scoring_summary["counts"])
    playlist_obj = cast(dict[str, Any], playlist_stage["playlist"])
    playlist_report = cast(dict[str, Any], playlist_stage["report"])

    ranked_rows = cast(list[dict[str, object]], scoring_stage["scored_rows"])
    playlist_tracks = cast(list[dict[str, object]], playlist_obj["tracks"])
    rank_map = {str(row["track_id"]): int(cast(Any, row["rank"])) for row in ranked_rows}
    top10_ids = [str(row["track_id"]) for row in ranked_rows[:10]]
    playlist_ids = [str(track["track_id"]) for track in playlist_tracks]

    effective_config = {
        "scenario_id": scenario["scenario_id"],
        "test_id": scenario["test_id"],
        "control_surface": scenario["control_surface"],
        "variation_mode": scenario.get("variation_mode", "single_factor"),
        "interaction_axes": list(cast(list[str], scenario.get("interaction_axes", []))),
        "description": scenario["description"],
        "expected_effect": scenario["expected_effect"],
        "acceptance_bounds": list(cast(list[dict[str, object]], scenario.get("acceptance_bounds", []))),
        "alignment_seed_controls": dict(cast(dict[str, Any], scenario.get("alignment_seed_controls") or {})),
        "profile": profile["config"],
        "retrieval": retrieval_diagnostics["config"],
        "scoring": scoring_summary["config"],
        "assembly": playlist_obj["config"],
    }

    texts = merge_stage_maps(
        cast(dict[str, str], profile_stage["texts"]),
        cast(dict[str, str], retrieval_stage["texts"]),
        cast(dict[str, str], scoring_stage["texts"]),
        cast(dict[str, str], playlist_stage["texts"]),
    )

    stable_hashes = merge_stage_maps(
        cast(dict[str, str], profile_stage["stable_hashes"]),
        cast(dict[str, str], retrieval_stage["stable_hashes"]),
        cast(dict[str, str], scoring_stage["stable_hashes"]),
        cast(dict[str, str], playlist_stage["stable_hashes"]),
    )

    return {
        "scenario_id": scenario["scenario_id"],
        "test_id": scenario["test_id"],
        "control_surface": scenario["control_surface"],
        "variation_mode": scenario.get("variation_mode", "single_factor"),
        "interaction_axes": list(cast(list[str], scenario.get("interaction_axes", []))),
        "description": scenario["description"],
        "expected_effect": scenario["expected_effect"],
        "effective_config": effective_config,
        "config_hash": canonical_json_hash(effective_config),
        "texts": texts,
        "stable_hashes": stable_hashes,
        "metrics": {
            "selected_event_count": cast(dict[str, Any], profile["diagnostics"])["events_total"],
            "matched_seed_count": cast(dict[str, Any], profile["diagnostics"])["matched_seed_count"],
            "candidate_pool_size": retrieval_counts["kept_candidates"],
            "scored_candidate_count": scoring_counts["candidates_scored"],
            "playlist_length": playlist_obj["playlist_length"],
            "top10_track_ids": top10_ids,
            "playlist_track_ids": playlist_ids,
            "dominant_lead_genres": profile_summary["dominant_lead_genres"],
            "dominant_tags": profile_summary["dominant_tags"],
            "mean_component_contributions": scoring_summary["mean_component_contributions"],
            "playlist_genre_mix": playlist_report["playlist_genre_mix"],
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
