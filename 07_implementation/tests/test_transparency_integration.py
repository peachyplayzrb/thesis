"""Integration tests for transparency.main."""

import csv
import json
from pathlib import Path

from transparency.main import main


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_transparency_main_writes_outputs_and_hash_fields(tmp_path: Path, monkeypatch) -> None:
    scored_csv = tmp_path / "scored.csv"
    score_summary_json = tmp_path / "score_summary.json"
    playlist_json = tmp_path / "playlist.json"
    trace_csv = tmp_path / "trace.csv"
    output_dir = tmp_path / "out"

    _write_csv(
        scored_csv,
        [
            "track_id",
            "raw_final_score",
            "tempo_similarity",
            "tempo_contribution",
            "tag_overlap_similarity",
            "tag_overlap_contribution",
        ],
        [
            {
                "track_id": "t1",
                "raw_final_score": 0.75,
                "tempo_similarity": 0.9,
                "tempo_contribution": 0.40,
                "tag_overlap_similarity": 0.8,
                "tag_overlap_contribution": 0.39,
            }
        ],
    )
    score_summary_json.write_text(
        json.dumps(
            {
                "config": {
                    "active_component_weights": {
                        "tempo_score": 0.5,
                        "tag_overlap_score": 0.5,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    playlist_json.write_text(
        json.dumps(
            {
                "tracks": [
                    {
                        "playlist_position": 1,
                        "track_id": "t1",
                        "lead_genre": "rock",
                        "final_score": 0.79,
                        "score_rank": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        trace_csv,
        [
            "track_id",
            "decision",
            "exclusion_reason",
        ],
        [{"track_id": "t1", "decision": "included", "exclusion_reason": ""}],
    )

    monkeypatch.setenv("BL008_SCORED_CSV_PATH", str(scored_csv))
    monkeypatch.setenv("BL008_SCORE_SUMMARY_PATH", str(score_summary_json))
    monkeypatch.setenv("BL008_PLAYLIST_PATH", str(playlist_json))
    monkeypatch.setenv("BL008_TRACE_CSV_PATH", str(trace_csv))
    monkeypatch.setenv("BL008_OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("BL008_BLEND_PRIMARY_CONTRIBUTOR_ON_NEAR_TIE", "true")
    monkeypatch.setenv("BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA", "0.02")

    main()

    payloads_path = output_dir / "bl008_explanation_payloads.json"
    summary_path = output_dir / "bl008_explanation_summary.json"
    assert payloads_path.exists()
    assert summary_path.exists()

    payloads = json.loads(payloads_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert payloads["playlist_track_count"] == 1
    assert payloads["explanations"][0]["track_id"] == "t1"
    assert payloads["explanations"][0]["raw_final_score"] == 0.75
    assert payloads["explanations"][0]["primary_explanation_driver"]["label"] == "Tempo (BPM)"
    assert payloads["explanations"][0]["control_provenance_ref"] == "run_level"
    assert payloads["explanations"][0]["control_causality"]["schema_version"] == "bl008-control-causality-v1"
    assert "controlling_parameters" in payloads["explanations"][0]["control_causality"]
    assert isinstance(payloads["control_provenance_summary"], dict)
    assert "scoring" in payloads["control_provenance_summary"]
    assert summary["playlist_track_count"] == 1
    assert len(summary["input_artifact_hashes"]["bl006_scored_candidates.csv"]) == 64
    assert len(summary["output_artifact_hashes"]["bl008_explanation_payloads.json"]) == 64


def test_transparency_main_handles_playlist_track_missing_in_scored_index(
    tmp_path: Path,
    monkeypatch,
) -> None:
    scored_csv = tmp_path / "scored.csv"
    score_summary_json = tmp_path / "score_summary.json"
    playlist_json = tmp_path / "playlist.json"
    trace_csv = tmp_path / "trace.csv"
    output_dir = tmp_path / "out"

    _write_csv(
        scored_csv,
        ["track_id", "tempo_similarity", "tempo_contribution"],
        [{"track_id": "other", "tempo_similarity": 1.0, "tempo_contribution": 0.5}],
    )
    score_summary_json.write_text(
        json.dumps({"config": {"active_component_weights": {"tempo_score": 1.0}}}),
        encoding="utf-8",
    )
    playlist_json.write_text(
        json.dumps(
            {
                "tracks": [
                    {
                        "playlist_position": 1,
                        "track_id": "missing",
                        "lead_genre": "ambient",
                        "final_score": 0.5,
                        "score_rank": 5,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        trace_csv,
        ["track_id", "decision", "exclusion_reason"],
        [{"track_id": "missing", "decision": "included", "exclusion_reason": ""}],
    )

    monkeypatch.setenv("BL008_SCORED_CSV_PATH", str(scored_csv))
    monkeypatch.setenv("BL008_SCORE_SUMMARY_PATH", str(score_summary_json))
    monkeypatch.setenv("BL008_PLAYLIST_PATH", str(playlist_json))
    monkeypatch.setenv("BL008_TRACE_CSV_PATH", str(trace_csv))
    monkeypatch.setenv("BL008_OUTPUT_DIR", str(output_dir))

    main()

    payloads_path = output_dir / "bl008_explanation_payloads.json"
    payloads = json.loads(payloads_path.read_text(encoding="utf-8"))
    explanation = payloads["explanations"][0]
    assert explanation["track_id"] == "missing"
    assert explanation["score_breakdown"][0]["similarity"] == 0.0


def test_transparency_main_supports_provenance_dedup_toggles(tmp_path: Path, monkeypatch) -> None:
    scored_csv = tmp_path / "scored.csv"
    score_summary_json = tmp_path / "score_summary.json"
    playlist_json = tmp_path / "playlist.json"
    trace_csv = tmp_path / "trace.csv"
    output_dir = tmp_path / "out"

    _write_csv(
        scored_csv,
        ["track_id", "tempo_similarity", "tempo_contribution"],
        [{"track_id": "t1", "tempo_similarity": 0.9, "tempo_contribution": 0.4}],
    )
    score_summary_json.write_text(
        json.dumps({"config": {"active_component_weights": {"tempo_score": 1.0}}}),
        encoding="utf-8",
    )
    playlist_json.write_text(
        json.dumps(
            {
                "tracks": [
                    {
                        "playlist_position": 1,
                        "track_id": "t1",
                        "lead_genre": "rock",
                        "final_score": 0.79,
                        "score_rank": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        trace_csv,
        ["track_id", "decision", "exclusion_reason"],
        [{"track_id": "t1", "decision": "included", "exclusion_reason": ""}],
    )

    monkeypatch.setenv("BL008_SCORED_CSV_PATH", str(scored_csv))
    monkeypatch.setenv("BL008_SCORE_SUMMARY_PATH", str(score_summary_json))
    monkeypatch.setenv("BL008_PLAYLIST_PATH", str(playlist_json))
    monkeypatch.setenv("BL008_TRACE_CSV_PATH", str(trace_csv))
    monkeypatch.setenv("BL008_OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("BL008_INCLUDE_PER_TRACK_CONTROL_PROVENANCE", "false")
    monkeypatch.setenv("BL008_EMIT_RUN_LEVEL_CONTROL_PROVENANCE_SUMMARY", "false")

    main()

    payloads = json.loads((output_dir / "bl008_explanation_payloads.json").read_text(encoding="utf-8"))
    explanation = payloads["explanations"][0]
    assert explanation["control_provenance"] == {}
    assert explanation["control_provenance_ref"] == "inline"
    assert payloads["control_provenance_summary"] == {}


def test_transparency_main_enriches_assembly_context_from_report(tmp_path: Path, monkeypatch) -> None:
    scored_csv = tmp_path / "scored.csv"
    score_summary_json = tmp_path / "score_summary.json"
    playlist_json = tmp_path / "playlist.json"
    trace_csv = tmp_path / "trace.csv"
    report_json = tmp_path / "report.json"
    output_dir = tmp_path / "out"

    _write_csv(
        scored_csv,
        ["track_id", "tempo_similarity", "tempo_contribution"],
        [{"track_id": "t1", "tempo_similarity": 0.9, "tempo_contribution": 0.4}],
    )
    score_summary_json.write_text(
        json.dumps({"config": {"active_component_weights": {"tempo_score": 1.0}}}),
        encoding="utf-8",
    )
    playlist_json.write_text(
        json.dumps(
            {
                "tracks": [
                    {
                        "playlist_position": 1,
                        "track_id": "t1",
                        "lead_genre": "rock",
                        "final_score": 0.79,
                        "score_rank": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        trace_csv,
        [
            "track_id",
            "score_rank",
            "decision",
            "exclusion_reason",
            "influence_requested",
            "inclusion_path",
        ],
        [
            {
                "track_id": "t1",
                "score_rank": 1,
                "decision": "included",
                "exclusion_reason": "",
                "influence_requested": True,
                "inclusion_path": "competitive",
            }
        ],
    )
    report_json.write_text(
        json.dumps(
            {
                "config": {
                    "influence_policy_mode": "competitive",
                    "influence_enabled": True,
                    "influence_reserved_slots": 2,
                    "validation_policies": {
                        "bl006_bl007_handshake_validation_policy": "warn"
                    },
                },
                "influence_effectiveness_diagnostics": {"effectiveness_rate": 0.5},
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("BL008_SCORED_CSV_PATH", str(scored_csv))
    monkeypatch.setenv("BL008_SCORE_SUMMARY_PATH", str(score_summary_json))
    monkeypatch.setenv("BL008_PLAYLIST_PATH", str(playlist_json))
    monkeypatch.setenv("BL008_TRACE_CSV_PATH", str(trace_csv))
    monkeypatch.setenv("BL008_ASSEMBLY_REPORT_PATH", str(report_json))
    monkeypatch.setenv("BL008_OUTPUT_DIR", str(output_dir))

    main()

    payloads = json.loads((output_dir / "bl008_explanation_payloads.json").read_text(encoding="utf-8"))
    context = payloads["explanations"][0]["assembly_context"]
    assert context["policy_mode"] == "competitive"
    assert context["influence_enabled"] is True
    assert context["inclusion_path"] == "competitive"
    assert context["bl006_bl007_handshake_validation_policy"] == "warn"
    assert context["influence_effectiveness_rate"] == 0.5


def test_transparency_main_records_bl007_bl008_handshake_in_summary(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """BL-008 summary must carry validation_policies and validation.status for BL-014."""
    scored_csv = tmp_path / "scored.csv"
    score_summary_json = tmp_path / "score_summary.json"
    playlist_json = tmp_path / "playlist.json"
    trace_csv = tmp_path / "trace.csv"
    output_dir = tmp_path / "out"

    _write_csv(
        scored_csv,
        ["track_id", "tempo_similarity", "tempo_contribution"],
        [{"track_id": "t1", "tempo_similarity": 0.8, "tempo_contribution": 0.6}],
    )
    score_summary_json.write_text(
        json.dumps({"config": {"active_component_weights": {"tempo_score": 1.0}}}),
        encoding="utf-8",
    )
    playlist_json.write_text(
        json.dumps(
            {
                "tracks": [
                    {
                        "playlist_position": 1,
                        "track_id": "t1",
                        "lead_genre": "pop",
                        "final_score": 0.80,
                        "score_rank": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        trace_csv,
        ["track_id", "decision", "score_rank"],
        [{"track_id": "t1", "decision": "included", "score_rank": "1"}],
    )

    monkeypatch.setenv("BL008_SCORED_CSV_PATH", str(scored_csv))
    monkeypatch.setenv("BL008_SCORE_SUMMARY_PATH", str(score_summary_json))
    monkeypatch.setenv("BL008_PLAYLIST_PATH", str(playlist_json))
    monkeypatch.setenv("BL008_TRACE_CSV_PATH", str(trace_csv))
    monkeypatch.setenv("BL008_OUTPUT_DIR", str(output_dir))

    main()

    summary = json.loads((output_dir / "bl008_explanation_summary.json").read_text(encoding="utf-8"))
    config_policies = summary["config"]["validation_policies"]
    assert "bl007_bl008_handshake_validation_policy" in config_policies
    assert isinstance(summary["validation"]["status"], str)


def test_transparency_main_emits_rejected_track_control_causality(
    tmp_path: Path,
    monkeypatch,
) -> None:
    scored_csv = tmp_path / "scored.csv"
    score_summary_json = tmp_path / "score_summary.json"
    playlist_json = tmp_path / "playlist.json"
    trace_csv = tmp_path / "trace.csv"
    output_dir = tmp_path / "out"

    _write_csv(
        scored_csv,
        [
            "track_id",
            "lead_genre",
            "rank",
            "final_score",
            "raw_final_score",
            "tempo_similarity",
            "tempo_contribution",
        ],
        [
            {
                "track_id": "t1",
                "lead_genre": "rock",
                "rank": 1,
                "final_score": 0.91,
                "raw_final_score": 0.86,
                "tempo_similarity": 0.90,
                "tempo_contribution": 0.40,
            },
            {
                "track_id": "t2",
                "lead_genre": "jazz",
                "rank": 2,
                "final_score": 0.40,
                "raw_final_score": 0.40,
                "tempo_similarity": 0.35,
                "tempo_contribution": 0.10,
            },
        ],
    )
    score_summary_json.write_text(
        json.dumps({"config": {"active_component_weights": {"tempo_score": 1.0}}}),
        encoding="utf-8",
    )
    playlist_json.write_text(
        json.dumps(
            {
                "tracks": [
                    {
                        "playlist_position": 1,
                        "track_id": "t1",
                        "lead_genre": "rock",
                        "final_score": 0.91,
                        "score_rank": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        trace_csv,
        ["track_id", "decision", "score_rank", "exclusion_reason"],
        [
            {"track_id": "t1", "decision": "included", "score_rank": 1, "exclusion_reason": ""},
            {
                "track_id": "t2",
                "decision": "excluded",
                "score_rank": 2,
                "exclusion_reason": "below_score_threshold",
            },
        ],
    )

    monkeypatch.setenv("BL008_SCORED_CSV_PATH", str(scored_csv))
    monkeypatch.setenv("BL008_SCORE_SUMMARY_PATH", str(score_summary_json))
    monkeypatch.setenv("BL008_PLAYLIST_PATH", str(playlist_json))
    monkeypatch.setenv("BL008_TRACE_CSV_PATH", str(trace_csv))
    monkeypatch.setenv("BL008_OUTPUT_DIR", str(output_dir))

    main()

    payloads = json.loads((output_dir / "bl008_explanation_payloads.json").read_text(encoding="utf-8"))
    assert payloads["rejected_track_control_causality_count"] == 1
    assert len(payloads["rejected_track_control_causality"]) == 1
    rejected_payload = payloads["rejected_track_control_causality"][0]
    assert rejected_payload["payload_scope"] == "rejected_track_trace"
    assert rejected_payload["track_id"] == "t2"
    assert rejected_payload["raw_final_score"] == 0.4
    assert rejected_payload["control_causality"]["decision_outcome"]["included_in_playlist"] is False
    assert (
        rejected_payload["control_causality"]["effect_direction"]["expected_direction"]
        == "deprioritize_or_exclude"
    )
