"""Regression tests for DS-001 ID variant resolution across BL-003 paths."""

from __future__ import annotations

import json
from pathlib import Path

from alignment.constants import ALIGNMENT_OUTPUT_FILENAMES
from alignment.match_pipeline import match_events
from alignment.stage import AlignmentStage
from shared_utils.index_builder import resolve_ds001_id


def _event(*, spotify_track_id: str) -> dict[str, str]:
    return {
        "source_type": "saved_tracks",
        "spotify_track_id": spotify_track_id,
        "track_name": "Song",
        "artist_names": "Artist",
        "duration_ms": "200000",
        "time_range": "",
        "rank": "1",
        "playlist_position": "1",
        "source_row_index": "1",
        "isrc": "",
        "event_time": "",
        "playlist_id": "",
        "playlist_name": "",
    }


def test_resolve_ds001_id_accepts_schema_variants() -> None:
    assert resolve_ds001_id({"id": "track_id"}) == "track_id"
    assert resolve_ds001_id({"ds001_id": "track_ds001"}) == "track_ds001"
    assert resolve_ds001_id({"cid": "track_cid"}) == "track_cid"


def test_match_events_uses_cid_when_id_fields_missing() -> None:
    ds_row = {
        "cid": "cid_track_01",
        "spotify_id": "sp_001",
        "song": "Song",
        "artist": "Artist",
        "duration_ms": "200000",
    }

    trace_rows, matched_events, _, counts = match_events(
        [_event(spotify_track_id="sp_001")],
        {"sp_001": ds_row},
        {},
        {},
        top_range_weights={"short_term": 0.5, "medium_term": 0.3, "long_term": 0.2},
        source_base_weights={"top_tracks": 1.0, "saved_tracks": 0.6, "playlist_items": 0.4, "recently_played": 0.5},
    )

    assert counts["matched_by_spotify_id"] == 1
    assert matched_events[0]["ds001_id"] == "cid_track_01"
    assert trace_rows[0]["matched_ds001_id"] == "cid_track_01"


def test_stage_influence_injection_uses_cid_only_rows(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "input_scope_controls": {
                        "include_top_tracks": False,
                        "include_saved_tracks": False,
                        "include_playlists": False,
                        "include_recently_played": False,
                    },
                    "influence_controls": {
                        "influence_enabled": True,
                        "influence_track_ids": ["cid_track_01"],
                        "influence_preference_weight": 2.0,
                    },
                }
            }
        ),
    )

    ds001_path = tmp_path / "ds001_candidates.csv"
    ds001_path.write_text(
        "cid,spotify_id,song,artist,duration_ms\n"
        "cid_track_01,sp_001,Song,Artist,200000\n",
        encoding="utf-8",
    )

    spotify_dir = tmp_path / "spotify_export"
    spotify_dir.mkdir(parents=True, exist_ok=True)
    output_dir = tmp_path / "outputs"

    stage = AlignmentStage(
        ds001_path=ds001_path,
        spotify_dir=spotify_dir,
        output_dir=output_dir,
        allow_missing_selected_sources=True,
    )
    stage.run()

    matched_jsonl = output_dir / ALIGNMENT_OUTPUT_FILENAMES["matched_jsonl"]
    lines = [line for line in matched_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    payload = [json.loads(line) for line in lines]

    assert len(payload) == 1
    assert payload[0]["source_type"] == "influence"
    assert payload[0]["ds001_id"] == "cid_track_01"
