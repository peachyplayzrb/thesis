from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared_utils.config_loader import load_run_config_utils_module
from shared_utils.constants import (
    DEFAULT_LANGUAGE_FILTER_CODES,
    DEFAULT_LANGUAGE_FILTER_ENABLED,
    DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
    DEFAULT_NUMERIC_SUPPORT_MIN_PASS,
    DEFAULT_NUMERIC_SUPPORT_MIN_SCORE,
    DEFAULT_PROFILE_TOP_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_TAG_LIMIT,
    DEFAULT_RECENCY_YEARS_MIN_OFFSET,
    DEFAULT_RETRIEVAL_ENABLE_POPULARITY_NUMERIC,
    DEFAULT_RETRIEVAL_USE_CONTINUOUS_NUMERIC,
    DEFAULT_RETRIEVAL_USE_WEIGHTED_SEMANTICS,
    DEFAULT_SEMANTIC_MIN_KEEP_SCORE,
    DEFAULT_SEMANTIC_STRONG_KEEP_SCORE,
    NUMERIC_FEATURE_SPECS,
)
from shared_utils.env_utils import env_bool, env_float, env_int, env_str
from shared_utils.io_utils import load_csv_rows, load_json, open_text_write, sha256_of_file, utc_now
from shared_utils.path_utils import impl_root
from shared_utils.stage_runtime_resolver import load_positive_numeric_map_from_env, resolve_run_config_path
from shared_utils.stage_utils import ensure_paths_exist

from retrieval.candidate_evaluator import RetrievalEvaluator
from retrieval.candidate_parser import normalize_candidate_row
from retrieval.models import NumericFeatureSpec, RetrievalContext, RetrievalControls, RetrievalInputs, RetrievalPaths
from retrieval.profile_builder import build_active_numeric_specs, build_profile_label_set, build_profile_weight_map


DECISION_FIELDS = [
    "track_id",
    "is_seed_track",
    "lead_genre",
    "semantic_score",
    "lead_genre_similarity",
    "genre_overlap_score",
    "tag_overlap_score",
    "lead_genre_match",
    "genre_overlap_count",
    "tag_overlap_count",
    "language",
    "language_match",
    "release_year",
    "release_year_distance",
    "numeric_pass_count",
    "numeric_support_score",
    "danceability_distance",
    "danceability_similarity",
    "energy_distance",
    "energy_similarity",
    "valence_distance",
    "valence_similarity",
    "tempo_distance",
    "tempo_similarity",
    "popularity_distance",
    "popularity_similarity",
    "duration_ms_distance",
    "duration_ms_similarity",
    "key_distance",
    "key_similarity",
    "mode_distance",
    "mode_similarity",
    "decision",
    "decision_path",
    "decision_reason",
]


