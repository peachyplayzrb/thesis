from __future__ import annotations

import argparse
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict

from orchestration.cli import parse_args, validate_stage_order
from orchestration.config_resolver import (
    emit_run_config_artifact_pair,
    resolve_orchestration_controls,
    resolve_stage_control_payload,
    resolve_stage_control_payloads,
)
from orchestration.seed_freshness import validate_bl003_seed_freshness
from orchestration.stage_registry import BL003_SCRIPT, DEFAULT_STAGE_ORDER, STAGE_SCRIPT_MAP
from orchestration.stage_runner import (
    build_missing_script_result,
    run_bl003_seed_refresh,
    run_stage,
)
from orchestration.summary_builder import emit_and_exit_failure, emit_run_completion
from shared_utils.io_utils import utc_now
from shared_utils.path_utils import impl_root


class EffectiveOrchestrationState(TypedDict):
    oc_refresh_policy: str
    stage_order: list[str]
    required_stable_artifacts: list[str]
    effective_continue_on_error: bool
    effective_verify_determinism: bool
    effective_verify_replay_count: int
    effective_refresh_seed: bool


def _build_execution_stage_order(stage_order: list[str], *, refresh_seed: bool) -> list[str]:
    if not refresh_seed:
        return list(stage_order)
    return [stage_id for stage_id in stage_order if stage_id != "BL-003"]


def _resolve_run_config_path(root: Path, run_config_arg: str | None) -> Path | None:
    run_config_path = (root / run_config_arg).resolve() if run_config_arg else None
    if run_config_path is not None and not run_config_path.exists():
        raise FileNotFoundError(f"Run config file not found: {run_config_path}")
    return run_config_path


def _resolve_effective_orchestration_state(
    args: argparse.Namespace,
    run_config_path: Path | None,
) -> EffectiveOrchestrationState:
    oc = resolve_orchestration_controls(run_config_path)
    oc_stage_order: list[str] | None = oc.get("stage_order")  # type: ignore[assignment]
    oc_continue: bool = bool(oc.get("continue_on_error", False))
    oc_refresh_policy: str = str(oc.get("refresh_seed_policy") or "auto_if_stale")
    oc_verify_determinism: bool = bool(oc.get("determinism_verify_on_success", False))
    oc_verify_replay_count: int = int(oc.get("determinism_verify_replay_count") or 3)
    required_stable_artifacts = [
        str(item) for item in (oc.get("required_stable_artifacts") or [])
    ]

    if args.stages is not None:
        stage_order = validate_stage_order(args.stages)
    elif oc_stage_order:
        stage_order = validate_stage_order(oc_stage_order)
    else:
        stage_order = list(DEFAULT_STAGE_ORDER)

    effective_continue_on_error: bool = bool(args.continue_on_error) or oc_continue
    effective_verify_determinism: bool = bool(args.verify_determinism) or oc_verify_determinism
    effective_verify_replay_count: int = (
        int(args.verify_determinism_replay_count)
        if args.verify_determinism_replay_count is not None
        else oc_verify_replay_count
    )
    if effective_verify_replay_count < 1:
        raise ValueError("--verify-determinism-replay-count must be >= 1")

    if oc_refresh_policy == "always":
        effective_refresh_seed = True
    elif oc_refresh_policy == "never":
        effective_refresh_seed = False
    else:
        effective_refresh_seed = bool(args.refresh_seed)

    return {
        "oc_refresh_policy": oc_refresh_policy,
        "stage_order": stage_order,
        "required_stable_artifacts": required_stable_artifacts,
        "effective_continue_on_error": effective_continue_on_error,
        "effective_verify_determinism": effective_verify_determinism,
        "effective_verify_replay_count": effective_verify_replay_count,
        "effective_refresh_seed": effective_refresh_seed,
    }


def _maybe_emit_freshness_guard_failure(
    *,
    args: argparse.Namespace,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path,
    run_effective_config_path: Path,
    oc_refresh_policy: str,
    effective_refresh_seed: bool,
    stage_results: list[dict[str, object]],
    output_dir: Path,
    run_id: str,
    generated_at_utc: str,
    effective_continue_on_error: bool,
    effective_verify_determinism: bool,
    effective_verify_replay_count: int,
    stage_order: list[str],
    pipeline_started: float,
    run_config_artifacts: dict[str, object],
    required_stable_artifacts: list[str] | None = None,
) -> None:
    if oc_refresh_policy == "never" or run_config_path is None or effective_refresh_seed:
        return

    is_fresh, reason = validate_bl003_seed_freshness(
        root=root,
        run_config_path=run_config_path,
        run_effective_config_path=run_effective_config_path,
    )
    if is_fresh:
        return

    guard_result = {
        "stage_id": "BL-003-FRESHNESS-GUARD",
        "script_path": BL003_SCRIPT,
        "command": [args.python, BL003_SCRIPT],
        "run_config_path": str(run_config_path),
        "run_intent_path": str(run_intent_path),
        "run_effective_config_path": str(run_effective_config_path),
        "return_code": 2,
        "status": "fail",
        "elapsed_seconds": 0.0,
        "stdout": "",
        "stderr": (
            f"Seed freshness guard failed: {reason}. "
            "Run BL-013 with --refresh-seed or set refresh_seed_policy=always in run-config."
        ),
    }
    stage_results.append(guard_result)
    if effective_continue_on_error:
        return
    emit_and_exit_failure(
        output_dir=output_dir,
        summary_prefix=args.summary_prefix,
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        continue_on_error=effective_continue_on_error,
        python_executable=args.python,
        run_config_path=run_config_path,
        run_config_artifacts=run_config_artifacts,
        refresh_seed=effective_refresh_seed,
        verify_determinism=effective_verify_determinism,
        verify_determinism_replay_count=effective_verify_replay_count,
        stage_order=stage_order,
        stage_results=stage_results,
        pipeline_started=pipeline_started,
        root=root,
        required_stable_artifacts=required_stable_artifacts,
    )


