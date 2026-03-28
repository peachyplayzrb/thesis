"""Tests for shared_utils.io_utils.read_csv_index."""

import csv
from pathlib import Path

from shared_utils.io_utils import read_csv_index
from transparency.data_layer import read_csv_index as transparency_read_csv_index


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_read_csv_index_skips_blank_keys_and_indexes_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "rows.csv"
    _write_csv(
        csv_path,
        ["track_id", "value"],
        [
            {"track_id": "", "value": "skip"},
            {"track_id": "a", "value": "1"},
            {"track_id": "b", "value": "2"},
        ],
    )

    index = read_csv_index(csv_path, "track_id")

    assert set(index.keys()) == {"a", "b"}
    assert index["a"]["value"] == "1"
    assert index["b"]["value"] == "2"


def test_read_csv_index_last_row_wins_on_duplicate_key(tmp_path: Path) -> None:
    csv_path = tmp_path / "dupes.csv"
    _write_csv(
        csv_path,
        ["track_id", "value"],
        [
            {"track_id": "x", "value": "first"},
            {"track_id": "x", "value": "second"},
        ],
    )

    index = read_csv_index(csv_path, "track_id")

    assert index["x"]["value"] == "second"


def test_transparency_data_layer_wrapper_preserves_behavior(tmp_path: Path) -> None:
    csv_path = tmp_path / "wrapper.csv"
    _write_csv(
        csv_path,
        ["track_id", "value"],
        [
            {"track_id": "t1", "value": "ok"},
            {"track_id": "", "value": "skip"},
        ],
    )

    shared_index = read_csv_index(csv_path, "track_id")
    wrapped_index = transparency_read_csv_index(csv_path, "track_id")

    assert wrapped_index == shared_index
