"""
BL-006: Score candidates based on profile preference model.

Computes weighted similarity scores for each filtered candidate against
the user preference profile created by BL-004. Main scoring loop reduced
to high-level orchestration via modular sub-components.

Modules:
- scoring_engine: Core similarity computation (numeric_similarity, weighted_overlap, etc.)
- candidate_parsed: Candidate data extraction and normalization
- profile_extractor: Profile data extraction and specification building
- result_reporter: Result reporting and statistics accumulation
"""

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

from bl000_shared_utils.io_utils import open_text_write, sha256_of_file, load_json, load_csv_rows
from bl000_shared_utils.path_utils import impl_root
from bl000_shared_utils.config_loader import load_run_config_utils_module
from bl000_shared_utils.stage_runtime_resolver import (
    load_positive_numeric_map_from_env,
    resolve_run_config_path,
)
from bl006_scoring.scoring_engine import (
    compute_component_scores,
    compute_final_score,
    compute_weighted_contributions,
)
from bl006_scoring.candidate_parsed import parse_candidate_attributes
from bl006_scoring.profile_extractor import extract_profile_scoring_data, build_component_weights, build_numeric_specs


# Numeric feature specifications for comparison between profile and candidates
NUMERIC_FEATURE_SPECS = build_numeric_specs()
NUMERIC_COMPONENTS = set(NUMERIC_FEATURE_SPECS)
SCORED_CANDIDATE_FIELDS = [
    "rank",
    "track_id",
    "lead_genre",
    "matched_genres",
    "matched_tags",
    "final_score",
    "danceability_similarity",
    "danceability_contribution",
    "energy_similarity",
    "energy_contribution",
    "valence_similarity",
    "valence_contribution",
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


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    if p <= 0:
        return sorted_values[0]
    if p >= 100:
        return sorted_values[-1]
    rank = (len(sorted_values) - 1) * (p / 100.0)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    if lower == upper:
        return sorted_values[lower]
    fraction = rank - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction


def build_score_distribution_diagnostics(scored_rows: list[dict[str, object]]) -> dict[str, object]:
    score_desc = [float(row["final_score"]) for row in scored_rows]
    score_desc.sort(reverse=True)

    gaps: list[dict[str, float | int]] = []
    for index in range(len(score_desc) - 1):
        gap = score_desc[index] - score_desc[index + 1]
        gaps.append(
            {
                "between_rank": index + 1,
                "next_rank": index + 2,
                "score_gap": round(gap, 6),
            }
        )

    max_gap = max(gaps, key=lambda item: float(item["score_gap"])) if gaps else None
    rank_2_to_3_gap = round(score_desc[1] - score_desc[2], 6) if len(score_desc) >= 3 else 0.0
    is_rank_cliff = bool(max_gap and float(max_gap["score_gap"]) >= 0.1)

    score_asc = list(reversed(score_desc))
    percentiles = {
        "p10": round(percentile(score_asc, 10), 6),
        "p25": round(percentile(score_asc, 25), 6),
        "p50": round(percentile(score_asc, 50), 6),
        "p75": round(percentile(score_asc, 75), 6),
        "p90": round(percentile(score_asc, 90), 6),
        "p95": round(percentile(score_asc, 95), 6),
        "p99": round(percentile(score_asc, 99), 6),
    }

    return {
        "score_percentiles": percentiles,
        "score_range": {
            "max": round(score_desc[0], 6) if score_desc else 0.0,
            "min": round(score_desc[-1], 6) if score_desc else 0.0,
        },
        "rank_cliff": {
            "detected": is_rank_cliff,
            "rank_2_to_3_gap": rank_2_to_3_gap,
            "max_gap": max_gap or {"between_rank": 0, "next_rank": 0, "score_gap": 0.0},
            "classification": "cliff" if is_rank_cliff else "smooth",
        },
    }


def load_component_weight_overrides(defaults: dict[str, float]) -> dict[str, float]:
    """Load component weight overrides from environment."""
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


def build_active_component_weights(
    active_numeric_components: set[str],
    component_weights: dict[str, float],
) -> tuple[dict[str, float], dict[str, object]]:
    """
    Filter and normalize active component weights.

    Drops numeric components not present in active set and re-normalizes
    remaining weights to sum to 1.0. Generates diagnostics about rebalancing.
    """
    active = {}
    for component, weight in component_weights.items():
        component_name = component.removesuffix("_score")
        if component_name in NUMERIC_COMPONENTS and component_name not in active_numeric_components:
            continue
        active[component] = weight
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


def _load_bl006_numeric_thresholds_from_env() -> dict[str, float]:
    """Load numeric threshold overrides from environment."""
    return load_positive_numeric_map_from_env("BL006_NUMERIC_THRESHOLDS_JSON")


def resolve_bl006_runtime_controls() -> dict[str, object]:
    """Resolve runtime controls from run-config or environment."""
    default_weights = build_component_weights()
    run_config_path = resolve_run_config_path()
    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl006_controls(run_config_path)
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "component_weights": dict(controls.get("component_weights") or default_weights),
            "numeric_thresholds": dict(controls.get("numeric_thresholds") or {}),
        }
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "component_weights": load_component_weight_overrides(default_weights),
        "numeric_thresholds": _load_bl006_numeric_thresholds_from_env(),
    }


