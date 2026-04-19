from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RetrievalPaths:
    profile_path: Path
    seed_trace_path: Path
    candidate_path: Path
    output_dir: Path


@dataclass(frozen=True)
class RetrievalControls:
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    signal_mode: dict[str, object]
    profile_top_lead_genre_limit: int
    profile_top_tag_limit: int
    profile_top_genre_limit: int
    semantic_strong_keep_score: int
    semantic_min_keep_score: int
    numeric_support_min_pass: int
    numeric_support_min_score: float
    lead_genre_partial_match_threshold: float
    use_weighted_semantics: bool
    use_continuous_numeric: bool
    enable_popularity_numeric: bool
    language_filter_enabled: bool
    language_filter_codes: list[str]
    recency_years_min_offset: int | None
    numeric_thresholds: dict[str, float]
    profile_quality_penalty_enabled: bool = True
    profile_quality_threshold: float = 0.90
    profile_entropy_low_threshold: float = 0.35
    influence_share_threshold: float = 0.60
    profile_quality_penalty_increment: float = 0.20
    profile_entropy_penalty_increment: float = 0.20
    influence_share_penalty_increment: float = 0.15
    numeric_penalty_scale: float = 0.50
    semantic_overlap_damping_mid_entropy_threshold: float = 0.60
    semantic_overlap_damping_low_entropy: float = 0.85
    semantic_overlap_damping_mid_entropy: float = 0.92
    enable_numeric_confidence_scaling: bool = True
    numeric_confidence_floor: float = 0.0
    profile_numeric_confidence_mode: str = "direct"
    profile_numeric_confidence_blend_weight: float = 1.0
    numeric_support_score_mode: str = "weighted_absolute"
    emit_profile_policy_diagnostics: bool = True
    bl004_bl005_handshake_validation_policy: str = "warn"
    runtime_control_resolution_diagnostics: dict[str, object] = field(default_factory=dict)
    runtime_control_validation_warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NumericFeatureSpec:
    candidate_column: str
    threshold: float
    circular: bool


@dataclass(frozen=True)
class RetrievalInputs:
    profile: dict[str, object]
    candidate_rows: list[dict[str, str]]
    seed_trace_rows: list[dict[str, str]]


@dataclass(frozen=True)
class RetrievalContext:
    signal_mode: dict[str, object]
    profile_top_lead_genre_limit: int
    profile_top_tag_limit: int
    profile_top_genre_limit: int
    semantic_strong_keep_score: int
    semantic_min_keep_score: int
    numeric_support_min_pass: int
    numeric_support_min_score: float
    lead_genre_partial_match_threshold: float
    active_numeric_specs: dict[str, NumericFeatureSpec]
    seed_track_ids: set[str]
    top_lead_genres: set[str]
    top_tags: set[str]
    top_genres: set[str]
    lead_genre_weights: dict[str, float]
    tag_weights: dict[str, float]
    genre_weights: dict[str, float]
    numeric_centers: dict[str, float]
    numeric_features_enabled: bool
    use_weighted_semantics: bool
    use_continuous_numeric: bool
    language_filter_enabled: bool
    language_filter_codes: list[str]
    recency_years_min_offset: int | None
    current_year_utc: int
    recency_min_release_year: int | None
    feature_confidence_by_name: dict[str, float]
    profile_numeric_confidence_factor: float
    profile_match_quality: float
    top_genre_entropy: float
    top_tag_entropy: float
    history_weight_share: float
    influence_weight_share: float
    effective_semantic_strong_keep_score: float
    effective_semantic_min_keep_score: float
    effective_numeric_support_min_pass: int
    effective_numeric_support_min_score: float
    semantic_overlap_damping: float
    profile_quality_penalty_enabled: bool = True
    profile_quality_threshold: float = 0.90
    profile_entropy_low_threshold: float = 0.35
    influence_share_threshold: float = 0.60
    profile_quality_penalty_increment: float = 0.20
    profile_entropy_penalty_increment: float = 0.20
    influence_share_penalty_increment: float = 0.15
    numeric_penalty_scale: float = 0.50
    semantic_overlap_damping_mid_entropy_threshold: float = 0.60
    semantic_overlap_damping_low_entropy: float = 0.85
    semantic_overlap_damping_mid_entropy: float = 0.92
    enable_numeric_confidence_scaling: bool = True
    numeric_confidence_floor: float = 0.0
    profile_numeric_confidence_mode: str = "direct"
    profile_numeric_confidence_blend_weight: float = 1.0
    numeric_support_score_mode: str = "weighted_absolute"
    effective_threshold_penalty: float = 0.0
    emit_profile_policy_diagnostics: bool = True


@dataclass(frozen=True)
class RetrievalEvaluationResult:
    decisions: list[dict[str, object]]
    kept_rows: list[dict[str, str]]
    summary: dict[str, object]


@dataclass(frozen=True)
class RetrievalArtifacts:
    filtered_path: Path
    decisions_path: Path
    diagnostics_path: Path
    kept_candidates_count: int
    rejected_candidates_count: int
    seed_excluded_count: int
    elapsed_seconds: float


