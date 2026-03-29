"""Runtime control resolution for BL-004 profile construction."""

from __future__ import annotations

from shared_utils.constants import (
    DEFAULT_INCLUDE_INTERACTION_TYPES,
    DEFAULT_PROFILE_CONTROLS,
)
from shared_utils.env_utils import env_bool, env_float, env_int, env_str
from shared_utils.stage_runtime_resolver import resolve_stage_controls


def _normalize_include_interaction_types(raw_value: object) -> list[str]:
    allowed = {"history", "influence"}
    normalized: list[str] = []
    seen: set[str] = set()
    if isinstance(raw_value, list):
        values = raw_value
    elif isinstance(raw_value, str):
        values = [token.strip() for token in raw_value.split(",")]
    else:
        values = []

    for item in values:
        token = str(item).strip().lower()
        if token in allowed and token not in seen:
            seen.add(token)
            normalized.append(token)
    return normalized or list(DEFAULT_INCLUDE_INTERACTION_TYPES)


def _sanitize_bl004_controls(controls: dict[str, object]) -> dict[str, object]:
    defaults = DEFAULT_PROFILE_CONTROLS
    controls["top_tag_limit"] = max(1, int(controls.get("top_tag_limit", defaults["top_tag_limit"])))
    controls["top_genre_limit"] = max(1, int(controls.get("top_genre_limit", defaults["top_genre_limit"])))
    controls["top_lead_genre_limit"] = max(
        1,
        int(controls.get("top_lead_genre_limit", defaults["top_lead_genre_limit"])),
    )

    weighting_mode = str(
        controls.get("confidence_weighting_mode", defaults["confidence_weighting_mode"])
    ).strip().lower()
    controls["confidence_weighting_mode"] = (
        weighting_mode if weighting_mode in {"linear_half_bias", "direct_confidence", "none"} else str(defaults["confidence_weighting_mode"])
    )

    high_threshold = max(
        0.0,
        min(1.0, float(controls.get("confidence_bin_high_threshold", defaults["confidence_bin_high_threshold"]))),
    )
    medium_threshold = max(
        0.0,
        min(1.0, float(controls.get("confidence_bin_medium_threshold", defaults["confidence_bin_medium_threshold"]))),
    )
    controls["confidence_bin_high_threshold"] = high_threshold
    controls["confidence_bin_medium_threshold"] = min(medium_threshold, high_threshold)

    attribution_mode = str(
        controls.get("interaction_attribution_mode", defaults["interaction_attribution_mode"])
    ).strip().lower()
    controls["interaction_attribution_mode"] = (
        attribution_mode
        if attribution_mode in {"split_selected_types_equal_share", "primary_type_only"}
        else str(defaults["interaction_attribution_mode"])
    )

    controls["emit_profile_policy_diagnostics"] = bool(
        controls.get("emit_profile_policy_diagnostics", defaults["emit_profile_policy_diagnostics"])
    )

    controls["include_interaction_types"] = _normalize_include_interaction_types(
        controls.get("include_interaction_types")
    )
    controls["user_id"] = str(controls.get("user_id") or "unknown_user").strip() or "unknown_user"
    return controls


def _load_bl004_controls_from_run_config(run_config_utils: object, run_config_path: str) -> dict[str, object]:
    controls = run_config_utils.resolve_bl004_controls(run_config_path)
    env_user_id = env_str("BL004_USER_ID", "")
    env_types = _normalize_include_interaction_types(env_str("BL004_INCLUDE_INTERACTION_TYPES", ""))
    include_types = env_types if env_str("BL004_INCLUDE_INTERACTION_TYPES", "").strip() else list(controls.get("include_interaction_types") or DEFAULT_INCLUDE_INTERACTION_TYPES)
    return {
        "config_source": "run_config",
        "run_config_path": controls.get("config_path"),
        "run_config_schema_version": controls.get("schema_version"),
        "input_scope": dict(controls.get("input_scope") or {}),
        "top_tag_limit": controls.get("top_tag_limit"),
        "top_genre_limit": controls.get("top_genre_limit"),
        "top_lead_genre_limit": controls.get("top_lead_genre_limit"),
        "confidence_weighting_mode": controls.get("confidence_weighting_mode"),
        "confidence_bin_high_threshold": controls.get("confidence_bin_high_threshold"),
        "confidence_bin_medium_threshold": controls.get("confidence_bin_medium_threshold"),
        "interaction_attribution_mode": controls.get("interaction_attribution_mode"),
        "emit_profile_policy_diagnostics": controls.get("emit_profile_policy_diagnostics"),
        "user_id": env_user_id or controls.get("user_id") or "unknown_user",
        "include_interaction_types": include_types,
    }


def _load_bl004_controls_from_env() -> dict[str, object]:
    defaults = DEFAULT_PROFILE_CONTROLS
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope": {},
        "top_tag_limit": env_int("BL004_TOP_TAG_LIMIT", int(defaults["top_tag_limit"])),
        "top_genre_limit": env_int("BL004_TOP_GENRE_LIMIT", int(defaults["top_genre_limit"])),
        "top_lead_genre_limit": env_int("BL004_TOP_LEAD_GENRE_LIMIT", int(defaults["top_lead_genre_limit"])),
        "confidence_weighting_mode": env_str(
            "BL004_CONFIDENCE_WEIGHTING_MODE",
            str(defaults["confidence_weighting_mode"]),
        ),
        "confidence_bin_high_threshold": env_float(
            "BL004_CONFIDENCE_BIN_HIGH_THRESHOLD",
            float(defaults["confidence_bin_high_threshold"]),
        ),
        "confidence_bin_medium_threshold": env_float(
            "BL004_CONFIDENCE_BIN_MEDIUM_THRESHOLD",
            float(defaults["confidence_bin_medium_threshold"]),
        ),
        "interaction_attribution_mode": env_str(
            "BL004_INTERACTION_ATTRIBUTION_MODE",
            str(defaults["interaction_attribution_mode"]),
        ),
        "emit_profile_policy_diagnostics": env_bool(
            "BL004_EMIT_PROFILE_POLICY_DIAGNOSTICS",
            bool(defaults["emit_profile_policy_diagnostics"]),
        ),
        "user_id": env_str("BL004_USER_ID", "unknown_user"),
        "include_interaction_types": _normalize_include_interaction_types(
            env_str("BL004_INCLUDE_INTERACTION_TYPES", "")
        ),
    }


def resolve_bl004_runtime_controls(*, inferred_user_id: str | None = None) -> dict[str, object]:
    controls = resolve_stage_controls(
        load_from_run_config=_load_bl004_controls_from_run_config,
        load_from_env=_load_bl004_controls_from_env,
        sanitize=_sanitize_bl004_controls,
    )
    if controls.get("user_id") in {None, "", "unknown_user"} and inferred_user_id:
        controls["user_id"] = inferred_user_id
    return controls
