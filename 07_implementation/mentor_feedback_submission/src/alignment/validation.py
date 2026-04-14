"""Validation helpers for the BL-003 outputs."""
from __future__ import annotations


def validate_match_rate(summary_counts: dict[str, int], threshold: float) -> None:
    """Fail if the matched fraction falls below the configured minimum threshold."""
    if summary_counts["input_event_rows"] > 0 and threshold > 0.0:
        matched = (
            summary_counts["matched_by_spotify_id"]
            + summary_counts["matched_by_metadata"]
            + summary_counts.get("matched_by_fuzzy", 0)
        )
        match_rate = matched / summary_counts["input_event_rows"]
        if match_rate < threshold:
            raise RuntimeError(
                f"BL-003 match-rate validation failed: {match_rate:.1%} matched "
                f"({matched} events), below minimum threshold {threshold:.1%}. "
                f"This indicates high bias in the preference profile (built from only "
                f"{match_rate:.1%} of imported history). "
                f"Either increase the match-rate threshold in seed_controls if this is expected, "
                f"or investigate DS-001 corpus coverage and import data quality."
            )
