"""Diagnostics helpers for BL-006 scoring outputs."""

from __future__ import annotations

import statistics


def _to_float(value: object) -> float:
    return float(str(value))


def percentile(sorted_values: list[float], p: float) -> float:
    """Compute percentile with linear interpolation."""
    if not sorted_values:
        return 0.0
    if p <= 0:
        return sorted_values[0]
    if p >= 100:
        return sorted_values[-1]
    rank = (len(sorted_values) - 1) * (p / 100.0)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    if lower == upper:
        return sorted_values[lower]
    fraction = rank - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction


def build_score_distribution_diagnostics(scored_rows: list[dict[str, object]]) -> dict[str, object]:
    """Build score spread and rank-cliff diagnostics."""
    score_desc = [_to_float(row["final_score"]) for row in scored_rows]
    score_desc.sort(reverse=True)

    gaps: list[dict[str, float | int]] = []
    for index in range(len(score_desc) - 1):
        gap = score_desc[index] - score_desc[index + 1]
        gaps.append(
            {
                "between_rank": index + 1,
                "next_rank": index + 2,
                "score_gap": round(gap, 6),
            }
        )

    max_gap = max(gaps, key=lambda item: _to_float(item["score_gap"])) if gaps else None
    rank_2_to_3_gap = round(score_desc[1] - score_desc[2], 6) if len(score_desc) >= 3 else 0.0
    is_rank_cliff = bool(max_gap and _to_float(max_gap["score_gap"]) >= 0.1)

    score_asc = list(reversed(score_desc))
    percentiles = {
        "p10": round(percentile(score_asc, 10), 6),
        "p25": round(percentile(score_asc, 25), 6),
        "p50": round(percentile(score_asc, 50), 6),
        "p75": round(percentile(score_asc, 75), 6),
        "p90": round(percentile(score_asc, 90), 6),
        "p95": round(percentile(score_asc, 95), 6),
        "p99": round(percentile(score_asc, 99), 6),
    }

    return {
        "score_percentiles": percentiles,
        "score_range": {
            "max": round(score_desc[0], 6) if score_desc else 0.0,
            "min": round(score_desc[-1], 6) if score_desc else 0.0,
        },
        "rank_cliff": {
            "detected": is_rank_cliff,
            "rank_2_to_3_gap": rank_2_to_3_gap,
            "max_gap": max_gap or {"between_rank": 0, "next_rank": 0, "score_gap": 0.0},
            "classification": "cliff" if is_rank_cliff else "smooth",
        },
    }


def contribution_breakdown(rows: list[dict[str, object]]) -> dict[str, float]:
    """Compute average contribution values across the scored rows."""
    numeric_components = ["danceability", "energy", "valence", "tempo", "duration_ms", "popularity", "key", "mode"]
    semantic_components = ["lead_genre", "genre_overlap", "tag_overlap"]
    if not rows:
        return {
            "numeric_contribution_mean": 0.0,
            "semantic_contribution_mean": 0.0,
            **{f"{component}_mean": 0.0 for component in numeric_components + semantic_components},
        }

    def mean_of(key: str) -> float:
        return round(statistics.mean(_to_float(row.get(key, 0.0)) for row in rows), 6)

    component_means = {
        f"{component}_mean": mean_of(f"{component}_contribution")
        for component in numeric_components + semantic_components
    }

    numeric_mean = round(sum(component_means[f"{component}_mean"] for component in numeric_components), 6)
    semantic_mean = round(sum(component_means[f"{component}_mean"] for component in semantic_components), 6)

    return {
        "numeric_contribution_mean": numeric_mean,
        "semantic_contribution_mean": semantic_mean,
        **component_means,
    }


