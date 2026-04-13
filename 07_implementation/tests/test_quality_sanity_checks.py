"""Tier-A unit tests for quality.sanity_checks helper functions."""

import csv
import json
from pathlib import Path

import pytest

from quality import sanity_checks
from quality.sanity_checks import (
    bl003_bl004_handshake_contract_ok,
    bl005_filtered_has_required_columns,
    csv_header,
    csv_row_count,
    ensure_exists,
    sha256_file,
)


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_bl014_fixture(tmp_path: Path, *, include_runtime_scope_diagnostics: bool) -> Path:
    repo_root = tmp_path / "impl"
    repo_root.mkdir(parents=True, exist_ok=True)

    bl003_summary_path = repo_root / "alignment/outputs/bl003_ds001_spotify_summary.json"
    bl003_seed_table_path = repo_root / "alignment/outputs/bl003_ds001_spotify_seed_table.csv"
    profile_path = repo_root / "profile/outputs/bl004_preference_profile.json"
    bl004_summary_path = repo_root / "profile/outputs/profile_summary.json"
    bl004_seed_trace_path = repo_root / "profile/outputs/bl004_seed_trace.csv"
    bl005_filtered_path = repo_root / "retrieval/outputs/bl005_filtered_candidates.csv"
    bl005_decisions_path = repo_root / "retrieval/outputs/bl005_candidate_decisions.csv"
    bl005_diag_path = repo_root / "retrieval/outputs/bl005_candidate_diagnostics.json"
    bl006_scored_path = repo_root / "scoring/outputs/bl006_scored_candidates.csv"
    bl006_summary_path = repo_root / "scoring/outputs/bl006_score_summary.json"
    playlist_path = repo_root / "playlist/outputs/playlist.json"
    bl007_trace_path = repo_root / "playlist/outputs/bl007_assembly_trace.csv"
    bl007_report_path = repo_root / "playlist/outputs/bl007_assembly_report.json"
    bl008_payloads_path = repo_root / "transparency/outputs/bl008_explanation_payloads.json"
    bl008_summary_path = repo_root / "transparency/outputs/bl008_explanation_summary.json"
    bl009_log_path = repo_root / "observability/outputs/bl009_run_observability_log.json"
    bl009_index_path = repo_root / "observability/outputs/bl009_run_index.csv"
    candidate_stub_path = repo_root / "data_layer/outputs/ds001_working_candidate_dataset.csv"

    _write_csv(
        bl003_seed_table_path,
        [
            ["ds001_id", "match_confidence_score"],
            ["track_1", "1.0"],
        ],
    )
    _write_csv(bl004_seed_trace_path, [["seed_rank", "track_id"], ["1", "track_1"]])
    _write_csv(
        bl005_filtered_path,
        [
            ["id", "track_id", "artist", "song", "tags", "genres", "tempo", "duration_ms", "key", "mode"],
            ["cand_1", "track_1", "Artist A", "Song A", "rock", "rock", "120", "180000", "1", "1"],
        ],
    )
    _write_csv(
        bl005_decisions_path,
        [["track_id", "semantic_score", "decision", "decision_reason"], ["track_1", "0.9", "keep", "ok"]],
    )
    _write_csv(
        bl006_scored_path,
        [["rank", "track_id", "lead_genre", "final_score", "lead_genre_contribution", "genre_overlap_contribution", "tag_overlap_contribution"], ["1", "track_1", "rock", "0.95", "0.3", "0.3", "0.35"]],
    )
    _write_csv(bl007_trace_path, [["rank", "track_id"], ["1", "track_1"]])
    _write_csv(candidate_stub_path, [["track_id", "artist", "song"], ["track_1", "Artist A", "Song A"]])

    summary_inputs = {
        "seed_contract": {
            "seed_contract_schema_version": "bl003-seed-contract-v1",
            "contract_hash": "seed-contract-hash",
        },
        "structural_contract": {
            "structural_contract_schema_version": "bl003-structural-contract-v1",
            "contract_hash": "structural-contract-hash",
            "seed_table_fieldnames": ["ds001_id", "match_confidence_score"],
        },
        "fuzzy_matching": {"enabled": False},
    }
    if include_runtime_scope_diagnostics:
        summary_inputs["runtime_scope_diagnostics"] = {"resolution_path": "run_config"}

    _write_json(
        bl003_summary_path,
        {
            "inputs": summary_inputs,
            "counts": {"matched_by_fuzzy": 0},
            "outputs": {},
        },
    )

    _write_json(
        profile_path,
        {
            "run_id": "BL004-PROFILE-TEST",
            "diagnostics": {
                "validation_policies": {
                    "bl003_handshake_validation_policy": "warn",
                }
            },
            "input_artifacts": {
                "seed_table_path": str(bl003_seed_table_path),
                "seed_table_sha256": sha256_file(bl003_seed_table_path),
            },
        },
    )
    _write_json(
        bl004_summary_path,
        {
            "run_id": "BL004-PROFILE-TEST",
            "task": "BL-004",
            "user_id": "user_1",
            "matched_seed_count": 1,
            "total_effective_weight": 1.0,
            "dominant_lead_genres": [],
            "dominant_tags": [],
            "dominant_genres": [],
            "feature_centers": {},
            "input_hashes": {},
        },
    )

    _write_json(
        bl005_diag_path,
        {
            "run_id": "BL005-FILTER-TEST",
            "counts": {"kept_candidates": 1},
            "input_artifacts": {
                "profile_sha256": sha256_file(profile_path),
                "seed_trace_sha256": sha256_file(bl004_seed_trace_path),
                "candidate_stub_path": str(candidate_stub_path),
                "candidate_stub_sha256": sha256_file(candidate_stub_path),
            },
            "output_hashes_sha256": {
                "bl005_filtered_candidates.csv": sha256_file(bl005_filtered_path),
                "bl005_candidate_decisions.csv": sha256_file(bl005_decisions_path),
            },
        },
    )
    _write_json(
        bl006_summary_path,
        {
            "run_id": "BL006-SCORE-TEST",
            "counts": {"candidates_scored": 1},
            "input_artifacts": {
                "profile_sha256": sha256_file(profile_path),
                "filtered_candidates_sha256": sha256_file(bl005_filtered_path),
            },
            "output_hashes_sha256": {
                "bl006_scored_candidates.csv": sha256_file(bl006_scored_path),
            },
        },
    )
    _write_json(
        playlist_path,
        {
            "playlist_length": 1,
            "tracks": [{"track_id": "track_1"}],
            "config": {"target_size": 1},
        },
    )
    _write_json(
        bl007_report_path,
        {
            "run_id": "BL007-ASSEMBLE-TEST",
            "input_artifact_hashes": {
                "bl006_scored_candidates.csv": sha256_file(bl006_scored_path),
            },
            "output_artifact_hashes": {
                "playlist.json": sha256_file(playlist_path),
                "bl007_assembly_trace.csv": sha256_file(bl007_trace_path),
            },
        },
    )
    _write_json(
        bl008_payloads_path,
        {
            "playlist_track_count": 1,
            "explanations": [{"track_id": "track_1"}],
        },
    )
    _write_json(
        bl008_summary_path,
        {
            "run_id": "BL008-EXPLAIN-TEST",
            "input_artifact_hashes": {
                "bl006_scored_candidates.csv": sha256_file(bl006_scored_path),
                "bl006_score_summary.json": sha256_file(bl006_summary_path),
                "playlist.json": sha256_file(playlist_path),
                "bl007_assembly_trace.csv": sha256_file(bl007_trace_path),
            },
            "output_artifact_hashes": {
                "bl008_explanation_payloads.json": sha256_file(bl008_payloads_path),
            },
        },
    )
    _write_json(
        bl009_log_path,
        {
            "run_metadata": {},
            "run_config": {"alignment_seed_controls": {"fuzzy_matching": {"enabled": False}}},
            "ingestion_alignment_diagnostics": {},
            "stage_diagnostics": {"alignment": {"counts": {"matched_by_fuzzy": 0}}},
            "exclusion_diagnostics": {},
            "output_artifacts": {},
        },
    )
    _write_csv(
        bl009_index_path,
        [[
            "run_id",
            "profile_run_id",
            "retrieval_run_id",
            "scoring_run_id",
            "assembly_run_id",
            "transparency_run_id",
            "kept_candidates",
            "candidates_scored",
            "playlist_length",
            "explanation_count",
            "playlist_sha256",
            "explanation_payloads_sha256",
            "observability_log_sha256",
        ], [
            "BL009-OBSERVE-TEST",
            "BL004-PROFILE-TEST",
            "BL005-FILTER-TEST",
            "BL006-SCORE-TEST",
            "BL007-ASSEMBLE-TEST",
            "BL008-EXPLAIN-TEST",
            "1",
            "1",
            "1",
            "1",
            sha256_file(playlist_path),
            sha256_file(bl008_payloads_path),
            sha256_file(bl009_log_path),
        ]],
    )

    return repo_root


