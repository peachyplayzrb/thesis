"""Tests for transparency.explanation_driver."""

from transparency.explanation_driver import (
    build_why_selected,
    select_primary_explanation_driver,
)


def test_build_why_selected_includes_position_score_and_lead_genre() -> None:
    text = build_why_selected(
        lead_genre="indie",
        final_score=0.8123,
        top_contributors=[{"label": "Tempo (BPM)"}, {"label": "Genre overlap"}],
        playlist_position=3,
        top_contributor_limit=2,
    )
    assert "position 3" in text
    assert "0.8123" in text
    assert "Tempo (BPM), Genre overlap" in text
    assert "Lead genre is 'indie'" in text


def test_select_primary_explanation_driver_returns_unknown_when_empty() -> None:
    picked = select_primary_explanation_driver(
        [],
        1,
        enable_near_tie_blend=True,
        near_tie_delta=0.02,
    )
    assert picked["label"] == "Unknown"
    assert picked["contribution"] == 0.0


def test_select_primary_explanation_driver_rotates_when_near_tied() -> None:
    top = [
        {"label": "Tempo", "contribution": 0.4},
        {"label": "Tag overlap", "contribution": 0.39},
    ]
    picked_pos1 = select_primary_explanation_driver(
        top,
        1,
        enable_near_tie_blend=True,
        near_tie_delta=0.02,
    )
    picked_pos2 = select_primary_explanation_driver(
        top,
        2,
        enable_near_tie_blend=True,
        near_tie_delta=0.02,
    )
    assert picked_pos1["label"] == "Tempo"
    assert picked_pos2["label"] == "Tag overlap"
