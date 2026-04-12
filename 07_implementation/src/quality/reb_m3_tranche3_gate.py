#!/usr/bin/env python3
"""REB-M3 tranche-3 gate checks for control-causality hardening.

This script validates that tranche-3 contracts are present in active artifacts:
- BL-008 explanations include control provenance snapshots
- BL-009 observability includes explicit validity boundaries
- BL-011 controllability reports no-op control diagnostics

Outputs are written to:
- quality/outputs/reb_m3_tranche3_gate_report.json
- quality/outputs/reb_m3_tranche3_gate_matrix.csv
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from shared_utils.io_utils import format_utc_iso
from shared_utils.io_utils import load_json as load_json_shared
from shared_utils.path_utils import impl_root
from shared_utils.report_utils import write_csv_rows, write_json_ascii


REPO_ROOT = impl_root()
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path}")


def load_json(path: Path) -> dict[str, Any]:
    return load_json_shared(path)


def _nested_get(data: dict[str, Any], keys: list[str]) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def main() -> int:
    started = datetime.now(UTC)
    run_id = f"REB-M3-TRANCHE3-GATE-{started.strftime('%Y%m%d-%H%M%S-%f')}"

    artifacts = {
        "bl008_payloads": REPO_ROOT / "transparency/outputs/bl008_explanation_payloads.json",
        "bl009_log": REPO_ROOT / "observability/outputs/bl009_run_observability_log.json",
        "bl011_report": REPO_ROOT / "controllability/outputs/controllability_report.json",
    }
    for artifact_path in artifacts.values():
        ensure_exists(artifact_path)

    bl008_payloads = load_json(artifacts["bl008_payloads"])
    bl009_log = load_json(artifacts["bl009_log"])
    bl011_report = load_json(artifacts["bl011_report"])

    checks: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, details: str) -> None:
        checks.append(
            {
                "id": check_id,
                "status": "pass" if passed else "fail",
                "details": details,
            }
        )

    explanations = bl008_payloads.get("explanations")
    first_explanation = explanations[0] if isinstance(explanations, list) and explanations else {}

    check(
        "t3_bl008_control_provenance_present",
        isinstance(_nested_get(first_explanation, ["control_provenance"]), dict),
        "BL-008 explanations include control_provenance block",
    )
    check(
        "t3_bl008_scoring_control_snapshot_present",
        isinstance(_nested_get(first_explanation, ["control_provenance", "scoring", "active_component_weights"]), dict)
        and isinstance(_nested_get(first_explanation, ["control_provenance", "scoring", "lead_genre_strategy"]), str)
        and isinstance(_nested_get(first_explanation, ["control_provenance", "scoring", "semantic_overlap_strategy"]), str),
        "BL-008 control provenance includes scoring control snapshot",
    )
    check(
        "t3_bl008_transparency_control_snapshot_present",
        isinstance(_nested_get(first_explanation, ["control_provenance", "transparency", "top_contributor_limit"]), int)
        and isinstance(_nested_get(first_explanation, ["control_provenance", "transparency", "blend_primary_contributor_on_near_tie"]), bool),
        "BL-008 control provenance includes transparency control snapshot",
    )

    check(
        "t3_bl009_validity_boundaries_present",
        isinstance(_nested_get(bl009_log, ["validity_boundaries"]), dict),
        "BL-009 run log includes validity_boundaries section",
    )
    check(
        "t3_bl009_validity_boundary_sections_present",
        isinstance(_nested_get(bl009_log, ["validity_boundaries", "scope"]), dict)
        and isinstance(_nested_get(bl009_log, ["validity_boundaries", "known_limits"]), dict)
        and isinstance(_nested_get(bl009_log, ["validity_boundaries", "run_caveats"]), dict),
        "BL-009 validity boundaries include scope, known_limits, and run_caveats",
    )
    check(
        "t3_bl009_scope_boundary_keys_present",
        isinstance(_nested_get(bl009_log, ["validity_boundaries", "scope", "single_user_deterministic"]), bool)
        and isinstance(_nested_get(bl009_log, ["validity_boundaries", "scope", "interaction_types_included"]), list),
        "BL-009 scope boundary includes deterministic-scope and interaction-set keys",
    )

    no_op_controls = _nested_get(bl011_report, ["results", "no_op_control_diagnostics"])
    no_op_count = _nested_get(bl011_report, ["results", "no_op_controls_count"])
    shifts_observable = _nested_get(bl011_report, ["results", "all_variant_shifts_observable"])

    check(
        "t3_bl011_no_op_diagnostics_present",
        isinstance(no_op_controls, list) and isinstance(no_op_count, int),
        "BL-011 results include explicit no-op control diagnostics",
    )
    check(
        "t3_bl011_no_op_count_consistent",
        isinstance(no_op_controls, list) and isinstance(no_op_count, int) and len(no_op_controls) == no_op_count,
        "BL-011 no-op controls count matches diagnostics list length",
    )
    check(
        "t3_bl011_shift_vs_noop_consistency",
        (isinstance(shifts_observable, bool) and isinstance(no_op_count, int))
        and ((not shifts_observable) or no_op_count == 0),
        "BL-011 no-op diagnostics are consistent with shift-observability verdict",
    )

    failed = [c for c in checks if c["status"] == "fail"]
    overall_status = "pass" if not failed else "fail"

    finished = datetime.now(UTC)
    report = {
        "run_id": run_id,
        "task": "REB-M3 tranche-3 control-causality gate",
        "generated_at_utc": format_utc_iso(finished),
        "elapsed_seconds": round((finished - started).total_seconds(), 3),
        "overall_status": overall_status,
        "total_checks": len(checks),
        "passed_checks": len(checks) - len(failed),
        "failed_checks": len(failed),
        "checks": checks,
        "artifacts_checked": {k: str(v) for k, v in artifacts.items()},
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "reb_m3_tranche3_gate_report.json"
    matrix_path = OUTPUT_DIR / "reb_m3_tranche3_gate_matrix.csv"

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


if __name__ == "__main__":
    raise SystemExit(main())
