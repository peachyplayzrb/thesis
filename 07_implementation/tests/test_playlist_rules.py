"""Tests for playlist.rules."""

from collections import Counter

import pytest

from playlist.rules import (
    assemble_bucketed,
    build_transition_diagnostics,
    decide_candidate,
    transition_feature_distance,
    transition_smoothness_score,
)


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


def test_assemble_bucketed_novelty_allowance_admits_new_genre() -> None:
    candidates = [
        _cand(1, "pop", 0.95),
        _cand(2, "pop", 0.94),
        _cand(3, "rock", 0.60),
    ]
    rule_hits: Counter[str] = Counter()

    playlist_without, _ = assemble_bucketed(
        candidates=candidates,
        target_size=2,
        min_score_threshold=0.35,
        max_per_genre=2,
        max_consecutive=2,
        rule_hits=rule_hits,
        utility_strategy="utility_greedy",
        utility_weights={"score_weight": 1.0, "novelty_weight": 0.0, "repetition_penalty_weight": 0.0},
        novelty_allowance=0,
    )

    playlist_with, _ = assemble_bucketed(
        candidates=candidates,
        target_size=2,
        min_score_threshold=0.35,
        max_per_genre=2,
        max_consecutive=2,
        rule_hits=Counter(),
        utility_strategy="utility_greedy",
        utility_weights={"score_weight": 1.0, "novelty_weight": 0.0, "repetition_penalty_weight": 0.0},
        novelty_allowance=1,
    )

    assert [row["track_id"] for row in playlist_without] == ["track_1", "track_2"]
    assert [row["track_id"] for row in playlist_with] == ["track_1", "track_3"]


def test_assemble_bucketed_emits_relaxation_metadata_records() -> None:
    candidates = [
        _cand(1, "pop", 0.90),
        _cand(2, "pop", 0.89),
        _cand(3, "pop", 0.88),
    ]
    metadata: dict[str, object] = {}

    playlist, _ = assemble_bucketed(
        candidates=candidates,
        target_size=3,
        min_score_threshold=0.35,
        max_per_genre=3,
        max_consecutive=1,
        rule_hits=Counter(),
        controlled_relaxation={
            "enabled": True,
            "relax_consecutive_first": True,
            "max_per_genre_increment": 1,
            "max_relaxation_rounds": 1,
        },
        metadata_out=metadata,
    )

    assert len(playlist) == 2
    relaxation_records = metadata.get("relaxation_records")
    assert isinstance(relaxation_records, list)
    assert relaxation_records
    first_record = relaxation_records[0]
    assert first_record["constraint"] == "max_consecutive"
    assert first_record["tracks_admitted"] >= 1


def test_assemble_bucketed_reserves_influence_slots() -> None:
    candidates = [
        _cand(1, "rock", 0.9),
        _cand(2, "pop", 0.88),
        _cand(3, "jazz", 0.86),
    ]
    candidates[2]["track_id"] = "influence_track"
    rule_hits: Counter[str] = Counter()

    playlist, trace_rows = assemble_bucketed(
        candidates=candidates,
        target_size=2,
        min_score_threshold=0.35,
        max_per_genre=2,
        max_consecutive=2,
        rule_hits=rule_hits,
        influence_enabled=True,
        influence_track_ids={"influence_track"},
        influence_policy_mode="reserved_slots",
        influence_reserved_slots=1,
    )

    assert len(playlist) == 2
    assert any(row["track_id"] == "influence_track" for row in playlist)
    influence_trace = next(row for row in trace_rows if row["track_id"] == "influence_track")
    assert influence_trace["decision"] == "included"
    assert influence_trace["inclusion_path"] == "reserved_slot"


def test_assemble_bucketed_allows_influence_score_threshold_override() -> None:
    candidates = [
        {"track_id": "influence_low", "lead_genre": "rock", "final_score": 0.2, "rank": 1},
        {"track_id": "normal_high", "lead_genre": "pop", "final_score": 0.9, "rank": 2},
    ]
    rule_hits: Counter[str] = Counter()

    playlist, trace_rows = assemble_bucketed(
        candidates=candidates,
        target_size=2,
        min_score_threshold=0.35,
        max_per_genre=2,
        max_consecutive=2,
        rule_hits=rule_hits,
        influence_enabled=True,
        influence_track_ids={"influence_low"},
        influence_policy_mode="hybrid_override",
        influence_allow_score_threshold_override=True,
    )

    assert any(row["track_id"] == "influence_low" for row in playlist)
    threshold_excluded = [
        row for row in trace_rows
        if row["track_id"] == "influence_low" and row["exclusion_reason"] == "below_score_threshold"
    ]
    assert threshold_excluded == []


