from __future__ import annotations

import csv
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from observability.input_validation import validate_bl008_bl009_handshake
from observability.runtime_controls import resolve_bl009_runtime_controls
from run_config.control_registry import build_control_registry_snapshot
from shared_utils.artifact_registry import bl009_required_paths
from shared_utils.coerce import to_mapping, to_string_list
from shared_utils.hashing import sha256_of_values
from shared_utils.io_utils import (
    load_csv_rows,
    open_text_write,
    sha256_of_file,
    utc_now,
)
from shared_utils.parsing import safe_float, safe_int
from shared_utils.path_utils import impl_root
from shared_utils.stage_utils import (
    ensure_paths_exist,
    ensure_required_keys,
    load_required_json_object,
    relpath,
    safe_relpath,
)

BL009_OBSERVABILITY_SCHEMA_VERSION = "bl009-observability-v1"


def _object_mapping(value: object) -> dict[str, object]:
    return to_mapping(value)


def _optional_str(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None


def build_signal_mode_calibration_summary(
    bl005_diagnostics: dict[str, object],
    bl006_summary: dict[str, object],
) -> dict[str, object]:
    retrieval_config = to_mapping(bl005_diagnostics.get("config"))
    scoring_config = to_mapping(bl006_summary.get("config"))
    signal_mode = to_mapping(retrieval_config.get("signal_mode") or scoring_config.get("signal_mode"))
    popularity_profile = to_mapping(signal_mode.get("popularity_profile"))
    component_weights = to_mapping(scoring_config.get("base_component_weights"))
    numeric_thresholds = to_mapping(retrieval_config.get("numeric_thresholds"))

    return {
        "mode_name": signal_mode.get("name"),
        "semantic_profile": signal_mode.get("semantic_profile"),
        "numeric_profile": signal_mode.get("numeric_profile"),
        "retrieval": {
            "use_weighted_semantics": bool(retrieval_config.get("use_weighted_semantics", False)),
            "use_continuous_numeric": bool(retrieval_config.get("use_continuous_numeric", False)),
            "numeric_support_min_score": safe_float(retrieval_config.get("numeric_support_min_score"), 0.0),
            "popularity_numeric_enabled": bool(popularity_profile.get("retrieval_enabled", False)),
            "numeric_feature_count": len(numeric_thresholds),
        },
        "scoring": {
            "popularity_weight": safe_float(component_weights.get("popularity"), 0.0),
            "popularity_scoring_enabled": bool(popularity_profile.get("scoring_enabled", False)),
        },
    }


def first_items(values: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    return values[:limit]


def parse_exclusion_samples(rows: list[dict[str, str]], field: str, limit: int) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        key = row.get(field, "")
        if not key:
            continue
        grouped.setdefault(key, [])
        if len(grouped[key]) >= limit:
            continue
        grouped[key].append(row)
    return grouped


def build_source_resilience_diagnostics(bl003_summary: dict[str, object]) -> dict[str, object]:
    inputs = _object_mapping(bl003_summary.get("inputs"))
    source_stats = _object_mapping(bl003_summary.get("source_stats"))

    expected_sources = {
        str(key): bool(value)
        for key, value in _object_mapping(inputs.get("selected_sources_expected")).items()
    }
    available_sources = {
        str(key): bool(value)
        for key, value in _object_mapping(inputs.get("selected_sources_available")).items()
    }
    source_resilience_policy = {
        str(key): str(value)
        for key, value in _object_mapping(inputs.get("source_resilience_policy")).items()
    }

    missing_selected_sources = set(
        to_string_list(inputs.get("missing_selected_sources"), allow_tuple=True, drop_empty=True)
    )
    missing_required_sources = set(
        to_string_list(inputs.get("missing_required_sources"), allow_tuple=True, drop_empty=True)
    )
    degraded_optional_sources = set(
        to_string_list(inputs.get("degraded_optional_sources"), allow_tuple=True, drop_empty=True)
    )

    source_decisions: dict[str, dict[str, object]] = {}
    for source in sorted(set(expected_sources) | set(source_stats)):
        source_stat = _object_mapping(source_stats.get(source))
        expected = bool(expected_sources.get(source, False))
        available = bool(available_sources.get(source, False))
        selected = expected

        if source in missing_required_sources:
            reason_code = "missing_required"
        elif source in degraded_optional_sources:
            reason_code = "degraded_optional"
        elif source in missing_selected_sources:
            reason_code = "missing_selected"
        elif selected and available:
            reason_code = "selected_and_available"
        elif not selected:
            reason_code = "not_selected"
        else:
            reason_code = "unknown"

        source_decisions[source] = {
            "selected": selected,
            "expected": expected,
            "available": available,
            "resilience_policy": source_resilience_policy.get(source),
            "export_outcome_status": source_stat.get("export_outcome_status"),
            "degraded_missing": bool(source_stat.get("degraded_missing", False)),
            "missing_required": bool(source_stat.get("missing_required", False)),
            "reason_code": reason_code,
        }

    return {
        "expected_sources": expected_sources,
        "available_sources": available_sources,
        "source_resilience_policy": source_resilience_policy,
        "missing_selected_sources": sorted(missing_selected_sources),
        "missing_required_sources": sorted(missing_required_sources),
        "degraded_optional_sources": sorted(degraded_optional_sources),
        "source_decisions": source_decisions,
    }


def summarize_control_causality(explanations: list[dict[str, object]]) -> dict[str, object]:
    required_top_keys = [
        "schema_version",
        "decision_outcome",
        "controlling_parameters",
        "effect_direction",
        "evidence_sources",
    ]
    missing_top_key_counts = {key: 0 for key in required_top_keys}
    missing_tracks: list[str] = []
    schema_versions: dict[str, int] = {}

    for explanation in explanations:
        track_id = str(explanation.get("track_id", ""))
        control_causality_raw = explanation.get("control_causality")
        control_causality = to_mapping(control_causality_raw)

        if not control_causality:
            missing_tracks.append(track_id)
            for key in required_top_keys:
                missing_top_key_counts[key] += 1
            continue

        schema_version = str(control_causality.get("schema_version", ""))
        schema_versions[schema_version] = schema_versions.get(schema_version, 0) + 1
        for key in required_top_keys:
            if key not in control_causality:
                missing_top_key_counts[key] += 1

    tracks_total = len(explanations)
    tracks_with_control_causality = max(0, tracks_total - len(missing_tracks))
    tracks_missing_required_keys = max(missing_top_key_counts.values()) if missing_top_key_counts else 0
    return {
        "required_keys": required_top_keys,
        "schema_versions": schema_versions,
        "tracks_total": tracks_total,
        "tracks_with_control_causality": tracks_with_control_causality,
        "tracks_missing_control_causality": len(missing_tracks),
        "tracks_missing_required_keys": tracks_missing_required_keys,
        "missing_top_key_counts": missing_top_key_counts,
        "sample_missing_track_ids": missing_tracks[:5],
    }


def ensure_required_sections(run_log: dict) -> None:
    required_keys = [
        "run_metadata",
        "execution_scope_summary",
        "run_config",
        "ingestion_alignment_diagnostics",
        "stage_diagnostics",
        "exclusion_diagnostics",
        "validity_boundaries",
        "output_artifacts",
    ]
    missing = [key for key in required_keys if key not in run_log]
    if missing:
        raise RuntimeError(f"BL-009 run log missing required sections: {missing}")


def resolve_canonical_config_artifacts(
    runtime_controls: dict[str, object],
    root: Path,
) -> dict[str, dict[str, object]]:
    canonical_config_artifacts: dict[str, dict[str, object]] = {}
    for alias, env_key in [
        ("run_intent", "run_intent_path"),
        ("run_effective_config", "run_effective_config_path"),
    ]:
        raw_path = runtime_controls.get(env_key)
        if not raw_path:
            canonical_config_artifacts[alias] = {
                "path": None,
                "available": False,
                "sha256": None,
            }
            continue
        candidate_path = Path(str(raw_path))
        if not candidate_path.is_absolute():
            candidate_path = (root / candidate_path).resolve()
        available = candidate_path.exists()
        canonical_config_artifacts[alias] = {
            "path": safe_relpath(candidate_path, root),
            "available": available,
            "sha256": sha256_of_file(candidate_path) if available else None,
        }
    return canonical_config_artifacts


def build_artifact_maps(
    paths: dict[str, Path],
    root: Path,
    script_keys: set[str],
) -> tuple[dict[str, str], dict[str, int]]:
    artifact_hashes = {
        relpath(path, root): sha256_of_file(path)
        for key, path in paths.items()
        if key not in script_keys and path.exists()
    }
    artifact_sizes = {
        relpath(path, root): path.stat().st_size
        for key, path in paths.items()
        if key not in script_keys and path.exists()
    }
    return artifact_hashes, artifact_sizes


def build_retrieval_fidelity_summary(bl005_diagnostics: dict[str, object]) -> dict[str, object]:
    counts = to_mapping(bl005_diagnostics.get("counts"))
    candidate_fidelity = to_mapping(bl005_diagnostics.get("candidate_shaping_fidelity"))
    pool_progression = to_mapping(candidate_fidelity.get("pool_progression"))
    exclusion_categories = to_mapping(candidate_fidelity.get("exclusion_categories"))
    control_effects = to_mapping(candidate_fidelity.get("control_effect_observability"))
    rejection_driver_contribution = to_mapping(candidate_fidelity.get("rejection_driver_contribution"))
    threshold_effects = to_mapping(candidate_fidelity.get("threshold_effects"))
    threshold_attribution = to_mapping(threshold_effects.get("threshold_attribution"))
    directional_impact_summary = to_mapping(threshold_effects.get("directional_impact_summary"))

    top_failure_features_raw = threshold_attribution.get("top_failure_features")
    top_failure_features = (
        list(top_failure_features_raw)
        if isinstance(top_failure_features_raw, list)
        else []
    )
    ranked_rejection_drivers_raw = rejection_driver_contribution.get("ranked_rejection_drivers")
    ranked_rejection_drivers = (
        list(ranked_rejection_drivers_raw)
        if isinstance(ranked_rejection_drivers_raw, list)
        else []
    )

    return {
        "run_id": bl005_diagnostics.get("run_id"),
        "pool_progression": {
            "candidate_rows_total": safe_int(counts.get("candidate_rows_total"), 0),
            "post_seed_exclusion_pool": safe_int(pool_progression.get("post_seed_exclusion_pool"), 0),
            "post_language_filter_pool": safe_int(pool_progression.get("post_language_filter_pool"), 0),
            "post_recency_gate_pool": safe_int(pool_progression.get("post_recency_gate_pool"), 0),
            "kept_candidates": safe_int(counts.get("kept_candidates"), 0),
            "rejected_non_seed_candidates": safe_int(counts.get("rejected_non_seed_candidates"), 0),
        },
        "exclusion_categories": exclusion_categories,
        "control_effect_observability": control_effects,
        "rejection_driver_contribution": {
            "dominant_rejection_driver": str(
                rejection_driver_contribution.get("dominant_rejection_driver", "")
            ),
            "dominant_rejection_driver_share_of_total_rejections": safe_float(
                rejection_driver_contribution.get(
                    "dominant_rejection_driver_share_of_total_rejections", 0.0
                ),
                0.0,
            ),
            "ranked_rejection_drivers": ranked_rejection_drivers[:5],
        },
        "threshold_directional_impact": directional_impact_summary,
        "top_threshold_failure_features": top_failure_features[:5],
    }


def build_playlist_tradeoff_summary(bl007_report: dict[str, object]) -> dict[str, object]:
    tradeoff_raw = bl007_report.get("tradeoff_metrics_summary")
    tradeoff = to_mapping(tradeoff_raw)
    diversity = to_mapping(tradeoff.get("diversity_distribution_summary"))
    novelty = to_mapping(tradeoff.get("novelty_distance_summary"))
    ordering = to_mapping(tradeoff.get("ordering_pressure_summary"))
    return {
        "run_id": bl007_report.get("run_id"),
        "playlist_size": safe_int(tradeoff.get("playlist_size"), 0),
        "diversity_distribution_summary": {
            "unique_genre_count": safe_int(diversity.get("unique_genre_count"), 0),
            "dominant_genre_share": safe_float(diversity.get("dominant_genre_share"), 0.0),
            "normalized_genre_entropy": safe_float(diversity.get("normalized_genre_entropy"), 0.0),
            "genre_switch_rate": safe_float(diversity.get("genre_switch_rate"), 0.0),
        },
        "novelty_distance_summary": {
            "transition_pair_count": safe_int(novelty.get("transition_pair_count"), 0),
            "mean_adjacent_transition_distance": safe_float(
                novelty.get("mean_adjacent_transition_distance"),
                0.0,
            ),
            "max_adjacent_transition_distance": safe_float(
                novelty.get("max_adjacent_transition_distance"),
                0.0,
            ),
        },
        "ordering_pressure_summary": {
            "mean_selected_rank": safe_float(ordering.get("mean_selected_rank"), 0.0),
            "median_selected_rank": safe_int(ordering.get("median_selected_rank"), 0),
            "selected_rank_span": safe_int(ordering.get("selected_rank_span"), 0),
            "top_100_exclusion_rate": safe_float(ordering.get("top_100_exclusion_rate"), 0.0),
            "dominant_top_100_exclusion_reason": str(
                ordering.get("dominant_top_100_exclusion_reason") or ""
            ),
        },
    }


def build_cross_stage_influence_attribution_summary(
    *,
    profile: dict[str, object],
    bl005_diagnostics: dict[str, object],
    bl006_summary: dict[str, object],
    bl007_report: dict[str, object],
    control_causality_summary: dict[str, object],
    influence_track_diagnostics: list[dict[str, object]],
) -> dict[str, object]:
    interaction_attribution = to_mapping(profile.get("interaction_attribution"))
    contribution_by_type = to_mapping(interaction_attribution.get("contribution_by_type"))
    influence_contribution = to_mapping(contribution_by_type.get("influence"))
    history_contribution = to_mapping(contribution_by_type.get("history"))

    candidate_fidelity = to_mapping(bl005_diagnostics.get("candidate_shaping_fidelity"))
    threshold_effects = to_mapping(candidate_fidelity.get("threshold_effects"))
    directional_impact = to_mapping(threshold_effects.get("directional_impact_summary"))
    bounded_what_if = to_mapping(bl005_diagnostics.get("bounded_what_if_estimates"))
    per_family = to_mapping(bounded_what_if.get("per_control_family_scenarios"))
    language_family = to_mapping(per_family.get("language_filter"))

    scoring_counts = to_mapping(bl006_summary.get("counts"))
    scoring_statistics = to_mapping(bl006_summary.get("score_statistics"))

    assembly_config = to_mapping(bl007_report.get("config"))
    influence_effectiveness = to_mapping(bl007_report.get("influence_effectiveness_diagnostics"))
    requested_count = len(influence_track_diagnostics)
    included_count = sum(
        1
        for row in influence_track_diagnostics
        if bool(to_mapping(row).get("included_in_playlist", False))
    )

    causality_missing = safe_int(control_causality_summary.get("tracks_missing_control_causality"), 0)
    causality_total = safe_int(control_causality_summary.get("tracks_total"), 0)
    causality_coverage = round((1.0 - (causality_missing / causality_total)), 6) if causality_total > 0 else 0.0

    return {
        "schema_version": "cross-stage-influence-attribution-v1",
        "stage_chain": ["BL-004", "BL-005", "BL-006", "BL-007", "BL-009"],
        "bl004_profile_influence": {
            "interaction_attribution_mode": str(interaction_attribution.get("policy_name", "")),
            "filtered_types_requested": to_string_list(
                interaction_attribution.get("filtered_types_requested"),
                allow_tuple=True,
                drop_empty=True,
            ),
            "influence_row_share": safe_float(influence_contribution.get("row_share"), 0.0),
            "influence_effective_weight": safe_float(influence_contribution.get("effective_weight"), 0.0),
            "history_row_share": safe_float(history_contribution.get("row_share"), 0.0),
        },
        "bl005_retrieval_effects": {
            "dominant_direction": str(directional_impact.get("dominant_direction", "")),
            "language_filter_rejection_share": safe_float(
                to_mapping(candidate_fidelity.get("control_effect_observability")).get("language_filter_rejection_share"),
                0.0,
            ),
            "language_filter_disabled_delta_vs_base": safe_int(language_family.get("delta_vs_base"), 0),
        },
        "bl006_scoring_context": {
            "candidate_count": safe_int(scoring_counts.get("candidate_count"), 0),
            "scored_rows": safe_int(scoring_counts.get("scored_rows"), 0),
            "influence_contract_source": str(bl006_summary.get("influence_contract_source", "")),
            "mean_final_score": safe_float(scoring_statistics.get("mean_final_score"), 0.0),
            "mean_raw_final_score": safe_float(scoring_statistics.get("mean_raw_final_score"), 0.0),
        },
        "bl007_assembly_effects": {
            "influence_enabled": bool(assembly_config.get("influence_enabled", False)),
            "influence_policy_mode": str(assembly_config.get("influence_policy_mode", "")),
            "influence_reserved_slots": safe_int(assembly_config.get("influence_reserved_slots"), 0),
            "requested_influence_tracks": requested_count,
            "included_influence_tracks": included_count,
            "influence_effectiveness_rate": safe_float(influence_effectiveness.get("effectiveness_rate"), 0.0),
        },
        "bl009_explanation_linkage": {
            "control_causality_coverage": causality_coverage,
            "tracks_with_control_causality": safe_int(
                control_causality_summary.get("tracks_with_control_causality"),
                0,
            ),
            "tracks_missing_control_causality": causality_missing,
        },
        "notes": (
            "Bounded cross-stage attribution summary linking profile influence inputs, retrieval diagnostics, "
            "scoring context, assembly outcomes, and BL-009 causality coverage. "
            "This is an additive observability surface, not full causal proof."
        ),
    }


def build_feature_availability_summary(
    bl004_profile: dict[str, object],
    bl006_summary: dict[str, object],
) -> dict[str, object]:
    profile_summary = to_mapping(bl004_profile.get("feature_availability_summary"))
    scoring_summary = to_mapping(bl006_summary.get("feature_availability_summary"))

    profile_missing_ratio = safe_float(profile_summary.get("missing_numeric_track_ratio"), 0.0)
    candidate_no_numeric_ratio = safe_float(
        scoring_summary.get("rows_with_no_numeric_features"),
        0.0,
    ) / max(1, safe_int(scoring_summary.get("candidate_count"), 0))
    candidate_no_semantic_ratio = safe_float(
        scoring_summary.get("rows_with_no_semantic_signal"),
        0.0,
    ) / max(1, safe_int(scoring_summary.get("candidate_count"), 0))

    return {
        "profile": {
            "matched_seed_count": safe_int(profile_summary.get("matched_seed_count"), 0),
            "missing_numeric_track_count": safe_int(
                profile_summary.get("missing_numeric_track_count"),
                0,
            ),
            "missing_numeric_track_ratio": profile_missing_ratio,
            "no_numeric_signal_row_count": safe_int(
                profile_summary.get("no_numeric_signal_row_count"),
                0,
            ),
            "malformed_numeric_row_count": safe_int(
                profile_summary.get("malformed_numeric_row_count"),
                0,
            ),
            "numeric_feature_coverage_by_feature": to_mapping(
                profile_summary.get("numeric_feature_coverage_by_feature")
            ),
        },
        "candidates": {
            "candidate_count": safe_int(scoring_summary.get("candidate_count"), 0),
            "rows_with_all_numeric_features": safe_int(
                scoring_summary.get("rows_with_all_numeric_features"),
                0,
            ),
            "rows_with_no_numeric_features": safe_int(
                scoring_summary.get("rows_with_no_numeric_features"),
                0,
            ),
            "rows_with_no_semantic_signal": safe_int(
                scoring_summary.get("rows_with_no_semantic_signal"),
                0,
            ),
            "numeric_feature_coverage_by_feature": to_mapping(
                scoring_summary.get("numeric_feature_coverage_by_feature")
            ),
            "lead_genre_source_counts": to_mapping(
                scoring_summary.get("lead_genre_source_counts")
            ),
        },
        "boundary_indicators": {
            "profile_numeric_missingness": profile_missing_ratio,
            "candidate_no_numeric_ratio": round(candidate_no_numeric_ratio, 6),
            "candidate_no_semantic_ratio": round(candidate_no_semantic_ratio, 6),
            "status": (
                "bounded-risk"
                if profile_missing_ratio > 0.25
                or candidate_no_numeric_ratio > 0.25
                or candidate_no_semantic_ratio > 0.25
                else "within-expected-bounds"
            ),
        },
    }


def build_reproducibility_interpretation() -> dict[str, object]:
    """Return an explicit reproducibility scope framing for BL-009 validity_boundaries."""
    return {
        "verdict_basis": (
            "Reproducibility verdicts (BL-010) reflect artifact-level stable-hash consistency "
            "under fixed inputs and a pinned configuration snapshot. "
            "Stable-hash comparison excludes volatile run-metadata fields by design."
        ),
        "non_claims": [
            "cross-environment or cross-OS behavioral invariance",
            "behavioral invariance under different run-config values",
            "multi-user or population-level generalizability",
            "temporal stability beyond the pinned configuration window",
        ],
        "schema_version": "reproducibility-interpretation-v1",
    }


def _resolve_interaction_types_included(input_scope: dict[str, object]) -> list[str]:
    interaction_types_included: list[str] = []
    if input_scope.get("include_top_tracks"):
        interaction_types_included.append("top_tracks")
    if input_scope.get("include_saved_tracks"):
        interaction_types_included.append("saved_tracks")
    if input_scope.get("include_playlists"):
        interaction_types_included.append("playlists")
    if input_scope.get("include_recently_played"):
        interaction_types_included.append("recently_played")
    return interaction_types_included


def _validate_and_prepare_bl008_handshake(
    *,
    bl008_summary: dict[str, object],
    bl008_payloads: dict[str, object],
    policy: str,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]], dict[str, object], dict[str, object]]:
    handshake_validation = validate_bl008_bl009_handshake(
        bl008_summary=bl008_summary,
        bl008_payloads=bl008_payloads,
        policy=policy,
    )
    if handshake_validation["status"] == "fail":
        violations_obj = handshake_validation.get("control_constraint_violations")
        violations = list(violations_obj) if isinstance(violations_obj, list) else []
        raise RuntimeError(
            "BL-008↔BL-009 handshake validation failed: "
            + "; ".join(str(item) for item in violations)
        )
    if handshake_validation["status"] in {"warn", "allow"}:
        logging.getLogger(__name__).warning(
            "BL-008↔BL-009 handshake validation status=%s policy=%s sampled=%s",
            handshake_validation["status"],
            handshake_validation["policy"],
            handshake_validation.get("sampled_violations", []),
        )

    explanations_obj = bl008_payloads.get("explanations")
    explanations = [
        to_mapping(item)
        for item in (explanations_obj if isinstance(explanations_obj, list) else [])
        if isinstance(item, dict)
    ]
    rejected_causality_obj = bl008_payloads.get("rejected_track_control_causality")
    rejected_causality = [
        to_mapping(item)
        for item in (rejected_causality_obj if isinstance(rejected_causality_obj, list) else [])
        if isinstance(item, dict)
    ]
    control_causality_summary = summarize_control_causality(explanations)
    rejected_control_causality_summary = summarize_control_causality(rejected_causality)
    return (
        handshake_validation,
        explanations,
        rejected_causality,
        control_causality_summary,
        rejected_control_causality_summary,
    )


