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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, cast


from shared_utils.env_utils import env_path
from shared_utils.parsing import safe_float, safe_int
from shared_utils.io_utils import sha256_of_file, write_json, utc_now
from shared_utils.path_utils import impl_root
from shared_utils.stage_utils import ensure_named_paths_exist, load_required_json_object
from transparency.runtime_controls import resolve_bl008_runtime_controls
from transparency.data_layer import read_csv_index
from transparency.explanation_driver import (
    build_why_selected,
    select_primary_explanation_driver,
)
from transparency.payload_builder import (
    build_ordered_components,
    build_score_breakdown,
    build_track_payload,
    top_contributor_counts,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DEFAULT_SCORED_CSV = Path("scoring/outputs/bl006_scored_candidates.csv")
DEFAULT_SCORE_SUMMARY_JSON = Path("scoring/outputs/bl006_score_summary.json")
DEFAULT_PLAYLIST_JSON = Path("playlist/outputs/playlist.json")
DEFAULT_TRACE_CSV = Path("playlist/outputs/bl007_assembly_trace.csv")
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
    output_dir = env_path("BL008_OUTPUT_DIR", impl_root() / DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    runtime_controls = resolve_bl008_runtime_controls()
    top_contributor_limit = safe_int(runtime_controls["top_contributor_limit"], 3)
    blend_primary_contributor_on_near_tie = bool(runtime_controls["blend_primary_contributor_on_near_tie"])
    primary_contributor_tie_delta = safe_float(runtime_controls["primary_contributor_tie_delta"], 0.0)

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
    ordered_components = build_ordered_components(active_weights)

    # Load BL-007 playlist (ordered)
    playlist_data = load_required_json_object(playlist_json, label="BL-007 playlist", stage_label="BL-008")
    playlist_tracks = _playlist_tracks(_mapping_from_json(playlist_data).get("tracks", []))

    # Load BL-007 assembly trace keyed by track_id
    trace_index = read_csv_index(trace_csv, "track_id")

    payloads: list[dict[str, object]] = []

    for pt in playlist_tracks:
        track_id         = str(pt.get("track_id", ""))
        playlist_pos     = safe_int(pt.get("playlist_position", 0))
        final_score      = safe_float(pt.get("final_score", 0.0))
        score_rank       = safe_int(pt.get("score_rank", 0))
        lead_genre       = str(pt.get("lead_genre", ""))

        scored_row  = scored_index.get(track_id, {})
        trace_row   = trace_index.get(track_id, {})

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
                score_breakdown=score_breakdown,
                top_contributors=top_contributors,
                primary_driver=primary_driver,
                trace_row=trace_row,
                why_selected=why_selected,
            )
        )

    elapsed = round(time.time() - t0, 3)
    now     = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    run_id  = f"BL008-EXPLAIN-{now}"

    # ---- explanation payloads JSON ----------------------------------------
    payloads_path = output_dir / "bl008_explanation_payloads.json"
    payloads_obj  = {
        "run_id":           run_id,
        "generated_at_utc": utc_now(),
        "elapsed_seconds":  elapsed,
        "playlist_track_count": len(payloads),
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
