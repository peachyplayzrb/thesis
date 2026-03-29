"""
BL-003 influence-track injection.

Reads influence controls from the run config and injects user-curated tracks
into the matched-events list, returning a complete influence contract dict.
"""

from __future__ import annotations

from typing import Any

from shared_utils.config_loader import load_run_config_utils_module
from alignment.resolved_context import AlignmentResolvedContext


def inject_influence_tracks(
    matched_events: list[dict[str, Any]],
    by_ds001_id: dict[str, dict[str, str]],
    run_config_path: str | None = None,
    *,
    context: AlignmentResolvedContext | None = None,
) -> dict[str, Any]:
    """
    Inject influence tracks from the run config into matched_events (mutates in place).

    Returns the influence contract dict to embed in the BL-003 summary.
    When run_config_path is None, returns a disabled contract with zero counts.
    """
    if context is not None:
        infl = dict(context.influence_controls)
    elif run_config_path:
        _rc_utils = load_run_config_utils_module()
        infl = _rc_utils.resolve_bl003_influence_controls(run_config_path)
    else:
        return {
            "enabled": False,
            "track_ids": [],
            "preference_weight": 1.0,
            "injected_count": 0,
            "skipped_track_ids": [],
        }

    influence_injected_count = 0
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
                        ev["interaction_type"] = "history,influence"
            else:
                infl_event: dict[str, Any] = {
                    "event_id": f"ds001_influence_{influence_injected_count + 1:06d}",
                    "source_type": "influence",
                    "source_row_index": 0,
                    "source_timestamp": "",
                    "spotify_track_id": candidate.get("spotify_id", ""),
                    "spotify_isrc": "",
                    "spotify_track_name": candidate.get("song", ""),
                    "spotify_artist_names": candidate.get("artist", ""),
                    "match_method": "influence_direct",
                    "duration_delta_ms": None,
                    "ds001_id": candidate.get("id", ""),
                    "ds001_spotify_id": candidate.get("spotify_id", ""),
                    "artist": candidate.get("artist", ""),
                    "song": candidate.get("song", ""),
                    "release": candidate.get("release", ""),
                    "duration_ms": candidate.get("duration_ms", ""),
                    "popularity": candidate.get("popularity", ""),
                    "danceability": candidate.get("danceability", ""),
                    "energy": candidate.get("energy", ""),
                    "key": candidate.get("key", ""),
                    "mode": candidate.get("mode", ""),
                    "valence": candidate.get("valence", ""),
                    "tempo": candidate.get("tempo", ""),
                    "genres": candidate.get("genres", ""),
                    "tags": candidate.get("tags", ""),
                    "lang": candidate.get("lang", ""),
                    "preference_weight": infl_weight,
                    "interaction_count": max(1, int(round(infl_weight * 10))),
                    "interaction_type": "influence",
                }
                matched_events.append(infl_event)
                existing_ds001_ids.add(track_id)

            influence_injected_count += 1

    return {
        "enabled": bool(infl.get("influence_enabled", False)),
        "track_ids": list(infl.get("influence_track_ids") or []),
        "preference_weight": float(infl.get("influence_preference_weight") or 1.0),
        "injected_count": influence_injected_count,
        "skipped_track_ids": influence_skipped_ids,
    }
