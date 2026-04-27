from __future__ import annotations

import hashlib
import json
import locale
import os
import platform
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from run_config.schema import FieldSpec, RunConfigSchemaError, validate_section
from shared_utils.constants import (
    CUSTOM_SIGNAL_MODE_NAME,
    DEFAULT_ASSEMBLY_CONTROLS,
    DEFAULT_CONTROL_MODE,
    DEFAULT_CONTROLLABILITY_CONTROLS,
    DEFAULT_INCLUDE_INTERACTION_TYPES,
    DEFAULT_INFLUENCE_TRACKS,
    DEFAULT_INGESTION_CONTROLS,
    DEFAULT_INPUT_SCOPE,
    DEFAULT_INTERACTION_SCOPE,
    DEFAULT_OBSERVABILITY_CONTROLS,
    DEFAULT_ORCHESTRATION_CONTROLS,
    DEFAULT_PROFILE_CONTROLS,
    DEFAULT_RECENCY_YEARS_MIN_OFFSET,
    DEFAULT_REPORTING_SCORE_THRESHOLDS,
    DEFAULT_RETRIEVAL_CONTROLS,
    DEFAULT_SCENARIO_DEFINITIONS,
    DEFAULT_SCENARIO_POLICY,
    DEFAULT_SCORING_CONTROLS,
    DEFAULT_SEED_CONTROLS,
    DEFAULT_SIGNAL_MODE_NAME,
    DEFAULT_TOP_CONTRIBUTOR_LIMIT,
    DEFAULT_TRANSPARENCY_CONTROLS,
    DEFAULT_WEIGHTING_POLICY,
    ENHANCED_SIGNAL_MODE_NAME,
)
from shared_utils.io_utils import open_text_write
from shared_utils.parsing import safe_float, safe_int

RUN_CONFIG_SCHEMA_VERSION = "run-config-v1"
RUN_INTENT_ARTIFACT_SCHEMA_VERSION = "run-intent-v1"
RUN_EFFECTIVE_ARTIFACT_SCHEMA_VERSION = "run-effective-config-v1"
RUN_CONFIG_SCHEMA_FILENAME = "run_config-v1.schema.json"

BL003_MATCH_METHOD_SPOTIFY_ID_EXACT = "spotify_id_exact"
BL003_MATCH_METHOD_METADATA_FALLBACK = "metadata_fallback"
BL003_MATCH_METHOD_FUZZY_TITLE_ARTIST = "fuzzy_title_artist"
BL003_ALLOWED_MATCH_METHODS: tuple[str, ...] = (
    BL003_MATCH_METHOD_SPOTIFY_ID_EXACT,
    BL003_MATCH_METHOD_METADATA_FALLBACK,
    BL003_MATCH_METHOD_FUZZY_TITLE_ARTIST,
)


def _build_default_run_config() -> dict[str, Any]:
    return {
        "schema_version": RUN_CONFIG_SCHEMA_VERSION,
        "control_mode": dict(DEFAULT_CONTROL_MODE),
        "user_context": {
            "user_id": None,
        },
        "input_scope": dict(DEFAULT_INPUT_SCOPE),
        "interaction_scope": dict(DEFAULT_INTERACTION_SCOPE),
        "influence_tracks": dict(DEFAULT_INFLUENCE_TRACKS),
        "ingestion_controls": dict(DEFAULT_INGESTION_CONTROLS),
        "profile_controls": {
            "top_tag_limit": safe_int(DEFAULT_PROFILE_CONTROLS["top_tag_limit"]),
            "top_genre_limit": safe_int(DEFAULT_PROFILE_CONTROLS["top_genre_limit"]),
            "top_lead_genre_limit": safe_int(DEFAULT_PROFILE_CONTROLS["top_lead_genre_limit"]),
            "confidence_weighting_mode": str(DEFAULT_PROFILE_CONTROLS["confidence_weighting_mode"]),
            "confidence_bin_high_threshold": safe_float(DEFAULT_PROFILE_CONTROLS["confidence_bin_high_threshold"]),
            "confidence_bin_medium_threshold": safe_float(DEFAULT_PROFILE_CONTROLS["confidence_bin_medium_threshold"]),
            "interaction_attribution_mode": str(DEFAULT_PROFILE_CONTROLS["interaction_attribution_mode"]),
            "emit_profile_policy_diagnostics": bool(DEFAULT_PROFILE_CONTROLS["emit_profile_policy_diagnostics"]),
            "confidence_validation_policy": str(DEFAULT_PROFILE_CONTROLS["confidence_validation_policy"]),
            "interaction_type_validation_policy": str(DEFAULT_PROFILE_CONTROLS["interaction_type_validation_policy"]),
            "synthetic_data_validation_policy": str(DEFAULT_PROFILE_CONTROLS["synthetic_data_validation_policy"]),
            "bl003_handshake_validation_policy": str(DEFAULT_PROFILE_CONTROLS["bl003_handshake_validation_policy"]),
            "numeric_malformed_row_threshold": DEFAULT_PROFILE_CONTROLS["numeric_malformed_row_threshold"],
            "no_numeric_signal_row_threshold": DEFAULT_PROFILE_CONTROLS["no_numeric_signal_row_threshold"],
        },
        "retrieval_controls": {
            "profile_top_tag_limit": safe_int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_tag_limit"]),
            "profile_top_genre_limit": safe_int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_genre_limit"]),
            "profile_top_lead_genre_limit": safe_int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_lead_genre_limit"]),
            "semantic_strong_keep_score": safe_int(DEFAULT_RETRIEVAL_CONTROLS["semantic_strong_keep_score"]),
            "semantic_min_keep_score": safe_int(DEFAULT_RETRIEVAL_CONTROLS["semantic_min_keep_score"]),
            "numeric_support_min_pass": safe_int(DEFAULT_RETRIEVAL_CONTROLS["numeric_support_min_pass"]),
            "numeric_support_min_score": safe_float(DEFAULT_RETRIEVAL_CONTROLS["numeric_support_min_score"]),
            "use_weighted_semantics": bool(DEFAULT_RETRIEVAL_CONTROLS["use_weighted_semantics"]),
            "use_continuous_numeric": bool(DEFAULT_RETRIEVAL_CONTROLS["use_continuous_numeric"]),
            "enable_popularity_numeric": bool(DEFAULT_RETRIEVAL_CONTROLS["enable_popularity_numeric"]),
            "language_filter_enabled": bool(DEFAULT_RETRIEVAL_CONTROLS["language_filter_enabled"]),
            "language_filter_codes": _coerce_str_list(DEFAULT_RETRIEVAL_CONTROLS["language_filter_codes"]),
            "recency_years_min_offset": _coerce_optional_int(
                DEFAULT_RETRIEVAL_CONTROLS["recency_years_min_offset"],
                DEFAULT_RECENCY_YEARS_MIN_OFFSET,
            ),
            "numeric_thresholds": _coerce_object_mapping(DEFAULT_RETRIEVAL_CONTROLS["numeric_thresholds"]),
            "profile_quality_penalty_enabled": bool(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_penalty_enabled"]),
            "profile_quality_threshold": safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_threshold"]),
            "profile_entropy_low_threshold": safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_entropy_low_threshold"]),
            "influence_share_threshold": safe_float(DEFAULT_RETRIEVAL_CONTROLS["influence_share_threshold"]),
            "profile_quality_penalty_increment": safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_penalty_increment"]),
            "profile_entropy_penalty_increment": safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_entropy_penalty_increment"]),
            "influence_share_penalty_increment": safe_float(DEFAULT_RETRIEVAL_CONTROLS["influence_share_penalty_increment"]),
            "numeric_penalty_scale": safe_float(DEFAULT_RETRIEVAL_CONTROLS["numeric_penalty_scale"]),
            "semantic_overlap_damping_mid_entropy_threshold": safe_float(
                DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_mid_entropy_threshold"]
            ),
            "semantic_overlap_damping_low_entropy": safe_float(DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_low_entropy"]),
            "semantic_overlap_damping_mid_entropy": safe_float(DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_mid_entropy"]),
            "enable_numeric_confidence_scaling": bool(DEFAULT_RETRIEVAL_CONTROLS["enable_numeric_confidence_scaling"]),
            "numeric_confidence_floor": safe_float(DEFAULT_RETRIEVAL_CONTROLS["numeric_confidence_floor"]),
            "profile_numeric_confidence_mode": str(DEFAULT_RETRIEVAL_CONTROLS["profile_numeric_confidence_mode"]),
            "profile_numeric_confidence_blend_weight": safe_float(
                DEFAULT_RETRIEVAL_CONTROLS["profile_numeric_confidence_blend_weight"]
            ),
            "numeric_support_score_mode": str(DEFAULT_RETRIEVAL_CONTROLS["numeric_support_score_mode"]),
            "emit_profile_policy_diagnostics": bool(DEFAULT_RETRIEVAL_CONTROLS["emit_profile_policy_diagnostics"]),
            "bl004_bl005_handshake_validation_policy": str(
                DEFAULT_RETRIEVAL_CONTROLS["bl004_bl005_handshake_validation_policy"]
            ),
        },
        "scoring_controls": {
            "component_weights": _coerce_object_mapping(DEFAULT_SCORING_CONTROLS["component_weights"]),
            "numeric_thresholds": _coerce_object_mapping(DEFAULT_SCORING_CONTROLS["numeric_thresholds"]),
            "lead_genre_strategy": str(DEFAULT_SCORING_CONTROLS["lead_genre_strategy"]),
            "semantic_overlap_strategy": str(DEFAULT_SCORING_CONTROLS["semantic_overlap_strategy"]),
            "semantic_precision_alpha_mode": str(DEFAULT_SCORING_CONTROLS["semantic_precision_alpha_mode"]),
            "semantic_precision_alpha_fixed": safe_float(DEFAULT_SCORING_CONTROLS["semantic_precision_alpha_fixed"]),
            "enable_numeric_confidence_scaling": bool(DEFAULT_SCORING_CONTROLS["enable_numeric_confidence_scaling"]),
            "numeric_confidence_floor": safe_float(DEFAULT_SCORING_CONTROLS["numeric_confidence_floor"]),
            "profile_numeric_confidence_mode": str(DEFAULT_SCORING_CONTROLS["profile_numeric_confidence_mode"]),
            "profile_numeric_confidence_blend_weight": safe_float(DEFAULT_SCORING_CONTROLS["profile_numeric_confidence_blend_weight"]),
            "emit_confidence_impact_diagnostics": bool(DEFAULT_SCORING_CONTROLS["emit_confidence_impact_diagnostics"]),
            "emit_semantic_precision_diagnostics": bool(DEFAULT_SCORING_CONTROLS["emit_semantic_precision_diagnostics"]),
            "apply_bl003_influence_tracks": bool(DEFAULT_SCORING_CONTROLS["apply_bl003_influence_tracks"]),
            "influence_track_bonus_scale": safe_float(DEFAULT_SCORING_CONTROLS["influence_track_bonus_scale"]),
            "bl005_bl006_handshake_validation_policy": str(
                DEFAULT_SCORING_CONTROLS["bl005_bl006_handshake_validation_policy"]
            ),
        },
        "assembly_controls": dict(DEFAULT_ASSEMBLY_CONTROLS),
        "transparency_controls": {
            "top_contributor_limit": DEFAULT_TOP_CONTRIBUTOR_LIMIT,
            "blend_primary_contributor_on_near_tie": bool(DEFAULT_TRANSPARENCY_CONTROLS["blend_primary_contributor_on_near_tie"]),
            "primary_contributor_tie_delta": safe_float(DEFAULT_TRANSPARENCY_CONTROLS["primary_contributor_tie_delta"]),
        },
        "observability_controls": dict(DEFAULT_OBSERVABILITY_CONTROLS),
        "reporting_controls": {
            "score_thresholds": _coerce_object_mapping(DEFAULT_REPORTING_SCORE_THRESHOLDS),
        },
        "controllability_controls": {
            **dict(DEFAULT_CONTROLLABILITY_CONTROLS),
            "scenario_policy": {
                "enabled_scenario_ids": _coerce_str_list(DEFAULT_SCENARIO_POLICY["enabled_scenario_ids"]),
                "repeat_count": safe_int(DEFAULT_SCENARIO_POLICY["repeat_count"]),
                "stage_scope": _coerce_str_list(DEFAULT_SCENARIO_POLICY["stage_scope"]),
                "comparison_mode": str(DEFAULT_SCENARIO_POLICY["comparison_mode"]),
            },
            "scenario_definitions": _coerce_object_list(DEFAULT_SCENARIO_DEFINITIONS),
        },
        "seed_controls": {
            "match_rate_min_threshold": DEFAULT_SEED_CONTROLS["match_rate_min_threshold"],
            "top_range_weights": _coerce_object_mapping(DEFAULT_SEED_CONTROLS["top_range_weights"]),
            "source_base_weights": _coerce_object_mapping(DEFAULT_SEED_CONTROLS["source_base_weights"]),
            "source_resilience_policy": _coerce_object_mapping(DEFAULT_SEED_CONTROLS["source_resilience_policy"]),
            "fuzzy_matching": _coerce_object_mapping(DEFAULT_SEED_CONTROLS["fuzzy_matching"]),
            "match_strategy": _coerce_object_mapping(DEFAULT_SEED_CONTROLS["match_strategy"]),
            "match_strategy_order": _coerce_str_list(DEFAULT_SEED_CONTROLS["match_strategy_order"]),
            "temporal_controls": _coerce_object_mapping(DEFAULT_SEED_CONTROLS["temporal_controls"]),
            "aggregation_policy": _coerce_object_mapping(DEFAULT_SEED_CONTROLS["aggregation_policy"]),
            "decay_half_lives": _coerce_object_mapping(DEFAULT_SEED_CONTROLS["decay_half_lives"]),
            "weighting_policy": {
                "top_tracks": _coerce_object_mapping(DEFAULT_WEIGHTING_POLICY["top_tracks"]),
                "playlist_items": _coerce_object_mapping(DEFAULT_WEIGHTING_POLICY["playlist_items"]),
            },
        },
        "orchestration_controls": {
            "stage_order": _coerce_str_list(DEFAULT_ORCHESTRATION_CONTROLS["stage_order"]),
            "continue_on_error": bool(DEFAULT_ORCHESTRATION_CONTROLS["continue_on_error"]),
            "refresh_seed_policy": str(DEFAULT_ORCHESTRATION_CONTROLS["refresh_seed_policy"]),
            "required_stable_artifacts": _coerce_str_list(DEFAULT_ORCHESTRATION_CONTROLS["required_stable_artifacts"]),
        },
    }


class RunConfigError(RuntimeError):
    pass


def _coerce_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return []


def _coerce_object_list(value: Any) -> list[object]:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return []


def _coerce_object_mapping(value: Any) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def _coerce_optional_int(value: Any, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


DEFAULT_RUN_CONFIG: dict[str, Any] = _build_default_run_config()

PROFILE_CONTROLS_SCHEMA: dict[str, FieldSpec] = {
    "top_tag_limit": FieldSpec(type="positive_int", default=safe_int(DEFAULT_PROFILE_CONTROLS["top_tag_limit"])),
    "top_genre_limit": FieldSpec(type="positive_int", default=safe_int(DEFAULT_PROFILE_CONTROLS["top_genre_limit"])),
    "top_lead_genre_limit": FieldSpec(
        type="positive_int", default=safe_int(DEFAULT_PROFILE_CONTROLS["top_lead_genre_limit"])
    ),
    "confidence_weighting_mode": FieldSpec(
        type="enum",
        default=str(DEFAULT_PROFILE_CONTROLS["confidence_weighting_mode"]),
        choices=("linear_half_bias", "direct_confidence", "none"),
    ),
    "confidence_bin_high_threshold": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_PROFILE_CONTROLS["confidence_bin_high_threshold"]),
    ),
    "confidence_bin_medium_threshold": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_PROFILE_CONTROLS["confidence_bin_medium_threshold"]),
    ),
    "interaction_attribution_mode": FieldSpec(
        type="enum",
        default=str(DEFAULT_PROFILE_CONTROLS["interaction_attribution_mode"]),
        choices=("split_selected_types_equal_share", "primary_type_only"),
    ),
    "emit_profile_policy_diagnostics": FieldSpec(
        type="bool",
        default=bool(DEFAULT_PROFILE_CONTROLS["emit_profile_policy_diagnostics"]),
    ),
    "confidence_validation_policy": FieldSpec(
        type="enum",
        default=str(DEFAULT_PROFILE_CONTROLS["confidence_validation_policy"]),
        choices=("allow", "warn", "strict"),
    ),
    "interaction_type_validation_policy": FieldSpec(
        type="enum",
        default=str(DEFAULT_PROFILE_CONTROLS["interaction_type_validation_policy"]),
        choices=("allow", "warn", "strict"),
    ),
    "synthetic_data_validation_policy": FieldSpec(
        type="enum",
        default=str(DEFAULT_PROFILE_CONTROLS["synthetic_data_validation_policy"]),
        choices=("allow", "warn", "strict"),
    ),
    "bl003_handshake_validation_policy": FieldSpec(
        type="enum",
        default=str(DEFAULT_PROFILE_CONTROLS["bl003_handshake_validation_policy"]),
        choices=("allow", "warn", "strict"),
    ),
}

