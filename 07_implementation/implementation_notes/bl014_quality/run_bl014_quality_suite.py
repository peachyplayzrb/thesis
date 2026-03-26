#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.report_utils import write_csv_rows, write_json_ascii


REPO_ROOT = Path(__file__).resolve().parents[3]
QUALITY_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = QUALITY_DIR / "outputs"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relpath(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def add_check(checks: list[dict[str, str]], check_id: str, passed: bool, details: str) -> None:
    checks.append(
        {
            "id": check_id,
            "status": "pass" if passed else "fail",
            "details": details,
        }
    )


def run_python_script(script_path: Path) -> tuple[int, str]:
    process = subprocess.run(
        [sys.executable, str(script_path)],
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
    return {
        "bl010_snapshot": REPO_ROOT
        / "07_implementation"
        / "implementation_notes"
        / "bl010_reproducibility"
        / "outputs"
        / "bl010_reproducibility_config_snapshot.json",
        "bl010_report": REPO_ROOT
        / "07_implementation"
        / "implementation_notes"
        / "bl010_reproducibility"
        / "outputs"
        / "bl010_reproducibility_report.json",
        "bl011_snapshot": REPO_ROOT
        / "07_implementation"
        / "implementation_notes"
        / "bl011_controllability"
        / "outputs"
        / "bl011_controllability_config_snapshot.json",
        "bl011_report": REPO_ROOT
        / "07_implementation"
        / "implementation_notes"
        / "bl011_controllability"
        / "outputs"
        / "bl011_controllability_report.json",
    }


def ensure_paths_exist(paths: list[Path], *, label: str) -> None:
    missing = [relpath(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required {label}: {missing}")


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
        relpath(paths_bl011["active_seed_trace"]): bl011_module.sha256_of_file(paths_bl011["active_seed_trace"]),
        relpath(paths_bl011["active_candidates"]): bl011_module.sha256_of_file(paths_bl011["active_candidates"]),
    }

    optional_inputs = {
        "legacy_manifest": paths_bl011["legacy_manifest"],
        "legacy_coverage": paths_bl011["legacy_coverage"],
    }
    for path in optional_inputs.values():
        if path.exists():
            fixed_inputs[relpath(path)] = bl011_module.sha256_of_file(path)

    return {
        "task": "BL-011",
        "generated_from": relpath(paths_bl011["baseline_snapshot"]),
        "baseline_config_hash": baseline_config_hash,
        "input_source": "active_pipeline_outputs",
        "fixed_inputs": fixed_inputs,
        "optional_dependency_availability": {
            key: {
                "path": relpath(path),
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


def refresh_bl010_bl011_evidence() -> tuple[int, dict[str, str]]:
    """Refresh BL-010 and BL-011 evidence artifacts used by freshness checks."""
    bl010_script = (
        REPO_ROOT
        / "07_implementation"
        / "implementation_notes"
        / "bl010_reproducibility"
        / "run_bl010_reproducibility_check.py"
    )
    bl011_script = (
        REPO_ROOT
        / "07_implementation"
        / "implementation_notes"
        / "bl011_controllability"
        / "run_bl011_controllability_check.py"
    )
    bl010_return, bl010_output = run_python_script(bl010_script)
    if bl010_return != 0:
        return bl010_return, {
            "bl010_stdout_stderr": bl010_output,
            "bl011_stdout_stderr": "",
        }
    bl011_return, bl011_output = run_python_script(bl011_script)
    return bl011_return, {
        "bl010_stdout_stderr": bl010_output,
        "bl011_stdout_stderr": bl011_output,
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
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
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
        "bl010_reproducibility_check",
        REPO_ROOT / "07_implementation" / "implementation_notes" / "bl010_reproducibility" / "run_bl010_reproducibility_check.py",
    )
    bl011_module = load_module(
        "bl011_controllability_check",
        REPO_ROOT / "07_implementation" / "implementation_notes" / "bl011_controllability" / "run_bl011_controllability_check.py",
    )

    freshness_paths = freshness_input_paths()
    required_paths = [
        freshness_paths["bl010_snapshot"],
        freshness_paths["bl010_report"],
        freshness_paths["bl011_snapshot"],
        freshness_paths["bl011_report"],
    ]
    ensure_paths_exist(required_paths, label="freshness inputs")

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
            "bl010_config_snapshot": relpath(freshness_paths["bl010_snapshot"]),
            "bl010_report": relpath(freshness_paths["bl010_report"]),
            "bl011_config_snapshot": relpath(freshness_paths["bl011_snapshot"]),
            "bl011_report": relpath(freshness_paths["bl011_report"]),
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

    bl013_latest_path = (
        REPO_ROOT
        / "07_implementation"
        / "implementation_notes"
        / "bl013_entrypoint"
        / "outputs"
        / "bl013_orchestration_run_latest.json"
    )
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

    bl014_script = QUALITY_DIR / "run_bl014_sanity_checks.py"
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

    refresh_outputs: dict[str, str] = {}
    freshness_return = run_freshness_mode()
    freshness_refresh_attempted = False
    freshness_auto_refreshed = False
    if freshness_return != 0:
        freshness_refresh_attempted = True
        refresh_return, refresh_outputs = refresh_bl010_bl011_evidence()
        add_check(
            checks,
            "bl010_bl011_refresh_exit_zero",
            refresh_return == 0,
            f"BL-010/BL-011 evidence refresh return code={refresh_return}",
        )
        if refresh_return == 0:
            freshness_return = run_freshness_mode()
            freshness_auto_refreshed = True

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
            "bl013_latest_summary": relpath(bl013_latest_path),
            "bl014_report": relpath(bl014_report_path),
            "bl010_bl011_freshness_report": relpath(freshness_report_path),
        },
        checks=checks,
        report_path=report_path,
        matrix_path=matrix_path,
        script_outputs={
            "bl014_stdout_stderr": bl014_output,
            **refresh_outputs,
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
