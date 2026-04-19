"""
Golden-artifact reproducibility tests for MFT-C2.

These tests verify that key pipeline assembly functions produce byte-stable,
hash-stable outputs on fixed fixture inputs across runs. Any change to the
assembly logic, serialization, or scoring that would alter the output for
a fixed input will cause these tests to fail — signalling a potential
reproducibility regression.

Policy: golden hashes are computed from a canonical JSON serialization
(sorted keys, no trailing whitespace) of the deterministic output fields.
If a hash changes intentionally (e.g. after a deliberate logic change),
update the constant and document the reason in the change log.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from playlist.main import main as playlist_main
from shared_utils.coerce import clamp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stable_hash(data: Any) -> str:
    """Return SHA-256 of the canonical JSON serialization of *data*."""
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_scored_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Golden constants
# ---------------------------------------------------------------------------

# Expected SHA-256 of the canonical playlist JSON output fields.
# Computed from the deterministic fixture below on first validated run (2026-04-19).
# To regenerate: run the test with -s and read the printed hash, then update.
GOLDEN_PLAYLIST_TRACKS_HASH = "7011583b35be2dcd3892183855dd1907db5a4edf9224df87aa45c438dfc99117"
GOLDEN_PLAYLIST_REPORT_MIX_HASH = "e448ae95ce49fa3156c23cc70ab7420926c46375f5976f9529156aacfd16dc8e"


# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------

def _build_scored_rows() -> list[dict]:
    """Fixed deterministic fixture for golden tests."""
    return [
        {"rank": "1", "track_id": "gold-t1", "lead_genre": "rock", "final_score": "0.95"},
        {"rank": "2", "track_id": "gold-t2", "lead_genre": "rock", "final_score": "0.94"},
        {"rank": "3", "track_id": "gold-t3", "lead_genre": "indie", "final_score": "0.91"},
        {"rank": "4", "track_id": "gold-t4", "lead_genre": "pop",  "final_score": "0.88"},
        {"rank": "5", "track_id": "gold-t5", "lead_genre": "pop",  "final_score": "0.85"},
        {"rank": "6", "track_id": "gold-t6", "lead_genre": "rock", "final_score": "0.80"},
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_playlist_assembly_output_is_hash_stable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify that the playlist assembly produces a byte-stable, hash-stable
    track order and genre mix for a fixed scored-candidates fixture.
    """
    scored_path = tmp_path / "scored.csv"
    output_dir = tmp_path / "out"

    _write_scored_csv(scored_path, _build_scored_rows())

    monkeypatch.setenv("BL007_SCORED_CANDIDATES_PATH", str(scored_path))
    monkeypatch.setenv("BL007_OUTPUT_DIR", str(output_dir))
    monkeypatch.setenv("BL007_TARGET_SIZE", "4")
    monkeypatch.setenv("BL007_MIN_SCORE_THRESHOLD", "0.5")
    monkeypatch.setenv("BL007_MAX_PER_GENRE", "2")
    monkeypatch.setenv("BL007_MAX_CONSECUTIVE", "2")

    playlist_main()

    playlist = json.loads((output_dir / "playlist.json").read_text(encoding="utf-8"))
    report = json.loads((output_dir / "bl007_assembly_report.json").read_text(encoding="utf-8"))

    # Extract only the deterministic structural fields (exclude timestamps/run-ids).
    tracks_fingerprint = [
        {"track_id": t["track_id"], "playlist_position": t["playlist_position"]}
        for t in playlist.get("tracks", [])
    ]
    mix_fingerprint = report.get("playlist_genre_mix", {})

    tracks_hash = _stable_hash(tracks_fingerprint)
    mix_hash = _stable_hash(mix_fingerprint)

    assert tracks_hash == GOLDEN_PLAYLIST_TRACKS_HASH, (
        f"Playlist track order changed.\n"
        f"  Expected: {GOLDEN_PLAYLIST_TRACKS_HASH}\n"
        f"  Got:      {tracks_hash}\n"
        f"  Tracks:   {tracks_fingerprint}"
    )
    assert mix_hash == GOLDEN_PLAYLIST_REPORT_MIX_HASH, (
        f"Playlist genre mix changed.\n"
        f"  Expected: {GOLDEN_PLAYLIST_REPORT_MIX_HASH}\n"
        f"  Got:      {mix_hash}\n"
        f"  Mix:      {mix_fingerprint}"
    )


def test_clamp_output_is_deterministic() -> None:
    """
    Verify that coerce.clamp produces stable outputs for fixed inputs —
    a simple golden-value boundary test for the shared coercion layer.
    """
    cases = [
        (0.0, 0.0, 1.0, 0.0),
        (1.0, 0.0, 1.0, 1.0),
        (0.5, 0.0, 1.0, 0.5),
        (-0.1, 0.0, 1.0, 0.0),
        (1.1, 0.0, 1.0, 1.0),
        (0.35, 0.35, 0.35, 0.35),
    ]
    for value, lo, hi, expected in cases:
        result = clamp(value, lo, hi)
        assert result == expected, f"clamp({value}, {lo}, {hi}) = {result}, expected {expected}"
