#!/usr/bin/env python3
"""
BL-008: Transparency outputs — per-track explanation payloads.

Reads BL-006 scored candidates, BL-007 playlist, and BL-007 assembly trace
to produce human-readable and machine-readable explanation artifacts for every
track in the final playlist.

Each explanation payload contains:
  - playlist_position and score_rank
  - final_score
  - top_score_contributors  (top 3 components by weighted contribution)
  - score_breakdown         (all component similarities and contributions)
  - assembly_context        (which rule admitted this track, position in run)
  - why_selected            (concise human-readable sentence)

Outputs
-------
  bl008_explanation_payloads.json   -- one payload per playlist track
  bl008_explanation_summary.json    -- run metadata, counts, input hashes
"""

import csv
import time
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from shared_utils.env_utils import env_path
from shared_utils.io_utils import sha256_of_file, utc_now, write_json
from shared_utils.parsing import safe_float, safe_int
from shared_utils.path_utils import impl_root
from shared_utils.stage_utils import ensure_named_paths_exist, load_required_json_object
from transparency.data_layer import read_csv_index
from transparency.explanation_driver import (
    build_why_selected,
    select_causal_driver,
    select_primary_explanation_driver,
)
from transparency.input_validation import validate_bl007_bl008_handshake
from transparency.payload_builder import (
    build_ordered_components,
    build_rejected_track_payload,
    build_score_breakdown,
    build_track_payload,
    top_contributor_counts,
)
from transparency.runtime_controls import resolve_bl008_runtime_controls

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DEFAULT_SCORED_CSV = Path("scoring/outputs/bl006_scored_candidates.csv")
DEFAULT_SCORE_SUMMARY_JSON = Path("scoring/outputs/bl006_score_summary.json")
DEFAULT_PLAYLIST_JSON = Path("playlist/outputs/playlist.json")
DEFAULT_TRACE_CSV = Path("playlist/outputs/bl007_assembly_trace.csv")
DEFAULT_ASSEMBLY_REPORT_JSON = Path("playlist/outputs/bl007_assembly_report.json")
DEFAULT_OUTPUT_DIR = Path("transparency/outputs")


def _mapping_from_json(value: object) -> Mapping[str, object]:
    if isinstance(value, dict):
        return cast(Mapping[str, object], value)
    return {}


