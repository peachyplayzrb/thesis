"""Tests for alignment/user_csv_schema.py — dynamic user CSV schema detection."""

from __future__ import annotations

# pyright: reportMissingImports=false

import warnings

import pytest

from alignment.user_csv_schema import normalize_user_csv_rows


# ---------------------------------------------------------------------------
# Alias resolution
# ---------------------------------------------------------------------------

class TestAliasResolution:
    def test_canonical_names_map_to_themselves(self):
        rows = [{"track_id": "sp1", "track_name": "Song", "artist_names": "Artist",
                 "album_name": "Album", "duration_ms": "200000", "added_at": "2024-01-01"}]
        norm, report = normalize_user_csv_rows(rows)
        assert report["column_map"]["track_id"] == "track_id"
        assert report["column_map"]["track_name"] == "track_name"
        assert report["column_map"]["artist_names"] == "artist_names"
        assert report["column_map"]["album_name"] == "album_name"
        assert report["column_map"]["duration_ms"] == "duration_ms"
        assert report["column_map"]["added_at"] == "added_at"

    def test_track_id_aliases(self):
        for alias in ["spotify_id", "spotify_track_id", "id"]:
            rows = [{"track_name": "T", "artist_names": "A", alias: "sp1"}]
            _, report = normalize_user_csv_rows(rows)
            assert report["column_map"]["track_id"] == alias, f"alias '{alias}' not detected"

    def test_track_name_aliases(self):
        for alias in ["title", "song", "name", "track_title"]:
            rows = [{alias: "Song", "artist_names": "Artist"}]
            _, report = normalize_user_csv_rows(rows)
            assert report["column_map"]["track_name"] == alias

    def test_artist_names_aliases(self):
        for alias in ["artist", "artists", "artist_name", "performer"]:
            rows = [{"track_name": "Song", alias: "Artist"}]
            _, report = normalize_user_csv_rows(rows)
            assert report["column_map"]["artist_names"] == alias

    def test_album_name_aliases(self):
        for alias in ["album", "album_title", "record"]:
            rows = [{"track_name": "T", "artist_names": "A", alias: "My Album"}]
            _, report = normalize_user_csv_rows(rows)
            assert report["column_map"]["album_name"] == alias

    def test_duration_aliases(self):
        for alias in ["duration", "length_ms", "duration_millis"]:
            rows = [{"track_name": "T", "artist_names": "A", alias: "200000"}]
            _, report = normalize_user_csv_rows(rows)
            assert report["column_map"]["duration_ms"] == alias

    def test_added_at_aliases(self):
        for alias in ["date", "timestamp", "listened_at", "played_at", "datetime"]:
            rows = [{"track_name": "T", "artist_names": "A", alias: "2024-01-01"}]
            _, report = normalize_user_csv_rows(rows)
            assert report["column_map"]["added_at"] == alias

    def test_alias_matching_is_case_insensitive(self):
        rows = [{"TRACK_NAME": "Song", "ARTIST_NAMES": "Artist"}]
        _, report = normalize_user_csv_rows(rows)
        assert report["column_map"]["track_name"] == "TRACK_NAME"
        assert report["column_map"]["artist_names"] == "ARTIST_NAMES"

    def test_isrc_not_in_alias_map(self):
        """isrc must NOT be a recognized alias — DS-001 has no isrc index."""
        rows = [{"track_name": "T", "artist_names": "A", "isrc": "USABC1234567"}]
        _, report = normalize_user_csv_rows(rows)
        assert "isrc" not in report["column_map"]
        assert "isrc" in report["unmapped"]


# ---------------------------------------------------------------------------
# Viability checks
# ---------------------------------------------------------------------------

class TestViability:
    def test_viable_with_track_id_only(self):
        rows = [{"spotify_id": "sp1"}]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, report = normalize_user_csv_rows(rows)
        assert report["viable"] is True

    def test_viable_with_track_name_and_artist(self):
        rows = [{"title": "Song", "artist": "Artist"}]
        _, report = normalize_user_csv_rows(rows)
        assert report["viable"] is True

    def test_not_viable_emits_warning(self):
        rows = [{"album_name": "Album only"}]
        with pytest.warns(UserWarning, match="no usable match columns"):
            _, report = normalize_user_csv_rows(rows)
        assert report["viable"] is False

    def test_not_viable_does_not_raise(self):
        rows = [{"random_column": "value"}]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            norm, report = normalize_user_csv_rows(rows)
        assert report["viable"] is False
        assert isinstance(norm, list)

    def test_track_name_without_artist_is_not_viable(self):
        rows = [{"track_name": "Song"}]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, report = normalize_user_csv_rows(rows)
        assert report["viable"] is False

    def test_album_name_alone_is_not_viable(self):
        rows = [{"album": "My Album"}]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, report = normalize_user_csv_rows(rows)
        assert report["viable"] is False


