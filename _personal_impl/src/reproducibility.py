from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
import importlib.util
from pathlib import Path
from datetime import datetime, timezone

from shared.io_utils import load_json, sha256_of_file, utc_now
from shared.path_utils import impl_root


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def bl010_required_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "bl003_script": repo_root / "alignment.py",
        "bl004_script": repo_root / "profile.py",
        "bl005_script": repo_root / "retrieval.py",
        "bl006_script": repo_root / "scoring.py",
        "bl007_script": repo_root / "playlist.py",
        "bl008_script": repo_root / "transparency.py",
        "bl009_script": repo_root / "observability.py",
        "bl003_summary": repo_root / "alignment/outputs/bl003_ds001_spotify_summary.json",
        "bl003_seed_table": repo_root / "alignment/outputs/bl003_ds001_spotify_seed_table.csv",
        "profile": repo_root / "profile/outputs/bl004_preference_profile.json",
        "bl004_profile": repo_root / "profile/outputs/bl004_preference_profile.json",
        "bl004_summary": repo_root / "profile/outputs/profile_summary.json",
        "bl004_seed_trace": repo_root / "profile/outputs/bl004_seed_trace.csv",
        "bl005_filtered": repo_root / "retrieval/outputs/bl005_filtered_candidates.csv",
        "bl005_decisions": repo_root / "retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_diagnostics": repo_root / "retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl006_scored": repo_root / "scoring/outputs/bl006_scored_candidates.csv",
        "bl006_summary": repo_root / "scoring/outputs/bl006_score_summary.json",
        "playlist": repo_root / "playlist/outputs/playlist.json",
        "bl007_playlist": repo_root / "playlist/outputs/playlist.json",
        "bl007_trace": repo_root / "playlist/outputs/bl007_assembly_trace.csv",
        "bl007_report": repo_root / "playlist/outputs/bl007_assembly_report.json",
        "bl008_payloads": repo_root / "transparency/outputs/bl008_explanation_payloads.json",
        "bl008_summary": repo_root / "transparency/outputs/bl008_explanation_summary.json",
        "bl009_log": repo_root / "observability/outputs/bl009_run_observability_log.json",
        "bl009_index": repo_root / "observability/outputs/bl009_run_index.csv",
    }


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


DEFAULT_REPLAY_COUNT = 3


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _object_mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def _object_dict_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def build_signal_mode_calibration_snapshot(
    bl005_diagnostics: dict[str, object],
    bl006_summary: dict[str, object],
) -> dict[str, object]:
    retrieval_config = _object_mapping(bl005_diagnostics.get("config"))
    scoring_config = _object_mapping(bl006_summary.get("config"))
    signal_mode = _object_mapping(retrieval_config.get("signal_mode") or scoring_config.get("signal_mode"))
    popularity_profile = _object_mapping(signal_mode.get("popularity_profile"))
    component_weights = _object_mapping(scoring_config.get("base_component_weights"))

    return {
        "mode_name": signal_mode.get("name"),
        "semantic_profile": signal_mode.get("semantic_profile"),
        "numeric_profile": signal_mode.get("numeric_profile"),
        "retrieval_numeric_support_min_score": safe_float(retrieval_config.get("numeric_support_min_score"), 0.0),
        "retrieval_use_weighted_semantics": bool(retrieval_config.get("use_weighted_semantics", False)),
        "retrieval_use_continuous_numeric": bool(retrieval_config.get("use_continuous_numeric", False)),
        "retrieval_popularity_numeric_enabled": bool(popularity_profile.get("retrieval_enabled", False)),
        "scoring_popularity_weight": safe_float(component_weights.get("popularity"), 0.0),
        "scoring_popularity_enabled": bool(popularity_profile.get("scoring_enabled", False)),
    }


