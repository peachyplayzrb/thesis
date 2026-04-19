"""Shared helpers for REB-M3 tranche gate scripts."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from shared_utils.io_utils import format_utc_iso
from shared_utils.io_utils import load_json as load_json_shared
from shared_utils.report_utils import write_csv_rows, write_json_ascii


def ensure_exists(path: Path) -> None:
    """Raise if a required artifact path is missing."""
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path}")


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON artifact as a mapping payload."""
    return load_json_shared(path)


def nested_get(data: dict[str, Any], keys: list[str]) -> Any:
    """Safely read a nested value from a dictionary by key path."""
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def finalize_gate_report(
    *,
    run_id: str,
    task: str,
    started: datetime,
    checks: list[dict[str, Any]],
    artifacts: dict[str, Path],
    output_dir: Path,
    report_filename: str,
    matrix_filename: str,
) -> int:
    """Write gate report + matrix and return shell exit code (0 pass, 1 fail)."""
    failed = [c for c in checks if c["status"] == "fail"]
    overall_status = "pass" if not failed else "fail"

    finished = datetime.now(UTC)
    report = {
        "run_id": run_id,
        "task": task,
        "generated_at_utc": format_utc_iso(finished),
        "elapsed_seconds": round((finished - started).total_seconds(), 3),
        "overall_status": overall_status,
        "total_checks": len(checks),
        "passed_checks": len(checks) - len(failed),
        "failed_checks": len(failed),
        "checks": checks,
        "artifacts_checked": {k: str(v) for k, v in artifacts.items()},
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / report_filename
    matrix_path = output_dir / matrix_filename

    write_json_ascii(report_path, report)
    write_csv_rows(
        matrix_path,
        [
            {
                "run_id": run_id,
                "check_id": item["id"],
                "status": item["status"],
                "details": item["details"],
            }
            for item in checks
        ],
    )

    print(f"[reb-m3-gate] status={overall_status} report={report_path}")
    return 0 if overall_status == "pass" else 1
