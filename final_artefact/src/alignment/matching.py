"""
BL-003 DS-001 matching helpers.

Provides DS-001 index construction, text normalisation, duration-based
tie-breaking, and the main per-event matching loop.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from shared_utils.parsing import normalize_ascii_text, parse_int
from alignment.weighting import compute_weight


def normalize_text(value: str) -> str:
    """Normalise a string to ASCII lower-case tokens for fuzzy key comparison."""
    return normalize_ascii_text(value)


def first_artist(artist_names: str) -> str:
    """Return the primary artist from a pipe-, semicolon-, or comma-separated string."""
    if "|" in artist_names:
        return artist_names.split("|", 1)[0].strip()
    if ";" in artist_names:
        return artist_names.split(";", 1)[0].strip()
    if "," in artist_names:
        return artist_names.split(",", 1)[0].strip()
    return artist_names.strip()


def build_ds001_indices(
    rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, str]], dict[tuple[str, str], list[dict[str, str]]]]:
    """Build Spotify-ID and (title, artist) lookup indices over the DS-001 candidate set."""
    by_spotify_id: dict[str, dict[str, str]] = {}
    by_title_artist: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)

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

    for candidate_rows in by_title_artist.values():
        candidate_rows.sort(key=lambda r: (r.get("id") or ""))

    return by_spotify_id, by_title_artist


def choose_best_duration_match(
    candidates: list[dict[str, str]],
    target_duration_ms: int | None,
) -> tuple[dict[str, str], int | None]:
    """Select the candidate whose duration is closest to the target, falling back to first."""
    if not candidates:
        raise ValueError("candidates must not be empty")

    if target_duration_ms is None:
        return candidates[0], None

    best_row = candidates[0]
    best_delta: int | None = None

    for row in candidates:
        candidate_duration = parse_int(row.get("duration_ms", ""))
        if candidate_duration is None:
            continue
        delta = abs(candidate_duration - target_duration_ms)
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_row = row

    if best_delta is None:
        return candidates[0], None
    return best_row, best_delta


def match_events(
    events: list[dict[str, str]],
    by_spotify_id: dict[str, dict[str, str]],
    by_title_artist: dict[tuple[str, str], list[dict[str, str]]],
    top_range_weights: dict,
    source_base_weights: dict,
    decay_half_lives: dict[str, float] | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], list[dict[str, str]], dict[str, int]]:
    """
    Match every event against DS-001 using Spotify-ID first, metadata fallback second.

    Returns (trace_rows, matched_events, unmatched_rows, match_counts).
    match_counts contains the per-method tallies but NOT input_event_rows.
    """
    trace_rows: list[dict[str, str]] = []
    matched_events: list[dict[str, Any]] = []
    unmatched_rows: list[dict[str, str]] = []
    match_counts: dict[str, int] = {
        "matched_by_spotify_id": 0,
        "matched_by_metadata": 0,
        "unmatched": 0,
        "unmatched_missing_keys": 0,
        "unmatched_no_candidate": 0,
    }

    for event in events:
        spotify_track_id = event["spotify_track_id"]
        track_name = event["track_name"]
        artist_names = event["artist_names"]
        artist_primary = first_artist(artist_names)
        event_duration = parse_int(event["duration_ms"])
        weight = compute_weight(
            event,
            top_range_weights,
            source_base_weights,
            decay_half_lives=decay_half_lives,
        )

        trace = dict(event)
        trace["match_status"] = ""
        trace["match_method"] = ""
        trace["matched_ds001_id"] = ""
        trace["matched_song"] = ""
        trace["matched_artist"] = ""
        trace["duration_delta_ms"] = ""
        trace["reason"] = ""
        trace["preference_weight"] = f"{weight:.6f}"

        matched_row: dict[str, str] | None = None
        duration_delta: int | None = None
        match_method = ""

        if spotify_track_id and spotify_track_id in by_spotify_id:
            matched_row = by_spotify_id[spotify_track_id]
            match_method = "spotify_id_exact"
            match_counts["matched_by_spotify_id"] += 1
        else:
            title_key = normalize_text(track_name)
            artist_key = normalize_text(artist_primary)
            if title_key and artist_key:
                candidates = by_title_artist.get((title_key, artist_key), [])
                if candidates:
                    matched_row, duration_delta = choose_best_duration_match(candidates, event_duration)
                    match_method = "metadata_fallback"
                    match_counts["matched_by_metadata"] += 1

        if matched_row is None:
            match_counts["unmatched"] += 1
            trace["match_status"] = "unmatched"
            if not spotify_track_id and not (track_name and artist_primary):
                match_counts["unmatched_missing_keys"] += 1
                trace["reason"] = "missing_track_id_and_metadata"
            else:
                match_counts["unmatched_no_candidate"] += 1
                trace["reason"] = "no_ds001_candidate"
            unmatched_rows.append(trace)
            trace_rows.append(trace)
            continue

        trace["match_status"] = "matched"
        trace["match_method"] = match_method
        trace["matched_ds001_id"] = matched_row.get("id", "")
        trace["matched_song"] = matched_row.get("song", "")
        trace["matched_artist"] = matched_row.get("artist", "")
        trace["duration_delta_ms"] = "" if duration_delta is None else str(duration_delta)

        matched_event: dict[str, Any] = {
            "event_id": f"ds001_align_{len(matched_events) + 1:06d}",
            "source_type": event["source_type"],
            "source_row_index": int(event["source_row_index"]),
            "source_timestamp": event["event_time"],
            "spotify_track_id": spotify_track_id,
            "spotify_isrc": event["isrc"],
            "spotify_track_name": track_name,
            "spotify_artist_names": artist_names,
            "match_method": match_method,
            "duration_delta_ms": duration_delta,
            "ds001_id": matched_row.get("id", ""),
            "ds001_spotify_id": matched_row.get("spotify_id", ""),
            "artist": matched_row.get("artist", ""),
            "song": matched_row.get("song", ""),
            "release": matched_row.get("release", ""),
            "duration_ms": matched_row.get("duration_ms", ""),
            "popularity": matched_row.get("popularity", ""),
            "danceability": matched_row.get("danceability", ""),
            "energy": matched_row.get("energy", ""),
            "key": matched_row.get("key", ""),
            "mode": matched_row.get("mode", ""),
            "valence": matched_row.get("valence", ""),
            "tempo": matched_row.get("tempo", ""),
            "genres": matched_row.get("genres", ""),
            "tags": matched_row.get("tags", ""),
            "lang": matched_row.get("lang", ""),
            "preference_weight": weight,
            "interaction_count": max(1, int(round(weight * 10))),
            "interaction_type": "history",
        }
        matched_events.append(matched_event)
        trace_rows.append(trace)

    return trace_rows, matched_events, unmatched_rows, match_counts
