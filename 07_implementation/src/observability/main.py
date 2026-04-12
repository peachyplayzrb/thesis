from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from observability.runtime_controls import resolve_bl009_runtime_controls
from shared_utils.artifact_registry import bl009_required_paths
from shared_utils.hashing import sha256_of_values
from shared_utils.io_utils import (
    load_csv_rows,
    open_text_write,
    sha256_of_file,
    utc_now,
)
from shared_utils.path_utils import impl_root
from shared_utils.parsing import safe_float, safe_int
from shared_utils.stage_utils import ensure_paths_exist, ensure_required_keys, load_required_json_object, relpath, safe_relpath


BL009_OBSERVABILITY_SCHEMA_VERSION = "bl009-observability-v1"


def _object_mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def build_signal_mode_calibration_summary(
    bl005_diagnostics: dict[str, object],
    bl006_summary: dict[str, object],
) -> dict[str, object]:
    retrieval_config = _object_mapping(bl005_diagnostics.get("config"))
    scoring_config = _object_mapping(bl006_summary.get("config"))
    signal_mode = _object_mapping(retrieval_config.get("signal_mode") or scoring_config.get("signal_mode"))
    popularity_profile = _object_mapping(signal_mode.get("popularity_profile"))
    component_weights = _object_mapping(scoring_config.get("base_component_weights"))
    numeric_thresholds = _object_mapping(retrieval_config.get("numeric_thresholds"))

    return {
        "mode_name": signal_mode.get("name"),
        "semantic_profile": signal_mode.get("semantic_profile"),
        "numeric_profile": signal_mode.get("numeric_profile"),
        "retrieval": {
            "use_weighted_semantics": bool(retrieval_config.get("use_weighted_semantics", False)),
            "use_continuous_numeric": bool(retrieval_config.get("use_continuous_numeric", False)),
            "numeric_support_min_score": safe_float(retrieval_config.get("numeric_support_min_score"), 0.0),
            "popularity_numeric_enabled": bool(popularity_profile.get("retrieval_enabled", False)),
            "numeric_feature_count": len(numeric_thresholds),
        },
        "scoring": {
            "popularity_weight": safe_float(component_weights.get("popularity"), 0.0),
            "popularity_scoring_enabled": bool(popularity_profile.get("scoring_enabled", False)),
        },
    }


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


