from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scoring.profile_extractor import build_numeric_specs

NUMERIC_FEATURE_SPECS = build_numeric_specs()
NUMERIC_COMPONENTS = set(NUMERIC_FEATURE_SPECS)
SCORED_CANDIDATE_FIELDS = [
    "rank",
    "track_id",
    "lead_genre",
    "matched_genres",
    "matched_tags",
    "final_score",
    "danceability_similarity",
    "danceability_contribution",
    "energy_similarity",
    "energy_contribution",
    "valence_similarity",
    "valence_contribution",
    "tempo_similarity",
    "tempo_contribution",
    "duration_ms_similarity",
    "duration_ms_contribution",
    "popularity_similarity",
    "popularity_contribution",
    "key_similarity",
    "key_contribution",
    "mode_similarity",
    "mode_contribution",
    "lead_genre_similarity",
    "lead_genre_contribution",
    "genre_overlap_similarity",
    "genre_overlap_contribution",
    "tag_overlap_similarity",
    "tag_overlap_contribution",
]


@dataclass(frozen=True)
class ScoringPaths:
    profile_path: Path
    filtered_candidates_path: Path
    output_dir: Path
    bl003_summary_path: Path | None = None


@dataclass(frozen=True)
class ScoringControls:
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    signal_mode: dict[str, object]
    component_weights: dict[str, float]
    numeric_thresholds: dict[str, float]
    lead_genre_strategy: str = "weighted_top_lead_genres"
    semantic_overlap_strategy: str = "precision_aware"
    semantic_precision_alpha_mode: str = "profile_adaptive"
    semantic_precision_alpha_fixed: float = 0.35
    enable_numeric_confidence_scaling: bool = True
    numeric_confidence_floor: float = 0.0
    profile_numeric_confidence_mode: str = "direct"
    profile_numeric_confidence_blend_weight: float = 1.0
    emit_confidence_impact_diagnostics: bool = True
    emit_semantic_precision_diagnostics: bool = False
    enable_scoring_sensitivity_diagnostics: bool = False
    scoring_sensitivity_top_k: int = 10
    scoring_sensitivity_perturbation_pct: float = 0.10
    scoring_sensitivity_max_components: int = 5
    apply_bl003_influence_tracks: bool = False
    influence_track_bonus_scale: float = 0.0
    bl005_bl006_handshake_validation_policy: str = "warn"
    runtime_control_resolution_diagnostics: dict[str, object] = field(default_factory=dict)
    runtime_control_validation_warnings: list[str] = field(default_factory=list)

    def as_mapping(self) -> dict[str, object]:
        return {
            "config_source": self.config_source,
            "run_config_path": self.run_config_path,
            "run_config_schema_version": self.run_config_schema_version,
            "signal_mode": dict(self.signal_mode),
            "component_weights": dict(self.component_weights),
            "numeric_thresholds": dict(self.numeric_thresholds),
            "lead_genre_strategy": self.lead_genre_strategy,
            "semantic_overlap_strategy": self.semantic_overlap_strategy,
            "semantic_precision_alpha_mode": self.semantic_precision_alpha_mode,
            "semantic_precision_alpha_fixed": self.semantic_precision_alpha_fixed,
            "enable_numeric_confidence_scaling": self.enable_numeric_confidence_scaling,
            "numeric_confidence_floor": self.numeric_confidence_floor,
            "profile_numeric_confidence_mode": self.profile_numeric_confidence_mode,
            "profile_numeric_confidence_blend_weight": self.profile_numeric_confidence_blend_weight,
            "emit_confidence_impact_diagnostics": self.emit_confidence_impact_diagnostics,
            "emit_semantic_precision_diagnostics": self.emit_semantic_precision_diagnostics,
            "enable_scoring_sensitivity_diagnostics": self.enable_scoring_sensitivity_diagnostics,
            "scoring_sensitivity_top_k": self.scoring_sensitivity_top_k,
            "scoring_sensitivity_perturbation_pct": self.scoring_sensitivity_perturbation_pct,
            "scoring_sensitivity_max_components": self.scoring_sensitivity_max_components,
            "apply_bl003_influence_tracks": self.apply_bl003_influence_tracks,
            "influence_track_bonus_scale": self.influence_track_bonus_scale,
            "bl005_bl006_handshake_validation_policy": self.bl005_bl006_handshake_validation_policy,
            "runtime_control_resolution_diagnostics": dict(self.runtime_control_resolution_diagnostics),
            "runtime_control_validation_warnings": list(self.runtime_control_validation_warnings),
        }


