from __future__ import annotations

import json
import os

from alignment.constants import (
    DEFAULT_TOP_TIME_RANGES,
    SOURCE_PLAYLIST_ITEMS,
    SOURCE_RECENTLY_PLAYED,
    SOURCE_SAVED_TRACKS,
    SOURCE_TOP_TRACKS,
    SOURCE_USER_CSV,
)
from alignment.models import AlignmentBehaviorControls
from shared_utils.constants import DEFAULT_INPUT_SCOPE
from shared_utils.parsing import safe_int


def resolve_bl003_runtime_scope() -> dict[str, object]:
    payload_json = os.environ.get("BL_STAGE_CONFIG_JSON", "").strip()
    input_scope_json = os.environ.get("BL003_INPUT_SCOPE_JSON", "").strip()
    default_scope = dict(DEFAULT_INPUT_SCOPE)
    diagnostics: dict[str, object] = {
        "payload_json_parse_error": False,
        "input_scope_json_parse_error": False,
    }

    if payload_json:
        try:
            payload = json.loads(payload_json)
        except (json.JSONDecodeError, TypeError, ValueError):
            payload = None
            diagnostics["payload_json_parse_error"] = True
        if isinstance(payload, dict):
            stage_controls = payload.get("controls")
            payload_controls = dict(stage_controls) if isinstance(stage_controls, dict) else dict(payload)
            input_scope_controls = payload_controls.get("input_scope_controls")
            if isinstance(input_scope_controls, dict):
                merged_scope = dict(default_scope)
                merged_scope.update({str(k): v for k, v in input_scope_controls.items()})
                return {
                    "config_source": "orchestration_payload",
                    "run_config_path": None,
                    "run_config_schema_version": str(payload.get("schema_version") or "") or None,
                    "input_scope": merged_scope,
                    "scope_resolution_diagnostics": {
                        **diagnostics,
                        "resolution_path": "orchestration_payload",
                    },
                }

    if input_scope_json:
        try:
            parsed_scope = json.loads(input_scope_json)
            if isinstance(parsed_scope, dict):
                merged_scope = dict(default_scope)
                merged_scope.update({str(k): v for k, v in parsed_scope.items()})
                return {
                    "config_source": "environment",
                    "run_config_path": None,
                    "run_config_schema_version": None,
                    "input_scope": merged_scope,
                    "scope_resolution_diagnostics": {
                        **diagnostics,
                        "resolution_path": "environment",
                    },
                }
        except (json.JSONDecodeError, TypeError, ValueError):
            diagnostics["input_scope_json_parse_error"] = True

    return {
        "config_source": "export_selection",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope": default_scope,
        "scope_resolution_diagnostics": {
            **diagnostics,
            "resolution_path": "export_selection",
        },
    }


def as_positive_int_or_none(value: object) -> int | None:
    if value is None:
        return None
    parsed = safe_int(value, 0)
    return parsed if parsed > 0 else None


def filter_top_tracks_rows(rows: list[dict[str, str]], allowed_time_ranges: set[str]) -> list[dict[str, str]]:
    if not allowed_time_ranges:
        return list(rows)
    return [
        row for row in rows
        if (row.get("time_range") or "").strip() in allowed_time_ranges
    ]