def main() -> None:
    runtime_controls = resolve_bl009_runtime_controls()
    control_mode = _object_mapping(runtime_controls.get("control_mode"))
    input_scope = _object_mapping(runtime_controls.get("input_scope"))
    diagnostic_sample_limit = safe_int(runtime_controls.get("diagnostic_sample_limit"), 5)
    bootstrap_mode = bool(runtime_controls.get("bootstrap_mode", True))
    root = impl_root()
    output_dir = root / "observability" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    required_paths = bl009_required_paths(root, bl009_script_path=Path(__file__).resolve())

    ensure_paths_exist(list(required_paths.values()), stage_label="BL-009", label="inputs", root=root)

    start_time = time.time()

    paths = dict(required_paths)
    bl003_summary = load_required_json_object(paths["bl003_summary"], label="BL-003 alignment summary", stage_label="BL-009")
    profile = load_required_json_object(paths["bl004_profile"], label="BL-004 profile", stage_label="BL-009")
    bl004_summary = load_required_json_object(paths["bl004_summary"], label="BL-004 profile summary", stage_label="BL-009")
    bl005_diagnostics = load_required_json_object(paths["bl005_diagnostics"], label="BL-005 diagnostics", stage_label="BL-009")
    bl006_summary = load_required_json_object(paths["bl006_summary"], label="BL-006 score summary", stage_label="BL-009")
    bl007_report = load_required_json_object(paths["bl007_report"], label="BL-007 assembly report", stage_label="BL-009")
    bl008_summary = load_required_json_object(paths["bl008_summary"], label="BL-008 explanation summary", stage_label="BL-009")

    ensure_required_keys(bl003_summary, ["inputs", "counts"], label="BL-003 alignment summary", stage_label="BL-009")
    ensure_required_keys(profile, ["run_id", "user_id", "diagnostics", "seed_summary", "config"], label="BL-004 profile", stage_label="BL-009")
    ensure_required_keys(bl004_summary, ["dominant_lead_genres", "dominant_tags"], label="BL-004 profile summary", stage_label="BL-009")
    ensure_required_keys(bl005_diagnostics, ["run_id", "counts", "rule_hits", "top_kept_track_ids", "config"], label="BL-005 diagnostics", stage_label="BL-009")
    ensure_required_keys(bl006_summary, ["run_id", "counts", "score_statistics", "top_candidates", "config"], label="BL-006 score summary", stage_label="BL-009")
    ensure_required_keys(bl007_report, ["run_id", "counts", "rule_hits", "playlist_genre_mix", "playlist_score_range", "config"], label="BL-007 assembly report", stage_label="BL-009")
    ensure_required_keys(bl008_summary, ["run_id", "playlist_track_count", "top_contributor_distribution"], label="BL-008 explanation summary", stage_label="BL-009")

    bl003_counts = _object_mapping(bl003_summary.get("counts"))
    bl003_inputs = _object_mapping(bl003_summary.get("inputs"))
    bl003_fuzzy_controls = _object_mapping(bl003_inputs.get("fuzzy_matching"))
    bl003_match_by_fuzzy = safe_int(bl003_counts.get("matched_by_fuzzy"), 0)
    bl003_match_total = safe_int(bl003_counts.get("matched_events_rows"), 0)

    bl005_decisions = load_csv_rows(paths["bl005_decisions"])
    bl007_trace = load_csv_rows(paths["bl007_trace"])
    playlist = load_required_json_object(paths["bl007_playlist"], label="BL-007 playlist", stage_label="BL-009")
    bl008_payloads = load_required_json_object(paths["bl008_payloads"], label="BL-008 explanation payloads", stage_label="BL-009")
    ensure_required_keys(playlist, ["playlist_length"], label="BL-007 playlist", stage_label="BL-009")
    ensure_required_keys(bl008_payloads, ["explanations"], label="BL-008 explanation payloads", stage_label="BL-009")

    generated_at_utc = utc_now()
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
    pipeline_version = sha256_of_values([script_hashes[key] for key in sorted(script_hashes)])

    dataset_hash_sources = ["bl004_seed_trace", "bl005_filtered", "bl006_scored"]
    dataset_version_source = "active_pipeline_outputs"

    dataset_component_hashes = {
        relpath(paths[key], root): sha256_of_file(paths[key])
        for key in dataset_hash_sources
    }
    dataset_version = sha256_of_values([dataset_component_hashes[key] for key in sorted(dataset_component_hashes)])

    interaction_types_included: list[str] = []
    if input_scope.get("include_top_tracks"):
        interaction_types_included.append("top_tracks")
    if input_scope.get("include_saved_tracks"):
        interaction_types_included.append("saved_tracks")
    if input_scope.get("include_playlists"):
        interaction_types_included.append("playlists")
    if input_scope.get("include_recently_played"):
        interaction_types_included.append("recently_played")

    seed_summary = _object_mapping(profile.get("seed_summary"))
    seed_counts_by_type = _object_mapping(seed_summary.get("counts_by_interaction_type"))
    influence_track_count = safe_int(seed_counts_by_type.get("influence"), 0)
    history_track_count = safe_int(seed_counts_by_type.get("history"), 0)
    influence_tracks_included = influence_track_count > 0

    rejected_non_seed = [
        row for row in bl005_decisions
        if row.get("decision") == "reject" and row.get("is_seed_track") == "0"
    ]
    retrieval_samples = [
        {
            "track_id": row["track_id"],
            "lead_genre": row["lead_genre"],
            "semantic_score": float(row["semantic_score"]),
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
    retrieval_signal_mode = _object_mapping(_object_mapping(bl005_diagnostics.get("config")).get("signal_mode"))
    scoring_signal_mode = _object_mapping(_object_mapping(bl006_summary.get("config")).get("signal_mode"))
    signal_mode = retrieval_signal_mode or scoring_signal_mode
    signal_mode_calibration = build_signal_mode_calibration_summary(bl005_diagnostics, bl006_summary)

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
            "signal_mode_name": signal_mode.get("name"),
        },
        "execution_scope_summary": {
            "observability_schema_version": BL009_OBSERVABILITY_SCHEMA_VERSION,
            "source_family": input_scope.get("source_family"),
            "signal_mode": signal_mode,
            "signal_mode_calibration": signal_mode_calibration,
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
            "signal_mode": signal_mode,
            "signal_mode_calibration": signal_mode_calibration,
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
            "alignment_seed_controls": {
                "fuzzy_matching": bl003_fuzzy_controls,
                "match_rate_validation": _object_mapping(bl003_counts.get("match_rate_validation")),
                "match_rate_min_threshold": safe_float(
                    _object_mapping(bl003_counts.get("match_rate_validation")).get("min_threshold"),
                    0.0,
                ),
            },
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
            "alignment_summary": {
                "summary_path": relpath(paths["bl003_summary"], root),
                "matched_by_spotify_id": safe_int(bl003_counts.get("matched_by_spotify_id"), 0),
                "matched_by_metadata": safe_int(bl003_counts.get("matched_by_metadata"), 0),
                "matched_by_fuzzy": bl003_match_by_fuzzy,
                "matched_events_rows": bl003_match_total,
                "unmatched_rows": safe_int(bl003_counts.get("unmatched_rows"), 0),
                "fuzzy_match_ratio": round(
                    (bl003_match_by_fuzzy / bl003_match_total) if bl003_match_total > 0 else 0.0,
                    6,
                ),
                "fuzzy_matching": bl003_fuzzy_controls,
            },
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
            "alignment": {
                "task": "BL-003",
                "summary_path": relpath(paths["bl003_summary"], root),
                "counts": {
                    "input_event_rows": safe_int(bl003_counts.get("input_event_rows"), 0),
                    "matched_by_spotify_id": safe_int(bl003_counts.get("matched_by_spotify_id"), 0),
                    "matched_by_metadata": safe_int(bl003_counts.get("matched_by_metadata"), 0),
                    "matched_by_fuzzy": bl003_match_by_fuzzy,
                    "unmatched": safe_int(bl003_counts.get("unmatched"), 0),
                    "seed_table_rows": safe_int(bl003_counts.get("seed_table_rows"), 0),
                },
                "fuzzy_matching": bl003_fuzzy_controls,
            },
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
        "matched_by_fuzzy": bl003_match_by_fuzzy,
        "fuzzy_enabled": int(bool(bl003_fuzzy_controls.get("enabled", False))),
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
