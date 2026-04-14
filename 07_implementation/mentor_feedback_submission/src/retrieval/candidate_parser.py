"""Helpers for reading raw candidate rows into the shapes BL-005 expects."""

from pathlib import Path

from shared_utils.parsing import normalize_candidate_row
from shared_utils.parsing import parse_float


def candidate_numeric_value(
    row: dict[str, str],
    profile_column: str,
    candidate_column: str,
) -> float | None:
    """Read one numeric candidate value, including the duration seconds-to-ms conversion when needed."""
    value = parse_float(row.get(candidate_column, ""))
    if value is None:
        return None

    # DS-001 stores duration in seconds, while the profile logic works in milliseconds.
    if profile_column == "duration_ms" and candidate_column == "duration":
        return value * 1000.0  # Convert seconds to milliseconds

    return value


def resolve_candidate_column(
    profile_column: str,
    preferred_column: str,
    candidate_columns: set[str],
) -> str | None:
    """Map one profile field to the candidate column that can actually supply it."""
    if preferred_column in candidate_columns:
        return preferred_column

    if profile_column == "duration_ms" and "duration" in candidate_columns:
        return "duration"

    return None


def resolve_lead_genre(candidate_genres: list[str], candidate_tags: list[str]) -> str:
    """Pick the candidate's primary genre label, falling back from genres to tags."""
    if candidate_genres:
        return candidate_genres[0]
    if candidate_tags:
        return candidate_tags[0]
    return ""


def candidate_language_code(row: dict[str, str]) -> str | None:
    """Extract normalized ISO-like language code from candidate row."""
    raw = str(row.get("lang", "")).strip().lower()
    if not raw:
        return None
    if len(raw) > 8:
        return None
    return raw


def candidate_release_year(row: dict[str, str]) -> int | None:
    """Extract candidate release year with conservative bounds."""
    raw = str(row.get("release", "")).strip()
    if not raw:
        return None
    try:
        year = int(float(raw))
    except ValueError:
        return None
    if year < 1900 or year > 2100:
        return None
    return year
