"""Explanation selection helpers for BL-008 transparency."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from shared_utils.parsing import safe_float

# Score-band thresholds for explanation framing
_STRONG_MATCH_THRESHOLD: float = 0.75
_MODERATE_MATCH_THRESHOLD: float = 0.5

_STRONG_PERCENTILE_THRESHOLD: float = 90.0
_MODERATE_PERCENTILE_THRESHOLD: float = 60.0


def classify_score_band(final_score: float, score_percentile: float | None = None) -> str:
    """Classify score into a stable score band label.

    Percentile takes precedence when provided, so labels remain meaningful even
    when absolute score ranges are tightly bounded.
    """
    if score_percentile is not None:
        if score_percentile >= _STRONG_PERCENTILE_THRESHOLD:
            return "strong"
        if score_percentile >= _MODERATE_PERCENTILE_THRESHOLD:
            return "moderate"
        return "weak"

    if final_score >= _STRONG_MATCH_THRESHOLD:
        return "strong"
    if final_score >= _MODERATE_MATCH_THRESHOLD:
        return "moderate"
    return "weak"


def build_why_selected(
    lead_genre: str,
    final_score: float,
    top_contributors: Sequence[Mapping[str, object]],
    playlist_position: int,
    top_contributor_limit: int,
    score_band: str | None = None,
) -> str:
    """Build the human-readable explanation sentence."""
    top_labels = [
        str(c.get("label", "Unknown"))
        for c in top_contributors[:top_contributor_limit]
    ]
    contributors_str = ", ".join(top_labels)
    score_band = score_band or classify_score_band(final_score)
    if score_band == "strong":
        strength_phrase = "shows a strong profile match"
    elif score_band == "moderate":
        strength_phrase = "shows a moderate profile match"
    else:
        strength_phrase = "shows a weaker but acceptable profile match"
    return (
        f"Selected at playlist position {playlist_position} "
        f"(score {final_score:.4f}) because it {strength_phrase} "
        f"on {contributors_str}. "
        f"Lead genre is '{lead_genre}'."
    )


def select_causal_driver(
    top_contributors: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    """Pick the highest-contribution driver as the mechanism-linked cause."""
    if not top_contributors:
        return {
            "component": "unknown",
            "label": "Unknown",
            "weight": 0.0,
            "similarity": 0.0,
            "contribution": 0.0,
        }
    return top_contributors[0]


def select_primary_explanation_driver(
    top_contributors: Sequence[Mapping[str, object]],
    playlist_position: int,
    *,
    enable_near_tie_blend: bool,
    near_tie_delta: float,
) -> Mapping[str, object]:
    """Select the primary explanation driver with optional near-tie rotation."""
    if not top_contributors:
        return {
            "component": "unknown",
            "label": "Unknown",
            "weight": 0.0,
            "similarity": 0.0,
            "contribution": 0.0,
        }

    if not enable_near_tie_blend or len(top_contributors) == 1:
        return top_contributors[0]

    best = safe_float(top_contributors[0].get("contribution", 0.0))
    near_tied = [
        c
        for c in top_contributors
        if best - safe_float(c.get("contribution", 0.0)) <= near_tie_delta
    ]
    if len(near_tied) <= 1:
        return top_contributors[0]

    idx = (max(int(playlist_position), 1) - 1) % len(near_tied)
    return near_tied[idx]
