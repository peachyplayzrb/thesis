from __future__ import annotations

import os
from typing import Any

from alignment.constants import DEFAULT_TOP_TIME_RANGES, SOURCE_PLAYLIST_ITEMS, SOURCE_RECENTLY_PLAYED, SOURCE_SAVED_TRACKS, SOURCE_TOP_TRACKS
from alignment.models import AlignmentBehaviorControls
from shared_utils.config_loader import load_run_config_utils_module
from shared_utils.constants import DEFAULT_INPUT_SCOPE


def resolve_bl003_runtime_scope() -> dict[str, object]:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    default_scope = DEFAULT_INPUT_SCOPE

    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_input_scope_controls(run_config_path)
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "input_scope": dict(controls.get("input_scope") or default_scope),
        }

    return {
        "config_source": "defaults",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope": dict(default_scope),
    }


def as_positive_int_or_none(value: object) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
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

    selected_rows = {
        SOURCE_TOP_TRACKS: top_rows_selected,
        SOURCE_SAVED_TRACKS: saved_rows_selected,
        SOURCE_PLAYLIST_ITEMS: playlist_rows_selected,
        SOURCE_RECENTLY_PLAYED: recent_rows_selected,
    }
    scope_filter_stats = {
        "requested_input_scope": scope_mapping,
        "limits": {
            "saved_tracks_limit": saved_tracks_limit,
            "playlists_limit": playlists_limit,
            "playlist_items_per_playlist_limit": playlist_items_per_playlist_limit,
            "recently_played_limit": recently_played_limit,
        },
        "rows_available": {
            SOURCE_TOP_TRACKS: len(top_rows),
            SOURCE_SAVED_TRACKS: len(saved_rows),
            SOURCE_PLAYLIST_ITEMS: len(playlist_rows),
            SOURCE_RECENTLY_PLAYED: len(recent_rows),
        },
        "rows_selected": {
            SOURCE_TOP_TRACKS: len(top_rows_selected),
            SOURCE_SAVED_TRACKS: len(saved_rows_selected),
            SOURCE_PLAYLIST_ITEMS: len(playlist_rows_selected),
            SOURCE_RECENTLY_PLAYED: len(recent_rows_selected),
        },
    }

    return selected_rows, scope_filter_stats
