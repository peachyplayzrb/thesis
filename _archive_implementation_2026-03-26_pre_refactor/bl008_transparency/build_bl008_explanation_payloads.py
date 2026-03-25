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
import hashlib
import importlib.util
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCORED_CSV   = Path("07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv")
SCORE_SUMMARY_JSON = Path("07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json")
PLAYLIST_JSON = Path("07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json")
TRACE_CSV    = Path("07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv")
OUTPUT_DIR   = Path("07_implementation/implementation_notes/bl008_transparency/outputs")

# Human labels for known BL-006 scoring components.
COMPONENT_LABELS = {
    "tempo": "Tempo (BPM)",
    "duration_ms": "Duration match",
    "key": "Musical key",
    "mode": "Mode (major/minor)",
    "lead_genre": "Lead genre match",
    "genre_overlap": "Genre overlap",
    "tag_overlap": "Tag overlap",
}

COMPONENT_ORDER = [
    "tempo",
    "duration_ms",
    "key",
    "mode",
    "lead_genre",
    "genre_overlap",
    "tag_overlap",
]

# Assembly rule labels
RULE_LABELS = {
    "":                     "Admitted on first evaluation",
    "below_score_threshold": "R1 — score below threshold",
    "genre_cap_exceeded":    "R2 — genre cap exceeded",
    "consecutive_genre_run": "R3 — consecutive genre run",
    "length_cap_reached":    "R4 — length cap reached",
}


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


DEFAULT_TOP_CONTRIBUTOR_LIMIT = 3


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_run_config_utils_module():
    module_path = (
        repo_root()
        / "07_implementation"
        / "implementation_notes"
        / "bl000_run_config"
        / "run_config_utils.py"
    )
    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_bl008_runtime_controls() -> dict[str, object]:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl008_controls(run_config_path)
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "top_contributor_limit": int(controls["top_contributor_limit"]),
            "blend_primary_contributor_on_near_tie": bool(controls.get("blend_primary_contributor_on_near_tie", False)),
            "primary_contributor_tie_delta": float(controls.get("primary_contributor_tie_delta", 0.02)),
        }
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "top_contributor_limit": max(1, env_int("BL008_TOP_CONTRIBUTOR_LIMIT", DEFAULT_TOP_CONTRIBUTOR_LIMIT)),
        "blend_primary_contributor_on_near_tie": False,
        "primary_contributor_tie_delta": 0.02,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest().upper()


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def build_why_selected(track_id: str, lead_genre: str, final_score: float,
                       top_contributors: list, playlist_position: int,
                       top_contributor_limit: int) -> str:
    top_labels = [c["label"] for c in top_contributors[:top_contributor_limit]]
    contributors_str = ", ".join(top_labels)
    return (
        f"Selected at playlist position {playlist_position} "
        f"(score {final_score:.4f}) because it strongly matches the preference profile "
        f"on {contributors_str}. "
        f"Lead genre is '{lead_genre}'."
    )


