from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.hashing import canonical_json_hash as shared_canonical_json_hash
from bl000_shared_utils.hashing import sha256_of_file
from bl000_shared_utils.io_utils import load_csv_rows
from bl000_shared_utils.io_utils import load_json
from bl000_shared_utils.path_utils import repo_root
from bl000_shared_utils.report_utils import write_csv_rows, write_json_ascii


DEFAULT_REPLAY_COUNT = 3


def canonical_json_hash(payload: object, *, uppercase: bool = True) -> str:
    """Preserve BL-010 historical default of uppercase JSON hash output."""
    return shared_canonical_json_hash(payload, uppercase=uppercase)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BL-010 reproducibility replay for BL-004 to BL-009 outputs."
    )
    parser.add_argument(
        "--replay-count",
        type=int,
        default=DEFAULT_REPLAY_COUNT,
        help="Number of BL-004..BL-009 replay cycles to execute (default: 3).",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to run stage scripts.",
    )
    parser.add_argument(
        "--output-dir",
        default="07_implementation/implementation_notes/bl010_reproducibility/outputs",
        help="Directory for reproducibility report artifacts.",
    )
    parser.add_argument(
        "--run-config",
        default=None,
        help="Optional run-config path forwarded to BL-004..BL-009 replay stages.",
    )
    return parser.parse_args()


def ensure_positive_replay_count(value: int) -> int:
    if value < 1:
        raise ValueError(f"--replay-count must be >= 1, got {value}")
    return value


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    last_error: OSError | None = None

    for _ in range(3):
        try:
            shutil.copy2(src, dst)
            return
        except OSError as exc:
            last_error = exc
            is_windows_retryable = os.name == "nt" and (
                getattr(exc, "winerror", None) == 1224 or exc.errno == 22
            )
            if not is_windows_retryable:
                raise
            time.sleep(0.05)

    source_bytes = src.read_bytes()
    normalized_dst = os.path.abspath(os.path.normpath(str(dst))).replace("/", "\\")
    for _ in range(3):
        try:
            with open(normalized_dst, "wb") as handle:
                handle.write(source_bytes)
            try:
                shutil.copystat(src, Path(normalized_dst))
            except OSError:
                pass
            return
        except OSError as exc:
            last_error = exc
            is_windows_retryable = os.name == "nt" and (
                getattr(exc, "winerror", None) == 1224 or exc.errno == 22
            )
            if not is_windows_retryable:
                raise
            time.sleep(0.05)

    raise last_error if last_error is not None else RuntimeError("Unexpected copy failure")


def build_file_hash_map(paths: dict[str, Path], keys: list[str]) -> dict[str, str]:
    return {key: sha256_of_file(paths[key], uppercase=True) for key in keys}