def _playlist_tracks(value: object) -> list[Mapping[str, object]]:
    if not isinstance(value, list):
        return []
    return [cast(Mapping[str, object], item) for item in value if isinstance(item, dict)]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()
    scored_csv = env_path("BL008_SCORED_CSV_PATH", impl_root() / DEFAULT_SCORED_CSV)
    score_summary_json = env_path("BL008_SCORE_SUMMARY_PATH", impl_root() / DEFAULT_SCORE_SUMMARY_JSON)
    playlist_json = env_path("BL008_PLAYLIST_PATH", impl_root() / DEFAULT_PLAYLIST_JSON)
    trace_csv = env_path("BL008_TRACE_CSV_PATH", impl_root() / DEFAULT_TRACE_CSV)
    assembly_report_json = env_path(
        "BL008_ASSEMBLY_REPORT_PATH",
        impl_root() / DEFAULT_ASSEMBLY_REPORT_JSON,
    )
    output_dir = env_path("BL008_OUTPUT_DIR", impl_root() / DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    runtime_controls = resolve_bl008_runtime_controls()
    top_contributor_limit = safe_int(runtime_controls["top_contributor_limit"], 3)
    blend_primary_contributor_on_near_tie = bool(runtime_controls["blend_primary_contributor_on_near_tie"])
    primary_contributor_tie_delta = safe_float(runtime_controls["primary_contributor_tie_delta"], 0.0)
    include_per_track_control_provenance = bool(
        runtime_controls.get("include_per_track_control_provenance", True)
    )
    emit_run_level_control_provenance_summary = bool(
        runtime_controls.get("emit_run_level_control_provenance_summary", True)
    )
    bl007_bl008_handshake_validation_policy = str(
        runtime_controls.get("bl007_bl008_handshake_validation_policy", "warn")
    )

    ensure_named_paths_exist({
        "scored_csv": scored_csv,
        "score_summary_json": score_summary_json,
        "playlist_json": playlist_json,
        "trace_csv": trace_csv,
    }, stage_label="BL-008")

    # Load BL-006 scored candidates keyed by track_id
    scored_index = read_csv_index(scored_csv, "track_id")
    score_summary = load_required_json_object(score_summary_json, label="BL-006 score summary", stage_label="BL-008")
    active_weights = _mapping_from_json(
        _mapping_from_json(score_summary.get("config", {})).get("active_component_weights", {})
    )
    scoring_config = _mapping_from_json(score_summary.get("config", {}))
    control_provenance = {
        "scoring": {
            "active_component_weights": dict(active_weights),
            "lead_genre_strategy": scoring_config.get("lead_genre_strategy"),
            "semantic_overlap_strategy": scoring_config.get("semantic_overlap_strategy"),
            "signal_mode": scoring_config.get("signal_mode"),
        },
        "transparency": {
            "top_contributor_limit": top_contributor_limit,
            "blend_primary_contributor_on_near_tie": blend_primary_contributor_on_near_tie,
            "primary_contributor_tie_delta": primary_contributor_tie_delta,
        },
    }
    ordered_components = build_ordered_components(active_weights)

    # Load BL-007 playlist (ordered)
    playlist_data = load_required_json_object(playlist_json, label="BL-007 playlist", stage_label="BL-008")
    playlist_tracks = _playlist_tracks(_mapping_from_json(playlist_data).get("tracks", []))

    # Load BL-007 assembly trace keyed by track_id
    trace_index = read_csv_index(trace_csv, "track_id")
    with trace_csv.open("r", encoding="utf-8", newline="") as trace_handle:
        trace_rows = list(csv.DictReader(trace_handle))

    # BL-007 ↔ BL-008 handshake validation
    with trace_csv.open("r", encoding="utf-8", newline="") as _th:
        trace_header = next(csv.reader(_th))
    handshake_validation = validate_bl007_bl008_handshake(
        playlist_tracks=list(playlist_tracks),
        trace_header=trace_header,
        policy=bl007_bl008_handshake_validation_policy,
    )
    if handshake_validation["status"] == "fail":
        violations = handshake_validation.get("sampled_violations")
        raise RuntimeError(
            "BL-008 handshake validation failed under strict policy: "
            f"violations={violations}"
        )
    if handshake_validation["status"] in {"warn", "allow"}:
        import logging
        logging.getLogger(__name__).warning(
            "BL-008 handshake validation status=%s policy=%s violations=%s",
            handshake_validation.get("status"),
            handshake_validation.get("policy"),
            handshake_validation.get("sampled_violations"),
        )

    assembly_report: dict[str, object] = {}
    if assembly_report_json.exists():
        assembly_report = load_required_json_object(
            assembly_report_json,
            label="BL-007 assembly report",
            stage_label="BL-008",
        )

    payloads: list[dict[str, object]] = []
    rejected_payloads: list[dict[str, object]] = []

    for pt in playlist_tracks:
        track_id = str(pt.get("track_id", ""))
        playlist_pos = safe_int(pt.get("playlist_position", 0))
        final_score = safe_float(pt.get("final_score", 0.0))
        score_rank = safe_int(pt.get("score_rank", 0))
        lead_genre = str(pt.get("lead_genre", ""))

        scored_row = scored_index.get(track_id, {})
        trace_row = trace_index.get(track_id, {})
        raw_final_score = safe_float(scored_row.get("raw_final_score", final_score))

        score_breakdown = build_score_breakdown(scored_row, ordered_components, active_weights)

        # Top-N contributors by contribution value.
        top_contributors = sorted(
            score_breakdown,
            key=lambda contributor: safe_float(contributor.get("contribution", 0.0)),
            reverse=True,
        )[:top_contributor_limit]
        primary_driver = select_primary_explanation_driver(
            top_contributors,
            playlist_pos,
            enable_near_tie_blend=blend_primary_contributor_on_near_tie,
            near_tie_delta=primary_contributor_tie_delta,
        )
        causal_driver = select_causal_driver(top_contributors)
        narrative_driver = primary_driver

        why_selected = build_why_selected(
            lead_genre, final_score, top_contributors, playlist_pos,
            top_contributor_limit,
        )

        payloads.append(
            build_track_payload(
                track_id=track_id,
                lead_genre=lead_genre,
                playlist_position=playlist_pos,
                score_rank=score_rank,
                final_score=final_score,
                raw_final_score=raw_final_score,
                score_breakdown=score_breakdown,
                top_contributors=top_contributors,
                primary_driver=primary_driver,
                causal_driver=causal_driver,
                narrative_driver=narrative_driver,
                trace_row=trace_row,
                why_selected=why_selected,
                control_provenance_ref=("run_level" if emit_run_level_control_provenance_summary else "inline"),
                control_provenance=(control_provenance if include_per_track_control_provenance else {}),
                assembly_report=assembly_report,
            )
        )

    playlist_track_ids = {str(track.get("track_id", "")) for track in playlist_tracks}
    emitted_rejected_track_ids: set[str] = set()
    for trace_row in trace_rows:
        decision = str(trace_row.get("decision", "")).strip().lower()
        if decision == "included":
            continue
        track_id = str(trace_row.get("track_id", "")).strip()
        if not track_id:
            continue
        if track_id in playlist_track_ids or track_id in emitted_rejected_track_ids:
            continue

        scored_row = scored_index.get(track_id, {})
        lead_genre = str(scored_row.get("lead_genre", ""))
        final_score = safe_float(scored_row.get("final_score", 0.0))
        raw_final_score = safe_float(scored_row.get("raw_final_score", final_score))
        score_rank = safe_int(trace_row.get("score_rank", scored_row.get("rank", 0)))
        score_breakdown = build_score_breakdown(scored_row, ordered_components, active_weights)
        top_contributors = sorted(
            score_breakdown,
            key=lambda contributor: safe_float(contributor.get("contribution", 0.0)),
            reverse=True,
        )[:top_contributor_limit]
        primary_driver = select_primary_explanation_driver(
            top_contributors,
            score_rank,
            enable_near_tie_blend=blend_primary_contributor_on_near_tie,
            near_tie_delta=primary_contributor_tie_delta,
        )
        causal_driver = select_causal_driver(top_contributors)
        narrative_driver = primary_driver

        rejected_payloads.append(
            build_rejected_track_payload(
                track_id=track_id,
                lead_genre=lead_genre,
                score_rank=score_rank,
                final_score=final_score,
                raw_final_score=raw_final_score,
                score_breakdown=score_breakdown,
                top_contributors=top_contributors,
                primary_driver=primary_driver,
                causal_driver=causal_driver,
                narrative_driver=narrative_driver,
                trace_row=trace_row,
                control_provenance_ref=("run_level" if emit_run_level_control_provenance_summary else "inline"),
                control_provenance=(control_provenance if include_per_track_control_provenance else {}),
                assembly_report=assembly_report,
            )
        )
        emitted_rejected_track_ids.add(track_id)

    elapsed = round(time.time() - t0, 3)
    now = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%f")
    run_id = f"BL008-EXPLAIN-{now}"

    # ---- explanation payloads JSON ----------------------------------------
    payloads_path = output_dir / "bl008_explanation_payloads.json"
    payloads_obj = {
        "run_id":           run_id,
        "generated_at_utc": utc_now(),
        "elapsed_seconds":  elapsed,
        "playlist_track_count": len(payloads),
        "rejected_track_control_causality_count": len(rejected_payloads),
        "control_provenance_summary": (
            control_provenance if emit_run_level_control_provenance_summary else {}
        ),
        "rejected_track_control_causality": rejected_payloads,
        "explanations":     payloads,
    }
    write_json(payloads_path, payloads_obj)

    # ---- explanation summary JSON -----------------------------------------
    summary_path = output_dir / "bl008_explanation_summary.json"
    generated_at_utc = utc_now()
    summary = {
        "run_id":           run_id,
        "generated_at_utc": generated_at_utc,
        "elapsed_seconds":  elapsed,
        "playlist_track_count": len(payloads),
        "top_contributor_distribution": top_contributor_counts(payloads),
        "config": {
            "validation_policies": {
                "bl007_bl008_handshake_validation_policy": bl007_bl008_handshake_validation_policy,
            },
        },
        "validation": {
            "status": handshake_validation.get("status", "pass"),
            "policy": handshake_validation.get("policy", bl007_bl008_handshake_validation_policy),
        },
        "input_artifact_hashes": {
            "bl006_scored_candidates.csv":   sha256_of_file(scored_csv),
            "bl006_score_summary.json":      sha256_of_file(score_summary_json),
            "playlist.json":           sha256_of_file(playlist_json),
            "bl007_assembly_trace.csv":      sha256_of_file(trace_csv),
        },
        "output_artifact_hashes": {
            "bl008_explanation_payloads.json": sha256_of_file(payloads_path),
        },
    }
    write_json(summary_path, summary)

    print(f"BL-008 explanation payloads complete. Tracks explained: {len(payloads)}")
    print(f"Run ID: {run_id}")
    for p in payloads:
        primary_driver = _mapping_from_json(p.get("primary_explanation_driver", {}))
        print(
            f"  pos={safe_int(p.get('playlist_position', 0)):>2}  "
            f"{p.get('track_id', '')}  top={primary_driver.get('label', 'Unknown')}"
        )


if __name__ == "__main__":
    main()