@dataclass(frozen=True)
class ScoringInputs:
    profile: dict[str, object]
    bl003_summary: dict[str, object]
    candidates: list[dict[str, str]]


@dataclass(frozen=True)
class ScoringContext:
    signal_mode: dict[str, object]
    effective_component_weights: dict[str, float]
    active_numeric_specs: dict[str, dict[str, object]]
    profile_scoring_data: dict[str, object]
    active_component_weights: dict[str, float]
    weight_rebalance_diagnostics: dict[str, object]
    numeric_confidence_by_feature: dict[str, float]
    profile_numeric_confidence_factor: float
    semantic_precision_alpha: float
    lead_genre_strategy: str = "weighted_top_lead_genres"
    semantic_overlap_strategy: str = "precision_aware"
    semantic_precision_alpha_mode: str = "profile_adaptive"
    semantic_precision_alpha_fixed: float = 0.35
    enable_numeric_confidence_scaling: bool = True
    numeric_confidence_floor: float = 0.0
    profile_numeric_confidence_mode: str = "direct"
    profile_numeric_confidence_blend_weight: float = 1.0
    emit_confidence_impact_diagnostics: bool = True
    emit_semantic_precision_diagnostics: bool = False
    enable_scoring_sensitivity_diagnostics: bool = False
    scoring_sensitivity_top_k: int = 10
    scoring_sensitivity_perturbation_pct: float = 0.10
    scoring_sensitivity_max_components: int = 5
    apply_bl003_influence_tracks: bool = False
    influence_track_ids: set[str] | None = None
    influence_preference_weight: float = 0.0
    influence_track_bonus_scale: float = 0.0


@dataclass(frozen=True)
class ScoringArtifacts:
    scored_path: Path
    diagnostics_path: Path
    summary_path: Path


def controls_from_mapping(payload: Mapping[str, Any]) -> ScoringControls:
    component_weights = _mapping_to_float_dict(payload.get("component_weights"))
    numeric_thresholds = _mapping_to_float_dict(payload.get("numeric_thresholds"))
    runtime_control_resolution_diagnostics = _mapping_to_str_object_dict(
        payload.get("runtime_control_resolution_diagnostics")
    )
    runtime_control_validation_warnings = _payload_str_list(
        payload.get("runtime_control_validation_warnings")
    )

    return ScoringControls(
        config_source=str(payload.get("config_source") or "environment"),
        run_config_path=(str(payload["run_config_path"]) if payload.get("run_config_path") else None),
        run_config_schema_version=(
            str(payload["run_config_schema_version"])
            if payload.get("run_config_schema_version")
            else None
        ),
        signal_mode={str(k): v for k, v in dict(payload.get("signal_mode") or {}).items()},
        component_weights=component_weights,
        numeric_thresholds=numeric_thresholds,
        lead_genre_strategy=str(payload.get("lead_genre_strategy") or "weighted_top_lead_genres"),
        semantic_overlap_strategy=str(payload.get("semantic_overlap_strategy") or "precision_aware"),
        semantic_precision_alpha_mode=str(payload.get("semantic_precision_alpha_mode") or "profile_adaptive"),
        semantic_precision_alpha_fixed=float(
            payload["semantic_precision_alpha_fixed"]
            if payload.get("semantic_precision_alpha_fixed") is not None
            else 0.35
        ),
        enable_numeric_confidence_scaling=bool(payload.get("enable_numeric_confidence_scaling", True)),
        numeric_confidence_floor=float(
            payload["numeric_confidence_floor"]
            if payload.get("numeric_confidence_floor") is not None
            else 0.0
        ),
        profile_numeric_confidence_mode=str(payload.get("profile_numeric_confidence_mode") or "direct"),
        profile_numeric_confidence_blend_weight=float(
            payload["profile_numeric_confidence_blend_weight"]
            if payload.get("profile_numeric_confidence_blend_weight") is not None
            else 1.0
        ),
        emit_confidence_impact_diagnostics=bool(payload.get("emit_confidence_impact_diagnostics", True)),
        emit_semantic_precision_diagnostics=bool(payload.get("emit_semantic_precision_diagnostics", False)),
        enable_scoring_sensitivity_diagnostics=bool(
            payload.get("enable_scoring_sensitivity_diagnostics", False)
        ),
        scoring_sensitivity_top_k=int(payload.get("scoring_sensitivity_top_k", 10)),
        scoring_sensitivity_perturbation_pct=float(
            payload.get("scoring_sensitivity_perturbation_pct", 0.10)
        ),
        scoring_sensitivity_max_components=int(payload.get("scoring_sensitivity_max_components", 5)),
        apply_bl003_influence_tracks=bool(payload.get("apply_bl003_influence_tracks", False)),
        influence_track_bonus_scale=float(
            payload["influence_track_bonus_scale"]
            if payload.get("influence_track_bonus_scale") is not None
            else 0.0
        ),
        bl005_bl006_handshake_validation_policy=str(
            payload.get("bl005_bl006_handshake_validation_policy") or "warn"
        ),
        runtime_control_resolution_diagnostics=runtime_control_resolution_diagnostics,
        runtime_control_validation_warnings=runtime_control_validation_warnings,
    )