def ensure_paths_exist(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "BL-006 missing required input artifact(s): " + ", ".join(missing)
        )


def contribution_breakdown(rows: list[dict[str, object]]) -> dict[str, float]:
    """Compute average component contributions across rows."""
    numeric_components = ["danceability", "energy", "valence", "tempo", "duration_ms", "key", "mode"]
    semantic_components = ["lead_genre", "genre_overlap", "tag_overlap"]
    if not rows:
        return {
            "numeric_contribution_mean": 0.0,
            "semantic_contribution_mean": 0.0,
            **{f"{component}_mean": 0.0 for component in numeric_components + semantic_components},
        }

    def mean_of(key: str) -> float:
        return round(statistics.mean(float(row[key]) for row in rows), 6)

    component_means = {
        f"{component}_mean": mean_of(f"{component}_contribution")
        for component in numeric_components + semantic_components
    }

    numeric_mean = round(sum(component_means[f"{component}_mean"] for component in numeric_components), 6)
    semantic_mean = round(sum(component_means[f"{component}_mean"] for component in semantic_components), 6)

    return {
        "numeric_contribution_mean": numeric_mean,
        "semantic_contribution_mean": semantic_mean,
        **component_means,
    }


def resolve_bl006_paths(root: Path) -> dict[str, Path]:
    profile_path = root / "bl004_profile" / "outputs" / "bl004_preference_profile.json"
    filtered_candidates_path = (
        root / "bl005_retrieval" / "outputs" / "bl005_filtered_candidates.csv"
    )
    output_dir = root / "bl006_scoring" / "outputs"
    return {
        "profile_path": profile_path,
        "filtered_candidates_path": filtered_candidates_path,
        "output_dir": output_dir,
    }


def load_bl006_inputs(paths: dict[str, Path]) -> tuple[dict[str, object], list[dict[str, object]]]:
    profile = load_json(paths["profile_path"])
    candidates = load_csv_rows(paths["filtered_candidates_path"])
    if not candidates:
        raise RuntimeError("No BL-005 filtered candidates found for BL-006")
    return profile, candidates


