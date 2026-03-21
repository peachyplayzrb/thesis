from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


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


def ensure_required_sections(run_log: dict) -> None:
    required_keys = [
        "run_metadata",
        "run_config",
        "ingestion_alignment_diagnostics",
        "stage_diagnostics",
        "exclusion_diagnostics",
        "output_artifacts",
    ]
    missing = [key for key in required_keys if key not in run_log]
    if missing:
        raise RuntimeError(f"BL-009 run log missing required sections: {missing}")


def main() -> None:
    root = repo_root()
    output_dir = root / "07_implementation" / "implementation_notes" / "observability" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "bl017_coverage": root / "07_implementation" / "implementation_notes" / "data_layer" / "outputs" / "onion_join_coverage_report.json",
        "bl016_manifest": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_asset_manifest.json",
        "bl016_events": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_synthetic_aligned_events.jsonl",
        "bl016_candidates": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_candidate_stub.csv",
        "bl004_profile": root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_preference_profile.json",
        "bl004_summary": root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_profile_summary.json",
        "bl004_seed_trace": root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_seed_trace.csv",
        "bl005_diagnostics": root / "07_implementation" / "implementation_notes" / "retrieval" / "outputs" / "bl005_candidate_diagnostics.json",
        "bl005_decisions": root / "07_implementation" / "implementation_notes" / "retrieval" / "outputs" / "bl005_candidate_decisions.csv",
        "bl005_filtered": root / "07_implementation" / "implementation_notes" / "retrieval" / "outputs" / "bl005_filtered_candidates.csv",
        "bl006_summary": root / "07_implementation" / "implementation_notes" / "scoring" / "outputs" / "bl006_score_summary.json",
        "bl006_scored": root / "07_implementation" / "implementation_notes" / "scoring" / "outputs" / "bl006_scored_candidates.csv",
        "bl007_report": root / "07_implementation" / "implementation_notes" / "playlist" / "outputs" / "bl007_assembly_report.json",
        "bl007_trace": root / "07_implementation" / "implementation_notes" / "playlist" / "outputs" / "bl007_assembly_trace.csv",
        "bl007_playlist": root / "07_implementation" / "implementation_notes" / "playlist" / "outputs" / "bl007_playlist.json",
        "bl008_summary": root / "07_implementation" / "implementation_notes" / "transparency" / "outputs" / "bl008_explanation_summary.json",
        "bl008_payloads": root / "07_implementation" / "implementation_notes" / "transparency" / "outputs" / "bl008_explanation_payloads.json",
        "bl017_script": root / "07_implementation" / "implementation_notes" / "data_layer" / "build_onion_canonical_layer.py",
        "bl016_script": root / "07_implementation" / "implementation_notes" / "test_assets" / "build_bl016_synthetic_assets.py",
        "bl004_script": root / "07_implementation" / "implementation_notes" / "profile" / "build_bl004_preference_profile.py",
        "bl005_script": root / "07_implementation" / "implementation_notes" / "retrieval" / "build_bl005_candidate_filter.py",
        "bl006_script": root / "07_implementation" / "implementation_notes" / "scoring" / "build_bl006_scored_candidates.py",
        "bl007_script": root / "07_implementation" / "implementation_notes" / "playlist" / "build_bl007_playlist.py",
        "bl008_script": root / "07_implementation" / "implementation_notes" / "transparency" / "build_bl008_explanation_payloads.py",
        "bl009_script": Path(__file__).resolve(),
    }

    missing_paths = [relpath(path, root) for path in paths.values() if not path.exists()]
    if missing_paths:
        raise FileNotFoundError(f"BL-009 missing required inputs: {missing_paths}")

    start_time = time.time()

    bl017_coverage = load_json(paths["bl017_coverage"])
    bl016_manifest = load_json(paths["bl016_manifest"])
    bl004_profile = load_json(paths["bl004_profile"])
    bl004_summary = load_json(paths["bl004_summary"])
    bl005_diagnostics = load_json(paths["bl005_diagnostics"])
    bl006_summary = load_json(paths["bl006_summary"])
    bl007_report = load_json(paths["bl007_report"])
    bl008_summary = load_json(paths["bl008_summary"])

    bl005_decisions = load_csv_rows(paths["bl005_decisions"])
    bl007_trace = load_csv_rows(paths["bl007_trace"])
    bl007_playlist = load_json(paths["bl007_playlist"])
    bl008_payloads = load_json(paths["bl008_payloads"])

    generated_at_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_id = f"BL009-OBSERVE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    script_hashes = {
        relpath(paths[key], root): sha256_of_file(paths[key])
        for key in [
            "bl017_script",
            "bl016_script",
            "bl004_script",
            "bl005_script",
            "bl006_script",
            "bl007_script",
            "bl008_script",
            "bl009_script",
        ]
    }
    pipeline_version = combined_sha256([script_hashes[key] for key in sorted(script_hashes)])

    dataset_component_hashes = {
        relpath(paths["bl017_coverage"], root): sha256_of_file(paths["bl017_coverage"]),
        relpath(paths["bl016_manifest"], root): sha256_of_file(paths["bl016_manifest"]),
        relpath(paths["bl016_events"], root): sha256_of_file(paths["bl016_events"]),
        relpath(paths["bl016_candidates"], root): sha256_of_file(paths["bl016_candidates"]),
    }
    dataset_version = combined_sha256([dataset_component_hashes[key] for key in sorted(dataset_component_hashes)])

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
        for row in first_items(rejected_non_seed, 5)
    ]

    assembly_excluded = [row for row in bl007_trace if row.get("decision") == "excluded"]
    assembly_rule_samples_raw = parse_exclusion_samples(assembly_excluded, "exclusion_reason", 3)
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

    artifact_hashes = {
        relpath(path, root): sha256_of_file(path)
        for key, path in paths.items()
        if key not in {
            "bl017_script",
            "bl016_script",
            "bl004_script",
            "bl005_script",
            "bl006_script",
            "bl007_script",
            "bl008_script",
            "bl009_script",
        }
    }

    artifact_sizes = {
        relpath(path, root): path.stat().st_size
        for key, path in paths.items()
        if key not in {
            "bl017_script",
            "bl016_script",
            "bl004_script",
            "bl005_script",
            "bl006_script",
            "bl007_script",
            "bl008_script",
            "bl009_script",
        }
    }

    run_log = {
        "run_metadata": {
            "run_id": run_id,
            "task": "BL-009",
            "generated_at_utc": generated_at_utc,
            "elapsed_seconds": None,
            "observability_scope": "artifact-level deterministic audit log",
            "bootstrap_mode": True,
            "dataset_version": dataset_version,
            "pipeline_version": pipeline_version,
            "dataset_component_hashes": dataset_component_hashes,
            "pipeline_script_hashes": script_hashes,
            "upstream_stage_run_ids": {
                "BL-004": bl004_profile["run_id"],
                "BL-005": bl005_diagnostics["run_id"],
                "BL-006": bl006_summary["run_id"],
                "BL-007": bl007_report["run_id"],
                "BL-008": bl008_summary["run_id"],
            },
        },
        "run_config": {
            "data_layer": bl017_coverage["run_metadata"],
            "bootstrap_assets": bl016_manifest["selection_rules"],
            "profile": bl004_profile["config"],
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
            "stage_status": "deferred_bootstrap_mode",
            "reason": "BL-001 to BL-003 were intentionally deferred under the synthetic pre-aligned bootstrap strategy (D-005).",
            "surrogate_inputs": {
                "aligned_events_path": relpath(paths["bl016_events"], root),
                "candidate_stub_path": relpath(paths["bl016_candidates"], root),
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
            "data_layer": {
                "task": "BL-017",
                "track_id_universe_count": bl017_coverage["track_id_universe_count"],
                "source_track_counts": bl017_coverage["source_track_counts"],
                "join_intersections": bl017_coverage["join_intersections"],
                "availability_counts": bl017_coverage["availability_counts"],
            },
            "bootstrap_assets": {
                "task": "BL-016",
                "summary": bl016_manifest["summary"],
                "history_track_ids": bl016_manifest["history_track_ids"],
                "influence_track_ids": bl016_manifest["influence_track_ids"],
            },
            "profile": {
                "task": "BL-004",
                "run_id": bl004_profile["run_id"],
                "user_id": bl004_profile["user_id"],
                "diagnostics": bl004_profile["diagnostics"],
                "seed_summary": bl004_profile["seed_summary"],
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
            },
            "assembly": {
                "task": "BL-007",
                "run_id": bl007_report["run_id"],
                "counts": bl007_report["counts"],
                "rule_hits": bl007_report["rule_hits"],
                "playlist_genre_mix": bl007_report["playlist_genre_mix"],
                "playlist_score_range": bl007_report["playlist_score_range"],
                "playlist_length": bl007_playlist["playlist_length"],
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
                "data_layer_coverage": {
                    "path": relpath(paths["bl017_coverage"], root),
                    "sha256": artifact_hashes[relpath(paths["bl017_coverage"], root)],
                },
                "bootstrap_manifest": {
                    "path": relpath(paths["bl016_manifest"], root),
                    "sha256": artifact_hashes[relpath(paths["bl016_manifest"], root)],
                },
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
            },
        },
    }

    ensure_required_sections(run_log)

    run_log["run_metadata"]["elapsed_seconds"] = round(time.time() - start_time, 3)

    run_log_path = output_dir / "bl009_run_observability_log.json"
    run_log_path.write_text(json.dumps(run_log, indent=2, ensure_ascii=True), encoding="utf-8")

    run_index_path = output_dir / "bl009_run_index.csv"
    run_index_row = {
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "dataset_version": dataset_version,
        "pipeline_version": pipeline_version,
        "bootstrap_mode": 1,
        "profile_run_id": bl004_profile["run_id"],
        "retrieval_run_id": bl005_diagnostics["run_id"],
        "scoring_run_id": bl006_summary["run_id"],
        "assembly_run_id": bl007_report["run_id"],
        "transparency_run_id": bl008_summary["run_id"],
        "kept_candidates": bl005_diagnostics["counts"]["kept_candidates"],
        "candidates_scored": bl006_summary["counts"]["candidates_scored"],
        "playlist_length": bl007_playlist["playlist_length"],
        "explanation_count": len(bl008_payloads["explanations"]),
        "playlist_sha256": artifact_hashes[relpath(paths["bl007_playlist"], root)],
        "explanation_payloads_sha256": artifact_hashes[relpath(paths["bl008_payloads"], root)],
        "observability_log_sha256": sha256_of_file(run_log_path),
    }
    with run_index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(run_index_row.keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(run_index_row)

    print("BL-009 observability logging complete.")
    print(f"run_log={run_log_path}")
    print(f"run_index={run_index_path}")
    print(f"run_id={run_id}")


if __name__ == "__main__":
    main()