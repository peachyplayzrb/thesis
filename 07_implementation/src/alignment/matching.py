"""
BL-003 DS-001 matching helpers.

Provides DS-001 index construction, text normalisation, duration-based
tie-breaking, and the main per-event matching loop.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any
from rapidfuzz import fuzz

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


def _resolve_fuzzy_controls(raw_controls: dict[str, Any] | None) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "enabled": False,
        "artist_threshold": 0.90,
        "title_threshold": 0.90,
        "combined_threshold": 0.90,
        "max_duration_delta_ms": 5000,
        "max_artist_candidates": 5,
    }
    if not isinstance(raw_controls, dict):
        return defaults
    controls = dict(defaults)
    controls["enabled"] = bool(raw_controls.get("enabled", defaults["enabled"]))
    for key in ("artist_threshold", "title_threshold", "combined_threshold"):
        try:
            value = float(raw_controls.get(key, defaults[key]))
        except (TypeError, ValueError):
            value = float(defaults[key])
        controls[key] = min(1.0, max(0.0, value))
    for key in ("max_duration_delta_ms", "max_artist_candidates"):
        try:
            value = int(raw_controls.get(key, defaults[key]))
        except (TypeError, ValueError):
            value = int(defaults[key])
        controls[key] = max(1, value)
    return controls


def _fuzzy_find_candidate(
    *,
    title_key: str,
    artist_key: str,
    event_duration: int | None,
    by_artist: dict[str, list[dict[str, str]]],
    fuzzy_controls: dict[str, Any],
) -> tuple[dict[str, str] | None, int | None, float | None, float | None, float | None]:
    artist_keys = sorted(by_artist.keys())
    if not artist_keys:
        return None, None, None, None, None

    artist_matches: list[tuple[str, float]] = []
    artist_cutoff = float(fuzzy_controls["artist_threshold"])
    for candidate_artist_key in artist_keys:
        artist_score = float(fuzz.ratio(artist_key, candidate_artist_key)) / 100.0
        if artist_score >= artist_cutoff:
            artist_matches.append((candidate_artist_key, artist_score))

    if not artist_matches:
        return None, None, None, None, None

    artist_matches = sorted(
        artist_matches,
        key=lambda match: (-float(match[1]), str(match[0])),
    )[: int(fuzzy_controls["max_artist_candidates"])]

    deduped_candidates: dict[str, tuple[dict[str, str], float]] = {}
    for artist_match_key, artist_score in artist_matches:
        for candidate in by_artist.get(artist_match_key, []):
            ds001_id = (candidate.get("id") or "").strip()
            if not ds001_id:
                continue
            previous = deduped_candidates.get(ds001_id)
            if previous is None or artist_score > previous[1]:
                deduped_candidates[ds001_id] = (candidate, artist_score)

    best_choice: tuple[dict[str, str], int | None, float, float, float] | None = None
    best_sort_key: tuple[float, float, float, int, str] | None = None
    for ds001_id in sorted(deduped_candidates.keys()):
        candidate, artist_score = deduped_candidates[ds001_id]
        candidate_title_key = normalize_text(candidate.get("song", ""))
        if not candidate_title_key:
            continue

        title_score = float(fuzz.ratio(title_key, candidate_title_key)) / 100.0
        if title_score < fuzzy_controls["title_threshold"]:
            continue

        combined_score = (artist_score + title_score) / 2.0
        if combined_score < fuzzy_controls["combined_threshold"]:
            continue

        duration_delta: int | None = None
        candidate_duration = parse_int(candidate.get("duration_ms", ""))
        if event_duration is not None and candidate_duration is not None:
            duration_delta = abs(candidate_duration - event_duration)
            if duration_delta > fuzzy_controls["max_duration_delta_ms"]:
                continue

        duration_sort = duration_delta if duration_delta is not None else 10**12
        sort_key = (-combined_score, -title_score, -artist_score, duration_sort, ds001_id)
        if best_sort_key is None or sort_key < best_sort_key:
            best_sort_key = sort_key
            best_choice = (candidate, duration_delta, title_score, artist_score, combined_score)

    if best_choice is None:
        return None, None, None, None, None
    return best_choice


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
    by_artist: dict[str, list[dict[str, str]]],
    top_range_weights: dict,
    source_base_weights: dict,
    decay_half_lives: dict[str, float] | None = None,
    fuzzy_controls: dict[str, Any] | None = None,
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
        "matched_by_fuzzy": 0,
        "unmatched": 0,
        "unmatched_missing_keys": 0,
        "unmatched_no_candidate": 0,
    }
    resolved_fuzzy_controls = _resolve_fuzzy_controls(fuzzy_controls)

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
        trace["fuzzy_title_score"] = ""
        trace["fuzzy_artist_score"] = ""
        trace["fuzzy_combined_score"] = ""
        trace["reason"] = ""
        trace["preference_weight"] = f"{weight:.6f}"

        matched_row: dict[str, str] | None = None
        duration_delta: int | None = None
        match_method = ""
        fuzzy_title_score: float | None = None
        fuzzy_artist_score: float | None = None
        fuzzy_combined_score: float | None = None

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
                elif resolved_fuzzy_controls["enabled"]:
                    (
                        matched_row,
                        duration_delta,
                        fuzzy_title_score,
                        fuzzy_artist_score,
                        fuzzy_combined_score,
                    ) = _fuzzy_find_candidate(
                        title_key=title_key,
                        artist_key=artist_key,
                        event_duration=event_duration,
                        by_artist=by_artist,
                        fuzzy_controls=resolved_fuzzy_controls,
                    )
                    if matched_row is not None:
                        match_method = "fuzzy_title_artist"
                        match_counts["matched_by_fuzzy"] += 1

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
        if fuzzy_title_score is not None:
            trace["fuzzy_title_score"] = f"{fuzzy_title_score:.6f}"
        if fuzzy_artist_score is not None:
            trace["fuzzy_artist_score"] = f"{fuzzy_artist_score:.6f}"
        if fuzzy_combined_score is not None:
            trace["fuzzy_combined_score"] = f"{fuzzy_combined_score:.6f}"

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
            "fuzzy_title_score": fuzzy_title_score,
            "fuzzy_artist_score": fuzzy_artist_score,
            "fuzzy_combined_score": fuzzy_combined_score,
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
