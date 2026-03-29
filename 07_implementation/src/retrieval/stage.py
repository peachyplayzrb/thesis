from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared_utils.constants import (
    NUMERIC_FEATURE_SPECS,
)
from shared_utils.io_utils import load_csv_rows, load_json, open_text_write, sha256_of_file, utc_now
from shared_utils.path_utils import impl_root
from shared_utils.stage_utils import ensure_paths_exist

from retrieval.candidate_evaluator import RetrievalEvaluator
from retrieval.candidate_parser import normalize_candidate_row
from retrieval.models import NumericFeatureSpec, RetrievalContext, RetrievalControls, RetrievalInputs, RetrievalPaths
from retrieval.models import RetrievalArtifacts
from retrieval.profile_builder import build_active_numeric_specs, build_profile_label_set, build_profile_weight_map
from retrieval.runtime_controls import resolve_bl005_runtime_controls


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
    "numeric_support_score_weighted",
    "numeric_support_score_weighted_absolute",
    "numeric_support_score_selected",
    "numeric_support_score_mode",
    "numeric_confidence_weight_sum",
    "profile_numeric_confidence_factor",
    "effective_semantic_strong_keep_score",
    "effective_semantic_min_keep_score",
    "effective_numeric_support_min_pass",
    "effective_numeric_support_min_score",
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
    def _clamp_0_1(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _safe_float(raw: object, fallback: float = 0.0) -> float:
        try:
            return float(str(raw))
        except (TypeError, ValueError):
            return fallback

    def resolve_paths(self) -> RetrievalPaths:
        return RetrievalPaths(
            profile_path=self.root / "profile" / "outputs" / "bl004_preference_profile.json",
            seed_trace_path=self.root / "profile" / "outputs" / "bl004_seed_trace.csv",
            candidate_path=self.root / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv",
            output_dir=self.root / "retrieval" / "outputs",
        )

    def resolve_runtime_controls(self) -> RetrievalControls:
        payload = resolve_bl005_runtime_controls()
        return RetrievalControls(
            config_source=str(payload.get("config_source") or "environment"),
            run_config_path=(str(payload["run_config_path"]) if payload.get("run_config_path") else None),
            run_config_schema_version=(
                str(payload["run_config_schema_version"])
                if payload.get("run_config_schema_version")
                else None
            ),
            signal_mode={str(k): v for k, v in dict(payload.get("signal_mode") or {}).items()},
            profile_top_lead_genre_limit=int(payload.get("profile_top_lead_genre_limit", 6)),
            profile_top_tag_limit=int(payload.get("profile_top_tag_limit", 10)),
            profile_top_genre_limit=int(payload.get("profile_top_genre_limit", 8)),
            semantic_strong_keep_score=int(payload.get("semantic_strong_keep_score", 2)),
            semantic_min_keep_score=int(payload.get("semantic_min_keep_score", 1)),
            numeric_support_min_pass=int(payload.get("numeric_support_min_pass", 1)),
            numeric_support_min_score=float(payload.get("numeric_support_min_score", 1.0)),
            lead_genre_partial_match_threshold=float(payload.get("lead_genre_partial_match_threshold", 0.5)),
            use_weighted_semantics=bool(payload.get("use_weighted_semantics", False)),
            use_continuous_numeric=bool(payload.get("use_continuous_numeric", False)),
            enable_popularity_numeric=bool(payload.get("enable_popularity_numeric", False)),
            language_filter_enabled=bool(payload.get("language_filter_enabled", False)),
            language_filter_codes=[str(v) for v in list(payload.get("language_filter_codes") or []) if str(v)],
            recency_years_min_offset=(
                int(payload["recency_years_min_offset"])
                if payload.get("recency_years_min_offset") is not None
                else None
            ),
            numeric_thresholds={
                str(k): float(v)
                for k, v in dict(payload.get("numeric_thresholds") or {}).items()
            },
            profile_quality_penalty_enabled=bool(payload.get("profile_quality_penalty_enabled", True)),
            profile_quality_threshold=float(payload.get("profile_quality_threshold", 0.90)),
            profile_entropy_low_threshold=float(payload.get("profile_entropy_low_threshold", 0.35)),
            influence_share_threshold=float(payload.get("influence_share_threshold", 0.60)),
            profile_quality_penalty_increment=float(payload.get("profile_quality_penalty_increment", 0.20)),
            profile_entropy_penalty_increment=float(payload.get("profile_entropy_penalty_increment", 0.20)),
            influence_share_penalty_increment=float(payload.get("influence_share_penalty_increment", 0.15)),
            numeric_penalty_scale=float(payload.get("numeric_penalty_scale", 0.50)),
            semantic_overlap_damping_mid_entropy_threshold=float(
                payload.get("semantic_overlap_damping_mid_entropy_threshold", 0.60)
            ),
            semantic_overlap_damping_low_entropy=float(payload.get("semantic_overlap_damping_low_entropy", 0.85)),
            semantic_overlap_damping_mid_entropy=float(payload.get("semantic_overlap_damping_mid_entropy", 0.92)),
            enable_numeric_confidence_scaling=bool(payload.get("enable_numeric_confidence_scaling", True)),
            numeric_confidence_floor=float(payload.get("numeric_confidence_floor", 0.0)),
            profile_numeric_confidence_mode=str(payload.get("profile_numeric_confidence_mode") or "direct"),
            profile_numeric_confidence_blend_weight=float(
                payload.get("profile_numeric_confidence_blend_weight", 1.0)
            ),
            numeric_support_score_mode=str(payload.get("numeric_support_score_mode") or "weighted_absolute"),
            emit_profile_policy_diagnostics=bool(payload.get("emit_profile_policy_diagnostics", True)),
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

        numeric_confidence_obj = inputs.profile.get("numeric_confidence")
        numeric_confidence = (
            numeric_confidence_obj if isinstance(numeric_confidence_obj, dict) else {}
        )
        confidence_by_feature_obj = numeric_confidence.get("confidence_by_feature")
        confidence_by_feature = (
            confidence_by_feature_obj if isinstance(confidence_by_feature_obj, dict) else {}
        )
        feature_confidence_by_name = {
            feature: RetrievalStage._clamp_0_1(
                RetrievalStage._safe_float(confidence_by_feature.get(feature), 1.0)
            )
            for feature in active_numeric_specs
        }
        profile_numeric_confidence_factor_base = 1.0
        if feature_confidence_by_name:
            profile_numeric_confidence_factor_base = sum(feature_confidence_by_name.values()) / float(
                len(feature_confidence_by_name)
            )

        if controls.enable_numeric_confidence_scaling:
            numeric_confidence_floor = RetrievalStage._clamp_0_1(controls.numeric_confidence_floor)
            feature_confidence_by_name = {
                key: max(numeric_confidence_floor, value)
                for key, value in feature_confidence_by_name.items()
            }
        else:
            numeric_confidence_floor = 0.0
            feature_confidence_by_name = {
                key: 1.0
                for key in feature_confidence_by_name
            }

        if controls.profile_numeric_confidence_mode == "blended":
            blend_weight = RetrievalStage._clamp_0_1(controls.profile_numeric_confidence_blend_weight)
            profile_numeric_confidence_factor = (
                blend_weight * profile_numeric_confidence_factor_base
            ) + ((1.0 - blend_weight) * 1.0)
        elif controls.enable_numeric_confidence_scaling:
            profile_numeric_confidence_factor = profile_numeric_confidence_factor_base
        else:
            profile_numeric_confidence_factor = 1.0

        signal_vector_obj = inputs.profile.get("profile_signal_vector")
        signal_vector = signal_vector_obj if isinstance(signal_vector_obj, dict) else {}
        bl003_quality_obj = inputs.profile.get("bl003_quality")
        bl003_quality = bl003_quality_obj if isinstance(bl003_quality_obj, dict) else {}

        profile_match_quality = RetrievalStage._clamp_0_1(
            RetrievalStage._safe_float(
                signal_vector.get(
                    "alignment_match_rate",
                    bl003_quality.get("match_rate", 1.0),
                ),
                1.0,
            )
        )
        top_genre_entropy = RetrievalStage._clamp_0_1(
            RetrievalStage._safe_float(signal_vector.get("top_genre_entropy"), 0.0)
        )
        top_tag_entropy = RetrievalStage._clamp_0_1(
            RetrievalStage._safe_float(signal_vector.get("top_tag_entropy"), 0.0)
        )
        history_weight_share = RetrievalStage._clamp_0_1(
            RetrievalStage._safe_float(signal_vector.get("history_weight_share"), 1.0)
        )
        influence_weight_share = RetrievalStage._clamp_0_1(
            RetrievalStage._safe_float(signal_vector.get("influence_weight_share"), 0.0)
        )

        average_entropy = (top_genre_entropy + top_tag_entropy) / 2.0
        threshold_penalty = 0.0
        if controls.profile_quality_penalty_enabled:
            if profile_match_quality < controls.profile_quality_threshold:
                threshold_penalty += controls.profile_quality_penalty_increment
            if average_entropy < controls.profile_entropy_low_threshold:
                threshold_penalty += controls.profile_entropy_penalty_increment
            if influence_weight_share > controls.influence_share_threshold:
                threshold_penalty += controls.influence_share_penalty_increment

        effective_semantic_min_keep_score = min(
            3.0,
            float(controls.semantic_min_keep_score) + threshold_penalty,
        )
        effective_semantic_strong_keep_score = min(
            3.0,
            max(
                effective_semantic_min_keep_score,
                float(controls.semantic_strong_keep_score) + threshold_penalty,
            ),
        )
        effective_numeric_support_min_pass = max(
            0,
            int(round(float(controls.numeric_support_min_pass) * (1.0 + (threshold_penalty * controls.numeric_penalty_scale)))),
        )
        effective_numeric_support_min_score = max(
            0.0,
            float(controls.numeric_support_min_score) * (1.0 + (threshold_penalty * controls.numeric_penalty_scale)),
        )

        semantic_overlap_damping = 1.0
        if average_entropy < controls.profile_entropy_low_threshold:
            semantic_overlap_damping = controls.semantic_overlap_damping_low_entropy
        elif average_entropy < controls.semantic_overlap_damping_mid_entropy_threshold:
            semantic_overlap_damping = controls.semantic_overlap_damping_mid_entropy

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
            feature_confidence_by_name=feature_confidence_by_name,
            profile_numeric_confidence_factor=profile_numeric_confidence_factor,
            profile_match_quality=profile_match_quality,
            top_genre_entropy=top_genre_entropy,
            top_tag_entropy=top_tag_entropy,
            history_weight_share=history_weight_share,
            influence_weight_share=influence_weight_share,
            effective_semantic_strong_keep_score=effective_semantic_strong_keep_score,
            effective_semantic_min_keep_score=effective_semantic_min_keep_score,
            effective_numeric_support_min_pass=effective_numeric_support_min_pass,
            effective_numeric_support_min_score=effective_numeric_support_min_score,
            semantic_overlap_damping=semantic_overlap_damping,
            profile_quality_penalty_enabled=controls.profile_quality_penalty_enabled,
            profile_quality_threshold=controls.profile_quality_threshold,
            profile_entropy_low_threshold=controls.profile_entropy_low_threshold,
            influence_share_threshold=controls.influence_share_threshold,
            profile_quality_penalty_increment=controls.profile_quality_penalty_increment,
            profile_entropy_penalty_increment=controls.profile_entropy_penalty_increment,
            influence_share_penalty_increment=controls.influence_share_penalty_increment,
            numeric_penalty_scale=controls.numeric_penalty_scale,
            semantic_overlap_damping_mid_entropy_threshold=controls.semantic_overlap_damping_mid_entropy_threshold,
            semantic_overlap_damping_low_entropy=controls.semantic_overlap_damping_low_entropy,
            semantic_overlap_damping_mid_entropy=controls.semantic_overlap_damping_mid_entropy,
            enable_numeric_confidence_scaling=controls.enable_numeric_confidence_scaling,
            numeric_confidence_floor=numeric_confidence_floor,
            profile_numeric_confidence_mode=controls.profile_numeric_confidence_mode,
            profile_numeric_confidence_blend_weight=controls.profile_numeric_confidence_blend_weight,
            numeric_support_score_mode=controls.numeric_support_score_mode,
            effective_threshold_penalty=threshold_penalty,
            emit_profile_policy_diagnostics=controls.emit_profile_policy_diagnostics,
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
                "effective_thresholds": {
                    "semantic_strong_keep_score": round(
                        runtime_context.effective_semantic_strong_keep_score,
                        6,
                    ),
                    "semantic_min_keep_score": round(
                        runtime_context.effective_semantic_min_keep_score,
                        6,
                    ),
                    "numeric_support_min_pass": runtime_context.effective_numeric_support_min_pass,
                    "numeric_support_min_score": round(
                        runtime_context.effective_numeric_support_min_score,
                        6,
                    ),
                    "semantic_overlap_damping": round(runtime_context.semantic_overlap_damping, 6),
                },
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
                    f"keep if not seed and (semantic_score >= {runtime_context.effective_semantic_strong_keep_score:.3f} or "
                    f"(semantic_score >= {runtime_context.effective_semantic_min_keep_score:.3f} and "
                    f"{'numeric_support_score' if runtime_context.use_continuous_numeric else 'numeric_pass_count'} >= "
                    f"{runtime_context.effective_numeric_support_min_score if runtime_context.use_continuous_numeric else runtime_context.effective_numeric_support_min_pass}))"
                    if runtime_context.numeric_features_enabled
                    else f"keep if not seed and semantic_score >= {runtime_context.effective_semantic_min_keep_score:.3f}"
                ),
                "semantic_source": "ds001_tags_and_genres_columns",
                "profile_quality_inputs": {
                    "profile_match_quality": round(runtime_context.profile_match_quality, 6),
                    "top_genre_entropy": round(runtime_context.top_genre_entropy, 6),
                    "top_tag_entropy": round(runtime_context.top_tag_entropy, 6),
                    "history_weight_share": round(runtime_context.history_weight_share, 6),
                    "influence_weight_share": round(runtime_context.influence_weight_share, 6),
                    "profile_numeric_confidence_factor": round(
                        runtime_context.profile_numeric_confidence_factor,
                        6,
                    ),
                    "feature_confidence_by_name": dict(runtime_context.feature_confidence_by_name),
                    "profile_quality_penalty_enabled": runtime_context.profile_quality_penalty_enabled,
                    "profile_quality_threshold": round(runtime_context.profile_quality_threshold, 6),
                    "profile_entropy_low_threshold": round(runtime_context.profile_entropy_low_threshold, 6),
                    "influence_share_threshold": round(runtime_context.influence_share_threshold, 6),
                    "profile_quality_penalty_increment": round(runtime_context.profile_quality_penalty_increment, 6),
                    "profile_entropy_penalty_increment": round(runtime_context.profile_entropy_penalty_increment, 6),
                    "influence_share_penalty_increment": round(runtime_context.influence_share_penalty_increment, 6),
                    "numeric_penalty_scale": round(runtime_context.numeric_penalty_scale, 6),
                    "numeric_confidence_scaling_enabled": runtime_context.enable_numeric_confidence_scaling,
                    "numeric_confidence_floor": round(runtime_context.numeric_confidence_floor, 6),
                    "profile_numeric_confidence_mode": runtime_context.profile_numeric_confidence_mode,
                    "profile_numeric_confidence_blend_weight": round(
                        runtime_context.profile_numeric_confidence_blend_weight,
                        6,
                    ),
                    "numeric_support_score_mode": runtime_context.numeric_support_score_mode,
                    "effective_threshold_penalty": round(runtime_context.effective_threshold_penalty, 6),
                },
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
                "numeric_support_score_weighted": summary.get("numeric_support_score_weighted_distribution", {}),
                "numeric_support_score_weighted_absolute": summary.get(
                    "numeric_support_score_weighted_absolute_distribution",
                    {},
                ),
                "numeric_support_score_selected": summary.get("numeric_support_score_selected_distribution", {}),
                "effective_semantic_min_keep_score": summary.get("effective_semantic_min_distribution", {}),
                "effective_numeric_support_min_score": summary.get("effective_numeric_support_min_score_distribution", {}),
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

    def run(self) -> RetrievalArtifacts:
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

        elapsed_seconds = time.time() - start_time
        diagnostics = self.build_diagnostics_payload(
            run_id=run_id,
            elapsed_seconds=elapsed_seconds,
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

        decision_counts = evaluation.summary.get("decision_counts")
        decision_counts_map = decision_counts if isinstance(decision_counts, dict) else {}
        return RetrievalArtifacts(
            filtered_path=output_paths["filtered_path"],
            decisions_path=output_paths["decisions_path"],
            diagnostics_path=diagnostics_path,
            kept_candidates_count=len(evaluation.kept_rows),
            rejected_candidates_count=int(decision_counts_map.get("rejected_threshold", 0)),
            seed_excluded_count=int(decision_counts_map.get("seed_excluded", 0)),
            elapsed_seconds=round(elapsed_seconds, 3),
        )
