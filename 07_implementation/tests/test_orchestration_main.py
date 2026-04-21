from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from orchestration import main as orchestration_main
from orchestration.main import _build_execution_stage_order


def test_build_execution_stage_order_keeps_all_stages_without_refresh_seed() -> None:
    stage_order = ["BL-003", "BL-004", "BL-005"]

    result = _build_execution_stage_order(stage_order, refresh_seed=False)

    assert result == ["BL-003", "BL-004", "BL-005"]


def test_build_execution_stage_order_skips_bl003_when_refresh_seed_enabled() -> None:
    stage_order = ["BL-003", "BL-004", "BL-005"]

    result = _build_execution_stage_order(stage_order, refresh_seed=True)

    assert result == ["BL-004", "BL-005"]


def test_build_execution_stage_order_noop_when_bl003_absent() -> None:
    stage_order = ["BL-004", "BL-005"]

    result = _build_execution_stage_order(stage_order, refresh_seed=True)

    assert result == ["BL-004", "BL-005"]


def test_freshness_guard_respects_continue_on_error(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        orchestration_main,
        "validate_bl003_seed_freshness",
        lambda **kwargs: (False, "stale test seed"),
    )

    def fail_if_called(**kwargs) -> None:
        raise AssertionError("freshness guard should not exit when continue_on_error is enabled")

    monkeypatch.setattr(orchestration_main, "emit_and_exit_failure", fail_if_called)

    stage_results: list[dict[str, object]] = []
    args = SimpleNamespace(python="python", summary_prefix="bl013_orchestration_run")

    orchestration_main._maybe_emit_freshness_guard_failure(
        args=args,
        root=tmp_path,
        run_config_path=Path("run_config.json"),
        run_intent_path=Path("run_intent.json"),
        run_effective_config_path=Path("run_effective.json"),
        oc_refresh_policy="auto_if_stale",
        effective_refresh_seed=False,
        stage_results=stage_results,
        output_dir=tmp_path,
        run_id="BL013-ENTRYPOINT-TEST",
        generated_at_utc="2026-04-18T03:00:00Z",
        effective_continue_on_error=True,
        effective_verify_determinism=False,
        effective_verify_replay_count=1,
        stage_order=["BL-004"],
        pipeline_started=0.0,
        run_config_artifacts={},
    )

    assert stage_results[0]["stage_id"] == "BL-003-FRESHNESS-GUARD"
    assert stage_results[0]["status"] == "fail"