def context_as_mapping(context: ScoringContext) -> dict[str, object]:
    return {
        "signal_mode": dict(context.signal_mode),
        "effective_component_weights": dict(context.effective_component_weights),
        "active_numeric_specs": dict(context.active_numeric_specs),
        "profile_scoring_data": dict(context.profile_scoring_data),
        "active_component_weights": dict(context.active_component_weights),
        "weight_rebalance_diagnostics": dict(context.weight_rebalance_diagnostics),
        "numeric_confidence_by_feature": dict(context.numeric_confidence_by_feature),
        "profile_numeric_confidence_factor": context.profile_numeric_confidence_factor,
        "semantic_precision_alpha": context.semantic_precision_alpha,
        "lead_genre_strategy": context.lead_genre_strategy,
        "semantic_overlap_strategy": context.semantic_overlap_strategy,
        "semantic_precision_alpha_mode": context.semantic_precision_alpha_mode,
        "semantic_precision_alpha_fixed": context.semantic_precision_alpha_fixed,
        "enable_numeric_confidence_scaling": context.enable_numeric_confidence_scaling,
        "numeric_confidence_floor": context.numeric_confidence_floor,
        "profile_numeric_confidence_mode": context.profile_numeric_confidence_mode,
        "profile_numeric_confidence_blend_weight": context.profile_numeric_confidence_blend_weight,
        "emit_confidence_impact_diagnostics": context.emit_confidence_impact_diagnostics,
        "emit_semantic_precision_diagnostics": context.emit_semantic_precision_diagnostics,
        "enable_scoring_sensitivity_diagnostics": context.enable_scoring_sensitivity_diagnostics,
        "scoring_sensitivity_top_k": context.scoring_sensitivity_top_k,
        "scoring_sensitivity_perturbation_pct": context.scoring_sensitivity_perturbation_pct,
        "scoring_sensitivity_max_components": context.scoring_sensitivity_max_components,
        "apply_bl003_influence_tracks": context.apply_bl003_influence_tracks,
        "influence_track_ids": sorted(context.influence_track_ids or set()),
        "influence_preference_weight": context.influence_preference_weight,
        "influence_track_bonus_scale": context.influence_track_bonus_scale,
    }


def _mapping_to_float_dict(value: object) -> dict[str, float]:
    if not isinstance(value, Mapping):
        return {}
    return {str(k): float(v) for k, v in dict(value).items()}


