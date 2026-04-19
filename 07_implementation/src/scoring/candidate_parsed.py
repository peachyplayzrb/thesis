"""
Candidate data parsing and attribute extraction for BL-006 scoring.

Parses raw candidate rows and extracts attributes needed for scoring.
"""

from shared_utils.parsing import parse_csv_labels, parse_float


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
    popularity = parse_float(row.get("popularity", ""))
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
        "popularity": popularity,
        "key": key,
        "mode": mode,
        "genres": genres,
        "tags": tags,
        "lead_genre": lead_genre,
    }
