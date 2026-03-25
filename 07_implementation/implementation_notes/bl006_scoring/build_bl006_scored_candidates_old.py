from __future__ import annotations

import csv
import json
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.io_utils import sha256_of_file, load_json, load_csv_rows
from bl000_shared_utils.path_utils import repo_root
from bl000_shared_utils.config_loader import load_run_config_utils_module
from bl006_scoring.scoring_engine import numeric_similarity, weighted_overlap, compute_component_scores, compute_final_score
from bl006_scoring.candidate_parsed import parse_candidate_attributes
from bl006_scoring.profile_extractor import extract_profile_scoring_data, build_component_weights, build_numeric_specs
from bl006_scoring.result_reporter import initialize_scoring_report, add_result_to_report, finalize_report, generate_summary_report


# Numeric feature specifications for comparison between profile and candidates
NUMERIC_FEATURE_SPECS = build_numeric_specs()


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
        / "bl000_run_config"
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
    """Main BL-006 scoring orchestrator."""
    root = repo_root()
    profile_path = root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs" / "bl004_preference_profile.json"
    filtered_candidates_path = root / "07_implementation" / "implementation_notes" / "bl005_retrieval" / "outputs" / "bl005_filtered_candidates.csv"
    output_dir = root / "07_implementation" / "implementation_notes" / "bl006_scoring" / "outputs"
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

    # Extract scoring data from profile
    profile_scoring_data = extract_profile_scoring_data(profile, effective_numeric_specs)
    numeric_centers = profile_scoring_data["numeric_centers"]
    numeric_thresholds = profile_scoring_data["numeric_thresholds"]
    lead_genre = profile_scoring_data["lead_genre"]
    genre_weights = profile_scoring_data["genre_weights"]
    tag_weights = profile_scoring_data["tag_weights"]

    # Determine which numeric components are active
    active_numeric_specs = {k: v for k, v in effective_numeric_specs.items() if k in numeric_centers}

    active_component_weights, weight_rebalance_diagnostics = build_active_component_weights(
        set(active_numeric_specs),
        effective_component_weights,
    )
    if round(sum(active_component_weights.values()), 6) != 1.0:
        raise RuntimeError("BL-006 active component weights must sum to 1.0")

    start_time = time.time()
    run_id = f"BL006-SCORE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    scored_rows: list[dict[str, object]] = []

    for row in candidates:
        # Parse candidate attributes  
        candidate_attrs = parse_candidate_attributes(row)
        candidate_genres = candidate_attrs.get("genres", [])
        candidate_tags = candidate_attrs.get("tags", [])

        # Compute component scores using scoring engine
        component_scores = compute_component_scores(
            candidate_attrs, 
            profile_scoring_data,
            active_numeric_specs,
        )
        
        # Compute final score via weighted aggregation
        final_score = compute_final_score(component_scores, active_component_weights)

        scored_rows.append(
            {
                "track_id": row["track_id"],
                "lead_genre": candidate_attrs.get("lead_genre", ""),
                "matched_genres": "|".join(candidate_attrs.get("matched_genres", [])),
                "matched_tags": "|".join(candidate_attrs.get("matched_tags", [])),
                "final_score": final_score,
                "tempo_similarity":        component_scores.get("tempo_similarity", 0.0),
                "tempo_contribution":      component_scores.get("tempo_contribution", 0.0),
                "duration_ms_similarity":  component_scores.get("duration_ms_similarity", 0.0),
                "duration_ms_contribution": component_scores.get("duration_ms_contribution", 0.0),
                "key_similarity":          component_scores.get("key_similarity", 0.0),
                "key_contribution":        component_scores.get("key_contribution", 0.0),
                "mode_similarity":         component_scores.get("mode_similarity", 0.0),
                "mode_contribution":       component_scores.get("mode_contribution", 0.0),
                "lead_genre_similarity":   component_scores.get("lead_genre_similarity", 0.0),
                "lead_genre_contribution": component_scores.get("lead_genre_contribution", 0.0),
                "genre_overlap_similarity": component_scores.get("genre_overlap_similarity", 0.0),
                "genre_overlap_contribution": component_scores.get("genre_overlap_contribution", 0.0),
                "tag_overlap_similarity":  component_scores.get("tag_overlap_similarity", 0.0),
                "tag_overlap_contribution": component_scores.get("tag_overlap_contribution", 0.0),
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