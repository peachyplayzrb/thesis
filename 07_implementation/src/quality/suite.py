#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from shared_utils.io_utils import load_json, utc_now
from shared_utils.report_utils import write_csv_rows, write_json_ascii
from shared_utils.path_utils import impl_root
from shared_utils.stage_utils import ensure_paths_exist, relpath as stage_relpath
from shared_utils.artifact_registry import (
    bl014_bl013_latest_summary_path,
    bl014_freshness_input_paths,
    bl014_pipeline_script_paths,
    bl014_refinement_diagnostic_paths,
)


REPO_ROOT = impl_root()
QUALITY_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = QUALITY_DIR / "outputs"


def add_check(checks: list[dict[str, str]], check_id: str, passed: bool, details: str) -> None:
    checks.append(
        {
            "id": check_id,
            "status": "pass" if passed else "fail",
            "details": details,
        }
    )


def run_python_script(script_path: Path, args: list[str] | None = None) -> tuple[int, str]:
    command = [sys.executable, str(script_path)]
    if args:
        command.extend(args)
    process = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    output = (process.stdout or "").strip()
    if process.stderr:
        output = f"{output}\n{process.stderr.strip()}".strip()
    return process.returncode, output


def freshness_input_paths() -> dict[str, Path]:
    return bl014_freshness_input_paths(REPO_ROOT)


def build_current_bl011_snapshot(
    bl011_module: Any,
    *,
    paths_bl011: dict[str, Path],
    current_bl010_snapshot: dict[str, Any],
) -> dict[str, Any]:
    baseline_config_hash = bl011_module.canonical_json_hash(current_bl010_snapshot)
    runtime_controls = bl011_module.resolve_bl011_runtime_controls()
    scenarios = bl011_module.build_scenarios(current_bl010_snapshot, runtime_controls)

    fixed_inputs = {
        stage_relpath(paths_bl011["active_seed_trace"], REPO_ROOT): bl011_module.sha256_of_file(paths_bl011["active_seed_trace"]),
        stage_relpath(paths_bl011["active_candidates"], REPO_ROOT): bl011_module.sha256_of_file(paths_bl011["active_candidates"]),
    }

    optional_inputs = {
        "legacy_manifest": paths_bl011["legacy_manifest"],
        "legacy_coverage": paths_bl011["legacy_coverage"],
    }
    for path in optional_inputs.values():
        if path.exists():
            fixed_inputs[stage_relpath(path, REPO_ROOT)] = bl011_module.sha256_of_file(path)

    return {
        "task": "BL-011",
        "generated_from": stage_relpath(paths_bl011["baseline_snapshot"], REPO_ROOT),
        "baseline_config_hash": baseline_config_hash,
        "input_source": "active_pipeline_outputs",
        "fixed_inputs": fixed_inputs,
        "optional_dependency_availability": {
            key: {
                "path": stage_relpath(path, REPO_ROOT),
                "available": path.exists(),
            }
            for key, path in optional_inputs.items()
        },
        "scenario_count": len(scenarios),
        "runtime_controls": {
            "config_source": runtime_controls["config_source"],
            "run_config_path": runtime_controls["run_config_path"],
            "weight_override_value_if_component_present": runtime_controls["weight_override_value_if_component_present"],
            "weight_override_increment_fallback": runtime_controls["weight_override_increment_fallback"],
            "weight_override_cap_fallback": runtime_controls["weight_override_cap_fallback"],
            "stricter_threshold_scale": runtime_controls["stricter_threshold_scale"],
            "looser_threshold_scale": runtime_controls["looser_threshold_scale"],
        },
        "scenarios": scenarios,
    }


