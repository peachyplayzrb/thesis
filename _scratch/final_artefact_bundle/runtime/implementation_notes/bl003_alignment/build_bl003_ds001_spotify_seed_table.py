from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.config_loader import load_run_config_utils_module
from bl000_shared_utils.hashing import canonical_json_hash as shared_canonical_json_hash
from bl000_shared_utils.io_utils import load_csv_rows, sha256_of_file as sha256_of_file_shared
from bl000_shared_utils.io_utils import open_text_write
from bl000_shared_utils.parsing import parse_int
from bl000_shared_utils.constants import (
    DEFAULT_TOP_RANGE_WEIGHTS,
    DEFAULT_SOURCE_BASE_WEIGHTS,
    DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK,
)

# Default weights; will be overridden by run_config if available
_DEFAULT_TOP_RANGE_WEIGHTS = DEFAULT_TOP_RANGE_WEIGHTS
_DEFAULT_SOURCE_BASE_WEIGHTS = DEFAULT_SOURCE_BASE_WEIGHTS
_DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK = DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK

TRACE_FIELDNAMES = [
    "source_type",
    "source_row_index",
    "spotify_track_id",
    "isrc",
    "track_name",
    "artist_names",
    "duration_ms",
    "event_time",
    "time_range",
    "rank",
    "playlist_id",
    "playlist_name",
    "playlist_position",
    "match_status",
    "match_method",
    "matched_ds001_id",
    "matched_song",
    "matched_artist",
    "duration_delta_ms",
    "reason",
    "preference_weight",
]


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}

SEED_TABLE_FIELDNAMES = [
    "ds001_id",
    "spotify_id",
    "song",
    "artist",
    "release",
    "duration_ms",
    "popularity",
    "danceability",
    "energy",
    "key",
    "mode",
    "valence",
    "tempo",
    "genres",
    "tags",
    "lang",
    "matched_event_count",
    "interaction_count_sum",
    "preference_weight_sum",
    "preference_weight_max",
    "source_types",
    "spotify_track_ids",
    "interaction_types",
]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]

    parser = argparse.ArgumentParser(
        description="BL-003 DS-001: Build Spotify-aligned seed tables with full trace logging."
    )
    parser.add_argument(
        "--ds001-candidates",
        type=Path,
        default=repo_root / "07_implementation" / "implementation_notes" / "bl000_data_layer" / "outputs" / "ds001_working_candidate_dataset.csv",
    )
    parser.add_argument(
        "--spotify-export-dir",
        type=Path,
        default=repo_root / "07_implementation" / "implementation_notes" / "bl001_bl002_ingestion" / "outputs" / "spotify_api_export",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "07_implementation" / "implementation_notes" / "bl003_alignment" / "outputs",
    )
    parser.add_argument(
        "--allow-missing-selected-sources",
        action="store_true",
        default=env_bool("BL003_ALLOW_MISSING_SELECTED_SOURCES", False),
        help="Do not fail when BL-002 selection indicates a source should exist but its flat CSV is missing.",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_bl003_runtime_scope() -> dict[str, object]:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    default_scope = {
        "source_family": "spotify_api_export",
        "include_top_tracks": True,
        "top_time_ranges": ["short_term", "medium_term", "long_term"],
        "include_saved_tracks": True,
        "saved_tracks_limit": None,
        "include_playlists": True,
        "playlists_limit": None,
        "playlist_items_per_playlist_limit": None,
        "include_recently_played": True,
        "recently_played_limit": 50,
    }

    env_scope_raw = os.environ.get("BL003_INPUT_SCOPE_JSON", "").strip()
    if env_scope_raw:
        try:
            env_scope = json.loads(env_scope_raw)
            if isinstance(env_scope, dict):
                return {
                    "config_source": "environment",
                    "run_config_path": None,
                    "run_config_schema_version": None,
                    "input_scope": dict(env_scope),
                }
        except json.JSONDecodeError:
            pass

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
        "config_source": "export_selection",
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
    input_scope: dict[str, object],
) -> tuple[dict[str, list[dict[str, str]]], dict[str, object]]:
    include_top_tracks = bool(input_scope.get("include_top_tracks", True))
    include_saved_tracks = bool(input_scope.get("include_saved_tracks", True))
    include_playlists = bool(input_scope.get("include_playlists", True))
    include_recently_played = bool(input_scope.get("include_recently_played", True))

    top_time_ranges_raw = input_scope.get("top_time_ranges")
    top_time_ranges = {
        str(item).strip()
        for item in (top_time_ranges_raw if isinstance(top_time_ranges_raw, list) else [])
        if str(item).strip()
    }
    if not top_time_ranges:
        top_time_ranges = {"short_term", "medium_term", "long_term"}

    saved_tracks_limit = as_positive_int_or_none(input_scope.get("saved_tracks_limit"))
    playlists_limit = as_positive_int_or_none(input_scope.get("playlists_limit"))
    playlist_items_per_playlist_limit = as_positive_int_or_none(
        input_scope.get("playlist_items_per_playlist_limit")
    )
    recently_played_limit = as_positive_int_or_none(input_scope.get("recently_played_limit"))

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
        "top_tracks": top_rows_selected,
        "saved_tracks": saved_rows_selected,
        "playlist_items": playlist_rows_selected,
        "recently_played": recent_rows_selected,
    }
    scope_filter_stats = {
        "requested_input_scope": input_scope,
        "limits": {
            "saved_tracks_limit": saved_tracks_limit,
            "playlists_limit": playlists_limit,
            "playlist_items_per_playlist_limit": playlist_items_per_playlist_limit,
            "recently_played_limit": recently_played_limit,
        },
        "rows_available": {
            "top_tracks": len(top_rows),
            "saved_tracks": len(saved_rows),
            "playlist_items": len(playlist_rows),
            "recently_played": len(recent_rows),
        },
        "rows_selected": {
            "top_tracks": len(top_rows_selected),
            "saved_tracks": len(saved_rows_selected),
            "playlist_items": len(playlist_rows_selected),
            "recently_played": len(recent_rows_selected),
        },
    }

    return selected_rows, scope_filter_stats


