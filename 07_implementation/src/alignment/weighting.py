"""
BL-003 event weighting helpers.

Computes per-event preference weights and converts raw Spotify export rows
into normalised event dicts consumed by the matching loop.
"""

from __future__ import annotations

import math
import os
from datetime import datetime, timezone

from shared_utils.constants import (
    DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
    DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
    DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK,
)
from shared_utils.parsing import parse_int


def _parse_event_time(raw_value: str) -> datetime | None:
    token = raw_value.strip()
    if not token:
        return None
    normalized = token.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _resolve_reference_now_utc(now_utc: datetime | None = None) -> datetime:
    if now_utc is not None:
        return now_utc.astimezone(timezone.utc)
    override = (os.getenv("BL_REFERENCE_NOW_UTC") or "").strip()
    if override:
        parsed = _parse_event_time(override)
        if parsed is not None:
            return parsed
    return datetime.now(timezone.utc)


def compute_temporal_decay(event_time: str, half_life_days: float, now_utc: datetime | None = None) -> float:
    """Return exponential time-decay factor using a half-life in days."""
    if half_life_days <= 0:
        return 1.0
    event_dt = _parse_event_time(event_time)
    if event_dt is None:
        return 1.0
    reference_now = _resolve_reference_now_utc(now_utc)
    age_days = max(0.0, (reference_now - event_dt).total_seconds() / 86400.0)
    decay = math.exp(-math.log(2.0) * (age_days / half_life_days))
    return round(max(0.0, min(decay, 1.0)), 6)


def compute_weight(
    event: dict[str, str],
    top_range_weights: dict,
    source_base_weights: dict,
    decay_half_lives: dict[str, float] | None = None,
    weighting_policy: dict | None = None,
) -> float:
    """Return a preference weight for a single event based on its source type and position."""
    source_type = event["source_type"]
    base = source_base_weights.get(source_type, DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK)
    effective_decay_half_lives = dict(decay_half_lives or {})

    # Resolve weighting policy knobs — defaults match previously embedded constants.
    _policy = dict(weighting_policy or {})
    _min_rank_floor = float(_policy.get("top_tracks_min_rank_floor", 0.05))
    _scale_top = float(_policy.get("top_tracks_scale_multiplier", 100.0))
    _default_time_range_w = float(_policy.get("top_tracks_default_time_range_weight", 0.20))
    _min_pos_floor = float(_policy.get("playlist_items_min_position_floor", 0.05))
    _scale_pl = float(_policy.get("playlist_items_scale_multiplier", 20.0))

    def apply_decay(raw_weight: float, source_key: str, default_half_life: float) -> float:
        half_life = float(effective_decay_half_lives.get(source_key, default_half_life))
        decay_factor = compute_temporal_decay(event.get("event_time", ""), half_life)
        return raw_weight * decay_factor

    if source_type == "top_tracks":
        rank = parse_int(event.get("rank", ""))
        rank = rank if (rank is not None and rank > 0) else 50
        range_weight = top_range_weights.get(event.get("time_range", ""), _default_time_range_w)
        rank_score = max(_min_rank_floor, 1.0 / rank)
        return round(base * range_weight * rank_score * _scale_top, 6)

    if source_type == "saved_tracks":
        return round(
            apply_decay(base * 1.0, "saved_tracks", DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS),
            6,
        )

    if source_type == "playlist_items":
        pos = parse_int(event.get("playlist_position", ""))
        if pos is None or pos <= 0:
            pos = 50
        return round(base * max(_min_pos_floor, 1.0 / pos) * _scale_pl, 6)

    if source_type == "recently_played":
        return round(
            apply_decay(
                base * 1.0,
                "recently_played",
                DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
            ),
            6,
        )

    return round(base, 6)


def to_event_rows(source_type: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Convert raw Spotify export rows into normalised event dicts for matching."""
    events: list[dict[str, str]] = []

    for idx, row in enumerate(rows, start=1):
        event: dict[str, str] = {
            "source_type": source_type,
            "source_row_index": str(idx),
            "spotify_track_id": (row.get("track_id") or "").strip(),
            "isrc": (row.get("isrc") or "").strip(),
            "track_name": (row.get("track_name") or "").strip(),
            "artist_names": (row.get("artist_names") or "").strip(),
            "duration_ms": (row.get("duration_ms") or "").strip(),
            "event_time": "",
            "time_range": (row.get("time_range") or "").strip(),
            "rank": (row.get("rank") or "").strip(),
            "playlist_id": (row.get("playlist_id") or "").strip(),
            "playlist_name": (row.get("playlist_name") or "").strip(),
            "playlist_position": (row.get("playlist_position") or "").strip(),
        }

        if source_type == "saved_tracks":
            event["event_time"] = (row.get("added_at") or "").strip()
        elif source_type == "playlist_items":
            event["event_time"] = (row.get("added_at") or "").strip()
        elif source_type == "recently_played":
            event["event_time"] = (row.get("played_at") or "").strip()

        events.append(event)

    return events
