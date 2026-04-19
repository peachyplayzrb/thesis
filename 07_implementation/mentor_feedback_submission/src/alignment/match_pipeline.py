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
    MATCH_STATUS_MATCHED,
    MATCH_STATUS_UNMATCHED,
    MATCH_STRATEGY_ORDER,
    UNMATCHED_REASON_FUZZY_ARTIST_THRESHOLD_FAILED,
    UNMATCHED_REASON_FUZZY_COMBINED_THRESHOLD_FAILED,
    UNMATCHED_REASON_FUZZY_DURATION_REJECTED,
    UNMATCHED_REASON_FUZZY_TITLE_THRESHOLD_FAILED,
    UNMATCHED_REASON_MISSING_KEYS,
    UNMATCHED_REASON_NO_CANDIDATE,
    format_alignment_event_id,
)
from alignment.models import AlignmentBehaviorControls, MatchedEvent, MatchTrace, SourceEvent
from alignment.resolved_context import AlignmentResolvedContext
from alignment.weighting import compute_weight
from shared_utils.index_builder import resolve_ds001_id
from shared_utils.parsing import parse_int
from shared_utils.text_matching import (
    choose_best_duration_match,
    first_artist,
    fuzzy_find_candidate,
    normalize_text,
    resolve_fuzzy_controls,
    split_artists,
)