def _build_influence_track_diagnostics(
    *,
    requested_influence_track_ids: list[str],
    trace_by_track_id: dict[str, dict[str, str]],
    scored_track_ids: set[str],
    playlist_position_by_track_id: dict[str, int],
) -> list[dict[str, Any]]:
    influence_track_diagnostics: list[dict[str, Any]] = []
    for track_id in requested_influence_track_ids:
        row = trace_by_track_id.get(track_id, {})
        included = track_id in playlist_position_by_track_id
        inclusion_path = row.get("inclusion_path")
        exclusion_reason = row.get("exclusion_reason", "")
        influence_track_diagnostics.append(
            {
                "track_id": track_id,
                "scored": track_id in scored_track_ids,
                "included_in_playlist": included,
                "playlist_position": playlist_position_by_track_id.get(track_id) if included else None,
                "inclusion_path": inclusion_path or ("competitive" if included else ""),
                "exclusion_reason": "" if included else exclusion_reason,
            }
        )
    return influence_track_diagnostics


def _build_run_log(
    *,
    run_id: str,
    generated_at_utc: str,
    bootstrap_mode: bool,
    dataset_version: str,
    dataset_version_source: str,
    pipeline_version: str,
    dataset_component_hashes: dict[str, str],
    script_hashes: dict[str, str],
    runtime_controls: dict[str, Any],
    signal_mode: dict[str, Any],
    signal_mode_calibration: dict[str, Any],
    control_mode: dict[str, Any],
    input_scope: dict[str, Any],
    diagnostic_sample_limit: int,
    bl008_bl009_handshake_validation_policy: str,
    canonical_config_artifacts: dict[str, Any],
    profile: dict[str, Any],
    bl004_summary: dict[str, Any],
    bl005_diagnostics: dict[str, Any],
    bl006_summary: dict[str, Any],
    bl007_report: dict[str, Any],
    playlist: dict[str, Any],
    bl008_summary: dict[str, Any],
    bl008_payloads: dict[str, Any],
    rejected_causality: list[dict[str, Any]],
    handshake_validation: dict[str, Any],
    paths: dict[str, Path],
    root: Path,
    bl003_counts: dict[str, Any],
    bl003_match_by_fuzzy: int,
    bl003_match_total: int,
    bl003_fuzzy_controls: dict[str, Any],
    source_resilience_diagnostics: dict[str, Any],
    interaction_types_included: list[str],
    history_track_count: int,
    influence_tracks_included: bool,
    influence_track_count: int,
    control_causality_summary: dict[str, Any],
    rejected_control_causality_summary: dict[str, Any],
    influence_track_diagnostics: list[dict[str, Any]],
    retrieval_samples: list[dict[str, Any]],
    first_length_cap: dict[str, str] | None,
    assembly_rule_samples: dict[str, list[dict[str, Any]]],
    artifact_hashes: dict[str, str],
    artifact_sizes: dict[str, int],
) -> dict[str, Any]:
    playlist_relpath = relpath(paths["bl007_playlist"], root)
    run_effective_sha = _optional_str(to_mapping(canonical_config_artifacts.get("run_effective_config")).get("sha256"))
    run_intent_sha = _optional_str(to_mapping(canonical_config_artifacts.get("run_intent")).get("sha256"))
    run_config_payload_sha256 = run_effective_sha or run_intent_sha
    scored_candidates_sha256 = dataset_component_hashes.get("scoring/outputs/bl006_scored_candidates.csv")
    seed_trace_sha256 = dataset_component_hashes.get("profile/outputs/bl004_seed_trace.csv")
    playlist_artifact_sha256 = artifact_hashes.get(playlist_relpath)
    output_hash_aliases = _build_output_hash_aliases(
        playlist_artifact_sha256=playlist_artifact_sha256,
        run_config_payload_sha256=run_config_payload_sha256,
        scored_candidates_sha256=scored_candidates_sha256,
        seed_trace_sha256=seed_trace_sha256,
    )

    return {
        # Additive top-level compatibility aliases for existing tooling snippets.
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "pipeline_version": pipeline_version,
        "dataset_component_hashes": dataset_component_hashes,
        "output_hashes": {
            "semantics_note": (
                "Compatibility aliases; playlist_track_ids_sha256 is retained for legacy snippets "
                "and equals the playlist artifact SHA-256."
            ),
            **output_hash_aliases,
        },
        "run_metadata": {
            "run_id": run_id,
            "task": "BL-009",
            "generated_at_utc": generated_at_utc,
            "elapsed_seconds": None,
            "observability_schema_version": BL009_OBSERVABILITY_SCHEMA_VERSION,
            "observability_scope": "artifact-level deterministic audit log",
            "bootstrap_mode": bootstrap_mode,
            "dataset_version": dataset_version,
            "dataset_version_source": dataset_version_source,
            "pipeline_version": pipeline_version,
            "dataset_component_hashes": dataset_component_hashes,
            "pipeline_script_hashes": script_hashes,
            "optional_dependency_availability": {},
            "upstream_stage_run_ids": {
                "BL-004": profile["run_id"],
                "BL-005": bl005_diagnostics["run_id"],
                "BL-006": bl006_summary["run_id"],
                "BL-007": bl007_report["run_id"],
                "BL-008": bl008_summary["run_id"],
            },
            "config_source": runtime_controls["config_source"],
            "run_config_path": runtime_controls["run_config_path"],
            "run_config_schema_version": runtime_controls["run_config_schema_version"],
            "run_intent_path": runtime_controls["run_intent_path"],
            "run_effective_config_path": runtime_controls["run_effective_config_path"],
            "signal_mode_name": signal_mode.get("name"),
        },
        "execution_scope_summary": {
            "observability_schema_version": BL009_OBSERVABILITY_SCHEMA_VERSION,
            "source_family": input_scope.get("source_family"),
            "signal_mode": signal_mode,
            "signal_mode_calibration": signal_mode_calibration,
            "interaction_types_included": interaction_types_included,
            "total_seed_count": profile["diagnostics"]["matched_seed_count"],
            "history_track_count": history_track_count,
            "influence_tracks_included": influence_tracks_included,
            "influence_track_count": influence_track_count,
            "canonical_config_artifact_pair_available": (
                canonical_config_artifacts.get("run_intent", {}).get("available", False)
                and canonical_config_artifacts.get("run_effective_config", {}).get("available", False)
            ),
        },
        "run_config": {
            "control_mode": control_mode,
            "input_scope": input_scope,
            "observability": {
                "diagnostic_sample_limit": diagnostic_sample_limit,
                "bootstrap_mode": bootstrap_mode,
                "validation_policies": {
                    "bl008_bl009_handshake_validation_policy": bl008_bl009_handshake_validation_policy,
                },
            },
            "signal_mode": signal_mode,
            "signal_mode_calibration": signal_mode_calibration,
            "canonical_config_artifacts": canonical_config_artifacts,
            "data_layer": {
                "status": "active_mode_not_required",
                "reason": "BL-009 uses active BL-004..BL-008 artifacts for observability diagnostics.",
            },
            "bootstrap_assets": {
                "status": "active_mode_not_required",
                "reason": "Legacy synthetic bootstrap assets are no longer part of active BL-009 execution.",
            },
            "profile": profile["config"],
            "retrieval": bl005_diagnostics["config"],
            "scoring": bl006_summary["config"],
            "assembly": bl007_report["config"],
            "alignment_seed_controls": {
                "fuzzy_matching": bl003_fuzzy_controls,
                "match_rate_validation": _object_mapping(bl003_counts.get("match_rate_validation")),
                "match_rate_min_threshold": safe_float(
                    _object_mapping(bl003_counts.get("match_rate_validation")).get("min_threshold"),
                    0.0,
                ),
            },
            "transparency": {
                "playlist_track_count": bl008_summary["playlist_track_count"],
                "top_contributor_distribution": bl008_summary["top_contributor_distribution"],
                "explanation_payload_rule": "top 3 contributors by weighted contribution; sentence derived from top contributors and playlist position",
                "rejected_track_control_causality_count": safe_int(
                    bl008_payloads.get("rejected_track_control_causality_count"),
                    len(rejected_causality),
                ),
            },
        },
        "validation": {
            "status": handshake_validation["status"],
            "policy": handshake_validation["policy"],
            "sampled_violations": handshake_validation["sampled_violations"],
        },
        "ingestion_alignment_diagnostics": {
            "stage_status": "active_bl004_to_bl008_mode",
            "reason": "BL-009 is aligned to current implementation scope and logs BL-004..BL-008 artifacts directly.",
            "surrogate_inputs": {
                "aligned_events_path": None,
                "candidate_stub_path": None,
            },
            "alignment_summary": {
                "summary_path": relpath(paths["bl003_summary"], root),
                "matched_by_spotify_id": safe_int(bl003_counts.get("matched_by_spotify_id"), 0),
                "matched_by_metadata": safe_int(bl003_counts.get("matched_by_metadata"), 0),
                "matched_by_fuzzy": bl003_match_by_fuzzy,
                "matched_events_rows": bl003_match_total,
                "unmatched_rows": safe_int(bl003_counts.get("unmatched_rows"), 0),
                "fuzzy_match_ratio": round(
                    (bl003_match_by_fuzzy / bl003_match_total) if bl003_match_total > 0 else 0.0,
                    6,
                ),
                "fuzzy_matching": bl003_fuzzy_controls,
            },
            "source_resilience_diagnostics": source_resilience_diagnostics,
        },
        "stage_diagnostics": {
            "data_layer": {
                "task": "BL-017",
                "status": "inactive_in_active_mode",
                "reason": "BL-009 observability does not require BL-017 in active mode.",
            },
            "bootstrap_assets": {
                "task": "BL-016",
                "status": "inactive_in_active_mode",
                "reason": "BL-009 observability does not require BL-016 in active mode.",
            },
            "alignment": {
                "task": "BL-003",
                "summary_path": relpath(paths["bl003_summary"], root),
                "counts": {
                    "input_event_rows": safe_int(bl003_counts.get("input_event_rows"), 0),
                    "matched_by_spotify_id": safe_int(bl003_counts.get("matched_by_spotify_id"), 0),
                    "matched_by_metadata": safe_int(bl003_counts.get("matched_by_metadata"), 0),
                    "matched_by_fuzzy": bl003_match_by_fuzzy,
                    "unmatched": safe_int(bl003_counts.get("unmatched"), 0),
                    "seed_table_rows": safe_int(bl003_counts.get("seed_table_rows"), 0),
                },
                "fuzzy_matching": bl003_fuzzy_controls,
            },
            "profile": {
                "task": "BL-004",
                "run_id": profile["run_id"],
                "user_id": profile["user_id"],
                "diagnostics": profile["diagnostics"],
                "feature_availability_summary": profile.get("feature_availability_summary", {}),
                "seed_summary": profile["seed_summary"],
                "dominant_lead_genres": bl004_summary["dominant_lead_genres"],
                "dominant_tags": bl004_summary["dominant_tags"],
            },
            "retrieval": {
                "task": "BL-005",
                "run_id": bl005_diagnostics["run_id"],
                "counts": bl005_diagnostics["counts"],
                "rule_hits": bl005_diagnostics["rule_hits"],
                "decision_path_counts": bl005_diagnostics.get("decision_path_counts", {}),
                "threshold_attribution": bl005_diagnostics.get("threshold_attribution", {}),
                "bounded_what_if_estimates": bl005_diagnostics.get("bounded_what_if_estimates", {}),
                "candidate_shaping_fidelity": bl005_diagnostics.get("candidate_shaping_fidelity", {}),
                "top_kept_track_ids": bl005_diagnostics["top_kept_track_ids"],
            },
            "scoring": {
                "task": "BL-006",
                "run_id": bl006_summary["run_id"],
                "counts": bl006_summary["counts"],
                "score_statistics": bl006_summary["score_statistics"],
                "top_candidates": bl006_summary["top_candidates"],
                "feature_availability_summary": bl006_summary.get("feature_availability_summary", {}),
                "scoring_sensitivity_diagnostics": bl006_summary.get("scoring_sensitivity_diagnostics"),
                "weight_rebalance_diagnostics": (
                    bl006_summary.get("config", {}).get("weight_rebalance_diagnostics")
                    or {
                        "status": "not_available",
                        "reason": "BL-006 summary does not include weight_rebalance_diagnostics",
                    }
                ),
            },
            "assembly": {
                "task": "BL-007",
                "run_id": bl007_report["run_id"],
                "counts": bl007_report["counts"],
                "rule_hits": bl007_report["rule_hits"],
                "playlist_genre_mix": bl007_report["playlist_genre_mix"],
                "playlist_score_range": bl007_report["playlist_score_range"],
                "playlist_length": playlist["playlist_length"],
                "influence_track_diagnostics": influence_track_diagnostics,
                "transition_diagnostics": bl007_report.get("transition_diagnostics"),
                "tradeoff_metrics_summary": bl007_report.get("tradeoff_metrics_summary", {}),
            },
            "transparency": {
                "task": "BL-008",
                "run_id": bl008_summary["run_id"],
                "playlist_track_count": bl008_summary["playlist_track_count"],
                "top_contributor_distribution": bl008_summary["top_contributor_distribution"],
                "explanation_count": len(bl008_payloads["explanations"]),
                "control_causality_summary": control_causality_summary,
                "rejected_control_causality_summary": rejected_control_causality_summary,
            },
        },
        "exclusion_diagnostics": {
            "retrieval": {
                "seed_tracks_excluded": bl005_diagnostics["counts"]["seed_tracks_excluded"],
                "rejected_non_seed_candidates": bl005_diagnostics["counts"]["rejected_non_seed_candidates"],
                "sample_rejected_non_seed_rows": retrieval_samples,
            },
            "assembly": {
                "tracks_excluded": bl007_report["counts"]["tracks_excluded"],
                "rule_hits": bl007_report["rule_hits"],
                "first_length_cap_boundary": (
                    {
                        "score_rank": int(first_length_cap["score_rank"]),
                        "track_id": first_length_cap["track_id"],
                        "lead_genre": first_length_cap["lead_genre"],
                        "final_score": float(first_length_cap["final_score"]),
                    }
                    if first_length_cap is not None
                    else None
                ),
                "sample_exclusions_by_rule": assembly_rule_samples,
            },
        },
        "retrieval_fidelity_summary": build_retrieval_fidelity_summary(bl005_diagnostics),
        "playlist_tradeoff_summary": build_playlist_tradeoff_summary(bl007_report),
        "cross_stage_influence_attribution_summary": build_cross_stage_influence_attribution_summary(
            profile=profile,
            bl005_diagnostics=bl005_diagnostics,
            bl006_summary=bl006_summary,
            bl007_report=bl007_report,
            control_causality_summary=control_causality_summary,
            influence_track_diagnostics=influence_track_diagnostics,
        ),
        "feature_availability_summary": build_feature_availability_summary(profile, bl006_summary),
        "control_registry_snapshot": build_control_registry_snapshot(),
        "validity_boundaries": {
            "scope": {
                "single_user_deterministic": True,
                "source_family": input_scope.get("source_family"),
                "interaction_types_included": interaction_types_included,
            },
            "reproducibility_interpretation": build_reproducibility_interpretation(),
            "known_limits": {
                "explanation_fidelity_vs_persuasiveness": (
                    "BL-008 explanations are mechanism-linked, but human usefulness does not by itself prove full causal fidelity."
                ),
                "candidate_generation_dependency": (
                    "Ranking and playlist outcomes are bounded by BL-005 candidate shaping and exclusion behavior."
                ),
                "reproducibility_contract_boundary": (
                    "Reproducibility claims are bounded to declared fixed inputs/config snapshots and stable-content checks."
                ),
            },
            "run_caveats": {
                "bl003_unmatched_events": safe_int(bl003_counts.get("unmatched"), 0),
                "bl003_match_rate_actual": safe_float(
                    _object_mapping(bl003_counts.get("match_rate_validation")).get("actual_match_rate"),
                    0.0,
                ),
                "bl007_undersized_playlist": bool(
                    _object_mapping(bl007_report.get("undersized_playlist_warning")).get("is_undersized", False)
                ),
                "bl008_missing_control_causality_tracks": safe_int(
                    control_causality_summary.get("tracks_missing_control_causality"),
                    0,
                ),
                "bl008_missing_rejected_control_causality_tracks": safe_int(
                    rejected_control_causality_summary.get("tracks_missing_control_causality"),
                    0,
                ),
                "bl010_retry_required": None,
            },
        },
        "output_artifacts": {
            "playlist_track_ids_sha256": output_hash_aliases["playlist_track_ids_sha256"],
            "playlist_artifact_sha256": output_hash_aliases["playlist_artifact_sha256"],
            "run_config_payload_sha256": output_hash_aliases["run_config_payload_sha256"],
            "scoring_records_sha256": output_hash_aliases["scoring_records_sha256"],
            "profile_seed_trace_sha256": output_hash_aliases["profile_seed_trace_sha256"],
            "primary_outputs": {
                "playlist": {
                    "path": relpath(paths["bl007_playlist"], root),
                    "sha256": artifact_hashes[relpath(paths["bl007_playlist"], root)],
                    "size_bytes": artifact_sizes[relpath(paths["bl007_playlist"], root)],
                },
                "explanation_payloads": {
                    "path": relpath(paths["bl008_payloads"], root),
                    "sha256": artifact_hashes[relpath(paths["bl008_payloads"], root)],
                    "size_bytes": artifact_sizes[relpath(paths["bl008_payloads"], root)],
                },
            },
            "trace_outputs": {
                "seed_trace": {
                    "path": relpath(paths["bl004_seed_trace"], root),
                    "sha256": artifact_hashes[relpath(paths["bl004_seed_trace"], root)],
                },
                "candidate_decisions": {
                    "path": relpath(paths["bl005_decisions"], root),
                    "sha256": artifact_hashes[relpath(paths["bl005_decisions"], root)],
                },
                "scored_candidates": {
                    "path": relpath(paths["bl006_scored"], root),
                    "sha256": artifact_hashes[relpath(paths["bl006_scored"], root)],
                },
                "assembly_trace": {
                    "path": relpath(paths["bl007_trace"], root),
                    "sha256": artifact_hashes[relpath(paths["bl007_trace"], root)],
                },
            },
            "supporting_outputs": {
                "profile": {
                    "path": relpath(paths["bl004_profile"], root),
                    "sha256": artifact_hashes[relpath(paths["bl004_profile"], root)],
                },
                "retrieval_diagnostics": {
                    "path": relpath(paths["bl005_diagnostics"], root),
                    "sha256": artifact_hashes[relpath(paths["bl005_diagnostics"], root)],
                },
                "score_summary": {
                    "path": relpath(paths["bl006_summary"], root),
                    "sha256": artifact_hashes[relpath(paths["bl006_summary"], root)],
                },
                "assembly_report": {
                    "path": relpath(paths["bl007_report"], root),
                    "sha256": artifact_hashes[relpath(paths["bl007_report"], root)],
                },
                "explanation_summary": {
                    "path": relpath(paths["bl008_summary"], root),
                    "sha256": artifact_hashes[relpath(paths["bl008_summary"], root)],
                },
                "data_layer_coverage": {
                    "path": None,
                    "status": "inactive_in_active_mode",
                },
                "bootstrap_manifest": {
                    "path": None,
                    "status": "inactive_in_active_mode",
                },
            },
        },
    }


