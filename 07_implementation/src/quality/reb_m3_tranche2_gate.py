#!/usr/bin/env python3
"""REB-M3 tranche-2 gate checks for O4 to O6 evidence surfaces.

This script validates that the current BL-007 to BL-011 outputs contain the
minimum objective-linked evidence fields required for REB-M3 tranche-2:
- O4 mechanism-linked explanations and run observability evidence
- O5 reproducibility and controllability evaluation evidence
- O6 bounded guidance and failure-boundary reporting evidence

Outputs are written to:
- quality/outputs/reb_m3_tranche2_gate_report.json
- quality/outputs/reb_m3_tranche2_gate_matrix.csv
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
    run_id = f"REB-M3-TRANCHE2-GATE-{started.strftime('%Y%m%d-%H%M%S-%f')}"

    artifacts = {
        "bl007_report": REPO_ROOT / "playlist/outputs/bl007_assembly_report.json",
        "bl008_payloads": REPO_ROOT / "transparency/outputs/bl008_explanation_payloads.json",
        "bl009_log": REPO_ROOT / "observability/outputs/bl009_run_observability_log.json",
        "bl010_report": REPO_ROOT / "reproducibility/outputs/reproducibility_report.json",
        "bl011_report": REPO_ROOT / "controllability/outputs/controllability_report.json",
    }
    for artifact_path in artifacts.values():
        ensure_exists(artifact_path)

    bl007_report = load_json(artifacts["bl007_report"])
    bl008_payloads = load_json(artifacts["bl008_payloads"])
    bl009_log = load_json(artifacts["bl009_log"])
    bl010_report = load_json(artifacts["bl010_report"])
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
    primary_driver_component = _nested_get(first_explanation, ["primary_explanation_driver", "component"])
    score_breakdown_components = {
        row.get("component")
        for row in (first_explanation.get("score_breakdown") or [])
        if isinstance(row, dict)
    }

    # O4: mechanism-linked explanations and observability
    check(
        "o4_bl008_mechanism_fields_present",
        isinstance(explanations, list)
        and len(explanations) > 0
        and isinstance(_nested_get(first_explanation, ["primary_explanation_driver", "component"]), str)
        and isinstance(first_explanation.get("score_breakdown"), list)
        and isinstance(first_explanation.get("assembly_context"), dict),
        "BL-008 explanations include mechanism-level driver, score-breakdown, and assembly-context fields",
    )
    check(
        "o4_bl008_driver_maps_to_breakdown",
        isinstance(primary_driver_component, str)
        and primary_driver_component in score_breakdown_components,
        "BL-008 primary explanation driver maps to an explicit BL-006 score-breakdown component",
    )
    check(
        "o4_bl009_run_lineage_present",
        isinstance(_nested_get(bl009_log, ["run_metadata", "upstream_stage_run_ids"]), dict)
        and {"BL-007", "BL-008"}.issubset(set((_nested_get(bl009_log, ["run_metadata", "upstream_stage_run_ids"]) or {}).keys())),
        "BL-009 observability log includes upstream run lineage for explanation-linked stages",
    )

    # O5: reproducibility and controllability evidence
    check(
        "o5_bl010_repro_pass",
        _nested_get(bl010_report, ["results", "status"]) == "pass"
        and _nested_get(bl010_report, ["results", "deterministic_match"]) is True,
        "BL-010 report indicates deterministic replay pass",
    )
    check(
        "o5_bl011_control_pass",
        _nested_get(bl011_report, ["results", "status"]) == "pass"
        and _nested_get(bl011_report, ["results", "all_scenarios_repeat_consistent"]) is True
        and _nested_get(bl011_report, ["results", "all_variant_shifts_observable"]) is True,
        "BL-011 report indicates repeat consistency and observable control shifts",
    )
    check(
        "o5_bl009_config_contract_pair_present",
        _nested_get(bl009_log, ["execution_scope_summary", "canonical_config_artifact_pair_available"]) is True
        and isinstance(_nested_get(bl009_log, ["run_metadata", "run_intent_path"]), str)
        and isinstance(_nested_get(bl009_log, ["run_metadata", "run_effective_config_path"]), str),
        "BL-009 observability includes canonical run-intent/effective-config contract pointers",
    )

    # O6: bounded guidance and failure-boundary reporting evidence
    check(
        "o6_bl007_boundary_reporting_present",
        isinstance(bl007_report.get("undersized_playlist_warning"), dict)
        and isinstance(bl007_report.get("rank_continuity_diagnostics"), dict)
        and isinstance(bl007_report.get("assembly_pressure_diagnostics"), dict),
        "BL-007 report includes explicit boundary diagnostics for size, ranking pressure, and exclusion pressure",
    )
    check(
        "o6_bl010_retry_boundary_reporting_present",
        isinstance(_nested_get(bl010_report, ["results", "all_stage_runs_succeeded_without_retry"]), bool)
        and isinstance(_nested_get(bl010_report, ["results", "stages_requiring_retry"]), list),
        "BL-010 report captures retry-boundary behavior for reproducibility validity limits",
    )
    check(
        "o6_bl009_scope_boundary_present",
        isinstance(_nested_get(bl009_log, ["execution_scope_summary", "source_family"]), str)
        and isinstance(_nested_get(bl009_log, ["execution_scope_summary", "interaction_types_included"]), list)
        and isinstance(_nested_get(bl009_log, ["execution_scope_summary", "total_seed_count"]), int),
        "BL-009 execution scope summary includes source/signal and seed boundary context",
    )

    failed = [c for c in checks if c["status"] == "fail"]
    overall_status = "pass" if not failed else "fail"

    finished = datetime.now(UTC)
    report = {
        "run_id": run_id,
        "task": "REB-M3 tranche-2 O4-O6 gate",
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
    report_path = OUTPUT_DIR / "reb_m3_tranche2_gate_report.json"
    matrix_path = OUTPUT_DIR / "reb_m3_tranche2_gate_matrix.csv"

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
