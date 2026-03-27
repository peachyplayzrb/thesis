from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
from typing import Any

from bl000_shared_utils.constants import (
    DEFAULT_PROFILE_TOP_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_TAG_LIMIT,
    DEFAULT_SCORING_COMPONENT_WEIGHTS,
)

try:
    from bl000_shared_utils.io_utils import open_text_write
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from bl000_shared_utils.io_utils import open_text_write

RUN_CONFIG_SCHEMA_VERSION = "run-config-v1"
RUN_INTENT_ARTIFACT_SCHEMA_VERSION = "run-intent-v1"
RUN_EFFECTIVE_ARTIFACT_SCHEMA_VERSION = "run-effective-config-v1"

DEFAULT_RUN_CONFIG: dict[str, Any] = {
    "schema_version": RUN_CONFIG_SCHEMA_VERSION,
    "control_mode": {
        "validation_profile": "strict",
        "allow_threshold_decoupling": False,
        "allow_weight_auto_normalization": False,
    },
    "user_context": {
        "user_id": None,
    },
    "input_scope": {
        "source_family": "spotify_api_export",
        "include_top_tracks": True,
        "top_time_ranges": ["short_term", "medium_term", "long_term"],
        "include_saved_tracks": True,
        "saved_tracks_limit": None,
        "include_playlists": True,
        "playlists_limit": None,
        "playlist_items_per_playlist_limit": None,
        "include_recently_played": True,
        "recently_played_limit": 50,
    },
    "interaction_scope": {
        "include_interaction_types": ["history", "influence"],
    },
    "influence_tracks": {
        "enabled": True,
        "track_ids": [],
        "preference_weight": 1.0,
        "source": None,
    },
    "seed_controls": {
        "match_rate_min_threshold": 0.0,
        "top_range_weights": {
            "short_term": 0.50,
            "medium_term": 0.30,
            "long_term": 0.20,
        },
        "source_base_weights": {
            "top_tracks": 1.00,
            "saved_tracks": 0.60,
            "playlist_items": 0.40,
            "recently_played": 0.50,
        },
    },
    "ingestion_controls": {
        "cache_ttl_seconds": 86400,
        "throttle_sleep_seconds": 0.12,
        "max_retries": 6,
        "base_backoff_delay_seconds": 1.0,
    },
    "profile_controls": {
        "top_tag_limit": DEFAULT_PROFILE_TOP_TAG_LIMIT,
        "top_genre_limit": DEFAULT_PROFILE_TOP_GENRE_LIMIT,
        "top_lead_genre_limit": DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    },
    "retrieval_controls": {
        "profile_top_tag_limit": 10,
        "profile_top_genre_limit": 8,
        "profile_top_lead_genre_limit": 6,
        "semantic_strong_keep_score": 2,
        "semantic_min_keep_score": 1,
        "numeric_support_min_pass": 1,
        "numeric_thresholds": {
            "danceability": 0.20,
            "energy": 0.20,
            "valence": 0.20,
            "tempo": 20.0,
            "key": 2.0,
            "mode": 0.5,
            "duration_ms": 45000.0,
        },
    },
    "scoring_controls": {
        "component_weights": dict(DEFAULT_SCORING_COMPONENT_WEIGHTS),
        "numeric_thresholds": {
            "danceability": 0.20,
            "energy": 0.20,
            "valence": 0.20,
            "tempo": 20.0,
            "key": 2.0,
            "mode": 0.5,
            "duration_ms": 45000.0,
        },
    },
    "assembly_controls": {
        "target_size": 10,
        "min_score_threshold": 0.35,
        "max_per_genre": 4,
        "max_consecutive": 2,
    },
    "transparency_controls": {
        "top_contributor_limit": 3,
        "blend_primary_contributor_on_near_tie": False,
        "primary_contributor_tie_delta": 0.02,
    },
    "observability_controls": {
        "diagnostic_sample_limit": 5,
        "bootstrap_mode": True,
    },
    "reporting_controls": {
        "score_thresholds": {
            "perfect_score": 0.99,
            "above_threshold": 0.50,
        },
    },
    "controllability_controls": {
        "weight_override_value_if_component_present": 0.20,
        "weight_override_increment_fallback": 0.08,
        "weight_override_cap_fallback": 0.35,
        "stricter_threshold_scale": 0.75,
        "looser_threshold_scale": 1.25,
    },
}



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

    interaction_scope = effective.setdefault("interaction_scope", {})
    if not isinstance(interaction_scope, dict):
        interaction_scope = {}
        effective["interaction_scope"] = interaction_scope
    interaction_scope["include_interaction_types"] = _normalize_allowed_tokens(
        interaction_scope.get("include_interaction_types"),
        {"history", "influence"},
        list(DEFAULT_RUN_CONFIG["interaction_scope"]["include_interaction_types"]),
    )

    influence_tracks = effective.setdefault("influence_tracks", {})
    if not isinstance(influence_tracks, dict):
        influence_tracks = {}
        effective["influence_tracks"] = influence_tracks
    influence_defaults = DEFAULT_RUN_CONFIG["influence_tracks"]
    influence_tracks["enabled"] = _coerce_bool(influence_tracks.get("enabled"), bool(influence_defaults["enabled"]))
    raw_ids = influence_tracks.get("track_ids")
    if isinstance(raw_ids, list):
        track_ids: list[str] = []
        seen_track_ids: set[str] = set()
        for item in raw_ids:
            track_id = str(item).strip()
            if not track_id or track_id in seen_track_ids:
                continue
            seen_track_ids.add(track_id)
            track_ids.append(track_id)
        influence_tracks["track_ids"] = track_ids
    else:
        influence_tracks["track_ids"] = []
    raw_pw = influence_tracks.get("preference_weight")
    try:
        pw = float(raw_pw) if raw_pw is not None else float(influence_defaults["preference_weight"])
    except (TypeError, ValueError):
        pw = float(influence_defaults["preference_weight"])
    influence_tracks["preference_weight"] = pw if pw > 0 else float(influence_defaults["preference_weight"])
    influence_tracks["source"] = _coerce_optional_str(influence_tracks.get("source"))

    seed_controls = effective.setdefault("seed_controls", {})
    if not isinstance(seed_controls, dict):
        raise RunConfigError("run_config.seed_controls must be an object")
    seed_defaults = DEFAULT_RUN_CONFIG["seed_controls"]
    seed_controls["match_rate_min_threshold"] = _coerce_fraction_zero_to_one(
        seed_controls.get("match_rate_min_threshold"),
        float(seed_defaults["match_rate_min_threshold"]),
    )
    
    # Resolve weight dicts for seed controls (env override support via direct access)
    if "top_range_weights" not in seed_controls or not isinstance(seed_controls.get("top_range_weights"), dict):
        seed_controls["top_range_weights"] = seed_defaults["top_range_weights"].copy()
    if "source_base_weights" not in seed_controls or not isinstance(seed_controls.get("source_base_weights"), dict):
        seed_controls["source_base_weights"] = seed_defaults["source_base_weights"].copy()

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
    _enforce_profile_retrieval_limit_constraints(profile_controls, retrieval_controls)

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


def resolve_bl005_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    retrieval = effective["retrieval_controls"]
    defaults = DEFAULT_RUN_CONFIG["retrieval_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
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
        "numeric_thresholds": _validate_positive_thresholds(
            retrieval.get("numeric_thresholds") or defaults["numeric_thresholds"],
            "retrieval_controls.numeric_thresholds"
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
        "component_weights": component_weights,
        "numeric_thresholds": _validate_positive_thresholds(
            scoring.get("numeric_thresholds") or defaults["numeric_thresholds"],
            "scoring_controls.numeric_thresholds"
        ),
    }


def resolve_bl007_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    assembly = effective["assembly_controls"]
    defaults = DEFAULT_RUN_CONFIG["assembly_controls"]
    min_threshold = assembly.get("min_score_threshold")
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
