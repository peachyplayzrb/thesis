"""Tests for retrieval.candidate_evaluator."""

import pytest

from retrieval.candidate_evaluator import circular_distance_12
from retrieval.candidate_evaluator import evaluate_bl005_candidates


def _base_runtime_context() -> dict[str, object]:
    return {
        "active_numeric_specs": {},
        "seed_track_ids": set(),
        "top_lead_genres": {"rock"},
        "top_tags": {"indie"},
        "top_genres": {"rock"},
        "lead_genre_weights": {"rock": 1.0},
        "tag_weights": {"indie": 1.0},
        "genre_weights": {"rock": 1.0},
        "numeric_centers": {},
        "numeric_features_enabled": False,
        "semantic_strong_keep_score": 2,
        "semantic_min_keep_score": 1,
        "numeric_support_min_pass": 1,
        "numeric_support_min_score": 1.0,
        "lead_genre_partial_match_threshold": 0.5,
        "use_weighted_semantics": False,
        "use_continuous_numeric": False,
        "language_filter_enabled": False,
        "language_filter_codes": ["en"],
        "recency_min_release_year": None,
    }


def _candidate(track_id: str, *, genres: str = "rock", tags: str = "indie", lang: str = "en", release: str = "2020") -> dict[str, object]:
    return {
        "track_id": track_id,
        "genres": genres,
        "tags": tags,
        "lang": lang,
        "release": release,
    }


def test_seed_track_is_rejected() -> None:
    runtime_context = _base_runtime_context()
    runtime_context["seed_track_ids"] = {"seed_1"}

    tracker, decisions, kept_rows, summary = evaluate_bl005_candidates(
        candidate_rows=[_candidate("seed_1")],
        runtime_context=runtime_context,
    )

    assert len(decisions) == 1
    assert decisions[0]["decision"] == "reject"
    assert decisions[0]["decision_path"] == "reject_seed_track"
    assert kept_rows == []
    assert summary["decision_counts"]["seed_excluded"] == 1


def test_semantic_only_candidate_is_kept() -> None:
    runtime_context = _base_runtime_context()

    _, decisions, kept_rows, summary = evaluate_bl005_candidates(
        candidate_rows=[_candidate("cand_1")],
        runtime_context=runtime_context,
    )

    assert decisions[0]["decision"] == "keep"
    assert decisions[0]["decision_path"] == "keep_semantic_only"
    assert len(kept_rows) == 1
    assert summary["decision_counts"]["kept_candidates"] == 1


def test_language_filter_rejects_mismatch() -> None:
    runtime_context = _base_runtime_context()
    runtime_context["language_filter_enabled"] = True

    _, decisions, kept_rows, summary = evaluate_bl005_candidates(
        candidate_rows=[_candidate("cand_2", lang="es")],
        runtime_context=runtime_context,
    )

    assert decisions[0]["decision"] == "reject"
    assert decisions[0]["decision_path"] == "reject_language_filter"
    assert kept_rows == []
    assert summary["decision_path_counts"]["reject_language_filter"] == 1


def test_partial_lead_genre_match_counts_as_semantic_signal() -> None:
    runtime_context = _base_runtime_context()

    _, decisions, kept_rows, _ = evaluate_bl005_candidates(
        candidate_rows=[_candidate("cand_partial", genres="classic rock", tags="")],
        runtime_context=runtime_context,
    )

    assert decisions[0]["decision"] == "reject"
    assert decisions[0]["lead_genre_match"] == 1
    assert float(decisions[0]["semantic_score"]) == 0.5
    assert len(kept_rows) == 0


@pytest.mark.parametrize(
    ("candidate_key", "center_key", "expected"),
    [
        (-1.0, 0.0, 1.0),
        (13.0, 0.0, 1.0),
        (25.0, 0.0, 1.0),
        (11.0, 1.0, 2.0),
    ],
)
def test_circular_distance_12_handles_out_of_range_values(
    candidate_key: float,
    center_key: float,
    expected: float,
) -> None:
    assert circular_distance_12(candidate_key, center_key) == expected


def test_circular_distance_12_matches_existing_valid_domain_behavior() -> None:
    assert circular_distance_12(11.0, 1.0) == 2.0
    assert circular_distance_12(2.0, 10.0) == 4.0


def test_out_of_range_key_value_never_produces_negative_distance() -> None:
    runtime_context = _base_runtime_context()
    runtime_context["numeric_features_enabled"] = True
    runtime_context["active_numeric_specs"] = {
        "key": {
            "candidate_column": "key",
            "threshold": 0.5,
            "circular": True,
        }
    }
    runtime_context["numeric_centers"] = {"key": 0.0}

    candidate = _candidate("cand_key", genres="", tags="")
    candidate["key"] = "13"

    _, decisions, _, _ = evaluate_bl005_candidates(
        candidate_rows=[candidate],
        runtime_context=runtime_context,
    )

    assert decisions[0]["key_distance"] == 1.0
    assert decisions[0]["numeric_pass_count"] == 0


def test_weighted_semantics_uses_profile_weights_for_overlap_strength() -> None:
    runtime_context = _base_runtime_context()
    runtime_context["use_weighted_semantics"] = True
    runtime_context["top_genres"] = {"rock", "jazz"}
    runtime_context["genre_weights"] = {"rock": 0.8, "jazz": 0.2}
    runtime_context["top_tags"] = {"indie", "melancholic"}
    runtime_context["tag_weights"] = {"indie": 0.7, "melancholic": 0.3}

    _, decisions, _, _ = evaluate_bl005_candidates(
        candidate_rows=[_candidate("cand_weighted", genres="rock", tags="indie")],
        runtime_context=runtime_context,
    )

    assert decisions[0]["genre_overlap_score"] == 0.8
    assert decisions[0]["tag_overlap_score"] == 0.7
    assert decisions[0]["semantic_score"] == pytest.approx(2.5)


def test_continuous_numeric_support_keeps_partial_match_when_enabled() -> None:
    runtime_context = _base_runtime_context()
    runtime_context["numeric_features_enabled"] = True
    runtime_context["use_continuous_numeric"] = True
    runtime_context["numeric_support_min_pass"] = 1
    runtime_context["numeric_support_min_score"] = 1.0
    runtime_context["semantic_min_keep_score"] = 0
    runtime_context["semantic_strong_keep_score"] = 2
    runtime_context["top_lead_genres"] = set()
    runtime_context["top_tags"] = set()
    runtime_context["top_genres"] = set()
    runtime_context["active_numeric_specs"] = {
        "danceability": {
            "candidate_column": "danceability",
            "threshold": 0.2,
            "circular": False,
        },
        "energy": {
            "candidate_column": "energy",
            "threshold": 0.2,
            "circular": False,
        },
    }
    runtime_context["numeric_centers"] = {"danceability": 0.5, "energy": 0.5}

    candidate = _candidate("cand_continuous", genres="", tags="")
    candidate["danceability"] = "0.6"
    candidate["energy"] = "0.6"

    _, decisions, kept_rows, _ = evaluate_bl005_candidates(
        candidate_rows=[candidate],
        runtime_context=runtime_context,
    )

    assert decisions[0]["numeric_pass_count"] == 2
    assert decisions[0]["numeric_support_score"] == pytest.approx(1.5)
    assert decisions[0]["decision"] == "keep"
    assert len(kept_rows) == 1
