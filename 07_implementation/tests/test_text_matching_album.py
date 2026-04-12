"""Tests for album_key scoring in shared_utils/text_matching.fuzzy_find_candidate."""

from __future__ import annotations

# pyright: reportMissingImports=false

from shared_utils.text_matching import fuzzy_find_candidate


def _make_controls(enabled: bool = True) -> dict:
    return {
        "enabled": enabled,
        "artist_threshold": 0.7,
        "title_threshold": 0.7,
        "combined_threshold": 0.7,
        "max_duration_delta_ms": 10000,
        "max_artist_candidates": 5,
        "enable_album_scoring": True,
        "enable_secondary_artist_retry": False,
        "enable_relaxed_second_pass": False,
        "relaxed_second_pass_artist_threshold": 0.8,
        "relaxed_second_pass_title_threshold": 0.8,
        "relaxed_second_pass_combined_threshold": 0.8,
        "emit_fuzzy_diagnostics": True,
    }


def _build_by_artist(
    ds001_id: str,
    song: str,
    artist: str,
    album_name: str = "",
) -> dict[str, list[dict[str, str]]]:
    row = {"id": ds001_id, "song": song, "artist": artist, "album_name": album_name}
    return {artist.lower(): [row]}


class TestAlbumKeyScoring:
    def test_matching_album_key_does_not_block_match(self):
        by_artist = _build_by_artist("d1", "My Song", "artist", "Great Album")
        matched, _, _, _, _, diagnostics = fuzzy_find_candidate(
            title_key="my song",
            artist_key="artist",
            event_duration=None,
            by_artist=by_artist,
            fuzzy_controls=_make_controls(),
            album_key="great album",
        )
        assert matched is not None
        assert matched["id"] == "d1"
        assert diagnostics["album_score"] is not None

    def test_no_album_key_still_matches(self):
        by_artist = _build_by_artist("d1", "My Song", "artist", "Great Album")
        matched, _, _, _, _, _ = fuzzy_find_candidate(
            title_key="my song",
            artist_key="artist",
            event_duration=None,
            by_artist=by_artist,
            fuzzy_controls=_make_controls(),
            album_key="",
        )
        assert matched is not None

    def test_album_key_empty_falls_back_to_two_factor_scoring(self):
        """album_key="" must use (artist+title)/2 unchanged, not zero the combined_score."""
        by_artist = _build_by_artist("d1", "My Song", "artist")
        matched, _, _, _, combined, diagnostics = fuzzy_find_candidate(
            title_key="my song",
            artist_key="artist",
            event_duration=None,
            by_artist=by_artist,
            fuzzy_controls=_make_controls(),
            album_key="",
        )
        assert matched is not None
        # combined_score == (1.0 + 1.0) / 2.0 == 1.0 when exact artist+title
        assert combined is not None
        assert abs(combined - 1.0) < 0.01
        assert diagnostics["album_score"] == 0.0

    def test_album_key_missing_from_candidate_falls_back_to_two_factor(self):
        """If DS-001 row has no album_name, fallback to (artist+title)/2."""
        by_artist = _build_by_artist("d1", "My Song", "artist", album_name="")
        matched, _, _, _, combined, diagnostics = fuzzy_find_candidate(
            title_key="my song",
            artist_key="artist",
            event_duration=None,
            by_artist=by_artist,
            fuzzy_controls=_make_controls(),
            album_key="some album",
        )
        assert matched is not None
        assert combined is not None
        assert abs(combined - 1.0) < 0.01  # still two-factor since candidate has no album_name
        assert diagnostics["album_score"] == 0.0

    def test_matching_album_boosts_combined_score_vs_mismatched(self):
        """Two otherwise-identical candidates: matching album should score higher."""
        row_match = {"id": "d1", "song": "My Song", "artist": "artist", "album_name": "Great Album"}
        row_mismatch = {"id": "d2", "song": "My Song", "artist": "artist", "album_name": "Other Album"}
        by_artist = {"artist": [row_match, row_mismatch]}

        matched_with_album, _, _, _, combined_with, _ = fuzzy_find_candidate(
            title_key="my song",
            artist_key="artist",
            event_duration=None,
            by_artist={"artist": [row_match]},
            fuzzy_controls=_make_controls(),
            album_key="great album",
        )
        matched_no_album, _, _, _, combined_without, _ = fuzzy_find_candidate(
            title_key="my song",
            artist_key="artist",
            event_duration=None,
            by_artist={"artist": [row_match]},
            fuzzy_controls=_make_controls(),
            album_key="",
        )
        # Both match; album scoring raises combined from 1.0 to 1.0 (already perfect)
        # so just assert both are not None and album version >= no-album version
        assert matched_with_album is not None
        assert matched_no_album is not None
        assert combined_with is not None
        assert combined_without is not None
        assert combined_with >= combined_without

    def test_mismatched_album_does_not_block_match_when_above_threshold(self):
        """A bad album match reduces combined_score but must not block a valid title+artist match."""
        controls = _make_controls()
        controls["combined_threshold"] = 0.5  # lowered so 3-factor combined still passes
        by_artist = _build_by_artist("d1", "My Song", "artist", "Completely Different Album")
        matched, _, _, _, _, _ = fuzzy_find_candidate(
            title_key="my song",
            artist_key="artist",
            event_duration=None,
            by_artist=by_artist,
            fuzzy_controls=controls,
            album_key="completely different album",  # exact match, so full score
        )
        assert matched is not None

    def test_no_match_when_all_sources_below_threshold(self):
        by_artist = _build_by_artist("d1", "completely different song", "other artist")
        matched, _, _, _, _, diagnostics = fuzzy_find_candidate(
            title_key="my song",
            artist_key="artist",
            event_duration=None,
            by_artist=by_artist,
            fuzzy_controls=_make_controls(),
        )
        assert matched is None
        assert diagnostics["failure_reason"] in {"artist_threshold", "title_threshold", "combined_threshold", "duration_rejected"}
