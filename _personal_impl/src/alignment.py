from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from difflib import SequenceMatcher
import hashlib
import json
from importlib import import_module
import math
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from shared.io_utils import load_csv_rows, sha256_of_file, utc_now, open_text_write
from shared.path_utils import impl_root
from shared.coerce_utils import safe_float, safe_int
from shared.run_store import SQLiteRunStore, resolve_run_store_path
from run_config.stage_control_resolution import defaults_loader, resolve_stage_controls

DEFAULT_TOP_RANGE_WEIGHTS = {
    "short_term": 0.50,
    "medium_term": 0.30,
    "long_term": 0.20,
}
DEFAULT_SOURCE_BASE_WEIGHTS = {
    "top_tracks": 1.00,
    "saved_tracks": 0.60,
    "playlist_items": 0.40,
    "recently_played": 0.50,
}
DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK = 0.25
DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS = 90.0
DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS = 365.0
DEFAULT_INPUT_SCOPE: dict[str, object] = {
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
DEFAULT_SEED_CONTROLS: dict[str, Any] = {
    "match_rate_min_threshold": 0.0,
    "top_range_weights": dict(DEFAULT_TOP_RANGE_WEIGHTS),
    "source_base_weights": dict(DEFAULT_SOURCE_BASE_WEIGHTS),
    "decay_half_lives": {
        "recently_played": DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
        "saved_tracks": DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
    },
    "fuzzy_matching": {
        "enabled": False,
        "artist_threshold": 0.90,
        "title_threshold": 0.90,
        "combined_threshold": 0.90,
        "max_duration_delta_ms": 5000,
        "max_artist_candidates": 5,
    },
    "match_strategy": {
        "enable_spotify_id_match": True,
        "enable_metadata_match": True,
        "enable_fuzzy_match": True,
    },
    "match_strategy_order": [
        "spotify_id_exact",
        "metadata_fallback",
        "fuzzy_title_artist",
    ],
    "temporal_controls": {
        "reference_mode": "system",
        "reference_now_utc": None,
    },
    "aggregation_policy": {
        "preference_weight_mode": "sum",
        "preference_weight_cap_per_event": None,
    },
}
DEFAULT_WEIGHTING_POLICY: dict[str, dict[str, float]] = {
    "top_tracks": {
        "min_rank_floor": 0.05,
        "scale_multiplier": 100.0,
        "default_time_range_weight": 0.20,
    },
    "playlist_items": {
        "min_position_floor": 0.05,
        "scale_multiplier": 20.0,
    },
}



SOURCE_TOP_TRACKS: Final[str] = "top_tracks"
SOURCE_SAVED_TRACKS: Final[str] = "saved_tracks"
SOURCE_PLAYLIST_ITEMS: Final[str] = "playlist_items"
SOURCE_RECENTLY_PLAYED: Final[str] = "recently_played"
SOURCE_INFLUENCE: Final[str] = "influence"

SOURCE_TYPES: Final[tuple[str, ...]] = (
    SOURCE_TOP_TRACKS,
    SOURCE_SAVED_TRACKS,
    SOURCE_PLAYLIST_ITEMS,
    SOURCE_RECENTLY_PLAYED,
)

SOURCE_SCOPE_SPECS: Final[dict[str, dict[str, str]]] = {
    SOURCE_TOP_TRACKS: {
        "input_scope_flag": "include_top_tracks",
        "export_selection_flag": "include_top_tracks",
        "rows_attr": "top_rows",
        "exists_attr": "top_exists",
    },
    SOURCE_SAVED_TRACKS: {
        "input_scope_flag": "include_saved_tracks",
        "export_selection_flag": "include_saved_tracks",
        "rows_attr": "saved_rows",
        "exists_attr": "saved_exists",
    },
    SOURCE_PLAYLIST_ITEMS: {
        "input_scope_flag": "include_playlists",
        "export_selection_flag": "include_playlists",
        "rows_attr": "playlist_rows",
        "exists_attr": "playlist_exists",
    },
    SOURCE_RECENTLY_PLAYED: {
        "input_scope_flag": "include_recently_played",
        "export_selection_flag": "include_recently_played",
        "rows_attr": "recent_rows",
        "exists_attr": "recent_exists",
    },
}

SPOTIFY_EXPORT_FILENAMES: Final[dict[str, str]] = {
    SOURCE_TOP_TRACKS: "spotify_top_tracks_flat.csv",
    SOURCE_SAVED_TRACKS: "spotify_saved_tracks_flat.csv",
    SOURCE_PLAYLIST_ITEMS: "spotify_playlist_items_flat.csv",
    SOURCE_RECENTLY_PLAYED: "spotify_recently_played_flat.csv",
}

ALIGNMENT_OUTPUT_FILENAMES: Final[dict[str, str]] = {
    "matched_jsonl": "bl003_ds001_spotify_matched_events.jsonl",
    "seed_table_csv": "bl003_ds001_spotify_seed_table.csv",
    "trace_csv": "bl003_ds001_spotify_trace.csv",
    "unmatched_csv": "bl003_ds001_spotify_unmatched.csv",
    "summary_json": "bl003_ds001_spotify_summary.json",
    "source_scope_manifest_json": "bl003_source_scope_manifest.json",
}

TRACE_FIELDNAMES: Final[list[str]] = [
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
    "fuzzy_title_score",
    "fuzzy_artist_score",
    "fuzzy_combined_score",
    "reason",
    "preference_weight",
]

SEED_TABLE_FIELDNAMES: Final[list[str]] = [
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

ALIGNMENT_ARTIFACT_SCHEMA_VERSION: Final[str] = "bl003-artifacts-v1"
ALIGNMENT_SUMMARY_SCHEMA_VERSION: Final[str] = "bl003-summary-v1"
ALIGNMENT_SOURCE_SCOPE_MANIFEST_SCHEMA_VERSION: Final[str] = "bl003-source-scope-manifest-v1"
ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION: Final[str] = "bl003-seed-contract-v1"
ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION: Final[str] = "bl003-structural-contract-v1"

ALIGNMENT_DEFAULT_RELATIVE_PATHS: Final[dict[str, Path]] = {
    "ds001_candidates": Path("data_layer") / "outputs" / "ds001_working_candidate_dataset.csv",
    "spotify_export_dir": Path("ingestion") / "outputs" / "spotify_api_export",
    "output_dir": Path("alignment") / "outputs",
}

MATCH_STATUS_MATCHED: Final[str] = "matched"
MATCH_STATUS_UNMATCHED: Final[str] = "unmatched"

MATCH_METHOD_SPOTIFY_ID_EXACT: Final[str] = "spotify_id_exact"
MATCH_METHOD_METADATA_FALLBACK: Final[str] = "metadata_fallback"
MATCH_METHOD_FUZZY_TITLE_ARTIST: Final[str] = "fuzzy_title_artist"
MATCH_METHOD_INFLUENCE_DIRECT: Final[str] = "influence_direct"

UNMATCHED_REASON_MISSING_KEYS: Final[str] = "missing_track_id_and_metadata"
UNMATCHED_REASON_NO_CANDIDATE: Final[str] = "no_ds001_candidate"

INTERACTION_TYPE_HISTORY: Final[str] = "history"
INTERACTION_TYPE_INFLUENCE: Final[str] = "influence"
INTERACTION_TYPE_HISTORY_INFLUENCE: Final[str] = "history,influence"
DEFAULT_INFLUENCE_PREFERENCE_WEIGHT: Final[float] = 1.0
DS001_ID_FIELD_CANDIDATES: Final[tuple[str, ...]] = ("id", "cid", "track_id")

ARTIST_NAME_DELIMITERS: Final[tuple[str, ...]] = ("|", ";", ",")
DEFAULT_TOP_TIME_RANGES: Final[tuple[str, ...]] = ("short_term", "medium_term", "long_term")

EVENT_ID_ALIGNMENT_TEMPLATE: Final[str] = "ds001_align_{index:06d}"
EVENT_ID_INFLUENCE_TEMPLATE: Final[str] = "ds001_influence_{index:06d}"
MATCH_STRATEGY_ORDER: Final[tuple[str, ...]] = (
    MATCH_METHOD_SPOTIFY_ID_EXACT,
    MATCH_METHOD_METADATA_FALLBACK,
    MATCH_METHOD_FUZZY_TITLE_ARTIST,
)
TEXT_NORMALIZATION_RULES: Final[str] = "unicode_nfd_lowercase_ascii_folding"
CONFIG_PRECEDENCE_HIERARCHY: Final[tuple[str, ...]] = (
    "BL003_INPUT_SCOPE_JSON",
    "BL_RUN_CONFIG_PATH",
    "defaults",
)

FLOAT_PRECISION_DECIMALS: Final[int] = 6
SUMMARY_RATE_PRECISION_DECIMALS: Final[int] = 4
JSON_INDENT_SPACES: Final[int] = 2
SECONDS_PER_DAY: Final[float] = 86400.0
INTERACTION_COUNT_WEIGHT_SCALE: Final[int] = 10

SUMMARY_TASK_NAME: Final[str] = "BL-003-DS001-spotify-seed-build"
SUMMARY_NOTE_POLICY: Final[str] = (
    "spotify_id exact match is primary for DS-001; metadata fallback used when needed; "
    "optional fuzzy fallback applies only after both exact paths fail"
)
SUMMARY_NOTE_LOGGING: Final[str] = "full row-level trace includes matched and unmatched reasons"
SUMMARY_NOTE_SEED_TABLE_ENRICHMENT: Final[str] = (
    "seed table includes DS-001 numeric feature columns so downstream "
    "profile stages can consume a single BL-003 artifact"
)


def parse_int(value: str) -> int | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None


def normalize_ascii_text(value: str | None) -> str:
    """Normalize text to lowercase ASCII alphanumeric tokens separated by spaces."""
    if value is None:
        return ""
    text = " ".join(str(value).split())
    if not text:
        return ""
    raw = unicodedata.normalize("NFKD", text)
    ascii_text = raw.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower()
    cleaned = re.sub(r"[^a-z0-9 ]", " ", lowered)
    return " ".join(cleaned.split())





def resolve_ds001_id(candidate: dict[str, Any]) -> str:
    for field in DS001_ID_FIELD_CANDIDATES:
        token = str(candidate.get(field, "") or "").strip()
        if token:
            return token
    return ""


def normalize_ds001_row_identity(row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    ds001_id = resolve_ds001_id(normalized)
    if ds001_id:
        normalized["id"] = ds001_id
    return normalized


def build_seed_aggregation_health(
    *,
    matched_events_rows: int,
    seed_table_rows: int,
    warn_min_ratio: float,
    collapse_max_rows: int,
) -> dict[str, Any]:
    ratio = round(
        (seed_table_rows / matched_events_rows) if matched_events_rows > 0 else 0.0,
        6,
    )
    collapsed = matched_events_rows > 0 and seed_table_rows <= collapse_max_rows
    sparse = matched_events_rows > 0 and ratio < warn_min_ratio
    return {
        "status": "warn" if (collapsed or sparse) else "pass",
        "matched_events_rows": matched_events_rows,
        "seed_table_rows": seed_table_rows,
        "aggregation_ratio": ratio,
        "warn_min_ratio": warn_min_ratio,
        "collapse_max_rows": collapse_max_rows,
        "collapsed": collapsed,
        "sparse": sparse,
    }


def _compute_ratio(left: str, right: str) -> float:
    try:
        fuzz_module = import_module("rapidfuzz.fuzz")
    except ModuleNotFoundError:
        return SequenceMatcher(None, left, right).ratio() * 100.0
    ratio_fn = getattr(fuzz_module, "ratio", None)
    if callable(ratio_fn):
        return safe_float(ratio_fn(left, right))
    return SequenceMatcher(None, left, right).ratio() * 100.0


class fuzz:
    @staticmethod
    def ratio(left: str, right: str) -> float:
        return _compute_ratio(left, right)


def normalize_text(value: str) -> str:
    """Normalise a string to ASCII lower-case tokens for fuzzy key comparison."""
    return normalize_ascii_text(value)


def first_artist(artist_names: str) -> str:
    """Return the primary artist from a pipe-, semicolon-, or comma-separated string."""
    for delimiter in ARTIST_NAME_DELIMITERS:
        if delimiter in artist_names:
            return artist_names.split(delimiter, 1)[0].strip()
    return artist_names.strip()


def choose_best_duration_match(
    candidates: list[dict[str, str]],
    target_duration_ms: int | None,
) -> tuple[dict[str, str], int | None]:
    """Select the candidate whose duration is closest to the target, falling back to first."""
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


def resolve_fuzzy_controls(raw_controls: dict[str, Any] | None) -> dict[str, Any]:
    defaults: dict[str, Any] = dict(DEFAULT_SEED_CONTROLS.get("fuzzy_matching") or {})
    if not isinstance(raw_controls, dict):
        return defaults
    controls = dict(defaults)
    controls["enabled"] = bool(raw_controls.get("enabled", defaults["enabled"]))
    for key in ("artist_threshold", "title_threshold", "combined_threshold"):
        try:
            value = float(raw_controls.get(key, defaults[key]))
        except (TypeError, ValueError):
            value = float(defaults[key])
        controls[key] = min(1.0, max(0.0, value))
    for key in ("max_duration_delta_ms", "max_artist_candidates"):
        try:
            value = int(raw_controls.get(key, defaults[key]))
        except (TypeError, ValueError):
            value = int(defaults[key])
        controls[key] = max(1, value)
    return controls


def fuzzy_find_candidate(
    *,
    title_key: str,
    artist_key: str,
    event_duration: int | None,
    by_artist: dict[str, list[dict[str, str]]],
    fuzzy_controls: dict[str, Any],
) -> tuple[dict[str, str] | None, int | None, float | None, float | None, float | None]:
    artist_keys = sorted(by_artist.keys())
    if not artist_keys:
        return None, None, None, None, None

    artist_matches: list[tuple[str, float]] = []
    artist_cutoff = float(fuzzy_controls["artist_threshold"])
    for candidate_artist_key in artist_keys:
        artist_score = fuzz.ratio(artist_key, candidate_artist_key) / 100.0
        if artist_score >= artist_cutoff:
            artist_matches.append((candidate_artist_key, artist_score))

    if not artist_matches:
        return None, None, None, None, None

    artist_matches = sorted(
        artist_matches,
        key=lambda match: (-float(match[1]), str(match[0])),
    )[: int(fuzzy_controls["max_artist_candidates"])]

    deduped_candidates: dict[str, tuple[dict[str, str], float]] = {}
    for artist_match_key, artist_score in artist_matches:
        for candidate in by_artist.get(artist_match_key, []):
            ds001_id = resolve_ds001_id(candidate)
            if not ds001_id:
                continue
            previous = deduped_candidates.get(ds001_id)
            if previous is None or artist_score > previous[1]:
                deduped_candidates[ds001_id] = (candidate, artist_score)

    best_choice: tuple[dict[str, str], int | None, float, float, float] | None = None
    best_sort_key: tuple[float, float, float, int, str] | None = None
    for ds001_id in sorted(deduped_candidates.keys()):
        candidate, artist_score = deduped_candidates[ds001_id]
        candidate_title_key = normalize_text(candidate.get("song", ""))
        if not candidate_title_key:
            continue

        title_score = fuzz.ratio(title_key, candidate_title_key) / 100.0
        if title_score < fuzzy_controls["title_threshold"]:
            continue

        combined_score = (artist_score + title_score) / 2.0
        if combined_score < fuzzy_controls["combined_threshold"]:
            continue

        duration_delta: int | None = None
        candidate_duration = parse_int(candidate.get("duration_ms", ""))
        if event_duration is not None and candidate_duration is not None:
            duration_delta = abs(candidate_duration - event_duration)
            if duration_delta > fuzzy_controls["max_duration_delta_ms"]:
                continue

        duration_sort = duration_delta if duration_delta is not None else 10**12
        sort_key = (-combined_score, -title_score, -artist_score, duration_sort, ds001_id)
        if best_sort_key is None or sort_key < best_sort_key:
            best_sort_key = sort_key
            best_choice = (candidate, duration_delta, title_score, artist_score, combined_score)

    if best_choice is None:
        return None, None, None, None, None
    return best_choice


def build_ds001_indices(
    rows: list[dict[str, str]],
) -> tuple[
    dict[str, dict[str, str]],
    dict[tuple[str, str], list[dict[str, str]]],
    dict[str, list[dict[str, str]]],
]:
    """Build Spotify-ID, (title, artist), and artist-only indices over DS-001 candidates."""
    by_spotify_id: dict[str, dict[str, str]] = {}
    by_title_artist: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    by_artist: dict[str, list[dict[str, str]]] = defaultdict(list)

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
            by_artist[artist_key].append(row)

    for candidate_rows in by_title_artist.values():
        candidate_rows.sort(key=lambda r: resolve_ds001_id(r))

    for candidate_rows in by_artist.values():
        candidate_rows.sort(key=lambda r: resolve_ds001_id(r))

    return by_spotify_id, by_title_artist, by_artist


def format_alignment_event_id(index: int) -> str:
    return EVENT_ID_ALIGNMENT_TEMPLATE.format(index=index)


def format_influence_event_id(index: int) -> str:
    return EVENT_ID_INFLUENCE_TEMPLATE.format(index=index)


@dataclass(frozen=True, slots=True)
class AlignmentBehaviorControls:
    input_scope: dict[str, object]
    top_range_weights: dict[str, float]
    source_base_weights: dict[str, float]
    decay_half_lives: dict[str, float]
    match_rate_min_threshold: float
    fuzzy_matching_controls: dict[str, Any]
    match_strategy: dict[str, bool]
    match_strategy_order: list[str]
    temporal_controls: dict[str, Any]
    aggregation_policy: dict[str, Any]
    seed_aggregation_health: dict[str, Any]
    weighting_policy: dict[str, Any] | None
    influence_controls: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AlignmentStructuralContract:
    spotify_export_filenames: dict[str, str]
    output_filenames: dict[str, str]
    trace_fieldnames: list[str]
    seed_table_fieldnames: list[str]
    artifact_schema_version: str
    summary_schema_version: str
    source_scope_manifest_schema_version: str
    default_relative_paths: dict[str, Path]

    @classmethod
    def from_defaults(cls) -> AlignmentStructuralContract:
        return cls(
            spotify_export_filenames=dict(SPOTIFY_EXPORT_FILENAMES),
            output_filenames=dict(ALIGNMENT_OUTPUT_FILENAMES),
            trace_fieldnames=list(TRACE_FIELDNAMES),
            seed_table_fieldnames=list(SEED_TABLE_FIELDNAMES),
            artifact_schema_version=ALIGNMENT_ARTIFACT_SCHEMA_VERSION,
            summary_schema_version=ALIGNMENT_SUMMARY_SCHEMA_VERSION,
            source_scope_manifest_schema_version=ALIGNMENT_SOURCE_SCOPE_MANIFEST_SCHEMA_VERSION,
            default_relative_paths=dict(ALIGNMENT_DEFAULT_RELATIVE_PATHS),
        )


@dataclass(slots=True)
class SourceEvent:
    source_type: str
    source_row_index: str
    spotify_track_id: str
    isrc: str
    track_name: str
    artist_names: str
    duration_ms: str
    event_time: str
    time_range: str
    rank: str
    playlist_id: str
    playlist_name: str
    playlist_position: str

    @classmethod
    def from_raw_row(cls, source_type: str, row_index: int, row: dict[str, str]) -> SourceEvent:
        event_time = ""
        if source_type in {SOURCE_SAVED_TRACKS, SOURCE_PLAYLIST_ITEMS}:
            event_time = (row.get("added_at") or "").strip()
        elif source_type == SOURCE_RECENTLY_PLAYED:
            event_time = (row.get("played_at") or "").strip()

        return cls(
            source_type=source_type,
            source_row_index=str(row_index),
            spotify_track_id=(row.get("track_id") or "").strip(),
            isrc=(row.get("isrc") or "").strip(),
            track_name=(row.get("track_name") or "").strip(),
            artist_names=(row.get("artist_names") or "").strip(),
            duration_ms=(row.get("duration_ms") or "").strip(),
            event_time=event_time,
            time_range=(row.get("time_range") or "").strip(),
            rank=(row.get("rank") or "").strip(),
            playlist_id=(row.get("playlist_id") or "").strip(),
            playlist_name=(row.get("playlist_name") or "").strip(),
            playlist_position=(row.get("playlist_position") or "").strip(),
        )

    @classmethod
    def from_dict(cls, payload: dict[str, str]) -> SourceEvent:
        return cls(
            source_type=str(payload.get("source_type", "")),
            source_row_index=str(payload.get("source_row_index", "")),
            spotify_track_id=str(payload.get("spotify_track_id", "")),
            isrc=str(payload.get("isrc", "")),
            track_name=str(payload.get("track_name", "")),
            artist_names=str(payload.get("artist_names", "")),
            duration_ms=str(payload.get("duration_ms", "")),
            event_time=str(payload.get("event_time", "")),
            time_range=str(payload.get("time_range", "")),
            rank=str(payload.get("rank", "")),
            playlist_id=str(payload.get("playlist_id", "")),
            playlist_name=str(payload.get("playlist_name", "")),
            playlist_position=str(payload.get("playlist_position", "")),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "source_type": self.source_type,
            "source_row_index": self.source_row_index,
            "spotify_track_id": self.spotify_track_id,
            "isrc": self.isrc,
            "track_name": self.track_name,
            "artist_names": self.artist_names,
            "duration_ms": self.duration_ms,
            "event_time": self.event_time,
            "time_range": self.time_range,
            "rank": self.rank,
            "playlist_id": self.playlist_id,
            "playlist_name": self.playlist_name,
            "playlist_position": self.playlist_position,
        }


@dataclass(slots=True)
class MatchTrace:
    source_type: str
    source_row_index: str
    spotify_track_id: str
    isrc: str
    track_name: str
    artist_names: str
    duration_ms: str
    event_time: str
    time_range: str
    rank: str
    playlist_id: str
    playlist_name: str
    playlist_position: str
    match_status: str = ""
    match_method: str = ""
    matched_ds001_id: str = ""
    matched_song: str = ""
    matched_artist: str = ""
    duration_delta_ms: str = ""
    fuzzy_title_score: str = ""
    fuzzy_artist_score: str = ""
    fuzzy_combined_score: str = ""
    reason: str = ""
    preference_weight: str = ""

    @classmethod
    def from_event(cls, event: SourceEvent, preference_weight: float) -> MatchTrace:
        return cls(
            source_type=event.source_type,
            source_row_index=event.source_row_index,
            spotify_track_id=event.spotify_track_id,
            isrc=event.isrc,
            track_name=event.track_name,
            artist_names=event.artist_names,
            duration_ms=event.duration_ms,
            event_time=event.event_time,
            time_range=event.time_range,
            rank=event.rank,
            playlist_id=event.playlist_id,
            playlist_name=event.playlist_name,
            playlist_position=event.playlist_position,
            preference_weight=f"{preference_weight:.{FLOAT_PRECISION_DECIMALS}f}",
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "source_type": self.source_type,
            "source_row_index": self.source_row_index,
            "spotify_track_id": self.spotify_track_id,
            "isrc": self.isrc,
            "track_name": self.track_name,
            "artist_names": self.artist_names,
            "duration_ms": self.duration_ms,
            "event_time": self.event_time,
            "time_range": self.time_range,
            "rank": self.rank,
            "playlist_id": self.playlist_id,
            "playlist_name": self.playlist_name,
            "playlist_position": self.playlist_position,
            "match_status": self.match_status,
            "match_method": self.match_method,
            "matched_ds001_id": self.matched_ds001_id,
            "matched_song": self.matched_song,
            "matched_artist": self.matched_artist,
            "duration_delta_ms": self.duration_delta_ms,
            "fuzzy_title_score": self.fuzzy_title_score,
            "fuzzy_artist_score": self.fuzzy_artist_score,
            "fuzzy_combined_score": self.fuzzy_combined_score,
            "reason": self.reason,
            "preference_weight": self.preference_weight,
        }


@dataclass(slots=True)
class MatchedEvent:
    event_id: str
    source_type: str
    source_row_index: int
    source_timestamp: str
    spotify_track_id: str
    spotify_isrc: str
    spotify_track_name: str
    spotify_artist_names: str
    match_method: str
    duration_delta_ms: int | None
    fuzzy_title_score: float | None
    fuzzy_artist_score: float | None
    fuzzy_combined_score: float | None
    ds001_id: str
    ds001_spotify_id: str
    artist: str
    song: str
    release: str
    duration_ms: str
    popularity: str
    danceability: str
    energy: str
    key: str
    mode: str
    valence: str
    tempo: str
    genres: str
    tags: str
    lang: str
    preference_weight: float
    interaction_count: int
    interaction_type: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> MatchedEvent:
        def _as_int(raw: Any, default: int) -> int:
            try:
                return int(raw)
            except (TypeError, ValueError):
                return default

        def _as_float(raw: Any, default: float | None = None) -> float | None:
            if raw is None:
                return default
            try:
                return float(raw)
            except (TypeError, ValueError):
                return default

        return cls(
            event_id=str(payload.get("event_id", "")),
            source_type=str(payload.get("source_type", "")),
            source_row_index=_as_int(payload.get("source_row_index"), 0),
            source_timestamp=str(payload.get("source_timestamp", "")),
            spotify_track_id=str(payload.get("spotify_track_id", "")),
            spotify_isrc=str(payload.get("spotify_isrc", "")),
            spotify_track_name=str(payload.get("spotify_track_name", "")),
            spotify_artist_names=str(payload.get("spotify_artist_names", "")),
            match_method=str(payload.get("match_method", "")),
            duration_delta_ms=_as_int(payload.get("duration_delta_ms"), 0)
            if payload.get("duration_delta_ms") is not None
            else None,
            fuzzy_title_score=_as_float(payload.get("fuzzy_title_score"), None),
            fuzzy_artist_score=_as_float(payload.get("fuzzy_artist_score"), None),
            fuzzy_combined_score=_as_float(payload.get("fuzzy_combined_score"), None),
            ds001_id=str(payload.get("ds001_id", "")),
            ds001_spotify_id=str(payload.get("ds001_spotify_id", "")),
            artist=str(payload.get("artist", "")),
            song=str(payload.get("song", "")),
            release=str(payload.get("release", "")),
            duration_ms=str(payload.get("duration_ms", "")),
            popularity=str(payload.get("popularity", "")),
            danceability=str(payload.get("danceability", "")),
            energy=str(payload.get("energy", "")),
            key=str(payload.get("key", "")),
            mode=str(payload.get("mode", "")),
            valence=str(payload.get("valence", "")),
            tempo=str(payload.get("tempo", "")),
            genres=str(payload.get("genres", "")),
            tags=str(payload.get("tags", "")),
            lang=str(payload.get("lang", "")),
            preference_weight=float(payload.get("preference_weight", 0.0)),
            interaction_count=_as_int(payload.get("interaction_count"), 0),
            interaction_type=str(payload.get("interaction_type", INTERACTION_TYPE_HISTORY)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source_type": self.source_type,
            "source_row_index": self.source_row_index,
            "source_timestamp": self.source_timestamp,
            "spotify_track_id": self.spotify_track_id,
            "spotify_isrc": self.spotify_isrc,
            "spotify_track_name": self.spotify_track_name,
            "spotify_artist_names": self.spotify_artist_names,
            "match_method": self.match_method,
            "duration_delta_ms": self.duration_delta_ms,
            "fuzzy_title_score": self.fuzzy_title_score,
            "fuzzy_artist_score": self.fuzzy_artist_score,
            "fuzzy_combined_score": self.fuzzy_combined_score,
            "ds001_id": self.ds001_id,
            "ds001_spotify_id": self.ds001_spotify_id,
            "artist": self.artist,
            "song": self.song,
            "release": self.release,
            "duration_ms": self.duration_ms,
            "popularity": self.popularity,
            "danceability": self.danceability,
            "energy": self.energy,
            "key": self.key,
            "mode": self.mode,
            "valence": self.valence,
            "tempo": self.tempo,
            "genres": self.genres,
            "tags": self.tags,
            "lang": self.lang,
            "preference_weight": self.preference_weight,
            "interaction_count": self.interaction_count,
            "interaction_type": self.interaction_type,
        }


@dataclass(slots=True)
class AggregatedEvent:
    ds001_id: str
    spotify_id: str
    song: str
    artist: str
    release: str
    duration_ms: str
    popularity: str
    danceability: str
    energy: str
    key: str
    mode: str
    valence: str
    tempo: str
    genres: str
    tags: str
    lang: str
    matched_event_count: int = 0
    interaction_count_sum: int = 0
    preference_weight_sum: float = 0.0
    preference_weight_max: float = 0.0
    source_types: set[str] = field(default_factory=set)
    interaction_types: set[str] = field(default_factory=set)
    spotify_track_ids: set[str] = field(default_factory=set)

    @classmethod
    def from_matched_event(cls, event: MatchedEvent) -> AggregatedEvent:
        return cls(
            ds001_id=event.ds001_id,
            spotify_id=event.ds001_spotify_id,
            song=event.song,
            artist=event.artist,
            release=event.release,
            duration_ms=event.duration_ms,
            popularity=event.popularity,
            danceability=event.danceability,
            energy=event.energy,
            key=event.key,
            mode=event.mode,
            valence=event.valence,
            tempo=event.tempo,
            genres=event.genres,
            tags=event.tags,
            lang=event.lang,
        )

    def apply_event(self, event: MatchedEvent) -> None:
        self.matched_event_count += 1
        self.interaction_count_sum += int(event.interaction_count)
        self.preference_weight_sum += float(event.preference_weight)
        self.preference_weight_max = max(self.preference_weight_max, float(event.preference_weight))
        self.source_types.add(event.source_type)
        if event.spotify_track_id:
            self.spotify_track_ids.add(event.spotify_track_id)
        for interaction_type in str(event.interaction_type or INTERACTION_TYPE_HISTORY).split(","):
            token = interaction_type.strip()
            if token:
                self.interaction_types.add(token)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ds001_id": self.ds001_id,
            "spotify_id": self.spotify_id,
            "song": self.song,
            "artist": self.artist,
            "release": self.release,
            "duration_ms": self.duration_ms,
            "popularity": self.popularity,
            "danceability": self.danceability,
            "energy": self.energy,
            "key": self.key,
            "mode": self.mode,
            "valence": self.valence,
            "tempo": self.tempo,
            "genres": self.genres,
            "tags": self.tags,
            "lang": self.lang,
            "matched_event_count": self.matched_event_count,
            "interaction_count_sum": self.interaction_count_sum,
            "preference_weight_sum": self.preference_weight_sum,
            "preference_weight_max": self.preference_weight_max,
            "source_types": self.source_types,
            "interaction_types": self.interaction_types,
            "spotify_track_ids": self.spotify_track_ids,
        }


@dataclass(frozen=True, slots=True)
class AlignmentPaths:
    ds001_path: Path
    spotify_dir: Path
    output_dir: Path
    top_path: Path
    saved_path: Path
    playlist_items_path: Path
    recently_played_path: Path
    summary_path: Path
    source_scope_manifest_path: Path


@dataclass(frozen=True, slots=True)
class AlignmentSourceRows:
    top_rows: list[dict[str, str]]
    saved_rows: list[dict[str, str]]
    playlist_rows: list[dict[str, str]]
    recent_rows: list[dict[str, str]]
    top_exists: bool
    saved_exists: bool
    playlist_exists: bool
    recent_exists: bool


@dataclass(frozen=True, slots=True)
class AlignmentRunArtifacts:
    summary_path: Path
    summary_counts: dict[str, int]
    matched_events_rows: int
    seed_table_rows: int
    trace_rows: int
    unmatched_rows: int


@dataclass(frozen=True, slots=True)
class AlignmentSummaryMetrics:
    summary_counts: dict[str, int]
    matched_events_rows: int
    seed_table_rows: int
    trace_rows: int
    unmatched_rows: int


@dataclass(frozen=True, slots=True)
class AlignmentSummaryContext:
    elapsed_seconds: float
    ds001_path: Path
    spotify_dir: Path
    top_path: Path
    saved_path: Path
    playlist_items_path: Path
    recently_played_path: Path
    export_selection: dict[str, Any]
    runtime_scope: dict[str, Any]
    input_scope: dict[str, Any]
    influence_contract: dict[str, Any]
    expected_sources: dict[str, bool]
    available_sources: dict[str, bool]
    missing_selected_sources: list[str]
    allow_missing_selected_sources: bool
    source_stats: dict[str, Any]
    scope_filter_stats: dict[str, Any]
    behavior_controls: AlignmentBehaviorControls
    structural_contract: AlignmentStructuralContract
    metrics: AlignmentSummaryMetrics
    output_paths: dict[str, Path]
    match_rate_min_threshold: float
    fuzzy_matching_controls: dict[str, Any]


@dataclass(frozen=True)
class AlignmentResolvedContext:
    runtime_scope: dict[str, object]
    behavior_controls: AlignmentBehaviorControls
    structural_contract: AlignmentStructuralContract


@dataclass(frozen=True)
class _ScopeSelectionResult:
    selected_rows: dict[str, list[dict[str, str]]]
    scope_filter_stats: dict[str, Any]
    runtime_scope: dict[str, object]
    input_scope: dict[str, object]
    export_selection: dict[str, object]
    expected_sources: dict[str, bool]
    available_sources: dict[str, bool]
    missing_selected_sources: list[str]
    source_stats: dict[str, dict[str, int | bool]]


@dataclass(frozen=True)
class _MatchAggregationResult:
    trace_rows: list[dict[str, Any]]
    matched_events: list[dict[str, Any]]
    unmatched_rows: list[dict[str, Any]]
    summary_counts: dict[str, int]
    influence_contract: dict[str, Any]
    aggregated: Any


DEFAULT_INFLUENCE_CONTROLS: dict[str, Any] = {
    "influence_enabled": False,
    "influence_track_ids": [],
    "influence_preference_weight": DEFAULT_INFLUENCE_PREFERENCE_WEIGHT,
}


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _env_truthy(name: str) -> bool:
    raw = os.environ.get(name, "")
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _bl003_require_payload() -> bool:
    return _env_truthy("BL003_STRICT_PAYLOAD") or _env_truthy("BL_STRICT_STAGE_PAYLOAD")


def _load_bl003_runtime_scope_from_env() -> dict[str, object]:
    input_scope_json = os.environ.get("BL003_INPUT_SCOPE_JSON", "").strip()
    if input_scope_json:
        try:
            parsed_scope = json.loads(input_scope_json)
            if isinstance(parsed_scope, dict):
                return {
                    "config_source": "environment",
                    "run_config_path": None,
                    "run_config_schema_version": None,
                    "input_scope_controls": {str(k): v for k, v in parsed_scope.items()},
                }
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    return {
        "config_source": "export_selection",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope_controls": dict(DEFAULT_INPUT_SCOPE),
    }


def _sanitize_bl003_runtime_scope_controls(controls: dict[str, object]) -> dict[str, object]:
    scope_payload = _mapping(controls.get("input_scope_controls") or controls.get("input_scope"))
    merged_scope = dict(DEFAULT_INPUT_SCOPE)
    merged_scope.update({str(k): v for k, v in scope_payload.items()})
    payload_present = bool(os.environ.get("BL_STAGE_CONFIG_JSON", "").strip())
    return {
        "config_source": "orchestration_payload" if payload_present else str(controls.get("config_source") or "export_selection"),
        "run_config_path": controls.get("config_path") or controls.get("run_config_path"),
        "run_config_schema_version": controls.get("schema_version") or controls.get("run_config_schema_version"),
        "input_scope": merged_scope,
    }


def resolve_bl003_runtime_scope() -> dict[str, object]:
    return resolve_stage_controls(
        load_from_env=_load_bl003_runtime_scope_from_env,
        load_payload_defaults=defaults_loader({"input_scope_controls": dict(DEFAULT_INPUT_SCOPE)}),
        sanitize=_sanitize_bl003_runtime_scope_controls,
        require_payload=_bl003_require_payload(),
    )


def _load_stage_config_payload() -> dict[str, Any] | None:
    payload_json = os.environ.get("BL_STAGE_CONFIG_JSON", "").strip()
    if not payload_json:
        return None
    try:
        payload = json.loads(payload_json)
        if isinstance(payload, dict):
            stage_controls = payload.get("controls")
            if isinstance(stage_controls, dict):
                controls = dict(stage_controls)
                if "schema_version" in payload and "run_config_schema_version" not in controls:
                    controls["run_config_schema_version"] = payload.get("schema_version")
                return controls
            return payload
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _resolve_from_orchestration_payload(payload: dict[str, Any]) -> AlignmentResolvedContext:
    input_scope_controls = _mapping(payload.get("input_scope_controls"))
    seed_controls = _mapping(payload.get("seed_controls"))
    weighting_policy = payload.get("weighting_policy")
    influence_controls = _mapping(payload.get("influence_controls") or DEFAULT_INFLUENCE_CONTROLS)

    top_range_weights = _mapping(seed_controls.get("top_range_weights") or DEFAULT_TOP_RANGE_WEIGHTS)
    source_base_weights = _mapping(seed_controls.get("source_base_weights") or DEFAULT_SOURCE_BASE_WEIGHTS)
    fuzzy_matching_controls = _mapping(seed_controls.get("fuzzy_matching") or DEFAULT_SEED_CONTROLS.get("fuzzy_matching"))
    match_strategy = _mapping(seed_controls.get("match_strategy") or DEFAULT_SEED_CONTROLS.get("match_strategy"))
    match_strategy_order = _string_list(seed_controls.get("match_strategy_order") or DEFAULT_SEED_CONTROLS.get("match_strategy_order"))
    temporal_controls = _mapping(seed_controls.get("temporal_controls") or DEFAULT_SEED_CONTROLS.get("temporal_controls"))
    aggregation_policy = _mapping(seed_controls.get("aggregation_policy") or DEFAULT_SEED_CONTROLS.get("aggregation_policy"))
    seed_aggregation_health = _mapping(
        seed_controls.get("seed_aggregation_health") or DEFAULT_SEED_CONTROLS.get("seed_aggregation_health")
    )
    match_rate_min_threshold = float(seed_controls.get("match_rate_min_threshold", 0.0))

    seed_decay_half_lives = _mapping(seed_controls.get("decay_half_lives"))
    decay_half_lives = {
        "recently_played": float(seed_decay_half_lives.get("recently_played", DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS)),
        "saved_tracks": float(seed_decay_half_lives.get("saved_tracks", DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS)),
    }

    runtime_scope = {
        "config_source": "orchestration_payload",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope": input_scope_controls,
    }

    return AlignmentResolvedContext(
        runtime_scope=runtime_scope,
        behavior_controls=AlignmentBehaviorControls(
            input_scope=dict(input_scope_controls),
            top_range_weights=dict(top_range_weights),
            source_base_weights=dict(source_base_weights),
            decay_half_lives=dict(decay_half_lives),
            match_rate_min_threshold=float(match_rate_min_threshold),
            fuzzy_matching_controls=dict(fuzzy_matching_controls),
            match_strategy={k: bool(v) for k, v in match_strategy.items()},
            match_strategy_order=list(match_strategy_order),
            temporal_controls=dict(temporal_controls),
            aggregation_policy=dict(aggregation_policy),
            seed_aggregation_health=dict(seed_aggregation_health),
            weighting_policy=(_mapping(weighting_policy) if weighting_policy is not None else None),
            influence_controls=dict(influence_controls),
        ),
        structural_contract=AlignmentStructuralContract.from_defaults(),
    )


def _resolve_from_legacy_sources() -> AlignmentResolvedContext:
    runtime_scope = resolve_bl003_runtime_scope()
    input_scope = _mapping(runtime_scope.get("input_scope"))
    return AlignmentResolvedContext(
        runtime_scope=dict(runtime_scope),
        behavior_controls=AlignmentBehaviorControls(
            input_scope=dict(input_scope),
            top_range_weights=dict(DEFAULT_TOP_RANGE_WEIGHTS),
            source_base_weights=dict(DEFAULT_SOURCE_BASE_WEIGHTS),
            decay_half_lives={
                "recently_played": DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS,
                "saved_tracks": DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS,
            },
            match_rate_min_threshold=0.0,
            fuzzy_matching_controls=_mapping(DEFAULT_SEED_CONTROLS.get("fuzzy_matching")),
            match_strategy={str(k): bool(v) for k, v in _mapping(DEFAULT_SEED_CONTROLS.get("match_strategy")).items()},
            match_strategy_order=_string_list(DEFAULT_SEED_CONTROLS.get("match_strategy_order")),
            temporal_controls=_mapping(DEFAULT_SEED_CONTROLS.get("temporal_controls")),
            aggregation_policy=_mapping(DEFAULT_SEED_CONTROLS.get("aggregation_policy")),
            seed_aggregation_health=_mapping(DEFAULT_SEED_CONTROLS.get("seed_aggregation_health")),
            weighting_policy=None,
            influence_controls=dict(DEFAULT_INFLUENCE_CONTROLS),
        ),
        structural_contract=AlignmentStructuralContract.from_defaults(),
    )


def resolve_alignment_context() -> AlignmentResolvedContext:
    stage_payload = _load_stage_config_payload()
    if stage_payload:
        return _resolve_from_orchestration_payload(stage_payload)
    return _resolve_from_legacy_sources()


def as_positive_int_or_none(value: object) -> int | None:
    if value is None:
        return None
    parsed = safe_int(value, 0)
    return parsed if parsed > 0 else None


def filter_top_tracks_rows(rows: list[dict[str, str]], allowed_time_ranges: set[str]) -> list[dict[str, str]]:
    if not allowed_time_ranges:
        return list(rows)
    return [row for row in rows if (row.get("time_range") or "").strip() in allowed_time_ranges]


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
    scope_mapping = dict(input_scope.input_scope) if isinstance(input_scope, AlignmentBehaviorControls) else dict(input_scope)
    include_top_tracks = bool(scope_mapping.get("include_top_tracks", True))
    include_saved_tracks = bool(scope_mapping.get("include_saved_tracks", True))
    include_playlists = bool(scope_mapping.get("include_playlists", True))
    include_recently_played = bool(scope_mapping.get("include_recently_played", True))

    top_time_ranges_raw = scope_mapping.get("top_time_ranges")
    top_time_ranges = {str(item).strip() for item in (top_time_ranges_raw if isinstance(top_time_ranges_raw, list) else []) if str(item).strip()}
    if not top_time_ranges:
        top_time_ranges = set(DEFAULT_TOP_TIME_RANGES)

    saved_tracks_limit = as_positive_int_or_none(scope_mapping.get("saved_tracks_limit"))
    playlists_limit = as_positive_int_or_none(scope_mapping.get("playlists_limit"))
    playlist_items_per_playlist_limit = as_positive_int_or_none(scope_mapping.get("playlist_items_per_playlist_limit"))
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


def _parse_event_time(raw_value: str) -> datetime | None:
    token = raw_value.strip()
    if not token:
        return None
    normalized = token.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _resolve_reference_now_utc(now_utc: datetime | None = None, temporal_controls: dict[str, object] | None = None) -> datetime:
    if now_utc is not None:
        return now_utc.astimezone(timezone.utc)

    controls = dict(temporal_controls or {})
    reference_mode = str(controls.get("reference_mode") or "system").strip().lower()
    if reference_mode == "fixed":
        configured_reference = str(controls.get("reference_now_utc") or "").strip()
        if configured_reference:
            parsed = _parse_event_time(configured_reference)
            if parsed is not None:
                return parsed
    if reference_mode == "system":
        env_reference = os.environ.get("BL_REFERENCE_NOW_UTC", "").strip()
        if env_reference:
            parsed_env = _parse_event_time(env_reference)
            if parsed_env is not None:
                return parsed_env
    return datetime.now(timezone.utc)


def compute_temporal_decay(
    event_time: str,
    half_life_days: float,
    now_utc: datetime | None = None,
    temporal_controls: dict[str, object] | None = None,
) -> float:
    if half_life_days <= 0:
        return 1.0
    event_dt = _parse_event_time(event_time)
    if event_dt is None:
        return 1.0
    reference_now = _resolve_reference_now_utc(now_utc, temporal_controls=temporal_controls)
    age_days = max(0.0, (reference_now - event_dt).total_seconds() / SECONDS_PER_DAY)
    decay = math.exp(-math.log(2.0) * (age_days / half_life_days))
    return round(max(0.0, min(decay, 1.0)), FLOAT_PRECISION_DECIMALS)


def compute_weight(
    event: dict[str, str],
    top_range_weights: dict | None = None,
    source_base_weights: dict | None = None,
    decay_half_lives: dict[str, float] | None = None,
    temporal_controls: dict[str, object] | None = None,
    weighting_policy: dict | None = None,
    behavior_controls: AlignmentBehaviorControls | None = None,
) -> float:
    if behavior_controls is not None:
        top_range_weights = dict(behavior_controls.top_range_weights)
        source_base_weights = dict(behavior_controls.source_base_weights)
        decay_half_lives = dict(behavior_controls.decay_half_lives)
        temporal_controls = dict(behavior_controls.temporal_controls)
        weighting_policy = dict(behavior_controls.weighting_policy) if behavior_controls.weighting_policy is not None else None

    if top_range_weights is None or source_base_weights is None:
        raise ValueError("compute_weight requires top/source weight dictionaries or behavior_controls")

    source_type = event["source_type"]
    base = source_base_weights.get(source_type, DEFAULT_SOURCE_BASE_WEIGHT_FALLBACK)
    effective_decay_half_lives = dict(decay_half_lives or {})

    _policy = dict(weighting_policy or {})
    _top_policy = dict(DEFAULT_WEIGHTING_POLICY["top_tracks"])
    _playlist_policy = dict(DEFAULT_WEIGHTING_POLICY["playlist_items"])
    _min_rank_floor = float(_policy.get("top_tracks_min_rank_floor", _top_policy["min_rank_floor"]))
    _scale_top = float(_policy.get("top_tracks_scale_multiplier", _top_policy["scale_multiplier"]))
    _default_time_range_w = float(_policy.get("top_tracks_default_time_range_weight", _top_policy["default_time_range_weight"]))
    _min_pos_floor = float(_policy.get("playlist_items_min_position_floor", _playlist_policy["min_position_floor"]))
    _scale_pl = float(_policy.get("playlist_items_scale_multiplier", _playlist_policy["scale_multiplier"]))

    def apply_decay(raw_weight: float, source_key: str, default_half_life: float) -> float:
        half_life = float(effective_decay_half_lives.get(source_key, default_half_life))
        decay_factor = compute_temporal_decay(event.get("event_time", ""), half_life, temporal_controls=temporal_controls)
        return raw_weight * decay_factor

    if source_type == SOURCE_TOP_TRACKS:
        rank = parse_int(event.get("rank", ""))
        rank = rank if (rank is not None and rank > 0) else 50
        range_weight = top_range_weights.get(event.get("time_range", ""), _default_time_range_w)
        rank_score = max(_min_rank_floor, 1.0 / rank)
        return round(base * range_weight * rank_score * _scale_top, FLOAT_PRECISION_DECIMALS)

    if source_type == SOURCE_SAVED_TRACKS:
        return round(apply_decay(base * 1.0, SOURCE_SAVED_TRACKS, DEFAULT_SAVED_TRACKS_DECAY_HALF_LIFE_DAYS), FLOAT_PRECISION_DECIMALS)

    if source_type == SOURCE_PLAYLIST_ITEMS:
        pos = parse_int(event.get("playlist_position", ""))
        if pos is None or pos <= 0:
            pos = 50
        return round(base * max(_min_pos_floor, 1.0 / pos) * _scale_pl, FLOAT_PRECISION_DECIMALS)

    if source_type == SOURCE_RECENTLY_PLAYED:
        return round(apply_decay(base * 1.0, SOURCE_RECENTLY_PLAYED, DEFAULT_RECENTLY_PLAYED_DECAY_HALF_LIFE_DAYS), FLOAT_PRECISION_DECIMALS)

    return round(base, FLOAT_PRECISION_DECIMALS)


def to_event_rows(source_type: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    for idx, row in enumerate(rows, start=1):
        events.append(SourceEvent.from_raw_row(source_type, idx, row).to_dict())
    return events


def match_events(
    events: list[dict[str, str]],
    by_spotify_id: dict[str, dict[str, str]],
    by_title_artist: dict[tuple[str, str], list[dict[str, str]]],
    by_artist: dict[str, list[dict[str, str]]],
    top_range_weights: dict | None = None,
    source_base_weights: dict | None = None,
    decay_half_lives: dict[str, float] | None = None,
    fuzzy_controls: dict[str, Any] | None = None,
    weighting_policy: dict | None = None,
    behavior_controls: AlignmentBehaviorControls | None = None,
    *,
    context: AlignmentResolvedContext | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], list[dict[str, str]], dict[str, int]]:
    trace_rows: list[dict[str, str]] = []
    matched_events: list[dict[str, Any]] = []
    unmatched_rows: list[dict[str, str]] = []
    match_counts: dict[str, int] = {
        "matched_by_spotify_id": 0,
        "matched_by_metadata": 0,
        "matched_by_fuzzy": 0,
        "unmatched": 0,
        "unmatched_missing_keys": 0,
        "unmatched_no_candidate": 0,
    }
    effective_top_range_weights = top_range_weights
    effective_source_base_weights = source_base_weights
    effective_decay_half_lives = decay_half_lives
    effective_fuzzy_controls = fuzzy_controls
    effective_weighting_policy = weighting_policy
    effective_match_strategy = {
        "enable_spotify_id_match": True,
        "enable_metadata_match": True,
        "enable_fuzzy_match": True,
    }
    effective_match_strategy_order = list(MATCH_STRATEGY_ORDER)
    if context is not None:
        behavior_controls = context.behavior_controls

    if behavior_controls is not None:
        effective_top_range_weights = dict(behavior_controls.top_range_weights)
        effective_source_base_weights = dict(behavior_controls.source_base_weights)
        effective_decay_half_lives = dict(behavior_controls.decay_half_lives)
        effective_fuzzy_controls = dict(behavior_controls.fuzzy_matching_controls)
        effective_weighting_policy = dict(behavior_controls.weighting_policy) if behavior_controls.weighting_policy is not None else None
        effective_match_strategy.update({k: bool(v) for k, v in dict(behavior_controls.match_strategy).items()})
        if behavior_controls.match_strategy_order:
            effective_match_strategy_order = list(behavior_controls.match_strategy_order)

    if effective_top_range_weights is None or effective_source_base_weights is None:
        raise ValueError("match_events requires either context or top/source weight dictionaries")

    resolved_fuzzy_controls = resolve_fuzzy_controls(effective_fuzzy_controls)

    for event in events:
        source_event = SourceEvent.from_dict(event)
        spotify_track_id = source_event.spotify_track_id
        track_name = source_event.track_name
        artist_names = source_event.artist_names
        artist_primary = first_artist(artist_names)
        event_duration = parse_int(source_event.duration_ms)
        weight = compute_weight(
            source_event.to_dict(),
            effective_top_range_weights,
            effective_source_base_weights,
            decay_half_lives=effective_decay_half_lives,
            weighting_policy=effective_weighting_policy,
            behavior_controls=behavior_controls,
        )

        trace = MatchTrace.from_event(source_event, weight)

        matched_row: dict[str, str] | None = None
        duration_delta: int | None = None
        match_method = ""
        fuzzy_title_score: float | None = None
        fuzzy_artist_score: float | None = None
        fuzzy_combined_score: float | None = None

        title_key = normalize_text(track_name)
        artist_key = normalize_text(artist_primary)

        for method in effective_match_strategy_order:
            if method == MATCH_METHOD_SPOTIFY_ID_EXACT:
                if effective_match_strategy.get("enable_spotify_id_match", True) and spotify_track_id and spotify_track_id in by_spotify_id:
                    matched_row = by_spotify_id[spotify_track_id]
                    match_method = MATCH_METHOD_SPOTIFY_ID_EXACT
                    match_counts["matched_by_spotify_id"] += 1
                    break
                continue

            if method == MATCH_METHOD_METADATA_FALLBACK:
                if not effective_match_strategy.get("enable_metadata_match", True):
                    continue
                if not (title_key and artist_key):
                    continue
                candidates = by_title_artist.get((title_key, artist_key), [])
                if candidates:
                    matched_row, duration_delta = choose_best_duration_match(candidates, event_duration)
                    match_method = MATCH_METHOD_METADATA_FALLBACK
                    match_counts["matched_by_metadata"] += 1
                    break
                continue

            if method == MATCH_METHOD_FUZZY_TITLE_ARTIST:
                if not effective_match_strategy.get("enable_fuzzy_match", True):
                    continue
                if not resolved_fuzzy_controls["enabled"]:
                    continue
                if not (title_key and artist_key):
                    continue
                matched_row, duration_delta, fuzzy_title_score, fuzzy_artist_score, fuzzy_combined_score = fuzzy_find_candidate(
                    title_key=title_key,
                    artist_key=artist_key,
                    event_duration=event_duration,
                    by_artist=by_artist,
                    fuzzy_controls=resolved_fuzzy_controls,
                )
                if matched_row is not None:
                    match_method = MATCH_METHOD_FUZZY_TITLE_ARTIST
                    match_counts["matched_by_fuzzy"] += 1
                    break

        if matched_row is None:
            match_counts["unmatched"] += 1
            trace.match_status = MATCH_STATUS_UNMATCHED
            if not spotify_track_id and not (track_name and artist_primary):
                match_counts["unmatched_missing_keys"] += 1
                trace.reason = UNMATCHED_REASON_MISSING_KEYS
            else:
                match_counts["unmatched_no_candidate"] += 1
                trace.reason = UNMATCHED_REASON_NO_CANDIDATE
            trace_dict = trace.to_dict()
            unmatched_rows.append(trace_dict)
            trace_rows.append(trace_dict)
            continue

        trace.match_status = MATCH_STATUS_MATCHED
        trace.match_method = match_method
        matched_ds001_id = resolve_ds001_id(matched_row)
        trace.matched_ds001_id = matched_ds001_id
        trace.matched_song = matched_row.get("song", "")
        trace.matched_artist = matched_row.get("artist", "")
        trace.duration_delta_ms = "" if duration_delta is None else str(duration_delta)
        if fuzzy_title_score is not None:
            trace.fuzzy_title_score = f"{fuzzy_title_score:.{FLOAT_PRECISION_DECIMALS}f}"
        if fuzzy_artist_score is not None:
            trace.fuzzy_artist_score = f"{fuzzy_artist_score:.{FLOAT_PRECISION_DECIMALS}f}"
        if fuzzy_combined_score is not None:
            trace.fuzzy_combined_score = f"{fuzzy_combined_score:.{FLOAT_PRECISION_DECIMALS}f}"

        source_row_index = parse_int(source_event.source_row_index)
        source_row_index = source_row_index if source_row_index is not None else 0
        matched_event = MatchedEvent(
            event_id=format_alignment_event_id(len(matched_events) + 1),
            source_type=source_event.source_type,
            source_row_index=source_row_index,
            source_timestamp=source_event.event_time,
            spotify_track_id=spotify_track_id,
            spotify_isrc=source_event.isrc,
            spotify_track_name=track_name,
            spotify_artist_names=artist_names,
            match_method=match_method,
            duration_delta_ms=duration_delta,
            fuzzy_title_score=fuzzy_title_score,
            fuzzy_artist_score=fuzzy_artist_score,
            fuzzy_combined_score=fuzzy_combined_score,
            ds001_id=matched_ds001_id,
            ds001_spotify_id=matched_row.get("spotify_id", ""),
            artist=matched_row.get("artist", ""),
            song=matched_row.get("song", ""),
            release=matched_row.get("release", ""),
            duration_ms=matched_row.get("duration_ms", ""),
            popularity=matched_row.get("popularity", ""),
            danceability=matched_row.get("danceability", ""),
            energy=matched_row.get("energy", ""),
            key=matched_row.get("key", ""),
            mode=matched_row.get("mode", ""),
            valence=matched_row.get("valence", ""),
            tempo=matched_row.get("tempo", ""),
            genres=matched_row.get("genres", ""),
            tags=matched_row.get("tags", ""),
            lang=matched_row.get("lang", ""),
            preference_weight=weight,
            interaction_count=max(1, int(round(weight * INTERACTION_COUNT_WEIGHT_SCALE))),
            interaction_type=INTERACTION_TYPE_HISTORY,
        )
        matched_events.append(matched_event.to_dict())
        trace_rows.append(trace.to_dict())

    return trace_rows, matched_events, unmatched_rows, match_counts


def _apply_preference_weight_policy(weights: list[float], mode: str, cap_per_event: float | None) -> float:
    if not weights:
        return 0.0
    if mode == "max":
        return max(weights)
    if mode == "mean":
        return sum(weights) / len(weights)
    if mode == "capped":
        cap = float(cap_per_event) if cap_per_event is not None else None
        if cap is None:
            return sum(weights)
        return sum(min(weight, cap) for weight in weights)
    return sum(weights)


def aggregate_matched_events(
    matched_events: list[dict[str, Any]],
    *,
    behavior_controls: AlignmentBehaviorControls | None = None,
    aggregation_policy: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    if aggregation_policy is not None:
        effective_policy = dict(aggregation_policy)
    elif behavior_controls is not None:
        effective_policy = dict(behavior_controls.aggregation_policy)
    else:
        effective_policy = {}
    preference_weight_mode = str(effective_policy.get("preference_weight_mode", "sum")).strip().lower() or "sum"
    preference_weight_cap_per_event = effective_policy.get("preference_weight_cap_per_event")

    aggregated: dict[str, AggregatedEvent] = {}
    preference_weights_by_id: dict[str, list[float]] = {}

    for raw_event in matched_events:
        event = MatchedEvent.from_dict(raw_event)
        ds001_id = event.ds001_id
        agg = aggregated.get(ds001_id)

        if agg is None:
            agg = AggregatedEvent.from_matched_event(event)
            aggregated[ds001_id] = agg
            preference_weights_by_id[ds001_id] = []

        agg.apply_event(event)
        preference_weights_by_id.setdefault(ds001_id, []).append(float(event.preference_weight))

    for ds001_id, agg in aggregated.items():
        agg.preference_weight_sum = round(
            _apply_preference_weight_policy(
                preference_weights_by_id.get(ds001_id, []),
                preference_weight_mode,
                float(preference_weight_cap_per_event) if preference_weight_cap_per_event is not None else None,
            ),
            6,
        )

    return {ds001_id: agg.to_dict() for ds001_id, agg in aggregated.items()}


_DS001_PASSTHROUGH_FIELDS: tuple[str, ...] = (
    "song",
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
)


def _make_influence_event(candidate: dict[str, Any], event_id: str, infl_weight: float) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "source_type": SOURCE_INFLUENCE,
        "source_row_index": 0,
        "source_timestamp": "",
        "spotify_track_id": candidate.get("spotify_id", ""),
        "spotify_isrc": "",
        "spotify_track_name": candidate.get("song", ""),
        "spotify_artist_names": candidate.get("artist", ""),
        "match_method": MATCH_METHOD_INFLUENCE_DIRECT,
        "duration_delta_ms": None,
        "ds001_id": resolve_ds001_id(candidate),
        "ds001_spotify_id": candidate.get("spotify_id", ""),
        "artist": candidate.get("artist", ""),
        **{f: candidate.get(f, "") for f in _DS001_PASSTHROUGH_FIELDS},
        "preference_weight": infl_weight,
        "interaction_count": max(1, int(round(infl_weight * INTERACTION_COUNT_WEIGHT_SCALE))),
        "interaction_type": INTERACTION_TYPE_INFLUENCE,
    }


def inject_influence_tracks(
    matched_events: list[dict[str, Any]],
    by_ds001_id: dict[str, dict[str, str]],
    run_config_path: str | None = None,
    *,
    context: AlignmentResolvedContext | None = None,
    behavior_controls: AlignmentBehaviorControls | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if context is not None:
        infl = dict(context.behavior_controls.influence_controls)
    elif behavior_controls is not None:
        infl = dict(behavior_controls.influence_controls)
    else:
        infl = dict(DEFAULT_INFLUENCE_CONTROLS)

    influence_injected_count = 0
    influence_skipped_ids: list[str] = []
    updated_events = [dict(event) for event in matched_events]

    if infl["influence_enabled"] and infl["influence_track_ids"]:
        infl_weight = float(infl["influence_preference_weight"])
        existing_ds001_ids = {str(event["ds001_id"]) for event in updated_events}
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
                for event in updated_events:
                    if str(event["ds001_id"]) == track_id:
                        existing_type = str(event.get("interaction_type", "")).strip().lower()
                        if existing_type and existing_type != INTERACTION_TYPE_INFLUENCE:
                            if "influence" not in existing_type.split(","):
                                event["interaction_type"] = INTERACTION_TYPE_HISTORY_INFLUENCE
                        else:
                            event["interaction_type"] = INTERACTION_TYPE_HISTORY_INFLUENCE
            else:
                updated_events.append(
                    _make_influence_event(
                        candidate,
                        format_influence_event_id(influence_injected_count + 1),
                        infl_weight,
                    )
                )
                existing_ds001_ids.add(track_id)

            influence_injected_count += 1

    return updated_events, {
        "enabled": bool(infl.get("influence_enabled", False)),
        "track_ids": list(infl.get("influence_track_ids") or []),
        "preference_weight": float(infl.get("influence_preference_weight") or DEFAULT_INFLUENCE_PREFERENCE_WEIGHT),
        "injected_count": influence_injected_count,
        "skipped_track_ids": influence_skipped_ids,
    }


def validate_match_rate(summary_counts: dict[str, int], threshold: float) -> None:
    if summary_counts["input_event_rows"] > 0 and threshold > 0.0:
        matched = (
            summary_counts["matched_by_spotify_id"]
            + summary_counts["matched_by_metadata"]
            + summary_counts.get("matched_by_fuzzy", 0)
        )
        match_rate = matched / summary_counts["input_event_rows"]
        if match_rate < threshold:
            raise RuntimeError(
                f"BL-003 match-rate validation failed: {match_rate:.1%} matched "
                f"({matched} events), below minimum threshold {threshold:.1%}. "
                f"This indicates high bias in the preference profile (built from only "
                f"{match_rate:.1%} of imported history). "
                f"Either increase the match-rate threshold in seed_controls if this is expected, "
                f"or investigate DS-001 corpus coverage and import data quality."
            )


def canonical_json_hash(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()


def build_seed_contract_payload(behavior_controls: AlignmentBehaviorControls) -> dict[str, Any]:
    match_strategy = dict(getattr(behavior_controls, "match_strategy", {}) or {})
    if not match_strategy:
        match_strategy = {
            "enable_spotify_id_match": True,
            "enable_metadata_match": True,
            "enable_fuzzy_match": True,
        }

    match_strategy_order = list(getattr(behavior_controls, "match_strategy_order", ()) or MATCH_STRATEGY_ORDER)
    temporal_controls = dict(getattr(behavior_controls, "temporal_controls", {}) or {})
    if not temporal_controls:
        temporal_controls = {
            "reference_mode": "system",
            "reference_now_utc": None,
        }

    aggregation_policy = dict(getattr(behavior_controls, "aggregation_policy", {}) or {})
    if not aggregation_policy:
        aggregation_policy = {
            "preference_weight_mode": "sum",
            "preference_weight_cap_per_event": None,
        }

    return {
        "seed_contract_schema_version": ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION,
        "input_scope": dict(behavior_controls.input_scope),
        "top_range_weights": dict(behavior_controls.top_range_weights),
        "source_base_weights": dict(behavior_controls.source_base_weights),
        "decay_half_lives": dict(behavior_controls.decay_half_lives),
        "match_rate_min_threshold": float(behavior_controls.match_rate_min_threshold),
        "weighting_policy": dict(behavior_controls.weighting_policy or {}),
        "influence_tracks": {
            "enabled": bool(behavior_controls.influence_controls.get("influence_enabled", False)),
            "track_ids": list(behavior_controls.influence_controls.get("influence_track_ids") or []),
            "preference_weight": float(behavior_controls.influence_controls.get("influence_preference_weight", 0.0)),
        },
        "fuzzy_matching": dict(behavior_controls.fuzzy_matching_controls),
        "match_strategy": match_strategy,
        "match_strategy_order": match_strategy_order,
        "temporal_controls": temporal_controls,
        "aggregation_policy": aggregation_policy,
        "text_normalization_rules": TEXT_NORMALIZATION_RULES,
        "artifact_naming_templates": {
            "alignment_event_id": EVENT_ID_ALIGNMENT_TEMPLATE,
            "influence_event_id": EVENT_ID_INFLUENCE_TEMPLATE,
        },
        "config_precedence_hierarchy": list(CONFIG_PRECEDENCE_HIERARCHY),
    }


def build_structural_contract_payload(structural_contract: AlignmentStructuralContract) -> dict[str, Any]:
    return {
        "structural_contract_schema_version": ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION,
        "spotify_export_filenames": dict(structural_contract.spotify_export_filenames),
        "output_filenames": dict(structural_contract.output_filenames),
        "trace_fieldnames": list(structural_contract.trace_fieldnames),
        "seed_table_fieldnames": list(structural_contract.seed_table_fieldnames),
        "default_relative_paths": {
            key: str(path)
            for key, path in structural_contract.default_relative_paths.items()
        },
        "artifact_schema_version": structural_contract.artifact_schema_version,
        "summary_schema_version": structural_contract.summary_schema_version,
        "source_scope_manifest_schema_version": structural_contract.source_scope_manifest_schema_version,
    }


def _write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with open_text_write(path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _serialize_row(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    to_dict = getattr(row, "to_dict", None)
    if callable(to_dict):
        payload = to_dict()
        if isinstance(payload, dict):
            return dict(payload)
    return {"value": str(row)}


def _serialize_aggregated_rows(aggregated: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ds001_id in sorted(aggregated.keys()):
        raw_agg = aggregated[ds001_id]
        rows.append(_serialize_row(raw_agg))
    return rows


def write_alignment_run_store(
    *,
    summary_payload: dict[str, Any],
    paths: AlignmentPaths,
    match_result: _MatchAggregationResult,
) -> Path:
    pipeline_run_id = (os.getenv("BL_PIPELINE_RUN_ID") or "").strip()
    if pipeline_run_id:
        run_id = pipeline_run_id
    else:
        run_id = f"BL003-STANDALONE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    run_store_path = resolve_run_store_path(impl_root(), run_id)
    outputs = _mapping(summary_payload.get("outputs"))
    output_hashes = _mapping(outputs.get("sha256"))
    manifest_payload = json.loads(paths.source_scope_manifest_path.read_text(encoding="utf-8"))

    with SQLiteRunStore(run_store_path) as run_store:
        generated_at_utc = str(summary_payload.get("generated_at_utc") or utc_now())
        run_store.upsert_run(
            run_id=run_id,
            created_at_utc=generated_at_utc,
            source_stage_id="BL-003",
        )
        stage_run_pk = run_store.insert_stage_run(
            run_id=run_id,
            stage_id="BL-003",
            stage_run_ref=generated_at_utc,
            generated_at_utc=generated_at_utc,
            status="pass",
            summary=summary_payload,
        )

        run_store.insert_artifact(
            stage_run_pk=stage_run_pk,
            artifact_key="matched_events",
            artifact_type="jsonl",
            artifact_path=str(paths.output_dir / ALIGNMENT_OUTPUT_FILENAMES["matched_jsonl"]),
            sha256=str(output_hashes.get("matched_events_jsonl") or "") or None,
            rows=[_serialize_row(row) for row in match_result.matched_events],
        )
        run_store.insert_artifact(
            stage_run_pk=stage_run_pk,
            artifact_key="seed_table",
            artifact_type="csv",
            artifact_path=str(paths.output_dir / ALIGNMENT_OUTPUT_FILENAMES["seed_table_csv"]),
            sha256=str(output_hashes.get("seed_table_csv") or "") or None,
            rows=_serialize_aggregated_rows(match_result.aggregated),
        )
        run_store.insert_artifact(
            stage_run_pk=stage_run_pk,
            artifact_key="trace",
            artifact_type="csv",
            artifact_path=str(paths.output_dir / ALIGNMENT_OUTPUT_FILENAMES["trace_csv"]),
            sha256=str(output_hashes.get("trace_csv") or "") or None,
            rows=[_serialize_row(row) for row in match_result.trace_rows],
        )
        run_store.insert_artifact(
            stage_run_pk=stage_run_pk,
            artifact_key="unmatched",
            artifact_type="csv",
            artifact_path=str(paths.output_dir / ALIGNMENT_OUTPUT_FILENAMES["unmatched_csv"]),
            sha256=str(output_hashes.get("unmatched_csv") or "") or None,
            rows=[_serialize_row(row) for row in match_result.unmatched_rows],
        )
        run_store.insert_artifact(
            stage_run_pk=stage_run_pk,
            artifact_key="summary",
            artifact_type="json",
            artifact_path=str(paths.summary_path),
            sha256=None,
            payload=summary_payload,
        )
        run_store.insert_artifact(
            stage_run_pk=stage_run_pk,
            artifact_key="source_scope_manifest",
            artifact_type="json",
            artifact_path=str(paths.source_scope_manifest_path),
            sha256=str(output_hashes.get("source_scope_manifest_json") or "") or None,
            payload=manifest_payload,
        )

    return run_store_path


def write_alignment_outputs(
    output_dir: Path,
    matched_events: list[dict[str, Any]],
    aggregated: dict[str, dict[str, Any]],
    trace_rows: list[dict[str, Any]],
    unmatched_rows: list[dict[str, Any]],
) -> dict[str, Path]:
    matched_jsonl_path = output_dir / ALIGNMENT_OUTPUT_FILENAMES["matched_jsonl"]
    seed_table_path = output_dir / ALIGNMENT_OUTPUT_FILENAMES["seed_table_csv"]
    trace_path = output_dir / ALIGNMENT_OUTPUT_FILENAMES["trace_csv"]
    unmatched_path = output_dir / ALIGNMENT_OUTPUT_FILENAMES["unmatched_csv"]

    with open_text_write(matched_jsonl_path) as handle:
        for row in matched_events:
            payload = row.to_dict() if isinstance(row, MatchedEvent) else row
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")

    seed_rows_output: list[dict[str, Any]] = []
    for ds001_id in sorted(aggregated.keys()):
        raw_agg = aggregated[ds001_id]
        agg = raw_agg.to_dict() if isinstance(raw_agg, AggregatedEvent) else raw_agg
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
                "preference_weight_sum": f"{float(agg['preference_weight_sum']):.{FLOAT_PRECISION_DECIMALS}f}",
                "preference_weight_max": f"{float(agg['preference_weight_max']):.{FLOAT_PRECISION_DECIMALS}f}",
                "source_types": "|".join(sorted(agg["source_types"])),
                "interaction_types": "|".join(sorted(agg["interaction_types"])) if agg["interaction_types"] else INTERACTION_TYPE_HISTORY,
                "spotify_track_ids": "|".join(sorted(agg["spotify_track_ids"])),
            }
        )

    _write_csv_rows(seed_table_path, SEED_TABLE_FIELDNAMES, seed_rows_output)
    _write_csv_rows(trace_path, TRACE_FIELDNAMES, trace_rows)
    _write_csv_rows(unmatched_path, TRACE_FIELDNAMES, unmatched_rows)

    return {
        "matched_jsonl": matched_jsonl_path,
        "seed_table_csv": seed_table_path,
        "trace_csv": trace_path,
        "unmatched_csv": unmatched_path,
    }


def write_source_scope_manifest(
    manifest_path: Path,
    runtime_scope: dict[str, Any],
    input_scope: dict[str, Any],
    scope_filter_stats: dict[str, Any],
    seed_contract: dict[str, Any] | None = None,
    structural_contract: dict[str, Any] | None = None,
) -> None:
    manifest = {
        "artifact_schema_version": ALIGNMENT_SOURCE_SCOPE_MANIFEST_SCHEMA_VERSION,
        "artifact_contract_version": ALIGNMENT_ARTIFACT_SCHEMA_VERSION,
        "generated_at_utc": utc_now(),
        "config_source": runtime_scope["config_source"],
        "run_config_path": runtime_scope["run_config_path"],
        "run_config_schema_version": runtime_scope["run_config_schema_version"],
        "input_scope": input_scope,
        "rows_available": scope_filter_stats["rows_available"],
        "rows_selected": scope_filter_stats["rows_selected"],
    }
    if isinstance(seed_contract, dict) and seed_contract:
        manifest["seed_contract"] = {
            **seed_contract,
            "contract_hash": canonical_json_hash(seed_contract),
        }
    if isinstance(structural_contract, dict) and structural_contract:
        manifest["structural_contract"] = {
            **structural_contract,
            "contract_hash": canonical_json_hash(structural_contract),
        }
    with open_text_write(manifest_path) as handle:
        json.dump(manifest, handle, indent=JSON_INDENT_SPACES, ensure_ascii=True)


def _build_summary_payload(summary_path: Path, context: AlignmentSummaryContext) -> dict[str, Any]:
    summary_counts = context.metrics.summary_counts
    seed_contract = build_seed_contract_payload(context.behavior_controls)
    structural_contract = build_structural_contract_payload(context.structural_contract)
    seed_aggregation_controls = _mapping(context.behavior_controls.seed_aggregation_health)
    warn_min_ratio = safe_float(seed_aggregation_controls.get("warn_min_ratio"), 0.01)
    collapse_max_rows = max(0, safe_int(seed_aggregation_controls.get("collapse_max_rows"), 1))
    seed_aggregation_health = build_seed_aggregation_health(
        matched_events_rows=context.metrics.matched_events_rows,
        seed_table_rows=context.metrics.seed_table_rows,
        warn_min_ratio=warn_min_ratio,
        collapse_max_rows=collapse_max_rows,
    )

    matched_count = (
        summary_counts["matched_by_spotify_id"]
        + summary_counts["matched_by_metadata"]
        + summary_counts.get("matched_by_fuzzy", 0)
    )
    input_rows = summary_counts["input_event_rows"]
    actual_match_rate = round(matched_count / input_rows if input_rows > 0 else 0.0, SUMMARY_RATE_PRECISION_DECIMALS)

    source_scope_manifest_path = context.output_paths.get(
        "source_scope_manifest",
        summary_path.parent / ALIGNMENT_OUTPUT_FILENAMES["source_scope_manifest_json"],
    )

    summary: dict[str, Any] = {
        "task": SUMMARY_TASK_NAME,
        "summary_schema_version": ALIGNMENT_SUMMARY_SCHEMA_VERSION,
        "artifact_contract_version": ALIGNMENT_ARTIFACT_SCHEMA_VERSION,
        "generated_at_utc": utc_now(),
        "elapsed_seconds": context.elapsed_seconds,
        "inputs": {
            "ds001_candidates": str(context.ds001_path),
            "ds001_candidates_sha256": sha256_of_file(context.ds001_path),
            "spotify_export_dir": str(context.spotify_dir),
            "files": {
                "spotify_top_tracks_flat_csv": str(context.top_path),
                "spotify_saved_tracks_flat_csv": str(context.saved_path),
                "spotify_playlist_items_flat_csv": str(context.playlist_items_path),
                "spotify_recently_played_flat_csv": str(context.recently_played_path),
            },
            "selection": context.export_selection,
            "config_source": context.runtime_scope["config_source"],
            "run_config_path": context.runtime_scope["run_config_path"],
            "run_config_schema_version": context.runtime_scope["run_config_schema_version"],
            "input_scope": context.input_scope,
            "influence_tracks": context.influence_contract,
            "fuzzy_matching": dict(context.fuzzy_matching_controls),
            "seed_contract": {
                **seed_contract,
                "contract_hash": canonical_json_hash(seed_contract),
            },
            "structural_contract": {
                **structural_contract,
                "contract_hash": canonical_json_hash(structural_contract),
            },
            "selected_sources_expected": context.expected_sources,
            "selected_sources_available": context.available_sources,
            "missing_selected_sources": context.missing_selected_sources,
            "allow_missing_selected_sources": bool(context.allow_missing_selected_sources),
        },
        "source_stats": context.source_stats,
        "source_scope_filtering": context.scope_filter_stats,
        "counts": {
            **summary_counts,
            "matched_events_rows": context.metrics.matched_events_rows,
            "seed_table_rows": context.metrics.seed_table_rows,
            "trace_rows": context.metrics.trace_rows,
            "unmatched_rows": context.metrics.unmatched_rows,
            "seed_aggregation_health": seed_aggregation_health,
            "match_rate_validation": {
                "threshold_enforced": context.match_rate_min_threshold > 0.0,
                "min_threshold": round(context.match_rate_min_threshold, SUMMARY_RATE_PRECISION_DECIMALS),
                "actual_match_rate": actual_match_rate,
                "status": "pass" if input_rows == 0 or actual_match_rate >= context.match_rate_min_threshold else "fail",
            },
        },
        "outputs": {
            "artifact_schema_version": ALIGNMENT_ARTIFACT_SCHEMA_VERSION,
            "source_scope_manifest_schema_version": ALIGNMENT_SOURCE_SCOPE_MANIFEST_SCHEMA_VERSION,
            "matched_events_jsonl": str(context.output_paths["matched_jsonl"]),
            "seed_table_csv": str(context.output_paths["seed_table_csv"]),
            "trace_csv": str(context.output_paths["trace_csv"]),
            "unmatched_csv": str(context.output_paths["unmatched_csv"]),
            "summary_json": str(summary_path),
            "source_scope_manifest_json": str(source_scope_manifest_path),
            "sha256": {
                "matched_events_jsonl": sha256_of_file(context.output_paths["matched_jsonl"]),
                "seed_table_csv": sha256_of_file(context.output_paths["seed_table_csv"]),
                "trace_csv": sha256_of_file(context.output_paths["trace_csv"]),
                "unmatched_csv": sha256_of_file(context.output_paths["unmatched_csv"]),
                "source_scope_manifest_json": sha256_of_file(source_scope_manifest_path),
            },
        },
        "notes": {
            "policy": SUMMARY_NOTE_POLICY,
            "logging": SUMMARY_NOTE_LOGGING,
            "seed_table_enrichment": SUMMARY_NOTE_SEED_TABLE_ENRICHMENT,
        },
    }
    return summary


def build_and_write_summary_from_context(summary_path: Path, context: AlignmentSummaryContext) -> dict[str, Any]:
    summary = _build_summary_payload(summary_path, context)
    with open_text_write(summary_path) as handle:
        json.dump(summary, handle, indent=JSON_INDENT_SPACES, ensure_ascii=True)
    return summary


class AlignmentStage:
    """Object-oriented BL-003 alignment workflow shell."""

    def __init__(
        self,
        root: Path | None = None,
        *,
        ds001_path: Path | None = None,
        spotify_dir: Path | None = None,
        output_dir: Path | None = None,
        allow_missing_selected_sources: bool = False,
    ) -> None:
        self.root = root if root is not None else impl_root()
        self._ds001_path_override = ds001_path
        self._spotify_dir_override = spotify_dir
        self._output_dir_override = output_dir
        self.allow_missing_selected_sources = allow_missing_selected_sources

    def resolve_paths(self) -> AlignmentPaths:
        defaults = ALIGNMENT_DEFAULT_RELATIVE_PATHS
        ds001 = self._ds001_path_override or self.root / defaults["ds001_candidates"]
        spotify = self._spotify_dir_override or self.root / defaults["spotify_export_dir"]
        output = self._output_dir_override or self.root / defaults["output_dir"]
        return AlignmentPaths(
            ds001_path=ds001,
            spotify_dir=spotify,
            output_dir=output,
            top_path=spotify / SPOTIFY_EXPORT_FILENAMES["top_tracks"],
            saved_path=spotify / SPOTIFY_EXPORT_FILENAMES["saved_tracks"],
            playlist_items_path=spotify / SPOTIFY_EXPORT_FILENAMES["playlist_items"],
            recently_played_path=spotify / SPOTIFY_EXPORT_FILENAMES["recently_played"],
            summary_path=output / ALIGNMENT_OUTPUT_FILENAMES["summary_json"],
            source_scope_manifest_path=output / ALIGNMENT_OUTPUT_FILENAMES["source_scope_manifest_json"],
        )

    @staticmethod
    def resolve_runtime_controls() -> AlignmentResolvedContext:
        return resolve_alignment_context()

    @staticmethod
    def load_export_selection(spotify_export_dir: Path) -> dict[str, object]:
        summary_path = spotify_export_dir / "spotify_export_run_summary.json"
        if not summary_path.exists():
            return {}
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"BL-003 could not parse BL-002 export summary: {summary_path}") from exc
        selection = payload.get("selection")
        if not isinstance(selection, dict):
            raise RuntimeError("BL-003 export summary missing required selection block: " f"{summary_path}")
        return selection

    @staticmethod
    def resolve_expected_sources(
        *,
        runtime_scope: dict[str, object],
        input_scope: dict[str, object],
        export_selection: dict[str, object],
    ) -> dict[str, bool]:
        if runtime_scope.get("config_source") == "run_config":
            return {
                source: bool(input_scope.get(str(SOURCE_SCOPE_SPECS[source]["input_scope_flag"]), True))
                for source in SOURCE_TYPES
            }
        return {
            source: bool(export_selection.get(str(SOURCE_SCOPE_SPECS[source]["export_selection_flag"]), False))
            for source in SOURCE_TYPES
        }

    def enforce_selected_source_requirements(
        self,
        *,
        expected_sources: dict[str, bool],
        available_sources: dict[str, bool],
    ) -> list[str]:
        missing_selected_sources = [
            source
            for source, expected in expected_sources.items()
            if expected and not available_sources.get(source, False)
        ]
        if missing_selected_sources and not self.allow_missing_selected_sources:
            raise RuntimeError(
                "BL-003 strict selected-source check failed. Missing required source files from BL-002 selection: "
                f"{', '.join(missing_selected_sources)}. Re-run BL-002 export or pass "
                "--allow-missing-selected-sources to continue."
            )
        return missing_selected_sources

    def load_source_rows(self, paths: AlignmentPaths) -> AlignmentSourceRows:
        def load_if_present(path: Path) -> tuple[list[dict[str, str]], bool]:
            if not path.exists():
                return [], False
            return load_csv_rows(path), True

        top_rows, top_exists = load_if_present(paths.top_path)
        saved_rows, saved_exists = load_if_present(paths.saved_path)
        playlist_rows, playlist_exists = load_if_present(paths.playlist_items_path)
        recent_rows, recent_exists = load_if_present(paths.recently_played_path)

        return AlignmentSourceRows(
            top_rows=top_rows,
            saved_rows=saved_rows,
            playlist_rows=playlist_rows,
            recent_rows=recent_rows,
            top_exists=top_exists,
            saved_exists=saved_exists,
            playlist_exists=playlist_exists,
            recent_exists=recent_exists,
        )

    def _resolve_scope_selection(
        self,
        *,
        source_rows: AlignmentSourceRows,
        context: AlignmentResolvedContext,
        paths: AlignmentPaths,
    ) -> _ScopeSelectionResult:
        runtime_scope = context.runtime_scope
        input_scope = dict(context.behavior_controls.input_scope)
        selected_rows, scope_filter_stats = apply_input_scope_filters(
            source_rows.top_rows,
            source_rows.saved_rows,
            source_rows.playlist_rows,
            source_rows.recent_rows,
            context.behavior_controls,
        )

        export_selection = self.load_export_selection(paths.spotify_dir)
        expected_sources = self.resolve_expected_sources(
            runtime_scope=runtime_scope,
            input_scope=input_scope,
            export_selection=export_selection,
        )

        available_sources = {
            source: bool(getattr(source_rows, str(SOURCE_SCOPE_SPECS[source]["exists_attr"])))
            for source in SOURCE_TYPES
        }
        missing_selected_sources = self.enforce_selected_source_requirements(
            expected_sources=expected_sources,
            available_sources=available_sources,
        )

        source_stats = {
            source: {
                "file_present": bool(getattr(source_rows, str(SOURCE_SCOPE_SPECS[source]["exists_attr"]))),
                "rows_available": len(getattr(source_rows, str(SOURCE_SCOPE_SPECS[source]["rows_attr"]))),
                "rows_selected": len(selected_rows[source]),
            }
            for source in SOURCE_TYPES
        }
        return _ScopeSelectionResult(
            selected_rows=selected_rows,
            scope_filter_stats=scope_filter_stats,
            runtime_scope=runtime_scope,
            input_scope=input_scope,
            export_selection=export_selection,
            expected_sources=expected_sources,
            available_sources=available_sources,
            missing_selected_sources=missing_selected_sources,
            source_stats=source_stats,
        )

    def _run_matching_and_aggregation(
        self,
        *,
        paths: AlignmentPaths,
        selected_rows: dict[str, list[dict[str, str]]],
        context: AlignmentResolvedContext,
    ) -> _MatchAggregationResult:
        ds001_rows = [normalize_ds001_row_identity(row) for row in load_csv_rows(paths.ds001_path)]
        by_spotify_id, by_title_artist, by_artist = build_ds001_indices(ds001_rows)
        by_ds001_id = {
            resolve_ds001_id(row): row
            for row in ds001_rows
            if resolve_ds001_id(row)
        }
        events: list[dict[str, str]] = []
        for source in SOURCE_TYPES:
            events.extend(to_event_rows(source, selected_rows[source]))

        trace_rows, matched_events, unmatched_rows, match_counts = match_events(
            events,
            by_spotify_id,
            by_title_artist,
            by_artist,
            context=context,
        )
        summary_counts = {"input_event_rows": len(events), **match_counts}

        matched_events_with_influence, influence_contract = inject_influence_tracks(
            matched_events,
            by_ds001_id,
            context=context,
        )

        aggregated = aggregate_matched_events(
            matched_events_with_influence,
            behavior_controls=context.behavior_controls,
        )
        return _MatchAggregationResult(
            trace_rows=trace_rows,
            matched_events=matched_events_with_influence,
            unmatched_rows=unmatched_rows,
            summary_counts=summary_counts,
            influence_contract=influence_contract,
            aggregated=aggregated,
        )

    def _write_outputs_and_summary(
        self,
        *,
        elapsed_seconds: float,
        paths: AlignmentPaths,
        scope_result: _ScopeSelectionResult,
        match_result: _MatchAggregationResult,
        behavior_controls: Any,
        structural_contract_model: AlignmentStructuralContract,
    ) -> None:
        output_paths: dict[str, Path] = {}
        seed_contract = build_seed_contract_payload(behavior_controls)
        structural_contract = build_structural_contract_payload(structural_contract_model)

        validate_match_rate(match_result.summary_counts, float(behavior_controls.match_rate_min_threshold))

        summary_context = AlignmentSummaryContext(
            elapsed_seconds=elapsed_seconds,
            ds001_path=paths.ds001_path,
            spotify_dir=paths.spotify_dir,
            top_path=paths.top_path,
            saved_path=paths.saved_path,
            playlist_items_path=paths.playlist_items_path,
            recently_played_path=paths.recently_played_path,
            export_selection=scope_result.export_selection,
            runtime_scope=scope_result.runtime_scope,
            input_scope=scope_result.input_scope,
            influence_contract=match_result.influence_contract,
            expected_sources=scope_result.expected_sources,
            available_sources=scope_result.available_sources,
            missing_selected_sources=scope_result.missing_selected_sources,
            allow_missing_selected_sources=self.allow_missing_selected_sources,
            source_stats=scope_result.source_stats,
            scope_filter_stats=scope_result.scope_filter_stats,
            behavior_controls=behavior_controls,
            structural_contract=structural_contract_model,
            metrics=AlignmentSummaryMetrics(
                summary_counts=match_result.summary_counts,
                matched_events_rows=len(match_result.matched_events),
                seed_table_rows=len(match_result.aggregated),
                trace_rows=len(match_result.trace_rows),
                unmatched_rows=len(match_result.unmatched_rows),
            ),
            output_paths=output_paths,
            match_rate_min_threshold=float(behavior_controls.match_rate_min_threshold),
            fuzzy_matching_controls=dict(behavior_controls.fuzzy_matching_controls),
        )

        output_paths = write_alignment_outputs(
            paths.output_dir,
            match_result.matched_events,
            match_result.aggregated,
            match_result.trace_rows,
            match_result.unmatched_rows,
        )
        write_source_scope_manifest(
            paths.source_scope_manifest_path,
            scope_result.runtime_scope,
            scope_result.input_scope,
            scope_result.scope_filter_stats,
            seed_contract=seed_contract,
            structural_contract=structural_contract,
        )
        output_paths["source_scope_manifest"] = paths.source_scope_manifest_path
        summary_context.output_paths.update(output_paths)
        summary_payload = build_and_write_summary_from_context(paths.summary_path, summary_context)
        run_store_path = write_alignment_run_store(
            summary_payload=summary_payload,
            paths=paths,
            match_result=match_result,
        )
        outputs = _mapping(summary_payload.get("outputs"))
        outputs["sqlite_run_store"] = str(run_store_path)
        summary_payload["outputs"] = outputs
        with open_text_write(paths.summary_path) as handle:
            json.dump(summary_payload, handle, indent=JSON_INDENT_SPACES, ensure_ascii=True)

    def run(self) -> AlignmentRunArtifacts:
        t0 = time.time()
        paths = self.resolve_paths()
        if not paths.ds001_path.exists():
            raise FileNotFoundError(f"DS-001 working dataset not found: {paths.ds001_path}")

        source_rows = self.load_source_rows(paths)
        context: AlignmentResolvedContext = self.resolve_runtime_controls()
        scope_result = self._resolve_scope_selection(
            source_rows=source_rows,
            context=context,
            paths=paths,
        )

        match_result = self._run_matching_and_aggregation(
            paths=paths,
            selected_rows=scope_result.selected_rows,
            context=context,
        )

        paths.output_dir.mkdir(parents=True, exist_ok=True)
        elapsed_seconds = round(time.time() - t0, 3)
        self._write_outputs_and_summary(
            elapsed_seconds=elapsed_seconds,
            paths=paths,
            scope_result=scope_result,
            match_result=match_result,
            behavior_controls=context.behavior_controls,
            structural_contract_model=context.structural_contract,
        )

        return AlignmentRunArtifacts(
            summary_path=paths.summary_path,
            summary_counts=match_result.summary_counts,
            matched_events_rows=len(match_result.matched_events),
            seed_table_rows=len(match_result.aggregated),
            trace_rows=len(match_result.trace_rows),
            unmatched_rows=len(match_result.unmatched_rows),
        )


def parse_args() -> argparse.Namespace:
    root = impl_root()
    parser = argparse.ArgumentParser(
        description="BL-003 DS-001: Build Spotify-aligned seed tables with full trace logging."
    )
    parser.add_argument(
        "--ds001-candidates",
        type=Path,
        default=root / ALIGNMENT_DEFAULT_RELATIVE_PATHS["ds001_candidates"],
    )
    parser.add_argument(
        "--spotify-export-dir",
        type=Path,
        default=root / ALIGNMENT_DEFAULT_RELATIVE_PATHS["spotify_export_dir"],
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / ALIGNMENT_DEFAULT_RELATIVE_PATHS["output_dir"],
    )
    parser.add_argument(
        "--allow-missing-selected-sources",
        action="store_true",
        help="Do not fail when BL-002 selection indicates a source should exist but its flat CSV is missing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts = AlignmentStage(
        ds001_path=args.ds001_candidates,
        spotify_dir=args.spotify_export_dir,
        output_dir=args.output_dir,
        allow_missing_selected_sources=bool(args.allow_missing_selected_sources),
    ).run()

    print(f"input_event_rows={artifacts.summary_counts['input_event_rows']}")
    print(f"matched_by_spotify_id={artifacts.summary_counts['matched_by_spotify_id']}")
    print(f"matched_by_metadata={artifacts.summary_counts['matched_by_metadata']}")
    print(f"matched_by_fuzzy={artifacts.summary_counts.get('matched_by_fuzzy', 0)}")
    print(f"unmatched={artifacts.summary_counts['unmatched']}")
    print(f"matched_events_rows={artifacts.matched_events_rows}")
    print(f"seed_table_rows={artifacts.seed_table_rows}")
    print(f"trace_rows={artifacts.trace_rows}")
    print(f"unmatched_rows={artifacts.unmatched_rows}")
    print(f"summary_path={artifacts.summary_path}")


if __name__ == "__main__":
    main()
