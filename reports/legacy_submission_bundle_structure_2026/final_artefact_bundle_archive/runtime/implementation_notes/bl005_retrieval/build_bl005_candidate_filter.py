from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add shared utilities to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.config_loader import load_run_config_utils_module
from bl000_shared_utils.constants import (
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
from bl000_shared_utils.env_utils import env_bool, env_int, env_str
from bl000_shared_utils.io_utils import (
    load_csv_rows,
    load_json,
    open_text_write,
    parse_csv_labels,
    sha256_of_file,
)
from bl000_shared_utils.path_utils import repo_root
from bl000_shared_utils.stage_runtime_resolver import (
    load_positive_numeric_map_from_env,
    resolve_run_config_path,
)

# Import modularized BL-005 components
from candidate_parser import (
    candidate_language_code,
    candidate_numeric_value,
    candidate_release_year,
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
    env_numeric_thresholds = load_positive_numeric_map_from_env("BL005_NUMERIC_THRESHOLDS_JSON")
    env_language_filter_enabled = env_bool("BL005_LANGUAGE_FILTER_ENABLED", DEFAULT_LANGUAGE_FILTER_ENABLED)
    env_language_filter_codes_raw = env_str("BL005_LANGUAGE_FILTER_CODES", "")
    env_recency_years_min_offset_raw = env_str("BL005_RECENCY_YEARS_MIN_OFFSET", "")

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
            "language_filter_enabled": env_language_filter_enabled,
            "language_filter_codes": env_language_filter_codes,
            "recency_years_min_offset": env_recency_years_min_offset,
            "numeric_thresholds": env_numeric_thresholds,
        }
    )


def resolve_bl005_paths(root: Path) -> dict[str, Path]:
    profile_path = root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs" / "bl004_preference_profile.json"
    seed_trace_path = root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs" / "bl004_seed_trace.csv"
    candidate_path = (
        root / "07_implementation" / "implementation_notes"
        / "bl000_data_layer" / "outputs" / "ds001_working_candidate_dataset.csv"
    )
    output_dir = root / "07_implementation" / "implementation_notes" / "bl005_retrieval" / "outputs"
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


def evaluate_bl005_candidates(
    *,
    candidate_rows: list[dict[str, object]],
    runtime_context: dict[str, object],
) -> tuple[DecisionTracker, list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    active_numeric_specs: dict[str, dict[str, object]] = runtime_context["active_numeric_specs"]
    seed_track_ids: set[str] = runtime_context["seed_track_ids"]
    top_lead_genres: set[str] = runtime_context["top_lead_genres"]
    top_tags: set[str] = runtime_context["top_tags"]
    top_genres: set[str] = runtime_context["top_genres"]
    numeric_centers: dict[str, float] = runtime_context["numeric_centers"]
    numeric_features_enabled = bool(runtime_context["numeric_features_enabled"])
    semantic_strong_keep_score = int(runtime_context["semantic_strong_keep_score"])
    semantic_min_keep_score = int(runtime_context["semantic_min_keep_score"])
    numeric_support_min_pass = int(runtime_context["numeric_support_min_pass"])
    language_filter_enabled = bool(runtime_context["language_filter_enabled"])
    language_filter_codes = set(runtime_context["language_filter_codes"])
    recency_min_release_year = runtime_context["recency_min_release_year"]

    tracker = DecisionTracker(active_numeric_specs)

    for row in candidate_rows:
        track_id = row["track_id"]
        is_seed_track = track_id in seed_track_ids

        candidate_tags = parse_csv_labels(row.get("tags", ""))
        candidate_genres = parse_csv_labels(row.get("genres", ""))
        lead_genre = resolve_lead_genre(candidate_genres, candidate_tags)
        language_code = candidate_language_code(row)
        release_year = candidate_release_year(row)

        language_match: bool | None = None
        if language_filter_enabled:
            language_match = bool(language_code and language_code in language_filter_codes)

        recency_pass: bool | None = None
        if recency_min_release_year is not None:
            recency_pass = bool(release_year is not None and release_year >= int(recency_min_release_year))

        lead_genre_match = lead_genre in top_lead_genres if lead_genre else False
        genre_overlap = len(top_genres.intersection(candidate_genres))
        tag_overlap = len(top_tags.intersection(candidate_tags))

        semantic_score = 0
        semantic_score += 1 if lead_genre_match else 0
        semantic_score += 1 if genre_overlap > 0 else 0
        semantic_score += 1 if tag_overlap > 0 else 0

        tracker.record_semantic_scores(semantic_score, lead_genre_match, genre_overlap, tag_overlap)

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

        tracker.record_numeric_scores(numeric_pass_count, numeric_rule_hits_this_candidate)

        kept, decision_path = keep_decision(
            is_seed_track,
            semantic_score,
            numeric_pass_count,
            numeric_features_enabled,
            semantic_strong_keep_score,
            semantic_min_keep_score,
            numeric_support_min_pass,
            language_match=language_match,
            recency_pass=recency_pass,
        )

        decision_row = {
            "track_id": track_id,
            "is_seed_track": int(is_seed_track),
            "lead_genre": lead_genre,
            "semantic_score": semantic_score,
            "lead_genre_match": int(lead_genre_match),
            "genre_overlap_count": genre_overlap,
            "tag_overlap_count": tag_overlap,
            "language": language_code or "",
            "language_match": "" if language_match is None else int(language_match),
            "release_year": "" if release_year is None else release_year,
            "release_year_distance": numeric_distances.get("release_year"),
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

        tracker.record_decision(
            track_id,
            is_seed_track,
            kept,
            decision_path,
            decision_row,
            row if kept else None,
        )

    summary = tracker.get_summary()
    return tracker, tracker.decisions, tracker.kept_rows, summary


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
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
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
    root = repo_root()
    paths = resolve_bl005_paths(root)
    output_dir = paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_paths_exist([paths["profile_path"], paths["seed_trace_path"], paths["candidate_path"]])

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
