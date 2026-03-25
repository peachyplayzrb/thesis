"""
Candidate data parsing and normalization for BL-005.

Handles transformation of raw candidate CSV rows into normalized, structured data
suitable for semantic and numeric scoring.
"""

import json
from typing import Any

from sys import path as sys_path
from pathlib import Path

# Add shared utilities to path
sys_path.insert(0, str(Path(__file__).resolve().parents[3] / "07_implementation" / "implementation_notes"))

from bl000_shared_utils.io_utils import parse_float


def normalize_candidate_row(row: dict[str, str]) -> dict[str, str]:
    """
    Normalize a candidate row by standardizing common field variations.
    
    Handles:
    - track_id vs id column variants (tries track_id first, falls back to id)
    
    Args:
        row: Raw candidate row from CSV
    
    Returns:
        Normalized row dict with standardized fields
    """
    normalized = dict(row)
    track_id = (normalized.get("track_id") or "").strip()
    if not track_id:
        track_id = (normalized.get("id") or "").strip()
    normalized["track_id"] = track_id
    return normalized


def candidate_numeric_value(
    row: dict[str, str],
    profile_column: str,
    candidate_column: str,
) -> float | None:
    """
    Extract a numeric value from candidate row with unit conversions.
    
    Handles special conversions:
    - duration (seconds) → duration_ms (milliseconds)
    
    Args:
        row: Candidate row
        profile_column: Column name from profile (e.g., "duration_ms")
        candidate_column: Column name in candidate dataset (e.g., "duration")
    
    Returns:
        Parsed float value or None if missing/invalid
    """
    value = parse_float(row.get(candidate_column, ""))
    if value is None:
        return None
    
    # Apply unit conversions where candidate differs from profile
    if profile_column == "duration_ms" and candidate_column == "duration":
        return value * 1000.0  # Convert seconds to milliseconds
    
    return value


def resolve_candidate_column(
    profile_column: str,
    preferred_column: str,
    candidate_columns: set[str],
) -> str | None:
    """
    Map a profile column to the corresponding candidate dataset column.
    
    Logic:
    1. Try exact match (preferred_column)
    2. Try fallback (e.g., "duration" if looking for "duration_ms")
    3. Return None if no match found
    
    Args:
        profile_column: Column name from profile (e.g., "duration_ms")
        preferred_column: Preferred candidate column name (e.g., "duration_ms")
        candidate_columns: Set of available columns in candidate dataset
    
    Returns:
        Candidate column name or None if unresolved
    """
    # Try direct match first
    if preferred_column in candidate_columns:
        return preferred_column
    
    # Try special fallbacks
    if profile_column == "duration_ms" and "duration" in candidate_columns:
        return "duration"
    
    return None


def parse_list(raw_value: str, label_key: str) -> list[str]:
    """
    Parse a JSON-encoded list from a CSV cell, extracting a specific key.
    
    Expected format:
        [{"label": "Rock", ...}, {"label": "Alternative", ...}, ...]
    
    Args:
        raw_value: Raw string value from CSV cell (should be JSON array)
        label_key: Key to extract from each item (e.g., "label")
    
    Returns:
        List of extracted label values, or empty list if parsing fails
    """
    if not raw_value:
        return []
    
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    
    result: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        label = item.get(label_key)
        if isinstance(label, str) and label.strip():
            result.append(label.strip())
    
    return result


def resolve_lead_genre(candidate_genres: list[str], candidate_tags: list[str]) -> str:
    """
    Determine primary genre for a candidate track.
    
    Selection priority:
    1. First genre (if genres list is non-empty)
    2. First tag (if genres list empty but tags present)
    3. Empty string (fallback if both empty)
    
    Args:
        candidate_genres: List of genres for candidate
        candidate_tags: List of tags for candidate
    
    Returns:
        Primary genre string, or empty string if none available
    """
    if candidate_genres:
        return candidate_genres[0]
    if candidate_tags:
        return candidate_tags[0]
    return ""
