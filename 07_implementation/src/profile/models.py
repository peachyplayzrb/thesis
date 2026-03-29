from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProfilePaths:
    seed_table_path: Path
    bl003_summary_path: Path
    bl003_manifest_path: Path
    output_dir: Path
    seed_trace_path: Path
    profile_path: Path
    summary_path: Path


@dataclass(frozen=True)
class ProfileControls:
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    input_scope: dict[str, object]
    top_tag_limit: int
    top_genre_limit: int
    top_lead_genre_limit: int
    user_id: str
    include_interaction_types: list[str]

    def as_mapping(self) -> dict[str, object]:
        return {
            "config_source": self.config_source,
            "run_config_path": self.run_config_path,
            "run_config_schema_version": self.run_config_schema_version,
            "input_scope": dict(self.input_scope),
            "top_tag_limit": self.top_tag_limit,
            "top_genre_limit": self.top_genre_limit,
            "top_lead_genre_limit": self.top_lead_genre_limit,
            "user_id": self.user_id,
            "include_interaction_types": list(self.include_interaction_types),
        }


@dataclass(frozen=True)
class ProfileInputs:
    seed_rows: list[dict[str, object]]
    bl003_summary: dict[str, object]
    bl003_manifest: dict[str, object]
    bl003_seed_contract: dict[str, object]
    bl003_structural_contract: dict[str, object]
    bl003_seed_contract_hash: str
    bl003_structural_contract_hash: str


@dataclass(frozen=True)
class ProfileAggregation:
    input_row_count: int
    seed_trace_rows: list[dict[str, object]]
    numeric_profile: dict[str, float]
    tag_weights: dict[str, float]
    genre_weights: dict[str, float]
    lead_genre_weights: dict[str, float]
    counts_by_type: dict[str, int]
    weight_by_type: dict[str, float]
    interaction_count_sum_by_type: dict[str, int]
    numeric_observations: dict[str, int]
    missing_numeric_track_ids: list[str]
    blank_track_id_row_count: int
    total_effective_weight: float
    confidence_adjusted_weight_sum: float
    confidence_bins: dict[str, int]
    match_method_counts: dict[str, int]
    history_preference_weight_sum: float
    influence_preference_weight_sum: float
    history_interaction_count_sum: int
    influence_interaction_count_sum: int
    matched_seed_count: int


@dataclass(frozen=True)
class ProfileArtifacts:
    profile_path: Path
    summary_path: Path
    seed_trace_path: Path
