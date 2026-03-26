#!/usr/bin/env python3
"""BL-014 sanity checks for BL-020 artifacts.

This script validates:
1. Required artifact presence and schema shape
2. Cross-stage hash-link integrity
3. Basic count continuity across BL-004 to BL-009 outputs

Outputs are written to:
- 07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_report.json
- 07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_run_matrix.csv
- 07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_config_snapshot.json
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.io_utils import load_json as load_json_shared
from bl000_shared_utils.io_utils import sha256_of_file
from bl000_shared_utils.path_utils import repo_root


REPO_ROOT = repo_root()
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def sha256_file(path: Path) -> str:
    return sha256_of_file(path).upper()


def load_json(path: Path) -> dict[str, Any]:
    return load_json_shared(path)


def csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader)
        return sum(1 for _ in reader)


def ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path}")


def main() -> int:
    started = datetime.now(UTC)
    run_id = f"BL014-SANITY-{started.strftime('%Y%m%d-%H%M%S-%f')}"

    artifacts = {
        "bl004_profile": REPO_ROOT / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json",
        "bl004_summary": REPO_ROOT / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json",
        "bl005_filtered": REPO_ROOT / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv",
        "bl005_decisions": REPO_ROOT / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_diag": REPO_ROOT / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl006_scored": REPO_ROOT / "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv",
        "bl006_summary": REPO_ROOT / "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json",
        "bl007_playlist": REPO_ROOT / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json",
        "bl007_trace": REPO_ROOT / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv",
        "bl007_report": REPO_ROOT / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json",
        "bl008_payloads": REPO_ROOT / "07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_payloads.json",
        "bl008_summary": REPO_ROOT / "07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json",
        "bl009_log": REPO_ROOT / "07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json",
        "bl009_index": REPO_ROOT / "07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_index.csv",
        "bl004_seed_trace": REPO_ROOT / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv",
    }

    for artifact_path in artifacts.values():
        ensure_exists(artifact_path)

    bl004_summary = load_json(artifacts["bl004_summary"])
    bl005_diag = load_json(artifacts["bl005_diag"])
    bl006_summary = load_json(artifacts["bl006_summary"])
    bl007_report = load_json(artifacts["bl007_report"])
    bl008_summary = load_json(artifacts["bl008_summary"])
    bl008_payloads = load_json(artifacts["bl008_payloads"])
    bl007_playlist = load_json(artifacts["bl007_playlist"])
    bl009_log = load_json(artifacts["bl009_log"])

    with artifacts["bl009_index"].open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        bl009_index_rows = list(reader)
    if len(bl009_index_rows) != 1:
        raise RuntimeError("Expected exactly one row in bl009_run_index.csv")
    bl009_index = bl009_index_rows[0]

    hashes = {name: sha256_file(path) for name, path in artifacts.items()}

    checks: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, details: str) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "fail", "details": details})

    # Schema checks
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
    check(
        "schema_bl004_summary",
        profile_required.issubset(set(bl004_summary.keys())),
        "BL-004 summary contains required top-level keys",
    )

    filtered_required_cols = {
        "track_id",
        "id",
        "artist",
        "song",
        "tags",
        "genres",
        "tempo",
        "duration_ms",
        "key",
        "mode",
    }
    candidate_stub_path = Path(bl005_diag["input_artifacts"]["candidate_stub_path"])
    ensure_exists(candidate_stub_path)
    candidate_stub_hash = sha256_file(candidate_stub_path)

    check(
        "schema_bl005_filtered_csv",
        filtered_required_cols.issubset(set(csv_header(artifacts["bl005_filtered"]))),
        "BL-005 filtered candidates CSV contains required columns",
    )

    decisions_required_cols = {
        "track_id",
        "semantic_score",
        "decision",
        "decision_reason",
    }
    check(
        "schema_bl005_decisions_csv",
        decisions_required_cols.issubset(set(csv_header(artifacts["bl005_decisions"]))),
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
    check(
        "schema_bl006_scored_csv",
        scored_required_cols.issubset(set(csv_header(artifacts["bl006_scored"]))),
        "BL-006 scored candidates CSV contains required columns",
    )

    check(
        "schema_bl007_playlist_json",
        isinstance(bl007_playlist.get("tracks"), list)
        and bl007_playlist.get("playlist_length") == len(bl007_playlist.get("tracks", [])),
        "BL-007 playlist JSON tracks length matches playlist_length",
    )

    check(
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
    check(
        "schema_bl009_observability_log",
        obs_required_sections.issubset(set(bl009_log.keys())),
        "BL-009 observability log contains required sections",
    )

    # Hash-link integrity checks
    check(
        "hash_bl005_input_profile",
        bl005_diag["input_artifacts"]["profile_sha256"].upper() == hashes["bl004_profile"],
        "BL-005 references BL-004 profile hash correctly",
    )
    check(
        "hash_bl005_input_seed_trace",
        bl005_diag["input_artifacts"]["seed_trace_sha256"].upper() == hashes["bl004_seed_trace"],
        "BL-005 references BL-004 seed trace hash correctly",
    )
    check(
        "hash_bl005_input_dataset",
        bl005_diag["input_artifacts"]["candidate_stub_sha256"].upper() == candidate_stub_hash,
        "BL-005 references candidate dataset hash correctly",
    )
    check(
        "hash_bl005_outputs",
        bl005_diag["output_hashes_sha256"]["bl005_filtered_candidates.csv"].upper() == hashes["bl005_filtered"]
        and bl005_diag["output_hashes_sha256"]["bl005_candidate_decisions.csv"].upper() == hashes["bl005_decisions"],
        "BL-005 output hashes match actual files",
    )

    check(
        "hash_bl006_inputs",
        bl006_summary["input_artifacts"]["profile_sha256"].upper() == hashes["bl004_profile"]
        and bl006_summary["input_artifacts"]["filtered_candidates_sha256"].upper() == hashes["bl005_filtered"],
        "BL-006 input hashes match BL-004 and BL-005 outputs",
    )
    check(
        "hash_bl006_output",
        bl006_summary["output_hashes_sha256"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"],
        "BL-006 output hash matches actual scored CSV",
    )

    check(
        "hash_bl007_links",
        bl007_report["input_artifact_hashes"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"]
        and bl007_report["output_artifact_hashes"]["bl007_playlist.json"].upper() == hashes["bl007_playlist"]
        and bl007_report["output_artifact_hashes"]["bl007_assembly_trace.csv"].upper() == hashes["bl007_trace"],
        "BL-007 report links to BL-006 input and BL-007 outputs correctly",
    )

    check(
        "hash_bl008_links",
        bl008_summary["input_artifact_hashes"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"]
        and bl008_summary["input_artifact_hashes"]["bl006_score_summary.json"].upper() == hashes["bl006_summary"]
        and bl008_summary["input_artifact_hashes"]["bl007_playlist.json"].upper() == hashes["bl007_playlist"]
        and bl008_summary["input_artifact_hashes"]["bl007_assembly_trace.csv"].upper() == hashes["bl007_trace"]
        and bl008_summary["output_artifact_hashes"]["bl008_explanation_payloads.json"].upper() == hashes["bl008_payloads"],
        "BL-008 summary links to upstream inputs and output hash correctly",
    )

    check(
        "hash_bl009_index",
        bl009_index["playlist_sha256"].upper() == hashes["bl007_playlist"]
        and bl009_index["explanation_payloads_sha256"].upper() == hashes["bl008_payloads"]
        and bl009_index["observability_log_sha256"].upper() == hashes["bl009_log"],
        "BL-009 index hashes match playlist, explanation payloads, and observability log",
    )

    # Count/run-id continuity checks
    bl005_kept = int(bl005_diag["counts"]["kept_candidates"])
    bl005_rows = csv_row_count(artifacts["bl005_filtered"])
    check(
        "continuity_bl005_count",
        bl005_kept == bl005_rows,
        f"BL-005 kept_candidates ({bl005_kept}) equals filtered CSV rows ({bl005_rows})",
    )

    bl006_scored_count = int(bl006_summary["counts"]["candidates_scored"])
    bl006_rows = csv_row_count(artifacts["bl006_scored"])
    check(
        "continuity_bl006_count",
        bl006_scored_count == bl006_rows,
        f"BL-006 candidates_scored ({bl006_scored_count}) equals scored CSV rows ({bl006_rows})",
    )

    playlist_len = int(bl007_playlist["playlist_length"])
    bl007_target_size = int((bl007_playlist.get("config") or {}).get("target_size", playlist_len))
    undersized_shortfall = max(0, bl007_target_size - playlist_len)
    undersized_playlist = undersized_shortfall > 0
    explanations_len = int(bl008_payloads["playlist_track_count"])
    check(
        "continuity_bl007_bl008_counts",
        playlist_len == len(bl007_playlist["tracks"]) == explanations_len == len(bl008_payloads["explanations"]),
        "BL-007 playlist length and BL-008 explanation count are aligned",
    )

    check(
        "quality_bl007_target_size_met",
        playlist_len >= bl007_target_size,
        f"BL-007 playlist length ({playlist_len}) meets target_size ({bl007_target_size})",
    )

    check(
        "continuity_bl009_index_counts",
        int(bl009_index["kept_candidates"]) == bl005_kept
        and int(bl009_index["candidates_scored"]) == bl006_scored_count
        and int(bl009_index["playlist_length"]) == playlist_len
        and int(bl009_index["explanation_count"]) == explanations_len,
        "BL-009 index counts match BL-005/006/007/008 outputs",
    )

    check(
        "continuity_bl009_run_ids",
        bl009_index["profile_run_id"] == bl004_summary["run_id"]
        and bl009_index["retrieval_run_id"] == bl005_diag["run_id"]
        and bl009_index["scoring_run_id"] == bl006_summary["run_id"]
        and bl009_index["assembly_run_id"] == bl007_report["run_id"]
        and bl009_index["transparency_run_id"] == bl008_summary["run_id"],
        "BL-009 index run_ids match upstream stage run_ids",
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

    passed = sum(1 for item in checks if item["status"] == "pass")
    failed = len(checks) - passed
    overall_status = "pass" if failed == 0 else "fail"

    finished = datetime.now(UTC)
    elapsed_seconds = round((finished - started).total_seconds(), 3)

    report = {
        "run_id": run_id,
        "task": "BL-014",
        "generated_at_utc": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_seconds": elapsed_seconds,
        "overall_status": overall_status,
        "checks_total": len(checks),
        "checks_passed": passed,
        "checks_failed": failed,
        "advisories_total": len(advisories),
        "advisories": advisories,
        "artifact_hashes_sha256": {k: v for k, v in hashes.items()},
        "checks": checks,
    }

    config_snapshot = {
        "task": "BL-014",
        "description": "Automated sanity checks for BL-020 artifact schema, hash linkage, and count continuity",
        "run_id": run_id,
        "required_artifacts": {k: str(v.relative_to(REPO_ROOT)) for k, v in artifacts.items()},
        "schema_checks": [
            "BL-004 summary top-level keys",
            "BL-005 filtered CSV required columns",
            "BL-005 decisions CSV required columns",
            "BL-006 scored CSV required columns",
            "BL-007 playlist length consistency",
            "BL-008 explanation count consistency",
            "BL-009 required top-level observability sections",
        ],
        "integrity_checks": [
            "BL-005 input/output hashes",
            "BL-006 input/output hashes",
            "BL-007 input/output hashes",
            "BL-008 input/output hashes",
            "BL-009 index hash linkage",
        ],
        "continuity_checks": [
            "BL-005 kept count matches filtered rows",
            "BL-006 scored count matches scored rows",
            "BL-007 playlist count aligns with BL-008 explanations",
            "BL-007 playlist meets configured target size",
            "BL-009 index counts align with upstream stage outputs",
            "BL-009 run_id linkage aligns with upstream stage summaries",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "bl014_sanity_report.json"
    config_path = OUTPUT_DIR / "bl014_sanity_config_snapshot.json"
    matrix_path = OUTPUT_DIR / "bl014_sanity_run_matrix.csv"

    with report_path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    with config_path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(config_snapshot, handle, indent=2)
        handle.write("\n")

    with matrix_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "run_id",
                "generated_at_utc",
                "overall_status",
                "checks_total",
                "checks_passed",
                "checks_failed",
                "bl005_kept_candidates",
                "bl006_candidates_scored",
                "playlist_length",
                "bl007_target_size",
                "undersized_playlist",
                "undersized_shortfall",
                "explanation_count",
                "bl009_run_id",
                "bl007_playlist_sha256",
                "bl008_payloads_sha256",
                "bl009_log_sha256",
            ],
        )
        writer.writeheader()
        writer.writerow(
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
                "bl009_run_id": bl009_index["run_id"],
                "bl007_playlist_sha256": hashes["bl007_playlist"],
                "bl008_payloads_sha256": hashes["bl008_payloads"],
                "bl009_log_sha256": hashes["bl009_log"],
            }
        )

    print(f"[BL-014] run_id={run_id}")
    print(f"[BL-014] overall_status={overall_status} checks_passed={passed}/{len(checks)}")
    print(f"[BL-014] report={report_path}")
    print(f"[BL-014] run_matrix={matrix_path}")
    print(f"[BL-014] config_snapshot={config_path}")

    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
