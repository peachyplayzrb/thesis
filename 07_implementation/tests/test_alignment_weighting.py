"""Tests for alignment.weighting — compute_weight and to_event_rows."""
from datetime import datetime, timezone

import pytest
from alignment.weighting import compute_temporal_decay, compute_weight, to_event_rows

# Actual constant values from shared_utils.constants
SOURCE_BASE_WEIGHTS = {"top_tracks": 1.0, "saved_tracks": 0.6, "playlist_items": 0.4, "recently_played": 0.5}
TOP_RANGE_WEIGHTS = {"short_term": 0.5, "medium_term": 0.3, "long_term": 0.2}
FALLBACK_BASE = 0.25


def _event(source_type, **kwargs):
    base = {
        "source_type": source_type,
        "time_range": "",
        "rank": "",
        "playlist_position": "",
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# compute_weight — top_tracks
# ---------------------------------------------------------------------------
class TestComputeWeightTopTracks:
    def test_short_term_rank1(self):
        event = _event("top_tracks", time_range="short_term", rank="1")
        # base=1.0, range=0.5, rank_score=1/1=1.0 → 1.0*0.5*1.0*100 = 50.0
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == 50.0

    def test_short_term_rank2(self):
        event = _event("top_tracks", time_range="short_term", rank="2")
        # 1.0 * 0.5 * 0.5 * 100 = 25.0
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == 25.0

    def test_medium_term_rank1(self):
        event = _event("top_tracks", time_range="medium_term", rank="1")
        # 1.0 * 0.3 * 1.0 * 100 = 30.0
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == 30.0

    def test_long_term_rank1(self):
        event = _event("top_tracks", time_range="long_term", rank="1")
        # 1.0 * 0.2 * 1.0 * 100 = 20.0
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == 20.0

    def test_missing_rank_defaults_to_50(self):
        # rank defaults to 50 → rank_score = max(0.05, 1/50) = 0.02, but max floors at 0.05
        event = _event("top_tracks", time_range="short_term", rank="")
        w = compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS)
        expected = round(1.0 * 0.5 * max(0.05, 1.0 / 50) * 100.0, 6)
        assert w == expected

    def test_unknown_time_range_uses_fallback_02(self):
        event = _event("top_tracks", time_range="unknown", rank="1")
        # fallback range_weight=0.20
        expected = round(1.0 * 0.20 * 1.0 * 100.0, 6)
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == expected


# ---------------------------------------------------------------------------
# compute_weight — saved_tracks
# ---------------------------------------------------------------------------
class TestComputeWeightSavedTracks:
    def test_saved_tracks_base_times_one(self):
        event = _event("saved_tracks")
        # base=0.6 * 1.0 = 0.6
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == 0.6


# ---------------------------------------------------------------------------
# compute_weight — recently_played
# ---------------------------------------------------------------------------
class TestComputeWeightRecentlyPlayed:
    def test_recently_played_base_times_one(self):
        event = _event("recently_played")
        # base=0.5 * 1.0 = 0.5
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == 0.5

    def test_recently_played_applies_temporal_decay(self):
        event = _event("recently_played", event_time="2026-01-01T00:00:00+00:00")
        weight = compute_weight(
            event,
            TOP_RANGE_WEIGHTS,
            SOURCE_BASE_WEIGHTS,
            decay_half_lives={"recently_played": 30.0},
        )
        assert 0.0 < weight < 0.5


# ---------------------------------------------------------------------------
# compute_weight — playlist_items
# ---------------------------------------------------------------------------
class TestComputeWeightPlaylistItems:
    def test_position_1(self):
        event = _event("playlist_items", playlist_position="1")
        # base=0.4, pos=1, pos_score=1/1=1.0 → 0.4*1.0*20 = 8.0
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == 8.0

    def test_position_2(self):
        event = _event("playlist_items", playlist_position="2")
        expected = round(0.4 * max(0.05, 1.0 / 2) * 20.0, 6)
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == expected

    def test_missing_position_defaults_to_50(self):
        event = _event("playlist_items", playlist_position="")
        expected = round(0.4 * max(0.05, 1.0 / 50) * 20.0, 6)
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == expected


