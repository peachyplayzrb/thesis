"""Dynamic schema detection and normalization for user-supplied CSV ingestion.

At load time this module inspects the actual column headers of a user CSV,
maps them to the internal BL-003 field names via a configurable alias table,
warns if the minimum match columns are absent, and returns rows renamed to
standard internal keys so all downstream code sees a consistent schema.

Match key rationale (what DS-001 actually indexes):
  - track_id    → spotify_id exact match (strongest)
  - track_name  → song + artist metadata fallback
  - artist_names→ artist fuzzy candidate pool
  - album_name  → album fuzzy scoring boost (optional, no DS-001 index needed)
  - duration_ms → tiebreak only
  - added_at    → temporal decay only
  isrc is intentionally excluded: DS-001 has no isrc column and no isrc index.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Alias table — maps each internal field name to accepted CSV header variants.
# Lookup is case-insensitive with leading/trailing whitespace stripped.
# ---------------------------------------------------------------------------
_ALIAS_MAP: dict[str, list[str]] = {
    "track_id":     ["track_id", "spotify_id", "spotify_track_id", "id"],
    "track_name":   ["track_name", "title", "song", "name", "track_title"],
    "artist_names": ["artist_names", "artist", "artists", "artist_name", "performer"],
    "album_name":   ["album_name", "album", "album_title", "record"],
    "duration_ms":  ["duration_ms", "duration", "length_ms", "duration_millis"],
    "added_at":     ["added_at", "date", "timestamp", "listened_at", "played_at", "datetime"],
}

# Minimum viable match: need track_id OR (track_name AND artist_names)
_MATCH_REQUIRED_EITHER: str = "track_id"
_MATCH_REQUIRED_BOTH: tuple[str, str] = ("track_name", "artist_names")


def _build_column_map(headers: list[str]) -> dict[str, str | None]:
    """Return {internal_field: matched_header | None} for every alias group."""
    normalised_headers = {h.strip().lower(): h for h in headers}
    mapping: dict[str, str | None] = {}
    for internal_field, aliases in _ALIAS_MAP.items():
        matched: str | None = None
        for alias in aliases:
            if alias in normalised_headers:
                matched = normalised_headers[alias]
                break
        mapping[internal_field] = matched
    return mapping


def normalize_user_csv_rows(
    rows: list[dict[str, str]],
    path: Path | str | None = None,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Detect schema, normalise rows to internal field names, and return a schema report.

    Parameters
    ----------
    rows:
        Raw rows from csv.DictReader (or equivalent).  May be empty.
    path:
        Optional file path used only in warning messages.

    Returns
    -------
    (normalized_rows, schema_report) where schema_report contains:
      original_headers: list[str]
      column_map: dict[str, str | None]
      mapped: list[str]           internal fields that were successfully mapped
      unmapped: list[str]         CSV headers that did not match any alias
      viable: bool                True when minimum match columns are present
    """
    path_label = str(path) if path else "<user_csv>"

    if not rows:
        schema_report: dict[str, Any] = {
            "original_headers": [],
            "column_map": {f: None for f in _ALIAS_MAP},
            "mapped": [],
            "unmapped": [],
            "viable": False,
        }
        warnings.warn(
            f"BL-003 user_csv: no rows loaded from {path_label}; skipping schema detection.",
            UserWarning,
            stacklevel=2,
        )
        return [], schema_report

    original_headers = list(rows[0].keys())
    column_map = _build_column_map(original_headers)

    mapped = [f for f, h in column_map.items() if h is not None]

    # Determine which original headers were not matched by any alias group
    all_matched_originals = {h for h in column_map.values() if h is not None}
    unmapped = [h for h in original_headers if h not in all_matched_originals]

    # Viability check
    has_id = column_map["track_id"] is not None
    has_title_artist = (
        column_map["track_name"] is not None and column_map["artist_names"] is not None
    )
    viable = has_id or has_title_artist
    if not viable:
        warnings.warn(
            f"BL-003 user_csv: {path_label} has no usable match columns "
            "(needs track_id or both track_name+artist_names). "
            "All rows will be unmatched; source is advisory and pipeline continues.",
            UserWarning,
            stacklevel=2,
        )

    # Normalise rows: rename matched headers to internal keys; missing fields → ""
    normalized_rows: list[dict[str, str]] = []
    for raw in rows:
        norm: dict[str, str] = {}
        for internal_field, original_header in column_map.items():
            if original_header is not None:
                norm[internal_field] = (raw.get(original_header) or "").strip()
            else:
                norm[internal_field] = ""
        normalized_rows.append(norm)

    schema_report = {
        "original_headers": original_headers,
        "column_map": column_map,
        "mapped": mapped,
        "unmapped": unmapped,
        "viable": viable,
    }
    return normalized_rows, schema_report