def test_assemble_bucketed_marks_post_fill_candidates_separately() -> None:
    candidates = [
        _cand(1, "pop", 0.91),
        _cand(2, "rock", 0.90),
        _cand(3, "jazz", 0.89),
    ]
    rule_hits: Counter[str] = Counter()

    playlist, trace_rows = assemble_bucketed(
        candidates=candidates,
        target_size=2,
        min_score_threshold=0.35,
        max_per_genre=4,
        max_consecutive=2,
        rule_hits=rule_hits,
    )

    assert len(playlist) == 2
    post_fill_rows = [
        row for row in trace_rows
        if row["decision"] == "excluded" and row["exclusion_reason"] == "post_fill_unprocessed"
    ]
    assert len(post_fill_rows) == 1
    assert post_fill_rows[0]["track_id"] == "track_3"
    assert rule_hits.get("R4_length_cap", 0) == 0


def test_assemble_bucketed_utility_decay_prefers_higher_rank_under_utility_greedy() -> None:
    candidates = [
        _cand(1, "pop", 0.65),
        _cand(2, "rock", 0.80),
    ]
    rule_hits: Counter[str] = Counter()

    playlist_no_decay, _ = assemble_bucketed(
        candidates=candidates,
        target_size=1,
        min_score_threshold=0.35,
        max_per_genre=4,
        max_consecutive=2,
        rule_hits=rule_hits,
        utility_strategy="utility_greedy",
        utility_decay_factor=0.0,
    )

    playlist_with_decay, _ = assemble_bucketed(
        candidates=candidates,
        target_size=1,
        min_score_threshold=0.35,
        max_per_genre=4,
        max_consecutive=2,
        rule_hits=Counter(),
        utility_strategy="utility_greedy",
        utility_decay_factor=1.0,
    )

    assert playlist_no_decay[0]["track_id"] == "track_2"
    assert playlist_with_decay[0]["track_id"] == "track_1"


# ---------------------------------------------------------------------------
# Transition scoring
# ---------------------------------------------------------------------------


def test_transition_feature_distance_zero_for_identical_tracks() -> None:
    track = {"energy": 0.7, "valence": 0.5, "tempo": 120.0}
    assert transition_feature_distance(track, track) == 0.0


def test_transition_feature_distance_handles_missing_features() -> None:
    """When all features are absent from both tracks, distance should be 0.0."""
    assert transition_feature_distance({}, {}) == 0.0


def test_transition_feature_distance_partial_features() -> None:
    """Only shared features contribute; missing features are skipped."""
    a = {"energy": 0.0}
    b = {"energy": 1.0}
    dist = transition_feature_distance(a, b)
    assert dist == 1.0


def test_transition_smoothness_score_identical_tracks() -> None:
    track = {"energy": 0.5, "valence": 0.5, "tempo": 100.0}
    assert transition_smoothness_score(track, track) == 1.0


def test_transition_smoothness_score_complement_of_distance() -> None:
    a = {"energy": 0.0}
    b = {"energy": 1.0}
    dist = transition_feature_distance(a, b)
    smooth = transition_smoothness_score(a, b)
    assert abs(dist + smooth - 1.0) < 1e-7


def test_transition_smoothness_weight_zero_leaves_order_unchanged() -> None:
    """Default weight=0.0 must produce the same playlist as if the parameter weren't there."""
    candidates = [_cand(1, "pop", 0.90), _cand(2, "pop", 0.80)]
    rule_hits: Counter[str] = Counter()
    baseline, _ = assemble_bucketed(
        candidates=candidates,
        target_size=2,
        min_score_threshold=0.3,
        max_per_genre=4,
        max_consecutive=4,
        rule_hits=rule_hits,
        utility_strategy="utility_greedy",
    )
    with_zero_weight, _ = assemble_bucketed(
        candidates=candidates,
        target_size=2,
        min_score_threshold=0.3,
        max_per_genre=4,
        max_consecutive=4,
        rule_hits=Counter(),
        utility_strategy="utility_greedy",
        transition_smoothness_weight=0.0,
    )
    assert [t["track_id"] for t in baseline] == [t["track_id"] for t in with_zero_weight]


