"""Output writers for BL-003 alignment artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from alignment.constants import (
    ALIGNMENT_ARTIFACT_SCHEMA_VERSION,
    ALIGNMENT_OUTPUT_FILENAMES,
    ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION,
    ALIGNMENT_SOURCE_SCOPE_MANIFEST_SCHEMA_VERSION,
    ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION,
    ALIGNMENT_SUMMARY_SCHEMA_VERSION,
    CONFIG_PRECEDENCE_HIERARCHY,
    EVENT_ID_ALIGNMENT_TEMPLATE,
    EVENT_ID_INFLUENCE_TEMPLATE,
    FLOAT_PRECISION_DECIMALS,
    INTERACTION_TYPE_HISTORY,
    JSON_INDENT_SPACES,
    MATCH_STRATEGY_ORDER,
    SEED_TABLE_FIELDNAMES,
    SUMMARY_NOTE_LOGGING,
    SUMMARY_NOTE_POLICY,
    SUMMARY_NOTE_SEED_TABLE_ENRICHMENT,
    SUMMARY_RATE_PRECISION_DECIMALS,
    SUMMARY_TASK_NAME,
    TEXT_NORMALIZATION_RULES,
    TRACE_FIELDNAMES,
)
from alignment.models import (
    AggregatedEvent,
    AlignmentBehaviorControls,
    AlignmentStructuralContract,
    AlignmentSummaryContext,
    MatchedEvent,
)
from shared_utils.hashing import canonical_json_hash as _canonical_json_hash
from shared_utils.io_utils import open_text_write, sha256_of_file, utc_now


def canonical_json_hash(payload: object) -> str:
    return _canonical_json_hash(payload, uppercase=True)


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
        "source_resilience_policy": dict(behavior_controls.source_resilience_policy),
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
                "match_confidence_score": f"{float(agg.get('match_confidence_score', 1.0)):.{FLOAT_PRECISION_DECIMALS}f}",
                "source_types": "|".join(sorted(agg["source_types"])),
                "interaction_types": (
                    "|".join(sorted(agg["interaction_types"]))
                    if agg["interaction_types"]
                    else INTERACTION_TYPE_HISTORY
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
    seed_contract: dict[str, Any] | None = None,
    structural_contract: dict[str, Any] | None = None,
) -> None:
    """Write the BL-003 source-scope manifest JSON."""
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


def _build_summary_payload(
    summary_path: Path,
    context: AlignmentSummaryContext,
) -> dict[str, Any]:
    """Assemble the BL-003 summary JSON payload from a typed context."""
    summary_counts = context.metrics.summary_counts
    seed_contract = build_seed_contract_payload(context.behavior_controls)
    structural_contract = build_structural_contract_payload(context.structural_contract)

    matched_count = (
        summary_counts["matched_by_spotify_id"]
        + summary_counts["matched_by_metadata"]
        + summary_counts.get("matched_by_fuzzy", 0)
    )
    input_rows = summary_counts["input_event_rows"]
    actual_match_rate = round(
        matched_count / input_rows if input_rows > 0 else 0.0,
        SUMMARY_RATE_PRECISION_DECIMALS,
    )

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
            "runtime_scope_diagnostics": dict(
                context.runtime_scope.get("scope_resolution_diagnostics", {})
            ),
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
            "source_resilience_policy": context.source_resilience_policy,
            "missing_selected_sources": context.missing_selected_sources,
            "missing_required_sources": context.missing_required_sources,
            "degraded_optional_sources": context.degraded_optional_sources,
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
            "match_rate_validation": {
                "threshold_enforced": context.match_rate_min_threshold > 0.0,
                "min_threshold": round(context.match_rate_min_threshold, SUMMARY_RATE_PRECISION_DECIMALS),
                "actual_match_rate": actual_match_rate,
                "status": (
                    "pass"
                    if input_rows == 0 or actual_match_rate >= context.match_rate_min_threshold
                    else "fail"
                ),
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


def build_and_write_summary_from_context(
    summary_path: Path,
    context: AlignmentSummaryContext,
) -> dict[str, Any]:
    """Assemble and write BL-003 summary JSON using a typed context contract."""
    summary = _build_summary_payload(summary_path, context)

    with open_text_write(summary_path) as handle:
        json.dump(summary, handle, indent=JSON_INDENT_SPACES, ensure_ascii=True)

    return summary
