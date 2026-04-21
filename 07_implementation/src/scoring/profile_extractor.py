"""
Profile data extraction for BL-006 scoring.

Parses the BL-004 profile JSON and extracts data structures
needed for candidate scoring.
"""

from typing import Any

from shared_utils.constants import DEFAULT_SCORING_COMPONENT_WEIGHTS, NUMERIC_FEATURE_SPECS


def _clamp_0_1(value: float) -> float:
    return max(0.0, min(1.0, value))


def _build_weight_map(items: list[dict[str, Any]]) -> dict[str, float]:
    labels: list[str] = []
    weighted_entries: list[tuple[str, float]] = []
    for item in items:
        label = item.get("label")
        if not isinstance(label, str) or not label:
            continue
        labels.append(label)
        raw_weight = item.get("weight")
        if isinstance(raw_weight, (int, float)) and float(raw_weight) > 0:
            weighted_entries.append((label, float(raw_weight)))

    if weighted_entries:
        # Only positively-weighted items contribute; zero/missing-weight items are
        # intentionally excluded so they do not dilute the profile.
        total = sum(weight for _, weight in weighted_entries)
        if total > 0:
            return {
                label: round(weight / total, 6)
                for label, weight in weighted_entries
            }

    # Fallback: no items carried a positive weight (weights absent or all zero).
    # Give every labeled item equal weight so the profile is still usable.
    if not labels:
        return {}
    uniform_weight = round(1.0 / len(labels), 6)
    return {label: uniform_weight for label in labels}


def extract_profile_scoring_data(
    profile: dict[str, Any],
    numeric_specs: dict[str, dict[str, Any]],
) -> dict[str, object]:
    """
    Extract and organize profile data for scoring operations.

    Processes BL-004 profile to create lightweight data structures
    suitable for repeated candidate scoring.

    Args:
        profile: Full BL-004 profile JSON
            Expected structure:
            {
                "numeric_feature_profile": {"tempo": X, "duration_ms": Y, ...},
                "semantic_profile": {
                    "top_lead_genres": [{"label": "Rock", ...}, ...],
                    "top_genres": [{"label": "Rock", ...}, ...],
                    "top_tags": [{"label": "energy", ...}, ...]
                }
            }
        numeric_specs: Numeric feature specifications (for validation)

    Returns:
        Dict with extracted scoring data:
        - "numeric_centers": dict of profile numeric values
        - "numeric_thresholds": dict of thresholds for each dimension
        - "lead_genre": primary genre from profile
        - "genre_weights": dict mapping genres to weights
        - "tag_weights": dict mapping tags to weights
    """
    scoring_data = {}

    # Extract numeric centers and thresholds.
    numeric_profile = profile.get("numeric_feature_profile", {})
    numeric_centers = {}
    numeric_thresholds = {}

    for dimension, spec in numeric_specs.items():
        if dimension in numeric_profile:
            numeric_centers[dimension] = float(numeric_profile[dimension])
            # Threshold comes from spec (e.g., NUMERIC_FEATURE_SPECS)
            numeric_thresholds[dimension] = float(spec.get("threshold", 1.0))

    scoring_data["numeric_centers"] = numeric_centers
    scoring_data["numeric_thresholds"] = numeric_thresholds

    numeric_confidence_payload = profile.get("numeric_confidence", {})
    confidence_by_feature_raw = (
        numeric_confidence_payload.get("confidence_by_feature", {})
        if isinstance(numeric_confidence_payload, dict)
        else {}
    )
    numeric_confidence_by_feature: dict[str, float] = {}
    for dimension in numeric_centers:
        raw_value = 1.0
        if isinstance(confidence_by_feature_raw, dict):
            raw_value = float(confidence_by_feature_raw.get(dimension, 1.0))
        numeric_confidence_by_feature[dimension] = round(_clamp_0_1(raw_value), 6)
    scoring_data["numeric_confidence_by_feature"] = numeric_confidence_by_feature
    if numeric_confidence_by_feature:
        scoring_data["profile_numeric_confidence_factor"] = round(
            sum(numeric_confidence_by_feature.values()) / float(len(numeric_confidence_by_feature)),
            6,
        )
    else:
        scoring_data["profile_numeric_confidence_factor"] = 1.0

    # Extract semantic profile data
    semantic_profile = profile.get("semantic_profile", {})

    # Lead-genre scoring keeps weights for the full top-lead-genre block.
    top_lead_genres = semantic_profile.get("top_lead_genres", [])
    lead_genre = top_lead_genres[0]["label"] if top_lead_genres else ""
    scoring_data["lead_genre"] = lead_genre
    lead_genre_weights = _build_weight_map(top_lead_genres)
    scoring_data["lead_genre_weights"] = lead_genre_weights

    # Genre weights: prefer BL-004 weights; fallback to uniform weights.
    top_genres = semantic_profile.get("top_genres", [])
    genre_weights = _build_weight_map(top_genres)
    scoring_data["genre_weights"] = genre_weights

    # Tag weights: prefer BL-004 weights; fallback to uniform weights.
    top_tags = semantic_profile.get("top_tags", [])
    tag_weights = _build_weight_map(top_tags)
    scoring_data["tag_weights"] = tag_weights

    signal_vector = profile.get("profile_signal_vector", {})
    top_genre_entropy = 0.5
    top_tag_entropy = 0.5
    if isinstance(signal_vector, dict):
        if "top_genre_entropy" in signal_vector:
            top_genre_entropy = _clamp_0_1(float(signal_vector.get("top_genre_entropy", 0.5)))
        if "top_tag_entropy" in signal_vector:
            top_tag_entropy = _clamp_0_1(float(signal_vector.get("top_tag_entropy", 0.5)))
    average_entropy = (top_genre_entropy + top_tag_entropy) / 2.0
    scoring_data["semantic_precision_alpha"] = round(0.2 + ((1.0 - average_entropy) * 0.4), 6)

    return scoring_data


def build_component_weights() -> dict[str, float]:
    """
    Build the component weight dict for final score aggregation.

    These weights determine how much each component contributes to the
    final ranking score. Weights should sum to 1.0 (or be normalized).

    Returns:
        Dict mapping component names to weights

        Component breakdown:
        - Numeric components (53%): tempo (20%), duration_ms (13%),
                                    key (13%), mode (9%)
        - Lead genre (17%): exact match weight
        - Genre overlap (12%): weighted jaccard similarity
        - Tag overlap (16%): weighted jaccard similarity
    """
    return {
        f"{component}_score": weight
        for component, weight in DEFAULT_SCORING_COMPONENT_WEIGHTS.items()
    }


def build_numeric_specs() -> dict[str, dict[str, object]]:
    """
    Build numeric feature specifications for scoring.

    Defines which numeric dimensions are evaluated, their thresholds,
    and whether they use circular distance calculation.

    This mirrors NUMERIC_FEATURE_SPECS from constants but is included
    here for BL-006 clarity. In production, import from shared_utils.

    Returns:
        Dict of numeric dimension specs
    """
    return {
        dimension: {
            "threshold": float(spec["threshold"]),
            "circular": bool(spec["circular"]),
        }
        for dimension, spec in NUMERIC_FEATURE_SPECS.items()
    }