def _maybe_run_seed_refresh(
    *,
    args: argparse.Namespace,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path,
    run_effective_config_path: Path,
    stage_control_payloads: dict[str, dict[str, object]],
    effective_refresh_seed: bool,
    stage_results: list[dict[str, object]],
    effective_continue_on_error: bool,
    output_dir: Path,
    run_id: str,
    generated_at_utc: str,
    effective_verify_determinism: bool,
    effective_verify_replay_count: int,
    stage_order: list[str],
    pipeline_started: float,
    run_config_artifacts: dict[str, object],
    required_stable_artifacts: list[str] | None = None,
) -> None:
    if not effective_refresh_seed:
        return

    if "BL-003" not in stage_control_payloads:
        stage_control_payloads["BL-003"] = resolve_stage_control_payload(
            "BL-003",
            run_config_path,
        )
    seed_result = run_bl003_seed_refresh(
        args.python,
        root,
        run_config_path,
        run_intent_path,
        run_effective_config_path,
        stage_config_payload=stage_control_payloads.get("BL-003"),
    )
    stage_results.append(seed_result)
    if seed_result["status"] == "fail" and not effective_continue_on_error:
        emit_and_exit_failure(
            output_dir=output_dir,
            summary_prefix=args.summary_prefix,
            run_id=run_id,
            generated_at_utc=generated_at_utc,
            continue_on_error=effective_continue_on_error,
            python_executable=args.python,
            run_config_path=run_config_path,
            run_config_artifacts=run_config_artifacts,
            refresh_seed=effective_refresh_seed,
            verify_determinism=effective_verify_determinism,
            verify_determinism_replay_count=effective_verify_replay_count,
            stage_order=stage_order,
            stage_results=stage_results,
            pipeline_started=pipeline_started,
            root=root,
            required_stable_artifacts=required_stable_artifacts,
        )


def _run_execution_stages(
    *,
    args: argparse.Namespace,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path,
    run_effective_config_path: Path,
    execution_stage_order: list[str],
    stage_control_payloads: dict[str, dict[str, object]],
    stage_results: list[dict[str, object]],
    effective_continue_on_error: bool,
) -> None:
    for stage_id in execution_stage_order:
        script_relpath = STAGE_SCRIPT_MAP[stage_id]
        script_path = root / script_relpath
        if not script_path.exists():
            stage_results.append(
                build_missing_script_result(
                    stage_id=stage_id,
                    script_relpath=script_relpath,
                    python_executable=args.python,
                    run_config_path=run_config_path,
                    run_intent_path=run_intent_path,
                    run_effective_config_path=run_effective_config_path,
                )
            )
            if not effective_continue_on_error:
                break
            continue

        result = run_stage(
            args.python,
            stage_id,
            script_path,
            root,
            run_config_path,
            run_intent_path,
            run_effective_config_path,
            stage_config_payload=stage_control_payloads.get(stage_id),
        )
        stage_results.append(result)

        if result["status"] == "fail" and not effective_continue_on_error:
            break


def _maybe_run_determinism_verify(
    *,
    args: argparse.Namespace,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path,
    run_effective_config_path: Path,
    stage_results: list[dict[str, object]],
    effective_verify_determinism: bool,
    effective_verify_replay_count: int,
) -> None:
    stage_failures = [item for item in stage_results if item["status"] == "fail"]
    if not (effective_verify_determinism and not stage_failures):
        return

    bl010_script = root / "reproducibility" / "main.py"
    if not bl010_script.exists():
        stage_results.append(
            build_missing_script_result(
                stage_id="BL-010",
                script_relpath="reproducibility/main.py",
                python_executable=args.python,
                run_config_path=run_config_path,
                run_intent_path=run_intent_path,
                run_effective_config_path=run_effective_config_path,
            )
        )
        return

    replay_args = ["--replay-count", str(effective_verify_replay_count)]
    if run_config_path is not None:
        replay_args.extend(["--run-config", str(run_config_path)])
    determinism_payload = {
        "stage_id": "BL-010",
        "schema_version": "stage-config-v1",
        "resolved_from": "run_config" if run_config_path else "defaults",
        "controls": {
            "replay_count": effective_verify_replay_count,
        },
    }
    stage_results.append(
        run_stage(
            args.python,
            "BL-010",
            bl010_script,
            root,
            run_config_path,
            run_intent_path,
            run_effective_config_path,
            stage_config_payload=determinism_payload,
            extra_args=replay_args,
        )
    )


