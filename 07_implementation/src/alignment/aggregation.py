"""
BL-003 matched-event aggregation.

Collapses the per-event matched list into a per-DS-001-song summary dict
that feeds the seed table CSV.
"""

from __future__ import annotations

from typing import Any

from alignment.models import AggregatedEvent, AlignmentBehaviorControls, MatchedEvent


def _apply_preference_weight_policy(
    weights: list[float],
    mode: str,
    cap_per_event: float | None,
) -> float:
    if not weights:
        return 0.0

    if mode == "max":
        return max(weights)
    if mode == "mean":
        return sum(weights) / len(weights)
    if mode == "capped":
        cap = float(cap_per_event) if cap_per_event is not None else None
        if cap is None:
            return sum(weights)
        return sum(min(weight, cap) for weight in weights)
    return sum(weights)


def aggregate_matched_events(
    matched_events: list[dict[str, Any]],
    *,
    behavior_controls: AlignmentBehaviorControls | None = None,
    aggregation_policy: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Aggregate matched events by DS-001 ID.

    Returns a dict keyed by ds001_id where each value contains cumulative
    interaction statistics and set-valued fields (source_types, spotify_track_ids,
    interaction_types) that are serialised to pipe-separated strings at write time.
    """
    if aggregation_policy is not None:
        effective_policy = dict(aggregation_policy)
    elif behavior_controls is not None:
        effective_policy = dict(behavior_controls.aggregation_policy)
    else:
        effective_policy = {}
    preference_weight_mode = str(
        effective_policy.get("preference_weight_mode", "sum")
    ).strip().lower() or "sum"
    preference_weight_cap_per_event = effective_policy.get("preference_weight_cap_per_event")

    aggregated: dict[str, AggregatedEvent] = {}
    preference_weights_by_id: dict[str, list[float]] = {}

    for raw_event in matched_events:
        event = MatchedEvent.from_dict(raw_event)
        ds001_id = event.ds001_id
        agg = aggregated.get(ds001_id)

        if agg is None:
            agg = AggregatedEvent.from_matched_event(event)
            aggregated[ds001_id] = agg
            preference_weights_by_id[ds001_id] = []

        agg.apply_event(event)
        preference_weights_by_id.setdefault(ds001_id, []).append(float(event.preference_weight))

    for ds001_id, agg in aggregated.items():
        agg.preference_weight_sum = round(
            _apply_preference_weight_policy(
            preference_weights_by_id.get(ds001_id, []),
            preference_weight_mode,
            (
                float(preference_weight_cap_per_event)
                if preference_weight_cap_per_event is not None
                else None
            ),
            ),
            6,
        )

    return {ds001_id: agg.to_dict() for ds001_id, agg in aggregated.items()}
