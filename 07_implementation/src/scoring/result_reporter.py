"""
Result reporting for BL-006 scoring.

Generates summary statistics, organizes scored results, and produces
output JSON for downstream consumption.
"""

from collections.abc import Mapping
from typing import Any, cast

from shared_utils.constants import DEFAULT_ABOVE_THRESHOLD_SCORE, DEFAULT_PERFECT_SCORE_THRESHOLD
from shared_utils.parsing import safe_float, safe_int


def initialize_scoring_report() -> dict[str, object]:
    """
    Initialize an empty report structure for accumulating results.

    Returns:
        Dict with report fields ready for population
    """
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
    """
    Add a single scored candidate result to the report.

    Updates report statistics inline. Accumulates top matches.

    Args:
        report: Report dict (mutated in place)
        scored_candidate: Dict with structure:
            {
                "track_id": "...",
                "final_score": X.XX,
                "component_scores": {
                    "tempo_score": ...,
                    "key_score": ...,
                    ...
                }
            }
        perfect_score_threshold: Score threshold for "perfect" category (default 0.99)
        above_threshold_score: Score threshold for "above threshold" category (default 0.50)
    """
    final_score = safe_float(scored_candidate.get("final_score", 0.0))

    # Update counters
    report["total_candidates_scored"] = safe_int(report.get("total_candidates_scored", 0)) + 1

    if final_score >= perfect_score_threshold:
        report["candidates_with_perfect_scores"] = safe_int(report.get("candidates_with_perfect_scores", 0)) + 1

    if final_score >= above_threshold_score:
        report["candidates_above_threshold"] = safe_int(report.get("candidates_above_threshold", 0)) + 1

    # Add to distribution
    distribution = report["score_distribution"]
    if isinstance(distribution, list):
        distribution.append(final_score)

    # Maintain top matches (keep top 10)
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
    """
    Compute summary statistics for a list of scores.

    Args:
        scores: List of numeric scores

    Returns:
        Dict with statistics:
        - "min": minimum score
        - "max": maximum score
        - "mean": average score
        - "median": middle value
    """
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
    """
    Compute final statistics and close out the report.

    Args:
        report: Report dict (mutated in place)

    Returns:
        The finalized report
    """
    # Compute score statistics from distribution
    scores = report.get("score_distribution", [])
    if isinstance(scores, list):
        score_stats = compute_score_statistics(scores)
        report["score_statistics"] = score_stats

    return report


def candidates_to_json(
    scored_candidates: list[dict[str, Any]],
) -> dict[str, object]:
    """
    Prepare scored candidates for JSON export.

    Restructures candidates into output format suitable for downstream
    stages and reporting.

    Args:
        scored_candidates: List of scored candidate dicts

    Returns:
        Dict with JSON-exportable structure:
        - "total": count
        - "candidates": list of dicts with track_id and final_score
    """
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
    """
    Generate a human-readable text summary of the report.

    Args:
        report: Finalized report dict
        perfect_score_threshold: Score threshold for "perfect" category (default 0.99)
        above_threshold_score: Score threshold for "above threshold" category (default 0.50)

    Returns:
        Formatted text summary
    """
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
