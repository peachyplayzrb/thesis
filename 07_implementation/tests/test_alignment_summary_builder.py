"""Tests for BL-003 summary-builder context migration."""

from __future__ import annotations

# pyright: reportMissingImports=false

from pathlib import Path
from types import SimpleNamespace

from alignment.constants import ALIGNMENT_OUTPUT_FILENAMES, SEED_TABLE_FIELDNAMES, SPOTIFY_EXPORT_FILENAMES, TRACE_FIELDNAMES
from alignment.writers import (
    build_and_write_summary_from_context,
)


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_context_entrypoint_writes_expected_contract_payload(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("alignment.writers.utc_now", lambda: "2026-03-29T00:00:00Z")

    ds001_path = tmp_path / "ds001.csv"
    spotify_dir = tmp_path / "spotify"
    top_path = spotify_dir / "spotify_top_tracks_flat.csv"
    saved_path = spotify_dir / "spotify_saved_tracks_flat.csv"
    playlist_path = spotify_dir / "spotify_playlist_items_flat.csv"
    recent_path = spotify_dir / "spotify_recently_played_flat.csv"

    _write_file(ds001_path, "id,spotify_id,song,artist\n1,s1,Song,Artist\n")
    _write_file(top_path, "track_id\n")
    _write_file(saved_path, "track_id\n")
    _write_file(playlist_path, "track_id\n")
    _write_file(recent_path, "track_id\n")

    output_dir = tmp_path / "alignment_outputs"
    matched_jsonl = output_dir / "bl003_ds001_spotify_matched_events.jsonl"
    seed_csv = output_dir / "bl003_ds001_spotify_seed_table.csv"
    trace_csv = output_dir / "bl003_ds001_spotify_trace.csv"
    unmatched_csv = output_dir / "bl003_ds001_spotify_unmatched.csv"
    scope_manifest = output_dir / "bl003_source_scope_manifest.json"
    summary_path = output_dir / "bl003_ds001_spotify_summary.json"

    _write_file(matched_jsonl, "")
    _write_file(seed_csv, "header\n")
    _write_file(trace_csv, "header\n")
    _write_file(unmatched_csv, "header\n")
    _write_file(scope_manifest, "{}")

    output_paths = {
        "matched_jsonl": matched_jsonl,
        "seed_table_csv": seed_csv,
        "trace_csv": trace_csv,
        "unmatched_csv": unmatched_csv,
        "source_scope_manifest": scope_manifest,
    }
    behavior_controls = {
        "input_scope": {"include_top_tracks": True},
        "top_range_weights": {"short_term": 0.5, "medium_term": 0.3, "long_term": 0.2},
        "source_base_weights": {
            "top_tracks": 1.0,
            "saved_tracks": 0.6,
            "playlist_items": 0.4,
            "recently_played": 0.5,
        },
        "source_resilience_policy": {
            "top_tracks": "required",
            "saved_tracks": "optional",
            "playlist_items": "optional",
            "recently_played": "advisory",
        },
        "decay_half_lives": {"recently_played": 90.0, "saved_tracks": 365.0},
        "match_rate_min_threshold": 0.0,
        "fuzzy_matching_controls": {"enabled": False},
        "weighting_policy": {
            "top_tracks_min_rank_floor": 0.05,
            "top_tracks_scale_multiplier": 100.0,
            "top_tracks_default_time_range_weight": 0.2,
            "playlist_items_min_position_floor": 0.05,
            "playlist_items_scale_multiplier": 20.0,
        },
        "influence_controls": {
            "influence_enabled": False,
            "influence_track_ids": [],
            "influence_preference_weight": 1.0,
        },
    }
    structural_contract = {
        "spotify_export_filenames": dict(SPOTIFY_EXPORT_FILENAMES),
        "output_filenames": dict(ALIGNMENT_OUTPUT_FILENAMES),
        "trace_fieldnames": list(TRACE_FIELDNAMES),
        "seed_table_fieldnames": list(SEED_TABLE_FIELDNAMES),
        "default_relative_paths": {
            "ds001_candidates": Path("data_layer") / "outputs" / "ds001_working_candidate_dataset.csv",
            "spotify_export_dir": Path("ingestion") / "outputs" / "spotify_api_export",
            "output_dir": Path("alignment") / "outputs",
        },
        "artifact_schema_version": "bl003-artifacts-v1",
        "summary_schema_version": "bl003-summary-v1",
        "source_scope_manifest_schema_version": "bl003-source-scope-manifest-v1",
    }

    context_summary = build_and_write_summary_from_context(
        summary_path,
        SimpleNamespace(
            elapsed_seconds=0.123,
            ds001_path=ds001_path,
            spotify_dir=spotify_dir,
            top_path=top_path,
            saved_path=saved_path,
            playlist_items_path=playlist_path,
            recently_played_path=recent_path,
            export_selection={"include_top_tracks": True},
            runtime_scope={
                "config_source": "environment",
                "run_config_path": None,
                "run_config_schema_version": None,
            },
            input_scope={"include_top_tracks": True},
            influence_contract={
                "enabled": False,
                "track_ids": [],
                "preference_weight": 1.0,
                "injected_count": 0,
                "skipped_track_ids": [],
            },
            expected_sources={
                "top_tracks": True,
                "saved_tracks": True,
                "playlist_items": True,
                "recently_played": True,
            },
            available_sources={
                "top_tracks": True,
                "saved_tracks": True,
                "playlist_items": True,
                "recently_played": True,
            },
            missing_selected_sources=[],
            source_resilience_policy=behavior_controls["source_resilience_policy"],
            missing_required_sources=[],
            degraded_optional_sources=[],
            allow_missing_selected_sources=False,
            source_stats={
                "top_tracks": {"file_present": True, "rows_available": 0, "rows_selected": 0},
                "saved_tracks": {"file_present": True, "rows_available": 0, "rows_selected": 0},
                "playlist_items": {"file_present": True, "rows_available": 0, "rows_selected": 0},
                "recently_played": {"file_present": True, "rows_available": 0, "rows_selected": 0},
            },
            scope_filter_stats={"rows_available": {}, "rows_selected": {}},
            behavior_controls=SimpleNamespace(**behavior_controls),
            structural_contract=SimpleNamespace(**structural_contract),
            metrics=SimpleNamespace(
                summary_counts={
                    "input_event_rows": 0,
                    "matched_by_spotify_id": 0,
                    "matched_by_metadata": 0,
                    "matched_by_fuzzy": 0,
                    "unmatched": 0,
                    "unmatched_missing_keys": 0,
                    "unmatched_no_candidate": 0,
                },
                matched_events_rows=0,
                seed_table_rows=0,
                trace_rows=0,
                unmatched_rows=0,
                unmatched_reason_counts={
                    "no_ds001_candidate": 0,
                    "missing_track_id_and_metadata": 0,
                },
            ),
            output_paths=output_paths,
            match_rate_min_threshold=0.0,
            fuzzy_matching_controls={"enabled": False},
        ),
    )

    assert context_summary["summary_schema_version"] == "bl003-summary-v1"
    assert context_summary["artifact_contract_version"] == "bl003-artifacts-v1"
    assert context_summary["outputs"]["artifact_schema_version"] == "bl003-artifacts-v1"
    assert context_summary["outputs"]["source_scope_manifest_schema_version"] == "bl003-source-scope-manifest-v1"
    assert context_summary["inputs"]["seed_contract"]["seed_contract_schema_version"] == "bl003-seed-contract-v1"
    assert context_summary["inputs"]["seed_contract"]["top_range_weights"]["short_term"] == 0.5
    assert context_summary["inputs"]["seed_contract"]["source_base_weights"]["saved_tracks"] == 0.6
    assert context_summary["inputs"]["seed_contract"]["decay_half_lives"]["saved_tracks"] == 365.0
    assert context_summary["inputs"]["seed_contract"]["weighting_policy"]["top_tracks_scale_multiplier"] == 100.0
    assert context_summary["inputs"]["seed_contract"]["config_precedence_hierarchy"] == [
        "BL003_INPUT_SCOPE_JSON",
        "BL_RUN_CONFIG_PATH",
        "defaults",
    ]
    assert context_summary["inputs"]["structural_contract"]["structural_contract_schema_version"] == "bl003-structural-contract-v1"
    assert context_summary["inputs"]["structural_contract"]["output_filenames"]["summary_json"] == "bl003_ds001_spotify_summary.json"
    assert context_summary["analysis"]["unmatched_reason_counts"]["no_ds001_candidate"] == 0
    assert context_summary["analysis"]["unmatched_reason_classification"]["dataset_coverage_likely"] == 0
