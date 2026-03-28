from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from shared_utils.config_loader import load_run_config_utils_module
from shared_utils.constants import (
    DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
    DEFAULT_NUMERIC_SUPPORT_MIN_PASS,
    DEFAULT_LANGUAGE_FILTER_CODES,
    DEFAULT_LANGUAGE_FILTER_ENABLED,
    DEFAULT_PROFILE_TOP_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_TAG_LIMIT,
    DEFAULT_RECENCY_YEARS_MIN_OFFSET,
    DEFAULT_SEMANTIC_MIN_KEEP_SCORE,
    DEFAULT_SEMANTIC_STRONG_KEEP_SCORE,
    NUMERIC_FEATURE_SPECS,
)
from shared_utils.env_utils import env_bool, env_float, env_int, env_str
from shared_utils.io_utils import (
    load_csv_rows,
    load_json,
    open_text_write,
    sha256_of_file,
    utc_now,
)
from shared_utils.path_utils import impl_root
from shared_utils.stage_utils import ensure_paths_exist
from shared_utils.stage_runtime_resolver import (
    load_positive_numeric_map_from_env,
    resolve_run_config_path,
)

# Import modularized BL-005 components
from retrieval.candidate_parser import (
    normalize_candidate_row,
)
from retrieval.profile_builder import build_active_numeric_specs, build_profile_label_set
from retrieval.candidate_evaluator import evaluate_bl005_candidates


DECISION_FIELDS = [
    "track_id",
    "is_seed_track",
    "lead_genre",
    "semantic_score",
    "lead_genre_match",
    "genre_overlap_count",
    "tag_overlap_count",
    "language",
    "language_match",
    "release_year",
    "release_year_distance",
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




def resolve_bl005_runtime_controls() -> dict[str, object]:
    env_numeric_thresholds = load_positive_numeric_map_from_env("BL005_NUMERIC_THRESHOLDS_JSON")
    env_language_filter_enabled = env_bool("BL005_LANGUAGE_FILTER_ENABLED", DEFAULT_LANGUAGE_FILTER_ENABLED)
    env_language_filter_codes_raw = env_str("BL005_LANGUAGE_FILTER_CODES", "")
    env_recency_years_min_offset_raw = env_str("BL005_RECENCY_YEARS_MIN_OFFSET", "")
    env_lead_genre_partial_match_threshold = env_float(
        "BL005_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD",
        DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
    )

    def parse_optional_positive_int(raw: object) -> int | None:
        text = str(raw).strip()
        if not text:
            return None
        try:
            parsed = int(text)
        except ValueError:
            return None
        return parsed if parsed > 0 else None

    def normalize_language_codes(raw_values: object) -> list[str]:
        if not isinstance(raw_values, list):
            return []
        normalized: list[str] = []
        seen: set[str] = set()
        for item in raw_values:
            code = str(item).strip().lower()
            if not code or code in seen:
                continue
            seen.add(code)
            normalized.append(code)
        return normalized

    env_language_filter_codes = [
        token.strip().lower()
        for token in env_language_filter_codes_raw.split(",")
        if token.strip()
    ]
    env_recency_years_min_offset = parse_optional_positive_int(env_recency_years_min_offset_raw)

    def sanitize_controls(controls: dict[str, object]) -> dict[str, object]:
        controls["profile_top_lead_genre_limit"] = max(1, int(controls["profile_top_lead_genre_limit"]))
        controls["profile_top_tag_limit"] = max(1, int(controls["profile_top_tag_limit"]))
        controls["profile_top_genre_limit"] = max(1, int(controls["profile_top_genre_limit"]))
        controls["semantic_strong_keep_score"] = max(0, min(3, int(controls["semantic_strong_keep_score"])))
        controls["semantic_min_keep_score"] = max(0, min(3, int(controls["semantic_min_keep_score"])))
        controls["numeric_support_min_pass"] = max(0, int(controls["numeric_support_min_pass"]))
        controls["lead_genre_partial_match_threshold"] = max(
            0.0,
            min(1.0, float(controls.get("lead_genre_partial_match_threshold", DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD))),
        )
        controls["language_filter_codes"] = normalize_language_codes(controls.get("language_filter_codes", []))
        controls["language_filter_enabled"] = bool(controls.get("language_filter_enabled", False)) and bool(controls["language_filter_codes"])
        controls["recency_years_min_offset"] = parse_optional_positive_int(controls.get("recency_years_min_offset", ""))
        if controls["semantic_min_keep_score"] > controls["semantic_strong_keep_score"]:
            controls["semantic_min_keep_score"] = controls["semantic_strong_keep_score"]
        return controls

    run_config_path = resolve_run_config_path()
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
                "lead_genre_partial_match_threshold": controls.get(
                    "lead_genre_partial_match_threshold",
                    DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
                ),
                "language_filter_enabled": bool(controls.get("language_filter_enabled", DEFAULT_LANGUAGE_FILTER_ENABLED)),
                "language_filter_codes": list(controls.get("language_filter_codes") or DEFAULT_LANGUAGE_FILTER_CODES),
                "recency_years_min_offset": controls.get("recency_years_min_offset", DEFAULT_RECENCY_YEARS_MIN_OFFSET),
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
            "lead_genre_partial_match_threshold": env_lead_genre_partial_match_threshold,
            "language_filter_enabled": env_language_filter_enabled,
            "language_filter_codes": env_language_filter_codes,
            "recency_years_min_offset": env_recency_years_min_offset,
            "numeric_thresholds": env_numeric_thresholds,
        }
    )


