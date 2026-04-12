#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

from shared.io_utils import load_json, sha256_of_file, utc_now
from shared.path_utils import impl_root



DEFAULT_CONTROLLABILITY_CONTROLS: dict[str, float] = {
    "weight_override_value_if_component_present": 0.20,
    "weight_override_increment_fallback": 0.08,
    "weight_override_cap_fallback": 0.35,
    "stricter_threshold_scale": 0.75,
    "looser_threshold_scale": 1.25,
}
DEFAULT_SCENARIO_POLICY: dict[str, Any] = {
    "enabled_scenario_ids": ["all"],
    "repeat_count": 1,
    "stage_scope": ["all"],
    "comparison_mode": "baseline_reference",
}
DEFAULT_SCENARIO_DEFINITIONS: list[dict[str, object]] = []


def stage_relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def bl003_required_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "summary": repo_root / "alignment/outputs/bl003_ds001_spotify_summary.json",
        "seed_table": repo_root / "alignment/outputs/bl003_ds001_spotify_seed_table.csv",
        "matched_events": repo_root / "alignment/outputs/bl003_ds001_spotify_matched_events.jsonl",
        "trace": repo_root / "alignment/outputs/bl003_ds001_spotify_trace.csv",
        "unmatched": repo_root / "alignment/outputs/bl003_ds001_spotify_unmatched.csv",
        "source_scope_manifest": repo_root / "alignment/outputs/bl003_source_scope_manifest.json",
    }


def bl014_bl013_latest_summary_path(repo_root: Path) -> Path:
    return repo_root / "orchestration/outputs/bl013_orchestration_run_latest.json"


def bl014_freshness_input_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "bl010_snapshot": repo_root / "reproducibility/outputs/reproducibility_config_snapshot.json",
        "bl010_report": repo_root / "reproducibility/outputs/reproducibility_report.json",
        "bl011_snapshot": repo_root / "controllability/outputs/controllability_config_snapshot.json",
        "bl011_report": repo_root / "controllability/outputs/controllability_report.json",
    }


def bl014_pipeline_script_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "bl010_script": repo_root / "reproducibility.py",
        "bl011_script": repo_root / "controllability.py",
        "bl013_script": repo_root / "orchestration.py",
    }


def bl014_refinement_diagnostic_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "bl006_distribution": repo_root / "scoring/outputs/bl006_score_distribution_diagnostics.json",
        "bl007_assembly_report": repo_root / "playlist/outputs/bl007_assembly_report.json",
    }


def ensure_paths_exist(
    paths: list[Path],
    *,
    stage_label: str,
    label: str = "input artifact(s)",
    root: Path | None = None,
) -> None:
    missing: list[str] = []
    for path in paths:
        if path.exists():
            continue
        if root is None:
            missing.append(str(path))
            continue
        try:
            missing.append(path.relative_to(root).as_posix())
        except ValueError:
            missing.append(str(path))
    if missing:
        raise FileNotFoundError(f"{stage_label} missing required {label}: {missing}")


REPO_ROOT = impl_root()
QUALITY_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = QUALITY_DIR / "outputs"


