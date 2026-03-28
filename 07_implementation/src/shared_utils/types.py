"""
Shared type definitions and data contracts for implementation stages.

Provides TypedDicts and other type hints for data structures that are used
across multiple stages.
"""

from typing import Any, TypedDict


class NumericFeatureSpec(TypedDict):
    """Specification for a numeric feature dimension.

    Attributes:
        candidate_column: Column name in candidate dataset
        threshold: Maximum allowed distance for matching
        circular: Whether this is a circular dimension (e.g., key/mode)
    """
    candidate_column: str
    threshold: float
    circular: bool


class RunConfigControls(TypedDict):
    """Run configuration controls resolved at runtime.

    Attributes:
        config_source: Source of configuration ("run_config" or "environment")
        run_config_path: Path to run config file or None
        run_config_schema_version: Schema version or None
        profile_top_lead_genre_limit: Max lead genres in profile
        profile_top_tag_limit: Max tags in profile
        profile_top_genre_limit: Max genres in profile
        semantic_strong_keep_score: Threshold for strong semantic keep
        semantic_min_keep_score: Threshold for minimum semantic keep
        numeric_support_min_pass: Minimum numeric feature support count
        numeric_thresholds: Dict of numeric threshold overrides
    """
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    profile_top_lead_genre_limit: int
    profile_top_tag_limit: int
    profile_top_genre_limit: int
    semantic_strong_keep_score: int
    semantic_min_keep_score: int
    numeric_support_min_pass: int
    numeric_thresholds: dict[str, Any]


class ControlModeConfig(TypedDict):
    validation_profile: str
    allow_threshold_decoupling: bool
    allow_weight_auto_normalization: bool


class InputScopeConfig(TypedDict):
    source_family: str
    include_top_tracks: bool
    top_time_ranges: list[str]
    include_saved_tracks: bool
    saved_tracks_limit: int | None
    include_playlists: bool
    playlists_limit: int | None
    playlist_items_per_playlist_limit: int | None
    include_recently_played: bool
    recently_played_limit: int | None


class InteractionScopeConfig(TypedDict):
    include_interaction_types: list[str]


class InfluenceTracksConfig(TypedDict):
    enabled: bool
    track_ids: list[str]
    preference_weight: float
    source: str | None


class SeedControlsConfig(TypedDict):
    match_rate_min_threshold: float
    top_range_weights: dict[str, float]
    source_base_weights: dict[str, float]


class IngestionControlsConfig(TypedDict):
    cache_ttl_seconds: int
    throttle_sleep_seconds: float
    max_retries: int
    base_backoff_delay_seconds: float


class TransparencyControlsConfig(TypedDict):
    top_contributor_limit: int
    blend_primary_contributor_on_near_tie: bool
    primary_contributor_tie_delta: float


class ObservabilityControlsConfig(TypedDict):
    diagnostic_sample_limit: int
    bootstrap_mode: bool


class ReportingScoreThresholdsConfig(TypedDict):
    perfect_score: float
    above_threshold: float


class ControllabilityControlsConfig(TypedDict):
    weight_override_value_if_component_present: float
    weight_override_increment_fallback: float
    weight_override_cap_fallback: float
    stricter_threshold_scale: float
    looser_threshold_scale: float


class CsvRow(TypedDict):
    """Base type for CSV row data.

    Maps column names to string values as parsed by csv.DictReader.
    """
    pass  # Dict[str, str] - subclasses will extend this
