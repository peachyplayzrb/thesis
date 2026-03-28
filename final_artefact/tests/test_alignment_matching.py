"""Tests for alignment.matching — normalize_text, first_artist,
build_ds001_indices, choose_best_duration_match, match_events."""
import pytest
from alignment.matching import (
    normalize_text,
    first_artist,
    build_ds001_indices,
    choose_best_duration_match,
    match_events,
)


# ---------------------------------------------------------------------------
# normalize_text
# ---------------------------------------------------------------------------
class TestNormalizeText:
    def test_strips_and_lowercases(self):
        assert normalize_text("  The Beatles  ") == "the beatles"

    def test_unicode_nfkd(self):
        assert normalize_text("Björk") == "bjork"

    def test_removes_punctuation(self):
        assert normalize_text("Rock & Roll!") == "rock roll"

    def test_collapses_whitespace(self):
        assert normalize_text("a   b   c") == "a b c"

    def test_empty_string(self):
        assert normalize_text("") == ""


# ---------------------------------------------------------------------------
# first_artist
# ---------------------------------------------------------------------------
class TestFirstArtist:
    def test_pipe_separator(self):
        assert first_artist("A | B | C") == "A"

    def test_semicolon_separator(self):
        assert first_artist("A; B") == "A"

    def test_comma_separator(self):
        assert first_artist("A, B") == "A"

    def test_no_separator(self):
        assert first_artist("Solo") == "Solo"

    def test_strips_whitespace(self):
        assert first_artist("  Artist  |  Other  ") == "Artist"

    def test_pipe_has_priority_over_comma(self):
        # pipe separator takes precedence
        assert first_artist("A, B | C") == "A, B"


# ---------------------------------------------------------------------------
# build_ds001_indices
# ---------------------------------------------------------------------------

def _make_ds001_row(spotify_id="", song="Test Song", artist="Test Artist", duration_ms="200000"):
    return {
        "spotify_id": spotify_id,
        "song": song,
        "artist": artist,
        "duration_ms": duration_ms,
    }


class TestBuildDs001Indices:
    def test_builds_spotify_id_index(self):
        rows = [_make_ds001_row(spotify_id="abc123")]
        by_id, _ = build_ds001_indices(rows)
        assert "abc123" in by_id

    def test_builds_title_artist_index(self):
        rows = [_make_ds001_row(song="Song One", artist="Artist One")]
        _, by_ta = build_ds001_indices(rows)
        key = ("song one", "artist one")
        assert key in by_ta
        assert len(by_ta[key]) == 1

    def test_row_without_spotify_id_not_in_id_index(self):
        rows = [_make_ds001_row(spotify_id="")]
        by_id, _ = build_ds001_indices(rows)
        assert len(by_id) == 0

    def test_multiple_rows_same_title_artist_grouped(self):
        rows = [
            _make_ds001_row(song="Dup", artist="X", duration_ms="100000"),
            _make_ds001_row(song="Dup", artist="X", duration_ms="200000"),
        ]
        _, by_ta = build_ds001_indices(rows)
        assert len(by_ta[("dup", "x")]) == 2


# ---------------------------------------------------------------------------
# choose_best_duration_match
# ---------------------------------------------------------------------------

def _candidate(duration_ms):
    return {"duration_ms": str(duration_ms)}


class TestChooseBestDurationMatch:
    def test_returns_first_when_no_target(self):
        candidates = [_candidate(200_000), _candidate(190_000)]
        row, delta = choose_best_duration_match(candidates, None)
        assert row == candidates[0]
        assert delta is None

    def test_picks_closest_duration(self):
        candidates = [_candidate(200_000), _candidate(190_000)]
        row, delta = choose_best_duration_match(candidates, 192_000)
        assert row == candidates[1]
        assert delta == 2_000

    def test_returns_first_on_tie(self):
        # Both equidistant — first one wins
        candidates = [_candidate(190_000), _candidate(210_000)]
        row, _ = choose_best_duration_match(candidates, 200_000)
        assert row == candidates[0]

    def test_single_candidate(self):
        candidates = [_candidate(180_000)]
        row, delta = choose_best_duration_match(candidates, 180_000)
        assert row == candidates[0]
        assert delta == 0


# ---------------------------------------------------------------------------
# match_events
# ---------------------------------------------------------------------------

def _event(spotify_track_id="", track_name="", artist_names="",
           duration_ms="", source_type="saved_tracks", time_range="", rank="1"):
    return {
        "source_type": source_type,
        "spotify_track_id": spotify_track_id,
        "track_name": track_name,
        "artist_names": artist_names,
        "duration_ms": duration_ms,
        "time_range": time_range,
        "rank": rank,
        "playlist_position": "1",
        "source_row_index": "1",
        "isrc": "",
        "event_time": "",
        "playlist_id": "",
        "playlist_name": "",
    }


TOP_RANGE_WEIGHTS = {"short_term": 0.5, "medium_term": 0.3, "long_term": 0.2}
SOURCE_BASE_WEIGHTS = {"top_tracks": 1.0, "saved_tracks": 0.6, "playlist_items": 0.4, "recently_played": 0.5}


class TestMatchEvents:
    def test_empty_indices_all_unmatched(self):
        events = [_event(spotify_track_id="abc", track_name="T", artist_names="A")]
        trace, matched, unmatched, counts = match_events(
            events, {}, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
        )
        assert counts["unmatched"] == 1
        assert counts["matched_by_spotify_id"] == 0
        assert counts["matched_by_metadata"] == 0
        assert len(matched) == 0
        assert len(unmatched) == 1

    def test_matched_by_spotify_id(self):
        ds_row = _make_ds001_row(spotify_id="abc", song="Song", artist="Artist")
        by_id = {"abc": ds_row}
        events = [_event(spotify_track_id="abc", track_name="Song", artist_names="Artist")]
        _, matched, _, counts = match_events(
            events, by_id, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
        )
        assert counts["matched_by_spotify_id"] == 1
        assert len(matched) == 1

    def test_matched_by_metadata(self):
        from collections import defaultdict
        ds_row = _make_ds001_row(song="A Song", artist="An Artist")
        by_ta = defaultdict(list)
        by_ta[("a song", "an artist")].append(ds_row)
        events = [_event(track_name="A Song", artist_names="An Artist")]
        _, matched, _, counts = match_events(
            events, {}, by_ta, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
        )
        assert counts["matched_by_metadata"] == 1
        assert len(matched) == 1

    def test_unmatched_missing_keys(self):
        """Event with no spotify_id and no track_name → missing_keys bucket."""
        events = [_event()]  # all fields empty
        _, _, unmatched, counts = match_events(
            events, {}, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
        )
        assert counts["unmatched_missing_keys"] == 1

    def test_unmatched_no_candidate(self):
        """Event has metadata keys but nothing in the index."""
        events = [_event(track_name="No Match", artist_names="Unknown")]
        _, _, unmatched, counts = match_events(
            events, {}, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
        )
        assert counts["unmatched_no_candidate"] == 1
