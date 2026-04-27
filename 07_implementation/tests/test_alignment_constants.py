"""Baseline contract tests for alignment constants extraction."""

from __future__ import annotations

# pyright: reportMissingImports=false

from alignment import (
    ALIGNMENT_OUTPUT_FILENAMES,
    ARTIST_NAME_DELIMITERS,
    INTERACTION_TYPE_HISTORY,
    INTERACTION_TYPE_HISTORY_INFLUENCE,
    INTERACTION_TYPE_INFLUENCE,
    MATCH_METHOD_FUZZY_TITLE_ARTIST,
    MATCH_METHOD_INFLUENCE_DIRECT,
    MATCH_METHOD_METADATA_FALLBACK,
    MATCH_METHOD_SPOTIFY_ID_EXACT,
    MATCH_STATUS_AMBIGUOUS,
    MATCH_STATUS_INVALID,
    MATCH_STATUS_MATCHED,
    MATCH_STATUS_UNMATCHED,
    SEED_TABLE_FIELDNAMES,
    SOURCE_TYPES,
    SPOTIFY_EXPORT_FILENAMES,
    SUMMARY_TASK_NAME,
    TRACE_FIELDNAMES,
    format_alignment_event_id,
    format_influence_event_id,
)


def test_source_types_contract_order_is_stable() -> None:
    assert SOURCE_TYPES == (
        "top_tracks",
        "saved_tracks",
        "playlist_items",
        "recently_played",
        "user_csv",
    )


def test_export_filename_contract_is_stable() -> None:
    assert SPOTIFY_EXPORT_FILENAMES == {
        "top_tracks": "spotify_top_tracks_flat.csv",
        "saved_tracks": "spotify_saved_tracks_flat.csv",
        "playlist_items": "spotify_playlist_items_flat.csv",
        "recently_played": "spotify_recently_played_flat.csv",
        "user_csv": "user_csv_flat.csv",
    }


def test_output_filename_contract_is_stable() -> None:
    assert ALIGNMENT_OUTPUT_FILENAMES == {
        "matched_jsonl": "bl003_ds001_spotify_matched_events.jsonl",
        "seed_table_csv": "bl003_ds001_spotify_seed_table.csv",
        "trace_csv": "bl003_ds001_spotify_trace.csv",
        "unmatched_csv": "bl003_ds001_spotify_unmatched.csv",
        "summary_json": "bl003_ds001_spotify_summary.json",
        "source_scope_manifest_json": "bl003_source_scope_manifest.json",
    }


def test_label_contracts_are_stable() -> None:
    assert MATCH_STATUS_MATCHED == "matched"
    assert MATCH_STATUS_UNMATCHED == "unmatched"
    assert MATCH_STATUS_AMBIGUOUS == "ambiguous"
    assert MATCH_STATUS_INVALID == "invalid"
    assert MATCH_METHOD_SPOTIFY_ID_EXACT == "spotify_id_exact"
    assert MATCH_METHOD_METADATA_FALLBACK == "metadata_fallback"
    assert MATCH_METHOD_FUZZY_TITLE_ARTIST == "fuzzy_title_artist"
    assert MATCH_METHOD_INFLUENCE_DIRECT == "influence_direct"
    assert INTERACTION_TYPE_HISTORY == "history"
    assert INTERACTION_TYPE_INFLUENCE == "influence"
    assert INTERACTION_TYPE_HISTORY_INFLUENCE == "history,influence"


def test_event_id_templates_are_stable() -> None:
    assert format_alignment_event_id(1) == "ds001_align_000001"
    assert format_influence_event_id(7) == "ds001_influence_000007"


def test_summary_and_artist_delimiter_contracts_are_stable() -> None:
    assert SUMMARY_TASK_NAME == "BL-003-DS001-spotify-seed-build"
    assert ARTIST_NAME_DELIMITERS == ("|", ";", ",")


def test_csv_schema_field_order_contracts_are_stable() -> None:
    assert TRACE_FIELDNAMES == [
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
    assert SEED_TABLE_FIELDNAMES == [
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