def resolve_bl005_paths(root: Path) -> dict[str, Path]:
    profile_path = root / "profile" / "outputs" / "bl004_preference_profile.json"
    seed_trace_path = root / "profile" / "outputs" / "bl004_seed_trace.csv"
    candidate_path = (
        root / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv"
    )
    output_dir = root / "retrieval" / "outputs"
    return {
        "profile_path": profile_path,
        "seed_trace_path": seed_trace_path,
        "candidate_path": candidate_path,
        "output_dir": output_dir,
    }


def load_bl005_inputs(paths: dict[str, Path]) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    profile = load_json(paths["profile_path"])
    candidate_rows_raw = load_csv_rows(paths["candidate_path"])
    if not candidate_rows_raw:
        raise RuntimeError("BL-005 candidate corpus is empty; cannot build retrieval outputs")
    candidate_rows = [normalize_candidate_row(row) for row in candidate_rows_raw]
    seed_trace_rows = load_csv_rows(paths["seed_trace_path"])
    return profile, candidate_rows, seed_trace_rows


def build_bl005_runtime_context(
    *,
    profile: dict[str, object],
    candidate_rows: list[dict[str, object]],
    seed_trace_rows: list[dict[str, object]],
    runtime_controls: dict[str, object],
) -> dict[str, object]:
    profile_top_lead_genre_limit = int(runtime_controls["profile_top_lead_genre_limit"])
    profile_top_tag_limit = int(runtime_controls["profile_top_tag_limit"])
    profile_top_genre_limit = int(runtime_controls["profile_top_genre_limit"])
    semantic_strong_keep_score = int(runtime_controls["semantic_strong_keep_score"])
    semantic_min_keep_score = int(runtime_controls["semantic_min_keep_score"])
    numeric_support_min_pass = int(runtime_controls["numeric_support_min_pass"])
    lead_genre_partial_match_threshold = float(runtime_controls["lead_genre_partial_match_threshold"])
    numeric_threshold_overrides: dict[str, float] = runtime_controls.get("numeric_thresholds") or {}

    effective_numeric_specs = {
        k: {**v, "threshold": float(numeric_threshold_overrides.get(k, v["threshold"]))}
        for k, v in NUMERIC_FEATURE_SPECS.items()
    }

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
    language_filter_enabled = bool(runtime_controls.get("language_filter_enabled", False))
    language_filter_codes = {
        code for code in list(runtime_controls.get("language_filter_codes") or []) if code
    }
    recency_years_min_offset_raw = runtime_controls.get("recency_years_min_offset")
    recency_years_min_offset = int(recency_years_min_offset_raw) if recency_years_min_offset_raw else None
    current_year_utc = datetime.now(timezone.utc).year
    recency_min_release_year = (
        current_year_utc - recency_years_min_offset if recency_years_min_offset is not None else None
    )

    return {
        "profile_top_lead_genre_limit": profile_top_lead_genre_limit,
        "profile_top_tag_limit": profile_top_tag_limit,
        "profile_top_genre_limit": profile_top_genre_limit,
        "semantic_strong_keep_score": semantic_strong_keep_score,
        "semantic_min_keep_score": semantic_min_keep_score,
        "numeric_support_min_pass": numeric_support_min_pass,
        "lead_genre_partial_match_threshold": lead_genre_partial_match_threshold,
        "active_numeric_specs": active_numeric_specs,
        "seed_track_ids": seed_track_ids,
        "top_lead_genres": top_lead_genres,
        "top_tags": top_tags,
        "top_genres": top_genres,
        "numeric_centers": numeric_centers,
        "numeric_features_enabled": numeric_features_enabled,
        "language_filter_enabled": language_filter_enabled,
        "language_filter_codes": sorted(language_filter_codes),
        "recency_years_min_offset": recency_years_min_offset,
        "current_year_utc": current_year_utc,
        "recency_min_release_year": recency_min_release_year,
    }




