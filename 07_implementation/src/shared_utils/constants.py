"""
Shared constants for implementation stages.

Centralizes feature specifications, default values, and other constants
that were previously duplicated across multiple stages.
"""

from typing import Any

# BL-003 Alignment Default Weights (for seed table preference weighting)
DEFAULT_TOP_RANGE_WEIGHTS = {
    "short_term": 0.50,
    "medium_term": 0.30,
    "long_term": 0.20,
}
DEFAULT_SOURCE_BASE_WEIGHTS = {
    "top_tracks": 1.00,
    "saved_tracks": 0.60,
    "playlist_items": 0.40,
    "recently_played": 0.50,
    "user_csv": 0.75,
}
DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK = 0.25

# BL-005 Candidate Filtering Default Values
DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT = 6
DEFAULT_PROFILE_TOP_TAG_LIMIT = 10
DEFAULT_PROFILE_TOP_GENRE_LIMIT = 8
DEFAULT_BL004_CONFIDENCE_WEIGHTING_MODE = "linear_half_bias"
DEFAULT_BL004_CONFIDENCE_BIN_HIGH_THRESHOLD = 0.90
DEFAULT_BL004_CONFIDENCE_BIN_MEDIUM_THRESHOLD = 0.50
DEFAULT_BL004_INTERACTION_ATTRIBUTION_MODE = "split_selected_types_equal_share"
DEFAULT_BL004_EMIT_PROFILE_POLICY_DIAGNOSTICS = True
DEFAULT_BL004_CONFIDENCE_VALIDATION_POLICY = "warn"
DEFAULT_BL004_INTERACTION_TYPE_VALIDATION_POLICY = "warn"
DEFAULT_BL004_SYNTHETIC_DATA_VALIDATION_POLICY = "warn"
DEFAULT_BL004_HANDSHAKE_VALIDATION_POLICY = "warn"
DEFAULT_BL004_NUMERIC_MALFORMED_ROW_THRESHOLD: int | None = None
DEFAULT_BL004_NO_NUMERIC_SIGNAL_ROW_THRESHOLD: int | None = None
DEFAULT_SEMANTIC_STRONG_KEEP_SCORE = 2
DEFAULT_SEMANTIC_MIN_KEEP_SCORE = 1
DEFAULT_NUMERIC_SUPPORT_MIN_PASS = 1
DEFAULT_NUMERIC_SUPPORT_MIN_SCORE = 1.0
DEFAULT_LANGUAGE_FILTER_ENABLED = False
DEFAULT_LANGUAGE_FILTER_CODES: list[str] = []
DEFAULT_RECENCY_YEARS_MIN_OFFSET: int | None = None
DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD = 0.5
DEFAULT_RETRIEVAL_USE_WEIGHTED_SEMANTICS = False
DEFAULT_RETRIEVAL_USE_CONTINUOUS_NUMERIC = False
DEFAULT_RETRIEVAL_ENABLE_POPULARITY_NUMERIC = False
DEFAULT_BL005_HANDSHAKE_VALIDATION_POLICY = "warn"
DEFAULT_SIGNAL_MODE_NAME = "v1f-compat"
ENHANCED_SIGNAL_MODE_NAME = "v1g-enhanced"
CUSTOM_SIGNAL_MODE_NAME = "custom"

DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS = 90.0
DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS = 365.0

# BL-006 Score Reporting Thresholds (for categorizing final scores)
DEFAULT_PERFECT_SCORE_THRESHOLD = 0.99
DEFAULT_ABOVE_THRESHOLD_SCORE = 0.50

# BL-006 Default Scoring Component Weights
DEFAULT_SCORING_COMPONENT_WEIGHTS = {
    "danceability": 0.10,
    "energy": 0.10,
    "valence": 0.08,
    "tempo": 0.10,
    "duration_ms": 0.07,
    "popularity": 0.0,
    "key": 0.06,
    "mode": 0.04,
    "lead_genre": 0.17,
    "genre_overlap": 0.12,
    "tag_overlap": 0.16,
}

