"""
Filtering logic for BL-005: core decision engine and reasoning.

Provides pure decision-making functions independent of I/O or data parsing.
"""


def keep_decision(
    is_seed_track: bool,
    semantic_score: int,
    numeric_pass_count: int,
    numeric_features_enabled: bool,
    semantic_strong_keep_score: int,
    semantic_min_keep_score: int,
    numeric_support_min_pass: int,
) -> tuple[bool, str]:
    """
    Determine whether a candidate should be kept based on scoring rules.
    
    Decision logic:
    1. Seed tracks are always excluded (not part of retrieval output)
    2. If numeric features disabled: keep if semantic score meets minimum
    3. If numeric features enabled:
       - Keep if semantic score is STRONG (even without numeric support)
       - Keep if semantic score meets MINIMUM AND numeric support passes
       - Otherwise reject
    
    Args:
        is_seed_track: True if candidate is a seed track
        semantic_score: 0-3 score from semantic rules (genre/tag matching)
        numeric_pass_count: Count of numeric features passing within threshold
        numeric_features_enabled: True if numeric features are active
        semantic_strong_keep_score: Threshold for strong semantic signal (typically 2)
        semantic_min_keep_score: Threshold for minimum semantic signal (typically 1)
        numeric_support_min_pass: Minimum numeric features needed to support weak semantic (typically 1)
    
    Returns:
        Tuple of (bool kept, str decision_path) where decision_path identifies
        why the decision was made (e.g., "keep_strong_semantic", "reject_seed_track")
    """
    # Rule 1: Exclude seed tracks (they're part of the seed dataset)
    if is_seed_track:
        return False, "reject_seed_track"
    
    # Rule 2: Semantic-only mode (no numeric features)
    if not numeric_features_enabled:
        if semantic_score >= semantic_min_keep_score:
            return True, "keep_semantic_only"
        return False, "reject_insufficient_semantic"
    
    # Rule 3: Numeric features enabled - multi-signal evaluation
    # Strong semantic signal overrides numeric requirements
    if semantic_score >= semantic_strong_keep_score:
        return True, "keep_strong_semantic"
    
    # Weak semantic signal needs numeric support
    if semantic_score >= semantic_min_keep_score and numeric_pass_count >= numeric_support_min_pass:
        return True, "keep_semantic_numeric_supported"
    
    # Semantic signal too weak, check if numeric alone could save it
    if semantic_score >= semantic_min_keep_score:
        return False, "reject_semantic_without_numeric_support"
    
    # Numeric signal without semantic support
    if numeric_pass_count > 0:
        return False, "reject_numeric_without_semantic_support"
    
    # No signal on any dimension
    return False, "reject_no_signal"


def decision_reason(decision_path: str, semantic_score: int, numeric_pass_count: int) -> str:
    """
    Generate human-readable explanation for a keep/reject decision.
    
    Args:
        decision_path: Decision path identifier from keep_decision()
        semantic_score: Semantic score (for context in explanation)
        numeric_pass_count: Count of numeric features passing (for context)
    
    Returns:
        Human-readable string explaining the decision
    """
    if decision_path == "reject_seed_track":
        return "reject: seed track excluded from retrieval output"
    
    if decision_path == "keep_semantic_only":
        return f"keep: semantic_score={semantic_score} with semantic-only mode"
    
    if decision_path == "keep_strong_semantic":
        return f"keep: semantic_score={semantic_score} meets strong semantic threshold"
    
    if decision_path == "keep_semantic_numeric_supported":
        return f"keep: semantic_score={semantic_score} with numeric_pass_count={numeric_pass_count}"
    
    if decision_path == "reject_semantic_without_numeric_support":
        return f"reject: semantic_score={semantic_score} lacks numeric support (numeric_pass_count={numeric_pass_count})"
    
    if decision_path == "reject_numeric_without_semantic_support":
        return f"reject: numeric_pass_count={numeric_pass_count} without semantic evidence"
    
    return f"reject: semantic_score={semantic_score}, numeric_pass_count={numeric_pass_count} below keep threshold"
