from __future__ import annotations

from orchestration import summary_builder


def test_finalize_run_passes_with_determinism_stage(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        summary_builder,
        "compute_stable_artifact_hashes",
        lambda root: ({"artifact": "ABC"}, []),
    )
    monkeypatch.setattr(
        summary_builder,
        "collect_refinement_diagnostics",
        lambda root: {},
    )

    stage_results = [
        {"stage_id": "BL-003", "status": "pass", "return_code": 0},
        {"stage_id": "BL-004", "status": "pass", "return_code": 0},
        {"stage_id": "BL-010", "status": "pass", "return_code": 0},
    ]

    summary, _, _ = summary_builder.finalize_run(
        output_dir=tmp_path,
        summary_prefix="bl013_orchestration_run",
        run_id="BL013-ENTRYPOINT-TEST",
        generated_at_utc="2026-04-18T03:00:00Z",
        continue_on_error=False,
        python_executable="python",
        run_config_path=None,
        run_config_artifacts={},
        refresh_seed=False,
        verify_determinism=True,
        verify_determinism_replay_count=3,
        stage_order=["BL-003", "BL-004"],
        stage_results=stage_results,
        pipeline_started=0.0,
        root=tmp_path,
    )

    assert summary["overall_status"] == "pass"
    assert summary["verify_determinism"] is True
    assert summary["verify_determinism_replay_count"] == 3
    stage_execution = summary["stage_execution"]
    assert stage_execution["requested_stage_order"] == ["BL-003", "BL-004"]
    assert stage_execution["executed_stage_sequence"] == ["BL-003", "BL-004", "BL-010"]
    assert stage_execution["requested_stage_execution_sequence"] == ["BL-003", "BL-004"]
    assert stage_execution["requested_stages_not_executed"] == []
    assert stage_execution["executed_non_requested_stages"] == ["BL-010"]
    assert stage_execution["duplicate_requested_stage_executions"] == {}


def test_finalize_run_reports_requested_stage_skips_and_duplicates(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        summary_builder,
        "compute_stable_artifact_hashes",
        lambda root: ({"artifact": "ABC"}, []),
    )
    monkeypatch.setattr(
        summary_builder,
        "collect_refinement_diagnostics",
        lambda root: {},
    )

    stage_results = [
        {"stage_id": "BL-003", "status": "pass", "return_code": 0},
        {"stage_id": "BL-003", "status": "pass", "return_code": 0},
        {"stage_id": "BL-005", "status": "pass", "return_code": 0},
    ]

    summary, _, _ = summary_builder.finalize_run(
        output_dir=tmp_path,
        summary_prefix="bl013_orchestration_run",
        run_id="BL013-ENTRYPOINT-TEST",
        generated_at_utc="2026-04-18T03:00:00Z",
        continue_on_error=False,
        python_executable="python",
        run_config_path=None,
        run_config_artifacts={},
        refresh_seed=True,
        verify_determinism=False,
        verify_determinism_replay_count=1,
        stage_order=["BL-003", "BL-004", "BL-005"],
        stage_results=stage_results,
        pipeline_started=0.0,
        root=tmp_path,
    )

    stage_execution = summary["stage_execution"]
    assert stage_execution["requested_stage_order"] == ["BL-003", "BL-004", "BL-005"]
    assert stage_execution["executed_stage_sequence"] == ["BL-003", "BL-003", "BL-005"]
    assert stage_execution["requested_stage_execution_sequence"] == ["BL-003", "BL-003", "BL-005"]
    assert stage_execution["requested_stages_not_executed"] == ["BL-004"]
    assert stage_execution["executed_non_requested_stages"] == []
    assert stage_execution["duplicate_requested_stage_executions"] == {"BL-003": 2}
