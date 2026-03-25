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
from pathlib import Path
from typing import Any


def sha256_of_file(path: Path) -> str:
    """
    Compute SHA256 hash of a file by reading it in chunks.
    
    This is memory-efficient for large files.
    
    Args:
        path: Path to the file to hash
        
    Returns:
        SHA256 hexdigest as uppercase string
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


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
    if not raw_value:
        return []
    labels: list[str] = []
    seen: set[str] = set()
    for piece in raw_value.split(","):
        label = piece.strip().lower()
        if not label or label in seen:
            continue
        seen.add(label)
        labels.append(label)
    return labels