def refresh_bl010_bl011_evidence() -> dict[str, Any]:
    """Refresh BL-010 and BL-011 evidence artifacts used by freshness checks."""
    script_paths = bl014_pipeline_script_paths(REPO_ROOT)
    bl010_script = script_paths["bl010_script"]
    bl011_script = script_paths["bl011_script"]
    bl013_script = script_paths["bl013_script"]
    bl013_latest_summary = bl014_bl013_latest_summary_path(REPO_ROOT)

    ensure_paths_exist([bl013_latest_summary], stage_label="BL-014", label="BL-013 latest summary", root=REPO_ROOT)
    bl013_latest = load_json(bl013_latest_summary)
    bl013_args: list[str] = []
    if bool(bl013_latest.get("refresh_seed")):
        bl013_args.append("--refresh-seed")
    run_config_path = bl013_latest.get("run_config_path")
    bl010_args: list[str] = []
    if run_config_path:
        bl010_args.extend(["--run-config", str(run_config_path)])
        bl013_args.extend(["--run-config", str(run_config_path)])

    bl010_return, bl010_output = run_python_script(bl010_script, args=bl010_args)
    if bl010_return != 0:
        return {
            "combined_return_code": bl010_return,
            "bl010_return_code": bl010_return,
            "bl013_return_code": None,
            "bl011_return_code": None,
            "bl013_post_bl011_return_code": None,
            "bl010_ran": True,
            "bl013_ran": False,
            "bl011_ran": False,
            "bl013_post_bl011_ran": False,
            "outputs": {
                "bl010_stdout_stderr": bl010_output,
                "bl013_stdout_stderr": "",
                "bl011_stdout_stderr": "",
                "bl013_post_bl011_stdout_stderr": "",
            },
        }

    bl013_return, bl013_output = run_python_script(bl013_script, args=bl013_args)
    if bl013_return != 0:
        return {
            "combined_return_code": bl013_return,
            "bl010_return_code": bl010_return,
            "bl013_return_code": bl013_return,
            "bl011_return_code": None,
            "bl013_post_bl011_return_code": None,
            "bl010_ran": True,
            "bl013_ran": True,
            "bl011_ran": False,
            "bl013_post_bl011_ran": False,
            "outputs": {
                "bl010_stdout_stderr": bl010_output,
                "bl013_stdout_stderr": bl013_output,
                "bl011_stdout_stderr": "",
                "bl013_post_bl011_stdout_stderr": "",
            },
        }

    bl011_return, bl011_output = run_python_script(bl011_script)
    if bl011_return != 0:
        return {
            "combined_return_code": bl011_return,
            "bl010_return_code": bl010_return,
            "bl013_return_code": bl013_return,
            "bl011_return_code": bl011_return,
            "bl013_post_bl011_return_code": None,
            "bl010_ran": True,
            "bl013_ran": True,
            "bl011_ran": True,
            "bl013_post_bl011_ran": False,
            "outputs": {
                "bl010_stdout_stderr": bl010_output,
                "bl013_stdout_stderr": bl013_output,
                "bl011_stdout_stderr": bl011_output,
                "bl013_post_bl011_stdout_stderr": "",
            },
        }

    bl013_post_return, bl013_post_output = run_python_script(bl013_script, args=bl013_args)
    return {
        "combined_return_code": bl013_post_return,
        "bl010_return_code": bl010_return,
        "bl013_return_code": bl013_return,
        "bl011_return_code": bl011_return,
        "bl013_post_bl011_return_code": bl013_post_return,
        "bl010_ran": True,
        "bl013_ran": True,
        "bl011_ran": True,
        "bl013_post_bl011_ran": True,
        "outputs": {
            "bl010_stdout_stderr": bl010_output,
            "bl013_stdout_stderr": bl013_output,
            "bl011_stdout_stderr": bl011_output,
            "bl013_post_bl011_stdout_stderr": bl013_post_output,
        },
    }


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_counts(checks: list[dict[str, str]]) -> tuple[int, int]:
    passed = sum(1 for item in checks if item["status"] == "pass")
    failed = len(checks) - passed
    return passed, failed


