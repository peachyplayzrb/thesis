"""BL-003 summary assembly and writing."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shared_utils.io_utils import open_text_write, sha256_of_file, utc_now

from alignment.writers import canonical_json_hash


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
    fuzzy_matching_controls: dict[str, Any],
) -> dict[str, Any]:
    """Assemble and write the BL-003 summary JSON. Returns the full summary dict."""
    seed_contract: dict[str, Any] = {
        "input_scope": input_scope,
        "influence_tracks": {
            "enabled": influence_contract["enabled"],
            "track_ids": influence_contract["track_ids"],
            "preference_weight": influence_contract["preference_weight"],
        },
        "fuzzy_matching": dict(fuzzy_matching_controls),
    }

    matched_count = (
        summary_counts["matched_by_spotify_id"]
        + summary_counts["matched_by_metadata"]
        + summary_counts.get("matched_by_fuzzy", 0)
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
            "fuzzy_matching": dict(fuzzy_matching_controls),
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
            "policy": (
                "spotify_id exact match is primary for DS-001; metadata fallback used when needed; "
                "optional fuzzy fallback applies only after both exact paths fail"
            ),
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
