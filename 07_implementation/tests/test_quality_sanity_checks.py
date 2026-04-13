"""Tier-A unit tests for quality.sanity_checks helper functions."""

import csv
import json
from pathlib import Path

import pytest

from quality import sanity_checks
from quality.sanity_checks import (
    bl008_explanation_fidelity_warnings,
    bl008_bl009_handshake_contract_ok,
    bl005_control_resolution_fallback_volume_advisory,
    bl005_handshake_warning_volume_advisory,
    bl007_bl008_handshake_contract_ok,
    bl006_bl007_handshake_contract_ok,
    bl005_bl006_handshake_contract_ok,
    bl004_bl005_handshake_contract_ok,
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


def _build_bl014_fixture(
    tmp_path: Path,
    *,
    include_runtime_scope_diagnostics: bool,
    include_numeric_confidence: bool = True,
    include_bl005_handshake_policy: bool = True,
    include_bl006_handshake_policy: bool = True,
    include_bl007_handshake_policy: bool = True,
    include_bl008_handshake_policy: bool = True,
    include_bl009_handshake_policy: bool = True,
    runtime_control_normalization_event_count: int = 0,
) -> Path:
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
    _write_csv(
        bl004_seed_trace_path,
        [["seed_rank", "track_id", "match_confidence_score"], ["1", "track_1", "1.0"]],
    )
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
    _write_csv(bl007_trace_path, [["rank", "track_id", "decision", "score_rank"], ["1", "track_1", "included", "1"]])
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

    profile_payload = {
        "run_id": "BL004-PROFILE-TEST",
        "semantic_profile": {
            "top_tags": [{"label": "rock", "weight": 1.0}],
            "top_genres": [{"label": "rock", "weight": 1.0}],
            "top_lead_genres": [{"label": "rock", "weight": 1.0}],
        },
        "numeric_feature_profile": {"tempo": 120.0},
        "diagnostics": {
            "validation_policies": {
                "bl003_handshake_validation_policy": "warn",
            }
        },
        "input_artifacts": {
            "seed_table_path": str(bl003_seed_table_path),
            "seed_table_sha256": sha256_file(bl003_seed_table_path),
        },
    }
    if include_numeric_confidence:
        profile_payload["numeric_confidence"] = {"confidence_by_feature": {"tempo": 1.0}}
    _write_json(profile_path, profile_payload)
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

    bl005_diagnostics_payload = {
        "run_id": "BL005-FILTER-TEST",
        "config": {
            "validation_policies": {
                "bl004_bl005_handshake_validation_policy": "warn",
            },
            "runtime_control_resolution": {
                "normalization_event_count": runtime_control_normalization_event_count,
                "normalization_event_counts_by_field": {
                    "profile_top_tag_limit": runtime_control_normalization_event_count,
                },
                "normalization_events_sampled": [
                    {
                        "field": "profile_top_tag_limit",
                        "reason": "coerced_to_positive_int",
                        "raw": "bad",
                        "normalized": 10,
                    }
                ],
            },
        },
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
    }
    if not include_bl005_handshake_policy:
        bl005_diagnostics_payload["config"] = {"validation_policies": {}}
    _write_json(bl005_diag_path, bl005_diagnostics_payload)
    _write_json(
        bl006_summary_path,
        {
            "run_id": "BL006-SCORE-TEST",
            "counts": {"candidates_scored": 1},
            "config": {
                "validation_policies": {
                    "bl005_bl006_handshake_validation_policy": "warn",
                }
            },
            "validation": {"status": "pass"},
            "input_artifacts": {
                "profile_sha256": sha256_file(profile_path),
                "filtered_candidates_sha256": sha256_file(bl005_filtered_path),
            },
            "output_hashes_sha256": {
                "bl006_scored_candidates.csv": sha256_file(bl006_scored_path),
            },
        },
    )
    if not include_bl006_handshake_policy:
        _write_json(
            bl006_summary_path,
            {
                "run_id": "BL006-SCORE-TEST",
                "counts": {"candidates_scored": 1},
                "config": {"validation_policies": {}},
                "validation": {},
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
            "tracks": [{"track_id": "track_1", "final_score": 0.85, "playlist_position": 1}],
            "config": {"target_size": 1},
        },
    )
    _write_json(
        bl007_report_path,
        {
            "run_id": "BL007-ASSEMBLE-TEST",
            "config": {
                "validation_policies": {
                    "bl006_bl007_handshake_validation_policy": "warn",
                }
            },
            "validation": {"status": "pass"},
            "input_artifact_hashes": {
                "bl006_scored_candidates.csv": sha256_file(bl006_scored_path),
            },
            "output_artifact_hashes": {
                "playlist.json": sha256_file(playlist_path),
                "bl007_assembly_trace.csv": sha256_file(bl007_trace_path),
            },
        },
    )
    if not include_bl007_handshake_policy:
        _write_json(
            bl007_report_path,
            {
                "run_id": "BL007-ASSEMBLE-TEST",
                "config": {"validation_policies": {}},
                "validation": {},
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
            "explanations": [
                {
                    "track_id": "track_1",
                    "final_score": 0.85,
                    "why_selected": "Selected at playlist position 1 (score 0.8500) because it shows a strong profile match on Lead genre match. Lead genre is 'rock'.",
                    "primary_explanation_driver": {"label": "Lead genre match"},
                    "causal_driver": {"label": "Lead genre match"},
                    "narrative_driver": {"label": "Lead genre match"},
                    "top_score_contributors": [{"label": "Lead genre match"}],
                    "score_breakdown": [
                        {
                            "label": "Lead genre match",
                            "contribution": 0.95,
                            "contribution_share_pct": 100.0,
                            "margin_vs_next_contributor": 0.0,
                        }
                    ],
                    "assembly_context": {
                        "decision": "included",
                        "admission_rule": "Admitted on first evaluation",
                        "genre_at_position": "rock",
                    },
                }
            ],
        },
    )
    _write_json(
        bl008_summary_path,
        {
            "run_id": "BL008-EXPLAIN-TEST",
            "playlist_track_count": 1,
            "top_contributor_distribution": {"Lead genre match": 1},
            "config": {
                "validation_policies": {
                    "bl007_bl008_handshake_validation_policy": "warn",
                }
            },
            "validation": {"status": "pass"},
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
    if not include_bl008_handshake_policy:
        _write_json(
            bl008_summary_path,
            {
                "run_id": "BL008-EXPLAIN-TEST",
                "playlist_track_count": 1,
                "top_contributor_distribution": {"Lead genre match": 1},
                "config": {"validation_policies": {}},
                "validation": {},
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
            "run_config": {
                "alignment_seed_controls": {"fuzzy_matching": {"enabled": False}},
                "observability": {
                    "validation_policies": {
                        "bl008_bl009_handshake_validation_policy": "warn"
                    }
                },
            },
            "validation": {"status": "pass"},
            "ingestion_alignment_diagnostics": {},
            "stage_diagnostics": {"alignment": {"counts": {"matched_by_fuzzy": 0}}},
            "exclusion_diagnostics": {},
            "output_artifacts": {},
        },
    )
    if not include_bl009_handshake_policy:
        _write_json(
            bl009_log_path,
            {
                "run_metadata": {},
                "run_config": {
                    "alignment_seed_controls": {"fuzzy_matching": {"enabled": False}},
                    "observability": {"validation_policies": {}},
                },
                "validation": {},
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


def test_bl004_bl005_handshake_contract_ok_when_fields_present() -> None:
    ok, details = bl004_bl005_handshake_contract_ok(
        bl004_profile={
            "semantic_profile": {},
            "numeric_feature_profile": {},
            "numeric_confidence": {},
            "input_artifacts": {},
        },
        bl005_diagnostics={
            "config": {
                "validation_policies": {
                    "bl004_bl005_handshake_validation_policy": "warn",
                }
            }
        },
        bl004_seed_trace_header=["track_id", "match_confidence_score"],
    )

    assert ok is True
    assert "present" in details


def test_bl004_bl005_handshake_contract_fails_when_fields_missing() -> None:
    ok, details = bl004_bl005_handshake_contract_ok(
        bl004_profile={"run_id": "BL004-PROFILE-TEST"},
        bl005_diagnostics={"config": {}},
        bl004_seed_trace_header=[],
    )

    assert ok is False
    assert "missing BL-004 profile keys" in details
    assert "missing BL-004 seed trace fields" in details
    assert "missing BL-005 config.validation_policies.bl004_bl005_handshake_validation_policy" in details


def test_bl005_bl006_handshake_contract_ok_when_fields_present() -> None:
    ok, details = bl005_bl006_handshake_contract_ok(
        bl005_filtered_header=[
            "cid",
            "track_id",
            "artist",
            "song",
            "tags",
            "genres",
            "tempo",
            "duration_ms",
            "key",
            "mode",
        ],
        bl006_summary={
            "config": {
                "validation_policies": {
                    "bl005_bl006_handshake_validation_policy": "warn",
                }
            },
            "validation": {"status": "pass"},
        },
    )

    assert ok is True
    assert "present" in details


def test_bl005_bl006_handshake_contract_fails_when_fields_missing() -> None:
    ok, details = bl005_bl006_handshake_contract_ok(
        bl005_filtered_header=["track_id"],
        bl006_summary={"config": {}, "validation": {}},
    )

    assert ok is False
    assert "missing BL-005 filtered fields" in details
    assert "missing BL-005 source identifier field=id_or_cid" in details
    assert "missing BL-006 config.validation_policies.bl005_bl006_handshake_validation_policy" in details
    assert "missing BL-006 validation.status" in details


def test_bl005_handshake_warning_volume_advisory_emits_when_warn_volume_exceeds_threshold() -> None:
    advisory = bl005_handshake_warning_volume_advisory(
        {
            "config": {
                "validation_policies": {
                    "bl004_bl005_handshake_validation_policy": "warn",
                }
            },
            "validation": {
                "status": "warn",
                "control_constraint_violations": ["v1", "v2", "v3", "v4"],
                "sampled_violations": ["v1", "v2", "v3", "v4"],
            },
        },
        threshold=3,
    )

    assert advisory is not None
    assert advisory["id"] == "advisory_bl005_handshake_warning_volume"
    assert "4 > 3" in advisory["details"]


def test_bl005_handshake_warning_volume_advisory_not_emitted_when_within_threshold() -> None:
    advisory = bl005_handshake_warning_volume_advisory(
        {
            "config": {
                "validation_policies": {
                    "bl004_bl005_handshake_validation_policy": "warn",
                }
            },
            "validation": {
                "status": "warn",
                "control_constraint_violations": ["v1", "v2", "v3"],
                "sampled_violations": ["v1", "v2", "v3"],
            },
        },
        threshold=3,
    )

    assert advisory is None


def test_bl005_control_resolution_fallback_volume_advisory_emits_when_volume_exceeds_threshold() -> None:
    advisory = bl005_control_resolution_fallback_volume_advisory(
        {
            "config": {
                "runtime_control_resolution": {
                    "normalization_event_count": 4,
                    "normalization_event_counts_by_field": {
                        "profile_top_tag_limit": 4,
                    },
                    "normalization_events_sampled": [{"field": "profile_top_tag_limit"}],
                }
            }
        },
        threshold=3,
    )

    assert advisory is not None
    assert advisory["id"] == "advisory_bl005_control_resolution_fallback_volume"
    assert "4 > 3" in advisory["details"]


def test_bl005_control_resolution_fallback_volume_advisory_not_emitted_when_within_threshold() -> None:
    advisory = bl005_control_resolution_fallback_volume_advisory(
        {
            "config": {
                "runtime_control_resolution": {
                    "normalization_event_count": 3,
                }
            }
        },
        threshold=3,
    )

    assert advisory is None


def test_bl008_explanation_fidelity_warnings_none_for_coherent_payload() -> None:
    warnings = bl008_explanation_fidelity_warnings(
        {
            "explanations": [
                {
                    "final_score": 0.8,
                    "why_selected": "Selected because it shows a strong profile match on Tempo (BPM).",
                    "primary_explanation_driver": {"label": "Tempo (BPM)"},
                    "causal_driver": {"label": "Tempo (BPM)"},
                    "top_score_contributors": [{"label": "Tempo (BPM)"}],
                    "score_breakdown": [
                        {
                            "label": "Tempo (BPM)",
                            "contribution": 0.4,
                            "contribution_share_pct": 100.0,
                            "margin_vs_next_contributor": 0.0,
                        }
                    ],
                    "assembly_context": {
                        "decision": "included",
                        "admission_rule": "Admitted on first evaluation",
                        "genre_at_position": "rock",
                    },
                }
            ]
        }
    )
    assert warnings == []


def test_bl008_explanation_fidelity_warnings_detect_mismatch() -> None:
    warnings = bl008_explanation_fidelity_warnings(
        {
            "explanations": [
                {
                    "final_score": 0.82,
                    "why_selected": "Selected because it shows a moderate profile match on Tag overlap.",
                    "primary_explanation_driver": {"label": "Tag overlap"},
                    "causal_driver": {"label": "Tag overlap"},
                    "top_score_contributors": [{"label": "Tempo (BPM)"}],
                    "score_breakdown": [
                        {
                            "label": "Tempo (BPM)",
                            "contribution": 0.4,
                            "contribution_share_pct": 70.0,
                            "margin_vs_next_contributor": -0.1,
                        },
                        {
                            "label": "Tag overlap",
                            "contribution": 0.2,
                            "contribution_share_pct": 20.0,
                            "margin_vs_next_contributor": 0.0,
                        },
                    ],
                    "assembly_context": {"decision": "included"},
                }
            ]
        }
    )
    assert any("primary_driver_not_in_top_contributors" in warning for warning in warnings)
    assert any("why_selected_score_band_mismatch" in warning for warning in warnings)
    assert any("negative_margin_vs_next_contributor" in warning for warning in warnings)
    assert any("assembly_context_incomplete" in warning for warning in warnings)


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


def test_bl014_main_fails_on_missing_bl004_bl005_handshake_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = _build_bl014_fixture(
        tmp_path,
        include_runtime_scope_diagnostics=True,
        include_numeric_confidence=False,
    )
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
    assert set(failed_checks) == {"schema_bl004_bl005_handshake_contract"}
    assert "missing BL-004 profile keys" in failed_checks["schema_bl004_bl005_handshake_contract"]["details"]


def test_bl014_main_emits_control_resolution_advisory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = _build_bl014_fixture(
        tmp_path,
        include_runtime_scope_diagnostics=True,
        runtime_control_normalization_event_count=5,
    )
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

    assert exit_code == 0
    report = json.loads((output_dir / "bl014_sanity_report.json").read_text(encoding="utf-8"))
    advisories = {item["id"]: item for item in report["advisories"]}
    assert report["overall_status"] == "pass"
    assert "advisory_bl005_control_resolution_fallback_volume" in advisories


def test_bl014_main_fails_on_missing_bl005_bl006_handshake_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = _build_bl014_fixture(
        tmp_path,
        include_runtime_scope_diagnostics=True,
        include_bl006_handshake_policy=False,
    )
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
    assert set(failed_checks) == {"schema_bl005_bl006_handshake_contract"}
    assert "missing BL-006 config.validation_policies.bl005_bl006_handshake_validation_policy" in failed_checks[
        "schema_bl005_bl006_handshake_contract"
    ]["details"]


# ---------------------------------------------------------------------------
# Unit tests for bl006_bl007_handshake_contract_ok
# ---------------------------------------------------------------------------


def _bl006_scored_header_full() -> list[str]:
    return [
        "rank",
        "track_id",
        "lead_genre",
        "final_score",
        "matched_genres",
        "matched_tags",
        "lead_genre_contribution",
        "genre_overlap_contribution",
        "tag_overlap_contribution",
    ]


def _bl007_report_full() -> dict:
    return {
        "run_id": "BL007-TEST",
        "config": {
            "validation_policies": {
                "bl006_bl007_handshake_validation_policy": "warn",
            }
        },
        "validation": {"status": "pass"},
    }


def test_bl006_bl007_handshake_contract_ok_when_fields_present() -> None:
    ok, details = bl006_bl007_handshake_contract_ok(
        _bl006_scored_header_full(),
        _bl007_report_full(),
    )

    assert ok is True
    assert "present" in details


def test_bl006_bl007_handshake_contract_fails_missing_required_scored_fields() -> None:
    header = ["track_id", "final_score", "lead_genre_contribution"]  # missing rank/matched_*

    ok, details = bl006_bl007_handshake_contract_ok(header, _bl007_report_full())

    assert ok is False
    assert "missing BL-006 scored fields" in details


def test_bl006_bl007_handshake_contract_fails_when_no_scoring_component_columns() -> None:
    header = ["rank", "track_id", "lead_genre", "final_score", "matched_genres", "matched_tags"]

    ok, details = bl006_bl007_handshake_contract_ok(header, _bl007_report_full())

    assert ok is False
    assert "missing BL-006 scoring component contribution columns" in details


def test_bl006_bl007_handshake_contract_fails_when_policy_missing() -> None:
    report = {
        "config": {"validation_policies": {}},
        "validation": {"status": "pass"},
    }

    ok, details = bl006_bl007_handshake_contract_ok(_bl006_scored_header_full(), report)

    assert ok is False
    assert "missing BL-007 config.validation_policies.bl006_bl007_handshake_validation_policy" in details


def test_bl006_bl007_handshake_contract_fails_when_validation_status_missing() -> None:
    report = {
        "config": {
            "validation_policies": {"bl006_bl007_handshake_validation_policy": "warn"}
        },
        "validation": {},
    }

    ok, details = bl006_bl007_handshake_contract_ok(_bl006_scored_header_full(), report)

    assert ok is False
    assert "missing BL-007 report validation.status" in details


# ---------------------------------------------------------------------------
# BL-014 integration — schema_bl006_bl007_handshake_contract
# ---------------------------------------------------------------------------


def test_bl014_main_fails_on_missing_bl006_bl007_handshake_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = _build_bl014_fixture(
        tmp_path,
        include_runtime_scope_diagnostics=True,
        include_bl007_handshake_policy=False,
    )
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
    assert set(failed_checks) == {"schema_bl006_bl007_handshake_contract"}
    assert "missing BL-007 config.validation_policies.bl006_bl007_handshake_validation_policy" in failed_checks[
        "schema_bl006_bl007_handshake_contract"
    ]["details"]


# ---------------------------------------------------------------------------
# Unit tests for bl007_bl008_handshake_contract_ok
# ---------------------------------------------------------------------------


def _bl007_playlist_full() -> dict:
    return {
        "playlist_length": 1,
        "tracks": [{"track_id": "track_1", "final_score": 0.85, "playlist_position": 1}],
    }


def _bl008_summary_full() -> dict:
    return {
        "run_id": "BL008-TEST",
        "config": {
            "validation_policies": {
                "bl007_bl008_handshake_validation_policy": "warn",
            }
        },
        "validation": {"status": "pass"},
    }


def test_bl007_bl008_handshake_contract_ok_when_fields_present() -> None:
    ok, details = bl007_bl008_handshake_contract_ok(
        _bl007_playlist_full(),
        _bl008_summary_full(),
    )

    assert ok is True
    assert "present" in details


def test_bl007_bl008_handshake_contract_fails_when_playlist_empty() -> None:
    playlist = {"playlist_length": 0, "tracks": []}

    ok, details = bl007_bl008_handshake_contract_ok(playlist, _bl008_summary_full())

    assert ok is False
    assert "playlist tracks list is empty" in details


def test_bl007_bl008_handshake_contract_fails_when_track_fields_missing() -> None:
    playlist = {
        "playlist_length": 1,
        "tracks": [{"track_id": "t1", "final_score": 0.8}],  # missing playlist_position
    }

    ok, details = bl007_bl008_handshake_contract_ok(playlist, _bl008_summary_full())

    assert ok is False
    assert "missing BL-007 playlist track fields" in details
    assert "playlist_position" in details


def test_bl007_bl008_handshake_contract_fails_when_policy_missing() -> None:
    summary = {
        "config": {"validation_policies": {}},
        "validation": {"status": "pass"},
    }

    ok, details = bl007_bl008_handshake_contract_ok(_bl007_playlist_full(), summary)

    assert ok is False
    assert "missing BL-008 config.validation_policies.bl007_bl008_handshake_validation_policy" in details


def test_bl007_bl008_handshake_contract_fails_when_validation_status_missing() -> None:
    summary = {
        "config": {
            "validation_policies": {"bl007_bl008_handshake_validation_policy": "warn"}
        },
        "validation": {},
    }

    ok, details = bl007_bl008_handshake_contract_ok(_bl007_playlist_full(), summary)

    assert ok is False
    assert "missing BL-008 summary validation.status" in details


def _bl009_log_full() -> dict:
    return {
        "run_config": {
            "observability": {
                "validation_policies": {
                    "bl008_bl009_handshake_validation_policy": "warn"
                }
            }
        },
        "validation": {"status": "pass"},
    }


def test_bl008_bl009_handshake_contract_ok_when_fields_present() -> None:
    ok, details = bl008_bl009_handshake_contract_ok(
        {
            "run_id": "BL008-TEST",
            "playlist_track_count": 1,
            "top_contributor_distribution": {"Lead genre match": 1},
        },
        {
            "playlist_track_count": 1,
            "explanations": [{"track_id": "track_1"}],
        },
        _bl009_log_full(),
    )

    assert ok is True
    assert "present" in details


def test_bl008_bl009_handshake_contract_fails_when_summary_keys_missing() -> None:
    ok, details = bl008_bl009_handshake_contract_ok(
        {"run_id": "BL008-TEST"},
        {"playlist_track_count": 1, "explanations": [{"track_id": "track_1"}]},
        _bl009_log_full(),
    )

    assert ok is False
    assert "missing BL-008 summary keys" in details


def test_bl008_bl009_handshake_contract_fails_when_counts_mismatch() -> None:
    ok, details = bl008_bl009_handshake_contract_ok(
        {
            "run_id": "BL008-TEST",
            "playlist_track_count": 2,
            "top_contributor_distribution": {"Lead genre match": 1},
        },
        {
            "playlist_track_count": 1,
            "explanations": [{"track_id": "track_1"}],
        },
        _bl009_log_full(),
    )

    assert ok is False
    assert "counts are inconsistent" in details


def test_bl008_bl009_handshake_contract_fails_when_policy_missing() -> None:
    ok, details = bl008_bl009_handshake_contract_ok(
        {
            "run_id": "BL008-TEST",
            "playlist_track_count": 1,
            "top_contributor_distribution": {"Lead genre match": 1},
        },
        {
            "playlist_track_count": 1,
            "explanations": [{"track_id": "track_1"}],
        },
        {"run_config": {"observability": {"validation_policies": {}}}, "validation": {"status": "pass"}},
    )

    assert ok is False
    assert "missing BL-009 run_config.observability.validation_policies.bl008_bl009_handshake_validation_policy" in details


def test_bl008_bl009_handshake_contract_fails_when_validation_status_missing() -> None:
    ok, details = bl008_bl009_handshake_contract_ok(
        {
            "run_id": "BL008-TEST",
            "playlist_track_count": 1,
            "top_contributor_distribution": {"Lead genre match": 1},
        },
        {
            "playlist_track_count": 1,
            "explanations": [{"track_id": "track_1"}],
        },
        {
            "run_config": {
                "observability": {
                    "validation_policies": {"bl008_bl009_handshake_validation_policy": "warn"}
                }
            },
            "validation": {},
        },
    )

    assert ok is False
    assert "missing BL-009 log validation.status" in details


# ---------------------------------------------------------------------------
# BL-014 integration — schema_bl007_bl008_handshake_contract
# ---------------------------------------------------------------------------


def test_bl014_main_fails_on_missing_bl007_bl008_handshake_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = _build_bl014_fixture(
        tmp_path,
        include_runtime_scope_diagnostics=True,
        include_bl008_handshake_policy=False,
    )
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
    assert set(failed_checks) == {"schema_bl007_bl008_handshake_contract"}
    assert "missing BL-008 config.validation_policies.bl007_bl008_handshake_validation_policy" in failed_checks[
        "schema_bl007_bl008_handshake_contract"
    ]["details"]


def test_bl014_main_fails_on_missing_bl008_bl009_handshake_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = _build_bl014_fixture(
        tmp_path,
        include_runtime_scope_diagnostics=True,
        include_bl009_handshake_policy=False,
    )
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
    assert set(failed_checks) == {"schema_bl008_bl009_handshake_contract"}
    assert "missing BL-009 run_config.observability.validation_policies.bl008_bl009_handshake_validation_policy" in failed_checks[
        "schema_bl008_bl009_handshake_contract"
    ]["details"]