def main() -> None:
    args = parse_args()
    root = impl_root()

    run_config_path = _resolve_run_config_path(root, args.run_config)
    effective_state = _resolve_effective_orchestration_state(args, run_config_path)
    oc_refresh_policy = str(effective_state["oc_refresh_policy"])
    stage_order = list(effective_state["stage_order"])
    required_stable_artifacts = list(effective_state["required_stable_artifacts"])
    effective_continue_on_error = bool(effective_state["effective_continue_on_error"])
    effective_verify_determinism = bool(effective_state["effective_verify_determinism"])
    effective_verify_replay_count = int(effective_state["effective_verify_replay_count"])
    effective_refresh_seed = bool(effective_state["effective_refresh_seed"])

    stage_control_payloads = resolve_stage_control_payloads(
        stage_order,
        run_config_path,
        include_stage_ids=["BL-003"] if effective_refresh_seed else None,
    )

    output_dir = root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    run_id = f"BL013-ENTRYPOINT-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S-%f')}"
    generated_at_utc = utc_now()
    run_config_artifact_dir = (root / args.run_config_artifact_dir).resolve()
    run_config_artifacts = emit_run_config_artifact_pair(
        run_id=run_id,
        run_config_path=run_config_path,
        artifact_dir=run_config_artifact_dir,
        generated_at_utc=generated_at_utc,
    )
    run_intent_path = Path(str(dict(run_config_artifacts["run_intent"])["path"]))  # type: ignore[arg-type]
    run_effective_config_path = Path(str(dict(run_config_artifacts["run_effective_config"])["path"]))  # type: ignore[arg-type]

    stage_results: list[dict[str, object]] = []
    pipeline_started = time.time()

    _maybe_emit_freshness_guard_failure(
        args=args,
        root=root,
        run_config_path=run_config_path,
        run_intent_path=run_intent_path,
        run_effective_config_path=run_effective_config_path,
        oc_refresh_policy=oc_refresh_policy,
        effective_refresh_seed=effective_refresh_seed,
        stage_results=stage_results,
        output_dir=output_dir,
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        effective_continue_on_error=effective_continue_on_error,
        effective_verify_determinism=effective_verify_determinism,
        effective_verify_replay_count=effective_verify_replay_count,
        stage_order=stage_order,
        pipeline_started=pipeline_started,
        run_config_artifacts=run_config_artifacts,
        required_stable_artifacts=required_stable_artifacts,
    )

    _maybe_run_seed_refresh(
        args=args,
        root=root,
        run_config_path=run_config_path,
        run_intent_path=run_intent_path,
        run_effective_config_path=run_effective_config_path,
        stage_control_payloads=stage_control_payloads,
        effective_refresh_seed=effective_refresh_seed,
        stage_results=stage_results,
        effective_continue_on_error=effective_continue_on_error,
        output_dir=output_dir,
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        effective_verify_determinism=effective_verify_determinism,
        effective_verify_replay_count=effective_verify_replay_count,
        stage_order=stage_order,
        pipeline_started=pipeline_started,
        run_config_artifacts=run_config_artifacts,
        required_stable_artifacts=required_stable_artifacts,
    )

    execution_stage_order = _build_execution_stage_order(stage_order, refresh_seed=effective_refresh_seed)

    _run_execution_stages(
        args=args,
        root=root,
        run_config_path=run_config_path,
        run_intent_path=run_intent_path,
        run_effective_config_path=run_effective_config_path,
        execution_stage_order=execution_stage_order,
        stage_control_payloads=stage_control_payloads,
        stage_results=stage_results,
        effective_continue_on_error=effective_continue_on_error,
    )

    _maybe_run_determinism_verify(
        args=args,
        root=root,
        run_config_path=run_config_path,
        run_intent_path=run_intent_path,
        run_effective_config_path=run_effective_config_path,
        stage_results=stage_results,
        effective_verify_determinism=effective_verify_determinism,
        effective_verify_replay_count=effective_verify_replay_count,
    )

    summary, failed = emit_run_completion(
        output_dir=output_dir,
        summary_prefix=args.summary_prefix,
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        continue_on_error=effective_continue_on_error,
        python_executable=args.python,
        run_config_path=run_config_path,
        run_config_artifacts=run_config_artifacts,
        refresh_seed=effective_refresh_seed,
        verify_determinism=effective_verify_determinism,
        verify_determinism_replay_count=effective_verify_replay_count,
        stage_order=stage_order,
        stage_results=stage_results,
        pipeline_started=pipeline_started,
        root=root,
        required_stable_artifacts=required_stable_artifacts,
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
