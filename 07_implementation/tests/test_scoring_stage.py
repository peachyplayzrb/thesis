"""Stage-level tests for scoring.stage."""

from __future__ import annotations

from pathlib import Path

from scoring.models import ScoringControls, ScoringPaths
from scoring.stage import ScoringStage


def _controls() -> ScoringControls:
    return ScoringControls(
        config_source="test",
        run_config_path=None,
        run_config_schema_version=None,
        signal_mode={"name": "custom"},
        component_weights={
            "tempo_score": 0.5,
            "lead_genre_score": 0.25,
            "genre_overlap_score": 0.15,
            "tag_overlap_score": 0.1,
        },
        numeric_thresholds={"tempo": 25.0},
    )


def _controls_with_influence_apply() -> ScoringControls:
    return ScoringControls(
        config_source="test",
        run_config_path=None,
        run_config_schema_version=None,
        signal_mode={"name": "custom"},
        component_weights={
            "tempo_score": 0.5,
            "lead_genre_score": 0.25,
            "genre_overlap_score": 0.15,
            "tag_overlap_score": 0.1,
        },
        numeric_thresholds={"tempo": 25.0},
        apply_bl003_influence_tracks=True,
        influence_track_bonus_scale=0.25,
    )


def test_build_runtime_context_applies_numeric_override() -> None:
    profile = {
        "numeric_feature_profile": {"tempo": 120.0},
        "semantic_profile": {
            "top_lead_genres": [{"label": "rock", "weight": 1.0}],
            "top_genres": [{"label": "rock", "weight": 1.0}],
            "top_tags": [{"label": "indie", "weight": 1.0}],
        },
    }

    context = ScoringStage.build_runtime_context(
        profile=profile,
        runtime_controls=_controls(),
    )

    assert "tempo" in context.active_numeric_specs
    assert context.active_numeric_specs["tempo"]["threshold"] == 25.0
    assert round(sum(context.active_component_weights.values()), 6) == 1.0


def test_build_summary_includes_expected_output_paths(tmp_path: Path) -> None:
    profile_path = tmp_path / "bl004_preference_profile.json"
    filtered_path = tmp_path / "bl005_filtered_candidates.csv"
    output_dir = tmp_path / "scoring_outputs"
    output_dir.mkdir()

    profile_path.write_text("{}", encoding="utf-8")
    filtered_path.write_text("track_id\ncand_1\n", encoding="utf-8")

    paths = ScoringPaths(
        profile_path=profile_path,
        filtered_candidates_path=filtered_path,
        output_dir=output_dir,
    )

    diagnostics_path = output_dir / "bl006_score_distribution_diagnostics.json"
    scored_path = output_dir / "bl006_scored_candidates.csv"
    diagnostics_path.write_text("{}", encoding="utf-8")
    scored_path.write_text("rank,track_id,final_score\n1,cand_1,0.9\n", encoding="utf-8")

    runtime_context = ScoringStage.build_runtime_context(
        profile={
            "numeric_feature_profile": {"tempo": 120.0},
            "semantic_profile": {
                "top_lead_genres": [{"label": "rock", "weight": 1.0}],
                "top_genres": [{"label": "rock", "weight": 1.0}],
                "top_tags": [{"label": "indie", "weight": 1.0}],
            },
        },
        runtime_controls=_controls(),
    )

    scored_rows = [
        {
            "rank": 1,
            "track_id": "cand_1",
            "lead_genre": "rock",
            "matched_genres": "rock",
            "matched_tags": "indie",
            "final_score": 0.9,
            "raw_final_score": 0.9,
            "danceability_similarity": 0.0,
            "danceability_contribution": 0.0,
            "energy_similarity": 0.0,
            "energy_contribution": 0.0,
            "valence_similarity": 0.0,
            "valence_contribution": 0.0,
            "tempo_similarity": 1.0,
            "tempo_contribution": 0.5,
            "duration_ms_similarity": 0.0,
            "duration_ms_contribution": 0.0,
            "popularity_similarity": 0.0,
            "popularity_contribution": 0.0,
            "key_similarity": 0.0,
            "key_contribution": 0.0,
            "mode_similarity": 0.0,
            "mode_contribution": 0.0,
            "lead_genre_similarity": 1.0,
            "lead_genre_contribution": 0.25,
            "genre_overlap_similarity": 1.0,
            "genre_overlap_contribution": 0.15,
            "tag_overlap_similarity": 1.0,
            "tag_overlap_contribution": 0.1,
        }
    ]

    summary = ScoringStage.build_summary(
        run_id="BL006-SCORE-TEST",
        elapsed_seconds=0.123,
        paths=paths,
        runtime_context=runtime_context,
        scored_rows=scored_rows,
        distribution_diagnostics={"rank_cliff": None},
        feature_availability_summary={"candidate_count": 1},
        diagnostics_path=diagnostics_path,
        scored_path=scored_path,
    )

    assert summary["task"] == "BL-006"
    assert summary["counts"]["candidates_scored"] == 1
    assert summary["config"]["signal_mode"]["name"] == "custom"
    assert summary["score_statistics"]["mean_final_score"] == 0.9
    assert summary["score_statistics"]["mean_raw_final_score"] == 0.9
    assert summary["feature_availability_summary"]["candidate_count"] == 1
    assert "scoring_sensitivity_diagnostics" in summary
    assert summary["output_files"]["scored_candidates_path"] == str(scored_path)
    assert summary["output_files"]["score_distribution_diagnostics_path"] == str(diagnostics_path)


