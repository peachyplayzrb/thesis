"""
Profile data extraction for BL-006 scoring.

Parses the BL-004 profile JSON and extracts data structures
needed for candidate scoring.
"""

from typing import Any


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
    
    # Extract numeric centers and thresholds
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
    
    # Extract semantic profile data
    semantic_profile = profile.get("semantic_profile", {})
    
    # Lead genre: first from top_lead_genres list
    top_lead_genres = semantic_profile.get("top_lead_genres", [])
    lead_genre = top_lead_genres[0]["label"] if top_lead_genres else ""
    scoring_data["lead_genre"] = lead_genre
    
    # Genre weights: convert list of dicts to weight dict
    top_genres = semantic_profile.get("top_genres", [])
    genre_weights = {item["label"]: 1.0 / len(top_genres) 
                     for item in top_genres} if top_genres else {}
    scoring_data["genre_weights"] = genre_weights
    
    # Tag weights: convert list of dicts to weight dict
    top_tags = semantic_profile.get("top_tags", [])
    tag_weights = {item["label"]: 1.0 / len(top_tags) 
                   for item in top_tags} if top_tags else {}
    scoring_data["tag_weights"] = tag_weights
    
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
        "tempo_score": 0.20,
        "duration_ms_score": 0.13,
        "key_score": 0.13,
        "mode_score": 0.09,
        "lead_genre_score": 0.17,
        "genre_overlap_score": 0.12,
        "tag_overlap_score": 0.16,
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
        "tempo": {
            "threshold": 20.0,
            "circular": False,
        },
        "key": {
            "threshold": 2.0,
            "circular": True,  # 0-11 wraps around
        },
        "mode": {
            "threshold": 0.5,
            "circular": False,
        },
        "duration_ms": {
            "threshold": 45000.0,
            "circular": False,
        },
    }