def sha256_of_file(path: Path) -> str:
    return sha256_of_file_shared(path).upper()


def canonical_json_hash(payload: object) -> str:
    return shared_canonical_json_hash(payload, uppercase=True)


def normalize_text(value: str) -> str:
    raw = unicodedata.normalize("NFKD", value)
    ascii_text = raw.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower()
    cleaned = re.sub(r"[^a-z0-9 ]", " ", lowered)
    return " ".join(cleaned.split())


def first_artist(artist_names: str) -> str:
    if "|" in artist_names:
        return artist_names.split("|", 1)[0].strip()
    if ";" in artist_names:
        return artist_names.split(";", 1)[0].strip()
    if "," in artist_names:
        return artist_names.split(",", 1)[0].strip()
    return artist_names.strip()


def load_csv(path: Path) -> list[dict[str, str]]:
    return load_csv_rows(path)


def load_optional_csv(path: Path) -> tuple[list[dict[str, str]], bool]:
    if not path.exists():
        return [], False
    return load_csv(path), True


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object | str]]) -> None:
    with open_text_write(path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_export_selection(spotify_export_dir: Path) -> dict[str, object]:
    summary_path = spotify_export_dir / "spotify_export_run_summary.json"
    if not summary_path.exists():
        return {}
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"BL-003 could not parse BL-002 export summary: {summary_path}"
        ) from exc
    selection = payload.get("selection")
    if not isinstance(selection, dict):
        raise RuntimeError(
            f"BL-003 export summary missing required selection block: {summary_path}"
        )
    return selection


def compute_weight(event: dict[str, str], top_range_weights: dict, source_base_weights: dict) -> float:
    source_type = event["source_type"]
    base = source_base_weights.get(source_type, _DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK)

    if source_type == "top_tracks":
        rank = parse_int(event.get("rank", ""))
        rank = rank if (rank is not None and rank > 0) else 50
        range_weight = top_range_weights.get(event.get("time_range", ""), 0.20)
        rank_score = max(0.05, 1.0 / rank)
        return round(base * range_weight * rank_score * 100.0, 6)

    if source_type == "saved_tracks":
        return round(base * 1.0, 6)

    if source_type == "playlist_items":
        pos = parse_int(event.get("playlist_position", ""))
        if pos is None or pos <= 0:
            pos = 50
        return round(base * max(0.05, 1.0 / pos) * 20.0, 6)

    if source_type == "recently_played":
        return round(base * 1.0, 6)

    return round(base, 6)


