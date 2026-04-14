"""Parse raw BL-005 candidate rows into the typed attributes BL-006 scoring uses."""

from shared_utils.parsing import parse_csv_labels, parse_float


def parse_candidate_attributes(row: dict[str, str]) -> dict[str, object]:
    """Extract numeric and semantic candidate attributes from one CSV row."""
    # Some historical exports use `id` instead of `track_id`, so I support both.
    track_id = (row.get("track_id") or row.get("id") or "").strip()

    # Parse numeric fields defensively so malformed values stay `None` instead of crashing scoring.
    danceability = parse_float(row.get("danceability", ""))
    energy = parse_float(row.get("energy", ""))
    valence = parse_float(row.get("valence", ""))
    tempo = parse_float(row.get("tempo", ""))
    duration_ms = parse_float(row.get("duration_ms", ""))
    popularity = parse_float(row.get("popularity", ""))
    key = parse_float(row.get("key", ""))
    mode = parse_float(row.get("mode", ""))

    # Semantic labels are stored as CSV-like lists in the source columns.
    genres = parse_csv_labels(row.get("genres", ""))
    tags = parse_csv_labels(row.get("tags", ""))

    # Keep lead-genre fallback aligned with earlier stages: genres first, tags second.
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
