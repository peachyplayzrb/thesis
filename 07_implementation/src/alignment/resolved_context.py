"""Unified BL-003 runtime context resolution."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from alignment.constants import DEFAULT_INFLUENCE_PREFERENCE_WEIGHT
from alignment.models import AlignmentBehaviorControls, AlignmentStructuralContract
from shared_utils.constants import (
    DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
    DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
    DEFAULT_SEED_CONTROLS,
    DEFAULT_SOURCE_BASE_WEIGHTS,
    DEFAULT_TOP_RANGE_WEIGHTS,
)

from alignment.runtime_scope import resolve_bl003_runtime_scope


@dataclass(frozen=True)
class AlignmentResolvedContext:
    """Resolved control surface used by BL-003 matching and influence stages."""

    runtime_scope: dict[str, object]
    behavior_controls: AlignmentBehaviorControls
    structural_contract: AlignmentStructuralContract


DEFAULT_INFLUENCE_CONTROLS: dict[str, Any] = {
    "influence_enabled": False,
    "influence_track_ids": [],
    "influence_preference_weight": DEFAULT_INFLUENCE_PREFERENCE_WEIGHT,
}


def _load_stage_config_payload() -> dict[str, Any] | None:
    """Try to load orchestration-injected BL_STAGE_CONFIG_JSON payload (Phase 2 handoff).

    Returns:
        dict with keys like 'seed_controls', 'weighting_policy', 'influence_controls', etc., or None.
    """
    payload_json = os.environ.get("BL_STAGE_CONFIG_JSON", "").strip()
    if not payload_json:
        return None
    try:
        payload = json.loads(payload_json)
        if isinstance(payload, dict):
            stage_controls = payload.get("controls")
            if isinstance(stage_controls, dict):
                controls = dict(stage_controls)
                if "schema_version" in payload and "run_config_schema_version" not in controls:
                    controls["run_config_schema_version"] = payload.get("schema_version")
                return controls
            return payload
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def resolve_alignment_context() -> AlignmentResolvedContext:
    """Resolve BL-003 controls from orchestration payload, env, then defaults.

    Priority (Phase 3+):
    1. BL_STAGE_CONFIG_JSON (orchestration-injected, Phase 2 handoff)
    2. env defaults (BL003_*, etc.)
    """
    # Phase 2 payload-first approach: try orchestration handoff first
    stage_payload = _load_stage_config_payload()
    if stage_payload:
        return _resolve_from_orchestration_payload(stage_payload)

    # Phase 1/2 fallback: use legacy resolution (env/run_config/defaults)
    return _resolve_from_legacy_sources()


def _resolve_from_orchestration_payload(payload: dict[str, Any]) -> AlignmentResolvedContext:
    """Resolve alignment context from orchestration-injected payload (Phase 2 handoff).

    Payload structure from config_resolver.resolve_stage_control_payload(BL-003):
    {
        'input_scope_controls': {...},
        'seed_controls': {...},
        'weighting_policy': {...},
        'influence_controls': {...},
    }
    """
    # Use the orchestration-resolved controls directly
    input_scope_controls = dict(payload.get("input_scope_controls") or {})
    seed_controls = dict(payload.get("seed_controls") or {})
    weighting_policy = payload.get("weighting_policy")
    influence_controls = dict(payload.get("influence_controls") or DEFAULT_INFLUENCE_CONTROLS)

    # Extract seed control fields
    top_range_weights = dict(seed_controls.get("top_range_weights", DEFAULT_TOP_RANGE_WEIGHTS))
    source_base_weights = dict(seed_controls.get("source_base_weights", DEFAULT_SOURCE_BASE_WEIGHTS))
    fuzzy_matching_controls = dict(
        seed_controls.get("fuzzy_matching") or DEFAULT_SEED_CONTROLS.get("fuzzy_matching") or {}
    )
    match_strategy = dict(
        seed_controls.get("match_strategy") or DEFAULT_SEED_CONTROLS.get("match_strategy") or {}
    )
    match_strategy_order = list(
        seed_controls.get("match_strategy_order") or DEFAULT_SEED_CONTROLS.get("match_strategy_order") or []
    )
    temporal_controls = dict(
        seed_controls.get("temporal_controls") or DEFAULT_SEED_CONTROLS.get("temporal_controls") or {}
    )
    aggregation_policy = dict(
        seed_controls.get("aggregation_policy") or DEFAULT_SEED_CONTROLS.get("aggregation_policy") or {}
    )
    match_rate_min_threshold = float(seed_controls.get("match_rate_min_threshold", 0.0))

    # Decay half-lives
    seed_decay_half_lives = dict(seed_controls.get("decay_half_lives") or {})
    decay_half_lives = {
        "recently_played": float(
            seed_decay_half_lives.get(
                "recently_played",
                DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
            )
        ),
        "saved_tracks": float(
            seed_decay_half_lives.get(
                "saved_tracks",
                DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
            )
        ),
    }

    # Build runtime_scope from payload (no file path needed; orchestration resolved already)
    runtime_scope = {
        "config_source": "orchestration_payload",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope": input_scope_controls,
    }

    return AlignmentResolvedContext(
        runtime_scope=runtime_scope,
        behavior_controls=AlignmentBehaviorControls(
            input_scope=dict(input_scope_controls),
            top_range_weights=dict(top_range_weights),
            source_base_weights=dict(source_base_weights),
            decay_half_lives=dict(decay_half_lives),
            match_rate_min_threshold=float(match_rate_min_threshold),
            fuzzy_matching_controls=dict(fuzzy_matching_controls),
            match_strategy={k: bool(v) for k, v in match_strategy.items()},
            match_strategy_order=list(match_strategy_order),
            temporal_controls=dict(temporal_controls),
            aggregation_policy=dict(aggregation_policy),
            weighting_policy=(dict(weighting_policy) if weighting_policy is not None else None),
            influence_controls=dict(influence_controls),
        ),
        structural_contract=AlignmentStructuralContract.from_defaults(),
    )


def _resolve_from_legacy_sources() -> AlignmentResolvedContext:
    """Resolve alignment context from env/defaults when payload is unavailable."""
    runtime_scope = resolve_bl003_runtime_scope()
    input_scope = dict(runtime_scope["input_scope"])

    top_range_weights: dict[str, float] = dict(DEFAULT_TOP_RANGE_WEIGHTS)
    source_base_weights: dict[str, float] = dict(DEFAULT_SOURCE_BASE_WEIGHTS)
    decay_half_lives: dict[str, float] = {
        "recently_played": DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
        "saved_tracks": DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
    }
    match_rate_min_threshold = 0.0
    fuzzy_matching_controls: dict[str, Any] = dict(
        DEFAULT_SEED_CONTROLS.get("fuzzy_matching") or {}
    )
    match_strategy: dict[str, bool] = dict(DEFAULT_SEED_CONTROLS.get("match_strategy") or {})
    match_strategy_order: list[str] = list(DEFAULT_SEED_CONTROLS.get("match_strategy_order") or [])
    temporal_controls: dict[str, Any] = dict(DEFAULT_SEED_CONTROLS.get("temporal_controls") or {})
    aggregation_policy: dict[str, Any] = dict(DEFAULT_SEED_CONTROLS.get("aggregation_policy") or {})
    weighting_policy: dict[str, Any] | None = None
    influence_controls: dict[str, Any] = dict(DEFAULT_INFLUENCE_CONTROLS)

    return AlignmentResolvedContext(
        runtime_scope=dict(runtime_scope),
        behavior_controls=AlignmentBehaviorControls(
            input_scope=dict(input_scope),
            top_range_weights=dict(top_range_weights),
            source_base_weights=dict(source_base_weights),
            decay_half_lives=dict(decay_half_lives),
            match_rate_min_threshold=float(match_rate_min_threshold),
            fuzzy_matching_controls=dict(fuzzy_matching_controls),
            match_strategy={k: bool(v) for k, v in match_strategy.items()},
            match_strategy_order=list(match_strategy_order),
            temporal_controls=dict(temporal_controls),
            aggregation_policy=dict(aggregation_policy),
            weighting_policy=(dict(weighting_policy) if weighting_policy is not None else None),
            influence_controls=dict(influence_controls),
        ),
        structural_contract=AlignmentStructuralContract.from_defaults(),
    )
