"""Tests for scoring.scoring_engine helpers."""

from scoring.scoring_engine import compute_weighted_contributions
from scoring.scoring_engine import numeric_similarity
from scoring.scoring_engine import weighted_overlap
from shared_utils.genre_utils import lead_genre_token_similarity


def test_numeric_similarity_parabolic_midpoint() -> None:
    # Mid-threshold distance now uses parabolic falloff: 1 - (0.5^2) = 0.75
    assert numeric_similarity(0.6, center=0.5, threshold=0.2) == 0.75


def test_numeric_similarity_threshold_and_beyond() -> None:
    assert numeric_similarity(0.7, center=0.5, threshold=0.2) == 0.0
    assert numeric_similarity(0.9, center=0.5, threshold=0.2) == 0.0


def test_numeric_similarity_wraps_out_of_range_circular_values() -> None:
    assert numeric_similarity(13.0, center=0.0, threshold=2.0, circular=True) == 0.75


def test_weighted_overlap_uses_profile_weights() -> None:
    assert weighted_overlap(["rock"], {"rock": 0.8, "jazz": 0.2}) == 0.8


def test_weighted_contributions_uses_pre_resolved_profile_confidence_factor() -> None:
    contributions = compute_weighted_contributions(
        {"tempo_similarity": 1.0},
        {"tempo_score": 1.0},
        numeric_confidence_by_feature={"tempo": 1.0},
        profile_numeric_confidence_factor=0.75,
        profile_numeric_confidence_mode="blended",
        profile_numeric_confidence_blend_weight=0.5,
    )

    assert contributions["tempo_contribution"] == 0.75


def test_lead_genre_token_similarity_partial_and_exact() -> None:
    assert lead_genre_token_similarity("classic rock", "rock") == 0.5
    assert lead_genre_token_similarity("pop", "pop") == 1.0
    assert lead_genre_token_similarity("jazz", "rock") == 0.0
