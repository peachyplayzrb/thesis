"""Runtime control helpers for BL-006 scoring."""

from __future__ import annotations

from shared_utils.constants import (
    DEFAULT_BL006_HANDSHAKE_VALIDATION_POLICY,
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
from shared_utils.runtime_control_utils import (
    apply_normalization_diagnostics,
    apply_payload_resolution_diagnostics,
    inspect_stage_payload_resolution,
    record_normalization_event,
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
    defaults = DEFAULT_SCORING_CONTROLS
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
        "enable_scoring_sensitivity_diagnostics": env_bool(
            "BL006_ENABLE_SCORING_SENSITIVITY_DIAGNOSTICS",
            bool(defaults["enable_scoring_sensitivity_diagnostics"]),
        ),
        "scoring_sensitivity_top_k": env_float(
            "BL006_SCORING_SENSITIVITY_TOP_K",
            coerce_float(defaults.get("scoring_sensitivity_top_k"), 10.0),
        ),
        "scoring_sensitivity_perturbation_pct": env_float(
            "BL006_SCORING_SENSITIVITY_PERTURBATION_PCT",
            coerce_float(defaults.get("scoring_sensitivity_perturbation_pct"), 0.10),
        ),
        "scoring_sensitivity_max_components": env_float(
            "BL006_SCORING_SENSITIVITY_MAX_COMPONENTS",
            coerce_float(defaults.get("scoring_sensitivity_max_components"), 5.0),
        ),
        "apply_bl003_influence_tracks": env_bool("BL006_APPLY_BL003_INFLUENCE_TRACKS", False),
        "influence_track_bonus_scale": env_float("BL006_INFLUENCE_TRACK_BONUS_SCALE", 0.0),
        "bl005_bl006_handshake_validation_policy": env_str(
            "BL006_HANDSHAKE_VALIDATION_POLICY",
            str(defaults["bl005_bl006_handshake_validation_policy"]),
        ),
    }


def _sanitize_bl006_controls(controls: dict[str, object]) -> dict[str, object]:
    normalization_events: list[dict[str, object]] = []
    normalization_event_counts_by_field: dict[str, int] = {}

    cw = controls.get("component_weights")
    if not isinstance(cw, dict) or not cw:
        raise RuntimeError(
            "BL-006 component_weights must be supplied via orchestration payload "
            "or BL006_COMPONENT_WEIGHTS_JSON environment variable"
        )
    controls["component_weights"] = {
        str(k): float(v) for k, v in cw.items() if isinstance(v, int | float)
    }

    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="component_weights",
        raw_value=cw,
        normalized_value=controls["component_weights"],
        reason="kept_numeric_component_weights_only",
    )

    raw_numeric_thresholds = controls.get("numeric_thresholds")
    controls["numeric_thresholds"] = coerce_dict(controls.get("numeric_thresholds"))
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="numeric_thresholds",
        raw_value=raw_numeric_thresholds,
        normalized_value=controls["numeric_thresholds"],
        reason="normalized_to_object",
    )

    raw_signal_mode = controls.get("signal_mode")
    controls["signal_mode"] = coerce_dict(controls.get("signal_mode"))
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="signal_mode",
        raw_value=raw_signal_mode,
        normalized_value=controls["signal_mode"],
        reason="normalized_to_object",
    )

    raw_lead_genre_strategy = controls.get("lead_genre_strategy")
    controls["lead_genre_strategy"] = coerce_enum(
        controls.get("lead_genre_strategy"), VALID_LEAD_GENRE_STRATEGIES, "weighted_top_lead_genres"
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="lead_genre_strategy",
        raw_value=raw_lead_genre_strategy,
        normalized_value=controls["lead_genre_strategy"],
        reason="normalized_to_supported_enum",
    )

    raw_semantic_overlap_strategy = controls.get("semantic_overlap_strategy")
    controls["semantic_overlap_strategy"] = coerce_enum(
        controls.get("semantic_overlap_strategy"), VALID_SEMANTIC_OVERLAP_STRATEGIES, "precision_aware"
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="semantic_overlap_strategy",
        raw_value=raw_semantic_overlap_strategy,
        normalized_value=controls["semantic_overlap_strategy"],
        reason="normalized_to_supported_enum",
    )

    raw_alpha_mode = controls.get("semantic_precision_alpha_mode")
    controls["semantic_precision_alpha_mode"] = coerce_enum(
        controls.get("semantic_precision_alpha_mode"), VALID_SEMANTIC_ALPHA_MODES, "profile_adaptive"
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="semantic_precision_alpha_mode",
        raw_value=raw_alpha_mode,
        normalized_value=controls["semantic_precision_alpha_mode"],
        reason="normalized_to_supported_enum",
    )

    raw_alpha_fixed = controls.get("semantic_precision_alpha_fixed")
    controls["semantic_precision_alpha_fixed"] = max(
        0.0, min(1.0, coerce_float(controls.get("semantic_precision_alpha_fixed"), 0.35))
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="semantic_precision_alpha_fixed",
        raw_value=raw_alpha_fixed,
        normalized_value=controls["semantic_precision_alpha_fixed"],
        reason="coerced_and_clamped_to_range_0_1",
    )

    controls["enable_numeric_confidence_scaling"] = bool(
        controls.get("enable_numeric_confidence_scaling", True)
    )

    raw_numeric_floor = controls.get("numeric_confidence_floor")
    controls["numeric_confidence_floor"] = max(
        0.0, coerce_float(controls.get("numeric_confidence_floor"), 0.0)
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="numeric_confidence_floor",
        raw_value=raw_numeric_floor,
        normalized_value=controls["numeric_confidence_floor"],
        reason="coerced_to_non_negative_float",
    )

    raw_profile_numeric_mode = controls.get("profile_numeric_confidence_mode")
    controls["profile_numeric_confidence_mode"] = coerce_enum(
        controls.get("profile_numeric_confidence_mode"), VALID_NUMERIC_CONFIDENCE_MODES, "direct"
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="profile_numeric_confidence_mode",
        raw_value=raw_profile_numeric_mode,
        normalized_value=controls["profile_numeric_confidence_mode"],
        reason="normalized_to_supported_enum",
    )

    raw_profile_numeric_blend = controls.get("profile_numeric_confidence_blend_weight")
    controls["profile_numeric_confidence_blend_weight"] = max(
        0.0, min(1.0, coerce_float(controls.get("profile_numeric_confidence_blend_weight"), 1.0))
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="profile_numeric_confidence_blend_weight",
        raw_value=raw_profile_numeric_blend,
        normalized_value=controls["profile_numeric_confidence_blend_weight"],
        reason="coerced_and_clamped_to_range_0_1",
    )

    controls["emit_confidence_impact_diagnostics"] = bool(
        controls.get("emit_confidence_impact_diagnostics", True)
    )
    controls["emit_semantic_precision_diagnostics"] = bool(
        controls.get("emit_semantic_precision_diagnostics", False)
    )

    controls["enable_scoring_sensitivity_diagnostics"] = bool(
        controls.get("enable_scoring_sensitivity_diagnostics", False)
    )

    raw_sensitivity_top_k = controls.get("scoring_sensitivity_top_k")
    controls["scoring_sensitivity_top_k"] = max(
        1,
        min(100, int(coerce_float(controls.get("scoring_sensitivity_top_k"), 10.0))),
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="scoring_sensitivity_top_k",
        raw_value=raw_sensitivity_top_k,
        normalized_value=controls["scoring_sensitivity_top_k"],
        reason="coerced_to_int_and_clamped_to_range_1_100",
    )

    raw_sensitivity_perturbation = controls.get("scoring_sensitivity_perturbation_pct")
    controls["scoring_sensitivity_perturbation_pct"] = max(
        0.0,
        min(0.5, coerce_float(controls.get("scoring_sensitivity_perturbation_pct"), 0.10)),
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="scoring_sensitivity_perturbation_pct",
        raw_value=raw_sensitivity_perturbation,
        normalized_value=controls["scoring_sensitivity_perturbation_pct"],
        reason="coerced_and_clamped_to_range_0_0.5",
    )

    raw_sensitivity_max_components = controls.get("scoring_sensitivity_max_components")
    controls["scoring_sensitivity_max_components"] = max(
        1,
        min(11, int(coerce_float(controls.get("scoring_sensitivity_max_components"), 5.0))),
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="scoring_sensitivity_max_components",
        raw_value=raw_sensitivity_max_components,
        normalized_value=controls["scoring_sensitivity_max_components"],
        reason="coerced_to_int_and_clamped_to_range_1_11",
    )

    controls["apply_bl003_influence_tracks"] = bool(
        controls.get("apply_bl003_influence_tracks", False)
    )

    raw_influence_scale = controls.get("influence_track_bonus_scale")
    controls["influence_track_bonus_scale"] = max(
        0.0, coerce_float(controls.get("influence_track_bonus_scale"), 0.0)
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="influence_track_bonus_scale",
        raw_value=raw_influence_scale,
        normalized_value=controls["influence_track_bonus_scale"],
        reason="coerced_to_non_negative_float",
    )

    raw_handshake_policy = controls.get(
        "bl005_bl006_handshake_validation_policy",
        DEFAULT_BL006_HANDSHAKE_VALIDATION_POLICY,
    )
    controls["bl005_bl006_handshake_validation_policy"] = coerce_enum(
        raw_handshake_policy,
        frozenset({"allow", "warn", "strict"}),
        DEFAULT_BL006_HANDSHAKE_VALIDATION_POLICY,
    )
    record_normalization_event(
        normalization_events,
        normalization_event_counts_by_field,
        field="bl005_bl006_handshake_validation_policy",
        raw_value=raw_handshake_policy,
        normalized_value=controls["bl005_bl006_handshake_validation_policy"],
        reason="normalized_to_supported_enum",
    )

    return apply_normalization_diagnostics(
        controls,
        normalization_events=normalization_events,
        normalization_event_counts_by_field=normalization_event_counts_by_field,
    )


def resolve_bl006_runtime_controls() -> dict[str, object]:
    """Resolve runtime controls with payload-first precedence."""
    payload_status = inspect_stage_payload_resolution()

    controls = resolve_stage_controls(
        load_from_env=_load_bl006_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_SCORING_CONTROLS),
        sanitize=_sanitize_bl006_controls,
    )
    return apply_payload_resolution_diagnostics(
        controls,
        stage_label="BL-006",
        payload_status=payload_status,
    )