RETRIEVAL_CONTROLS_SCHEMA: dict[str, FieldSpec] = {
    "profile_top_tag_limit": FieldSpec(
        type="positive_int",
        default=safe_int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_tag_limit"]),
    ),
    "profile_top_genre_limit": FieldSpec(
        type="positive_int",
        default=safe_int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_genre_limit"]),
    ),
    "profile_top_lead_genre_limit": FieldSpec(
        type="positive_int",
        default=safe_int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_lead_genre_limit"]),
    ),
    "profile_quality_penalty_enabled": FieldSpec(
        type="bool",
        default=bool(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_penalty_enabled"]),
    ),
    "profile_quality_threshold": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_threshold"]),
    ),
    "profile_entropy_low_threshold": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_entropy_low_threshold"]),
    ),
    "influence_share_threshold": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["influence_share_threshold"]),
    ),
    "profile_quality_penalty_increment": FieldSpec(
        type="non_negative_float",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_penalty_increment"]),
    ),
    "profile_entropy_penalty_increment": FieldSpec(
        type="non_negative_float",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_entropy_penalty_increment"]),
    ),
    "influence_share_penalty_increment": FieldSpec(
        type="non_negative_float",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["influence_share_penalty_increment"]),
    ),
    "numeric_penalty_scale": FieldSpec(
        type="non_negative_float",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["numeric_penalty_scale"]),
    ),
    "semantic_overlap_damping_mid_entropy_threshold": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_mid_entropy_threshold"]),
    ),
    "semantic_overlap_damping_low_entropy": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_low_entropy"]),
    ),
    "semantic_overlap_damping_mid_entropy": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_mid_entropy"]),
    ),
    "enable_numeric_confidence_scaling": FieldSpec(
        type="bool",
        default=bool(DEFAULT_RETRIEVAL_CONTROLS["enable_numeric_confidence_scaling"]),
    ),
    "numeric_confidence_floor": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["numeric_confidence_floor"]),
    ),
    "profile_numeric_confidence_mode": FieldSpec(
        type="enum",
        default=str(DEFAULT_RETRIEVAL_CONTROLS["profile_numeric_confidence_mode"]),
        choices=("direct", "blended"),
    ),
    "profile_numeric_confidence_blend_weight": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_RETRIEVAL_CONTROLS["profile_numeric_confidence_blend_weight"]),
    ),
    "numeric_support_score_mode": FieldSpec(
        type="enum",
        default=str(DEFAULT_RETRIEVAL_CONTROLS["numeric_support_score_mode"]),
        choices=("raw", "weighted", "weighted_absolute"),
    ),
    "emit_profile_policy_diagnostics": FieldSpec(
        type="bool",
        default=bool(DEFAULT_RETRIEVAL_CONTROLS["emit_profile_policy_diagnostics"]),
    ),
    "bl004_bl005_handshake_validation_policy": FieldSpec(
        type="enum",
        default=str(DEFAULT_RETRIEVAL_CONTROLS["bl004_bl005_handshake_validation_policy"]),
        choices=("allow", "warn", "strict"),
    ),
}

SCORING_CONTROLS_SCHEMA: dict[str, FieldSpec] = {
    "lead_genre_strategy": FieldSpec(
        type="enum",
        default=str(DEFAULT_SCORING_CONTROLS["lead_genre_strategy"]),
        choices=("single_anchor", "weighted_top_lead_genres"),
    ),
    "semantic_overlap_strategy": FieldSpec(
        type="enum",
        default=str(DEFAULT_SCORING_CONTROLS["semantic_overlap_strategy"]),
        choices=("overlap_only", "precision_aware"),
    ),
    "semantic_precision_alpha_mode": FieldSpec(
        type="enum",
        default=str(DEFAULT_SCORING_CONTROLS["semantic_precision_alpha_mode"]),
        choices=("profile_adaptive", "fixed"),
    ),
    "semantic_precision_alpha_fixed": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_SCORING_CONTROLS["semantic_precision_alpha_fixed"]),
    ),
    "enable_numeric_confidence_scaling": FieldSpec(
        type="bool",
        default=bool(DEFAULT_SCORING_CONTROLS["enable_numeric_confidence_scaling"]),
    ),
    "numeric_confidence_floor": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_SCORING_CONTROLS["numeric_confidence_floor"]),
    ),
    "profile_numeric_confidence_mode": FieldSpec(
        type="enum",
        default=str(DEFAULT_SCORING_CONTROLS["profile_numeric_confidence_mode"]),
        choices=("direct", "blended"),
    ),
    "profile_numeric_confidence_blend_weight": FieldSpec(
        type="fraction",
        default=safe_float(DEFAULT_SCORING_CONTROLS["profile_numeric_confidence_blend_weight"]),
    ),
    "emit_confidence_impact_diagnostics": FieldSpec(
        type="bool",
        default=bool(DEFAULT_SCORING_CONTROLS["emit_confidence_impact_diagnostics"]),
    ),
    "emit_semantic_precision_diagnostics": FieldSpec(
        type="bool",
        default=bool(DEFAULT_SCORING_CONTROLS["emit_semantic_precision_diagnostics"]),
    ),
    "apply_bl003_influence_tracks": FieldSpec(
        type="bool",
        default=bool(DEFAULT_SCORING_CONTROLS["apply_bl003_influence_tracks"]),
    ),
    "bl005_bl006_handshake_validation_policy": FieldSpec(
        type="enum",
        default=str(DEFAULT_SCORING_CONTROLS["bl005_bl006_handshake_validation_policy"]),
        choices=("allow", "warn", "strict"),
    ),
}

OBSERVABILITY_CONTROLS_SCHEMA: dict[str, FieldSpec] = {
    "diagnostic_sample_limit": FieldSpec(
        type="positive_int",
        default=safe_int(DEFAULT_OBSERVABILITY_CONTROLS["diagnostic_sample_limit"]),
    ),
    "bl008_bl009_handshake_validation_policy": FieldSpec(
        type="enum",
        default=str(DEFAULT_OBSERVABILITY_CONTROLS["bl008_bl009_handshake_validation_policy"]),
        choices=("allow", "warn", "strict"),
    ),
}

TRANSPARENCY_CONTROLS_SCHEMA: dict[str, FieldSpec] = {
    "top_contributor_limit": FieldSpec(
        type="positive_int",
        default=safe_int(DEFAULT_TOP_CONTRIBUTOR_LIMIT),
    ),
    "primary_contributor_tie_delta": FieldSpec(
        type="non_negative_float",
        default=safe_float(DEFAULT_TRANSPARENCY_CONTROLS["primary_contributor_tie_delta"]),
    ),
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _coerce_optional_positive_int(value: Any, default: int | None) -> int | None:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"1", "true", "yes", "on"}:
            return True
        if text in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, int | float):
        return bool(value)
    return default


def _coerce_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _coerce_validation_profile(value: Any, default: str) -> str:
    allowed = {"strict", "explore"}
    if isinstance(value, str):
        token = value.strip().lower()
        if token in allowed:
            return token
    return default


def _coerce_non_negative_float(value: Any, default: float) -> float:
    parsed = safe_float(value, default)
    return parsed if parsed >= 0 else default


def _coerce_min_positive_float(value: Any, default: float, *, min_value: float = 0.001) -> float:
    """Coerce to float and clamp to a minimum positive value, falling back on parse errors."""
    parsed = safe_float(value, default)
    return max(min_value, parsed)


def _normalize_allowed_tokens(raw_values: Any, allowed: set[str], defaults: list[str]) -> list[str]:
    """Normalize list values to allowed tokens with stable-order de-duplication."""
    if not isinstance(raw_values, list):
        return list(defaults)

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_values:
        token = str(item).strip()
        if token not in allowed or token in seen:
            continue
        seen.add(token)
        normalized.append(token)
    return normalized or list(defaults)


