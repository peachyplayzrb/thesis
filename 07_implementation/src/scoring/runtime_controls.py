"""Runtime control helpers for BL-006 scoring."""

from __future__ import annotations

from shared_utils.constants import (
    DEFAULT_SCORING_CONTROLS,
    VALID_LEAD_GENRE_STRATEGIES,
    VALID_NUMERIC_CONFIDENCE_MODES,
    VALID_SEMANTIC_ALPHA_MODES,
    VALID_SEMANTIC_OVERLAP_STRATEGIES,
)
from shared_utils.env_utils import (
    coerce_dict,
    coerce_enum,
    coerce_float,
    env_bool,
    env_float,
    env_str,
)
from shared_utils.stage_runtime_resolver import (
    defaults_loader,
    load_positive_numeric_map_from_env,
    resolve_stage_controls,
)


def build_active_component_weights(
    active_numeric_components: set[str],
    component_weights: dict[str, float],
    numeric_components: set[str],
) -> tuple[dict[str, float], dict[str, object]]:
    """Filter and normalize active component weights."""
    active: dict[str, float] = {}
    for component, weight in component_weights.items():
        component_name = component.removesuffix("_score")
        if component_name in numeric_components and component_name not in active_numeric_components:
            continue
        active[component] = weight
    total = sum(active.values())
    if total <= 0:
        raise RuntimeError("BL-006 requires at least one active scoring component")

    normalized = {component: weight / total for component, weight in active.items()}
    rebalanced = abs(total - 1.0) > 1e-9
    diagnostics = {
        "rebalanced": rebalanced,
        "active_weight_sum_pre_normalization": round(total, 6),
        "active_component_count": len(active),
        "inactive_components": sorted(set(component_weights) - set(active)),
        "original_active_component_weights": {k: round(v, 6) for k, v in active.items()},
        "normalized_active_component_weights": {k: round(v, 6) for k, v in normalized.items()},
        "warning": (
            "BL-006 rebalanced active component weights to sum to 1.0"
            if rebalanced
            else None
        ),
    }
    return normalized, diagnostics


def _load_bl006_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "signal_mode": {},
        "component_weights": load_positive_numeric_map_from_env("BL006_COMPONENT_WEIGHTS_JSON"),
        "numeric_thresholds": load_positive_numeric_map_from_env("BL006_NUMERIC_THRESHOLDS_JSON"),
        "lead_genre_strategy": env_str("BL006_LEAD_GENRE_STRATEGY", "weighted_top_lead_genres"),
        "semantic_overlap_strategy": env_str("BL006_SEMANTIC_OVERLAP_STRATEGY", "precision_aware"),
        "semantic_precision_alpha_mode": env_str("BL006_SEMANTIC_PRECISION_ALPHA_MODE", "profile_adaptive"),
        "semantic_precision_alpha_fixed": env_float("BL006_SEMANTIC_PRECISION_ALPHA_FIXED", 0.35),
        "enable_numeric_confidence_scaling": env_bool("BL006_ENABLE_NUMERIC_CONFIDENCE_SCALING", True),
        "numeric_confidence_floor": env_float("BL006_NUMERIC_CONFIDENCE_FLOOR", 0.0),
        "profile_numeric_confidence_mode": env_str("BL006_PROFILE_NUMERIC_CONFIDENCE_MODE", "direct"),
        "profile_numeric_confidence_blend_weight": env_float(
            "BL006_PROFILE_NUMERIC_CONFIDENCE_BLEND_WEIGHT", 1.0
        ),
        "emit_confidence_impact_diagnostics": env_bool("BL006_EMIT_CONFIDENCE_IMPACT_DIAGNOSTICS", True),
        "emit_semantic_precision_diagnostics": env_bool("BL006_EMIT_SEMANTIC_PRECISION_DIAGNOSTICS", False),
        "apply_bl003_influence_tracks": env_bool("BL006_APPLY_BL003_INFLUENCE_TRACKS", False),
        "influence_track_bonus_scale": env_float("BL006_INFLUENCE_TRACK_BONUS_SCALE", 0.0),
    }


def _sanitize_bl006_controls(controls: dict[str, object]) -> dict[str, object]:
    cw = controls.get("component_weights")
    if not isinstance(cw, dict) or not cw:
        raise RuntimeError(
            "BL-006 component_weights must be supplied via orchestration payload "
            "or BL006_COMPONENT_WEIGHTS_JSON environment variable"
        )
    controls["component_weights"] = {
        str(k): float(v) for k, v in cw.items() if isinstance(v, (int, float))
    }
    controls["numeric_thresholds"] = coerce_dict(controls.get("numeric_thresholds"))
    controls["signal_mode"] = coerce_dict(controls.get("signal_mode"))

    controls["lead_genre_strategy"] = coerce_enum(
        controls.get("lead_genre_strategy"), VALID_LEAD_GENRE_STRATEGIES, "weighted_top_lead_genres"
    )
    controls["semantic_overlap_strategy"] = coerce_enum(
        controls.get("semantic_overlap_strategy"), VALID_SEMANTIC_OVERLAP_STRATEGIES, "precision_aware"
    )
    controls["semantic_precision_alpha_mode"] = coerce_enum(
        controls.get("semantic_precision_alpha_mode"), VALID_SEMANTIC_ALPHA_MODES, "profile_adaptive"
    )
    controls["semantic_precision_alpha_fixed"] = max(
        0.0, min(1.0, coerce_float(controls.get("semantic_precision_alpha_fixed"), 0.35))
    )
    controls["enable_numeric_confidence_scaling"] = bool(
        controls.get("enable_numeric_confidence_scaling", True)
    )
    controls["numeric_confidence_floor"] = max(
        0.0, coerce_float(controls.get("numeric_confidence_floor"), 0.0)
    )
    controls["profile_numeric_confidence_mode"] = coerce_enum(
        controls.get("profile_numeric_confidence_mode"), VALID_NUMERIC_CONFIDENCE_MODES, "direct"
    )
    controls["profile_numeric_confidence_blend_weight"] = max(
        0.0, min(1.0, coerce_float(controls.get("profile_numeric_confidence_blend_weight"), 1.0))
    )
    controls["emit_confidence_impact_diagnostics"] = bool(
        controls.get("emit_confidence_impact_diagnostics", True)
    )
    controls["emit_semantic_precision_diagnostics"] = bool(
        controls.get("emit_semantic_precision_diagnostics", False)
    )
    controls["apply_bl003_influence_tracks"] = bool(
        controls.get("apply_bl003_influence_tracks", False)
    )
    controls["influence_track_bonus_scale"] = max(
        0.0, coerce_float(controls.get("influence_track_bonus_scale"), 0.0)
    )
    return controls


def resolve_bl006_runtime_controls() -> dict[str, object]:
    """Resolve runtime controls with payload-first precedence."""
    return resolve_stage_controls(
        load_from_env=_load_bl006_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_SCORING_CONTROLS),
        sanitize=_sanitize_bl006_controls,
    )