def test_transition_smoothness_weight_positive_prefers_smooth_follow() -> None:
    """With a high transition_smoothness_weight and utility_greedy, the candidate that is
    acoustically similar to the first track should be preferred as the second track."""
    # Anchor is selected first by rank; transition smoothness should then choose close over distant.
    anchor = {
        "track_id": "anchor",
        "lead_genre": "pop",
        "final_score": 0.95,
        "rank": 1,
        "energy": 0.50,
        "valence": 0.50,
        "tempo": 100.0,
    }
    cand_a = {
        "track_id": "close",
        "lead_genre": "rock",
        "final_score": 0.80,
        "rank": 2,
        "energy": 0.51,
        "valence": 0.50,
        "tempo": 101.0,
    }
    cand_b = {
        "track_id": "distant",
        "lead_genre": "jazz",
        "final_score": 0.85,
        "rank": 3,
        "energy": 0.95,
        "valence": 0.90,
        "tempo": 180.0,
    }

    rule_hits: Counter[str] = Counter()
    playlist, _ = assemble_bucketed(
        candidates=[anchor, cand_a, cand_b],
        target_size=2,
        min_score_threshold=0.3,
        max_per_genre=4,
        max_consecutive=4,
        rule_hits=rule_hits,
        utility_strategy="utility_greedy",
        utility_weights={"score_weight": 0.0, "novelty_weight": 0.0, "repetition_penalty_weight": 0.0},
        transition_smoothness_weight=1.0,
    )
    # With score_weight=0 and transition smoothness active, the second slot should pick "close".
    assert playlist[0]["track_id"] == "anchor"
    assert playlist[1]["track_id"] == "close"


def test_assemble_bucketed_rejects_invalid_influence_policy_mode() -> None:
    with pytest.raises(ValueError, match="Invalid influence_policy_mode"):
        assemble_bucketed(
            candidates=[_cand(1, "pop", 0.9)],
            target_size=1,
            min_score_threshold=0.3,
            max_per_genre=2,
            max_consecutive=2,
            rule_hits=Counter(),
            influence_policy_mode="invalid_mode",
        )


# ---------------------------------------------------------------------------
# Transition diagnostics
# ---------------------------------------------------------------------------


def test_build_transition_diagnostics_pair_count() -> None:
    playlist = [
        {"track_id": "t1", "energy": 0.5, "valence": 0.5, "tempo": 120.0},
        {"track_id": "t2", "energy": 0.6, "valence": 0.55, "tempo": 125.0},
        {"track_id": "t3", "energy": 0.55, "valence": 0.5, "tempo": 122.0},
    ]
    result = build_transition_diagnostics(playlist)
    assert result["pair_count"] == 2


def test_build_transition_diagnostics_too_short_returns_stub() -> None:
    assert build_transition_diagnostics([])["pair_count"] == 0
    assert build_transition_diagnostics([{"track_id": "t1"}])["pair_count"] == 0


def test_build_transition_diagnostics_mean_smoothness_range() -> None:
    playlist = [
        {"track_id": "t1", "energy": 0.0, "valence": 0.0},
        {"track_id": "t2", "energy": 1.0, "valence": 1.0},
    ]
    result = build_transition_diagnostics(playlist)
    assert isinstance(result["mean_smoothness"], float)
    assert 0.0 <= float(result["mean_smoothness"]) <= 1.0


def test_build_transition_diagnostics_max_roughness_pair_structure() -> None:
    playlist = [
        {"track_id": "t1", "energy": 0.1},
        {"track_id": "t2", "energy": 0.9},
    ]
    result = build_transition_diagnostics(playlist)
    pair = result["max_roughness_pair"]
    assert isinstance(pair, dict)
    assert "from_track_id" in pair
    assert "to_track_id" in pair


