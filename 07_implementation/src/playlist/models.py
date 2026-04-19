from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PlaylistPaths:
    scored_candidates_path: Path
    output_dir: Path


@dataclass(frozen=True)
class PlaylistControls:
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    target_size: int
    min_score_threshold: float
    max_per_genre: int
    max_consecutive: int
    utility_strategy: str
    utility_decay_factor: float
    utility_weights: dict[str, float]
    adaptive_limits: dict[str, object]
    controlled_relaxation: dict[str, object]
    lead_genre_fallback_strategy: str
    use_component_contributions_for_tiebreak: bool
    use_semantic_strength_for_tiebreak: bool
    emit_opportunity_cost_metrics: bool
    opportunity_cost_top_k_examples: int
    detail_log_top_k: int
    influence_enabled: bool
    influence_track_ids: list[str]
    influence_policy_mode: str
    influence_reserved_slots: int
    influence_allow_genre_cap_override: bool
    influence_allow_consecutive_override: bool
    influence_allow_score_threshold_override: bool
    bl006_bl007_handshake_validation_policy: str = "warn"
    transition_smoothness_weight: float = 0.0

    def as_mapping(self) -> dict[str, object]:
        return {
            "config_source": self.config_source,
            "run_config_path": self.run_config_path,
            "run_config_schema_version": self.run_config_schema_version,
            "target_size": self.target_size,
            "min_score_threshold": self.min_score_threshold,
            "max_per_genre": self.max_per_genre,
            "max_consecutive": self.max_consecutive,
            "utility_strategy": self.utility_strategy,
            "utility_decay_factor": self.utility_decay_factor,
            "utility_weights": dict(self.utility_weights),
            "adaptive_limits": dict(self.adaptive_limits),
            "controlled_relaxation": dict(self.controlled_relaxation),
            "lead_genre_fallback_strategy": self.lead_genre_fallback_strategy,
            "use_component_contributions_for_tiebreak": self.use_component_contributions_for_tiebreak,
            "use_semantic_strength_for_tiebreak": self.use_semantic_strength_for_tiebreak,
            "emit_opportunity_cost_metrics": self.emit_opportunity_cost_metrics,
            "opportunity_cost_top_k_examples": self.opportunity_cost_top_k_examples,
            "detail_log_top_k": self.detail_log_top_k,
            "influence_enabled": self.influence_enabled,
            "influence_track_ids": list(self.influence_track_ids),
            "influence_policy_mode": self.influence_policy_mode,
            "influence_reserved_slots": self.influence_reserved_slots,
            "influence_allow_genre_cap_override": self.influence_allow_genre_cap_override,
            "influence_allow_consecutive_override": self.influence_allow_consecutive_override,
            "influence_allow_score_threshold_override": self.influence_allow_score_threshold_override,
            "bl006_bl007_handshake_validation_policy": self.bl006_bl007_handshake_validation_policy,
            "transition_smoothness_weight": self.transition_smoothness_weight,
        }


@dataclass(frozen=True)
class PlaylistInputs:
    candidates: list[dict[str, str]]


@dataclass(frozen=True)
class PlaylistContext:
    target_size: int
    min_score_threshold: float
    max_per_genre: int
    max_consecutive: int
    utility_strategy: str
    utility_decay_factor: float
    utility_weights: dict[str, float]
    adaptive_limits: dict[str, object]
    controlled_relaxation: dict[str, object]
    lead_genre_fallback_strategy: str
    use_component_contributions_for_tiebreak: bool
    use_semantic_strength_for_tiebreak: bool
    emit_opportunity_cost_metrics: bool
    opportunity_cost_top_k_examples: int
    detail_log_top_k: int
    influence_enabled: bool
    influence_track_ids: set[str]
    influence_policy_mode: str
    influence_reserved_slots: int
    influence_allow_genre_cap_override: bool
    influence_allow_consecutive_override: bool
    influence_allow_score_threshold_override: bool
    transition_smoothness_weight: float = 0.0


@dataclass(frozen=True)
class PlaylistAggregation:
    playlist: list[dict[str, object]]
    trace_rows: list[dict[str, object]]
    rule_hits: dict[str, int]


@dataclass(frozen=True)
class PlaylistArtifacts:
    playlist_path: Path
    trace_path: Path
    report_path: Path
    detail_log_path: Path
    run_id: str
    target_size: int
    playlist_size: int
    genre_mix: dict[str, int]
    undersized_diagnostics: dict[str, object]


