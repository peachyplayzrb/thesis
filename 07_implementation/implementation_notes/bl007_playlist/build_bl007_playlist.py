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
  bl007_playlist.json        -- ordered final playlist with per-track metadata
  bl007_assembly_trace.csv   -- one row per BL-006 candidate with decision + rule
  bl007_assembly_report.json -- config, counts, rule stats, artifact hashes
"""

import csv
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.config_loader import load_run_config_utils_module
from bl000_shared_utils.env_utils import env_float, env_int, env_str
from bl000_shared_utils.io_utils import open_text_write, sha256_of_file, write_json
from bl000_shared_utils.path_utils import repo_root

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEFAULT_SCORED_CANDIDATES_PATH = Path(
    "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv"
)
DEFAULT_OUTPUT_DIR = Path("07_implementation/implementation_notes/bl007_playlist/outputs")

DEFAULT_TARGET_SIZE         = 10
DEFAULT_MIN_SCORE_THRESHOLD = 0.35
DEFAULT_MAX_PER_GENRE       = 4
DEFAULT_MAX_CONSECUTIVE     = 2
REQUIRED_CANDIDATE_COLUMNS = ("rank", "track_id", "lead_genre", "final_score")


def _env_path(name: str, default_relative: Path) -> Path:
    raw = env_str(name, "")
    if raw:
        return Path(raw)
    return repo_root() / default_relative


def _sanitize_bl007_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["target_size"] = max(1, int(controls["target_size"]))
    controls["min_score_threshold"] = max(0.0, min(1.0, float(controls["min_score_threshold"])))
    controls["max_per_genre"] = max(1, int(controls["max_per_genre"]))
    controls["max_consecutive"] = max(1, int(controls["max_consecutive"]))
    return controls


def resolve_bl007_runtime_controls() -> dict[str, object]:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl007_controls(run_config_path)
        return _sanitize_bl007_controls({
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "target_size": int(controls["target_size"]),
            "min_score_threshold": float(controls["min_score_threshold"]),
            "max_per_genre": int(controls["max_per_genre"]),
            "max_consecutive": int(controls["max_consecutive"]),
        })
    return _sanitize_bl007_controls({
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "target_size": env_int("BL007_TARGET_SIZE", DEFAULT_TARGET_SIZE),
        "min_score_threshold": env_float("BL007_MIN_SCORE_THRESHOLD", DEFAULT_MIN_SCORE_THRESHOLD),
        "max_per_genre": env_int("BL007_MAX_PER_GENRE", DEFAULT_MAX_PER_GENRE),
        "max_consecutive": env_int("BL007_MAX_CONSECUTIVE", DEFAULT_MAX_CONSECUTIVE),
    })


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sha256(path: Path) -> str:
    return sha256_of_file(path).upper()


def last_n_genres(playlist: list, n: int) -> list:
    return [t["lead_genre"] for t in playlist[-n:]]


def build_undersized_diagnostics(
    target_size: int,
    playlist_size: int,
    candidates_evaluated: int,
    trace_rows: list[dict],
) -> dict:
    is_undersized = playlist_size < target_size
    exclusion_counts = Counter(
        str(row.get("exclusion_reason") or "")
        for row in trace_rows
        if row.get("decision") == "excluded" and row.get("exclusion_reason")
    )

    reasons: list[str] = []
    if is_undersized:
        shortfall = target_size - playlist_size
        reasons.append(
            f"final playlist length is {playlist_size}/{target_size} (shortfall={shortfall})"
        )
        if candidates_evaluated < target_size:
            reasons.append(
                f"candidate pool is smaller than target size ({candidates_evaluated} < {target_size})"
            )
        for reason, count in exclusion_counts.most_common(3):
            reasons.append(f"exclusion pressure: {reason} ({count} rows)")

    return {
        "is_undersized": is_undersized,
        "target_size": target_size,
        "actual_size": playlist_size,
        "shortfall": max(0, target_size - playlist_size),
        "exclusion_reason_counts": dict(exclusion_counts),
        "reasons": reasons,
    }


def build_rank_continuity_diagnostics(playlist: list[dict]) -> dict:
    selected_ranks = [int(track["score_rank"]) for track in playlist]
    selected_scores = [float(track["final_score"]) for track in playlist]
    max_selected_rank = max(selected_ranks) if selected_ranks else 0
    median_selected_rank = sorted(selected_ranks)[len(selected_ranks) // 2] if selected_ranks else 0
    rank_2_to_3_gap = 0.0
    if len(selected_scores) >= 3:
        rank_2_to_3_gap = round(selected_scores[1] - selected_scores[2], 6)
    return {
        "selected_ranks": selected_ranks,
        "max_selected_rank": max_selected_rank,
        "median_selected_rank": median_selected_rank,
        "rank_2_to_3_score_gap": rank_2_to_3_gap,
        "rank_cliff_detected": rank_2_to_3_gap >= 0.1,
    }


def build_assembly_pressure_diagnostics(trace_rows: list[dict]) -> dict:
    top_100_rows = [row for row in trace_rows if int(row["score_rank"]) <= 100]
    top_100_excluded = [row for row in top_100_rows if row["decision"] == "excluded"]
    reason_counts = Counter(
        str(row.get("exclusion_reason") or "")
        for row in top_100_excluded
        if row.get("exclusion_reason")
    )
    return {
        "top_100_considered": len(top_100_rows),
        "top_100_excluded": len(top_100_excluded),
        "top_100_exclusion_reason_counts": dict(reason_counts),
        "dominant_top_100_exclusion_reason": reason_counts.most_common(1)[0][0] if reason_counts else None,
    }


def build_assembly_detail_log(trace_rows: list[dict]) -> dict:
    top_100_rows = [row for row in trace_rows if int(row["score_rank"]) <= 100]
    included_ranks = sorted(int(row["score_rank"]) for row in trace_rows if row["decision"] == "included")

    detail_rows: list[dict[str, object]] = []
    for row in top_100_rows:
        current_rank = int(row["score_rank"])
        alternative_rank = next((rank for rank in included_ranks if rank > current_rank), None)
        detail_rows.append(
            {
                "score_rank": current_rank,
                "track_id": row["track_id"],
                "final_score": float(row["final_score"]),
                "decision": row["decision"],
                "exclusion_reason": row.get("exclusion_reason", ""),
                "selected_alternative_rank": alternative_rank,
            }
        )

    return {
        "top_rank_window": 100,
        "rows": detail_rows,
    }


def ensure_paths_exist(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "BL-007 missing required input artifact(s): " + ", ".join(missing)
        )


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def read_scored_candidates(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("BL-007 scored candidates CSV has no header row.")
        missing_columns = [
            column for column in REQUIRED_CANDIDATE_COLUMNS if column not in set(reader.fieldnames)
        ]
        if missing_columns:
            raise ValueError(
                "BL-007 scored candidates CSV is missing required column(s): "
                + ", ".join(missing_columns)
            )
        return list(reader)


def decide_candidate(
    *,
    playlist: list[dict],
    lead_genre: str,
    final_score: float,
    target_size: int,
    min_score_threshold: float,
    max_per_genre: int,
    max_consecutive: int,
    rule_hits: Counter,
) -> tuple[str, str]:
    if len(playlist) >= target_size:
        rule_hits["R4_length_cap"] += 1
        return "excluded", "length_cap_reached"

    if final_score < min_score_threshold:
        rule_hits["R1_score_threshold"] += 1
        return "excluded", "below_score_threshold"

    if sum(1 for track in playlist if track["lead_genre"] == lead_genre) >= max_per_genre:
        rule_hits["R2_genre_cap"] += 1
        return "excluded", "genre_cap_exceeded"

    if len(playlist) >= max_consecutive and all(
        genre == lead_genre for genre in last_n_genres(playlist, max_consecutive)
    ):
        rule_hits["R3_consecutive_run"] += 1
        return "excluded", "consecutive_genre_run"

    return "included", ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()
    scored_candidates_path = _env_path("BL007_SCORED_CANDIDATES_PATH", DEFAULT_SCORED_CANDIDATES_PATH)
    output_dir = _env_path("BL007_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    runtime_controls    = resolve_bl007_runtime_controls()
    target_size         = int(runtime_controls["target_size"])
    min_score_threshold = float(runtime_controls["min_score_threshold"])
    max_per_genre       = int(runtime_controls["max_per_genre"])
    max_consecutive     = int(runtime_controls["max_consecutive"])

    ensure_paths_exist([scored_candidates_path])
    candidates = read_scored_candidates(scored_candidates_path)

    playlist: list[dict] = []
    trace_rows: list[dict] = []
    rule_hits: Counter = Counter()

    for cand in candidates:
        track_id = str(cand.get("track_id", ""))
        lead_genre = str(cand.get("lead_genre", ""))
        final_score = safe_float(cand.get("final_score"), 0.0)
        score_rank = safe_int(cand.get("rank"), 0)

        decision, exclusion_reason = decide_candidate(
            playlist=playlist,
            lead_genre=lead_genre,
            final_score=final_score,
            target_size=target_size,
            min_score_threshold=min_score_threshold,
            max_per_genre=max_per_genre,
            max_consecutive=max_consecutive,
            rule_hits=rule_hits,
        )

        playlist_position: int | None = None
        if decision == "included":
            playlist_position = len(playlist) + 1
            playlist.append(
                {
                    "playlist_position": playlist_position,
                    "track_id":          track_id,
                    "lead_genre":        lead_genre,
                    "final_score":       round(final_score, 6),
                    "score_rank":        score_rank,
                }
            )

        trace_rows.append(
            {
                "score_rank":        score_rank,
                "track_id":          track_id,
                "lead_genre":        lead_genre,
                "final_score":       round(final_score, 6),
                "decision":          decision,
                "playlist_position": playlist_position if playlist_position else "",
                "exclusion_reason":  exclusion_reason,
            }
        )

    elapsed = round(time.time() - t0, 3)
    now     = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    run_id  = f"BL007-ASSEMBLE-{now}"

    # ---- playlist JSON --------------------------------------------------------
    playlist_path = output_dir / "bl007_playlist.json"
    playlist_obj = {
        "run_id":            run_id,
        "generated_at_utc":  datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
    write_json(playlist_path, playlist_obj)

    # ---- assembly trace CSV --------------------------------------------------
    trace_path   = output_dir / "bl007_assembly_trace.csv"
    trace_fields = [
        "score_rank", "track_id", "lead_genre", "final_score",
        "decision", "playlist_position", "exclusion_reason",
    ]
    with open_text_write(trace_path, newline="") as f:
        w = csv.DictWriter(f, fieldnames=trace_fields)
        w.writeheader()
        w.writerows(trace_rows)

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
    write_json(detail_log_path, detail_log)

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
            "bl006_scored_candidates.csv": sha256(scored_candidates_path),
        },
        "output_artifact_hashes": {
            "bl007_playlist.json":       sha256(playlist_path),
            "bl007_assembly_trace.csv":  sha256(trace_path),
            "bl007_assembly_detail_log.json": sha256(detail_log_path),
        },
    }
    write_json(report_path, report)

    print(f"BL-007 playlist assembly complete.  Playlist: {len(playlist)}/{target_size} tracks")
    print(f"Run ID : {run_id}")
    print(f"Genre mix : {dict(genre_mix)}")
    if undersized_diagnostics["is_undersized"]:
        print("WARNING: BL-007 produced an undersized playlist.")
        for reason in undersized_diagnostics["reasons"]:
            print(f"  - {reason}")


if __name__ == "__main__":
    main()