def test_build_influence_apply_noop_warning_when_requested_but_bl003_disabled() -> None:
    controls = _controls_with_influence_apply()
    profile = {
        "numeric_feature_profile": {"tempo": 120.0},
        "semantic_profile": {
            "top_lead_genres": [{"label": "rock", "weight": 1.0}],
            "top_genres": [{"label": "rock", "weight": 1.0}],
            "top_tags": [{"label": "indie", "weight": 1.0}],
        },
    }

    context = ScoringStage.build_runtime_context(
        profile=profile,
        bl003_summary={
            "inputs": {
                "influence_tracks": {
                    "enabled": False,
                    "track_ids": ["cand_1"],
                    "preference_weight": 0.8,
                }
            }
        },
        runtime_controls=controls,
    )

    warning = ScoringStage._build_influence_apply_noop_warning(
        controls=controls,
        context=context,
    )

    assert context.apply_bl003_influence_tracks is False
    assert warning is not None
    assert "requested" in warning
    assert "no influence bonus was applied" in warning


def test_build_summary_surfaces_influence_noop_diagnostic(tmp_path: Path) -> None:
    profile_path = tmp_path / "bl004_preference_profile.json"
    filtered_path = tmp_path / "bl005_filtered_candidates.csv"
    output_dir = tmp_path / "scoring_outputs"
    output_dir.mkdir()

    profile_path.write_text("{}", encoding="utf-8")
    filtered_path.write_text("track_id\ncand_1\n", encoding="utf-8")

    paths = ScoringPaths(
        profile_path=profile_path,
        filtered_candidates_path=filtered_path,
        output_dir=output_dir,
    )

    diagnostics_path = output_dir / "bl006_score_distribution_diagnostics.json"
    scored_path = output_dir / "bl006_scored_candidates.csv"
    diagnostics_path.write_text("{}", encoding="utf-8")
    scored_path.write_text("rank,track_id,final_score\n1,cand_1,0.9\n", encoding="utf-8")

    runtime_context = ScoringStage.build_runtime_context(
        profile={
            "numeric_feature_profile": {"tempo": 120.0},
            "semantic_profile": {
                "top_lead_genres": [{"label": "rock", "weight": 1.0}],
                "top_genres": [{"label": "rock", "weight": 1.0}],
                "top_tags": [{"label": "indie", "weight": 1.0}],
            },
        },
        bl003_summary={
            "inputs": {
                "influence_tracks": {
                    "enabled": False,
                    "track_ids": ["cand_1"],
                    "preference_weight": 0.8,
                }
            }
        },
        runtime_controls=_controls_with_influence_apply(),
    )

    scored_rows = [
        {
            "rank": 1,
            "track_id": "cand_1",
            "lead_genre": "rock",
            "matched_genres": "rock",
            "matched_tags": "indie",
            "final_score": 0.9,
            "raw_final_score": 0.85,
            "danceability_similarity": 0.0,
            "danceability_contribution": 0.0,
            "energy_similarity": 0.0,
            "energy_contribution": 0.0,
            "valence_similarity": 0.0,
            "valence_contribution": 0.0,
            "tempo_similarity": 1.0,
            "tempo_contribution": 0.5,
            "duration_ms_similarity": 0.0,
            "duration_ms_contribution": 0.0,
            "popularity_similarity": 0.0,
            "popularity_contribution": 0.0,
            "key_similarity": 0.0,
            "key_contribution": 0.0,
            "mode_similarity": 0.0,
            "mode_contribution": 0.0,
            "lead_genre_similarity": 1.0,
            "lead_genre_contribution": 0.25,
            "genre_overlap_similarity": 1.0,
            "genre_overlap_contribution": 0.15,
            "tag_overlap_similarity": 1.0,
            "tag_overlap_contribution": 0.1,
        }
    ]

    warning = "BL-006 influence apply was requested but no influence bonus was applied"
    summary = ScoringStage.build_summary(
        run_id="BL006-SCORE-TEST",
        elapsed_seconds=0.123,
        paths=paths,
        runtime_context=runtime_context,
        scored_rows=scored_rows,
        distribution_diagnostics={"rank_cliff": None},
        feature_availability_summary={"candidate_count": 1},
        runtime_controls=_controls_with_influence_apply(),
        influence_apply_noop_warning=warning,
        diagnostics_path=diagnostics_path,
        scored_path=scored_path,
    )

    assert summary["config"]["influence_apply_requested"] is True
    assert summary["config"]["influence_apply_active"] is False
    assert summary["config"]["influence_apply_noop_warning"] == warning


def test_score_candidates_influence_bonus_preserves_raw_final_score() -> None:
    controls = _controls_with_influence_apply()
    runtime_context = ScoringStage.build_runtime_context(
        profile={
            "numeric_feature_profile": {"tempo": 120.0},
            "semantic_profile": {
                "top_lead_genres": [{"label": "rock", "weight": 1.0}],
                "top_genres": [{"label": "rock", "weight": 1.0}],
                "top_tags": [{"label": "indie", "weight": 1.0}],
            },
        },
        bl003_summary={
            "inputs": {
                "influence_tracks": {
                    "enabled": True,
                    "track_ids": ["cand_1"],
                    "preference_weight": 1.0,
                }
            }
        },
        runtime_controls=controls,
    )

    scored_rows = ScoringStage.score_candidates(
        candidates=[
            {
                "track_id": "cand_1",
                "tempo": "120",
                "genres": "rock",
                "tags": "",
            }
        ],
        runtime_context=runtime_context,
    )

    assert len(scored_rows) == 1
    scored = scored_rows[0]
    assert float(scored["raw_final_score"]) > 0.0
    assert float(scored["final_score"]) > float(scored["raw_final_score"])