def test_csv_header_reads_first_row(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.csv"
    _write_csv(file_path, [["a", "b"], ["1", "2"]])
    assert csv_header(file_path) == ["a", "b"]


def test_csv_row_count_excludes_header(tmp_path: Path) -> None:
    file_path = tmp_path / "rows.csv"
    _write_csv(file_path, [["a"], ["1"], ["2"], ["3"]])
    assert csv_row_count(file_path) == 3


def test_ensure_exists_passes_for_existing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "exists.txt"
    file_path.write_text("ok", encoding="utf-8")
    ensure_exists(file_path)


def test_ensure_exists_raises_for_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        ensure_exists(missing)


def test_sha256_file_returns_uppercase_hex(tmp_path: Path) -> None:
    file_path = tmp_path / "hash.txt"
    file_path.write_text("hello", encoding="utf-8")
    digest = sha256_file(file_path)
    assert len(digest) == 64
    assert digest == digest.upper()


def test_bl005_filtered_has_required_columns_accepts_cid_contract() -> None:
    header = [
        "cid",
        "artist",
        "song",
        "tags",
        "genres",
        "tempo",
        "duration_ms",
        "key",
        "mode",
        "track_id",
    ]

    assert bl005_filtered_has_required_columns(header) is True


def test_bl005_filtered_has_required_columns_requires_source_identifier() -> None:
    header = [
        "artist",
        "song",
        "tags",
        "genres",
        "tempo",
        "duration_ms",
        "key",
        "mode",
        "track_id",
    ]

    assert bl005_filtered_has_required_columns(header) is False


def test_bl003_bl004_handshake_contract_ok_when_fields_present() -> None:
    ok, details = bl003_bl004_handshake_contract_ok(
        bl003_summary={
            "inputs": {
                "runtime_scope_diagnostics": {"resolution_path": "run_config"},
                "structural_contract": {
                    "seed_table_fieldnames": ["match_confidence_score", "ds001_id"],
                },
            }
        },
        bl004_profile={
            "diagnostics": {
                "validation_policies": {
                    "bl003_handshake_validation_policy": "warn",
                }
            }
        },
    )

    assert ok is True
    assert "present" in details


def test_bl003_bl004_handshake_contract_fails_when_fields_missing() -> None:
    ok, details = bl003_bl004_handshake_contract_ok(
        bl003_summary={"inputs": {"structural_contract": {"seed_table_fieldnames": ["ds001_id"]}}},
        bl004_profile={"diagnostics": {"validation_policies": {}}},
    )

    assert ok is False
    assert "missing summary input keys" in details
    assert "missing structural seed fields" in details
    assert "missing BL-004 diagnostics.validation_policies.bl003_handshake_validation_policy" in details


def test_bl014_main_fails_on_missing_handshake_contract(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    repo_root = _build_bl014_fixture(tmp_path, include_runtime_scope_diagnostics=False)
    output_dir = tmp_path / "quality_outputs"

    monkeypatch.setattr(sanity_checks, "REPO_ROOT", repo_root)
    monkeypatch.setattr(sanity_checks, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(
        sanity_checks,
        "bl003_required_paths",
        lambda _root: {
            "summary": repo_root / "alignment/outputs/bl003_ds001_spotify_summary.json",
            "seed_table": repo_root / "alignment/outputs/bl003_ds001_spotify_seed_table.csv",
        },
    )

    exit_code = sanity_checks.main()

    assert exit_code == 1
    report = json.loads((output_dir / "bl014_sanity_report.json").read_text(encoding="utf-8"))
    failed_checks = {check["id"]: check for check in report["checks"] if check["status"] == "fail"}
    assert report["overall_status"] == "fail"
    assert set(failed_checks) == {"schema_bl003_bl004_handshake_contract"}
    assert "missing summary input keys" in failed_checks["schema_bl003_bl004_handshake_contract"]["details"]