def _build_output_hash_aliases(
    *,
    playlist_artifact_sha256: str | None,
    run_config_payload_sha256: str | None,
    scored_candidates_sha256: str | None,
    seed_trace_sha256: str | None,
) -> dict[str, str | None]:
    """Build backward-compatible and semantically explicit output hash aliases."""
    return {
        "playlist_track_ids_sha256": playlist_artifact_sha256,
        "playlist_artifact_sha256": playlist_artifact_sha256,
        "run_config_payload_sha256": run_config_payload_sha256,
        "bl006_scored_candidates_sha256": scored_candidates_sha256,
        "scoring_records_sha256": scored_candidates_sha256,
        "bl004_seed_trace_sha256": seed_trace_sha256,
        "profile_seed_trace_sha256": seed_trace_sha256,
    }


def _build_run_index_row(
    *,
    run_id: str,
    generated_at_utc: str,
    dataset_version: str,
    pipeline_version: str,
    bootstrap_mode: bool,
    profile: dict[str, Any],
    bl005_diagnostics: dict[str, Any],
    bl006_summary: dict[str, Any],
    bl007_report: dict[str, Any],
    bl008_summary: dict[str, Any],
    playlist: dict[str, Any],
    bl008_payloads: dict[str, Any],
    bl003_match_by_fuzzy: int,
    bl003_fuzzy_controls: dict[str, Any],
    artifact_hashes: dict[str, str],
    paths: dict[str, Path],
    root: Path,
    run_log_path: Path,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "dataset_version": dataset_version,
        "pipeline_version": pipeline_version,
        "bootstrap_mode": int(bootstrap_mode),
        "profile_run_id": profile["run_id"],
        "retrieval_run_id": bl005_diagnostics["run_id"],
        "scoring_run_id": bl006_summary["run_id"],
        "assembly_run_id": bl007_report["run_id"],
        "transparency_run_id": bl008_summary["run_id"],
        "kept_candidates": bl005_diagnostics["counts"]["kept_candidates"],
        "candidates_scored": bl006_summary["counts"]["candidates_scored"],
        "playlist_length": playlist["playlist_length"],
        "explanation_count": len(bl008_payloads["explanations"]),
        "matched_by_fuzzy": bl003_match_by_fuzzy,
        "fuzzy_enabled": int(bool(bl003_fuzzy_controls.get("enabled", False))),
        "playlist_sha256": artifact_hashes[relpath(paths["bl007_playlist"], root)],
        "explanation_payloads_sha256": artifact_hashes[relpath(paths["bl008_payloads"], root)],
        "observability_log_sha256": sha256_of_file(run_log_path),
    }


