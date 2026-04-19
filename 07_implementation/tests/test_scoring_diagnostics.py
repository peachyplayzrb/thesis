"""Tests for scoring.diagnostics."""

from scoring.diagnostics import (
    build_feature_availability_summary,
    build_score_distribution_diagnostics,
    build_scoring_sensitivity_diagnostics,
    contribution_breakdown,
)


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


def test_scoring_sensitivity_diagnostics_disabled_returns_stub() -> None:
    diagnostics = build_scoring_sensitivity_diagnostics(
        [],
        active_component_weights={"tempo_score": 0.5, "lead_genre_score": 0.5},
        enabled=False,
        top_k=10,
        perturbation_pct=0.10,
        max_components=5,
    )

    assert diagnostics["active"] is False
    assert diagnostics["reason"] == "disabled_by_control"


def test_scoring_sensitivity_diagnostics_reports_rank_shift() -> None:
    rows = [
        {
            "track_id": "a",
            "final_score": 0.70,
            "tempo_contribution": 0.30,
            "lead_genre_contribution": 0.40,
        },
        {
            "track_id": "b",
            "final_score": 0.69,
            "tempo_contribution": 0.45,
            "lead_genre_contribution": 0.24,
        },
        {
            "track_id": "c",
            "final_score": 0.68,
            "tempo_contribution": 0.15,
            "lead_genre_contribution": 0.53,
        },
    ]

    diagnostics = build_scoring_sensitivity_diagnostics(
        rows,
        active_component_weights={"tempo_score": 0.5, "lead_genre_score": 0.5},
        enabled=True,
        top_k=2,
        perturbation_pct=0.50,
        max_components=2,
    )

    assert diagnostics["active"] is True
    assert diagnostics["top_k"] == 2
    assert diagnostics["perturbations"]
    assert diagnostics["component_sensitivity_ranking"]
    assert any(item["rank_shifts_count"] > 0 for item in diagnostics["perturbations"])


def test_build_feature_availability_summary_reports_numeric_and_semantic_sparsity() -> None:
    summary = build_feature_availability_summary(
        [
            {
                "danceability": "0.5",
                "energy": "0.6",
                "valence": "0.7",
                "tempo": "120",
                "duration_ms": "180000",
                "popularity": "55",
                "key": "1",
                "mode": "1",
                "genres": "rock,indie",
                "tags": "guitar",
            },
            {
                "danceability": "",
                "energy": "",
                "valence": "",
                "tempo": "",
                "duration_ms": "",
                "popularity": "",
                "key": "",
                "mode": "",
                "genres": "",
                "tags": "mellow",
            },
        ]
    )

    assert summary["candidate_count"] == 2
    assert summary["rows_with_all_numeric_features"] == 1
    assert summary["rows_with_no_numeric_features"] == 1
    assert summary["rows_with_no_semantic_signal"] == 0
    assert summary["lead_genre_source_counts"]["genres"] == 1
    assert summary["lead_genre_source_counts"]["tags"] == 1
    assert summary["numeric_feature_coverage_by_feature"]["tempo"] == 0.5
