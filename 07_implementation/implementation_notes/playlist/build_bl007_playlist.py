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
import hashlib
import importlib.util
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCORED_CANDIDATES_PATH = Path(
    "07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv"
)
OUTPUT_DIR = Path("07_implementation/implementation_notes/playlist/outputs")

def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


DEFAULT_TARGET_SIZE         = 10
DEFAULT_MIN_SCORE_THRESHOLD = 0.35
DEFAULT_MAX_PER_GENRE       = 4
DEFAULT_MAX_CONSECUTIVE     = 2


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_run_config_utils_module():
    module_path = (
        repo_root()
        / "07_implementation"
        / "implementation_notes"
        / "run_config"
        / "run_config_utils.py"
    )
    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_bl007_runtime_controls() -> dict[str, object]:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl007_controls(run_config_path)
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "target_size": int(controls["target_size"]),
            "min_score_threshold": float(controls["min_score_threshold"]),
            "max_per_genre": int(controls["max_per_genre"]),
            "max_consecutive": int(controls["max_consecutive"]),
        }
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "target_size": env_int("BL007_TARGET_SIZE", DEFAULT_TARGET_SIZE),
        "min_score_threshold": env_float("BL007_MIN_SCORE_THRESHOLD", DEFAULT_MIN_SCORE_THRESHOLD),
        "max_per_genre": env_int("BL007_MAX_PER_GENRE", DEFAULT_MAX_PER_GENRE),
        "max_consecutive": env_int("BL007_MAX_CONSECUTIVE", DEFAULT_MAX_CONSECUTIVE),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest().upper()


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    runtime_controls    = resolve_bl007_runtime_controls()
    target_size         = int(runtime_controls["target_size"])
    min_score_threshold = float(runtime_controls["min_score_threshold"])
    max_per_genre       = int(runtime_controls["max_per_genre"])
    max_consecutive     = int(runtime_controls["max_consecutive"])

    candidates = list(
        csv.DictReader(
            SCORED_CANDIDATES_PATH.open(encoding="utf-8", newline="")
        )
    )

    playlist: list[dict] = []
    trace_rows: list[dict] = []
    rule_hits: Counter = Counter()

    for cand in candidates:
        track_id    = cand["track_id"]
        lead_genre  = cand["lead_genre"]
        final_score = float(cand["final_score"])
        score_rank  = int(cand["rank"])

        decision         = "included"
        exclusion_reason = ""

        if len(playlist) >= target_size:
            # R4 checked first so we still log remaining candidates as excluded
            decision         = "excluded"
            exclusion_reason = "length_cap_reached"
            rule_hits["R4_length_cap"] += 1

        elif final_score < min_score_threshold:
            decision         = "excluded"
            exclusion_reason = "below_score_threshold"
            rule_hits["R1_score_threshold"] += 1

        elif sum(1 for t in playlist if t["lead_genre"] == lead_genre) >= max_per_genre:
            decision         = "excluded"
            exclusion_reason = "genre_cap_exceeded"
            rule_hits["R2_genre_cap"] += 1

        elif (
            len(playlist) >= max_consecutive
            and all(g == lead_genre for g in last_n_genres(playlist, max_consecutive))
        ):
            decision         = "excluded"
            exclusion_reason = "consecutive_genre_run"
            rule_hits["R3_consecutive_run"] += 1

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
    playlist_path = OUTPUT_DIR / "bl007_playlist.json"
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
    trace_path   = OUTPUT_DIR / "bl007_assembly_trace.csv"
    trace_fields = [
        "score_rank", "track_id", "lead_genre", "final_score",
        "decision", "playlist_position", "exclusion_reason",
    ]
    with trace_path.open("w", encoding="utf-8", newline="") as f:
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

    report_path = OUTPUT_DIR / "bl007_assembly_report.json"
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
        "input_artifact_hashes": {
            "bl006_scored_candidates.csv": sha256(SCORED_CANDIDATES_PATH),
        },
        "output_artifact_hashes": {
            "bl007_playlist.json":       sha256(playlist_path),
            "bl007_assembly_trace.csv":  sha256(trace_path),
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