# BL-003 Input Scope Default (canonical cross-stage default)
DEFAULT_INPUT_SCOPE: dict[str, object] = {
    "source_family": "spotify_api_export",
    "include_top_tracks": True,
    "top_time_ranges": ["short_term", "medium_term", "long_term"],
    "include_saved_tracks": True,
    "saved_tracks_limit": None,
    "include_playlists": True,
    "playlists_limit": None,
    "playlist_items_per_playlist_limit": None,
    "include_recently_played": True,
    "recently_played_limit": 50,
    "include_user_csv": True,
    "user_csv_limit": None,
}

# BL-004 Interaction Scope Default
DEFAULT_INCLUDE_INTERACTION_TYPES: list[str] = ["history", "influence"]

DEFAULT_INTERACTION_SCOPE: dict[str, object] = {
    "include_interaction_types": list(DEFAULT_INCLUDE_INTERACTION_TYPES),
}

DEFAULT_PROFILE_CONTROLS: dict[str, object] = {
    "input_scope": dict(DEFAULT_INPUT_SCOPE),
    "top_tag_limit": DEFAULT_PROFILE_TOP_TAG_LIMIT,
    "top_genre_limit": DEFAULT_PROFILE_TOP_GENRE_LIMIT,
    "top_lead_genre_limit": DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    "confidence_weighting_mode": DEFAULT_BL004_CONFIDENCE_WEIGHTING_MODE,
    "confidence_bin_high_threshold": DEFAULT_BL004_CONFIDENCE_BIN_HIGH_THRESHOLD,
    "confidence_bin_medium_threshold": DEFAULT_BL004_CONFIDENCE_BIN_MEDIUM_THRESHOLD,
    "interaction_attribution_mode": DEFAULT_BL004_INTERACTION_ATTRIBUTION_MODE,
    "emit_profile_policy_diagnostics": DEFAULT_BL004_EMIT_PROFILE_POLICY_DIAGNOSTICS,
    "confidence_validation_policy": DEFAULT_BL004_CONFIDENCE_VALIDATION_POLICY,
    "interaction_type_validation_policy": DEFAULT_BL004_INTERACTION_TYPE_VALIDATION_POLICY,
    "synthetic_data_validation_policy": DEFAULT_BL004_SYNTHETIC_DATA_VALIDATION_POLICY,
    "bl003_handshake_validation_policy": DEFAULT_BL004_HANDSHAKE_VALIDATION_POLICY,
    "numeric_malformed_row_threshold": DEFAULT_BL004_NUMERIC_MALFORMED_ROW_THRESHOLD,
    "no_numeric_signal_row_threshold": DEFAULT_BL004_NO_NUMERIC_SIGNAL_ROW_THRESHOLD,
    "user_id": "unknown_user",
    "include_interaction_types": list(DEFAULT_INCLUDE_INTERACTION_TYPES),
}

DEFAULT_CONTROL_MODE: dict[str, object] = {
    "validation_profile": "strict",
    "allow_threshold_decoupling": False,
    "allow_weight_auto_normalization": False,
}

DEFAULT_INFLUENCE_TRACKS: dict[str, object] = {
    "enabled": True,
    "track_ids": [],
    "preference_weight": 1.0,
    "source": None,
}

DEFAULT_SEED_CONTROLS: dict[str, Any] = {
    "match_rate_min_threshold": 0.0,
    "top_range_weights": dict(DEFAULT_TOP_RANGE_WEIGHTS),
    "source_base_weights": dict(DEFAULT_SOURCE_BASE_WEIGHTS),
    "source_resilience_policy": {
        "top_tracks": "required",
        "saved_tracks": "optional",
        "playlist_items": "optional",
        "recently_played": "advisory",
        "user_csv": "advisory",
    },
    "decay_half_lives": {
        "recently_played": DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
        "saved_tracks": DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
    },
    "fuzzy_matching": {
        "enabled": False,
        "artist_threshold": 0.90,
        "title_threshold": 0.90,
        "combined_threshold": 0.90,
        "max_duration_delta_ms": 5000,
        "max_artist_candidates": 5,
        "enable_album_scoring": True,
        "enable_secondary_artist_retry": False,
        "enable_relaxed_second_pass": False,
        "relaxed_second_pass_artist_threshold": 0.80,
        "relaxed_second_pass_title_threshold": 0.80,
        "relaxed_second_pass_combined_threshold": 0.80,
        "emit_fuzzy_diagnostics": True,
    },
    "match_strategy": {
        "enable_spotify_id_match": True,
        "enable_metadata_match": True,
        "enable_fuzzy_match": True,
    },
    "match_strategy_order": [
        "spotify_id_exact",
        "metadata_fallback",
        "fuzzy_title_artist",
    ],
    "temporal_controls": {
        "reference_mode": "system",
        "reference_now_utc": None,
    },
    "aggregation_policy": {
        "preference_weight_mode": "sum",
        "preference_weight_cap_per_event": None,
    },
}

