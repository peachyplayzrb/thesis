"""Tier-A unit tests for ingestion.ingest_history_parser helper functions."""

from ingestion.ingest_history_parser import (
    classify_row,
    normalize_isrc,
    parse_ms_played,
    parse_timestamp_to_utc,
)


def test_normalize_isrc_accepts_valid_and_uppercases() -> None:
    assert normalize_isrc("usrc17607839") == "USRC17607839"


def test_normalize_isrc_rejects_invalid_pattern() -> None:
    assert normalize_isrc("not-an-isrc") == ""


def test_parse_timestamp_to_utc_accepts_iso_z() -> None:
    value, ok = parse_timestamp_to_utc("2024-01-01T10:00:00Z")
    assert ok is True
    assert value == "2024-01-01T10:00:00Z"


def test_parse_timestamp_to_utc_rejects_invalid_value() -> None:
    value, ok = parse_timestamp_to_utc("bad timestamp")
    assert ok is False
    assert value == ""


def test_parse_ms_played_accepts_non_negative_int() -> None:
    value, ok = parse_ms_played("1234")
    assert ok is True
    assert value == 1234


def test_parse_ms_played_rejects_negative() -> None:
    value, ok = parse_ms_played("-1")
    assert ok is False
    assert value is None


def test_classify_row_ok() -> None:
    quality, played_at, ms_played = classify_row(
        track_name="track",
        artist_name="artist",
        played_at_raw="2024-01-01T00:00:00Z",
        ms_played_raw="2000",
        isrc="USRC17607839",
    )
    assert quality == "ok"
    assert played_at == "2024-01-01T00:00:00Z"
    assert ms_played == 2000


def test_classify_row_missing_isrc() -> None:
    quality, _, _ = classify_row(
        track_name="track",
        artist_name="artist",
        played_at_raw="2024-01-01T00:00:00Z",
        ms_played_raw="2000",
        isrc="",
    )
    assert quality == "missing_isrc"


def test_classify_row_missing_core_field() -> None:
    quality, _, _ = classify_row(
        track_name="",
        artist_name="artist",
        played_at_raw="2024-01-01T00:00:00Z",
        ms_played_raw="2000",
        isrc="USRC17607839",
    )
    assert quality == "missing_core_field"
