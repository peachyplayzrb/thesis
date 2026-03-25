from __future__ import annotations

import csv
import hashlib
import json
import importlib.util
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path


# Numeric features that remain comparable between the BL-004 profile contract
# and the current candidate dataset.
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

# Base component weights. Numeric components are dropped and re-normalized when
# the profile is semantic-only.
DEFAULT_COMPONENT_WEIGHTS: dict[str, float] = {
    "tempo":         0.20,
    "duration_ms":   0.13,
    "key":           0.13,
    "mode":          0.09,
    "lead_genre":    0.17,
    "genre_overlap": 0.12,
    "tag_overlap":   0.16,
}

NUMERIC_COMPONENTS = {"tempo", "duration_ms", "key", "mode"}


def load_component_weight_overrides(defaults: dict[str, float]) -> dict[str, float]:
    raw = os.environ.get("BL006_COMPONENT_WEIGHTS_JSON", "").strip()
    if not raw:
        return dict(defaults)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return dict(defaults)
    if not isinstance(payload, dict):
        return dict(defaults)

    merged = dict(defaults)
    for key, value in payload.items():
        if key in merged and isinstance(value, (int, float)) and value >= 0:
            merged[key] = float(value)
    return merged


def apply_numeric_threshold_overrides(specs: dict[str, dict[str, object]]) -> None:
    raw = os.environ.get("BL006_NUMERIC_THRESHOLDS_JSON", "").strip()
    if not raw:
        return
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return
    if not isinstance(payload, dict):
        return

    for feature_name, threshold in payload.items():
        if feature_name in specs and isinstance(threshold, (int, float)) and threshold > 0:
            specs[feature_name]["threshold"] = float(threshold)


def build_active_component_weights(
    active_numeric_components: set[str],
    component_weights: dict[str, float],
) -> tuple[dict[str, float], dict[str, object]]:
    active = {
        component: weight
        for component, weight in component_weights.items()
        if component not in NUMERIC_COMPONENTS or component in active_numeric_components
    }
    total = sum(active.values())
    if total <= 0:
        raise RuntimeError("BL-006 requires at least one active scoring component")

    normalized = {component: weight / total for component, weight in active.items()}
    rebalanced = abs(total - 1.0) > 1e-9
    diagnostics = {
        "rebalanced": rebalanced,
        "active_weight_sum_pre_normalization": round(total, 6),
        "active_component_count": len(active),
        "inactive_components": sorted(set(component_weights) - set(active)),
        "original_active_component_weights": {k: round(v, 6) for k, v in active.items()},
        "normalized_active_component_weights": {k: round(v, 6) for k, v in normalized.items()},
        "warning": (
            "BL-006 rebalanced active component weights to sum to 1.0"
            if rebalanced
            else None
        ),
    }
    return normalized, diagnostics


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


def _load_bl006_numeric_thresholds_from_env() -> dict[str, float]:
    raw = os.environ.get("BL006_NUMERIC_THRESHOLDS_JSON", "").strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {
        k: float(v)
        for k, v in payload.items()
        if isinstance(v, (int, float)) and v > 0
    }


def resolve_bl006_runtime_controls() -> dict[str, object]:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl006_controls(run_config_path)
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "component_weights": dict(controls.get("component_weights") or DEFAULT_COMPONENT_WEIGHTS),
            "numeric_thresholds": dict(controls.get("numeric_thresholds") or {}),
        }
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "component_weights": load_component_weight_overrides(DEFAULT_COMPONENT_WEIGHTS),
        "numeric_thresholds": _load_bl006_numeric_thresholds_from_env(),
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


def parse_labels(raw_value: str, label_key: str) -> list[str]:
    if not raw_value:
        return []
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    labels: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        label = item.get(label_key)
        if isinstance(label, str) and label.strip():
            labels.append(label.strip())
    return labels


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


def resolve_lead_genre(candidate_genres: list[str], candidate_tags: list[str]) -> str:
    if candidate_genres:
        return candidate_genres[0]
    if candidate_tags:
        return candidate_tags[0]
    return ""