def to_event_rows(source_type: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []

    for idx, row in enumerate(rows, start=1):
        event = {
            "source_type": source_type,
            "source_row_index": str(idx),
            "spotify_track_id": (row.get("track_id") or "").strip(),
            "isrc": (row.get("isrc") or "").strip(),
            "track_name": (row.get("track_name") or "").strip(),
            "artist_names": (row.get("artist_names") or "").strip(),
            "duration_ms": (row.get("duration_ms") or "").strip(),
            "event_time": "",
            "time_range": (row.get("time_range") or "").strip(),
            "rank": (row.get("rank") or "").strip(),
            "playlist_id": (row.get("playlist_id") or "").strip(),
            "playlist_name": (row.get("playlist_name") or "").strip(),
            "playlist_position": (row.get("playlist_position") or "").strip(),
        }

        if source_type == "saved_tracks":
            event["event_time"] = (row.get("added_at") or "").strip()
        elif source_type == "playlist_items":
            event["event_time"] = (row.get("added_at") or "").strip()
        elif source_type == "recently_played":
            event["event_time"] = (row.get("played_at") or "").strip()

        events.append(event)

    return events


def build_ds001_indices(rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[tuple[str, str], list[dict[str, str]]]]:
    by_spotify_id: dict[str, dict[str, str]] = {}
    by_title_artist: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)

    for row in rows:
        spotify_id = (row.get("spotify_id") or "").strip()
        song = (row.get("song") or "").strip()
        artist = (row.get("artist") or "").strip()

        if spotify_id:
            by_spotify_id[spotify_id] = row

        title_key = normalize_text(song)
        artist_key = normalize_text(artist)
        if title_key and artist_key:
            by_title_artist[(title_key, artist_key)].append(row)

    for candidate_rows in by_title_artist.values():
        candidate_rows.sort(key=lambda r: (r.get("id") or ""))

    return by_spotify_id, by_title_artist


def choose_best_duration_match(candidates: list[dict[str, str]], target_duration_ms: int | None) -> tuple[dict[str, str], int | None]:
    if not candidates:
        raise ValueError("candidates must not be empty")

    if target_duration_ms is None:
        return candidates[0], None

    best_row = candidates[0]
    best_delta: int | None = None

    for row in candidates:
        candidate_duration = parse_int(row.get("duration_ms", ""))
        if candidate_duration is None:
            continue
        delta = abs(candidate_duration - target_duration_ms)
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_row = row

    if best_delta is None:
        return candidates[0], None
    return best_row, best_delta


