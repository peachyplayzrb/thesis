"""Runtime control helpers for BL-006 scoring."""

from __future__ import annotations

import json
import os

from shared_utils.config_loader import load_run_config_utils_module
from shared_utils.stage_runtime_resolver import (
    load_positive_numeric_map_from_env,
    resolve_run_config_path,
)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    token = str(raw).strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(str(raw).strip())
    except ValueError:
        return default


def _env_str(name: str, default: str) -> str:
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = str(raw).strip()
    return value if value else default


def load_component_weight_overrides(defaults: dict[str, float]) -> dict[str, float]:
    """Load component weight overrides from environment."""
    raw = os.environ.get("BL006_COMPONENT_WEIGHTS_JSON", "").strip()
    if not raw:
        return dict(defaults)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return dict(defaults)
    if not isinstance(payload, dict):
        return dict(defaults)

    merged = dict(defaults)
    for key, value in payload.items():
        if key in merged and isinstance(value, (int, float)) and value >= 0:
            merged[key] = float(value)
    return merged


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


def _load_bl006_numeric_thresholds_from_env() -> dict[str, float]:
    """Load numeric threshold overrides from environment."""
    return load_positive_numeric_map_from_env("BL006_NUMERIC_THRESHOLDS_JSON")


def resolve_bl006_runtime_controls(default_weights: dict[str, float]) -> dict[str, object]:
    """Resolve runtime controls from run-config or environment."""
    run_config_path = resolve_run_config_path()
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl006_controls(run_config_path)
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "signal_mode": dict(controls.get("signal_mode") or {}),
            "component_weights": dict(controls.get("component_weights") or default_weights),
            "numeric_thresholds": dict(controls.get("numeric_thresholds") or {}),
            "lead_genre_strategy": str(controls.get("lead_genre_strategy") or "weighted_top_lead_genres"),
            "semantic_overlap_strategy": str(controls.get("semantic_overlap_strategy") or "precision_aware"),
            "semantic_precision_alpha_mode": str(controls.get("semantic_precision_alpha_mode") or "profile_adaptive"),
            "semantic_precision_alpha_fixed": float(controls.get("semantic_precision_alpha_fixed", 0.35)),
            "enable_numeric_confidence_scaling": bool(controls.get("enable_numeric_confidence_scaling", True)),
            "numeric_confidence_floor": float(controls.get("numeric_confidence_floor", 0.0)),
            "profile_numeric_confidence_mode": str(controls.get("profile_numeric_confidence_mode") or "direct"),
            "profile_numeric_confidence_blend_weight": float(
                controls.get("profile_numeric_confidence_blend_weight", 1.0)
            ),
            "emit_confidence_impact_diagnostics": bool(controls.get("emit_confidence_impact_diagnostics", True)),
            "emit_semantic_precision_diagnostics": bool(controls.get("emit_semantic_precision_diagnostics", False)),
        }
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "signal_mode": {},
        "component_weights": load_component_weight_overrides(default_weights),
        "numeric_thresholds": _load_bl006_numeric_thresholds_from_env(),
        "lead_genre_strategy": _env_str("BL006_LEAD_GENRE_STRATEGY", "weighted_top_lead_genres"),
        "semantic_overlap_strategy": _env_str("BL006_SEMANTIC_OVERLAP_STRATEGY", "precision_aware"),
        "semantic_precision_alpha_mode": _env_str("BL006_SEMANTIC_PRECISION_ALPHA_MODE", "profile_adaptive"),
        "semantic_precision_alpha_fixed": _env_float("BL006_SEMANTIC_PRECISION_ALPHA_FIXED", 0.35),
        "enable_numeric_confidence_scaling": _env_bool("BL006_ENABLE_NUMERIC_CONFIDENCE_SCALING", True),
        "numeric_confidence_floor": _env_float("BL006_NUMERIC_CONFIDENCE_FLOOR", 0.0),
        "profile_numeric_confidence_mode": _env_str("BL006_PROFILE_NUMERIC_CONFIDENCE_MODE", "direct"),
        "profile_numeric_confidence_blend_weight": _env_float(
            "BL006_PROFILE_NUMERIC_CONFIDENCE_BLEND_WEIGHT",
            1.0,
        ),
        "emit_confidence_impact_diagnostics": _env_bool("BL006_EMIT_CONFIDENCE_IMPACT_DIAGNOSTICS", True),
        "emit_semantic_precision_diagnostics": _env_bool("BL006_EMIT_SEMANTIC_PRECISION_DIAGNOSTICS", False),
    }
