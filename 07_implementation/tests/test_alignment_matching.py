"""Tests for alignment text matching and match pipeline helpers."""
import pytest
from alignment.index_builder import build_ds001_indices
from alignment.match_pipeline import match_events
from alignment.text_matching import (
    choose_best_duration_match,
    first_artist,
    fuzzy_find_candidate,
    normalize_text,
    resolve_fuzzy_controls,
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
        by_id, _, _ = build_ds001_indices(rows)
        assert "abc123" in by_id

    def test_builds_title_artist_index(self):
        rows = [_make_ds001_row(song="Song One", artist="Artist One")]
        _, by_ta, _ = build_ds001_indices(rows)
        key = ("song one", "artist one")
        assert key in by_ta
        assert len(by_ta[key]) == 1

    def test_row_without_spotify_id_not_in_id_index(self):
        rows = [_make_ds001_row(spotify_id="")]
        by_id, _, _ = build_ds001_indices(rows)
        assert len(by_id) == 0

    def test_multiple_rows_same_title_artist_grouped(self):
        rows = [
            _make_ds001_row(song="Dup", artist="X", duration_ms="100000"),
            _make_ds001_row(song="Dup", artist="X", duration_ms="200000"),
        ]
        _, by_ta, _ = build_ds001_indices(rows)
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
            events, {}, {}, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
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
            events, by_id, {}, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
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
            events, {}, by_ta, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
        )
        assert counts["matched_by_metadata"] == 1
        assert len(matched) == 1

    def test_unmatched_missing_keys(self):
        """Event with no spotify_id and no track_name → missing_keys bucket."""
        events = [_event()]  # all fields empty
        _, _, unmatched, counts = match_events(
            events, {}, {}, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
        )
        assert counts["unmatched_missing_keys"] == 1

    def test_unmatched_no_candidate(self):
        """Event has metadata keys but nothing in the index."""
        events = [_event(track_name="No Match", artist_names="Unknown")]
        _, _, unmatched, counts = match_events(
            events, {}, {}, {}, TOP_RANGE_WEIGHTS, SOURCE_BASE_WEIGHTS
        )
        assert counts["unmatched_no_candidate"] == 1


class TestFuzzyControls:
    def test_defaults_used_when_none(self):
        controls = resolve_fuzzy_controls(None)
        assert controls["enabled"] is False
        assert controls["artist_threshold"] == 0.90
        assert controls["title_threshold"] == 0.90
        assert controls["combined_threshold"] == 0.90
        assert controls["max_duration_delta_ms"] == 5000
        assert controls["max_artist_candidates"] == 5

    def test_controls_are_clamped_and_sanitized(self):
        controls = resolve_fuzzy_controls(
            {
                "enabled": 1,
                "artist_threshold": 2.5,
                "title_threshold": -1,
                "combined_threshold": "0.85",
                "max_duration_delta_ms": "-2",
                "max_artist_candidates": "0",
            }
        )
        assert controls["enabled"] is True
        assert controls["artist_threshold"] == 1.0
        assert controls["title_threshold"] == 0.0
        assert controls["combined_threshold"] == 0.85
        assert controls["max_duration_delta_ms"] == 1
        assert controls["max_artist_candidates"] == 1


class TestFuzzyFindCandidate:
    def test_threshold_boundary_at_point_nine_is_inclusive(self, monkeypatch):
        def fake_ratio(left, right):
            if left == "artist a" and right == "artist a":
                return 90.0
            if left == "song a" and right == "song a":
                return 90.0
            return 0.0

        monkeypatch.setattr("alignment.text_matching.fuzz.ratio", fake_ratio)

        by_artist = {
            "artist a": [
                {
                    "id": "id-1",
                    "song": "Song A",
                    "artist": "Artist A",
                    "duration_ms": "200000",
                }
            ]
        }
        controls = resolve_fuzzy_controls(
            {
                "enabled": True,
                "artist_threshold": 0.90,
                "title_threshold": 0.90,
                "combined_threshold": 0.90,
            }
        )
        row, delta, title_score, artist_score, combined = fuzzy_find_candidate(
            title_key="song a",
            artist_key="artist a",
            event_duration=200000,
            by_artist=by_artist,
            fuzzy_controls=controls,
        )
        assert row is not None
        assert delta == 0
        assert title_score == 0.9
        assert artist_score == 0.9
        assert combined == 0.9

    def test_duration_gate_boundary_5000_is_inclusive(self, monkeypatch):
        monkeypatch.setattr("alignment.text_matching.fuzz.ratio", lambda *_: 100.0)
        by_artist = {
            "artist a": [
                {"id": "id-pass", "song": "Song A", "artist": "Artist A", "duration_ms": "205000"},
                {"id": "id-fail", "song": "Song A", "artist": "Artist A", "duration_ms": "205001"},
            ]
        }
        controls = resolve_fuzzy_controls({"enabled": True, "max_duration_delta_ms": 5000})
        row, delta, _, _, _ = fuzzy_find_candidate(
            title_key="song a",
            artist_key="artist a",
            event_duration=200000,
            by_artist=by_artist,
            fuzzy_controls=controls,
        )
        assert row is not None
        assert row["id"] == "id-pass"
        assert delta == 5000

    def test_tie_break_prefers_lexicographically_smaller_ds001_id(self, monkeypatch):
        monkeypatch.setattr("alignment.text_matching.fuzz.ratio", lambda *_: 95.0)
        by_artist = {
            "artist a": [
                {"id": "track-z", "song": "Song A", "artist": "Artist A", "duration_ms": "200000"},
                {"id": "track-a", "song": "Song A", "artist": "Artist A", "duration_ms": "200000"},
            ]
        }
        controls = resolve_fuzzy_controls({"enabled": True})
        row, _, _, _, _ = fuzzy_find_candidate(
            title_key="song a",
            artist_key="artist a",
            event_duration=200000,
            by_artist=by_artist,
            fuzzy_controls=controls,
        )
        assert row is not None
        assert row["id"] == "track-a"


class TestExactMatchPrecedence:
    def test_spotify_exact_match_wins_over_fuzzy(self):
        exact_row = _make_ds001_row(spotify_id="exact-id", song="Exact Song", artist="Exact Artist")
        exact_row["id"] = "exact-track"
        fuzzy_row = _make_ds001_row(song="Exact Song", artist="Exact Artist")
        fuzzy_row["id"] = "fuzzy-track"

        events = [
            _event(
                spotify_track_id="exact-id",
                track_name="Exact Song",
                artist_names="Exact Artist",
                duration_ms="200000",
            )
        ]

        _, matched, _, counts = match_events(
            events,
            {"exact-id": exact_row},
            {},
            {"exact artist": [fuzzy_row]},
            TOP_RANGE_WEIGHTS,
            SOURCE_BASE_WEIGHTS,
            fuzzy_controls={"enabled": True},
        )

        assert counts["matched_by_spotify_id"] == 1
        assert counts["matched_by_fuzzy"] == 0
        assert matched[0]["match_method"] == "spotify_id_exact"
        assert matched[0]["ds001_id"] == "exact-track"