def main() -> None:
    args = parse_args()

    t0 = time.time()
    ds001_path = args.ds001_candidates
    spotify_dir = args.spotify_export_dir
    output_dir = args.output_dir

    if not ds001_path.exists():
        raise FileNotFoundError(f"DS-001 working dataset not found: {ds001_path}")

    top_path = spotify_dir / "spotify_top_tracks_flat.csv"
    saved_path = spotify_dir / "spotify_saved_tracks_flat.csv"
    playlist_items_path = spotify_dir / "spotify_playlist_items_flat.csv"
    recently_played_path = spotify_dir / "spotify_recently_played_flat.csv"

    top_rows, top_exists = load_optional_csv(top_path)
    saved_rows, saved_exists = load_optional_csv(saved_path)
    playlist_rows, playlist_exists = load_optional_csv(playlist_items_path)
    recent_rows, recent_exists = load_optional_csv(recently_played_path)

    runtime_scope = resolve_bl003_runtime_scope()
    input_scope = dict(runtime_scope["input_scope"])

    # Load seed controls (weights, validation thresholds)
    top_range_weights = _DEFAULT_TOP_RANGE_WEIGHTS.copy()
    source_base_weights = _DEFAULT_SOURCE_BASE_WEIGHTS.copy()
    match_rate_min_threshold = 0.0
    if runtime_scope["config_source"] == "run_config" and runtime_scope.get("run_config_path"):
        _rc_utils = load_run_config_utils_module()
        seed_controls = _rc_utils.resolve_bl003_seed_controls(runtime_scope["run_config_path"])
        top_range_weights = dict(seed_controls.get("top_range_weights", _DEFAULT_TOP_RANGE_WEIGHTS))
        source_base_weights = dict(seed_controls.get("source_base_weights", _DEFAULT_SOURCE_BASE_WEIGHTS))
        match_rate_min_threshold = float(seed_controls.get("match_rate_min_threshold", 0.0))

    selected_rows, scope_filter_stats = apply_input_scope_filters(
        top_rows,
        saved_rows,
        playlist_rows,
        recent_rows,
        input_scope,
    )

    export_selection = load_export_selection(spotify_dir)
    if runtime_scope["config_source"] == "run_config":
        expected_sources = {
            "top_tracks": bool(input_scope.get("include_top_tracks", True)),
            "saved_tracks": bool(input_scope.get("include_saved_tracks", True)),
            "playlist_items": bool(input_scope.get("include_playlists", True)),
            "recently_played": bool(input_scope.get("include_recently_played", True)),
        }
    else:
        expected_sources = {
            "top_tracks": bool(export_selection.get("include_top_tracks", False)),
            "saved_tracks": bool(export_selection.get("include_saved_tracks", False)),
            "playlist_items": bool(export_selection.get("include_playlists", False)),
            "recently_played": bool(export_selection.get("include_recently_played", False)),
        }
    available_sources = {
        "top_tracks": top_exists,
        "saved_tracks": saved_exists,
        "playlist_items": playlist_exists,
        "recently_played": recent_exists,
    }
    missing_selected_sources = [
        source_name
        for source_name, expected in expected_sources.items()
        if expected and not available_sources[source_name]
    ]
    if missing_selected_sources and not args.allow_missing_selected_sources:
        missing_details = ", ".join(missing_selected_sources)
        raise RuntimeError(
            "BL-003 strict selected-source check failed. Missing required source files from BL-002 selection: "
            f"{missing_details}. Re-run BL-002 export or pass --allow-missing-selected-sources to continue."
        )

    ds001_rows = load_csv(ds001_path)
    by_spotify_id, by_title_artist = build_ds001_indices(ds001_rows)
    by_ds001_id: dict[str, dict[str, str]] = {str(row.get("id", "")).strip(): row for row in ds001_rows if row.get("id", "").strip()}

    events: list[dict[str, str]] = []
    events.extend(to_event_rows("top_tracks", selected_rows["top_tracks"]))
    events.extend(to_event_rows("saved_tracks", selected_rows["saved_tracks"]))
    events.extend(to_event_rows("playlist_items", selected_rows["playlist_items"]))
    events.extend(to_event_rows("recently_played", selected_rows["recently_played"]))

    trace_rows: list[dict[str, str]] = []
    matched_events: list[dict[str, object]] = []
    unmatched_rows: list[dict[str, str]] = []

    summary_counts = {
        "input_event_rows": len(events),
        "matched_by_spotify_id": 0,
        "matched_by_metadata": 0,
        "unmatched": 0,
        "unmatched_missing_keys": 0,
        "unmatched_no_candidate": 0,
    }

    source_stats = {
        "top_tracks": {
            "file_present": top_exists,
            "rows_available": len(top_rows),
            "rows_selected": len(selected_rows["top_tracks"]),
        },
        "saved_tracks": {
            "file_present": saved_exists,
            "rows_available": len(saved_rows),
            "rows_selected": len(selected_rows["saved_tracks"]),
        },
        "playlist_items": {
            "file_present": playlist_exists,
            "rows_available": len(playlist_rows),
            "rows_selected": len(selected_rows["playlist_items"]),
        },
        "recently_played": {
            "file_present": recent_exists,
            "rows_available": len(recent_rows),
            "rows_selected": len(selected_rows["recently_played"]),
        },
    }

    for event in events:
        spotify_track_id = event["spotify_track_id"]
        track_name = event["track_name"]
        artist_names = event["artist_names"]
        artist_primary = first_artist(artist_names)
        event_duration = parse_int(event["duration_ms"])
        weight = compute_weight(event, top_range_weights, source_base_weights)

        trace = dict(event)
        trace["match_status"] = ""
        trace["match_method"] = ""
        trace["matched_ds001_id"] = ""
        trace["matched_song"] = ""
        trace["matched_artist"] = ""
        trace["duration_delta_ms"] = ""
        trace["reason"] = ""
        trace["preference_weight"] = f"{weight:.6f}"

        matched_row: dict[str, str] | None = None
        duration_delta: int | None = None
        match_method = ""

        if spotify_track_id and spotify_track_id in by_spotify_id:
            matched_row = by_spotify_id[spotify_track_id]
            match_method = "spotify_id_exact"
            summary_counts["matched_by_spotify_id"] += 1
        else:
            title_key = normalize_text(track_name)
            artist_key = normalize_text(artist_primary)
            if title_key and artist_key:
                candidates = by_title_artist.get((title_key, artist_key), [])
                if candidates:
                    matched_row, duration_delta = choose_best_duration_match(candidates, event_duration)
                    match_method = "metadata_fallback"
                    summary_counts["matched_by_metadata"] += 1

        if matched_row is None:
            summary_counts["unmatched"] += 1
            trace["match_status"] = "unmatched"
            if not spotify_track_id and not (track_name and artist_primary):
                summary_counts["unmatched_missing_keys"] += 1
                trace["reason"] = "missing_track_id_and_metadata"
            else:
                summary_counts["unmatched_no_candidate"] += 1
                trace["reason"] = "no_ds001_candidate"
            unmatched_rows.append(trace)
            trace_rows.append(trace)
            continue

        trace["match_status"] = "matched"
        trace["match_method"] = match_method
        trace["matched_ds001_id"] = matched_row.get("id", "")
        trace["matched_song"] = matched_row.get("song", "")
        trace["matched_artist"] = matched_row.get("artist", "")
        trace["duration_delta_ms"] = "" if duration_delta is None else str(duration_delta)

        matched_event = {
            "event_id": f"ds001_align_{len(matched_events) + 1:06d}",
            "source_type": event["source_type"],
            "source_row_index": int(event["source_row_index"]),
            "source_timestamp": event["event_time"],
            "spotify_track_id": spotify_track_id,
            "spotify_isrc": event["isrc"],
            "spotify_track_name": track_name,
            "spotify_artist_names": artist_names,
            "match_method": match_method,
            "duration_delta_ms": duration_delta,
            "ds001_id": matched_row.get("id", ""),
            "ds001_spotify_id": matched_row.get("spotify_id", ""),
            "artist": matched_row.get("artist", ""),
            "song": matched_row.get("song", ""),
            "release": matched_row.get("release", ""),
            "duration_ms": matched_row.get("duration_ms", ""),
            "popularity": matched_row.get("popularity", ""),
            "danceability": matched_row.get("danceability", ""),
            "energy": matched_row.get("energy", ""),
            "key": matched_row.get("key", ""),
            "mode": matched_row.get("mode", ""),
            "valence": matched_row.get("valence", ""),
            "tempo": matched_row.get("tempo", ""),
            "genres": matched_row.get("genres", ""),
            "tags": matched_row.get("tags", ""),
            "lang": matched_row.get("lang", ""),
            "preference_weight": weight,
            "interaction_count": max(1, int(round(weight * 10))),
            "interaction_type": "history",
        }
        matched_events.append(matched_event)
        trace_rows.append(trace)

    # --- Influence track injection ---
    run_config_path_infl = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    influence_injected_count = 0
    influence_skipped_ids: list[str] = []
    if run_config_path_infl:
        _rc_utils = load_run_config_utils_module()
        infl = _rc_utils.resolve_bl003_influence_controls(run_config_path_infl)
        if infl["influence_enabled"] and infl["influence_track_ids"]:
            infl_weight = float(infl["influence_preference_weight"])
            existing_ds001_ids = {str(e["ds001_id"]) for e in matched_events}
            seen_influence_track_ids: set[str] = set()
            for track_id in infl["influence_track_ids"]:
                track_id = str(track_id).strip()
                if not track_id or track_id in seen_influence_track_ids:
                    continue
                seen_influence_track_ids.add(track_id)
                candidate = by_ds001_id.get(track_id)
                if candidate is None:
                    influence_skipped_ids.append(track_id)
                    continue
                if track_id in existing_ds001_ids:
                    for ev in matched_events:
                        if str(ev["ds001_id"]) == track_id:
                            ev["interaction_type"] = "history,influence"
                else:
                    infl_event = {
                        "event_id": f"ds001_influence_{influence_injected_count + 1:06d}",
                        "source_type": "influence",
                        "source_row_index": 0,
                        "source_timestamp": "",
                        "spotify_track_id": candidate.get("spotify_id", ""),
                        "spotify_isrc": "",
                        "spotify_track_name": candidate.get("song", ""),
                        "spotify_artist_names": candidate.get("artist", ""),
                        "match_method": "influence_direct",
                        "duration_delta_ms": None,
                        "ds001_id": candidate.get("id", ""),
                        "ds001_spotify_id": candidate.get("spotify_id", ""),
                        "artist": candidate.get("artist", ""),
                        "song": candidate.get("song", ""),
                        "release": candidate.get("release", ""),
                        "duration_ms": candidate.get("duration_ms", ""),
                        "popularity": candidate.get("popularity", ""),
                        "danceability": candidate.get("danceability", ""),
                        "energy": candidate.get("energy", ""),
                        "key": candidate.get("key", ""),
                        "mode": candidate.get("mode", ""),
                        "valence": candidate.get("valence", ""),
                        "tempo": candidate.get("tempo", ""),
                        "genres": candidate.get("genres", ""),
                        "tags": candidate.get("tags", ""),
                        "lang": candidate.get("lang", ""),
                        "preference_weight": infl_weight,
                        "interaction_count": max(1, int(round(infl_weight * 10))),
                        "interaction_type": "influence",
                    }
                    matched_events.append(infl_event)
                    existing_ds001_ids.add(track_id)
                influence_injected_count += 1

    aggregated: dict[str, dict[str, object]] = {}

    for event in matched_events:
        ds001_id = str(event["ds001_id"])
        agg = aggregated.get(ds001_id)
        if agg is None:
            agg = {
                "ds001_id": ds001_id,
                "spotify_id": event["ds001_spotify_id"],
                "song": event["song"],
                "artist": event["artist"],
                "release": event["release"],
                "duration_ms": event["duration_ms"],
                "popularity": event["popularity"],
                "danceability": event["danceability"],
                "energy": event["energy"],
                "key": event["key"],
                "mode": event["mode"],
                "valence": event["valence"],
                "tempo": event["tempo"],
                "genres": event["genres"],
                "tags": event["tags"],
                "lang": event["lang"],
                "matched_event_count": 0,
                "interaction_count_sum": 0,
                "preference_weight_sum": 0.0,
                "preference_weight_max": 0.0,
                "source_types": set(),
                "interaction_types": set(),
                "spotify_track_ids": set(),
            }
            aggregated[ds001_id] = agg

        agg["matched_event_count"] += 1
        agg["interaction_count_sum"] += int(event["interaction_count"])
        agg["preference_weight_sum"] += float(event["preference_weight"])
        agg["preference_weight_max"] = max(float(agg["preference_weight_max"]), float(event["preference_weight"]))
        agg["source_types"].add(str(event["source_type"]))
        if event["spotify_track_id"]:
            agg["spotify_track_ids"].add(str(event["spotify_track_id"]))
        for itype in str(event.get("interaction_type", "history")).split(","):
            itype = itype.strip()
            if itype:
                agg["interaction_types"].add(itype)

    output_dir.mkdir(parents=True, exist_ok=True)

    matched_jsonl_path = output_dir / "bl003_ds001_spotify_matched_events.jsonl"
    seed_table_path = output_dir / "bl003_ds001_spotify_seed_table.csv"
    trace_path = output_dir / "bl003_ds001_spotify_trace.csv"
    unmatched_path = output_dir / "bl003_ds001_spotify_unmatched.csv"
    summary_path = output_dir / "bl003_ds001_spotify_summary.json"
    source_scope_manifest_path = output_dir / "bl003_source_scope_manifest.json"

    with open_text_write(matched_jsonl_path) as handle:
        for row in matched_events:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    seed_rows_output: list[dict[str, object | str]] = []
    for ds001_id in sorted(aggregated.keys()):
        agg = aggregated[ds001_id]
        seed_rows_output.append(
            {
                "ds001_id": agg["ds001_id"],
                "spotify_id": agg["spotify_id"],
                "song": agg["song"],
                "artist": agg["artist"],
                "release": agg["release"],
                "duration_ms": agg["duration_ms"],
                "popularity": agg["popularity"],
                "danceability": agg["danceability"],
                "energy": agg["energy"],
                "key": agg["key"],
                "mode": agg["mode"],
                "valence": agg["valence"],
                "tempo": agg["tempo"],
                "genres": agg["genres"],
                "tags": agg["tags"],
                "lang": agg["lang"],
                "matched_event_count": agg["matched_event_count"],
                "interaction_count_sum": agg["interaction_count_sum"],
                "preference_weight_sum": f"{float(agg['preference_weight_sum']):.6f}",
                "preference_weight_max": f"{float(agg['preference_weight_max']):.6f}",
                "source_types": "|".join(sorted(agg["source_types"])),
                "interaction_types": "|".join(sorted(agg["interaction_types"])) if agg["interaction_types"] else "history",
                "spotify_track_ids": "|".join(sorted(agg["spotify_track_ids"])),
            }
        )

    write_csv_rows(seed_table_path, SEED_TABLE_FIELDNAMES, seed_rows_output)
    write_csv_rows(trace_path, TRACE_FIELDNAMES, trace_rows)
    write_csv_rows(unmatched_path, TRACE_FIELDNAMES, unmatched_rows)

    source_scope_manifest = {
        "generated_at_utc": utc_now(),
        "config_source": runtime_scope["config_source"],
        "run_config_path": runtime_scope["run_config_path"],
        "run_config_schema_version": runtime_scope["run_config_schema_version"],
        "input_scope": input_scope,
        "rows_available": scope_filter_stats["rows_available"],
        "rows_selected": scope_filter_stats["rows_selected"],
    }
    with open_text_write(source_scope_manifest_path) as handle:
        json.dump(source_scope_manifest, handle, indent=2, ensure_ascii=True)

    # --- Match-rate validation (CRI-001 mitigation) ---
    if summary_counts["input_event_rows"] > 0 and match_rate_min_threshold > 0.0:
        match_rate = summary_counts["matched_by_spotify_id"] + summary_counts["matched_by_metadata"]
        match_rate /= summary_counts["input_event_rows"]
        if match_rate < match_rate_min_threshold:
            raise RuntimeError(
                f"BL-003 match-rate validation failed: {match_rate:.1%} matched ({match_rate * summary_counts['input_event_rows']:.0f} events), "
                f"below minimum threshold {match_rate_min_threshold:.1%}. "
                f"This indicates high bias in the preference profile (built from only {match_rate:.1%} of imported history). "
                f"Either increase the match-rate threshold in seed_controls if this is expected, "
                f"or investigate DS-001 corpus coverage and import data quality."
            )

    elapsed_seconds = round(time.time() - t0, 3)

    influence_contract = {
        "enabled": False,
        "track_ids": [],
        "preference_weight": 1.0,
        "injected_count": influence_injected_count,
        "skipped_track_ids": influence_skipped_ids,
    }
    if run_config_path_infl:
        influence_contract = {
            "enabled": bool(infl.get("influence_enabled", False)),
            "track_ids": list(infl.get("influence_track_ids") or []),
            "preference_weight": float(infl.get("influence_preference_weight") or 1.0),
            "injected_count": influence_injected_count,
            "skipped_track_ids": influence_skipped_ids,
        }

    seed_contract = {
        "input_scope": input_scope,
        "influence_tracks": {
            "enabled": influence_contract["enabled"],
            "track_ids": influence_contract["track_ids"],
            "preference_weight": influence_contract["preference_weight"],
        },
    }

    summary = {
        "task": "BL-003-DS001-spotify-seed-build",
        "generated_at_utc": utc_now(),
        "elapsed_seconds": elapsed_seconds,
        "inputs": {
            "ds001_candidates": str(ds001_path),
            "ds001_candidates_sha256": sha256_of_file(ds001_path),
            "spotify_export_dir": str(spotify_dir),
            "files": {
                "spotify_top_tracks_flat_csv": str(top_path),
                "spotify_saved_tracks_flat_csv": str(saved_path),
                "spotify_playlist_items_flat_csv": str(playlist_items_path),
                "spotify_recently_played_flat_csv": str(recently_played_path),
            },
            "selection": export_selection,
            "config_source": runtime_scope["config_source"],
            "run_config_path": runtime_scope["run_config_path"],
            "run_config_schema_version": runtime_scope["run_config_schema_version"],
            "input_scope": input_scope,
            "influence_tracks": influence_contract,
            "seed_contract": {
                **seed_contract,
                "contract_hash": canonical_json_hash(seed_contract),
            },
            "selected_sources_expected": expected_sources,
            "selected_sources_available": available_sources,
            "missing_selected_sources": missing_selected_sources,
            "allow_missing_selected_sources": bool(args.allow_missing_selected_sources),
        },
        "source_stats": source_stats,
        "source_scope_filtering": scope_filter_stats,
        "counts": {
            **summary_counts,
            "matched_events_rows": len(matched_events),
            "seed_table_rows": len(aggregated),
            "trace_rows": len(trace_rows),
            "unmatched_rows": len(unmatched_rows),
            "match_rate_validation": {
                "threshold_enforced": match_rate_min_threshold > 0.0,
                "min_threshold": round(match_rate_min_threshold, 4),
                "actual_match_rate": round(
                    (summary_counts["matched_by_spotify_id"] + summary_counts["matched_by_metadata"]) / summary_counts["input_event_rows"]
                    if summary_counts["input_event_rows"] > 0
                    else 0.0,
                    4,
                ),
                "status": "pass" if summary_counts["input_event_rows"] == 0 or (summary_counts["matched_by_spotify_id"] + summary_counts["matched_by_metadata"]) / summary_counts["input_event_rows"] >= match_rate_min_threshold else "fail",
            },
        },
        "outputs": {
            "matched_events_jsonl": str(matched_jsonl_path),
            "seed_table_csv": str(seed_table_path),
            "trace_csv": str(trace_path),
            "unmatched_csv": str(unmatched_path),
            "summary_json": str(summary_path),
            "source_scope_manifest_json": str(source_scope_manifest_path),
            "sha256": {
                "matched_events_jsonl": sha256_of_file(matched_jsonl_path),
                "seed_table_csv": sha256_of_file(seed_table_path),
                "trace_csv": sha256_of_file(trace_path),
                "unmatched_csv": sha256_of_file(unmatched_path),
                "source_scope_manifest_json": sha256_of_file(source_scope_manifest_path),
            },
        },
        "notes": {
            "policy": "spotify_id exact match is primary for DS-001; metadata fallback used only when needed",
            "logging": "full row-level trace includes matched and unmatched reasons",
            "seed_table_enrichment": "seed table includes DS-001 numeric feature columns so downstream profile stages can consume a single BL-003 artifact",
        },
    }

    with open_text_write(summary_path) as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    print(f"input_event_rows={summary_counts['input_event_rows']}")
    print(f"matched_by_spotify_id={summary_counts['matched_by_spotify_id']}")
    print(f"matched_by_metadata={summary_counts['matched_by_metadata']}")
    print(f"unmatched={summary_counts['unmatched']}")
    print(f"matched_events_rows={len(matched_events)}")
    print(f"seed_table_rows={len(aggregated)}")
    print(f"trace_rows={len(trace_rows)}")
    print(f"unmatched_rows={len(unmatched_rows)}")
    print(f"summary_path={summary_path}")



if __name__ == "__main__":
    main()
