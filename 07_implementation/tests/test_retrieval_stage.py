"""Stage-level stabilization tests for retrieval.stage."""

from __future__ import annotations

from pathlib import Path

from retrieval.models import RetrievalControls, RetrievalInputs, RetrievalPaths
from retrieval.stage import RetrievalStage


def _controls(*, recency_offset: int | None = 5) -> RetrievalControls:
    return RetrievalControls(
        config_source="test",
        run_config_path=None,
        run_config_schema_version=None,
        profile_top_lead_genre_limit=3,
        profile_top_tag_limit=3,
        profile_top_genre_limit=3,
        semantic_strong_keep_score=2,
        semantic_min_keep_score=1,
        numeric_support_min_pass=1,
        lead_genre_partial_match_threshold=0.5,
        language_filter_enabled=True,
        language_filter_codes=["en"],
        recency_years_min_offset=recency_offset,
        numeric_thresholds={"tempo": 17.0},
    )


def test_build_runtime_context_uses_threshold_overrides_and_recency() -> None:
    inputs = RetrievalInputs(
        profile={
            "semantic_profile": {
                "top_tags": [{"label": "rock"}],
                "top_genres": [{"label": "alt-rock"}],
                "top_lead_genres": [{"label": "rock"}],
            },
            "numeric_feature_profile": {
                "tempo": 120.0,
            },
        },
        candidate_rows=[{"track_id": "cand_1", "tempo": "121"}],
        seed_trace_rows=[{"track_id": "seed_1"}],
    )

    context = RetrievalStage.build_runtime_context(inputs=inputs, controls=_controls())

    assert context.seed_track_ids == {"seed_1"}
    assert context.numeric_features_enabled is True
    assert context.active_numeric_specs["tempo"].threshold == 17.0
    assert context.recency_min_release_year == context.current_year_utc - 5
    assert context.language_filter_codes == ["en"]


def test_build_diagnostics_payload_includes_expected_counts(tmp_path: Path) -> None:
    profile_path = tmp_path / "bl004_preference_profile.json"
    seed_trace_path = tmp_path / "bl004_seed_trace.csv"
    candidate_path = tmp_path / "ds001_working_candidate_dataset.csv"
    output_dir = tmp_path / "retrieval_outputs"
    output_dir.mkdir()

    profile_path.write_text("{}", encoding="utf-8")
    seed_trace_path.write_text("track_id\nseed_1\n", encoding="utf-8")
    candidate_path.write_text("track_id\ncand_1\n", encoding="utf-8")

    paths = RetrievalPaths(
        profile_path=profile_path,
        seed_trace_path=seed_trace_path,
        candidate_path=candidate_path,
        output_dir=output_dir,
    )

    inputs = RetrievalInputs(
        profile={
            "semantic_profile": {
                "top_tags": [{"label": "indie"}],
                "top_genres": [{"label": "rock"}],
                "top_lead_genres": [{"label": "rock"}],
            },
            "numeric_feature_profile": {"tempo": 100.0},
        },
        candidate_rows=[{"track_id": "cand_1", "tempo": "100"}],
        seed_trace_rows=[{"track_id": "seed_1"}],
    )
    context = RetrievalStage.build_runtime_context(inputs=inputs, controls=_controls(recency_offset=None))

    filtered_path = output_dir / "bl005_filtered_candidates.csv"
    decisions_path = output_dir / "bl005_candidate_decisions.csv"
    filtered_path.write_text("track_id\ncand_1\n", encoding="utf-8")
    decisions_path.write_text("track_id,decision\ncand_1,keep\n", encoding="utf-8")

    summary = {
        "decision_counts": {"seed_excluded": 1, "rejected_threshold": 2},
        "decision_path_counts": {"reject_language_filter": 1, "reject_recency_gate": 1},
        "semantic_rule_hits": {"lead_genre": 1},
        "numeric_rule_hits": {"tempo": 1},
        "semantic_score_distribution": {"2": 1},
        "numeric_pass_distribution": {"1": 1},
    }

    payload = RetrievalStage.build_diagnostics_payload(
        run_id="BL005-FILTER-TEST",
        elapsed_seconds=0.123,
        paths=paths,
        runtime_context=context,
        summary=summary,
        candidate_rows=inputs.candidate_rows,
        kept_rows=inputs.candidate_rows,
        output_paths={"filtered_path": filtered_path, "decisions_path": decisions_path},
    )

    assert payload["task"] == "BL-005"
    assert payload["counts"]["seed_tracks_excluded"] == 1
    assert payload["counts"]["rejected_by_language_filter"] == 1
    assert payload["config"]["language_filter"]["enabled"] is True
    assert payload["output_files"]["filtered_candidates_path"] == str(filtered_path)