def select_primary_explanation_driver(
    top_contributors: list[dict],
    playlist_position: int,
    *,
    enable_near_tie_blend: bool,
    near_tie_delta: float,
) -> dict:
    if not top_contributors:
        return {
            "component": "unknown",
            "label": "Unknown",
            "weight": 0.0,
            "similarity": 0.0,
            "contribution": 0.0,
        }

    if not enable_near_tie_blend or len(top_contributors) == 1:
        return top_contributors[0]

    best = float(top_contributors[0].get("contribution", 0.0))
    near_tied = [
        c
        for c in top_contributors
        if best - float(c.get("contribution", 0.0)) <= near_tie_delta
    ]
    if len(near_tied) <= 1:
        return top_contributors[0]

    # Rotate across near-tied contributors by playlist position to avoid one label dominating explanations.
    idx = (max(int(playlist_position), 1) - 1) % len(near_tied)
    return near_tied[idx]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    runtime_controls = resolve_bl008_runtime_controls()
    top_contributor_limit = int(runtime_controls["top_contributor_limit"])
    blend_primary_contributor_on_near_tie = bool(runtime_controls["blend_primary_contributor_on_near_tie"])
    primary_contributor_tie_delta = float(runtime_controls["primary_contributor_tie_delta"])

    # Load BL-006 scored candidates keyed by track_id
    scored_index: dict[str, dict] = {}
    for row in csv.DictReader(SCORED_CSV.open(encoding="utf-8", newline="")):
        scored_index[row["track_id"]] = row
    score_summary = json.loads(SCORE_SUMMARY_JSON.read_text(encoding="utf-8"))
    active_weights = score_summary.get("config", {}).get("active_component_weights", {})

    # Load BL-007 playlist (ordered)
    playlist_data = json.loads(PLAYLIST_JSON.read_text(encoding="utf-8"))
    playlist_tracks = playlist_data["tracks"]

    # Load BL-007 assembly trace keyed by track_id
    trace_index: dict[str, dict] = {}
    for row in csv.DictReader(TRACE_CSV.open(encoding="utf-8", newline="")):
        trace_index[row["track_id"]] = row

    payloads = []

    for pt in playlist_tracks:
        track_id         = pt["track_id"]
        playlist_pos     = pt["playlist_position"]
        final_score      = pt["final_score"]
        score_rank       = pt["score_rank"]
        lead_genre       = pt["lead_genre"]

        scored_row  = scored_index.get(track_id, {})
        trace_row   = trace_index.get(track_id, {})

        # Build score breakdown
        score_breakdown = []
        ordered_components = [
            component
            for component in COMPONENT_ORDER
            if component in active_weights
        ]
        ordered_components.extend(
            sorted(component for component in active_weights if component not in set(ordered_components))
        )

        for prefix in ordered_components:
            sim_key  = f"{prefix}_similarity"
            cont_key = f"{prefix}_contribution"
            similarity   = float(scored_row.get(sim_key, 0))
            contribution = float(scored_row.get(cont_key, 0))
            score_breakdown.append({
                "component":    prefix,
                "label":        COMPONENT_LABELS.get(prefix, prefix.replace("_", " ").title()),
                "weight":       round(float(active_weights.get(prefix, 0.0)), 6),
                "similarity":   round(similarity, 6),
                "contribution": round(contribution, 6),
            })

        # Top-N contributors by contribution value.
        top_contributors = sorted(score_breakdown, key=lambda x: x["contribution"], reverse=True)[:top_contributor_limit]
        primary_driver = select_primary_explanation_driver(
            top_contributors,
            playlist_pos,
            enable_near_tie_blend=blend_primary_contributor_on_near_tie,
            near_tie_delta=primary_contributor_tie_delta,
        )

        # Assembly context
        exclusion_reason = trace_row.get("exclusion_reason", "")
        assembly_context = {
            "decision":          trace_row.get("decision", "included"),
            "admission_rule":    RULE_LABELS.get(exclusion_reason, exclusion_reason),
            "genre_at_position": lead_genre,
        }

        why_selected = build_why_selected(
            track_id, lead_genre, final_score, top_contributors, playlist_pos,
            top_contributor_limit,
        )

        payloads.append({
            "playlist_position":  playlist_pos,
            "track_id":           track_id,
            "lead_genre":         lead_genre,
            "final_score":        round(final_score, 6),
            "score_rank":         score_rank,
            "why_selected":       why_selected,
            "primary_explanation_driver": primary_driver,
            "top_score_contributors": top_contributors,
            "score_breakdown":    score_breakdown,
            "assembly_context":   assembly_context,
        })

    elapsed = round(time.time() - t0, 3)
    now     = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    run_id  = f"BL008-EXPLAIN-{now}"

    # ---- explanation payloads JSON ----------------------------------------
    payloads_path = OUTPUT_DIR / "bl008_explanation_payloads.json"
    payloads_obj  = {
        "run_id":           run_id,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_seconds":  elapsed,
        "playlist_track_count": len(payloads),
        "explanations":     payloads,
    }
    write_json(payloads_path, payloads_obj)

    # ---- explanation summary JSON -----------------------------------------
    summary_path = OUTPUT_DIR / "bl008_explanation_summary.json"
    summary = {
        "run_id":           run_id,
        "generated_at_utc": payloads_obj["generated_at_utc"],
        "elapsed_seconds":  elapsed,
        "playlist_track_count": len(payloads),
        "top_contributor_distribution": _top_contributor_counts(payloads),
        "input_artifact_hashes": {
            "bl006_scored_candidates.csv":   sha256(SCORED_CSV),
            "bl006_score_summary.json":      sha256(SCORE_SUMMARY_JSON),
            "bl007_playlist.json":           sha256(PLAYLIST_JSON),
            "bl007_assembly_trace.csv":      sha256(TRACE_CSV),
        },
        "output_artifact_hashes": {
            "bl008_explanation_payloads.json": sha256(payloads_path),
        },
    }
    write_json(summary_path, summary)

    print(f"BL-008 explanation payloads complete. Tracks explained: {len(payloads)}")
    print(f"Run ID: {run_id}")
    for p in payloads:
        print(f"  pos={p['playlist_position']:>2}  {p['track_id']}  top={p['primary_explanation_driver']['label']}")


def _top_contributor_counts(payloads: list) -> dict:
    from collections import Counter
    c: Counter = Counter()
    for p in payloads:
        primary = p.get("primary_explanation_driver") or {}
        c[primary.get("label", "Unknown")] += 1
    return dict(c)


if __name__ == "__main__":
    main()
