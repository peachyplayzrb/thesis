"""
Scoring engine for BL-006 candidate scoring.

Core similarity and scoring computation functions for comparing
candidates against the user preference profile.
"""

from typing import Any

from shared_utils.genre_utils import lead_genre_token_similarity


def _clamp_0_1(value: float) -> float:
    return max(0.0, min(1.0, value))


def circular_distance_12(value: float, center: float) -> float:
    """Return shortest non-negative distance on the 12-step key circle."""
    normalized_value = value % 12.0
    normalized_center = center % 12.0
    raw_diff = abs(normalized_value - normalized_center)
    return min(raw_diff, 12.0 - raw_diff)


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def numeric_similarity(value: float | None, center: float, threshold: float, circular: bool = False) -> float:
    """
    Compute similarity score for numeric dimensions.

    Score = max(0.0, 1.0 - (distance / threshold)^2), clamped to [0, 1].
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
        diff = circular_distance_12(value, center)
    else:
        diff = abs(value - center)

    if threshold <= 0:
        return 0.0

    ratio = diff / threshold
    similarity = 1.0 - (ratio * ratio)
    return round(max(0.0, min(similarity, 1.0)), 6)


def weighted_overlap(
    candidate_set: list[str],
    profile_weights: dict[str, float],
    *,
    precision_alpha: float = 0.35,
) -> float:
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
    unmatched_count = sum(1 for label in candidate_set if label not in profile_weights)

    denominator = total_weight + (max(0.0, precision_alpha) * float(unmatched_count))
    if denominator <= 0:
        return 0.0

    return round(_clamp_0_1(matched_weight / denominator), 6)


def weighted_lead_genre_similarity(candidate_label: str, profile_weights: dict[str, float]) -> float:
    if not candidate_label or not profile_weights:
        return 0.0
    weighted_score = sum(
        lead_genre_token_similarity(candidate_label, profile_label) * weight
        for profile_label, weight in profile_weights.items()
    )
    return round(_clamp_0_1(weighted_score), 6)


def _dict_or_empty(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _float_dict_or_empty(value: object) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}
    return {str(k): _to_float(v) for k, v in value.items()}


def _candidate_str_list(candidate_attrs: dict[str, Any], key: str) -> list[str]:
    values_raw = candidate_attrs.get(key, [])
    return [str(value) for value in values_raw] if isinstance(values_raw, list) else []


def _overlap_precision_alpha(overlap_strategy: str, effective_alpha: float) -> float:
    return effective_alpha if str(overlap_strategy).strip().lower() == "precision_aware" else 0.0


def _resolve_lead_genre_similarity(
    candidate_lead_genre: str,
    profile_lead_genre: str,
    lead_genre_weights: dict[str, float],
    *,
    lead_genre_strategy: str,
) -> float:
    if str(lead_genre_strategy).strip().lower() == "single_anchor":
        return lead_genre_token_similarity(candidate_lead_genre, profile_lead_genre)
    if lead_genre_weights:
        return weighted_lead_genre_similarity(candidate_lead_genre, lead_genre_weights)
    return lead_genre_token_similarity(candidate_lead_genre, profile_lead_genre)


def _add_numeric_similarity_scores(
    scores: dict[str, object],
    candidate_attrs: dict[str, Any],
    *,
    numeric_centers: dict[str, object],
    numeric_thresholds: dict[str, object],
    active_numeric_specs: dict[str, dict[str, object]],
) -> None:
    for dimension, spec in active_numeric_specs.items():
        value = candidate_attrs.get(dimension)
        center = numeric_centers.get(dimension)
        threshold = numeric_thresholds.get(dimension, 1.0)
        circular = bool(spec.get("circular", False))
        similarity = numeric_similarity(
            _to_float(value) if value is not None else None,
            _to_float(center, 0.0),
            _to_float(threshold, 1.0),
            circular,
        )
        scores[f"{dimension}_similarity"] = similarity


def compute_component_scores(
    candidate_attrs: dict[str, Any],
    profile_data: dict[str, object],
    active_numeric_specs: dict[str, dict[str, object]],
    *,
    lead_genre_strategy: str = "weighted_top_lead_genres",
    overlap_strategy: str = "precision_aware",
    semantic_precision_alpha: float | None = None,
) -> dict[str, object]:
    """
    Compute all 7 component scores for a candidate.

    Args:
        candidate_attrs: Parsed candidate attributes from candidate_parsed.parse_candidate_attributes()
        profile_data: Profile scoring data from profile_extractor.extract_profile_scoring_data()
        active_numeric_specs: Active numeric specs dict mapping dimensions to their thresholds

    Returns:
        Dict with raw component similarities plus semantic match traces:
        - "tempo_similarity"
        - "duration_ms_similarity"
        - "key_similarity"
        - "mode_similarity"
        - "lead_genre_similarity"
        - "genre_overlap_similarity"
        - "tag_overlap_similarity"
        - "matched_genres", "matched_tags" (for output)
    """
    scores: dict[str, object] = {}
    numeric_centers = _dict_or_empty(profile_data.get("numeric_centers"))
    numeric_thresholds = _dict_or_empty(profile_data.get("numeric_thresholds"))
    genre_weights = _float_dict_or_empty(profile_data.get("genre_weights"))
    tag_weights = _float_dict_or_empty(profile_data.get("tag_weights"))
    lead_genre_weights_raw = profile_data.get("lead_genre_weights")
    lead_genre_weights = _float_dict_or_empty(lead_genre_weights_raw)
    semantic_precision_alpha_effective = (
        _to_float(semantic_precision_alpha, 0.35)
        if semantic_precision_alpha is not None
        else _to_float(profile_data.get("semantic_precision_alpha", 0.35), 0.35)
    )

    # Numeric components are driven by active_numeric_specs so BL-006 stays aligned to shared config.
    _add_numeric_similarity_scores(
        scores,
        candidate_attrs,
        numeric_centers=numeric_centers,
        numeric_thresholds=numeric_thresholds,
        active_numeric_specs=active_numeric_specs,
    )

    # Lead genre: weighted token overlap vs profile top lead genres (or fallback to single lead genre).
    candidate_lead_genre = str(candidate_attrs.get("lead_genre", "")).lower()
    profile_lead_genre = str(profile_data.get("lead_genre", "")).lower()
    lead_genre_similarity = _resolve_lead_genre_similarity(
        candidate_lead_genre,
        profile_lead_genre,
        lead_genre_weights,
        lead_genre_strategy=lead_genre_strategy,
    )
    scores["lead_genre_similarity"] = lead_genre_similarity

    # Genre overlap: weighted Jaccard similarity
    candidate_genres = _candidate_str_list(candidate_attrs, "genres")
    genre_overlap_similarity = weighted_overlap(
        candidate_genres,
        genre_weights,
        precision_alpha=_overlap_precision_alpha(overlap_strategy, semantic_precision_alpha_effective),
    )
    scores["genre_overlap_similarity"] = genre_overlap_similarity

    # Tag overlap: weighted Jaccard similarity
    candidate_tags = _candidate_str_list(candidate_attrs, "tags")
    tag_overlap_similarity = weighted_overlap(
        candidate_tags,
        tag_weights,
        precision_alpha=_overlap_precision_alpha(overlap_strategy, semantic_precision_alpha_effective),
    )
    scores["tag_overlap_similarity"] = tag_overlap_similarity

    # Also capture matched genres/tags for output
    scores["matched_genres"] = [g for g in candidate_genres if g in genre_weights]
    scores["matched_tags"] = [t for t in candidate_tags if t in tag_weights]

    return scores


def compute_weighted_contributions(
    component_scores: dict[str, object],
    component_weights: dict[str, float],
    *,
    numeric_confidence_by_feature: dict[str, float] | None = None,
    profile_numeric_confidence_factor: float = 1.0,
    enable_numeric_confidence_scaling: bool = True,
    numeric_confidence_floor: float = 0.0,
    profile_numeric_confidence_mode: str = "direct",
    profile_numeric_confidence_blend_weight: float = 1.0,
) -> dict[str, float]:
    """Convert raw component similarities into weighted score contributions."""
    contributions: dict[str, float] = {}
    confidence_map = numeric_confidence_by_feature or {}
    profile_factor_direct = _clamp_0_1(profile_numeric_confidence_factor)
    blend_weight = _clamp_0_1(profile_numeric_confidence_blend_weight)
    if str(profile_numeric_confidence_mode).strip().lower() == "blended":
        profile_factor = (blend_weight * profile_factor_direct) + ((1.0 - blend_weight) * 1.0)
    else:
        profile_factor = profile_factor_direct
    confidence_floor = _clamp_0_1(numeric_confidence_floor)
    for component, weight in component_weights.items():
        component_name = component.removesuffix("_score")
        score_key = f"{component_name}_similarity"
        similarity = _to_float(component_scores.get(score_key, 0.0))
        confidence_multiplier = 1.0
        if enable_numeric_confidence_scaling and component_name in confidence_map:
            per_feature_confidence = _clamp_0_1(_to_float(confidence_map.get(component_name), 1.0))
            per_feature_confidence = max(confidence_floor, per_feature_confidence)
            confidence_multiplier = per_feature_confidence * profile_factor
        contributions[f"{component_name}_contribution"] = round(
            similarity * weight * confidence_multiplier,
            6,
        )
    return contributions


def compute_final_score(
    component_scores: dict[str, object],
    component_weights: dict[str, float],
    *,
    weighted_contributions: dict[str, float] | None = None,
) -> float:
    """
    Compute final score via weighted aggregation.

    Args:
        component_scores: Dict of similarity scores from compute_component_scores()
        component_weights: Dict mapping component names to their weights (should sum to 1.0)

    Returns:
        Final weighted score (0.0 to 1.0)
    """
    contributions = (
        weighted_contributions
        if weighted_contributions is not None
        else compute_weighted_contributions(component_scores, component_weights)
    )
    total = sum(contributions.values())
    return round(total, 6)