def _normalize_string_tokens(raw_values: Any, defaults: list[str]) -> list[str]:
    """Normalize list values to lowercase string tokens with stable-order de-duplication."""
    if not isinstance(raw_values, list):
        return list(defaults)

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_values:
        token = str(item).strip().lower()
        if not token or token in seen:
            continue
        seen.add(token)
        normalized.append(token)
    return normalized or list(defaults)


def _validate_positive_thresholds(thresholds: dict[str, Any] | None, context: str) -> dict[str, float]:
    """Validate that all numeric thresholds in the dict are positive (> 0).

    Args:
        thresholds: Dictionary of threshold name -> value
        context: Description of where thresholds come from (for error messages)

    Returns:
        The validated thresholds as float values

    Raises:
        RunConfigError if any threshold is <= 0 or non-numeric
    """
    if not thresholds:
        return {}

    validated = {}
    for key, value in thresholds.items():
        try:
            float_val = float(value)
        except (TypeError, ValueError) as exc:
            raise RunConfigError(
                f"{context}: threshold '{key}' must be numeric, got {type(value).__name__}: {value!r}"
            ) from exc
        if float_val <= 0:
            raise RunConfigError(
                f"{context}: threshold '{key}' must be positive (> 0), got {float_val}"
            )
        validated[key] = float_val

    return validated


def _validate_positive_float(value: Any, param_name: str) -> float:
    """Validate that a single threshold value is a positive float (> 0).

    Args:
        value: The value to validate
        param_name: Name of the parameter (for error messages)

    Returns:
        The validated float value

    Raises:
        RunConfigError if value is <= 0 or non-numeric
    """
    try:
        float_val = float(value)
    except (TypeError, ValueError) as exc:
        raise RunConfigError(
            f"{param_name} must be numeric, got {type(value).__name__}: {value!r}"
        ) from exc
    if float_val <= 0:
        raise RunConfigError(
            f"{param_name} must be positive (> 0), got {float_val}"
        )
    return float_val


