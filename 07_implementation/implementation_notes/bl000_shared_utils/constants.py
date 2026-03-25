"""
Shared constants for implementation stages.

Centralizes feature specifications, default values, and other constants
that were previously duplicated across multiple stages.
"""

# BL-005 Candidate Filtering Default Values
DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT = 6
DEFAULT_PROFILE_TOP_TAG_LIMIT = 10
DEFAULT_PROFILE_TOP_GENRE_LIMIT = 8
DEFAULT_SEMANTIC_STRONG_KEEP_SCORE = 2
DEFAULT_SEMANTIC_MIN_KEEP_SCORE = 1
DEFAULT_NUMERIC_SUPPORT_MIN_PASS = 1

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
