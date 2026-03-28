from __future__ import annotations

from typing import Any


def build_rank_shift_summary(baseline_rank_map: dict[str, int], scenario_rank_map: dict[str, int]) -> dict[str, object]:
    common_ids = sorted(set(baseline_rank_map).intersection(scenario_rank_map))
    if not common_ids:
        return {
            "common_candidate_count": 0,
            "mean_abs_rank_delta": 0.0,
            "max_rank_improvement": 0,
            "max_rank_drop": 0,
            "top_risers": [],
            "top_fallers": [],
        }

    deltas: list[dict[str, Any]] = []
    for track_id in common_ids:
        baseline_rank = baseline_rank_map[track_id]
        scenario_rank = scenario_rank_map[track_id]
        delta = baseline_rank - scenario_rank
        deltas.append(
            {
                "track_id": track_id,
                "baseline_rank": baseline_rank,
                "scenario_rank": scenario_rank,
                "rank_delta": delta,
            }
        )

    mean_abs_rank_delta = round(sum(abs(item["rank_delta"]) for item in deltas) / len(deltas), 3)
    top_risers = sorted(
        [item for item in deltas if item["rank_delta"] > 0],
        key=lambda item: (-item["rank_delta"], item["track_id"]),
    )[:5]
    top_fallers = sorted(
        [item for item in deltas if item["rank_delta"] < 0],
        key=lambda item: (item["rank_delta"], item["track_id"]),
    )[:5]

    return {
        "common_candidate_count": len(common_ids),
        "mean_abs_rank_delta": mean_abs_rank_delta,
        "max_rank_improvement": max((item["rank_delta"] for item in deltas), default=0),
        "max_rank_drop": min((item["rank_delta"] for item in deltas), default=0),
        "top_risers": top_risers,
        "top_fallers": top_fallers,
    }


def compare_to_baseline(baseline_result: dict[str, object], scenario_result: dict[str, object]) -> dict[str, object]:
    baseline_metrics = baseline_result["metrics"]
    scenario_metrics = scenario_result["metrics"]
    baseline_top10 = baseline_metrics["top10_track_ids"]
    scenario_top10 = scenario_metrics["top10_track_ids"]
    baseline_playlist = baseline_metrics["playlist_track_ids"]
    scenario_playlist = scenario_metrics["playlist_track_ids"]

    top10_overlap = sorted(set(baseline_top10).intersection(scenario_top10))
    playlist_overlap = sorted(set(baseline_playlist).intersection(scenario_playlist))
    component_delta = {
        key: round(
            float(scenario_metrics["mean_component_contributions"].get(key, 0.0))
            - float(baseline_metrics["mean_component_contributions"].get(key, 0.0)),
            6,
        )
        for key in sorted(
            set(baseline_metrics["mean_component_contributions"]).union(
                scenario_metrics["mean_component_contributions"]
            )
        )
    }
    rank_shift_summary = build_rank_shift_summary(
        baseline_metrics["rank_map"], scenario_metrics["rank_map"]
    )

    observable_shift = any(
        [
            scenario_metrics["candidate_pool_size"] != baseline_metrics["candidate_pool_size"],
            scenario_metrics["playlist_track_ids"] != baseline_metrics["playlist_track_ids"],
            scenario_metrics["top10_track_ids"] != baseline_metrics["top10_track_ids"],
            rank_shift_summary["mean_abs_rank_delta"] > 0,
            scenario_result["stable_hashes"]["profile_semantic_hash"]
            != baseline_result["stable_hashes"]["profile_semantic_hash"],
        ]
    )

    expected_direction_met = None
    scenario_id = str(scenario_result["scenario_id"])
    if scenario_id == "no_influence_tracks":
        expected_direction_met = (
            scenario_result["stable_hashes"]["profile_semantic_hash"]
            != baseline_result["stable_hashes"]["profile_semantic_hash"]
            and observable_shift
        )
    elif scenario_id == "valence_weight_up":
        override_component = str(
            scenario_result["effective_config"]["scoring"].get("weight_override_component") or ""
        )
        expected_direction_met = (
            component_delta.get(override_component, 0.0) > 0
            and rank_shift_summary["mean_abs_rank_delta"] > 0
        )
    elif scenario_id == "stricter_thresholds":
        expected_direction_met = (
            scenario_metrics["candidate_pool_size"] < baseline_metrics["candidate_pool_size"]
        )
    elif scenario_id == "looser_thresholds":
        expected_direction_met = (
            scenario_metrics["candidate_pool_size"] > baseline_metrics["candidate_pool_size"]
        )

    return {
        "observable_shift": observable_shift,
        "expected_direction_met": expected_direction_met,
        "candidate_pool_size_delta": (
            scenario_metrics["candidate_pool_size"] - baseline_metrics["candidate_pool_size"]
        ),
        "playlist_length_delta": (
            scenario_metrics["playlist_length"] - baseline_metrics["playlist_length"]
        ),
        "top10_overlap_count": len(top10_overlap),
        "top10_overlap_ratio": round(len(top10_overlap) / max(len(baseline_top10), 1), 3),
        "playlist_overlap_count": len(playlist_overlap),
        "playlist_overlap_ratio": round(len(playlist_overlap) / max(len(baseline_playlist), 1), 3),
        "top10_added_track_ids": [
            track_id for track_id in scenario_top10 if track_id not in baseline_top10
        ],
        "top10_removed_track_ids": [
            track_id for track_id in baseline_top10 if track_id not in scenario_top10
        ],
        "playlist_added_track_ids": [
            track_id for track_id in scenario_playlist if track_id not in baseline_playlist
        ],
        "playlist_removed_track_ids": [
            track_id for track_id in baseline_playlist if track_id not in scenario_playlist
        ],
        "profile_lead_genres_before": baseline_metrics["dominant_lead_genres"],
        "profile_lead_genres_after": scenario_metrics["dominant_lead_genres"],
        "component_mean_delta": component_delta,
        "rank_shift_summary": rank_shift_summary,
    }