def _coerce_fraction_zero_to_one(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if parsed < 0.0 or parsed > 1.0:
        return default
    return parsed


def _validate_allowed_keys(config_section: dict[str, Any], allowed_keys: set[str], context: str) -> None:
    unexpected_keys = sorted(set(config_section) - allowed_keys)
    if unexpected_keys:
        raise RunConfigError(
            f"{context} contains unsupported keys: {', '.join(unexpected_keys)}"
        )


def _validate_bool_like(value: Any, param_name: str, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        token = value.strip().lower()
        if token in {"1", "true", "yes", "on"}:
            return True
        if token in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, int | float) and value in {0, 1}:
        return bool(value)
    raise RunConfigError(f"{param_name} must be boolean-like, got {value!r}")


def _validate_fraction_zero_to_one(value: Any, param_name: str, default: float) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise RunConfigError(f"{param_name} must be numeric, got {value!r}") from exc
    if parsed < 0.0 or parsed > 1.0:
        raise RunConfigError(f"{param_name} must be within [0, 1], got {parsed}")
    return parsed


def _validate_non_negative_float(value: Any, param_name: str, default: float) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise RunConfigError(f"{param_name} must be numeric, got {value!r}") from exc
    if parsed < 0:
        raise RunConfigError(f"{param_name} must be >= 0, got {parsed}")
    return parsed


def _validate_non_negative_int(value: Any, param_name: str, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RunConfigError(f"{param_name} must be an integer, got {value!r}") from exc
    if parsed < 0:
        raise RunConfigError(f"{param_name} must be >= 0, got {parsed}")
    return parsed


def _validate_positive_int_or_error(value: Any, param_name: str, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RunConfigError(f"{param_name} must be an integer, got {value!r}") from exc
    if parsed <= 0:
        raise RunConfigError(f"{param_name} must be > 0, got {parsed}")
    return parsed


def _validate_string_list(raw_values: Any, context: str, defaults: list[str]) -> list[str]:
    if raw_values is None:
        return list(defaults)
    if not isinstance(raw_values, list):
        raise RunConfigError(f"{context} must be an array of strings")

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_values:
        token = str(item).strip()
        if not token or token in seen:
            continue
        seen.add(token)
        normalized.append(token)
    return normalized


def _validate_non_negative_float_map(
    raw_values: Any,
    defaults: dict[str, float],
    context: str,
) -> dict[str, float]:
    if raw_values is None:
        return {key: float(value) for key, value in defaults.items()}
    if not isinstance(raw_values, dict):
        raise RunConfigError(f"{context} must be an object")

    _validate_allowed_keys(raw_values, set(defaults), context)
    return {
        key: _validate_non_negative_float(raw_values.get(key), f"{context}.{key}", float(default_value))
        for key, default_value in defaults.items()
    }


def _validate_bl003_weighting_policy(
    raw_policy: Any,
    defaults: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    context = "run_config.seed_controls.weighting_policy"
    if raw_policy is None:
        return {
            section: {key: float(value) for key, value in section_defaults.items()}
            for section, section_defaults in defaults.items()
        }
    if not isinstance(raw_policy, dict):
        raise RunConfigError(f"{context} must be an object")

    _validate_allowed_keys(raw_policy, set(defaults), context)
    validated: dict[str, dict[str, float]] = {}
    for section, section_defaults in defaults.items():
        raw_section = raw_policy.get(section)
        section_context = f"{context}.{section}"
        if raw_section is None:
            validated[section] = {key: float(value) for key, value in section_defaults.items()}
            continue
        if not isinstance(raw_section, dict):
            raise RunConfigError(f"{section_context} must be an object")
        _validate_allowed_keys(raw_section, set(section_defaults), section_context)
        validated[section] = {
            key: _validate_non_negative_float(raw_section.get(key), f"{section_context}.{key}", float(default_value))
            for key, default_value in section_defaults.items()
        }
    return validated


def _parse_iso8601_utc(raw_value: str, context: str) -> str:
    normalized = raw_value.strip().replace("Z", "+00:00")
    if not normalized:
        raise RunConfigError(f"{context} must be a non-empty ISO-8601 datetime")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RunConfigError(f"{context} must be a valid ISO-8601 datetime") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    else:
        parsed = parsed.astimezone(UTC)
    return parsed.isoformat().replace("+00:00", "Z")


def _validate_bl003_temporal_controls(raw_temporal: Any, defaults: dict[str, Any]) -> dict[str, Any]:
    context = "run_config.seed_controls.temporal_controls"
    if raw_temporal is None:
        raw_temporal = {}
    if not isinstance(raw_temporal, dict):
        raise RunConfigError(f"{context} must be an object")

    _validate_allowed_keys(raw_temporal, set(defaults), context)
    allowed_modes = {"system", "fixed"}
    default_mode = str(defaults.get("reference_mode", "system")).strip().lower() or "system"
    raw_mode = raw_temporal.get("reference_mode")
    mode = default_mode if raw_mode is None else str(raw_mode).strip().lower()
    if mode not in allowed_modes:
        raise RunConfigError(
            f"{context}.reference_mode must be one of: {', '.join(sorted(allowed_modes))}"
        )

    raw_reference_now_utc = raw_temporal.get("reference_now_utc", defaults.get("reference_now_utc"))
    if raw_reference_now_utc is None:
        if mode == "fixed":
            raise RunConfigError(f"{context}.reference_now_utc is required when reference_mode='fixed'")
        return {
            "reference_mode": mode,
            "reference_now_utc": None,
        }

    reference_now_utc = _parse_iso8601_utc(str(raw_reference_now_utc), f"{context}.reference_now_utc")
    return {
        "reference_mode": mode,
        "reference_now_utc": reference_now_utc,
    }


def _validate_bl003_aggregation_policy(raw_policy: Any, defaults: dict[str, Any]) -> dict[str, Any]:
    context = "run_config.seed_controls.aggregation_policy"
    if raw_policy is None:
        raw_policy = {}
    if not isinstance(raw_policy, dict):
        raise RunConfigError(f"{context} must be an object")

    _validate_allowed_keys(raw_policy, set(defaults), context)

    mode_default = str(defaults.get("preference_weight_mode", "sum")).strip().lower() or "sum"
    raw_mode = raw_policy.get("preference_weight_mode")
    mode = mode_default if raw_mode is None else str(raw_mode).strip().lower()
    allowed_modes = {"sum", "max", "mean", "capped"}
    if mode not in allowed_modes:
        raise RunConfigError(
            f"{context}.preference_weight_mode must be one of: {', '.join(sorted(allowed_modes))}"
        )

    raw_cap = raw_policy.get("preference_weight_cap_per_event", defaults.get("preference_weight_cap_per_event"))
    cap: float | None
    if raw_cap is None:
        cap = None
    else:
        try:
            cap = float(raw_cap)
        except (TypeError, ValueError) as exc:
            raise RunConfigError(
                f"{context}.preference_weight_cap_per_event must be a number or null"
            ) from exc
        if cap < 0:
            raise RunConfigError(
                f"{context}.preference_weight_cap_per_event must be >= 0"
            )

    if mode == "capped" and cap is None:
        raise RunConfigError(
            f"{context}.preference_weight_cap_per_event is required when preference_weight_mode='capped'"
        )

    return {
        "preference_weight_mode": mode,
        "preference_weight_cap_per_event": cap,
    }


def _validate_bl003_seed_controls(seed_controls: Any, defaults: dict[str, Any]) -> dict[str, Any]:
    context = "run_config.seed_controls"
    if not isinstance(seed_controls, dict):
        raise RunConfigError(f"{context} must be an object")

    _validate_allowed_keys(seed_controls, set(defaults), context)
    fuzzy_defaults = dict(defaults.get("fuzzy_matching") or {})
    fuzzy_matching = seed_controls.get("fuzzy_matching")
    if fuzzy_matching is None:
        fuzzy_matching = {}
    if not isinstance(fuzzy_matching, dict):
        raise RunConfigError("run_config.seed_controls.fuzzy_matching must be an object")
    _validate_allowed_keys(fuzzy_matching, set(fuzzy_defaults), "run_config.seed_controls.fuzzy_matching")

    match_strategy_defaults = dict(defaults.get("match_strategy") or {})
    match_strategy = seed_controls.get("match_strategy")
    if match_strategy is None:
        match_strategy = {}
    if not isinstance(match_strategy, dict):
        raise RunConfigError("run_config.seed_controls.match_strategy must be an object")
    _validate_allowed_keys(match_strategy, set(match_strategy_defaults), "run_config.seed_controls.match_strategy")

    raw_match_strategy_order = seed_controls.get("match_strategy_order")
    default_match_strategy_order = list(defaults.get("match_strategy_order") or [])
    if raw_match_strategy_order is None:
        validated_match_strategy_order = list(default_match_strategy_order)
    elif not isinstance(raw_match_strategy_order, list):
        raise RunConfigError("run_config.seed_controls.match_strategy_order must be an array")
    else:
        validated_match_strategy_order = []
        seen_methods: set[str] = set()
        for item in raw_match_strategy_order:
            method = str(item).strip()
            if not method:
                continue
            if method not in BL003_ALLOWED_MATCH_METHODS:
                raise RunConfigError(
                    "run_config.seed_controls.match_strategy_order contains unsupported method "
                    f"'{method}' (allowed: {', '.join(BL003_ALLOWED_MATCH_METHODS)})"
                )
            if method in seen_methods:
                raise RunConfigError(
                    "run_config.seed_controls.match_strategy_order must not contain duplicates"
                )
            seen_methods.add(method)
            validated_match_strategy_order.append(method)
        if not validated_match_strategy_order:
            raise RunConfigError(
                "run_config.seed_controls.match_strategy_order must include at least one method"
            )

    temporal_controls = _validate_bl003_temporal_controls(
        seed_controls.get("temporal_controls"),
        dict(defaults.get("temporal_controls") or {}),
    )
    aggregation_policy = _validate_bl003_aggregation_policy(
        seed_controls.get("aggregation_policy"),
        dict(defaults.get("aggregation_policy") or {}),
    )

    source_resilience_policy = _validate_source_resilience_policy(
        seed_controls.get("source_resilience_policy"),
        dict(defaults.get("source_resilience_policy") or {}),
    )

    return {
        "match_rate_min_threshold": _validate_fraction_zero_to_one(
            seed_controls.get("match_rate_min_threshold"),
            "run_config.seed_controls.match_rate_min_threshold",
            float(defaults["match_rate_min_threshold"]),
        ),
        "top_range_weights": _validate_non_negative_float_map(
            seed_controls.get("top_range_weights"),
            dict(defaults["top_range_weights"]),
            "run_config.seed_controls.top_range_weights",
        ),
        "source_base_weights": _validate_non_negative_float_map(
            seed_controls.get("source_base_weights"),
            dict(defaults["source_base_weights"]),
            "run_config.seed_controls.source_base_weights",
        ),
        "source_resilience_policy": dict(source_resilience_policy),
        "decay_half_lives": _validate_non_negative_float_map(
            seed_controls.get("decay_half_lives"),
            dict(defaults["decay_half_lives"]),
            "run_config.seed_controls.decay_half_lives",
        ),
        "fuzzy_matching": {
            "enabled": _validate_bool_like(
                fuzzy_matching.get("enabled"),
                "run_config.seed_controls.fuzzy_matching.enabled",
                bool(fuzzy_defaults.get("enabled", False)),
            ),
            "artist_threshold": _validate_fraction_zero_to_one(
                fuzzy_matching.get("artist_threshold"),
                "run_config.seed_controls.fuzzy_matching.artist_threshold",
                float(fuzzy_defaults.get("artist_threshold", 0.90)),
            ),
            "title_threshold": _validate_fraction_zero_to_one(
                fuzzy_matching.get("title_threshold"),
                "run_config.seed_controls.fuzzy_matching.title_threshold",
                float(fuzzy_defaults.get("title_threshold", 0.90)),
            ),
            "combined_threshold": _validate_fraction_zero_to_one(
                fuzzy_matching.get("combined_threshold"),
                "run_config.seed_controls.fuzzy_matching.combined_threshold",
                float(fuzzy_defaults.get("combined_threshold", 0.90)),
            ),
            "max_duration_delta_ms": _validate_non_negative_int(
                fuzzy_matching.get("max_duration_delta_ms"),
                "run_config.seed_controls.fuzzy_matching.max_duration_delta_ms",
                int(fuzzy_defaults.get("max_duration_delta_ms", 5000)),
            ),
            "max_artist_candidates": _validate_positive_int_or_error(
                fuzzy_matching.get("max_artist_candidates"),
                "run_config.seed_controls.fuzzy_matching.max_artist_candidates",
                int(fuzzy_defaults.get("max_artist_candidates", 5)),
            ),
            "enable_album_scoring": _validate_bool_like(
                fuzzy_matching.get("enable_album_scoring"),
                "run_config.seed_controls.fuzzy_matching.enable_album_scoring",
                bool(fuzzy_defaults.get("enable_album_scoring", True)),
            ),
            "enable_secondary_artist_retry": _validate_bool_like(
                fuzzy_matching.get("enable_secondary_artist_retry"),
                "run_config.seed_controls.fuzzy_matching.enable_secondary_artist_retry",
                bool(fuzzy_defaults.get("enable_secondary_artist_retry", False)),
            ),
            "enable_relaxed_second_pass": _validate_bool_like(
                fuzzy_matching.get("enable_relaxed_second_pass"),
                "run_config.seed_controls.fuzzy_matching.enable_relaxed_second_pass",
                bool(fuzzy_defaults.get("enable_relaxed_second_pass", False)),
            ),
            "relaxed_second_pass_artist_threshold": _validate_fraction_zero_to_one(
                fuzzy_matching.get("relaxed_second_pass_artist_threshold"),
                "run_config.seed_controls.fuzzy_matching.relaxed_second_pass_artist_threshold",
                float(fuzzy_defaults.get("relaxed_second_pass_artist_threshold", 0.80)),
            ),
            "relaxed_second_pass_title_threshold": _validate_fraction_zero_to_one(
                fuzzy_matching.get("relaxed_second_pass_title_threshold"),
                "run_config.seed_controls.fuzzy_matching.relaxed_second_pass_title_threshold",
                float(fuzzy_defaults.get("relaxed_second_pass_title_threshold", 0.80)),
            ),
            "relaxed_second_pass_combined_threshold": _validate_fraction_zero_to_one(
                fuzzy_matching.get("relaxed_second_pass_combined_threshold"),
                "run_config.seed_controls.fuzzy_matching.relaxed_second_pass_combined_threshold",
                float(fuzzy_defaults.get("relaxed_second_pass_combined_threshold", 0.80)),
            ),
            "emit_fuzzy_diagnostics": _validate_bool_like(
                fuzzy_matching.get("emit_fuzzy_diagnostics"),
                "run_config.seed_controls.fuzzy_matching.emit_fuzzy_diagnostics",
                bool(fuzzy_defaults.get("emit_fuzzy_diagnostics", True)),
            ),
        },
        "match_strategy": {
            "enable_spotify_id_match": _validate_bool_like(
                match_strategy.get("enable_spotify_id_match"),
                "run_config.seed_controls.match_strategy.enable_spotify_id_match",
                bool(match_strategy_defaults.get("enable_spotify_id_match", True)),
            ),
            "enable_metadata_match": _validate_bool_like(
                match_strategy.get("enable_metadata_match"),
                "run_config.seed_controls.match_strategy.enable_metadata_match",
                bool(match_strategy_defaults.get("enable_metadata_match", True)),
            ),
            "enable_fuzzy_match": _validate_bool_like(
                match_strategy.get("enable_fuzzy_match"),
                "run_config.seed_controls.match_strategy.enable_fuzzy_match",
                bool(match_strategy_defaults.get("enable_fuzzy_match", True)),
            ),
        },
        "match_strategy_order": list(validated_match_strategy_order),
        "temporal_controls": dict(temporal_controls),
        "aggregation_policy": dict(aggregation_policy),
        "weighting_policy": _validate_bl003_weighting_policy(
            seed_controls.get("weighting_policy"),
            dict(defaults["weighting_policy"]),
        ),
    }


def _validate_source_resilience_policy(value: Any, defaults: dict[str, Any]) -> dict[str, str]:
    context = "run_config.seed_controls.source_resilience_policy"
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise RunConfigError(f"{context} must be an object")

    _validate_allowed_keys(value, set(defaults), context)

    allowed_modes = {"required", "optional", "advisory"}
    normalized: dict[str, str] = {}
    for source, default_mode in defaults.items():
        raw_mode = value.get(source, default_mode)
        mode = str(raw_mode).strip().lower()
        if mode not in allowed_modes:
            raise RunConfigError(
                f"{context}.{source} must be one of required|optional|advisory"
            )
        normalized[str(source)] = mode
    return normalized


def _validate_bl003_influence_tracks(influence_tracks: Any, defaults: dict[str, Any]) -> dict[str, Any]:
    context = "run_config.influence_tracks"
    if not isinstance(influence_tracks, dict):
        raise RunConfigError(f"{context} must be an object")

    _validate_allowed_keys(influence_tracks, set(defaults), context)
    return {
        "enabled": _validate_bool_like(
            influence_tracks.get("enabled"),
            "run_config.influence_tracks.enabled",
            bool(defaults["enabled"]),
        ),
        "track_ids": _validate_string_list(
            influence_tracks.get("track_ids"),
            "run_config.influence_tracks.track_ids",
            list(defaults["track_ids"]),
        ),
        "preference_weight": _validate_positive_float(
            influence_tracks.get("preference_weight", defaults["preference_weight"]),
            "run_config.influence_tracks.preference_weight",
        ),
        "source": _coerce_optional_str(influence_tracks.get("source")),
    }


def _build_signal_mode_summary(
    retrieval_controls: dict[str, Any],
    scoring_controls: dict[str, Any],
) -> dict[str, Any]:
    use_weighted_semantics = bool(retrieval_controls.get("use_weighted_semantics", False))
    use_continuous_numeric = bool(retrieval_controls.get("use_continuous_numeric", False))
    enable_popularity_numeric = bool(retrieval_controls.get("enable_popularity_numeric", False))
    popularity_weight = _coerce_non_negative_float(
        (scoring_controls.get("component_weights") or {}).get("popularity"),
        0.0,
    )

    if (
        not use_weighted_semantics
        and not use_continuous_numeric
        and not enable_popularity_numeric
        and popularity_weight == 0.0
    ):
        mode_name = DEFAULT_SIGNAL_MODE_NAME
    elif (
        use_weighted_semantics
        and use_continuous_numeric
        and enable_popularity_numeric
        and popularity_weight > 0.0
    ):
        mode_name = ENHANCED_SIGNAL_MODE_NAME
    else:
        mode_name = CUSTOM_SIGNAL_MODE_NAME

    return {
        "name": mode_name,
        "semantic_profile": "weighted_overlap" if use_weighted_semantics else "binary_overlap",
        "numeric_profile": "continuous_support" if use_continuous_numeric else "pass_count_support",
        "popularity_profile": {
            "retrieval_enabled": enable_popularity_numeric,
            "scoring_weight": popularity_weight,
            "scoring_enabled": popularity_weight > 0.0,
        },
    }


def _enforce_numeric_threshold_coupling(
    retrieval_thresholds: dict[str, float],
    scoring_thresholds: dict[str, float],
) -> None:
    """Ensure BL-005 and BL-006 numeric thresholds remain semantically coupled."""
    if retrieval_thresholds == scoring_thresholds:
        return

    retrieval_only = sorted(set(retrieval_thresholds) - set(scoring_thresholds))
    scoring_only = sorted(set(scoring_thresholds) - set(retrieval_thresholds))
    mismatched_values = []
    for key in sorted(set(retrieval_thresholds) & set(scoring_thresholds)):
        if retrieval_thresholds[key] != scoring_thresholds[key]:
            mismatched_values.append(
                f"{key}: retrieval={retrieval_thresholds[key]} vs scoring={scoring_thresholds[key]}"
            )

    detail_parts: list[str] = []
    if retrieval_only:
        detail_parts.append(
            "keys only in retrieval_controls.numeric_thresholds=" + ", ".join(retrieval_only)
        )
    if scoring_only:
        detail_parts.append(
            "keys only in scoring_controls.numeric_thresholds=" + ", ".join(scoring_only)
        )
    if mismatched_values:
        detail_parts.append("value mismatches=" + "; ".join(mismatched_values))

    suffix = ". " + " | ".join(detail_parts) if detail_parts else ""
    raise RunConfigError(
        "run_config numeric threshold coupling violation: "
        "retrieval_controls.numeric_thresholds must exactly match "
        "scoring_controls.numeric_thresholds"
        + suffix
    )


def _enforce_profile_retrieval_limit_constraints(
    profile_controls: dict[str, int],
    retrieval_controls: dict[str, int],
) -> None:
    """Ensure BL-005 retrieval limits never exceed BL-004 profile dimensions."""
    comparisons = [
        ("top_tag_limit", "profile_top_tag_limit"),
        ("top_genre_limit", "profile_top_genre_limit"),
        ("top_lead_genre_limit", "profile_top_lead_genre_limit"),
    ]

    violations: list[str] = []
    for profile_key, retrieval_key in comparisons:
        profile_limit = int(profile_controls[profile_key])
        retrieval_limit = int(retrieval_controls[retrieval_key])
        if retrieval_limit > profile_limit:
            violations.append(
                f"{retrieval_key}={retrieval_limit} exceeds profile_controls.{profile_key}={profile_limit}"
            )

    if violations:
        raise RunConfigError(
            "run_config profile-retrieval limit constraint violation: "
            "retrieval profile limits must be <= corresponding profile_controls limits. "
            + " | ".join(violations)
        )


def _validate_component_weights(
    component_weights: dict[str, Any] | None,
    context: str,
    *,
    tolerance: float = 0.01,
    enforce_sum: bool = True,
) -> dict[str, float]:
    """Validate scoring component weights are numeric, non-negative, and sum to 1.0 (+/- tolerance)."""
    if not component_weights:
        return {}

    validated: dict[str, float] = {}
    total = 0.0
    for key, value in component_weights.items():
        try:
            weight = float(value)
        except (TypeError, ValueError) as exc:
            raise RunConfigError(
                f"{context}: component weight '{key}' must be numeric, got {type(value).__name__}: {value!r}"
            ) from exc
        if weight < 0:
            raise RunConfigError(
                f"{context}: component weight '{key}' must be >= 0, got {weight}"
            )
        validated[str(key)] = weight
        total += weight

    if enforce_sum and abs(total - 1.0) > tolerance:
        raise RunConfigError(
            f"{context}: component weights must sum to 1.0 (+/- {tolerance}). Got {total:.6f}"
        )

    return validated


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_run_config_schema_path() -> Path | None:
    schema_path = Path(__file__).resolve().parent / "schemas" / RUN_CONFIG_SCHEMA_FILENAME
    if not schema_path.exists():
        return None
    return schema_path


def _build_run_config_schema_reference() -> dict[str, str | None]:
    schema_path = _resolve_run_config_schema_path()
    return {
        "schema_version": RUN_CONFIG_SCHEMA_VERSION,
        "schema_path": str(schema_path) if schema_path else None,
        "schema_sha256": _sha256_of_file(schema_path) if schema_path else None,
    }


def _build_runtime_environment_snapshot() -> dict[str, str | None]:
    try:
        locale_encoding = locale.getpreferredencoding(do_setlocale=False)
    except Exception:
        locale_encoding = None
    try:
        tz_name = datetime.now().astimezone().tzname()
    except Exception:
        tz_name = None
    return {
        "python_version": sys.version,
        "python_version_info": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.platform(),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "locale_preferred_encoding": locale_encoding,
        "timezone_name": tz_name,
    }


def _collect_env_override_provenance(resolved_run_config_path: Path | None) -> dict[str, dict[str, Any]]:
    provenance: dict[str, dict[str, Any]] = {}

    run_config_env_raw = os.environ.get("BL_RUN_CONFIG_PATH")
    if run_config_env_raw is not None and run_config_env_raw.strip():
        normalized = run_config_env_raw.strip()
        notes: list[str] = []
        if normalized != run_config_env_raw:
            notes.append("trimmed_surrounding_whitespace")

        normalized_path = str(Path(normalized).resolve())
        notes.append("normalized_to_absolute_path")

        applied = False
        if resolved_run_config_path is not None and normalized_path == str(resolved_run_config_path):
            applied = True
            notes.append("matches_resolved_run_config_path")

        provenance["BL_RUN_CONFIG_PATH"] = {
            "source": "environment",
            "raw_value_sha256": hashlib.sha256(run_config_env_raw.encode("utf-8")).hexdigest().upper(),
            "raw_value_length": len(run_config_env_raw),
            "normalized_value": normalized_path,
            "applied_to_effective_config": applied,
            "normalization_notes": notes,
        }

    stage_payload_raw = os.environ.get("BL_STAGE_CONFIG_JSON")
    if stage_payload_raw is not None and stage_payload_raw.strip():
        normalized = stage_payload_raw.strip()
        notes = []
        if normalized != stage_payload_raw:
            notes.append("trimmed_surrounding_whitespace")

        parsed_ok = False
        parsed_type = "unknown"
        try:
            parsed = json.loads(normalized)
            parsed_ok = True
            parsed_type = type(parsed).__name__
            notes.append(f"json_parse_ok_type={parsed_type}")
        except json.JSONDecodeError:
            notes.append("json_parse_failed")

        provenance["BL_STAGE_CONFIG_JSON"] = {
            "source": "environment",
            "raw_value_sha256": hashlib.sha256(stage_payload_raw.encode("utf-8")).hexdigest().upper(),
            "raw_value_length": len(stage_payload_raw),
            "normalized_value": normalized,
            "applied_to_effective_config": False,
            "normalization_notes": notes,
            "parse_status": {
                "ok": parsed_ok,
                "parsed_type": parsed_type,
            },
        }

    return provenance


def canonical_default_run_config() -> dict[str, Any]:
    return deepcopy(DEFAULT_RUN_CONFIG)


def load_run_config(run_config_path: str | Path | None) -> dict[str, Any] | None:
    if run_config_path is None:
        return None
    path = Path(run_config_path)
    if not path.exists():
        raise RunConfigError(f"Run config file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RunConfigError(f"Run config JSON is invalid: {path}") from exc
    if not isinstance(payload, dict):
        raise RunConfigError(f"Run config must be a JSON object: {path}")
    return payload


def _resolve_schema_version(effective: dict[str, Any]) -> None:
    schema_version = effective.get("schema_version")
    if schema_version is None:
        effective["schema_version"] = RUN_CONFIG_SCHEMA_VERSION
        return
    if schema_version != RUN_CONFIG_SCHEMA_VERSION:
        raise RunConfigError(
            f"Unsupported run config schema_version '{schema_version}'. Expected '{RUN_CONFIG_SCHEMA_VERSION}'."
        )


def _resolve_user_context_section(effective: dict[str, Any]) -> None:
    user_context = effective.setdefault("user_context", {})
    if not isinstance(user_context, dict):
        raise RunConfigError("run_config.user_context must be an object")
    user_context["user_id"] = _coerce_optional_str(user_context.get("user_id"))


def _resolve_control_mode_section(effective: dict[str, Any]) -> dict[str, Any]:
    control_mode = effective.setdefault("control_mode", {})
    if not isinstance(control_mode, dict):
        raise RunConfigError("run_config.control_mode must be an object")
    control_defaults = DEFAULT_RUN_CONFIG["control_mode"]
    control_mode["validation_profile"] = _coerce_validation_profile(
        control_mode.get("validation_profile"),
        str(control_defaults["validation_profile"]),
    )
    control_mode["allow_threshold_decoupling"] = _coerce_bool(
        control_mode.get("allow_threshold_decoupling"),
        bool(control_defaults["allow_threshold_decoupling"]),
    )
    control_mode["allow_weight_auto_normalization"] = _coerce_bool(
        control_mode.get("allow_weight_auto_normalization"),
        bool(control_defaults["allow_weight_auto_normalization"]),
    )
    return control_mode


def _resolve_input_scope_section(effective: dict[str, Any]) -> None:
    input_scope = effective.setdefault("input_scope", {})
    if not isinstance(input_scope, dict):
        raise RunConfigError("run_config.input_scope must be an object")
    input_defaults = DEFAULT_RUN_CONFIG["input_scope"]
    input_scope["source_family"] = _coerce_optional_str(
        input_scope.get("source_family")
    ) or str(input_defaults["source_family"])
    input_scope["include_top_tracks"] = _coerce_bool(
        input_scope.get("include_top_tracks"),
        bool(input_defaults["include_top_tracks"]),
    )
    input_scope["top_time_ranges"] = _normalize_allowed_tokens(
        input_scope.get("top_time_ranges"),
        {"short_term", "medium_term", "long_term"},
        list(input_defaults["top_time_ranges"]),
    )
    input_scope["include_saved_tracks"] = _coerce_bool(
        input_scope.get("include_saved_tracks"),
        bool(input_defaults["include_saved_tracks"]),
    )
    input_scope["saved_tracks_limit"] = _coerce_optional_positive_int(
        input_scope.get("saved_tracks_limit"),
        input_defaults["saved_tracks_limit"],
    )
    input_scope["include_playlists"] = _coerce_bool(
        input_scope.get("include_playlists"),
        bool(input_defaults["include_playlists"]),
    )
    input_scope["playlists_limit"] = _coerce_optional_positive_int(
        input_scope.get("playlists_limit"),
        input_defaults["playlists_limit"],
    )
    input_scope["playlist_items_per_playlist_limit"] = _coerce_optional_positive_int(
        input_scope.get("playlist_items_per_playlist_limit"),
        input_defaults["playlist_items_per_playlist_limit"],
    )
    input_scope["include_recently_played"] = _coerce_bool(
        input_scope.get("include_recently_played"),
        bool(input_defaults["include_recently_played"]),
    )
    input_scope["recently_played_limit"] = _coerce_optional_positive_int(
        input_scope.get("recently_played_limit"),
        input_defaults["recently_played_limit"],
    )
    input_scope["include_user_csv"] = _coerce_bool(
        input_scope.get("include_user_csv"),
        bool(input_defaults.get("include_user_csv", True)),
    )
    input_scope["user_csv_limit"] = _coerce_optional_positive_int(
        input_scope.get("user_csv_limit"),
        input_defaults.get("user_csv_limit", None),
    )


def _resolve_profile_controls_section(effective: dict[str, Any]) -> dict[str, Any]:
    profile_controls = effective.setdefault("profile_controls", {})
    if not isinstance(profile_controls, dict):
        raise RunConfigError("run_config.profile_controls must be an object")
    raw_profile_controls = dict(profile_controls)
    try:
        validated = validate_section(
            profile_controls,
            PROFILE_CONTROLS_SCHEMA,
            section="profile_controls",
        )
    except RunConfigSchemaError as exc:
        raise RunConfigError(str(exc)) from exc

    effective["profile_controls"] = validated
    numeric_malformed_default = _coerce_optional_positive_int(
        DEFAULT_PROFILE_CONTROLS.get("numeric_malformed_row_threshold"),
        None,
    )
    no_numeric_signal_default = _coerce_optional_positive_int(
        DEFAULT_PROFILE_CONTROLS.get("no_numeric_signal_row_threshold"),
        None,
    )
    validated["numeric_malformed_row_threshold"] = _coerce_optional_positive_int(
        raw_profile_controls.get("numeric_malformed_row_threshold"),
        numeric_malformed_default,
    )
    validated["no_numeric_signal_row_threshold"] = _coerce_optional_positive_int(
        raw_profile_controls.get("no_numeric_signal_row_threshold"),
        no_numeric_signal_default,
    )
    if float(validated["confidence_bin_medium_threshold"]) > float(validated["confidence_bin_high_threshold"]):
        raise RunConfigError(
            "profile_controls.confidence_bin_medium_threshold must be <= "
            "profile_controls.confidence_bin_high_threshold"
        )
    return validated


def _resolve_interaction_scope_section(effective: dict[str, Any]) -> None:
    interaction_scope = effective.setdefault("interaction_scope", {})
    if not isinstance(interaction_scope, dict):
        interaction_scope = {}
        effective["interaction_scope"] = interaction_scope
    interaction_scope["include_interaction_types"] = _normalize_allowed_tokens(
        interaction_scope.get("include_interaction_types"),
        {"history", "influence"},
        list(DEFAULT_INCLUDE_INTERACTION_TYPES),
    )


def _resolve_influence_tracks_section(effective: dict[str, Any]) -> None:
    influence_tracks = effective.setdefault("influence_tracks", {})
    if not isinstance(influence_tracks, dict):
        influence_tracks = {}
        effective["influence_tracks"] = influence_tracks
    influence_defaults = DEFAULT_RUN_CONFIG["influence_tracks"]
    effective["influence_tracks"] = _validate_bl003_influence_tracks(
        influence_tracks,
        influence_defaults,
    )


def _resolve_seed_controls_section(effective: dict[str, Any]) -> None:
    seed_controls = effective.setdefault("seed_controls", {})
    seed_defaults = DEFAULT_RUN_CONFIG["seed_controls"]
    effective["seed_controls"] = _validate_bl003_seed_controls(seed_controls, seed_defaults)


def _resolve_ingestion_controls_section(effective: dict[str, Any]) -> None:
    ingestion_controls = effective.setdefault("ingestion_controls", {})
    if not isinstance(ingestion_controls, dict):
        raise RunConfigError("run_config.ingestion_controls must be an object")
    ingestion_defaults = DEFAULT_RUN_CONFIG["ingestion_controls"]
    ingestion_controls["cache_ttl_seconds"] = _coerce_positive_int(
        ingestion_controls.get("cache_ttl_seconds"),
        ingestion_defaults["cache_ttl_seconds"],
    )
    ingestion_controls["throttle_sleep_seconds"] = _coerce_min_positive_float(
        ingestion_controls.get("throttle_sleep_seconds"),
        float(ingestion_defaults["throttle_sleep_seconds"]),
    )
    ingestion_controls["max_retries"] = _coerce_positive_int(
        ingestion_controls.get("max_retries"),
        ingestion_defaults["max_retries"],
    )
    ingestion_controls["base_backoff_delay_seconds"] = _coerce_min_positive_float(
        ingestion_controls.get("base_backoff_delay_seconds"),
        float(ingestion_defaults["base_backoff_delay_seconds"]),
    )


def _resolve_controllability_controls_section(effective: dict[str, Any]) -> None:
    controllability_controls = effective.setdefault("controllability_controls", {})
    if not isinstance(controllability_controls, dict):
        raise RunConfigError("run_config.controllability_controls must be an object")
    controllability_defaults = DEFAULT_RUN_CONFIG["controllability_controls"]
    controllability_controls["weight_override_value_if_component_present"] = _validate_positive_float(
        controllability_controls.get(
            "weight_override_value_if_component_present",
            controllability_defaults["weight_override_value_if_component_present"],
        ),
        "controllability_controls.weight_override_value_if_component_present",
    )
    controllability_controls["weight_override_increment_fallback"] = _validate_positive_float(
        controllability_controls.get(
            "weight_override_increment_fallback",
            controllability_defaults["weight_override_increment_fallback"],
        ),
        "controllability_controls.weight_override_increment_fallback",
    )
    controllability_controls["weight_override_cap_fallback"] = _validate_positive_float(
        controllability_controls.get(
            "weight_override_cap_fallback",
            controllability_defaults["weight_override_cap_fallback"],
        ),
        "controllability_controls.weight_override_cap_fallback",
    )
    controllability_controls["stricter_threshold_scale"] = _validate_positive_float(
        controllability_controls.get(
            "stricter_threshold_scale",
            controllability_defaults["stricter_threshold_scale"],
        ),
        "controllability_controls.stricter_threshold_scale",
    )
    controllability_controls["looser_threshold_scale"] = _validate_positive_float(
        controllability_controls.get(
            "looser_threshold_scale",
            controllability_defaults["looser_threshold_scale"],
        ),
        "controllability_controls.looser_threshold_scale",
    )


def _resolve_retrieval_controls_section(effective: dict[str, Any]) -> dict[str, Any]:
    retrieval_controls = effective.setdefault("retrieval_controls", {})
    if not isinstance(retrieval_controls, dict):
        raise RunConfigError("run_config.retrieval_controls must be an object")
    retrieval_defaults = DEFAULT_RUN_CONFIG["retrieval_controls"]
    try:
        retrieval_controls.update(
            validate_section(
                retrieval_controls,
                RETRIEVAL_CONTROLS_SCHEMA,
                section="retrieval_controls",
            )
        )
    except RunConfigSchemaError as exc:
        raise RunConfigError(str(exc)) from exc

    retrieval_controls["language_filter_enabled"] = _coerce_bool(
        retrieval_controls.get("language_filter_enabled"),
        bool(retrieval_defaults["language_filter_enabled"]),
    )
    retrieval_controls["language_filter_codes"] = _normalize_string_tokens(
        retrieval_controls.get("language_filter_codes"),
        list(retrieval_defaults["language_filter_codes"]),
    )
    retrieval_controls["recency_years_min_offset"] = _coerce_optional_positive_int(
        retrieval_controls.get("recency_years_min_offset"),
        retrieval_defaults["recency_years_min_offset"],
    )
    return retrieval_controls


def _resolve_scoring_controls_section(
    effective: dict[str, Any],
    retrieval_controls: dict[str, Any],
    profile_controls: dict[str, Any],
    control_mode: dict[str, Any],
) -> None:
    scoring_controls = effective.setdefault("scoring_controls", {})
    if not isinstance(scoring_controls, dict):
        raise RunConfigError("run_config.scoring_controls must be an object")
    scoring_defaults = DEFAULT_RUN_CONFIG["scoring_controls"]
    try:
        scoring_controls.update(
            validate_section(
                scoring_controls,
                SCORING_CONTROLS_SCHEMA,
                section="scoring_controls",
            )
        )
    except RunConfigSchemaError as exc:
        raise RunConfigError(str(exc)) from exc

    validated_component_weights = _validate_component_weights(
        scoring_controls.get("component_weights") or scoring_defaults["component_weights"],
        "scoring_controls.component_weights",
        enforce_sum=not bool(control_mode["allow_weight_auto_normalization"]),
    )
    scoring_controls["component_weights"] = validated_component_weights

    retrieval_thresholds = _validate_positive_thresholds(
        retrieval_controls.get("numeric_thresholds") or DEFAULT_RUN_CONFIG["retrieval_controls"]["numeric_thresholds"],
        "retrieval_controls.numeric_thresholds",
    )
    scoring_thresholds = _validate_positive_thresholds(
        scoring_controls.get("numeric_thresholds") or DEFAULT_RUN_CONFIG["scoring_controls"]["numeric_thresholds"],
        "scoring_controls.numeric_thresholds",
    )
    if not bool(control_mode["allow_threshold_decoupling"]):
        _enforce_numeric_threshold_coupling(retrieval_thresholds, scoring_thresholds)
    retrieval_controls["numeric_thresholds"] = retrieval_thresholds
    scoring_controls["numeric_thresholds"] = scoring_thresholds
    scoring_controls["influence_track_bonus_scale"] = _coerce_non_negative_float(
        scoring_controls.get("influence_track_bonus_scale"),
        float(scoring_defaults["influence_track_bonus_scale"]),
    )
    _enforce_profile_retrieval_limit_constraints(profile_controls, retrieval_controls)
    effective["signal_mode"] = _build_signal_mode_summary(retrieval_controls, scoring_controls)


def _resolve_observability_controls_section(effective: dict[str, Any]) -> None:
    observability_controls = effective.setdefault("observability_controls", {})
    if not isinstance(observability_controls, dict):
        raise RunConfigError("run_config.observability_controls must be an object")
    observability_defaults = DEFAULT_RUN_CONFIG["observability_controls"]
    try:
        observability_controls.update(
            validate_section(
                observability_controls,
                OBSERVABILITY_CONTROLS_SCHEMA,
                section="observability_controls",
            )
        )
    except RunConfigSchemaError as exc:
        raise RunConfigError(str(exc)) from exc

    observability_controls["bootstrap_mode"] = _coerce_bool(
        observability_controls.get("bootstrap_mode"),
        bool(observability_defaults["bootstrap_mode"]),
    )


def _resolve_transparency_controls_section(effective: dict[str, Any]) -> None:
    transparency_controls = effective.setdefault("transparency_controls", {})
    if not isinstance(transparency_controls, dict):
        raise RunConfigError("run_config.transparency_controls must be an object")
    transparency_defaults = DEFAULT_RUN_CONFIG["transparency_controls"]
    try:
        transparency_controls.update(
            validate_section(
                transparency_controls,
                TRANSPARENCY_CONTROLS_SCHEMA,
                section="transparency_controls",
            )
        )
    except RunConfigSchemaError as exc:
        raise RunConfigError(str(exc)) from exc

    transparency_controls["blend_primary_contributor_on_near_tie"] = _coerce_bool(
        transparency_controls.get("blend_primary_contributor_on_near_tie"),
        bool(transparency_defaults["blend_primary_contributor_on_near_tie"]),
    )


def _enforce_strict_validation_profile_handshake_policies(effective: dict[str, Any]) -> None:
    control_mode = effective.get("control_mode")
    if not isinstance(control_mode, dict):
        return
    if str(control_mode.get("validation_profile", "")).strip().lower() != "strict":
        return

    profile_controls = effective.setdefault("profile_controls", {})
    if isinstance(profile_controls, dict):
        profile_controls["bl003_handshake_validation_policy"] = "strict"

    retrieval_controls = effective.setdefault("retrieval_controls", {})
    if isinstance(retrieval_controls, dict):
        retrieval_controls["bl004_bl005_handshake_validation_policy"] = "strict"

    scoring_controls = effective.setdefault("scoring_controls", {})
    if isinstance(scoring_controls, dict):
        scoring_controls["bl005_bl006_handshake_validation_policy"] = "strict"

    assembly_controls = effective.setdefault("assembly_controls", {})
    if isinstance(assembly_controls, dict):
        assembly_controls["bl006_bl007_handshake_validation_policy"] = "strict"

    transparency_controls = effective.setdefault("transparency_controls", {})
    if isinstance(transparency_controls, dict):
        transparency_controls["bl007_bl008_handshake_validation_policy"] = "strict"

    observability_controls = effective.setdefault("observability_controls", {})
    if isinstance(observability_controls, dict):
        observability_controls["bl008_bl009_handshake_validation_policy"] = "strict"

    reproducibility_controls = effective.setdefault("reproducibility_controls", {})
    if isinstance(reproducibility_controls, dict):
        reproducibility_controls["bl009_bl010_handshake_validation_policy"] = "strict"

    controllability_controls = effective.setdefault("controllability_controls", {})
    if isinstance(controllability_controls, dict):
        controllability_controls["bl010_bl011_handshake_validation_policy"] = "strict"


def resolve_effective_run_config(run_config_path: str | Path | None) -> tuple[dict[str, Any], Path | None]:
    path = Path(run_config_path).resolve() if run_config_path else None
    payload = load_run_config(path) if path else None
    if payload is None:
        effective = canonical_default_run_config()
    else:
        effective = _deep_merge(canonical_default_run_config(), payload)

    _resolve_schema_version(effective)
    _resolve_user_context_section(effective)
    control_mode = _resolve_control_mode_section(effective)
    _resolve_input_scope_section(effective)

    profile_controls = _resolve_profile_controls_section(effective)
    _resolve_interaction_scope_section(effective)
    _resolve_influence_tracks_section(effective)
    _resolve_seed_controls_section(effective)

    _resolve_ingestion_controls_section(effective)
    _resolve_controllability_controls_section(effective)
    retrieval_controls = _resolve_retrieval_controls_section(effective)
    _resolve_scoring_controls_section(effective, retrieval_controls, profile_controls, control_mode)

    _resolve_observability_controls_section(effective)
    _resolve_transparency_controls_section(effective)
    _enforce_strict_validation_profile_handshake_policies(effective)

    return effective, path


def resolve_bl004_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    user_context = effective["user_context"]
    profile_controls = effective["profile_controls"]
    interaction_scope = effective["interaction_scope"]
    influence = effective["influence_tracks"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "user_id": user_context.get("user_id"),
        "input_scope": dict(effective["input_scope"]),
        "top_tag_limit": profile_controls["top_tag_limit"],
        "top_genre_limit": profile_controls["top_genre_limit"],
        "top_lead_genre_limit": profile_controls["top_lead_genre_limit"],
        "confidence_weighting_mode": profile_controls["confidence_weighting_mode"],
        "confidence_bin_high_threshold": float(profile_controls["confidence_bin_high_threshold"]),
        "confidence_bin_medium_threshold": float(profile_controls["confidence_bin_medium_threshold"]),
        "interaction_attribution_mode": profile_controls["interaction_attribution_mode"],
        "emit_profile_policy_diagnostics": bool(profile_controls["emit_profile_policy_diagnostics"]),
        "confidence_validation_policy": profile_controls["confidence_validation_policy"],
        "interaction_type_validation_policy": profile_controls["interaction_type_validation_policy"],
        "synthetic_data_validation_policy": profile_controls["synthetic_data_validation_policy"],
        "bl003_handshake_validation_policy": profile_controls["bl003_handshake_validation_policy"],
        "numeric_malformed_row_threshold": profile_controls["numeric_malformed_row_threshold"],
        "no_numeric_signal_row_threshold": profile_controls["no_numeric_signal_row_threshold"],
        "include_interaction_types": list(interaction_scope["include_interaction_types"]),
        "influence_enabled": bool(influence["enabled"]),
        "influence_track_ids": list(influence["track_ids"]),
        "influence_preference_weight": float(influence["preference_weight"]),
    }


def resolve_input_scope_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "input_scope": dict(effective["input_scope"]),
    }


def resolve_bl003_influence_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    influence = effective["influence_tracks"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "influence_enabled": bool(influence["enabled"]),
        "influence_track_ids": list(influence["track_ids"]),
        "influence_preference_weight": float(influence["preference_weight"]),
    }


def resolve_bl003_seed_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    seed = effective["seed_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "match_rate_min_threshold": float(seed["match_rate_min_threshold"]),
        "top_range_weights": dict(seed["top_range_weights"]),
        "source_base_weights": dict(seed["source_base_weights"]),
        "source_resilience_policy": dict(seed.get("source_resilience_policy") or {}),
        "decay_half_lives": dict(seed.get("decay_half_lives") or {}),
        "fuzzy_matching": dict(seed.get("fuzzy_matching") or {}),
        "match_strategy": dict(seed.get("match_strategy") or {}),
        "match_strategy_order": list(seed.get("match_strategy_order") or []),
        "temporal_controls": dict(seed.get("temporal_controls") or {}),
        "aggregation_policy": dict(seed.get("aggregation_policy") or {}),
    }


def resolve_ingestion_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    ingestion = effective["ingestion_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "cache_ttl_seconds": int(ingestion["cache_ttl_seconds"]),
        "throttle_sleep_seconds": float(ingestion["throttle_sleep_seconds"]),
        "max_retries": int(ingestion["max_retries"]),
        "base_backoff_delay_seconds": float(ingestion["base_backoff_delay_seconds"]),
    }


def resolve_bl011_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    controls = effective["controllability_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "bl010_bl011_handshake_validation_policy": str(
            controls.get("bl010_bl011_handshake_validation_policy", "warn")
        ),
        "weight_override_value_if_component_present": float(controls["weight_override_value_if_component_present"]),
        "weight_override_increment_fallback": float(controls["weight_override_increment_fallback"]),
        "weight_override_cap_fallback": float(controls["weight_override_cap_fallback"]),
        "stricter_threshold_scale": float(controls["stricter_threshold_scale"]),
        "looser_threshold_scale": float(controls["looser_threshold_scale"]),
    }


def resolve_bl011_scenario_policy(run_config_path: str | Path | None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Resolve BL-011 scenario policy and scenario definitions from run config.

    Returns:
        (scenario_policy_dict, scenario_definitions_list)
        scenario_policy keys: enabled_scenario_ids, repeat_count, stage_scope, comparison_mode
        scenario_definitions_list: list of scenario definition dicts (may be empty; Phase 2
            populates built-in defaults when the list is empty).
    """
    effective, _ = resolve_effective_run_config(run_config_path)
    controls = effective["controllability_controls"]
    default_policy = DEFAULT_RUN_CONFIG["controllability_controls"]["scenario_policy"]

    raw_policy = controls.get("scenario_policy") or {}
    policy: dict[str, Any] = {
        "enabled_scenario_ids": _normalize_string_tokens(
            raw_policy.get("enabled_scenario_ids"),
            list(default_policy["enabled_scenario_ids"]),
        ),
        "repeat_count": _coerce_positive_int(
            raw_policy.get("repeat_count"), default_policy["repeat_count"]
        ),
        "stage_scope": _normalize_string_tokens(
            raw_policy.get("stage_scope"), list(default_policy["stage_scope"])
        ),
        "comparison_mode": str(raw_policy.get("comparison_mode") or default_policy["comparison_mode"]),
    }

    raw_definitions = controls.get("scenario_definitions")
    definitions: list[dict[str, Any]] = list(raw_definitions) if raw_definitions else []

    return policy, definitions


def resolve_bl003_weighting_policy(run_config_path: str | Path | None) -> dict[str, Any]:
    """Resolve BL-003 weighting policy knobs from run config.

    Returns a flat dict of formula constants used by alignment/weighting.py:
        top_tracks_min_rank_floor, top_tracks_scale_multiplier,
        top_tracks_default_time_range_weight,
        playlist_items_min_position_floor, playlist_items_scale_multiplier.
    Defaults match the values previously embedded in alignment/weighting.py
    so there is no behavioral change until the caller switches over.
    """
    effective, _ = resolve_effective_run_config(run_config_path)
    seed = effective["seed_controls"]
    weighting_policy = seed.get("weighting_policy") or {}
    top_tracks = weighting_policy.get("top_tracks") or {}
    playlist_items = weighting_policy.get("playlist_items") or {}

    return {
        "top_tracks_min_rank_floor": float(top_tracks["min_rank_floor"]),
        "top_tracks_scale_multiplier": float(top_tracks["scale_multiplier"]),
        "top_tracks_default_time_range_weight": float(top_tracks["default_time_range_weight"]),
        "playlist_items_min_position_floor": float(playlist_items["min_position_floor"]),
        "playlist_items_scale_multiplier": float(playlist_items["scale_multiplier"]),
    }


def resolve_bl005_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    retrieval = effective["retrieval_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "signal_mode": dict(effective.get("signal_mode") or {}),
        "profile_top_lead_genre_limit": int(retrieval["profile_top_lead_genre_limit"]),
        "profile_top_tag_limit": int(retrieval["profile_top_tag_limit"]),
        "profile_top_genre_limit": int(retrieval["profile_top_genre_limit"]),
        "semantic_strong_keep_score": int(retrieval["semantic_strong_keep_score"]),
        "semantic_min_keep_score": int(retrieval["semantic_min_keep_score"]),
        "numeric_support_min_pass": int(retrieval["numeric_support_min_pass"]),
        "numeric_support_min_score": float(retrieval["numeric_support_min_score"]),
        "use_weighted_semantics": bool(retrieval["use_weighted_semantics"]),
        "use_continuous_numeric": bool(retrieval["use_continuous_numeric"]),
        "enable_popularity_numeric": bool(retrieval["enable_popularity_numeric"]),
        "language_filter_enabled": bool(retrieval["language_filter_enabled"]),
        "language_filter_codes": list(retrieval["language_filter_codes"]),
        "recency_years_min_offset": retrieval["recency_years_min_offset"],
        "numeric_thresholds": _validate_positive_thresholds(
            retrieval.get("numeric_thresholds") or {},
            "retrieval_controls.numeric_thresholds"
        ),
        "profile_quality_penalty_enabled": bool(retrieval["profile_quality_penalty_enabled"]),
        "profile_quality_threshold": float(retrieval["profile_quality_threshold"]),
        "profile_entropy_low_threshold": float(retrieval["profile_entropy_low_threshold"]),
        "influence_share_threshold": float(retrieval["influence_share_threshold"]),
        "profile_quality_penalty_increment": float(retrieval["profile_quality_penalty_increment"]),
        "profile_entropy_penalty_increment": float(retrieval["profile_entropy_penalty_increment"]),
        "influence_share_penalty_increment": float(retrieval["influence_share_penalty_increment"]),
        "numeric_penalty_scale": float(retrieval["numeric_penalty_scale"]),
        "semantic_overlap_damping_mid_entropy_threshold": float(retrieval["semantic_overlap_damping_mid_entropy_threshold"]),
        "semantic_overlap_damping_low_entropy": float(retrieval["semantic_overlap_damping_low_entropy"]),
        "semantic_overlap_damping_mid_entropy": float(retrieval["semantic_overlap_damping_mid_entropy"]),
        "enable_numeric_confidence_scaling": bool(retrieval["enable_numeric_confidence_scaling"]),
        "numeric_confidence_floor": float(retrieval["numeric_confidence_floor"]),
        "profile_numeric_confidence_mode": str(retrieval["profile_numeric_confidence_mode"]),
        "profile_numeric_confidence_blend_weight": float(retrieval["profile_numeric_confidence_blend_weight"]),
        "numeric_support_score_mode": str(retrieval["numeric_support_score_mode"]),
        "emit_profile_policy_diagnostics": bool(retrieval["emit_profile_policy_diagnostics"]),
        "bl004_bl005_handshake_validation_policy": str(
            retrieval["bl004_bl005_handshake_validation_policy"]
        ),
    }


def resolve_bl006_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    scoring = effective["scoring_controls"]
    control_mode = effective.get("control_mode") or {}
    component_weights = _validate_component_weights(
        scoring.get("component_weights") or {},
        "scoring_controls.component_weights",
        enforce_sum=not bool(control_mode.get("allow_weight_auto_normalization", False)),
    )
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "signal_mode": dict(effective.get("signal_mode") or {}),
        "component_weights": component_weights,
        "numeric_thresholds": _validate_positive_thresholds(
            scoring.get("numeric_thresholds") or {},
            "scoring_controls.numeric_thresholds"
        ),
        "lead_genre_strategy": str(scoring["lead_genre_strategy"]),
        "semantic_overlap_strategy": str(scoring["semantic_overlap_strategy"]),
        "semantic_precision_alpha_mode": str(scoring["semantic_precision_alpha_mode"]),
        "semantic_precision_alpha_fixed": float(scoring["semantic_precision_alpha_fixed"]),
        "enable_numeric_confidence_scaling": bool(scoring["enable_numeric_confidence_scaling"]),
        "numeric_confidence_floor": float(scoring["numeric_confidence_floor"]),
        "profile_numeric_confidence_mode": str(scoring["profile_numeric_confidence_mode"]),
        "profile_numeric_confidence_blend_weight": float(scoring["profile_numeric_confidence_blend_weight"]),
        "emit_confidence_impact_diagnostics": bool(scoring["emit_confidence_impact_diagnostics"]),
        "emit_semantic_precision_diagnostics": bool(scoring["emit_semantic_precision_diagnostics"]),
        "apply_bl003_influence_tracks": bool(scoring["apply_bl003_influence_tracks"]),
        "influence_track_bonus_scale": float(scoring["influence_track_bonus_scale"]),
        "bl005_bl006_handshake_validation_policy": str(
            scoring["bl005_bl006_handshake_validation_policy"]
        ),
    }


def _resolve_bl007_enum(
    value: Any,
    *,
    default_value: Any,
    allowed: set[str],
) -> str:
    normalized = str(value or default_value).strip().lower()
    default_normalized = str(default_value)
    return normalized if normalized in allowed else default_normalized


def _resolve_bl007_utility_weights(
    assembly: dict[str, Any],
    defaults: dict[str, Any],
) -> dict[str, float]:
    utility_weights_raw = assembly.get("utility_weights")
    utility_weights_defaults = defaults.get("utility_weights") or {}
    return {
        "score_weight": _coerce_non_negative_float(
            (utility_weights_raw or {}).get("score_weight") if isinstance(utility_weights_raw, dict) else None,
            float(utility_weights_defaults.get("score_weight", 1.0)),
        ),
        "novelty_weight": _coerce_non_negative_float(
            (utility_weights_raw or {}).get("novelty_weight") if isinstance(utility_weights_raw, dict) else None,
            float(utility_weights_defaults.get("novelty_weight", 0.0)),
        ),
        "repetition_penalty_weight": _coerce_non_negative_float(
            (utility_weights_raw or {}).get("repetition_penalty_weight") if isinstance(utility_weights_raw, dict) else None,
            float(utility_weights_defaults.get("repetition_penalty_weight", 0.0)),
        ),
    }


def _resolve_bl007_adaptive_limits(
    assembly: dict[str, Any],
    defaults: dict[str, Any],
) -> dict[str, Any]:
    adaptive_limits_raw = assembly.get("adaptive_limits")
    adaptive_defaults = defaults.get("adaptive_limits") or {}
    adaptive_limits = {
        "enabled": _coerce_bool(
            (adaptive_limits_raw or {}).get("enabled") if isinstance(adaptive_limits_raw, dict) else None,
            bool(adaptive_defaults.get("enabled", False)),
        ),
        "reference_top_k": _coerce_positive_int(
            (adaptive_limits_raw or {}).get("reference_top_k") if isinstance(adaptive_limits_raw, dict) else None,
            int(adaptive_defaults.get("reference_top_k", 100)),
        ),
        "max_per_genre_scale_min": _coerce_non_negative_float(
            (adaptive_limits_raw or {}).get("max_per_genre_scale_min") if isinstance(adaptive_limits_raw, dict) else None,
            float(adaptive_defaults.get("max_per_genre_scale_min", 0.75)),
        ),
        "max_per_genre_scale_max": _coerce_non_negative_float(
            (adaptive_limits_raw or {}).get("max_per_genre_scale_max") if isinstance(adaptive_limits_raw, dict) else None,
            float(adaptive_defaults.get("max_per_genre_scale_max", 1.25)),
        ),
    }
    if adaptive_limits["max_per_genre_scale_max"] < adaptive_limits["max_per_genre_scale_min"]:
        adaptive_limits["max_per_genre_scale_max"] = adaptive_limits["max_per_genre_scale_min"]
    return adaptive_limits


def _resolve_bl007_controlled_relaxation(
    assembly: dict[str, Any],
    defaults: dict[str, Any],
) -> dict[str, Any]:
    relaxation_raw = assembly.get("controlled_relaxation")
    relaxation_defaults = defaults.get("controlled_relaxation") or {}
    return {
        "enabled": _coerce_bool(
            (relaxation_raw or {}).get("enabled") if isinstance(relaxation_raw, dict) else None,
            bool(relaxation_defaults.get("enabled", False)),
        ),
        "relax_consecutive_first": _coerce_bool(
            (relaxation_raw or {}).get("relax_consecutive_first") if isinstance(relaxation_raw, dict) else None,
            bool(relaxation_defaults.get("relax_consecutive_first", True)),
        ),
        "max_per_genre_increment": _coerce_positive_int(
            (relaxation_raw or {}).get("max_per_genre_increment") if isinstance(relaxation_raw, dict) else None,
            int(relaxation_defaults.get("max_per_genre_increment", 1)),
        ),
        "max_relaxation_rounds": _coerce_positive_int(
            (relaxation_raw or {}).get("max_relaxation_rounds") if isinstance(relaxation_raw, dict) else None,
            int(relaxation_defaults.get("max_relaxation_rounds", 2)),
        ),
        "never_relax_score_threshold": _coerce_bool(
            (relaxation_raw or {}).get("never_relax_score_threshold") if isinstance(relaxation_raw, dict) else None,
            bool(relaxation_defaults.get("never_relax_score_threshold", True)),
        ),
    }


def resolve_bl007_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    assembly = effective["assembly_controls"]
    influence = effective["influence_tracks"]
    defaults = DEFAULT_RUN_CONFIG["assembly_controls"]
    min_threshold = assembly.get("min_score_threshold")
    utility_strategy = _resolve_bl007_enum(
        assembly.get("utility_strategy"),
        default_value=defaults["utility_strategy"],
        allowed={"rank_round_robin", "utility_greedy"},
    )
    utility_weights = _resolve_bl007_utility_weights(assembly, defaults)
    adaptive_limits = _resolve_bl007_adaptive_limits(assembly, defaults)
    controlled_relaxation = _resolve_bl007_controlled_relaxation(assembly, defaults)
    lead_genre_fallback_strategy = _resolve_bl007_enum(
        assembly.get("lead_genre_fallback_strategy"),
        default_value=defaults.get("lead_genre_fallback_strategy", "none"),
        allowed={"none", "semantic_component_proxy"},
    )
    influence_policy_mode = _resolve_bl007_enum(
        assembly.get("influence_policy_mode"),
        default_value=defaults.get("influence_policy_mode", "competitive"),
        allowed={"competitive", "reserved_slots", "hybrid_override"},
    )

    target_size = _coerce_positive_int(
        assembly.get("target_size"),
        defaults["target_size"],
    )
    influence_reserved_slots = _validate_non_negative_int(
        assembly.get("influence_reserved_slots"),
        "assembly_controls.influence_reserved_slots",
        int(defaults.get("influence_reserved_slots", 0)),
    )
    if influence_reserved_slots > target_size:
        influence_reserved_slots = target_size

    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "target_size": target_size,
        "min_score_threshold": _validate_positive_float(
            min_threshold if min_threshold is not None else defaults["min_score_threshold"],
            "assembly_controls.min_score_threshold"
        ),
        "max_per_genre": _coerce_positive_int(
            assembly.get("max_per_genre"),
            defaults["max_per_genre"],
        ),
        "max_consecutive": _coerce_positive_int(
            assembly.get("max_consecutive"),
            defaults["max_consecutive"],
        ),
        "novelty_allowance": _validate_non_negative_int(
            assembly.get("novelty_allowance"),
            "assembly_controls.novelty_allowance",
            int(defaults.get("novelty_allowance", 0)),
        ),
        "utility_strategy": utility_strategy,
        "utility_decay_factor": _coerce_fraction_zero_to_one(
            assembly.get("utility_decay_factor"),
            float(defaults.get("utility_decay_factor", 0.0)),
        ),
        "utility_weights": utility_weights,
        "adaptive_limits": adaptive_limits,
        "controlled_relaxation": controlled_relaxation,
        "lead_genre_fallback_strategy": lead_genre_fallback_strategy,
        "use_component_contributions_for_tiebreak": _coerce_bool(
            assembly.get("use_component_contributions_for_tiebreak"),
            bool(defaults.get("use_component_contributions_for_tiebreak", False)),
        ),
        "use_semantic_strength_for_tiebreak": _coerce_bool(
            assembly.get("use_semantic_strength_for_tiebreak"),
            bool(defaults.get("use_semantic_strength_for_tiebreak", False)),
        ),
        "emit_opportunity_cost_metrics": _coerce_bool(
            assembly.get("emit_opportunity_cost_metrics"),
            bool(defaults.get("emit_opportunity_cost_metrics", False)),
        ),
        "opportunity_cost_top_k_examples": _coerce_positive_int(
            assembly.get("opportunity_cost_top_k_examples"),
            int(defaults.get("opportunity_cost_top_k_examples", 10)),
        ),
        "detail_log_top_k": _coerce_positive_int(
            assembly.get("detail_log_top_k"),
            int(defaults.get("detail_log_top_k", 100)),
        ),
        "influence_enabled": _coerce_bool(
            influence.get("enabled"),
            bool(DEFAULT_RUN_CONFIG["influence_tracks"]["enabled"]),
        ),
        "influence_track_ids": _validate_string_list(
            influence.get("track_ids"),
            "run_config.influence_tracks.track_ids",
            list(DEFAULT_RUN_CONFIG["influence_tracks"]["track_ids"]),
        ),
        "influence_policy_mode": influence_policy_mode,
        "influence_reserved_slots": influence_reserved_slots,
        "influence_allow_genre_cap_override": _coerce_bool(
            assembly.get("influence_allow_genre_cap_override"),
            bool(defaults.get("influence_allow_genre_cap_override", False)),
        ),
        "influence_allow_consecutive_override": _coerce_bool(
            assembly.get("influence_allow_consecutive_override"),
            bool(defaults.get("influence_allow_consecutive_override", False)),
        ),
        "influence_allow_score_threshold_override": _coerce_bool(
            assembly.get("influence_allow_score_threshold_override"),
            bool(defaults.get("influence_allow_score_threshold_override", False)),
        ),
        "bl006_bl007_handshake_validation_policy": str(
            assembly.get("bl006_bl007_handshake_validation_policy")
            or defaults.get("bl006_bl007_handshake_validation_policy", "warn")
        ),
    }


def resolve_bl008_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    transparency = effective["transparency_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "top_contributor_limit": int(transparency["top_contributor_limit"]),
        "blend_primary_contributor_on_near_tie": bool(transparency["blend_primary_contributor_on_near_tie"]),
        "primary_contributor_tie_delta": float(transparency["primary_contributor_tie_delta"]),
        "bl007_bl008_handshake_validation_policy": str(
            transparency.get("bl007_bl008_handshake_validation_policy", "warn")
        ),
    }


def resolve_bl009_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    observability = effective["observability_controls"]
    control_mode = effective.get("control_mode") or {}
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "control_mode": {
            "validation_profile": str(control_mode.get("validation_profile", "strict")),
            "allow_threshold_decoupling": bool(control_mode.get("allow_threshold_decoupling", False)),
            "allow_weight_auto_normalization": bool(control_mode.get("allow_weight_auto_normalization", False)),
        },
        "diagnostic_sample_limit": int(observability["diagnostic_sample_limit"]),
        "bootstrap_mode": bool(observability["bootstrap_mode"]),
        "bl008_bl009_handshake_validation_policy": str(
            observability["bl008_bl009_handshake_validation_policy"]
        ),
    }


def resolve_bl010_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    reproducibility = effective.get("reproducibility_controls") or {}
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "bl009_bl010_handshake_validation_policy": str(
            reproducibility.get("bl009_bl010_handshake_validation_policy", "warn")
        ),
    }


def resolve_bl011_controls_extended(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    controllability = effective.get("controllability_controls") or {}
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "bl010_bl011_handshake_validation_policy": str(
            controllability.get("bl010_bl011_handshake_validation_policy", "warn")
        ),
        "weight_override_value_if_component_present": float(controllability.get("weight_override_value_if_component_present", 1.0)),
        "weight_override_increment_fallback": float(controllability.get("weight_override_increment_fallback", 0.05)),
        "weight_override_cap_fallback": float(controllability.get("weight_override_cap_fallback", 0.5)),
        "stricter_threshold_scale": float(controllability.get("stricter_threshold_scale", 1.1)),
        "looser_threshold_scale": float(controllability.get("looser_threshold_scale", 0.9)),
    }


def resolve_bl013_orchestration_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    raw = effective.get("orchestration_controls") or {}
    if not isinstance(raw, dict):
        raw = {}
    merged: dict[str, Any] = {**DEFAULT_ORCHESTRATION_CONTROLS, **raw}
    raw_stage_order = merged.get("stage_order")
    stage_order: list[str] | None = list(raw_stage_order) if isinstance(raw_stage_order, list) else None
    refresh_seed_policy = str(merged.get("refresh_seed_policy") or "auto_if_stale").strip().lower()
    if refresh_seed_policy not in {"auto_if_stale", "always", "never"}:
        refresh_seed_policy = str(DEFAULT_ORCHESTRATION_CONTROLS["refresh_seed_policy"])
    replay_count = _coerce_positive_int(
        merged.get("determinism_verify_replay_count"),
        int(DEFAULT_ORCHESTRATION_CONTROLS["determinism_verify_replay_count"]),
    )
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "stage_order": stage_order,
        "continue_on_error": _coerce_bool(
            merged.get("continue_on_error"),
            bool(DEFAULT_ORCHESTRATION_CONTROLS["continue_on_error"]),
        ),
        "refresh_seed_policy": refresh_seed_policy,
        "required_stable_artifacts": _validate_string_list(
            merged.get("required_stable_artifacts"),
            "orchestration_controls.required_stable_artifacts",
            list(DEFAULT_ORCHESTRATION_CONTROLS["required_stable_artifacts"]),
        ),
        "determinism_verify_on_success": _coerce_bool(
            merged.get("determinism_verify_on_success"),
            bool(DEFAULT_ORCHESTRATION_CONTROLS["determinism_verify_on_success"]),
        ),
        "determinism_verify_replay_count": replay_count,
    }


def build_run_intent_payload(
    run_id: str,
    run_config_path: str | Path | None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    resolved_path = Path(run_config_path).resolve() if run_config_path else None
    payload = load_run_config(resolved_path) if resolved_path else None
    requested_config = deepcopy(payload) if payload is not None else canonical_default_run_config()
    if requested_config.get("schema_version") is None:
        requested_config["schema_version"] = RUN_CONFIG_SCHEMA_VERSION

    return {
        "artifact_type": "run_intent",
        "artifact_schema_version": RUN_INTENT_ARTIFACT_SCHEMA_VERSION,
        "generated_at_utc": generated_at_utc or _utc_now_iso(),
        "run_id": run_id,
        "run_config_schema": _build_run_config_schema_reference(),
        "intent_source": {
            "mode": "explicit_run_config" if resolved_path else "implicit_default",
            "run_config_path": str(resolved_path) if resolved_path else None,
        },
        "requested_config": requested_config,
    }


def build_run_effective_payload(
    run_id: str,
    run_config_path: str | Path | None,
    run_intent_path: str | Path | None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    return {
        "artifact_type": "run_effective_config",
        "artifact_schema_version": RUN_EFFECTIVE_ARTIFACT_SCHEMA_VERSION,
        "generated_at_utc": generated_at_utc or _utc_now_iso(),
        "run_id": run_id,
        "run_config_schema": _build_run_config_schema_reference(),
        "runtime_environment": _build_runtime_environment_snapshot(),
        "resolved_from": {
            "run_config_path": str(resolved_path) if resolved_path else None,
            "run_intent_path": str(Path(run_intent_path).resolve()) if run_intent_path else None,
        },
        "env_overrides": _collect_env_override_provenance(resolved_path),
        "effective_config": effective,
    }


def write_run_config_artifact_pair(
    run_id: str,
    output_dir: str | Path,
    run_config_path: str | Path | None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    resolved_output_dir = Path(output_dir).resolve()
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
    intent_path = resolved_output_dir / f"run_intent_{timestamp}.json"
    effective_path = resolved_output_dir / f"run_effective_config_{timestamp}.json"

    intent_payload = build_run_intent_payload(
        run_id=run_id,
        run_config_path=run_config_path,
        generated_at_utc=generated_at_utc,
    )
    intent_json = json.dumps(intent_payload, indent=2, ensure_ascii=True, sort_keys=True)
    with open_text_write(intent_path) as handle:
        handle.write(intent_json)

    effective_payload = build_run_effective_payload(
        run_id=run_id,
        run_config_path=run_config_path,
        run_intent_path=intent_path,
        generated_at_utc=generated_at_utc,
    )
    effective_json = json.dumps(effective_payload, indent=2, ensure_ascii=True, sort_keys=True)
    with open_text_write(effective_path) as handle:
        handle.write(effective_json)

    latest_intent_path = resolved_output_dir / "run_intent_latest.json"
    latest_effective_path = resolved_output_dir / "run_effective_config_latest.json"
    with open_text_write(latest_intent_path) as handle:
        handle.write(intent_json)
    with open_text_write(latest_effective_path) as handle:
        handle.write(effective_json)

    return {
        "run_id": run_id,
        "generated_at_utc": generated_at_utc or _utc_now_iso(),
        "output_dir": str(resolved_output_dir),
        "run_intent": {
            "path": str(intent_path),
            "sha256": _sha256_of_file(intent_path),
            "artifact_schema_version": RUN_INTENT_ARTIFACT_SCHEMA_VERSION,
        },
        "run_effective_config": {
            "path": str(effective_path),
            "sha256": _sha256_of_file(effective_path),
            "artifact_schema_version": RUN_EFFECTIVE_ARTIFACT_SCHEMA_VERSION,
        },
        "latest": {
            "run_intent": str(latest_intent_path),
            "run_effective_config": str(latest_effective_path),
        },
    }