def build_paths(root: Path) -> dict[str, Path]:
    return {
        "bl004_script": root / "07_implementation" / "implementation_notes" / "bl004_profile" / "build_bl004_preference_profile.py",
        "bl005_script": root / "07_implementation" / "implementation_notes" / "bl005_retrieval" / "build_bl005_candidate_filter.py",
        "bl006_script": root / "07_implementation" / "implementation_notes" / "bl006_scoring" / "build_bl006_scored_candidates.py",
        "bl007_script": root / "07_implementation" / "implementation_notes" / "bl007_playlist" / "build_bl007_playlist.py",
        "bl008_script": root / "07_implementation" / "implementation_notes" / "bl008_transparency" / "build_bl008_explanation_payloads.py",
        "bl009_script": root / "07_implementation" / "implementation_notes" / "bl009_observability" / "build_bl009_observability_log.py",
        "bl004_profile": root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs" / "bl004_preference_profile.json",
        "bl004_summary": root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs" / "bl004_profile_summary.json",
        "bl004_seed_trace": root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs" / "bl004_seed_trace.csv",
        "bl005_filtered": root / "07_implementation" / "implementation_notes" / "bl005_retrieval" / "outputs" / "bl005_filtered_candidates.csv",
        "bl005_decisions": root / "07_implementation" / "implementation_notes" / "bl005_retrieval" / "outputs" / "bl005_candidate_decisions.csv",
        "bl005_diagnostics": root / "07_implementation" / "implementation_notes" / "bl005_retrieval" / "outputs" / "bl005_candidate_diagnostics.json",
        "bl006_scored": root / "07_implementation" / "implementation_notes" / "bl006_scoring" / "outputs" / "bl006_scored_candidates.csv",
        "bl006_summary": root / "07_implementation" / "implementation_notes" / "bl006_scoring" / "outputs" / "bl006_score_summary.json",
        "bl007_playlist": root / "07_implementation" / "implementation_notes" / "bl007_playlist" / "outputs" / "bl007_playlist.json",
        "bl007_trace": root / "07_implementation" / "implementation_notes" / "bl007_playlist" / "outputs" / "bl007_assembly_trace.csv",
        "bl007_report": root / "07_implementation" / "implementation_notes" / "bl007_playlist" / "outputs" / "bl007_assembly_report.json",
        "bl008_payloads": root / "07_implementation" / "implementation_notes" / "bl008_transparency" / "outputs" / "bl008_explanation_payloads.json",
        "bl008_summary": root / "07_implementation" / "implementation_notes" / "bl008_transparency" / "outputs" / "bl008_explanation_summary.json",
        "bl009_log": root / "07_implementation" / "implementation_notes" / "bl009_observability" / "outputs" / "bl009_run_observability_log.json",
        "bl009_index": root / "07_implementation" / "implementation_notes" / "bl009_observability" / "outputs" / "bl009_run_index.csv",
    }


def ensure_required_inputs(paths: dict[str, Path], root: Path) -> None:
    required_keys = list(paths.keys())
    missing = [relpath(paths[key], root) for key in required_keys if not paths[key].exists()]
    if missing:
        raise FileNotFoundError(f"BL-010 missing required inputs: {missing}")


def build_config_snapshot(
    paths: dict[str, Path],
    root: Path,
    replay_count: int = DEFAULT_REPLAY_COUNT,
) -> dict:
    bl004_profile = load_json(paths["bl004_profile"])
    bl005_diagnostics = load_json(paths["bl005_diagnostics"])
    bl006_summary = load_json(paths["bl006_summary"])
    bl007_report = load_json(paths["bl007_report"])
    bl008_summary = load_json(paths["bl008_summary"])

    fixed_input_source = "active_pipeline_outputs"
    fixed_input_keys = [
        "bl004_seed_trace",
        "bl005_filtered",
        "bl005_decisions",
        "bl006_scored",
        "bl007_trace",
    ]

    fixed_inputs = {
        relpath(paths[key], root): sha256_of_file(paths[key], uppercase=True)
        for key in fixed_input_keys
    }
    stage_script_keys = ["bl004_script", "bl005_script", "bl006_script", "bl007_script", "bl008_script", "bl009_script"]
    stage_scripts = {
        relpath(paths[key], root): digest
        for key, digest in build_file_hash_map(paths, stage_script_keys).items()
    }

    return {
        "task": "BL-010",
        "bootstrap_mode": False,
        "fixed_input_source": fixed_input_source,
        "replay_count": int(replay_count),
        "fixed_inputs": fixed_inputs,
        "optional_dependency_availability": {},
        "stage_scripts": stage_scripts,
        "stage_order": ["BL-004", "BL-005", "BL-006", "BL-007", "BL-008", "BL-009"],
        "stage_configs": {
            "profile": bl004_profile["config"],
            "retrieval": bl005_diagnostics["config"],
            "scoring": bl006_summary["config"],
            "assembly": bl007_report["config"],
            "transparency": {
                "playlist_track_count": bl008_summary["playlist_track_count"],
                "top_contributor_distribution": bl008_summary["top_contributor_distribution"],
            },
        },
    }


