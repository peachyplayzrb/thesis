"""Detect and normalize user-supplied CSV schemas for BL-003.

The point of this file is to let user CSVs come in with slightly different
headers while still mapping them onto the internal fields the alignment stage expects.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any


# Accepted header aliases for each internal BL-003 field.
# Matching is case-insensitive and ignores leading/trailing whitespace.
_ALIAS_MAP: dict[str, list[str]] = {
    "track_id":     ["track_id", "spotify_id", "spotify_track_id", "id"],
    "track_name":   ["track_name", "title", "song", "name", "track_title"],
    "artist_names": ["artist_names", "artist", "artists", "artist_name", "performer"],
    "album_name":   ["album_name", "album", "album_title", "record"],
    "duration_ms":  ["duration_ms", "duration", "length_ms", "duration_millis"],
    "added_at":     ["added_at", "date", "timestamp", "listened_at", "played_at", "datetime"],
}

# Minimum viable matching needs either a track id or a track-name + artist pair.
_MATCH_REQUIRED_EITHER: str = "track_id"
_MATCH_REQUIRED_BOTH: tuple[str, str] = ("track_name", "artist_names")


def _build_column_map(headers: list[str]) -> dict[str, str | None]:
    """Build the mapping from internal field names to whichever CSV headers matched them."""
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
    """
    Detect the user CSV schema, normalize the rows, and return a schema report.

    The report records which headers were recognized and whether the file has
    enough matchable fields to be useful for BL-003.
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

    # Keep track of which original headers were not recognized by any alias group.
    all_matched_originals = {h for h in column_map.values() if h is not None}
    unmapped = [h for h in original_headers if h not in all_matched_originals]

    # BL-003 can only use the file if there is enough information to match rows back to DS-001.
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

    # Normalize the rows so the rest of BL-003 can treat them like one stable schema.
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
