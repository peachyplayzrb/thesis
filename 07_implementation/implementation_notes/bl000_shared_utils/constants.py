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

# BL-006 Score Reporting Thresholds (for categorizing final scores)
DEFAULT_PERFECT_SCORE_THRESHOLD = 0.99
DEFAULT_ABOVE_THRESHOLD_SCORE = 0.50

# BL-006 Default Scoring Component Weights
DEFAULT_SCORING_COMPONENT_WEIGHTS = {
    "tempo": 0.20,
    "duration_ms": 0.13,
    "key": 0.13,
    "mode": 0.09,
    "lead_genre": 0.17,
    "genre_overlap": 0.12,
    "tag_overlap": 0.16,
}

# BL-001/BL-002 Ingestion Resilience Defaults
DEFAULT_API_CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours
DEFAULT_API_THROTTLE_SLEEP_SEC = 0.12  # 120ms between calls
DEFAULT_API_MAX_RETRIES = 6
DEFAULT_API_BASE_DELAY_SEC = 1.0  # Base exponential backoff

# Numeric features that are valid only when both the BL-004 profile and the
# candidate dataset provide comparable values.
# Each spec defines a candidate column, distance threshold, and whether the dimension is circular.
NUMERIC_FEATURE_SPECS = {
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
}
