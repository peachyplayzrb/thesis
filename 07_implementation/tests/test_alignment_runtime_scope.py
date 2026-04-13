"""Tests for alignment.runtime_scope — resolve_bl003_runtime_scope,
filter_top_tracks_rows, filter_playlist_item_rows, as_positive_int_or_none,
apply_input_scope_filters."""
import os
import pytest
from alignment.runtime_scope import (
    resolve_bl003_runtime_scope,
    filter_top_tracks_rows,
    filter_playlist_item_rows,
    as_positive_int_or_none,
    apply_input_scope_filters,
)


# ---------------------------------------------------------------------------
# as_positive_int_or_none
# ---------------------------------------------------------------------------
class TestAsPositiveIntOrNone:
    def test_none_returns_none(self):
        assert as_positive_int_or_none(None) is None

    def test_positive_int(self):
        assert as_positive_int_or_none(5) == 5

    def test_string_positive_int(self):
        assert as_positive_int_or_none("10") == 10

    def test_zero_returns_none(self):
        assert as_positive_int_or_none(0) is None

    def test_negative_returns_none(self):
        assert as_positive_int_or_none(-1) is None

    def test_non_numeric_returns_none(self):
        assert as_positive_int_or_none("abc") is None

    def test_float_string_returns_none(self):
        assert as_positive_int_or_none("1.5") is None


# ---------------------------------------------------------------------------
# resolve_bl003_runtime_scope
# ---------------------------------------------------------------------------
class TestResolveBl003RuntimeScope:
    def test_no_env_vars_returns_export_selection(self, monkeypatch):
        monkeypatch.delenv("BL003_INPUT_SCOPE_JSON", raising=False)
        monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)
        result = resolve_bl003_runtime_scope()
        assert result["config_source"] == "export_selection"
        assert result["run_config_path"] is None

    def test_payload_scope_overrides_default(self, monkeypatch):
        monkeypatch.setenv(
            "BL_STAGE_CONFIG_JSON",
            '{"stage_id":"BL-003","schema_version":"1.0","resolved_from":"defaults","controls":{"input_scope_controls":{"include_top_tracks":false}}}',
        )
        result = resolve_bl003_runtime_scope()
        assert result["config_source"] == "orchestration_payload"
        assert result["input_scope"]["include_top_tracks"] is False

    def test_env_scope_json_overrides_default(self, monkeypatch):
        monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)
        monkeypatch.setenv("BL003_INPUT_SCOPE_JSON", '{"include_top_tracks": false}')
        result = resolve_bl003_runtime_scope()
        assert result["config_source"] == "environment"
        assert result["input_scope"]["include_top_tracks"] is False

    def test_invalid_json_falls_through_to_default(self, monkeypatch):
        monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)
        monkeypatch.setenv("BL003_INPUT_SCOPE_JSON", "not-json")
        result = resolve_bl003_runtime_scope()
        assert result["config_source"] == "export_selection"
        diagnostics = result["scope_resolution_diagnostics"]
        assert diagnostics["input_scope_json_parse_error"] is True
        assert diagnostics["resolution_path"] == "export_selection"

    def test_invalid_payload_json_records_diagnostic(self, monkeypatch):
        monkeypatch.setenv("BL_STAGE_CONFIG_JSON", "not-json")
        monkeypatch.delenv("BL003_INPUT_SCOPE_JSON", raising=False)
        result = resolve_bl003_runtime_scope()
        diagnostics = result["scope_resolution_diagnostics"]
        assert diagnostics["payload_json_parse_error"] is True
        assert diagnostics["resolution_path"] == "export_selection"


# ---------------------------------------------------------------------------
# filter_top_tracks_rows
# ---------------------------------------------------------------------------
def _top_row(time_range):
    return {"time_range": time_range}


