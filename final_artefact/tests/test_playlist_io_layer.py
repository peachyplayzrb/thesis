"""Tests for playlist.io_layer."""

import csv
import json
from pathlib import Path

import pytest

from playlist.io_layer import (
    read_scored_candidates,
    resolve_bl007_paths,
    write_assembly_trace,
    write_detail_log,
    write_playlist,
    write_report,
)


def test_resolve_bl007_paths_reads_environment(monkeypatch, tmp_path: Path) -> None:
    scored = tmp_path / "scored.csv"
    out = tmp_path / "out"
    monkeypatch.setenv("BL007_SCORED_CANDIDATES_PATH", str(scored))
    monkeypatch.setenv("BL007_OUTPUT_DIR", str(out))

    resolved_scored, resolved_out = resolve_bl007_paths()

    assert resolved_scored == scored
    assert resolved_out == out


def test_read_scored_candidates_raises_on_missing_required_column(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["rank", "track_id", "final_score"])
        writer.writeheader()
        writer.writerow({"rank": 1, "track_id": "t1", "final_score": 0.5})

    with pytest.raises(ValueError):
        read_scored_candidates(path)


def test_write_helpers_emit_artifacts(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.csv"
    playlist_path = tmp_path / "playlist.json"
    report_path = tmp_path / "report.json"
    detail_path = tmp_path / "detail.json"

    write_assembly_trace(
        trace_path,
        [
            {
                "score_rank": 1,
                "track_id": "t1",
                "lead_genre": "rock",
                "final_score": 0.9,
                "decision": "included",
                "playlist_position": 1,
                "exclusion_reason": "",
            }
        ],
    )
    write_playlist(playlist_path, {"tracks": [{"track_id": "t1"}]})
    write_report(report_path, {"counts": {"tracks_included": 1}})
    write_detail_log(detail_path, {"rows": []})

    assert trace_path.exists()
    assert playlist_path.exists()
    assert report_path.exists()
    assert detail_path.exists()

    playlist_payload = json.loads(playlist_path.read_text(encoding="utf-8"))
    report_payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert playlist_payload["tracks"][0]["track_id"] == "t1"
    assert report_payload["counts"]["tracks_included"] == 1
