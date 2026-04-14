"""Core similarity and scoring functions for BL-006 candidate ranking."""

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
    """Compute numeric similarity with a quadratic falloff inside the feature threshold."""
    if value is None:
        return 0.0

    if circular:
        diff = circular_distance_12(value, center)
    else:
        diff = abs(value - center)

    if threshold <= 0:
        return 0.0

    ratio = diff / threshold
    # Quadratic decay gives a smoother penalty curve than a hard linear cutoff.
    similarity = 1.0 - (ratio * ratio)
    return round(max(0.0, min(similarity, 1.0)), 6)


def weighted_overlap(
    candidate_set: list[str],
    profile_weights: dict[str, float],
    *,
    precision_alpha: float = 0.35,
) -> float:
    """Compute precision-aware weighted semantic overlap between candidate labels and profile weights."""
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


def compute_component_scores(
    candidate_attrs: dict[str, Any],
    profile_data: dict[str, object],
    active_numeric_specs: dict[str, dict[str, object]],
    *,
    lead_genre_strategy: str = "weighted_top_lead_genres",
    overlap_strategy: str = "precision_aware",
    semantic_precision_alpha: float | None = None,
) -> dict[str, object]:
    """Compute per-component similarities for one candidate using the active BL-006 strategies and specs."""
    scores: dict[str, object] = {}
    numeric_centers_raw = profile_data.get("numeric_centers")
    numeric_thresholds_raw = profile_data.get("numeric_thresholds")
    genre_weights_raw = profile_data.get("genre_weights")
    tag_weights_raw = profile_data.get("tag_weights")

    numeric_centers = numeric_centers_raw if isinstance(numeric_centers_raw, dict) else {}
    numeric_thresholds = numeric_thresholds_raw if isinstance(numeric_thresholds_raw, dict) else {}
    genre_weights = genre_weights_raw if isinstance(genre_weights_raw, dict) else {}
    tag_weights = tag_weights_raw if isinstance(tag_weights_raw, dict) else {}
    lead_genre_weights_raw = profile_data.get("lead_genre_weights")
    lead_genre_weights = lead_genre_weights_raw if isinstance(lead_genre_weights_raw, dict) else {}
    semantic_precision_alpha_effective = (
        _to_float(semantic_precision_alpha, 0.35)
        if semantic_precision_alpha is not None
        else _to_float(profile_data.get("semantic_precision_alpha", 0.35), 0.35)
    )

    # Numeric components are driven by active_numeric_specs so BL-006 stays aligned to shared config.
    for dimension, spec in active_numeric_specs.items():
        value = candidate_attrs.get(dimension)
        center = numeric_centers.get(dimension)
        threshold = numeric_thresholds.get(dimension, 1.0)
        circular = bool(spec.get("circular", False))

        similarity = numeric_similarity(
            float(value) if value is not None else None,
            float(center) if center is not None else 0.0,
            float(threshold),
            circular,
        )
        scores[f"{dimension}_similarity"] = similarity

    # Lead genre: weighted token overlap vs profile top lead genres (or fallback to single lead genre).
    candidate_lead_genre = str(candidate_attrs.get("lead_genre", "")).lower()
    profile_lead_genre = str(profile_data.get("lead_genre", "")).lower()
    if str(lead_genre_strategy).strip().lower() == "single_anchor":
        lead_genre_similarity = lead_genre_token_similarity(candidate_lead_genre, profile_lead_genre)
    elif lead_genre_weights:
        lead_genre_similarity = weighted_lead_genre_similarity(candidate_lead_genre, lead_genre_weights)
    else:
        lead_genre_similarity = lead_genre_token_similarity(candidate_lead_genre, profile_lead_genre)
    scores["lead_genre_similarity"] = lead_genre_similarity

    # Genre overlap uses the same weighted-overlap logic as tags for consistency.
    candidate_genres_raw = candidate_attrs.get("genres", [])
    candidate_genres = [str(value) for value in candidate_genres_raw] if isinstance(candidate_genres_raw, list) else []
    genre_overlap_similarity = weighted_overlap(
        candidate_genres,
        genre_weights,
        precision_alpha=(
            semantic_precision_alpha_effective
            if str(overlap_strategy).strip().lower() == "precision_aware"
            else 0.0
        ),
    )
    scores["genre_overlap_similarity"] = genre_overlap_similarity

    # Tag overlap mirrors genre overlap but uses tag weights.
    candidate_tags_raw = candidate_attrs.get("tags", [])
    candidate_tags = [str(value) for value in candidate_tags_raw] if isinstance(candidate_tags_raw, list) else []
    tag_overlap_similarity = weighted_overlap(
        candidate_tags,
        tag_weights,
        precision_alpha=(
            semantic_precision_alpha_effective
            if str(overlap_strategy).strip().lower() == "precision_aware"
            else 0.0
        ),
    )
    scores["tag_overlap_similarity"] = tag_overlap_similarity

    # Keep explicit matched labels for transparency payloads and diagnostics.
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
    """Compute the final BL-006 score by summing weighted component contributions."""
    contributions = (
        weighted_contributions
        if weighted_contributions is not None
        else compute_weighted_contributions(component_scores, component_weights)
    )
    total = sum(contributions.values())
    return round(total, 6)
