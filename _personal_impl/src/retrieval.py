from __future__ import annotations

import csv
import json
import logging
import os
import time
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from shared.io_utils import load_csv_rows, load_json, sha256_of_file, utc_now, open_text_write
from shared.path_utils import impl_root
from shared.run_store import SQLiteRunStore, resolve_run_store_path
from shared.env_utils import env_bool, env_float, env_int, env_str
from shared.coerce_utils import coerce_enum, coerce_float, coerce_int, safe_float, safe_int, parse_float, parse_csv_labels
from run_config.stage_control_resolution import defaults_loader, resolve_stage_controls
from run_config.run_config_utils import DEFAULT_RETRIEVAL_CONTROLS as RUN_CONFIG_DEFAULT_RETRIEVAL_CONTROLS
from scoring import numeric_similarity, weighted_overlap


DEFAULT_RETRIEVAL_CONTROLS: dict[str, object] = {
    **deepcopy(RUN_CONFIG_DEFAULT_RETRIEVAL_CONTROLS),
    "signal_mode": {},
}
SHARED_NUMERIC_FEATURE_SPECS = {
    "danceability": {"candidate_column": "danceability", "threshold": 0.20, "circular": False},
    "energy": {"candidate_column": "energy", "threshold": 0.20, "circular": False},
    "valence": {"candidate_column": "valence", "threshold": 0.20, "circular": False},
    "tempo": {"candidate_column": "tempo", "threshold": 20.0, "circular": False},
    "popularity": {"candidate_column": "popularity", "threshold": 15.0, "circular": False},
    "key": {"candidate_column": "key", "threshold": 2.0, "circular": True},
    "mode": {"candidate_column": "mode", "threshold": 0.5, "circular": False},
    "duration_ms": {"candidate_column": "duration_ms", "threshold": 45000.0, "circular": False},
    "release_year": {"candidate_column": "release", "threshold": 8.0, "circular": False},
}
VALID_NUMERIC_CONFIDENCE_MODES: frozenset[str] = frozenset({"direct", "blended"})
VALID_NUMERIC_SUPPORT_SCORE_MODES: frozenset[str] = frozenset({"raw", "weighted", "weighted_absolute"})


def load_positive_numeric_map_from_env(env_var_name: str) -> dict[str, float]:
    raw = os.environ.get(env_var_name, "").strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {
        str(key): float(value)
        for key, value in payload.items()
        if isinstance(value, (int, float)) and float(value) > 0
    }


def ensure_paths_exist(
    paths: list[Path],
    *,
    stage_label: str,
    label: str = "input artifact(s)",
    root: Path | None = None,
) -> None:
    missing: list[str] = []
    for path in paths:
        if path.exists():
            continue
        if root is None:
            missing.append(str(path))
            continue
        try:
            missing.append(path.relative_to(root).as_posix())
        except ValueError:
            missing.append(str(path))
    if missing:
        raise FileNotFoundError(f"{stage_label} missing required {label}: {missing}")


logger = logging.getLogger(__name__)














