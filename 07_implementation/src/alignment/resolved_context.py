"""Unified BL-003 runtime context resolution."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
    input_scope: dict[str, object]
    top_range_weights: dict[str, float]
    source_base_weights: dict[str, float]
    decay_half_lives: dict[str, float]
    match_rate_min_threshold: float
    fuzzy_matching_controls: dict[str, Any]
    weighting_policy: dict[str, Any] | None
    influence_controls: dict[str, Any]


DEFAULT_INFLUENCE_CONTROLS: dict[str, Any] = {
    "influence_enabled": False,
    "influence_track_ids": [],
    "influence_preference_weight": 1.0,
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
        runtime_scope=runtime_scope,
        input_scope=input_scope,
        top_range_weights=top_range_weights,
        source_base_weights=source_base_weights,
        decay_half_lives=decay_half_lives,
        match_rate_min_threshold=match_rate_min_threshold,
        fuzzy_matching_controls=fuzzy_matching_controls,
        weighting_policy=weighting_policy,
        influence_controls=influence_controls,
    )
