from __future__ import annotations

import csv
import json
import logging
import time
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from retrieval.candidate_evaluator import RetrievalEvaluator
from retrieval.filtering_logic import keep_decision
from retrieval.input_validation import validate_bl004_bl005_handshake
from retrieval.models import (
    NumericFeatureSpec,
    RetrievalArtifacts,
    RetrievalContext,
    RetrievalControls,
    RetrievalInputs,
    RetrievalPaths,
)
from retrieval.profile_builder import (
    build_active_numeric_specs,
    build_profile_label_set,
    build_profile_weight_map,
)
from retrieval.runtime_controls import resolve_bl005_runtime_controls
from shared_utils.coerce import clamp, to_float, to_int, to_mapping, to_string_list
from shared_utils.constants import (
    DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
    DEFAULT_NUMERIC_SUPPORT_MIN_PASS,
    DEFAULT_NUMERIC_SUPPORT_MIN_SCORE,
    DEFAULT_PROFILE_TOP_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_TAG_LIMIT,
    DEFAULT_RETRIEVAL_CONTROLS,
    DEFAULT_SEMANTIC_MIN_KEEP_SCORE,
    DEFAULT_SEMANTIC_STRONG_KEEP_SCORE,
    NUMERIC_FEATURE_SPECS,
)
from shared_utils.io_utils import load_csv_rows, load_json, open_text_write, sha256_of_file, utc_now
from shared_utils.parsing import normalize_candidate_row, safe_float, safe_int
from shared_utils.path_utils import impl_root
from shared_utils.stage_utils import ensure_paths_exist

logger = logging.getLogger(__name__)

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


def _build_effective_numeric_specs(controls: RetrievalControls) -> dict[str, NumericFeatureSpec]:
    return {
        key: NumericFeatureSpec(
            candidate_column=str(spec["candidate_column"]),
            threshold=safe_float(
                controls.numeric_thresholds.get(
                    key,
                    spec["threshold"],
                ),
                0.0,
            ),
            circular=bool(spec["circular"]),
        )
        for key, spec in NUMERIC_FEATURE_SPECS.items()
        if controls.enable_popularity_numeric or key != "popularity"
    }


def _build_profile_semantic_context(
    inputs: RetrievalInputs,
    controls: RetrievalControls,
) -> tuple[set[str], dict[str, float], set[str], dict[str, float], set[str], dict[str, float]]:
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
    return (
        top_lead_genres,
        lead_genre_weights,
        top_tags,
        tag_weights,
        top_genres,
        genre_weights,
    )


def _build_numeric_profile_context(
    inputs: RetrievalInputs,
    controls: RetrievalControls,
    effective_numeric_specs: dict[str, NumericFeatureSpec],
    candidate_columns: set[str],
) -> tuple[dict[str, NumericFeatureSpec], dict[str, float], bool, dict[str, float], float, float]:
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
        feature: clamp(to_float(confidence_by_feature.get(feature), 1.0))
        for feature in active_numeric_specs
    }
    profile_numeric_confidence_factor_base = 1.0
    if feature_confidence_by_name:
        profile_numeric_confidence_factor_base = sum(feature_confidence_by_name.values()) / float(
            len(feature_confidence_by_name)
        )

    if controls.enable_numeric_confidence_scaling:
        numeric_confidence_floor = clamp(controls.numeric_confidence_floor)
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
        blend_weight = clamp(controls.profile_numeric_confidence_blend_weight)
        profile_numeric_confidence_factor = (
            blend_weight * profile_numeric_confidence_factor_base
        ) + ((1.0 - blend_weight) * 1.0)
    elif controls.enable_numeric_confidence_scaling:
        profile_numeric_confidence_factor = profile_numeric_confidence_factor_base
    else:
        profile_numeric_confidence_factor = 1.0

    return (
        active_numeric_specs,
        numeric_centers,
        numeric_features_enabled,
        feature_confidence_by_name,
        profile_numeric_confidence_factor,
        numeric_confidence_floor,
    )


def _build_profile_signal_metrics(inputs: RetrievalInputs) -> tuple[float, float, float, float, float]:
    signal_vector_obj = inputs.profile.get("profile_signal_vector")
    signal_vector = signal_vector_obj if isinstance(signal_vector_obj, dict) else {}
    bl003_quality_obj = inputs.profile.get("bl003_quality")
    bl003_quality = bl003_quality_obj if isinstance(bl003_quality_obj, dict) else {}

    profile_match_quality = clamp(
        to_float(
            signal_vector.get(
                "alignment_match_rate",
                bl003_quality.get("match_rate", 1.0),
            ),
            1.0,
        )
    )
    top_genre_entropy = clamp(to_float(signal_vector.get("top_genre_entropy"), 0.0))
    top_tag_entropy = clamp(to_float(signal_vector.get("top_tag_entropy"), 0.0))
    history_weight_share = clamp(to_float(signal_vector.get("history_weight_share"), 1.0))
    influence_weight_share = clamp(to_float(signal_vector.get("influence_weight_share"), 0.0))
    return (
        profile_match_quality,
        top_genre_entropy,
        top_tag_entropy,
        history_weight_share,
        influence_weight_share,
    )


