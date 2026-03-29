"""Tests for typed BL-003 resolved context and behavior controls."""

from __future__ import annotations

# pyright: reportMissingImports=false

from dataclasses import replace
import json

from alignment.influence import inject_influence_tracks
from alignment.match_pipeline import match_events
from alignment.models import AlignmentBehaviorControls, AlignmentStructuralContract
from alignment.resolved_context import resolve_alignment_context
from alignment.runtime_scope import apply_input_scope_filters
from alignment.weighting import compute_weight


def _behavior_controls() -> AlignmentBehaviorControls:
    return AlignmentBehaviorControls(
        input_scope={
            "include_top_tracks": False,
            "include_saved_tracks": True,
            "include_playlists": False,
            "include_recently_played": False,
            "saved_tracks_limit": 2,
        },
        top_range_weights={"short_term": 0.5, "medium_term": 0.3, "long_term": 0.2},
        source_base_weights={
            "top_tracks": 1.0,
            "saved_tracks": 0.6,
            "playlist_items": 0.4,
            "recently_played": 0.5,
        },
        decay_half_lives={"saved_tracks": 365.0, "recently_played": 90.0},
        match_rate_min_threshold=0.0,
        fuzzy_matching_controls={
            "enabled": False,
            "artist_threshold": 0.9,
            "title_threshold": 0.9,
            "combined_threshold": 0.9,
            "max_duration_delta_ms": 5000,
            "max_artist_candidates": 5,
        },
        match_strategy={
            "enable_spotify_id_match": True,
            "enable_metadata_match": True,
            "enable_fuzzy_match": True,
        },
        match_strategy_order=[
            "spotify_id_exact",
            "metadata_fallback",
            "fuzzy_title_artist",
        ],
        temporal_controls={
            "reference_mode": "system",
            "reference_now_utc": None,
        },
        aggregation_policy={
            "preference_weight_mode": "sum",
            "preference_weight_cap_per_event": None,
        },
        weighting_policy={
            "top_tracks_min_rank_floor": 0.05,
            "top_tracks_scale_multiplier": 100.0,
            "top_tracks_default_time_range_weight": 0.2,
            "playlist_items_min_position_floor": 0.05,
            "playlist_items_scale_multiplier": 20.0,
        },
        influence_controls={
            "influence_enabled": True,
            "influence_track_ids": ["track1"],
            "influence_preference_weight": 2.0,
        },
    )


def test_resolve_alignment_context_returns_typed_controls(monkeypatch) -> None:
    monkeypatch.delenv("BL003_INPUT_SCOPE_JSON", raising=False)
    monkeypatch.delenv("BL_RUN_CONFIG_PATH", raising=False)

    context = resolve_alignment_context()

    assert isinstance(context.behavior_controls, AlignmentBehaviorControls)
    assert isinstance(context.structural_contract, AlignmentStructuralContract)
    assert isinstance(context.behavior_controls.input_scope, dict)
    assert context.behavior_controls.match_strategy["enable_spotify_id_match"] is True
    assert context.behavior_controls.match_strategy_order == [
        "spotify_id_exact",
        "metadata_fallback",
        "fuzzy_title_artist",
    ]
    assert context.behavior_controls.temporal_controls["reference_mode"] == "system"
    assert context.behavior_controls.aggregation_policy["preference_weight_mode"] == "sum"
    assert context.structural_contract.output_filenames["summary_json"] == "bl003_ds001_spotify_summary.json"


