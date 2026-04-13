"""Tier-A unit tests for transparency.input_validation — BL-007↔BL-008 handshake."""

from __future__ import annotations

from typing import Mapping

import pytest

from transparency.input_validation import (
    normalize_validation_policy,
    validate_bl007_bl008_handshake,
    REQUIRED_BL007_PLAYLIST_TRACK_FIELDS,
    REQUIRED_BL007_TRACE_FIELDS,
)


def _full_trace_header() -> list[str]:
    return ["track_id", "decision", "score_rank", "exclusion_reason", "inclusion_path"]


def _full_playlist_tracks() -> list[Mapping[str, object]]:
    return [
        {
            "track_id": "track_1",
            "final_score": 0.85,
            "playlist_position": 1,
            "lead_genre": "rock",
            "score_rank": 2,
        }
    ]


# ---------------------------------------------------------------------------
# normalize_validation_policy
# ---------------------------------------------------------------------------


def test_normalize_validation_policy_accepts_valid_values() -> None:
    assert normalize_validation_policy("allow") == "allow"
    assert normalize_validation_policy("warn") == "warn"
    assert normalize_validation_policy("strict") == "strict"


def test_normalize_validation_policy_falls_back_for_unknown() -> None:
    assert normalize_validation_policy("bad_value") == "warn"
    assert normalize_validation_policy(None) == "warn"


def test_normalize_validation_policy_respects_custom_default() -> None:
    assert normalize_validation_policy("invalid", default="allow") == "allow"


# ---------------------------------------------------------------------------
# validate_bl007_bl008_handshake — pass paths
# ---------------------------------------------------------------------------


def test_handshake_passes_with_full_data() -> None:
    result = validate_bl007_bl008_handshake(
        playlist_tracks=_full_playlist_tracks(),
        trace_header=_full_trace_header(),
        policy="warn",
    )
    assert result["status"] == "pass"
    assert result["policy"] == "warn"
    assert result["control_constraint_violations"] == []


def test_handshake_passes_under_strict_when_no_violations() -> None:
    result = validate_bl007_bl008_handshake(
        playlist_tracks=_full_playlist_tracks(),
        trace_header=_full_trace_header(),
        policy="strict",
    )
    assert result["status"] == "pass"


# ---------------------------------------------------------------------------
# validate_bl007_bl008_handshake — violation detection
# ---------------------------------------------------------------------------


def test_handshake_detects_empty_playlist() -> None:
    result = validate_bl007_bl008_handshake(
        playlist_tracks=[],
        trace_header=_full_trace_header(),
        policy="warn",
    )
    assert result["status"] == "warn"
    assert any("playlist_tracks_empty" in v for v in result["control_constraint_violations"])


def test_handshake_detects_missing_playlist_track_fields() -> None:
    tracks = [{"track_id": "t1", "final_score": 0.9}]  # missing playlist_position
    result = validate_bl007_bl008_handshake(
        playlist_tracks=tracks,
        trace_header=_full_trace_header(),
        policy="warn",
    )
    assert result["status"] == "warn"
    assert result["missing_bl007_playlist_track_fields"] == ["playlist_position"]


def test_handshake_detects_missing_trace_fields() -> None:
    result = validate_bl007_bl008_handshake(
        playlist_tracks=_full_playlist_tracks(),
        trace_header=["track_id"],  # missing decision, score_rank
        policy="warn",
    )
    assert result["status"] == "warn"
    assert "decision" in result["missing_bl007_trace_fields"]
    assert "score_rank" in result["missing_bl007_trace_fields"]


def test_handshake_detects_rows_missing_track_id() -> None:
    tracks = [{"track_id": "", "final_score": 0.8, "playlist_position": 1}]
    result = validate_bl007_bl008_handshake(
        playlist_tracks=tracks,
        trace_header=_full_trace_header(),
        policy="warn",
    )
    assert result["status"] == "warn"
    assert result["playlist_rows_missing_track_id"] == 1


def test_handshake_detects_rows_missing_score() -> None:
    tracks = [{"track_id": "t1", "final_score": "nan", "playlist_position": 1}]
    result = validate_bl007_bl008_handshake(
        playlist_tracks=tracks,
        trace_header=_full_trace_header(),
        policy="warn",
    )
    assert result["status"] == "warn"
    assert result["playlist_rows_missing_final_score"] == 1


# ---------------------------------------------------------------------------
# validate_bl007_bl008_handshake — policy mode behaviour
# ---------------------------------------------------------------------------


def test_handshake_strict_fails_on_violations() -> None:
    result = validate_bl007_bl008_handshake(
        playlist_tracks=[],
        trace_header=_full_trace_header(),
        policy="strict",
    )
    assert result["status"] == "fail"


def test_handshake_allow_mode_does_not_escalate_violations() -> None:
    result = validate_bl007_bl008_handshake(
        playlist_tracks=[],
        trace_header=_full_trace_header(),
        policy="allow",
    )
    assert result["status"] == "allow"


def test_handshake_returns_sampled_violations_subset() -> None:
    tracks = [{"track_id": "", "final_score": "nan", "playlist_position": 1}]
    result = validate_bl007_bl008_handshake(
        playlist_tracks=tracks,
        trace_header=[],
        policy="warn",
    )
    assert isinstance(result["sampled_violations"], list)
    assert len(result["sampled_violations"]) <= 10