def _build_effective_threshold_context(
    controls: RetrievalControls,
    *,
    profile_match_quality: float,
    top_genre_entropy: float,
    top_tag_entropy: float,
    influence_weight_share: float,
) -> tuple[float, float, float, int, float, float]:
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

    return (
        threshold_penalty,
        effective_semantic_min_keep_score,
        effective_semantic_strong_keep_score,
        effective_numeric_support_min_pass,
        effective_numeric_support_min_score,
        semantic_overlap_damping,
    )


def _build_recency_context(controls: RetrievalControls) -> tuple[list[str], int, int | None]:
    language_filter_codes = sorted({code for code in controls.language_filter_codes if code})
    current_year_utc = datetime.now(UTC).year
    recency_min_release_year = (
        current_year_utc - controls.recency_years_min_offset
        if controls.recency_years_min_offset is not None
        else None
    )
    return language_filter_codes, current_year_utc, recency_min_release_year


class RetrievalStage:
    """Object-oriented BL-005 workflow shell over the existing retrieval logic."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    def resolve_paths(self) -> RetrievalPaths:
        return RetrievalPaths(
            profile_path=self.root / "profile" / "outputs" / "bl004_preference_profile.json",
            seed_trace_path=self.root / "profile" / "outputs" / "bl004_seed_trace.csv",
            candidate_path=self.root / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv",
            output_dir=self.root / "retrieval" / "outputs",
        )

    def resolve_runtime_controls(self) -> RetrievalControls:
        payload = resolve_bl005_runtime_controls()
        defaults = DEFAULT_RETRIEVAL_CONTROLS
        return RetrievalControls(
            config_source=str(payload.get("config_source") or "environment"),
            run_config_path=(str(payload["run_config_path"]) if payload.get("run_config_path") else None),
            run_config_schema_version=(
                str(payload["run_config_schema_version"])
                if payload.get("run_config_schema_version")
                else None
            ),
            signal_mode={str(k): v for k, v in to_mapping(payload.get("signal_mode")).items()},
            profile_top_lead_genre_limit=to_int(
                payload.get("profile_top_lead_genre_limit"),
                DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
            ),
            profile_top_tag_limit=to_int(
                payload.get("profile_top_tag_limit"),
                DEFAULT_PROFILE_TOP_TAG_LIMIT,
            ),
            profile_top_genre_limit=to_int(
                payload.get("profile_top_genre_limit"),
                DEFAULT_PROFILE_TOP_GENRE_LIMIT,
            ),
            semantic_strong_keep_score=to_int(
                payload.get("semantic_strong_keep_score"),
                DEFAULT_SEMANTIC_STRONG_KEEP_SCORE,
            ),
            semantic_min_keep_score=to_int(
                payload.get("semantic_min_keep_score"),
                DEFAULT_SEMANTIC_MIN_KEEP_SCORE,
            ),
            numeric_support_min_pass=to_int(
                payload.get("numeric_support_min_pass"),
                DEFAULT_NUMERIC_SUPPORT_MIN_PASS,
            ),
            numeric_support_min_score=to_float(
                payload.get("numeric_support_min_score"),
                DEFAULT_NUMERIC_SUPPORT_MIN_SCORE,
            ),
            lead_genre_partial_match_threshold=to_float(
                payload.get("lead_genre_partial_match_threshold"),
                DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
            ),
            use_weighted_semantics=bool(payload.get("use_weighted_semantics", False)),
            use_continuous_numeric=bool(payload.get("use_continuous_numeric", False)),
            enable_popularity_numeric=bool(payload.get("enable_popularity_numeric", False)),
            language_filter_enabled=bool(payload.get("language_filter_enabled", False)),
            language_filter_codes=to_string_list(payload.get("language_filter_codes"), allow_tuple=True, drop_empty=True),
            recency_years_min_offset=(
                to_int(payload["recency_years_min_offset"])
                if payload.get("recency_years_min_offset") is not None
                else None
            ),
            numeric_thresholds={
                str(k): to_float(v)
                for k, v in to_mapping(payload.get("numeric_thresholds")).items()
            },
            profile_quality_penalty_enabled=bool(
                payload.get("profile_quality_penalty_enabled", defaults["profile_quality_penalty_enabled"])
            ),
            profile_quality_threshold=to_float(
                payload.get("profile_quality_threshold"),
                to_float(defaults["profile_quality_threshold"], 0.90),
            ),
            profile_entropy_low_threshold=to_float(
                payload.get("profile_entropy_low_threshold"),
                to_float(defaults["profile_entropy_low_threshold"], 0.35),
            ),
            influence_share_threshold=to_float(
                payload.get("influence_share_threshold"),
                to_float(defaults["influence_share_threshold"], 0.60),
            ),
            profile_quality_penalty_increment=to_float(
                payload.get("profile_quality_penalty_increment"),
                to_float(defaults["profile_quality_penalty_increment"], 0.20),
            ),
            profile_entropy_penalty_increment=to_float(
                payload.get("profile_entropy_penalty_increment"),
                to_float(defaults["profile_entropy_penalty_increment"], 0.20),
            ),
            influence_share_penalty_increment=to_float(
                payload.get("influence_share_penalty_increment"),
                to_float(defaults["influence_share_penalty_increment"], 0.15),
            ),
            numeric_penalty_scale=to_float(
                payload.get("numeric_penalty_scale"),
                to_float(defaults["numeric_penalty_scale"], 0.50),
            ),
            semantic_overlap_damping_mid_entropy_threshold=to_float(
                payload.get("semantic_overlap_damping_mid_entropy_threshold"),
                to_float(defaults["semantic_overlap_damping_mid_entropy_threshold"], 0.60),
            ),
            semantic_overlap_damping_low_entropy=to_float(
                payload.get("semantic_overlap_damping_low_entropy"),
                to_float(defaults["semantic_overlap_damping_low_entropy"], 0.85),
            ),
            semantic_overlap_damping_mid_entropy=to_float(
                payload.get("semantic_overlap_damping_mid_entropy"),
                to_float(defaults["semantic_overlap_damping_mid_entropy"], 0.92),
            ),
            enable_numeric_confidence_scaling=bool(
                payload.get("enable_numeric_confidence_scaling", defaults["enable_numeric_confidence_scaling"])
            ),
            numeric_confidence_floor=to_float(
                payload.get("numeric_confidence_floor"),
                to_float(defaults["numeric_confidence_floor"], 0.0),
            ),
            profile_numeric_confidence_mode=str(
                payload.get("profile_numeric_confidence_mode")
                or defaults["profile_numeric_confidence_mode"]
            ),
            profile_numeric_confidence_blend_weight=to_float(
                payload.get("profile_numeric_confidence_blend_weight"),
                to_float(defaults["profile_numeric_confidence_blend_weight"], 1.0),
            ),
            numeric_support_score_mode=str(
                payload.get("numeric_support_score_mode") or defaults["numeric_support_score_mode"]
            ),
            emit_profile_policy_diagnostics=bool(
                payload.get("emit_profile_policy_diagnostics", defaults["emit_profile_policy_diagnostics"])
            ),
            bl004_bl005_handshake_validation_policy=str(
                payload.get("bl004_bl005_handshake_validation_policy")
                or defaults["bl004_bl005_handshake_validation_policy"]
            ),
            runtime_control_resolution_diagnostics={
                str(key): value
                for key, value in to_mapping(payload.get("runtime_control_resolution_diagnostics")).items()
            },
            runtime_control_validation_warnings=to_string_list(
                payload.get("runtime_control_validation_warnings")
            ),
        )

    @staticmethod
    def load_inputs(paths: RetrievalPaths, controls: RetrievalControls | None = None) -> RetrievalInputs:
        profile = load_json(paths.profile_path)
        if not isinstance(profile, dict):
            raise RuntimeError("BL-005 profile artifact is malformed; expected JSON object")
        candidate_rows_raw = load_csv_rows(paths.candidate_path)
        if not candidate_rows_raw:
            raise RuntimeError("BL-005 candidate corpus is empty; cannot build retrieval outputs")
        candidate_rows = [normalize_candidate_row(row) for row in candidate_rows_raw]
        seed_trace_rows = load_csv_rows(paths.seed_trace_path)
        numeric_thresholds = (
            controls.numeric_thresholds
            if controls is not None
            else {
                str(key): to_float(value)
                for key, value in to_mapping(DEFAULT_RETRIEVAL_CONTROLS.get("numeric_thresholds")).items()
            }
        )

        handshake_validation = validate_bl004_bl005_handshake(
            profile=profile,
            seed_trace_rows=seed_trace_rows,
            numeric_thresholds=numeric_thresholds,
            policy=(controls.bl004_bl005_handshake_validation_policy if controls else "warn"),
        )
        if handshake_validation["status"] == "fail":
            violations_obj = handshake_validation.get("sampled_violations")
            violations = list(violations_obj) if isinstance(violations_obj, list) else []
            raise RuntimeError(
                "BL-005 handshake validation failed under strict policy: " + "; ".join(str(v) for v in violations)
            )
        if handshake_validation["status"] in {"warn", "allow"}:
            logger.warning(
                "BL-005 handshake validation status=%s policy=%s violations=%s",
                handshake_validation.get("status"),
                handshake_validation.get("policy"),
                handshake_validation.get("sampled_violations"),
            )

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
        effective_numeric_specs = _build_effective_numeric_specs(controls)

        seed_track_ids = {str(row["track_id"]) for row in inputs.seed_trace_rows}
        candidate_columns = set(inputs.candidate_rows[0].keys()) if inputs.candidate_rows else set()

        (
            top_lead_genres,
            lead_genre_weights,
            top_tags,
            tag_weights,
            top_genres,
            genre_weights,
        ) = _build_profile_semantic_context(inputs, controls)
        (
            active_numeric_specs,
            numeric_centers,
            numeric_features_enabled,
            feature_confidence_by_name,
            profile_numeric_confidence_factor,
            numeric_confidence_floor,
        ) = _build_numeric_profile_context(
            inputs,
            controls,
            effective_numeric_specs,
            candidate_columns,
        )
        (
            profile_match_quality,
            top_genre_entropy,
            top_tag_entropy,
            history_weight_share,
            influence_weight_share,
        ) = _build_profile_signal_metrics(inputs)
        (
            threshold_penalty,
            effective_semantic_min_keep_score,
            effective_semantic_strong_keep_score,
            effective_numeric_support_min_pass,
            effective_numeric_support_min_score,
            semantic_overlap_damping,
        ) = _build_effective_threshold_context(
            controls,
            profile_match_quality=profile_match_quality,
            top_genre_entropy=top_genre_entropy,
            top_tag_entropy=top_tag_entropy,
            influence_weight_share=influence_weight_share,
        )
        language_filter_codes, current_year_utc, recency_min_release_year = _build_recency_context(controls)

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
    def _build_threshold_attribution(
        *,
        decisions: list[dict[str, object]],
        runtime_context: RetrievalContext,
    ) -> dict[str, object]:
        rejected_threshold_rows = [
            row
            for row in decisions
            if str(row.get("decision_path", "")).startswith("reject_threshold")
        ]
        numeric_fail_counts = {
            feature: 0 for feature in runtime_context.active_numeric_specs
        }
        numeric_missing_counts = {
            feature: 0 for feature in runtime_context.active_numeric_specs
        }
        semantic_below_min = 0
        semantic_between_min_and_strong = 0
        numeric_support_below_min = 0

        for row in rejected_threshold_rows:
            semantic_score = safe_float(row.get("semantic_score", 0.0), 0.0)
            if semantic_score < runtime_context.effective_semantic_min_keep_score:
                semantic_below_min += 1
            elif semantic_score < runtime_context.effective_semantic_strong_keep_score:
                semantic_between_min_and_strong += 1

            if runtime_context.use_continuous_numeric:
                selected_score = safe_float(row.get("numeric_support_score_selected", 0.0), 0.0)
                if selected_score < runtime_context.effective_numeric_support_min_score:
                    numeric_support_below_min += 1
            else:
                pass_count = safe_int(row.get("numeric_pass_count", 0), 0)
                if pass_count < runtime_context.effective_numeric_support_min_pass:
                    numeric_support_below_min += 1

            for feature, spec in runtime_context.active_numeric_specs.items():
                distance_key = f"{feature}_distance"
                distance_raw = row.get(distance_key)
                if distance_raw in (None, ""):
                    numeric_missing_counts[feature] += 1
                    continue
                distance = safe_float(distance_raw, -1.0)
                if distance >= 0.0 and distance > spec.threshold:
                    numeric_fail_counts[feature] += 1

        rejected_total = len(rejected_threshold_rows)
        top_failure_features = sorted(
            [
                {
                    "feature": feature,
                    "failed_count": int(count),
                    "failed_share": round((count / rejected_total), 6) if rejected_total else 0.0,
                    "missing_count": int(numeric_missing_counts.get(feature, 0)),
                    "configured_threshold": round(
                        safe_float(runtime_context.active_numeric_specs[feature].threshold, 0.0),
                        6,
                    ),
                }
                for feature, count in numeric_fail_counts.items()
            ],
            key=lambda item: (safe_int(item.get("failed_count", 0), 0), item.get("feature", "")),
            reverse=True,
        )[:5]

        return {
            "rejected_threshold_candidates": rejected_total,
            "semantic_below_effective_min_count": semantic_below_min,
            "semantic_between_min_and_strong_count": semantic_between_min_and_strong,
            "numeric_support_below_effective_min_count": numeric_support_below_min,
            "numeric_feature_fail_counts": numeric_fail_counts,
            "numeric_feature_missing_counts": numeric_missing_counts,
            "top_failure_features": top_failure_features,
            "notes": (
                "Counts are heuristic attribution summaries from candidate-level decision rows; "
                "they are diagnostic aids, not full causal proof."
            ),
        }

    @staticmethod
    def _build_bounded_what_if_estimates(
        *,
        decisions: list[dict[str, object]],
        runtime_context: RetrievalContext,
    ) -> dict[str, object]:
        candidate_rows = [
            row
            for row in decisions
            if not bool(safe_int(row.get("is_seed_track", 0), 0))
            and not str(row.get("decision_path", "")).startswith("reject_language_filter")
            and not str(row.get("decision_path", "")).startswith("reject_recency_gate")
        ]
        language_filtered_rows = [
            row
            for row in decisions
            if not bool(safe_int(row.get("is_seed_track", 0), 0))
            and str(row.get("decision_path", "")).startswith("reject_language_filter")
        ]

        def estimate_kept_from_rows(
            rows: list[dict[str, object]],
            *,
            semantic_strong: float,
            semantic_min: float,
            numeric_min_pass: int,
            numeric_min_score: float,
        ) -> int:
            kept_count = 0
            for row in rows:
                kept, _ = keep_decision(
                    False,
                    safe_float(row.get("semantic_score", 0.0), 0.0),
                    safe_int(row.get("numeric_pass_count", 0), 0),
                    runtime_context.numeric_features_enabled,
                    semantic_strong,
                    semantic_min,
                    numeric_min_pass,
                    numeric_support_score=safe_float(row.get("numeric_support_score_selected", 0.0), 0.0),
                    numeric_support_min_score=numeric_min_score,
                    use_continuous_numeric=runtime_context.use_continuous_numeric,
                    language_match=None,
                    recency_pass=None,
                )
                if kept:
                    kept_count += 1
            return kept_count

        def estimate_kept(
            *,
            semantic_strong: float,
            semantic_min: float,
            numeric_min_pass: int,
            numeric_min_score: float,
        ) -> int:
            return estimate_kept_from_rows(
                candidate_rows,
                semantic_strong=semantic_strong,
                semantic_min=semantic_min,
                numeric_min_pass=numeric_min_pass,
                numeric_min_score=numeric_min_score,
            )

        base_kept = sum(1 for row in candidate_rows if str(row.get("decision", "")) == "keep")
        perturbation_pct = 0.10

        relaxed_semantic_min = runtime_context.effective_semantic_min_keep_score * (1.0 - perturbation_pct)
        relaxed_semantic_strong = max(
            relaxed_semantic_min,
            runtime_context.effective_semantic_strong_keep_score * (1.0 - perturbation_pct),
        )
        if runtime_context.use_continuous_numeric:
            relaxed_numeric_min_pass = runtime_context.effective_numeric_support_min_pass
            relaxed_numeric_min_score = runtime_context.effective_numeric_support_min_score * (1.0 - perturbation_pct)
        else:
            relaxed_numeric_min_pass = max(0, runtime_context.effective_numeric_support_min_pass - 1)
            relaxed_numeric_min_score = runtime_context.effective_numeric_support_min_score

        tightened_semantic_min = runtime_context.effective_semantic_min_keep_score * (1.0 + perturbation_pct)
        tightened_semantic_strong = max(
            tightened_semantic_min,
            runtime_context.effective_semantic_strong_keep_score * (1.0 + perturbation_pct),
        )
        if runtime_context.use_continuous_numeric:
            tightened_numeric_min_pass = runtime_context.effective_numeric_support_min_pass
            tightened_numeric_min_score = runtime_context.effective_numeric_support_min_score * (1.0 + perturbation_pct)
        else:
            tightened_numeric_min_pass = runtime_context.effective_numeric_support_min_pass + 1
            tightened_numeric_min_score = runtime_context.effective_numeric_support_min_score

        relaxed_kept = estimate_kept(
            semantic_strong=relaxed_semantic_strong,
            semantic_min=relaxed_semantic_min,
            numeric_min_pass=relaxed_numeric_min_pass,
            numeric_min_score=relaxed_numeric_min_score,
        )
        tightened_kept = estimate_kept(
            semantic_strong=tightened_semantic_strong,
            semantic_min=tightened_semantic_min,
            numeric_min_pass=tightened_numeric_min_pass,
            numeric_min_score=tightened_numeric_min_score,
        )

        # Language filter what-if: re-evaluate threshold logic on rows that were
        # rejected only by the language gate, using base thresholds unchanged.
        # Rows that were language-filtered have all threshold feature scores
        # populated (scoring happens before the language gate in keep_decision),
        # so this is a bounded row-level estimate, not a full re-retrieval.
        all_non_seed_excl_recency = candidate_rows + language_filtered_rows
        language_filter_disabled_kept = estimate_kept_from_rows(
            all_non_seed_excl_recency,
            semantic_strong=runtime_context.effective_semantic_strong_keep_score,
            semantic_min=runtime_context.effective_semantic_min_keep_score,
            numeric_min_pass=runtime_context.effective_numeric_support_min_pass,
            numeric_min_score=runtime_context.effective_numeric_support_min_score,
        )
        language_filter_delta = language_filter_disabled_kept - base_kept

        return {
            "considered_candidates": len(candidate_rows),
            "base_kept_candidates": base_kept,
            "perturbation": {
                "label": "thresholds_plus_minus_10pct_with_discrete_pass_count_step",
                "fraction": perturbation_pct,
            },
            "relaxed_estimate": {
                "kept_candidates": relaxed_kept,
                "delta_vs_base": relaxed_kept - base_kept,
                "delta_share_vs_base": round(
                    ((relaxed_kept - base_kept) / base_kept),
                    6,
                ) if base_kept > 0 else 0.0,
            },
            "tightened_estimate": {
                "kept_candidates": tightened_kept,
                "delta_vs_base": tightened_kept - base_kept,
                "delta_share_vs_base": round(
                    ((tightened_kept - base_kept) / base_kept),
                    6,
                ) if base_kept > 0 else 0.0,
            },
            "per_control_family_scenarios": {
                "thresholds": {
                    "description": (
                        "Combined ±10% threshold perturbation across semantic and numeric params. "
                        "Shows sensitivity of kept-candidate count to coordinated threshold shifts."
                    ),
                    "relaxed_kept_candidates": relaxed_kept,
                    "relaxed_delta_vs_base": relaxed_kept - base_kept,
                    "tightened_kept_candidates": tightened_kept,
                    "tightened_delta_vs_base": tightened_kept - base_kept,
                },
                "language_filter": {
                    "description": (
                        "Bounded row-level estimate: if the language gate were disabled, "
                        "how many previously language-filtered candidates would pass the current "
                        "threshold rules. Uses existing decision-feature scores; not a full re-retrieval."
                    ),
                    "language_filtered_candidates": len(language_filtered_rows),
                    "disabled_kept_candidates": language_filter_disabled_kept,
                    "delta_vs_base": language_filter_delta,
                    "delta_share_vs_base": round(language_filter_delta / base_kept, 6) if base_kept > 0 else 0.0,
                },
                "assembly_limits": {
                    "description": (
                        "Assembly limit effects are downstream of BL-005 retrieval. "
                        "Per-control-family assembly what-if analysis is scoped to BL-007/BL-008 "
                        "observability payloads; see UNDO-Q for cross-stage attribution hardening."
                    ),
                    "scope": "out_of_bl005_scope",
                },
            },
            "notes": (
                "This is a bounded, row-level diagnostic estimate using existing decision features; "
                "it is not a full rerun-level counterfactual simulation."
            ),
        }

    @staticmethod
    def _build_candidate_shaping_fidelity(
        *,
        counts: Mapping[str, object],
        decision_path_counts: Mapping[str, object],
        threshold_attribution: dict[str, object],
        bounded_what_if_estimates: dict[str, object],
    ) -> dict[str, object]:
        total_candidates = safe_int(counts.get("candidate_rows_total", 0), 0)
        seed_tracks_excluded = safe_int(counts.get("seed_tracks_excluded", 0), 0)
        rejected_by_language_filter = safe_int(counts.get("rejected_by_language_filter", 0), 0)
        rejected_by_recency_gate = safe_int(counts.get("rejected_by_recency_gate", 0), 0)
        rejected_non_seed_candidates = safe_int(counts.get("rejected_non_seed_candidates", 0), 0)
        kept_candidates = safe_int(counts.get("kept_candidates", 0), 0)

        post_seed_pool = max(0, total_candidates - seed_tracks_excluded)
        post_language_pool = max(0, post_seed_pool - rejected_by_language_filter)
        post_recency_pool = max(0, post_language_pool - rejected_by_recency_gate)

        def _share(value: int, denominator: int) -> float:
            if denominator <= 0:
                return 0.0
            return round(value / denominator, 6)

        exclusion_categories = {
            "reject_seed_track": seed_tracks_excluded,
            "reject_language_filter": rejected_by_language_filter,
            "reject_recency_gate": rejected_by_recency_gate,
            "reject_semantic_without_numeric_support": safe_int(
                decision_path_counts.get("reject_semantic_without_numeric_support", 0),
                0,
            ),
            "reject_numeric_without_semantic_support": safe_int(
                decision_path_counts.get("reject_numeric_without_semantic_support", 0),
                0,
            ),
            "reject_no_signal": safe_int(decision_path_counts.get("reject_no_signal", 0), 0),
            "reject_insufficient_semantic": safe_int(
                decision_path_counts.get("reject_insufficient_semantic", 0),
                0,
            ),
        }

        threshold_rejection_count = (
            exclusion_categories["reject_semantic_without_numeric_support"]
            + exclusion_categories["reject_numeric_without_semantic_support"]
            + exclusion_categories["reject_no_signal"]
            + exclusion_categories["reject_insufficient_semantic"]
        )
        total_rejections = max(0, rejected_non_seed_candidates)
        ranked_rejection_drivers = sorted(
            [
                {
                    "driver": name,
                    "count": int(value),
                    "share_of_post_recency_pool": _share(int(value), post_recency_pool),
                    "share_of_total_rejections": _share(int(value), total_rejections),
                }
                for name, value in exclusion_categories.items()
            ],
            key=lambda item: (safe_int(item.get("count"), 0), str(item.get("driver", ""))),
            reverse=True,
        )
        dominant_rejection_driver = ranked_rejection_drivers[0] if ranked_rejection_drivers else None

        relaxed_estimate = to_mapping(bounded_what_if_estimates.get("relaxed_estimate"))
        tightened_estimate = to_mapping(bounded_what_if_estimates.get("tightened_estimate"))
        relaxed_delta = safe_int(relaxed_estimate.get("delta_vs_base"), 0)
        tightened_delta = safe_int(tightened_estimate.get("delta_vs_base"), 0)
        net_directional_span = relaxed_delta - tightened_delta
        directionality = "symmetric"
        if net_directional_span > 0:
            directionality = "relaxation_dominant"
        elif net_directional_span < 0:
            directionality = "tightening_dominant"

        return {
            "pool_progression": {
                "candidate_rows_total": total_candidates,
                "post_seed_exclusion_pool": post_seed_pool,
                "post_language_filter_pool": post_language_pool,
                "post_recency_gate_pool": post_recency_pool,
                "kept_candidates": kept_candidates,
                "rejected_non_seed_candidates": rejected_non_seed_candidates,
                "trend": [
                    {"stage": "candidate_rows_total", "count": total_candidates},
                    {"stage": "post_seed_exclusion_pool", "count": post_seed_pool},
                    {"stage": "post_language_filter_pool", "count": post_language_pool},
                    {"stage": "post_recency_gate_pool", "count": post_recency_pool},
                    {"stage": "kept_candidates", "count": kept_candidates},
                ],
            },
            "exclusion_categories": exclusion_categories,
            "control_effect_observability": {
                "seed_exclusion_share": _share(seed_tracks_excluded, total_candidates),
                "language_filter_rejection_share": _share(rejected_by_language_filter, post_seed_pool),
                "recency_gate_rejection_share": _share(rejected_by_recency_gate, post_language_pool),
                "threshold_rejection_share": _share(threshold_rejection_count, post_recency_pool),
                "retained_share_after_gates": _share(kept_candidates, post_recency_pool),
            },
            "rejection_driver_contribution": {
                "ranked_rejection_drivers": ranked_rejection_drivers,
                "dominant_rejection_driver": (
                    str(dominant_rejection_driver.get("driver", ""))
                    if isinstance(dominant_rejection_driver, dict)
                    else ""
                ),
                "dominant_rejection_driver_share_of_total_rejections": (
                    safe_float(
                        dominant_rejection_driver.get("share_of_total_rejections", 0.0),
                        0.0,
                    )
                    if isinstance(dominant_rejection_driver, dict)
                    else 0.0
                ),
            },
            "threshold_effects": {
                "threshold_attribution": threshold_attribution,
                "bounded_what_if_estimates": bounded_what_if_estimates,
                "directional_impact_summary": {
                    "relaxed_delta_vs_base": relaxed_delta,
                    "tightened_delta_vs_base": tightened_delta,
                    "net_directional_span": net_directional_span,
                    "dominant_direction": directionality,
                },
            },
            "notes": (
                "UNDO-C candidate-shaping fidelity block summarizes pool-size progression, "
                "exclusion categories, and control/threshold effects for BL-005 diagnostics visibility."
            ),
        }

    @staticmethod
    def build_diagnostics_payload(
        *,
        run_id: str,
        elapsed_seconds: float,
        paths: RetrievalPaths,
        runtime_context: RetrievalContext,
        controls: RetrievalControls | None = None,
        summary: dict[str, object],
        decisions: list[dict[str, object]] | None = None,
        candidate_rows: list[dict[str, str]],
        kept_rows: list[dict[str, str]],
        output_paths: dict[str, Path],
        handshake_validation: dict[str, object] | None = None,
    ) -> dict[str, object]:
        decision_counts_obj = summary.get("decision_counts")
        decision_counts = decision_counts_obj if isinstance(decision_counts_obj, dict) else {}
        decision_path_counts_obj = summary.get("decision_path_counts")
        decision_path_counts = decision_path_counts_obj if isinstance(decision_path_counts_obj, dict) else {}

        validation = dict(handshake_validation or {})
        resolved_decisions = decisions or []
        handshake_policy = "warn"
        if controls is not None:
            handshake_policy = controls.bl004_bl005_handshake_validation_policy
        counts = {
            "candidate_rows_total": len(candidate_rows),
            "seed_tracks_excluded": int(decision_counts.get("seed_excluded", 0)),
            "kept_candidates": len(kept_rows),
            "rejected_non_seed_candidates": int(decision_counts.get("rejected_threshold", 0)),
            "rejected_by_language_filter": int(decision_path_counts.get("reject_language_filter", 0)),
            "rejected_by_recency_gate": int(decision_path_counts.get("reject_recency_gate", 0)),
        }
        threshold_attribution = RetrievalStage._build_threshold_attribution(
            decisions=resolved_decisions,
            runtime_context=runtime_context,
        )
        bounded_what_if_estimates = RetrievalStage._build_bounded_what_if_estimates(
            decisions=resolved_decisions,
            runtime_context=runtime_context,
        )
        candidate_shaping_fidelity = RetrievalStage._build_candidate_shaping_fidelity(
            counts=counts,
            decision_path_counts=decision_path_counts,
            threshold_attribution=threshold_attribution,
            bounded_what_if_estimates=bounded_what_if_estimates,
        )
        profile_numeric_features_available_obj = validation.get("profile_numeric_features_available")
        numeric_threshold_keys_obj = validation.get("numeric_threshold_keys")

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
                "validation_policies": {
                    "bl004_bl005_handshake_validation_policy": handshake_policy,
                },
                "runtime_control_resolution": (
                    dict(controls.runtime_control_resolution_diagnostics)
                    if controls is not None
                    else {}
                ),
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
            "counts": counts,
            "rule_hits": {
                "semantic_rule_hits": summary["semantic_rule_hits"],
                "numeric_rule_hits": summary["numeric_rule_hits"],
            },
            "decision_path_counts": summary["decision_path_counts"],
            "threshold_attribution": threshold_attribution,
            "bounded_what_if_estimates": bounded_what_if_estimates,
            "candidate_shaping_fidelity": candidate_shaping_fidelity,
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
            "validation": validation,
            "handshake": {
                "bl004_bl005_policy": handshake_policy,
                "profile_schema_valid": bool(validation.get("bl004_profile_schema_valid", False)),
                "seed_trace_schema_valid": bool(validation.get("seed_trace_schema_valid", False)),
                "control_constraints_valid": bool(validation.get("control_constraints_valid", False)),
                "profile_numeric_features_available": (
                    list(profile_numeric_features_available_obj)
                    if isinstance(profile_numeric_features_available_obj, list)
                    else []
                ),
                "numeric_threshold_keys": (
                    list(numeric_threshold_keys_obj)
                    if isinstance(numeric_threshold_keys_obj, list)
                    else []
                ),
            },
            "elapsed_seconds": round(elapsed_seconds, 3),
            "runtime_control_validation_warnings": (
                list(controls.runtime_control_validation_warnings)
                if controls is not None
                else []
            ),
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
        if controls.runtime_control_validation_warnings:
            logger.warning(
                "BL-005 runtime control validation warnings=%s",
                controls.runtime_control_validation_warnings,
            )
        inputs = self.load_inputs(paths, controls)
        handshake_validation = validate_bl004_bl005_handshake(
            profile=inputs.profile,
            seed_trace_rows=inputs.seed_trace_rows,
            numeric_thresholds=controls.numeric_thresholds,
            policy=controls.bl004_bl005_handshake_validation_policy,
        )
        context = self.build_runtime_context(inputs=inputs, controls=controls)

        start_time = time.time()
        run_id = f"BL005-FILTER-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S-%f')}"
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
            controls=controls,
            summary=evaluation.summary,
            decisions=evaluation.decisions,
            candidate_rows=inputs.candidate_rows,
            kept_rows=evaluation.kept_rows,
            output_paths=output_paths,
            handshake_validation=handshake_validation,
        )

        diagnostics_path = paths.output_dir / "bl005_candidate_diagnostics.json"
        self.write_diagnostics_with_hashes(
            diagnostics=diagnostics,
            diagnostics_path=diagnostics_path,
            output_paths=output_paths,
        )

        logger.info("BL-005 candidate filtering complete.")
        logger.info("filtered_candidates=%s", output_paths["filtered_path"])
        logger.info("decisions=%s", output_paths["decisions_path"])
        logger.info("diagnostics=%s", diagnostics_path)

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
