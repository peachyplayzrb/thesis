from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from sys import path as sys_path

# Add shared utilities to path
sys_path.insert(0, str(Path(__file__).resolve().parents[3] / "07_implementation" / "implementation_notes"))

from bl000_shared_utils.config_loader import load_run_config_utils_module
from bl000_shared_utils.constants import (
    DEFAULT_NUMERIC_SUPPORT_MIN_PASS,
    DEFAULT_PROFILE_TOP_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_TAG_LIMIT,
    DEFAULT_SEMANTIC_MIN_KEEP_SCORE,
    DEFAULT_SEMANTIC_STRONG_KEEP_SCORE,
    NUMERIC_FEATURE_SPECS,
)
from bl000_shared_utils.env_utils import env_int
from bl000_shared_utils.io_utils import (
    load_csv_rows,
    load_json,
    open_text_write,
    parse_csv_labels,
    sha256_of_file,
)
from bl000_shared_utils.path_utils import repo_root

# Import modularized BL-005 components
from candidate_parser import (
    candidate_numeric_value,
    normalize_candidate_row,
    resolve_candidate_column,
    resolve_lead_genre,
)
from decision_tracker import DecisionTracker
from filtering_logic import decision_reason, keep_decision


DECISION_FIELDS = [
    "track_id",
    "is_seed_track",
    "lead_genre",
    "semantic_score",
    "lead_genre_match",
    "genre_overlap_count",
    "tag_overlap_count",
    "numeric_pass_count",
    "danceability_distance",
    "energy_distance",
    "valence_distance",
    "tempo_distance",
    "duration_ms_distance",
    "key_distance",
    "mode_distance",
    "decision",
    "decision_path",
    "decision_reason",
]


def ensure_paths_exist(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "BL-005 missing required input artifact(s): " + ", ".join(missing)
        )


def build_profile_label_set(
    profile: dict[str, object],
    semantic_key: str,
    limit: int,
) -> set[str]:
    semantic_profile = profile.get("semantic_profile")
    if not isinstance(semantic_profile, dict):
        return set()
    items = semantic_profile.get(semantic_key)
    if not isinstance(items, list):
        return set()

    labels: set[str] = set()
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        if isinstance(label, str) and label.strip():
            labels.add(label.strip().lower())
    return labels


def build_active_numeric_specs(
    profile: dict[str, object],
    effective_numeric_specs: dict[str, dict[str, object]],
    candidate_columns: set[str],
) -> dict[str, dict[str, object]]:
    numeric_profile = profile.get("numeric_feature_profile")
    if not isinstance(numeric_profile, dict):
        return {}

    active_specs: dict[str, dict[str, object]] = {}
    for profile_column, spec in effective_numeric_specs.items():
        if profile_column not in numeric_profile:
            continue
        resolved_column = resolve_candidate_column(
            profile_column,
            str(spec["candidate_column"]),
            candidate_columns,
        )
        if resolved_column is None:
            continue
        active_specs[profile_column] = {
            **spec,
            "candidate_column": resolved_column,
        }
    return active_specs