def build_bl006_runtime_context(
    *,
    profile: dict[str, object],
    runtime_controls: dict[str, object],
) -> dict[str, object]:
    effective_component_weights: dict[str, float] = dict(runtime_controls["component_weights"])
    numeric_threshold_overrides: dict[str, float] = dict(runtime_controls["numeric_thresholds"])
    effective_numeric_specs = {
        k: {**v, "threshold": float(numeric_threshold_overrides.get(k, v["threshold"]))}
        for k, v in NUMERIC_FEATURE_SPECS.items()
    }

    profile_scoring_data = extract_profile_scoring_data(profile, effective_numeric_specs)
    active_numeric_specs = {
        k: v
        for k, v in effective_numeric_specs.items()
        if k in profile_scoring_data["numeric_centers"]
    }

    active_component_weights, weight_rebalance_diagnostics = build_active_component_weights(
        set(active_numeric_specs),
        effective_component_weights,
    )
    if round(sum(active_component_weights.values()), 6) != 1.0:
        raise RuntimeError("BL-006 active component weights must sum to 1.0")

    return {
        "effective_component_weights": effective_component_weights,
        "active_numeric_specs": active_numeric_specs,
        "profile_scoring_data": profile_scoring_data,
        "active_component_weights": active_component_weights,
        "weight_rebalance_diagnostics": weight_rebalance_diagnostics,
    }


def score_bl006_candidates(
    *,
    candidates: list[dict[str, object]],
    runtime_context: dict[str, object],
) -> list[dict[str, object]]:
    profile_scoring_data: dict[str, object] = runtime_context["profile_scoring_data"]
    active_numeric_specs: dict[str, dict[str, object]] = runtime_context["active_numeric_specs"]
    active_component_weights: dict[str, float] = runtime_context["active_component_weights"]

    scored_rows: list[dict[str, object]] = []
    for row in candidates:
        candidate_attrs = parse_candidate_attributes(row)
        component_scores = compute_component_scores(
            candidate_attrs,
            profile_scoring_data,
            active_numeric_specs,
        )
        weighted_contributions = compute_weighted_contributions(
            component_scores,
            active_component_weights,
        )
        final_score = compute_final_score(component_scores, active_component_weights)

        scored_rows.append(
            {
                "track_id": row.get("track_id", ""),
                "lead_genre": candidate_attrs.get("lead_genre", ""),
                "matched_genres": "|".join(component_scores.get("matched_genres", [])),
                "matched_tags": "|".join(component_scores.get("matched_tags", [])),
                "final_score": final_score,
                "danceability_similarity": component_scores.get("danceability_similarity", 0.0),
                "danceability_contribution": weighted_contributions.get("danceability_contribution", 0.0),
                "energy_similarity": component_scores.get("energy_similarity", 0.0),
                "energy_contribution": weighted_contributions.get("energy_contribution", 0.0),
                "valence_similarity": component_scores.get("valence_similarity", 0.0),
                "valence_contribution": weighted_contributions.get("valence_contribution", 0.0),
                "tempo_similarity": component_scores.get("tempo_similarity", 0.0),
                "tempo_contribution": weighted_contributions.get("tempo_contribution", 0.0),
                "duration_ms_similarity": component_scores.get("duration_ms_similarity", 0.0),
                "duration_ms_contribution": weighted_contributions.get("duration_ms_contribution", 0.0),
                "key_similarity": component_scores.get("key_similarity", 0.0),
                "key_contribution": weighted_contributions.get("key_contribution", 0.0),
                "mode_similarity": component_scores.get("mode_similarity", 0.0),
                "mode_contribution": weighted_contributions.get("mode_contribution", 0.0),
                "lead_genre_similarity": component_scores.get("lead_genre_similarity", 0.0),
                "lead_genre_contribution": weighted_contributions.get("lead_genre_contribution", 0.0),
                "genre_overlap_similarity": component_scores.get("genre_overlap_similarity", 0.0),
                "genre_overlap_contribution": weighted_contributions.get("genre_overlap_contribution", 0.0),
                "tag_overlap_similarity": component_scores.get("tag_overlap_similarity", 0.0),
                "tag_overlap_contribution": weighted_contributions.get("tag_overlap_contribution", 0.0),
            }
        )

    scored_rows.sort(key=lambda item: (-float(item["final_score"]), str(item["track_id"])))
    for index, row in enumerate(scored_rows, start=1):
        row["rank"] = index
    return scored_rows


