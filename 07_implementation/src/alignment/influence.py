"""
BL-003 influence-track injection.

Reads influence controls from the run config and injects user-curated tracks
into the matched-events list, returning a complete influence contract dict.
"""

from __future__ import annotations

from typing import Any

from alignment.constants import (
    DEFAULT_INFLUENCE_PREFERENCE_WEIGHT,
    INTERACTION_COUNT_WEIGHT_SCALE,
    INTERACTION_TYPE_HISTORY_INFLUENCE,
    INTERACTION_TYPE_INFLUENCE,
    MATCH_METHOD_INFLUENCE_DIRECT,
    SOURCE_INFLUENCE,
    format_influence_event_id,
)
from alignment.models import AlignmentBehaviorControls
from alignment.resolved_context import AlignmentResolvedContext
from shared_utils.index_builder import resolve_ds001_id

_DS001_PASSTHROUGH_FIELDS: tuple[str, ...] = (
    "song", "release", "duration_ms", "popularity",
    "danceability", "energy", "key", "mode", "valence", "tempo", "genres", "tags", "lang",
)


def _make_influence_event(
    candidate: dict[str, Any],
    event_id: str,
    infl_weight: float,
) -> dict[str, Any]:
    resolved_ds001_id = resolve_ds001_id(candidate)
    return {
        "event_id": event_id,
        "source_type": SOURCE_INFLUENCE,
        "source_row_index": 0,
        "source_timestamp": "",
        "spotify_track_id": candidate.get("spotify_id", ""),
        "spotify_isrc": "",
        "spotify_track_name": candidate.get("song", ""),
        "spotify_artist_names": candidate.get("artist", ""),
        "match_method": MATCH_METHOD_INFLUENCE_DIRECT,
        "duration_delta_ms": None,
        "ds001_id": resolved_ds001_id,
        "ds001_spotify_id": candidate.get("spotify_id", ""),
        "artist": candidate.get("artist", ""),
        **{f: candidate.get(f, "") for f in _DS001_PASSTHROUGH_FIELDS},
        "preference_weight": infl_weight,
        "interaction_count": max(1, int(round(infl_weight * INTERACTION_COUNT_WEIGHT_SCALE))),
        "interaction_type": INTERACTION_TYPE_INFLUENCE,
    }


def inject_influence_tracks(
    matched_events: list[dict[str, Any]],
    by_ds001_id: dict[str, dict[str, str]],
    run_config_path: str | None = None,
    *,
    context: AlignmentResolvedContext | None = None,
    behavior_controls: AlignmentBehaviorControls | None = None,
) -> dict[str, Any]:
    """
    Inject influence tracks from the run config into matched_events (mutates in place).

    Returns the influence contract dict to embed in the BL-003 summary.
    """
    if context is not None:
        infl = dict(context.behavior_controls.influence_controls)
    elif behavior_controls is not None:
        infl = dict(behavior_controls.influence_controls)
    else:
        infl = {
            "influence_enabled": False,
            "influence_track_ids": [],
            "influence_preference_weight": DEFAULT_INFLUENCE_PREFERENCE_WEIGHT,
        }

    new_injected_count = 0
    relabelled_count = 0
    influence_skipped_ids: list[str] = []

    if infl["influence_enabled"] and infl["influence_track_ids"]:
        infl_weight = float(infl["influence_preference_weight"])
        existing_ds001_ids = {str(e["ds001_id"]) for e in matched_events}
        seen_influence_track_ids: set[str] = set()

        for track_id in infl["influence_track_ids"]:
            track_id = str(track_id).strip()
            if not track_id or track_id in seen_influence_track_ids:
                continue
            seen_influence_track_ids.add(track_id)

            candidate = by_ds001_id.get(track_id)
            if candidate is None:
                influence_skipped_ids.append(track_id)
                continue

            if track_id in existing_ds001_ids:
                for ev in matched_events:
                    if str(ev["ds001_id"]) == track_id:
                        existing_type = str(ev.get("interaction_type", "")).strip().lower()
                        if existing_type and existing_type != INTERACTION_TYPE_INFLUENCE:
                            if "influence" not in existing_type.split(","):
                                ev["interaction_type"] = INTERACTION_TYPE_HISTORY_INFLUENCE
                        else:
                            ev["interaction_type"] = INTERACTION_TYPE_HISTORY_INFLUENCE
                relabelled_count += 1
            else:
                matched_events.append(_make_influence_event(
                    candidate,
                    format_influence_event_id(new_injected_count + 1),
                    infl_weight,
                ))
                existing_ds001_ids.add(track_id)
                new_injected_count += 1

    return {
        "enabled": bool(infl.get("influence_enabled", False)),
        "track_ids": list(infl.get("influence_track_ids") or []),
        "preference_weight": float(
            infl.get("influence_preference_weight") or DEFAULT_INFLUENCE_PREFERENCE_WEIGHT
        ),
        "new_injected_count": new_injected_count,
        "relabelled_count": relabelled_count,
        "skipped_track_ids": influence_skipped_ids,
    }
