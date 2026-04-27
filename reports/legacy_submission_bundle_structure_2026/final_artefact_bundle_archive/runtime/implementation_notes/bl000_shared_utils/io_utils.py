"""
Consolidated file I/O utilities for all implementation stages.

Provides functions for:
- SHA256 hashing (both chunked and direct)
- JSON/JSONL loading and writing
- CSV loading and parsing
- Float parsing with error handling
"""

import csv
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from bl000_shared_utils.hashing import sha256_of_file as shared_sha256_of_file
from bl000_shared_utils.parsing import parse_csv_labels as shared_parse_csv_labels
from bl000_shared_utils.parsing import parse_float as shared_parse_float


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
    return shared_sha256_of_file(path, uppercase=False)


def sha256_direct(path: Path) -> str:
    """
    Compute SHA256 hash of a file directly in memory.
    
    Returns the hexdigest in uppercase.
    
    Args:
        path: Path to the file to hash
        
    Returns:
        SHA256 hexdigest as uppercase string
    """
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest().upper()


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


def parse_float(value: str) -> float | None:
    """
    Parse a string as float, returning None if parsing fails.
    
    Handles empty strings and invalid numeric strings gracefully.
    
    Args:
        value: String to parse
        
    Returns:
        Parsed float or None if parsing fails
    """
    return shared_parse_float(value)


def parse_csv_labels(raw_value: str) -> list[str]:
    """
    Parse a comma-separated string into a list of normalized labels.
    
    - Splits on commas
    - Strips whitespace
    - Lowercases each label
    - Removes empty strings and duplicates
    
    Args:
        raw_value: Comma-separated string of labels
        
    Returns:
        List of normalized, unique labels
    """
    return shared_parse_csv_labels(raw_value)
