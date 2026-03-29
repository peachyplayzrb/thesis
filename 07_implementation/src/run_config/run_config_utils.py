from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any

from shared_utils.constants import (
    CUSTOM_SIGNAL_MODE_NAME,
    DEFAULT_ASSEMBLY_CONTROLS,
    DEFAULT_CONTROLLABILITY_CONTROLS,
    DEFAULT_CONTROL_MODE,
    DEFAULT_INCLUDE_INTERACTION_TYPES,
    DEFAULT_INGESTION_CONTROLS,
    DEFAULT_INPUT_SCOPE,
    DEFAULT_INFLUENCE_TRACKS,
    DEFAULT_INTERACTION_SCOPE,
    DEFAULT_LANGUAGE_FILTER_CODES,
    DEFAULT_LANGUAGE_FILTER_ENABLED,
    DEFAULT_NUMERIC_SUPPORT_MIN_SCORE,
    DEFAULT_OBSERVABILITY_CONTROLS,
    DEFAULT_ORCHESTRATION_CONTROLS,
    DEFAULT_PROFILE_CONTROLS,
    DEFAULT_RECENCY_YEARS_MIN_OFFSET,
    DEFAULT_REPORTING_SCORE_THRESHOLDS,
    DEFAULT_RETRIEVAL_ENABLE_POPULARITY_NUMERIC,
    DEFAULT_RETRIEVAL_CONTROLS,
    DEFAULT_RETRIEVAL_NUMERIC_THRESHOLDS,
    DEFAULT_RETRIEVAL_USE_CONTINUOUS_NUMERIC,
    DEFAULT_RETRIEVAL_USE_WEIGHTED_SEMANTICS,
    DEFAULT_SIGNAL_MODE_NAME,
    DEFAULT_SCENARIO_DEFINITIONS,
    DEFAULT_SCENARIO_POLICY,
    DEFAULT_SCORING_CONTROLS,
    DEFAULT_SCORING_COMPONENT_WEIGHTS,
    DEFAULT_SCORING_NUMERIC_THRESHOLDS,
    DEFAULT_SEED_CONTROLS,
    DEFAULT_TOP_CONTRIBUTOR_LIMIT,
    DEFAULT_TRANSPARENCY_CONTROLS,
    DEFAULT_WEIGHTING_POLICY,
    ENHANCED_SIGNAL_MODE_NAME,
)

from shared_utils.io_utils import open_text_write

