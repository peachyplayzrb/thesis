"""Tests for transparency.explanation_driver."""

from transparency.explanation_driver import (
    build_why_selected,
    classify_score_band,
    select_causal_driver,
    select_primary_explanation_driver,
)


def test_classify_score_band_returns_expected_bands() -> None:
    assert classify_score_band(0.80) == "strong"
    assert classify_score_band(0.60) == "moderate"
    assert classify_score_band(0.40) == "weak"


def test_classify_score_band_prefers_percentile_when_present() -> None:
    assert classify_score_band(0.40, 95.0) == "strong"
    assert classify_score_band(0.40, 75.0) == "moderate"
    assert classify_score_band(0.99, 45.0) == "weak"


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
    assert "strong profile match" in text
    assert "Tempo (BPM), Genre overlap" in text
    assert "Lead genre is 'indie'" in text


def test_build_why_selected_uses_moderate_wording_band() -> None:
    text = build_why_selected(
        lead_genre="electronic",
        final_score=0.62,
        top_contributors=[{"label": "Tag overlap"}],
        playlist_position=1,
        top_contributor_limit=1,
    )
    assert "moderate profile match" in text


def test_build_why_selected_uses_weaker_wording_band() -> None:
    text = build_why_selected(
        lead_genre="pop",
        final_score=0.41,
        top_contributors=[{"label": "Tempo (BPM)"}],
        playlist_position=4,
        top_contributor_limit=1,
    )
    assert "weaker but acceptable profile match" in text


def test_build_why_selected_uses_explicit_score_band_override() -> None:
    text = build_why_selected(
        lead_genre="pop",
        final_score=0.41,
        top_contributors=[{"label": "Tempo (BPM)"}],
        playlist_position=2,
        top_contributor_limit=1,
        score_band="strong",
    )
    assert "strong profile match" in text


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


def test_select_causal_driver_prefers_top_contributor() -> None:
    top = [
        {"label": "Tempo", "contribution": 0.4},
        {"label": "Tag overlap", "contribution": 0.39},
    ]
    assert select_causal_driver(top)["label"] == "Tempo"