def format_utc_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc_iso(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
def write_json_ascii(path: Path, payload: dict[str, object] | list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def write_csv_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("rows must not be empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


@dataclass(frozen=True)
class CheckResult:
    id: str
    status: str
    details: str


@dataclass(frozen=True)
class RefreshResult:
    combined_return_code: int
    bl010_return_code: int
    bl013_return_code: int | None
    bl011_return_code: int | None
    bl013_post_bl011_return_code: int | None
    bl010_ran: bool
    bl013_ran: bool
    bl011_ran: bool
    bl013_post_bl011_ran: bool
    outputs: dict[str, str]


def _add_check(checks: list[CheckResult], check_id: str, passed: bool, details: str) -> None:
    checks.append(CheckResult(id=check_id, status="pass" if passed else "fail", details=details))


def _check_counts(checks: list[CheckResult]) -> tuple[int, int]:
    passed = sum(1 for item in checks if item.status == "pass")
    failed = len(checks) - passed
    return passed, failed


def _checks_as_rows(checks: list[CheckResult]) -> list[dict[str, str]]:
    return [{"id": item.id, "status": item.status, "details": item.details} for item in checks]


def _run_python_script(
    script_path: Path,
    args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> tuple[int, str]:
    command = [sys.executable, str(script_path)]
    if args:
        command.extend(args)
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    process = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (process.stdout or "").strip()
    if process.stderr:
        output = f"{output}\n{process.stderr.strip()}".strip()
    return process.returncode, output


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _nested_dict(raw: object, *keys: str) -> dict[str, Any]:
    current: object = raw
    for key in keys:
        if not isinstance(current, dict):
            return {}
        current = current.get(key)
    return dict(current) if isinstance(current, dict) else {}


def _build_refresh_result(
    *,
    combined_return_code: int,
    bl010_return_code: int,
    bl013_return_code: int | None,
    bl011_return_code: int | None,
    bl013_post_bl011_return_code: int | None,
    bl010_ran: bool,
    bl013_ran: bool,
    bl011_ran: bool,
    bl013_post_bl011_ran: bool,
    bl010_output: str,
    bl013_output: str,
    bl011_output: str,
    bl013_post_output: str,
) -> RefreshResult:
    return RefreshResult(
        combined_return_code=combined_return_code,
        bl010_return_code=bl010_return_code,
        bl013_return_code=bl013_return_code,
        bl011_return_code=bl011_return_code,
        bl013_post_bl011_return_code=bl013_post_bl011_return_code,
        bl010_ran=bl010_ran,
        bl013_ran=bl013_ran,
        bl011_ran=bl011_ran,
        bl013_post_bl011_ran=bl013_post_bl011_ran,
        outputs={
            "bl010_stdout_stderr": bl010_output,
            "bl013_stdout_stderr": bl013_output,
            "bl011_stdout_stderr": bl011_output,
            "bl013_post_bl011_stdout_stderr": bl013_post_output,
        },
    )


def _safe_relpath(path: Path) -> str:
    try:
        return stage_relpath(path, REPO_ROOT)
    except ValueError:
        return str(path)


def _write_suite_artifacts(
    *,
    run_id: str,
    task: str,
    elapsed_seconds: float,
    overall_status: str,
    evidence_paths: dict[str, str],
    checks: list[CheckResult],
    report_path: Path,
    matrix_path: Path,
    script_outputs: dict[str, str] | None = None,
    extra_sections: dict[str, Any] | None = None,
) -> None:
    checks_passed, checks_failed = _check_counts(checks)
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
        "checks": _checks_as_rows(checks),
    }
    if script_outputs:
        report["script_outputs"] = script_outputs
    if extra_sections:
        report.update(extra_sections)

    matrix_rows: list[dict[str, object]] = [
        {"check_id": item.id, "status": item.status, "details": item.details}
        for item in checks
    ]
    write_json_ascii(report_path, report)
    write_csv_rows(matrix_path, matrix_rows)


def _build_current_bl011_snapshot(
    bl011_module: Any,
    *,
    paths_bl011: dict[str, Path],
    current_bl010_snapshot: dict[str, Any],
    run_config_path: str | None = None,
) -> dict[str, Any]:
    baseline_config_hash = bl011_module.canonical_json_hash(current_bl010_snapshot)
    try:
        if run_config_path:
            run_config_utils = _load_module(
                "run_config_utils_for_quality",
                REPO_ROOT / "run_config" / "run_config_utils.py",
            )
            resolved_controls = run_config_utils.resolve_bl011_controls(run_config_path)
            runtime_controls = {
                "config_source": "orchestration_payload",
                "run_config_path": str(run_config_path),
                "weight_override_value_if_component_present": resolved_controls["weight_override_value_if_component_present"],
                "weight_override_increment_fallback": resolved_controls["weight_override_increment_fallback"],
                "weight_override_cap_fallback": resolved_controls["weight_override_cap_fallback"],
                "stricter_threshold_scale": resolved_controls["stricter_threshold_scale"],
                "looser_threshold_scale": resolved_controls["looser_threshold_scale"],
                "scenario_policy": dict(DEFAULT_SCENARIO_POLICY),
                "scenario_definitions": list(DEFAULT_SCENARIO_DEFINITIONS),
            }
        else:
            runtime_controls = bl011_module.resolve_bl011_runtime_controls()
    except Exception:
        # BL-011 can require orchestration payloads in strict mode; freshness checks
        # still need a deterministic local fallback to compare stored evidence.
        runtime_controls = {
            "config_source": "quality_fallback_defaults",
            "run_config_path": None,
            **dict(DEFAULT_CONTROLLABILITY_CONTROLS),
            "scenario_policy": dict(DEFAULT_SCENARIO_POLICY),
            "scenario_definitions": list(DEFAULT_SCENARIO_DEFINITIONS),
        }
    scenarios = bl011_module.build_scenarios(current_bl010_snapshot, runtime_controls)

    bl003_summary = load_json(paths_bl011["bl003_summary"])
    bl003_inputs = _nested_dict(bl003_summary, "inputs")
    alignment_fuzzy_controls = _nested_dict(bl003_inputs, "fuzzy_matching")
    alignment_counts = _nested_dict(bl003_summary, "counts")

    fixed_inputs = {
        _safe_relpath(paths_bl011["bl003_summary"]): bl011_module.sha256_of_file(paths_bl011["bl003_summary"]),
        _safe_relpath(paths_bl011["active_seed_trace"]): bl011_module.sha256_of_file(paths_bl011["active_seed_trace"]),
        _safe_relpath(paths_bl011["active_candidates"]): bl011_module.sha256_of_file(paths_bl011["active_candidates"]),
    }

    optional_inputs = {
        "legacy_manifest": paths_bl011["legacy_manifest"],
        "legacy_coverage": paths_bl011["legacy_coverage"],
    }
    for path in optional_inputs.values():
        if path.exists():
            fixed_inputs[_safe_relpath(path)] = bl011_module.sha256_of_file(path)

    return {
        "task": "BL-011",
        "generated_from": _safe_relpath(paths_bl011["baseline_snapshot"]),
        "baseline_config_hash": baseline_config_hash,
        "input_source": "active_pipeline_outputs",
        "alignment_seed_controls": {
            "fuzzy_matching": dict(alignment_fuzzy_controls),
        },
        "alignment_counts": {
            "input_event_rows": int(alignment_counts.get("input_event_rows", 0)),
            "matched_by_spotify_id": int(alignment_counts.get("matched_by_spotify_id", 0)),
            "matched_by_metadata": int(alignment_counts.get("matched_by_metadata", 0)),
            "matched_by_fuzzy": int(alignment_counts.get("matched_by_fuzzy", 0)),
            "unmatched": int(alignment_counts.get("unmatched", 0)),
            "seed_table_rows": int(alignment_counts.get("seed_table_rows", 0)),
        },
        "fixed_inputs": fixed_inputs,
        "optional_dependency_availability": {
            key: {
                "path": _safe_relpath(path),
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


def _refresh_bl010_bl011_evidence() -> RefreshResult:
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

    bl011_controls_payload = {
        "config_source": "orchestration_payload",
        "run_config_path": str(run_config_path) if run_config_path else None,
        **dict(DEFAULT_CONTROLLABILITY_CONTROLS),
        "scenario_policy": dict(DEFAULT_SCENARIO_POLICY),
        "scenario_definitions": list(DEFAULT_SCENARIO_DEFINITIONS),
    }
    if run_config_path:
        try:
            run_config_utils = _load_module(
                "run_config_utils_for_quality_refresh",
                REPO_ROOT / "run_config" / "run_config_utils.py",
            )
            resolved_controls = run_config_utils.resolve_bl011_controls(str(run_config_path))
            bl011_controls_payload.update(
                {
                    "weight_override_value_if_component_present": resolved_controls["weight_override_value_if_component_present"],
                    "weight_override_increment_fallback": resolved_controls["weight_override_increment_fallback"],
                    "weight_override_cap_fallback": resolved_controls["weight_override_cap_fallback"],
                    "stricter_threshold_scale": resolved_controls["stricter_threshold_scale"],
                    "looser_threshold_scale": resolved_controls["looser_threshold_scale"],
                }
            )
        except Exception:
            # Fall back to defaults if run-config resolution fails during auto-refresh.
            pass
    bl011_env = {
        "BL_STAGE_CONFIG_JSON": json.dumps({"controls": bl011_controls_payload}, ensure_ascii=True)
    }

    # Run BL-013 first so active artifacts are refreshed before BL-010/BL-011
    # capture contract snapshots and fixed-input hashes.
    bl013_return, bl013_output = _run_python_script(bl013_script, args=bl013_args)
    if bl013_return != 0:
        return _build_refresh_result(
            combined_return_code=bl013_return,
            bl010_return_code=-1,
            bl013_return_code=bl013_return,
            bl011_return_code=None,
            bl013_post_bl011_return_code=None,
            bl010_ran=False,
            bl013_ran=True,
            bl011_ran=False,
            bl013_post_bl011_ran=False,
            bl010_output="",
            bl013_output=bl013_output,
            bl011_output="",
            bl013_post_output="",
        )

    bl010_return, bl010_output = _run_python_script(bl010_script, args=bl010_args)
    if bl010_return != 0:
        return _build_refresh_result(
            combined_return_code=bl010_return,
            bl010_return_code=bl010_return,
            bl013_return_code=bl013_return,
            bl011_return_code=None,
            bl013_post_bl011_return_code=None,
            bl010_ran=True,
            bl013_ran=True,
            bl011_ran=False,
            bl013_post_bl011_ran=False,
            bl010_output=bl010_output,
            bl013_output=bl013_output,
            bl011_output="",
            bl013_post_output="",
        )

    bl011_return, bl011_output = _run_python_script(bl011_script, extra_env=bl011_env)
    if bl011_return != 0:
        return _build_refresh_result(
            combined_return_code=bl011_return,
            bl010_return_code=bl010_return,
            bl013_return_code=bl013_return,
            bl011_return_code=bl011_return,
            bl013_post_bl011_return_code=None,
            bl010_ran=True,
            bl013_ran=True,
            bl011_ran=True,
            bl013_post_bl011_ran=False,
            bl010_output=bl010_output,
            bl013_output=bl013_output,
            bl011_output=bl011_output,
            bl013_post_output="",
        )

    # Do not rerun BL-013 after BL-011 refresh. A post-refresh BL-013 mutates active
    # artifacts after BL-010/BL-011 snapshots are written, which invalidates freshness checks.
    return _build_refresh_result(
        combined_return_code=bl011_return,
        bl010_return_code=bl010_return,
        bl013_return_code=bl013_return,
        bl011_return_code=bl011_return,
        bl013_post_bl011_return_code=None,
        bl010_ran=True,
        bl013_ran=True,
        bl011_ran=True,
        bl013_post_bl011_ran=False,
        bl010_output=bl010_output,
        bl013_output=bl013_output,
        bl011_output=bl011_output,
        bl013_post_output="",
    )


def _csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def _csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader)
        return sum(1 for _ in reader)


def _bl005_filtered_has_required_columns(header: list[str]) -> bool:
    required = {
        "track_id",
        "artist",
        "song",
        "tags",
        "genres",
        "tempo",
        "duration_ms",
        "key",
        "mode",
    }
    header_set = set(header)
    return required.issubset(header_set) and (header_set & {"id", "cid"}) != set()


def _ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path}")


def _resolve_existing_path(preferred: Path, fallback: Path) -> Path:
    if preferred.exists():
        return preferred
    if fallback.exists():
        return fallback
    return preferred


def _as_float_dict(raw: object) -> dict[str, float]:
    if not isinstance(raw, dict):
        return {}
    parsed: dict[str, float] = {}
    for key, value in raw.items():
        try:
            parsed[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return parsed


def _build_sanity_artifacts() -> dict[str, Path]:
    bl003_paths = bl003_required_paths(REPO_ROOT)
    return {
        "bl003_summary": bl003_paths["summary"],
        "bl003_seed_table": bl003_paths["seed_table"],
        "profile": REPO_ROOT / "profile/outputs/bl004_preference_profile.json",
        "bl004_summary": REPO_ROOT / "profile/outputs/profile_summary.json",
        "bl005_filtered": REPO_ROOT / "retrieval/outputs/bl005_filtered_candidates.csv",
        "bl005_decisions": REPO_ROOT / "retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_diag": REPO_ROOT / "retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl006_scored": REPO_ROOT / "scoring/outputs/bl006_scored_candidates.csv",
        "bl006_summary": REPO_ROOT / "scoring/outputs/bl006_score_summary.json",
        "playlist": REPO_ROOT / "playlist/outputs/playlist.json",
        "bl007_trace": REPO_ROOT / "playlist/outputs/bl007_assembly_trace.csv",
        "bl007_report": REPO_ROOT / "playlist/outputs/bl007_assembly_report.json",
        "bl008_payloads": REPO_ROOT / "transparency/outputs/bl008_explanation_payloads.json",
        "bl008_summary": REPO_ROOT / "transparency/outputs/bl008_explanation_summary.json",
        "bl009_log": REPO_ROOT / "observability/outputs/bl009_run_observability_log.json",
        "bl009_index": REPO_ROOT / "observability/outputs/bl009_run_index.csv",
        "bl004_seed_trace": REPO_ROOT / "profile/outputs/bl004_seed_trace.csv",
    }


def run_sanity_mode() -> int:
    started = datetime.now(UTC)
    run_id = f"BL014-SANITY-{started.strftime('%Y%m%d-%H%M%S-%f')}"

    artifacts = _build_sanity_artifacts()
    for artifact_path in artifacts.values():
        _ensure_exists(artifact_path)

    bl003_summary = load_json(artifacts["bl003_summary"])
    profile = load_json(artifacts["profile"])
    bl004_summary = load_json(artifacts["bl004_summary"])
    bl005_diag = load_json(artifacts["bl005_diag"])
    bl006_summary = load_json(artifacts["bl006_summary"])
    bl007_report = load_json(artifacts["bl007_report"])
    bl008_summary = load_json(artifacts["bl008_summary"])
    bl008_payloads = load_json(artifacts["bl008_payloads"])
    playlist = load_json(artifacts["playlist"])
    bl009_log = load_json(artifacts["bl009_log"])

    with artifacts["bl009_index"].open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        bl009_index_rows = list(reader)
    if len(bl009_index_rows) != 1:
        raise RuntimeError("Expected exactly one row in bl009_run_index.csv")
    bl009_index = bl009_index_rows[0]

    hashes = {name: sha256_of_file(path).upper() for name, path in artifacts.items()}

    checks: list[CheckResult] = []
    advisories: list[dict[str, Any]] = []

    bl003_required = {"inputs", "counts", "outputs"}
    _add_check(
        checks,
        "schema_bl003_summary",
        bl003_required.issubset(set(bl003_summary.keys())),
        "BL-003 summary contains required top-level keys",
    )

    profile_required = {
        "run_id",
        "task",
        "user_id",
        "matched_seed_count",
        "total_effective_weight",
        "dominant_lead_genres",
        "dominant_tags",
        "dominant_genres",
        "feature_centers",
        "input_hashes",
    }
    _add_check(
        checks,
        "schema_bl004_summary",
        profile_required.issubset(set(bl004_summary.keys())),
        "BL-004 summary contains required top-level keys",
    )

    candidate_stub_path = _resolve_existing_path(
        Path(bl005_diag["input_artifacts"]["candidate_stub_path"]),
        REPO_ROOT / "data_layer/outputs/ds001_working_candidate_dataset.csv",
    )
    _ensure_exists(candidate_stub_path)
    candidate_stub_hash = sha256_of_file(candidate_stub_path).upper()

    _add_check(
        checks,
        "schema_bl005_filtered_csv",
        _bl005_filtered_has_required_columns(_csv_header(artifacts["bl005_filtered"])),
        "BL-005 filtered candidates CSV contains required columns",
    )

    decisions_required_cols = {
        "track_id",
        "semantic_score",
        "decision",
        "decision_reason",
    }
    _add_check(
        checks,
        "schema_bl005_decisions_csv",
        decisions_required_cols.issubset(set(_csv_header(artifacts["bl005_decisions"]))),
        "BL-005 decision trace CSV contains required columns",
    )

    scored_required_cols = {
        "rank",
        "track_id",
        "lead_genre",
        "final_score",
        "lead_genre_contribution",
        "genre_overlap_contribution",
        "tag_overlap_contribution",
    }
    _add_check(
        checks,
        "schema_bl006_scored_csv",
        scored_required_cols.issubset(set(_csv_header(artifacts["bl006_scored"]))),
        "BL-006 scored candidates CSV contains required columns",
    )

    _add_check(
        checks,
        "schema_playlist_json",
        isinstance(playlist.get("tracks"), list)
        and playlist.get("playlist_length") == len(playlist.get("tracks", [])),
        "BL-007 playlist JSON tracks length matches playlist_length",
    )

    _add_check(
        checks,
        "schema_bl008_payloads_json",
        isinstance(bl008_payloads.get("explanations"), list)
        and bl008_payloads.get("playlist_track_count") == len(bl008_payloads.get("explanations", [])),
        "BL-008 payload JSON explanation count matches playlist_track_count",
    )

    obs_required_sections = {
        "run_metadata",
        "run_config",
        "ingestion_alignment_diagnostics",
        "stage_diagnostics",
        "exclusion_diagnostics",
        "output_artifacts",
    }
    _add_check(
        checks,
        "schema_observability_log",
        obs_required_sections.issubset(set(bl009_log.keys())),
        "BL-009 observability log contains required sections",
    )
    _add_check(
        checks,
        "schema_bl003_fuzzy_controls",
        isinstance(_nested_dict(bl003_summary, "inputs", "fuzzy_matching"), dict),
        "BL-003 summary includes fuzzy matching control block",
    )
    _add_check(
        checks,
        "schema_bl003_seed_aggregation_health",
        isinstance(_nested_dict(bl003_summary, "counts", "seed_aggregation_health"), dict),
        "BL-003 summary includes seed aggregation health diagnostics",
    )
    _add_check(
        checks,
        "schema_bl004_confidence_diagnostics",
        isinstance(bl004_summary.get("confidence_diagnostics"), dict)
        and isinstance(bl004_summary.get("confidence_input_health"), dict),
        "BL-004 summary includes confidence diagnostics and confidence input health blocks",
    )
    _add_check(
        checks,
        "schema_bl006_spread_diagnostics",
        isinstance(_nested_dict(bl006_summary, "score_distribution_diagnostics", "score_range"), dict)
        and "spread_ratio" in _nested_dict(bl006_summary, "score_distribution_diagnostics", "score_range"),
        "BL-006 summary includes score spread diagnostics",
    )
    _add_check(
        checks,
        "schema_bl007_pressure_ratio_diagnostics",
        isinstance(_nested_dict(bl007_report, "assembly_pressure_diagnostics"), dict)
        and "top_100_exclusion_ratio" in _nested_dict(bl007_report, "assembly_pressure_diagnostics"),
        "BL-007 report includes top-100 exclusion ratio diagnostics",
    )

    profile_seed_table_path = _resolve_existing_path(
        Path(profile["input_artifacts"]["seed_table_path"]),
        artifacts["bl003_seed_table"],
    )
    _ensure_exists(profile_seed_table_path)
    _add_check(
        checks,
        "hash_bl004_input_seed_table",
        profile["input_artifacts"]["seed_table_sha256"].upper() == sha256_of_file(profile_seed_table_path).upper(),
        "BL-004 profile links to the seed table hash recorded in its input artifacts",
    )

    _add_check(
        checks,
        "hash_bl005_input_profile",
        bl005_diag["input_artifacts"]["profile_sha256"].upper() == hashes["profile"],
        "BL-005 references BL-004 profile hash correctly",
    )
    _add_check(
        checks,
        "hash_bl005_input_seed_trace",
        bl005_diag["input_artifacts"]["seed_trace_sha256"].upper() == hashes["bl004_seed_trace"],
        "BL-005 references BL-004 seed trace hash correctly",
    )
    _add_check(
        checks,
        "hash_bl005_input_dataset",
        bl005_diag["input_artifacts"]["candidate_stub_sha256"].upper() == candidate_stub_hash,
        "BL-005 references candidate dataset hash correctly",
    )
    _add_check(
        checks,
        "hash_bl005_outputs",
        bl005_diag["output_hashes_sha256"]["bl005_filtered_candidates.csv"].upper() == hashes["bl005_filtered"]
        and bl005_diag["output_hashes_sha256"]["bl005_candidate_decisions.csv"].upper() == hashes["bl005_decisions"],
        "BL-005 output hashes match actual files",
    )

    _add_check(
        checks,
        "hash_bl006_inputs",
        bl006_summary["input_artifacts"]["profile_sha256"].upper() == hashes["profile"]
        and bl006_summary["input_artifacts"]["filtered_candidates_sha256"].upper() == hashes["bl005_filtered"],
        "BL-006 input hashes match BL-004 and BL-005 outputs",
    )
    _add_check(
        checks,
        "hash_bl006_output",
        bl006_summary["output_hashes_sha256"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"],
        "BL-006 output hash matches actual scored CSV",
    )

    _add_check(
        checks,
        "hash_bl007_links",
        bl007_report["input_artifact_hashes"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"]
        and bl007_report["output_artifact_hashes"]["playlist.json"].upper() == hashes["playlist"]
        and bl007_report["output_artifact_hashes"]["bl007_assembly_trace.csv"].upper() == hashes["bl007_trace"],
        "BL-007 report links to BL-006 input and BL-007 outputs correctly",
    )

    _add_check(
        checks,
        "hash_bl008_links",
        bl008_summary["input_artifact_hashes"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"]
        and bl008_summary["input_artifact_hashes"]["bl006_score_summary.json"].upper() == hashes["bl006_summary"]
        and bl008_summary["input_artifact_hashes"]["playlist.json"].upper() == hashes["playlist"]
        and bl008_summary["input_artifact_hashes"]["bl007_assembly_trace.csv"].upper() == hashes["bl007_trace"]
        and bl008_summary["output_artifact_hashes"]["bl008_explanation_payloads.json"].upper() == hashes["bl008_payloads"],
        "BL-008 summary links to upstream inputs and output hash correctly",
    )

    _add_check(
        checks,
        "hash_bl009_index",
        bl009_index["playlist_sha256"].upper() == hashes["playlist"]
        and bl009_index["explanation_payloads_sha256"].upper() == hashes["bl008_payloads"]
        and bl009_index["observability_log_sha256"].upper() == hashes["bl009_log"],
        "BL-009 index hashes match playlist, explanation payloads, and observability log",
    )

    # Validate BL-005/BL-006 threshold coupling to guard run-config contract drift.
    bl005_numeric_thresholds = _as_float_dict(_nested_dict(bl005_diag, "config", "numeric_thresholds"))
    bl006_numeric_thresholds = _as_float_dict(_nested_dict(bl006_summary, "config", "numeric_thresholds"))
    bl005_popularity_enabled = bool(
        _nested_dict(bl005_diag, "config", "signal_mode", "popularity_profile").get("retrieval_enabled", False)
    )
    shared_threshold_keys = set(bl005_numeric_thresholds) & set(bl006_numeric_thresholds)
    shared_thresholds_match = all(
        bl005_numeric_thresholds[key] == bl006_numeric_thresholds[key]
        for key in shared_threshold_keys
    )
    bl005_only_keys = set(bl005_numeric_thresholds) - set(bl006_numeric_thresholds)
    bl006_only_keys = set(bl006_numeric_thresholds) - set(bl005_numeric_thresholds)
    allowed_bl006_only_keys = {"popularity"} if not bl005_popularity_enabled else set()
    threshold_coupling_pass = (
        shared_thresholds_match
        and not bl005_only_keys
        and bl006_only_keys.issubset(allowed_bl006_only_keys)
    )
    _add_check(
        checks,
        "contract_bl005_bl006_numeric_threshold_coupling",
        threshold_coupling_pass,
        "BL-005 and BL-006 numeric_thresholds are coupled (shared thresholds identical; BL-006-only popularity threshold allowed only when retrieval popularity is disabled)",
    )

    # Validate BL-009 emits upstream control-source matrix for traceability.
    upstream_sources = _nested_dict(bl009_log, "run_metadata", "upstream_stage_control_sources")
    expected_upstream_stages = {"BL-004", "BL-005", "BL-006", "BL-007", "BL-008"}
    _add_check(
        checks,
        "lineage_bl009_upstream_control_sources_present",
        expected_upstream_stages.issubset(set(upstream_sources.keys())),
        "BL-009 run metadata includes upstream stage control-source matrix",
    )

    # Validate BL-009 emits upstream run-config path matrix for traceability.
    upstream_run_config_paths = _nested_dict(bl009_log, "run_metadata", "upstream_stage_run_config_paths")
    _add_check(
        checks,
        "lineage_bl009_upstream_run_config_paths_present",
        expected_upstream_stages.issubset(set(upstream_run_config_paths.keys())),
        "BL-009 run metadata includes upstream stage run-config-path matrix",
    )

    # Validate BL-013 control-source summary is available and reports payload adoption.
    bl013_latest_summary_path = bl014_bl013_latest_summary_path(REPO_ROOT)
    if bl013_latest_summary_path.exists():
        bl013_latest_summary = load_json(bl013_latest_summary_path)
        control_source_summary = _nested_dict(bl013_latest_summary, "control_source_summary")
        payload_adoption_rate = float(control_source_summary.get("payload_adoption_rate", 0.0) or 0.0)
        _add_check(
            checks,
            "lineage_bl013_control_source_summary_present",
            bool(control_source_summary),
            "BL-013 latest summary includes control_source_summary block",
        )
        _add_check(
            checks,
            "lineage_bl013_payload_adoption_recorded",
            payload_adoption_rate > 0.0,
            "BL-013 control-source summary reports non-zero payload adoption",
        )

        schema_versions_non_null: dict[str, str] = {}
        bl003_run_config_schema = str(_nested_dict(bl003_summary, "inputs", "input_scope").get("schema_version") or "")
        if bl003_run_config_schema:
            schema_versions_non_null["BL-003"] = bl003_run_config_schema

        bl004_run_config_schema = str(bl004_summary.get("run_config_schema_version") or "")
        if bl004_run_config_schema:
            schema_versions_non_null["BL-004"] = bl004_run_config_schema

        run_effective_path_raw = _nested_dict(
            bl013_latest_summary,
            "canonical_run_config_artifacts",
            "run_effective_config",
        ).get("path")
        if isinstance(run_effective_path_raw, str) and run_effective_path_raw.strip():
            run_effective_path = Path(run_effective_path_raw)
            if run_effective_path.exists():
                run_effective_payload = load_json(run_effective_path)
                run_effective_schema = str(run_effective_payload.get("schema_version") or "")
                if run_effective_schema:
                    schema_versions_non_null["BL-013-effective"] = run_effective_schema

        distinct_versions = sorted(set(schema_versions_non_null.values()))
        _add_check(
            checks,
            "lineage_run_config_schema_version_consistency_non_null",
            bool(schema_versions_non_null) and len(distinct_versions) == 1,
            (
                "Non-null run-config schema versions are consistent across upstream artifacts: "
                f"{schema_versions_non_null}"
            ),
        )
    else:
        _add_check(
            checks,
            "lineage_bl013_control_source_summary_present",
            False,
            "BL-013 latest summary is missing",
        )

    bl003_fuzzy = _nested_dict(bl003_summary, "inputs", "fuzzy_matching")
    bl003_counts = _nested_dict(bl003_summary, "counts")
    bl009_fuzzy = _nested_dict(bl009_log, "run_config", "alignment_seed_controls", "fuzzy_matching")
    bl009_alignment_counts = _nested_dict(bl009_log, "stage_diagnostics", "alignment", "counts")

    _add_check(
        checks,
        "continuity_bl009_fuzzy_controls",
        bl009_fuzzy == bl003_fuzzy,
        "BL-009 run_config alignment fuzzy controls mirror BL-003 summary",
    )

    _add_check(
        checks,
        "continuity_bl009_fuzzy_count",
        int(bl009_alignment_counts.get("matched_by_fuzzy", 0)) == int(bl003_counts.get("matched_by_fuzzy", 0)),
        "BL-009 alignment diagnostics matched_by_fuzzy aligns with BL-003 summary",
    )

    fuzzy_enabled = bool(bl003_fuzzy.get("enabled", False))
    matched_by_fuzzy = int(bl003_counts.get("matched_by_fuzzy", 0))
    _add_check(
        checks,
        "continuity_bl003_fuzzy_enabled_consistency",
        matched_by_fuzzy == 0 if not fuzzy_enabled else matched_by_fuzzy >= 0,
        "BL-003 matched_by_fuzzy is zero when fuzzy is disabled",
    )

    bl005_kept = int(bl005_diag["counts"]["kept_candidates"])
    bl005_rows = _csv_row_count(artifacts["bl005_filtered"])
    bl005_candidate_rows_total = int(_nested_dict(bl005_diag, "counts").get("candidate_rows_total", 0))
    candidate_stub_rows = _csv_row_count(candidate_stub_path)
    _add_check(
        checks,
        "continuity_bl005_count",
        bl005_kept == bl005_rows,
        f"BL-005 kept_candidates ({bl005_kept}) equals filtered CSV rows ({bl005_rows})",
    )
    _add_check(
        checks,
        "continuity_bl005_candidate_total_count",
        bl005_candidate_rows_total == candidate_stub_rows,
        (
            "BL-005 candidate_rows_total "
            f"({bl005_candidate_rows_total}) equals candidate dataset rows ({candidate_stub_rows})"
        ),
    )

    bl003_seed_table_rows = int(bl003_counts.get("seed_table_rows", 0))
    bl004_matched_seed_count = int(bl004_summary.get("matched_seed_count", 0))
    bl004_seed_trace_rows = _csv_row_count(artifacts["bl004_seed_trace"])
    _add_check(
        checks,
        "continuity_bl003_bl004_seed_table_rows",
        bl003_seed_table_rows == bl004_matched_seed_count,
        (
            "BL-003 seed_table_rows "
            f"({bl003_seed_table_rows}) equals BL-004 matched_seed_count ({bl004_matched_seed_count})"
        ),
    )
    _add_check(
        checks,
        "continuity_bl004_seed_trace_rows",
        bl004_seed_trace_rows == bl004_matched_seed_count,
        (
            "BL-004 seed trace rows "
            f"({bl004_seed_trace_rows}) equals BL-004 matched_seed_count ({bl004_matched_seed_count})"
        ),
    )

    bl006_scored_count = int(bl006_summary["counts"]["candidates_scored"])
    bl006_rows = _csv_row_count(artifacts["bl006_scored"])
    _add_check(
        checks,
        "continuity_bl006_count",
        bl006_scored_count == bl006_rows,
        f"BL-006 candidates_scored ({bl006_scored_count}) equals scored CSV rows ({bl006_rows})",
    )

    playlist_len = int(playlist["playlist_length"])
    bl007_target_size = int((playlist.get("config") or {}).get("target_size", playlist_len))
    undersized_shortfall = max(0, bl007_target_size - playlist_len)
    undersized_playlist = undersized_shortfall > 0
    explanations_len = int(bl008_payloads["playlist_track_count"])
    _add_check(
        checks,
        "continuity_bl007_bl008_counts",
        playlist_len == len(playlist["tracks"]) == explanations_len == len(bl008_payloads["explanations"]),
        "BL-007 playlist length and BL-008 explanation count are aligned",
    )

    _add_check(
        checks,
        "quality_bl007_target_size_met",
        playlist_len >= bl007_target_size,
        f"BL-007 playlist length ({playlist_len}) meets target_size ({bl007_target_size})",
    )

    _add_check(
        checks,
        "continuity_bl009_index_counts",
        int(bl009_index["kept_candidates"]) == bl005_kept
        and int(bl009_index["candidates_scored"]) == bl006_scored_count
        and int(bl009_index["playlist_length"]) == playlist_len
        and int(bl009_index["explanation_count"]) == explanations_len,
        "BL-009 index counts match BL-005/006/007/008 outputs",
    )

    _add_check(
        checks,
        "continuity_bl009_run_ids",
        bl009_index["profile_run_id"] == bl004_summary["run_id"]
        and bl009_index["retrieval_run_id"] == bl005_diag["run_id"]
        and bl009_index["scoring_run_id"] == bl006_summary["run_id"]
        and bl009_index["assembly_run_id"] == bl007_report["run_id"]
        and bl009_index["transparency_run_id"] == bl008_summary["run_id"],
        "BL-009 index run_ids match upstream stage run_ids",
    )

    # Phase B: Contract-evolution compatibility adapters at stage boundaries
    # These checks allow graceful evolution of stage contracts without requiring rigid coupling.

    # BL-003 → BL-004 boundary: Profile schema version compatibility mapping
    bl003_schema_version = str(bl003_summary.get("artifact_contract_version", ""))
    bl004_schema_version = str(bl004_summary.get("output_contract_version", ""))
    both_schemas_non_empty = bool(bl003_schema_version) and bool(bl004_schema_version)
    _add_check(
        checks,
        "compat_bl003_bl004_schema_versions_present",
        both_schemas_non_empty,
        (
            "BL-003→BL-004 boundary: both schemas present for compatibility mapping "
            f"(BL-003={bl003_schema_version}, BL-004={bl004_schema_version})"
        ),
    )

    # BL-004 → BL-005 boundary: Profile structure availability for retrieval
    bl004_profile_required_keys = {"semantic_profile", "numeric_feature_profile"}
    bl004_has_required_structure = bl004_profile_required_keys.issubset(set(profile.keys()))
    bl005_expects_profile = bl005_diag is not None and isinstance(bl005_diag, dict)
    _add_check(
        checks,
        "compat_bl004_bl005_profile_structure",
        bl004_has_required_structure and bl005_expects_profile,
        (
            "BL-004→BL-005 boundary: profile has required structure "
            f"for retrieval input (has_required_keys={bl004_has_required_structure}, "
            f"bl005_expects_profile={bl005_expects_profile})"
        ),
    )

    # BL-005 → BL-006 boundary: Candidate dataset continuity and scoring readiness
    bl006_input_candidates = int(bl006_summary.get("counts", {}).get("candidates_scored", 0))
    bl005_output_candidates = bl005_kept
    candidates_continuity = bl006_input_candidates == bl005_output_candidates
    _add_check(
        checks,
        "compat_bl005_bl006_candidate_continuity",
        candidates_continuity,
        (
            "BL-005→BL-006 boundary: candidate count continuity maintained "
            f"(BL-005 kept={bl005_output_candidates}, BL-006 scored={bl006_input_candidates})"
        ),
    )

    if undersized_playlist:
        advisories.append(
            {
                "id": "advisory_bl007_undersized_playlist",
                "details": (
                    f"BL-007 produced {playlist_len}/{bl007_target_size} tracks "
                    f"(shortfall={undersized_shortfall}). Review BL-007 assembly report "
                    "undersized_playlist_warning for exclusion pressures."
                ),
            }
        )

    bl003_seed_health = _nested_dict(bl003_summary, "counts", "seed_aggregation_health")
    if str(bl003_seed_health.get("status", "pass")).lower() != "pass":
        advisories.append(
            {
                "id": "advisory_bl003_seed_aggregation_health",
                "details": (
                    "BL-003 seed aggregation health is in warning state: "
                    f"status={bl003_seed_health.get('status')}, "
                    f"aggregation_ratio={bl003_seed_health.get('aggregation_ratio')}"
                ),
            }
        )

    bl004_confidence_health = _nested_dict(bl004_summary, "confidence_input_health")
    if str(bl004_confidence_health.get("status", "pass")).lower() != "pass":
        advisories.append(
            {
                "id": "advisory_bl004_confidence_input_health",
                "details": (
                    "BL-004 confidence input health is in warning state: "
                    f"status={bl004_confidence_health.get('status')}, "
                    f"confidence_non_fallback_rate={bl004_confidence_health.get('confidence_non_fallback_rate')}"
                ),
            }
        )

    bl006_score_range = _nested_dict(bl006_summary, "score_distribution_diagnostics", "score_range")
    if str(bl006_score_range.get("spread_status", "pass")).lower() != "pass":
        advisories.append(
            {
                "id": "advisory_bl006_score_spread",
                "details": (
                    "BL-006 score spread advisory indicates low spread: "
                    f"spread_ratio={bl006_score_range.get('spread_ratio')}, "
                    f"threshold={bl006_score_range.get('spread_warn_threshold')}"
                ),
            }
        )

    bl007_pressure_diag = _nested_dict(bl007_report, "assembly_pressure_diagnostics")
    if str(bl007_pressure_diag.get("exclusion_ratio_status", "pass")).lower() != "pass":
        advisories.append(
            {
                "id": "advisory_bl007_assembly_pressure_ratio",
                "details": (
                    "BL-007 assembly pressure ratio is in warning state: "
                    f"top_100_exclusion_ratio={bl007_pressure_diag.get('top_100_exclusion_ratio')}, "
                    f"threshold={bl007_pressure_diag.get('exclusion_ratio_warn_threshold')}"
                ),
            }
        )

    passed, failed = _check_counts(checks)
    overall_status = "pass" if failed == 0 else "fail"

    finished = datetime.now(UTC)
    elapsed_seconds = round((finished - started).total_seconds(), 3)

    report = {
        "run_id": run_id,
        "task": "BL-014",
        "generated_at_utc": format_utc_iso(finished),
        "elapsed_seconds": elapsed_seconds,
        "overall_status": overall_status,
        "checks_total": len(checks),
        "checks_passed": passed,
        "checks_failed": failed,
        "advisories_total": len(advisories),
        "advisories": advisories,
        "artifact_hashes_sha256": {k: v for k, v in hashes.items()},
        "checks": _checks_as_rows(checks),
    }

    config_snapshot = {
        "task": "BL-014",
        "description": "Automated sanity checks for BL-020 artifact schema, hash linkage, and count continuity",
        "run_id": run_id,
        "required_artifacts": {k: str(v.relative_to(REPO_ROOT)) for k, v in artifacts.items()},
        "schema_checks": [
            "BL-003 summary top-level keys",
            "BL-004 summary top-level keys",
            "BL-005 filtered CSV required columns",
            "BL-005 decisions CSV required columns",
            "BL-006 scored CSV required columns",
            "BL-007 playlist length consistency",
            "BL-008 explanation count consistency",
            "BL-009 required top-level observability sections",
            "BL-003 fuzzy control block presence",
            "BL-003 seed aggregation health block presence",
            "BL-004 confidence diagnostics block presence",
            "BL-006 spread diagnostics block presence",
            "BL-007 pressure ratio diagnostics block presence",
        ],
        "integrity_checks": [
            "BL-004 seed table hash links to BL-003 seed table",
            "BL-005 input/output hashes",
            "BL-006 input/output hashes",
            "BL-007 input/output hashes",
            "BL-008 input/output hashes",
            "BL-009 index hash linkage",
        ],
        "continuity_checks": [
            "BL-003 seed_table_rows aligns with BL-004 matched_seed_count",
            "BL-004 seed trace rows align with BL-004 matched_seed_count",
            "BL-005 candidate_rows_total matches candidate dataset rows",
            "BL-003 fuzzy enabled consistency against matched_by_fuzzy",
            "BL-009 fuzzy controls mirror BL-003 controls",
            "BL-009 fuzzy count mirrors BL-003 count",
            "BL-005 kept count matches filtered rows",
            "BL-006 scored count matches scored rows",
            "BL-007 playlist count aligns with BL-008 explanations",
            "BL-007 playlist meets configured target size",
            "BL-009 index counts align with upstream stage outputs",
            "BL-009 run_id linkage aligns with upstream stage summaries",
            "Non-null run-config schema versions are consistent across BL-003/BL-004/BL-013-effective artifacts",
        ],
        "compatibility_checks_phase_b": [
            "BL-003→BL-004 boundary: schema version compatibility mapping present",
            "BL-004→BL-005 boundary: profile structure available for retrieval input",
            "BL-005→BL-006 boundary: candidate count continuity maintained",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "bl014_sanity_report.json"
    config_path = OUTPUT_DIR / "bl014_sanity_config_snapshot.json"
    matrix_path = OUTPUT_DIR / "bl014_sanity_run_matrix.csv"

    write_json_ascii(report_path, report)
    write_json_ascii(config_path, config_snapshot)
    write_csv_rows(
        matrix_path,
        [
            {
                "run_id": run_id,
                "generated_at_utc": report["generated_at_utc"],
                "overall_status": overall_status,
                "checks_total": len(checks),
                "checks_passed": passed,
                "checks_failed": failed,
                "bl005_kept_candidates": bl005_kept,
                "bl006_candidates_scored": bl006_scored_count,
                "playlist_length": playlist_len,
                "bl007_target_size": bl007_target_size,
                "undersized_playlist": str(undersized_playlist).lower(),
                "undersized_shortfall": undersized_shortfall,
                "explanation_count": explanations_len,
                "bl003_fuzzy_enabled": str(fuzzy_enabled).lower(),
                "bl003_matched_by_fuzzy": matched_by_fuzzy,
                "bl009_run_id": bl009_index["run_id"],
                "playlist_sha256": hashes["playlist"],
                "bl008_payloads_sha256": hashes["bl008_payloads"],
                "bl009_log_sha256": hashes["bl009_log"],
            }
        ],
    )

    print(f"[BL-014] run_id={run_id}")
    print(f"[BL-014] overall_status={overall_status} checks_passed={passed}/{len(checks)}")
    print(f"[BL-014] report={report_path}")
    print(f"[BL-014] run_matrix={matrix_path}")
    print(f"[BL-014] config_snapshot={config_path}")

    return 0 if overall_status == "pass" else 1


def run_freshness_mode() -> int:
    started = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[CheckResult] = []

    bl010_module = _load_module(
        "reproducibility_check",
        REPO_ROOT / "reproducibility" / "main.py",
    )
    bl011_module = _load_module(
        "controllability_check",
        REPO_ROOT / "controllability" / "main.py",
    )

    freshness_paths = bl014_freshness_input_paths(REPO_ROOT)
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

    run_config_path: str | None = None
    bl013_latest_path = bl014_bl013_latest_summary_path(REPO_ROOT)
    if bl013_latest_path.exists():
        bl013_latest = load_json(bl013_latest_path)
        raw_run_config_path = bl013_latest.get("run_config_path")
        if isinstance(raw_run_config_path, str) and raw_run_config_path.strip():
            run_config_path = raw_run_config_path.strip()

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
    current_bl011_snapshot = _build_current_bl011_snapshot(
        bl011_module,
        paths_bl011=paths_bl011,
        current_bl010_snapshot=current_bl010_snapshot,
        run_config_path=run_config_path,
    )
    current_bl011_hash = bl011_module.canonical_json_hash(current_bl011_snapshot)
    stored_bl011_snapshot_hash = bl011_module.canonical_json_hash(stored_bl011_snapshot)

    _add_check(
        checks,
        "bl010_snapshot_matches_current_contract",
        stored_bl010_snapshot_hash == current_bl010_hash,
        "BL-010 config snapshot matches the current active-pipeline reproducibility contract",
    )
    _add_check(
        checks,
        "bl010_report_hash_matches_current_contract",
        str(stored_bl010_report["run_metadata"]["config_hash"]) == current_bl010_hash,
        "BL-010 report config_hash matches the current active-pipeline reproducibility contract",
    )
    _add_check(
        checks,
        "bl010_fixed_input_hashes_match_current",
        stored_bl010_report["inputs"]["fixed_input_hashes"] == current_bl010_snapshot["fixed_inputs"],
        "BL-010 fixed input hashes match the current active pipeline outputs",
    )
    _add_check(
        checks,
        "bl010_stage_script_hashes_match_current",
        stored_bl010_report["inputs"]["stage_scripts"] == current_bl010_snapshot["stage_scripts"],
        "BL-010 stage script hashes match the current BL-004 to BL-009 code",
    )
    _add_check(
        checks,
        "bl010_active_mode",
        str(stored_bl010_report["run_metadata"]["fixed_input_source"]) == "active_pipeline_outputs",
        "BL-010 evidence mode matches requested freshness mode input source",
    )
    _add_check(
        checks,
        "bl011_snapshot_matches_current_contract",
        stored_bl011_snapshot_hash == current_bl011_hash,
        "BL-011 config snapshot matches the current active controllability contract",
    )
    _add_check(
        checks,
        "bl011_baseline_hash_matches_current_bl010",
        str(stored_bl011_report["run_metadata"]["baseline_config_hash"]) == current_bl010_hash,
        "BL-011 baseline_config_hash matches the current BL-010 baseline snapshot",
    )
    _add_check(
        checks,
        "bl011_fixed_input_hashes_match_current",
        stored_bl011_report["inputs"]["fixed_input_hashes"] == current_bl011_snapshot["fixed_inputs"],
        "BL-011 fixed input hashes match the current active controllability inputs",
    )
    _add_check(
        checks,
        "bl011_active_mode",
        str(stored_bl011_snapshot["input_source"]) == "active_pipeline_outputs",
        "BL-011 evidence mode matches requested freshness mode input source",
    )

    overall_status = "pass" if all(item.status == "pass" for item in checks) else "fail"
    report_path = OUTPUT_DIR / "bl010_bl011_freshness_report.json"
    matrix_path = OUTPUT_DIR / "bl010_bl011_freshness_matrix.csv"
    _write_suite_artifacts(
        run_id=f"BL-FRESHNESS-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}",
        task="BL-010/011 freshness check",
        elapsed_seconds=round(time.time() - started, 3),
        overall_status=overall_status,
        evidence_paths={
            "bl010_config_snapshot": _safe_relpath(freshness_paths["bl010_snapshot"]),
            "bl010_report": _safe_relpath(freshness_paths["bl010_report"]),
            "bl011_config_snapshot": _safe_relpath(freshness_paths["bl011_snapshot"]),
            "bl011_report": _safe_relpath(freshness_paths["bl011_report"]),
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

    checks: list[CheckResult] = []

    bl013_latest_path = bl014_bl013_latest_summary_path(REPO_ROOT)
    if not bl013_latest_path.exists():
        raise FileNotFoundError(f"Missing BL-013 latest summary: {bl013_latest_path}")
    bl013_latest = load_json(bl013_latest_path)
    pre_bl013_run_id = str(bl013_latest.get("run_id", ""))
    pre_bl013_generated_at = parse_utc_iso(bl013_latest.get("generated_at_utc"))

    freshness_paths = bl014_freshness_input_paths(REPO_ROOT)
    ensure_paths_exist(
        [
            freshness_paths["bl010_report"],
            freshness_paths["bl011_report"],
            freshness_paths["bl011_snapshot"],
        ],
        stage_label="BL-014",
        label="active-mode lineage inputs",
        root=REPO_ROOT,
    )
    pre_bl010_report = load_json(freshness_paths["bl010_report"])
    pre_bl011_report = load_json(freshness_paths["bl011_report"])
    bl011_snapshot = load_json(freshness_paths["bl011_snapshot"])

    pre_bl010_run_id = str(_nested_dict(pre_bl010_report, "run_metadata").get("run_id", ""))
    pre_bl011_run_id = str(_nested_dict(pre_bl011_report, "run_metadata").get("run_id", ""))

    _add_check(
        checks,
        "bl013_latest_pass",
        str(bl013_latest.get("overall_status")) == "pass",
        "BL-013 latest orchestration summary reports overall_status=pass",
    )
    _add_check(
        checks,
        "bl013_latest_no_failed_stages",
        int(bl013_latest.get("failed_stage_count", -1)) == 0,
        "BL-013 latest orchestration summary reports failed_stage_count=0",
    )

    bl014_return, bl014_output = _run_python_script(QUALITY_DIR / "main.py", args=["--mode", "sanity"])
    _add_check(
        checks,
        "bl014_script_exit_zero",
        bl014_return == 0,
        f"BL-014 sanity check script return code={bl014_return}",
    )

    bl014_report_path = OUTPUT_DIR / "bl014_sanity_report.json"
    if not bl014_report_path.exists():
        raise FileNotFoundError(f"Missing BL-014 report: {bl014_report_path}")
    bl014_report = load_json(bl014_report_path)
    _add_check(
        checks,
        "bl014_report_pass",
        str(bl014_report.get("overall_status")) == "pass",
        "BL-014 report overall_status is pass",
    )

    refinement_paths = bl014_refinement_diagnostic_paths(REPO_ROOT)
    bl006_distribution_path = refinement_paths["bl006_distribution"]
    bl007_report_path = refinement_paths["bl007_assembly_report"]

    _add_check(
        checks,
        "bl006_distribution_diagnostics_available",
        bl006_distribution_path.exists(),
        f"BL-006 distribution diagnostics present at {_safe_relpath(bl006_distribution_path)}",
    )
    _add_check(
        checks,
        "bl007_assembly_pressure_diagnostics_available",
        bl007_report_path.exists(),
        f"BL-007 assembly report present at {_safe_relpath(bl007_report_path)}",
    )

    if bl006_distribution_path.exists():
        bl006_distribution = load_json(bl006_distribution_path)
        rank_cliff = bl006_distribution.get("rank_cliff", {})
        score_range = _nested_dict(bl006_distribution, "score_range")
        _add_check(
            checks,
            "bl006_rank_cliff_advisory",
            True,
            (
                "BL-006 rank-cliff advisory: "
                f"detected={bool(rank_cliff.get('detected', False))}, "
                f"rank_2_to_3_gap={rank_cliff.get('rank_2_to_3_gap', 0.0)}"
            ),
        )
        _add_check(
            checks,
            "bl006_score_spread_advisory",
            True,
            (
                "BL-006 score spread advisory: "
                f"spread_ratio={score_range.get('spread_ratio')}, "
                f"spread_status={score_range.get('spread_status')}"
            ),
        )

    if bl007_report_path.exists():
        bl007_report = load_json(bl007_report_path)
        rank_diag = bl007_report.get("rank_continuity_diagnostics", {})
        pressure_diag = bl007_report.get("assembly_pressure_diagnostics", {})
        _add_check(
            checks,
            "bl007_rank_continuity_advisory",
            True,
            (
                "BL-007 rank continuity advisory: "
                f"max_selected_rank={rank_diag.get('max_selected_rank')}, "
                f"rank_2_to_3_score_gap={rank_diag.get('rank_2_to_3_score_gap')}"
            ),
        )
        _add_check(
            checks,
            "bl007_assembly_pressure_advisory",
            True,
            (
                "BL-007 assembly pressure advisory: "
                f"top_100_excluded={pressure_diag.get('top_100_excluded')}, "
                f"dominant_reason={pressure_diag.get('dominant_top_100_exclusion_reason')}"
            ),
        )
        _add_check(
            checks,
            "bl007_assembly_pressure_ratio_advisory",
            True,
            (
                "BL-007 assembly pressure ratio advisory: "
                f"top_100_exclusion_ratio={pressure_diag.get('top_100_exclusion_ratio')}, "
                f"status={pressure_diag.get('exclusion_ratio_status')}"
            ),
        )

    refresh_outputs: dict[str, str] = {}
    freshness_initial_return = run_freshness_mode()
    freshness_return = freshness_initial_return
    freshness_post_refresh_return: int | None = None
    freshness_refresh_attempted = False
    freshness_auto_refreshed = False
    refresh_result: RefreshResult | None = None

    if freshness_initial_return != 0:
        freshness_refresh_attempted = True
        refresh_result = _refresh_bl010_bl011_evidence()
        refresh_return = int(refresh_result.combined_return_code)
        refresh_outputs = dict(refresh_result.outputs)

        _add_check(
            checks,
            "bl010_refresh_exit_zero",
            int(refresh_result.bl010_return_code) == 0,
            f"BL-010 evidence refresh return code={refresh_result.bl010_return_code}",
        )
        _add_check(
            checks,
            "bl013_refresh_exit_zero",
            refresh_result.bl013_ran and refresh_result.bl013_return_code is not None and int(refresh_result.bl013_return_code) == 0,
            (
                f"BL-013 pipeline reapply return code={refresh_result.bl013_return_code}"
                if refresh_result.bl013_ran
                else "BL-013 pipeline reapply was skipped because BL-010 refresh failed"
            ),
        )
        _add_check(
            checks,
            "bl011_refresh_exit_zero",
            refresh_result.bl011_ran and refresh_result.bl011_return_code is not None and int(refresh_result.bl011_return_code) == 0,
            (
                f"BL-011 evidence refresh return code={refresh_result.bl011_return_code}"
                if refresh_result.bl011_ran
                else "BL-011 evidence refresh was skipped because BL-010 refresh failed"
            ),
        )
        _add_check(
            checks,
            "bl013_post_bl011_refresh_exit_zero",
            (not refresh_result.bl013_post_bl011_ran)
            or (
                refresh_result.bl013_post_bl011_return_code is not None
                and int(refresh_result.bl013_post_bl011_return_code) == 0
            ),
            (
                f"BL-013 post-BL-011 pipeline reapply return code={refresh_result.bl013_post_bl011_return_code}"
                if refresh_result.bl013_post_bl011_ran
                else "BL-013 post-BL-011 pipeline reapply not required after successful BL-011 refresh"
            ),
        )

        _add_check(
            checks,
            "bl010_bl011_refresh_exit_zero",
            refresh_return == 0,
            f"BL-010/BL-011 evidence refresh return code={refresh_return}",
        )
        if refresh_return == 0:
            freshness_return = run_freshness_mode()
            freshness_post_refresh_return = freshness_return
            freshness_auto_refreshed = freshness_return == 0

    _add_check(
        checks,
        "bl010_bl011_stale_detected",
        True,
        (
            "BL-010/BL-011 freshness was stale before active-suite checks"
            if freshness_initial_return != 0
            else "BL-010/BL-011 freshness was already up-to-date before active-suite checks"
        ),
    )

    _add_check(
        checks,
        "bl010_bl011_freshness_exit_zero",
        freshness_return == 0,
        f"BL-010/BL-011 freshness script return code={freshness_return}",
    )

    freshness_report_path = OUTPUT_DIR / "bl010_bl011_freshness_report.json"
    if not freshness_report_path.exists():
        raise FileNotFoundError(f"Missing BL-010/011 freshness report: {freshness_report_path}")
    freshness_report = load_json(freshness_report_path)
    _add_check(
        checks,
        "bl010_bl011_freshness_report_pass",
        str((freshness_report.get("run_metadata") or {}).get("overall_status")) == "pass",
        "BL-010/BL-011 freshness report overall_status is pass",
    )

    post_bl010_report = load_json(freshness_paths["bl010_report"])
    post_bl011_report = load_json(freshness_paths["bl011_report"])
    post_bl013_latest = load_json(bl013_latest_path)

    post_bl010_run_metadata = _nested_dict(post_bl010_report, "run_metadata")
    post_bl011_run_metadata = _nested_dict(post_bl011_report, "run_metadata")
    post_bl010_run_id = str(post_bl010_run_metadata.get("run_id", ""))
    post_bl011_run_id = str(post_bl011_run_metadata.get("run_id", ""))
    post_bl013_run_id = str(post_bl013_latest.get("run_id", ""))

    post_bl010_generated_at = parse_utc_iso(post_bl010_run_metadata.get("generated_at_utc"))
    post_bl011_generated_at = parse_utc_iso(post_bl011_run_metadata.get("generated_at_utc"))
    post_bl013_generated_at = parse_utc_iso(post_bl013_latest.get("generated_at_utc"))

    _add_check(
        checks,
        "lineage_bl011_baseline_matches_bl010_report",
        str(post_bl011_run_metadata.get("baseline_config_hash")) == str(post_bl010_run_metadata.get("config_hash")),
        "BL-011 report baseline_config_hash matches BL-010 report config_hash",
    )

    bl013_run_config_path = str(post_bl013_latest.get("run_config_path") or "")
    bl011_runtime_run_config_path = str(_nested_dict(bl011_snapshot, "runtime_controls").get("run_config_path") or "")
    _add_check(
        checks,
        "lineage_bl013_bl011_run_config_path_consistency",
        bool(bl013_run_config_path) and bl013_run_config_path == bl011_runtime_run_config_path,
        "BL-013 latest run_config_path is consistent with BL-011 runtime control run_config_path",
    )

    _add_check(
        checks,
        "lineage_bl011_not_older_than_bl010",
        post_bl010_generated_at is not None
        and post_bl011_generated_at is not None
        and post_bl011_generated_at >= post_bl010_generated_at,
        "BL-011 evidence timestamp is newer than or equal to BL-010 evidence timestamp",
    )

    if freshness_refresh_attempted:
        _add_check(
            checks,
            "staleness_bl010_report_advanced_after_refresh",
            post_bl010_run_id != pre_bl010_run_id,
            "BL-010 report run_id advanced after stale freshness auto-refresh",
        )
        _add_check(
            checks,
            "staleness_bl011_report_advanced_after_refresh",
            post_bl011_run_id != pre_bl011_run_id,
            "BL-011 report run_id advanced after stale freshness auto-refresh",
        )
        _add_check(
            checks,
            "convergence_bl013_latest_not_regressed_after_refresh",
            (
                pre_bl013_generated_at is None
                or post_bl013_generated_at is None
                or post_bl013_generated_at >= pre_bl013_generated_at
            )
            and bool(post_bl013_run_id),
            "BL-013 latest summary did not regress after stale freshness auto-refresh",
        )
        if refresh_result is not None and refresh_result.bl013_post_bl011_ran:
            _add_check(
                checks,
                "convergence_bl013_post_bl011_ordering",
                post_bl013_generated_at is not None
                and post_bl011_generated_at is not None
                and post_bl013_generated_at >= post_bl011_generated_at,
                "When BL-013 is rerun post BL-011 refresh, BL-013 latest summary timestamp is newer than BL-011",
            )
    _add_check(
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
        _add_check(
            checks,
            "bl010_bl011_freshness_post_refresh_exit_zero",
            freshness_post_refresh_return == 0,
            f"BL-010/BL-011 post-refresh freshness return code={freshness_post_refresh_return}",
        )

    overall_status = "pass" if all(item.status == "pass" for item in checks) else "fail"
    run_id = f"BL-FRESHNESS-SUITE-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"

    report_path = OUTPUT_DIR / "bl_active_freshness_suite_report.json"
    matrix_path = OUTPUT_DIR / "bl_active_freshness_suite_matrix.csv"
    _write_suite_artifacts(
        run_id=run_id,
        task="active freshness suite",
        elapsed_seconds=round(time.time() - started, 3),
        overall_status=overall_status,
        evidence_paths={
            "bl013_latest_summary": _safe_relpath(bl013_latest_path),
            "bl014_report": _safe_relpath(bl014_report_path),
            "bl010_bl011_freshness_report": _safe_relpath(freshness_report_path),
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
                    "bl010_return_code": None if refresh_result is None else refresh_result.bl010_return_code,
                    "bl011_return_code": None if refresh_result is None else refresh_result.bl011_return_code,
                    "combined_return_code": None if refresh_result is None else refresh_result.combined_return_code,
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
        choices=["sanity", "freshness", "active"],
        default="active",
        help="Run BL-014 sanity checks, BL-010/011 freshness only, or full active suite",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "sanity":
        return run_sanity_mode()
    if args.mode == "freshness":
        return run_freshness_mode()
    return run_active_mode()


if __name__ == "__main__":
    raise SystemExit(main())
