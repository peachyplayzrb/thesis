"""Orchestration-oriented tests for transparency payload assembly flow."""

from transparency.explanation_driver import (
    build_why_selected,
    select_primary_explanation_driver,
)
from transparency.payload_builder import (
    build_ordered_components,
    build_score_breakdown,
    build_track_payload,
)


def test_component_orchestration_builds_expected_track_payload() -> None:
    active_weights = {
        "tempo_score": 0.5,
        "tag_overlap_score": 0.5,
    }
    scored_row = {
        "tempo_similarity": 0.9,
        "tempo_contribution": 0.45,
        "tag_overlap_similarity": 0.8,
        "tag_overlap_contribution": 0.4,
    }
    trace_row = {"decision": "included", "exclusion_reason": ""}

    ordered = build_ordered_components(active_weights)
    breakdown = build_score_breakdown(scored_row, ordered, active_weights)
    top = sorted(breakdown, key=lambda item: item["contribution"], reverse=True)[:2]
    primary = select_primary_explanation_driver(
        top,
        playlist_position=1,
        enable_near_tie_blend=True,
        near_tie_delta=0.1,
    )
    why_selected = build_why_selected(
        lead_genre="rock",
        final_score=0.91,
        top_contributors=top,
        playlist_position=1,
        top_contributor_limit=2,
    )

    payload = build_track_payload(
        track_id="t1",
        lead_genre="rock",
        playlist_position=1,
        score_rank=2,
        score_percentile=99.0,
        score_band="strong",
        final_score=0.91,
        raw_final_score=0.88,
        score_breakdown=breakdown,
        top_contributors=top,
        primary_driver=primary,
        trace_row=trace_row,
        why_selected=why_selected,
    )

    assert payload["track_id"] == "t1"
    assert payload["assembly_context"]["admission_rule"] == "Admitted on first evaluation"
    assert payload["primary_explanation_driver"]["component"] == "tempo"
    assert payload["top_score_contributors"][0]["contribution"] == 0.45
    assert payload["raw_final_score"] == 0.88
    assert payload["score_percentile"] == 99.0
    assert payload["score_band"] == "strong"
