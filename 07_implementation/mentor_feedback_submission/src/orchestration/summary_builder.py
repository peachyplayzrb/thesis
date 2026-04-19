"""Run summary assembly, artifact hashing, and finalization for BL-013."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from orchestration.stage_registry import STABLE_ARTIFACTS, SUMMARY_NOTES
from shared_utils.hashing import sha256_of_file
from shared_utils.io_utils import load_json
from shared_utils.report_utils import write_json_ascii


def _build_stage_execution_metadata(
    *,
    requested_stage_order: list[str],
    stage_results: list[dict[str, object]],
) -> dict[str, object]:
    executed_stage_sequence = [str(item.get("stage_id", "")) for item in stage_results]
    requested_stage_set = set(requested_stage_order)

    requested_stage_execution_sequence = [
        stage_id
        for stage_id in executed_stage_sequence
        if stage_id in requested_stage_set
    ]

    requested_stages_executed = set(requested_stage_execution_sequence)
    requested_stages_not_executed = [
        stage_id
        for stage_id in requested_stage_order
        if stage_id not in requested_stages_executed
    ]

    executed_non_requested_stages = [
        stage_id
        for stage_id in executed_stage_sequence
        if stage_id not in requested_stage_set
    ]

    requested_stage_execution_counts: dict[str, int] = {}
    for stage_id in requested_stage_execution_sequence:
        requested_stage_execution_counts[stage_id] = requested_stage_execution_counts.get(stage_id, 0) + 1

    duplicate_requested_stage_executions = {
        stage_id: count
        for stage_id, count in requested_stage_execution_counts.items()
        if count > 1
    }

    return {
        "requested_stage_order": requested_stage_order,
        "executed_stage_sequence": executed_stage_sequence,
        "requested_stage_execution_sequence": requested_stage_execution_sequence,
        "requested_stages_not_executed": requested_stages_not_executed,
        "executed_non_requested_stages": executed_non_requested_stages,
        "duplicate_requested_stage_executions": duplicate_requested_stage_executions,
    }


def compute_stable_artifact_hashes(root: Path) -> tuple[dict[str, str], list[str]]:
    hashes: dict[str, str] = {}
    missing: list[str] = []

    for alias, relative_path in STABLE_ARTIFACTS.items():
        artifact_path = root / relative_path
        if not artifact_path.exists():
            missing.append(relative_path)
            continue
        hashes[alias] = sha256_of_file(artifact_path, uppercase=True)

    return hashes, missing


def collect_refinement_diagnostics(root: Path) -> dict[str, object]:
    diagnostics: dict[str, object] = {
        "bl006_distribution": {"available": False},
        "bl007_assembly_pressure": {"available": False},
    }

    bl006_distribution_path = (
        root
        / "scoring"
        / "outputs"
        / "bl006_score_distribution_diagnostics.json"
    )
    if bl006_distribution_path.exists():
        bl006_distribution = load_json(bl006_distribution_path)
        diagnostics["bl006_distribution"] = {
            "available": True,
            "path": bl006_distribution_path.relative_to(root).as_posix(),
            "rank_cliff": bl006_distribution.get("rank_cliff", {}),
        }

    bl007_report_path = (
        root
        / "playlist"
        / "outputs"
        / "bl007_assembly_report.json"
    )
    if bl007_report_path.exists():
        bl007_report = load_json(bl007_report_path)
        diagnostics["bl007_assembly_pressure"] = {
            "available": True,
            "path": bl007_report_path.relative_to(root).as_posix(),
            "rank_continuity_diagnostics": bl007_report.get("rank_continuity_diagnostics", {}),
            "assembly_pressure_diagnostics": bl007_report.get("assembly_pressure_diagnostics", {}),
        }

    return diagnostics


def build_summary(
    *,
    run_id: str,
    generated_at_utc: str,
    continue_on_error: bool,
    python_executable: str,
    run_config_path: Path | None,
    run_config_artifacts: dict[str, object],
    refresh_seed: bool,
    verify_determinism: bool,
    verify_determinism_replay_count: int,
    stage_order: list[str],
    stage_results: list[dict[str, object]],
    elapsed_seconds: float,
    overall_status: str,
    failed_stage_count: int,
    stable_hashes: dict[str, str],
    missing_stable: list[str],
    stage_diagnostics: dict[str, object],
) -> dict[str, object]:
    stage_execution = _build_stage_execution_metadata(
        requested_stage_order=stage_order,
        stage_results=stage_results,
    )

    return {
        "run_id": run_id,
        "task": "BL-013",
        "generated_at_utc": generated_at_utc,
        "overall_status": overall_status,
        "continue_on_error": continue_on_error,
        "python_executable": python_executable,
        "run_config_path": str(run_config_path) if run_config_path else None,
        "canonical_run_config_artifacts": run_config_artifacts,
        "refresh_seed": refresh_seed,
        "verify_determinism": verify_determinism,
        "verify_determinism_replay_count": verify_determinism_replay_count,
        "requested_stage_order": stage_order,
        "stage_execution": stage_execution,
        "executed_stage_count": len(stage_results),
        "failed_stage_count": failed_stage_count,
        "elapsed_seconds": elapsed_seconds,
        "stage_results": stage_results,
        "stage_diagnostics": stage_diagnostics,
        "stable_artifact_hashes": stable_hashes,
        "missing_stable_artifacts": missing_stable,
        "notes": SUMMARY_NOTES,
    }


def write_summary_artifacts(
    *,
    output_dir: Path,
    summary_prefix: str,
    run_id: str,
    summary: dict[str, object],
) -> tuple[Path, Path]:
    summary_path = output_dir / f"{summary_prefix}_{run_id}.json"
    write_json_ascii(summary_path, summary)

    latest_path = output_dir / f"{summary_prefix}_latest.json"
    write_json_ascii(latest_path, summary)
    return summary_path, latest_path


def print_run_footer(*, overall_status: str, run_id: str, summary_path: Path, latest_path: Path) -> None:
    print(f"BL-013 orchestration complete: status={overall_status}")
    print(f"run_id={run_id}")
    print(f"summary={summary_path}")
    print(f"latest={latest_path}")


def _emit_failed_stage_lines(stage_results: list[dict[str, object]]) -> list[dict[str, object]]:
    failed = [item for item in stage_results if item["status"] == "fail"]
    for item in failed:
        print(f"failed_stage={item['stage_id']} return_code={item['return_code']}")
    return failed


def finalize_run(
    *,
    output_dir: Path,
    summary_prefix: str,
    run_id: str,
    generated_at_utc: str,
    continue_on_error: bool,
    python_executable: str,
    run_config_path: Path | None,
    run_config_artifacts: dict[str, object],
    refresh_seed: bool,
    verify_determinism: bool,
    verify_determinism_replay_count: int,
    stage_order: list[str],
    stage_results: list[dict[str, object]],
    pipeline_started: float,
    root: Path,
) -> tuple[dict[str, Any], Path, Path]:
    elapsed_pipeline = round(time.time() - pipeline_started, 3)
    failed = [item for item in stage_results if item["status"] == "fail"]
    overall_status = "pass" if not failed else "fail"

    stable_hashes, missing_stable = compute_stable_artifact_hashes(root)
    stage_diagnostics = collect_refinement_diagnostics(root)
    summary = build_summary(
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        continue_on_error=continue_on_error,
        python_executable=python_executable,
        run_config_path=run_config_path,
        run_config_artifacts=run_config_artifacts,
        refresh_seed=refresh_seed,
        verify_determinism=verify_determinism,
        verify_determinism_replay_count=verify_determinism_replay_count,
        stage_order=stage_order,
        stage_results=stage_results,
        elapsed_seconds=elapsed_pipeline,
        overall_status=overall_status,
        failed_stage_count=len(failed),
        stable_hashes=stable_hashes,
        missing_stable=missing_stable,
        stage_diagnostics=stage_diagnostics,
    )

    summary_path, latest_path = write_summary_artifacts(
        output_dir=output_dir,
        summary_prefix=summary_prefix,
        run_id=run_id,
        summary=summary,
    )
    return summary, summary_path, latest_path


def emit_and_exit_failure(
    *,
    output_dir: Path,
    summary_prefix: str,
    run_id: str,
    generated_at_utc: str,
    continue_on_error: bool,
    python_executable: str,
    run_config_path: Path | None,
    run_config_artifacts: dict[str, object],
    refresh_seed: bool,
    verify_determinism: bool,
    verify_determinism_replay_count: int,
    stage_order: list[str],
    stage_results: list[dict[str, object]],
    pipeline_started: float,
    root: Path,
) -> None:
    _, failed = emit_run_completion(
        output_dir=output_dir,
        summary_prefix=summary_prefix,
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        continue_on_error=continue_on_error,
        python_executable=python_executable,
        run_config_path=run_config_path,
        run_config_artifacts=run_config_artifacts,
        refresh_seed=refresh_seed,
        verify_determinism=verify_determinism,
        verify_determinism_replay_count=verify_determinism_replay_count,
        stage_order=stage_order,
        stage_results=stage_results,
        pipeline_started=pipeline_started,
        root=root,
    )
    if not failed:
        raise SystemExit(1)
    raise SystemExit(1)


def emit_run_completion(
    *,
    output_dir: Path,
    summary_prefix: str,
    run_id: str,
    generated_at_utc: str,
    continue_on_error: bool,
    python_executable: str,
    run_config_path: Path | None,
    run_config_artifacts: dict[str, object],
    refresh_seed: bool,
    verify_determinism: bool,
    verify_determinism_replay_count: int,
    stage_order: list[str],
    stage_results: list[dict[str, object]],
    pipeline_started: float,
    root: Path,
) -> tuple[dict[str, Any], list[dict[str, object]]]:
    summary, summary_path, latest_path = finalize_run(
        output_dir=output_dir,
        summary_prefix=summary_prefix,
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        continue_on_error=continue_on_error,
        python_executable=python_executable,
        run_config_path=run_config_path,
        run_config_artifacts=run_config_artifacts,
        refresh_seed=refresh_seed,
        verify_determinism=verify_determinism,
        verify_determinism_replay_count=verify_determinism_replay_count,
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
    failed = _emit_failed_stage_lines(stage_results)
    return summary, failed
