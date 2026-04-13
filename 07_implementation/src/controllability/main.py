from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timezone


from controllability.input_validation import validate_bl010_baseline_snapshot
from shared_utils.io_utils import (
    canonical_json_hash,
    load_csv_rows,
    sha256_of_file,
    utc_now,
)
from controllability.scenarios import (
    build_paths,
    build_scenarios,
    ensure_required_inputs,
    resolve_bl011_runtime_controls,
)
from controllability.analysis import (
    build_baseline_comparison,
    compare_to_baseline,
    evaluate_results_status,
)
from controllability.reporting import (
    csv_text,
    json_text,
    write_scenario_outputs,
)
from controllability.pipeline_runner import (
    build_active_seed_events,
    execute_scenario,
)
from shared_utils.parsing import normalize_candidate_row, safe_int
from shared_utils.path_utils import impl_root
from shared_utils.report_utils import write_text
from shared_utils.stage_utils import ensure_required_keys, load_required_json_object, relpath

logger = logging.getLogger(__name__)


def _mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BL-011 controllability evaluation for BL-004 to BL-007 behavior shifts."
    )
    return parser.parse_args()


def ensure_baseline_snapshot_shape(snapshot: dict) -> None:
    ensure_required_keys(snapshot, ["stage_configs"], label="baseline snapshot", stage_label="BL-011")
    stage_configs = snapshot.get("stage_configs")
    if not isinstance(stage_configs, dict):
        raise RuntimeError("BL-011 baseline snapshot field stage_configs must be a JSON object")
    ensure_required_keys(stage_configs, ["profile", "retrieval", "scoring", "assembly"], label="baseline stage_configs", stage_label="BL-011")


