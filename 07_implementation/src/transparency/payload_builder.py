"""Payload-building helpers for BL-008 transparency."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping

from shared_utils.coerce import to_mapping
from shared_utils.parsing import safe_float, safe_int

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


def build_ordered_components(active_weights: Mapping[str, object]) -> list[str]:
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
    scored_row: Mapping[str, object],
    ordered_components: list[str],
    active_weights: Mapping[str, object],
) -> list[dict[str, object]]:
    score_breakdown: list[dict[str, object]] = []
    contribution_values: dict[str, float] = {}
    for component in ordered_components:
        canonical = canonical_component_name(component)
        sim_key = f"{canonical}_similarity"
        cont_key = f"{canonical}_contribution"
        similarity = safe_float(scored_row.get(sim_key, 0.0))
        contribution = safe_float(scored_row.get(cont_key, 0.0))
        contribution_values[canonical] = contribution
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

    positive_total = sum(max(value, 0.0) for value in contribution_values.values())
    ranked_components = sorted(
        contribution_values.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    margins_by_component: dict[str, float] = {}
    for index, (component, value) in enumerate(ranked_components):
        if index + 1 >= len(ranked_components):
            margins_by_component[component] = 0.0
            continue
        next_value = ranked_components[index + 1][1]
        margins_by_component[component] = max(value - next_value, 0.0)

    for entry in score_breakdown:
        component = str(entry.get("component", ""))
        contribution = safe_float(entry.get("contribution", 0.0))
        if positive_total > 0.0:
            contribution_share_pct = round((max(contribution, 0.0) / positive_total) * 100.0, 3)
        else:
            contribution_share_pct = 0.0
        entry["contribution_share_pct"] = contribution_share_pct
        entry["margin_vs_next_contributor"] = round(
            margins_by_component.get(component, 0.0),
            6,
        )

    return score_breakdown


def build_track_payload(
    *,
    track_id: str,
    lead_genre: str,
    playlist_position: int,
    score_rank: int,
    final_score: float,
    raw_final_score: float,
    score_breakdown: list[dict[str, object]],
    top_contributors: list[dict[str, object]],
    primary_driver: Mapping[str, object],
    trace_row: Mapping[str, object],
    why_selected: str,
    causal_driver: Mapping[str, object] | None = None,
    narrative_driver: Mapping[str, object] | None = None,
    control_provenance_ref: str = "run_level",
    control_provenance: Mapping[str, object] | None = None,
    assembly_report: Mapping[str, object] | None = None,
) -> dict[str, object]:
    exclusion_reason = str(trace_row.get("exclusion_reason", ""))
    report_root = to_mapping(assembly_report)
    report_config = to_mapping(report_root.get("config"))
    validation_policies = to_mapping(report_config.get("validation_policies"))
    influence_effectiveness = to_mapping(report_root.get("influence_effectiveness_diagnostics"))
    assembly_context = {
        "decision": trace_row.get("decision", "included"),
        "admission_rule": RULE_LABELS.get(exclusion_reason, exclusion_reason),
        "exclusion_reason": exclusion_reason,
        "genre_at_position": lead_genre,
        "influence_requested": bool(trace_row.get("influence_requested", False)),
        "inclusion_path": str(trace_row.get("inclusion_path", "")),
        "source_score_rank": safe_int(trace_row.get("score_rank", score_rank)),
        "policy_mode": report_config.get("influence_policy_mode"),
        "influence_enabled": bool(report_config.get("influence_enabled", False)),
        "influence_reserved_slots": safe_int(report_config.get("influence_reserved_slots", 0)),
        "bl006_bl007_handshake_validation_policy": validation_policies.get(
            "bl006_bl007_handshake_validation_policy"
        ),
        "influence_effectiveness_rate": safe_float(
            influence_effectiveness.get("effectiveness_rate", 0.0)
        ),
    }

    provenance_root = to_mapping(control_provenance)
    scoring_controls = to_mapping(provenance_root.get("scoring"))
    transparency_controls = to_mapping(provenance_root.get("transparency"))

    control_causality = build_control_causality_block(
        assembly_context=assembly_context,
        primary_driver=primary_driver,
        top_contributors=top_contributors,
        score_breakdown=score_breakdown,
        control_provenance=scoring_controls,
        transparency_controls=transparency_controls,
        control_provenance_ref=control_provenance_ref,
    )

    return {
        "playlist_position": playlist_position,
        "track_id": track_id,
        "lead_genre": lead_genre,
        "final_score": round(final_score, 6),
        "raw_final_score": round(raw_final_score, 6),
        "score_rank": score_rank,
        "why_selected": why_selected,
        "primary_explanation_driver": primary_driver,
        "causal_driver": dict(causal_driver or primary_driver),
        "narrative_driver": dict(narrative_driver or primary_driver),
        "top_score_contributors": top_contributors,
        "score_breakdown": score_breakdown,
        "assembly_context": assembly_context,
        "control_provenance_ref": control_provenance_ref,
        "control_provenance": dict(control_provenance or {}),
        "control_causality": control_causality,
    }


def build_control_causality_block(
    *,
    assembly_context: Mapping[str, object],
    primary_driver: Mapping[str, object],
    top_contributors: list[dict[str, object]],
    score_breakdown: list[dict[str, object]],
    control_provenance: Mapping[str, object],
    transparency_controls: Mapping[str, object],
    control_provenance_ref: str,
) -> dict[str, object]:
    top_contribution_value = 0.0
    if top_contributors:
        top_contribution_value = safe_float(
            to_mapping(top_contributors[0]).get("contribution", 0.0),
            0.0,
        )

    decision = str(assembly_context.get("decision", "included"))
    included_in_playlist = decision == "included"
    return {
        "schema_version": "bl008-control-causality-v1",
        "decision_outcome": {
            "decision": decision,
            "included_in_playlist": included_in_playlist,
            "admission_rule": str(assembly_context.get("admission_rule", "")),
            "inclusion_path": str(assembly_context.get("inclusion_path", "")),
            "exclusion_reason": str(assembly_context.get("exclusion_reason", "")),
        },
        "controlling_parameters": {
            "scoring": {
                "active_component_weights": dict(
                    to_mapping(control_provenance.get("active_component_weights"))
                ),
                "lead_genre_strategy": control_provenance.get("lead_genre_strategy"),
                "semantic_overlap_strategy": control_provenance.get("semantic_overlap_strategy"),
                "signal_mode": control_provenance.get("signal_mode"),
            },
            "assembly": {
                "policy_mode": assembly_context.get("policy_mode"),
                "influence_enabled": bool(assembly_context.get("influence_enabled", False)),
                "influence_reserved_slots": safe_int(
                    assembly_context.get("influence_reserved_slots", 0),
                    0,
                ),
                "bl006_bl007_handshake_validation_policy": assembly_context.get(
                    "bl006_bl007_handshake_validation_policy"
                ),
            },
            "transparency": {
                "top_contributor_limit": safe_int(
                    transparency_controls.get("top_contributor_limit", len(top_contributors)),
                    len(top_contributors),
                ),
                "blend_primary_contributor_on_near_tie": bool(
                    transparency_controls.get("blend_primary_contributor_on_near_tie", False)
                ),
                "primary_contributor_tie_delta": safe_float(
                    transparency_controls.get("primary_contributor_tie_delta", 0.0),
                    0.0,
                ),
            },
        },
        "effect_direction": {
            "primary_driver_label": str(primary_driver.get("label", "")),
            "primary_driver_component": str(primary_driver.get("component", "")),
            "primary_driver_contribution": round(top_contribution_value, 6),
            "expected_direction": (
                "promote_or_admit" if included_in_playlist else "deprioritize_or_exclude"
            ),
        },
        "evidence_sources": {
            "trace_fields": [
                "decision",
                "exclusion_reason",
                "influence_requested",
                "inclusion_path",
                "score_rank",
            ],
            "score_breakdown_count": len(score_breakdown),
            "top_contributors_count": len(top_contributors),
            "control_provenance_ref": control_provenance_ref,
        },
    }


def build_rejected_track_payload(
    *,
    track_id: str,
    lead_genre: str,
    score_rank: int,
    final_score: float,
    raw_final_score: float,
    score_breakdown: list[dict[str, object]],
    top_contributors: list[dict[str, object]],
    primary_driver: Mapping[str, object],
    trace_row: Mapping[str, object],
    causal_driver: Mapping[str, object] | None = None,
    narrative_driver: Mapping[str, object] | None = None,
    control_provenance_ref: str = "run_level",
    control_provenance: Mapping[str, object] | None = None,
    assembly_report: Mapping[str, object] | None = None,
) -> dict[str, object]:
    exclusion_reason = str(trace_row.get("exclusion_reason", ""))
    report_root = to_mapping(assembly_report)
    report_config = to_mapping(report_root.get("config"))
    validation_policies = to_mapping(report_config.get("validation_policies"))
    influence_effectiveness = to_mapping(report_root.get("influence_effectiveness_diagnostics"))
    assembly_context = {
        "decision": trace_row.get("decision", "excluded"),
        "admission_rule": RULE_LABELS.get(exclusion_reason, exclusion_reason),
        "exclusion_reason": exclusion_reason,
        "genre_at_position": lead_genre,
        "influence_requested": bool(trace_row.get("influence_requested", False)),
        "inclusion_path": str(trace_row.get("inclusion_path", "")),
        "source_score_rank": safe_int(trace_row.get("score_rank", score_rank)),
        "policy_mode": report_config.get("influence_policy_mode"),
        "influence_enabled": bool(report_config.get("influence_enabled", False)),
        "influence_reserved_slots": safe_int(report_config.get("influence_reserved_slots", 0)),
        "bl006_bl007_handshake_validation_policy": validation_policies.get(
            "bl006_bl007_handshake_validation_policy"
        ),
        "influence_effectiveness_rate": safe_float(
            influence_effectiveness.get("effectiveness_rate", 0.0)
        ),
    }

    provenance_root = to_mapping(control_provenance)
    scoring_controls = to_mapping(provenance_root.get("scoring"))
    transparency_controls = to_mapping(provenance_root.get("transparency"))
    control_causality = build_control_causality_block(
        assembly_context=assembly_context,
        primary_driver=primary_driver,
        top_contributors=top_contributors,
        score_breakdown=score_breakdown,
        control_provenance=scoring_controls,
        transparency_controls=transparency_controls,
        control_provenance_ref=control_provenance_ref,
    )

    return {
        "payload_scope": "rejected_track_trace",
        "track_id": track_id,
        "lead_genre": lead_genre,
        "final_score": round(final_score, 6),
        "raw_final_score": round(raw_final_score, 6),
        "score_rank": score_rank,
        "primary_explanation_driver": primary_driver,
        "causal_driver": dict(causal_driver or primary_driver),
        "narrative_driver": dict(narrative_driver or primary_driver),
        "top_score_contributors": top_contributors,
        "score_breakdown": score_breakdown,
        "assembly_context": assembly_context,
        "control_provenance_ref": control_provenance_ref,
        "control_provenance": dict(control_provenance or {}),
        "control_causality": control_causality,
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
