#!/usr/bin/env python3
"""
BL-007: Rule-based playlist assembly.

Consumes the BL-006 ranked scored candidates and applies deterministic
diversity, coherence, and length rules to assemble a final playlist.

Rules applied in order (greedy, score-ranked traversal):
  R1 -- Score threshold : skip candidates below min_score_threshold.
  R2 -- Genre cap       : skip if this lead_genre has filled its per-genre quota.
  R3 -- Consecutive run : skip if the last max_consecutive playlist slots share
                          the same genre as this candidate.
  R4 -- Length cap      : stop once target_size tracks have been added.

Outputs
-------
  playlist.json        -- ordered final playlist with per-track metadata
  bl007_assembly_trace.csv   -- one row per BL-006 candidate with decision + rule
  bl007_assembly_report.json -- config, counts, rule stats, artifact hashes
"""

import csv
import time
from collections import Counter
from datetime import datetime, timezone


from shared_utils.io_utils import open_text_write, sha256_of_file, write_json, utc_now
from shared_utils.stage_utils import ensure_paths_exist
from playlist.io_layer import (
    read_scored_candidates,
    resolve_bl007_paths,
    write_assembly_trace,
    write_detail_log,
    write_playlist,
    write_report,
)
from playlist.reporting import (
    build_assembly_detail_log,
    build_assembly_pressure_diagnostics,
    build_rank_continuity_diagnostics,
    build_undersized_diagnostics,
)
from playlist.rules import assemble_bucketed
from playlist.runtime_controls import resolve_bl007_runtime_controls


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()
    scored_candidates_path, output_dir = resolve_bl007_paths()
    output_dir.mkdir(parents=True, exist_ok=True)

    runtime_controls    = resolve_bl007_runtime_controls()
    target_size         = int(runtime_controls["target_size"])
    min_score_threshold = float(runtime_controls["min_score_threshold"])
    max_per_genre       = int(runtime_controls["max_per_genre"])
    max_consecutive     = int(runtime_controls["max_consecutive"])

    ensure_paths_exist([scored_candidates_path], stage_label="BL-007")
    candidates = read_scored_candidates(scored_candidates_path)

    rule_hits: Counter = Counter()
    playlist, trace_rows = assemble_bucketed(
        candidates=candidates,
        target_size=target_size,
        min_score_threshold=min_score_threshold,
        max_per_genre=max_per_genre,
        max_consecutive=max_consecutive,
        rule_hits=rule_hits,
    )

    elapsed = round(time.time() - t0, 3)
    now     = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    run_id  = f"BL007-ASSEMBLE-{now}"

    # ---- playlist JSON --------------------------------------------------------
    playlist_path = output_dir / "playlist.json"
    playlist_obj = {
        "run_id":            run_id,
        "generated_at_utc":  utc_now(),
        "elapsed_seconds":   elapsed,
        "config": {
            "target_size":         target_size,
            "min_score_threshold": min_score_threshold,
            "max_per_genre":       max_per_genre,
            "max_consecutive":     max_consecutive,
        },
        "playlist_length": len(playlist),
        "tracks":           playlist,
    }
    write_playlist(playlist_path, playlist_obj)

    # ---- assembly trace CSV --------------------------------------------------
    trace_path = output_dir / "bl007_assembly_trace.csv"
    write_assembly_trace(trace_path, trace_rows)

    # ---- assembly report JSON ------------------------------------------------
    included    = [r for r in trace_rows if r["decision"] == "included"]
    excluded    = [r for r in trace_rows if r["decision"] != "included"]
    genre_mix   = Counter(t["lead_genre"] for t in playlist)
    undersized_diagnostics = build_undersized_diagnostics(
        target_size=target_size,
        playlist_size=len(playlist),
        candidates_evaluated=len(candidates),
        trace_rows=trace_rows,
    )

    report_path = output_dir / "bl007_assembly_report.json"
    rank_continuity_diagnostics = build_rank_continuity_diagnostics(playlist)
    assembly_pressure_diagnostics = build_assembly_pressure_diagnostics(trace_rows)
    detail_log = build_assembly_detail_log(trace_rows)

    detail_log_path = output_dir / "bl007_assembly_detail_log.json"
    write_detail_log(detail_log_path, detail_log)

    report = {
        "run_id":             run_id,
        "generated_at_utc":   playlist_obj["generated_at_utc"],
        "elapsed_seconds":    elapsed,
        "config":             playlist_obj["config"],
        "counts": {
            "candidates_evaluated": len(candidates),
            "tracks_included":      len(included),
            "tracks_excluded":      len(excluded),
        },
        "rule_hits":              dict(rule_hits),
        "undersized_playlist_warning": undersized_diagnostics,
        "playlist_genre_mix":     dict(genre_mix),
        "playlist_score_range": {
            "max": round(max(t["final_score"] for t in playlist), 6) if playlist else None,
            "min": round(min(t["final_score"] for t in playlist), 6) if playlist else None,
        },
        "rank_continuity_diagnostics": rank_continuity_diagnostics,
        "assembly_pressure_diagnostics": assembly_pressure_diagnostics,
        "input_artifact_hashes": {
            "bl006_scored_candidates.csv": sha256_of_file(scored_candidates_path),
        },
        "output_artifact_hashes": {
            "playlist.json":       sha256_of_file(playlist_path),
            "bl007_assembly_trace.csv":  sha256_of_file(trace_path),
            "bl007_assembly_detail_log.json": sha256_of_file(detail_log_path),
        },
    }
    write_report(report_path, report)

    print(f"BL-007 playlist assembly complete.  Playlist: {len(playlist)}/{target_size} tracks")
    print(f"Run ID : {run_id}")
    print(f"Genre mix : {dict(genre_mix)}")
    if undersized_diagnostics["is_undersized"]:
        print("WARNING: BL-007 produced an undersized playlist.")
        for reason in undersized_diagnostics["reasons"]:
            print(f"  - {reason}")


if __name__ == "__main__":
    main()