def build_baseline_comparison(baseline_result: dict[str, object]) -> dict[str, object]:
    baseline_metrics = baseline_result["metrics"]
    top10_count = len(baseline_metrics["top10_track_ids"])
    playlist_len = int(baseline_metrics["playlist_length"])
    return {
        "observable_shift": False,
        "expected_direction_met": True,
        "candidate_pool_size_delta": 0,
        "playlist_length_delta": 0,
        "top10_overlap_count": top10_count,
        "top10_overlap_ratio": 1.0,
        "playlist_overlap_count": playlist_len,
        "playlist_overlap_ratio": 1.0,
        "top10_added_track_ids": [],
        "top10_removed_track_ids": [],
        "playlist_added_track_ids": [],
        "playlist_removed_track_ids": [],
        "profile_lead_genres_before": baseline_metrics["dominant_lead_genres"],
        "profile_lead_genres_after": baseline_metrics["dominant_lead_genres"],
        "component_mean_delta": {
            key: 0.0 for key in baseline_metrics["mean_component_contributions"]
        },
        "rank_shift_summary": build_rank_shift_summary(
            baseline_metrics["rank_map"], baseline_metrics["rank_map"]
        ),
    }


def evaluate_results_status(scenario_records: list[dict[str, object]]) -> dict[str, object]:
    non_baseline_records = [
        record for record in scenario_records if record["scenario_id"] != "baseline"
    ]
    all_repeat = all(record["repeat_consistent"] for record in scenario_records)
    all_shift = all(
        record["comparison_to_baseline"]["observable_shift"] for record in non_baseline_records
    )
    all_direction = all(
        record["comparison_to_baseline"]["expected_direction_met"]
        for record in non_baseline_records
    )
    return {
        "all_scenarios_repeat_consistent": all_repeat,
        "all_variant_shifts_observable": all_shift,
        "all_variant_directions_met": all_direction,
        "status": "pass" if all_repeat and all_shift and all_direction else "bounded-risk",
    }
