"""Stage-level stabilization tests for retrieval.stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from retrieval.models import RetrievalArtifacts, RetrievalControls, RetrievalEvaluationResult, RetrievalInputs, RetrievalPaths
from retrieval.stage import RetrievalStage


def _controls(*, recency_offset: int | None = 5) -> RetrievalControls:
    return RetrievalControls(
        config_source="test",
        run_config_path=None,
        run_config_schema_version=None,
        signal_mode={"name": "custom"},
        profile_top_lead_genre_limit=3,
        profile_top_tag_limit=3,
        profile_top_genre_limit=3,
        semantic_strong_keep_score=2,
        semantic_min_keep_score=1,
        numeric_support_min_pass=1,
        numeric_support_min_score=1.0,
        use_weighted_semantics=False,
        use_continuous_numeric=False,
        enable_popularity_numeric=False,
        lead_genre_partial_match_threshold=0.5,
        language_filter_enabled=True,
        language_filter_codes=["en"],
        recency_years_min_offset=recency_offset,
        numeric_thresholds={"tempo": 17.0},
        bl004_bl005_handshake_validation_policy="warn",
        runtime_control_resolution_diagnostics={
            "resolution_path": "environment",
            "normalization_event_count": 1,
        },
        runtime_control_validation_warnings=["test warning"],
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

    summary: dict[str, object] = {
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
        controls=_controls(recency_offset=None),
        summary=summary,
        decisions=[
            {
                "track_id": "cand_1",
                "is_seed_track": 0,
                "decision": "reject",
                "decision_path": "reject_threshold",
                "semantic_score": 0.4,
                "numeric_pass_count": 0,
                "numeric_support_score_selected": 0.2,
                "tempo_distance": 25.0,
            }
        ],
        candidate_rows=inputs.candidate_rows,
        kept_rows=inputs.candidate_rows,
        output_paths={"filtered_path": filtered_path, "decisions_path": decisions_path},
    )
    payload_obj = cast(dict[str, Any], payload)
    counts = cast(dict[str, Any], payload_obj["counts"])
    config = cast(dict[str, Any], payload_obj["config"])
    language_filter = cast(dict[str, Any], config["language_filter"])
    output_files = cast(dict[str, Any], payload_obj["output_files"])
    runtime_control_resolution = cast(dict[str, Any], config["runtime_control_resolution"])
    threshold_attribution = cast(dict[str, Any], payload_obj["threshold_attribution"])
    bounded_what_if = cast(dict[str, Any], payload_obj["bounded_what_if_estimates"])

    assert payload_obj["task"] == "BL-005"
    assert counts["seed_tracks_excluded"] == 1
    assert counts["rejected_by_language_filter"] == 1
    assert cast(dict[str, Any], config["signal_mode"])["name"] == "custom"
    assert language_filter["enabled"] is True
    assert output_files["filtered_candidates_path"] == str(filtered_path)
    assert runtime_control_resolution["resolution_path"] == "environment"
    assert payload_obj["runtime_control_validation_warnings"] == ["test warning"]
    assert threshold_attribution["rejected_threshold_candidates"] == 1
    assert "tempo" in cast(dict[str, Any], threshold_attribution["numeric_feature_fail_counts"])
    assert "relaxed_estimate" in bounded_what_if
    assert "tightened_estimate" in bounded_what_if


def test_run_returns_typed_artifacts(monkeypatch, tmp_path: Path) -> None:
    stage = RetrievalStage(root=tmp_path)

    output_dir = tmp_path / "retrieval_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = RetrievalPaths(
        profile_path=tmp_path / "bl004_preference_profile.json",
        seed_trace_path=tmp_path / "bl004_seed_trace.csv",
        candidate_path=tmp_path / "ds001_working_candidate_dataset.csv",
        output_dir=output_dir,
    )
    inputs = RetrievalInputs(
        profile={"semantic_profile": {}},
        candidate_rows=[{"track_id": "cand_1"}],
        seed_trace_rows=[{"track_id": "seed_1"}],
    )
    controls = _controls(recency_offset=None)
    context = object()

    class _FakeRetrievalEvaluator:
        def __init__(self, runtime_context: object) -> None:
            self.runtime_context = runtime_context

        def evaluate(self, _: list[dict[str, str]]) -> RetrievalEvaluationResult:
            return RetrievalEvaluationResult(
                decisions=[{"track_id": "cand_1", "decision": "keep"}],
                kept_rows=[{"track_id": "cand_1"}],
                summary={"decision_counts": {"rejected_threshold": 2, "seed_excluded": 1}},
            )

    monkeypatch.setattr("retrieval.stage.ensure_paths_exist", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(RetrievalStage, "resolve_paths", lambda self: paths)
    monkeypatch.setattr(RetrievalStage, "resolve_runtime_controls", lambda self: controls)
    monkeypatch.setattr(RetrievalStage, "load_inputs", staticmethod(lambda *_args, **_kwargs: inputs))
    monkeypatch.setattr(RetrievalStage, "build_runtime_context", staticmethod(lambda **_kwargs: context))
    monkeypatch.setattr("retrieval.stage.RetrievalEvaluator", _FakeRetrievalEvaluator)

    filtered_path = output_dir / "bl005_filtered_candidates.csv"
    decisions_path = output_dir / "bl005_candidate_decisions.csv"
    diagnostics_path = output_dir / "bl005_candidate_diagnostics.json"
    monkeypatch.setattr(
        RetrievalStage,
        "write_output_artifacts",
        staticmethod(lambda **_kwargs: {"filtered_path": filtered_path, "decisions_path": decisions_path}),
    )
    monkeypatch.setattr(RetrievalStage, "build_diagnostics_payload", staticmethod(lambda **_kwargs: {}))
    monkeypatch.setattr(RetrievalStage, "write_diagnostics_with_hashes", staticmethod(lambda **_kwargs: None))

    artifacts = stage.run()

    assert isinstance(artifacts, RetrievalArtifacts)
    assert artifacts.filtered_path == filtered_path
    assert artifacts.decisions_path == decisions_path
    assert artifacts.diagnostics_path == diagnostics_path
    assert artifacts.kept_candidates_count == 1
    assert artifacts.rejected_candidates_count == 2
    assert artifacts.seed_excluded_count == 1
