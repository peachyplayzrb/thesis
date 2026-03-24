from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT = 6
DEFAULT_PROFILE_TOP_TAG_LIMIT = 10
DEFAULT_PROFILE_TOP_GENRE_LIMIT = 8
DEFAULT_SEMANTIC_STRONG_KEEP_SCORE = 2
DEFAULT_SEMANTIC_MIN_KEEP_SCORE = 1
DEFAULT_NUMERIC_SUPPORT_MIN_PASS = 1

# Numeric features that are valid only when both the BL-004 profile and the
# candidate dataset provide comparable values.
NUMERIC_FEATURE_SPECS = {
    "tempo": {
        "candidate_column": "tempo",
        "threshold": 20.0,
        "circular": False,
    },
    "key": {
        "candidate_column": "key",
        "threshold": 2.0,
        "circular": True,
    },
    "mode": {
        "candidate_column": "mode",
        "threshold": 0.5,
        "circular": False,
    },
    "duration_ms": {
        "candidate_column": "duration_ms",
        "threshold": 45000.0,
        "circular": False,
    },
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_run_config_utils_module():
    module_path = repo_root() / "07_implementation" / "implementation_notes" / "run_config" / "run_config_utils.py"
    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_bl005_runtime_controls() -> dict[str, object]:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl005_controls(run_config_path)
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "profile_top_lead_genre_limit": int(controls["profile_top_lead_genre_limit"]),
            "profile_top_tag_limit": int(controls["profile_top_tag_limit"]),
            "profile_top_genre_limit": int(controls["profile_top_genre_limit"]),
            "semantic_strong_keep_score": int(controls["semantic_strong_keep_score"]),
            "semantic_min_keep_score": int(controls["semantic_min_keep_score"]),
            "numeric_support_min_pass": int(controls["numeric_support_min_pass"]),
            "numeric_thresholds": controls.get("numeric_thresholds") or {},
        }
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "profile_top_lead_genre_limit": env_int("BL005_PROFILE_TOP_LEAD_GENRE_LIMIT", DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT),
        "profile_top_tag_limit": env_int("BL005_PROFILE_TOP_TAG_LIMIT", DEFAULT_PROFILE_TOP_TAG_LIMIT),
        "profile_top_genre_limit": env_int("BL005_PROFILE_TOP_GENRE_LIMIT", DEFAULT_PROFILE_TOP_GENRE_LIMIT),
        "semantic_strong_keep_score": env_int("BL005_SEMANTIC_STRONG_KEEP_SCORE", DEFAULT_SEMANTIC_STRONG_KEEP_SCORE),
        "semantic_min_keep_score": env_int("BL005_SEMANTIC_MIN_KEEP_SCORE", DEFAULT_SEMANTIC_MIN_KEEP_SCORE),
        "numeric_support_min_pass": env_int("BL005_NUMERIC_SUPPORT_MIN_PASS", DEFAULT_NUMERIC_SUPPORT_MIN_PASS),
        "numeric_thresholds": {},
    }


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_float(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_csv_labels(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    labels: list[str] = []
    seen: set[str] = set()
    for piece in raw_value.split(","):
        label = piece.strip().lower()
        if not label or label in seen:
            continue
        seen.add(label)
        labels.append(label)
    return labels


def candidate_numeric_value(row: dict[str, str], profile_column: str, candidate_column: str) -> float | None:
    value = parse_float(row.get(candidate_column, ""))
    if value is None:
        return None
    if profile_column == "duration_ms" and candidate_column == "duration":
        return value * 1000.0
    return value


def resolve_candidate_column(profile_column: str, preferred_column: str, candidate_columns: set[str]) -> str | None:
    if preferred_column in candidate_columns:
        return preferred_column
    if profile_column == "duration_ms" and "duration" in candidate_columns:
        return "duration"
    return None


def parse_list(raw_value: str, label_key: str) -> list[str]:
    if not raw_value:
        return []
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    result: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        label = item.get(label_key)
        if isinstance(label, str) and label.strip():
            result.append(label.strip())
    return result


def normalize_candidate_row(row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    track_id = (normalized.get("track_id") or "").strip()
    if not track_id:
        track_id = (normalized.get("id") or "").strip()
    normalized["track_id"] = track_id
    return normalized


def keep_decision(
    is_seed_track: bool,
    semantic_score: int,
    numeric_pass_count: int,
    numeric_features_enabled: bool,
    semantic_strong_keep_score: int,
    semantic_min_keep_score: int,
    numeric_support_min_pass: int,
) -> tuple[bool, str]:
    if is_seed_track:
        return False, "reject_seed_track"
    if not numeric_features_enabled:
        if semantic_score >= semantic_min_keep_score:
            return True, "keep_semantic_only"
        return False, "reject_insufficient_semantic"
    if semantic_score >= semantic_strong_keep_score:
        return True, "keep_strong_semantic"
    if semantic_score >= semantic_min_keep_score and numeric_pass_count >= numeric_support_min_pass:
        return True, "keep_semantic_numeric_supported"
    if semantic_score >= semantic_min_keep_score:
        return False, "reject_semantic_without_numeric_support"
    if numeric_pass_count > 0:
        return False, "reject_numeric_without_semantic_support"
    return False, "reject_no_signal"


def decision_reason(decision_path: str, semantic_score: int, numeric_pass_count: int) -> str:
    if decision_path == "reject_seed_track":
        return "reject: seed track excluded from retrieval output"
    if decision_path == "keep_semantic_only":
        return f"keep: semantic_score={semantic_score} with semantic-only mode"
    if decision_path == "keep_strong_semantic":
        return f"keep: semantic_score={semantic_score} meets strong semantic threshold"
    if decision_path == "keep_semantic_numeric_supported":
        return f"keep: semantic_score={semantic_score} with numeric_pass_count={numeric_pass_count}"
    if decision_path == "reject_semantic_without_numeric_support":
        return f"reject: semantic_score={semantic_score} lacks numeric support (numeric_pass_count={numeric_pass_count})"
    if decision_path == "reject_numeric_without_semantic_support":
        return f"reject: numeric_pass_count={numeric_pass_count} without semantic evidence"
    return f"reject: semantic_score={semantic_score}, numeric_pass_count={numeric_pass_count} below keep threshold"


def main() -> None:
    root = repo_root()
    profile_path = root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_preference_profile.json"
    seed_trace_path = root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_seed_trace.csv"
    candidate_path = (
        root / "07_implementation" / "implementation_notes"
        / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv"
    )
    output_dir = root / "07_implementation" / "implementation_notes" / "retrieval" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

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
    candidate_rows = [normalize_candidate_row(row) for row in candidate_rows_raw]
    seed_trace_rows = load_csv_rows(seed_trace_path)

    seed_track_ids = {row["track_id"] for row in seed_trace_rows}
    candidate_columns = set(candidate_rows[0].keys()) if candidate_rows else set()
    top_lead_genres = {item["label"] for item in profile["semantic_profile"]["top_lead_genres"][:profile_top_lead_genre_limit]}
    top_tags = {item["label"] for item in profile["semantic_profile"]["top_tags"][:profile_top_tag_limit]}
    top_genres = {item["label"] for item in profile["semantic_profile"]["top_genres"][:profile_top_genre_limit]}
    active_numeric_specs = {
        profile_column: {
            **spec,
            "candidate_column": resolved_column,
        }
        for profile_column, spec in effective_numeric_specs.items()
        for resolved_column in [
            resolve_candidate_column(profile_column, str(spec["candidate_column"]), candidate_columns)
        ]
        if profile_column in profile["numeric_feature_profile"]
        and resolved_column is not None
    }
    numeric_centers = {
        profile_column: float(profile["numeric_feature_profile"][profile_column])
        for profile_column in active_numeric_specs
    }
    numeric_features_enabled = bool(numeric_centers)

    decisions: list[dict[str, object]] = []
    kept_rows: list[dict[str, str]] = []
    decision_counts = {
        "seed_excluded": 0,
        "kept_candidates": 0,
        "rejected_threshold": 0,
    }
    decision_path_counts: dict[str, int] = {}
    semantic_rule_hits = {
        "lead_genre_match": 0,
        "genre_overlap": 0,
        "tag_overlap": 0,
    }
    numeric_rule_hits = {key: 0 for key in active_numeric_specs}
    semantic_score_distribution = {str(score): 0 for score in range(4)}
    numeric_pass_distribution = {str(score): 0 for score in range(len(active_numeric_specs) + 1)}

    start_time = time.time()
    run_id = f"BL005-FILTER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    for row in candidate_rows:
        track_id = row["track_id"]
        is_seed_track = track_id in seed_track_ids

        # DS-001 provides explicit tags and genres columns.
        lead_genre = ""
        candidate_tags = parse_csv_labels(row.get("tags", ""))
        candidate_genres = parse_csv_labels(row.get("genres", ""))
        if candidate_tags:
            lead_genre = candidate_tags[0]   # top tag acts as lead genre
        elif candidate_genres:
            lead_genre = candidate_genres[0]

        lead_genre_match = lead_genre in top_lead_genres if lead_genre else False
        genre_overlap = len(top_genres.intersection(candidate_genres))
        tag_overlap = len(top_tags.intersection(candidate_tags))

        if lead_genre_match:
            semantic_rule_hits["lead_genre_match"] += 1
        if genre_overlap > 0:
            semantic_rule_hits["genre_overlap"] += 1
        if tag_overlap > 0:
            semantic_rule_hits["tag_overlap"] += 1

        semantic_score = 0
        semantic_score += 1 if lead_genre_match else 0
        semantic_score += 1 if genre_overlap > 0 else 0
        semantic_score += 1 if tag_overlap > 0 else 0
        semantic_score_distribution[str(semantic_score)] = semantic_score_distribution.get(str(semantic_score), 0) + 1

        numeric_pass_count = 0
        numeric_distances: dict[str, float | None] = {}
        for profile_column, spec in active_numeric_specs.items():
            value = candidate_numeric_value(row, profile_column, str(spec["candidate_column"]))
            if value is None:
                numeric_distances[profile_column] = None
                continue
            center = numeric_centers.get(profile_column)
            if center is None:
                numeric_distances[profile_column] = None
                continue
            if bool(spec["circular"]):
                raw_diff = abs(value - center)
                distance = min(raw_diff, 12.0 - raw_diff)
            else:
                distance = abs(value - center)
            numeric_distances[profile_column] = round(distance, 6)
            if distance <= float(spec["threshold"]):
                numeric_pass_count += 1
                numeric_rule_hits[profile_column] += 1
        numeric_pass_distribution[str(numeric_pass_count)] = numeric_pass_distribution.get(str(numeric_pass_count), 0) + 1

        kept, decision_path = keep_decision(
            is_seed_track, semantic_score, numeric_pass_count, numeric_features_enabled,
            semantic_strong_keep_score, semantic_min_keep_score, numeric_support_min_pass,
        )
        decision_path_counts[decision_path] = decision_path_counts.get(decision_path, 0) + 1

        if is_seed_track:
            decision_counts["seed_excluded"] += 1
        elif kept:
            decision_counts["kept_candidates"] += 1
        else:
            decision_counts["rejected_threshold"] += 1

        decision_row = {
            "track_id": track_id,
            "is_seed_track": int(is_seed_track),
            "lead_genre": lead_genre,
            "semantic_score": semantic_score,
            "lead_genre_match": int(lead_genre_match),
            "genre_overlap_count": genre_overlap,
            "tag_overlap_count": tag_overlap,
            "numeric_pass_count": numeric_pass_count,
            "tempo_distance": numeric_distances.get("tempo"),
            "duration_ms_distance": numeric_distances.get("duration_ms"),
            "key_distance": numeric_distances.get("key"),
            "mode_distance": numeric_distances.get("mode"),
            "decision": "keep" if kept else "reject",
            "decision_path": decision_path,
            "decision_reason": decision_reason(decision_path, semantic_score, numeric_pass_count),
        }
        decisions.append(decision_row)
        if kept:
            kept_rows.append(row)

    filtered_path = output_dir / "bl005_filtered_candidates.csv"
    with filtered_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(candidate_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(kept_rows)

    decisions_path = output_dir / "bl005_candidate_decisions.csv"
    with decisions_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decisions[0].keys()), lineterminator="\n")
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
            "seed_tracks_excluded": decision_counts["seed_excluded"],
            "kept_candidates": len(kept_rows),
            "rejected_non_seed_candidates": decision_counts["rejected_threshold"],
        },
        "rule_hits": {
            "semantic_rule_hits": semantic_rule_hits,
            "numeric_rule_hits": numeric_rule_hits,
        },
        "decision_path_counts": decision_path_counts,
        "score_distributions": {
            "semantic_score": semantic_score_distribution,
            "numeric_pass_count": numeric_pass_distribution,
        },
        "top_kept_track_ids": [row["track_id"] for row in kept_rows[:15]],
        "elapsed_seconds": round(time.time() - start_time, 3),
        "output_files": {
            "filtered_candidates_path": str(filtered_path),
            "candidate_decisions_path": str(decisions_path),
        },
    }

    diagnostics_path = output_dir / "bl005_candidate_diagnostics.json"
    with diagnostics_path.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    diagnostics["output_hashes_sha256"] = {
        "bl005_filtered_candidates.csv": sha256_of_file(filtered_path),
        "bl005_candidate_decisions.csv": sha256_of_file(decisions_path),
    }
    diagnostics["diagnostics_hash_note"] = "diagnostics file does not store its own hash to avoid recursive self-reference"
    with diagnostics_path.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    print("BL-005 candidate filtering complete.")
    print(f"filtered_candidates={filtered_path}")
    print(f"decisions={decisions_path}")
    print(f"diagnostics={diagnostics_path}")


if __name__ == "__main__":
    main()