def normalize_candidate_row(row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    track_id = (normalized.get("track_id") or "").strip()
    if not track_id:
        track_id = (normalized.get("id") or "").strip()
    if not track_id:
        track_id = (normalized.get("ds001_id") or "").strip()
    if not track_id:
        track_id = (normalized.get("cid") or "").strip()
    normalized["track_id"] = track_id
    return normalized





def tokenize_genre(value: str) -> set[str]:
    """Tokenize genre-like strings for robust partial matching."""
    normalized = value.replace("-", " ").replace("/", " ").strip().lower()
    return {token for token in normalized.split() if token}


def lead_genre_token_similarity(candidate: str, profile: str) -> float:
    """Return Jaccard token overlap for candidate/profile lead genres."""
    candidate_tokens = tokenize_genre(candidate)
    profile_tokens = tokenize_genre(profile)
    if not candidate_tokens or not profile_tokens:
        return 0.0
    union = candidate_tokens.union(profile_tokens)
    if not union:
        return 0.0
    return round(len(candidate_tokens.intersection(profile_tokens)) / len(union), 6)

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

REQUIRED_CANDIDATE_COLUMNS = {
    "genres",
    "tags",
    "lang",
    "release",
    "danceability",
    "energy",
    "valence",
    "tempo",
    "key",
    "mode",
}

CANDIDATE_ID_COLUMN_ALIASES = frozenset({"track_id", "id", "ds001_id", "cid"})


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


def _clamp_0_1(value: float) -> float:
    return max(0.0, min(1.0, value))


def _safe_float(raw: object, fallback: float = 0.0) -> float:
    try:
        return float(str(raw))
    except (TypeError, ValueError):
        return fallback


def _safe_int(raw: object, fallback: int = 0) -> int:
    try:
        return int(str(raw))
    except (TypeError, ValueError):
        return fallback


def _mapping(raw: object) -> dict[str, object]:
    if isinstance(raw, dict):
        return {str(key): value for key, value in raw.items()}
    return {}


def _string_list(raw: object) -> list[str]:
    if isinstance(raw, (list, tuple)):
        return [str(value) for value in raw if str(value)]
    return []


def _circular_distance_12(a: float, b: float) -> float:
    normalized_a = a % 12.0
    normalized_b = b % 12.0
    raw_diff = abs(normalized_a - normalized_b)
    return min(raw_diff, 12.0 - raw_diff)


def candidate_numeric_value(
    row: dict[str, str],
    profile_column: str,
    candidate_column: str,
) -> float | None:
    value = parse_float(row.get(candidate_column, ""))
    if value is None:
        return None
    if profile_column == "duration_ms" and candidate_column == "duration":
        return value * 1000.0
    return value


def resolve_candidate_column(
    profile_column: str,
    preferred_column: str,
    candidate_columns: set[str],
) -> str | None:
    if preferred_column in candidate_columns:
        return preferred_column
    if profile_column == "duration_ms" and "duration" in candidate_columns:
        return "duration"
    return None


def resolve_lead_genre(candidate_genres: list[str], candidate_tags: list[str]) -> str:
    if candidate_genres:
        return candidate_genres[0]
    if candidate_tags:
        return candidate_tags[0]
    return ""


def candidate_language_code(row: dict[str, str]) -> str | None:
    raw = str(row.get("lang", "")).strip().lower()
    if not raw or len(raw) > 8:
        return None
    return raw


def candidate_release_year(row: dict[str, str]) -> int | None:
    raw = str(row.get("release", "")).strip()
    if not raw:
        return None
    try:
        year = int(float(raw))
    except ValueError:
        return None
    if year < 1900 or year > 2100:
        return None
    return year


def build_profile_weight_map(
    profile: dict[str, object],
    semantic_key: str,
    limit: int,
) -> dict[str, float]:
    semantic_profile = profile.get("semantic_profile")
    if not isinstance(semantic_profile, dict):
        return {}
    items = semantic_profile.get(semantic_key)
    if not isinstance(items, list):
        return {}

    labels: list[str] = []
    weighted_entries: list[tuple[str, float]] = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        if not isinstance(label, str) or not label.strip():
            continue
        normalized_label = label.strip().lower()
        labels.append(normalized_label)
        raw_weight = item.get("weight")
        if isinstance(raw_weight, (int, float)) and float(raw_weight) > 0:
            weighted_entries.append((normalized_label, float(raw_weight)))

    if weighted_entries:
        total = sum(weight for _, weight in weighted_entries)
        if total > 0:
            return {label: round(weight / total, 6) for label, weight in weighted_entries}

    unique_labels = list(dict.fromkeys(labels))
    if not unique_labels:
        return {}
    uniform_weight = round(1.0 / len(unique_labels), 6)
    return {label: uniform_weight for label in unique_labels}


def build_profile_label_set(
    profile: dict[str, object],
    semantic_key: str,
    limit: int,
) -> set[str]:
    return set(build_profile_weight_map(profile, semantic_key, limit))


def build_active_numeric_specs(
    profile: dict[str, object],
    effective_numeric_specs: dict[str, NumericFeatureSpec],
    candidate_columns: set[str],
) -> dict[str, NumericFeatureSpec]:
    numeric_profile = profile.get("numeric_feature_profile")
    if not isinstance(numeric_profile, dict):
        return {}

    active_specs: dict[str, NumericFeatureSpec] = {}
    for profile_column, spec in effective_numeric_specs.items():
        if profile_column not in numeric_profile:
            continue
        resolved_column = resolve_candidate_column(profile_column, spec.candidate_column, candidate_columns)
        if resolved_column is None:
            continue
        active_specs[profile_column] = NumericFeatureSpec(
            candidate_column=resolved_column,
            threshold=spec.threshold,
            circular=spec.circular,
        )
    return active_specs


def _validate_numeric_support_score_mode(mode: str) -> str:
    normalized = str(mode).strip().lower()
    if normalized not in VALID_NUMERIC_SUPPORT_SCORE_MODES:
        raise RuntimeError(
            f"BL-005 numeric_support_score_mode must be one of {sorted(VALID_NUMERIC_SUPPORT_SCORE_MODES)}, got '{mode}'"
        )
    return normalized


def keep_decision(
    is_seed_track: bool,
    semantic_score: float,
    numeric_pass_count: int,
    numeric_features_enabled: bool,
    semantic_strong_keep_score: float,
    semantic_min_keep_score: float,
    numeric_support_min_pass: int,
    *,
    numeric_support_score: float | None = None,
    numeric_support_min_score: float | None = None,
    use_continuous_numeric: bool = False,
    language_match: bool | None = None,
    recency_pass: bool | None = None,
) -> tuple[bool, str]:
    if is_seed_track:
        return False, "reject_seed_track"
    if language_match is False:
        return False, "reject_language_filter"
    if recency_pass is False:
        return False, "reject_recency_gate"
    if not numeric_features_enabled:
        if semantic_score >= semantic_min_keep_score:
            return True, "keep_semantic_only"
        return False, "reject_insufficient_semantic"
    if semantic_score >= semantic_strong_keep_score:
        return True, "keep_strong_semantic"

    numeric_support_met = numeric_pass_count >= numeric_support_min_pass
    if use_continuous_numeric and numeric_support_score is not None:
        numeric_support_met = numeric_support_score >= float(
            numeric_support_min_score if numeric_support_min_score is not None else numeric_support_min_pass
        )

    if semantic_score >= semantic_min_keep_score and numeric_support_met:
        return True, "keep_semantic_numeric_supported"
    if semantic_score >= semantic_min_keep_score:
        return False, "reject_semantic_without_numeric_support"

    has_numeric_signal = numeric_pass_count > 0
    if use_continuous_numeric and numeric_support_score is not None:
        has_numeric_signal = numeric_support_score > 0.0
    if has_numeric_signal:
        return False, "reject_numeric_without_semantic_support"
    return False, "reject_no_signal"


def decision_reason(
    decision_path: str,
    semantic_score: float,
    numeric_pass_count: int,
    *,
    numeric_support_score: float | None = None,
    use_continuous_numeric: bool = False,
) -> str:
    numeric_support_fragment = (
        f"numeric_support_score={numeric_support_score:.2f}"
        if use_continuous_numeric and numeric_support_score is not None
        else f"numeric_pass_count={numeric_pass_count}"
    )
    if decision_path == "reject_seed_track":
        return "reject: seed track excluded from retrieval output"
    if decision_path == "reject_language_filter":
        return "reject: language filter mismatch"
    if decision_path == "reject_recency_gate":
        return "reject: release year outside recency gate"
    if decision_path == "keep_semantic_only":
        return f"keep: semantic_score={semantic_score:.2f} with semantic-only mode"
    if decision_path == "keep_strong_semantic":
        return f"keep: semantic_score={semantic_score:.2f} meets strong semantic threshold"
    if decision_path == "keep_semantic_numeric_supported":
        return f"keep: semantic_score={semantic_score:.2f} with {numeric_support_fragment}"
    if decision_path == "reject_semantic_without_numeric_support":
        return f"reject: semantic_score={semantic_score:.2f} lacks numeric support ({numeric_support_fragment})"
    if decision_path == "reject_numeric_without_semantic_support":
        return f"reject: {numeric_support_fragment} without semantic evidence"
    return f"reject: semantic_score={semantic_score:.2f}, {numeric_support_fragment} below keep threshold"


class _DecisionTracker:
    def __init__(self, numeric_feature_specs: dict[str, Any]) -> None:
        self.decisions: list[dict[str, object]] = []
        self.kept_rows: list[dict[str, str]] = []
        self.decision_counts = {
            "seed_excluded": 0,
            "kept_candidates": 0,
            "rejected_threshold": 0,
        }
        self.decision_path_counts: dict[str, int] = {}
        self.semantic_rule_hits = {
            "lead_genre_match": 0,
            "genre_overlap": 0,
            "tag_overlap": 0,
        }
        self.numeric_rule_hits = {key: 0 for key in numeric_feature_specs}
        self.semantic_score_distribution: dict[str, int] = {}
        self.numeric_pass_distribution = {str(score): 0 for score in range(len(numeric_feature_specs) + 1)}
        self.numeric_support_score_distribution: dict[str, int] = {}
        self.numeric_support_score_weighted_distribution: dict[str, int] = {}
        self.numeric_support_score_weighted_absolute_distribution: dict[str, int] = {}
        self.numeric_support_score_selected_distribution: dict[str, int] = {}
        self.effective_semantic_min_distribution: dict[str, int] = {}
        self.effective_numeric_support_min_score_distribution: dict[str, int] = {}

    def record_decision(
        self,
        track_id: str,
        is_seed_track: bool,
        kept: bool,
        decision_path: str,
        decision_record: dict[str, object],
        candidate_row: dict[str, str] | None = None,
    ) -> None:
        self.decisions.append(decision_record)
        if is_seed_track:
            self.decision_counts["seed_excluded"] += 1
        elif kept:
            self.decision_counts["kept_candidates"] += 1
            if candidate_row:
                self.kept_rows.append(candidate_row)
        else:
            self.decision_counts["rejected_threshold"] += 1
        self.decision_path_counts[decision_path] = self.decision_path_counts.get(decision_path, 0) + 1

    def record_semantic_scores(
        self,
        semantic_score: float,
        lead_genre_match: bool,
        genre_overlap: int,
        tag_overlap: int,
    ) -> None:
        score_str = f"{semantic_score:.2f}"
        self.semantic_score_distribution[score_str] = self.semantic_score_distribution.get(score_str, 0) + 1
        if lead_genre_match:
            self.semantic_rule_hits["lead_genre_match"] += 1
        if genre_overlap > 0:
            self.semantic_rule_hits["genre_overlap"] += 1
        if tag_overlap > 0:
            self.semantic_rule_hits["tag_overlap"] += 1

    def record_numeric_scores(
        self,
        numeric_pass_count: int,
        numeric_support_score: float,
        numeric_rule_hits_this_candidate: dict[str, bool],
        *,
        numeric_support_score_weighted: float,
        numeric_support_score_weighted_absolute: float,
        numeric_support_score_selected: float,
        effective_semantic_min_keep_score: float,
        effective_numeric_support_min_score: float,
    ) -> None:
        count_str = str(numeric_pass_count)
        self.numeric_pass_distribution[count_str] = self.numeric_pass_distribution.get(count_str, 0) + 1
        support_str = f"{numeric_support_score:.2f}"
        self.numeric_support_score_distribution[support_str] = self.numeric_support_score_distribution.get(support_str, 0) + 1
        weighted_support_str = f"{numeric_support_score_weighted:.2f}"
        self.numeric_support_score_weighted_distribution[weighted_support_str] = self.numeric_support_score_weighted_distribution.get(weighted_support_str, 0) + 1
        weighted_absolute_support_str = f"{numeric_support_score_weighted_absolute:.2f}"
        self.numeric_support_score_weighted_absolute_distribution[weighted_absolute_support_str] = self.numeric_support_score_weighted_absolute_distribution.get(weighted_absolute_support_str, 0) + 1
        selected_support_str = f"{numeric_support_score_selected:.2f}"
        self.numeric_support_score_selected_distribution[selected_support_str] = self.numeric_support_score_selected_distribution.get(selected_support_str, 0) + 1
        effective_semantic_min_str = f"{effective_semantic_min_keep_score:.2f}"
        self.effective_semantic_min_distribution[effective_semantic_min_str] = self.effective_semantic_min_distribution.get(effective_semantic_min_str, 0) + 1
        effective_numeric_min_str = f"{effective_numeric_support_min_score:.2f}"
        self.effective_numeric_support_min_score_distribution[effective_numeric_min_str] = self.effective_numeric_support_min_score_distribution.get(effective_numeric_min_str, 0) + 1
        for feature_name, passed in numeric_rule_hits_this_candidate.items():
            if passed:
                self.numeric_rule_hits[feature_name] = self.numeric_rule_hits.get(feature_name, 0) + 1

    def get_summary(self) -> dict[str, object]:
        return {
            "decision_counts": self.decision_counts,
            "decision_path_counts": self.decision_path_counts,
            "semantic_rule_hits": self.semantic_rule_hits,
            "numeric_rule_hits": self.numeric_rule_hits,
            "semantic_score_distribution": self.semantic_score_distribution,
            "numeric_pass_distribution": self.numeric_pass_distribution,
            "numeric_support_score_distribution": self.numeric_support_score_distribution,
            "numeric_support_score_weighted_distribution": self.numeric_support_score_weighted_distribution,
            "numeric_support_score_weighted_absolute_distribution": self.numeric_support_score_weighted_absolute_distribution,
            "numeric_support_score_selected_distribution": self.numeric_support_score_selected_distribution,
            "effective_semantic_min_distribution": self.effective_semantic_min_distribution,
            "effective_numeric_support_min_score_distribution": self.effective_numeric_support_min_score_distribution,
        }


def evaluate_bl005_candidates(
    *,
    candidate_rows: list[dict[str, str]],
    runtime_context: RetrievalContext | dict[str, object],
) -> tuple[_DecisionTracker, list[dict[str, object]], list[dict[str, str]], dict[str, object]]:
    context = runtime_context if isinstance(runtime_context, RetrievalContext) else context_from_mapping(runtime_context)
    numeric_support_score_mode = _validate_numeric_support_score_mode(context.numeric_support_score_mode)
    tracker = _DecisionTracker(context.active_numeric_specs)

    for row in candidate_rows:
        track_id = str(row["track_id"])
        is_seed_track = track_id in context.seed_track_ids
        candidate_tags = parse_csv_labels(str(row.get("tags", "")))
        candidate_genres = parse_csv_labels(str(row.get("genres", "")))
        lead_genre = resolve_lead_genre(candidate_genres, candidate_tags)
        language_code = candidate_language_code(row)
        release_year = candidate_release_year(row)

        language_match: bool | None = None
        if context.language_filter_enabled:
            language_match = bool(language_code and language_code in set(context.language_filter_codes))

        recency_pass: bool | None = None
        if context.recency_min_release_year is not None:
            recency_pass = bool(release_year is not None and release_year >= int(context.recency_min_release_year))

        genre_overlap = len(context.top_genres.intersection(candidate_genres))
        tag_overlap = len(context.top_tags.intersection(candidate_tags))
        if context.use_weighted_semantics:
            lead_genre_match_score = round(
                max(0.0, min(sum(
                    lead_genre_token_similarity(lead_genre, profile_label) * weight
                    for profile_label, weight in context.lead_genre_weights.items()
                ), 1.0)),
                6,
            ) if lead_genre and context.lead_genre_weights else 0.0
            genre_overlap_fraction = weighted_overlap(candidate_genres, context.genre_weights)
            tag_overlap_fraction = weighted_overlap(candidate_tags, context.tag_weights)
        else:
            lead_genre_match_score = 0.0
            if lead_genre and context.top_lead_genres:
                lead_genre_match_score = max(
                    lead_genre_token_similarity(lead_genre, profile_lead_genre)
                    for profile_lead_genre in context.top_lead_genres
                )
            genre_overlap_fraction = min(1.0, genre_overlap / max(1, len(context.top_genres)))
            tag_overlap_fraction = min(1.0, tag_overlap / max(1, len(context.top_tags)))

        genre_overlap_fraction = round(genre_overlap_fraction * context.semantic_overlap_damping, 6)
        tag_overlap_fraction = round(tag_overlap_fraction * context.semantic_overlap_damping, 6)
        lead_genre_match = lead_genre_match_score >= context.lead_genre_partial_match_threshold
        semantic_score = lead_genre_match_score + genre_overlap_fraction + tag_overlap_fraction
        tracker.record_semantic_scores(semantic_score, lead_genre_match, genre_overlap, tag_overlap)

        numeric_pass_count = 0
        numeric_support_score = 0.0
        weighted_support_numerator = 0.0
        weighted_support_denominator = 0.0
        numeric_support_score_weighted = 0.0
        numeric_support_score_weighted_absolute = 0.0
        numeric_distances: dict[str, float | None] = {}
        numeric_similarities: dict[str, float] = {}
        numeric_rule_hits_this_candidate: dict[str, bool] = {}

        for profile_column, spec in context.active_numeric_specs.items():
            value = candidate_numeric_value(row, profile_column, spec.candidate_column)
            passed = False
            if value is not None:
                center = context.numeric_centers.get(profile_column)
                if center is not None:
                    distance = _circular_distance_12(value, center) if spec.circular else abs(value - center)
                    similarity = numeric_similarity(value, center, spec.threshold, spec.circular)
                    numeric_distances[profile_column] = round(distance, 6)
                    numeric_similarities[profile_column] = similarity
                    numeric_support_score += similarity
                    confidence_weight = max(0.0, min(1.0, float(context.feature_confidence_by_name.get(profile_column, 1.0))))
                    weighted_support_numerator += similarity * confidence_weight
                    weighted_support_denominator += confidence_weight
                    if distance <= spec.threshold:
                        numeric_pass_count += 1
                        passed = True
                else:
                    numeric_distances[profile_column] = None
                    numeric_similarities[profile_column] = 0.0
            else:
                numeric_distances[profile_column] = None
                numeric_similarities[profile_column] = 0.0
            numeric_rule_hits_this_candidate[profile_column] = passed

        numeric_support_score = round(numeric_support_score, 6)
        if weighted_support_denominator > 0:
            weighted_average_similarity = weighted_support_numerator / weighted_support_denominator
            numeric_support_score_weighted = weighted_average_similarity * float(len(context.active_numeric_specs))
        numeric_support_score_weighted = round(numeric_support_score_weighted, 6)
        numeric_support_score_weighted_absolute = round(
            numeric_support_score_weighted * max(0.0, min(1.0, context.profile_numeric_confidence_factor)),
            6,
        )
        if numeric_support_score_mode == "raw":
            numeric_support_score_selected = numeric_support_score
        elif numeric_support_score_mode == "weighted":
            numeric_support_score_selected = numeric_support_score_weighted
        else:
            numeric_support_score_selected = numeric_support_score_weighted_absolute

        tracker.record_numeric_scores(
            numeric_pass_count,
            numeric_support_score,
            numeric_rule_hits_this_candidate,
            numeric_support_score_weighted=numeric_support_score_weighted,
            numeric_support_score_weighted_absolute=numeric_support_score_weighted_absolute,
            numeric_support_score_selected=numeric_support_score_selected,
            effective_semantic_min_keep_score=context.effective_semantic_min_keep_score,
            effective_numeric_support_min_score=context.effective_numeric_support_min_score,
        )

        kept, decision_path = keep_decision(
            is_seed_track,
            semantic_score,
            numeric_pass_count,
            context.numeric_features_enabled,
            context.effective_semantic_strong_keep_score,
            context.effective_semantic_min_keep_score,
            context.effective_numeric_support_min_pass,
            numeric_support_score=numeric_support_score_selected,
            numeric_support_min_score=context.effective_numeric_support_min_score,
            use_continuous_numeric=context.use_continuous_numeric,
            language_match=language_match,
            recency_pass=recency_pass,
        )

        decision_row = {
            "track_id": track_id,
            "is_seed_track": int(is_seed_track),
            "lead_genre": lead_genre,
            "semantic_score": round(semantic_score, 6),
            "lead_genre_similarity": round(lead_genre_match_score, 6),
            "genre_overlap_score": round(genre_overlap_fraction, 6),
            "tag_overlap_score": round(tag_overlap_fraction, 6),
            "lead_genre_match": int(lead_genre_match),
            "genre_overlap_count": genre_overlap,
            "tag_overlap_count": tag_overlap,
            "language": language_code or "",
            "language_match": "" if language_match is None else int(language_match),
            "release_year": "" if release_year is None else release_year,
            "release_year_distance": numeric_distances.get("release_year"),
            "numeric_pass_count": numeric_pass_count,
            "numeric_support_score": numeric_support_score,
            "numeric_support_score_weighted": numeric_support_score_weighted,
            "numeric_support_score_weighted_absolute": numeric_support_score_weighted_absolute,
            "numeric_support_score_selected": numeric_support_score_selected,
            "numeric_support_score_mode": numeric_support_score_mode,
            "numeric_confidence_weight_sum": round(weighted_support_denominator, 6),
            "profile_numeric_confidence_factor": round(context.profile_numeric_confidence_factor, 6),
            "effective_semantic_strong_keep_score": round(context.effective_semantic_strong_keep_score, 6),
            "effective_semantic_min_keep_score": round(context.effective_semantic_min_keep_score, 6),
            "effective_numeric_support_min_pass": context.effective_numeric_support_min_pass,
            "effective_numeric_support_min_score": round(context.effective_numeric_support_min_score, 6),
            "danceability_distance": numeric_distances.get("danceability"),
            "danceability_similarity": numeric_similarities.get("danceability", 0.0),
            "energy_distance": numeric_distances.get("energy"),
            "energy_similarity": numeric_similarities.get("energy", 0.0),
            "valence_distance": numeric_distances.get("valence"),
            "valence_similarity": numeric_similarities.get("valence", 0.0),
            "tempo_distance": numeric_distances.get("tempo"),
            "tempo_similarity": numeric_similarities.get("tempo", 0.0),
            "popularity_distance": numeric_distances.get("popularity"),
            "popularity_similarity": numeric_similarities.get("popularity", 0.0),
            "duration_ms_distance": numeric_distances.get("duration_ms"),
            "duration_ms_similarity": numeric_similarities.get("duration_ms", 0.0),
            "key_distance": numeric_distances.get("key"),
            "key_similarity": numeric_similarities.get("key", 0.0),
            "mode_distance": numeric_distances.get("mode"),
            "mode_similarity": numeric_similarities.get("mode", 0.0),
            "decision": "keep" if kept else "reject",
            "decision_path": decision_path,
            "decision_reason": decision_reason(
                decision_path,
                semantic_score,
                numeric_pass_count,
                numeric_support_score=numeric_support_score_selected,
                use_continuous_numeric=context.use_continuous_numeric,
            ),
        }

        tracker.record_decision(track_id, is_seed_track, kept, decision_path, decision_row, row if kept else None)

    summary = tracker.get_summary()
    return tracker, tracker.decisions, tracker.kept_rows, summary


def _sanitize_bl005_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["profile_top_lead_genre_limit"] = max(1, coerce_int(controls.get("profile_top_lead_genre_limit", 6), 6))
    controls["profile_top_tag_limit"] = max(1, coerce_int(controls.get("profile_top_tag_limit", 10), 10))
    controls["profile_top_genre_limit"] = max(1, coerce_int(controls.get("profile_top_genre_limit", 8), 8))
    controls["semantic_strong_keep_score"] = max(0, min(3, coerce_int(controls.get("semantic_strong_keep_score", 2), 2)))
    controls["semantic_min_keep_score"] = max(0, min(3, coerce_int(controls.get("semantic_min_keep_score", 1), 1)))
    controls["numeric_support_min_pass"] = max(0, coerce_int(controls.get("numeric_support_min_pass", 1), 1))
    controls["numeric_support_min_score"] = max(0.0, coerce_float(controls.get("numeric_support_min_score", 1.0), 1.0))
    controls["lead_genre_partial_match_threshold"] = max(0.0, min(1.0, coerce_float(controls.get("lead_genre_partial_match_threshold", 0.5), 0.5)))
    controls["use_weighted_semantics"] = bool(controls.get("use_weighted_semantics", False))
    controls["use_continuous_numeric"] = bool(controls.get("use_continuous_numeric", False))
    controls["enable_popularity_numeric"] = bool(controls.get("enable_popularity_numeric", False))

    codes = controls.get("language_filter_codes")
    normalized_codes: list[str] = []
    if isinstance(codes, list):
        seen: set[str] = set()
        for item in codes:
            code = str(item).strip().lower()
            if not code or code in seen:
                continue
            seen.add(code)
            normalized_codes.append(code)
    controls["language_filter_codes"] = normalized_codes
    controls["language_filter_enabled"] = bool(controls.get("language_filter_enabled", False)) and bool(normalized_codes)

    recency_raw = str(controls.get("recency_years_min_offset", "")).strip()
    if recency_raw:
        try:
            parsed = int(recency_raw)
            controls["recency_years_min_offset"] = parsed if parsed > 0 else None
        except ValueError:
            controls["recency_years_min_offset"] = None
    else:
        controls["recency_years_min_offset"] = None

    numeric_thresholds_raw = controls.get("numeric_thresholds")
    numeric_thresholds: dict[str, float] = {}
    if isinstance(numeric_thresholds_raw, dict):
        for key, value in numeric_thresholds_raw.items():
            try:
                parsed_val = float(value)
            except (TypeError, ValueError):
                continue
            if parsed_val > 0:
                numeric_thresholds[str(key)] = parsed_val
    controls["numeric_thresholds"] = numeric_thresholds

    controls["profile_quality_penalty_enabled"] = bool(controls.get("profile_quality_penalty_enabled", True))
    controls["profile_quality_threshold"] = max(0.0, min(1.0, coerce_float(controls.get("profile_quality_threshold", 0.90), 0.90)))
    controls["profile_entropy_low_threshold"] = max(0.0, min(1.0, coerce_float(controls.get("profile_entropy_low_threshold", 0.35), 0.35)))
    controls["influence_share_threshold"] = max(0.0, min(1.0, coerce_float(controls.get("influence_share_threshold", 0.60), 0.60)))
    controls["profile_quality_penalty_increment"] = max(0.0, coerce_float(controls.get("profile_quality_penalty_increment", 0.20), 0.20))
    controls["profile_entropy_penalty_increment"] = max(0.0, coerce_float(controls.get("profile_entropy_penalty_increment", 0.20), 0.20))
    controls["influence_share_penalty_increment"] = max(0.0, coerce_float(controls.get("influence_share_penalty_increment", 0.15), 0.15))
    controls["numeric_penalty_scale"] = max(0.0, coerce_float(controls.get("numeric_penalty_scale", 0.50), 0.50))
    controls["semantic_overlap_damping_mid_entropy_threshold"] = max(0.0, min(1.0, coerce_float(controls.get("semantic_overlap_damping_mid_entropy_threshold", 0.60), 0.60)))
    controls["semantic_overlap_damping_low_entropy"] = max(0.0, min(1.0, coerce_float(controls.get("semantic_overlap_damping_low_entropy", 0.85), 0.85)))
    controls["semantic_overlap_damping_mid_entropy"] = max(0.0, min(1.0, coerce_float(controls.get("semantic_overlap_damping_mid_entropy", 0.92), 0.92)))
    controls["enable_numeric_confidence_scaling"] = bool(controls.get("enable_numeric_confidence_scaling", True))
    controls["numeric_confidence_floor"] = max(0.0, min(1.0, coerce_float(controls.get("numeric_confidence_floor", 0.0), 0.0)))
    controls["profile_numeric_confidence_mode"] = coerce_enum(
        controls.get("profile_numeric_confidence_mode", "direct"),
        VALID_NUMERIC_CONFIDENCE_MODES,
        "direct",
    )
    controls["profile_numeric_confidence_blend_weight"] = max(0.0, min(1.0, coerce_float(controls.get("profile_numeric_confidence_blend_weight", 1.0), 1.0)))

    mode_raw = str(controls.get("numeric_support_score_mode", "weighted_absolute")).strip().lower()
    if mode_raw not in VALID_NUMERIC_SUPPORT_SCORE_MODES:
        raise RuntimeError(
            f"BL-005 numeric_support_score_mode must be one of {sorted(VALID_NUMERIC_SUPPORT_SCORE_MODES)}, got '{mode_raw}'"
        )
    controls["numeric_support_score_mode"] = mode_raw
    controls["emit_profile_policy_diagnostics"] = bool(controls.get("emit_profile_policy_diagnostics", True))
    return controls


def _load_bl005_controls_from_env() -> dict[str, object]:
    defaults = DEFAULT_RETRIEVAL_CONTROLS
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "signal_mode": {},
        "profile_top_lead_genre_limit": env_int("BL005_PROFILE_TOP_LEAD_GENRE_LIMIT", coerce_int(defaults["profile_top_lead_genre_limit"], 6)),
        "profile_top_tag_limit": env_int("BL005_PROFILE_TOP_TAG_LIMIT", coerce_int(defaults["profile_top_tag_limit"], 10)),
        "profile_top_genre_limit": env_int("BL005_PROFILE_TOP_GENRE_LIMIT", coerce_int(defaults["profile_top_genre_limit"], 8)),
        "semantic_strong_keep_score": env_int("BL005_SEMANTIC_STRONG_KEEP_SCORE", coerce_int(defaults["semantic_strong_keep_score"], 2)),
        "semantic_min_keep_score": env_int("BL005_SEMANTIC_MIN_KEEP_SCORE", coerce_int(defaults["semantic_min_keep_score"], 1)),
        "numeric_support_min_pass": env_int("BL005_NUMERIC_SUPPORT_MIN_PASS", coerce_int(defaults["numeric_support_min_pass"], 1)),
        "numeric_support_min_score": env_float("BL005_NUMERIC_SUPPORT_MIN_SCORE", coerce_float(defaults["numeric_support_min_score"], 1.0)),
        "lead_genre_partial_match_threshold": env_float("BL005_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD", coerce_float(defaults["lead_genre_partial_match_threshold"], 0.5)),
        "use_weighted_semantics": env_bool("BL005_USE_WEIGHTED_SEMANTICS", bool(defaults["use_weighted_semantics"])),
        "use_continuous_numeric": env_bool("BL005_USE_CONTINUOUS_NUMERIC", bool(defaults["use_continuous_numeric"])),
        "enable_popularity_numeric": env_bool("BL005_ENABLE_POPULARITY_NUMERIC", bool(defaults["enable_popularity_numeric"])),
        "language_filter_enabled": env_bool("BL005_LANGUAGE_FILTER_ENABLED", bool(defaults["language_filter_enabled"])),
        "language_filter_codes": [token.strip().lower() for token in env_str("BL005_LANGUAGE_FILTER_CODES", "").split(",") if token.strip()],
        "recency_years_min_offset": env_str("BL005_RECENCY_YEARS_MIN_OFFSET", ""),
        "numeric_thresholds": load_positive_numeric_map_from_env("BL005_NUMERIC_THRESHOLDS_JSON"),
        "profile_quality_penalty_enabled": env_bool("BL005_PROFILE_QUALITY_PENALTY_ENABLED", bool(defaults["profile_quality_penalty_enabled"])),
        "profile_quality_threshold": env_float("BL005_PROFILE_QUALITY_THRESHOLD", coerce_float(defaults["profile_quality_threshold"], 0.90)),
        "profile_entropy_low_threshold": env_float("BL005_PROFILE_ENTROPY_LOW_THRESHOLD", coerce_float(defaults["profile_entropy_low_threshold"], 0.35)),
        "influence_share_threshold": env_float("BL005_INFLUENCE_SHARE_THRESHOLD", coerce_float(defaults["influence_share_threshold"], 0.60)),
        "profile_quality_penalty_increment": env_float("BL005_PROFILE_QUALITY_PENALTY_INCREMENT", coerce_float(defaults["profile_quality_penalty_increment"], 0.20)),
        "profile_entropy_penalty_increment": env_float("BL005_PROFILE_ENTROPY_PENALTY_INCREMENT", coerce_float(defaults["profile_entropy_penalty_increment"], 0.20)),
        "influence_share_penalty_increment": env_float("BL005_INFLUENCE_SHARE_PENALTY_INCREMENT", coerce_float(defaults["influence_share_penalty_increment"], 0.15)),
        "numeric_penalty_scale": env_float("BL005_NUMERIC_PENALTY_SCALE", coerce_float(defaults["numeric_penalty_scale"], 0.50)),
        "semantic_overlap_damping_mid_entropy_threshold": env_float("BL005_SEMANTIC_DAMPING_MID_THRESHOLD", coerce_float(defaults["semantic_overlap_damping_mid_entropy_threshold"], 0.60)),
        "semantic_overlap_damping_low_entropy": env_float("BL005_SEMANTIC_DAMPING_LOW_ENTROPY", coerce_float(defaults["semantic_overlap_damping_low_entropy"], 0.85)),
        "semantic_overlap_damping_mid_entropy": env_float("BL005_SEMANTIC_DAMPING_MID_ENTROPY", coerce_float(defaults["semantic_overlap_damping_mid_entropy"], 0.92)),
        "enable_numeric_confidence_scaling": env_bool("BL005_ENABLE_NUMERIC_CONFIDENCE_SCALING", bool(defaults["enable_numeric_confidence_scaling"])),
        "numeric_confidence_floor": env_float("BL005_NUMERIC_CONFIDENCE_FLOOR", coerce_float(defaults["numeric_confidence_floor"], 0.0)),
        "profile_numeric_confidence_mode": env_str("BL005_PROFILE_NUMERIC_CONFIDENCE_MODE", str(defaults["profile_numeric_confidence_mode"])),
        "profile_numeric_confidence_blend_weight": env_float("BL005_PROFILE_NUMERIC_CONFIDENCE_BLEND_WEIGHT", coerce_float(defaults["profile_numeric_confidence_blend_weight"], 1.0)),
        "numeric_support_score_mode": env_str("BL005_NUMERIC_SUPPORT_SCORE_MODE", str(defaults["numeric_support_score_mode"])),
        "emit_profile_policy_diagnostics": env_bool("BL005_EMIT_PROFILE_POLICY_DIAGNOSTICS", bool(defaults["emit_profile_policy_diagnostics"])),
    }


