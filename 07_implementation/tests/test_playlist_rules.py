"""Tests for playlist.rules."""

from collections import Counter

from playlist.rules import assemble_bucketed, decide_candidate


def test_assemble_bucketed_r1_counts_below_threshold_candidates() -> None:
    """R1 pre-filter in assemble_bucketed counts exactly the below-threshold candidates."""
    rule_hits: Counter[str] = Counter()
    candidates = [
        {"track_id": "t1", "lead_genre": "rock", "final_score": 0.9, "rank": 1},
        {"track_id": "t2", "lead_genre": "pop", "final_score": 0.8, "rank": 2},
        {"track_id": "t3", "lead_genre": "jazz", "final_score": 0.1, "rank": 3},
        {"track_id": "t4", "lead_genre": "rock", "final_score": 0.05, "rank": 4},
    ]
    assemble_bucketed(
        candidates=candidates,
        target_size=10,
        min_score_threshold=0.35,
        max_per_genre=4,
        max_consecutive=4,
        rule_hits=rule_hits,
    )
    assert rule_hits["R1_score_threshold"] == 2


def test_decide_candidate_excludes_on_consecutive_run() -> None:
    rule_hits: Counter[str] = Counter()
    playlist = [
        {"lead_genre": "rock"},
        {"lead_genre": "rock"},
    ]
    decision, reason = decide_candidate(
        playlist=playlist,
        assembly_genre="rock",
        target_size=10,
        max_per_genre=5,
        max_consecutive=2,
        rule_hits=rule_hits,
    )
    assert decision == "excluded"
    assert reason == "consecutive_genre_run"
    assert rule_hits["R3_consecutive_run"] == 1


def test_decide_candidate_includes_when_all_rules_pass() -> None:
    rule_hits: Counter[str] = Counter()
    playlist = [
        {"lead_genre": "rock"},
        {"lead_genre": "pop"},
    ]
    decision, reason = decide_candidate(
        playlist=playlist,
        assembly_genre="jazz",
        target_size=10,
        max_per_genre=4,
        max_consecutive=2,
        rule_hits=rule_hits,
    )
    assert decision == "included"
    assert reason == ""


def _cand(rank: int, genre: str, score: float) -> dict[str, object]:
    return {
        "track_id": f"track_{rank}",
        "lead_genre": genre,
        "final_score": score,
        "rank": rank,
    }


def test_assemble_bucketed_interleaves_genres() -> None:
    candidates = [
        _cand(1, "pop", 0.9),
        _cand(2, "pop", 0.89),
        _cand(3, "pop", 0.88),
        _cand(4, "rock", 0.87),
        _cand(5, "rock", 0.86),
    ]
    rule_hits: Counter[str] = Counter()

    playlist, _ = assemble_bucketed(
        candidates=candidates,
        target_size=4,
        min_score_threshold=0.35,
        max_per_genre=4,
        max_consecutive=2,
        rule_hits=rule_hits,
    )

    assert len(playlist) == 4
    assert playlist[0]["lead_genre"] == "pop"
    assert playlist[1]["lead_genre"] == "rock"


def test_assemble_bucketed_respects_genre_cap() -> None:
    candidates = [
        _cand(1, "pop", 0.9),
        _cand(2, "pop", 0.89),
        _cand(3, "pop", 0.88),
        _cand(4, "rock", 0.87),
        _cand(5, "jazz", 0.86),
    ]
    rule_hits: Counter[str] = Counter()

    playlist, _ = assemble_bucketed(
        candidates=candidates,
        target_size=5,
        min_score_threshold=0.35,
        max_per_genre=2,
        max_consecutive=2,
        rule_hits=rule_hits,
    )

    pop_count = sum(1 for row in playlist if row["lead_genre"] == "pop")
    assert pop_count == 2


def test_assemble_bucketed_respects_consecutive_limit() -> None:
    candidates = [
        _cand(1, "pop", 0.9),
        _cand(2, "pop", 0.89),
        _cand(3, "pop", 0.88),
        _cand(4, "rock", 0.8),
        _cand(5, "rock", 0.79),
    ]
    rule_hits: Counter[str] = Counter()

    playlist, _ = assemble_bucketed(
        candidates=candidates,
        target_size=4,
        min_score_threshold=0.35,
        max_per_genre=4,
        max_consecutive=1,
        rule_hits=rule_hits,
    )

    for i in range(len(playlist) - 1):
        assert playlist[i]["lead_genre"] != playlist[i + 1]["lead_genre"]