DEFAULT_RETRIEVAL_NUMERIC_THRESHOLDS: dict[str, float] = {
    "danceability": 0.20,
    "energy": 0.20,
    "valence": 0.20,
    "tempo": 20.0,
    "popularity": 15.0,
    "key": 2.0,
    "mode": 0.5,
    "duration_ms": 45000.0,
    "release_year": 8.0,
}

DEFAULT_RETRIEVAL_CONTROLS: dict[str, object] = {
    "signal_mode": {},
    "profile_top_tag_limit": DEFAULT_PROFILE_TOP_TAG_LIMIT,
    "profile_top_genre_limit": DEFAULT_PROFILE_TOP_GENRE_LIMIT,
    "profile_top_lead_genre_limit": DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    "lead_genre_partial_match_threshold": DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
    "semantic_strong_keep_score": DEFAULT_SEMANTIC_STRONG_KEEP_SCORE,
    "semantic_min_keep_score": DEFAULT_SEMANTIC_MIN_KEEP_SCORE,
    "numeric_support_min_pass": DEFAULT_NUMERIC_SUPPORT_MIN_PASS,
    "numeric_support_min_score": DEFAULT_NUMERIC_SUPPORT_MIN_SCORE,
    "use_weighted_semantics": DEFAULT_RETRIEVAL_USE_WEIGHTED_SEMANTICS,
    "use_continuous_numeric": DEFAULT_RETRIEVAL_USE_CONTINUOUS_NUMERIC,
    "enable_popularity_numeric": DEFAULT_RETRIEVAL_ENABLE_POPULARITY_NUMERIC,
    "language_filter_enabled": DEFAULT_LANGUAGE_FILTER_ENABLED,
    "language_filter_codes": list(DEFAULT_LANGUAGE_FILTER_CODES),
    "recency_years_min_offset": DEFAULT_RECENCY_YEARS_MIN_OFFSET,
    "numeric_thresholds": dict(DEFAULT_RETRIEVAL_NUMERIC_THRESHOLDS),
    "profile_quality_penalty_enabled": True,
    "profile_quality_threshold": 0.90,
    "profile_entropy_low_threshold": 0.35,
    "influence_share_threshold": 0.60,
    "profile_quality_penalty_increment": 0.20,
    "profile_entropy_penalty_increment": 0.20,
    "influence_share_penalty_increment": 0.15,
    "numeric_penalty_scale": 0.50,
    "semantic_overlap_damping_mid_entropy_threshold": 0.60,
    "semantic_overlap_damping_low_entropy": 0.85,
    "semantic_overlap_damping_mid_entropy": 0.92,
    "enable_numeric_confidence_scaling": True,
    "numeric_confidence_floor": 0.0,
    "profile_numeric_confidence_mode": "direct",
    "profile_numeric_confidence_blend_weight": 1.0,
    "numeric_support_score_mode": "weighted_absolute",
    "emit_profile_policy_diagnostics": True,
    "bl004_bl005_handshake_validation_policy": DEFAULT_BL005_HANDSHAKE_VALIDATION_POLICY,
}

DEFAULT_SCORING_NUMERIC_THRESHOLDS: dict[str, float] = dict(DEFAULT_RETRIEVAL_NUMERIC_THRESHOLDS)

