"""Tests for playlist.reporting."""

from playlist.reporting import (
    build_assembly_detail_log,
    build_assembly_pressure_diagnostics,
    build_rank_continuity_diagnostics,
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
