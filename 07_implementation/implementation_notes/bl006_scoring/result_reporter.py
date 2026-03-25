"""
Result reporting for BL-006 scoring.

Generates summary statistics, organizes scored results, and produces
output JSON for downstream consumption.
"""

from typing import Any


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
    """
    final_score = scored_candidate.get("final_score", 0.0)
    
    # Update counters
    report["total_candidates_scored"] = int(report["total_candidates_scored"]) + 1
    
    if final_score >= 0.99:
        report["candidates_with_perfect_scores"] = int(report["candidates_with_perfect_scores"]) + 1
    
    if final_score >= 0.50:
        report["candidates_above_threshold"] = int(report["candidates_above_threshold"]) + 1
    
    # Add to distribution
    distribution = report["score_distribution"]
    if isinstance(distribution, list):
        distribution.append(final_score)
    
    # Maintain top matches (keep top 10)
    top_matches = report["top_matches"]
    if isinstance(top_matches, list):
        top_matches.append(scored_candidate)
        top_matches.sort(key=lambda x: x.get("final_score", 0.0), reverse=True)
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
) -> str:
    """
    Generate a human-readable text summary of the report.
    
    Args:
        report: Finalized report dict
    
    Returns:
        Formatted text summary
    """
    total = int(report.get("total_candidates_scored", 0))
    perfect = int(report.get("candidates_with_perfect_scores", 0))
    above_thresh = int(report.get("candidates_above_threshold", 0))
    diagnostics = report.get("scoring_diagnostics", {})
    stats = report.get("score_statistics", {})
    
    lines = [
        "=== BL-006 Scoring Report ===",
        f"Total candidates scored: {total}",
        f"Perfect scores (≥0.99): {perfect}",
        f"Above threshold (≥0.50): {above_thresh}",
        "",
        "Score Distribution:",
        f"  Min: {stats.get('min', 0.0):.3f}",
        f"  Max: {stats.get('max', 0.0):.3f}",
        f"  Mean: {stats.get('mean', 0.0):.3f}",
        f"  Median: {stats.get('median', 0.0):.3f}",
        "",
        "Diagnostics:",
        f"  Candidates evaluated: {diagnostics.get('candidates_evaluated', 0)}",
        f"  Errors: {diagnostics.get('errors_encountered', 0)}",
    ]
    
    return "\n".join(lines)