def _load_observability_inputs(root: Path) -> tuple[dict[str, Path], dict[str, dict[str, Any]]]:
    required_paths = bl009_required_paths(root, bl009_script_path=Path(__file__).resolve())
    ensure_paths_exist(list(required_paths.values()), stage_label="BL-009", label="inputs", root=root)

    paths = dict(required_paths)
    loaded = {
        "bl003_summary": load_required_json_object(paths["bl003_summary"], label="BL-003 alignment summary", stage_label="BL-009"),
        "profile": load_required_json_object(paths["bl004_profile"], label="BL-004 profile", stage_label="BL-009"),
        "bl004_summary": load_required_json_object(paths["bl004_summary"], label="BL-004 profile summary", stage_label="BL-009"),
        "bl005_diagnostics": load_required_json_object(paths["bl005_diagnostics"], label="BL-005 diagnostics", stage_label="BL-009"),
        "bl006_summary": load_required_json_object(paths["bl006_summary"], label="BL-006 score summary", stage_label="BL-009"),
        "bl007_report": load_required_json_object(paths["bl007_report"], label="BL-007 assembly report", stage_label="BL-009"),
        "bl008_summary": load_required_json_object(paths["bl008_summary"], label="BL-008 explanation summary", stage_label="BL-009"),
    }
    return paths, loaded