def main() -> None:
    parse_args()
    root = impl_root()
    runtime_controls = resolve_bl011_runtime_controls()
    paths = build_paths(root)
    ensure_required_inputs(paths, root)

    output_dir = paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "scenarios").mkdir(parents=True, exist_ok=True)

    baseline_snapshot = load_required_json_object(paths["baseline_snapshot"], label="BL-010 baseline snapshot", stage_label="BL-011")
    ensure_baseline_snapshot_shape(baseline_snapshot)

    # Validate BL-010 baseline snapshot structure before scenario building
    validation_policy = str(runtime_controls.get("bl010_bl011_handshake_validation_policy", "warn"))
    validation_result = validate_bl010_baseline_snapshot(baseline_snapshot, validation_policy)

    if validation_result["status"] == "fail":
        raise RuntimeError(
            f"BL-011 controllability validation failed: {validation_result['violations']}"
        )
    elif validation_result["status"] == "warn":
        logger.warning(f"BL-011 validation warnings: {validation_result['violations']}")

    bl003_summary = load_required_json_object(paths["bl003_summary"], label="BL-003 alignment summary", stage_label="BL-011")
    ensure_required_keys(bl003_summary, ["inputs", "counts"], label="BL-003 alignment summary", stage_label="BL-011")
    bl003_inputs = _mapping(bl003_summary.get("inputs"))
    alignment_fuzzy_controls = _mapping(bl003_inputs.get("fuzzy_matching"))
    alignment_counts = _mapping(bl003_summary.get("counts"))
    seed_rows = load_csv_rows(paths["active_seed_trace"])
    events = build_active_seed_events(seed_rows)
    candidate_rows = [normalize_candidate_row(row) for row in load_csv_rows(paths["active_candidates"])]
    input_artifacts = {
        "aligned_events_path": relpath(paths["active_seed_trace"], root),
        "candidate_stub_path": relpath(paths["active_candidates"], root),
    }

    candidate_rows_by_id = {row["track_id"]: row for row in candidate_rows}

    baseline_config_hash = canonical_json_hash(baseline_snapshot)
    scenarios = build_scenarios(baseline_snapshot, runtime_controls)

    fixed_inputs = {
        relpath(paths["bl003_summary"], root): sha256_of_file(paths["bl003_summary"]),
        input_artifacts["aligned_events_path"]: sha256_of_file(paths["active_seed_trace"]),
        input_artifacts["candidate_stub_path"]: sha256_of_file(paths["active_candidates"]),
    }
    optional_inputs = {
        "legacy_manifest": paths["legacy_manifest"],
        "legacy_coverage": paths["legacy_coverage"],
    }
    for path in optional_inputs.values():
        if path.exists():
            fixed_inputs[relpath(path, root)] = sha256_of_file(path)

    config_snapshot = {
        "task": "BL-011",
        "generated_from": relpath(paths["baseline_snapshot"], root),
        "baseline_config_hash": baseline_config_hash,
        "input_source": "active_pipeline_outputs",
        "alignment_seed_controls": {
            "fuzzy_matching": alignment_fuzzy_controls,
        },
        "alignment_counts": {
            "input_event_rows": safe_int(alignment_counts.get("input_event_rows"), 0),
            "matched_by_spotify_id": safe_int(alignment_counts.get("matched_by_spotify_id"), 0),
            "matched_by_metadata": safe_int(alignment_counts.get("matched_by_metadata"), 0),
            "matched_by_fuzzy": safe_int(alignment_counts.get("matched_by_fuzzy"), 0),
            "unmatched": safe_int(alignment_counts.get("unmatched"), 0),
            "seed_table_rows": safe_int(alignment_counts.get("seed_table_rows"), 0),
        },
        "fixed_inputs": fixed_inputs,
        "optional_dependency_availability": {
            key: {
                "path": relpath(path, root),
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
    config_snapshot_path = output_dir / "controllability_config_snapshot.json"
    write_text(config_snapshot_path, json_text(config_snapshot))

    run_started = time.time()
    run_id = f"BL011-CTRL-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    scenario_records: list[dict[str, object]] = []

    for scenario in scenarios:
        first_run = execute_scenario(scenario, events, candidate_rows, candidate_rows_by_id, root, input_artifacts)
        second_run = execute_scenario(scenario, events, candidate_rows, candidate_rows_by_id, root, input_artifacts)
        repeat_consistent = first_run["stable_hashes"] == second_run["stable_hashes"]
        write_scenario_outputs(output_dir, first_run)

        scenario_dir = output_dir / "scenarios" / str(first_run["scenario_id"])
        scenario_records.append(
            {
                **first_run,
                "repeat_consistent": repeat_consistent,
                "archive_dir": relpath(scenario_dir, root),
            }
        )

    baseline_result = next(record for record in scenario_records if record["scenario_id"] == "baseline")
    for record in scenario_records:
        if record["scenario_id"] == "baseline":
            record["comparison_to_baseline"] = build_baseline_comparison(baseline_result)
        else:
            record["comparison_to_baseline"] = compare_to_baseline(baseline_result, record)

    matrix_rows = []
    for record in scenario_records:
        comparison = _mapping(record.get("comparison_to_baseline"))
        metrics = _mapping(record.get("metrics"))
        rank_shift_summary = _mapping(comparison.get("rank_shift_summary"))
        stable_hashes = _mapping(record.get("stable_hashes"))
        matrix_rows.append(
            {
                "scenario_id": record["scenario_id"],
                "test_id": record["test_id"],
                "control_surface": record["control_surface"],
                "repeat_consistent": record["repeat_consistent"],
                "config_hash": record["config_hash"],
                "candidate_pool_size": metrics.get("candidate_pool_size"),
                "candidate_pool_size_delta": comparison.get("candidate_pool_size_delta"),
                "playlist_length": metrics.get("playlist_length"),
                "top10_overlap_count": comparison.get("top10_overlap_count"),
                "playlist_overlap_count": comparison.get("playlist_overlap_count"),
                "mean_abs_rank_delta": rank_shift_summary.get("mean_abs_rank_delta"),
                "observable_shift": comparison.get("observable_shift"),
                "expected_direction_met": comparison.get("expected_direction_met"),
                "profile_semantic_hash": stable_hashes.get("profile_semantic_hash"),
                "ranked_output_hash": stable_hashes.get("ranked_output_hash"),
                "playlist_output_hash": stable_hashes.get("playlist_output_hash"),
                "archive_dir": record["archive_dir"],
                "alignment_fuzzy_enabled": bool(alignment_fuzzy_controls.get("enabled", False)),
                "alignment_matched_by_fuzzy": safe_int(alignment_counts.get("matched_by_fuzzy"), 0),
            }
        )

    run_matrix_path = output_dir / "controllability_run_matrix.csv"
    write_text(run_matrix_path, csv_text(list(matrix_rows[0].keys()), matrix_rows))

    scenario_report_records = []
    for record in scenario_records:
        scenario_report_records.append(
            {
                "scenario_id": record["scenario_id"],
                "test_id": record["test_id"],
                "control_surface": record["control_surface"],
                "description": record["description"],
                "expected_effect": record["expected_effect"],
                "repeat_consistent": record["repeat_consistent"],
                "config_hash": record["config_hash"],
                "effective_config": record["effective_config"],
                "stable_hashes": record["stable_hashes"],
                "metrics": {
                    key: value for key, value in _mapping(record.get("metrics")).items() if key != "rank_map"
                },
                "comparison_to_baseline": record["comparison_to_baseline"],
                "archive_dir": record["archive_dir"],
            }
        )

    results_summary = evaluate_results_status(scenario_records)

    def _expects_no_shift(record: dict[str, object]) -> bool:
        expected_effect = str(record.get("expected_effect", "")).lower()
        scenario_id = str(record.get("scenario_id", "")).strip().lower()
        return ("no shift" in expected_effect) or ("not expected" in expected_effect) or scenario_id in {"fuzzy_enabled_strict"}

    no_op_control_diagnostics = []
    for record in scenario_records:
        if record.get("scenario_id") == "baseline":
            continue
        comparison = _mapping(record.get("comparison_to_baseline"))
        observable_shift = bool(comparison.get("observable_shift", False))
        if (not observable_shift) and (not _expects_no_shift(record)):
            no_op_control_diagnostics.append(
                {
                    "scenario_id": record.get("scenario_id"),
                    "control_surface": record.get("control_surface"),
                    "expected_effect": record.get("expected_effect"),
                    "candidate_pool_size_delta": comparison.get("candidate_pool_size_delta"),
                    "playlist_overlap_ratio": comparison.get("playlist_overlap_ratio"),
                }
            )

    report = {
        "run_metadata": {
            "run_id": run_id,
            "task": "BL-011",
            "generated_at_utc": utc_now(),
            "elapsed_seconds": round(time.time() - run_started, 3),
            "baseline_config_hash": baseline_config_hash,
            "scenario_count": len(scenario_records),
        },
        "validation": {
            "policy": validation_result["policy"],
            "status": validation_result["status"],
            "violations": validation_result["violations"],
            "details": validation_result["details"],
        },
        "inputs": {
            "baseline_snapshot_path": relpath(paths["baseline_snapshot"], root),
            "alignment_summary_path": relpath(paths["bl003_summary"], root),
            "controllability_config_snapshot_path": relpath(config_snapshot_path, root),
            "fixed_input_hashes": config_snapshot["fixed_inputs"],
        },
        "scope": {
            "evaluation_tests": ["EP-CTRL-001", "EP-CTRL-002", "EP-CTRL-003"],
            "scenario_ids": [record["scenario_id"] for record in scenario_records],
            "stage_scope": ["BL-004", "BL-005", "BL-006", "BL-007"],
            "repeat_method": "each scenario was executed twice with identical parameters and compared via stable stage hashes",
        },
        "scenario_results": scenario_report_records,
        "results": {
            **results_summary,
            "no_op_control_diagnostics": no_op_control_diagnostics,
            "no_op_controls_count": len(no_op_control_diagnostics),
        },
        "output_artifacts": {
            "config_snapshot_path": relpath(config_snapshot_path, root),
            "run_matrix_path": relpath(run_matrix_path, root),
            "scenario_dirs": [record["archive_dir"] for record in scenario_records],
        },
    }
    report_path = output_dir / "controllability_report.json"
    write_text(report_path, json_text(report))

    print("BL-011 controllability evaluation complete.")
    print(f"run_id={run_id}")
    print(f"status={report['results']['status']}")
    print(f"report={report_path}")
    print(f"run_matrix={run_matrix_path}")


if __name__ == "__main__":
    main()
