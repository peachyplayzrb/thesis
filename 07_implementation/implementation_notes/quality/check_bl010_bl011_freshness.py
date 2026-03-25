#!/usr/bin/env python3

from __future__ import annotations

import csv
import importlib.util
import json
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relpath(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def check(checks: list[dict[str, str]], check_id: str, passed: bool, details: str) -> None:
    checks.append({
        "id": check_id,
        "status": "pass" if passed else "fail",
        "details": details,
    })


def build_current_bl010_snapshot(bl010_module) -> dict[str, Any]:
    paths = bl010_module.build_paths(REPO_ROOT)
    bl010_module.ensure_required_inputs(paths, REPO_ROOT)
    return bl010_module.build_config_snapshot(
        paths,
        REPO_ROOT,
        allow_legacy_surrogate_inputs=False,
    )


def build_current_bl011_snapshot(bl011_module, current_bl010_snapshot: dict[str, Any]) -> dict[str, Any]:
    paths = bl011_module.build_paths(REPO_ROOT)
    bl011_module.ensure_required_inputs(paths, REPO_ROOT, False)
    baseline_config_hash = bl011_module.canonical_json_hash(current_bl010_snapshot)
    scenarios = bl011_module.build_scenarios(current_bl010_snapshot)

    fixed_inputs = {
        relpath(paths["active_seed_trace"]): bl011_module.sha256_of_file(paths["active_seed_trace"]),
        relpath(paths["active_candidates"]): bl011_module.sha256_of_file(paths["active_candidates"]),
    }
    optional_inputs = {
        "legacy_manifest": paths["legacy_manifest"],
        "legacy_coverage": paths["legacy_coverage"],
    }
    for path in optional_inputs.values():
        if path.exists():
            fixed_inputs[relpath(path)] = bl011_module.sha256_of_file(path)

    return {
        "task": "BL-011",
        "generated_from": relpath(paths["baseline_snapshot"]),
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
        "scenarios": scenarios,
    }


def main() -> int:
    started = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    bl010_module = load_module(
        "bl010_reproducibility_check",
        REPO_ROOT / "07_implementation" / "implementation_notes" / "reproducibility" / "run_bl010_reproducibility_check.py",
    )
    bl011_module = load_module(
        "bl011_controllability_check",
        REPO_ROOT / "07_implementation" / "implementation_notes" / "controllability" / "run_bl011_controllability_check.py",
    )

    bl010_snapshot_path = REPO_ROOT / "07_implementation" / "implementation_notes" / "reproducibility" / "outputs" / "bl010_reproducibility_config_snapshot.json"
    bl010_report_path = REPO_ROOT / "07_implementation" / "implementation_notes" / "reproducibility" / "outputs" / "bl010_reproducibility_report.json"
    bl011_snapshot_path = REPO_ROOT / "07_implementation" / "implementation_notes" / "controllability" / "outputs" / "bl011_controllability_config_snapshot.json"
    bl011_report_path = REPO_ROOT / "07_implementation" / "implementation_notes" / "controllability" / "outputs" / "bl011_controllability_report.json"

    required_paths = [
        bl010_snapshot_path,
        bl010_report_path,
        bl011_snapshot_path,
        bl011_report_path,
    ]
    missing = [relpath(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required freshness inputs: {missing}")

    stored_bl010_snapshot = load_json(bl010_snapshot_path)
    stored_bl010_report = load_json(bl010_report_path)
    stored_bl011_snapshot = load_json(bl011_snapshot_path)
    stored_bl011_report = load_json(bl011_report_path)

    current_bl010_snapshot = build_current_bl010_snapshot(bl010_module)
    current_bl010_hash = bl010_module.canonical_json_hash(current_bl010_snapshot)
    stored_bl010_snapshot_hash = bl010_module.canonical_json_hash(stored_bl010_snapshot)

    current_bl011_snapshot = build_current_bl011_snapshot(bl011_module, current_bl010_snapshot)
    current_bl011_hash = bl011_module.canonical_json_hash(current_bl011_snapshot)
    stored_bl011_snapshot_hash = bl011_module.canonical_json_hash(stored_bl011_snapshot)

    checks: list[dict[str, str]] = []

    check(
        checks,
        "bl010_snapshot_matches_current_contract",
        stored_bl010_snapshot_hash == current_bl010_hash,
        "BL-010 config snapshot matches the current active-pipeline reproducibility contract",
    )
    check(
        checks,
        "bl010_report_hash_matches_current_contract",
        str(stored_bl010_report["run_metadata"]["config_hash"]) == current_bl010_hash,
        "BL-010 report config_hash matches the current active-pipeline reproducibility contract",
    )
    check(
        checks,
        "bl010_fixed_input_hashes_match_current",
        stored_bl010_report["inputs"]["fixed_input_hashes"] == current_bl010_snapshot["fixed_inputs"],
        "BL-010 fixed input hashes match the current active pipeline outputs",
    )
    check(
        checks,
        "bl010_stage_script_hashes_match_current",
        stored_bl010_report["inputs"]["stage_scripts"] == current_bl010_snapshot["stage_scripts"],
        "BL-010 stage script hashes match the current BL-004 to BL-009 code",
    )
    check(
        checks,
        "bl010_active_mode",
        stored_bl010_report["run_metadata"]["fixed_input_source"] == "active_pipeline_outputs",
        "BL-010 evidence is using active pipeline outputs rather than legacy surrogate inputs",
    )
    check(
        checks,
        "bl011_snapshot_matches_current_contract",
        stored_bl011_snapshot_hash == current_bl011_hash,
        "BL-011 config snapshot matches the current active controllability contract",
    )
    check(
        checks,
        "bl011_baseline_hash_matches_current_bl010",
        str(stored_bl011_report["run_metadata"]["baseline_config_hash"]) == current_bl010_hash,
        "BL-011 baseline_config_hash matches the current BL-010 baseline snapshot",
    )
    check(
        checks,
        "bl011_fixed_input_hashes_match_current",
        stored_bl011_report["inputs"]["fixed_input_hashes"] == current_bl011_snapshot["fixed_inputs"],
        "BL-011 fixed input hashes match the current active controllability inputs",
    )
    check(
        checks,
        "bl011_active_mode",
        stored_bl011_snapshot["input_source"] == "active_pipeline_outputs",
        "BL-011 evidence is using active pipeline outputs rather than legacy surrogate inputs",
    )

    overall_status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    report = {
        "run_metadata": {
            "run_id": f"BL-FRESHNESS-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}",
            "task": "BL-010/011 freshness check",
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "elapsed_seconds": round(time.time() - started, 3),
            "overall_status": overall_status,
            "checks_total": len(checks),
            "checks_passed": sum(1 for item in checks if item["status"] == "pass"),
            "checks_failed": sum(1 for item in checks if item["status"] == "fail"),
        },
        "current_contract_hashes": {
            "bl010_config_hash": current_bl010_hash,
            "bl011_config_hash": current_bl011_hash,
        },
        "evidence_paths": {
            "bl010_config_snapshot": relpath(bl010_snapshot_path),
            "bl010_report": relpath(bl010_report_path),
            "bl011_config_snapshot": relpath(bl011_snapshot_path),
            "bl011_report": relpath(bl011_report_path),
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

    report_path = OUTPUT_DIR / "bl010_bl011_freshness_report.json"
    matrix_path = OUTPUT_DIR / "bl010_bl011_freshness_matrix.csv"
    write_json(report_path, report)
    write_csv(matrix_path, matrix_rows)

    print("BL-010/BL-011 freshness check complete.")
    print(f"overall_status={overall_status}")
    print(f"report={report_path}")
    print(f"run_matrix={matrix_path}")
    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())