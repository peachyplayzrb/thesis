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
    hash_input_chain = summary["hash_input_chain"]
    assert hash_input_chain["schema_version"] == "bl013-hash-input-chain-v1"
    assert isinstance(hash_input_chain["stable_input_artifacts"], list)
    assert "chain_component_count" in hash_input_chain
    if hash_input_chain["chain_component_count"] > 0:
        assert isinstance(hash_input_chain["chain_sha256"], str)


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


def test_finalize_run_hash_input_chain_includes_authority_artifacts(monkeypatch, tmp_path) -> None:
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

    run_config_path = tmp_path / "run_config.json"
    run_config_path.write_text("{}", encoding="utf-8")

    summary, _, _ = summary_builder.finalize_run(
        output_dir=tmp_path,
        summary_prefix="bl013_orchestration_run",
        run_id="BL013-ENTRYPOINT-TEST",
        generated_at_utc="2026-04-18T03:00:00Z",
        continue_on_error=False,
        python_executable="python",
        run_config_path=run_config_path,
        run_config_artifacts={
            "run_intent": {
                "path": "run_intent.json",
                "sha256": "INTENT_SHA",
                "artifact_schema_version": "run-intent-config-v1",
            },
            "run_effective_config": {
                "path": "run_effective_config.json",
                "sha256": "EFFECTIVE_SHA",
                "artifact_schema_version": "run-effective-config-v1",
            },
        },
        refresh_seed=False,
        verify_determinism=False,
        verify_determinism_replay_count=1,
        stage_order=["BL-004"],
        stage_results=[{"stage_id": "BL-004", "status": "pass", "return_code": 0}],
        pipeline_started=0.0,
        root=tmp_path,
    )

    hash_input_chain = summary["hash_input_chain"]
    authority_chain = hash_input_chain["authority_chain"]

    assert authority_chain["requested_run_config"]["exists"] is True
    assert authority_chain["requested_run_config"]["sha256"] is not None
    assert authority_chain["run_intent"]["sha256"] == "INTENT_SHA"
    assert authority_chain["run_effective_config"]["sha256"] == "EFFECTIVE_SHA"
    assert hash_input_chain["chain_component_count"] >= 3
    assert isinstance(hash_input_chain["chain_sha256"], str)