def stable_profile_fingerprint(profile: dict, summary: dict) -> str:
    payload = {
        "user_id": profile["user_id"],
        "config": profile["config"],
        "diagnostics": {
            "events_total": profile["diagnostics"]["events_total"],
            "matched_seed_count": profile["diagnostics"]["matched_seed_count"],
            "missing_seed_count": profile["diagnostics"]["missing_seed_count"],
            "candidate_rows_total": profile["diagnostics"]["candidate_rows_total"],
            "total_effective_weight": profile["diagnostics"]["total_effective_weight"],
        },
        "seed_summary": profile["seed_summary"],
        "numeric_feature_profile": profile["numeric_feature_profile"],
        "semantic_profile": profile["semantic_profile"],
        "summary": {
            "matched_seed_count": summary["matched_seed_count"],
            "total_effective_weight": summary["total_effective_weight"],
            "dominant_lead_genres": summary["dominant_lead_genres"],
            "dominant_tags": summary["dominant_tags"],
            "dominant_genres": summary["dominant_genres"],
            "feature_centers": summary["feature_centers"],
        },
    }
    return canonical_json_hash(payload, uppercase=True)


def stable_playlist_fingerprint(playlist: dict) -> str:
    return canonical_json_hash(playlist["tracks"], uppercase=True)


def stable_explanations_fingerprint(payloads: dict) -> str:
    return canonical_json_hash(payloads["explanations"], uppercase=True)


def stable_observability_fingerprint(run_log: dict, playlist_stable_hash: str, explanations_stable_hash: str) -> str:
    stage_diagnostics = run_log["stage_diagnostics"]
    stable_profile = {
        key: value
        for key, value in stage_diagnostics["profile"].items()
        if key != "run_id"
    }
    stable_profile["diagnostics"] = {
        key: value
        for key, value in stable_profile["diagnostics"].items()
        if key != "elapsed_seconds"
    }
    stable_stage_diagnostics = {
        "data_layer": stage_diagnostics["data_layer"],
        "bootstrap_assets": stage_diagnostics["bootstrap_assets"],
        "profile": stable_profile,
        "retrieval": {
            key: value
            for key, value in stage_diagnostics["retrieval"].items()
            if key != "run_id"
        },
        "scoring": {
            key: value
            for key, value in stage_diagnostics["scoring"].items()
            if key != "run_id"
        },
        "assembly": {
            key: value
            for key, value in stage_diagnostics["assembly"].items()
            if key != "run_id"
        },
        "transparency": {
            key: value
            for key, value in stage_diagnostics["transparency"].items()
            if key != "run_id"
        },
    }
    payload = {
        "dataset_version": run_log["run_metadata"]["dataset_version"],
        "pipeline_version": run_log["run_metadata"]["pipeline_version"],
        "bootstrap_mode": run_log["run_metadata"]["bootstrap_mode"],
        "run_config": run_log["run_config"],
        "ingestion_alignment_diagnostics": run_log["ingestion_alignment_diagnostics"],
        "stage_diagnostics": stable_stage_diagnostics,
        "exclusion_diagnostics": run_log["exclusion_diagnostics"],
        "stable_outputs": {
            "playlist_content_hash": playlist_stable_hash,
            "explanation_content_hash": explanations_stable_hash,
        },
    }
    return canonical_json_hash(payload, uppercase=True)