RUN_CONFIG_SCHEMA_VERSION = "run-config-v1"
RUN_INTENT_ARTIFACT_SCHEMA_VERSION = "run-intent-v1"
RUN_EFFECTIVE_ARTIFACT_SCHEMA_VERSION = "run-effective-config-v1"

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
            "top_tag_limit": int(DEFAULT_PROFILE_CONTROLS["top_tag_limit"]),
            "top_genre_limit": int(DEFAULT_PROFILE_CONTROLS["top_genre_limit"]),
            "top_lead_genre_limit": int(DEFAULT_PROFILE_CONTROLS["top_lead_genre_limit"]),
            "confidence_weighting_mode": str(DEFAULT_PROFILE_CONTROLS["confidence_weighting_mode"]),
            "confidence_bin_high_threshold": float(DEFAULT_PROFILE_CONTROLS["confidence_bin_high_threshold"]),
            "confidence_bin_medium_threshold": float(DEFAULT_PROFILE_CONTROLS["confidence_bin_medium_threshold"]),
            "interaction_attribution_mode": str(DEFAULT_PROFILE_CONTROLS["interaction_attribution_mode"]),
            "emit_profile_policy_diagnostics": bool(DEFAULT_PROFILE_CONTROLS["emit_profile_policy_diagnostics"]),
        },
        "retrieval_controls": {
            "profile_top_tag_limit": int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_tag_limit"]),
            "profile_top_genre_limit": int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_genre_limit"]),
            "profile_top_lead_genre_limit": int(DEFAULT_RETRIEVAL_CONTROLS["profile_top_lead_genre_limit"]),
            "semantic_strong_keep_score": int(DEFAULT_RETRIEVAL_CONTROLS["semantic_strong_keep_score"]),
            "semantic_min_keep_score": int(DEFAULT_RETRIEVAL_CONTROLS["semantic_min_keep_score"]),
            "numeric_support_min_pass": int(DEFAULT_RETRIEVAL_CONTROLS["numeric_support_min_pass"]),
            "numeric_support_min_score": float(DEFAULT_RETRIEVAL_CONTROLS["numeric_support_min_score"]),
            "use_weighted_semantics": bool(DEFAULT_RETRIEVAL_CONTROLS["use_weighted_semantics"]),
            "use_continuous_numeric": bool(DEFAULT_RETRIEVAL_CONTROLS["use_continuous_numeric"]),
            "enable_popularity_numeric": bool(DEFAULT_RETRIEVAL_CONTROLS["enable_popularity_numeric"]),
            "language_filter_enabled": bool(DEFAULT_RETRIEVAL_CONTROLS["language_filter_enabled"]),
            "language_filter_codes": list(DEFAULT_RETRIEVAL_CONTROLS["language_filter_codes"]),
            "recency_years_min_offset": DEFAULT_RETRIEVAL_CONTROLS["recency_years_min_offset"],
            "numeric_thresholds": dict(DEFAULT_RETRIEVAL_CONTROLS["numeric_thresholds"]),
            "profile_quality_penalty_enabled": bool(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_penalty_enabled"]),
            "profile_quality_threshold": float(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_threshold"]),
            "profile_entropy_low_threshold": float(DEFAULT_RETRIEVAL_CONTROLS["profile_entropy_low_threshold"]),
            "influence_share_threshold": float(DEFAULT_RETRIEVAL_CONTROLS["influence_share_threshold"]),
            "profile_quality_penalty_increment": float(DEFAULT_RETRIEVAL_CONTROLS["profile_quality_penalty_increment"]),
            "profile_entropy_penalty_increment": float(DEFAULT_RETRIEVAL_CONTROLS["profile_entropy_penalty_increment"]),
            "influence_share_penalty_increment": float(DEFAULT_RETRIEVAL_CONTROLS["influence_share_penalty_increment"]),
            "numeric_penalty_scale": float(DEFAULT_RETRIEVAL_CONTROLS["numeric_penalty_scale"]),
            "semantic_overlap_damping_mid_entropy_threshold": float(
                DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_mid_entropy_threshold"]
            ),
            "semantic_overlap_damping_low_entropy": float(DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_low_entropy"]),
            "semantic_overlap_damping_mid_entropy": float(DEFAULT_RETRIEVAL_CONTROLS["semantic_overlap_damping_mid_entropy"]),
            "enable_numeric_confidence_scaling": bool(DEFAULT_RETRIEVAL_CONTROLS["enable_numeric_confidence_scaling"]),
            "numeric_confidence_floor": float(DEFAULT_RETRIEVAL_CONTROLS["numeric_confidence_floor"]),
            "profile_numeric_confidence_mode": str(DEFAULT_RETRIEVAL_CONTROLS["profile_numeric_confidence_mode"]),
            "profile_numeric_confidence_blend_weight": float(
                DEFAULT_RETRIEVAL_CONTROLS["profile_numeric_confidence_blend_weight"]
            ),
            "numeric_support_score_mode": str(DEFAULT_RETRIEVAL_CONTROLS["numeric_support_score_mode"]),
            "emit_profile_policy_diagnostics": bool(DEFAULT_RETRIEVAL_CONTROLS["emit_profile_policy_diagnostics"]),
        },
        "scoring_controls": {
            "component_weights": dict(DEFAULT_SCORING_CONTROLS["component_weights"]),
            "numeric_thresholds": dict(DEFAULT_SCORING_CONTROLS["numeric_thresholds"]),
            "lead_genre_strategy": str(DEFAULT_SCORING_CONTROLS["lead_genre_strategy"]),
            "semantic_overlap_strategy": str(DEFAULT_SCORING_CONTROLS["semantic_overlap_strategy"]),
            "semantic_precision_alpha_mode": str(DEFAULT_SCORING_CONTROLS["semantic_precision_alpha_mode"]),
            "semantic_precision_alpha_fixed": float(DEFAULT_SCORING_CONTROLS["semantic_precision_alpha_fixed"]),
            "enable_numeric_confidence_scaling": bool(DEFAULT_SCORING_CONTROLS["enable_numeric_confidence_scaling"]),
            "numeric_confidence_floor": float(DEFAULT_SCORING_CONTROLS["numeric_confidence_floor"]),
            "profile_numeric_confidence_mode": str(DEFAULT_SCORING_CONTROLS["profile_numeric_confidence_mode"]),
            "profile_numeric_confidence_blend_weight": float(DEFAULT_SCORING_CONTROLS["profile_numeric_confidence_blend_weight"]),
            "emit_confidence_impact_diagnostics": bool(DEFAULT_SCORING_CONTROLS["emit_confidence_impact_diagnostics"]),
            "emit_semantic_precision_diagnostics": bool(DEFAULT_SCORING_CONTROLS["emit_semantic_precision_diagnostics"]),
            "apply_bl003_influence_tracks": bool(DEFAULT_SCORING_CONTROLS["apply_bl003_influence_tracks"]),
            "influence_track_bonus_scale": float(DEFAULT_SCORING_CONTROLS["influence_track_bonus_scale"]),
        },
        "assembly_controls": dict(DEFAULT_ASSEMBLY_CONTROLS),
        "transparency_controls": {
            "top_contributor_limit": DEFAULT_TOP_CONTRIBUTOR_LIMIT,
            "blend_primary_contributor_on_near_tie": bool(DEFAULT_TRANSPARENCY_CONTROLS["blend_primary_contributor_on_near_tie"]),
            "primary_contributor_tie_delta": float(DEFAULT_TRANSPARENCY_CONTROLS["primary_contributor_tie_delta"]),
        },
        "observability_controls": dict(DEFAULT_OBSERVABILITY_CONTROLS),
        "reporting_controls": {
            "score_thresholds": dict(DEFAULT_REPORTING_SCORE_THRESHOLDS),
        },
        "controllability_controls": {
            **dict(DEFAULT_CONTROLLABILITY_CONTROLS),
            "scenario_policy": {
                "enabled_scenario_ids": list(DEFAULT_SCENARIO_POLICY["enabled_scenario_ids"]),
                "repeat_count": int(DEFAULT_SCENARIO_POLICY["repeat_count"]),
                "stage_scope": list(DEFAULT_SCENARIO_POLICY["stage_scope"]),
                "comparison_mode": str(DEFAULT_SCENARIO_POLICY["comparison_mode"]),
            },
            "scenario_definitions": list(DEFAULT_SCENARIO_DEFINITIONS),
        },
        "seed_controls": {
            "match_rate_min_threshold": DEFAULT_SEED_CONTROLS["match_rate_min_threshold"],
            "top_range_weights": dict(DEFAULT_SEED_CONTROLS["top_range_weights"]),
            "source_base_weights": dict(DEFAULT_SEED_CONTROLS["source_base_weights"]),
            "fuzzy_matching": dict(DEFAULT_SEED_CONTROLS["fuzzy_matching"]),
            "match_strategy": dict(DEFAULT_SEED_CONTROLS["match_strategy"]),
            "match_strategy_order": list(DEFAULT_SEED_CONTROLS["match_strategy_order"]),
            "temporal_controls": dict(DEFAULT_SEED_CONTROLS["temporal_controls"]),
            "aggregation_policy": dict(DEFAULT_SEED_CONTROLS["aggregation_policy"]),
            "decay_half_lives": dict(DEFAULT_SEED_CONTROLS["decay_half_lives"]),
            "weighting_policy": {
                "top_tracks": dict(DEFAULT_WEIGHTING_POLICY["top_tracks"]),
                "playlist_items": dict(DEFAULT_WEIGHTING_POLICY["playlist_items"]),
            },
        },
        "orchestration_controls": {
            "stage_order": DEFAULT_ORCHESTRATION_CONTROLS["stage_order"],
            "continue_on_error": bool(DEFAULT_ORCHESTRATION_CONTROLS["continue_on_error"]),
            "refresh_seed_policy": str(DEFAULT_ORCHESTRATION_CONTROLS["refresh_seed_policy"]),
            "required_stable_artifacts": list(DEFAULT_ORCHESTRATION_CONTROLS["required_stable_artifacts"]),
        },
    }


DEFAULT_RUN_CONFIG: dict[str, Any] = _build_default_run_config()



class RunConfigError(RuntimeError):
    pass


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
    if isinstance(value, (int, float)):
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
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0 else default


def _coerce_min_positive_float(value: Any, default: float, *, min_value: float = 0.001) -> float:
    """Coerce to float and clamp to a minimum positive value, falling back on parse errors."""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = default
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
        except (TypeError, ValueError):
            raise RunConfigError(
                f"{context}: threshold '{key}' must be numeric, got {type(value).__name__}: {value!r}"
            )
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
    except (TypeError, ValueError):
        raise RunConfigError(
            f"{param_name} must be numeric, got {type(value).__name__}: {value!r}"
        )
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
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    raise RunConfigError(f"{param_name} must be boolean-like, got {value!r}")


def _validate_fraction_zero_to_one(value: Any, param_name: str, default: float) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise RunConfigError(f"{param_name} must be numeric, got {value!r}")
    if parsed < 0.0 or parsed > 1.0:
        raise RunConfigError(f"{param_name} must be within [0, 1], got {parsed}")
    return parsed


def _validate_non_negative_float(value: Any, param_name: str, default: float) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise RunConfigError(f"{param_name} must be numeric, got {value!r}")
    if parsed < 0:
        raise RunConfigError(f"{param_name} must be >= 0, got {parsed}")
    return parsed


def _validate_non_negative_int(value: Any, param_name: str, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise RunConfigError(f"{param_name} must be an integer, got {value!r}")
    if parsed < 0:
        raise RunConfigError(f"{param_name} must be >= 0, got {parsed}")
    return parsed


def _validate_positive_int_or_error(value: Any, param_name: str, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise RunConfigError(f"{param_name} must be an integer, got {value!r}")
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
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
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
        except (TypeError, ValueError):
            raise RunConfigError(
                f"{context}: component weight '{key}' must be numeric, got {type(value).__name__}: {value!r}"
            )
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
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def resolve_effective_run_config(run_config_path: str | Path | None) -> tuple[dict[str, Any], Path | None]:
    path = Path(run_config_path).resolve() if run_config_path else None
    payload = load_run_config(path) if path else None
    if payload is None:
        effective = canonical_default_run_config()
    else:
        effective = _deep_merge(canonical_default_run_config(), payload)

    schema_version = effective.get("schema_version")
    if schema_version is None:
        effective["schema_version"] = RUN_CONFIG_SCHEMA_VERSION
    elif schema_version != RUN_CONFIG_SCHEMA_VERSION:
        raise RunConfigError(
            f"Unsupported run config schema_version '{schema_version}'. Expected '{RUN_CONFIG_SCHEMA_VERSION}'."
        )

    user_context = effective.setdefault("user_context", {})
    if not isinstance(user_context, dict):
        raise RunConfigError("run_config.user_context must be an object")
    user_context["user_id"] = _coerce_optional_str(user_context.get("user_id"))

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

    profile_controls = effective.setdefault("profile_controls", {})
    if not isinstance(profile_controls, dict):
        raise RunConfigError("run_config.profile_controls must be an object")
    profile_controls["top_tag_limit"] = _coerce_positive_int(
        profile_controls.get("top_tag_limit"),
        DEFAULT_RUN_CONFIG["profile_controls"]["top_tag_limit"],
    )
    profile_controls["top_genre_limit"] = _coerce_positive_int(
        profile_controls.get("top_genre_limit"),
        DEFAULT_RUN_CONFIG["profile_controls"]["top_genre_limit"],
    )
    profile_controls["top_lead_genre_limit"] = _coerce_positive_int(
        profile_controls.get("top_lead_genre_limit"),
        DEFAULT_RUN_CONFIG["profile_controls"]["top_lead_genre_limit"],
    )
    confidence_weighting_mode_raw = str(
        profile_controls.get("confidence_weighting_mode")
        or DEFAULT_RUN_CONFIG["profile_controls"]["confidence_weighting_mode"]
    ).strip().lower()
    profile_controls["confidence_weighting_mode"] = (
        confidence_weighting_mode_raw
        if confidence_weighting_mode_raw in {"linear_half_bias", "direct_confidence", "none"}
        else str(DEFAULT_RUN_CONFIG["profile_controls"]["confidence_weighting_mode"])
    )
    profile_controls["confidence_bin_high_threshold"] = _validate_fraction_zero_to_one(
        profile_controls.get("confidence_bin_high_threshold"),
        "profile_controls.confidence_bin_high_threshold",
        float(DEFAULT_RUN_CONFIG["profile_controls"]["confidence_bin_high_threshold"]),
    )
    profile_controls["confidence_bin_medium_threshold"] = _validate_fraction_zero_to_one(
        profile_controls.get("confidence_bin_medium_threshold"),
        "profile_controls.confidence_bin_medium_threshold",
        float(DEFAULT_RUN_CONFIG["profile_controls"]["confidence_bin_medium_threshold"]),
    )
    if float(profile_controls["confidence_bin_medium_threshold"]) > float(profile_controls["confidence_bin_high_threshold"]):
        raise RunConfigError(
            "profile_controls.confidence_bin_medium_threshold must be <= "
            "profile_controls.confidence_bin_high_threshold"
        )
    interaction_attribution_mode_raw = str(
        profile_controls.get("interaction_attribution_mode")
        or DEFAULT_RUN_CONFIG["profile_controls"]["interaction_attribution_mode"]
    ).strip().lower()
    profile_controls["interaction_attribution_mode"] = (
        interaction_attribution_mode_raw
        if interaction_attribution_mode_raw in {"split_selected_types_equal_share", "primary_type_only"}
        else str(DEFAULT_RUN_CONFIG["profile_controls"]["interaction_attribution_mode"])
    )
    profile_controls["emit_profile_policy_diagnostics"] = _validate_bool_like(
        profile_controls.get("emit_profile_policy_diagnostics"),
        "profile_controls.emit_profile_policy_diagnostics",
        bool(DEFAULT_RUN_CONFIG["profile_controls"]["emit_profile_policy_diagnostics"]),
    )

    interaction_scope = effective.setdefault("interaction_scope", {})
    if not isinstance(interaction_scope, dict):
        interaction_scope = {}
        effective["interaction_scope"] = interaction_scope
    interaction_scope["include_interaction_types"] = _normalize_allowed_tokens(
        interaction_scope.get("include_interaction_types"),
        {"history", "influence"},
        list(DEFAULT_INCLUDE_INTERACTION_TYPES),
    )

    influence_tracks = effective.setdefault("influence_tracks", {})
    if not isinstance(influence_tracks, dict):
        influence_tracks = {}
        effective["influence_tracks"] = influence_tracks
    influence_defaults = DEFAULT_RUN_CONFIG["influence_tracks"]
    effective["influence_tracks"] = _validate_bl003_influence_tracks(
        influence_tracks,
        influence_defaults,
    )
    influence_tracks = effective["influence_tracks"]

    seed_controls = effective.setdefault("seed_controls", {})
    seed_defaults = DEFAULT_RUN_CONFIG["seed_controls"]
    effective["seed_controls"] = _validate_bl003_seed_controls(seed_controls, seed_defaults)
    seed_controls = effective["seed_controls"]

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

    retrieval_controls = effective.setdefault("retrieval_controls", {})
    if not isinstance(retrieval_controls, dict):
        raise RunConfigError("run_config.retrieval_controls must be an object")
    retrieval_defaults = DEFAULT_RUN_CONFIG["retrieval_controls"]
    retrieval_controls["profile_top_tag_limit"] = _coerce_positive_int(
        retrieval_controls.get("profile_top_tag_limit"),
        retrieval_defaults["profile_top_tag_limit"],
    )
    retrieval_controls["profile_top_genre_limit"] = _coerce_positive_int(
        retrieval_controls.get("profile_top_genre_limit"),
        retrieval_defaults["profile_top_genre_limit"],
    )
    retrieval_controls["profile_top_lead_genre_limit"] = _coerce_positive_int(
        retrieval_controls.get("profile_top_lead_genre_limit"),
        retrieval_defaults["profile_top_lead_genre_limit"],
    )
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
    retrieval_controls["profile_quality_penalty_enabled"] = _validate_bool_like(
        retrieval_controls.get("profile_quality_penalty_enabled"),
        "retrieval_controls.profile_quality_penalty_enabled",
        bool(retrieval_defaults["profile_quality_penalty_enabled"]),
    )
    retrieval_controls["profile_quality_threshold"] = _validate_fraction_zero_to_one(
        retrieval_controls.get("profile_quality_threshold"),
        "retrieval_controls.profile_quality_threshold",
        float(retrieval_defaults["profile_quality_threshold"]),
    )
    retrieval_controls["profile_entropy_low_threshold"] = _validate_fraction_zero_to_one(
        retrieval_controls.get("profile_entropy_low_threshold"),
        "retrieval_controls.profile_entropy_low_threshold",
        float(retrieval_defaults["profile_entropy_low_threshold"]),
    )
    retrieval_controls["influence_share_threshold"] = _validate_fraction_zero_to_one(
        retrieval_controls.get("influence_share_threshold"),
        "retrieval_controls.influence_share_threshold",
        float(retrieval_defaults["influence_share_threshold"]),
    )
    retrieval_controls["profile_quality_penalty_increment"] = _coerce_non_negative_float(
        retrieval_controls.get("profile_quality_penalty_increment"),
        float(retrieval_defaults["profile_quality_penalty_increment"]),
    )
    retrieval_controls["profile_entropy_penalty_increment"] = _coerce_non_negative_float(
        retrieval_controls.get("profile_entropy_penalty_increment"),
        float(retrieval_defaults["profile_entropy_penalty_increment"]),
    )
    retrieval_controls["influence_share_penalty_increment"] = _coerce_non_negative_float(
        retrieval_controls.get("influence_share_penalty_increment"),
        float(retrieval_defaults["influence_share_penalty_increment"]),
    )
    retrieval_controls["numeric_penalty_scale"] = _coerce_non_negative_float(
        retrieval_controls.get("numeric_penalty_scale"),
        float(retrieval_defaults["numeric_penalty_scale"]),
    )
    retrieval_controls["semantic_overlap_damping_mid_entropy_threshold"] = _validate_fraction_zero_to_one(
        retrieval_controls.get("semantic_overlap_damping_mid_entropy_threshold"),
        "retrieval_controls.semantic_overlap_damping_mid_entropy_threshold",
        float(retrieval_defaults["semantic_overlap_damping_mid_entropy_threshold"]),
    )
    retrieval_controls["semantic_overlap_damping_low_entropy"] = _validate_fraction_zero_to_one(
        retrieval_controls.get("semantic_overlap_damping_low_entropy"),
        "retrieval_controls.semantic_overlap_damping_low_entropy",
        float(retrieval_defaults["semantic_overlap_damping_low_entropy"]),
    )
    retrieval_controls["semantic_overlap_damping_mid_entropy"] = _validate_fraction_zero_to_one(
        retrieval_controls.get("semantic_overlap_damping_mid_entropy"),
        "retrieval_controls.semantic_overlap_damping_mid_entropy",
        float(retrieval_defaults["semantic_overlap_damping_mid_entropy"]),
    )
    retrieval_controls["enable_numeric_confidence_scaling"] = _validate_bool_like(
        retrieval_controls.get("enable_numeric_confidence_scaling"),
        "retrieval_controls.enable_numeric_confidence_scaling",
        bool(retrieval_defaults["enable_numeric_confidence_scaling"]),
    )
    retrieval_controls["numeric_confidence_floor"] = _validate_fraction_zero_to_one(
        retrieval_controls.get("numeric_confidence_floor"),
        "retrieval_controls.numeric_confidence_floor",
        float(retrieval_defaults["numeric_confidence_floor"]),
    )
    profile_numeric_mode_raw = str(
        retrieval_controls.get("profile_numeric_confidence_mode") or retrieval_defaults["profile_numeric_confidence_mode"]
    ).strip().lower()
    retrieval_controls["profile_numeric_confidence_mode"] = (
        profile_numeric_mode_raw
        if profile_numeric_mode_raw in {"direct", "blended"}
        else str(retrieval_defaults["profile_numeric_confidence_mode"])
    )
    retrieval_controls["profile_numeric_confidence_blend_weight"] = _validate_fraction_zero_to_one(
        retrieval_controls.get("profile_numeric_confidence_blend_weight"),
        "retrieval_controls.profile_numeric_confidence_blend_weight",
        float(retrieval_defaults["profile_numeric_confidence_blend_weight"]),
    )
    numeric_support_mode_raw = str(
        retrieval_controls.get("numeric_support_score_mode") or retrieval_defaults["numeric_support_score_mode"]
    ).strip().lower()
    retrieval_controls["numeric_support_score_mode"] = (
        numeric_support_mode_raw
        if numeric_support_mode_raw in {"raw", "weighted", "weighted_absolute"}
        else str(retrieval_defaults["numeric_support_score_mode"])
    )
    retrieval_controls["emit_profile_policy_diagnostics"] = _validate_bool_like(
        retrieval_controls.get("emit_profile_policy_diagnostics"),
        "retrieval_controls.emit_profile_policy_diagnostics",
        bool(retrieval_defaults["emit_profile_policy_diagnostics"]),
    )

    scoring_controls = effective.setdefault("scoring_controls", {})
    if not isinstance(scoring_controls, dict):
        raise RunConfigError("run_config.scoring_controls must be an object")
    scoring_defaults = DEFAULT_RUN_CONFIG["scoring_controls"]
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

    lead_genre_strategy_raw = str(
        scoring_controls.get("lead_genre_strategy") or scoring_defaults["lead_genre_strategy"]
    ).strip().lower()
    scoring_controls["lead_genre_strategy"] = (
        lead_genre_strategy_raw
        if lead_genre_strategy_raw in {"single_anchor", "weighted_top_lead_genres"}
        else str(scoring_defaults["lead_genre_strategy"])
    )

    overlap_strategy_raw = str(
        scoring_controls.get("semantic_overlap_strategy") or scoring_defaults["semantic_overlap_strategy"]
    ).strip().lower()
    scoring_controls["semantic_overlap_strategy"] = (
        overlap_strategy_raw
        if overlap_strategy_raw in {"overlap_only", "precision_aware"}
        else str(scoring_defaults["semantic_overlap_strategy"])
    )

    precision_mode_raw = str(
        scoring_controls.get("semantic_precision_alpha_mode") or scoring_defaults["semantic_precision_alpha_mode"]
    ).strip().lower()
    scoring_controls["semantic_precision_alpha_mode"] = (
        precision_mode_raw
        if precision_mode_raw in {"profile_adaptive", "fixed"}
        else str(scoring_defaults["semantic_precision_alpha_mode"])
    )
    scoring_controls["semantic_precision_alpha_fixed"] = _validate_fraction_zero_to_one(
        scoring_controls.get("semantic_precision_alpha_fixed"),
        "scoring_controls.semantic_precision_alpha_fixed",
        float(scoring_defaults["semantic_precision_alpha_fixed"]),
    )
    scoring_controls["enable_numeric_confidence_scaling"] = _validate_bool_like(
        scoring_controls.get("enable_numeric_confidence_scaling"),
        "scoring_controls.enable_numeric_confidence_scaling",
        bool(scoring_defaults["enable_numeric_confidence_scaling"]),
    )
    scoring_controls["numeric_confidence_floor"] = _validate_fraction_zero_to_one(
        scoring_controls.get("numeric_confidence_floor"),
        "scoring_controls.numeric_confidence_floor",
        float(scoring_defaults["numeric_confidence_floor"]),
    )

    profile_conf_mode_raw = str(
        scoring_controls.get("profile_numeric_confidence_mode") or scoring_defaults["profile_numeric_confidence_mode"]
    ).strip().lower()
    scoring_controls["profile_numeric_confidence_mode"] = (
        profile_conf_mode_raw
        if profile_conf_mode_raw in {"direct", "blended"}
        else str(scoring_defaults["profile_numeric_confidence_mode"])
    )
    scoring_controls["profile_numeric_confidence_blend_weight"] = _validate_fraction_zero_to_one(
        scoring_controls.get("profile_numeric_confidence_blend_weight"),
        "scoring_controls.profile_numeric_confidence_blend_weight",
        float(scoring_defaults["profile_numeric_confidence_blend_weight"]),
    )
    scoring_controls["emit_confidence_impact_diagnostics"] = _validate_bool_like(
        scoring_controls.get("emit_confidence_impact_diagnostics"),
        "scoring_controls.emit_confidence_impact_diagnostics",
        bool(scoring_defaults["emit_confidence_impact_diagnostics"]),
    )
    scoring_controls["emit_semantic_precision_diagnostics"] = _validate_bool_like(
        scoring_controls.get("emit_semantic_precision_diagnostics"),
        "scoring_controls.emit_semantic_precision_diagnostics",
        bool(scoring_defaults["emit_semantic_precision_diagnostics"]),
    )
    scoring_controls["apply_bl003_influence_tracks"] = _validate_bool_like(
        scoring_controls.get("apply_bl003_influence_tracks"),
        "scoring_controls.apply_bl003_influence_tracks",
        bool(scoring_defaults["apply_bl003_influence_tracks"]),
    )
    scoring_controls["influence_track_bonus_scale"] = _coerce_non_negative_float(
        scoring_controls.get("influence_track_bonus_scale"),
        float(scoring_defaults["influence_track_bonus_scale"]),
    )
    _enforce_profile_retrieval_limit_constraints(profile_controls, retrieval_controls)
    effective["signal_mode"] = _build_signal_mode_summary(retrieval_controls, scoring_controls)

    observability_controls = effective.setdefault("observability_controls", {})
    if not isinstance(observability_controls, dict):
        raise RunConfigError("run_config.observability_controls must be an object")
    observability_defaults = DEFAULT_RUN_CONFIG["observability_controls"]
    observability_controls["diagnostic_sample_limit"] = _coerce_positive_int(
        observability_controls.get("diagnostic_sample_limit"),
        int(observability_defaults["diagnostic_sample_limit"]),
    )
    observability_controls["bootstrap_mode"] = _coerce_bool(
        observability_controls.get("bootstrap_mode"),
        bool(observability_defaults["bootstrap_mode"]),
    )

    transparency_controls = effective.setdefault("transparency_controls", {})
    if not isinstance(transparency_controls, dict):
        raise RunConfigError("run_config.transparency_controls must be an object")
    transparency_defaults = DEFAULT_RUN_CONFIG["transparency_controls"]
    transparency_controls["top_contributor_limit"] = _coerce_positive_int(
        transparency_controls.get("top_contributor_limit"),
        int(transparency_defaults["top_contributor_limit"]),
    )
    transparency_controls["blend_primary_contributor_on_near_tie"] = _coerce_bool(
        transparency_controls.get("blend_primary_contributor_on_near_tie"),
        bool(transparency_defaults["blend_primary_contributor_on_near_tie"]),
    )
    transparency_controls["primary_contributor_tie_delta"] = _coerce_non_negative_float(
        transparency_controls.get("primary_contributor_tie_delta"),
        float(transparency_defaults["primary_contributor_tie_delta"]),
    )

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
    raw = (seed.get("weighting_policy") or {})
    default_top = DEFAULT_WEIGHTING_POLICY["top_tracks"]
    default_pl = DEFAULT_WEIGHTING_POLICY["playlist_items"]

    raw_top = raw.get("top_tracks") or {}
    raw_pl = raw.get("playlist_items") or {}

    return {
        "top_tracks_min_rank_floor": float(
            raw_top.get("min_rank_floor", default_top["min_rank_floor"])
        ),
        "top_tracks_scale_multiplier": float(
            raw_top.get("scale_multiplier", default_top["scale_multiplier"])
        ),
        "top_tracks_default_time_range_weight": float(
            raw_top.get("default_time_range_weight", default_top["default_time_range_weight"])
        ),
        "playlist_items_min_position_floor": float(
            raw_pl.get("min_position_floor", default_pl["min_position_floor"])
        ),
        "playlist_items_scale_multiplier": float(
            raw_pl.get("scale_multiplier", default_pl["scale_multiplier"])
        ),
    }


def resolve_bl005_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    retrieval = effective["retrieval_controls"]
    defaults = DEFAULT_RUN_CONFIG["retrieval_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "signal_mode": dict(effective.get("signal_mode") or {}),
        "profile_top_lead_genre_limit": _coerce_positive_int(
            retrieval.get("profile_top_lead_genre_limit"),
            defaults["profile_top_lead_genre_limit"],
        ),
        "profile_top_tag_limit": _coerce_positive_int(
            retrieval.get("profile_top_tag_limit"),
            defaults["profile_top_tag_limit"],
        ),
        "profile_top_genre_limit": _coerce_positive_int(
            retrieval.get("profile_top_genre_limit"),
            defaults["profile_top_genre_limit"],
        ),
        "semantic_strong_keep_score": _coerce_positive_int(
            retrieval.get("semantic_strong_keep_score"),
            defaults["semantic_strong_keep_score"],
        ),
        "semantic_min_keep_score": _coerce_positive_int(
            retrieval.get("semantic_min_keep_score"),
            defaults["semantic_min_keep_score"],
        ),
        "numeric_support_min_pass": _coerce_positive_int(
            retrieval.get("numeric_support_min_pass"),
            defaults["numeric_support_min_pass"],
        ),
        "numeric_support_min_score": _coerce_non_negative_float(
            retrieval.get("numeric_support_min_score"),
            float(defaults["numeric_support_min_score"]),
        ),
        "use_weighted_semantics": _coerce_bool(
            retrieval.get("use_weighted_semantics"),
            bool(defaults["use_weighted_semantics"]),
        ),
        "use_continuous_numeric": _coerce_bool(
            retrieval.get("use_continuous_numeric"),
            bool(defaults["use_continuous_numeric"]),
        ),
        "enable_popularity_numeric": _coerce_bool(
            retrieval.get("enable_popularity_numeric"),
            bool(defaults["enable_popularity_numeric"]),
        ),
        "language_filter_enabled": _coerce_bool(
            retrieval.get("language_filter_enabled"),
            bool(defaults["language_filter_enabled"]),
        ),
        "language_filter_codes": _normalize_string_tokens(
            retrieval.get("language_filter_codes"),
            list(defaults["language_filter_codes"]),
        ),
        "recency_years_min_offset": _coerce_optional_positive_int(
            retrieval.get("recency_years_min_offset"),
            defaults["recency_years_min_offset"],
        ),
        "numeric_thresholds": _validate_positive_thresholds(
            retrieval.get("numeric_thresholds") or defaults["numeric_thresholds"],
            "retrieval_controls.numeric_thresholds"
        ),
        "profile_quality_penalty_enabled": _validate_bool_like(
            retrieval.get("profile_quality_penalty_enabled"),
            "retrieval_controls.profile_quality_penalty_enabled",
            bool(defaults["profile_quality_penalty_enabled"]),
        ),
        "profile_quality_threshold": _validate_fraction_zero_to_one(
            retrieval.get("profile_quality_threshold"),
            "retrieval_controls.profile_quality_threshold",
            float(defaults["profile_quality_threshold"]),
        ),
        "profile_entropy_low_threshold": _validate_fraction_zero_to_one(
            retrieval.get("profile_entropy_low_threshold"),
            "retrieval_controls.profile_entropy_low_threshold",
            float(defaults["profile_entropy_low_threshold"]),
        ),
        "influence_share_threshold": _validate_fraction_zero_to_one(
            retrieval.get("influence_share_threshold"),
            "retrieval_controls.influence_share_threshold",
            float(defaults["influence_share_threshold"]),
        ),
        "profile_quality_penalty_increment": _coerce_non_negative_float(
            retrieval.get("profile_quality_penalty_increment"),
            float(defaults["profile_quality_penalty_increment"]),
        ),
        "profile_entropy_penalty_increment": _coerce_non_negative_float(
            retrieval.get("profile_entropy_penalty_increment"),
            float(defaults["profile_entropy_penalty_increment"]),
        ),
        "influence_share_penalty_increment": _coerce_non_negative_float(
            retrieval.get("influence_share_penalty_increment"),
            float(defaults["influence_share_penalty_increment"]),
        ),
        "numeric_penalty_scale": _coerce_non_negative_float(
            retrieval.get("numeric_penalty_scale"),
            float(defaults["numeric_penalty_scale"]),
        ),
        "semantic_overlap_damping_mid_entropy_threshold": _validate_fraction_zero_to_one(
            retrieval.get("semantic_overlap_damping_mid_entropy_threshold"),
            "retrieval_controls.semantic_overlap_damping_mid_entropy_threshold",
            float(defaults["semantic_overlap_damping_mid_entropy_threshold"]),
        ),
        "semantic_overlap_damping_low_entropy": _validate_fraction_zero_to_one(
            retrieval.get("semantic_overlap_damping_low_entropy"),
            "retrieval_controls.semantic_overlap_damping_low_entropy",
            float(defaults["semantic_overlap_damping_low_entropy"]),
        ),
        "semantic_overlap_damping_mid_entropy": _validate_fraction_zero_to_one(
            retrieval.get("semantic_overlap_damping_mid_entropy"),
            "retrieval_controls.semantic_overlap_damping_mid_entropy",
            float(defaults["semantic_overlap_damping_mid_entropy"]),
        ),
        "enable_numeric_confidence_scaling": _validate_bool_like(
            retrieval.get("enable_numeric_confidence_scaling"),
            "retrieval_controls.enable_numeric_confidence_scaling",
            bool(defaults["enable_numeric_confidence_scaling"]),
        ),
        "numeric_confidence_floor": _validate_fraction_zero_to_one(
            retrieval.get("numeric_confidence_floor"),
            "retrieval_controls.numeric_confidence_floor",
            float(defaults["numeric_confidence_floor"]),
        ),
        "profile_numeric_confidence_mode": str(
            retrieval.get("profile_numeric_confidence_mode") or defaults["profile_numeric_confidence_mode"]
        ),
        "profile_numeric_confidence_blend_weight": _validate_fraction_zero_to_one(
            retrieval.get("profile_numeric_confidence_blend_weight"),
            "retrieval_controls.profile_numeric_confidence_blend_weight",
            float(defaults["profile_numeric_confidence_blend_weight"]),
        ),
        "numeric_support_score_mode": str(
            retrieval.get("numeric_support_score_mode") or defaults["numeric_support_score_mode"]
        ),
        "emit_profile_policy_diagnostics": _validate_bool_like(
            retrieval.get("emit_profile_policy_diagnostics"),
            "retrieval_controls.emit_profile_policy_diagnostics",
            bool(defaults["emit_profile_policy_diagnostics"]),
        ),
    }


def resolve_bl006_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    scoring = effective["scoring_controls"]
    control_mode = effective.get("control_mode") or {}
    defaults = DEFAULT_RUN_CONFIG["scoring_controls"]
    component_weights = _validate_component_weights(
        scoring.get("component_weights") or defaults["component_weights"],
        "scoring_controls.component_weights",
        enforce_sum=not bool(control_mode.get("allow_weight_auto_normalization", False)),
    )
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "signal_mode": dict(effective.get("signal_mode") or {}),
        "component_weights": component_weights,
        "numeric_thresholds": _validate_positive_thresholds(
            scoring.get("numeric_thresholds") or defaults["numeric_thresholds"],
            "scoring_controls.numeric_thresholds"
        ),
        "lead_genre_strategy": str(scoring.get("lead_genre_strategy") or defaults["lead_genre_strategy"]),
        "semantic_overlap_strategy": str(scoring.get("semantic_overlap_strategy") or defaults["semantic_overlap_strategy"]),
        "semantic_precision_alpha_mode": str(scoring.get("semantic_precision_alpha_mode") or defaults["semantic_precision_alpha_mode"]),
        "semantic_precision_alpha_fixed": _validate_fraction_zero_to_one(
            scoring.get("semantic_precision_alpha_fixed"),
            "scoring_controls.semantic_precision_alpha_fixed",
            float(defaults["semantic_precision_alpha_fixed"]),
        ),
        "enable_numeric_confidence_scaling": _validate_bool_like(
            scoring.get("enable_numeric_confidence_scaling"),
            "scoring_controls.enable_numeric_confidence_scaling",
            bool(defaults["enable_numeric_confidence_scaling"]),
        ),
        "numeric_confidence_floor": _validate_fraction_zero_to_one(
            scoring.get("numeric_confidence_floor"),
            "scoring_controls.numeric_confidence_floor",
            float(defaults["numeric_confidence_floor"]),
        ),
        "profile_numeric_confidence_mode": str(
            scoring.get("profile_numeric_confidence_mode") or defaults["profile_numeric_confidence_mode"]
        ),
        "profile_numeric_confidence_blend_weight": _validate_fraction_zero_to_one(
            scoring.get("profile_numeric_confidence_blend_weight"),
            "scoring_controls.profile_numeric_confidence_blend_weight",
            float(defaults["profile_numeric_confidence_blend_weight"]),
        ),
        "emit_confidence_impact_diagnostics": _validate_bool_like(
            scoring.get("emit_confidence_impact_diagnostics"),
            "scoring_controls.emit_confidence_impact_diagnostics",
            bool(defaults["emit_confidence_impact_diagnostics"]),
        ),
        "emit_semantic_precision_diagnostics": _validate_bool_like(
            scoring.get("emit_semantic_precision_diagnostics"),
            "scoring_controls.emit_semantic_precision_diagnostics",
            bool(defaults["emit_semantic_precision_diagnostics"]),
        ),
        "apply_bl003_influence_tracks": _validate_bool_like(
            scoring.get("apply_bl003_influence_tracks"),
            "scoring_controls.apply_bl003_influence_tracks",
            bool(defaults["apply_bl003_influence_tracks"]),
        ),
        "influence_track_bonus_scale": _coerce_non_negative_float(
            scoring.get("influence_track_bonus_scale"),
            float(defaults["influence_track_bonus_scale"]),
        ),
    }


def resolve_bl007_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    assembly = effective["assembly_controls"]
    defaults = DEFAULT_RUN_CONFIG["assembly_controls"]
    min_threshold = assembly.get("min_score_threshold")
    utility_strategy_raw = str(assembly.get("utility_strategy") or defaults["utility_strategy"]).strip().lower()
    utility_strategy = utility_strategy_raw if utility_strategy_raw in {"rank_round_robin", "utility_greedy"} else str(defaults["utility_strategy"])

    utility_weights_raw = assembly.get("utility_weights")
    utility_weights_defaults = defaults.get("utility_weights") or {}
    utility_weights = {
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

    relaxation_raw = assembly.get("controlled_relaxation")
    relaxation_defaults = defaults.get("controlled_relaxation") or {}
    controlled_relaxation = {
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

    lead_genre_fallback_raw = str(
        assembly.get("lead_genre_fallback_strategy") or defaults.get("lead_genre_fallback_strategy", "none")
    ).strip().lower()
    lead_genre_fallback_strategy = (
        lead_genre_fallback_raw
        if lead_genre_fallback_raw in {"none", "semantic_component_proxy"}
        else str(defaults.get("lead_genre_fallback_strategy", "none"))
    )

    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "target_size": _coerce_positive_int(
            assembly.get("target_size"),
            defaults["target_size"],
        ),
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
        "utility_strategy": utility_strategy,
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
        "detail_log_top_k": _coerce_positive_int(
            assembly.get("detail_log_top_k"),
            int(defaults.get("detail_log_top_k", 100)),
        ),
    }


def resolve_bl008_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    transparency = effective["transparency_controls"]
    defaults = DEFAULT_RUN_CONFIG["transparency_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "top_contributor_limit": _coerce_positive_int(
            transparency.get("top_contributor_limit"),
            defaults["top_contributor_limit"],
        ),
        "blend_primary_contributor_on_near_tie": _coerce_bool(
            transparency.get("blend_primary_contributor_on_near_tie"),
            bool(defaults["blend_primary_contributor_on_near_tie"]),
        ),
        "primary_contributor_tie_delta": _coerce_non_negative_float(
            transparency.get("primary_contributor_tie_delta"),
            float(defaults["primary_contributor_tie_delta"]),
        ),
    }


def resolve_bl009_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    observability = effective["observability_controls"]
    control_mode = effective.get("control_mode") or {}
    defaults = DEFAULT_RUN_CONFIG["observability_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "control_mode": {
            "validation_profile": str(control_mode.get("validation_profile", "strict")),
            "allow_threshold_decoupling": bool(control_mode.get("allow_threshold_decoupling", False)),
            "allow_weight_auto_normalization": bool(control_mode.get("allow_weight_auto_normalization", False)),
        },
        "diagnostic_sample_limit": _coerce_positive_int(
            observability.get("diagnostic_sample_limit"),
            defaults["diagnostic_sample_limit"],
        ),
        "bootstrap_mode": _coerce_bool(
            observability.get("bootstrap_mode"),
            bool(defaults["bootstrap_mode"]),
        ),
    }


def resolve_bl013_orchestration_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    raw = effective.get("orchestration_controls") or {}
    if not isinstance(raw, dict):
        raw = {}
    merged: dict[str, Any] = {**DEFAULT_ORCHESTRATION_CONTROLS, **raw}
    raw_stage_order = merged.get("stage_order")
    stage_order: list[str] | None = list(raw_stage_order) if isinstance(raw_stage_order, list) else None
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "stage_order": stage_order,
        "continue_on_error": bool(merged.get("continue_on_error", False)),
        "refresh_seed_policy": str(merged.get("refresh_seed_policy") or "auto_if_stale"),
        "required_stable_artifacts": list(merged.get("required_stable_artifacts") or []),
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
        "resolved_from": {
            "run_config_path": str(resolved_path) if resolved_path else None,
            "run_intent_path": str(Path(run_intent_path).resolve()) if run_intent_path else None,
        },
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

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
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
