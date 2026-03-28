"""Diagnostics helpers for BL-006 scoring outputs."""

from __future__ import annotations

import statistics


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
    score_desc = [float(row["final_score"]) for row in scored_rows]
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

    max_gap = max(gaps, key=lambda item: float(item["score_gap"])) if gaps else None
    rank_2_to_3_gap = round(score_desc[1] - score_desc[2], 6) if len(score_desc) >= 3 else 0.0
    is_rank_cliff = bool(max_gap and float(max_gap["score_gap"]) >= 0.1)

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
    numeric_components = ["danceability", "energy", "valence", "tempo", "duration_ms", "key", "mode"]
    semantic_components = ["lead_genre", "genre_overlap", "tag_overlap"]
    if not rows:
        return {
            "numeric_contribution_mean": 0.0,
            "semantic_contribution_mean": 0.0,
            **{f"{component}_mean": 0.0 for component in numeric_components + semantic_components},
        }

    def mean_of(key: str) -> float:
        return round(statistics.mean(float(row[key]) for row in rows), 6)

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
