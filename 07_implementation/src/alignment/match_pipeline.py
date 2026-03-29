"""Per-event DS-001 matching pipeline for BL-003."""
from __future__ import annotations

from typing import Any

from alignment.constants import (
    FLOAT_PRECISION_DECIMALS,
    INTERACTION_COUNT_WEIGHT_SCALE,
    INTERACTION_TYPE_HISTORY,
    MATCH_METHOD_FUZZY_TITLE_ARTIST,
    MATCH_METHOD_METADATA_FALLBACK,
    MATCH_METHOD_SPOTIFY_ID_EXACT,
    MATCH_STRATEGY_ORDER,
    MATCH_STATUS_MATCHED,
    MATCH_STATUS_UNMATCHED,
    UNMATCHED_REASON_MISSING_KEYS,
    UNMATCHED_REASON_NO_CANDIDATE,
    format_alignment_event_id,
)
from alignment.models import AlignmentBehaviorControls, MatchTrace, MatchedEvent, SourceEvent
from alignment.resolved_context import AlignmentResolvedContext
from shared_utils.parsing import parse_int
from alignment.text_matching import (
    choose_best_duration_match,
    first_artist,
    fuzzy_find_candidate,
    normalize_text,
    resolve_fuzzy_controls,
)
from alignment.weighting import compute_weight