def _validate_observability_inputs(loaded: dict[str, dict[str, Any]]) -> None:
    ensure_required_keys(loaded["bl003_summary"], ["inputs", "counts"], label="BL-003 alignment summary", stage_label="BL-009")
    ensure_required_keys(loaded["profile"], ["run_id", "user_id", "diagnostics", "seed_summary", "config"], label="BL-004 profile", stage_label="BL-009")
    ensure_required_keys(loaded["bl004_summary"], ["dominant_lead_genres", "dominant_tags"], label="BL-004 profile summary", stage_label="BL-009")
    ensure_required_keys(loaded["bl005_diagnostics"], ["run_id", "counts", "rule_hits", "top_kept_track_ids", "config"], label="BL-005 diagnostics", stage_label="BL-009")
    ensure_required_keys(loaded["bl006_summary"], ["run_id", "counts", "score_statistics", "top_candidates", "config"], label="BL-006 score summary", stage_label="BL-009")
    ensure_required_keys(loaded["bl007_report"], ["run_id", "counts", "rule_hits", "playlist_genre_mix", "playlist_score_range", "config"], label="BL-007 assembly report", stage_label="BL-009")
    ensure_required_keys(loaded["bl008_summary"], ["run_id", "playlist_track_count", "top_contributor_distribution"], label="BL-008 explanation summary", stage_label="BL-009")


