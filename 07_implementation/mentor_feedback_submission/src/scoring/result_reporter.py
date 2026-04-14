"""BL-006 reporting helpers for score summaries, diagnostics, and export formatting."""

from typing import Any, Mapping, cast
from shared_utils.constants import DEFAULT_PERFECT_SCORE_THRESHOLD, DEFAULT_ABOVE_THRESHOLD_SCORE
from shared_utils.parsing import safe_float, safe_int


def initialize_scoring_report() -> dict[str, object]:
    """Create an empty scoring report payload ready to accumulate results."""
    return {
        "total_candidates_scored": 0,
        "candidates_with_perfect_scores": 0,
        "candidates_above_threshold": 0,
        "score_distribution": [],
        "component_score_stats": {
            "numeric_avg": 0.0,
            "semantic_avg": 0.0,
        },
        "top_matches": [],
        "scoring_diagnostics": {
            "candidates_evaluated": 0,
            "errors_encountered": 0,
        },
    }


def add_result_to_report(
    report: dict[str, object],
    scored_candidate: dict[str, Any],
    perfect_score_threshold: float = DEFAULT_PERFECT_SCORE_THRESHOLD,
    above_threshold_score: float = DEFAULT_ABOVE_THRESHOLD_SCORE,
) -> None:
    """Add one scored candidate and update report counters, distribution, and top-match list in place."""
    final_score = safe_float(scored_candidate.get("final_score", 0.0))

    report["total_candidates_scored"] = safe_int(report.get("total_candidates_scored", 0)) + 1

    if final_score >= perfect_score_threshold:
        report["candidates_with_perfect_scores"] = safe_int(report.get("candidates_with_perfect_scores", 0)) + 1

    if final_score >= above_threshold_score:
        report["candidates_above_threshold"] = safe_int(report.get("candidates_above_threshold", 0)) + 1

    distribution = report["score_distribution"]
    if isinstance(distribution, list):
        distribution.append(final_score)

    # Keep the top-match list trimmed so summaries stay lightweight.
    top_matches = report["top_matches"]
    if isinstance(top_matches, list):
        top_matches.append(scored_candidate)
        top_matches.sort(
            key=lambda candidate: safe_float(
                cast(Mapping[str, object], candidate).get("final_score", 0.0)
            ),
            reverse=True,
        )
        if len(top_matches) > 10:
            top_matches.pop()


def compute_score_statistics(scores: list[float]) -> dict[str, float]:
    """Compute min/max/mean/median for a list of scores."""
    if not scores:
        return {"min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0}

    sorted_scores = sorted(scores)
    count = len(sorted_scores)

    return {
        "min": float(sorted_scores[0]),
        "max": float(sorted_scores[-1]),
        "mean": sum(sorted_scores) / count,
        "median": sorted_scores[count // 2],
    }


def finalize_report(report: dict[str, object]) -> dict[str, object]:
    """Finalize the report by computing score statistics from the accumulated distribution."""
    scores = report.get("score_distribution", [])
    if isinstance(scores, list):
        score_stats = compute_score_statistics(scores)
        report["score_statistics"] = score_stats

    return report


def candidates_to_json(
    scored_candidates: list[dict[str, Any]],
) -> dict[str, object]:
    """Build a compact JSON-friendly view of scored candidates for downstream use."""
    return {
        "total": len(scored_candidates),
        "candidates": [
            {
                "track_id": cand.get("track_id", "unknown"),
                "final_score": cand.get("final_score", 0.0),
            }
            for cand in scored_candidates
        ],
    }


def generate_summary_report(
    report: dict[str, object],
    perfect_score_threshold: float = DEFAULT_PERFECT_SCORE_THRESHOLD,
    above_threshold_score: float = DEFAULT_ABOVE_THRESHOLD_SCORE,
) -> str:
    """Render the finalized report as a human-readable text summary."""
    total = safe_int(report.get("total_candidates_scored", 0))
    perfect = safe_int(report.get("candidates_with_perfect_scores", 0))
    above_thresh = safe_int(report.get("candidates_above_threshold", 0))
    diagnostics = cast(Mapping[str, object], report.get("scoring_diagnostics", {}))
    stats = cast(Mapping[str, object], report.get("score_statistics", {}))

    lines = [
        "=== BL-006 Scoring Report ===",
        f"Total candidates scored: {total}",
        f"Perfect scores (≥{perfect_score_threshold:.2f}): {perfect}",
        f"Above threshold (≥{above_threshold_score:.2f}): {above_thresh}",
        "",
        "Score Distribution:",
        f"  Min: {safe_float(stats.get('min', 0.0)):.3f}",
        f"  Max: {safe_float(stats.get('max', 0.0)):.3f}",
        f"  Mean: {safe_float(stats.get('mean', 0.0)):.3f}",
        f"  Median: {safe_float(stats.get('median', 0.0)):.3f}",
        "",
        "Diagnostics:",
        f"  Candidates evaluated: {safe_int(diagnostics.get('candidates_evaluated', 0))}",
        f"  Errors: {safe_int(diagnostics.get('errors_encountered', 0))}",
    ]

    return "\n".join(lines)
