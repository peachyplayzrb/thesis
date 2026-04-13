"""Runtime control resolution for BL-004 profile construction."""

from __future__ import annotations

from typing import Mapping

from shared_utils.constants import (
    DEFAULT_INCLUDE_INTERACTION_TYPES,
    DEFAULT_INPUT_SCOPE,
    DEFAULT_PROFILE_CONTROLS,
    VALID_CONFIDENCE_WEIGHTING_MODES,
    VALID_INTERACTION_ATTRIBUTION_MODES,
)
from shared_utils.env_utils import (
    coerce_enum,
    coerce_float,
    coerce_int,
    env_bool,
    env_float,
    env_int,
    env_str,
)
from shared_utils.stage_runtime_resolver import defaults_loader, resolve_stage_controls


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
    controls["top_tag_limit"] = max(1, coerce_int(controls.get("top_tag_limit", defaults["top_tag_limit"]), 10))
    controls["top_genre_limit"] = max(1, coerce_int(controls.get("top_genre_limit", defaults["top_genre_limit"]), 8))
    controls["top_lead_genre_limit"] = max(
        1, coerce_int(controls.get("top_lead_genre_limit", defaults["top_lead_genre_limit"]), 6),
    )

    controls["confidence_weighting_mode"] = coerce_enum(
        controls.get("confidence_weighting_mode", defaults["confidence_weighting_mode"]),
        VALID_CONFIDENCE_WEIGHTING_MODES,
        str(defaults["confidence_weighting_mode"]),
    )

    high_threshold = max(
        0.0, min(1.0, coerce_float(controls.get("confidence_bin_high_threshold", defaults["confidence_bin_high_threshold"]), 0.90)),
    )
    medium_threshold = max(
        0.0, min(1.0, coerce_float(controls.get("confidence_bin_medium_threshold", defaults["confidence_bin_medium_threshold"]), 0.50)),
    )
    controls["confidence_bin_high_threshold"] = high_threshold
    controls["confidence_bin_medium_threshold"] = min(medium_threshold, high_threshold)

    controls["interaction_attribution_mode"] = coerce_enum(
        controls.get("interaction_attribution_mode", defaults["interaction_attribution_mode"]),
        VALID_INTERACTION_ATTRIBUTION_MODES,
        str(defaults["interaction_attribution_mode"]),
    )

    controls["emit_profile_policy_diagnostics"] = bool(
        controls.get("emit_profile_policy_diagnostics", defaults["emit_profile_policy_diagnostics"])
    )
    controls["confidence_validation_policy"] = coerce_enum(
        controls.get("confidence_validation_policy", defaults["confidence_validation_policy"]),
        ("allow", "warn", "strict"),
        str(defaults["confidence_validation_policy"]),
    )
    controls["interaction_type_validation_policy"] = coerce_enum(
        controls.get("interaction_type_validation_policy", defaults["interaction_type_validation_policy"]),
        ("allow", "warn", "strict"),
        str(defaults["interaction_type_validation_policy"]),
    )
    controls["synthetic_data_validation_policy"] = coerce_enum(
        controls.get("synthetic_data_validation_policy", defaults["synthetic_data_validation_policy"]),
        ("allow", "warn", "strict"),
        str(defaults["synthetic_data_validation_policy"]),
    )
    controls["bl003_handshake_validation_policy"] = coerce_enum(
        controls.get("bl003_handshake_validation_policy", defaults["bl003_handshake_validation_policy"]),
        ("allow", "warn", "strict"),
        str(defaults["bl003_handshake_validation_policy"]),
    )
    malformed_threshold = coerce_int(
        controls.get("numeric_malformed_row_threshold", defaults["numeric_malformed_row_threshold"]),
        0,
    )
    controls["numeric_malformed_row_threshold"] = malformed_threshold if malformed_threshold > 0 else None
    no_signal_threshold = coerce_int(
        controls.get("no_numeric_signal_row_threshold", defaults["no_numeric_signal_row_threshold"]),
        0,
    )
    controls["no_numeric_signal_row_threshold"] = no_signal_threshold if no_signal_threshold > 0 else None

    controls["include_interaction_types"] = _normalize_include_interaction_types(
        controls.get("include_interaction_types")
    )
    controls["user_id"] = str(controls.get("user_id") or "unknown_user").strip() or "unknown_user"
    input_scope_raw = controls.get("input_scope")
    input_scope_payload = dict(input_scope_raw) if isinstance(input_scope_raw, Mapping) else {}
    controls["input_scope"] = input_scope_payload or dict(DEFAULT_INPUT_SCOPE)
    return controls