DEFAULT_SCORING_CONTROLS: dict[str, object] = {
    "signal_mode": {},
    "component_weights": dict(DEFAULT_SCORING_COMPONENT_WEIGHTS),
    "numeric_thresholds": dict(DEFAULT_SCORING_NUMERIC_THRESHOLDS),
    "lead_genre_strategy": "weighted_top_lead_genres",
    "semantic_overlap_strategy": "precision_aware",
    "semantic_precision_alpha_mode": "profile_adaptive",
    "semantic_precision_alpha_fixed": 0.35,
    "enable_numeric_confidence_scaling": True,
    "numeric_confidence_floor": 0.0,
    "profile_numeric_confidence_mode": "direct",
    "profile_numeric_confidence_blend_weight": 1.0,
    "emit_confidence_impact_diagnostics": True,
    "emit_semantic_precision_diagnostics": False,
    "apply_bl003_influence_tracks": False,
    "influence_track_bonus_scale": 0.0,
}

DEFAULT_ASSEMBLY_CONTROLS: dict[str, object] = {
    "target_size": 10,
    "min_score_threshold": 0.35,
    "max_per_genre": 4,
    "max_consecutive": 2,
    "utility_strategy": "rank_round_robin",
    "utility_weights": {
        "score_weight": 1.0,
        "novelty_weight": 0.0,
        "repetition_penalty_weight": 0.0,
    },
    "adaptive_limits": {
        "enabled": False,
        "reference_top_k": 100,
        "max_per_genre_scale_min": 0.75,
        "max_per_genre_scale_max": 1.25,
    },
    "controlled_relaxation": {
        "enabled": False,
        "relax_consecutive_first": True,
        "max_per_genre_increment": 1,
        "max_relaxation_rounds": 2,
        "never_relax_score_threshold": True,
    },
    "lead_genre_fallback_strategy": "none",
    "use_component_contributions_for_tiebreak": False,
    "use_semantic_strength_for_tiebreak": False,
    "emit_opportunity_cost_metrics": False,
    "detail_log_top_k": 100,
    "influence_policy_mode": "competitive",
    "influence_reserved_slots": 0,
    "influence_allow_genre_cap_override": False,
    "influence_allow_consecutive_override": False,
    "influence_allow_score_threshold_override": False,
}

# BL-008 Transparency Default
DEFAULT_TOP_CONTRIBUTOR_LIMIT = 3

DEFAULT_TRANSPARENCY_CONTROLS: dict[str, Any] = {
    "top_contributor_limit": DEFAULT_TOP_CONTRIBUTOR_LIMIT,
    "blend_primary_contributor_on_near_tie": False,
    "primary_contributor_tie_delta": 0.02,
}

DEFAULT_OBSERVABILITY_CONTROLS: dict[str, Any] = {
    "control_mode": dict(DEFAULT_CONTROL_MODE),
    "input_scope": dict(DEFAULT_INPUT_SCOPE),
    "diagnostic_sample_limit": 5,
    "bootstrap_mode": True,
}

DEFAULT_REPORTING_SCORE_THRESHOLDS: dict[str, float] = {
    "perfect_score": DEFAULT_PERFECT_SCORE_THRESHOLD,
    "above_threshold": DEFAULT_ABOVE_THRESHOLD_SCORE,
}

DEFAULT_CONTROLLABILITY_CONTROLS: dict[str, float] = {
    "weight_override_value_if_component_present": 0.20,
    "weight_override_increment_fallback": 0.08,
    "weight_override_cap_fallback": 0.35,
    "stricter_threshold_scale": 0.75,
    "looser_threshold_scale": 1.25,
}

# BL-003 Weighting policy — formula knobs extracted from alignment/weighting.py.
# Values match the previously embedded constants exactly so existing runs are
# numerically identical when this policy is wired in Phase 4.
DEFAULT_WEIGHTING_POLICY: dict[str, dict[str, float]] = {
    "top_tracks": {
        "min_rank_floor": 0.05,
        "scale_multiplier": 100.0,
        "default_time_range_weight": 0.20,
    },
    "playlist_items": {
        "min_position_floor": 0.05,
        "scale_multiplier": 20.0,
    },
}

# BL-011 Scenario policy — controls which scenarios run and how comparisons work.
DEFAULT_SCENARIO_POLICY: dict[str, Any] = {
    "enabled_scenario_ids": ["all"],
    "repeat_count": 1,
    "stage_scope": ["all"],
    "comparison_mode": "baseline_reference",
}