def fingerprint_outputs(paths: dict[str, Path]) -> dict[str, object]:
    bl004_profile = load_json(paths["bl004_profile"])
    bl004_summary = load_json(paths["bl004_summary"])
    bl007_playlist = load_json(paths["bl007_playlist"])
    bl008_payloads = load_json(paths["bl008_payloads"])
    bl009_log = load_json(paths["bl009_log"])
    bl009_index_rows = load_csv_rows(paths["bl009_index"])

    playlist_track_ids = [track["track_id"] for track in bl007_playlist["tracks"]]
    explanation_track_ids = [item["track_id"] for item in bl008_payloads["explanations"]]
    playlist_stable_hash = stable_playlist_fingerprint(bl007_playlist)
    explanation_stable_hash = stable_explanations_fingerprint(bl008_payloads)
    observability_stable_hash = stable_observability_fingerprint(
        bl009_log,
        playlist_stable_hash=playlist_stable_hash,
        explanations_stable_hash=explanation_stable_hash,
    )

    raw_hash_map = build_file_hash_map(
        paths,
        [
            "bl004_seed_trace",
            "bl005_filtered",
            "bl005_decisions",
            "bl006_scored",
            "bl007_trace",
            "bl007_playlist",
            "bl008_payloads",
            "bl009_log",
            "bl009_index",
        ],
    )

    return {
        "stage_run_ids": {
            "BL-004": bl004_profile["run_id"],
            "BL-005": load_json(paths["bl005_diagnostics"])["run_id"],
            "BL-006": load_json(paths["bl006_summary"])["run_id"],
            "BL-007": load_json(paths["bl007_report"])["run_id"],
            "BL-008": load_json(paths["bl008_summary"])["run_id"],
            "BL-009": bl009_log["run_metadata"]["run_id"],
        },
        "raw_hashes": {
            "bl004_seed_trace": raw_hash_map["bl004_seed_trace"],
            "bl005_filtered": raw_hash_map["bl005_filtered"],
            "bl005_decisions": raw_hash_map["bl005_decisions"],
            "bl006_scored": raw_hash_map["bl006_scored"],
            "bl007_trace": raw_hash_map["bl007_trace"],
            "bl007_playlist": raw_hash_map["bl007_playlist"],
            "bl008_payloads": raw_hash_map["bl008_payloads"],
            "bl009_log": raw_hash_map["bl009_log"],
            "bl009_index": raw_hash_map["bl009_index"],
        },
        "stable_hashes": {
            "profile_semantic_hash": stable_profile_fingerprint(bl004_profile, bl004_summary),
            "ranked_output_hash": raw_hash_map["bl006_scored"],
            "playlist_output_hash": playlist_stable_hash,
            "explanation_output_hash": explanation_stable_hash,
            "observability_output_hash": observability_stable_hash,
            "seed_trace_hash": raw_hash_map["bl004_seed_trace"],
            "candidate_decisions_hash": raw_hash_map["bl005_decisions"],
            "filtered_candidates_hash": raw_hash_map["bl005_filtered"],
            "assembly_trace_hash": raw_hash_map["bl007_trace"],
        },
        "semantic_snapshots": {
            "playlist_track_ids": playlist_track_ids,
            "explanation_track_ids": explanation_track_ids,
            "observability_dataset_version": bl009_log["run_metadata"]["dataset_version"],
            "observability_pipeline_version": bl009_log["run_metadata"]["pipeline_version"],
            "observability_index_row": bl009_index_rows[0] if bl009_index_rows else {},
        },
    }


def _canonicalize_stage_stdout_lines(stdout: str, root: Path) -> list[str]:
    root_with_sep = str(root) + "\\"
    canonical_lines: list[str] = []
    for line in stdout.strip().splitlines():
        normalized = line.strip()
        normalized = normalized.replace(root_with_sep, "")
        normalized = normalized.replace("\\", "/")
        canonical_lines.append(normalized)
    return canonical_lines


