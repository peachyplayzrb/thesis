#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    started = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, str]] = []

    bl013_latest_path = (
        REPO_ROOT
        / "07_implementation"
        / "implementation_notes"
        / "entrypoint"
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
        "BL-014 sanity check script exited with code 0",
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

    freshness_script = QUALITY_DIR / "check_bl010_bl011_freshness.py"
    freshness_return, freshness_output = run_python_script(freshness_script)
    add_check(
        checks,
        "bl010_bl011_freshness_exit_zero",
        freshness_return == 0,
        "BL-010/BL-011 freshness script exited with code 0",
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

    overall_status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    run_id = f"BL-FRESHNESS-SUITE-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"

    report = {
        "run_metadata": {
            "run_id": run_id,
            "task": "active freshness suite",
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "elapsed_seconds": round(time.time() - started, 3),
            "overall_status": overall_status,
            "checks_total": len(checks),
            "checks_passed": sum(1 for item in checks if item["status"] == "pass"),
            "checks_failed": sum(1 for item in checks if item["status"] == "fail"),
        },
        "evidence_paths": {
            "bl013_latest_summary": relpath(bl013_latest_path),
            "bl014_report": relpath(bl014_report_path),
            "bl010_bl011_freshness_report": relpath(freshness_report_path),
        },
        "script_outputs": {
            "bl014_stdout_stderr": bl014_output,
            "bl010_bl011_freshness_stdout_stderr": freshness_output,
        },
        "checks": checks,
    }

    matrix_rows = [
        {
            "check_id": item["id"],
            "status": item["status"],
            "details": item["details"],
        }
        for item in checks
    ]

    report_path = OUTPUT_DIR / "bl_active_freshness_suite_report.json"
    matrix_path = OUTPUT_DIR / "bl_active_freshness_suite_matrix.csv"
    write_json(report_path, report)
    write_csv(matrix_path, matrix_rows)

    print("Active freshness suite complete.")
    print(f"overall_status={overall_status}")
    print(f"report={report_path}")
    print(f"run_matrix={matrix_path}")

    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())