def write_bl005_output_artifacts(
    *,
    output_dir: Path,
    candidate_rows: list[dict[str, object]],
    decisions: list[dict[str, object]],
    kept_rows: list[dict[str, object]],
) -> dict[str, Path]:
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

    return {
        "filtered_path": filtered_path,
        "decisions_path": decisions_path,
    }


def build_bl005_diagnostics_payload(
    *,
    run_id: str,
    elapsed_seconds: float,
    paths: dict[str, Path],
    runtime_context: dict[str, object],
    summary: dict[str, object],
    candidate_rows: list[dict[str, object]],
    kept_rows: list[dict[str, object]],
    output_paths: dict[str, Path],
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "task": "BL-005",
        "generated_at_utc": utc_now(),
        "input_artifacts": {
            "profile_path": str(paths["profile_path"]),
            "profile_sha256": sha256_of_file(paths["profile_path"]),
            "seed_trace_path": str(paths["seed_trace_path"]),
            "seed_trace_sha256": sha256_of_file(paths["seed_trace_path"]),
            "candidate_stub_path": str(paths["candidate_path"]),
            "candidate_stub_sha256": sha256_of_file(paths["candidate_path"]),
        },
        "config": {
            "top_lead_genre_limit": int(runtime_context["profile_top_lead_genre_limit"]),
            "top_tag_limit": int(runtime_context["profile_top_tag_limit"]),
            "top_genre_limit": int(runtime_context["profile_top_genre_limit"]),
            "numeric_thresholds": {
                profile_column: spec["threshold"]
                for profile_column, spec in runtime_context["active_numeric_specs"].items()
            },
            "language_filter": {
                "enabled": bool(runtime_context["language_filter_enabled"]),
                "codes": list(runtime_context["language_filter_codes"]),
            },
            "recency_gate": {
                "years_min_offset": runtime_context["recency_years_min_offset"],
                "current_year_utc": runtime_context["current_year_utc"],
                "min_release_year": runtime_context["recency_min_release_year"],
            },
            "numeric_feature_mapping": {
                profile_column: spec["candidate_column"]
                for profile_column, spec in runtime_context["active_numeric_specs"].items()
            },
            "numeric_features_enabled": bool(runtime_context["numeric_features_enabled"]),
            "keep_rule": (
                f"keep if not seed and (semantic_score >= {int(runtime_context['semantic_strong_keep_score'])} or "
                f"(semantic_score >= {int(runtime_context['semantic_min_keep_score'])} and numeric_pass_count >= {int(runtime_context['numeric_support_min_pass'])}))"
                if runtime_context["numeric_features_enabled"]
                else f"keep if not seed and semantic_score >= {int(runtime_context['semantic_min_keep_score'])}"
            ),
            "semantic_source": "ds001_tags_and_genres_columns",
        },
        "counts": {
            "candidate_rows_total": len(candidate_rows),
            "seed_tracks_excluded": summary["decision_counts"]["seed_excluded"],
            "kept_candidates": len(kept_rows),
            "rejected_non_seed_candidates": summary["decision_counts"]["rejected_threshold"],
            "rejected_by_language_filter": int(summary["decision_path_counts"].get("reject_language_filter", 0)),
            "rejected_by_recency_gate": int(summary["decision_path_counts"].get("reject_recency_gate", 0)),
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
        "elapsed_seconds": round(elapsed_seconds, 3),
        "output_files": {
            "filtered_candidates_path": str(output_paths["filtered_path"]),
            "candidate_decisions_path": str(output_paths["decisions_path"]),
        },
    }


def write_bl005_diagnostics_with_hashes(
    *,
    diagnostics: dict[str, object],
    diagnostics_path: Path,
    output_paths: dict[str, Path],
) -> None:
    with open_text_write(diagnostics_path) as handle:
        json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    diagnostics["output_hashes_sha256"] = {
        "bl005_filtered_candidates.csv": sha256_of_file(output_paths["filtered_path"]),
        "bl005_candidate_decisions.csv": sha256_of_file(output_paths["decisions_path"]),
    }
    diagnostics["diagnostics_hash_note"] = "diagnostics file does not store its own hash to avoid recursive self-reference"
    with open_text_write(diagnostics_path) as handle:
        json.dump(diagnostics, handle, indent=2, ensure_ascii=True)


def main() -> None:
    root = impl_root()
    paths = resolve_bl005_paths(root)
    output_dir = paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_paths_exist([paths["profile_path"], paths["seed_trace_path"], paths["candidate_path"]], stage_label="BL-005")

    runtime_controls = resolve_bl005_runtime_controls()
    profile, candidate_rows, seed_trace_rows = load_bl005_inputs(paths)
    runtime_context = build_bl005_runtime_context(
        profile=profile,
        candidate_rows=candidate_rows,
        seed_trace_rows=seed_trace_rows,
        runtime_controls=runtime_controls,
    )

    start_time = time.time()
    run_id = f"BL005-FILTER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    _, decisions, kept_rows, summary = evaluate_bl005_candidates(
        candidate_rows=candidate_rows,
        runtime_context=runtime_context,
    )

    output_paths = write_bl005_output_artifacts(
        output_dir=output_dir,
        candidate_rows=candidate_rows,
        decisions=decisions,
        kept_rows=kept_rows,
    )

    diagnostics = build_bl005_diagnostics_payload(
        run_id=run_id,
        elapsed_seconds=time.time() - start_time,
        paths=paths,
        runtime_context=runtime_context,
        summary=summary,
        candidate_rows=candidate_rows,
        kept_rows=kept_rows,
        output_paths=output_paths,
    )

    diagnostics_path = output_dir / "bl005_candidate_diagnostics.json"
    write_bl005_diagnostics_with_hashes(
        diagnostics=diagnostics,
        diagnostics_path=diagnostics_path,
        output_paths=output_paths,
    )

    print("BL-005 candidate filtering complete.")
    print(f"filtered_candidates={output_paths['filtered_path']}")
    print(f"decisions={output_paths['decisions_path']}")
    print(f"diagnostics={diagnostics_path}")


if __name__ == "__main__":
    main()