def match_events(
    events: list[dict[str, str]],
    by_spotify_id: dict[str, dict[str, str]],
    by_title_artist: dict[tuple[str, str], list[dict[str, str]]],
    by_artist: dict[str, list[dict[str, str]]],
    top_range_weights: dict | None = None,
    source_base_weights: dict | None = None,
    decay_half_lives: dict[str, float] | None = None,
    fuzzy_controls: dict[str, Any] | None = None,
    weighting_policy: dict | None = None,
    behavior_controls: AlignmentBehaviorControls | None = None,
    context: AlignmentResolvedContext | None = None,
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
    effective_top_range_weights = top_range_weights
    effective_source_base_weights = source_base_weights
    effective_decay_half_lives = decay_half_lives
    effective_fuzzy_controls = fuzzy_controls
    effective_weighting_policy = weighting_policy
    effective_match_strategy = {
        "enable_spotify_id_match": True,
        "enable_metadata_match": True,
        "enable_fuzzy_match": True,
    }
    effective_match_strategy_order = list(MATCH_STRATEGY_ORDER)
    if context is not None:
        behavior_controls = context.behavior_controls

    if behavior_controls is not None:
        effective_top_range_weights = dict(behavior_controls.top_range_weights)
        effective_source_base_weights = dict(behavior_controls.source_base_weights)
        effective_decay_half_lives = dict(behavior_controls.decay_half_lives)
        effective_fuzzy_controls = dict(behavior_controls.fuzzy_matching_controls)
        effective_weighting_policy = (
            dict(behavior_controls.weighting_policy)
            if behavior_controls.weighting_policy is not None
            else None
        )
        effective_match_strategy.update(
            {k: bool(v) for k, v in dict(behavior_controls.match_strategy).items()}
        )
        if behavior_controls.match_strategy_order:
            effective_match_strategy_order = list(behavior_controls.match_strategy_order)

    if effective_top_range_weights is None or effective_source_base_weights is None:
        raise ValueError(
            "match_events requires either context or top/source weight dictionaries"
        )

    resolved_fuzzy_controls = resolve_fuzzy_controls(effective_fuzzy_controls)

    for event in events:
        source_event = SourceEvent.from_dict(event)
        spotify_track_id = source_event.spotify_track_id
        track_name = source_event.track_name
        artist_names = source_event.artist_names
        artist_primary = first_artist(artist_names)
        event_duration = parse_int(source_event.duration_ms)
        weight = compute_weight(
            source_event.to_dict(),
            effective_top_range_weights,
            effective_source_base_weights,
            decay_half_lives=effective_decay_half_lives,
            weighting_policy=effective_weighting_policy,
            behavior_controls=behavior_controls,
        )

        trace = MatchTrace.from_event(source_event, weight)

        matched_row: dict[str, str] | None = None
        duration_delta: int | None = None
        match_method = ""
        fuzzy_title_score: float | None = None
        fuzzy_artist_score: float | None = None
        fuzzy_combined_score: float | None = None

        title_key = normalize_text(track_name)
        artist_key = normalize_text(artist_primary)

        for method in effective_match_strategy_order:
            if method == MATCH_METHOD_SPOTIFY_ID_EXACT:
                if (
                    effective_match_strategy.get("enable_spotify_id_match", True)
                    and spotify_track_id
                    and spotify_track_id in by_spotify_id
                ):
                    matched_row = by_spotify_id[spotify_track_id]
                    match_method = MATCH_METHOD_SPOTIFY_ID_EXACT
                    match_counts["matched_by_spotify_id"] += 1
                    break
                continue

            if method == MATCH_METHOD_METADATA_FALLBACK:
                if not effective_match_strategy.get("enable_metadata_match", True):
                    continue
                if not (title_key and artist_key):
                    continue
                candidates = by_title_artist.get((title_key, artist_key), [])
                if candidates:
                    matched_row, duration_delta = choose_best_duration_match(candidates, event_duration)
                    match_method = MATCH_METHOD_METADATA_FALLBACK
                    match_counts["matched_by_metadata"] += 1
                    break
                continue

            if method == MATCH_METHOD_FUZZY_TITLE_ARTIST:
                if not effective_match_strategy.get("enable_fuzzy_match", True):
                    continue
                if not resolved_fuzzy_controls["enabled"]:
                    continue
                if not (title_key and artist_key):
                    continue
                (
                    matched_row,
                    duration_delta,
                    fuzzy_title_score,
                    fuzzy_artist_score,
                    fuzzy_combined_score,
                ) = fuzzy_find_candidate(
                    title_key=title_key,
                    artist_key=artist_key,
                    event_duration=event_duration,
                    by_artist=by_artist,
                    fuzzy_controls=resolved_fuzzy_controls,
                )
                if matched_row is not None:
                    match_method = MATCH_METHOD_FUZZY_TITLE_ARTIST
                    match_counts["matched_by_fuzzy"] += 1
                    break

        if matched_row is None:
            match_counts["unmatched"] += 1
            trace.match_status = MATCH_STATUS_UNMATCHED
            if not spotify_track_id and not (track_name and artist_primary):
                match_counts["unmatched_missing_keys"] += 1
                trace.reason = UNMATCHED_REASON_MISSING_KEYS
            else:
                match_counts["unmatched_no_candidate"] += 1
                trace.reason = UNMATCHED_REASON_NO_CANDIDATE
            trace_dict = trace.to_dict()
            unmatched_rows.append(trace_dict)
            trace_rows.append(trace_dict)
            continue

        trace.match_status = MATCH_STATUS_MATCHED
        trace.match_method = match_method
        trace.matched_ds001_id = matched_row.get("id", "")
        trace.matched_song = matched_row.get("song", "")
        trace.matched_artist = matched_row.get("artist", "")
        trace.duration_delta_ms = "" if duration_delta is None else str(duration_delta)
        if fuzzy_title_score is not None:
            trace.fuzzy_title_score = f"{fuzzy_title_score:.{FLOAT_PRECISION_DECIMALS}f}"
        if fuzzy_artist_score is not None:
            trace.fuzzy_artist_score = f"{fuzzy_artist_score:.{FLOAT_PRECISION_DECIMALS}f}"
        if fuzzy_combined_score is not None:
            trace.fuzzy_combined_score = f"{fuzzy_combined_score:.{FLOAT_PRECISION_DECIMALS}f}"

        source_row_index = parse_int(source_event.source_row_index)
        source_row_index = source_row_index if source_row_index is not None else 0
        matched_event = MatchedEvent(
            event_id=format_alignment_event_id(len(matched_events) + 1),
            source_type=source_event.source_type,
            source_row_index=source_row_index,
            source_timestamp=source_event.event_time,
            spotify_track_id=spotify_track_id,
            spotify_isrc=source_event.isrc,
            spotify_track_name=track_name,
            spotify_artist_names=artist_names,
            match_method=match_method,
            duration_delta_ms=duration_delta,
            fuzzy_title_score=fuzzy_title_score,
            fuzzy_artist_score=fuzzy_artist_score,
            fuzzy_combined_score=fuzzy_combined_score,
            ds001_id=matched_row.get("id", ""),
            ds001_spotify_id=matched_row.get("spotify_id", ""),
            artist=matched_row.get("artist", ""),
            song=matched_row.get("song", ""),
            release=matched_row.get("release", ""),
            duration_ms=matched_row.get("duration_ms", ""),
            popularity=matched_row.get("popularity", ""),
            danceability=matched_row.get("danceability", ""),
            energy=matched_row.get("energy", ""),
            key=matched_row.get("key", ""),
            mode=matched_row.get("mode", ""),
            valence=matched_row.get("valence", ""),
            tempo=matched_row.get("tempo", ""),
            genres=matched_row.get("genres", ""),
            tags=matched_row.get("tags", ""),
            lang=matched_row.get("lang", ""),
            preference_weight=weight,
            interaction_count=max(1, int(round(weight * INTERACTION_COUNT_WEIGHT_SCALE))),
            interaction_type=INTERACTION_TYPE_HISTORY,
        )
        matched_events.append(matched_event.to_dict())
        trace_rows.append(trace.to_dict())

    return trace_rows, matched_events, unmatched_rows, match_counts