def write_suite_artifacts(
    *,
    run_id: str,
    task: str,
    elapsed_seconds: float,
    overall_status: str,
    evidence_paths: dict[str, str],
    checks: list[dict[str, str]],
    report_path: Path,
    matrix_path: Path,
    script_outputs: dict[str, str] | None = None,
    extra_sections: dict[str, Any] | None = None,
) -> None:
    checks_passed, checks_failed = check_counts(checks)
    report: dict[str, Any] = {
        "run_metadata": {
            "run_id": run_id,
            "task": task,
            "generated_at_utc": utc_now(),
            "elapsed_seconds": elapsed_seconds,
            "overall_status": overall_status,
            "checks_total": len(checks),
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
        },
        "evidence_paths": evidence_paths,
        "checks": checks,
    }
    if script_outputs:
        report["script_outputs"] = script_outputs
    if extra_sections:
        report.update(extra_sections)

    matrix_rows = [{"check_id": item["id"], "status": item["status"], "details": item["details"]} for item in checks]
    write_json_ascii(report_path, report)
    write_csv_rows(matrix_path, matrix_rows)


def run_freshness_mode() -> int:
    started = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, str]] = []

    bl010_module = load_module(
        "reproducibility_check",
        REPO_ROOT / "reproducibility" / "main.py",
    )
    bl011_module = load_module(
        "controllability_check",
        REPO_ROOT / "controllability" / "main.py",
    )

    freshness_paths = freshness_input_paths()
    required_paths = [
        freshness_paths["bl010_snapshot"],
        freshness_paths["bl010_report"],
        freshness_paths["bl011_snapshot"],
        freshness_paths["bl011_report"],
    ]
    ensure_paths_exist(required_paths, stage_label="BL-014", label="freshness inputs", root=REPO_ROOT)

    stored_bl010_snapshot = load_json(freshness_paths["bl010_snapshot"])
    stored_bl010_report = load_json(freshness_paths["bl010_report"])
    stored_bl011_snapshot = load_json(freshness_paths["bl011_snapshot"])
    stored_bl011_report = load_json(freshness_paths["bl011_report"])

    paths_bl010 = bl010_module.build_paths(REPO_ROOT)
    bl010_module.ensure_required_inputs(paths_bl010, REPO_ROOT)
    current_bl010_snapshot = bl010_module.build_config_snapshot(
        paths_bl010,
        REPO_ROOT,
    )
    current_bl010_hash = bl010_module.canonical_json_hash(current_bl010_snapshot)
    stored_bl010_snapshot_hash = bl010_module.canonical_json_hash(stored_bl010_snapshot)

    paths_bl011 = bl011_module.build_paths(REPO_ROOT)
    bl011_module.ensure_required_inputs(paths_bl011, REPO_ROOT)
    current_bl011_snapshot = build_current_bl011_snapshot(
        bl011_module,
        paths_bl011=paths_bl011,
        current_bl010_snapshot=current_bl010_snapshot,
    )
    current_bl011_hash = bl011_module.canonical_json_hash(current_bl011_snapshot)
    stored_bl011_snapshot_hash = bl011_module.canonical_json_hash(stored_bl011_snapshot)

    add_check(
        checks,
        "bl010_snapshot_matches_current_contract",
        stored_bl010_snapshot_hash == current_bl010_hash,
        "BL-010 config snapshot matches the current active-pipeline reproducibility contract",
    )
    add_check(
        checks,
        "bl010_report_hash_matches_current_contract",
        str(stored_bl010_report["run_metadata"]["config_hash"]) == current_bl010_hash,
        "BL-010 report config_hash matches the current active-pipeline reproducibility contract",
    )
    add_check(
        checks,
        "bl010_fixed_input_hashes_match_current",
        stored_bl010_report["inputs"]["fixed_input_hashes"] == current_bl010_snapshot["fixed_inputs"],
        "BL-010 fixed input hashes match the current active pipeline outputs",
    )
    add_check(
        checks,
        "bl010_stage_script_hashes_match_current",
        stored_bl010_report["inputs"]["stage_scripts"] == current_bl010_snapshot["stage_scripts"],
        "BL-010 stage script hashes match the current BL-004 to BL-009 code",
    )
    add_check(
        checks,
        "bl010_active_mode",
        str(stored_bl010_report["run_metadata"]["fixed_input_source"]) == "active_pipeline_outputs",
        "BL-010 evidence mode matches requested freshness mode input source",
    )
    add_check(
        checks,
        "bl011_snapshot_matches_current_contract",
        stored_bl011_snapshot_hash == current_bl011_hash,
        "BL-011 config snapshot matches the current active controllability contract",
    )
    add_check(
        checks,
        "bl011_baseline_hash_matches_current_bl010",
        str(stored_bl011_report["run_metadata"]["baseline_config_hash"]) == current_bl010_hash,
        "BL-011 baseline_config_hash matches the current BL-010 baseline snapshot",
    )
    add_check(
        checks,
        "bl011_fixed_input_hashes_match_current",
        stored_bl011_report["inputs"]["fixed_input_hashes"] == current_bl011_snapshot["fixed_inputs"],
        "BL-011 fixed input hashes match the current active controllability inputs",
    )
    add_check(
        checks,
        "bl011_active_mode",
        str(stored_bl011_snapshot["input_source"]) == "active_pipeline_outputs",
        "BL-011 evidence mode matches requested freshness mode input source",
    )

    overall_status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    report_path = OUTPUT_DIR / "bl010_bl011_freshness_report.json"
    matrix_path = OUTPUT_DIR / "bl010_bl011_freshness_matrix.csv"
    write_suite_artifacts(
        run_id=f"BL-FRESHNESS-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}",
        task="BL-010/011 freshness check",
        elapsed_seconds=round(time.time() - started, 3),
        overall_status=overall_status,
        evidence_paths={
            "bl010_config_snapshot": stage_relpath(freshness_paths["bl010_snapshot"], REPO_ROOT),
            "bl010_report": stage_relpath(freshness_paths["bl010_report"], REPO_ROOT),
            "bl011_config_snapshot": stage_relpath(freshness_paths["bl011_snapshot"], REPO_ROOT),
            "bl011_report": stage_relpath(freshness_paths["bl011_report"], REPO_ROOT),
            "bl010_config_hash": current_bl010_hash,
            "bl011_config_hash": current_bl011_hash,
        },
        checks=checks,
        report_path=report_path,
        matrix_path=matrix_path,
        extra_sections={
            "current_contract_hashes": {
                "bl010_config_hash": current_bl010_hash,
                "bl011_config_hash": current_bl011_hash,
            }
        },
    )

    print("BL-010/BL-011 freshness check complete.")
    print(f"overall_status={overall_status}")
    print(f"report={report_path}")
    print(f"run_matrix={matrix_path}")
    return 0 if overall_status == "pass" else 1


