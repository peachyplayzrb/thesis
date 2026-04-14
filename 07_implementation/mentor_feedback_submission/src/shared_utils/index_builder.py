"""Build the lookup tables BL-003 uses while matching events to DS-001 tracks."""
from __future__ import annotations

from collections import defaultdict

from shared_utils.text_matching import normalize_text


def resolve_ds001_id(row: dict[str, str]) -> str:
    """Pick the DS-001 identifier field that is present in this row schema."""
    return ((row.get("id") or row.get("ds001_id") or row.get("cid") or "").strip())


def build_ds001_indices(
    rows: list[dict[str, str]],
) -> tuple[
    dict[str, dict[str, str]],
    dict[tuple[str, str], list[dict[str, str]]],
    dict[str, list[dict[str, str]]],
]:
    """Build the main in-memory indices BL-003 uses for exact and fallback matching."""
    by_spotify_id: dict[str, dict[str, str]] = {}
    by_title_artist: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    by_artist: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        spotify_id = (row.get("spotify_id") or "").strip()
        song = (row.get("song") or "").strip()
        artist = (row.get("artist") or "").strip()

        if spotify_id:
            by_spotify_id[spotify_id] = row

        title_key = normalize_text(song)
        artist_key = normalize_text(artist)
        if title_key and artist_key:
            by_title_artist[(title_key, artist_key)].append(row)
            by_artist[artist_key].append(row)

    for candidate_rows in by_title_artist.values():
        candidate_rows.sort(key=resolve_ds001_id)

    for candidate_rows in by_artist.values():
        candidate_rows.sort(key=resolve_ds001_id)

    return by_spotify_id, by_title_artist, by_artist