def _load_bl004_controls_from_env() -> dict[str, object]:
    defaults = DEFAULT_PROFILE_CONTROLS
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope": {},
        "top_tag_limit": env_int("BL004_TOP_TAG_LIMIT", int(str(defaults["top_tag_limit"]))),
        "top_genre_limit": env_int("BL004_TOP_GENRE_LIMIT", int(str(defaults["top_genre_limit"]))),
        "top_lead_genre_limit": env_int("BL004_TOP_LEAD_GENRE_LIMIT", int(str(defaults["top_lead_genre_limit"]))),
        "confidence_weighting_mode": env_str(
            "BL004_CONFIDENCE_WEIGHTING_MODE",
            str(defaults["confidence_weighting_mode"]),
        ),
        "confidence_bin_high_threshold": env_float(
            "BL004_CONFIDENCE_BIN_HIGH_THRESHOLD",
            float(str(defaults["confidence_bin_high_threshold"])),
        ),
        "confidence_bin_medium_threshold": env_float(
            "BL004_CONFIDENCE_BIN_MEDIUM_THRESHOLD",
            float(str(defaults["confidence_bin_medium_threshold"])),
        ),
        "interaction_attribution_mode": env_str(
            "BL004_INTERACTION_ATTRIBUTION_MODE",
            str(defaults["interaction_attribution_mode"]),
        ),
        "emit_profile_policy_diagnostics": env_bool(
            "BL004_EMIT_PROFILE_POLICY_DIAGNOSTICS",
            bool(defaults["emit_profile_policy_diagnostics"]),
        ),
        "confidence_validation_policy": env_str(
            "BL004_CONFIDENCE_VALIDATION_POLICY",
            str(defaults["confidence_validation_policy"]),
        ),
        "interaction_type_validation_policy": env_str(
            "BL004_INTERACTION_TYPE_VALIDATION_POLICY",
            str(defaults["interaction_type_validation_policy"]),
        ),
        "synthetic_data_validation_policy": env_str(
            "BL004_SYNTHETIC_DATA_VALIDATION_POLICY",
            str(defaults["synthetic_data_validation_policy"]),
        ),
        "bl003_handshake_validation_policy": env_str(
            "BL004_BL003_HANDSHAKE_VALIDATION_POLICY",
            str(defaults["bl003_handshake_validation_policy"]),
        ),
        "numeric_malformed_row_threshold": env_int(
            "BL004_NUMERIC_MALFORMED_ROW_THRESHOLD",
            int(defaults.get("numeric_malformed_row_threshold") or 0),
        ),
        "no_numeric_signal_row_threshold": env_int(
            "BL004_NO_NUMERIC_SIGNAL_ROW_THRESHOLD",
            int(defaults.get("no_numeric_signal_row_threshold") or 0),
        ),
        "user_id": env_str("BL004_USER_ID", "unknown_user"),
        "include_interaction_types": _normalize_include_interaction_types(
            env_str("BL004_INCLUDE_INTERACTION_TYPES", "")
        ),
    }


def resolve_bl004_runtime_controls(*, inferred_user_id: str | None = None) -> dict[str, object]:
    controls = resolve_stage_controls(
        load_from_env=_load_bl004_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_PROFILE_CONTROLS),
        sanitize=_sanitize_bl004_controls,
    )
    if controls.get("user_id") in {None, "", "unknown_user"} and inferred_user_id:
        controls["user_id"] = inferred_user_id
    return controls
