"""String constants and fixed filenames used by BL-003 alignment."""

from __future__ import annotations

from pathlib import Path
from typing import Final


SOURCE_TOP_TRACKS: Final[str] = "top_tracks"
SOURCE_SAVED_TRACKS: Final[str] = "saved_tracks"
SOURCE_PLAYLIST_ITEMS: Final[str] = "playlist_items"
SOURCE_RECENTLY_PLAYED: Final[str] = "recently_played"
SOURCE_USER_CSV: Final[str] = "user_csv"
SOURCE_INFLUENCE: Final[str] = "influence"

SOURCE_TYPES: Final[tuple[str, ...]] = (
    SOURCE_TOP_TRACKS,
    SOURCE_SAVED_TRACKS,
    SOURCE_PLAYLIST_ITEMS,
    SOURCE_RECENTLY_PLAYED,
    SOURCE_USER_CSV,
)

SOURCE_RESILIENCE_REQUIRED: Final[str] = "required"
SOURCE_RESILIENCE_OPTIONAL: Final[str] = "optional"
SOURCE_RESILIENCE_ADVISORY: Final[str] = "advisory"
SOURCE_RESILIENCE_ALLOWED_MODES: Final[tuple[str, ...]] = (
    SOURCE_RESILIENCE_REQUIRED,
    SOURCE_RESILIENCE_OPTIONAL,
    SOURCE_RESILIENCE_ADVISORY,
)
DEFAULT_SOURCE_RESILIENCE_POLICY: Final[dict[str, str]] = {
    SOURCE_TOP_TRACKS: SOURCE_RESILIENCE_REQUIRED,
    SOURCE_SAVED_TRACKS: SOURCE_RESILIENCE_OPTIONAL,
    SOURCE_PLAYLIST_ITEMS: SOURCE_RESILIENCE_OPTIONAL,
    SOURCE_RECENTLY_PLAYED: SOURCE_RESILIENCE_ADVISORY,
    SOURCE_USER_CSV: SOURCE_RESILIENCE_ADVISORY,
}

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
    SOURCE_USER_CSV: {
        "input_scope_flag": "include_user_csv",
        "export_selection_flag": "include_user_csv",
        "rows_attr": "user_csv_rows",
        "exists_attr": "user_csv_exists",
    },
}

SPOTIFY_EXPORT_FILENAMES: Final[dict[str, str]] = {
    SOURCE_TOP_TRACKS: "spotify_top_tracks_flat.csv",
    SOURCE_SAVED_TRACKS: "spotify_saved_tracks_flat.csv",
    SOURCE_PLAYLIST_ITEMS: "spotify_playlist_items_flat.csv",
    SOURCE_RECENTLY_PLAYED: "spotify_recently_played_flat.csv",
    SOURCE_USER_CSV: "user_csv_flat.csv",
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
    "fuzzy_album_score",
    "fuzzy_pass_used",
    "fuzzy_artist_attempt_count",
    "fuzzy_candidate_count",
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
    "match_confidence_score",
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
UNMATCHED_REASON_FUZZY_ARTIST_THRESHOLD_FAILED: Final[str] = "fuzzy_artist_threshold_failed"
UNMATCHED_REASON_FUZZY_TITLE_THRESHOLD_FAILED: Final[str] = "fuzzy_title_threshold_failed"
UNMATCHED_REASON_FUZZY_COMBINED_THRESHOLD_FAILED: Final[str] = "fuzzy_combined_threshold_failed"
UNMATCHED_REASON_FUZZY_DURATION_REJECTED: Final[str] = "fuzzy_duration_rejected"

INTERACTION_TYPE_HISTORY: Final[str] = "history"
INTERACTION_TYPE_INFLUENCE: Final[str] = "influence"
INTERACTION_TYPE_HISTORY_INFLUENCE: Final[str] = "history,influence"
DEFAULT_INFLUENCE_PREFERENCE_WEIGHT: Final[float] = 1.0

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


def format_alignment_event_id(index: int) -> str:
    return EVENT_ID_ALIGNMENT_TEMPLATE.format(index=index)


def format_influence_event_id(index: int) -> str:
    return EVENT_ID_INFLUENCE_TEMPLATE.format(index=index)