def build_confidence_impact_diagnostics(
    scored_rows: list[dict[str, object]],
    numeric_confidence_by_feature: dict[str, float],
    profile_numeric_confidence_factor: float,
    *,
    enabled: bool = True,
    numeric_confidence_floor: float = 0.0,
    profile_numeric_confidence_mode: str = "direct",
    profile_numeric_confidence_blend_weight: float = 1.0,
) -> dict[str, object]:
    """Estimate pre/post confidence impact from contribution columns and static multipliers."""
    if not enabled:
        return {
            "active": False,
            "disabled": True,
            "reason": "confidence scaling disabled by scoring control",
        }

    if not scored_rows:
        return {
            "active": False,
            "profile_numeric_confidence_factor": round(profile_numeric_confidence_factor, 6),
            "feature_confidence_by_name": dict(numeric_confidence_by_feature),
            "numeric_confidence_floor": round(numeric_confidence_floor, 6),
            "profile_numeric_confidence_mode": str(profile_numeric_confidence_mode),
            "profile_numeric_confidence_blend_weight": round(profile_numeric_confidence_blend_weight, 6),
            "component_multiplier": {},
            "mean_adjusted_contribution": {},
            "mean_estimated_unadjusted_contribution": {},
            "mean_estimated_reduction": {},
            "total_numeric_adjusted_mean": 0.0,
            "total_numeric_estimated_unadjusted_mean": 0.0,
            "total_numeric_estimated_reduction": 0.0,
        }

    profile_factor = max(0.0, min(1.0, float(profile_numeric_confidence_factor)))
    component_multiplier = {
        component: round(max(0.0, min(1.0, float(confidence))) * profile_factor, 6)
        for component, confidence in numeric_confidence_by_feature.items()
    }

    def mean_of(key: str) -> float:
        values = [_to_float(row.get(key, 0.0)) for row in scored_rows]
        return round(statistics.mean(values), 6)

    adjusted_by_component: dict[str, float] = {}
    estimated_unadjusted_by_component: dict[str, float] = {}
    estimated_reduction_by_component: dict[str, float] = {}

    for component, multiplier in component_multiplier.items():
        contribution_key = f"{component}_contribution"
        adjusted_mean = mean_of(contribution_key)
        adjusted_by_component[component] = adjusted_mean
        if multiplier > 0:
            estimated_unadjusted = round(adjusted_mean / multiplier, 6)
        else:
            estimated_unadjusted = adjusted_mean
        estimated_unadjusted_by_component[component] = estimated_unadjusted
        estimated_reduction_by_component[component] = round(
            max(0.0, estimated_unadjusted - adjusted_mean),
            6,
        )

    total_adjusted = round(sum(adjusted_by_component.values()), 6)
    total_unadjusted = round(sum(estimated_unadjusted_by_component.values()), 6)

    return {
        "active": bool(component_multiplier),
        "profile_numeric_confidence_factor": round(profile_factor, 6),
        "numeric_confidence_floor": round(numeric_confidence_floor, 6),
        "profile_numeric_confidence_mode": str(profile_numeric_confidence_mode),
        "profile_numeric_confidence_blend_weight": round(profile_numeric_confidence_blend_weight, 6),
        "feature_confidence_by_name": {
            key: round(float(value), 6)
            for key, value in numeric_confidence_by_feature.items()
        },
        "component_multiplier": component_multiplier,
        "mean_adjusted_contribution": adjusted_by_component,
        "mean_estimated_unadjusted_contribution": estimated_unadjusted_by_component,
        "mean_estimated_reduction": estimated_reduction_by_component,
        "total_numeric_adjusted_mean": total_adjusted,
        "total_numeric_estimated_unadjusted_mean": total_unadjusted,
        "total_numeric_estimated_reduction": round(max(0.0, total_unadjusted - total_adjusted), 6),
    }


def build_semantic_precision_diagnostics(
    *,
    enabled: bool,
    overlap_strategy: str,
    alpha_mode: str,
    alpha_effective: float,
    alpha_fixed: float,
) -> dict[str, object]:
    """Emit additive semantic precision diagnostics for BL-006 controls."""
    return {
        "active": bool(enabled),
        "overlap_strategy": str(overlap_strategy),
        "semantic_precision_alpha_mode": str(alpha_mode),
        "semantic_precision_alpha_effective": round(float(alpha_effective), 6),
        "semantic_precision_alpha_fixed": round(float(alpha_fixed), 6),
    }
