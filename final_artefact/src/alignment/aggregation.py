"""
BL-003 matched-event aggregation.

Collapses the per-event matched list into a per-DS-001-song summary dict
that feeds the seed table CSV.
"""

from __future__ import annotations

from typing import Any


def aggregate_matched_events(
    matched_events: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Aggregate matched events by DS-001 ID.

    Returns a dict keyed by ds001_id where each value contains cumulative
    interaction statistics and set-valued fields (source_types, spotify_track_ids,
    interaction_types) that are serialised to pipe-separated strings at write time.
    """
    aggregated: dict[str, dict[str, Any]] = {}

    for event in matched_events:
        ds001_id = str(event["ds001_id"])
        agg = aggregated.get(ds001_id)

        if agg is None:
            agg = {
                "ds001_id": ds001_id,
                "spotify_id": event["ds001_spotify_id"],
                "song": event["song"],
                "artist": event["artist"],
                "release": event["release"],
                "duration_ms": event["duration_ms"],
                "popularity": event["popularity"],
                "danceability": event["danceability"],
                "energy": event["energy"],
                "key": event["key"],
                "mode": event["mode"],
                "valence": event["valence"],
                "tempo": event["tempo"],
                "genres": event["genres"],
                "tags": event["tags"],
                "lang": event["lang"],
                "matched_event_count": 0,
                "interaction_count_sum": 0,
                "preference_weight_sum": 0.0,
                "preference_weight_max": 0.0,
                "source_types": set(),
                "interaction_types": set(),
                "spotify_track_ids": set(),
            }
            aggregated[ds001_id] = agg

        agg["matched_event_count"] += 1
        agg["interaction_count_sum"] += int(event["interaction_count"])
        agg["preference_weight_sum"] += float(event["preference_weight"])
        agg["preference_weight_max"] = max(
            float(agg["preference_weight_max"]), float(event["preference_weight"])
        )
        agg["source_types"].add(str(event["source_type"]))
        if event["spotify_track_id"]:
            agg["spotify_track_ids"].add(str(event["spotify_track_id"]))
        for itype in str(event.get("interaction_type", "history")).split(","):
            itype = itype.strip()
            if itype:
                agg["interaction_types"].add(itype)

    return aggregated