def normalize_weight_map(items: list[dict[str, object]], top_k: int) -> tuple[dict[str, float], float]:
    subset = items[:top_k]
    weight_map: dict[str, float] = {}
    total = 0.0
    for item in subset:
        label = item.get("label")
        weight = item.get("weight")
        if not isinstance(label, str):
            continue
        try:
            numeric_weight = float(weight)
        except (TypeError, ValueError):
            continue
        weight_map[label] = numeric_weight
        total += numeric_weight
    return weight_map, total


def numeric_similarity(value: float | None, center: float, threshold: float, circular: bool = False) -> float:
    if value is None:
        return 0.0
    if circular:
        raw_diff = abs(value - center)
        diff = min(raw_diff, 12.0 - raw_diff)
    else:
        diff = abs(value - center)
    similarity = 1.0 - (diff / threshold)
    if similarity < 0:
        return 0.0
    if similarity > 1:
        return 1.0
    return round(similarity, 6)


def weighted_overlap(candidate_labels: list[str], profile_weight_map: dict[str, float], profile_total: float) -> tuple[float, list[str]]:
    matched = [label for label in candidate_labels if label in profile_weight_map]
    if not matched or profile_total <= 0:
        return 0.0, []
    overlap_weight = sum(profile_weight_map[label] for label in matched)
    return round(overlap_weight / profile_total, 6), matched


def contribution_breakdown(rows: list[dict[str, object]]) -> dict[str, float]:
    if not rows:
        return {
            "numeric_contribution_mean": 0.0,
            "semantic_contribution_mean": 0.0,
            "tempo_mean": 0.0,
            "duration_ms_mean": 0.0,
            "key_mean": 0.0,
            "mode_mean": 0.0,
            "lead_genre_mean": 0.0,
            "genre_overlap_mean": 0.0,
            "tag_overlap_mean": 0.0,
        }

    def mean_of(key: str) -> float:
        return round(statistics.mean(float(row[key]) for row in rows), 6)

    tempo_mean = mean_of("tempo_contribution")
    duration_mean = mean_of("duration_ms_contribution")
    key_mean = mean_of("key_contribution")
    mode_mean = mean_of("mode_contribution")
    lead_mean = mean_of("lead_genre_contribution")
    genre_overlap_mean = mean_of("genre_overlap_contribution")
    tag_overlap_mean = mean_of("tag_overlap_contribution")

    numeric_mean = round(tempo_mean + duration_mean + key_mean + mode_mean, 6)
    semantic_mean = round(lead_mean + genre_overlap_mean + tag_overlap_mean, 6)

    return {
        "numeric_contribution_mean": numeric_mean,
        "semantic_contribution_mean": semantic_mean,
        "tempo_mean": tempo_mean,
        "duration_ms_mean": duration_mean,
        "key_mean": key_mean,
        "mode_mean": mode_mean,
        "lead_genre_mean": lead_mean,
        "genre_overlap_mean": genre_overlap_mean,
        "tag_overlap_mean": tag_overlap_mean,
    }