def _resolve_bl005_runtime_controls_payload() -> dict[str, object]:
    return resolve_stage_controls(
        load_from_env=_load_bl005_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_RETRIEVAL_CONTROLS),
        sanitize=_sanitize_bl005_controls,
    )


def resolve_bl005_runtime_controls() -> RetrievalControls:
    payload = _resolve_bl005_runtime_controls_payload()
    return RetrievalControls(
        config_source=str(payload.get("config_source") or "environment"),
        run_config_path=(str(payload["run_config_path"]) if payload.get("run_config_path") else None),
        run_config_schema_version=(str(payload["run_config_schema_version"]) if payload.get("run_config_schema_version") else None),
        signal_mode={str(k): v for k, v in _mapping(payload.get("signal_mode")).items()},
        profile_top_lead_genre_limit=_safe_int(payload.get("profile_top_lead_genre_limit"), 6),
        profile_top_tag_limit=_safe_int(payload.get("profile_top_tag_limit"), 10),
        profile_top_genre_limit=_safe_int(payload.get("profile_top_genre_limit"), 8),
        semantic_strong_keep_score=_safe_int(payload.get("semantic_strong_keep_score"), 2),
        semantic_min_keep_score=_safe_int(payload.get("semantic_min_keep_score"), 1),
        numeric_support_min_pass=_safe_int(payload.get("numeric_support_min_pass"), 1),
        numeric_support_min_score=_safe_float(payload.get("numeric_support_min_score"), 1.0),
        lead_genre_partial_match_threshold=_safe_float(payload.get("lead_genre_partial_match_threshold"), 0.5),
        use_weighted_semantics=bool(payload.get("use_weighted_semantics", False)),
        use_continuous_numeric=bool(payload.get("use_continuous_numeric", False)),
        enable_popularity_numeric=bool(payload.get("enable_popularity_numeric", False)),
        language_filter_enabled=bool(payload.get("language_filter_enabled", False)),
        language_filter_codes=_string_list(payload.get("language_filter_codes")),
        recency_years_min_offset=(
            _safe_int(payload["recency_years_min_offset"]) if payload.get("recency_years_min_offset") is not None else None
        ),
        numeric_thresholds={str(k): _safe_float(v) for k, v in _mapping(payload.get("numeric_thresholds")).items()},
        profile_quality_penalty_enabled=bool(payload.get("profile_quality_penalty_enabled", True)),
        profile_quality_threshold=_safe_float(payload.get("profile_quality_threshold"), 0.90),
        profile_entropy_low_threshold=_safe_float(payload.get("profile_entropy_low_threshold"), 0.35),
        influence_share_threshold=_safe_float(payload.get("influence_share_threshold"), 0.60),
        profile_quality_penalty_increment=_safe_float(payload.get("profile_quality_penalty_increment"), 0.20),
        profile_entropy_penalty_increment=_safe_float(payload.get("profile_entropy_penalty_increment"), 0.20),
        influence_share_penalty_increment=_safe_float(payload.get("influence_share_penalty_increment"), 0.15),
        numeric_penalty_scale=_safe_float(payload.get("numeric_penalty_scale"), 0.50),
        semantic_overlap_damping_mid_entropy_threshold=_safe_float(payload.get("semantic_overlap_damping_mid_entropy_threshold"), 0.60),
        semantic_overlap_damping_low_entropy=_safe_float(payload.get("semantic_overlap_damping_low_entropy"), 0.85),
        semantic_overlap_damping_mid_entropy=_safe_float(payload.get("semantic_overlap_damping_mid_entropy"), 0.92),
        enable_numeric_confidence_scaling=bool(payload.get("enable_numeric_confidence_scaling", True)),
        numeric_confidence_floor=_safe_float(payload.get("numeric_confidence_floor"), 0.0),
        profile_numeric_confidence_mode=str(payload.get("profile_numeric_confidence_mode") or "direct"),
        profile_numeric_confidence_blend_weight=_safe_float(payload.get("profile_numeric_confidence_blend_weight"), 1.0),
        numeric_support_score_mode=_validate_numeric_support_score_mode(payload.get("numeric_support_score_mode", "weighted_absolute")),
        emit_profile_policy_diagnostics=bool(payload.get("emit_profile_policy_diagnostics", True)),
    )


