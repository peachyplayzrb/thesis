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
    assert report["rule_hits"].get("R2_genre_cap", 0) + report["rule_hits"].get("R4_length_cap", 0) >= 1
    assert report["playlist_genre_mix"] == {"pop": 1, "rock": 2}
