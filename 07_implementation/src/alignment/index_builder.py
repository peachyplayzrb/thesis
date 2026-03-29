"""DS-001 candidate index construction for BL-003 matching."""
from __future__ import annotations

from collections import defaultdict

from alignment.text_matching import normalize_text


def build_ds001_indices(
    rows: list[dict[str, str]],
) -> tuple[
    dict[str, dict[str, str]],
    dict[tuple[str, str], list[dict[str, str]]],
    dict[str, list[dict[str, str]]],
]:
    """Build Spotify-ID, (title, artist), and artist-only indices over DS-001 candidates."""
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
        candidate_rows.sort(key=lambda r: (r.get("id") or ""))

    for candidate_rows in by_artist.values():
        candidate_rows.sort(key=lambda r: (r.get("id") or ""))

    return by_spotify_id, by_title_artist, by_artist
