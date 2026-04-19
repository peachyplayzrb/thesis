"""Tests for playlist.reporting."""

from playlist.reporting import (
    build_assembly_detail_log,
    build_assembly_pressure_diagnostics,
    build_influence_effectiveness_diagnostics,
    build_rank_continuity_diagnostics,
    build_tradeoff_metrics_summary,
    build_undersized_diagnostics,
)


def test_build_undersized_diagnostics_flags_shortfall() -> None:
    trace_rows = [
        {"decision": "excluded", "exclusion_reason": "below_score_threshold"},
        {"decision": "included", "exclusion_reason": ""},
    ]
    diagnostics = build_undersized_diagnostics(
        target_size=10,
        playlist_size=8,
        candidates_evaluated=8,
        trace_rows=trace_rows,
    )
    assert diagnostics["is_undersized"] is True
    assert diagnostics["shortfall"] == 2
    assert diagnostics["exclusion_reason_counts"]["below_score_threshold"] == 1


def test_build_rank_continuity_diagnostics_detects_cliff() -> None:
    playlist = [
        {"score_rank": 1, "final_score": 0.95},
        {"score_rank": 2, "final_score": 0.80},
        {"score_rank": 3, "final_score": 0.60},
    ]
    diagnostics = build_rank_continuity_diagnostics(playlist)
    assert diagnostics["rank_cliff_detected"] is True
    assert diagnostics["rank_2_to_3_score_gap"] == 0.2


def test_build_assembly_pressure_diagnostics_counts_top100_exclusions() -> None:
    trace_rows = [
        {"score_rank": 10, "decision": "excluded", "exclusion_reason": "genre_cap_exceeded"},
        {"score_rank": 20, "decision": "included", "exclusion_reason": ""},
        {"score_rank": 101, "decision": "excluded", "exclusion_reason": "below_score_threshold"},
    ]
    diagnostics = build_assembly_pressure_diagnostics(trace_rows)
    assert diagnostics["top_100_considered"] == 2
    assert diagnostics["top_100_excluded"] == 1
    assert diagnostics["dominant_top_100_exclusion_reason"] == "genre_cap_exceeded"


def test_build_assembly_detail_log_links_next_included_rank() -> None:
    trace_rows = [
        {
            "score_rank": 1,
            "track_id": "t1",
            "final_score": 0.9,
            "decision": "excluded",
            "exclusion_reason": "below_score_threshold",
        },
        {
            "score_rank": 2,
            "track_id": "t2",
            "final_score": 0.85,
            "decision": "included",
            "exclusion_reason": "",
        },
    ]
    detail = build_assembly_detail_log(trace_rows)
    first_row = detail["rows"][0]
    assert first_row["track_id"] == "t1"
    assert first_row["selected_alternative_rank"] == 2


def test_build_influence_effectiveness_diagnostics_counts_paths() -> None:
    trace_rows = [
        {
            "decision": "included",
            "influence_requested": True,
            "inclusion_path": "reserved_slot",
        },
        {
            "decision": "included",
            "influence_requested": True,
            "inclusion_path": "competitive",
        },
        {
            "decision": "excluded",
            "influence_requested": True,
            "inclusion_path": "",
        },
    ]
    diagnostics = build_influence_effectiveness_diagnostics(
        trace_rows,
        influence_track_ids={"a", "b", "c"},
        candidate_track_ids={"a", "b", "x", "y"},
        policy_mode="reserved_slots",
        influence_enabled=True,
        reserved_slot_target=2,
    )

    assert diagnostics["requested_track_ids_count"] == 3
    assert diagnostics["matched_candidate_track_ids_count"] == 2
    assert diagnostics["included_track_ids_count"] == 2
    assert diagnostics["effectiveness_rate"] == 1.0
    assert diagnostics["reserved_slot_included_count"] == 1
    assert diagnostics["reserved_slot_utilization_rate"] == 0.5
    assert diagnostics["inclusion_path_counts"]["reserved_slot"] == 1
    assert diagnostics["inclusion_path_counts"]["competitive"] == 1


def test_build_tradeoff_metrics_summary_emits_expected_sections() -> None:
    playlist = [
        {"track_id": "t1", "lead_genre": "rock", "score_rank": 1},
        {"track_id": "t2", "lead_genre": "rock", "score_rank": 4},
        {"track_id": "t3", "lead_genre": "pop", "score_rank": 10},
    ]
    trace_rows = [
        {"score_rank": 2, "decision": "excluded", "exclusion_reason": "genre_cap_exceeded"},
        {"score_rank": 3, "decision": "excluded", "exclusion_reason": "genre_cap_exceeded"},
        {"score_rank": 1, "decision": "included", "exclusion_reason": ""},
    ]
    transition_diagnostics = {
        "pair_count": 2,
        "mean_smoothness": 0.7,
        "min_smoothness": 0.4,
    }

    summary = build_tradeoff_metrics_summary(
        playlist=playlist,
        trace_rows=trace_rows,
        transition_diagnostics=transition_diagnostics,
    )

    assert summary["playlist_size"] == 3
    diversity = summary["diversity_distribution_summary"]
    assert diversity["unique_genre_count"] == 2
    assert diversity["genre_counts"] == {"rock": 2, "pop": 1}

    novelty = summary["novelty_distance_summary"]
    assert novelty["transition_pair_count"] == 2
    assert novelty["mean_adjacent_transition_distance"] == 0.3
    assert novelty["max_adjacent_transition_distance"] == 0.6

    ordering = summary["ordering_pressure_summary"]
    assert ordering["median_selected_rank"] == 4
    assert ordering["selected_rank_span"] == 9
    assert ordering["dominant_top_100_exclusion_reason"] == "genre_cap_exceeded"
