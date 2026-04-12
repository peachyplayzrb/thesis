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
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence, cast

from run_config.stage_control_resolution import defaults_loader as _defaults_loader
from run_config.stage_control_resolution import resolve_stage_controls as _resolve_stage_controls
from run_config.run_config_utils import (
    DEFAULT_TOP_CONTRIBUTOR_LIMIT as RUN_CONFIG_DEFAULT_TOP_CONTRIBUTOR_LIMIT,
    DEFAULT_TRANSPARENCY_CONTROLS as RUN_CONFIG_DEFAULT_TRANSPARENCY_CONTROLS,
)
from shared.io_utils import (
    load_csv_index,
    sha256_of_file,
    utc_now,
    write_json,
)
from shared.path_utils import impl_root
from shared.env_utils import env_bool, env_float, env_int, env_path
from shared.coerce_utils import coerce_float, coerce_int, safe_float, safe_int


DEFAULT_TOP_CONTRIBUTOR_LIMIT = RUN_CONFIG_DEFAULT_TOP_CONTRIBUTOR_LIMIT
DEFAULT_TRANSPARENCY_CONTROLS: dict[str, Any] = deepcopy(RUN_CONFIG_DEFAULT_TRANSPARENCY_CONTROLS)


def load_required_json_object(path: Path, *, label: str, stage_label: str) -> dict[str, object]:
    """Load JSON file and validate it's a dict, with detailed error messages."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"{stage_label} could not read {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{stage_label} could not parse {label} as valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{stage_label} expected {label} to be a JSON object: {path}")
    return {str(key): value for key, value in payload.items()}


def ensure_named_paths_exist(
    paths: Mapping[str, Path],
    *,
    stage_label: str,
    label: str = "input artifacts",
) -> None:
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        details = ", ".join(f"{name}={paths[name]}" for name in missing)
        raise FileNotFoundError(f"{stage_label} missing required {label}: {details}")


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DEFAULT_SCORED_CSV = Path("scoring/outputs/bl006_scored_candidates.csv")
DEFAULT_SCORE_SUMMARY_JSON = Path("scoring/outputs/bl006_score_summary.json")
DEFAULT_PLAYLIST_JSON = Path("playlist/outputs/playlist.json")
DEFAULT_TRACE_CSV = Path("playlist/outputs/bl007_assembly_trace.csv")
DEFAULT_OUTPUT_DIR = Path("transparency/outputs")


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

RULE_LABELS = {
    "": "Admitted on first evaluation",
    "below_score_threshold": "R1 - score below threshold",
    "genre_cap_exceeded": "R2 - genre cap exceeded",
    "consecutive_genre_run": "R3 - consecutive genre run",
    "length_cap_reached": "R4 - length cap reached",
}


def _mapping_from_json(value: object) -> Mapping[str, object]:
    if isinstance(value, dict):
        return cast(Mapping[str, object], value)
    return {}


def _playlist_tracks(value: object) -> list[Mapping[str, object]]:
    if not isinstance(value, list):
        return []
    return [cast(Mapping[str, object], item) for item in value if isinstance(item, dict)]


def canonical_component_name(name: str) -> str:
    return name.removesuffix("_score")


def build_ordered_components(active_weights: Mapping[str, object]) -> list[str]:
    ordered_components: list[str] = []
    active_keys = list(active_weights.keys())
    for canonical in COMPONENT_ORDER:
        for component in active_keys:
            if (
                canonical_component_name(component) == canonical
                and component not in ordered_components
            ):
                ordered_components.append(component)
    ordered_set = set(ordered_components)
    ordered_components.extend(
        sorted(component for component in active_keys if component not in ordered_set)
    )
    return ordered_components


def build_score_breakdown(
    scored_row: Mapping[str, object],
    ordered_components: list[str],
    active_weights: Mapping[str, object],
) -> list[dict[str, object]]:
    score_breakdown: list[dict[str, object]] = []
    for component in ordered_components:
        canonical = canonical_component_name(component)
        sim_key = f"{canonical}_similarity"
        cont_key = f"{canonical}_contribution"
        similarity = safe_float(scored_row.get(sim_key, 0.0))
        contribution = safe_float(scored_row.get(cont_key, 0.0))
        score_breakdown.append(
            {
                "component": canonical,
                "label": COMPONENT_LABELS.get(
                    canonical,
                    canonical.replace("_", " ").title(),
                ),
                "weight": round(
                    safe_float(active_weights.get(component, active_weights.get(canonical, 0.0))),
                    6,
                ),
                "similarity": round(similarity, 6),
                "contribution": round(contribution, 6),
            }
        )
    return score_breakdown


def _unknown_driver() -> dict[str, object]:
    return {
        "component": "unknown",
        "label": "Unknown",
        "weight": 0.0,
        "similarity": 0.0,
        "contribution": 0.0,
    }


def select_primary_explanation_driver(
    top_contributors: Sequence[Mapping[str, object]],
    playlist_position: int,
    *,
    enable_near_tie_blend: bool,
    near_tie_delta: float,
) -> Mapping[str, object]:
    if not top_contributors:
        return _unknown_driver()

    if not enable_near_tie_blend or len(top_contributors) == 1:
        return top_contributors[0]

    # Defense-in-depth: clamp delta here even though controls are sanitized.
    clamped_delta = max(0.0, float(near_tie_delta))
    best = safe_float(top_contributors[0].get("contribution", 0.0))
    near_tied = [
        candidate
        for candidate in top_contributors
        if best - safe_float(candidate.get("contribution", 0.0)) <= clamped_delta
    ]
    if len(near_tied) <= 1:
        return top_contributors[0]

    idx = (max(int(playlist_position), 1) - 1) % len(near_tied)
    return near_tied[idx]


def build_why_selected(
    lead_genre: str,
    final_score: float,
    top_contributors: Sequence[Mapping[str, object]],
    playlist_position: int,
    top_contributor_limit: int,
) -> str:
    top_labels = [
        str(candidate.get("label", "Unknown"))
        for candidate in top_contributors[:top_contributor_limit]
    ]
    contributors_str = ", ".join(top_labels) if top_labels else "no dominant score components"
    return (
        f"Selected at playlist position {playlist_position} "
        f"(score {final_score:.4f}) because it strongly matches the preference profile "
        f"on {contributors_str}. "
        f"Lead genre is '{lead_genre}'."
    )


def build_track_payload(
    *,
    track_id: str,
    lead_genre: str,
    playlist_position: int,
    score_rank: int,
    final_score: float,
    score_breakdown: list[dict[str, object]],
    top_contributors: list[dict[str, object]],
    primary_driver: Mapping[str, object],
    trace_row: Mapping[str, object],
    why_selected: str,
) -> dict[str, object]:
    exclusion_reason = str(trace_row.get("exclusion_reason", ""))
    assembly_context = {
        "decision": trace_row.get("decision", "included"),
        "admission_rule": RULE_LABELS.get(exclusion_reason, exclusion_reason),
        "genre_at_position": lead_genre,
    }
    return {
        "playlist_position": playlist_position,
        "track_id": track_id,
        "lead_genre": lead_genre,
        "final_score": round(final_score, 6),
        "score_rank": score_rank,
        "why_selected": why_selected,
        "primary_explanation_driver": primary_driver,
        "top_score_contributors": top_contributors,
        "score_breakdown": score_breakdown,
        "assembly_context": assembly_context,
    }


def top_contributor_counts(payloads: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for payload in payloads:
        primary = payload.get("primary_explanation_driver") or {}
        label = "Unknown"
        if isinstance(primary, dict):
            label = str(primary.get("label", "Unknown"))
        counts[label] = counts.get(label, 0) + 1
    return counts


def _sanitize_bl008_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["top_contributor_limit"] = max(1, coerce_int(controls.get("top_contributor_limit"), 3))
    controls["blend_primary_contributor_on_near_tie"] = bool(
        controls.get("blend_primary_contributor_on_near_tie", False)
    )
    controls["primary_contributor_tie_delta"] = max(
        0.0, min(1.0, coerce_float(controls.get("primary_contributor_tie_delta"), 0.02)),
    )
    return controls


def _load_bl008_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "top_contributor_limit": max(
            1,
            env_int("BL008_TOP_CONTRIBUTOR_LIMIT", DEFAULT_TOP_CONTRIBUTOR_LIMIT),
        ),
        "blend_primary_contributor_on_near_tie": env_bool(
            "BL008_BLEND_PRIMARY_CONTRIBUTOR_ON_NEAR_TIE", False
        ),
        "primary_contributor_tie_delta": env_float(
            "BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA", 0.02
        ),
    }


def _env_truthy(name: str) -> bool:
    raw = os.environ.get(name, "")
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _bl008_require_payload() -> bool:
    return _env_truthy("BL008_STRICT_PAYLOAD") or _env_truthy("BL_STRICT_STAGE_PAYLOAD")


def resolve_bl008_runtime_controls() -> dict[str, object]:
    return _resolve_stage_controls(
        load_from_env=_load_bl008_controls_from_env,
        load_payload_defaults=_defaults_loader(DEFAULT_TRANSPARENCY_CONTROLS),
        sanitize=_sanitize_bl008_controls,
        require_payload=_bl008_require_payload(),
    )


class TransparencyStage:
    def __init__(self, *, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    def resolve_paths(self) -> dict[str, Path]:
        scored_csv = env_path("BL008_SCORED_CSV_PATH", self.root / DEFAULT_SCORED_CSV)
        score_summary_json = env_path("BL008_SCORE_SUMMARY_PATH", self.root / DEFAULT_SCORE_SUMMARY_JSON)
        playlist_json = env_path("BL008_PLAYLIST_PATH", self.root / DEFAULT_PLAYLIST_JSON)
        trace_csv = env_path("BL008_TRACE_CSV_PATH", self.root / DEFAULT_TRACE_CSV)
        output_dir = env_path("BL008_OUTPUT_DIR", self.root / DEFAULT_OUTPUT_DIR)
        return {
            "scored_csv": scored_csv,
            "score_summary_json": score_summary_json,
            "playlist_json": playlist_json,
            "trace_csv": trace_csv,
            "output_dir": output_dir,
        }

    def load_inputs(
        self,
        *,
        scored_csv: Path,
        score_summary_json: Path,
        playlist_json: Path,
        trace_csv: Path,
    ) -> tuple[
        dict[str, dict[str, str]],
        Mapping[str, object],
        list[str],
        list[Mapping[str, object]],
        dict[str, dict[str, str]],
    ]:
        scored_index = load_csv_index(scored_csv, "track_id")
        score_summary = load_required_json_object(
            score_summary_json,
            label="BL-006 score summary",
            stage_label="BL-008",
        )
        active_weights = _mapping_from_json(
            _mapping_from_json(score_summary.get("config", {})).get("active_component_weights", {})
        )
        ordered_components = build_ordered_components(active_weights)
        playlist_data = load_required_json_object(
            playlist_json,
            label="BL-007 playlist",
            stage_label="BL-008",
        )
        playlist_tracks = _playlist_tracks(_mapping_from_json(playlist_data).get("tracks", []))
        trace_index = load_csv_index(trace_csv, "track_id")
        return scored_index, active_weights, ordered_components, playlist_tracks, trace_index

    def build_payloads(
        self,
        *,
        playlist_tracks: list[Mapping[str, object]],
        scored_index: dict[str, dict[str, str]],
        trace_index: dict[str, dict[str, str]],
        ordered_components: list[str],
        active_weights: Mapping[str, object],
        top_contributor_limit: int,
        blend_primary_contributor_on_near_tie: bool,
        primary_contributor_tie_delta: float,
    ) -> list[dict[str, object]]:
        payloads: list[dict[str, object]] = []
        for playlist_track in playlist_tracks:
            track_id = str(playlist_track.get("track_id", ""))
            playlist_pos = safe_int(playlist_track.get("playlist_position", 0))
            final_score = safe_float(playlist_track.get("final_score", 0.0))
            score_rank = safe_int(playlist_track.get("score_rank", 0))
            lead_genre = str(playlist_track.get("lead_genre", ""))

            scored_row = scored_index.get(track_id, {})
            trace_row = trace_index.get(track_id, {})
            score_breakdown = build_score_breakdown(scored_row, ordered_components, active_weights)

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
                lead_genre,
                final_score,
                top_contributors,
                playlist_pos,
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
        return payloads

    def write_artifacts(
        self,
        *,
        payloads: list[dict[str, object]],
        output_dir: Path,
        scored_csv: Path,
        score_summary_json: Path,
        playlist_json: Path,
        trace_csv: Path,
        elapsed: float,
    ) -> tuple[str, Path, Path]:
        now = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        run_id = f"BL008-EXPLAIN-{now}"

        payloads_path = output_dir / "bl008_explanation_payloads.json"
        payloads_obj = {
            "run_id": run_id,
            "generated_at_utc": utc_now(),
            "elapsed_seconds": elapsed,
            "playlist_track_count": len(payloads),
            "explanations": payloads,
        }
        write_json(payloads_path, payloads_obj)

        summary_path = output_dir / "bl008_explanation_summary.json"
        summary = {
            "run_id": run_id,
            "generated_at_utc": utc_now(),
            "elapsed_seconds": elapsed,
            "playlist_track_count": len(payloads),
            "top_contributor_distribution": top_contributor_counts(payloads),
            "input_artifact_hashes": {
                "bl006_scored_candidates.csv": sha256_of_file(scored_csv),
                "bl006_score_summary.json": sha256_of_file(score_summary_json),
                "playlist.json": sha256_of_file(playlist_json),
                "bl007_assembly_trace.csv": sha256_of_file(trace_csv),
            },
            "output_artifact_hashes": {
                "bl008_explanation_payloads.json": sha256_of_file(payloads_path),
            },
        }
        write_json(summary_path, summary)
        return run_id, payloads_path, summary_path

    def run(self) -> None:
        t0 = time.time()
        paths = self.resolve_paths()
        output_dir = paths["output_dir"]
        output_dir.mkdir(parents=True, exist_ok=True)

        controls = resolve_bl008_runtime_controls()
        top_contributor_limit = safe_int(controls["top_contributor_limit"], 3)
        blend_primary_contributor_on_near_tie = bool(controls["blend_primary_contributor_on_near_tie"])
        primary_contributor_tie_delta = safe_float(controls["primary_contributor_tie_delta"], 0.0)

        ensure_named_paths_exist(
            {
                "scored_csv": paths["scored_csv"],
                "score_summary_json": paths["score_summary_json"],
                "playlist_json": paths["playlist_json"],
                "trace_csv": paths["trace_csv"],
            },
            stage_label="BL-008",
        )

        scored_index, active_weights, ordered_components, playlist_tracks, trace_index = self.load_inputs(
            scored_csv=paths["scored_csv"],
            score_summary_json=paths["score_summary_json"],
            playlist_json=paths["playlist_json"],
            trace_csv=paths["trace_csv"],
        )

        payloads = self.build_payloads(
            playlist_tracks=playlist_tracks,
            scored_index=scored_index,
            trace_index=trace_index,
            ordered_components=ordered_components,
            active_weights=active_weights,
            top_contributor_limit=top_contributor_limit,
            blend_primary_contributor_on_near_tie=blend_primary_contributor_on_near_tie,
            primary_contributor_tie_delta=primary_contributor_tie_delta,
        )

        elapsed = round(time.time() - t0, 3)
        run_id, payloads_path, summary_path = self.write_artifacts(
            payloads=payloads,
            output_dir=output_dir,
            scored_csv=paths["scored_csv"],
            score_summary_json=paths["score_summary_json"],
            playlist_json=paths["playlist_json"],
            trace_csv=paths["trace_csv"],
            elapsed=elapsed,
        )

        print(f"BL-008 explanation payloads complete. Tracks explained: {len(payloads)}")
        print(f"Run ID: {run_id}")
        print(f"Payloads: {payloads_path}")
        print(f"Summary: {summary_path}")
        for payload in payloads:
            primary_driver = _mapping_from_json(payload.get("primary_explanation_driver", {}))
            print(
                f"  pos={safe_int(payload.get('playlist_position', 0)):>2}  "
                f"{payload.get('track_id', '')}  top={primary_driver.get('label', 'Unknown')}"
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    TransparencyStage().run()


if __name__ == "__main__":
    main()