def run_stage(
    stage_id: str,
    script_path: Path,
    root: Path,
    python_executable: str,
    run_config_path: str | None,
) -> dict[str, object]:
    started = time.time()
    command = [python_executable, str(script_path)]
    if run_config_path:
        command.extend(["--run-config", run_config_path])
    completed: subprocess.CompletedProcess[str] | None = None
    attempts: list[dict[str, object]] = []
    for attempt in range(1, 4):
        attempt_started = time.time()
        completed = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        attempts.append(
            {
                "attempt_number": attempt,
                "return_code": completed.returncode,
                "elapsed_seconds": round(time.time() - attempt_started, 3),
                "stdout": _canonicalize_stage_stdout_lines(completed.stdout or "", root),
                "stderr": _canonicalize_stage_stdout_lines(completed.stderr or "", root),
            }
        )
        if completed.returncode == 0:
            break
        if attempt < 3:
            time.sleep(0.1)
    if completed is None or completed.returncode != 0:
        serialized_attempts = json.dumps(attempts, indent=2, ensure_ascii=True)
        raise RuntimeError(
            f"BL-010 stage {stage_id} failed after retries: {script_path.name}\n"
            f"attempts:\n{serialized_attempts}"
        )
    canonical_script_path = relpath(script_path, root)
    final_attempt = attempts[-1]
    command_suffix = f" --run-config {run_config_path}" if run_config_path else ""
    return {
        "stage": stage_id,
        "script": script_path.name,
        "script_path": canonical_script_path,
        "command": f"python {canonical_script_path}{command_suffix}",
        "elapsed_seconds": round(time.time() - started, 3),
        "stdout": list(final_attempt["stdout"]),
        "stderr": list(final_attempt["stderr"]),
        "attempt_count": len(attempts),
        "had_retry": len(attempts) > 1,
        "attempts": attempts,
    }


def build_stage_sequence(paths: dict[str, Path]) -> list[tuple[str, Path]]:
    return [
        ("BL-004", paths["bl004_script"]),
        ("BL-005", paths["bl005_script"]),
        ("BL-006", paths["bl006_script"]),
        ("BL-007", paths["bl007_script"]),
        ("BL-008", paths["bl008_script"]),
        ("BL-009", paths["bl009_script"]),
    ]


def execute_replays(
    *,
    replay_count: int,
    stage_sequence: list[tuple[str, Path]],
    python_executable: str,
    root: Path,
    output_dir: Path,
    paths: dict[str, Path],
    run_config_path: str | None,
) -> list[dict[str, object]]:
    replay_records: list[dict[str, object]] = []
    for replay_number in range(1, replay_count + 1):
        stage_runs = [
            run_stage(stage_id, script_path, root, python_executable, run_config_path)
            for stage_id, script_path in stage_sequence
        ]
        fingerprints = fingerprint_outputs(paths)

        replay_dir = output_dir / f"replay_{replay_number:02d}"
        replay_dir.mkdir(parents=True, exist_ok=True)
        archive_replay_outputs(paths, replay_dir)

        replay_records.append(
            {
                "replay_number": replay_number,
                "stage_runs": stage_runs,
                "stage_run_ids": fingerprints["stage_run_ids"],
                "raw_hashes": fingerprints["raw_hashes"],
                "stable_hashes": fingerprints["stable_hashes"],
                "semantic_snapshots": fingerprints["semantic_snapshots"],
                "archive_dir": relpath(replay_dir, root),
            }
        )
    return replay_records


def archive_replay_outputs(paths: dict[str, Path], replay_dir: Path) -> None:
    archive_map = {
        "bl004_preference_profile.json": paths["bl004_profile"],
        "bl004_profile_summary.json": paths["bl004_summary"],
        "bl004_seed_trace.csv": paths["bl004_seed_trace"],
        "bl005_filtered_candidates.csv": paths["bl005_filtered"],
        "bl005_candidate_decisions.csv": paths["bl005_decisions"],
        "bl005_candidate_diagnostics.json": paths["bl005_diagnostics"],
        "bl006_scored_candidates.csv": paths["bl006_scored"],
        "bl006_score_summary.json": paths["bl006_summary"],
        "bl007_playlist.json": paths["bl007_playlist"],
        "bl007_assembly_trace.csv": paths["bl007_trace"],
        "bl007_assembly_report.json": paths["bl007_report"],
        "bl008_explanation_payloads.json": paths["bl008_payloads"],
        "bl008_explanation_summary.json": paths["bl008_summary"],
        "bl009_run_observability_log.json": paths["bl009_log"],
        "bl009_run_index.csv": paths["bl009_index"],
    }
    for filename, source_path in archive_map.items():
        copy_file(source_path, replay_dir / filename)