# ---------------------------------------------------------------------------
# compute_weight — unknown source falls back to base
# ---------------------------------------------------------------------------
class TestComputeWeightFallback:
    def test_unknown_source_returns_fallback_base(self):
        event = _event("unknown_source")
        assert compute_weight(event, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS) == FALLBACK_BASE


class TestTemporalDecay:
    def test_half_life_decay_is_around_half(self):
        now = datetime(2026, 3, 1, tzinfo=timezone.utc)
        event_time = "2026-01-30T00:00:00+00:00"
        decay = compute_temporal_decay(event_time, half_life_days=30.0, now_utc=now)
        assert pytest.approx(decay, abs=1e-2) == 0.5

    def test_invalid_event_time_returns_no_decay(self):
        decay = compute_temporal_decay("not-a-time", half_life_days=30.0)
        assert decay == 1.0

    def test_temporal_controls_fixed_reference_is_used(self):
        event_time = "2026-01-01T00:00:00+00:00"
        decay = compute_temporal_decay(
            event_time,
            half_life_days=30.0,
            temporal_controls={
                "reference_mode": "fixed",
                "reference_now_utc": "2026-01-31T00:00:00Z",
            },
        )
        assert pytest.approx(decay, abs=1e-2) == 0.5

    def test_temporal_controls_system_uses_env_fallback(self, monkeypatch):
        monkeypatch.setenv("BL_REFERENCE_NOW_UTC", "2026-01-31T00:00:00Z")
        event_time = "2026-01-01T00:00:00+00:00"
        decay = compute_temporal_decay(
            event_time,
            half_life_days=30.0,
            temporal_controls={"reference_mode": "system", "reference_now_utc": None},
        )
        assert pytest.approx(decay, abs=1e-2) == 0.5


# ---------------------------------------------------------------------------
# to_event_rows
# ---------------------------------------------------------------------------

def _raw_row(**kwargs):
    base = {
        "track_id": "id1",
        "track_name": "Test Track",
        "artist_names": "Test Artist",
        "duration_ms": "200000",
        "isrc": "",
        "time_range": "",
        "rank": "1",
        "playlist_id": "",
        "playlist_name": "",
        "playlist_position": "",
        "added_at": "2024-01-01T00:00:00",
        "played_at": "2024-02-01T00:00:00",
    }
    base.update(kwargs)
    return base


class TestToEventRows:
    def test_saved_tracks_event_time_from_added_at(self):
        rows = [_raw_row(added_at="2024-01-15")]
        events = to_event_rows("saved_tracks", rows)
        assert events[0]["event_time"] == "2024-01-15"

    def test_playlist_items_event_time_from_added_at(self):
        rows = [_raw_row(added_at="2024-03-01")]
        events = to_event_rows("playlist_items", rows)
        assert events[0]["event_time"] == "2024-03-01"

    def test_recently_played_event_time_from_played_at(self):
        rows = [_raw_row(played_at="2024-04-20")]
        events = to_event_rows("recently_played", rows)
        assert events[0]["event_time"] == "2024-04-20"

    def test_top_tracks_event_time_empty(self):
        rows = [_raw_row()]
        events = to_event_rows("top_tracks", rows)
        assert events[0]["event_time"] == ""

    def test_source_type_set_correctly(self):
        rows = [_raw_row()]
        events = to_event_rows("saved_tracks", rows)
        assert events[0]["source_type"] == "saved_tracks"

    def test_source_row_index_is_1_based(self):
        rows = [_raw_row(), _raw_row()]
        events = to_event_rows("saved_tracks", rows)
        assert events[0]["source_row_index"] == "1"
        assert events[1]["source_row_index"] == "2"

    def test_empty_rows_returns_empty_list(self):
        assert to_event_rows("saved_tracks", []) == []
