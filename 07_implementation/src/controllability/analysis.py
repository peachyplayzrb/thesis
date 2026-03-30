from __future__ import annotations

from typing import Any


def _expects_no_shift(expected_effect: str) -> bool:
    """Return True if expected_effect text signals that no observable shift is expected."""
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
    """Evaluate declarative acceptance-bound rules against comparison metrics.

    Called when a scenario carries an explicit ``acceptance_bounds`` list (from
    config-provided scenario definitions).  Each rule has the shape::

        { "metric": str, "comparator": str, "value": <scalar>, "required": bool }

    Supported comparators: less_than, greater_than, equal_to, not_equal_to,
    less_than_or_equal, greater_than_or_equal.

    Returns True if all required rules pass, False if any required rule fails.
    Rules that reference an unknown metric are skipped.
    """
    rank_shift = dict(comparison.get("rank_shift_summary") or {})
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
            scenario_result["stable_hashes"]["profile_semantic_hash"]
            != baseline_result["stable_hashes"]["profile_semantic_hash"]
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
    """Determine whether a scenario achieved its expected directional effect.

    Tries config-provided ``acceptance_bounds`` first (from effective_config),
    then falls back to control_surface-based built-in logic.

    Built-in dispatch replaces the previous scenario_id if/elif coupling,
    using ``control_surface`` as the dispatch key so new scenario IDs work
    automatically when their control_surface matches a known variant type.

    Returns:
        True  — direction confirmed.
        False — direction not met.
        None  — cannot be determined for this control_surface / configuration.
    """
    control_surface = str(scenario_result.get("control_surface", ""))
    scenario_id = str(scenario_result.get("scenario_id", "")).strip().lower()
    effective_config = dict(scenario_result.get("effective_config") or {})
    observable_shift = bool(partial_comparison["observable_shift"])
    candidate_pool_size_delta = int(partial_comparison["candidate_pool_size_delta"])
    component_delta = dict(partial_comparison.get("component_mean_delta") or {})
    rank_shift = dict(partial_comparison.get("rank_shift_summary") or {})

    # Config-driven acceptance bounds (for scenario definitions loaded from config).
    acceptance_bounds = list(effective_config.get("acceptance_bounds") or [])
    if acceptance_bounds:
        return _evaluate_acceptance_bounds(acceptance_bounds, partial_comparison, scenario_result, baseline_result)

    # Built-in control_surface dispatch.
    if control_surface == "fixed_bl010_baseline":
        return True

    if control_surface == "influence_tracks":
        profile_hash_changed = (
            scenario_result["stable_hashes"]["profile_semantic_hash"]
            != baseline_result["stable_hashes"]["profile_semantic_hash"]
        )
        return profile_hash_changed and observable_shift

    if control_surface == "alignment_fuzzy_mode" or scenario_id == "fuzzy_enabled_strict":
        return not observable_shift

    override_component = str(
        effective_config.get("scoring", {}).get("weight_override_component") or ""
    )
    if control_surface == "feature_weight" or override_component:
        return (
            component_delta.get(override_component, 0.0) > 0
            and float(rank_shift.get("mean_abs_rank_delta", 0.0)) > 0
        )

    if control_surface == "candidate_threshold":
        retrieval_config = dict(effective_config.get("retrieval") or {})
        threshold_scale = float(retrieval_config.get("threshold_scale") or 1.0)
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

    partial_comparison: dict[str, object] = {
        "observable_shift": observable_shift,
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
        "profile_lead_genres_before": baseline_metrics["dominant_lead_genres"],
        "profile_lead_genres_after": scenario_metrics["dominant_lead_genres"],
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
        if not _record_expects_no_shift(record)
    )
    all_expected_no_shift = all(
        not record["comparison_to_baseline"]["observable_shift"] for record in non_baseline_records
        if _record_expects_no_shift(record)
    )
    all_direction = all(
        record["comparison_to_baseline"]["expected_direction_met"]
        for record in non_baseline_records
    )
    return {
        "all_scenarios_repeat_consistent": all_repeat,
        "all_variant_shifts_observable": all_shift,
        "all_expected_no_shift_variants_stable": all_expected_no_shift,
        "all_variant_directions_met": all_direction,
        "status": "pass" if all_repeat and all_shift and all_expected_no_shift and all_direction else "bounded-risk",
    }
