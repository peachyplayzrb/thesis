"""Scenario-comparison helpers for BL-011 controllability results."""
from __future__ import annotations

from typing import Any

from shared_utils.parsing import safe_float, safe_int


def _mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _int_mapping(value: object) -> dict[str, int]:
    normalized: dict[str, int] = {}
    for key, item in _mapping(value).items():
        normalized[str(key)] = safe_int(item, 0)
    return normalized


def _object_list(value: object) -> list[object]:
    if isinstance(value, list):
        return list(value)
    return []


def _dict_list(value: object) -> list[dict[str, Any]]:
    return [item for item in _object_list(value) if isinstance(item, dict)]


def _expects_no_shift(expected_effect: str) -> bool:
    """Return True when scenario text explicitly expects no observable shift."""
    lower = expected_effect.lower()
    return "no shift" in lower or "no bl-004" in lower or "not expected" in lower


def _record_expects_no_shift(record: dict[str, object]) -> bool:
    expected_effect = str(record.get("expected_effect", ""))
    if _expects_no_shift(expected_effect):
        return True
    scenario_id = str(record.get("scenario_id", "")).strip().lower()
    return scenario_id in {"fuzzy_enabled_strict"}


def _evaluate_acceptance_bounds(
    bounds: list[dict[str, Any]],
    comparison: dict[str, object],
    scenario_result: dict[str, object],
    baseline_result: dict[str, object],
) -> bool:
    """Evaluate optional acceptance-bound rules against computed comparison metrics."""
    rank_shift = _mapping(comparison.get("rank_shift_summary"))
    scenario_hashes = _mapping(scenario_result.get("stable_hashes"))
    baseline_hashes = _mapping(baseline_result.get("stable_hashes"))
    metrics: dict[str, object] = {
        "observable_shift": comparison["observable_shift"],
        "candidate_pool_size_delta": comparison["candidate_pool_size_delta"],
        "playlist_length_delta": comparison["playlist_length_delta"],
        "top10_overlap_count": comparison["top10_overlap_count"],
        "top10_overlap_ratio": comparison["top10_overlap_ratio"],
        "playlist_overlap_count": comparison["playlist_overlap_count"],
        "playlist_overlap_ratio": comparison["playlist_overlap_ratio"],
        "mean_abs_rank_delta": rank_shift.get("mean_abs_rank_delta", 0.0),
        "profile_hash_changed": (
            scenario_hashes.get("profile_semantic_hash")
            != baseline_hashes.get("profile_semantic_hash")
        ),
    }
    _comparators = {
        "less_than": lambda a, b: float(a) < float(b),
        "greater_than": lambda a, b: float(a) > float(b),
        "equal_to": lambda a, b: a == b,
        "not_equal_to": lambda a, b: a != b,
        "less_than_or_equal": lambda a, b: float(a) <= float(b),
        "greater_than_or_equal": lambda a, b: float(a) >= float(b),
    }
    for rule in bounds:
        metric_key = str(rule.get("metric", ""))
        comparator_key = str(rule.get("comparator", "equal_to"))
        value = rule.get("value")
        required = bool(rule.get("required", True))
        if metric_key not in metrics:
            continue
        op = _comparators.get(comparator_key)
        if op is None:
            continue
        if not op(metrics[metric_key], value) and required:
            return False
    return True