def test_resolve_alignment_context_reads_validated_run_config(tmp_path, monkeypatch) -> None:
    run_config_path = tmp_path / "run_config.json"
    run_config_path.write_text(
        json.dumps(
            {
                "seed_controls": {
                    "top_range_weights": {"short_term": 0.8},
                    "match_strategy": {"enable_metadata_match": False},
                    "match_strategy_order": ["spotify_id_exact", "fuzzy_title_artist"],
                    "temporal_controls": {
                        "reference_mode": "fixed",
                        "reference_now_utc": "2026-01-15T00:00:00Z",
                    },
                    "aggregation_policy": {
                        "preference_weight_mode": "capped",
                        "preference_weight_cap_per_event": 0.5,
                    },
                    "weighting_policy": {
                        "top_tracks": {"scale_multiplier": 55.0},
                    },
                },
                "influence_tracks": {
                    "enabled": True,
                    "track_ids": ["track_a", "track_b"],
                    "preference_weight": 1.75,
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("BL003_INPUT_SCOPE_JSON", raising=False)
    monkeypatch.setenv("BL_RUN_CONFIG_PATH", str(run_config_path))

    context = resolve_alignment_context()

    assert context.behavior_controls.top_range_weights["short_term"] == 0.8
    assert context.behavior_controls.match_strategy["enable_metadata_match"] is False
    assert context.behavior_controls.match_strategy_order == ["spotify_id_exact", "fuzzy_title_artist"]
    assert context.behavior_controls.temporal_controls == {
        "reference_mode": "fixed",
        "reference_now_utc": "2026-01-15T00:00:00Z",
    }
    assert context.behavior_controls.aggregation_policy == {
        "preference_weight_mode": "capped",
        "preference_weight_cap_per_event": 0.5,
    }
    assert context.behavior_controls.weighting_policy is not None
    assert context.behavior_controls.weighting_policy["top_tracks_scale_multiplier"] == 55.0
    assert context.behavior_controls.influence_controls["influence_track_ids"] == ["track_a", "track_b"]
    assert context.behavior_controls.influence_controls["influence_preference_weight"] == 1.75


def test_apply_input_scope_filters_accepts_behavior_controls() -> None:
    controls = _behavior_controls()
    selected_rows, stats = apply_input_scope_filters(
        top_rows=[{"time_range": "short_term"}],
        saved_rows=[{}, {}, {}],
        playlist_rows=[{"playlist_id": "pl1"}],
        recent_rows=[{}],
        input_scope=controls,
    )

    assert selected_rows["top_tracks"] == []
    assert len(selected_rows["saved_tracks"]) == 2
    assert stats["requested_input_scope"]["saved_tracks_limit"] == 2


def test_compute_weight_accepts_behavior_controls() -> None:
    controls = _behavior_controls()
    weight = compute_weight(
        {"source_type": "saved_tracks", "event_time": "", "rank": "", "playlist_position": ""},
        behavior_controls=controls,
    )

    assert weight == 0.6


def test_match_events_accepts_behavior_controls() -> None:
    controls = _behavior_controls()
    events = [
        {
            "source_type": "saved_tracks",
            "spotify_track_id": "abc",
            "track_name": "Song",
            "artist_names": "Artist",
            "duration_ms": "200000",
            "time_range": "",
            "rank": "",
            "playlist_position": "",
            "source_row_index": "1",
            "isrc": "",
            "event_time": "",
            "playlist_id": "",
            "playlist_name": "",
        }
    ]
    by_id = {"abc": {"id": "track1", "spotify_id": "abc", "song": "Song", "artist": "Artist"}}

    _, matched, _, counts = match_events(
        events,
        by_id,
        {},
        {},
        behavior_controls=controls,
    )

    assert counts["matched_by_spotify_id"] == 1
    assert len(matched) == 1


def test_inject_influence_tracks_accepts_behavior_controls() -> None:
    controls = _behavior_controls()
    matched_events: list[dict[str, object]] = []
    by_ds001_id = {
        "track1": {
            "id": "track1",
            "spotify_id": "sp_track1",
            "song": "Song",
            "artist": "Artist",
            "release": "",
            "duration_ms": "200000",
            "popularity": "",
            "danceability": "",
            "energy": "",
            "key": "",
            "mode": "",
            "valence": "",
            "tempo": "",
            "genres": "",
            "tags": "",
            "lang": "",
        }
    }

    contract = inject_influence_tracks(
        matched_events,
        by_ds001_id,
        behavior_controls=controls,
    )

    assert contract["enabled"] is True
    assert contract["preference_weight"] == 2.0
    assert len(matched_events) == 1


def test_match_events_respects_disabled_metadata_strategy() -> None:
    controls = replace(
        _behavior_controls(),
        match_strategy={
            "enable_spotify_id_match": False,
            "enable_metadata_match": False,
            "enable_fuzzy_match": False,
        },
        match_strategy_order=["metadata_fallback", "spotify_id_exact", "fuzzy_title_artist"],
    )
    events = [
        {
            "source_type": "saved_tracks",
            "spotify_track_id": "",
            "track_name": "Song",
            "artist_names": "Artist",
            "duration_ms": "200000",
            "time_range": "",
            "rank": "",
            "playlist_position": "",
            "source_row_index": "1",
            "isrc": "",
            "event_time": "",
            "playlist_id": "",
            "playlist_name": "",
        }
    ]
    by_title_artist = {("song", "artist"): [{"id": "track_meta", "song": "Song", "artist": "Artist"}]}

    _, matched, _, counts = match_events(
        events,
        {},
        by_title_artist,
        {},
        behavior_controls=controls,
    )

    assert matched == []
    assert counts["matched_by_metadata"] == 0
    assert counts["unmatched_no_candidate"] == 1


def test_match_events_respects_strategy_order_with_fuzzy_first(monkeypatch) -> None:
    controls = replace(
        _behavior_controls(),
        fuzzy_matching_controls={
            "enabled": True,
            "artist_threshold": 0.9,
            "title_threshold": 0.9,
            "combined_threshold": 0.9,
            "max_duration_delta_ms": 5000,
            "max_artist_candidates": 5,
        },
        match_strategy={
            "enable_spotify_id_match": True,
            "enable_metadata_match": True,
            "enable_fuzzy_match": True,
        },
        match_strategy_order=["fuzzy_title_artist", "metadata_fallback", "spotify_id_exact"],
    )

    def _fake_fuzzy_find_candidate(**_kwargs):
        return ({"id": "track_fuzzy", "song": "Song", "artist": "Artist"}, 0, 1.0, 1.0, 1.0)

    monkeypatch.setattr("alignment.match_pipeline.fuzzy_find_candidate", _fake_fuzzy_find_candidate)

    events = [
        {
            "source_type": "saved_tracks",
            "spotify_track_id": "",
            "track_name": "Song",
            "artist_names": "Artist",
            "duration_ms": "200000",
            "time_range": "",
            "rank": "",
            "playlist_position": "",
            "source_row_index": "1",
            "isrc": "",
            "event_time": "",
            "playlist_id": "",
            "playlist_name": "",
        }
    ]
    by_title_artist = {("song", "artist"): [{"id": "track_meta", "song": "Song", "artist": "Artist"}]}

    _, matched, _, counts = match_events(
        events,
        {},
        by_title_artist,
        {"artist": []},
        behavior_controls=controls,
    )

    assert counts["matched_by_fuzzy"] == 1
    assert counts["matched_by_metadata"] == 0
    assert matched[0]["match_method"] == "fuzzy_title_artist"
    assert matched[0]["ds001_id"] == "track_fuzzy"
