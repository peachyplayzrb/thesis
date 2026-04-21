"""Diagnostics helpers for BL-006 scoring outputs."""

from __future__ import annotations

import statistics

NUMERIC_COMPONENTS = ["danceability", "energy", "valence", "tempo", "duration_ms", "popularity", "key", "mode"]
SEMANTIC_COMPONENTS = ["lead_genre", "genre_overlap", "tag_overlap"]
SCORING_COMPONENTS = NUMERIC_COMPONENTS + SEMANTIC_COMPONENTS


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
    """Compute average component contributions across rows."""
    if not rows:
        return {
            "numeric_contribution_mean": 0.0,
            "semantic_contribution_mean": 0.0,
            **{f"{component}_mean": 0.0 for component in SCORING_COMPONENTS},
        }

    def mean_of(key: str) -> float:
        return round(statistics.mean(_to_float(row.get(key, 0.0)) for row in rows), 6)

    component_means = {
        f"{component}_mean": mean_of(f"{component}_contribution")
        for component in SCORING_COMPONENTS
    }

    numeric_mean = round(sum(component_means[f"{component}_mean"] for component in NUMERIC_COMPONENTS), 6)
    semantic_mean = round(sum(component_means[f"{component}_mean"] for component in SEMANTIC_COMPONENTS), 6)

    return {
        "numeric_contribution_mean": numeric_mean,
        "semantic_contribution_mean": semantic_mean,
        **component_means,
    }


def _contribution_map(row: dict[str, object]) -> dict[str, float]:
    return {
        component: _to_float(row.get(f"{component}_contribution", 0.0))
        for component in SCORING_COMPONENTS
    }


def _adjusted_score(row: dict[str, object], factors: dict[str, float]) -> float:
    contributions = _contribution_map(row)
    return sum(contributions[component] * factors.get(component, 1.0) for component in SCORING_COMPONENTS)


def _ranked_rows_by_adjusted_score(
    scored_rows: list[dict[str, object]],
    factors: dict[str, float],
) -> list[dict[str, object]]:
    ranked = [
        {
            "track_id": str(row.get("track_id", "")),
            "adjusted_score": round(_adjusted_score(row, factors), 6),
        }
        for row in scored_rows
    ]
    ranked.sort(key=lambda item: (-_to_float(item["adjusted_score"]), str(item["track_id"])))
    return ranked


