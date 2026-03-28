"""
Candidate data parsing and attribute extraction for BL-006 scoring.

Parses raw candidate rows and extracts attributes needed for scoring.
"""

import sys
from pathlib import Path

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_utils.io_utils import parse_csv_labels, parse_float


def parse_candidate_attributes(row: dict[str, str]) -> dict[str, object]:
    """
    Parse and extract all relevant attributes from a candidate CSV row.

    Args:
        row: Raw candidate row (all values are strings from CSV)

    Returns:
        Dict with parsed/extracted attributes:
        - "track_id": str
        - "danceability": float | None
        - "energy": float | None
        - "valence": float | None
        - "tempo": float | None
        - "duration_ms": float | None
        - "key": float | None (0-11, musical semitones)
        - "mode": float | None (0=minor, 1=major)
        - "genres": list[str]
        - "tags": list[str]
        - "lead_genre": str
    """
    # Track ID (handle both "track_id" and "id" variants)
    track_id = (row.get("track_id") or row.get("id") or "").strip()

    # Numeric attributes (with None-safe parsing)
    danceability = parse_float(row.get("danceability", ""))
    energy = parse_float(row.get("energy", ""))
    valence = parse_float(row.get("valence", ""))
    tempo = parse_float(row.get("tempo", ""))
    duration_ms = parse_float(row.get("duration_ms", ""))
    key = parse_float(row.get("key", ""))
    mode = parse_float(row.get("mode", ""))

    # Categorical attributes (CSV-encoded lists)
    genres = parse_csv_labels(row.get("genres", ""))
    tags = parse_csv_labels(row.get("tags", ""))

    # Derive lead genre (first priority: first genre, second: first tag)
    lead_genre = genres[0] if genres else (tags[0] if tags else "")

    return {
        "track_id": track_id,
        "danceability": danceability,
        "energy": energy,
        "valence": valence,
        "tempo": tempo,
        "duration_ms": duration_ms,
        "key": key,
        "mode": mode,
        "genres": genres,
        "tags": tags,
        "lead_genre": lead_genre,
    }


def normalize_candidate_numeric(
    value: float | None,
    profile_column: str,
    candidate_column: str,
) -> float | None:
    """
    Normalize candidate numeric value to match profile scale.

    Handles unit conversions:
    - duration (seconds) → duration_ms (milliseconds)

    Args:
        value: Parsed numeric value from candidate
        profile_column: Profile column name (e.g., "duration_ms")
        candidate_column: Candidate column name (e.g., "duration")

    Returns:
        Normalized value or None if input was None
    """
    if value is None:
        return None

    # Apply unit conversions
    if profile_column == "duration_ms" and candidate_column == "duration":
        return value * 1000.0  # Convert seconds to milliseconds

    return value


def resolve_numeric_column(
    profile_column: str,
    candidate_columns: set[str],
) -> str | None:
    """
    Map a profile numeric column to the candidate dataset column.

    Handles common naming variations:
    - profile "duration_ms" ← candidate "duration" (+ conversion)

    Args:
        profile_column: Numeric column name from profile
        candidate_columns: Set of available columns in candidate dataset

    Returns:
        Candidate column name or None if cannot be resolved
    """
    # Try direct match first
    if profile_column in candidate_columns:
        return profile_column

    # Try fallbacks for common variations
    if profile_column == "duration_ms" and "duration" in candidate_columns:
        return "duration"

    return None
