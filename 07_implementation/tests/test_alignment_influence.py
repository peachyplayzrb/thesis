"""Tests for alignment.influence — inject_influence_tracks."""
from types import SimpleNamespace

from alignment.influence import inject_influence_tracks


def _make_candidate(track_id, song="Song", artist="Artist"):
    return {
        "id": track_id,
        "spotify_id": f"sp_{track_id}",
        "song": song,
        "artist": artist,
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


def _make_behavior_controls(enabled=True, track_ids=None, weight=1.0):
    return SimpleNamespace(
        influence_controls={
        "influence_enabled": enabled,
        "influence_track_ids": track_ids or [],
        "influence_preference_weight": weight,
        }
    )


class TestInjectInfluenceTracksNoConfig:
    def test_none_path_returns_disabled_contract(self):
        contract = inject_influence_tracks([], {}, None)
        assert contract["enabled"] is False
        assert contract["new_injected_count"] == 0
        assert contract["relabelled_count"] == 0
        assert contract["track_ids"] == []
        assert contract["skipped_track_ids"] == []
        assert contract["preference_weight"] == 1.0

    def test_none_path_does_not_mutate_matched_events(self):
        events = [{"ds001_id": "1"}]
        inject_influence_tracks(events, {}, None)
        assert len(events) == 1


class TestInjectInfluenceTracksNewTrack:
    def test_new_track_appended_to_matched_events(self):
        by_ds001_id = {"track1": _make_candidate("track1")}
        matched_events = []
        behavior_controls = _make_behavior_controls(track_ids=["track1"])
        contract = inject_influence_tracks(
            matched_events,
            by_ds001_id,
            "dummy_path",
            behavior_controls=behavior_controls,
        )
        assert contract["new_injected_count"] == 1
        assert contract["relabelled_count"] == 0
        assert len(matched_events) == 1
        assert matched_events[0]["interaction_type"] == "influence"
        assert matched_events[0]["ds001_id"] == "track1"

    def test_new_track_contract_fields(self):
        by_ds001_id = {"t1": _make_candidate("t1", song="My Song")}
        behavior_controls = _make_behavior_controls(track_ids=["t1"], weight=2.0)
        matched_events = []
        contract = inject_influence_tracks(
            matched_events,
            by_ds001_id,
            "dummy_path",
            behavior_controls=behavior_controls,
        )
        assert contract["enabled"] is True
        assert contract["preference_weight"] == 2.0
        assert "t1" in contract["track_ids"]


class TestInjectInfluenceTracksExistingTrack:
    def test_existing_track_interaction_type_updated(self):
        existing_event = {"ds001_id": "track1", "interaction_type": "history"}
        matched_events = [existing_event]
        by_ds001_id = {"track1": _make_candidate("track1")}
        behavior_controls = _make_behavior_controls(track_ids=["track1"])
        contract = inject_influence_tracks(
            matched_events,
            by_ds001_id,
            "dummy_path",
            behavior_controls=behavior_controls,
        )
        assert contract["new_injected_count"] == 0
        assert contract["relabelled_count"] == 1
        # List not extended — same event updated
        assert len(matched_events) == 1
        assert matched_events[0]["interaction_type"] == "history,influence"


class TestInjectInfluenceTracksInvalidId:
    def test_unknown_track_id_goes_to_skipped(self):
        by_ds001_id = {}
        behavior_controls = _make_behavior_controls(track_ids=["nonexistent"])
        matched_events = []
        contract = inject_influence_tracks(
            matched_events,
            by_ds001_id,
            "dummy_path",
            behavior_controls=behavior_controls,
        )
        assert "nonexistent" in contract["skipped_track_ids"]
        assert contract["new_injected_count"] == 0
        assert contract["relabelled_count"] == 0
        assert len(matched_events) == 0


class TestInjectInfluenceTracksDedup:
    def test_duplicate_ids_only_injected_once(self):
        by_ds001_id = {"t1": _make_candidate("t1")}
        behavior_controls = _make_behavior_controls(track_ids=["t1", "t1"])
        matched_events = []
        contract = inject_influence_tracks(
            matched_events,
            by_ds001_id,
            "dummy_path",
            behavior_controls=behavior_controls,
        )
        assert len(matched_events) == 1
        assert contract["new_injected_count"] == 1
        assert contract["relabelled_count"] == 0


class TestInjectInfluenceTracksDisabled:
    def test_disabled_flag_means_no_injection(self):
        by_ds001_id = {"t1": _make_candidate("t1")}
        behavior_controls = _make_behavior_controls(enabled=False, track_ids=["t1"])
        matched_events = []
        contract = inject_influence_tracks(
            matched_events,
            by_ds001_id,
            "dummy_path",
            behavior_controls=behavior_controls,
        )
        assert len(matched_events) == 0
        assert contract["new_injected_count"] == 0
        assert contract["relabelled_count"] == 0
        assert contract["enabled"] is False