def _extract_bl003_context(bl003_summary: dict[str, Any]) -> dict[str, Any]:
    bl003_counts = _object_mapping(bl003_summary.get("counts"))
    bl003_inputs = _object_mapping(bl003_summary.get("inputs"))
    return {
        "bl003_counts": bl003_counts,
        "bl003_inputs": bl003_inputs,
        "source_resilience_diagnostics": build_source_resilience_diagnostics(bl003_summary),
        "bl003_fuzzy_controls": _object_mapping(bl003_inputs.get("fuzzy_matching")),
        "bl003_match_by_fuzzy": safe_int(bl003_counts.get("matched_by_fuzzy"), 0),
        "bl003_match_total": safe_int(bl003_counts.get("matched_events_rows"), 0),
    }


def _load_bl008_bl009_runtime_artifacts(paths: dict[str, Path]) -> dict[str, Any]:
    bl005_decisions = load_csv_rows(paths["bl005_decisions"])
    bl006_scored = load_csv_rows(paths["bl006_scored"])
    bl007_trace = load_csv_rows(paths["bl007_trace"])
    playlist = load_required_json_object(paths["bl007_playlist"], label="BL-007 playlist", stage_label="BL-009")
    bl008_payloads = load_required_json_object(paths["bl008_payloads"], label="BL-008 explanation payloads", stage_label="BL-009")
    ensure_required_keys(playlist, ["playlist_length"], label="BL-007 playlist", stage_label="BL-009")
    ensure_required_keys(bl008_payloads, ["explanations"], label="BL-008 explanation payloads", stage_label="BL-009")
    return {
        "bl005_decisions": bl005_decisions,
        "bl006_scored": bl006_scored,
        "bl007_trace": bl007_trace,
        "playlist": playlist,
        "bl008_payloads": bl008_payloads,
    }