def run_active_mode() -> int:
    started = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, str]] = []

    bl013_latest_path = bl014_bl013_latest_summary_path(REPO_ROOT)
    if not bl013_latest_path.exists():
        raise FileNotFoundError(f"Missing BL-013 latest summary: {bl013_latest_path}")
    bl013_latest = load_json(bl013_latest_path)

    add_check(
        checks,
        "bl013_latest_pass",
        str(bl013_latest.get("overall_status")) == "pass",
        "BL-013 latest orchestration summary reports overall_status=pass",
    )
    add_check(
        checks,
        "bl013_latest_no_failed_stages",
        int(bl013_latest.get("failed_stage_count", -1)) == 0,
        "BL-013 latest orchestration summary reports failed_stage_count=0",
    )

    bl014_script = QUALITY_DIR / "sanity_checks.py"
    bl014_return, bl014_output = run_python_script(bl014_script)
    add_check(
        checks,
        "bl014_script_exit_zero",
        bl014_return == 0,
        f"BL-014 sanity check script return code={bl014_return}",
    )

    bl014_report_path = OUTPUT_DIR / "bl014_sanity_report.json"
    if not bl014_report_path.exists():
        raise FileNotFoundError(f"Missing BL-014 report: {bl014_report_path}")
    bl014_report = load_json(bl014_report_path)
    add_check(
        checks,
        "bl014_report_pass",
        str(bl014_report.get("overall_status")) == "pass",
        "BL-014 report overall_status is pass",
    )

    refinement_paths = bl014_refinement_diagnostic_paths(REPO_ROOT)
    bl006_distribution_path = refinement_paths["bl006_distribution"]
    bl007_report_path = refinement_paths["bl007_assembly_report"]

    add_check(
        checks,
        "bl006_distribution_diagnostics_available",
        bl006_distribution_path.exists(),
        f"BL-006 distribution diagnostics present at {stage_relpath(bl006_distribution_path, REPO_ROOT)}",
    )
    add_check(
        checks,
        "bl007_assembly_pressure_diagnostics_available",
        bl007_report_path.exists(),
        f"BL-007 assembly report present at {stage_relpath(bl007_report_path, REPO_ROOT)}",
    )

    if bl006_distribution_path.exists():
        bl006_distribution = load_json(bl006_distribution_path)
        rank_cliff = bl006_distribution.get("rank_cliff", {})
        add_check(
            checks,
            "bl006_rank_cliff_advisory",
            True,
            (
                "BL-006 rank-cliff advisory: "
                f"detected={bool(rank_cliff.get('detected', False))}, "
                f"rank_2_to_3_gap={rank_cliff.get('rank_2_to_3_gap', 0.0)}"
            ),
        )

    if bl007_report_path.exists():
        bl007_report = load_json(bl007_report_path)
        rank_diag = bl007_report.get("rank_continuity_diagnostics", {})
        pressure_diag = bl007_report.get("assembly_pressure_diagnostics", {})
        add_check(
            checks,
            "bl007_rank_continuity_advisory",
            True,
            (
                "BL-007 rank continuity advisory: "
                f"max_selected_rank={rank_diag.get('max_selected_rank')}, "
                f"rank_2_to_3_score_gap={rank_diag.get('rank_2_to_3_score_gap')}"
            ),
        )
        add_check(
            checks,
            "bl007_assembly_pressure_advisory",
            True,
            (
                "BL-007 assembly pressure advisory: "
                f"top_100_excluded={pressure_diag.get('top_100_excluded')}, "
                f"dominant_reason={pressure_diag.get('dominant_top_100_exclusion_reason')}"
            ),
        )

    refresh_outputs: dict[str, str] = {}
    freshness_initial_return = run_freshness_mode()
    freshness_return = freshness_initial_return
    freshness_post_refresh_return: int | None = None
    freshness_refresh_attempted = False
    freshness_auto_refreshed = False
    refresh_result: dict[str, Any] | None = None

    if freshness_initial_return != 0:
        freshness_refresh_attempted = True
        refresh_result = refresh_bl010_bl011_evidence()
        refresh_return = int(refresh_result["combined_return_code"])
        refresh_outputs = dict(refresh_result["outputs"])

        add_check(
            checks,
            "bl010_refresh_exit_zero",
            int(refresh_result["bl010_return_code"]) == 0,
            f"BL-010 evidence refresh return code={refresh_result['bl010_return_code']}",
        )
        bl013_ran = bool(refresh_result["bl013_ran"])
        bl013_return = refresh_result["bl013_return_code"]
        add_check(
            checks,
            "bl013_refresh_exit_zero",
            bl013_ran and int(bl013_return) == 0,
            (
                f"BL-013 pipeline reapply return code={bl013_return}"
                if bl013_ran
                else "BL-013 pipeline reapply was skipped because BL-010 refresh failed"
            ),
        )
        bl011_ran = bool(refresh_result["bl011_ran"])
        bl011_return = refresh_result["bl011_return_code"]
        add_check(
            checks,
            "bl011_refresh_exit_zero",
            bl011_ran and int(bl011_return) == 0,
            (
                f"BL-011 evidence refresh return code={bl011_return}"
                if bl011_ran
                else "BL-011 evidence refresh was skipped because BL-010 refresh failed"
            ),
        )
        bl013_post_ran = bool(refresh_result["bl013_post_bl011_ran"])
        bl013_post_return = refresh_result["bl013_post_bl011_return_code"]
        add_check(
            checks,
            "bl013_post_bl011_refresh_exit_zero",
            bl013_post_ran and int(bl013_post_return) == 0,
            (
                f"BL-013 post-BL-011 pipeline reapply return code={bl013_post_return}"
                if bl013_post_ran
                else "BL-013 post-BL-011 pipeline reapply was skipped because BL-011 refresh failed"
            ),
        )

        add_check(
            checks,
            "bl010_bl011_refresh_exit_zero",
            refresh_return == 0,
            f"BL-010/BL-011 evidence refresh return code={refresh_return}",
        )
        if refresh_return == 0:
            freshness_return = run_freshness_mode()
            freshness_post_refresh_return = freshness_return
            freshness_auto_refreshed = freshness_return == 0

    add_check(
        checks,
        "bl010_bl011_stale_detected",
        freshness_initial_return != 0,
        (
            "BL-010/BL-011 freshness was stale before active-suite checks"
            if freshness_initial_return != 0
            else "BL-010/BL-011 freshness was already up-to-date before active-suite checks"
        ),
    )

    add_check(
        checks,
        "bl010_bl011_freshness_exit_zero",
        freshness_return == 0,
        f"BL-010/BL-011 freshness script return code={freshness_return}",
    )

    freshness_report_path = OUTPUT_DIR / "bl010_bl011_freshness_report.json"
    if not freshness_report_path.exists():
        raise FileNotFoundError(f"Missing BL-010/011 freshness report: {freshness_report_path}")
    freshness_report = load_json(freshness_report_path)
    add_check(
        checks,
        "bl010_bl011_freshness_report_pass",
        str(freshness_report.get("run_metadata", {}).get("overall_status")) == "pass",
        "BL-010/BL-011 freshness report overall_status is pass",
    )
    add_check(
        checks,
        "bl010_bl011_freshness_auto_refresh",
        (not freshness_refresh_attempted) or freshness_auto_refreshed,
        "BL-010/BL-011 freshness auto-refresh succeeded"
        if freshness_auto_refreshed
        else (
            "BL-010/BL-011 freshness auto-refresh was attempted but failed"
            if freshness_refresh_attempted
            else "BL-010/BL-011 freshness auto-refresh was not needed"
        ),
    )

    if freshness_refresh_attempted:
        add_check(
            checks,
            "bl010_bl011_freshness_post_refresh_exit_zero",
            freshness_post_refresh_return == 0,
            f"BL-010/BL-011 post-refresh freshness return code={freshness_post_refresh_return}",
        )

    overall_status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    run_id = f"BL-FRESHNESS-SUITE-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"

    report_path = OUTPUT_DIR / "bl_active_freshness_suite_report.json"
    matrix_path = OUTPUT_DIR / "bl_active_freshness_suite_matrix.csv"
    write_suite_artifacts(
        run_id=run_id,
        task="active freshness suite",
        elapsed_seconds=round(time.time() - started, 3),
        overall_status=overall_status,
        evidence_paths={
            "bl013_latest_summary": stage_relpath(bl013_latest_path, REPO_ROOT),
            "bl014_report": stage_relpath(bl014_report_path, REPO_ROOT),
            "bl010_bl011_freshness_report": stage_relpath(freshness_report_path, REPO_ROOT),
        },
        checks=checks,
        report_path=report_path,
        matrix_path=matrix_path,
        script_outputs={
            "bl014_stdout_stderr": bl014_output,
            **refresh_outputs,
        },
        extra_sections={
            "freshness_execution": {
                "initial_freshness_return_code": freshness_initial_return,
                "stale_detected": freshness_initial_return != 0,
                "refresh_attempted": freshness_refresh_attempted,
                "refresh_auto_recovered": freshness_auto_refreshed,
                "post_refresh_freshness_return_code": freshness_post_refresh_return,
                "refresh_stage_results": {
                    "bl010_return_code": None if refresh_result is None else refresh_result["bl010_return_code"],
                    "bl011_return_code": None if refresh_result is None else refresh_result["bl011_return_code"],
                    "combined_return_code": None if refresh_result is None else refresh_result["combined_return_code"],
                },
            }
        },
    )

    print("Active freshness suite complete.")
    print(f"overall_status={overall_status}")
    print(f"report={report_path}")
    print(f"run_matrix={matrix_path}")

    return 0 if overall_status == "pass" else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BL-014 consolidated quality runner")
    parser.add_argument(
        "--mode",
        choices=["freshness", "active"],
        default="active",
        help="Run BL-010/011 freshness only, or full active suite",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "freshness":
        return run_freshness_mode()
    return run_active_mode()


if __name__ == "__main__":
    raise SystemExit(main())
