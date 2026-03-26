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
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.config_loader import load_run_config_utils_module
from bl000_shared_utils.env_utils import env_bool, env_float, env_int, env_str
from bl000_shared_utils.io_utils import sha256_of_file, write_json
from bl000_shared_utils.path_utils import repo_root

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DEFAULT_SCORED_CSV = Path("07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv")
DEFAULT_SCORE_SUMMARY_JSON = Path("07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json")
DEFAULT_PLAYLIST_JSON = Path("07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json")
DEFAULT_TRACE_CSV = Path("07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv")
DEFAULT_OUTPUT_DIR = Path("07_implementation/implementation_notes/bl008_transparency/outputs")

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


DEFAULT_TOP_CONTRIBUTOR_LIMIT = 3


def _env_path(name: str, default_relative: Path) -> Path:
    raw = env_str(name, "")
    if raw:
        return Path(raw)
    return repo_root() / default_relative


def load_required_json(path: Path, *, label: str) -> dict | list:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"BL-008 could not read {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"BL-008 could not parse {label} as valid JSON: {path}") from exc


def _sanitize_bl008_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["top_contributor_limit"] = max(1, int(controls["top_contributor_limit"]))
    controls["blend_primary_contributor_on_near_tie"] = bool(controls["blend_primary_contributor_on_near_tie"])
    controls["primary_contributor_tie_delta"] = max(0.0, min(1.0, float(controls["primary_contributor_tie_delta"])))
    return controls


def resolve_bl008_runtime_controls() -> dict[str, object]:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl008_controls(run_config_path)
        return _sanitize_bl008_controls({
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "top_contributor_limit": int(controls["top_contributor_limit"]),
            "blend_primary_contributor_on_near_tie": bool(controls.get("blend_primary_contributor_on_near_tie", False)),
            "primary_contributor_tie_delta": float(controls.get("primary_contributor_tie_delta", 0.02)),
        })
    return _sanitize_bl008_controls({
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "top_contributor_limit": max(1, env_int("BL008_TOP_CONTRIBUTOR_LIMIT", DEFAULT_TOP_CONTRIBUTOR_LIMIT)),
        "blend_primary_contributor_on_near_tie": env_bool("BL008_BLEND_PRIMARY_CONTRIBUTOR_ON_NEAR_TIE", False),
        "primary_contributor_tie_delta": env_float("BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA", 0.02),
    })


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sha256(path: Path) -> str:
    return sha256_of_file(path).upper()


def ensure_paths_exist(paths: dict[str, Path]) -> None:
    missing = [label for label, path in paths.items() if not path.exists()]
    if missing:
        details = ", ".join(f"{label}={paths[label]}" for label in missing)
        raise FileNotFoundError(f"BL-008 missing required input artifacts: {details}")


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def canonical_component_name(name: str) -> str:
    return name.removesuffix("_score")


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


def read_csv_index(path: Path, key_field: str) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for row in csv.DictReader(path.open(encoding="utf-8", newline="")):
        key = (row.get(key_field) or "").strip()
        if key:
            index[key] = row
    return index


def build_ordered_components(active_weights: dict[str, object]) -> list[str]:
    ordered_components: list[str] = []
    active_keys = list(active_weights.keys())
    for canonical in COMPONENT_ORDER:
        for component in active_keys:
            if canonical_component_name(component) == canonical and component not in ordered_components:
                ordered_components.append(component)
    ordered_set = set(ordered_components)
    ordered_components.extend(sorted(component for component in active_keys if component not in ordered_set))
    return ordered_components


