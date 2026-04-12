"""Shared I/O utilities consolidated from all stages."""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load and parse a JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    """Load CSV file as list of dictionaries."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_csv_index(path: Path, key_field: str) -> dict[str, dict[str, str]]:
    """Load CSV file as dict indexed by key_field."""
    index: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row.get(key_field) or "").strip()
            if key:
                index[key] = row
    return index


def open_text_write(path: Path, *, newline: str | None = None):
    """Open a UTF-8 text file for writing, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open("w", encoding="utf-8", newline=newline)


def write_json(path: Path, obj: dict[str, Any] | list[Any], *, indent: int = 2, ensure_ascii: bool = False) -> None:
    """Save an object as formatted JSON."""
    with open_text_write(path) as handle:
        json.dump(obj, handle, indent=indent, ensure_ascii=ensure_ascii)


def sha256_of_file(path: Path, *, uppercase: bool = True) -> str:
    """Compute SHA-256 hash of file contents."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    result = digest.hexdigest()
    return result.upper() if uppercase else result


def utc_now() -> str:
    """Get current UTC time in ISO-8601 format (Z-suffix)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
