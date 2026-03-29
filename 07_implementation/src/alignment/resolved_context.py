"""Unified BL-003 runtime context resolution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from alignment.constants import DEFAULT_INFLUENCE_PREFERENCE_WEIGHT
from alignment.models import AlignmentBehaviorControls, AlignmentStructuralContract
from shared_utils.config_loader import load_run_config_utils_module
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


def resolve_alignment_context() -> AlignmentResolvedContext:
    """Resolve BL-003 controls from env/run-config/defaults once per run."""
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

    run_config_path = runtime_scope.get("run_config_path")
    if runtime_scope.get("config_source") == "run_config" and run_config_path:
        rc_utils = load_run_config_utils_module()
        seed_controls = rc_utils.resolve_bl003_seed_controls(run_config_path)
        top_range_weights = dict(
            seed_controls.get("top_range_weights", DEFAULT_TOP_RANGE_WEIGHTS)
        )
        source_base_weights = dict(
            seed_controls.get("source_base_weights", DEFAULT_SOURCE_BASE_WEIGHTS)
        )
        fuzzy_matching_controls = dict(
            seed_controls.get("fuzzy_matching")
            or DEFAULT_SEED_CONTROLS.get("fuzzy_matching")
            or {}
        )
        match_strategy = dict(
            seed_controls.get("match_strategy")
            or DEFAULT_SEED_CONTROLS.get("match_strategy")
            or {}
        )
        match_strategy_order = list(
            seed_controls.get("match_strategy_order")
            or DEFAULT_SEED_CONTROLS.get("match_strategy_order")
            or []
        )
        temporal_controls = dict(
            seed_controls.get("temporal_controls")
            or DEFAULT_SEED_CONTROLS.get("temporal_controls")
            or {}
        )
        aggregation_policy = dict(
            seed_controls.get("aggregation_policy")
            or DEFAULT_SEED_CONTROLS.get("aggregation_policy")
            or {}
        )
        seed_decay_half_lives = dict(seed_controls.get("decay_half_lives") or {})
        decay_half_lives.update(
            {
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
        )
        match_rate_min_threshold = float(
            seed_controls.get("match_rate_min_threshold", 0.0)
        )
        weighting_policy = rc_utils.resolve_bl003_weighting_policy(run_config_path)
        influence_controls = rc_utils.resolve_bl003_influence_controls(run_config_path)

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
