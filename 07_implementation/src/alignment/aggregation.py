"""
BL-003 matched-event aggregation.

Collapses the per-event matched list into a per-DS-001-song summary dict
that feeds the seed table CSV.
"""

from __future__ import annotations

from typing import Any

from alignment.models import AggregatedEvent, MatchedEvent


def aggregate_matched_events(
    matched_events: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Aggregate matched events by DS-001 ID.

    Returns a dict keyed by ds001_id where each value contains cumulative
    interaction statistics and set-valued fields (source_types, spotify_track_ids,
    interaction_types) that are serialised to pipe-separated strings at write time.
    """
    aggregated: dict[str, AggregatedEvent] = {}

    for raw_event in matched_events:
        event = MatchedEvent.from_dict(raw_event)
        ds001_id = event.ds001_id
        agg = aggregated.get(ds001_id)

        if agg is None:
            agg = AggregatedEvent.from_matched_event(event)
            aggregated[ds001_id] = agg

        agg.apply_event(event)

    return {ds001_id: agg.to_dict() for ds001_id, agg in aggregated.items()}
