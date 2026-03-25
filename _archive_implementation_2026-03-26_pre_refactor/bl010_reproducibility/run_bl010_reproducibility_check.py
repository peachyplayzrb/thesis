from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


REPLAY_COUNT = 3

LEGACY_FIXED_INPUT_KEYS = [
    "bl016_events",
    "bl016_candidates",
    "bl016_manifest",
    "bl017_coverage",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BL-010 reproducibility replay for BL-004 to BL-009 outputs."
    )
    parser.add_argument(
        "--allow-legacy-surrogate-inputs",
        action="store_true",
        help=(
            "Opt in to legacy surrogate assets (BL-016/BL-017) when available. "
            "Default uses active pipeline outputs only."
        ),
    )
    return parser.parse_args()


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def canonical_json_hash(payload: object) -> str:
    return sha256_of_text(json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":")))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_paths(root: Path) -> dict[str, Path]:
    return {
        "bl016_events": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_synthetic_aligned_events.jsonl",
        "bl016_candidates": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_candidate_stub.csv",
        "bl016_manifest": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_asset_manifest.json",
        "bl017_coverage": root / "07_implementation" / "implementation_notes" / "bl000_data_layer" / "outputs" / "onion_join_coverage_report.json",
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
    required_keys = [
        key
        for key in paths
        if key not in LEGACY_FIXED_INPUT_KEYS
    ]
    missing = [relpath(paths[key], root) for key in required_keys if not paths[key].exists()]
    if missing:
        raise FileNotFoundError(f"BL-010 missing required inputs: {missing}")


def build_config_snapshot(paths: dict[str, Path], root: Path, allow_legacy_surrogate_inputs: bool) -> dict:
    bl004_profile = load_json(paths["bl004_profile"])
    bl005_diagnostics = load_json(paths["bl005_diagnostics"])
    bl006_summary = load_json(paths["bl006_summary"])
    bl007_report = load_json(paths["bl007_report"])
    bl008_summary = load_json(paths["bl008_summary"])

    has_legacy_fixed_inputs = allow_legacy_surrogate_inputs and all(paths[key].exists() for key in LEGACY_FIXED_INPUT_KEYS)
    if has_legacy_fixed_inputs:
        fixed_input_source = "legacy_surrogate_assets"
        fixed_input_keys = list(LEGACY_FIXED_INPUT_KEYS)
    else:
        fixed_input_source = "active_pipeline_outputs"
        fixed_input_keys = [
            "bl004_seed_trace",
            "bl005_filtered",
            "bl005_decisions",
            "bl006_scored",
            "bl007_trace",
        ]

    fixed_inputs = {
        relpath(paths[key], root): sha256_of_file(paths[key])
        for key in fixed_input_keys
    }
    stage_scripts = {
        relpath(paths[key], root): sha256_of_file(paths[key])
        for key in ["bl004_script", "bl005_script", "bl006_script", "bl007_script", "bl008_script", "bl009_script"]
    }

    return {
        "task": "BL-010",
        "bootstrap_mode": has_legacy_fixed_inputs,
        "fixed_input_source": fixed_input_source,
        "replay_count": REPLAY_COUNT,
        "fixed_inputs": fixed_inputs,
        "optional_dependency_availability": {
            key: {
                "path": relpath(paths[key], root),
                "available": paths[key].exists(),
            }
            for key in LEGACY_FIXED_INPUT_KEYS
        },
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
    return canonical_json_hash(payload)


def stable_playlist_fingerprint(playlist: dict) -> str:
    return canonical_json_hash(playlist["tracks"])


def stable_explanations_fingerprint(payloads: dict) -> str:
    return canonical_json_hash(payloads["explanations"])


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
    return canonical_json_hash(payload)


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
            "bl004_seed_trace": sha256_of_file(paths["bl004_seed_trace"]),
            "bl005_filtered": sha256_of_file(paths["bl005_filtered"]),
            "bl005_decisions": sha256_of_file(paths["bl005_decisions"]),
            "bl006_scored": sha256_of_file(paths["bl006_scored"]),
            "bl007_trace": sha256_of_file(paths["bl007_trace"]),
            "bl007_playlist": sha256_of_file(paths["bl007_playlist"]),
            "bl008_payloads": sha256_of_file(paths["bl008_payloads"]),
            "bl009_log": sha256_of_file(paths["bl009_log"]),
            "bl009_index": sha256_of_file(paths["bl009_index"]),
        },
        "stable_hashes": {
            "profile_semantic_hash": stable_profile_fingerprint(bl004_profile, bl004_summary),
            "ranked_output_hash": sha256_of_file(paths["bl006_scored"]),
            "playlist_output_hash": playlist_stable_hash,
            "explanation_output_hash": explanation_stable_hash,
            "observability_output_hash": observability_stable_hash,
            "seed_trace_hash": sha256_of_file(paths["bl004_seed_trace"]),
            "candidate_decisions_hash": sha256_of_file(paths["bl005_decisions"]),
            "filtered_candidates_hash": sha256_of_file(paths["bl005_filtered"]),
            "assembly_trace_hash": sha256_of_file(paths["bl007_trace"]),
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


def run_stage(stage_id: str, script_path: Path, root: Path) -> dict[str, object]:
    started = time.time()
    command = [sys.executable, str(script_path)]
    completed = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    canonical_script_path = relpath(script_path, root)
    return {
        "stage": stage_id,
        "script": script_path.name,
        "script_path": canonical_script_path,
        "command": f"python {canonical_script_path}",
        "elapsed_seconds": round(time.time() - started, 3),
        "stdout": _canonicalize_stage_stdout_lines(completed.stdout, root),
    }


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
    output_dir = root / "07_implementation" / "implementation_notes" / "bl010_reproducibility" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = build_paths(root)
    ensure_required_inputs(paths, root)

    config_snapshot = build_config_snapshot(
        paths,
        root,
        allow_legacy_surrogate_inputs=bool(args.allow_legacy_surrogate_inputs),
    )
    config_hash = canonical_json_hash(config_snapshot)
    config_path = output_dir / "bl010_reproducibility_config_snapshot.json"
    config_path.write_text(json.dumps(config_snapshot, indent=2, ensure_ascii=True), encoding="utf-8")

    replay_records: list[dict[str, object]] = []
    run_started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_id = f"BL010-REPRO-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    started = time.time()

    stage_sequence = [
        ("BL-004", paths["bl004_script"]),
        ("BL-005", paths["bl005_script"]),
        ("BL-006", paths["bl006_script"]),
        ("BL-007", paths["bl007_script"]),
        ("BL-008", paths["bl008_script"]),
        ("BL-009", paths["bl009_script"]),
    ]

    for replay_number in range(1, REPLAY_COUNT + 1):
        stage_runs = [run_stage(stage_id, script_path, root) for stage_id, script_path in stage_sequence]
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

    stable_hashes_by_run = [record["stable_hashes"] for record in replay_records]
    baseline_stable = stable_hashes_by_run[0]
    deterministic_match = all(candidate == baseline_stable for candidate in stable_hashes_by_run[1:])
    first_mismatch_artifact = first_mismatch(stable_hashes_by_run)

    raw_playlist_hash_match = len({record["raw_hashes"]["bl007_playlist"] for record in replay_records}) == 1
    raw_explanation_hash_match = len({record["raw_hashes"]["bl008_payloads"] for record in replay_records}) == 1
    raw_observability_hash_match = len({record["raw_hashes"]["bl009_log"] for record in replay_records}) == 1

    summary_rows: list[dict[str, object]] = []
    for record in replay_records:
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
            "archive_dir": record["archive_dir"],
        }
        summary_rows.append(row)

    summary_csv_path = output_dir / "bl010_reproducibility_run_matrix.csv"
    with summary_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    report = {
        "run_metadata": {
            "run_id": run_id,
            "task": "BL-010",
            "generated_at_utc": run_started_at,
            "elapsed_seconds": round(time.time() - started, 3),
            "replay_count": REPLAY_COUNT,
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
        },
        "output_artifacts": {
            "config_snapshot_path": relpath(config_path, root),
            "run_matrix_path": relpath(summary_csv_path, root),
            "archived_replay_dirs": [record["archive_dir"] for record in replay_records],
        },
    }

    report_path = output_dir / "bl010_reproducibility_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    print("BL-010 reproducibility replay complete.")
    print(f"run_id={run_id}")
    print(f"deterministic_match={deterministic_match}")
    print(f"config_hash={config_hash}")
    print(f"report={report_path}")
    print(f"run_matrix={summary_csv_path}")


if __name__ == "__main__":
    main()