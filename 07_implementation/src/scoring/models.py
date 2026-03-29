from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from scoring.profile_extractor import build_numeric_specs


NUMERIC_FEATURE_SPECS = build_numeric_specs()
NUMERIC_COMPONENTS = set(NUMERIC_FEATURE_SPECS)
SCORED_CANDIDATE_FIELDS = [
    "rank",
    "track_id",
    "lead_genre",
    "matched_genres",
    "matched_tags",
    "final_score",
    "danceability_similarity",
    "danceability_contribution",
    "energy_similarity",
    "energy_contribution",
    "valence_similarity",
    "valence_contribution",
    "tempo_similarity",
    "tempo_contribution",
    "duration_ms_similarity",
    "duration_ms_contribution",
    "key_similarity",
    "key_contribution",
    "mode_similarity",
    "mode_contribution",
    "lead_genre_similarity",
    "lead_genre_contribution",
    "genre_overlap_similarity",
    "genre_overlap_contribution",
    "tag_overlap_similarity",
    "tag_overlap_contribution",
]


@dataclass(frozen=True)
class ScoringPaths:
    profile_path: Path
    filtered_candidates_path: Path
    output_dir: Path


@dataclass(frozen=True)
class ScoringControls:
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    component_weights: dict[str, float]
    numeric_thresholds: dict[str, float]

    def as_mapping(self) -> dict[str, object]:
        return {
            "config_source": self.config_source,
            "run_config_path": self.run_config_path,
            "run_config_schema_version": self.run_config_schema_version,
            "component_weights": dict(self.component_weights),
            "numeric_thresholds": dict(self.numeric_thresholds),
        }


@dataclass(frozen=True)
class ScoringInputs:
    profile: dict[str, object]
    candidates: list[dict[str, str]]


@dataclass(frozen=True)
class ScoringContext:
    effective_component_weights: dict[str, float]
    active_numeric_specs: dict[str, dict[str, object]]
    profile_scoring_data: dict[str, object]
    active_component_weights: dict[str, float]
    weight_rebalance_diagnostics: dict[str, object]


@dataclass(frozen=True)
class ScoringArtifacts:
    scored_path: Path
    diagnostics_path: Path
    summary_path: Path


def controls_from_mapping(payload: Mapping[str, Any]) -> ScoringControls:
    component_weights_raw = payload.get("component_weights")
    numeric_thresholds_raw = payload.get("numeric_thresholds")

    component_weights = {
        str(k): float(v)
        for k, v in dict(component_weights_raw).items()
    } if isinstance(component_weights_raw, Mapping) else {}
    numeric_thresholds = {
        str(k): float(v)
        for k, v in dict(numeric_thresholds_raw).items()
    } if isinstance(numeric_thresholds_raw, Mapping) else {}

    return ScoringControls(
        config_source=str(payload.get("config_source") or "environment"),
        run_config_path=(str(payload["run_config_path"]) if payload.get("run_config_path") else None),
        run_config_schema_version=(
            str(payload["run_config_schema_version"])
            if payload.get("run_config_schema_version")
            else None
        ),
        component_weights=component_weights,
        numeric_thresholds=numeric_thresholds,
    )


def context_as_mapping(context: ScoringContext) -> dict[str, object]:
    return {
        "effective_component_weights": dict(context.effective_component_weights),
        "active_numeric_specs": dict(context.active_numeric_specs),
        "profile_scoring_data": dict(context.profile_scoring_data),
        "active_component_weights": dict(context.active_component_weights),
        "weight_rebalance_diagnostics": dict(context.weight_rebalance_diagnostics),
    }


def context_from_mapping(payload: Mapping[str, Any]) -> ScoringContext:
    effective_component_weights_raw = payload.get("effective_component_weights")
    active_numeric_specs_raw = payload.get("active_numeric_specs")
    profile_scoring_data_raw = payload.get("profile_scoring_data")
    active_component_weights_raw = payload.get("active_component_weights")
    weight_rebalance_diagnostics_raw = payload.get("weight_rebalance_diagnostics")

    effective_component_weights = {
        str(k): float(v)
        for k, v in dict(effective_component_weights_raw).items()
    } if isinstance(effective_component_weights_raw, Mapping) else {}

    active_numeric_specs: dict[str, dict[str, object]] = {}
    if isinstance(active_numeric_specs_raw, Mapping):
        for key, value in active_numeric_specs_raw.items():
            if isinstance(value, Mapping):
                active_numeric_specs[str(key)] = {str(k): v for k, v in value.items()}

    profile_scoring_data = (
        {str(k): v for k, v in dict(profile_scoring_data_raw).items()}
        if isinstance(profile_scoring_data_raw, Mapping)
        else {}
    )
    active_component_weights = {
        str(k): float(v)
        for k, v in dict(active_component_weights_raw).items()
    } if isinstance(active_component_weights_raw, Mapping) else {}
    weight_rebalance_diagnostics = (
        {str(k): v for k, v in dict(weight_rebalance_diagnostics_raw).items()}
        if isinstance(weight_rebalance_diagnostics_raw, Mapping)
        else {}
    )

    return ScoringContext(
        effective_component_weights=effective_component_weights,
        active_numeric_specs=active_numeric_specs,
        profile_scoring_data=profile_scoring_data,
        active_component_weights=active_component_weights,
        weight_rebalance_diagnostics=weight_rebalance_diagnostics,
    )
