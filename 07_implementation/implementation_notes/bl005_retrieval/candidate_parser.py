"""
Candidate data parsing and normalization for BL-005.

Handles transformation of raw candidate CSV rows into normalized, structured data
suitable for semantic and numeric scoring.
"""

from sys import path as sys_path
from pathlib import Path

# Add shared utilities to path
sys_path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.parsing import normalize_candidate_row
from bl000_shared_utils.parsing import parse_float


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
