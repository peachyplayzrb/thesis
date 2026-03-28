"""Payload-building helpers for BL-008 transparency."""

from __future__ import annotations

from collections import Counter

from shared_utils.parsing import safe_float


COMPONENT_LABELS = {
    "tempo": "Tempo (BPM)",
    "duration_ms": "Duration match",
    "key": "Musical key",
    "mode": "Mode (major/minor)",
    "lead_genre": "Lead genre match",
    "genre_overlap": "Genre overlap",
    "tag_overlap": "Tag overlap",
}

COMPONENT_ORDER = [
    "tempo",
    "duration_ms",
    "key",
    "mode",
    "lead_genre",
    "genre_overlap",
    "tag_overlap",
]

RULE_LABELS = {
    "": "Admitted on first evaluation",
    "below_score_threshold": "R1 - score below threshold",
    "genre_cap_exceeded": "R2 - genre cap exceeded",
    "consecutive_genre_run": "R3 - consecutive genre run",
    "length_cap_reached": "R4 - length cap reached",
}


def canonical_component_name(name: str) -> str:
    return name.removesuffix("_score")


def build_ordered_components(active_weights: dict[str, object]) -> list[str]:
    ordered_components: list[str] = []
    active_keys = list(active_weights.keys())
    for canonical in COMPONENT_ORDER:
        for component in active_keys:
            if (
                canonical_component_name(component) == canonical
                and component not in ordered_components
            ):
                ordered_components.append(component)
    ordered_set = set(ordered_components)
    ordered_components.extend(
        sorted(component for component in active_keys if component not in ordered_set)
    )
    return ordered_components


def build_score_breakdown(
    scored_row: dict[str, object],
    ordered_components: list[str],
    active_weights: dict[str, object],
) -> list[dict[str, object]]:
    score_breakdown: list[dict[str, object]] = []
    for component in ordered_components:
        canonical = canonical_component_name(component)
        sim_key = f"{canonical}_similarity"
        cont_key = f"{canonical}_contribution"
        similarity = safe_float(scored_row.get(sim_key, 0.0))
        contribution = safe_float(scored_row.get(cont_key, 0.0))
        score_breakdown.append(
            {
                "component": canonical,
                "label": COMPONENT_LABELS.get(
                    canonical,
                    canonical.replace("_", " ").title(),
                ),
                "weight": round(
                    safe_float(active_weights.get(component, active_weights.get(canonical, 0.0))),
                    6,
                ),
                "similarity": round(similarity, 6),
                "contribution": round(contribution, 6),
            }
        )
    return score_breakdown


def build_track_payload(
    *,
    track_id: str,
    lead_genre: str,
    playlist_position: int,
    score_rank: int,
    final_score: float,
    score_breakdown: list[dict[str, object]],
    top_contributors: list[dict[str, object]],
    primary_driver: dict[str, object],
    trace_row: dict[str, object],
    why_selected: str,
) -> dict[str, object]:
    exclusion_reason = str(trace_row.get("exclusion_reason", ""))
    assembly_context = {
        "decision": trace_row.get("decision", "included"),
        "admission_rule": RULE_LABELS.get(exclusion_reason, exclusion_reason),
        "genre_at_position": lead_genre,
    }
    return {
        "playlist_position": playlist_position,
        "track_id": track_id,
        "lead_genre": lead_genre,
        "final_score": round(final_score, 6),
        "score_rank": score_rank,
        "why_selected": why_selected,
        "primary_explanation_driver": primary_driver,
        "top_score_contributors": top_contributors,
        "score_breakdown": score_breakdown,
        "assembly_context": assembly_context,
    }


def top_contributor_counts(payloads: list[dict[str, object]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for payload in payloads:
        primary = payload.get("primary_explanation_driver") or {}
        if isinstance(primary, dict):
            counts[str(primary.get("label", "Unknown"))] += 1
        else:
            counts["Unknown"] += 1
    return dict(counts)