def context_from_mapping(payload: Mapping[str, Any]) -> RetrievalContext:
    required_keys = [
        "signal_mode",
        "profile_top_lead_genre_limit",
        "profile_top_tag_limit",
        "profile_top_genre_limit",
        "semantic_strong_keep_score",
        "semantic_min_keep_score",
        "numeric_support_min_pass",
        "numeric_support_min_score",
        "lead_genre_partial_match_threshold",
        "active_numeric_specs",
        "seed_track_ids",
        "top_lead_genres",
        "top_tags",
        "top_genres",
        "lead_genre_weights",
        "tag_weights",
        "genre_weights",
        "numeric_centers",
        "numeric_features_enabled",
        "use_weighted_semantics",
        "use_continuous_numeric",
        "language_filter_enabled",
        "language_filter_codes",
        "feature_confidence_by_name",
        "profile_numeric_confidence_factor",
        "profile_match_quality",
        "top_genre_entropy",
        "top_tag_entropy",
        "history_weight_share",
        "influence_weight_share",
        "effective_semantic_strong_keep_score",
        "effective_semantic_min_keep_score",
        "effective_numeric_support_min_pass",
        "effective_numeric_support_min_score",
        "semantic_overlap_damping",
        "numeric_support_score_mode",
    ]
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"BL-005 runtime context mapping is missing required field(s): {', '.join(sorted(missing))}")

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
        signal_mode={str(k): v for k, v in dict(payload.get("signal_mode") or {}).items()},
        profile_top_lead_genre_limit=int(payload["profile_top_lead_genre_limit"]),
        profile_top_tag_limit=int(payload["profile_top_tag_limit"]),
        profile_top_genre_limit=int(payload["profile_top_genre_limit"]),
        semantic_strong_keep_score=int(payload["semantic_strong_keep_score"]),
        semantic_min_keep_score=int(payload["semantic_min_keep_score"]),
        numeric_support_min_pass=int(payload["numeric_support_min_pass"]),
        numeric_support_min_score=float(payload["numeric_support_min_score"]),
        lead_genre_partial_match_threshold=float(payload["lead_genre_partial_match_threshold"]),
        active_numeric_specs=active_specs,
        seed_track_ids={str(v) for v in set(payload["seed_track_ids"] or set())},
        top_lead_genres={str(v) for v in set(payload["top_lead_genres"] or set())},
        top_tags={str(v) for v in set(payload["top_tags"] or set())},
        top_genres={str(v) for v in set(payload["top_genres"] or set())},
        lead_genre_weights={str(k): float(v) for k, v in dict(payload["lead_genre_weights"] or {}).items()},
        tag_weights={str(k): float(v) for k, v in dict(payload["tag_weights"] or {}).items()},
        genre_weights={str(k): float(v) for k, v in dict(payload["genre_weights"] or {}).items()},
        numeric_centers={str(k): float(v) for k, v in dict(payload["numeric_centers"] or {}).items()},
        numeric_features_enabled=bool(payload["numeric_features_enabled"]),
        use_weighted_semantics=bool(payload["use_weighted_semantics"]),
        use_continuous_numeric=bool(payload["use_continuous_numeric"]),
        language_filter_enabled=bool(payload["language_filter_enabled"]),
        language_filter_codes=[str(v) for v in list(payload["language_filter_codes"] or []) if str(v)],
        recency_years_min_offset=(int(payload["recency_years_min_offset"]) if payload.get("recency_years_min_offset") is not None else None),
        current_year_utc=int(payload.get("current_year_utc", 0)),
        recency_min_release_year=(int(payload["recency_min_release_year"]) if payload.get("recency_min_release_year") is not None else None),
        feature_confidence_by_name={str(k): float(v) for k, v in dict(payload["feature_confidence_by_name"] or {}).items()},
        profile_numeric_confidence_factor=float(payload["profile_numeric_confidence_factor"]),
        profile_match_quality=float(payload["profile_match_quality"]),
        top_genre_entropy=float(payload["top_genre_entropy"]),
        top_tag_entropy=float(payload["top_tag_entropy"]),
        history_weight_share=float(payload["history_weight_share"]),
        influence_weight_share=float(payload["influence_weight_share"]),
        effective_semantic_strong_keep_score=float(payload["effective_semantic_strong_keep_score"]),
        effective_semantic_min_keep_score=float(payload["effective_semantic_min_keep_score"]),
        effective_numeric_support_min_pass=int(payload["effective_numeric_support_min_pass"]),
        effective_numeric_support_min_score=float(payload["effective_numeric_support_min_score"]),
        semantic_overlap_damping=float(payload["semantic_overlap_damping"]),
        profile_quality_penalty_enabled=bool(payload.get("profile_quality_penalty_enabled", True)),
        profile_quality_threshold=float(payload.get("profile_quality_threshold", 0.90)),
        profile_entropy_low_threshold=float(payload.get("profile_entropy_low_threshold", 0.35)),
        influence_share_threshold=float(payload.get("influence_share_threshold", 0.60)),
        profile_quality_penalty_increment=float(payload.get("profile_quality_penalty_increment", 0.20)),
        profile_entropy_penalty_increment=float(payload.get("profile_entropy_penalty_increment", 0.20)),
        influence_share_penalty_increment=float(payload.get("influence_share_penalty_increment", 0.15)),
        numeric_penalty_scale=float(payload.get("numeric_penalty_scale", 0.50)),
        semantic_overlap_damping_mid_entropy_threshold=float(payload.get("semantic_overlap_damping_mid_entropy_threshold", 0.60)),
        semantic_overlap_damping_low_entropy=float(payload.get("semantic_overlap_damping_low_entropy", 0.85)),
        semantic_overlap_damping_mid_entropy=float(payload.get("semantic_overlap_damping_mid_entropy", 0.92)),
        enable_numeric_confidence_scaling=bool(payload.get("enable_numeric_confidence_scaling", True)),
        numeric_confidence_floor=float(payload.get("numeric_confidence_floor", 0.0)),
        profile_numeric_confidence_mode=str(payload.get("profile_numeric_confidence_mode", "direct")),
        profile_numeric_confidence_blend_weight=float(payload.get("profile_numeric_confidence_blend_weight", 1.0)),
        numeric_support_score_mode=_validate_numeric_support_score_mode(payload["numeric_support_score_mode"]),
        effective_threshold_penalty=float(payload.get("effective_threshold_penalty", 0.0)),
        emit_profile_policy_diagnostics=bool(payload.get("emit_profile_policy_diagnostics", True)),
    )