def write_bl006_scored_csv(*, scored_rows: list[dict[str, object]], scored_path: Path) -> None:
    with open_text_write(scored_path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCORED_CANDIDATE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(scored_rows)


def build_bl006_summary(
    *,
    run_id: str,
    elapsed_seconds: float,
    paths: dict[str, Path],
    runtime_context: dict[str, object],
    scored_rows: list[dict[str, object]],
    distribution_diagnostics: dict[str, object],
    diagnostics_path: Path,
    scored_path: Path,
) -> dict[str, object]:
    effective_component_weights: dict[str, float] = runtime_context["effective_component_weights"]
    active_numeric_specs: dict[str, dict[str, object]] = runtime_context["active_numeric_specs"]
    active_component_weights: dict[str, float] = runtime_context["active_component_weights"]
    weight_rebalance_diagnostics: dict[str, object] = runtime_context["weight_rebalance_diagnostics"]

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

    return {
        "run_id": run_id,
        "task": "BL-006",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_artifacts": {
            "profile_path": str(paths["profile_path"]),
            "profile_sha256": sha256_of_file(paths["profile_path"]),
            "filtered_candidates_path": str(paths["filtered_candidates_path"]),
            "filtered_candidates_sha256": sha256_of_file(paths["filtered_candidates_path"]),
        },
        "config": {
            "numeric_thresholds": {
                profile_column: spec["threshold"]
                for profile_column, spec in active_numeric_specs.items()
            },
            "numeric_feature_mapping": {
                profile_column: spec.get("candidate_column", profile_column)
                for profile_column, spec in active_numeric_specs.items()
            },
            "base_component_weights": effective_component_weights,
            "active_component_weights": {key: round(value, 6) for key, value in active_component_weights.items()},
            "inactive_components": sorted(set(effective_component_weights) - set(active_component_weights)),
            "weight_rebalance_diagnostics": weight_rebalance_diagnostics,
            "lead_genre_normalization": "binary exact match against non-empty profile lead genre",
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
        "score_distribution_diagnostics": distribution_diagnostics,
        "top_candidates": top_candidates,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "output_files": {
            "scored_candidates_path": str(scored_path),
            "score_distribution_diagnostics_path": str(diagnostics_path),
        },
    }


def main() -> None:
    """Main BL-006 scoring orchestrator."""
    root = impl_root()
    paths = resolve_bl006_paths(root)
    output_dir = paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    ensure_paths_exist([paths["profile_path"], paths["filtered_candidates_path"]])
    profile, candidates = load_bl006_inputs(paths)

    runtime_controls = resolve_bl006_runtime_controls()
    runtime_context = build_bl006_runtime_context(
        profile=profile,
        runtime_controls=runtime_controls,
    )
    weight_rebalance_diagnostics: dict[str, object] = runtime_context["weight_rebalance_diagnostics"]

    start_time = time.time()
    run_id = f"BL006-SCORE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    scored_rows = score_bl006_candidates(
        candidates=candidates,
        runtime_context=runtime_context,
    )

    scored_path = output_dir / "bl006_scored_candidates.csv"
    write_bl006_scored_csv(scored_rows=scored_rows, scored_path=scored_path)

    distribution_diagnostics = build_score_distribution_diagnostics(scored_rows)

    diagnostics_path = output_dir / "bl006_score_distribution_diagnostics.json"
    with open_text_write(diagnostics_path) as handle:
        json.dump(distribution_diagnostics, handle, indent=2, ensure_ascii=True)

    summary = build_bl006_summary(
        run_id=run_id,
        elapsed_seconds=time.time() - start_time,
        paths=paths,
        runtime_context=runtime_context,
        scored_rows=scored_rows,
        distribution_diagnostics=distribution_diagnostics,
        diagnostics_path=diagnostics_path,
        scored_path=scored_path,
    )

    summary["output_hashes_sha256"] = {
        "bl006_scored_candidates.csv": sha256_of_file(scored_path),
        "bl006_score_distribution_diagnostics.json": sha256_of_file(diagnostics_path),
    }
    summary["summary_hash_note"] = "summary file hash collected separately in experiment logging to avoid recursive self-reference"
    summary_path = output_dir / "bl006_score_summary.json"
    with open_text_write(summary_path) as handle:
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