def resolve_bl005_runtime_controls() -> dict[str, object]:
    env_numeric_thresholds_raw = os.environ.get("BL005_NUMERIC_THRESHOLDS_JSON", "").strip()
    env_numeric_thresholds: dict[str, float] = {}
    if env_numeric_thresholds_raw:
        try:
            payload = json.loads(env_numeric_thresholds_raw)
            if isinstance(payload, dict):
                env_numeric_thresholds = {
                    str(key): float(value)
                    for key, value in payload.items()
                    if isinstance(value, (int, float)) and float(value) > 0
                }
        except json.JSONDecodeError:
            env_numeric_thresholds = {}

    def sanitize_controls(controls: dict[str, object]) -> dict[str, object]:
        controls["profile_top_lead_genre_limit"] = max(1, int(controls["profile_top_lead_genre_limit"]))
        controls["profile_top_tag_limit"] = max(1, int(controls["profile_top_tag_limit"]))
        controls["profile_top_genre_limit"] = max(1, int(controls["profile_top_genre_limit"]))
        controls["semantic_strong_keep_score"] = max(0, min(3, int(controls["semantic_strong_keep_score"])))
        controls["semantic_min_keep_score"] = max(0, min(3, int(controls["semantic_min_keep_score"])))
        controls["numeric_support_min_pass"] = max(0, int(controls["numeric_support_min_pass"]))
        if controls["semantic_min_keep_score"] > controls["semantic_strong_keep_score"]:
            controls["semantic_min_keep_score"] = controls["semantic_strong_keep_score"]
        return controls

    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl005_controls(run_config_path)
        return sanitize_controls(
            {
                "config_source": "run_config",
                "run_config_path": controls.get("config_path"),
                "run_config_schema_version": controls.get("schema_version"),
                "profile_top_lead_genre_limit": int(controls["profile_top_lead_genre_limit"]),
                "profile_top_tag_limit": int(controls["profile_top_tag_limit"]),
                "profile_top_genre_limit": int(controls["profile_top_genre_limit"]),
                "semantic_strong_keep_score": int(controls["semantic_strong_keep_score"]),
                "semantic_min_keep_score": int(controls["semantic_min_keep_score"]),
                "numeric_support_min_pass": int(controls["numeric_support_min_pass"]),
                "numeric_thresholds": env_numeric_thresholds or controls.get("numeric_thresholds") or {},
            }
        )
    return sanitize_controls(
        {
            "config_source": "environment",
            "run_config_path": None,
            "run_config_schema_version": None,
            "profile_top_lead_genre_limit": env_int("BL005_PROFILE_TOP_LEAD_GENRE_LIMIT", DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT),
            "profile_top_tag_limit": env_int("BL005_PROFILE_TOP_TAG_LIMIT", DEFAULT_PROFILE_TOP_TAG_LIMIT),
            "profile_top_genre_limit": env_int("BL005_PROFILE_TOP_GENRE_LIMIT", DEFAULT_PROFILE_TOP_GENRE_LIMIT),
            "semantic_strong_keep_score": env_int("BL005_SEMANTIC_STRONG_KEEP_SCORE", DEFAULT_SEMANTIC_STRONG_KEEP_SCORE),
            "semantic_min_keep_score": env_int("BL005_SEMANTIC_MIN_KEEP_SCORE", DEFAULT_SEMANTIC_MIN_KEEP_SCORE),
            "numeric_support_min_pass": env_int("BL005_NUMERIC_SUPPORT_MIN_PASS", DEFAULT_NUMERIC_SUPPORT_MIN_PASS),
            "numeric_thresholds": env_numeric_thresholds,
        }
    )


