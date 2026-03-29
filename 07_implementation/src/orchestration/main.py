from __future__ import annotations

import importlib.util
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared_utils.io_utils import utc_now
from shared_utils.path_utils import impl_root
from orchestration.stage_registry import BL003_SCRIPT, DEFAULT_STAGE_ORDER, STAGE_SCRIPT_MAP
from orchestration.cli import parse_args, validate_stage_order
from orchestration.seed_freshness import validate_bl003_seed_freshness
from orchestration.stage_runner import build_missing_script_result, run_bl003_seed_refresh, run_stage
from orchestration.summary_builder import emit_and_exit_failure, finalize_run, print_run_footer


def load_run_config_utils_module(root: Path):
    module_path = (
        root
        / "run_config"
        / "run_config_utils.py"
    )
    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def emit_run_config_artifact_pair(
    root: Path,
    run_id: str,
    run_config_path: Path | None,
    artifact_dir: Path,
    generated_at_utc: str,
) -> dict[str, object]:
    run_config_utils = load_run_config_utils_module(root)
    return run_config_utils.write_run_config_artifact_pair(
        run_id=run_id,
        output_dir=artifact_dir,
        run_config_path=run_config_path,
        generated_at_utc=generated_at_utc,
    )




def _resolve_oc(run_config_path: Path | None, root: Path) -> dict[str, Any]:
    """Load orchestration_controls from run-config, merged with defaults."""
    run_config_utils = load_run_config_utils_module(root)
    return run_config_utils.resolve_bl013_orchestration_controls(
        str(run_config_path) if run_config_path else None
    )


def main() -> None:
    args = parse_args()
    root = impl_root()

    # Resolve run_config_path first — needed for orchestration_controls lookup.
    run_config_path = (root / args.run_config).resolve() if args.run_config else None
    if run_config_path is not None and not run_config_path.exists():
        raise FileNotFoundError(f"Run config file not found: {run_config_path}")

    # Load orchestration_controls from run-config (merged with defaults).
    oc = _resolve_oc(run_config_path, root)
    oc_stage_order: list[str] | None = oc.get("stage_order")  # type: ignore[assignment]
    oc_continue: bool = bool(oc.get("continue_on_error", False))
    oc_refresh_policy: str = str(oc.get("refresh_seed_policy") or "auto_if_stale")

    # Priority: explicit CLI arg > run-config orchestration_controls > system default.
    if args.stages is not None:
        stage_order = validate_stage_order(args.stages)
    elif oc_stage_order:
        stage_order = validate_stage_order(oc_stage_order)
    else:
        stage_order = list(DEFAULT_STAGE_ORDER)

    effective_continue_on_error: bool = bool(args.continue_on_error) or oc_continue

    if oc_refresh_policy == "always":
        effective_refresh_seed = True
    elif oc_refresh_policy == "never":
        effective_refresh_seed = False
    else:  # "auto_if_stale" or any unknown value
        effective_refresh_seed = bool(args.refresh_seed)

    output_dir = root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    run_id = f"BL013-ENTRYPOINT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    generated_at_utc = utc_now()
    run_config_artifact_dir = (root / args.run_config_artifact_dir).resolve()
    run_config_artifacts = emit_run_config_artifact_pair(
        root=root,
        run_id=run_id,
        run_config_path=run_config_path,
        artifact_dir=run_config_artifact_dir,
        generated_at_utc=generated_at_utc,
    )
    run_intent_path = Path(str(dict(run_config_artifacts["run_intent"])["path"]))  # type: ignore[arg-type]
    run_effective_config_path = Path(str(dict(run_config_artifacts["run_effective_config"])["path"]))  # type: ignore[arg-type]

    stage_results: list[dict[str, object]] = []
    pipeline_started = time.time()

    # Freshness guard: skipped entirely when policy is "never" or we are already refreshing.
    if oc_refresh_policy != "never" and run_config_path is not None and not effective_refresh_seed:
        is_fresh, reason = validate_bl003_seed_freshness(
            root=root,
            run_config_path=run_config_path,
            run_effective_config_path=run_effective_config_path,
        )
        if not is_fresh:
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
                stage_order=stage_order,
                stage_results=stage_results,
                pipeline_started=pipeline_started,
                root=root,
            )

    if effective_refresh_seed:
        seed_result = run_bl003_seed_refresh(
            args.python,
            root,
            run_config_path,
            run_intent_path,
            run_effective_config_path,
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
                stage_order=stage_order,
                stage_results=stage_results,
                pipeline_started=pipeline_started,
                root=root,
            )

    for stage_id in stage_order:
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
        )
        stage_results.append(result)

        if result["status"] == "fail" and not effective_continue_on_error:
            break

    summary, summary_path, latest_path = finalize_run(
        output_dir=output_dir,
        summary_prefix=args.summary_prefix,
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        continue_on_error=effective_continue_on_error,
        python_executable=args.python,
        run_config_path=run_config_path,
        run_config_artifacts=run_config_artifacts,
        refresh_seed=effective_refresh_seed,
        stage_order=stage_order,
        stage_results=stage_results,
        pipeline_started=pipeline_started,
        root=root,
    )

    print_run_footer(
        overall_status=str(summary["overall_status"]),
        run_id=run_id,
        summary_path=summary_path,
        latest_path=latest_path,
    )

    failed = [item for item in stage_results if item["status"] == "fail"]
    if failed:
        for item in failed:
            print(f"failed_stage={item['stage_id']} return_code={item['return_code']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