def _prepare_bl008_bl009_handshake_context(
    *,
    bl008_summary: dict[str, Any],
    bl008_payloads: dict[str, Any],
    policy: str,
) -> dict[str, Any]:
    (
        handshake_validation,
        _explanations,
        rejected_causality,
        control_causality_summary,
        rejected_control_causality_summary,
    ) = _validate_and_prepare_bl008_handshake(
        bl008_summary=bl008_summary,
        bl008_payloads=bl008_payloads,
        policy=policy,
    )
    return {
        "handshake_validation": handshake_validation,
        "rejected_causality": rejected_causality,
        "control_causality_summary": control_causality_summary,
        "rejected_control_causality_summary": rejected_control_causality_summary,
    }


def _prepare_pipeline_versions(paths: dict[str, Path], root: Path) -> dict[str, Any]:
    script_hash_keys = [
        "bl004_script",
        "bl005_script",
        "bl006_script",
        "bl007_script",
        "bl008_script",
        "bl009_script",
    ]
    script_hashes = {
        relpath(paths[key], root): sha256_of_file(paths[key])
        for key in script_hash_keys
    }
    pipeline_version = sha256_of_values([script_hashes[key] for key in sorted(script_hashes)])

    dataset_hash_sources = ["bl004_seed_trace", "bl005_filtered", "bl006_scored"]
    dataset_component_hashes = {
        relpath(paths[key], root): sha256_of_file(paths[key])
        for key in dataset_hash_sources
    }
    dataset_version = sha256_of_values([dataset_component_hashes[key] for key in sorted(dataset_component_hashes)])
    return {
        "script_hashes": script_hashes,
        "pipeline_version": pipeline_version,
        "dataset_version": dataset_version,
        "dataset_version_source": "active_pipeline_outputs",
        "dataset_component_hashes": dataset_component_hashes,
    }


def _prepare_retrieval_and_assembly_samples(
    *,
    profile: dict[str, Any],
    bl005_decisions: list[dict[str, str]],
    bl006_scored: list[dict[str, str]],
    bl007_trace: list[dict[str, str]],
    playlist: dict[str, Any],
    diagnostic_sample_limit: int,
    requested_influence_track_ids: list[str],
) -> dict[str, Any]:
    rejected_non_seed = [
        row for row in bl005_decisions
        if row.get("decision") == "reject" and row.get("is_seed_track") == "0"
    ]
    retrieval_samples = [
        {
            "track_id": row["track_id"],
            "lead_genre": row["lead_genre"],
            "semantic_score": float(row["semantic_score"]),
            "numeric_pass_count": int(row["numeric_pass_count"]),
            "decision_reason": row["decision_reason"],
        }
        for row in first_items(rejected_non_seed, diagnostic_sample_limit)
    ]

    assembly_excluded = [row for row in bl007_trace if row.get("decision") == "excluded"]
    assembly_rule_samples_raw = parse_exclusion_samples(assembly_excluded, "exclusion_reason", diagnostic_sample_limit)
    assembly_rule_samples = {
        reason: [
            {
                "score_rank": int(row["score_rank"]),
                "track_id": row["track_id"],
                "lead_genre": row["lead_genre"],
                "final_score": float(row["final_score"]),
            }
            for row in rows
        ]
        for reason, rows in assembly_rule_samples_raw.items()
    }
    first_length_cap = next(
        (row for row in assembly_excluded if row.get("exclusion_reason") == "length_cap_reached"),
        None,
    )

    scored_track_ids = {
        str(row.get("track_id", "")).strip()
        for row in bl006_scored
        if str(row.get("track_id", "")).strip()
    }
    trace_by_track_id = {
        str(row.get("track_id", "")).strip(): row
        for row in bl007_trace
        if str(row.get("track_id", "")).strip()
    }
    playlist_tracks = _object_mapping(playlist).get("tracks")
    playlist_track_rows = list(playlist_tracks) if isinstance(playlist_tracks, list) else []
    playlist_position_by_track_id = {
        str(row.get("track_id", "")).strip(): safe_int(row.get("playlist_position"), 0)
        for row in playlist_track_rows
        if str(row.get("track_id", "")).strip()
    }
    influence_track_diagnostics = _build_influence_track_diagnostics(
        requested_influence_track_ids=requested_influence_track_ids,
        trace_by_track_id=trace_by_track_id,
        scored_track_ids=scored_track_ids,
        playlist_position_by_track_id=playlist_position_by_track_id,
    )
    return {
        "retrieval_samples": retrieval_samples,
        "first_length_cap": first_length_cap,
        "assembly_rule_samples": assembly_rule_samples,
        "influence_track_diagnostics": influence_track_diagnostics,
    }


def _prepare_observability_context(
    *,
    root: Path,
    runtime_controls: dict[str, object],
    bl008_bl009_handshake_validation_policy: str,
    input_scope: dict[str, object],
    diagnostic_sample_limit: int,
) -> dict[str, Any]:
    paths, loaded = _load_observability_inputs(root)
    _validate_observability_inputs(loaded)

    bl003_summary = loaded["bl003_summary"]
    profile = loaded["profile"]
    bl004_summary = loaded["bl004_summary"]
    bl005_diagnostics = loaded["bl005_diagnostics"]
    bl006_summary = loaded["bl006_summary"]
    bl007_report = loaded["bl007_report"]
    bl008_summary = loaded["bl008_summary"]

    bl003_context = _extract_bl003_context(bl003_summary)
    runtime_artifacts = _load_bl008_bl009_runtime_artifacts(paths)
    handshake_context = _prepare_bl008_bl009_handshake_context(
        bl008_summary=bl008_summary,
        bl008_payloads=runtime_artifacts["bl008_payloads"],
        policy=bl008_bl009_handshake_validation_policy,
    )

    generated_at_utc = utc_now()
    run_id = f"BL009-OBSERVE-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S-%f')}"
    version_context = _prepare_pipeline_versions(paths, root)

    interaction_types_included = _resolve_interaction_types_included(input_scope)

    seed_summary = _object_mapping(profile.get("seed_summary"))
    bl003_influence_tracks = _object_mapping(bl003_context["bl003_inputs"].get("influence_tracks"))
    raw_requested_influence_track_ids = bl003_influence_tracks.get("track_ids")
    requested_track_values = (
        raw_requested_influence_track_ids
        if isinstance(raw_requested_influence_track_ids, list)
        else []
    )
    requested_influence_track_ids = [
        str(v).strip()
        for v in requested_track_values
        if str(v).strip()
    ]
    seed_counts_by_type = _object_mapping(seed_summary.get("counts_by_interaction_type"))
    influence_track_count = safe_int(seed_counts_by_type.get("influence"), 0)
    history_track_count = safe_int(seed_counts_by_type.get("history"), 0)
    influence_tracks_included = influence_track_count > 0
    sample_context = _prepare_retrieval_and_assembly_samples(
        profile=profile,
        bl005_decisions=runtime_artifacts["bl005_decisions"],
        bl006_scored=runtime_artifacts["bl006_scored"],
        bl007_trace=runtime_artifacts["bl007_trace"],
        playlist=runtime_artifacts["playlist"],
        diagnostic_sample_limit=diagnostic_sample_limit,
        requested_influence_track_ids=requested_influence_track_ids,
    )

    script_keys = {
        "bl004_script",
        "bl005_script",
        "bl006_script",
        "bl007_script",
        "bl008_script",
        "bl009_script",
    }
    canonical_config_artifacts = resolve_canonical_config_artifacts(runtime_controls, root)
    artifact_hashes, artifact_sizes = build_artifact_maps(paths, root, script_keys)
    retrieval_signal_mode = _object_mapping(_object_mapping(bl005_diagnostics.get("config")).get("signal_mode"))
    scoring_signal_mode = _object_mapping(_object_mapping(bl006_summary.get("config")).get("signal_mode"))
    signal_mode = retrieval_signal_mode or scoring_signal_mode
    signal_mode_calibration = build_signal_mode_calibration_summary(bl005_diagnostics, bl006_summary)

    return {
        "paths": paths,
        "bl003_counts": bl003_context["bl003_counts"],
        "bl003_fuzzy_controls": bl003_context["bl003_fuzzy_controls"],
        "bl003_match_by_fuzzy": bl003_context["bl003_match_by_fuzzy"],
        "bl003_match_total": bl003_context["bl003_match_total"],
        "source_resilience_diagnostics": bl003_context["source_resilience_diagnostics"],
        "profile": profile,
        "bl004_summary": bl004_summary,
        "bl005_diagnostics": bl005_diagnostics,
        "bl006_summary": bl006_summary,
        "bl007_report": bl007_report,
        "bl008_summary": bl008_summary,
        "playlist": runtime_artifacts["playlist"],
        "bl008_payloads": runtime_artifacts["bl008_payloads"],
        "handshake_validation": handshake_context["handshake_validation"],
        "rejected_causality": handshake_context["rejected_causality"],
        "control_causality_summary": handshake_context["control_causality_summary"],
        "rejected_control_causality_summary": handshake_context["rejected_control_causality_summary"],
        "generated_at_utc": generated_at_utc,
        "run_id": run_id,
        "script_hashes": version_context["script_hashes"],
        "pipeline_version": version_context["pipeline_version"],
        "dataset_version": version_context["dataset_version"],
        "dataset_version_source": version_context["dataset_version_source"],
        "dataset_component_hashes": version_context["dataset_component_hashes"],
        "interaction_types_included": interaction_types_included,
        "history_track_count": history_track_count,
        "influence_tracks_included": influence_tracks_included,
        "influence_track_count": influence_track_count,
        "retrieval_samples": sample_context["retrieval_samples"],
        "first_length_cap": sample_context["first_length_cap"],
        "assembly_rule_samples": sample_context["assembly_rule_samples"],
        "influence_track_diagnostics": sample_context["influence_track_diagnostics"],
        "canonical_config_artifacts": canonical_config_artifacts,
        "artifact_hashes": artifact_hashes,
        "artifact_sizes": artifact_sizes,
        "signal_mode": signal_mode,
        "signal_mode_calibration": signal_mode_calibration,
    }