def _mapping_to_str_object_dict(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        return {}
    return {str(k): v for k, v in dict(value).items()}


def _nested_mapping_to_str_object_dict(value: object) -> dict[str, dict[str, object]]:
    normalized: dict[str, dict[str, object]] = {}
    if not isinstance(value, Mapping):
        return normalized
    for key, nested_value in value.items():
        if isinstance(nested_value, Mapping):
            normalized[str(key)] = {str(k): v for k, v in nested_value.items()}
    return normalized


def _payload_str_set(payload: Mapping[str, Any], key: str) -> set[str]:
    return {str(v) for v in list(payload.get(key) or []) if str(v)}


def _payload_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def context_from_mapping(payload: Mapping[str, Any]) -> ScoringContext:
    effective_component_weights_raw = payload.get("effective_component_weights")
    active_numeric_specs_raw = payload.get("active_numeric_specs")
    profile_scoring_data_raw = payload.get("profile_scoring_data")
    active_component_weights_raw = payload.get("active_component_weights")
    weight_rebalance_diagnostics_raw = payload.get("weight_rebalance_diagnostics")
    numeric_confidence_by_feature_raw = payload.get("numeric_confidence_by_feature")
    profile_numeric_confidence_factor_raw = payload.get("profile_numeric_confidence_factor")
    semantic_precision_alpha_raw = payload.get("semantic_precision_alpha")
    signal_mode_raw = payload.get("signal_mode")

    effective_component_weights = _mapping_to_float_dict(effective_component_weights_raw)
    active_numeric_specs = _nested_mapping_to_str_object_dict(active_numeric_specs_raw)
    profile_scoring_data = _mapping_to_str_object_dict(profile_scoring_data_raw)
    active_component_weights = _mapping_to_float_dict(active_component_weights_raw)
    weight_rebalance_diagnostics = _mapping_to_str_object_dict(weight_rebalance_diagnostics_raw)
    numeric_confidence_by_feature = _mapping_to_float_dict(numeric_confidence_by_feature_raw)

    return ScoringContext(
        signal_mode=_mapping_to_str_object_dict(signal_mode_raw),
        effective_component_weights=effective_component_weights,
        active_numeric_specs=active_numeric_specs,
        profile_scoring_data=profile_scoring_data,
        active_component_weights=active_component_weights,
        weight_rebalance_diagnostics=weight_rebalance_diagnostics,
        numeric_confidence_by_feature=numeric_confidence_by_feature,
        profile_numeric_confidence_factor=float(profile_numeric_confidence_factor_raw or 1.0),
        semantic_precision_alpha=float(semantic_precision_alpha_raw or 0.35),
        lead_genre_strategy=str(payload.get("lead_genre_strategy") or "weighted_top_lead_genres"),
        semantic_overlap_strategy=str(payload.get("semantic_overlap_strategy") or "precision_aware"),
        semantic_precision_alpha_mode=str(payload.get("semantic_precision_alpha_mode") or "profile_adaptive"),
        semantic_precision_alpha_fixed=float(
            payload["semantic_precision_alpha_fixed"]
            if payload.get("semantic_precision_alpha_fixed") is not None
            else 0.35
        ),
        enable_numeric_confidence_scaling=bool(payload.get("enable_numeric_confidence_scaling", True)),
        numeric_confidence_floor=float(
            payload["numeric_confidence_floor"]
            if payload.get("numeric_confidence_floor") is not None
            else 0.0
        ),
        profile_numeric_confidence_mode=str(payload.get("profile_numeric_confidence_mode") or "direct"),
        profile_numeric_confidence_blend_weight=float(
            payload["profile_numeric_confidence_blend_weight"]
            if payload.get("profile_numeric_confidence_blend_weight") is not None
            else 1.0
        ),
        emit_confidence_impact_diagnostics=bool(payload.get("emit_confidence_impact_diagnostics", True)),
        emit_semantic_precision_diagnostics=bool(payload.get("emit_semantic_precision_diagnostics", False)),
        enable_scoring_sensitivity_diagnostics=bool(
            payload.get("enable_scoring_sensitivity_diagnostics", False)
        ),
        scoring_sensitivity_top_k=int(payload.get("scoring_sensitivity_top_k", 10)),
        scoring_sensitivity_perturbation_pct=float(
            payload.get("scoring_sensitivity_perturbation_pct", 0.10)
        ),
        scoring_sensitivity_max_components=int(payload.get("scoring_sensitivity_max_components", 5)),
        apply_bl003_influence_tracks=bool(payload.get("apply_bl003_influence_tracks", False)),
        influence_track_ids=_payload_str_set(payload, "influence_track_ids"),
        influence_preference_weight=float(payload.get("influence_preference_weight", 0.0)),
        influence_track_bonus_scale=float(payload.get("influence_track_bonus_scale", 0.0)),
    )