def _build_fuzzy_pass_controls(
    resolved_fuzzy_controls: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    fuzzy_pass_controls: list[tuple[str, dict[str, Any]]] = [
        ("pass_1", dict(resolved_fuzzy_controls))
    ]
    if not resolved_fuzzy_controls.get("enable_relaxed_second_pass"):
        return fuzzy_pass_controls

    relaxed_controls = dict(resolved_fuzzy_controls)
    relaxed_controls["artist_threshold"] = float(
        str(
            resolved_fuzzy_controls.get(
                "relaxed_second_pass_artist_threshold",
                resolved_fuzzy_controls.get("artist_threshold", 0.0),
            )
        )
    )
    relaxed_controls["title_threshold"] = float(
        str(
            resolved_fuzzy_controls.get(
                "relaxed_second_pass_title_threshold",
                resolved_fuzzy_controls.get("title_threshold", 0.0),
            )
        )
    )
    relaxed_controls["combined_threshold"] = float(
        str(
            resolved_fuzzy_controls.get(
                "relaxed_second_pass_combined_threshold",
                resolved_fuzzy_controls.get("combined_threshold", 0.0),
            )
        )
    )
    fuzzy_pass_controls.append(("pass_2_relaxed", relaxed_controls))
    return fuzzy_pass_controls


def _resolve_fuzzy_failure_reason(current_reason: str, previous_reason: str) -> str:
    failure_rank = {
        "": -1,
        "artist_threshold": 1,
        "title_threshold": 2,
        "combined_threshold": 3,
        "duration_rejected": 4,
    }
    if failure_rank.get(current_reason, -1) > failure_rank.get(previous_reason, -1):
        return current_reason
    return previous_reason


def _run_fuzzy_match(
    *,
    title_key: str,
    album_key: str,
    artist_names: str,
    artist_primary: str,
    event_duration: int | None,
    by_artist: dict[str, list[dict[str, str]]],
    resolved_fuzzy_controls: dict[str, Any],
) -> dict[str, Any]:
    artist_candidates = [artist_primary] if artist_primary else []
    if resolved_fuzzy_controls.get("enable_secondary_artist_retry"):
        artist_candidates = split_artists(artist_names)
    if not artist_candidates and artist_primary:
        artist_candidates = [artist_primary]

    fuzzy_pass_controls = _build_fuzzy_pass_controls(resolved_fuzzy_controls)
    fuzzy_candidate_count = 0
    fuzzy_failure_reason = ""

    for pass_used, pass_controls in fuzzy_pass_controls:
        for attempt_index, candidate_artist in enumerate(artist_candidates, start=1):
            (
                matched_row,
                duration_delta,
                fuzzy_title_score,
                fuzzy_artist_score,
                fuzzy_combined_score,
                fuzzy_diagnostics,
            ) = fuzzy_find_candidate(
                title_key=title_key,
                artist_key=normalize_text(candidate_artist),
                event_duration=event_duration,
                by_artist=by_artist,
                fuzzy_controls=pass_controls,
                album_key=album_key,
            )

            fuzzy_candidate_count = max(
                fuzzy_candidate_count,
                int(fuzzy_diagnostics.get("candidate_count_after_artist_filter", 0) or 0),
            )
            current_reason = str(fuzzy_diagnostics.get("failure_reason", "") or "")
            fuzzy_failure_reason = _resolve_fuzzy_failure_reason(current_reason, fuzzy_failure_reason)

            if matched_row is None:
                continue

            fuzzy_album_score_raw = fuzzy_diagnostics.get("album_score")
            fuzzy_album_score = (
                float(fuzzy_album_score_raw)
                if fuzzy_album_score_raw is not None
                else None
            )
            return {
                "matched_row": matched_row,
                "duration_delta": duration_delta,
                "fuzzy_title_score": fuzzy_title_score,
                "fuzzy_artist_score": fuzzy_artist_score,
                "fuzzy_combined_score": fuzzy_combined_score,
                "fuzzy_album_score": fuzzy_album_score,
                "fuzzy_pass_used": pass_used,
                "fuzzy_artist_attempt_count": attempt_index,
                "fuzzy_candidate_count": fuzzy_candidate_count,
                "fuzzy_failure_reason": fuzzy_failure_reason,
            }

    return {
        "matched_row": None,
        "duration_delta": None,
        "fuzzy_title_score": None,
        "fuzzy_artist_score": None,
        "fuzzy_combined_score": None,
        "fuzzy_album_score": None,
        "fuzzy_pass_used": "",
        "fuzzy_artist_attempt_count": 0,
        "fuzzy_candidate_count": fuzzy_candidate_count,
        "fuzzy_failure_reason": fuzzy_failure_reason,
    }


def _update_unmatched_reason_counts(
    *,
    match_counts: dict[str, int],
    spotify_track_id: str,
    track_name: str,
    artist_primary: str,
    fuzzy_failure_reason: str,
) -> str:
    if not spotify_track_id and not (track_name and artist_primary):
        match_counts["unmatched_missing_keys"] += 1
        return UNMATCHED_REASON_MISSING_KEYS

    match_counts["unmatched_no_candidate"] += 1
    if fuzzy_failure_reason == "artist_threshold":
        match_counts["fuzzy_artist_threshold_failed"] += 1
        return UNMATCHED_REASON_FUZZY_ARTIST_THRESHOLD_FAILED
    if fuzzy_failure_reason == "title_threshold":
        match_counts["fuzzy_title_threshold_failed"] += 1
        return UNMATCHED_REASON_FUZZY_TITLE_THRESHOLD_FAILED
    if fuzzy_failure_reason == "combined_threshold":
        match_counts["fuzzy_combined_threshold_failed"] += 1
        return UNMATCHED_REASON_FUZZY_COMBINED_THRESHOLD_FAILED
    if fuzzy_failure_reason == "duration_rejected":
        match_counts["fuzzy_duration_rejected"] += 1
        return UNMATCHED_REASON_FUZZY_DURATION_REJECTED
    return UNMATCHED_REASON_NO_CANDIDATE


def _resolve_match_for_event(
    *,
    effective_match_strategy_order: list[str],
    effective_match_strategy: dict[str, bool],
    spotify_track_id: str,
    title_key: str,
    artist_key: str,
    album_key: str,
    artist_names: str,
    artist_primary: str,
    event_duration: int | None,
    by_spotify_id: dict[str, dict[str, str]],
    by_title_artist: dict[tuple[str, str], list[dict[str, str]]],
    by_artist: dict[str, list[dict[str, str]]],
    resolved_fuzzy_controls: dict[str, Any],
    match_counts: dict[str, int],
) -> dict[str, Any]:
    resolved_match: dict[str, Any] = {
        "matched_row": None,
        "duration_delta": None,
        "match_method": "",
        "fuzzy_title_score": None,
        "fuzzy_artist_score": None,
        "fuzzy_combined_score": None,
        "fuzzy_album_score": None,
        "fuzzy_pass_used": "",
        "fuzzy_artist_attempt_count": 0,
        "fuzzy_candidate_count": 0,
        "fuzzy_failure_reason": "",
    }

    for method in effective_match_strategy_order:
        if method == MATCH_METHOD_SPOTIFY_ID_EXACT:
            if (
                effective_match_strategy.get("enable_spotify_id_match", True)
                and spotify_track_id
                and spotify_track_id in by_spotify_id
            ):
                resolved_match["matched_row"] = by_spotify_id[spotify_track_id]
                resolved_match["match_method"] = MATCH_METHOD_SPOTIFY_ID_EXACT
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
                resolved_match["matched_row"] = matched_row
                resolved_match["duration_delta"] = duration_delta
                resolved_match["match_method"] = MATCH_METHOD_METADATA_FALLBACK
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

            match_counts["fuzzy_attempted_rows"] += 1
            fuzzy_match = _run_fuzzy_match(
                title_key=title_key,
                album_key=album_key,
                artist_names=artist_names,
                artist_primary=artist_primary,
                event_duration=event_duration,
                by_artist=by_artist,
                resolved_fuzzy_controls=resolved_fuzzy_controls,
            )
            resolved_match.update(fuzzy_match)

            if resolved_match["matched_row"] is not None:
                resolved_match["match_method"] = MATCH_METHOD_FUZZY_TITLE_ARTIST
                match_counts["matched_by_fuzzy"] += 1
                if resolved_match["fuzzy_pass_used"] == "pass_2_relaxed":
                    match_counts["fuzzy_second_pass_matches"] += 1
                if resolved_match["fuzzy_album_score"] is not None and album_key:
                    match_counts["fuzzy_album_boost_matches"] += 1
                break

    return resolved_match


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
    *,
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
        "fuzzy_attempted_rows": 0,
        "fuzzy_second_pass_matches": 0,
        "fuzzy_album_boost_matches": 0,
        "fuzzy_artist_threshold_failed": 0,
        "fuzzy_title_threshold_failed": 0,
        "fuzzy_combined_threshold_failed": 0,
        "fuzzy_duration_rejected": 0,
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
        fuzzy_album_score: float | None = None
        fuzzy_pass_used = ""
        fuzzy_artist_attempt_count = 0
        fuzzy_candidate_count = 0
        fuzzy_failure_reason = ""

        title_key = normalize_text(track_name)
        artist_key = normalize_text(artist_primary)
        album_key = normalize_text(source_event.album_name)
        resolved_match = _resolve_match_for_event(
            effective_match_strategy_order=effective_match_strategy_order,
            effective_match_strategy=effective_match_strategy,
            spotify_track_id=spotify_track_id,
            title_key=title_key,
            artist_key=artist_key,
            album_key=album_key,
            artist_names=artist_names,
            artist_primary=artist_primary,
            event_duration=event_duration,
            by_spotify_id=by_spotify_id,
            by_title_artist=by_title_artist,
            by_artist=by_artist,
            resolved_fuzzy_controls=resolved_fuzzy_controls,
            match_counts=match_counts,
        )
        matched_row = resolved_match["matched_row"]
        duration_delta = resolved_match["duration_delta"]
        match_method = str(resolved_match["match_method"])
        fuzzy_title_score = resolved_match["fuzzy_title_score"]
        fuzzy_artist_score = resolved_match["fuzzy_artist_score"]
        fuzzy_combined_score = resolved_match["fuzzy_combined_score"]
        fuzzy_album_score = resolved_match["fuzzy_album_score"]
        fuzzy_pass_used = str(resolved_match["fuzzy_pass_used"])
        fuzzy_artist_attempt_count = int(resolved_match["fuzzy_artist_attempt_count"])
        fuzzy_candidate_count = int(resolved_match["fuzzy_candidate_count"])
        fuzzy_failure_reason = str(resolved_match["fuzzy_failure_reason"])

        if matched_row is None:
            match_counts["unmatched"] += 1
            trace.match_status = MATCH_STATUS_UNMATCHED
            trace.reason = _update_unmatched_reason_counts(
                match_counts=match_counts,
                spotify_track_id=spotify_track_id,
                track_name=track_name,
                artist_primary=artist_primary,
                fuzzy_failure_reason=fuzzy_failure_reason,
            )
            trace.fuzzy_pass_used = fuzzy_pass_used
            trace.fuzzy_artist_attempt_count = str(fuzzy_artist_attempt_count) if fuzzy_artist_attempt_count else ""
            trace.fuzzy_candidate_count = str(fuzzy_candidate_count) if fuzzy_candidate_count else ""
            trace_dict = trace.to_dict()
            unmatched_rows.append(trace_dict)
            trace_rows.append(trace_dict)
            continue

        trace.match_status = MATCH_STATUS_MATCHED
        trace.match_method = match_method
        matched_ds001_id = resolve_ds001_id(matched_row)
        trace.matched_ds001_id = matched_ds001_id
        trace.matched_song = matched_row.get("song", "")
        trace.matched_artist = matched_row.get("artist", "")
        trace.duration_delta_ms = "" if duration_delta is None else str(duration_delta)
        if fuzzy_title_score is not None:
            trace.fuzzy_title_score = f"{fuzzy_title_score:.{FLOAT_PRECISION_DECIMALS}f}"
        if fuzzy_artist_score is not None:
            trace.fuzzy_artist_score = f"{fuzzy_artist_score:.{FLOAT_PRECISION_DECIMALS}f}"
        if fuzzy_combined_score is not None:
            trace.fuzzy_combined_score = f"{fuzzy_combined_score:.{FLOAT_PRECISION_DECIMALS}f}"
        if fuzzy_album_score is not None:
            trace.fuzzy_album_score = f"{fuzzy_album_score:.{FLOAT_PRECISION_DECIMALS}f}"
        trace.fuzzy_pass_used = fuzzy_pass_used
        trace.fuzzy_artist_attempt_count = str(fuzzy_artist_attempt_count) if fuzzy_artist_attempt_count else ""
        trace.fuzzy_candidate_count = str(fuzzy_candidate_count) if fuzzy_candidate_count else ""

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
            ds001_id=matched_ds001_id,
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