# ---------------------------------------------------------------------------
# Unmapped columns
# ---------------------------------------------------------------------------

class TestUnmappedColumns:
    def test_unrecognised_headers_appear_in_unmapped(self):
        rows = [{"track_name": "T", "artist_names": "A", "custom_col": "x", "another": "y"}]
        _, report = normalize_user_csv_rows(rows)
        assert "custom_col" in report["unmapped"]
        assert "another" in report["unmapped"]

    def test_mapped_headers_not_in_unmapped(self):
        rows = [{"track_name": "T", "artist_names": "A"}]
        _, report = normalize_user_csv_rows(rows)
        assert "track_name" not in report["unmapped"]
        assert "artist_names" not in report["unmapped"]


# ---------------------------------------------------------------------------
# Row normalisation
# ---------------------------------------------------------------------------

class TestRowNormalisation:
    def test_rows_renamed_to_internal_keys(self):
        rows = [{"title": "My Song", "artist": "My Artist", "spotify_id": "sp1"}]
        norm, _ = normalize_user_csv_rows(rows)
        assert len(norm) == 1
        row = norm[0]
        assert row["track_name"] == "My Song"
        assert row["artist_names"] == "My Artist"
        assert row["track_id"] == "sp1"

    def test_missing_fields_default_to_empty_string(self):
        rows = [{"track_name": "Song", "artist_names": "Artist"}]
        norm, _ = normalize_user_csv_rows(rows)
        row = norm[0]
        assert row["track_id"] == ""
        assert row["album_name"] == ""
        assert row["duration_ms"] == ""
        assert row["added_at"] == ""

    def test_album_name_passthrough(self):
        rows = [{"track_name": "T", "artist_names": "A", "album": "My Album"}]
        norm, _ = normalize_user_csv_rows(rows)
        assert norm[0]["album_name"] == "My Album"

    def test_whitespace_stripped_from_values(self):
        rows = [{"track_name": "  Song  ", "artist_names": "  Artist  "}]
        norm, _ = normalize_user_csv_rows(rows)
        assert norm[0]["track_name"] == "Song"
        assert norm[0]["artist_names"] == "Artist"

    def test_multiple_rows_all_normalised(self):
        rows = [
            {"title": "Song A", "artist": "Artist A"},
            {"title": "Song B", "artist": "Artist B"},
        ]
        norm, _ = normalize_user_csv_rows(rows)
        assert len(norm) == 2
        assert norm[0]["track_name"] == "Song A"
        assert norm[1]["track_name"] == "Song B"


# ---------------------------------------------------------------------------
# Empty input
# ---------------------------------------------------------------------------

class TestEmptyInput:
    def test_empty_rows_returns_empty_list_and_not_viable(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            norm, report = normalize_user_csv_rows([])
        assert norm == []
        assert report["viable"] is False
        assert report["original_headers"] == []

    def test_empty_rows_emits_warning(self):
        with pytest.warns(UserWarning, match="no rows loaded"):
            normalize_user_csv_rows([], path="test.csv")


# ---------------------------------------------------------------------------
# Schema report structure
# ---------------------------------------------------------------------------

class TestSchemaReport:
    def test_report_contains_all_expected_keys(self):
        rows = [{"track_name": "T", "artist_names": "A"}]
        _, report = normalize_user_csv_rows(rows)
        assert "original_headers" in report
        assert "column_map" in report
        assert "mapped" in report
        assert "unmapped" in report
        assert "viable" in report

    def test_mapped_list_reflects_detected_fields(self):
        rows = [{"track_name": "T", "artist_names": "A", "album_name": "ALB"}]
        _, report = normalize_user_csv_rows(rows)
        assert "track_name" in report["mapped"]
        assert "artist_names" in report["mapped"]
        assert "album_name" in report["mapped"]
        # undetected fields not in mapped
        assert "track_id" not in report["mapped"]
