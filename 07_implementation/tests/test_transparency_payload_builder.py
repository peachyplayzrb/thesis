"""Tests for transparency.payload_builder."""

from transparency.payload_builder import (
    build_ordered_components,
    build_score_breakdown,
    build_track_payload,
    top_contributor_counts,
)


def test_build_ordered_components_prefers_known_component_order() -> None:
    active = {
        "genre_overlap_score": 0.2,
        "tempo_score": 0.3,
        "unknown_score": 0.1,
    }
    ordered = build_ordered_components(active)
    assert ordered[:2] == ["tempo_score", "genre_overlap_score"]
    assert ordered[-1] == "unknown_score"


def test_build_score_breakdown_uses_component_and_canonical_weights() -> None:
    scored = {
        "tempo_similarity": 0.8,
        "tempo_contribution": 0.24,
        "genre_overlap_similarity": 0.5,
        "genre_overlap_contribution": 0.1,
    }
    active = {
        "tempo_score": 0.3,
        "genre_overlap": 0.2,
    }
    breakdown = build_score_breakdown(
        scored,
        ["tempo_score", "genre_overlap"],
        active,
    )
    assert breakdown[0]["component"] == "tempo"
    assert breakdown[0]["weight"] == 0.3
    assert breakdown[1]["component"] == "genre_overlap"
    assert breakdown[1]["weight"] == 0.2
    assert breakdown[0]["contribution_share_pct"] == 70.588
    assert breakdown[0]["margin_vs_next_contributor"] == 0.14
    assert breakdown[1]["contribution_share_pct"] == 29.412
    assert breakdown[1]["margin_vs_next_contributor"] == 0.0


def test_build_score_breakdown_zero_sum_share_guard() -> None:
    breakdown = build_score_breakdown(
        {
            "tempo_similarity": 0.0,
            "tempo_contribution": 0.0,
            "genre_overlap_similarity": 0.0,
            "genre_overlap_contribution": 0.0,
        },
        ["tempo", "genre_overlap"],
        {"tempo": 0.5, "genre_overlap": 0.5},
    )
    assert breakdown[0]["contribution_share_pct"] == 0.0
    assert breakdown[1]["contribution_share_pct"] == 0.0
    assert breakdown[0]["margin_vs_next_contributor"] == 0.0
    assert breakdown[1]["margin_vs_next_contributor"] == 0.0


def test_build_score_breakdown_single_component_margin_guard() -> None:
    breakdown = build_score_breakdown(
        {
            "tempo_similarity": 0.8,
            "tempo_contribution": 0.24,
        },
        ["tempo"],
        {"tempo": 0.3},
    )
    assert breakdown[0]["contribution_share_pct"] == 100.0
    assert breakdown[0]["margin_vs_next_contributor"] == 0.0


def test_build_track_payload_maps_assembly_rule_label() -> None:
    payload = build_track_payload(
        track_id="t1",
        lead_genre="rock",
        playlist_position=1,
        score_rank=2,
        score_percentile=99.5,
        score_band="moderate",
        final_score=0.72,
        raw_final_score=0.69,
        score_breakdown=[],
        top_contributors=[],
        primary_driver={"label": "Tempo"},
        causal_driver={"label": "Tempo"},
        narrative_driver={"label": "Tag overlap"},
        control_provenance_ref="run_level",
        trace_row={"decision": "included", "exclusion_reason": "genre_cap_exceeded"},
        why_selected="why",
    )
    assert payload["assembly_context"]["admission_rule"] == "R2 - genre cap exceeded"
    assert payload["primary_explanation_driver"]["label"] == "Tempo"
    assert payload["score_percentile"] == 99.5
    assert payload["score_band"] == "moderate"
    assert payload["causal_driver"]["label"] == "Tempo"
    assert payload["narrative_driver"]["label"] == "Tag overlap"
    assert payload["control_provenance_ref"] == "run_level"
    assert payload["raw_final_score"] == 0.69
    assert payload["control_causality"]["schema_version"] == "bl008-control-causality-v1"
    assert payload["control_causality"]["decision_outcome"]["included_in_playlist"] is True
    assert payload["control_causality"]["effect_direction"]["expected_direction"] == "promote_or_admit"


def test_top_contributor_counts_aggregates_labels() -> None:
    payloads = [
        {"primary_explanation_driver": {"label": "Tempo"}},
        {"primary_explanation_driver": {"label": "Tempo"}},
        {"primary_explanation_driver": {"label": "Tag overlap"}},
    ]
    counts = top_contributor_counts(payloads)
    assert counts == {"Tempo": 2, "Tag overlap": 1}