class TestFilterTopTracksRows:
    def test_empty_set_returns_all_rows(self):
        rows = [_top_row("short_term"), _top_row("long_term")]
        assert filter_top_tracks_rows(rows, set()) == rows

    def test_filters_to_specified_ranges_only(self):
        rows = [_top_row("short_term"), _top_row("long_term"), _top_row("medium_term")]
        result = filter_top_tracks_rows(rows, {"short_term"})
        assert len(result) == 1
        assert result[0]["time_range"] == "short_term"

    def test_no_matching_range_returns_empty(self):
        rows = [_top_row("long_term")]
        assert filter_top_tracks_rows(rows, {"short_term"}) == []

    def test_multiple_allowed_ranges(self):
        rows = [_top_row("short_term"), _top_row("long_term"), _top_row("medium_term")]
        result = filter_top_tracks_rows(rows, {"short_term", "medium_term"})
        assert len(result) == 2


# ---------------------------------------------------------------------------
# filter_playlist_item_rows
# ---------------------------------------------------------------------------
def _pl_row(playlist_id, position=1):
    return {"playlist_id": playlist_id, "playlist_position": str(position)}


class TestFilterPlaylistItemRows:
    def test_no_limits_returns_all(self):
        rows = [_pl_row("pl1"), _pl_row("pl1"), _pl_row("pl2")]
        result = filter_playlist_item_rows(rows, None, None)
        assert len(result) == 3

    def test_playlists_limit_caps_number_of_playlists(self):
        rows = [_pl_row("pl1"), _pl_row("pl2"), _pl_row("pl3")]
        result = filter_playlist_item_rows(rows, playlists_limit=2, items_per_playlist_limit=None)
        playlist_ids = {r["playlist_id"] for r in result}
        assert len(playlist_ids) == 2
        assert "pl3" not in playlist_ids

    def test_items_per_playlist_limit(self):
        # 4 items from same playlist, limit 2
        rows = [_pl_row("pl1") for _ in range(4)]
        result = filter_playlist_item_rows(rows, playlists_limit=None, items_per_playlist_limit=2)
        assert len(result) == 2

    def test_combined_limits(self):
        rows = (
            [_pl_row("pl1") for _ in range(5)]
            + [_pl_row("pl2") for _ in range(5)]
            + [_pl_row("pl3") for _ in range(5)]
        )
        result = filter_playlist_item_rows(rows, playlists_limit=2, items_per_playlist_limit=3)
        playlist_ids = {r["playlist_id"] for r in result}
        assert len(playlist_ids) == 2
        assert len(result) == 6  # 2 playlists × 3 items each


# ---------------------------------------------------------------------------
# apply_input_scope_filters
# ---------------------------------------------------------------------------
class TestApplyInputScopeFilters:
    def _make_rows(self, n, source_type="saved_tracks", playlist_id="pl1"):
        if source_type == "top_tracks":
            return [{"time_range": "short_term"} for _ in range(n)]
        if source_type == "playlist_items":
            return [{"playlist_id": playlist_id} for _ in range(n)]
        return [{} for _ in range(n)]

    def test_include_flags_false_exclude_source(self):
        scope = {
            "include_top_tracks": False,
            "include_saved_tracks": True,
            "include_playlists": False,
            "include_recently_played": False,
        }
        top = self._make_rows(3, "top_tracks")
        saved = self._make_rows(5)
        selected, _ = apply_input_scope_filters(top, saved, [], [], scope)
        assert selected["top_tracks"] == []
        assert len(selected["saved_tracks"]) == 5
        assert selected["playlist_items"] == []

    def test_saved_tracks_limit_applied(self):
        scope = {"saved_tracks_limit": 3}
        saved = self._make_rows(10)
        selected, _ = apply_input_scope_filters([], saved, [], [], scope)
        assert len(selected["saved_tracks"]) == 3

    def test_scope_filter_stats_rows_available_correct(self):
        scope = {}
        saved = self._make_rows(7)
        _, stats = apply_input_scope_filters([], saved, [], [], scope)
        assert stats["rows_available"]["saved_tracks"] == 7