def resolve_bl005_paths(root: Path) -> RetrievalPaths:
    return RetrievalStage(root=root).resolve_paths()


def _validate_candidate_schema(candidate_rows_raw: list[dict[str, object]]) -> None:
    first_row = candidate_rows_raw[0] if candidate_rows_raw else {}
    candidate_columns = {str(key) for key in first_row.keys()}
    missing = sorted(REQUIRED_CANDIDATE_COLUMNS - candidate_columns)
    if missing:
        raise RuntimeError(f"BL-005 candidate corpus is missing required column(s): {', '.join(missing)}")
    if candidate_columns.isdisjoint(CANDIDATE_ID_COLUMN_ALIASES):
        aliases = ", ".join(sorted(CANDIDATE_ID_COLUMN_ALIASES))
        raise RuntimeError(f"BL-005 candidate corpus must include one identifier column: {aliases}")
    if "duration_ms" not in candidate_columns and "duration" not in candidate_columns:
        raise RuntimeError("BL-005 candidate corpus must include either duration_ms or duration column")


def load_bl005_inputs(paths: RetrievalPaths) -> RetrievalInputs:
    return RetrievalStage.load_inputs(paths)


def build_bl005_runtime_context(
    *,
    profile: dict[str, object],
    candidate_rows: list[dict[str, str]],
    seed_trace_rows: list[dict[str, str]],
    runtime_controls: RetrievalControls,
) -> RetrievalContext:
    inputs = RetrievalInputs(profile=profile, candidate_rows=candidate_rows, seed_trace_rows=seed_trace_rows)
    return RetrievalStage.build_runtime_context(inputs=inputs, controls=runtime_controls)


