from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


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
    profile_top_lead_genre_limit: int
    profile_top_tag_limit: int
    profile_top_genre_limit: int
    semantic_strong_keep_score: int
    semantic_min_keep_score: int
    numeric_support_min_pass: int
    lead_genre_partial_match_threshold: float
    language_filter_enabled: bool
    language_filter_codes: list[str]
    recency_years_min_offset: int | None
    numeric_thresholds: dict[str, float]


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
    profile_top_lead_genre_limit: int
    profile_top_tag_limit: int
    profile_top_genre_limit: int
    semantic_strong_keep_score: int
    semantic_min_keep_score: int
    numeric_support_min_pass: int
    lead_genre_partial_match_threshold: float
    active_numeric_specs: dict[str, NumericFeatureSpec]
    seed_track_ids: set[str]
    top_lead_genres: set[str]
    top_tags: set[str]
    top_genres: set[str]
    numeric_centers: dict[str, float]
    numeric_features_enabled: bool
    language_filter_enabled: bool
    language_filter_codes: list[str]
    recency_years_min_offset: int | None
    current_year_utc: int
    recency_min_release_year: int | None


@dataclass(frozen=True)
class RetrievalEvaluationResult:
    decisions: list[dict[str, object]]
    kept_rows: list[dict[str, str]]
    summary: dict[str, object]


def context_from_mapping(payload: Mapping[str, Any]) -> RetrievalContext:
    """Compatibility bridge for tests/callers still passing dict runtime context."""
    active_raw = payload.get("active_numeric_specs") or {}
    active_specs: dict[str, NumericFeatureSpec] = {}
    if isinstance(active_raw, Mapping):
        for key, value in active_raw.items():
            if isinstance(value, NumericFeatureSpec):
                active_specs[str(key)] = value
                continue
            if isinstance(value, Mapping):
                active_specs[str(key)] = NumericFeatureSpec(
                    candidate_column=str(value.get("candidate_column", "")),
                    threshold=float(value.get("threshold", 0.0)),
                    circular=bool(value.get("circular", False)),
                )

    return RetrievalContext(
        profile_top_lead_genre_limit=int(payload.get("profile_top_lead_genre_limit", 1)),
        profile_top_tag_limit=int(payload.get("profile_top_tag_limit", 1)),
        profile_top_genre_limit=int(payload.get("profile_top_genre_limit", 1)),
        semantic_strong_keep_score=int(payload.get("semantic_strong_keep_score", 0)),
        semantic_min_keep_score=int(payload.get("semantic_min_keep_score", 0)),
        numeric_support_min_pass=int(payload.get("numeric_support_min_pass", 0)),
        lead_genre_partial_match_threshold=float(payload.get("lead_genre_partial_match_threshold", 0.0)),
        active_numeric_specs=active_specs,
        seed_track_ids={str(v) for v in set(payload.get("seed_track_ids") or set())},
        top_lead_genres={str(v) for v in set(payload.get("top_lead_genres") or set())},
        top_tags={str(v) for v in set(payload.get("top_tags") or set())},
        top_genres={str(v) for v in set(payload.get("top_genres") or set())},
        numeric_centers={
            str(k): float(v) for k, v in dict(payload.get("numeric_centers") or {}).items()
        },
        numeric_features_enabled=bool(payload.get("numeric_features_enabled", False)),
        language_filter_enabled=bool(payload.get("language_filter_enabled", False)),
        language_filter_codes=[
            str(v) for v in list(payload.get("language_filter_codes") or []) if str(v)
        ],
        recency_years_min_offset=(
            int(payload["recency_years_min_offset"])
            if payload.get("recency_years_min_offset") is not None
            else None
        ),
        current_year_utc=int(payload.get("current_year_utc", 0)),
        recency_min_release_year=(
            int(payload["recency_min_release_year"])
            if payload.get("recency_min_release_year") is not None
            else None
        ),
    )
