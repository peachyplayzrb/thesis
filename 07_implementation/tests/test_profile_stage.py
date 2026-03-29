"""Tests for BL-004 profile stage OO shell."""

from __future__ import annotations

from profile.models import ProfileControls, ProfileInputs
from profile.stage import ProfileStage


def _controls(include_types: list[str] | None = None) -> ProfileControls:
    return ProfileControls(
        config_source="test",
        run_config_path=None,
        run_config_schema_version=None,
        input_scope={"spotify_sources": ["top_tracks"]},
        top_tag_limit=3,
        top_genre_limit=3,
        top_lead_genre_limit=3,
        user_id="user_1",
        include_interaction_types=include_types or ["history", "influence"],
    )


def test_circular_mean_key_handles_zero_vector() -> None:
    assert ProfileStage.circular_mean_key(0.0, 0.0) is None


def test_sorted_weight_map_is_deterministic_on_ties() -> None:
    weights = {"rock": 1.0, "jazz": 1.0, "ambient": 2.0}
    result = ProfileStage.sorted_weight_map(weights, limit=3)
    assert [row["label"] for row in result] == ["ambient", "jazz", "rock"]


def test_aggregate_inputs_respects_interaction_type_filter() -> None:
    inputs = ProfileInputs(
        seed_rows=[
            {
                "ds001_id": "track_history",
                "spotify_track_ids": "sp_hist",
                "interaction_types": "history",
                "preference_weight_sum": "0.7",
                "interaction_count_sum": "7",
                "tags": "rock,indie",
                "genres": "rock",
                "tempo": "100",
                "release": "2011",
                "key": "1",
                "artist": "A",
                "song": "S1",
            },
            {
                "ds001_id": "track_influence",
                "spotify_track_ids": "sp_inf",
                "interaction_types": "influence",
                "preference_weight_sum": "0.6",
                "interaction_count_sum": "6",
                "tags": "jazz",
                "genres": "jazz",
                "tempo": "130",
                "release": "2019",
                "key": "11",
                "artist": "B",
                "song": "S2",
            },
        ]
    )

    aggregation = ProfileStage.aggregate_inputs(inputs, _controls(include_types=["history"]))

    assert aggregation.input_row_count == 2
    assert aggregation.matched_seed_count == 1
    assert [row["track_id"] for row in aggregation.seed_trace_rows] == ["track_history"]
    assert aggregation.counts_by_type["history"] == 1
    assert aggregation.counts_by_type["influence"] == 0
    assert "release_year" in aggregation.numeric_profile
    assert round(aggregation.numeric_profile["tempo"], 3) == 100.0