def canonical_json_hash(payload: object, *, uppercase: bool = True) -> str:
    """Preserve BL-010 historical default of uppercase JSON hash output."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return digest.upper() if uppercase else digest


def sha256_of_file(path: Path, *, uppercase: bool = False) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    result = digest.hexdigest()
    return result.upper() if uppercase else result


def impl_root(impl_root_override: str | None = None) -> Path:
    if impl_root_override:
        return Path(impl_root_override).resolve()
    env_root = os.environ.get("IMPL_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parents[1]


def load_run_config_utils_module() -> object:
    module_path = impl_root() / "run_config" / "run_config_utils.py"
    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        default="reproducibility/outputs",
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
        except Exception:
            if _ == 2:
                raise
            time.sleep(0.05)


            return


def build_signal_mode_replay_payload(
    *,
    paths: dict[str, Path],
    root: Path,
    replay_count: int = DEFAULT_REPLAY_COUNT,
) -> dict:
    bl003_summary = load_json(paths["bl003_summary"])
    profile = load_json(paths["profile"])
    bl005_diagnostics = load_json(paths["bl005_diagnostics"])
    bl006_summary = load_json(paths["bl006_summary"])
    bl007_report = load_json(paths["bl007_report"])
    bl008_summary = load_json(paths["bl008_summary"])

    fixed_input_source = "active_pipeline_outputs"
    fixed_input_keys = [
        "bl003_seed_table",
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
    stage_script_keys = ["bl003_script", "bl004_script", "bl005_script", "bl006_script", "bl007_script", "bl008_script", "bl009_script"]
    stage_scripts = {
        relpath(paths[key], root): digest
        for key, digest in build_file_hash_map(paths, stage_script_keys).items()
    }

    return {
        "task": "BL-010",
        "bootstrap_mode": False,
        "signal_mode": dict((bl005_diagnostics.get("config") or {}).get("signal_mode") or (bl006_summary.get("config") or {}).get("signal_mode") or {}),
        "signal_mode_calibration": build_signal_mode_calibration_snapshot(bl005_diagnostics, bl006_summary),
        "fixed_input_source": fixed_input_source,
        "replay_count": int(replay_count),
        "fixed_inputs": fixed_inputs,
        "optional_dependency_availability": {},
        "stage_scripts": stage_scripts,
        "stage_order": ["BL-003", "BL-004", "BL-005", "BL-006", "BL-007", "BL-008", "BL-009"],
        "stage_configs": {
            "alignment_seed_controls": {
                "fuzzy_matching": dict((bl003_summary.get("inputs") or {}).get("fuzzy_matching") or {}),
            },
            "profile": profile["config"],
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
    diagnostics = profile["diagnostics"]
    missing_numeric_track_count = diagnostics["missing_numeric_track_count"]

    payload = {
        "user_id": profile["user_id"],
        "config": profile["config"],
        "diagnostics": {
            "events_total": diagnostics["events_total"],
            "matched_seed_count": diagnostics["matched_seed_count"],
            "missing_numeric_track_count": missing_numeric_track_count,
            "candidate_rows_total": diagnostics["candidate_rows_total"],
            "total_effective_weight": diagnostics["total_effective_weight"],
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
    bl003_summary = load_json(paths["bl003_summary"])
    profile = load_json(paths["profile"])
    bl004_summary = load_json(paths["bl004_summary"])
    playlist = load_json(paths["playlist"])
    bl008_payloads = load_json(paths["bl008_payloads"])
    bl009_log = load_json(paths["bl009_log"])
    bl009_index_rows = load_csv_rows(paths["bl009_index"])

    playlist_track_ids = [track["track_id"] for track in playlist["tracks"]]
    explanation_track_ids = [item["track_id"] for item in bl008_payloads["explanations"]]
    playlist_stable_hash = stable_playlist_fingerprint(playlist)
    explanation_stable_hash = stable_explanations_fingerprint(bl008_payloads)
    observability_stable_hash = stable_observability_fingerprint(
        bl009_log,
        playlist_stable_hash=playlist_stable_hash,
        explanations_stable_hash=explanation_stable_hash,
    )

    raw_hash_map = build_file_hash_map(
        paths,
        [
            "bl003_summary",
            "bl003_seed_table",
            "bl004_seed_trace",
            "bl005_filtered",
            "bl005_decisions",
            "bl006_scored",
            "bl007_trace",
            "playlist",
            "bl008_payloads",
            "bl009_log",
            "bl009_index",
        ],
    )

    return {
        "stage_run_ids": {
            "BL-003": str(bl003_summary.get("generated_at_utc") or "unknown"),
            "BL-004": profile["run_id"],
            "BL-005": load_json(paths["bl005_diagnostics"])["run_id"],
            "BL-006": load_json(paths["bl006_summary"])["run_id"],
            "BL-007": load_json(paths["bl007_report"])["run_id"],
            "BL-008": load_json(paths["bl008_summary"])["run_id"],
            "BL-009": bl009_log["run_metadata"]["run_id"],
        },
        "raw_hashes": {
            "bl003_summary": raw_hash_map["bl003_summary"],
            "bl003_seed_table": raw_hash_map["bl003_seed_table"],
            "bl004_seed_trace": raw_hash_map["bl004_seed_trace"],
            "bl005_filtered": raw_hash_map["bl005_filtered"],
            "bl005_decisions": raw_hash_map["bl005_decisions"],
            "bl006_scored": raw_hash_map["bl006_scored"],
            "bl007_trace": raw_hash_map["bl007_trace"],
            "playlist": raw_hash_map["playlist"],
            "bl008_payloads": raw_hash_map["bl008_payloads"],
            "bl009_log": raw_hash_map["bl009_log"],
            "bl009_index": raw_hash_map["bl009_index"],
        },
        "stable_hashes": {
            "alignment_summary_hash": canonical_json_hash(
                {
                    "counts": bl003_summary.get("counts"),
                    "source_stats": bl003_summary.get("source_stats"),
                    "fuzzy_matching": ((bl003_summary.get("inputs") or {}).get("fuzzy_matching") or {}),
                    "seed_contract": ((bl003_summary.get("inputs") or {}).get("seed_contract") or {}),
                },
                uppercase=True,
            ),
            "profile_semantic_hash": stable_profile_fingerprint(profile, bl004_summary),
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
            "alignment_match_counts": dict(bl003_summary.get("counts") or {}),
            "alignment_fuzzy_matching": dict((bl003_summary.get("inputs") or {}).get("fuzzy_matching") or {}),
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


def build_replay_run_config(
    *,
    root: Path,
    output_dir: Path,
    run_config_path: str | None,
    reference_now_utc: str,
) -> str | None:
    """Create a replay-local run-config with fixed BL-003 temporal controls."""
    if not run_config_path:
        return None

    source_path = Path(run_config_path)
    if not source_path.is_absolute():
        candidates = [
            (root / source_path).resolve(),
            (root.parent / source_path).resolve(),
        ]
        resolved = next((candidate for candidate in candidates if candidate.exists()), None)
        if resolved is None:
            raise FileNotFoundError(
                "BL-010 run-config path does not exist in src-root or package-root resolution: "
                f"{run_config_path}"
            )
        source_path = resolved
    elif not source_path.exists():
        raise FileNotFoundError(f"BL-010 run-config path does not exist: {source_path}")

    payload = load_json(source_path)
    seed_controls = payload.get("seed_controls")
    if not isinstance(seed_controls, dict):
        seed_controls = {}
        payload["seed_controls"] = seed_controls

    temporal_controls = seed_controls.get("temporal_controls")
    if not isinstance(temporal_controls, dict):
        temporal_controls = {}
        seed_controls["temporal_controls"] = temporal_controls

    temporal_controls["reference_mode"] = "fixed"
    temporal_controls["reference_now_utc"] = reference_now_utc

    replay_config_path = output_dir / "bl010_replay_run_config_fixed_temporal.json"
    write_json_ascii(replay_config_path, payload)
    return str(replay_config_path)


def _build_stage_payload(
    *,
    stage_id: str,
    run_config_path: str | None,
    controls: dict[str, object],
) -> dict[str, object]:
    return {
        "stage_id": stage_id,
        "schema_version": "1.0",
        "resolved_from": "run_config" if run_config_path else "defaults",
        "controls": controls,
    }


def resolve_stage_control_payloads(
    stage_order: list[str],
    run_config_path: str | None,
) -> dict[str, dict[str, object]]:
    run_config_utils = load_run_config_utils_module()
    stage_bundle = run_config_utils.resolve_stage_control_bundle(run_config_path)
    payloads: dict[str, dict[str, object]] = {}
    for stage_id in stage_order:
        controls = stage_bundle.get(stage_id)
        if not isinstance(controls, dict):
            raise ValueError(f"Unsupported stage for payload resolution: {stage_id}")
        payloads[stage_id] = _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls={str(key): value for key, value in controls.items()},
        )
    return payloads


def run_stage(
    stage_id: str,
    script_path: Path,
    root: Path,
    python_executable: str,
    run_config_path: str | None,
    reference_now_utc: str | None,
    stage_payloads: dict[str, dict[str, object]] | None = None,
) -> dict[str, object]:
    started = time.time()
    command = [python_executable, str(script_path)]
    if stage_id == "BL-003":
        command.append("--allow-missing-selected-sources")
    completed: subprocess.CompletedProcess[str] | None = None
    attempts: list[dict[str, object]] = []
    stage_env = os.environ.copy()
    existing_pythonpath = stage_env.get("PYTHONPATH", "")
    pythonpath_parts = [str(root)]
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    stage_env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    if run_config_path:
        stage_env["BL_RUN_CONFIG_PATH"] = run_config_path
    if reference_now_utc:
        stage_env["BL_REFERENCE_NOW_UTC"] = reference_now_utc
    payload_for_stage = (stage_payloads or {}).get(stage_id)
    if isinstance(payload_for_stage, dict):
        stage_env["BL_STAGE_CONFIG_JSON"] = json.dumps(
            payload_for_stage,
            ensure_ascii=True,
            separators=(",", ":"),
        )
    else:
        stage_env.pop("BL_STAGE_CONFIG_JSON", None)
    for attempt in range(1, 4):
        attempt_started = time.time()
        completed = subprocess.run(
            command,
            cwd=root,
            env=stage_env,
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
    command_suffix = ""
    stdout_lines = final_attempt.get("stdout")
    stderr_lines = final_attempt.get("stderr")
    return {
        "stage": stage_id,
        "script": script_path.name,
        "script_path": canonical_script_path,
        "command": f"python {canonical_script_path}{command_suffix}",
        "elapsed_seconds": round(time.time() - started, 3),
        "stdout": [str(item) for item in stdout_lines] if isinstance(stdout_lines, list) else [],
        "stderr": [str(item) for item in stderr_lines] if isinstance(stderr_lines, list) else [],
        "attempt_count": len(attempts),
        "had_retry": len(attempts) > 1,
        "attempts": attempts,
    }


def build_stage_sequence(paths: dict[str, Path]) -> list[tuple[str, Path]]:
    return [
        ("BL-003", paths["bl003_script"]),
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
    reference_now_utc: str | None,
    stage_payloads: dict[str, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    replay_records: list[dict[str, object]] = []
    for replay_number in range(1, replay_count + 1):
        stage_runs = [
            run_stage(
                stage_id,
                script_path,
                root,
                python_executable,
                run_config_path,
                reference_now_utc,
                stage_payloads,
            )
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


def _active_output_archive_map(paths: dict[str, Path]) -> dict[str, Path]:
    return {
        "bl003_ds001_spotify_summary.json": paths["bl003_summary"],
        "bl003_ds001_spotify_seed_table.csv": paths["bl003_seed_table"],
        "bl004_preference_profile.json": paths["profile"],
        "profile_summary.json": paths["bl004_summary"],
        "bl004_seed_trace.csv": paths["bl004_seed_trace"],
        "bl005_filtered_candidates.csv": paths["bl005_filtered"],
        "bl005_candidate_decisions.csv": paths["bl005_decisions"],
        "bl005_candidate_diagnostics.json": paths["bl005_diagnostics"],
        "bl006_scored_candidates.csv": paths["bl006_scored"],
        "bl006_score_summary.json": paths["bl006_summary"],
        "playlist.json": paths["playlist"],
        "bl007_assembly_trace.csv": paths["bl007_trace"],
        "bl007_assembly_report.json": paths["bl007_report"],
        "bl008_explanation_payloads.json": paths["bl008_payloads"],
        "bl008_explanation_summary.json": paths["bl008_summary"],
        "bl009_run_observability_log.json": paths["bl009_log"],
        "bl009_run_index.csv": paths["bl009_index"],
    }


def archive_replay_outputs(paths: dict[str, Path], replay_dir: Path) -> None:
    for filename, source_path in _active_output_archive_map(paths).items():
        copy_file(source_path, replay_dir / filename)


def restore_active_outputs(paths: dict[str, Path], baseline_dir: Path) -> None:
    for filename, destination_path in _active_output_archive_map(paths).items():
        copy_file(baseline_dir / filename, destination_path)


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
    root = impl_root()
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
    config_path = output_dir / "reproducibility_config_snapshot.json"
    write_json_ascii(config_path, config_snapshot)

    run_started_at = utc_now()
    reference_now_utc = run_started_at
    replay_run_config_path = build_replay_run_config(
        root=root,
        output_dir=output_dir,
        run_config_path=str(args.run_config) if args.run_config else None,
        reference_now_utc=reference_now_utc,
    )
    run_id = f"BL010-REPRO-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    started = time.time()

    stage_sequence = build_stage_sequence(paths)
    stage_order = [stage_id for stage_id, _ in stage_sequence]
    stage_payloads = resolve_stage_control_payloads(stage_order, replay_run_config_path)
    baseline_outputs_dir = output_dir / "_active_outputs_baseline"
    if baseline_outputs_dir.exists():
        shutil.rmtree(baseline_outputs_dir)
    baseline_outputs_dir.mkdir(parents=True, exist_ok=True)
    archive_replay_outputs(paths, baseline_outputs_dir)

    replay_records: list[dict[str, object]]
    try:
        replay_records = execute_replays(
            replay_count=replay_count,
            stage_sequence=stage_sequence,
            python_executable=str(args.python),
            root=root,
            output_dir=output_dir,
            paths=paths,
            run_config_path=replay_run_config_path,
            reference_now_utc=reference_now_utc,
            stage_payloads=stage_payloads,
        )
    finally:
        restore_active_outputs(paths, baseline_outputs_dir)

    stable_hashes_by_run = [
        {str(key): str(value) for key, value in _object_mapping(record.get("stable_hashes")).items()}
        for record in replay_records
    ]
    baseline_stable = stable_hashes_by_run[0]
    deterministic_match = all(candidate == baseline_stable for candidate in stable_hashes_by_run[1:])
    first_mismatch_artifact = first_mismatch(stable_hashes_by_run)

    raw_playlist_hash_match = len({_object_mapping(record.get("raw_hashes")).get("playlist") for record in replay_records}) == 1
    raw_explanation_hash_match = len({_object_mapping(record.get("raw_hashes")).get("bl008_payloads") for record in replay_records}) == 1
    raw_observability_hash_match = len({_object_mapping(record.get("raw_hashes")).get("bl009_log") for record in replay_records}) == 1
    all_stage_runs = [stage_run for record in replay_records for stage_run in _object_dict_list(record.get("stage_runs"))]
    stage_runs_with_retries = [
        {
            "replay_number": record["replay_number"],
            "stage": stage_run["stage"],
            "attempt_count": stage_run["attempt_count"],
        }
        for record in replay_records
        for stage_run in _object_dict_list(record.get("stage_runs"))
        if bool(stage_run.get("had_retry"))
    ]

    summary_rows: list[dict[str, object]] = []
    for record in replay_records:
        stage_runs = _object_dict_list(record.get("stage_runs"))
        stage_run_ids = _object_mapping(record.get("stage_run_ids"))
        stable_hashes = _object_mapping(record.get("stable_hashes"))
        raw_hashes = _object_mapping(record.get("raw_hashes"))
        semantic_snapshots = _object_mapping(record.get("semantic_snapshots"))
        alignment_match_counts = _object_mapping(semantic_snapshots.get("alignment_match_counts"))
        alignment_fuzzy_matching = _object_mapping(semantic_snapshots.get("alignment_fuzzy_matching"))
        retry_count = sum(1 for stage_run in stage_runs if bool(stage_run.get("had_retry")))
        row = {
            "replay_number": record["replay_number"],
            "bl003_generated_at_utc": stage_run_ids.get("BL-003"),
            "bl004_run_id": stage_run_ids.get("BL-004"),
            "bl005_run_id": stage_run_ids.get("BL-005"),
            "bl006_run_id": stage_run_ids.get("BL-006"),
            "bl007_run_id": stage_run_ids.get("BL-007"),
            "bl008_run_id": stage_run_ids.get("BL-008"),
            "bl009_run_id": stage_run_ids.get("BL-009"),
            "alignment_summary_hash": stable_hashes.get("alignment_summary_hash"),
            "ranked_output_hash": stable_hashes.get("ranked_output_hash"),
            "playlist_output_hash": stable_hashes.get("playlist_output_hash"),
            "explanation_output_hash": stable_hashes.get("explanation_output_hash"),
            "observability_output_hash": stable_hashes.get("observability_output_hash"),
            "matched_by_fuzzy": safe_int(alignment_match_counts.get("matched_by_fuzzy"), 0),
            "fuzzy_enabled": int(bool(alignment_fuzzy_matching.get("enabled", False))),
            "raw_playlist_hash": raw_hashes.get("playlist"),
            "raw_explanation_hash": raw_hashes.get("bl008_payloads"),
            "raw_observability_hash": raw_hashes.get("bl009_log"),
            "dataset_version": semantic_snapshots.get("observability_dataset_version"),
            "pipeline_version": semantic_snapshots.get("observability_pipeline_version"),
            "stage_retry_count": retry_count,
            "archive_dir": record["archive_dir"],
        }
        summary_rows.append(row)

    summary_csv_path = output_dir / "reproducibility_run_matrix.csv"
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
            "replay_run_config_path": relpath(Path(replay_run_config_path), root) if replay_run_config_path else None,
            "fixed_input_hashes": config_snapshot["fixed_inputs"],
            "stage_scripts": config_snapshot["stage_scripts"],
        },
        "replay_scope": {
            "stage_order": config_snapshot["stage_order"],
            "stable_comparison_artifacts": [
                "alignment_summary_hash",
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
                "playlist.json",
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
                "playlist_raw_hash_match": raw_playlist_hash_match,
                "bl008_payloads_raw_hash_match": raw_explanation_hash_match,
                "bl009_log_raw_hash_match": raw_observability_hash_match,
            },
            "observed_reason_for_raw_hash_variation": "run_id, generated_at_utc, elapsed_seconds, and upstream run linkage fields vary across identical replays even when stable recommendation content remains unchanged",
            "playlist_track_ids_match": len({
                tuple(_string_list(_object_mapping(record.get("semantic_snapshots")).get("playlist_track_ids")))
                for record in replay_records
            }) == 1,
            "explanation_track_ids_match": len({
                tuple(_string_list(_object_mapping(record.get("semantic_snapshots")).get("explanation_track_ids")))
                for record in replay_records
            }) == 1,
            "dataset_version_match": len({
                _object_mapping(record.get("semantic_snapshots")).get("observability_dataset_version")
                for record in replay_records
            }) == 1,
            "pipeline_version_match": len({
                _object_mapping(record.get("semantic_snapshots")).get("observability_pipeline_version")
                for record in replay_records
            }) == 1,
            "all_stage_runs_succeeded_without_retry": all(not bool(stage_run.get("had_retry")) for stage_run in all_stage_runs),
            "replay_count_with_retries": len({item["replay_number"] for item in stage_runs_with_retries}),
            "stages_requiring_retry": stage_runs_with_retries,
        },
        "output_artifacts": {
            "config_snapshot_path": relpath(config_path, root),
            "replay_run_config_path": relpath(Path(replay_run_config_path), root) if replay_run_config_path else None,
            "run_matrix_path": relpath(summary_csv_path, root),
            "archived_replay_dirs": [record["archive_dir"] for record in replay_records],
        },
    }

    report_path = output_dir / "reproducibility_report.json"
    write_json_ascii(report_path, report)

    print("BL-010 reproducibility replay complete.")
    print(f"run_id={run_id}")
    print(f"deterministic_match={deterministic_match}")
    print(f"config_hash={config_hash}")
    print(f"report={report_path}")
    print(f"run_matrix={summary_csv_path}")


if __name__ == "__main__":
    main()
