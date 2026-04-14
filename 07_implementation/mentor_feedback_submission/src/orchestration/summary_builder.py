"""Summary assembly and finalization helpers for BL-013 runs."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from shared_utils.hashing import sha256_of_file
from shared_utils.io_utils import load_json
from shared_utils.report_utils import write_json_ascii
from orchestration.stage_registry import STABLE_ARTIFACTS, SUMMARY_NOTES


def compute_stable_artifact_hashes(root: Path) -> tuple[dict[str, str], list[str]]:
    """Hash stable artifacts and report any expected files that are missing."""
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
    """Collect optional BL-006 and BL-007 diagnostics for run summaries."""
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
    stage_order: list[str],
    stage_results: list[dict[str, object]],
    elapsed_seconds: float,
    overall_status: str,
    failed_stage_count: int,
    stable_hashes: dict[str, str],
    missing_stable: list[str],
    stage_diagnostics: dict[str, object],
) -> dict[str, object]:
    """Build the canonical BL-013 summary payload."""
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
        "requested_stage_order": stage_order,
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
    """Write versioned and latest summary artifacts to disk."""
    summary_path = output_dir / f"{summary_prefix}_{run_id}.json"
    write_json_ascii(summary_path, summary)

    latest_path = output_dir / f"{summary_prefix}_latest.json"
    write_json_ascii(latest_path, summary)
    return summary_path, latest_path


def print_run_footer(*, overall_status: str, run_id: str, summary_path: Path, latest_path: Path) -> None:
    """Print a short run footer with status and artifact paths."""
    print(f"BL-013 orchestration complete: status={overall_status}")
    print(f"run_id={run_id}")
    print(f"summary={summary_path}")
    print(f"latest={latest_path}")


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
    stage_order: list[str],
    stage_results: list[dict[str, object]],
    pipeline_started: float,
    root: Path,
) -> tuple[dict[str, Any], Path, Path]:
    """Finalize one orchestration run and persist summary artifacts."""
    elapsed_pipeline = round(time.time() - pipeline_started, 3)
    failed = [item for item in stage_results if item["status"] == "fail"]
    expected_stage_count = len(stage_order) + (1 if refresh_seed else 0)
    overall_status = "pass" if not failed and len(stage_results) == expected_stage_count else "fail"

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
    stage_order: list[str],
    stage_results: list[dict[str, object]],
    pipeline_started: float,
    root: Path,
) -> None:
    """Emit failure summary artifacts, print context, and exit non-zero."""
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
    for item in failed:
        print(f"failed_stage={item['stage_id']} return_code={item['return_code']}")
    raise SystemExit(1)
