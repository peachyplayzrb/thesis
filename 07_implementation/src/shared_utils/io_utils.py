"""
Consolidated file I/O utilities for all implementation stages.

Provides functions for:
- SHA256 hashing (both chunked and direct)
- JSON/JSONL loading and writing
- CSV loading and parsing
- Float parsing with error handling
"""

import csv
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from shared_utils.hashing import canonical_json_hash as _canonical_json_hash
from shared_utils.hashing import sha256_of_file as shared_sha256_of_file
from shared_utils.hashing import sha256_of_text as _sha256_of_text
from shared_utils.parsing import parse_csv_labels as parse_csv_labels
from shared_utils.parsing import parse_float as parse_float


def utc_now() -> str:
    """Return the current UTC time as an ISO 8601 string (YYYY-MM-DDTHH:MM:SSZ)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_utc_iso(dt: datetime) -> str:
    """Format an existing datetime object as an ISO 8601 UTC string (YYYY-MM-DDTHH:MM:SSZ)."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def open_text_write(path: Path, *, newline: str | None = None):
    """Open a text file for writing with a small Windows retry/fallback guard."""
    path.parent.mkdir(parents=True, exist_ok=True)
    last_error: OSError | None = None
    for _ in range(3):
        try:
            return path.open("w", encoding="utf-8", newline=newline)
        except OSError as exc:
            last_error = exc
            if os.name != "nt" or exc.errno != 22:
                raise
            time.sleep(0.05)

    if last_error is not None and os.name == "nt" and last_error.errno == 22:
        normalized = os.path.abspath(os.path.normpath(str(path))).replace("/", "\\")
        try:
            return open(normalized, "w", encoding="utf-8", newline=newline)
        except OSError as fallback_error:
            if fallback_error.errno != 22:
                raise
            extended_path = normalized if normalized.startswith("\\\\?\\") else f"\\\\?\\{normalized}"
            return open(extended_path, "w", encoding="utf-8", newline=newline)
    raise last_error if last_error is not None else RuntimeError("Unexpected file open failure")


def sha256_of_file(path: Path) -> str:
    """
    Compute SHA256 hash of a file by reading it in chunks.

    This is memory-efficient for large files.

    Args:
        path: Path to the file to hash

    Returns:
        SHA256 hexdigest as uppercase string
    """
    return shared_sha256_of_file(path, uppercase=True)


def sha256_of_text(text: str) -> str:
    """Compute SHA256 hash of UTF-8 text, returned as an uppercase hex string."""
    return _sha256_of_text(text, uppercase=True)


def canonical_json_hash(payload: Any) -> str:
    """Compute a deterministic SHA256 hash of a JSON-serializable payload, uppercase."""
    return _canonical_json_hash(payload, uppercase=True)


def load_json(path: Path) -> dict:
    """
    Load a JSON file.

    Args:
        path: Path to the JSON file

    Returns:
        Parsed JSON as dict

    Raises:
        json.JSONDecodeError: If file is not valid JSON
        FileNotFoundError: If file does not exist
    """
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """
    Load a JSONL (JSON Lines) file.

    Each line is parsed as a separate JSON object.

    Args:
        path: Path to the JSONL file

    Returns:
        List of dicts, one per line

    Raises:
        json.JSONDecodeError: If a line is not valid JSON
        FileNotFoundError: If file does not exist
    """
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            rows.append(json.loads(text))
    return rows


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    """
    Load a CSV file as list of dicts.

    Uses csv.DictReader to map column headers to values.

    Args:
        path: Path to the CSV file

    Returns:
        List of dicts, one per CSV row

    Raises:
        FileNotFoundError: If file does not exist
    """
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_csv_index(path: Path, key_field: str) -> dict[str, dict[str, str]]:
    """
    Load CSV rows indexed by a key field.

    Rows with missing or empty key_field values are skipped.
    If a key appears multiple times, the last row wins.
    """
    index: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row.get(key_field) or "").strip()
            if key:
                index[key] = row
    return index


def write_json(path: Path, obj: dict | list) -> None:
    """
    Write a dict or list to a JSON file with pretty indentation.

    Args:
        path: Path where JSON should be written
        obj: Dict or list to write

    Raises:
        IOError: If file cannot be written
    """
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