def filter_playlist_item_rows(
    rows: list[dict[str, str]],
    playlists_limit: int | None,
    items_per_playlist_limit: int | None,
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    playlist_order: list[str] = []
    playlist_seen: set[str] = set()
    counts_by_playlist: dict[str, int] = {}

    for idx, row in enumerate(rows, start=1):
        playlist_id = (row.get("playlist_id") or "").strip()
        if not playlist_id:
            playlist_id = f"__missing_playlist__{idx}"

        if playlist_id not in playlist_seen:
            if playlists_limit is not None and len(playlist_order) >= playlists_limit:
                continue
            playlist_seen.add(playlist_id)
            playlist_order.append(playlist_id)
            counts_by_playlist[playlist_id] = 0

        counts_by_playlist[playlist_id] += 1
        if items_per_playlist_limit is not None and counts_by_playlist[playlist_id] > items_per_playlist_limit:
            continue

        selected.append(row)

    return selected


def apply_input_scope_filters(
    top_rows: list[dict[str, str]],
    saved_rows: list[dict[str, str]],
    playlist_rows: list[dict[str, str]],
    recent_rows: list[dict[str, str]],
    input_scope: dict[str, object] | AlignmentBehaviorControls,
    *,
    user_csv_rows: list[dict[str, str]] | None = None,
) -> tuple[dict[str, list[dict[str, str]]], dict[str, object]]:
    scope_mapping = (
        dict(input_scope.input_scope)
        if isinstance(input_scope, AlignmentBehaviorControls)
        else dict(input_scope)
    )
    include_top_tracks = bool(scope_mapping.get("include_top_tracks", True))
    include_saved_tracks = bool(scope_mapping.get("include_saved_tracks", True))
    include_playlists = bool(scope_mapping.get("include_playlists", True))
    include_recently_played = bool(scope_mapping.get("include_recently_played", True))
    include_user_csv = bool(scope_mapping.get("include_user_csv", True))

    top_time_ranges_raw = scope_mapping.get("top_time_ranges")
    top_time_ranges = {
        str(item).strip()
        for item in (top_time_ranges_raw if isinstance(top_time_ranges_raw, list) else [])
        if str(item).strip()
    }
    if not top_time_ranges:
        top_time_ranges = set(DEFAULT_TOP_TIME_RANGES)

    saved_tracks_limit = as_positive_int_or_none(scope_mapping.get("saved_tracks_limit"))
    playlists_limit = as_positive_int_or_none(scope_mapping.get("playlists_limit"))
    playlist_items_per_playlist_limit = as_positive_int_or_none(
        scope_mapping.get("playlist_items_per_playlist_limit")
    )
    recently_played_limit = as_positive_int_or_none(scope_mapping.get("recently_played_limit"))
    user_csv_limit = as_positive_int_or_none(scope_mapping.get("user_csv_limit"))

    top_rows_selected = filter_top_tracks_rows(top_rows, top_time_ranges) if include_top_tracks else []
    saved_rows_selected = list(saved_rows[:saved_tracks_limit]) if include_saved_tracks else []
    if include_saved_tracks and saved_tracks_limit is None:
        saved_rows_selected = list(saved_rows)

    playlist_rows_selected = (
        filter_playlist_item_rows(
            playlist_rows,
            playlists_limit=playlists_limit,
            items_per_playlist_limit=playlist_items_per_playlist_limit,
        )
        if include_playlists
        else []
    )
    recent_rows_selected = list(recent_rows[:recently_played_limit]) if include_recently_played else []
    if include_recently_played and recently_played_limit is None:
        recent_rows_selected = list(recent_rows)

    _user_csv = list(user_csv_rows) if user_csv_rows is not None else []
    user_csv_rows_selected = list(_user_csv[:user_csv_limit]) if include_user_csv else []
    if include_user_csv and user_csv_limit is None:
        user_csv_rows_selected = list(_user_csv)

    selected_rows = {
        SOURCE_TOP_TRACKS: top_rows_selected,
        SOURCE_SAVED_TRACKS: saved_rows_selected,
        SOURCE_PLAYLIST_ITEMS: playlist_rows_selected,
        SOURCE_RECENTLY_PLAYED: recent_rows_selected,
        SOURCE_USER_CSV: user_csv_rows_selected,
    }
    scope_filter_stats = {
        "requested_input_scope": scope_mapping,
        "limits": {
            "saved_tracks_limit": saved_tracks_limit,
            "playlists_limit": playlists_limit,
            "playlist_items_per_playlist_limit": playlist_items_per_playlist_limit,
            "recently_played_limit": recently_played_limit,
            "user_csv_limit": user_csv_limit,
        },
        "rows_available": {
            SOURCE_TOP_TRACKS: len(top_rows),
            SOURCE_SAVED_TRACKS: len(saved_rows),
            SOURCE_PLAYLIST_ITEMS: len(playlist_rows),
            SOURCE_RECENTLY_PLAYED: len(recent_rows),
            SOURCE_USER_CSV: len(_user_csv),
        },
        "rows_selected": {
            SOURCE_TOP_TRACKS: len(top_rows_selected),
            SOURCE_SAVED_TRACKS: len(saved_rows_selected),
            SOURCE_PLAYLIST_ITEMS: len(playlist_rows_selected),
            SOURCE_RECENTLY_PLAYED: len(recent_rows_selected),
            SOURCE_USER_CSV: len(user_csv_rows_selected),
        },
    }

    return selected_rows, scope_filter_stats
