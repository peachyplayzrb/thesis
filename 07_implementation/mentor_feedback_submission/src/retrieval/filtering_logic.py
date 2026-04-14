"""Core keep/reject logic for BL-005 candidate filtering.

This file keeps the decision rules separate from CSV parsing and file writing so
the retrieval thresholds can be reasoned about in one place.
"""


def keep_decision(
    is_seed_track: bool,
    semantic_score: float,
    numeric_pass_count: int,
    numeric_features_enabled: bool,
    semantic_strong_keep_score: float,
    semantic_min_keep_score: float,
    numeric_support_min_pass: int,
    *,
    numeric_support_score: float | None = None,
    numeric_support_min_score: float | None = None,
    use_continuous_numeric: bool = False,
    language_match: bool | None = None,
    recency_pass: bool | None = None,
) -> tuple[bool, str]:
    """Decide whether a candidate should be kept.

    Seed tracks are always excluded because they are the profile input, not retrieval output. Without numeric
    features, a candidate only needs enough semantic evidence to pass. When numeric features are enabled, a very
    strong semantic signal can keep a track on its own, but borderline semantic cases need numeric support as well.
    """
    # Seed tracks are the training signal for the profile, so they never belong in the retrieval result.
    if is_seed_track:
        return False, "reject_seed_track"

    # These optional gates are meant to fail early before the scoring rules try to rescue the row.
    if language_match is False:
        return False, "reject_language_filter"

    if recency_pass is False:
        return False, "reject_recency_gate"

    if not numeric_features_enabled:
        if semantic_score >= semantic_min_keep_score:
            return True, "keep_semantic_only"
        return False, "reject_insufficient_semantic"

    # A very strong semantic match is enough on its own even if the numeric side is weak.
    if semantic_score >= semantic_strong_keep_score:
        return True, "keep_strong_semantic"

    # Weaker semantic matches only survive if the numeric evidence also points the same way.
    numeric_support_met = numeric_pass_count >= numeric_support_min_pass
    if use_continuous_numeric and numeric_support_score is not None:
        numeric_support_met = numeric_support_score >= float(
            numeric_support_min_score
            if numeric_support_min_score is not None
            else numeric_support_min_pass
        )

    if semantic_score >= semantic_min_keep_score and numeric_support_met:
        return True, "keep_semantic_numeric_supported"

    if semantic_score >= semantic_min_keep_score:
        return False, "reject_semantic_without_numeric_support"

    has_numeric_signal = numeric_pass_count > 0
    if use_continuous_numeric and numeric_support_score is not None:
        has_numeric_signal = numeric_support_score > 0.0

    if has_numeric_signal:
        return False, "reject_numeric_without_semantic_support"

    return False, "reject_no_signal"


def decision_reason(
    decision_path: str,
    semantic_score: float,
    numeric_pass_count: int,
    *,
    numeric_support_score: float | None = None,
    use_continuous_numeric: bool = False,
) -> str:
    """Turn the internal decision path into a short human-readable explanation string."""
    numeric_support_fragment = (
        f"numeric_support_score={numeric_support_score:.2f}"
        if use_continuous_numeric and numeric_support_score is not None
        else f"numeric_pass_count={numeric_pass_count}"
    )

    if decision_path == "reject_seed_track":
        return "reject: seed track excluded from retrieval output"

    if decision_path == "reject_language_filter":
        return "reject: language filter mismatch"

    if decision_path == "reject_recency_gate":
        return "reject: release year outside recency gate"

    if decision_path == "keep_semantic_only":
        return f"keep: semantic_score={semantic_score:.2f} with semantic-only mode"

    if decision_path == "keep_strong_semantic":
        return f"keep: semantic_score={semantic_score:.2f} meets strong semantic threshold"

    if decision_path == "keep_semantic_numeric_supported":
        return f"keep: semantic_score={semantic_score:.2f} with {numeric_support_fragment}"

    if decision_path == "reject_semantic_without_numeric_support":
        return f"reject: semantic_score={semantic_score:.2f} lacks numeric support ({numeric_support_fragment})"

    if decision_path == "reject_numeric_without_semantic_support":
        return f"reject: {numeric_support_fragment} without semantic evidence"

    return f"reject: semantic_score={semantic_score:.2f}, {numeric_support_fragment} below keep threshold"
