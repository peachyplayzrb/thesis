"""Helpers for selecting and wording BL-008 explanation drivers."""

from __future__ import annotations

from typing import Mapping, Sequence

from shared_utils.parsing import safe_float


def build_why_selected(
    lead_genre: str,
    final_score: float,
    top_contributors: Sequence[Mapping[str, object]],
    playlist_position: int,
    top_contributor_limit: int,
) -> str:
    """Build the final human-readable explanation sentence for one playlist track."""
    top_labels = [
        str(c.get("label", "Unknown"))
        for c in top_contributors[:top_contributor_limit]
    ]
    contributors_str = ", ".join(top_labels)
    if final_score >= 0.75:
        strength_phrase = "shows a strong profile match"
    elif final_score >= 0.5:
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
    """Select the primary explanation driver, with optional near-tie rotation for diversity."""
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