class RetrievalStage:
    """Object-oriented BL-005 workflow shell over single-file helpers."""

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
        return resolve_bl005_runtime_controls()

    @staticmethod
    def load_inputs(paths: RetrievalPaths) -> RetrievalInputs:
        profile = load_json(paths.profile_path)
        if not isinstance(profile, dict):
            raise RuntimeError("BL-005 profile artifact is malformed; expected JSON object")
        candidate_rows_raw = load_csv_rows(paths.candidate_path)
        if not candidate_rows_raw:
            raise RuntimeError("BL-005 candidate corpus is empty; cannot build retrieval outputs")
        _validate_candidate_schema(candidate_rows_raw)
        candidate_rows = [normalize_candidate_row(row) for row in candidate_rows_raw]
        seed_trace_rows = load_csv_rows(paths.seed_trace_path)
        return RetrievalInputs(profile=profile, candidate_rows=candidate_rows, seed_trace_rows=seed_trace_rows)

    @staticmethod
    def build_runtime_context(*, inputs: RetrievalInputs, controls: RetrievalControls) -> RetrievalContext:
        effective_numeric_specs = {
            key: NumericFeatureSpec(
                candidate_column=str(spec["candidate_column"]),
                threshold=safe_float(controls.numeric_thresholds.get(key, spec["threshold"]), 0.0),
                circular=bool(spec["circular"]),
            )
            for key, spec in SHARED_NUMERIC_FEATURE_SPECS.items()
            if controls.enable_popularity_numeric or key != "popularity"
        }

        seed_track_ids = {str(row["track_id"]) for row in inputs.seed_trace_rows}
        candidate_columns = set(inputs.candidate_rows[0].keys()) if inputs.candidate_rows else set()
        top_lead_genres = build_profile_label_set(inputs.profile, "top_lead_genres", controls.profile_top_lead_genre_limit)
        lead_genre_weights = build_profile_weight_map(inputs.profile, "top_lead_genres", controls.profile_top_lead_genre_limit)
        top_tags = build_profile_label_set(inputs.profile, "top_tags", controls.profile_top_tag_limit)
        tag_weights = build_profile_weight_map(inputs.profile, "top_tags", controls.profile_top_tag_limit)
        top_genres = build_profile_label_set(inputs.profile, "top_genres", controls.profile_top_genre_limit)
        genre_weights = build_profile_weight_map(inputs.profile, "top_genres", controls.profile_top_genre_limit)
        active_numeric_specs = build_active_numeric_specs(inputs.profile, effective_numeric_specs, candidate_columns)

        if controls.enable_popularity_numeric and "popularity" not in candidate_columns:
            raise RuntimeError("BL-005 popularity numeric mode enabled but candidate corpus is missing popularity column")

        numeric_feature_profile_obj = inputs.profile.get("numeric_feature_profile")
        numeric_feature_profile: dict[str, Any] = numeric_feature_profile_obj if isinstance(numeric_feature_profile_obj, dict) else {}
        numeric_centers = {
            profile_column: float(str(numeric_feature_profile[profile_column]))
            for profile_column in active_numeric_specs
            if profile_column in numeric_feature_profile and numeric_feature_profile[profile_column] is not None
        }
        numeric_features_enabled = bool(numeric_centers)

        numeric_confidence_obj = inputs.profile.get("numeric_confidence")
        numeric_confidence = numeric_confidence_obj if isinstance(numeric_confidence_obj, dict) else {}
        confidence_by_feature_obj = numeric_confidence.get("confidence_by_feature")
        confidence_by_feature = confidence_by_feature_obj if isinstance(confidence_by_feature_obj, dict) else {}
        feature_confidence_by_name = {
            feature: _clamp_0_1(_safe_float(confidence_by_feature.get(feature), 1.0))
            for feature in active_numeric_specs
        }
        profile_numeric_confidence_factor_base = 1.0
        if feature_confidence_by_name:
            profile_numeric_confidence_factor_base = sum(feature_confidence_by_name.values()) / float(len(feature_confidence_by_name))

        if controls.enable_numeric_confidence_scaling:
            numeric_confidence_floor = _clamp_0_1(controls.numeric_confidence_floor)
            feature_confidence_by_name = {key: max(numeric_confidence_floor, value) for key, value in feature_confidence_by_name.items()}
        else:
            numeric_confidence_floor = 0.0
            feature_confidence_by_name = {key: 1.0 for key in feature_confidence_by_name}

        if controls.profile_numeric_confidence_mode == "blended":
            blend_weight = _clamp_0_1(controls.profile_numeric_confidence_blend_weight)
            profile_numeric_confidence_factor = (blend_weight * profile_numeric_confidence_factor_base) + ((1.0 - blend_weight) * 1.0)
        elif controls.enable_numeric_confidence_scaling:
            profile_numeric_confidence_factor = profile_numeric_confidence_factor_base
        else:
            profile_numeric_confidence_factor = 1.0

        signal_vector = inputs.profile.get("profile_signal_vector") if isinstance(inputs.profile.get("profile_signal_vector"), dict) else {}
        bl003_quality = inputs.profile.get("bl003_quality") if isinstance(inputs.profile.get("bl003_quality"), dict) else {}
        profile_match_quality = _clamp_0_1(_safe_float(signal_vector.get("alignment_match_rate", bl003_quality.get("match_rate", 1.0)), 1.0))
        top_genre_entropy = _clamp_0_1(_safe_float(signal_vector.get("top_genre_entropy"), 0.0))
        top_tag_entropy = _clamp_0_1(_safe_float(signal_vector.get("top_tag_entropy"), 0.0))
        history_weight_share = _clamp_0_1(_safe_float(signal_vector.get("history_weight_share"), 1.0))
        influence_weight_share = _clamp_0_1(_safe_float(signal_vector.get("influence_weight_share"), 0.0))
        average_entropy = (top_genre_entropy + top_tag_entropy) / 2.0

        threshold_penalty = 0.0
        if controls.profile_quality_penalty_enabled:
            if profile_match_quality < controls.profile_quality_threshold:
                threshold_penalty += controls.profile_quality_penalty_increment
            if average_entropy < controls.profile_entropy_low_threshold:
                threshold_penalty += controls.profile_entropy_penalty_increment
            if influence_weight_share > controls.influence_share_threshold:
                threshold_penalty += controls.influence_share_penalty_increment
        threshold_penalty = min(1.0, threshold_penalty)

        effective_semantic_min_keep_score = min(3.0, float(controls.semantic_min_keep_score) + threshold_penalty)
        effective_semantic_strong_keep_score = min(3.0, max(effective_semantic_min_keep_score, float(controls.semantic_strong_keep_score) + threshold_penalty))
        effective_numeric_support_min_pass = max(0, int(round(float(controls.numeric_support_min_pass) * (1.0 + (threshold_penalty * controls.numeric_penalty_scale)))))
        effective_numeric_support_min_score = max(0.0, float(controls.numeric_support_min_score) * (1.0 + (threshold_penalty * controls.numeric_penalty_scale)))

        semantic_overlap_damping = 1.0
        if average_entropy < controls.profile_entropy_low_threshold:
            semantic_overlap_damping = controls.semantic_overlap_damping_low_entropy
        elif average_entropy < controls.semantic_overlap_damping_mid_entropy_threshold:
            semantic_overlap_damping = controls.semantic_overlap_damping_mid_entropy

        language_filter_codes = sorted({code for code in controls.language_filter_codes if code})
        current_year_utc = datetime.now(timezone.utc).year
        recency_min_release_year = current_year_utc - controls.recency_years_min_offset if controls.recency_years_min_offset is not None else None

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
            numeric_support_score_mode=_validate_numeric_support_score_mode(controls.numeric_support_score_mode),
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

        return {"filtered_path": filtered_path, "decisions_path": decisions_path}

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
        decision_counts = summary.get("decision_counts") if isinstance(summary.get("decision_counts"), dict) else {}
        decision_path_counts = summary.get("decision_path_counts") if isinstance(summary.get("decision_path_counts"), dict) else {}
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
                "numeric_thresholds": {profile_column: spec.threshold for profile_column, spec in runtime_context.active_numeric_specs.items()},
                "numeric_support_min_score": runtime_context.numeric_support_min_score,
                "effective_thresholds": {
                    "semantic_strong_keep_score": round(runtime_context.effective_semantic_strong_keep_score, 6),
                    "semantic_min_keep_score": round(runtime_context.effective_semantic_min_keep_score, 6),
                    "numeric_support_min_pass": runtime_context.effective_numeric_support_min_pass,
                    "numeric_support_min_score": round(runtime_context.effective_numeric_support_min_score, 6),
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
                "numeric_feature_mapping": {profile_column: spec.candidate_column for profile_column, spec in runtime_context.active_numeric_specs.items()},
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
                    "profile_numeric_confidence_factor": round(runtime_context.profile_numeric_confidence_factor, 6),
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
                    "profile_numeric_confidence_blend_weight": round(runtime_context.profile_numeric_confidence_blend_weight, 6),
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
                "numeric_support_score_weighted_absolute": summary.get("numeric_support_score_weighted_absolute_distribution", {}),
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
        diagnostics["diagnostics_hash_note"] = "diagnostics file does not store its own hash to avoid recursive self-reference"
        with open_text_write(diagnostics_path) as handle:
            json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    @staticmethod
    def write_run_store(
        *,
        paths: RetrievalPaths,
        run_id: str,
        diagnostics: dict[str, object],
        diagnostics_path: Path,
        output_paths: dict[str, Path],
        decisions: list[dict[str, object]],
    ) -> Path:
        pipeline_run_id = (os.getenv("BL_PIPELINE_RUN_ID") or "").strip()
        store_run_id = pipeline_run_id or run_id
        run_store_path = resolve_run_store_path(impl_root(), store_run_id)
        generated_at_utc = str(diagnostics.get("generated_at_utc") or utc_now())

        with SQLiteRunStore(run_store_path) as run_store:
            run_store.upsert_run(
                run_id=store_run_id,
                created_at_utc=generated_at_utc,
                source_stage_id="BL-005",
            )
            stage_run_pk = run_store.insert_stage_run(
                run_id=store_run_id,
                stage_id="BL-005",
                stage_run_ref=run_id,
                generated_at_utc=generated_at_utc,
                status="pass",
                summary=diagnostics,
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="filtered_candidates",
                artifact_type="csv",
                artifact_path=str(output_paths["filtered_path"]),
                sha256=sha256_of_file(output_paths["filtered_path"]),
                rows=[{str(k): v for k, v in row.items()} for row in load_csv_rows(output_paths["filtered_path"])],
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="candidate_decisions",
                artifact_type="csv",
                artifact_path=str(output_paths["decisions_path"]),
                sha256=sha256_of_file(output_paths["decisions_path"]),
                rows=decisions,
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="diagnostics",
                artifact_type="json",
                artifact_path=str(diagnostics_path),
                sha256=sha256_of_file(diagnostics_path),
                payload=diagnostics,
            )

        return run_store_path

    def run(self) -> RetrievalArtifacts:
        paths = self.resolve_paths()
        paths.output_dir.mkdir(parents=True, exist_ok=True)
        ensure_paths_exist([paths.profile_path, paths.seed_trace_path, paths.candidate_path], stage_label="BL-005")

        controls = self.resolve_runtime_controls()
        inputs = self.load_inputs(paths)
        context = self.build_runtime_context(inputs=inputs, controls=controls)

        start_time = time.time()
        run_id = f"BL005-FILTER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        _, decisions, kept_rows, summary = evaluate_bl005_candidates(candidate_rows=inputs.candidate_rows, runtime_context=context)

        output_paths = self.write_output_artifacts(output_dir=paths.output_dir, candidate_rows=inputs.candidate_rows, decisions=decisions, kept_rows=kept_rows)
        elapsed_seconds = time.time() - start_time
        diagnostics = self.build_diagnostics_payload(
            run_id=run_id,
            elapsed_seconds=elapsed_seconds,
            paths=paths,
            runtime_context=context,
            summary=summary,
            candidate_rows=inputs.candidate_rows,
            kept_rows=kept_rows,
            output_paths=output_paths,
        )
        diagnostics_path = paths.output_dir / "bl005_candidate_diagnostics.json"
        self.write_diagnostics_with_hashes(diagnostics=diagnostics, diagnostics_path=diagnostics_path, output_paths=output_paths)
        run_store_path = self.write_run_store(
            paths=paths,
            run_id=run_id,
            diagnostics=diagnostics,
            diagnostics_path=diagnostics_path,
            output_paths=output_paths,
            decisions=decisions,
        )
        diagnostics["output_files"] = {
            **{str(key): value for key, value in _mapping(diagnostics.get("output_files")).items()},
            "sqlite_run_store": str(run_store_path),
        }
        self.write_diagnostics_with_hashes(diagnostics=diagnostics, diagnostics_path=diagnostics_path, output_paths=output_paths)

        logger.info("BL-005 candidate filtering complete.")
        logger.info("filtered_candidates=%s", output_paths["filtered_path"])
        logger.info("decisions=%s", output_paths["decisions_path"])
        logger.info("diagnostics=%s", diagnostics_path)

        decision_counts = summary.get("decision_counts") if isinstance(summary.get("decision_counts"), dict) else {}
        return RetrievalArtifacts(
            filtered_path=output_paths["filtered_path"],
            decisions_path=output_paths["decisions_path"],
            diagnostics_path=diagnostics_path,
            kept_candidates_count=len(kept_rows),
            rejected_candidates_count=int(decision_counts.get("rejected_threshold", 0)),
            seed_excluded_count=int(decision_counts.get("seed_excluded", 0)),
            elapsed_seconds=round(elapsed_seconds, 3),
        )


def main() -> None:
    RetrievalStage().run()


if __name__ == "__main__":
    main()
