"""
File and serialization helpers used across the implementation.

I kept the common JSON, CSV, hashing, and text-writing helpers here so the
stage files could stay focused on pipeline logic instead of boilerplate.
"""

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared_utils.hashing import sha256_of_file as shared_sha256_of_file
from shared_utils.hashing import sha256_of_text as _sha256_of_text
from shared_utils.hashing import canonical_json_hash as _canonical_json_hash
from shared_utils.parsing import parse_csv_labels
from shared_utils.parsing import parse_float


def utc_now() -> str:
    """Return the current UTC time as an ISO 8601 string (YYYY-MM-DDTHH:MM:SSZ)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
    """Hash a file as uppercase SHA256 without loading the whole file into memory."""
    return shared_sha256_of_file(path, uppercase=True)


def sha256_of_text(text: str) -> str:
    """Compute SHA256 hash of UTF-8 text, returned as an uppercase hex string."""
    return _sha256_of_text(text, uppercase=True)


def canonical_json_hash(payload: Any) -> str:
    """Compute a deterministic SHA256 hash of a JSON-serializable payload, uppercase."""
    return _canonical_json_hash(payload, uppercase=True)


def load_json(path: Path) -> dict:
    """Load a JSON file and return the decoded payload."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file, skipping blank lines and decoding one object per line."""
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            rows.append(json.loads(text))
    return rows


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    """Load a CSV file into a list of row dictionaries."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_csv_index(path: Path, key_field: str) -> dict[str, dict[str, str]]:
    """Load CSV rows into a key-based index, skipping rows with blank keys."""
    index: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row.get(key_field) or "").strip()
            if key:
                index[key] = row
    return index


def write_json(path: Path, obj: dict | list) -> None:
    """Write a dict or list as nicely formatted UTF-8 JSON."""
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


# These are re-exported from shared_utils.parsing so older import sites still work.
