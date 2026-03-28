"""Tests for retrieval.candidate_evaluator."""

from retrieval.candidate_evaluator import evaluate_bl005_candidates


def _base_runtime_context() -> dict[str, object]:
    return {
        "active_numeric_specs": {},
        "seed_track_ids": set(),
        "top_lead_genres": {"rock"},
        "top_tags": {"indie"},
        "top_genres": {"rock"},
        "numeric_centers": {},
        "numeric_features_enabled": False,
        "semantic_strong_keep_score": 2,
        "semantic_min_keep_score": 1,
        "numeric_support_min_pass": 1,
        "lead_genre_partial_match_threshold": 0.5,
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