class RetrievalStage:
    """Object-oriented BL-005 workflow shell over the existing retrieval logic."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    @staticmethod
    def _parse_optional_positive_int(raw: object) -> int | None:
        text = str(raw).strip()
        if not text:
            return None
        try:
            parsed = int(text)
        except ValueError:
            return None
        return parsed if parsed > 0 else None

    @staticmethod
    def _normalize_language_codes(raw_values: object) -> list[str]:
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

    def _sanitize_controls(self, payload: dict[str, object]) -> RetrievalControls:
        profile_top_lead_genre_limit = max(1, int(str(payload["profile_top_lead_genre_limit"])))
        profile_top_tag_limit = max(1, int(str(payload["profile_top_tag_limit"])))
        profile_top_genre_limit = max(1, int(str(payload["profile_top_genre_limit"])))
        semantic_strong_keep_score = max(0, min(3, int(str(payload["semantic_strong_keep_score"]))))
        semantic_min_keep_score = max(0, min(3, int(str(payload["semantic_min_keep_score"]))))
        numeric_support_min_pass = max(0, int(str(payload["numeric_support_min_pass"])))
        numeric_support_min_score = max(
            0.0,
            float(str(payload.get("numeric_support_min_score", numeric_support_min_pass))),
        )
        lead_genre_partial_match_threshold = max(
            0.0,
            min(
                1.0,
                float(str(payload.get("lead_genre_partial_match_threshold", DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD))),
            ),
        )
        use_weighted_semantics = bool(payload.get("use_weighted_semantics", False))
        use_continuous_numeric = bool(payload.get("use_continuous_numeric", False))
        enable_popularity_numeric = bool(payload.get("enable_popularity_numeric", False))

        language_filter_codes = self._normalize_language_codes(payload.get("language_filter_codes", []))
        language_filter_enabled = bool(payload.get("language_filter_enabled", False)) and bool(language_filter_codes)
        recency_years_min_offset = self._parse_optional_positive_int(payload.get("recency_years_min_offset", ""))
        if semantic_min_keep_score > semantic_strong_keep_score:
            semantic_min_keep_score = semantic_strong_keep_score

        numeric_thresholds_raw = payload.get("numeric_thresholds")
        numeric_thresholds: dict[str, float] = {}
        if isinstance(numeric_thresholds_raw, dict):
            for key, value in numeric_thresholds_raw.items():
                numeric_thresholds[str(key)] = float(str(value))

        run_config_path_raw = payload.get("run_config_path")
        run_config_schema_version_raw = payload.get("run_config_schema_version")
        return RetrievalControls(
            config_source=str(payload.get("config_source") or "environment"),
            run_config_path=(
                str(run_config_path_raw) if run_config_path_raw else None
            ),
            run_config_schema_version=(
                str(run_config_schema_version_raw) if run_config_schema_version_raw else None
            ),
            signal_mode={str(k): v for k, v in dict(payload.get("signal_mode") or {}).items()},
            profile_top_lead_genre_limit=profile_top_lead_genre_limit,
            profile_top_tag_limit=profile_top_tag_limit,
            profile_top_genre_limit=profile_top_genre_limit,
            semantic_strong_keep_score=semantic_strong_keep_score,
            semantic_min_keep_score=semantic_min_keep_score,
            numeric_support_min_pass=numeric_support_min_pass,
            numeric_support_min_score=numeric_support_min_score,
            lead_genre_partial_match_threshold=lead_genre_partial_match_threshold,
            use_weighted_semantics=use_weighted_semantics,
            use_continuous_numeric=use_continuous_numeric,
            enable_popularity_numeric=enable_popularity_numeric,
            language_filter_enabled=language_filter_enabled,
            language_filter_codes=language_filter_codes,
            recency_years_min_offset=recency_years_min_offset,
            numeric_thresholds=numeric_thresholds,
        )

    def resolve_paths(self) -> RetrievalPaths:
        return RetrievalPaths(
            profile_path=self.root / "profile" / "outputs" / "bl004_preference_profile.json",
            seed_trace_path=self.root / "profile" / "outputs" / "bl004_seed_trace.csv",
            candidate_path=self.root / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv",
            output_dir=self.root / "retrieval" / "outputs",
        )

    def resolve_runtime_controls(self) -> RetrievalControls:
        env_numeric_thresholds = load_positive_numeric_map_from_env("BL005_NUMERIC_THRESHOLDS_JSON")
        env_language_filter_enabled = env_bool("BL005_LANGUAGE_FILTER_ENABLED", DEFAULT_LANGUAGE_FILTER_ENABLED)
        env_language_filter_codes_raw = env_str("BL005_LANGUAGE_FILTER_CODES", "")
        env_recency_years_min_offset_raw = env_str("BL005_RECENCY_YEARS_MIN_OFFSET", "")
        env_lead_genre_partial_match_threshold = env_float(
            "BL005_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD",
            DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
        )
        env_numeric_support_min_score = env_float(
            "BL005_NUMERIC_SUPPORT_MIN_SCORE",
            DEFAULT_NUMERIC_SUPPORT_MIN_SCORE,
        )
        env_use_weighted_semantics = env_bool(
            "BL005_USE_WEIGHTED_SEMANTICS",
            DEFAULT_RETRIEVAL_USE_WEIGHTED_SEMANTICS,
        )
        env_use_continuous_numeric = env_bool(
            "BL005_USE_CONTINUOUS_NUMERIC",
            DEFAULT_RETRIEVAL_USE_CONTINUOUS_NUMERIC,
        )
        env_enable_popularity_numeric = env_bool(
            "BL005_ENABLE_POPULARITY_NUMERIC",
            DEFAULT_RETRIEVAL_ENABLE_POPULARITY_NUMERIC,
        )

        env_language_filter_codes = [
            token.strip().lower()
            for token in env_language_filter_codes_raw.split(",")
            if token.strip()
        ]
        env_recency_years_min_offset = self._parse_optional_positive_int(env_recency_years_min_offset_raw)

        run_config_path = resolve_run_config_path()
        if run_config_path:
            run_config_utils = load_run_config_utils_module()
            controls = run_config_utils.resolve_bl005_controls(run_config_path)
            return self._sanitize_controls(
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
                    "numeric_support_min_score": controls.get(
                        "numeric_support_min_score",
                        DEFAULT_NUMERIC_SUPPORT_MIN_SCORE,
                    ),
                    "lead_genre_partial_match_threshold": controls.get(
                        "lead_genre_partial_match_threshold",
                        DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
                    ),
                    "use_weighted_semantics": bool(controls.get("use_weighted_semantics", False)),
                    "use_continuous_numeric": bool(controls.get("use_continuous_numeric", False)),
                    "enable_popularity_numeric": bool(controls.get("enable_popularity_numeric", False)),
                    "language_filter_enabled": bool(
                        controls.get("language_filter_enabled", DEFAULT_LANGUAGE_FILTER_ENABLED)
                    ),
                    "language_filter_codes": list(
                        controls.get("language_filter_codes") or DEFAULT_LANGUAGE_FILTER_CODES
                    ),
                    "recency_years_min_offset": controls.get(
                        "recency_years_min_offset",
                        DEFAULT_RECENCY_YEARS_MIN_OFFSET,
                    ),
                    "numeric_thresholds": env_numeric_thresholds or controls.get("numeric_thresholds") or {},
                }
            )

        return self._sanitize_controls(
            {
                "config_source": "environment",
                "run_config_path": None,
                "run_config_schema_version": None,
                "profile_top_lead_genre_limit": env_int(
                    "BL005_PROFILE_TOP_LEAD_GENRE_LIMIT",
                    DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
                ),
                "profile_top_tag_limit": env_int("BL005_PROFILE_TOP_TAG_LIMIT", DEFAULT_PROFILE_TOP_TAG_LIMIT),
                "profile_top_genre_limit": env_int(
                    "BL005_PROFILE_TOP_GENRE_LIMIT",
                    DEFAULT_PROFILE_TOP_GENRE_LIMIT,
                ),
                "semantic_strong_keep_score": env_int(
                    "BL005_SEMANTIC_STRONG_KEEP_SCORE",
                    DEFAULT_SEMANTIC_STRONG_KEEP_SCORE,
                ),
                "semantic_min_keep_score": env_int(
                    "BL005_SEMANTIC_MIN_KEEP_SCORE",
                    DEFAULT_SEMANTIC_MIN_KEEP_SCORE,
                ),
                "numeric_support_min_pass": env_int(
                    "BL005_NUMERIC_SUPPORT_MIN_PASS",
                    DEFAULT_NUMERIC_SUPPORT_MIN_PASS,
                ),
                "numeric_support_min_score": env_numeric_support_min_score,
                "lead_genre_partial_match_threshold": env_lead_genre_partial_match_threshold,
                "use_weighted_semantics": env_use_weighted_semantics,
                "use_continuous_numeric": env_use_continuous_numeric,
                "enable_popularity_numeric": env_enable_popularity_numeric,
                "language_filter_enabled": env_language_filter_enabled,
                "language_filter_codes": env_language_filter_codes,
                "recency_years_min_offset": env_recency_years_min_offset,
                "numeric_thresholds": env_numeric_thresholds,
            }
        )

    @staticmethod
    def load_inputs(paths: RetrievalPaths) -> RetrievalInputs:
        profile = load_json(paths.profile_path)
        if not isinstance(profile, dict):
            raise RuntimeError("BL-005 profile artifact is malformed; expected JSON object")
        candidate_rows_raw = load_csv_rows(paths.candidate_path)
        if not candidate_rows_raw:
            raise RuntimeError("BL-005 candidate corpus is empty; cannot build retrieval outputs")
        candidate_rows = [normalize_candidate_row(row) for row in candidate_rows_raw]
        seed_trace_rows = load_csv_rows(paths.seed_trace_path)
        return RetrievalInputs(
            profile=profile,
            candidate_rows=candidate_rows,
            seed_trace_rows=seed_trace_rows,
        )

    @staticmethod
    def build_runtime_context(
        *,
        inputs: RetrievalInputs,
        controls: RetrievalControls,
    ) -> RetrievalContext:
        effective_numeric_specs = {
            key: NumericFeatureSpec(
                candidate_column=str(spec["candidate_column"]),
                threshold=float(
                    controls.numeric_thresholds.get(
                        key,
                        float(str(spec["threshold"])) if spec["threshold"] is not None else 0.0,
                    )
                ),
                circular=bool(spec["circular"]),
            )
            for key, spec in NUMERIC_FEATURE_SPECS.items()
            if controls.enable_popularity_numeric or key != "popularity"
        }

        seed_track_ids = {str(row["track_id"]) for row in inputs.seed_trace_rows}
        candidate_columns = set(inputs.candidate_rows[0].keys()) if inputs.candidate_rows else set()

        top_lead_genres = build_profile_label_set(
            inputs.profile,
            "top_lead_genres",
            controls.profile_top_lead_genre_limit,
        )
        lead_genre_weights = build_profile_weight_map(
            inputs.profile,
            "top_lead_genres",
            controls.profile_top_lead_genre_limit,
        )
        top_tags = build_profile_label_set(
            inputs.profile,
            "top_tags",
            controls.profile_top_tag_limit,
        )
        tag_weights = build_profile_weight_map(
            inputs.profile,
            "top_tags",
            controls.profile_top_tag_limit,
        )
        top_genres = build_profile_label_set(
            inputs.profile,
            "top_genres",
            controls.profile_top_genre_limit,
        )
        genre_weights = build_profile_weight_map(
            inputs.profile,
            "top_genres",
            controls.profile_top_genre_limit,
        )
        active_numeric_specs = build_active_numeric_specs(
            inputs.profile,
            effective_numeric_specs,
            candidate_columns,
        )

        numeric_feature_profile_obj = inputs.profile.get("numeric_feature_profile")
        numeric_feature_profile: dict[str, Any] = (
            numeric_feature_profile_obj if isinstance(numeric_feature_profile_obj, dict) else {}
        )
        numeric_centers = {
            profile_column: float(str(numeric_feature_profile[profile_column]))
            for profile_column in active_numeric_specs
            if profile_column in numeric_feature_profile
            and numeric_feature_profile[profile_column] is not None
        }
        numeric_features_enabled = bool(numeric_centers)
        language_filter_codes = sorted({code for code in controls.language_filter_codes if code})
        current_year_utc = datetime.now(timezone.utc).year
        recency_min_release_year = (
            current_year_utc - controls.recency_years_min_offset
            if controls.recency_years_min_offset is not None
            else None
        )

        return RetrievalContext(
            signal_mode=dict(controls.signal_mode),
            profile_top_lead_genre_limit=controls.profile_top_lead_genre_limit,
            profile_top_tag_limit=controls.profile_top_tag_limit,
            profile_top_genre_limit=controls.profile_top_genre_limit,
            semantic_strong_keep_score=controls.semantic_strong_keep_score,
            semantic_min_keep_score=controls.semantic_min_keep_score,
            numeric_support_min_pass=controls.numeric_support_min_pass,
            numeric_support_min_score=controls.numeric_support_min_score,
            lead_genre_partial_match_threshold=controls.lead_genre_partial_match_threshold,
            active_numeric_specs=active_numeric_specs,
            seed_track_ids=seed_track_ids,
            top_lead_genres=top_lead_genres,
            top_tags=top_tags,
            top_genres=top_genres,
            lead_genre_weights=lead_genre_weights,
            tag_weights=tag_weights,
            genre_weights=genre_weights,
            numeric_centers=numeric_centers,
            numeric_features_enabled=numeric_features_enabled,
            use_weighted_semantics=controls.use_weighted_semantics,
            use_continuous_numeric=controls.use_continuous_numeric,
            language_filter_enabled=controls.language_filter_enabled,
            language_filter_codes=language_filter_codes,
            recency_years_min_offset=controls.recency_years_min_offset,
            current_year_utc=current_year_utc,
            recency_min_release_year=recency_min_release_year,
        )

    @staticmethod
    def write_output_artifacts(
        *,
        output_dir: Path,
        candidate_rows: list[dict[str, str]],
        decisions: list[dict[str, object]],
        kept_rows: list[dict[str, str]],
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

    @staticmethod
    def build_diagnostics_payload(
        *,
        run_id: str,
        elapsed_seconds: float,
        paths: RetrievalPaths,
        runtime_context: RetrievalContext,
        summary: dict[str, object],
        candidate_rows: list[dict[str, str]],
        kept_rows: list[dict[str, str]],
        output_paths: dict[str, Path],
    ) -> dict[str, object]:
        decision_counts_obj = summary.get("decision_counts")
        decision_counts = decision_counts_obj if isinstance(decision_counts_obj, dict) else {}
        decision_path_counts_obj = summary.get("decision_path_counts")
        decision_path_counts = decision_path_counts_obj if isinstance(decision_path_counts_obj, dict) else {}

        return {
            "run_id": run_id,
            "task": "BL-005",
            "generated_at_utc": utc_now(),
            "input_artifacts": {
                "profile_path": str(paths.profile_path),
                "profile_sha256": sha256_of_file(paths.profile_path),
                "seed_trace_path": str(paths.seed_trace_path),
                "seed_trace_sha256": sha256_of_file(paths.seed_trace_path),
                "candidate_stub_path": str(paths.candidate_path),
                "candidate_stub_sha256": sha256_of_file(paths.candidate_path),
            },
            "config": {
                "top_lead_genre_limit": runtime_context.profile_top_lead_genre_limit,
                "top_tag_limit": runtime_context.profile_top_tag_limit,
                "top_genre_limit": runtime_context.profile_top_genre_limit,
                "signal_mode": dict(runtime_context.signal_mode),
                "numeric_thresholds": {
                    profile_column: spec.threshold
                    for profile_column, spec in runtime_context.active_numeric_specs.items()
                },
                "numeric_support_min_score": runtime_context.numeric_support_min_score,
                "use_weighted_semantics": runtime_context.use_weighted_semantics,
                "use_continuous_numeric": runtime_context.use_continuous_numeric,
                "language_filter": {
                    "enabled": runtime_context.language_filter_enabled,
                    "codes": list(runtime_context.language_filter_codes),
                },
                "recency_gate": {
                    "years_min_offset": runtime_context.recency_years_min_offset,
                    "current_year_utc": runtime_context.current_year_utc,
                    "min_release_year": runtime_context.recency_min_release_year,
                },
                "numeric_feature_mapping": {
                    profile_column: spec.candidate_column
                    for profile_column, spec in runtime_context.active_numeric_specs.items()
                },
                "numeric_features_enabled": runtime_context.numeric_features_enabled,
                "keep_rule": (
                    f"keep if not seed and (semantic_score >= {runtime_context.semantic_strong_keep_score} or "
                    f"(semantic_score >= {runtime_context.semantic_min_keep_score} and "
                    f"{'numeric_support_score' if runtime_context.use_continuous_numeric else 'numeric_pass_count'} >= "
                    f"{runtime_context.numeric_support_min_score if runtime_context.use_continuous_numeric else runtime_context.numeric_support_min_pass}))"
                    if runtime_context.numeric_features_enabled
                    else f"keep if not seed and semantic_score >= {runtime_context.semantic_min_keep_score}"
                ),
                "semantic_source": "ds001_tags_and_genres_columns",
            },
            "counts": {
                "candidate_rows_total": len(candidate_rows),
                "seed_tracks_excluded": int(decision_counts.get("seed_excluded", 0)),
                "kept_candidates": len(kept_rows),
                "rejected_non_seed_candidates": int(decision_counts.get("rejected_threshold", 0)),
                "rejected_by_language_filter": int(decision_path_counts.get("reject_language_filter", 0)),
                "rejected_by_recency_gate": int(decision_path_counts.get("reject_recency_gate", 0)),
            },
            "rule_hits": {
                "semantic_rule_hits": summary["semantic_rule_hits"],
                "numeric_rule_hits": summary["numeric_rule_hits"],
            },
            "decision_path_counts": summary["decision_path_counts"],
            "score_distributions": {
                "semantic_score": summary["semantic_score_distribution"],
                "numeric_pass_count": summary["numeric_pass_distribution"],
                "numeric_support_score": summary.get("numeric_support_score_distribution", {}),
            },
            "top_kept_track_ids": [str(row["track_id"]) for row in kept_rows[:15]],
            "elapsed_seconds": round(elapsed_seconds, 3),
            "output_files": {
                "filtered_candidates_path": str(output_paths["filtered_path"]),
                "candidate_decisions_path": str(output_paths["decisions_path"]),
            },
        }

    @staticmethod
    def write_diagnostics_with_hashes(
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
        diagnostics["diagnostics_hash_note"] = (
            "diagnostics file does not store its own hash to avoid recursive self-reference"
        )
        with open_text_write(diagnostics_path) as handle:
            json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    def run(self) -> None:
        paths = self.resolve_paths()
        paths.output_dir.mkdir(parents=True, exist_ok=True)
        ensure_paths_exist(
            [paths.profile_path, paths.seed_trace_path, paths.candidate_path],
            stage_label="BL-005",
        )

        controls = self.resolve_runtime_controls()
        inputs = self.load_inputs(paths)
        context = self.build_runtime_context(inputs=inputs, controls=controls)

        start_time = time.time()
        run_id = f"BL005-FILTER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        evaluation = RetrievalEvaluator(context).evaluate(inputs.candidate_rows)

        output_paths = self.write_output_artifacts(
            output_dir=paths.output_dir,
            candidate_rows=inputs.candidate_rows,
            decisions=evaluation.decisions,
            kept_rows=evaluation.kept_rows,
        )

        diagnostics = self.build_diagnostics_payload(
            run_id=run_id,
            elapsed_seconds=time.time() - start_time,
            paths=paths,
            runtime_context=context,
            summary=evaluation.summary,
            candidate_rows=inputs.candidate_rows,
            kept_rows=evaluation.kept_rows,
            output_paths=output_paths,
        )

        diagnostics_path = paths.output_dir / "bl005_candidate_diagnostics.json"
        self.write_diagnostics_with_hashes(
            diagnostics=diagnostics,
            diagnostics_path=diagnostics_path,
            output_paths=output_paths,
        )

        print("BL-005 candidate filtering complete.")
        print(f"filtered_candidates={output_paths['filtered_path']}")
        print(f"decisions={output_paths['decisions_path']}")
        print(f"diagnostics={diagnostics_path}")
