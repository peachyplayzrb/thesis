"""Runtime control resolution for BL-005 candidate retrieval."""

from __future__ import annotations

from shared_utils.constants import (
    DEFAULT_RETRIEVAL_CONTROLS,
)
from shared_utils.env_utils import env_bool, env_float, env_int, env_str
from shared_utils.stage_runtime_resolver import load_positive_numeric_map_from_env, resolve_stage_controls


def _sanitize_bl005_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["profile_top_lead_genre_limit"] = max(1, int(controls.get("profile_top_lead_genre_limit", 6)))
    controls["profile_top_tag_limit"] = max(1, int(controls.get("profile_top_tag_limit", 10)))
    controls["profile_top_genre_limit"] = max(1, int(controls.get("profile_top_genre_limit", 8)))
    controls["semantic_strong_keep_score"] = max(0, min(3, int(controls.get("semantic_strong_keep_score", 2))))
    controls["semantic_min_keep_score"] = max(0, min(3, int(controls.get("semantic_min_keep_score", 1))))
    controls["numeric_support_min_pass"] = max(0, int(controls.get("numeric_support_min_pass", 1)))
    controls["numeric_support_min_score"] = max(0.0, float(controls.get("numeric_support_min_score", 1.0)))
    controls["lead_genre_partial_match_threshold"] = max(
        0.0,
        min(1.0, float(controls.get("lead_genre_partial_match_threshold", 0.5))),
    )
    controls["use_weighted_semantics"] = bool(controls.get("use_weighted_semantics", False))
    controls["use_continuous_numeric"] = bool(controls.get("use_continuous_numeric", False))
    controls["enable_popularity_numeric"] = bool(controls.get("enable_popularity_numeric", False))

    codes = controls.get("language_filter_codes")
    normalized_codes: list[str] = []
    if isinstance(codes, list):
        seen: set[str] = set()
        for item in codes:
            code = str(item).strip().lower()
            if not code or code in seen:
                continue
            seen.add(code)
            normalized_codes.append(code)
    controls["language_filter_codes"] = normalized_codes
    controls["language_filter_enabled"] = bool(controls.get("language_filter_enabled", False)) and bool(normalized_codes)

    recency_raw = str(controls.get("recency_years_min_offset", "")).strip()
    if recency_raw:
        try:
            parsed = int(recency_raw)
            controls["recency_years_min_offset"] = parsed if parsed > 0 else None
        except ValueError:
            controls["recency_years_min_offset"] = None
    else:
        controls["recency_years_min_offset"] = None

    numeric_thresholds_raw = controls.get("numeric_thresholds")
    numeric_thresholds: dict[str, float] = {}
    if isinstance(numeric_thresholds_raw, dict):
        for key, value in numeric_thresholds_raw.items():
            try:
                parsed = float(value)
            except (TypeError, ValueError):
                continue
            if parsed > 0:
                numeric_thresholds[str(key)] = parsed
    controls["numeric_thresholds"] = numeric_thresholds

    controls["profile_quality_penalty_enabled"] = bool(controls.get("profile_quality_penalty_enabled", True))
    controls["profile_quality_threshold"] = max(0.0, min(1.0, float(controls.get("profile_quality_threshold", 0.90))))
    controls["profile_entropy_low_threshold"] = max(
        0.0,
        min(1.0, float(controls.get("profile_entropy_low_threshold", 0.35))),
    )
    controls["influence_share_threshold"] = max(0.0, min(1.0, float(controls.get("influence_share_threshold", 0.60))))
    controls["profile_quality_penalty_increment"] = max(
        0.0,
        float(controls.get("profile_quality_penalty_increment", 0.20)),
    )
    controls["profile_entropy_penalty_increment"] = max(
        0.0,
        float(controls.get("profile_entropy_penalty_increment", 0.20)),
    )
    controls["influence_share_penalty_increment"] = max(
        0.0,
        float(controls.get("influence_share_penalty_increment", 0.15)),
    )
    controls["numeric_penalty_scale"] = max(0.0, float(controls.get("numeric_penalty_scale", 0.50)))

    controls["semantic_overlap_damping_mid_entropy_threshold"] = max(
        0.0,
        min(1.0, float(controls.get("semantic_overlap_damping_mid_entropy_threshold", 0.60))),
    )
    controls["semantic_overlap_damping_low_entropy"] = max(
        0.0,
        min(1.0, float(controls.get("semantic_overlap_damping_low_entropy", 0.85))),
    )
    controls["semantic_overlap_damping_mid_entropy"] = max(
        0.0,
        min(1.0, float(controls.get("semantic_overlap_damping_mid_entropy", 0.92))),
    )

    controls["enable_numeric_confidence_scaling"] = bool(controls.get("enable_numeric_confidence_scaling", True))
    controls["numeric_confidence_floor"] = max(0.0, min(1.0, float(controls.get("numeric_confidence_floor", 0.0))))

    profile_mode = str(controls.get("profile_numeric_confidence_mode", "direct")).strip().lower()
    controls["profile_numeric_confidence_mode"] = profile_mode if profile_mode in {"direct", "blended"} else "direct"
    controls["profile_numeric_confidence_blend_weight"] = max(
        0.0,
        min(1.0, float(controls.get("profile_numeric_confidence_blend_weight", 1.0))),
    )

    score_mode = str(controls.get("numeric_support_score_mode", "weighted_absolute")).strip().lower()
    controls["numeric_support_score_mode"] = (
        score_mode if score_mode in {"raw", "weighted", "weighted_absolute"} else "weighted_absolute"
    )
    controls["emit_profile_policy_diagnostics"] = bool(controls.get("emit_profile_policy_diagnostics", True))

    return controls


