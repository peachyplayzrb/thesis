"""Data containers passed around inside the BL-004 profile stage."""

from __future__ import annotations

from dataclasses import dataclass, field
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
    confidence_weighting_mode: str = "linear_half_bias"
    confidence_bin_high_threshold: float = 0.90
    confidence_bin_medium_threshold: float = 0.50
    interaction_attribution_mode: str = "split_selected_types_equal_share"
    emit_profile_policy_diagnostics: bool = True
    confidence_validation_policy: str = "warn"
    interaction_type_validation_policy: str = "warn"
    synthetic_data_validation_policy: str = "warn"
    bl003_handshake_validation_policy: str = "warn"
    numeric_malformed_row_threshold: int | None = None
    no_numeric_signal_row_threshold: int | None = None

    def as_mapping(self) -> dict[str, object]:
        return {
            "config_source": self.config_source,
            "run_config_path": self.run_config_path,
            "run_config_schema_version": self.run_config_schema_version,
            "input_scope": dict(self.input_scope),
            "top_tag_limit": self.top_tag_limit,
            "top_genre_limit": self.top_genre_limit,
            "top_lead_genre_limit": self.top_lead_genre_limit,
            "confidence_weighting_mode": self.confidence_weighting_mode,
            "confidence_bin_high_threshold": self.confidence_bin_high_threshold,
            "confidence_bin_medium_threshold": self.confidence_bin_medium_threshold,
            "interaction_attribution_mode": self.interaction_attribution_mode,
            "emit_profile_policy_diagnostics": self.emit_profile_policy_diagnostics,
            "confidence_validation_policy": self.confidence_validation_policy,
            "interaction_type_validation_policy": self.interaction_type_validation_policy,
            "synthetic_data_validation_policy": self.synthetic_data_validation_policy,
            "bl003_handshake_validation_policy": self.bl003_handshake_validation_policy,
            "numeric_malformed_row_threshold": self.numeric_malformed_row_threshold,
            "no_numeric_signal_row_threshold": self.no_numeric_signal_row_threshold,
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
    bl003_quality: dict[str, int | float] = field(default_factory=dict)
    bl003_rows_selected: dict[str, int] = field(default_factory=dict)
    bl003_rows_available: dict[str, int] = field(default_factory=dict)
    bl003_coverage_rate_by_source: dict[str, float] = field(default_factory=dict)
    bl003_handshake_warnings: list[str] = field(default_factory=list)
    bl003_config_source: str = "unknown"


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
    confidence_fallback_row_count: int = 0
    confidence_malformed_row_count: int = 0
    defaulted_interaction_type_row_count: int = 0
    synthetic_interaction_count_row_count: int = 0
    interaction_count_malformed_row_count: int = 0
    synthetic_history_weight_row_count: int = 0
    history_weight_malformed_row_count: int = 0
    synthetic_influence_weight_row_count: int = 0
    influence_weight_malformed_row_count: int = 0
    synthetic_weight_reconstruction_row_count: int = 0
    synthetic_weight_reconstruction_track_ids: list[str] = field(default_factory=list)
    no_numeric_signal_row_count: int = 0
    malformed_numeric_row_count: int = 0
    malformed_numeric_value_count_by_feature: dict[str, int] = field(default_factory=dict)
    validation_policies: dict[str, str] = field(default_factory=dict)
    validation_warnings: list[str] = field(default_factory=list)
    mixed_interaction_row_count: int = 0
    primary_type_attribution_row_count: int = 0
    attribution_weight_by_type: dict[str, float] = field(
        default_factory=lambda: {"history": 0.0, "influence": 0.0}
    )
    attribution_interaction_count_by_type: dict[str, float] = field(
        default_factory=lambda: {"history": 0.0, "influence": 0.0}
    )
    attribution_row_share_by_type: dict[str, float] = field(
        default_factory=lambda: {"history": 0.0, "influence": 0.0}
    )
    bl003_event_level_match_method_counts: dict[str, int] = field(default_factory=dict)
    bl003_input_event_rows_total: int = 0


@dataclass(frozen=True)
class ProfileArtifacts:
    profile_path: Path
    summary_path: Path
    seed_trace_path: Path