def main() -> None:
    root = repo_root()
    profile_path = root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs" / "bl004_preference_profile.json"
    seed_trace_path = root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs" / "bl004_seed_trace.csv"
    candidate_path = (
        root / "07_implementation" / "implementation_notes"
        / "bl000_data_layer" / "outputs" / "ds001_working_candidate_dataset.csv"
    )
    output_dir = root / "07_implementation" / "implementation_notes" / "bl005_retrieval" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_paths_exist([profile_path, seed_trace_path, candidate_path])

    runtime_controls = resolve_bl005_runtime_controls()
    profile_top_lead_genre_limit = int(runtime_controls["profile_top_lead_genre_limit"])
    profile_top_tag_limit = int(runtime_controls["profile_top_tag_limit"])
    profile_top_genre_limit = int(runtime_controls["profile_top_genre_limit"])
    semantic_strong_keep_score = int(runtime_controls["semantic_strong_keep_score"])
    semantic_min_keep_score = int(runtime_controls["semantic_min_keep_score"])
    numeric_support_min_pass = int(runtime_controls["numeric_support_min_pass"])
    numeric_threshold_overrides: dict[str, float] = runtime_controls.get("numeric_thresholds") or {}
    effective_numeric_specs = {
        k: {**v, "threshold": float(numeric_threshold_overrides.get(k, v["threshold"]))}
        for k, v in NUMERIC_FEATURE_SPECS.items()
    }

    profile = load_json(profile_path)
    candidate_rows_raw = load_csv_rows(candidate_path)
    if not candidate_rows_raw:
        raise RuntimeError("BL-005 candidate corpus is empty; cannot build retrieval outputs")
    candidate_rows = [normalize_candidate_row(row) for row in candidate_rows_raw]
    seed_trace_rows = load_csv_rows(seed_trace_path)

    seed_track_ids = {row["track_id"] for row in seed_trace_rows}
    candidate_columns = set(candidate_rows[0].keys()) if candidate_rows else set()
    top_lead_genres = build_profile_label_set(
        profile,
        "top_lead_genres",
        profile_top_lead_genre_limit,
    )
    top_tags = build_profile_label_set(
        profile,
        "top_tags",
        profile_top_tag_limit,
    )
    top_genres = build_profile_label_set(
        profile,
        "top_genres",
        profile_top_genre_limit,
    )
    active_numeric_specs = build_active_numeric_specs(
        profile,
        effective_numeric_specs,
        candidate_columns,
    )
    numeric_centers = {
        profile_column: float(profile["numeric_feature_profile"][profile_column])
        for profile_column in active_numeric_specs
    }
    numeric_features_enabled = bool(numeric_centers)

    # Initialize decision tracker
    tracker = DecisionTracker(active_numeric_specs)
    start_time = time.time()
    run_id = f"BL005-FILTER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    for row in candidate_rows:
        track_id = row["track_id"]
        is_seed_track = track_id in seed_track_ids

        # DS-001 provides explicit tags and genres columns.
        candidate_tags = parse_csv_labels(row.get("tags", ""))
        candidate_genres = parse_csv_labels(row.get("genres", ""))
        lead_genre = resolve_lead_genre(candidate_genres, candidate_tags)

        lead_genre_match = lead_genre in top_lead_genres if lead_genre else False
        genre_overlap = len(top_genres.intersection(candidate_genres))
        tag_overlap = len(top_tags.intersection(candidate_tags))

        semantic_score = 0
        semantic_score += 1 if lead_genre_match else 0
        semantic_score += 1 if genre_overlap > 0 else 0
        semantic_score += 1 if tag_overlap > 0 else 0

        # Track semantic scores
        tracker.record_semantic_scores(semantic_score, lead_genre_match, genre_overlap, tag_overlap)

        # Compute numeric distances and pass counts
        numeric_pass_count = 0
        numeric_distances: dict[str, float | None] = {}
        numeric_rule_hits_this_candidate: dict[str, bool] = {}

        for profile_column, spec in active_numeric_specs.items():
            value = candidate_numeric_value(row, profile_column, str(spec["candidate_column"]))
            passed = False

            if value is not None:
                center = numeric_centers.get(profile_column)
                if center is not None:
                    if bool(spec["circular"]):
                        raw_diff = abs(value - center)
                        distance = min(raw_diff, 12.0 - raw_diff)
                    else:
                        distance = abs(value - center)
                    numeric_distances[profile_column] = round(distance, 6)
                    if distance <= float(spec["threshold"]):
                        numeric_pass_count += 1
                        passed = True
                else:
                    numeric_distances[profile_column] = None
            else:
                numeric_distances[profile_column] = None

            numeric_rule_hits_this_candidate[profile_column] = passed

        # Track numeric scores
        tracker.record_numeric_scores(numeric_pass_count, numeric_rule_hits_this_candidate)

        # Make filtering decision
        kept, decision_path = keep_decision(
            is_seed_track, semantic_score, numeric_pass_count, numeric_features_enabled,
            semantic_strong_keep_score, semantic_min_keep_score, numeric_support_min_pass,
        )

        # Build decision record
        decision_row = {
            "track_id": track_id,
            "is_seed_track": int(is_seed_track),
            "lead_genre": lead_genre,
            "semantic_score": semantic_score,
            "lead_genre_match": int(lead_genre_match),
            "genre_overlap_count": genre_overlap,
            "tag_overlap_count": tag_overlap,
            "numeric_pass_count": numeric_pass_count,
            "danceability_distance": numeric_distances.get("danceability"),
            "energy_distance": numeric_distances.get("energy"),
            "valence_distance": numeric_distances.get("valence"),
            "tempo_distance": numeric_distances.get("tempo"),
            "duration_ms_distance": numeric_distances.get("duration_ms"),
            "key_distance": numeric_distances.get("key"),
            "mode_distance": numeric_distances.get("mode"),
            "decision": "keep" if kept else "reject",
            "decision_path": decision_path,
            "decision_reason": decision_reason(decision_path, semantic_score, numeric_pass_count),
        }

        # Record decision in tracker
        tracker.record_decision(
            track_id,
            is_seed_track,
            kept,
            decision_path,
            decision_row,
            row if kept else None,
        )

    # Get tracked summaries
    summary = tracker.get_summary()
    decisions = tracker.decisions
    kept_rows = tracker.kept_rows

    filtered_path = output_dir / "bl005_filtered_candidates.csv"
    with open_text_write(filtered_path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(candidate_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(kept_rows)

    decisions_path = output_dir / "bl005_candidate_decisions.csv"
    with open_text_write(decisions_path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DECISION_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(decisions)

    diagnostics = {
        "run_id": run_id,
        "task": "BL-005",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_artifacts": {
            "profile_path": str(profile_path),
            "profile_sha256": sha256_of_file(profile_path),
            "seed_trace_path": str(seed_trace_path),
            "seed_trace_sha256": sha256_of_file(seed_trace_path),
            "candidate_stub_path": str(candidate_path),
            "candidate_stub_sha256": sha256_of_file(candidate_path),
        },
        "config": {
            "top_lead_genre_limit": profile_top_lead_genre_limit,
            "top_tag_limit": profile_top_tag_limit,
            "top_genre_limit": profile_top_genre_limit,
            "numeric_thresholds": {
                profile_column: spec["threshold"]
                for profile_column, spec in active_numeric_specs.items()
            },
            "numeric_feature_mapping": {
                profile_column: spec["candidate_column"]
                for profile_column, spec in active_numeric_specs.items()
            },
            "numeric_features_enabled": numeric_features_enabled,
            "keep_rule": (
                f"keep if not seed and (semantic_score >= {semantic_strong_keep_score} or "
                f"(semantic_score >= {semantic_min_keep_score} and numeric_pass_count >= {numeric_support_min_pass}))"
                if numeric_features_enabled
                else f"keep if not seed and semantic_score >= {semantic_min_keep_score}"
            ),
            "semantic_source": "ds001_tags_and_genres_columns",
        },
        "counts": {
            "candidate_rows_total": len(candidate_rows),
            "seed_tracks_excluded": summary["decision_counts"]["seed_excluded"],
            "kept_candidates": len(kept_rows),
            "rejected_non_seed_candidates": summary["decision_counts"]["rejected_threshold"],
        },
        "rule_hits": {
            "semantic_rule_hits": summary["semantic_rule_hits"],
            "numeric_rule_hits": summary["numeric_rule_hits"],
        },
        "decision_path_counts": summary["decision_path_counts"],
        "score_distributions": {
            "semantic_score": summary["semantic_score_distribution"],
            "numeric_pass_count": summary["numeric_pass_distribution"],
        },
        "top_kept_track_ids": [row["track_id"] for row in kept_rows[:15]],
        "elapsed_seconds": round(time.time() - start_time, 3),
        "output_files": {
            "filtered_candidates_path": str(filtered_path),
            "candidate_decisions_path": str(decisions_path),
        },
    }

    diagnostics_path = output_dir / "bl005_candidate_diagnostics.json"
    with open_text_write(diagnostics_path) as handle:
        json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    diagnostics["output_hashes_sha256"] = {
        "bl005_filtered_candidates.csv": sha256_of_file(filtered_path),
        "bl005_candidate_decisions.csv": sha256_of_file(decisions_path),
    }
    diagnostics["diagnostics_hash_note"] = "diagnostics file does not store its own hash to avoid recursive self-reference"
    with open_text_write(diagnostics_path) as handle:
        json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    print("BL-005 candidate filtering complete.")
    print(f"filtered_candidates={filtered_path}")
    print(f"decisions={decisions_path}")
    print(f"diagnostics={diagnostics_path}")


if __name__ == "__main__":
    main()
