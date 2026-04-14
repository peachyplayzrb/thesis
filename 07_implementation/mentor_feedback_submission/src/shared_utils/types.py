"""
Shared TypedDict definitions for structures that get passed between stages.

Keeping them here makes the stage contracts easier to reuse without repeating
the same shapes in multiple modules.
"""

from typing import Any, TypedDict


class NumericFeatureSpec(TypedDict):
    """Describes one numeric feature: which column it uses, its threshold, and whether it wraps."""
    candidate_column: str
    threshold: float
    circular: bool


class RunConfigControls(TypedDict):
    """
    The shared runtime controls several stages expect after config resolution.

    It includes provenance about where the config came from plus the main limits
    and thresholds used by profile, retrieval, and scoring.
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
    fuzzy_matching: dict[str, Any]
    decay_half_lives: dict[str, float]


class SeedWeightingPolicyConfig(TypedDict, total=False):
    """
    Optional knobs for the BL-003 preference-weight formula.

    These values control how top-track rank and playlist position are converted
    into event weights, while preserving the old defaults unless overridden.
    """
    top_tracks_min_rank_floor: float          # default 0.05
    top_tracks_scale_multiplier: float        # default 100.0
    top_tracks_default_time_range_weight: float  # default 0.20 (fallback when time_range absent)
    playlist_items_min_position_floor: float  # default 0.05
    playlist_items_scale_multiplier: float    # default 20.0


class AcceptanceBoundConfig(TypedDict, total=False):
    """One quantitative rule used to judge whether a controllability scenario passed."""
    metric: str       # e.g. "candidate_pool_size_delta"
    comparator: str   # "less_than" | "greater_than" | "equal_to" | "not_equal_to"
    value: float      # threshold value
    required: bool    # if True, failing this rule fails the scenario


class ScenarioDefinitionConfig(TypedDict, total=False):
    """The full declarative definition for one BL-011 controllability scenario."""
    scenario_id: str
    test_id: str
    control_surface: str
    description: str
    expected_effect: str
    profile_patch: dict[str, Any]
    retrieval_patch: dict[str, Any]
    scoring_patch: dict[str, Any]
    assembly_patch: dict[str, Any]
    acceptance_bounds: list[AcceptanceBoundConfig]


class ScenarioPolicyConfig(TypedDict, total=False):
    """Controls how BL-011 runs the scenario set and compares the results."""
    enabled_scenario_ids: list[str]  # ["all"] means run all defined scenarios
    repeat_count: int                # number of times each scenario is run (for stability)
    stage_scope: list[str]           # which stages to include; ["all"] = full pipeline
    comparison_mode: str             # "baseline_reference" | "pairwise"


class OrchestrationControlsConfig(TypedDict, total=False):
    """Control values for BL-013 stage order and execution policy."""
    stage_order: list[str] | None    # None = use static default order
    continue_on_error: bool          # default False; if True non-fatal stage failures are skipped
    refresh_seed_policy: str         # "auto_if_stale" | "always" | "never"
    required_stable_artifacts: list[str]  # artifact names that must hash-match between runs


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
    """Base type for a CSV row as parsed by `csv.DictReader`."""
    pass  # Dict[str, str] - subclasses will extend this