def _top_k_records(ranked_rows: list[dict[str, object]], top_k: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index, row in enumerate(ranked_rows[:top_k], start=1):
        records.append(
            {
                "rank": index,
                "track_id": str(row["track_id"]),
                "score": round(_to_float(row["adjusted_score"]), 6),
            }
        )
    return records


def _dominance_concentration(
    scored_rows: list[dict[str, object]],
    track_ids: set[str],
    factors: dict[str, float],
) -> dict[str, object]:
    rows = [row for row in scored_rows if str(row.get("track_id", "")) in track_ids]
    if not rows:
        return {
            "herfindahl_index": 0.0,
            "top_component_share": 0.0,
            "top_3_component_share": 0.0,
            "dominant_component": None,
            "component_shares": {},
        }

    adjusted_component_totals: dict[str, float] = {component: 0.0 for component in SCORING_COMPONENTS}
    for row in rows:
        contributions = _contribution_map(row)
        for component in SCORING_COMPONENTS:
            adjusted_component_totals[component] += (
                contributions[component] * factors.get(component, 1.0)
            )

    total = sum(adjusted_component_totals.values())
    if total <= 0:
        return {
            "herfindahl_index": 0.0,
            "top_component_share": 0.0,
            "top_3_component_share": 0.0,
            "dominant_component": None,
            "component_shares": {},
        }

    component_shares = {
        component: round(value / total, 6)
        for component, value in adjusted_component_totals.items()
    }
    sorted_shares = sorted(component_shares.items(), key=lambda item: item[1], reverse=True)
    herfindahl = round(sum(share * share for share in component_shares.values()), 6)
    top_component_share = sorted_shares[0][1] if sorted_shares else 0.0
    top_3_component_share = round(sum(share for _, share in sorted_shares[:3]), 6)

    return {
        "herfindahl_index": herfindahl,
        "top_component_share": round(top_component_share, 6),
        "top_3_component_share": top_3_component_share,
        "dominant_component": sorted_shares[0][0] if sorted_shares else None,
        "component_shares": component_shares,
    }


def build_scoring_sensitivity_diagnostics(
    scored_rows: list[dict[str, object]],
    *,
    active_component_weights: dict[str, float],
    enabled: bool,
    top_k: int,
    perturbation_pct: float,
    max_components: int,
) -> dict[str, object]:
    """Build additive rank-sensitivity diagnostics from weighted-contribution perturbations."""
    resolved_top_k = max(1, int(top_k))
    resolved_perturbation = max(0.0, min(0.5, float(perturbation_pct)))
    resolved_max_components = max(1, int(max_components))

    if not enabled:
        return {
            "active": False,
            "reason": "disabled_by_control",
            "top_k": resolved_top_k,
            "perturbation_percent": round(resolved_perturbation, 6),
            "max_components": resolved_max_components,
        }

    if not scored_rows:
        return {
            "active": False,
            "reason": "no_scored_rows",
            "top_k": resolved_top_k,
            "perturbation_percent": round(resolved_perturbation, 6),
            "max_components": resolved_max_components,
        }

    baseline_factors = {component: 1.0 for component in SCORING_COMPONENTS}
    baseline_ranked = _ranked_rows_by_adjusted_score(scored_rows, baseline_factors)
    baseline_top_k = _top_k_records(baseline_ranked, resolved_top_k)
    baseline_rank_by_track: dict[str, int] = {
        str(record["track_id"]): int(_to_float(record["rank"]))
        for record in baseline_top_k
    }
    baseline_ids = list(baseline_rank_by_track.keys())

    ranked_components = sorted(
        (
            (
                component.removesuffix("_score"),
                float(weight),
            )
            for component, weight in active_component_weights.items()
            if component.removesuffix("_score") in SCORING_COMPONENTS and float(weight) > 0
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    selected_components = [name for name, _ in ranked_components[:resolved_max_components]]

    perturbations: list[dict[str, object]] = []
    component_sensitivity_rows: list[dict[str, object]] = []
    baseline_dominance = _dominance_concentration(
        scored_rows,
        set(baseline_ids),
        baseline_factors,
    )

    for component in selected_components:
        factors = dict(baseline_factors)
        factors[component] = round(max(0.0, 1.0 - resolved_perturbation), 6)
        perturbed_ranked = _ranked_rows_by_adjusted_score(scored_rows, factors)
        perturbed_top_k = _top_k_records(perturbed_ranked, resolved_top_k)
        perturbed_rank_by_track: dict[str, int] = {
            str(record["track_id"]): int(_to_float(record["rank"]))
            for record in perturbed_top_k
        }

        perturbed_ids: set[str] = set(perturbed_rank_by_track.keys())
        overlap_count = len(set(baseline_ids) & perturbed_ids)
        union_count = len(set(baseline_ids) | perturbed_ids)
        jaccard = (overlap_count / union_count) if union_count > 0 else 1.0

        rank_deltas: list[dict[str, object]] = []
        abs_shift_values: list[float] = []
        shifted_count = 0
        max_rank_shift = 0
        for track_id in baseline_ids:
            baseline_rank = baseline_rank_by_track[track_id]
            perturbed_rank = perturbed_rank_by_track.get(track_id, resolved_top_k + 1)
            rank_delta = int(perturbed_rank - baseline_rank)
            if rank_delta != 0:
                shifted_count += 1
            abs_shift = abs(rank_delta)
            max_rank_shift = max(max_rank_shift, abs_shift)
            abs_shift_values.append(float(abs_shift))
            rank_deltas.append(
                {
                    "track_id": track_id,
                    "baseline_rank": baseline_rank,
                    "perturbed_rank": perturbed_rank,
                    "rank_delta": rank_delta,
                }
            )

        mean_abs_rank_shift = (
            statistics.mean(abs_shift_values) if abs_shift_values else 0.0
        )
        dominance = _dominance_concentration(scored_rows, perturbed_ids, factors)
        perturbations.append(
            {
                "type": f"decrease_{component}",
                "component": component,
                "factor": round(factors[component], 6),
                "top_k_after": perturbed_top_k,
                "rank_shifts_count": shifted_count,
                "top_k_overlap_count": overlap_count,
                "top_k_jaccard_similarity": round(jaccard, 6),
                "mean_absolute_rank_shift": round(mean_abs_rank_shift, 6),
                "max_rank_shift": int(max_rank_shift),
                "rank_deltas": rank_deltas,
                "dominance_concentration": dominance,
            }
        )
        component_sensitivity_rows.append(
            {
                "component": component,
                "weight_in_baseline": round(
                    float(active_component_weights.get(f"{component}_score", 0.0)),
                    6,
                ),
                "mean_absolute_rank_shift": round(mean_abs_rank_shift, 6),
                "max_rank_shift": int(max_rank_shift),
                "top_k_overlap_count": overlap_count,
                "top_k_jaccard_similarity": round(jaccard, 6),
            }
        )

    component_sensitivity_rows.sort(
        key=lambda item: (
            -_to_float(item["mean_absolute_rank_shift"]),
            str(item["component"]),
        )
    )

    most_sensitive = component_sensitivity_rows[0]["component"] if component_sensitivity_rows else None
    least_sensitive = component_sensitivity_rows[-1]["component"] if component_sensitivity_rows else None

    return {
        "active": True,
        "method": "contribution_rescaling_approximation",
        "method_note": (
            "Perturbations rescale weighted-contribution components directly (bounded approximation) "
            "without recomputing upstream candidate generation."
        ),
        "top_k": resolved_top_k,
        "perturbation_percent": round(resolved_perturbation, 6),
        "max_components": resolved_max_components,
        "baseline_top_k": baseline_top_k,
        "component_sensitivity_ranking": component_sensitivity_rows,
        "most_sensitive_component": most_sensitive,
        "least_sensitive_component": least_sensitive,
        "dominance_concentration_baseline": baseline_dominance,
        "perturbations": perturbations,
    }


def build_feature_availability_summary(candidate_rows: list[dict[str, str]]) -> dict[str, object]:
    """Build candidate-side feature availability/sparsity diagnostics for BL-006."""
    total_candidates = len(candidate_rows)
    numeric_presence_counts = {component: 0 for component in NUMERIC_COMPONENTS}
    lead_genre_sources = {"genres": 0, "tags": 0, "missing": 0}
    rows_with_all_numeric = 0
    rows_with_any_numeric = 0
    rows_with_any_semantic = 0

    for row in candidate_rows:
        has_all_numeric = True
        has_any_numeric = False
        for component in NUMERIC_COMPONENTS:
            raw_value = str(row.get(component, "")).strip()
            try:
                parsed = float(raw_value)
            except ValueError:
                parsed = None
            if parsed is not None:
                numeric_presence_counts[component] += 1
                has_any_numeric = True
            else:
                has_all_numeric = False

        if has_all_numeric:
            rows_with_all_numeric += 1
        if has_any_numeric:
            rows_with_any_numeric += 1

        genres = [item.strip() for item in str(row.get("genres", "")).split(",") if item.strip()]
        tags = [item.strip() for item in str(row.get("tags", "")).split(",") if item.strip()]
        if genres:
            lead_genre_sources["genres"] += 1
            rows_with_any_semantic += 1
        elif tags:
            lead_genre_sources["tags"] += 1
            rows_with_any_semantic += 1
        else:
            lead_genre_sources["missing"] += 1

    if total_candidates <= 0:
        numeric_coverage = {component: 0.0 for component in NUMERIC_COMPONENTS}
    else:
        numeric_coverage = {
            component: round(count / float(total_candidates), 6)
            for component, count in numeric_presence_counts.items()
        }

    numeric_sparsity = {
        component: round(max(0.0, 1.0 - ratio), 6)
        for component, ratio in numeric_coverage.items()
    }

    return {
        "candidate_count": total_candidates,
        "rows_with_any_numeric_feature": rows_with_any_numeric,
        "rows_with_all_numeric_features": rows_with_all_numeric,
        "rows_with_no_numeric_features": max(0, total_candidates - rows_with_any_numeric),
        "numeric_feature_presence_counts": numeric_presence_counts,
        "numeric_feature_coverage_by_feature": numeric_coverage,
        "numeric_feature_sparsity_by_feature": numeric_sparsity,
        "rows_with_any_semantic_signal": rows_with_any_semantic,
        "rows_with_no_semantic_signal": max(0, total_candidates - rows_with_any_semantic),
        "lead_genre_source_counts": lead_genre_sources,
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
    confidence_floor = max(0.0, min(1.0, float(numeric_confidence_floor)))
    component_multiplier = {
        component: round(
            max(confidence_floor, max(0.0, min(1.0, float(confidence)))) * profile_factor,
            6,
        )
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