def first_mismatch(stable_hashes_by_run: list[dict[str, str]]) -> str | None:
    if not stable_hashes_by_run:
        return None
    baseline = stable_hashes_by_run[0]
    for artifact_name in baseline:
        expected = baseline[artifact_name]
        for candidate in stable_hashes_by_run[1:]:
            if candidate[artifact_name] != expected:
                return artifact_name
    return None


def main() -> None:
    args = parse_args()
    root = repo_root()
    replay_count = ensure_positive_replay_count(int(args.replay_count))
    output_dir = (root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = build_paths(root)
    ensure_required_inputs(paths, root)

    config_snapshot = build_config_snapshot(
        paths,
        root,
        replay_count=replay_count,
    )
    config_hash = canonical_json_hash(config_snapshot, uppercase=True)
    config_path = output_dir / "bl010_reproducibility_config_snapshot.json"
    write_json_ascii(config_path, config_snapshot)

    run_started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_id = f"BL010-REPRO-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    started = time.time()

    stage_sequence = build_stage_sequence(paths)
    replay_records = execute_replays(
        replay_count=replay_count,
        stage_sequence=stage_sequence,
        python_executable=str(args.python),
        root=root,
        output_dir=output_dir,
        paths=paths,
        run_config_path=str(args.run_config) if args.run_config else None,
    )

    stable_hashes_by_run = [record["stable_hashes"] for record in replay_records]
    baseline_stable = stable_hashes_by_run[0]
    deterministic_match = all(candidate == baseline_stable for candidate in stable_hashes_by_run[1:])
    first_mismatch_artifact = first_mismatch(stable_hashes_by_run)

    raw_playlist_hash_match = len({record["raw_hashes"]["bl007_playlist"] for record in replay_records}) == 1
    raw_explanation_hash_match = len({record["raw_hashes"]["bl008_payloads"] for record in replay_records}) == 1
    raw_observability_hash_match = len({record["raw_hashes"]["bl009_log"] for record in replay_records}) == 1
    all_stage_runs = [stage_run for record in replay_records for stage_run in record["stage_runs"]]
    stage_runs_with_retries = [
        {
            "replay_number": record["replay_number"],
            "stage": stage_run["stage"],
            "attempt_count": stage_run["attempt_count"],
        }
        for record in replay_records
        for stage_run in record["stage_runs"]
        if bool(stage_run.get("had_retry"))
    ]

    summary_rows: list[dict[str, object]] = []
    for record in replay_records:
        retry_count = sum(1 for stage_run in record["stage_runs"] if bool(stage_run.get("had_retry")))
        row = {
            "replay_number": record["replay_number"],
            "bl004_run_id": record["stage_run_ids"]["BL-004"],
            "bl005_run_id": record["stage_run_ids"]["BL-005"],
            "bl006_run_id": record["stage_run_ids"]["BL-006"],
            "bl007_run_id": record["stage_run_ids"]["BL-007"],
            "bl008_run_id": record["stage_run_ids"]["BL-008"],
            "bl009_run_id": record["stage_run_ids"]["BL-009"],
            "ranked_output_hash": record["stable_hashes"]["ranked_output_hash"],
            "playlist_output_hash": record["stable_hashes"]["playlist_output_hash"],
            "explanation_output_hash": record["stable_hashes"]["explanation_output_hash"],
            "observability_output_hash": record["stable_hashes"]["observability_output_hash"],
            "raw_playlist_hash": record["raw_hashes"]["bl007_playlist"],
            "raw_explanation_hash": record["raw_hashes"]["bl008_payloads"],
            "raw_observability_hash": record["raw_hashes"]["bl009_log"],
            "dataset_version": record["semantic_snapshots"]["observability_dataset_version"],
            "pipeline_version": record["semantic_snapshots"]["observability_pipeline_version"],
            "stage_retry_count": retry_count,
            "archive_dir": record["archive_dir"],
        }
        summary_rows.append(row)

    summary_csv_path = output_dir / "bl010_reproducibility_run_matrix.csv"
    write_csv_rows(summary_csv_path, summary_rows)

    report = {
        "run_metadata": {
            "run_id": run_id,
            "task": "BL-010",
            "generated_at_utc": run_started_at,
            "elapsed_seconds": round(time.time() - started, 3),
            "replay_count": replay_count,
            "bootstrap_mode": bool(config_snapshot["bootstrap_mode"]),
            "config_hash": config_hash,
            "fixed_input_source": config_snapshot["fixed_input_source"],
        },
        "inputs": {
            "config_snapshot_path": relpath(config_path, root),
            "fixed_input_hashes": config_snapshot["fixed_inputs"],
            "stage_scripts": config_snapshot["stage_scripts"],
        },
        "replay_scope": {
            "stage_order": config_snapshot["stage_order"],
            "stable_comparison_artifacts": [
                "profile_semantic_hash",
                "seed_trace_hash",
                "filtered_candidates_hash",
                "candidate_decisions_hash",
                "ranked_output_hash",
                "assembly_trace_hash",
                "playlist_output_hash",
                "explanation_output_hash",
                "observability_output_hash",
            ],
            "volatile_raw_artifacts": [
                "bl007_playlist.json",
                "bl008_explanation_payloads.json",
                "bl009_run_observability_log.json",
            ],
        },
        "replays": replay_records,
        "results": {
            "deterministic_match": deterministic_match,
            "status": "pass" if deterministic_match else "fail",
            "first_mismatch_artifact": first_mismatch_artifact,
            "stable_hash_reference": baseline_stable,
            "raw_metadata_hash_checks": {
                "bl007_playlist_raw_hash_match": raw_playlist_hash_match,
                "bl008_payloads_raw_hash_match": raw_explanation_hash_match,
                "bl009_log_raw_hash_match": raw_observability_hash_match,
            },
            "observed_reason_for_raw_hash_variation": "run_id, generated_at_utc, elapsed_seconds, and upstream run linkage fields vary across identical replays even when stable recommendation content remains unchanged",
            "playlist_track_ids_match": len({tuple(record["semantic_snapshots"]["playlist_track_ids"]) for record in replay_records}) == 1,
            "explanation_track_ids_match": len({tuple(record["semantic_snapshots"]["explanation_track_ids"]) for record in replay_records}) == 1,
            "dataset_version_match": len({record["semantic_snapshots"]["observability_dataset_version"] for record in replay_records}) == 1,
            "pipeline_version_match": len({record["semantic_snapshots"]["observability_pipeline_version"] for record in replay_records}) == 1,
            "all_stage_runs_succeeded_without_retry": all(not bool(stage_run.get("had_retry")) for stage_run in all_stage_runs),
            "replay_count_with_retries": len({item["replay_number"] for item in stage_runs_with_retries}),
            "stages_requiring_retry": stage_runs_with_retries,
        },
        "output_artifacts": {
            "config_snapshot_path": relpath(config_path, root),
            "run_matrix_path": relpath(summary_csv_path, root),
            "archived_replay_dirs": [record["archive_dir"] for record in replay_records],
        },
    }

    report_path = output_dir / "bl010_reproducibility_report.json"
    write_json_ascii(report_path, report)

    print("BL-010 reproducibility replay complete.")
    print(f"run_id={run_id}")
    print(f"deterministic_match={deterministic_match}")
    print(f"config_hash={config_hash}")
    print(f"report={report_path}")
    print(f"run_matrix={summary_csv_path}")


if __name__ == "__main__":
    main()