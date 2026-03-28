"""Tests for scoring.diagnostics."""

from scoring.diagnostics import build_score_distribution_diagnostics, contribution_breakdown


def test_build_score_distribution_diagnostics_detects_rank_cliff() -> None:
    scored_rows = [
        {"final_score": 0.95},
        {"final_score": 0.82},
        {"final_score": 0.70},
    ]

    diagnostics = build_score_distribution_diagnostics(scored_rows)

    assert diagnostics["score_range"]["max"] == 0.95
    assert diagnostics["score_range"]["min"] == 0.7
    assert diagnostics["rank_cliff"]["detected"] is True
    assert diagnostics["rank_cliff"]["max_gap"]["between_rank"] == 1


def test_contribution_breakdown_returns_zeros_on_empty_input() -> None:
    result = contribution_breakdown([])

    assert result["numeric_contribution_mean"] == 0.0
    assert result["semantic_contribution_mean"] == 0.0
    assert result["tempo_mean"] == 0.0
    assert result["tag_overlap_mean"] == 0.0


def test_contribution_breakdown_aggregates_component_means() -> None:
    rows = [
        {
            "danceability_contribution": 0.1,
            "energy_contribution": 0.2,
            "valence_contribution": 0.3,
            "tempo_contribution": 0.1,
            "duration_ms_contribution": 0.05,
            "key_contribution": 0.02,
            "mode_contribution": 0.03,
            "lead_genre_contribution": 0.08,
            "genre_overlap_contribution": 0.05,
            "tag_overlap_contribution": 0.07,
        },
        {
            "danceability_contribution": 0.2,
            "energy_contribution": 0.1,
            "valence_contribution": 0.2,
            "tempo_contribution": 0.2,
            "duration_ms_contribution": 0.04,
            "key_contribution": 0.01,
            "mode_contribution": 0.02,
            "lead_genre_contribution": 0.1,
            "genre_overlap_contribution": 0.06,
            "tag_overlap_contribution": 0.08,
        },
    ]

    result = contribution_breakdown(rows)

    assert result["danceability_mean"] == 0.15
    assert result["tag_overlap_mean"] == 0.075
    assert result["numeric_contribution_mean"] == 0.785
    assert result["semantic_contribution_mean"] == 0.22
