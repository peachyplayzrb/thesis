"""Data-loading helpers for BL-008 transparency."""

from __future__ import annotations

from pathlib import Path

from shared_utils.io_utils import read_csv_index as shared_read_csv_index


def read_csv_index(path: Path, key_field: str) -> dict[str, dict[str, str]]:
    """Compatibility wrapper around shared CSV indexing helper."""
    return shared_read_csv_index(path, key_field)
