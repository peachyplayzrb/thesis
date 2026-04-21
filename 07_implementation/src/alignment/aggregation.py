"""
BL-003 matched-event aggregation.

Collapses the per-event matched list into a per-DS-001-song summary dict
that feeds the seed table CSV.
"""

from __future__ import annotations

from typing import Any

from alignment.constants import (
    MATCH_METHOD_FUZZY_TITLE_ARTIST,
    MATCH_METHOD_INFLUENCE_DIRECT,
    MATCH_METHOD_METADATA_FALLBACK,
    MATCH_METHOD_SPOTIFY_ID_EXACT,
)
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
    if mode == "sum":
        return sum(weights)

    raise ValueError(
        f"Invalid preference_weight_mode: {mode!r}. "
        f"Must be one of: 'sum', 'max', 'mean', 'capped'."
    )


def _clamp_confidence(raw_value: Any) -> float:
    try:
        parsed = float(raw_value)
    except (TypeError, ValueError):
        return 1.0
    return max(0.0, min(1.0, parsed))


def _event_match_confidence(event: MatchedEvent) -> float:
    method = str(event.match_method or "").strip()
    if method in {
        MATCH_METHOD_SPOTIFY_ID_EXACT,
        MATCH_METHOD_METADATA_FALLBACK,
        MATCH_METHOD_INFLUENCE_DIRECT,
    }:
        return 1.0
    if method == MATCH_METHOD_FUZZY_TITLE_ARTIST:
        return _clamp_confidence(event.fuzzy_combined_score)
    return 1.0


def _weighted_mean_confidence(weighted_confidences: list[tuple[float, float]]) -> float:
    if not weighted_confidences:
        return 1.0

    total_weight = 0.0
    weighted_sum = 0.0
    for weight, confidence in weighted_confidences:
        non_negative_weight = max(0.0, weight)
        total_weight += non_negative_weight
        weighted_sum += non_negative_weight * confidence

    if total_weight > 0.0:
        return weighted_sum / total_weight

    return sum(confidence for _, confidence in weighted_confidences) / len(weighted_confidences)


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
    confidence_weights_by_id: dict[str, list[tuple[float, float]]] = {}

    for raw_event in matched_events:
        event = MatchedEvent.from_dict(raw_event)
        ds001_id = event.ds001_id
        agg = aggregated.get(ds001_id)

        if agg is None:
            agg = AggregatedEvent.from_matched_event(event)
            aggregated[ds001_id] = agg
            preference_weights_by_id[ds001_id] = []
            confidence_weights_by_id[ds001_id] = []

        agg.apply_event(event)
        preference_weight = float(event.preference_weight)
        preference_weights_by_id[ds001_id].append(preference_weight)
        confidence_weights_by_id[ds001_id].append(
            (preference_weight, _event_match_confidence(event))
        )

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
        agg.match_confidence_score = round(
            _weighted_mean_confidence(confidence_weights_by_id.get(ds001_id, [])),
            6,
        )

    return {ds001_id: agg.to_dict() for ds001_id, agg in aggregated.items()}
