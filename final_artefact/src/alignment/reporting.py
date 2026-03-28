"""
BL-003 output writing and summary assembly.

Handles all file I/O for the alignment stage: primary artifacts (matched JSONL,
seed table, trace, unmatched CSVs), the source-scope manifest, match-rate
validation, and the BL-003 summary JSON.
"""

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


def validate_match_rate(summary_counts: dict[str, int], threshold: float) -> None:
    """Raise RuntimeError if the matched fraction falls below the configured threshold."""
    if summary_counts["input_event_rows"] > 0 and threshold > 0.0:
        matched = (
            summary_counts["matched_by_spotify_id"] + summary_counts["matched_by_metadata"]
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


def build_and_write_summary(
    summary_path: Path,
    *,
    elapsed_seconds: float,
    ds001_path: Path,
    spotify_dir: Path,
    top_path: Path,
    saved_path: Path,
    playlist_items_path: Path,
    recently_played_path: Path,
    export_selection: dict[str, Any],
    runtime_scope: dict[str, Any],
    input_scope: dict[str, Any],
    influence_contract: dict[str, Any],
    expected_sources: dict[str, bool],
    available_sources: dict[str, bool],
    missing_selected_sources: list[str],
    allow_missing_selected_sources: bool,
    source_stats: dict[str, Any],
    scope_filter_stats: dict[str, Any],
    summary_counts: dict[str, int],
    matched_events: list[dict[str, Any]],
    aggregated: dict[str, Any],
    trace_rows: list[dict[str, Any]],
    unmatched_rows: list[dict[str, Any]],
    output_paths: dict[str, Path],
    match_rate_min_threshold: float,
) -> dict[str, Any]:
    """Assemble and write the BL-003 summary JSON. Returns the full summary dict."""
    seed_contract: dict[str, Any] = {
        "input_scope": input_scope,
        "influence_tracks": {
            "enabled": influence_contract["enabled"],
            "track_ids": influence_contract["track_ids"],
            "preference_weight": influence_contract["preference_weight"],
        },
    }

    matched_count = (
        summary_counts["matched_by_spotify_id"] + summary_counts["matched_by_metadata"]
    )
    input_rows = summary_counts["input_event_rows"]
    actual_match_rate = round(matched_count / input_rows if input_rows > 0 else 0.0, 4)

    source_scope_manifest_path = output_paths.get(
        "source_scope_manifest",
        summary_path.parent / "bl003_source_scope_manifest.json",
    )

    summary: dict[str, Any] = {
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
            "allow_missing_selected_sources": bool(allow_missing_selected_sources),
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
                "actual_match_rate": actual_match_rate,
                "status": (
                    "pass"
                    if input_rows == 0 or actual_match_rate >= match_rate_min_threshold
                    else "fail"
                ),
            },
        },
        "outputs": {
            "matched_events_jsonl": str(output_paths["matched_jsonl"]),
            "seed_table_csv": str(output_paths["seed_table_csv"]),
            "trace_csv": str(output_paths["trace_csv"]),
            "unmatched_csv": str(output_paths["unmatched_csv"]),
            "summary_json": str(summary_path),
            "source_scope_manifest_json": str(source_scope_manifest_path),
            "sha256": {
                "matched_events_jsonl": sha256_of_file(output_paths["matched_jsonl"]),
                "seed_table_csv": sha256_of_file(output_paths["seed_table_csv"]),
                "trace_csv": sha256_of_file(output_paths["trace_csv"]),
                "unmatched_csv": sha256_of_file(output_paths["unmatched_csv"]),
                "source_scope_manifest_json": sha256_of_file(source_scope_manifest_path),
            },
        },
        "notes": {
            "policy": "spotify_id exact match is primary for DS-001; metadata fallback used only when needed",
            "logging": "full row-level trace includes matched and unmatched reasons",
            "seed_table_enrichment": (
                "seed table includes DS-001 numeric feature columns so downstream "
                "profile stages can consume a single BL-003 artifact"
            ),
        },
    }

    with open_text_write(summary_path) as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    return summary
