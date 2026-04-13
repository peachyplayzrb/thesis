"""Integration test for playlist.main."""

import csv
import json
from pathlib import Path

from playlist.main import main


def test_playlist_main_generates_consistent_outputs(tmp_path: Path, monkeypatch) -> None:
    scored_path = tmp_path / "scored.csv"
    output_dir = tmp_path / "out"

    with scored_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["rank", "track_id", "lead_genre", "final_score"],
        )
        writer.writeheader()
        writer.writerow({"rank": 1, "track_id": "t1", "lead_genre": "rock", "final_score": 0.95})
        writer.writerow({"rank": 2, "track_id": "t2", "lead_genre": "rock", "final_score": 0.94})
        writer.writerow({"rank": 3, "track_id": "t3", "lead_genre": "rock", "final_score": 0.93})
        writer.writerow({"rank": 4, "track_id": "t4", "lead_genre": "pop", "final_score": 0.90})

    monkeypatch.setenv("BL007_SCORED_CANDIDATES_PATH", str(scored_path))
    monkeypatch.setenv("BL007_OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("BL007_TARGET_SIZE", "3")
    monkeypatch.setenv("BL007_MIN_SCORE_THRESHOLD", "0.5")
    monkeypatch.setenv("BL007_MAX_PER_GENRE", "2")
    monkeypatch.setenv("BL007_MAX_CONSECUTIVE", "2")

    main()

    playlist_path = output_dir / "playlist.json"
    trace_path = output_dir / "bl007_assembly_trace.csv"
    report_path = output_dir / "bl007_assembly_report.json"
    detail_path = output_dir / "bl007_assembly_detail_log.json"

    assert playlist_path.exists()
    assert trace_path.exists()
    assert report_path.exists()
    assert detail_path.exists()

    playlist = json.loads(playlist_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert playlist["playlist_length"] == 3
    assert report["counts"]["tracks_included"] == 3
    assert report["counts"]["tracks_excluded"] == 1

    # Verify that at least one excluded track was logged in the trace
    trace_rows = list(csv.DictReader(trace_path.open(encoding="utf-8")))
    excluded_rows = [r for r in trace_rows if r.get("decision") != "included"]
    assert len(excluded_rows) >= 1, "Expected at least one excluded track in assembly trace"

    assert report["playlist_genre_mix"] == {"pop": 1, "rock": 2}


def test_playlist_main_with_payload_fixture(tmp_path: Path, monkeypatch) -> None:
    """Phase 4: Test playlist using orchestration-injected payload instead of env vars."""
    scored_path = tmp_path / "scored.csv"
    output_dir = tmp_path / "out"

    with scored_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["rank", "track_id", "lead_genre", "final_score"],
        )
        writer.writeheader()
        writer.writerow({"rank": 1, "track_id": "t1", "lead_genre": "rock", "final_score": 0.95})
        writer.writerow({"rank": 2, "track_id": "t2", "lead_genre": "rock", "final_score": 0.94})
        writer.writerow({"rank": 3, "track_id": "t3", "lead_genre": "rock", "final_score": 0.93})
        writer.writerow({"rank": 4, "track_id": "t4", "lead_genre": "pop", "final_score": 0.90})

    # Phase 4: Use orchestration-injected payload instead of individual env vars
    payload = {
        "target_size": 3,
        "min_score_threshold": 0.5,
        "max_per_genre": 2,
        "max_consecutive": 2,
    }

    # Inject via BL_STAGE_CONFIG_JSON instead of individual BL007_* vars
    monkeypatch.setenv("BL007_SCORED_CANDIDATES_PATH", str(scored_path))
    monkeypatch.setenv("BL007_OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", json.dumps(payload))

    main()

    playlist_path = output_dir / "playlist.json"
    trace_path = output_dir / "bl007_assembly_trace.csv"
    report_path = output_dir / "bl007_assembly_report.json"

    assert playlist_path.exists()
    assert trace_path.exists()
    assert report_path.exists()

    playlist = json.loads(playlist_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))

    # Same validation as legacy test - behavior unchanged
    assert playlist["playlist_length"] == 3
    assert report["counts"]["tracks_included"] == 3
    assert report["counts"]["tracks_excluded"] == 1
