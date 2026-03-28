"""
Shared constants for implementation stages.

Centralizes feature specifications, default values, and other constants
that were previously duplicated across multiple stages.
"""

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
}
DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK = 0.25

# BL-005 Candidate Filtering Default Values
DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT = 6
DEFAULT_PROFILE_TOP_TAG_LIMIT = 10
DEFAULT_PROFILE_TOP_GENRE_LIMIT = 8
DEFAULT_SEMANTIC_STRONG_KEEP_SCORE = 2
DEFAULT_SEMANTIC_MIN_KEEP_SCORE = 1
DEFAULT_NUMERIC_SUPPORT_MIN_PASS = 1
DEFAULT_LANGUAGE_FILTER_ENABLED = False
DEFAULT_LANGUAGE_FILTER_CODES: list[str] = []
DEFAULT_RECENCY_YEARS_MIN_OFFSET: int | None = None
DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD = 0.5

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
}

# BL-004 Interaction Scope Default
DEFAULT_INCLUDE_INTERACTION_TYPES: list[str] = ["history", "influence"]

DEFAULT_INTERACTION_SCOPE: dict[str, object] = {
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

DEFAULT_SEED_CONTROLS: dict[str, object] = {
    "match_rate_min_threshold": 0.0,
    "top_range_weights": dict(DEFAULT_TOP_RANGE_WEIGHTS),
    "source_base_weights": dict(DEFAULT_SOURCE_BASE_WEIGHTS),
    "decay_half_lives": {
        "recently_played": DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
        "saved_tracks": DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
    },
}

DEFAULT_RETRIEVAL_NUMERIC_THRESHOLDS: dict[str, float] = {
    "danceability": 0.20,
    "energy": 0.20,
    "valence": 0.20,
    "tempo": 20.0,
    "key": 2.0,
    "mode": 0.5,
    "duration_ms": 45000.0,
    "release_year": 8.0,
}

DEFAULT_SCORING_NUMERIC_THRESHOLDS: dict[str, float] = dict(DEFAULT_RETRIEVAL_NUMERIC_THRESHOLDS)

DEFAULT_ASSEMBLY_CONTROLS: dict[str, object] = {
    "target_size": 10,
    "min_score_threshold": 0.35,
    "max_per_genre": 4,
    "max_consecutive": 2,
}

# BL-008 Transparency Default
DEFAULT_TOP_CONTRIBUTOR_LIMIT = 3

DEFAULT_TRANSPARENCY_CONTROLS: dict[str, object] = {
    "top_contributor_limit": DEFAULT_TOP_CONTRIBUTOR_LIMIT,
    "blend_primary_contributor_on_near_tie": False,
    "primary_contributor_tie_delta": 0.02,
}

DEFAULT_OBSERVABILITY_CONTROLS: dict[str, object] = {
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