def controls_from_mapping(payload: Mapping[str, Any]) -> PlaylistControls:
    return PlaylistControls(
        config_source=str(payload.get("config_source") or "environment"),
        run_config_path=(str(payload["run_config_path"]) if payload.get("run_config_path") else None),
        run_config_schema_version=(
            str(payload["run_config_schema_version"])
            if payload.get("run_config_schema_version")
            else None
        ),
        target_size=int(payload.get("target_size", 10)),
        min_score_threshold=float(payload.get("min_score_threshold", 0.35)),
        max_per_genre=int(payload.get("max_per_genre", 4)),
        max_consecutive=int(payload.get("max_consecutive", 2)),
        utility_strategy=str(payload.get("utility_strategy", "rank_round_robin")),
        utility_decay_factor=float(payload.get("utility_decay_factor", 0.0)),
        utility_weights={
            str(k): float(v)
            for k, v in dict(payload.get("utility_weights") or {}).items()
        },
        adaptive_limits={str(k): v for k, v in dict(payload.get("adaptive_limits") or {}).items()},
        controlled_relaxation={str(k): v for k, v in dict(payload.get("controlled_relaxation") or {}).items()},
        lead_genre_fallback_strategy=str(payload.get("lead_genre_fallback_strategy", "none")),
        use_component_contributions_for_tiebreak=bool(payload.get("use_component_contributions_for_tiebreak", False)),
        use_semantic_strength_for_tiebreak=bool(payload.get("use_semantic_strength_for_tiebreak", False)),
        emit_opportunity_cost_metrics=bool(payload.get("emit_opportunity_cost_metrics", False)),
        opportunity_cost_top_k_examples=int(payload.get("opportunity_cost_top_k_examples", 10)),
        detail_log_top_k=int(payload.get("detail_log_top_k", 100)),
        influence_enabled=bool(payload.get("influence_enabled", False)),
        influence_track_ids=[str(v) for v in list(payload.get("influence_track_ids") or []) if str(v).strip()],
        influence_policy_mode=str(payload.get("influence_policy_mode", "competitive")),
        influence_reserved_slots=int(payload.get("influence_reserved_slots", 0)),
        influence_allow_genre_cap_override=bool(payload.get("influence_allow_genre_cap_override", False)),
        influence_allow_consecutive_override=bool(payload.get("influence_allow_consecutive_override", False)),
        influence_allow_score_threshold_override=bool(payload.get("influence_allow_score_threshold_override", False)),
        bl006_bl007_handshake_validation_policy=str(payload.get("bl006_bl007_handshake_validation_policy", "warn")),
        transition_smoothness_weight=float(payload.get("transition_smoothness_weight", 0.0)),
    )


def context_from_mapping(payload: Mapping[str, Any]) -> PlaylistContext:
    utility_weights_raw = payload.get("utility_weights")
    adaptive_limits_raw = payload.get("adaptive_limits")
    controlled_relaxation_raw = payload.get("controlled_relaxation")
    return PlaylistContext(
        target_size=int(payload.get("target_size", 10)),
        min_score_threshold=float(payload.get("min_score_threshold", 0.35)),
        max_per_genre=int(payload.get("max_per_genre", 4)),
        max_consecutive=int(payload.get("max_consecutive", 2)),
        utility_strategy=str(payload.get("utility_strategy", "rank_round_robin")),
        utility_decay_factor=float(payload.get("utility_decay_factor", 0.0)),
        utility_weights={
            str(k): float(v)
            for k, v in dict(utility_weights_raw or {}).items()
        } if isinstance(utility_weights_raw, Mapping) else {
            "score_weight": 1.0,
            "novelty_weight": 0.0,
            "repetition_penalty_weight": 0.0,
        },
        adaptive_limits={
            str(k): v
            for k, v in dict(adaptive_limits_raw or {}).items()
        } if isinstance(adaptive_limits_raw, Mapping) else {},
        controlled_relaxation={
            str(k): v
            for k, v in dict(controlled_relaxation_raw or {}).items()
        } if isinstance(controlled_relaxation_raw, Mapping) else {},
        lead_genre_fallback_strategy=str(payload.get("lead_genre_fallback_strategy", "none")),
        use_component_contributions_for_tiebreak=bool(payload.get("use_component_contributions_for_tiebreak", False)),
        use_semantic_strength_for_tiebreak=bool(payload.get("use_semantic_strength_for_tiebreak", False)),
        emit_opportunity_cost_metrics=bool(payload.get("emit_opportunity_cost_metrics", False)),
        opportunity_cost_top_k_examples=int(payload.get("opportunity_cost_top_k_examples", 10)),
        detail_log_top_k=int(payload.get("detail_log_top_k", 100)),
        influence_enabled=bool(payload.get("influence_enabled", False)),
        influence_track_ids={str(v) for v in list(payload.get("influence_track_ids") or []) if str(v).strip()},
        influence_policy_mode=str(payload.get("influence_policy_mode", "competitive")),
        influence_reserved_slots=int(payload.get("influence_reserved_slots", 0)),
        influence_allow_genre_cap_override=bool(payload.get("influence_allow_genre_cap_override", False)),
        influence_allow_consecutive_override=bool(payload.get("influence_allow_consecutive_override", False)),
        influence_allow_score_threshold_override=bool(payload.get("influence_allow_score_threshold_override", False)),
        transition_smoothness_weight=float(payload.get("transition_smoothness_weight", 0.0)),
    )


def context_as_mapping(context: PlaylistContext) -> dict[str, object]:
    return {
        "target_size": context.target_size,
        "min_score_threshold": context.min_score_threshold,
        "max_per_genre": context.max_per_genre,
        "max_consecutive": context.max_consecutive,
        "utility_strategy": context.utility_strategy,
        "utility_decay_factor": context.utility_decay_factor,
        "utility_weights": dict(context.utility_weights),
        "adaptive_limits": dict(context.adaptive_limits),
        "controlled_relaxation": dict(context.controlled_relaxation),
        "lead_genre_fallback_strategy": context.lead_genre_fallback_strategy,
        "use_component_contributions_for_tiebreak": context.use_component_contributions_for_tiebreak,
        "use_semantic_strength_for_tiebreak": context.use_semantic_strength_for_tiebreak,
        "emit_opportunity_cost_metrics": context.emit_opportunity_cost_metrics,
        "opportunity_cost_top_k_examples": context.opportunity_cost_top_k_examples,
        "detail_log_top_k": context.detail_log_top_k,
        "influence_enabled": context.influence_enabled,
        "influence_track_ids": sorted(context.influence_track_ids),
        "influence_policy_mode": context.influence_policy_mode,
        "influence_reserved_slots": context.influence_reserved_slots,
        "influence_allow_genre_cap_override": context.influence_allow_genre_cap_override,
        "influence_allow_consecutive_override": context.influence_allow_consecutive_override,
        "influence_allow_score_threshold_override": context.influence_allow_score_threshold_override,
        "transition_smoothness_weight": context.transition_smoothness_weight,
    }