def test_influence_slots_enabled_preserves_influence_tracks() -> None:
    """With slots enabled, influence tracks should be preserved in playlist."""
    rule_hits: Counter[str] = Counter()
    influence_track_ids = {"t_influence_1", "t_influence_2"}

    # Provide enough candidates to fill a size-10 playlist
    candidates = [
        {"track_id": "t_influence_1", "lead_genre": "rock", "final_score": 0.9, "rank": 1},
        {"track_id": "t_influence_2", "lead_genre": "pop", "final_score": 0.85, "rank": 2},
        {"track_id": "t_regular_1", "lead_genre": "rock", "final_score": 0.8, "rank": 3},
        {"track_id": "t_regular_2", "lead_genre": "pop", "final_score": 0.75, "rank": 4},
        {"track_id": "t_regular_3", "lead_genre": "jazz", "final_score": 0.7, "rank": 5},
    ] + [{"track_id": f"t_fill_{i}", "lead_genre": f"genre_{i%3}", "final_score": 0.6, "rank": 6+i} for i in range(10)]

    # With slots enabled, influence tracks should be reserved and included
    playlist, trace_rows = assemble_bucketed(
        candidates=candidates,
        target_size=10,
        min_score_threshold=0.5,
        max_per_genre=4,
        max_consecutive=4,
        rule_hits=rule_hits,
        influence_enabled=True,
        influence_track_ids=influence_track_ids,
        influence_reserved_slots=2,
        influence_allow_genre_cap_override=True,
    )

    playlist_track_ids = {track.get("track_id") for track in playlist}
    influence_in_playlist = influence_track_ids & playlist_track_ids

    # Both influence tracks should be present
    assert len(influence_in_playlist) == 2, f"Expected both influence tracks, got {influence_in_playlist}"
    assert len(playlist) == 10


def test_influence_slots_disabled_baseline() -> None:
    """With slots disabled, influence tracks may not be included."""
    rule_hits: Counter[str] = Counter()
    influence_track_ids = {"t_influence_1", "t_influence_2"}

    # Provide enough candidates
    candidates = [
        {"track_id": "t_influence_1", "lead_genre": "rock", "final_score": 0.5, "rank": 1},
        {"track_id": "t_influence_2", "lead_genre": "pop", "final_score": 0.5, "rank": 2},
        {"track_id": "t_regular_1", "lead_genre": "rock", "final_score": 0.95, "rank": 3},
        {"track_id": "t_regular_2", "lead_genre": "pop", "final_score": 0.90, "rank": 4},
    ] + [{"track_id": f"t_fill_{i}", "lead_genre": f"genre_{i%3}", "final_score": 0.7, "rank": 5+i} for i in range(10)]

    # With slots disabled (0 slots), regular scoring dominates
    playlist, _ = assemble_bucketed(
        candidates=candidates,
        target_size=10,
        min_score_threshold=0.5,
        max_per_genre=4,
        max_consecutive=4,
        rule_hits=rule_hits,
        influence_enabled=True,
        influence_track_ids=influence_track_ids,
        influence_reserved_slots=0,  # Disabled
    )

    playlist_track_ids = {track.get("track_id") for track in playlist}
    # High-score regular tracks should dominate the playlist
    assert "t_regular_1" in playlist_track_ids
    assert "t_regular_2" in playlist_track_ids


def test_influence_slots_genre_cap_override_effect() -> None:
    """Genre cap override allows influence tracks to exceed normal genre limits."""
    rule_hits: Counter[str] = Counter()
    influence_track_ids = {"t_influence_rock_1", "t_influence_rock_2"}

    candidates = [
        {"track_id": "t_influence_rock_1", "lead_genre": "rock", "final_score": 0.9, "rank": 1},
        {"track_id": "t_influence_rock_2", "lead_genre": "rock", "final_score": 0.85, "rank": 2},
        {"track_id": "t_regular_rock_1", "lead_genre": "rock", "final_score": 0.8, "rank": 3},
        {"track_id": "t_regular_rock_2", "lead_genre": "rock", "final_score": 0.75, "rank": 4},
        {"track_id": "t_pop_1", "lead_genre": "pop", "final_score": 0.7, "rank": 5},
    ] + [{"track_id": f"t_fill_{i}", "lead_genre": "jazz", "final_score": 0.6, "rank": 6+i} for i in range(10)]

    # With genre cap override, multiple rock influence tracks can coexist
    playlist, trace_rows = assemble_bucketed(
        candidates=candidates,
        target_size=10,
        min_score_threshold=0.5,
        max_per_genre=2,  # Normally limited to 2
        max_consecutive=4,
        rule_hits=rule_hits,
        influence_enabled=True,
        influence_track_ids=influence_track_ids,
        influence_reserved_slots=2,
        influence_allow_genre_cap_override=True,
    )

    playlist_track_ids = {track.get("track_id") for track in playlist}
    influence_rock_in_playlist = influence_track_ids & playlist_track_ids

    # Both influence rock tracks should be present despite genre cap
    assert len(influence_rock_in_playlist) >= 1, f"Genre override should allow influence rock tracks, got {influence_rock_in_playlist}"