# BL-011 Scenario definitions — populated from config; empty list here means
# the Python-side fallback in Phase 2 will generate the built-in 5 scenarios.
DEFAULT_SCENARIO_DEFINITIONS: list[dict[str, object]] = []

# BL-013 Orchestration controls — stage graph and execution policy.
DEFAULT_ORCHESTRATION_CONTROLS: dict[str, Any] = {
    "stage_order": None,           # None = use the static default order in orchestration/main.py
    "continue_on_error": False,
    "refresh_seed_policy": "auto_if_stale",
    "required_stable_artifacts": [],
}

# BL-001/BL-002 Ingestion Resilience Defaults
DEFAULT_API_CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours
DEFAULT_API_THROTTLE_SLEEP_SEC = 0.12  # 120ms between calls
DEFAULT_API_MAX_RETRIES = 6
DEFAULT_API_BASE_DELAY_SEC = 1.0  # Base exponential backoff

DEFAULT_INGESTION_CONTROLS: dict[str, object] = {
    "cache_ttl_seconds": DEFAULT_API_CACHE_TTL_SECONDS,
    "throttle_sleep_seconds": DEFAULT_API_THROTTLE_SLEEP_SEC,
    "max_retries": DEFAULT_API_MAX_RETRIES,
    "base_backoff_delay_seconds": DEFAULT_API_BASE_DELAY_SEC,
}

# ── Valid enum values for stage controls ──────────────────────────────────
VALID_LEAD_GENRE_STRATEGIES: frozenset[str] = frozenset({"single_anchor", "weighted_top_lead_genres"})
VALID_SEMANTIC_OVERLAP_STRATEGIES: frozenset[str] = frozenset({"overlap_only", "precision_aware"})
VALID_SEMANTIC_ALPHA_MODES: frozenset[str] = frozenset({"profile_adaptive", "fixed"})
VALID_NUMERIC_CONFIDENCE_MODES: frozenset[str] = frozenset({"direct", "blended"})
VALID_CONFIDENCE_WEIGHTING_MODES: frozenset[str] = frozenset({"linear_half_bias", "direct_confidence", "none"})
VALID_INTERACTION_ATTRIBUTION_MODES: frozenset[str] = frozenset({"split_selected_types_equal_share", "primary_type_only"})
VALID_UTILITY_STRATEGIES: frozenset[str] = frozenset({"rank_round_robin", "utility_greedy"})
VALID_NUMERIC_SUPPORT_SCORE_MODES: frozenset[str] = frozenset({"raw", "weighted", "weighted_absolute"})
VALID_LEAD_GENRE_FALLBACK_STRATEGIES: frozenset[str] = frozenset({"none", "semantic_component_proxy"})
VALID_INFLUENCE_POLICY_MODES: frozenset[str] = frozenset({"competitive", "reserved_slots", "hybrid_override"})

# Numeric features that are valid only when both the BL-004 profile and the
# candidate dataset provide comparable values.
# Each spec defines a candidate column, distance threshold, and whether the dimension is circular.
NUMERIC_FEATURE_SPECS = {
    "danceability": {
        "candidate_column": "danceability",
        "threshold": 0.20,
        "circular": False,
    },
    "energy": {
        "candidate_column": "energy",
        "threshold": 0.20,
        "circular": False,
    },
    "valence": {
        "candidate_column": "valence",
        "threshold": 0.20,
        "circular": False,
    },
    "tempo": {
        "candidate_column": "tempo",
        "threshold": 20.0,
        "circular": False,
    },
    "popularity": {
        "candidate_column": "popularity",
        "threshold": 15.0,
        "circular": False,
    },
    "key": {
        "candidate_column": "key",
        "threshold": 2.0,
        "circular": True,
    },
    "mode": {
        "candidate_column": "mode",
        "threshold": 0.5,
        "circular": False,
    },
    "duration_ms": {
        "candidate_column": "duration_ms",
        "threshold": 45000.0,
        "circular": False,
    },
    "release_year": {
        "candidate_column": "release",
        "threshold": 8.0,
        "circular": False,
    },
}