def _active_numeric_specs_from_payload(payload: Mapping[str, Any]) -> dict[str, NumericFeatureSpec]:
    active_raw = payload.get("active_numeric_specs") or {}
    active_specs: dict[str, NumericFeatureSpec] = {}
    if not isinstance(active_raw, Mapping):
        return active_specs

    for key, value in active_raw.items():
        normalized_key = str(key)
        if isinstance(value, NumericFeatureSpec):
            active_specs[normalized_key] = value
            continue
        if not isinstance(value, Mapping):
            continue
        active_specs[normalized_key] = NumericFeatureSpec(
            candidate_column=str(value.get("candidate_column", "")),
            threshold=float(value.get("threshold", 0.0)),
            circular=bool(value.get("circular", False)),
        )
    return active_specs


def _mapping_to_float_dict(value: Any) -> dict[str, float]:
    source = dict(value) if isinstance(value, Mapping) else {}
    return {str(k): float(v) for k, v in source.items()}


def _payload_str_set(payload: Mapping[str, Any], key: str) -> set[str]:
    raw = payload.get(key) or set()
    return {str(v) for v in set(raw)}


def _payload_optional_int(payload: Mapping[str, Any], key: str) -> int | None:
    value = payload.get(key)
    return int(value) if value is not None else None


def _payload_signal_mode(payload: Mapping[str, Any]) -> dict[str, object]:
    raw = payload.get("signal_mode") or {}
    source = dict(raw) if isinstance(raw, Mapping) else {}
    return {str(k): v for k, v in source.items()}


def context_from_mapping(payload: Mapping[str, Any]) -> RetrievalContext:
    """Compatibility bridge for tests/callers still passing dict runtime context."""
    active_specs = _active_numeric_specs_from_payload(payload)

    return RetrievalContext(
        signal_mode=_payload_signal_mode(payload),
        profile_top_lead_genre_limit=int(payload.get("profile_top_lead_genre_limit", 1)),
        profile_top_tag_limit=int(payload.get("profile_top_tag_limit", 1)),
        profile_top_genre_limit=int(payload.get("profile_top_genre_limit", 1)),
        semantic_strong_keep_score=int(payload.get("semantic_strong_keep_score", 0)),
        semantic_min_keep_score=int(payload.get("semantic_min_keep_score", 0)),
        numeric_support_min_pass=int(payload.get("numeric_support_min_pass", 0)),
        numeric_support_min_score=float(payload.get("numeric_support_min_score", payload.get("numeric_support_min_pass", 0.0))),
        lead_genre_partial_match_threshold=float(payload.get("lead_genre_partial_match_threshold", 0.0)),
        active_numeric_specs=active_specs,
        seed_track_ids=_payload_str_set(payload, "seed_track_ids"),
        top_lead_genres=_payload_str_set(payload, "top_lead_genres"),
        top_tags=_payload_str_set(payload, "top_tags"),
        top_genres=_payload_str_set(payload, "top_genres"),
        lead_genre_weights=_mapping_to_float_dict(payload.get("lead_genre_weights")),
        tag_weights=_mapping_to_float_dict(payload.get("tag_weights")),
        genre_weights=_mapping_to_float_dict(payload.get("genre_weights")),
        numeric_centers=_mapping_to_float_dict(payload.get("numeric_centers")),
        numeric_features_enabled=bool(payload.get("numeric_features_enabled", False)),
        use_weighted_semantics=bool(payload.get("use_weighted_semantics", False)),
        use_continuous_numeric=bool(payload.get("use_continuous_numeric", False)),
        language_filter_enabled=bool(payload.get("language_filter_enabled", False)),
        language_filter_codes=[
            str(v) for v in list(payload.get("language_filter_codes") or []) if str(v)
        ],
        recency_years_min_offset=_payload_optional_int(payload, "recency_years_min_offset"),
        current_year_utc=int(payload.get("current_year_utc", 0)),
        recency_min_release_year=_payload_optional_int(payload, "recency_min_release_year"),
        feature_confidence_by_name=_mapping_to_float_dict(payload.get("feature_confidence_by_name")),
        profile_numeric_confidence_factor=float(payload.get("profile_numeric_confidence_factor", 1.0)),
        profile_match_quality=float(payload.get("profile_match_quality", 1.0)),
        top_genre_entropy=float(payload.get("top_genre_entropy", 0.0)),
        top_tag_entropy=float(payload.get("top_tag_entropy", 0.0)),
        history_weight_share=float(payload.get("history_weight_share", 1.0)),
        influence_weight_share=float(payload.get("influence_weight_share", 0.0)),
        effective_semantic_strong_keep_score=float(
            payload.get("effective_semantic_strong_keep_score", payload.get("semantic_strong_keep_score", 0.0))
        ),
        effective_semantic_min_keep_score=float(
            payload.get("effective_semantic_min_keep_score", payload.get("semantic_min_keep_score", 0.0))
        ),
        effective_numeric_support_min_pass=int(
            payload.get("effective_numeric_support_min_pass", payload.get("numeric_support_min_pass", 0))
        ),
        effective_numeric_support_min_score=float(
            payload.get("effective_numeric_support_min_score", payload.get("numeric_support_min_score", 0.0))
        ),
        semantic_overlap_damping=float(payload.get("semantic_overlap_damping", 1.0)),
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
        profile_numeric_confidence_mode=str(payload.get("profile_numeric_confidence_mode", "direct")),
        profile_numeric_confidence_blend_weight=float(
            payload.get("profile_numeric_confidence_blend_weight", 1.0)
        ),
        numeric_support_score_mode=str(payload.get("numeric_support_score_mode", "weighted_absolute")),
        effective_threshold_penalty=float(payload.get("effective_threshold_penalty", 0.0)),
        emit_profile_policy_diagnostics=bool(payload.get("emit_profile_policy_diagnostics", True)),
    )
