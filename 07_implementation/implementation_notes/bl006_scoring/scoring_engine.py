"""
Scoring engine for BL-006 candidate scoring.

Core similarity and scoring computation functions for comparing
candidates against the user preference profile.
"""

from typing import Any


def numeric_similarity(value: float | None, center: float, threshold: float, circular: bool = False) -> float:
    """
    Compute similarity score for numeric dimensions.
    
    Score = 1.0 - (distance / threshold), clamped to [0, 1].
    Circular dimensions (key) wrap around at 12 (semitone circle).
    
    Args:
        value: Candidate numeric value
        center: Profile center value
        threshold: Distance threshold for scoring
        circular: Whether dimension wraps (key: 0-11 semitones)
    
    Returns:
        Similarity score 0.0 (no match) to 1.0 (perfect match)
    """
    if value is None:
        return 0.0
    
    if circular:
        # Circular distance: for key, wrap around 12
        raw_diff = abs(value - center)
        diff = min(raw_diff, 12.0 - raw_diff)
    else:
        diff = abs(value - center)
    
    similarity = 1.0 - (diff / threshold)
    return round(max(0.0, min(similarity, 1.0)), 6)


def weighted_overlap(candidate_set: list[str], profile_weights: dict[str, float]) -> float:
    """
    Score 0→1 based on semantic set intersection with profile weights.
    
    Uses weighted Jaccard-like metric:
    - overlap = sum of weights for labels in both candidate and profile
    - total = sum of all profile weights
    - score = overlap / total
    
    Args:
        candidate_set: List of candidate labels (genres or tags)
        profile_weights: Dict mapping profile labels to weights
    
    Returns:
        Similarity score 0.0 to 1.0
    """
    if not profile_weights or not candidate_set:
        return 0.0
    
    matched_weight = sum(profile_weights.get(label, 0.0) for label in candidate_set)
    total_weight = sum(profile_weights.values())
    
    if total_weight <= 0:
        return 0.0
    
    return round(matched_weight / total_weight, 6)


def compute_component_scores(
    candidate_attrs: dict[str, Any],
    profile_data: dict[str, object],
    active_numeric_specs: dict[str, dict[str, object]],
) -> dict[str, object]:
    """
    Compute all 7 component scores for a candidate.
    
    Args:
        candidate_attrs: Parsed candidate attributes from candidate_parsed.parse_candidate_attributes()
        profile_data: Profile scoring data from profile_extractor.extract_profile_scoring_data()
        active_numeric_specs: Active numeric specs dict mapping dimensions to their thresholds
    
    Returns:
        Dict with all similarities and contributions:
        - "tempo_similarity", "tempo_contribution"
        - "duration_ms_similarity", "duration_ms_contribution"
        - "key_similarity", "key_contribution"
        - "mode_similarity", "mode_contribution"
        - "lead_genre_similarity", "lead_genre_contribution"
        - "genre_overlap_similarity", "genre_overlap_contribution"
        - "tag_overlap_similarity", "tag_overlap_contribution"
        - "matched_genres", "matched_tags" (for output)
    """
    scores: dict[str, object] = {}
    numeric_centers = profile_data.get("numeric_centers", {})
    numeric_thresholds = profile_data.get("numeric_thresholds", {})
    
    # Numeric components: tempo, duration_ms, key, mode
    for dimension in ["tempo", "duration_ms", "key", "mode"]:
        if dimension in active_numeric_specs:
            value = candidate_attrs.get(dimension)
            center = numeric_centers.get(dimension)
            threshold = numeric_thresholds.get(dimension, 1.0)
            circular = active_numeric_specs[dimension].get("circular", False)
            
            similarity = numeric_similarity(float(value) if value is not None else None, 
                                           float(center) if center is not None else 0.0, 
                                           float(threshold), 
                                           circular)
            scores[f"{dimension}_similarity"] = similarity
            scores[f"{dimension}_contribution"] = similarity
        else:
            scores[f"{dimension}_similarity"] = 0.0
            scores[f"{dimension}_contribution"] = 0.0
    
    # Lead genre: direct match vs profile lead genre
    candidate_lead_genre = candidate_attrs.get("lead_genre", "").lower()
    profile_lead_genre = profile_data.get("lead_genre", "").lower()
    lead_genre_similarity = 1.0 if candidate_lead_genre == profile_lead_genre else 0.0
    scores["lead_genre_similarity"] = lead_genre_similarity
    scores["lead_genre_contribution"] = lead_genre_similarity
    
    # Genre overlap: weighted Jaccard similarity
    candidate_genres = candidate_attrs.get("genres", [])
    genre_weights = profile_data.get("genre_weights", {})
    genre_overlap_similarity = weighted_overlap(candidate_genres, genre_weights)
    scores["genre_overlap_similarity"] = genre_overlap_similarity
    scores["genre_overlap_contribution"] = genre_overlap_similarity
    
    # Tag overlap: weighted Jaccard similarity
    candidate_tags = candidate_attrs.get("tags", [])
    tag_weights = profile_data.get("tag_weights", {})
    tag_overlap_similarity = weighted_overlap(candidate_tags, tag_weights)
    scores["tag_overlap_similarity"] = tag_overlap_similarity
    scores["tag_overlap_contribution"] = tag_overlap_similarity
    
    # Also capture matched genres/tags for output
    scores["matched_genres"] = [g for g in candidate_genres if g in genre_weights]
    scores["matched_tags"] = [t for t in candidate_tags if t in tag_weights]
    
    return scores


def compute_final_score(
    component_scores: dict[str, object],
    component_weights: dict[str, float],
) -> float:
    """
    Compute final score via weighted aggregation.
    
    Args:
        component_scores: Dict of similarity scores from compute_component_scores()
        component_weights: Dict mapping component names to their weights (should sum to 1.0)
    
    Returns:
        Final weighted score (0.0 to 1.0)
    """
    total = 0.0
    for component, weight in component_weights.items():
        # Map component name to score key (e.g., "tempo" -> "tempo_similarity")
        score_key = f"{component}_similarity"
        similarity = float(component_scores.get(score_key, 0.0))
        contribution = round(similarity * weight, 6)
        total += contribution
    
    return round(total, 6)
