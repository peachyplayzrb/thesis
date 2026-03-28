from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_utils.config_loader import load_run_config_utils_module
from shared_utils.artifact_registry import bl009_required_paths
from shared_utils.env_utils import env_bool, env_int
from shared_utils.io_utils import (
    load_csv_rows,
    load_json,
    open_text_write,
    sha256_of_file as sha256_of_file_shared,
)
from shared_utils.path_utils import impl_root
from shared_utils.stage_runtime_resolver import resolve_run_config_path


BL009_OBSERVABILITY_SCHEMA_VERSION = "bl009-observability-v1"

DEFAULT_INPUT_SCOPE: dict[str, object] = {
    "source_family": "spotify_api_export",
    "include_top_tracks": True,
    "top_time_ranges": ["short_term", "medium_term", "long_term"],
    "include_saved_tracks": True,
    "saved_tracks_limit": None,
    "include_playlists": True,
    "playlists_limit": None,
    "playlist_items_per_playlist_limit": None,
    "include_recently_played": True,
    "recently_played_limit": 50,
}


def sha256_of_file(path: Path) -> str:
    return sha256_of_file_shared(path).upper()


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def safe_relpath(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def combined_sha256(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(value.encode("utf-8"))
    return digest.hexdigest().upper()


def first_items(values: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    return values[:limit]


def parse_exclusion_samples(rows: list[dict[str, str]], field: str, limit: int) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        key = row.get(field, "")
        if not key:
            continue
        grouped.setdefault(key, [])
        if len(grouped[key]) >= limit:
            continue
        grouped[key].append(row)
    return grouped


def load_required_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = load_json(path)
    except OSError as exc:
        raise RuntimeError(f"BL-009 could not read {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"BL-009 could not parse {label} as valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"BL-009 expected {label} to be a JSON object: {path}")
    return payload


def ensure_required_keys(payload: dict[str, Any], keys: list[str], *, label: str) -> None:
    missing = [key for key in keys if key not in payload]
    if missing:
        raise RuntimeError(f"BL-009 {label} missing required keys: {missing}")


def ensure_required_sections(run_log: dict) -> None:
    required_keys = [
        "run_metadata",
        "execution_scope_summary",
        "run_config",
        "ingestion_alignment_diagnostics",
        "stage_diagnostics",
        "exclusion_diagnostics",
        "output_artifacts",
    ]
    missing = [key for key in required_keys if key not in run_log]
    if missing:
        raise RuntimeError(f"BL-009 run log missing required sections: {missing}")


def ensure_paths_exist(paths: dict[str, Path], root: Path, *, label: str) -> None:
    missing_paths = [relpath(path, root) for path in paths.values() if not path.exists()]
    if missing_paths:
        raise FileNotFoundError(f"BL-009 missing required {label}: {missing_paths}")


def resolve_canonical_config_artifacts(
    runtime_controls: dict[str, object],
    root: Path,
) -> dict[str, dict[str, object]]:
    canonical_config_artifacts: dict[str, dict[str, object]] = {}
    for alias, env_key in [
        ("run_intent", "run_intent_path"),
        ("run_effective_config", "run_effective_config_path"),
    ]:
        raw_path = runtime_controls.get(env_key)
        if not raw_path:
            canonical_config_artifacts[alias] = {
                "path": None,
                "available": False,
                "sha256": None,
            }
            continue
        candidate_path = Path(str(raw_path))
        if not candidate_path.is_absolute():
            candidate_path = (root / candidate_path).resolve()
        available = candidate_path.exists()
        canonical_config_artifacts[alias] = {
            "path": safe_relpath(candidate_path, root),
            "available": available,
            "sha256": sha256_of_file(candidate_path) if available else None,
        }
    return canonical_config_artifacts


def build_artifact_maps(
    paths: dict[str, Path],
    root: Path,
    script_keys: set[str],
) -> tuple[dict[str, str], dict[str, int]]:
    artifact_hashes = {
        relpath(path, root): sha256_of_file(path)
        for key, path in paths.items()
        if key not in script_keys and path.exists()
    }
    artifact_sizes = {
        relpath(path, root): path.stat().st_size
        for key, path in paths.items()
        if key not in script_keys and path.exists()
    }
    return artifact_hashes, artifact_sizes


def resolve_bl009_runtime_controls() -> dict[str, object]:
    run_config_path = resolve_run_config_path("BL_RUN_CONFIG_PATH")
    run_intent_path = resolve_run_config_path("BL_RUN_INTENT_PATH")
    run_effective_config_path = resolve_run_config_path("BL_RUN_EFFECTIVE_CONFIG_PATH")
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl009_controls(run_config_path)
        input_scope_controls = run_config_utils.resolve_input_scope_controls(run_config_path)
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "control_mode": dict(controls.get("control_mode") or {}),
            "run_intent_path": run_intent_path,
            "run_effective_config_path": run_effective_config_path,
            "input_scope": dict(input_scope_controls.get("input_scope") or DEFAULT_INPUT_SCOPE),
            "diagnostic_sample_limit": int(controls["diagnostic_sample_limit"]),
            "bootstrap_mode": bool(controls.get("bootstrap_mode", True)),
        }
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "control_mode": {
            "validation_profile": "strict",
            "allow_threshold_decoupling": False,
            "allow_weight_auto_normalization": False,
        },
        "run_intent_path": run_intent_path,
        "run_effective_config_path": run_effective_config_path,
        "input_scope": dict(DEFAULT_INPUT_SCOPE),
        "diagnostic_sample_limit": max(1, env_int("BL009_DIAGNOSTIC_SAMPLE_LIMIT", 5)),
        "bootstrap_mode": env_bool("BL009_BOOTSTRAP_MODE", True),
    }


def main() -> None:
    runtime_controls = resolve_bl009_runtime_controls()
    control_mode = dict(runtime_controls.get("control_mode") or {})
    input_scope = dict(runtime_controls["input_scope"])
    diagnostic_sample_limit = int(runtime_controls["diagnostic_sample_limit"])
    bootstrap_mode = bool(runtime_controls.get("bootstrap_mode", True))
    root = impl_root()
    output_dir = root / "observability" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    required_paths = bl009_required_paths(root, bl009_script_path=Path(__file__).resolve())

    ensure_paths_exist(required_paths, root, label="inputs")

    start_time = time.time()

    paths = dict(required_paths)
    profile = load_required_json(paths["bl004_profile"], label="BL-004 profile")
    bl004_summary = load_required_json(paths["bl004_summary"], label="BL-004 profile summary")
    bl005_diagnostics = load_required_json(paths["bl005_diagnostics"], label="BL-005 diagnostics")
    bl006_summary = load_required_json(paths["bl006_summary"], label="BL-006 score summary")
    bl007_report = load_required_json(paths["bl007_report"], label="BL-007 assembly report")
    bl008_summary = load_required_json(paths["bl008_summary"], label="BL-008 explanation summary")

    ensure_required_keys(profile, ["run_id", "user_id", "diagnostics", "seed_summary", "config"], label="BL-004 profile")
    ensure_required_keys(bl004_summary, ["dominant_lead_genres", "dominant_tags"], label="BL-004 profile summary")
    ensure_required_keys(bl005_diagnostics, ["run_id", "counts", "rule_hits", "top_kept_track_ids", "config"], label="BL-005 diagnostics")
    ensure_required_keys(bl006_summary, ["run_id", "counts", "score_statistics", "top_candidates", "config"], label="BL-006 score summary")
    ensure_required_keys(bl007_report, ["run_id", "counts", "rule_hits", "playlist_genre_mix", "playlist_score_range", "config"], label="BL-007 assembly report")
    ensure_required_keys(bl008_summary, ["run_id", "playlist_track_count", "top_contributor_distribution"], label="BL-008 explanation summary")

    bl005_decisions = load_csv_rows(paths["bl005_decisions"])
    bl007_trace = load_csv_rows(paths["bl007_trace"])
    playlist = load_required_json(paths["bl007_playlist"], label="BL-007 playlist")
    bl008_payloads = load_required_json(paths["bl008_payloads"], label="BL-008 explanation payloads")
    ensure_required_keys(playlist, ["playlist_length"], label="BL-007 playlist")
    ensure_required_keys(bl008_payloads, ["explanations"], label="BL-008 explanation payloads")

    generated_at_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_id = f"BL009-OBSERVE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    script_hash_keys = [
        "bl004_script",
        "bl005_script",
        "bl006_script",
        "bl007_script",
        "bl008_script",
        "bl009_script",
    ]

    script_hashes = {
        relpath(paths[key], root): sha256_of_file(paths[key])
        for key in script_hash_keys
    }
    pipeline_version = combined_sha256([script_hashes[key] for key in sorted(script_hashes)])

    dataset_hash_sources = ["bl004_seed_trace", "bl005_filtered", "bl006_scored"]
    dataset_version_source = "active_pipeline_outputs"

    dataset_component_hashes = {
        relpath(paths[key], root): sha256_of_file(paths[key])
        for key in dataset_hash_sources
    }
    dataset_version = combined_sha256([dataset_component_hashes[key] for key in sorted(dataset_component_hashes)])

    interaction_types_included: list[str] = []
    if input_scope.get("include_top_tracks"):
        interaction_types_included.append("top_tracks")
    if input_scope.get("include_saved_tracks"):
        interaction_types_included.append("saved_tracks")
    if input_scope.get("include_playlists"):
        interaction_types_included.append("playlists")
    if input_scope.get("include_recently_played"):
        interaction_types_included.append("recently_played")

    seed_counts_by_type = profile.get("seed_summary", {}).get("counts_by_interaction_type", {})
    influence_track_count = int(seed_counts_by_type.get("influence", 0))
    history_track_count = int(seed_counts_by_type.get("history", 0))
    influence_tracks_included = influence_track_count > 0

    rejected_non_seed = [
        row for row in bl005_decisions
        if row.get("decision") == "reject" and row.get("is_seed_track") == "0"
    ]
    retrieval_samples = [
        {
            "track_id": row["track_id"],
            "lead_genre": row["lead_genre"],
            "semantic_score": int(row["semantic_score"]),
            "numeric_pass_count": int(row["numeric_pass_count"]),
            "decision_reason": row["decision_reason"],
        }
        for row in first_items(rejected_non_seed, diagnostic_sample_limit)
    ]

    assembly_excluded = [row for row in bl007_trace if row.get("decision") == "excluded"]
    assembly_rule_samples_raw = parse_exclusion_samples(assembly_excluded, "exclusion_reason", diagnostic_sample_limit)
    assembly_rule_samples = {
        reason: [
            {
                "score_rank": int(row["score_rank"]),
                "track_id": row["track_id"],
                "lead_genre": row["lead_genre"],
                "final_score": float(row["final_score"]),
            }
            for row in rows
        ]
        for reason, rows in assembly_rule_samples_raw.items()
    }

    first_length_cap = next(
        (row for row in assembly_excluded if row.get("exclusion_reason") == "length_cap_reached"),
        None,
    )

    script_keys = {
        "bl004_script",
        "bl005_script",
        "bl006_script",
        "bl007_script",
        "bl008_script",
        "bl009_script",
    }

    canonical_config_artifacts = resolve_canonical_config_artifacts(runtime_controls, root)
    artifact_hashes, artifact_sizes = build_artifact_maps(paths, root, script_keys)

    run_log = {
        "run_metadata": {
            "run_id": run_id,
            "task": "BL-009",
            "generated_at_utc": generated_at_utc,
            "elapsed_seconds": None,
            "observability_schema_version": BL009_OBSERVABILITY_SCHEMA_VERSION,
            "observability_scope": "artifact-level deterministic audit log",
            "bootstrap_mode": bootstrap_mode,
            "dataset_version": dataset_version,
            "dataset_version_source": dataset_version_source,
            "pipeline_version": pipeline_version,
            "dataset_component_hashes": dataset_component_hashes,
            "pipeline_script_hashes": script_hashes,
            "optional_dependency_availability": {},
            "upstream_stage_run_ids": {
                "BL-004": profile["run_id"],
                "BL-005": bl005_diagnostics["run_id"],
                "BL-006": bl006_summary["run_id"],
                "BL-007": bl007_report["run_id"],
                "BL-008": bl008_summary["run_id"],
            },
            "config_source": runtime_controls["config_source"],
            "run_config_path": runtime_controls["run_config_path"],
            "run_config_schema_version": runtime_controls["run_config_schema_version"],
            "run_intent_path": runtime_controls["run_intent_path"],
            "run_effective_config_path": runtime_controls["run_effective_config_path"],
        },
        "execution_scope_summary": {
            "observability_schema_version": BL009_OBSERVABILITY_SCHEMA_VERSION,
            "source_family": input_scope.get("source_family"),
            "interaction_types_included": interaction_types_included,
            "total_seed_count": profile["diagnostics"]["matched_seed_count"],
            "history_track_count": history_track_count,
            "influence_tracks_included": influence_tracks_included,
            "influence_track_count": influence_track_count,
            "canonical_config_artifact_pair_available": (
                canonical_config_artifacts.get("run_intent", {}).get("available", False)
                and canonical_config_artifacts.get("run_effective_config", {}).get("available", False)
            ),
        },
        "run_config": {
            "control_mode": control_mode,
            "input_scope": input_scope,
            "canonical_config_artifacts": canonical_config_artifacts,
            "data_layer": (
                {
                    "status": "active_mode_not_required",
                    "reason": "BL-009 uses active BL-004..BL-008 artifacts for observability diagnostics.",
                }
            ),
            "bootstrap_assets": (
                {
                    "status": "active_mode_not_required",
                    "reason": "Legacy synthetic bootstrap assets are no longer part of active BL-009 execution.",
                }
            ),
            "profile": profile["config"],
            "retrieval": bl005_diagnostics["config"],
            "scoring": bl006_summary["config"],
            "assembly": bl007_report["config"],
            "transparency": {
                "playlist_track_count": bl008_summary["playlist_track_count"],
                "top_contributor_distribution": bl008_summary["top_contributor_distribution"],
                "explanation_payload_rule": "top 3 contributors by weighted contribution; sentence derived from top contributors and playlist position",
            },
        },
        "ingestion_alignment_diagnostics": {
            "stage_status": "active_bl004_to_bl008_mode",
            "reason": "BL-009 is aligned to current implementation scope and logs BL-004..BL-008 artifacts directly.",
            "surrogate_inputs": {
                "aligned_events_path": None,
                "candidate_stub_path": None,
            },
            "conceptual_fields_recorded_as_not_applicable": [
                "imported_row_counts",
                "valid_invalid_counts",
                "matched_by_isrc",
                "matched_by_fallback",
                "unmatched_count",
            ],
        },
        "stage_diagnostics": {
            "data_layer": (
                {
                    "task": "BL-017",
                    "status": "inactive_in_active_mode",
                    "reason": "BL-009 observability does not require BL-017 in active mode.",
                }
            ),
            "bootstrap_assets": (
                {
                    "task": "BL-016",
                    "status": "inactive_in_active_mode",
                    "reason": "BL-009 observability does not require BL-016 in active mode.",
                }
            ),
            "profile": {
                "task": "BL-004",
                "run_id": profile["run_id"],
                "user_id": profile["user_id"],
                "diagnostics": profile["diagnostics"],
                "seed_summary": profile["seed_summary"],
                "dominant_lead_genres": bl004_summary["dominant_lead_genres"],
                "dominant_tags": bl004_summary["dominant_tags"],
            },
            "retrieval": {
                "task": "BL-005",
                "run_id": bl005_diagnostics["run_id"],
                "counts": bl005_diagnostics["counts"],
                "rule_hits": bl005_diagnostics["rule_hits"],
                "top_kept_track_ids": bl005_diagnostics["top_kept_track_ids"],
            },
            "scoring": {
                "task": "BL-006",
                "run_id": bl006_summary["run_id"],
                "counts": bl006_summary["counts"],
                "score_statistics": bl006_summary["score_statistics"],
                "top_candidates": bl006_summary["top_candidates"],
                "weight_rebalance_diagnostics": (
                    bl006_summary.get("config", {}).get("weight_rebalance_diagnostics")
                    or {
                        "status": "not_available",
                        "reason": "BL-006 summary does not include weight_rebalance_diagnostics",
                    }
                ),
            },
            "assembly": {
                "task": "BL-007",
                "run_id": bl007_report["run_id"],
                "counts": bl007_report["counts"],
                "rule_hits": bl007_report["rule_hits"],
                "playlist_genre_mix": bl007_report["playlist_genre_mix"],
                "playlist_score_range": bl007_report["playlist_score_range"],
                "playlist_length": playlist["playlist_length"],
            },
            "transparency": {
                "task": "BL-008",
                "run_id": bl008_summary["run_id"],
                "playlist_track_count": bl008_summary["playlist_track_count"],
                "top_contributor_distribution": bl008_summary["top_contributor_distribution"],
                "explanation_count": len(bl008_payloads["explanations"]),
            },
        },
        "exclusion_diagnostics": {
            "retrieval": {
                "seed_tracks_excluded": bl005_diagnostics["counts"]["seed_tracks_excluded"],
                "rejected_non_seed_candidates": bl005_diagnostics["counts"]["rejected_non_seed_candidates"],
                "sample_rejected_non_seed_rows": retrieval_samples,
            },
            "assembly": {
                "tracks_excluded": bl007_report["counts"]["tracks_excluded"],
                "rule_hits": bl007_report["rule_hits"],
                "first_length_cap_boundary": (
                    {
                        "score_rank": int(first_length_cap["score_rank"]),
                        "track_id": first_length_cap["track_id"],
                        "lead_genre": first_length_cap["lead_genre"],
                        "final_score": float(first_length_cap["final_score"]),
                    }
                    if first_length_cap is not None
                    else None
                ),
                "sample_exclusions_by_rule": assembly_rule_samples,
            },
        },
        "output_artifacts": {
            "primary_outputs": {
                "playlist": {
                    "path": relpath(paths["bl007_playlist"], root),
                    "sha256": artifact_hashes[relpath(paths["bl007_playlist"], root)],
                    "size_bytes": artifact_sizes[relpath(paths["bl007_playlist"], root)],
                },
                "explanation_payloads": {
                    "path": relpath(paths["bl008_payloads"], root),
                    "sha256": artifact_hashes[relpath(paths["bl008_payloads"], root)],
                    "size_bytes": artifact_sizes[relpath(paths["bl008_payloads"], root)],
                },
            },
            "trace_outputs": {
                "seed_trace": {
                    "path": relpath(paths["bl004_seed_trace"], root),
                    "sha256": artifact_hashes[relpath(paths["bl004_seed_trace"], root)],
                },
                "candidate_decisions": {
                    "path": relpath(paths["bl005_decisions"], root),
                    "sha256": artifact_hashes[relpath(paths["bl005_decisions"], root)],
                },
                "scored_candidates": {
                    "path": relpath(paths["bl006_scored"], root),
                    "sha256": artifact_hashes[relpath(paths["bl006_scored"], root)],
                },
                "assembly_trace": {
                    "path": relpath(paths["bl007_trace"], root),
                    "sha256": artifact_hashes[relpath(paths["bl007_trace"], root)],
                },
            },
            "supporting_outputs": {
                "profile": {
                    "path": relpath(paths["bl004_profile"], root),
                    "sha256": artifact_hashes[relpath(paths["bl004_profile"], root)],
                },
                "retrieval_diagnostics": {
                    "path": relpath(paths["bl005_diagnostics"], root),
                    "sha256": artifact_hashes[relpath(paths["bl005_diagnostics"], root)],
                },
                "score_summary": {
                    "path": relpath(paths["bl006_summary"], root),
                    "sha256": artifact_hashes[relpath(paths["bl006_summary"], root)],
                },
                "assembly_report": {
                    "path": relpath(paths["bl007_report"], root),
                    "sha256": artifact_hashes[relpath(paths["bl007_report"], root)],
                },
                "explanation_summary": {
                    "path": relpath(paths["bl008_summary"], root),
                    "sha256": artifact_hashes[relpath(paths["bl008_summary"], root)],
                },
                "data_layer_coverage": (
                    {
                        "path": None,
                        "status": "inactive_in_active_mode",
                    }
                ),
                "bootstrap_manifest": (
                    {
                        "path": None,
                        "status": "inactive_in_active_mode",
                    }
                ),
            },
        },
    }

    ensure_required_sections(run_log)

    run_log["run_metadata"]["elapsed_seconds"] = round(time.time() - start_time, 3)

    run_log_path = output_dir / "bl009_run_observability_log.json"
    with open_text_write(run_log_path) as handle:
        handle.write(json.dumps(run_log, indent=2, ensure_ascii=True))

    run_index_path = output_dir / "bl009_run_index.csv"
    run_index_row = {
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "dataset_version": dataset_version,
        "pipeline_version": pipeline_version,
        "bootstrap_mode": int(bootstrap_mode),
        "profile_run_id": profile["run_id"],
        "retrieval_run_id": bl005_diagnostics["run_id"],
        "scoring_run_id": bl006_summary["run_id"],
        "assembly_run_id": bl007_report["run_id"],
        "transparency_run_id": bl008_summary["run_id"],
        "kept_candidates": bl005_diagnostics["counts"]["kept_candidates"],
        "candidates_scored": bl006_summary["counts"]["candidates_scored"],
        "playlist_length": playlist["playlist_length"],
        "explanation_count": len(bl008_payloads["explanations"]),
        "playlist_sha256": artifact_hashes[relpath(paths["bl007_playlist"], root)],
        "explanation_payloads_sha256": artifact_hashes[relpath(paths["bl008_payloads"], root)],
        "observability_log_sha256": sha256_of_file(run_log_path),
    }
    with open_text_write(run_index_path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(run_index_row.keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(run_index_row)

    print("BL-009 observability logging complete.")
    print(f"run_log={run_log_path}")
    print(f"run_index={run_index_path}")
    print(f"run_id={run_id}")


if __name__ == "__main__":
    main()
