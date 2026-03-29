"""
BL-003 event weighting helpers.

Computes per-event preference weights and converts raw Spotify export rows
into normalised event dicts consumed by the matching loop.
"""

from __future__ import annotations

import math
import os
from datetime import datetime, timezone

from alignment.constants import (
    FLOAT_PRECISION_DECIMALS,
    SECONDS_PER_DAY,
    SOURCE_PLAYLIST_ITEMS,
    SOURCE_RECENTLY_PLAYED,
    SOURCE_SAVED_TRACKS,
    SOURCE_TOP_TRACKS,
)
from shared_utils.constants import (
    DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
    DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
    DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK,
    DEFAULT_WEIGHTING_POLICY,
)
from shared_utils.parsing import parse_int
from alignment.models import AlignmentBehaviorControls, SourceEvent


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


def _resolve_reference_now_utc(
    now_utc: datetime | None = None,
    temporal_controls: dict[str, object] | None = None,
) -> datetime:
    if now_utc is not None:
        return now_utc.astimezone(timezone.utc)

    controls = dict(temporal_controls or {})
    reference_mode = str(controls.get("reference_mode") or "system").strip().lower()
    if reference_mode == "fixed":
        configured_reference = str(controls.get("reference_now_utc") or "").strip()
        if configured_reference:
            parsed = _parse_event_time(configured_reference)
            if parsed is not None:
                return parsed

    override = (os.getenv("BL_REFERENCE_NOW_UTC") or "").strip()
    if override:
        parsed = _parse_event_time(override)
        if parsed is not None:
            return parsed
    return datetime.now(timezone.utc)


def compute_temporal_decay(
    event_time: str,
    half_life_days: float,
    now_utc: datetime | None = None,
    temporal_controls: dict[str, object] | None = None,
) -> float:
    """Return exponential time-decay factor using a half-life in days."""
    if half_life_days <= 0:
        return 1.0
    event_dt = _parse_event_time(event_time)
    if event_dt is None:
        return 1.0
    reference_now = _resolve_reference_now_utc(now_utc, temporal_controls=temporal_controls)
    age_days = max(0.0, (reference_now - event_dt).total_seconds() / SECONDS_PER_DAY)
    decay = math.exp(-math.log(2.0) * (age_days / half_life_days))
    return round(max(0.0, min(decay, 1.0)), FLOAT_PRECISION_DECIMALS)


def compute_weight(
    event: dict[str, str],
    top_range_weights: dict | None = None,
    source_base_weights: dict | None = None,
    decay_half_lives: dict[str, float] | None = None,
    temporal_controls: dict[str, object] | None = None,
    weighting_policy: dict | None = None,
    behavior_controls: AlignmentBehaviorControls | None = None,
) -> float:
    """Return a preference weight for a single event based on its source type and position."""
    if behavior_controls is not None:
        top_range_weights = dict(behavior_controls.top_range_weights)
        source_base_weights = dict(behavior_controls.source_base_weights)
        decay_half_lives = dict(behavior_controls.decay_half_lives)
        temporal_controls = dict(behavior_controls.temporal_controls)
        weighting_policy = (
            dict(behavior_controls.weighting_policy)
            if behavior_controls.weighting_policy is not None
            else None
        )

    if top_range_weights is None or source_base_weights is None:
        raise ValueError(
            "compute_weight requires top/source weight dictionaries or behavior_controls"
        )

    source_type = event["source_type"]
    base = source_base_weights.get(source_type, DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK)
    effective_decay_half_lives = dict(decay_half_lives or {})

    # Resolve weighting policy knobs — defaults match previously embedded constants.
    _policy = dict(weighting_policy or {})
    _top_policy = dict(DEFAULT_WEIGHTING_POLICY["top_tracks"])
    _playlist_policy = dict(DEFAULT_WEIGHTING_POLICY["playlist_items"])
    _min_rank_floor = float(_policy.get("top_tracks_min_rank_floor", _top_policy["min_rank_floor"]))
    _scale_top = float(_policy.get("top_tracks_scale_multiplier", _top_policy["scale_multiplier"]))
    _default_time_range_w = float(
        _policy.get("top_tracks_default_time_range_weight", _top_policy["default_time_range_weight"])
    )
    _min_pos_floor = float(_policy.get("playlist_items_min_position_floor", _playlist_policy["min_position_floor"]))
    _scale_pl = float(_policy.get("playlist_items_scale_multiplier", _playlist_policy["scale_multiplier"]))

    def apply_decay(raw_weight: float, source_key: str, default_half_life: float) -> float:
        half_life = float(effective_decay_half_lives.get(source_key, default_half_life))
        decay_factor = compute_temporal_decay(
            event.get("event_time", ""),
            half_life,
            temporal_controls=temporal_controls,
        )
        return raw_weight * decay_factor

    if source_type == SOURCE_TOP_TRACKS:
        rank = parse_int(event.get("rank", ""))
        rank = rank if (rank is not None and rank > 0) else 50
        range_weight = top_range_weights.get(event.get("time_range", ""), _default_time_range_w)
        rank_score = max(_min_rank_floor, 1.0 / rank)
        return round(base * range_weight * rank_score * _scale_top, FLOAT_PRECISION_DECIMALS)

    if source_type == SOURCE_SAVED_TRACKS:
        return round(
            apply_decay(base * 1.0, SOURCE_SAVED_TRACKS, DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS),
            FLOAT_PRECISION_DECIMALS,
        )

    if source_type == SOURCE_PLAYLIST_ITEMS:
        pos = parse_int(event.get("playlist_position", ""))
        if pos is None or pos <= 0:
            pos = 50
        return round(base * max(_min_pos_floor, 1.0 / pos) * _scale_pl, FLOAT_PRECISION_DECIMALS)

    if source_type == SOURCE_RECENTLY_PLAYED:
        return round(
            apply_decay(
                base * 1.0,
                SOURCE_RECENTLY_PLAYED,
                DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
            ),
            FLOAT_PRECISION_DECIMALS,
        )

    return round(base, FLOAT_PRECISION_DECIMALS)


def to_event_rows(source_type: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Convert raw Spotify export rows into normalised event dicts for matching."""
    events: list[dict[str, str]] = []

    for idx, row in enumerate(rows, start=1):
        events.append(SourceEvent.from_raw_row(source_type, idx, row).to_dict())

    return events