def _evaluate_expected_direction(
    scenario_result: dict[str, object],
    baseline_result: dict[str, object],
    partial_comparison: dict[str, object],
) -> bool | None:
    """Check whether a scenario achieved the expected directional effect.

    This prefers config acceptance bounds first, then falls back to built-in
    control-surface rules.
    """
    control_surface = str(scenario_result.get("control_surface", ""))
    scenario_id = str(scenario_result.get("scenario_id", "")).strip().lower()
    effective_config = _mapping(scenario_result.get("effective_config"))
    scenario_hashes = _mapping(scenario_result.get("stable_hashes"))
    baseline_hashes = _mapping(baseline_result.get("stable_hashes"))
    observable_shift = bool(partial_comparison["observable_shift"])
    candidate_pool_size_delta = safe_int(partial_comparison.get("candidate_pool_size_delta"), 0)
    component_delta = _mapping(partial_comparison.get("component_mean_delta"))
    rank_shift = _mapping(partial_comparison.get("rank_shift_summary"))

    # If config defines acceptance bounds, they take precedence over fallback heuristics.
    acceptance_bounds = _dict_list(effective_config.get("acceptance_bounds"))
    if acceptance_bounds:
        return _evaluate_acceptance_bounds(acceptance_bounds, partial_comparison, scenario_result, baseline_result)

    # Otherwise use built-in rules keyed by control surface.
    if control_surface == "fixed_bl010_baseline":
        return True

    if control_surface == "influence_tracks":
        profile_hash_changed = (
            scenario_hashes.get("profile_semantic_hash")
            != baseline_hashes.get("profile_semantic_hash")
        )
        return profile_hash_changed and observable_shift

    if control_surface == "alignment_fuzzy_mode" or scenario_id == "fuzzy_enabled_strict":
        return not observable_shift

    override_component = str(
        _mapping(effective_config.get("scoring")).get("weight_override_component") or ""
    )
    if control_surface == "feature_weight" or override_component:
        return (
            safe_float(component_delta.get(override_component), 0.0) > 0
            and safe_float(rank_shift.get("mean_abs_rank_delta"), 0.0) > 0
        )

    if control_surface == "candidate_threshold":
        retrieval_config = _mapping(effective_config.get("retrieval"))
        threshold_scale = safe_float(retrieval_config.get("threshold_scale"), 1.0)
        if threshold_scale < 1.0:
            return candidate_pool_size_delta < 0   # stricter → pool must shrink
        if threshold_scale > 1.0:
            return candidate_pool_size_delta > 0   # looser → pool must grow
        return None  # scale == 1.0, no direction expected

    return None  # unknown control_surface — no assertion possible



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
    baseline_metrics = _mapping(baseline_result.get("metrics"))
    scenario_metrics = _mapping(scenario_result.get("metrics"))
    baseline_top10 = _string_list(baseline_metrics.get("top10_track_ids"))
    scenario_top10 = _string_list(scenario_metrics.get("top10_track_ids"))
    baseline_playlist = _string_list(baseline_metrics.get("playlist_track_ids"))
    scenario_playlist = _string_list(scenario_metrics.get("playlist_track_ids"))
    baseline_component_contributions = _mapping(baseline_metrics.get("mean_component_contributions"))
    scenario_component_contributions = _mapping(scenario_metrics.get("mean_component_contributions"))
    baseline_rank_map = _int_mapping(baseline_metrics.get("rank_map"))
    scenario_rank_map = _int_mapping(scenario_metrics.get("rank_map"))
    scenario_hashes = _mapping(scenario_result.get("stable_hashes"))
    baseline_hashes = _mapping(baseline_result.get("stable_hashes"))

    top10_overlap = sorted(set(baseline_top10).intersection(scenario_top10))
    playlist_overlap = sorted(set(baseline_playlist).intersection(scenario_playlist))
    component_delta = {
        key: round(
            safe_float(scenario_component_contributions.get(key), 0.0)
            - safe_float(baseline_component_contributions.get(key), 0.0),
            6,
        )
        for key in sorted(
            set(baseline_component_contributions).union(
                scenario_component_contributions
            )
        )
    }
    rank_shift_summary = build_rank_shift_summary(
        baseline_rank_map, scenario_rank_map
    )

    observable_shift = any(
        [
            scenario_metrics.get("candidate_pool_size") != baseline_metrics.get("candidate_pool_size"),
            scenario_playlist != baseline_playlist,
            scenario_top10 != baseline_top10,
            safe_float(rank_shift_summary.get("mean_abs_rank_delta"), 0.0) > 0,
            scenario_hashes.get("profile_semantic_hash")
            != baseline_hashes.get("profile_semantic_hash"),
        ]
    )

    partial_comparison: dict[str, object] = {
        "observable_shift": observable_shift,
        "candidate_pool_size_delta": (
            safe_int(scenario_metrics.get("candidate_pool_size"), 0) - safe_int(baseline_metrics.get("candidate_pool_size"), 0)
        ),
        "playlist_length_delta": (
            safe_int(scenario_metrics.get("playlist_length"), 0) - safe_int(baseline_metrics.get("playlist_length"), 0)
        ),
        "top10_overlap_count": len(top10_overlap),
        "top10_overlap_ratio": round(len(top10_overlap) / max(len(baseline_top10), 1), 3),
        "playlist_overlap_count": len(playlist_overlap),
        "playlist_overlap_ratio": round(len(playlist_overlap) / max(len(baseline_playlist), 1), 3),
        "component_mean_delta": component_delta,
        "rank_shift_summary": rank_shift_summary,
    }
    expected_direction_met = _evaluate_expected_direction(scenario_result, baseline_result, partial_comparison)

    return {
        **partial_comparison,
        "expected_direction_met": expected_direction_met,
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
        "profile_lead_genres_before": _string_list(baseline_metrics.get("dominant_lead_genres")),
        "profile_lead_genres_after": _string_list(scenario_metrics.get("dominant_lead_genres")),
    }


def build_baseline_comparison(baseline_result: dict[str, object]) -> dict[str, object]:
    baseline_metrics = _mapping(baseline_result.get("metrics"))
    top10_track_ids = _string_list(baseline_metrics.get("top10_track_ids"))
    rank_map = _int_mapping(baseline_metrics.get("rank_map"))
    mean_component_contributions = _mapping(baseline_metrics.get("mean_component_contributions"))
    dominant_lead_genres = _string_list(baseline_metrics.get("dominant_lead_genres"))
    top10_count = len(top10_track_ids)
    playlist_len = safe_int(baseline_metrics.get("playlist_length"), 0)
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
        "profile_lead_genres_before": dominant_lead_genres,
        "profile_lead_genres_after": dominant_lead_genres,
        "component_mean_delta": {
            key: 0.0 for key in mean_component_contributions
        },
        "rank_shift_summary": build_rank_shift_summary(
            rank_map, rank_map
        ),
    }


def evaluate_results_status(scenario_records: list[dict[str, object]]) -> dict[str, object]:
    non_baseline_records = [
        record for record in scenario_records if record["scenario_id"] != "baseline"
    ]
    all_repeat = all(record["repeat_consistent"] for record in scenario_records)
    all_shift = all(
        _mapping(record.get("comparison_to_baseline")).get("observable_shift") for record in non_baseline_records
        if not _record_expects_no_shift(record)
    )
    all_expected_no_shift = all(
        not _mapping(record.get("comparison_to_baseline")).get("observable_shift") for record in non_baseline_records
        if _record_expects_no_shift(record)
    )
    all_direction = all(
        _mapping(record.get("comparison_to_baseline")).get("expected_direction_met")
        for record in non_baseline_records
    )
    return {
        "all_scenarios_repeat_consistent": all_repeat,
        "all_variant_shifts_observable": all_shift,
        "all_expected_no_shift_variants_stable": all_expected_no_shift,
        "all_variant_directions_met": all_direction,
        "status": "pass" if all_repeat and all_shift and all_expected_no_shift and all_direction else "bounded-risk",
    }