def main() -> None:
    root = repo_root()
    profile_path = root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_preference_profile.json"
    filtered_candidates_path = root / "07_implementation" / "implementation_notes" / "retrieval" / "outputs" / "bl005_filtered_candidates.csv"
    output_dir = root / "07_implementation" / "implementation_notes" / "scoring" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    profile = load_json(profile_path)
    candidates = load_csv_rows(filtered_candidates_path)
    if not candidates:
        raise RuntimeError("No BL-005 filtered candidates found for BL-006")

    runtime_controls = resolve_bl006_runtime_controls()
    effective_component_weights: dict[str, float] = dict(runtime_controls["component_weights"])
    numeric_threshold_overrides: dict[str, float] = dict(runtime_controls["numeric_thresholds"])
    effective_numeric_specs = {
        k: {**v, "threshold": float(numeric_threshold_overrides.get(k, v["threshold"]))}
        for k, v in NUMERIC_FEATURE_SPECS.items()
    }

    candidate_columns = set(candidates[0].keys()) if candidates else set()
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
    active_component_weights, weight_rebalance_diagnostics = build_active_component_weights(
        set(active_numeric_specs),
        effective_component_weights,
    )
    if round(sum(active_component_weights.values()), 6) != 1.0:
        raise RuntimeError("BL-006 active component weights must sum to 1.0")

    start_time = time.time()
    run_id = f"BL006-SCORE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    profile_lead_map, profile_lead_total = normalize_weight_map(profile["semantic_profile"]["top_lead_genres"], top_k=6)
    profile_genre_map, profile_genre_total = normalize_weight_map(profile["semantic_profile"]["top_genres"], top_k=8)
    profile_tag_map, profile_tag_total = normalize_weight_map(profile["semantic_profile"]["top_tags"], top_k=10)

    scored_rows: list[dict[str, object]] = []

    for row in candidates:
        # DS-001 semantic labels are provided as explicit CSV lists.
        candidate_tags = parse_csv_labels(row.get("tags", ""))
        candidate_genres = parse_csv_labels(row.get("genres", ""))
        lead_genre = resolve_lead_genre(candidate_genres, candidate_tags)

        component_similarity: dict[str, float] = {}
        component_contribution: dict[str, float] = {}

        for profile_column, spec in active_numeric_specs.items():
            value = candidate_numeric_value(row, profile_column, str(spec["candidate_column"]))
            center_raw = profile["numeric_feature_profile"].get(profile_column)
            if center_raw is None or profile_column not in active_component_weights:
                similarity = 0.0
            else:
                similarity = numeric_similarity(value, float(center_raw), float(spec["threshold"]), circular=bool(spec["circular"]))
            component_similarity[profile_column] = similarity
            component_contribution[profile_column] = round(similarity * active_component_weights.get(profile_column, 0.0), 6)

        lead_genre_similarity = 0.0
        if lead_genre and lead_genre in profile_lead_map and profile_lead_total > 0:
            lead_genre_similarity = round(profile_lead_map[lead_genre] / max(profile_lead_map.values()), 6)
        component_similarity["lead_genre"] = lead_genre_similarity
        component_contribution["lead_genre"] = round(lead_genre_similarity * active_component_weights.get("lead_genre", 0.0), 6)

        genre_overlap_similarity, matched_genres = weighted_overlap(candidate_genres, profile_genre_map, profile_genre_total)
        tag_overlap_similarity, matched_tags = weighted_overlap(candidate_tags, profile_tag_map, profile_tag_total)
        component_similarity["genre_overlap"] = genre_overlap_similarity
        component_contribution["genre_overlap"] = round(genre_overlap_similarity * active_component_weights.get("genre_overlap", 0.0), 6)
        component_similarity["tag_overlap"] = tag_overlap_similarity
        component_contribution["tag_overlap"] = round(tag_overlap_similarity * active_component_weights.get("tag_overlap", 0.0), 6)

        final_score = round(sum(component_contribution.values()), 6)

        scored_rows.append(
            {
                "track_id": row["track_id"],
                "lead_genre": lead_genre,
                "matched_genres": "|".join(matched_genres),
                "matched_tags": "|".join(matched_tags),
                "final_score": final_score,
                "tempo_similarity":        component_similarity["tempo"],
                "tempo_contribution":       component_contribution["tempo"],
                "duration_ms_similarity":   component_similarity["duration_ms"],
                "duration_ms_contribution": component_contribution["duration_ms"],
                "key_similarity":           component_similarity["key"],
                "key_contribution":         component_contribution["key"],
                "mode_similarity":          component_similarity["mode"],
                "mode_contribution":        component_contribution["mode"],
                "lead_genre_similarity":    component_similarity["lead_genre"],
                "lead_genre_contribution":  component_contribution["lead_genre"],
                "genre_overlap_similarity": component_similarity["genre_overlap"],
                "genre_overlap_contribution": component_contribution["genre_overlap"],
                "tag_overlap_similarity":   component_similarity["tag_overlap"],
                "tag_overlap_contribution": component_contribution["tag_overlap"],
            }
        )

    scored_rows.sort(key=lambda item: (-float(item["final_score"]), str(item["track_id"])))
    for index, row in enumerate(scored_rows, start=1):
        row["rank"] = index

    scored_path = output_dir / "bl006_scored_candidates.csv"
    with scored_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "rank",
            "track_id",
            "lead_genre",
            "matched_genres",
            "matched_tags",
            "final_score",
            "tempo_similarity",
            "tempo_contribution",
            "duration_ms_similarity",
            "duration_ms_contribution",
            "key_similarity",
            "key_contribution",
            "mode_similarity",
            "mode_contribution",
            "lead_genre_similarity",
            "lead_genre_contribution",
            "genre_overlap_similarity",
            "genre_overlap_contribution",
            "tag_overlap_similarity",
            "tag_overlap_contribution",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(scored_rows)

    top_candidates = [
        {
            "rank": row["rank"],
            "track_id": row["track_id"],
            "lead_genre": row["lead_genre"],
            "final_score": row["final_score"],
            "matched_genres": row["matched_genres"],
            "matched_tags": row["matched_tags"],
        }
        for row in scored_rows[:10]
    ]

    score_values = [float(row["final_score"]) for row in scored_rows]
    top_100_rows = scored_rows[:100]
    top_500_rows = scored_rows[:500]
    summary = {
        "run_id": run_id,
        "task": "BL-006",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_artifacts": {
            "profile_path": str(profile_path),
            "profile_sha256": sha256_of_file(profile_path),
            "filtered_candidates_path": str(filtered_candidates_path),
            "filtered_candidates_sha256": sha256_of_file(filtered_candidates_path),
        },
        "config": {
            "numeric_thresholds": {
                profile_column: spec["threshold"]
                for profile_column, spec in active_numeric_specs.items()
            },
            "numeric_feature_mapping": {
                profile_column: spec["candidate_column"]
                for profile_column, spec in active_numeric_specs.items()
            },
            "base_component_weights": effective_component_weights,
            "active_component_weights": {key: round(value, 6) for key, value in active_component_weights.items()},
            "inactive_components": sorted(set(effective_component_weights) - set(active_component_weights)),
            "weight_rebalance_diagnostics": weight_rebalance_diagnostics,
            "lead_genre_normalization": "candidate lead genre weight divided by max profile lead-genre weight",
            "genre_overlap_normalization": "sum overlapping profile genre weights / sum top profile genre weights",
            "tag_overlap_normalization": "sum overlapping profile tag weights / sum top profile tag weights",
            "semantic_source": "ds001_tags_and_genres_columns",
        },
        "counts": {
            "candidates_scored": len(scored_rows),
        },
        "score_statistics": {
            "max_score": round(max(score_values), 6),
            "min_score": round(min(score_values), 6),
            "mean_score": round(statistics.mean(score_values), 6),
            "median_score": round(statistics.median(score_values), 6),
        },
        "component_balance": {
            "all_candidates": contribution_breakdown(scored_rows),
            "top_100": contribution_breakdown(top_100_rows),
            "top_500": contribution_breakdown(top_500_rows),
        },
        "top_candidates": top_candidates,
        "elapsed_seconds": round(time.time() - start_time, 3),
        "output_files": {
            "scored_candidates_path": str(scored_path),
        },
    }

    summary_path = output_dir / "bl006_score_summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    summary["output_hashes_sha256"] = {
        "bl006_scored_candidates.csv": sha256_of_file(scored_path),
    }
    summary["summary_hash_note"] = "summary file hash collected separately in experiment logging to avoid recursive self-reference"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    print("BL-006 candidate scoring complete.")
    if weight_rebalance_diagnostics["rebalanced"]:
        print("WARNING: BL-006 rebalanced component weights.")
        print(
            "  original_active_weight_sum="
            f"{weight_rebalance_diagnostics['active_weight_sum_pre_normalization']}"
        )
    print(f"scored_candidates={scored_path}")
    print(f"score_summary={summary_path}")


if __name__ == "__main__":
    main()