def _load_bl005_controls_from_env() -> dict[str, object]:
    defaults = DEFAULT_RETRIEVAL_CONTROLS
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "signal_mode": {},
        "profile_top_lead_genre_limit": env_int("BL005_PROFILE_TOP_LEAD_GENRE_LIMIT", int(defaults["profile_top_lead_genre_limit"])),
        "profile_top_tag_limit": env_int("BL005_PROFILE_TOP_TAG_LIMIT", int(defaults["profile_top_tag_limit"])),
        "profile_top_genre_limit": env_int("BL005_PROFILE_TOP_GENRE_LIMIT", int(defaults["profile_top_genre_limit"])),
        "semantic_strong_keep_score": env_int("BL005_SEMANTIC_STRONG_KEEP_SCORE", int(defaults["semantic_strong_keep_score"])),
        "semantic_min_keep_score": env_int("BL005_SEMANTIC_MIN_KEEP_SCORE", int(defaults["semantic_min_keep_score"])),
        "numeric_support_min_pass": env_int("BL005_NUMERIC_SUPPORT_MIN_PASS", int(defaults["numeric_support_min_pass"])),
        "numeric_support_min_score": env_float("BL005_NUMERIC_SUPPORT_MIN_SCORE", float(defaults["numeric_support_min_score"])),
        "lead_genre_partial_match_threshold": env_float(
            "BL005_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD",
            float(defaults["lead_genre_partial_match_threshold"]),
        ),
        "use_weighted_semantics": env_bool("BL005_USE_WEIGHTED_SEMANTICS", bool(defaults["use_weighted_semantics"])),
        "use_continuous_numeric": env_bool("BL005_USE_CONTINUOUS_NUMERIC", bool(defaults["use_continuous_numeric"])),
        "enable_popularity_numeric": env_bool("BL005_ENABLE_POPULARITY_NUMERIC", bool(defaults["enable_popularity_numeric"])),
        "language_filter_enabled": env_bool("BL005_LANGUAGE_FILTER_ENABLED", bool(defaults["language_filter_enabled"])),
        "language_filter_codes": [
            token.strip().lower()
            for token in env_str("BL005_LANGUAGE_FILTER_CODES", "").split(",")
            if token.strip()
        ],
        "recency_years_min_offset": env_str("BL005_RECENCY_YEARS_MIN_OFFSET", ""),
        "numeric_thresholds": load_positive_numeric_map_from_env("BL005_NUMERIC_THRESHOLDS_JSON"),
        "profile_quality_penalty_enabled": env_bool(
            "BL005_PROFILE_QUALITY_PENALTY_ENABLED",
            bool(defaults["profile_quality_penalty_enabled"]),
        ),
        "profile_quality_threshold": env_float("BL005_PROFILE_QUALITY_THRESHOLD", float(defaults["profile_quality_threshold"])),
        "profile_entropy_low_threshold": env_float(
            "BL005_PROFILE_ENTROPY_LOW_THRESHOLD",
            float(defaults["profile_entropy_low_threshold"]),
        ),
        "influence_share_threshold": env_float("BL005_INFLUENCE_SHARE_THRESHOLD", float(defaults["influence_share_threshold"])),
        "profile_quality_penalty_increment": env_float(
            "BL005_PROFILE_QUALITY_PENALTY_INCREMENT",
            float(defaults["profile_quality_penalty_increment"]),
        ),
        "profile_entropy_penalty_increment": env_float(
            "BL005_PROFILE_ENTROPY_PENALTY_INCREMENT",
            float(defaults["profile_entropy_penalty_increment"]),
        ),
        "influence_share_penalty_increment": env_float(
            "BL005_INFLUENCE_SHARE_PENALTY_INCREMENT",
            float(defaults["influence_share_penalty_increment"]),
        ),
        "numeric_penalty_scale": env_float("BL005_NUMERIC_PENALTY_SCALE", float(defaults["numeric_penalty_scale"])),
        "semantic_overlap_damping_mid_entropy_threshold": env_float(
            "BL005_SEMANTIC_DAMPING_MID_THRESHOLD",
            float(defaults["semantic_overlap_damping_mid_entropy_threshold"]),
        ),
        "semantic_overlap_damping_low_entropy": env_float(
            "BL005_SEMANTIC_DAMPING_LOW_ENTROPY",
            float(defaults["semantic_overlap_damping_low_entropy"]),
        ),
        "semantic_overlap_damping_mid_entropy": env_float(
            "BL005_SEMANTIC_DAMPING_MID_ENTROPY",
            float(defaults["semantic_overlap_damping_mid_entropy"]),
        ),
        "enable_numeric_confidence_scaling": env_bool(
            "BL005_ENABLE_NUMERIC_CONFIDENCE_SCALING",
            bool(defaults["enable_numeric_confidence_scaling"]),
        ),
        "numeric_confidence_floor": env_float("BL005_NUMERIC_CONFIDENCE_FLOOR", float(defaults["numeric_confidence_floor"])),
        "profile_numeric_confidence_mode": env_str(
            "BL005_PROFILE_NUMERIC_CONFIDENCE_MODE",
            str(defaults["profile_numeric_confidence_mode"]),
        ),
        "profile_numeric_confidence_blend_weight": env_float(
            "BL005_PROFILE_NUMERIC_CONFIDENCE_BLEND_WEIGHT",
            float(defaults["profile_numeric_confidence_blend_weight"]),
        ),
        "numeric_support_score_mode": env_str("BL005_NUMERIC_SUPPORT_SCORE_MODE", str(defaults["numeric_support_score_mode"])),
        "emit_profile_policy_diagnostics": env_bool(
            "BL005_EMIT_PROFILE_POLICY_DIAGNOSTICS",
            bool(defaults["emit_profile_policy_diagnostics"]),
        ),
    }


def resolve_bl005_runtime_controls() -> dict[str, object]:
    """Resolve BL-005 controls from run config first, then environment defaults."""
    return resolve_stage_controls(
        load_from_env=_load_bl005_controls_from_env,
        sanitize=_sanitize_bl005_controls,
    )
