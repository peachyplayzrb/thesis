"""Output writers for BL-003 alignment artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from shared_utils.hashing import canonical_json_hash as _canonical_json_hash
from shared_utils.io_utils import open_text_write, sha256_of_file, utc_now


TRACE_FIELDNAMES: list[str] = [
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

SEED_TABLE_FIELDNAMES: list[str] = [
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


def canonical_json_hash(payload: object) -> str:
    return _canonical_json_hash(payload, uppercase=True)


def _write_csv_rows(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, Any]],
) -> None:
    with open_text_write(path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_alignment_outputs(
    output_dir: Path,
    matched_events: list[dict[str, Any]],
    aggregated: dict[str, dict[str, Any]],
    trace_rows: list[dict[str, Any]],
    unmatched_rows: list[dict[str, Any]],
) -> dict[str, Path]:
    """Write matched JSONL, seed table, trace, and unmatched CSVs. Return paths dict."""
    matched_jsonl_path = output_dir / "bl003_ds001_spotify_matched_events.jsonl"
    seed_table_path = output_dir / "bl003_ds001_spotify_seed_table.csv"
    trace_path = output_dir / "bl003_ds001_spotify_trace.csv"
    unmatched_path = output_dir / "bl003_ds001_spotify_unmatched.csv"

    with open_text_write(matched_jsonl_path) as handle:
        for row in matched_events:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    seed_rows_output: list[dict[str, Any]] = []
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
                "interaction_types": (
                    "|".join(sorted(agg["interaction_types"]))
                    if agg["interaction_types"]
                    else "history"
                ),
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
) -> None:
    """Write the BL-003 source-scope manifest JSON."""
    manifest = {
        "generated_at_utc": utc_now(),
        "config_source": runtime_scope["config_source"],
        "run_config_path": runtime_scope["run_config_path"],
        "run_config_schema_version": runtime_scope["run_config_schema_version"],
        "input_scope": input_scope,
        "rows_available": scope_filter_stats["rows_available"],
        "rows_selected": scope_filter_stats["rows_selected"],
    }
    with open_text_write(manifest_path) as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=True)
