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
            "tempo_similarity",
            "tempo_contribution",
            "tag_overlap_similarity",
            "tag_overlap_contribution",
        ],
        [
            {
                "track_id": "t1",
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
    assert payloads["explanations"][0]["primary_explanation_driver"]["label"] == "Tempo (BPM)"
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
