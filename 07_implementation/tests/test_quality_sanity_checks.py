"""Tier-A unit tests for quality.sanity_checks helper functions."""

import csv
from pathlib import Path

import pytest

from quality.sanity_checks import (
    bl005_filtered_has_required_columns,
    csv_header,
    csv_row_count,
    ensure_exists,
    sha256_file,
)


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


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