def build_score_breakdown(scored_row: dict[str, object], ordered_components: list[str],
                          active_weights: dict[str, object]) -> list[dict[str, object]]:
    score_breakdown: list[dict[str, object]] = []
    for component in ordered_components:
        canonical = canonical_component_name(component)
        sim_key = f"{canonical}_similarity"
        cont_key = f"{canonical}_contribution"
        similarity = safe_float(scored_row.get(sim_key, 0.0))
        contribution = safe_float(scored_row.get(cont_key, 0.0))
        score_breakdown.append({
            "component": canonical,
            "label": COMPONENT_LABELS.get(canonical, canonical.replace("_", " ").title()),
            "weight": round(safe_float(active_weights.get(component, active_weights.get(canonical, 0.0))), 6),
            "similarity": round(similarity, 6),
            "contribution": round(contribution, 6),
        })
    return score_breakdown


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
    scored_csv = _env_path("BL008_SCORED_CSV_PATH", DEFAULT_SCORED_CSV)
    score_summary_json = _env_path("BL008_SCORE_SUMMARY_PATH", DEFAULT_SCORE_SUMMARY_JSON)
    playlist_json = _env_path("BL008_PLAYLIST_PATH", DEFAULT_PLAYLIST_JSON)
    trace_csv = _env_path("BL008_TRACE_CSV_PATH", DEFAULT_TRACE_CSV)
    output_dir = _env_path("BL008_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    runtime_controls = resolve_bl008_runtime_controls()
    top_contributor_limit = int(runtime_controls["top_contributor_limit"])
    blend_primary_contributor_on_near_tie = bool(runtime_controls["blend_primary_contributor_on_near_tie"])
    primary_contributor_tie_delta = float(runtime_controls["primary_contributor_tie_delta"])

    ensure_paths_exist({
        "scored_csv": scored_csv,
        "score_summary_json": score_summary_json,
        "playlist_json": playlist_json,
        "trace_csv": trace_csv,
    })

    # Load BL-006 scored candidates keyed by track_id
    scored_index = read_csv_index(scored_csv, "track_id")
    score_summary = load_required_json(score_summary_json, label="BL-006 score summary")
    active_weights = score_summary.get("config", {}).get("active_component_weights", {})
    ordered_components = build_ordered_components(active_weights)

    # Load BL-007 playlist (ordered)
    playlist_data = load_required_json(playlist_json, label="BL-007 playlist")
    playlist_tracks = playlist_data["tracks"]

    # Load BL-007 assembly trace keyed by track_id
    trace_index = read_csv_index(trace_csv, "track_id")

    payloads = []

    for pt in playlist_tracks:
        track_id         = pt["track_id"]
        playlist_pos     = pt["playlist_position"]
        final_score      = safe_float(pt.get("final_score", 0.0))
        score_rank       = pt["score_rank"]
        lead_genre       = pt["lead_genre"]

        scored_row  = scored_index.get(track_id, {})
        trace_row   = trace_index.get(track_id, {})

        score_breakdown = build_score_breakdown(scored_row, ordered_components, active_weights)

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
    payloads_path = output_dir / "bl008_explanation_payloads.json"
    payloads_obj  = {
        "run_id":           run_id,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_seconds":  elapsed,
        "playlist_track_count": len(payloads),
        "explanations":     payloads,
    }
    write_json(payloads_path, payloads_obj)

    # ---- explanation summary JSON -----------------------------------------
    summary_path = output_dir / "bl008_explanation_summary.json"
    summary = {
        "run_id":           run_id,
        "generated_at_utc": payloads_obj["generated_at_utc"],
        "elapsed_seconds":  elapsed,
        "playlist_track_count": len(payloads),
        "top_contributor_distribution": _top_contributor_counts(payloads),
        "input_artifact_hashes": {
            "bl006_scored_candidates.csv":   sha256(scored_csv),
            "bl006_score_summary.json":      sha256(score_summary_json),
            "bl007_playlist.json":           sha256(playlist_json),
            "bl007_assembly_trace.csv":      sha256(trace_csv),
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
    c: Counter = Counter()
    for p in payloads:
        primary = p.get("primary_explanation_driver") or {}
        c[primary.get("label", "Unknown")] += 1
    return dict(c)


if __name__ == "__main__":
    main()