def main() -> None:
    runtime_controls = resolve_bl009_runtime_controls()
    control_mode = _object_mapping(runtime_controls.get("control_mode"))
    input_scope = _object_mapping(runtime_controls.get("input_scope"))
    diagnostic_sample_limit = safe_int(runtime_controls.get("diagnostic_sample_limit"), 5)
    bootstrap_mode = bool(runtime_controls.get("bootstrap_mode", True))
    bl008_bl009_handshake_validation_policy = str(
        runtime_controls.get("bl008_bl009_handshake_validation_policy", "warn")
    )
    root = impl_root()
    output_dir = root / "observability" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    context = _prepare_observability_context(
        root=root,
        runtime_controls=runtime_controls,
        bl008_bl009_handshake_validation_policy=bl008_bl009_handshake_validation_policy,
        input_scope=input_scope,
        diagnostic_sample_limit=diagnostic_sample_limit,
    )

    paths = context["paths"]
    bl003_counts = context["bl003_counts"]
    bl003_fuzzy_controls = context["bl003_fuzzy_controls"]
    bl003_match_by_fuzzy = context["bl003_match_by_fuzzy"]
    bl003_match_total = context["bl003_match_total"]
    source_resilience_diagnostics = context["source_resilience_diagnostics"]
    profile = context["profile"]
    bl004_summary = context["bl004_summary"]
    bl005_diagnostics = context["bl005_diagnostics"]
    bl006_summary = context["bl006_summary"]
    bl007_report = context["bl007_report"]
    bl008_summary = context["bl008_summary"]
    playlist = context["playlist"]
    bl008_payloads = context["bl008_payloads"]
    handshake_validation = context["handshake_validation"]
    rejected_causality = context["rejected_causality"]
    control_causality_summary = context["control_causality_summary"]
    rejected_control_causality_summary = context["rejected_control_causality_summary"]
    generated_at_utc = context["generated_at_utc"]
    run_id = context["run_id"]
    script_hashes = context["script_hashes"]
    pipeline_version = context["pipeline_version"]
    dataset_version = context["dataset_version"]
    dataset_version_source = context["dataset_version_source"]
    dataset_component_hashes = context["dataset_component_hashes"]
    interaction_types_included = context["interaction_types_included"]
    history_track_count = context["history_track_count"]
    influence_tracks_included = context["influence_tracks_included"]
    influence_track_count = context["influence_track_count"]
    retrieval_samples = context["retrieval_samples"]
    first_length_cap = context["first_length_cap"]
    assembly_rule_samples = context["assembly_rule_samples"]
    influence_track_diagnostics = context["influence_track_diagnostics"]
    canonical_config_artifacts = context["canonical_config_artifacts"]
    artifact_hashes = context["artifact_hashes"]
    artifact_sizes = context["artifact_sizes"]
    signal_mode = context["signal_mode"]
    signal_mode_calibration = context["signal_mode_calibration"]

    run_log = _build_run_log(
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        bootstrap_mode=bootstrap_mode,
        dataset_version=dataset_version,
        dataset_version_source=dataset_version_source,
        pipeline_version=pipeline_version,
        dataset_component_hashes=dataset_component_hashes,
        script_hashes=script_hashes,
        runtime_controls=runtime_controls,
        signal_mode=signal_mode,
        signal_mode_calibration=signal_mode_calibration,
        control_mode=control_mode,
        input_scope=input_scope,
        diagnostic_sample_limit=diagnostic_sample_limit,
        bl008_bl009_handshake_validation_policy=bl008_bl009_handshake_validation_policy,
        canonical_config_artifacts=canonical_config_artifacts,
        profile=profile,
        bl004_summary=bl004_summary,
        bl005_diagnostics=bl005_diagnostics,
        bl006_summary=bl006_summary,
        bl007_report=bl007_report,
        playlist=playlist,
        bl008_summary=bl008_summary,
        bl008_payloads=bl008_payloads,
        rejected_causality=rejected_causality,
        handshake_validation=handshake_validation,
        paths=paths,
        root=root,
        bl003_counts=bl003_counts,
        bl003_match_by_fuzzy=bl003_match_by_fuzzy,
        bl003_match_total=bl003_match_total,
        bl003_fuzzy_controls=bl003_fuzzy_controls,
        source_resilience_diagnostics=source_resilience_diagnostics,
        interaction_types_included=interaction_types_included,
        history_track_count=history_track_count,
        influence_tracks_included=influence_tracks_included,
        influence_track_count=influence_track_count,
        control_causality_summary=control_causality_summary,
        rejected_control_causality_summary=rejected_control_causality_summary,
        influence_track_diagnostics=influence_track_diagnostics,
        retrieval_samples=retrieval_samples,
        first_length_cap=first_length_cap,
        assembly_rule_samples=assembly_rule_samples,
        artifact_hashes=artifact_hashes,
        artifact_sizes=artifact_sizes,
    )

    ensure_required_sections(run_log)

    run_log["run_metadata"]["elapsed_seconds"] = round(time.time() - start_time, 3)

    run_log_path = output_dir / "bl009_run_observability_log.json"
    with open_text_write(run_log_path) as handle:
        handle.write(json.dumps(run_log, indent=2, ensure_ascii=True))

    run_index_path = output_dir / "bl009_run_index.csv"
    run_index_row = _build_run_index_row(
        run_id=run_id,
        generated_at_utc=generated_at_utc,
        dataset_version=dataset_version,
        pipeline_version=pipeline_version,
        bootstrap_mode=bootstrap_mode,
        profile=profile,
        bl005_diagnostics=bl005_diagnostics,
        bl006_summary=bl006_summary,
        bl007_report=bl007_report,
        bl008_summary=bl008_summary,
        playlist=playlist,
        bl008_payloads=bl008_payloads,
        bl003_match_by_fuzzy=bl003_match_by_fuzzy,
        bl003_fuzzy_controls=bl003_fuzzy_controls,
        artifact_hashes=artifact_hashes,
        paths=paths,
        root=root,
        run_log_path=run_log_path,
    )
    with open_text_write(run_index_path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(run_index_row.keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerow(run_index_row)

    print("BL-009 observability logging complete.")
    print(f"run_log={run_log_path}")
    print(f"run_index={run_index_path}")
    print(f"run_id={run_id}")


if __name__ == "__main__":
    main()
