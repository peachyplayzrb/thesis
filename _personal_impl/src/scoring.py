"""BL-006: Score candidates based on profile preference model."""

from __future__ import annotations

import csv
import json
import logging
import os
import statistics
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from run_config.stage_control_resolution import defaults_loader, resolve_stage_controls
from run_config.run_config_utils import (
    DEFAULT_SCORING_COMPONENT_WEIGHTS as RUN_CONFIG_DEFAULT_SCORING_COMPONENT_WEIGHTS,
    DEFAULT_SCORING_CONTROLS as RUN_CONFIG_DEFAULT_SCORING_CONTROLS,
)
from shared.io_utils import (
    load_csv_rows,
    load_json,
    open_text_write,
    sha256_of_file,
    utc_now,
)
from shared.path_utils import impl_root
from shared.run_store import SQLiteRunStore, resolve_run_store_path
from shared.env_utils import env_bool, env_float, env_str
from shared.coerce_utils import coerce_dict, coerce_enum, coerce_float, safe_float, safe_int

DEFAULT_SCORING_COMPONENT_WEIGHTS = deepcopy(RUN_CONFIG_DEFAULT_SCORING_COMPONENT_WEIGHTS)
DEFAULT_SCORING_CONTROLS: dict[str, object] = {
    **deepcopy(RUN_CONFIG_DEFAULT_SCORING_CONTROLS),
    "signal_mode": {},
    "component_weights": dict(DEFAULT_SCORING_COMPONENT_WEIGHTS),
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
VALID_LEAD_GENRE_STRATEGIES: frozenset[str] = frozenset({"single_anchor", "weighted_top_lead_genres"})
VALID_NUMERIC_CONFIDENCE_MODES: frozenset[str] = frozenset({"direct", "blended"})
VALID_SEMANTIC_ALPHA_MODES: frozenset[str] = frozenset({"profile_adaptive", "fixed"})
VALID_SEMANTIC_OVERLAP_STRATEGIES: frozenset[str] = frozenset({"overlap_only", "precision_aware"})


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


def parse_float(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


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


def build_numeric_specs() -> dict[str, dict[str, object]]:
    return {
        dimension: {
            "threshold": float(spec["threshold"]),
            "circular": bool(spec["circular"]),
        }
        for dimension, spec in SHARED_NUMERIC_FEATURE_SPECS.items()
    }


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
    "popularity_similarity",
    "popularity_contribution",
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


@dataclass(frozen=True)
class ScoringPaths:
    profile_path: Path
    filtered_candidates_path: Path
    output_dir: Path
    bl003_summary_path: Path | None = None


@dataclass(frozen=True)
class ScoringControls:
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    signal_mode: dict[str, object]
    component_weights: dict[str, float]
    numeric_thresholds: dict[str, float]
    lead_genre_strategy: str = "weighted_top_lead_genres"
    semantic_overlap_strategy: str = "precision_aware"
    semantic_precision_alpha_mode: str = "profile_adaptive"
    semantic_precision_alpha_fixed: float = 0.35
    enable_numeric_confidence_scaling: bool = True
    numeric_confidence_floor: float = 0.0
    profile_numeric_confidence_mode: str = "direct"
    profile_numeric_confidence_blend_weight: float = 1.0
    emit_confidence_impact_diagnostics: bool = True
    emit_semantic_precision_diagnostics: bool = False
    apply_bl003_influence_tracks: bool = False
    influence_track_bonus_scale: float = 0.0
    spread_warn_threshold: float = 0.15


@dataclass(frozen=True)
class ScoringInputs:
    profile: dict[str, object]
    bl003_summary: dict[str, object]
    candidates: list[dict[str, str]]


@dataclass(frozen=True)
class ScoringContext:
    signal_mode: dict[str, object]
    effective_component_weights: dict[str, float]
    active_numeric_specs: dict[str, dict[str, object]]
    profile_scoring_data: dict[str, object]
    active_component_weights: dict[str, float]
    weight_rebalance_diagnostics: dict[str, object]
    numeric_confidence_by_feature: dict[str, float]
    profile_numeric_confidence_factor: float
    semantic_precision_alpha: float
    lead_genre_strategy: str = "weighted_top_lead_genres"
    semantic_overlap_strategy: str = "precision_aware"
    semantic_precision_alpha_mode: str = "profile_adaptive"
    semantic_precision_alpha_fixed: float = 0.35
    enable_numeric_confidence_scaling: bool = True
    numeric_confidence_floor: float = 0.0
    profile_numeric_confidence_mode: str = "direct"
    profile_numeric_confidence_blend_weight: float = 1.0
    emit_confidence_impact_diagnostics: bool = True
    emit_semantic_precision_diagnostics: bool = False
    apply_bl003_influence_tracks: bool = False
    influence_track_ids: set[str] | None = None
    influence_preference_weight: float = 0.0
    influence_track_bonus_scale: float = 0.0
    spread_warn_threshold: float = 0.15


@dataclass(frozen=True)
class ScoringArtifacts:
    scored_path: Path
    diagnostics_path: Path
    summary_path: Path


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _clamp_0_1(value: float) -> float:
    return max(0.0, min(1.0, value))


def _build_weight_map(items: list[dict[str, Any]]) -> dict[str, float]:
    labels: list[str] = []
    weighted_entries: list[tuple[str, float]] = []
    for item in items:
        label = item.get("label")
        if not isinstance(label, str) or not label:
            continue
        labels.append(label)
        raw_weight = item.get("weight")
        if isinstance(raw_weight, (int, float)) and float(raw_weight) > 0:
            weighted_entries.append((label, float(raw_weight)))

    if weighted_entries:
        total = sum(weight for _, weight in weighted_entries)
        if total > 0:
            return {label: round(weight / total, 6) for label, weight in weighted_entries}

    if not labels:
        return {}
    uniform_weight = round(1.0 / len(labels), 6)
    return {label: uniform_weight for label in labels}


def parse_candidate_attributes(row: dict[str, str]) -> dict[str, object]:
    track_id = (row.get("track_id") or row.get("id") or "").strip()
    genres = parse_csv_labels(row.get("genres", ""))
    tags = parse_csv_labels(row.get("tags", ""))
    lead_genre = genres[0] if genres else (tags[0] if tags else "")
    return {
        "track_id": track_id,
        "danceability": parse_float(row.get("danceability", "")),
        "energy": parse_float(row.get("energy", "")),
        "valence": parse_float(row.get("valence", "")),
        "tempo": parse_float(row.get("tempo", "")),
        "duration_ms": parse_float(row.get("duration_ms", "")),
        "popularity": parse_float(row.get("popularity", "")),
        "key": parse_float(row.get("key", "")),
        "mode": parse_float(row.get("mode", "")),
        "genres": genres,
        "tags": tags,
        "lead_genre": lead_genre,
    }


def _validate_profile_contract(profile: Mapping[str, object]) -> None:
    numeric_feature_profile = profile.get("numeric_feature_profile")
    semantic_profile = profile.get("semantic_profile")
    if not isinstance(numeric_feature_profile, Mapping):
        raise RuntimeError("BL-006 profile is missing numeric_feature_profile object")
    if not isinstance(semantic_profile, Mapping):
        raise RuntimeError("BL-006 profile is missing semantic_profile object")
    for key in ["top_lead_genres", "top_genres", "top_tags"]:
        value = semantic_profile.get(key)
        if not isinstance(value, list):
            raise RuntimeError(f"BL-006 profile semantic_profile.{key} must be a list")


def extract_profile_scoring_data(
    profile: dict[str, Any],
    numeric_specs: dict[str, dict[str, Any]],
) -> dict[str, object]:
    _validate_profile_contract(profile)

    scoring_data: dict[str, object] = {}
    numeric_profile_obj = profile.get("numeric_feature_profile")
    numeric_profile = numeric_profile_obj if isinstance(numeric_profile_obj, dict) else {}
    numeric_centers: dict[str, float] = {}
    numeric_thresholds: dict[str, float] = {}
    for dimension, spec in numeric_specs.items():
        if dimension in numeric_profile:
            numeric_centers[dimension] = float(numeric_profile[dimension])
            numeric_thresholds[dimension] = float(spec.get("threshold", 1.0))

    scoring_data["numeric_centers"] = numeric_centers
    scoring_data["numeric_thresholds"] = numeric_thresholds

    numeric_confidence_payload = profile.get("numeric_confidence", {})
    confidence_by_feature_raw = (
        numeric_confidence_payload.get("confidence_by_feature", {})
        if isinstance(numeric_confidence_payload, dict)
        else {}
    )
    numeric_confidence_by_feature: dict[str, float] = {}
    if isinstance(confidence_by_feature_raw, dict):
        for name, raw_value in confidence_by_feature_raw.items():
            numeric_confidence_by_feature[str(name)] = round(_clamp_0_1(float(raw_value)), 6)
    for dimension in numeric_specs:
        numeric_confidence_by_feature.setdefault(dimension, 1.0)
    scoring_data["numeric_confidence_by_feature"] = numeric_confidence_by_feature

    if numeric_centers:
        active_confidence_values = [numeric_confidence_by_feature.get(dimension, 1.0) for dimension in numeric_centers]
        scoring_data["profile_numeric_confidence_factor"] = round(
            sum(active_confidence_values) / float(len(active_confidence_values)),
            6,
        )
    else:
        scoring_data["profile_numeric_confidence_factor"] = 1.0

    semantic_profile_obj = profile.get("semantic_profile")
    semantic_profile = semantic_profile_obj if isinstance(semantic_profile_obj, dict) else {}
    top_lead_genres_raw = semantic_profile.get("top_lead_genres", [])
    top_genres_raw = semantic_profile.get("top_genres", [])
    top_tags_raw = semantic_profile.get("top_tags", [])
    top_lead_genres = top_lead_genres_raw if isinstance(top_lead_genres_raw, list) else []
    top_genres = top_genres_raw if isinstance(top_genres_raw, list) else []
    top_tags = top_tags_raw if isinstance(top_tags_raw, list) else []

    lead_genre = top_lead_genres[0]["label"] if top_lead_genres and isinstance(top_lead_genres[0], dict) else ""
    scoring_data["lead_genre"] = lead_genre
    scoring_data["lead_genre_weights"] = _build_weight_map([item for item in top_lead_genres if isinstance(item, dict)])
    scoring_data["genre_weights"] = _build_weight_map([item for item in top_genres if isinstance(item, dict)])
    scoring_data["tag_weights"] = _build_weight_map([item for item in top_tags if isinstance(item, dict)])

    signal_vector = profile.get("profile_signal_vector", {})
    top_genre_entropy = 0.5
    top_tag_entropy = 0.5
    if isinstance(signal_vector, dict):
        if "top_genre_entropy" in signal_vector:
            top_genre_entropy = _clamp_0_1(float(signal_vector.get("top_genre_entropy", 0.5)))
        if "top_tag_entropy" in signal_vector:
            top_tag_entropy = _clamp_0_1(float(signal_vector.get("top_tag_entropy", 0.5)))
    average_entropy = (top_genre_entropy + top_tag_entropy) / 2.0
    scoring_data["semantic_precision_alpha"] = round(0.2 + ((1.0 - average_entropy) * 0.4), 6)
    return scoring_data


def controls_from_mapping(payload: Mapping[str, Any]) -> ScoringControls:
    component_weights_raw = payload.get("component_weights")
    numeric_thresholds_raw = payload.get("numeric_thresholds")
    return ScoringControls(
        config_source=str(payload.get("config_source") or "environment"),
        run_config_path=(str(payload["run_config_path"]) if payload.get("run_config_path") else None),
        run_config_schema_version=(
            str(payload["run_config_schema_version"]) if payload.get("run_config_schema_version") else None
        ),
        signal_mode={str(k): v for k, v in dict(payload.get("signal_mode") or {}).items()},
        component_weights={str(k): float(v) for k, v in dict(component_weights_raw or {}).items()},
        numeric_thresholds={str(k): float(v) for k, v in dict(numeric_thresholds_raw or {}).items()},
        lead_genre_strategy=str(payload.get("lead_genre_strategy") or "weighted_top_lead_genres"),
        semantic_overlap_strategy=str(payload.get("semantic_overlap_strategy") or "precision_aware"),
        semantic_precision_alpha_mode=str(payload.get("semantic_precision_alpha_mode") or "profile_adaptive"),
        semantic_precision_alpha_fixed=float(
            payload["semantic_precision_alpha_fixed"]
            if payload.get("semantic_precision_alpha_fixed") is not None
            else 0.35
        ),
        enable_numeric_confidence_scaling=bool(payload.get("enable_numeric_confidence_scaling", True)),
        numeric_confidence_floor=float(
            payload["numeric_confidence_floor"] if payload.get("numeric_confidence_floor") is not None else 0.0
        ),
        profile_numeric_confidence_mode=str(payload.get("profile_numeric_confidence_mode") or "direct"),
        profile_numeric_confidence_blend_weight=float(
            payload["profile_numeric_confidence_blend_weight"]
            if payload.get("profile_numeric_confidence_blend_weight") is not None
            else 1.0
        ),
        emit_confidence_impact_diagnostics=bool(payload.get("emit_confidence_impact_diagnostics", True)),
        emit_semantic_precision_diagnostics=bool(payload.get("emit_semantic_precision_diagnostics", False)),
        apply_bl003_influence_tracks=bool(payload.get("apply_bl003_influence_tracks", False)),
        influence_track_bonus_scale=float(
            payload["influence_track_bonus_scale"]
            if payload.get("influence_track_bonus_scale") is not None
            else 0.0
        ),
        spread_warn_threshold=float(payload.get("spread_warn_threshold", 0.15)),
    )


def context_from_mapping(payload: Mapping[str, Any]) -> ScoringContext:
    active_numeric_specs_raw = payload.get("active_numeric_specs")
    active_numeric_specs: dict[str, dict[str, object]] = {}
    if isinstance(active_numeric_specs_raw, Mapping):
        for key, value in active_numeric_specs_raw.items():
            if isinstance(value, Mapping):
                active_numeric_specs[str(key)] = {str(k): v for k, v in value.items()}
    return ScoringContext(
        signal_mode={str(k): v for k, v in dict(payload.get("signal_mode") or {}).items()},
        effective_component_weights={
            str(k): float(v) for k, v in dict(payload.get("effective_component_weights") or {}).items()
        },
        active_numeric_specs=active_numeric_specs,
        profile_scoring_data={str(k): v for k, v in dict(payload.get("profile_scoring_data") or {}).items()},
        active_component_weights={
            str(k): float(v) for k, v in dict(payload.get("active_component_weights") or {}).items()
        },
        weight_rebalance_diagnostics={
            str(k): v for k, v in dict(payload.get("weight_rebalance_diagnostics") or {}).items()
        },
        numeric_confidence_by_feature={
            str(k): float(v) for k, v in dict(payload.get("numeric_confidence_by_feature") or {}).items()
        },
        profile_numeric_confidence_factor=float(payload.get("profile_numeric_confidence_factor", 1.0)),
        semantic_precision_alpha=float(payload.get("semantic_precision_alpha", 0.35)),
        lead_genre_strategy=str(payload.get("lead_genre_strategy") or "weighted_top_lead_genres"),
        semantic_overlap_strategy=str(payload.get("semantic_overlap_strategy") or "precision_aware"),
        semantic_precision_alpha_mode=str(payload.get("semantic_precision_alpha_mode") or "profile_adaptive"),
        semantic_precision_alpha_fixed=float(payload.get("semantic_precision_alpha_fixed", 0.35)),
        enable_numeric_confidence_scaling=bool(payload.get("enable_numeric_confidence_scaling", True)),
        numeric_confidence_floor=float(payload.get("numeric_confidence_floor", 0.0)),
        profile_numeric_confidence_mode=str(payload.get("profile_numeric_confidence_mode") or "direct"),
        profile_numeric_confidence_blend_weight=float(payload.get("profile_numeric_confidence_blend_weight", 1.0)),
        emit_confidence_impact_diagnostics=bool(payload.get("emit_confidence_impact_diagnostics", True)),
        emit_semantic_precision_diagnostics=bool(payload.get("emit_semantic_precision_diagnostics", False)),
        apply_bl003_influence_tracks=bool(payload.get("apply_bl003_influence_tracks", False)),
        influence_track_ids={str(v) for v in list(payload.get("influence_track_ids") or []) if str(v)},
        influence_preference_weight=float(payload.get("influence_preference_weight", 0.0)),
        influence_track_bonus_scale=float(payload.get("influence_track_bonus_scale", 0.0)),
        spread_warn_threshold=float(payload.get("spread_warn_threshold", 0.15)),
    )


def build_active_component_weights(
    active_numeric_components: set[str],
    component_weights: dict[str, float],
    numeric_components: set[str],
) -> tuple[dict[str, float], dict[str, object]]:
    active: dict[str, float] = {}
    for component, weight in component_weights.items():
        component_name = component.removesuffix("_score")
        if component_name in numeric_components and component_name not in active_numeric_components:
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
            "BL-006 rebalanced active component weights to sum to 1.0" if rebalanced else None
        ),
    }
    return normalized, diagnostics


def _load_bl006_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "signal_mode": {},
        "component_weights": load_positive_numeric_map_from_env("BL006_COMPONENT_WEIGHTS_JSON"),
        "numeric_thresholds": load_positive_numeric_map_from_env("BL006_NUMERIC_THRESHOLDS_JSON"),
        "lead_genre_strategy": env_str("BL006_LEAD_GENRE_STRATEGY", "weighted_top_lead_genres"),
        "semantic_overlap_strategy": env_str("BL006_SEMANTIC_OVERLAP_STRATEGY", "precision_aware"),
        "semantic_precision_alpha_mode": env_str("BL006_SEMANTIC_PRECISION_ALPHA_MODE", "profile_adaptive"),
        "semantic_precision_alpha_fixed": env_float("BL006_SEMANTIC_PRECISION_ALPHA_FIXED", 0.35),
        "enable_numeric_confidence_scaling": env_bool("BL006_ENABLE_NUMERIC_CONFIDENCE_SCALING", True),
        "numeric_confidence_floor": env_float("BL006_NUMERIC_CONFIDENCE_FLOOR", 0.0),
        "profile_numeric_confidence_mode": env_str("BL006_PROFILE_NUMERIC_CONFIDENCE_MODE", "direct"),
        "profile_numeric_confidence_blend_weight": env_float("BL006_PROFILE_NUMERIC_CONFIDENCE_BLEND_WEIGHT", 1.0),
        "emit_confidence_impact_diagnostics": env_bool("BL006_EMIT_CONFIDENCE_IMPACT_DIAGNOSTICS", True),
        "emit_semantic_precision_diagnostics": env_bool("BL006_EMIT_SEMANTIC_PRECISION_DIAGNOSTICS", False),
        "apply_bl003_influence_tracks": env_bool("BL006_APPLY_BL003_INFLUENCE_TRACKS", False),
        "influence_track_bonus_scale": env_float("BL006_INFLUENCE_TRACK_BONUS_SCALE", 0.0),
        "spread_warn_threshold": env_float("BL006_SPREAD_WARN_THRESHOLD", 0.15),
    }


def _sanitize_bl006_controls(controls: dict[str, object]) -> dict[str, object]:
    component_weights = controls.get("component_weights")
    if not isinstance(component_weights, dict) or not component_weights:
        raise RuntimeError(
            "BL-006 component_weights must be supplied via orchestration payload or BL006_COMPONENT_WEIGHTS_JSON environment variable"
        )
    controls["component_weights"] = {
        str(k): float(v) for k, v in component_weights.items() if isinstance(v, (int, float))
    }
    controls["numeric_thresholds"] = coerce_dict(controls.get("numeric_thresholds"))
    controls["signal_mode"] = coerce_dict(controls.get("signal_mode"))
    controls["lead_genre_strategy"] = coerce_enum(
        controls.get("lead_genre_strategy"),
        VALID_LEAD_GENRE_STRATEGIES,
        "weighted_top_lead_genres",
    )
    controls["semantic_overlap_strategy"] = coerce_enum(
        controls.get("semantic_overlap_strategy"),
        VALID_SEMANTIC_OVERLAP_STRATEGIES,
        "precision_aware",
    )
    controls["semantic_precision_alpha_mode"] = coerce_enum(
        controls.get("semantic_precision_alpha_mode"),
        VALID_SEMANTIC_ALPHA_MODES,
        "profile_adaptive",
    )
    controls["semantic_precision_alpha_fixed"] = max(
        0.0,
        min(1.0, coerce_float(controls.get("semantic_precision_alpha_fixed"), 0.35)),
    )
    controls["enable_numeric_confidence_scaling"] = bool(controls.get("enable_numeric_confidence_scaling", True))
    controls["numeric_confidence_floor"] = max(0.0, coerce_float(controls.get("numeric_confidence_floor"), 0.0))
    controls["profile_numeric_confidence_mode"] = coerce_enum(
        controls.get("profile_numeric_confidence_mode"),
        VALID_NUMERIC_CONFIDENCE_MODES,
        "direct",
    )
    controls["profile_numeric_confidence_blend_weight"] = max(
        0.0,
        min(1.0, coerce_float(controls.get("profile_numeric_confidence_blend_weight"), 1.0)),
    )
    controls["emit_confidence_impact_diagnostics"] = bool(controls.get("emit_confidence_impact_diagnostics", True))
    controls["emit_semantic_precision_diagnostics"] = bool(controls.get("emit_semantic_precision_diagnostics", False))
    controls["apply_bl003_influence_tracks"] = bool(controls.get("apply_bl003_influence_tracks", False))
    controls["influence_track_bonus_scale"] = max(
        0.0,
        coerce_float(controls.get("influence_track_bonus_scale"), 0.0),
    )
    controls["spread_warn_threshold"] = max(
        0.0,
        min(1.0, coerce_float(controls.get("spread_warn_threshold"), 0.15)),
    )
    return controls


def resolve_bl006_runtime_controls() -> dict[str, object]:
    return resolve_stage_controls(
        load_from_env=_load_bl006_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_SCORING_CONTROLS),
        sanitize=_sanitize_bl006_controls,
    )


def _circular_distance_12(value: float, center: float) -> float:
    normalized_value = value % 12.0
    normalized_center = center % 12.0
    raw_diff = abs(normalized_value - normalized_center)
    return min(raw_diff, 12.0 - raw_diff)


def numeric_similarity(value: float | None, center: float, threshold: float, circular: bool = False) -> float:
    if value is None:
        return 0.0
    if threshold <= 0:
        return 0.0
    diff = _circular_distance_12(value, center) if circular else abs(value - center)
    ratio = diff / threshold
    similarity = 1.0 - (ratio * ratio)
    return round(max(0.0, min(similarity, 1.0)), 6)


def weighted_overlap(
    candidate_set: list[str],
    profile_weights: dict[str, float],
    *,
    precision_alpha: float = 0.35,
) -> float:
    if not profile_weights or not candidate_set:
        return 0.0
    matched_weight = sum(profile_weights.get(label, 0.0) for label in candidate_set)
    total_weight = sum(profile_weights.values())
    unmatched_count = sum(1 for label in candidate_set if label not in profile_weights)
    denominator = total_weight + (max(0.0, precision_alpha) * float(unmatched_count))
    if denominator <= 0:
        return 0.0
    return round(_clamp_0_1(matched_weight / denominator), 6)


def _weighted_lead_genre_similarity(candidate_label: str, profile_weights: dict[str, float]) -> float:
    if not candidate_label or not profile_weights:
        return 0.0
    weighted_score = sum(
        lead_genre_token_similarity(candidate_label, profile_label) * weight
        for profile_label, weight in profile_weights.items()
    )
    return round(_clamp_0_1(weighted_score), 6)


def _compute_component_scores(
    candidate_attrs: dict[str, Any],
    profile_data: dict[str, object],
    active_numeric_specs: dict[str, dict[str, object]],
    *,
    lead_genre_strategy: str = "weighted_top_lead_genres",
    overlap_strategy: str = "precision_aware",
    semantic_precision_alpha: float | None = None,
) -> dict[str, object]:
    scores: dict[str, object] = {}
    numeric_centers = dict(profile_data.get("numeric_centers") or {}) if isinstance(profile_data.get("numeric_centers"), dict) else {}
    numeric_thresholds = dict(profile_data.get("numeric_thresholds") or {}) if isinstance(profile_data.get("numeric_thresholds"), dict) else {}
    genre_weights = dict(profile_data.get("genre_weights") or {}) if isinstance(profile_data.get("genre_weights"), dict) else {}
    tag_weights = dict(profile_data.get("tag_weights") or {}) if isinstance(profile_data.get("tag_weights"), dict) else {}
    lead_genre_weights = dict(profile_data.get("lead_genre_weights") or {}) if isinstance(profile_data.get("lead_genre_weights"), dict) else {}
    semantic_precision_alpha_effective = (
        _to_float(semantic_precision_alpha, 0.35)
        if semantic_precision_alpha is not None
        else _to_float(profile_data.get("semantic_precision_alpha", 0.35), 0.35)
    )

    for dimension, spec in active_numeric_specs.items():
        value = candidate_attrs.get(dimension)
        center = numeric_centers.get(dimension)
        threshold = numeric_thresholds.get(dimension, 1.0)
        similarity = numeric_similarity(
            float(value) if value is not None else None,
            float(center) if center is not None else 0.0,
            float(threshold),
            bool(spec.get("circular", False)),
        )
        scores[f"{dimension}_similarity"] = similarity

    candidate_lead_genre = str(candidate_attrs.get("lead_genre", "")).lower()
    profile_lead_genre = str(profile_data.get("lead_genre", "")).lower()
    if str(lead_genre_strategy).strip().lower() == "single_anchor":
        lead_genre_similarity = lead_genre_token_similarity(candidate_lead_genre, profile_lead_genre)
    elif lead_genre_weights:
        lead_genre_similarity = _weighted_lead_genre_similarity(candidate_lead_genre, lead_genre_weights)
    else:
        lead_genre_similarity = lead_genre_token_similarity(candidate_lead_genre, profile_lead_genre)
    scores["lead_genre_similarity"] = lead_genre_similarity

    candidate_genres_raw = candidate_attrs.get("genres", [])
    candidate_genres = [str(value) for value in candidate_genres_raw] if isinstance(candidate_genres_raw, list) else []
    candidate_tags_raw = candidate_attrs.get("tags", [])
    candidate_tags = [str(value) for value in candidate_tags_raw] if isinstance(candidate_tags_raw, list) else []
    precision_alpha = semantic_precision_alpha_effective if str(overlap_strategy).strip().lower() == "precision_aware" else 0.0
    scores["genre_overlap_similarity"] = weighted_overlap(candidate_genres, genre_weights, precision_alpha=precision_alpha)
    scores["tag_overlap_similarity"] = weighted_overlap(candidate_tags, tag_weights, precision_alpha=precision_alpha)
    scores["matched_genres"] = [genre for genre in candidate_genres if genre in genre_weights]
    scores["matched_tags"] = [tag for tag in candidate_tags if tag in tag_weights]
    return scores


def _compute_weighted_contributions(
    component_scores: dict[str, object],
    component_weights: dict[str, float],
    *,
    numeric_confidence_by_feature: dict[str, float] | None = None,
    profile_numeric_confidence_factor: float = 1.0,
    enable_numeric_confidence_scaling: bool = True,
    numeric_confidence_floor: float = 0.0,
    profile_numeric_confidence_mode: str = "direct",
    profile_numeric_confidence_blend_weight: float = 1.0,
) -> dict[str, float]:
    contributions: dict[str, float] = {}
    confidence_map = numeric_confidence_by_feature or {}
    profile_factor_direct = _clamp_0_1(profile_numeric_confidence_factor)
    blend_weight = _clamp_0_1(profile_numeric_confidence_blend_weight)
    if str(profile_numeric_confidence_mode).strip().lower() == "blended":
        profile_factor = (blend_weight * profile_factor_direct) + ((1.0 - blend_weight) * 1.0)
    else:
        profile_factor = profile_factor_direct
    confidence_floor = _clamp_0_1(numeric_confidence_floor)
    for component, weight in component_weights.items():
        component_name = component.removesuffix("_score")
        similarity = _to_float(component_scores.get(f"{component_name}_similarity", 0.0))
        confidence_multiplier = 1.0
        if enable_numeric_confidence_scaling and component_name in confidence_map:
            per_feature_confidence = _clamp_0_1(_to_float(confidence_map.get(component_name), 1.0))
            per_feature_confidence = max(confidence_floor, per_feature_confidence)
            confidence_multiplier = per_feature_confidence * profile_factor
        contributions[f"{component_name}_contribution"] = round(similarity * weight * confidence_multiplier, 6)
    return contributions


def _compute_final_score(
    component_scores: dict[str, object],
    component_weights: dict[str, float],
    *,
    weighted_contributions: dict[str, float] | None = None,
) -> float:
    contributions = weighted_contributions if weighted_contributions is not None else _compute_weighted_contributions(component_scores, component_weights)
    return round(sum(contributions.values()), 6)


def _percentile(sorted_values: list[float], p: float) -> float:
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


def build_score_distribution_diagnostics(
    scored_rows: list[dict[str, object]],
    *,
    spread_warn_threshold: float = 0.15,
) -> dict[str, object]:
    score_desc = [_to_float(row.get("final_score", 0.0)) for row in scored_rows]
    score_desc.sort(reverse=True)
    gaps: list[dict[str, float | int]] = []
    for index in range(len(score_desc) - 1):
        gaps.append(
            {
                "between_rank": index + 1,
                "next_rank": index + 2,
                "score_gap": round(score_desc[index] - score_desc[index + 1], 6),
            }
        )
    max_gap = max(gaps, key=lambda item: _to_float(item["score_gap"])) if gaps else None
    rank_2_to_3_gap = round(score_desc[1] - score_desc[2], 6) if len(score_desc) >= 3 else 0.0
    is_rank_cliff = bool(max_gap and _to_float(max_gap["score_gap"]) >= 0.1)
    score_asc = list(reversed(score_desc))
    max_score = round(score_desc[0], 6) if score_desc else 0.0
    min_score = round(score_desc[-1], 6) if score_desc else 0.0
    spread = round(max_score - min_score, 6)
    spread_ratio = round(spread / max_score, 6) if max_score > 0.0 else 0.0
    spread_warn_threshold = max(0.0, min(1.0, float(spread_warn_threshold)))
    return {
        "score_percentiles": {
            "p10": round(_percentile(score_asc, 10), 6),
            "p25": round(_percentile(score_asc, 25), 6),
            "p50": round(_percentile(score_asc, 50), 6),
            "p75": round(_percentile(score_asc, 75), 6),
            "p90": round(_percentile(score_asc, 90), 6),
            "p95": round(_percentile(score_asc, 95), 6),
            "p99": round(_percentile(score_asc, 99), 6),
        },
        "score_range": {
            "max": max_score,
            "min": min_score,
            "spread": spread,
            "spread_ratio": spread_ratio,
            "spread_warn_threshold": spread_warn_threshold,
            "spread_status": "warn" if spread_ratio < spread_warn_threshold else "pass",
        },
        "rank_cliff": {
            "detected": is_rank_cliff,
            "rank_2_to_3_gap": rank_2_to_3_gap,
            "max_gap": max_gap or {"between_rank": 0, "next_rank": 0, "score_gap": 0.0},
            "classification": "cliff" if is_rank_cliff else "smooth",
        },
    }


def contribution_breakdown(rows: list[dict[str, object]]) -> dict[str, float]:
    numeric_components = ["danceability", "energy", "valence", "tempo", "duration_ms", "popularity", "key", "mode"]
    semantic_components = ["lead_genre", "genre_overlap", "tag_overlap"]
    if not rows:
        return {
            "numeric_contribution_mean": 0.0,
            "semantic_contribution_mean": 0.0,
            **{f"{component}_mean": 0.0 for component in numeric_components + semantic_components},
        }

    def mean_of(key: str) -> float:
        return round(statistics.mean(_to_float(row.get(key, 0.0)) for row in rows), 6)

    component_means = {f"{component}_mean": mean_of(f"{component}_contribution") for component in numeric_components + semantic_components}
    numeric_mean = round(sum(component_means[f"{component}_mean"] for component in numeric_components), 6)
    semantic_mean = round(sum(component_means[f"{component}_mean"] for component in semantic_components), 6)
    return {
        "numeric_contribution_mean": numeric_mean,
        "semantic_contribution_mean": semantic_mean,
        **component_means,
    }


def build_confidence_impact_diagnostics(
    scored_rows: list[dict[str, object]],
    numeric_confidence_by_feature: dict[str, float],
    profile_numeric_confidence_factor: float,
    *,
    enabled: bool = True,
    numeric_confidence_floor: float = 0.0,
    profile_numeric_confidence_mode: str = "direct",
    profile_numeric_confidence_blend_weight: float = 1.0,
) -> dict[str, object]:
    if not enabled:
        return {"active": False, "disabled": True, "reason": "confidence scaling disabled by scoring control"}
    if not scored_rows:
        return {
            "active": False,
            "profile_numeric_confidence_factor": round(profile_numeric_confidence_factor, 6),
            "feature_confidence_by_name": dict(numeric_confidence_by_feature),
            "numeric_confidence_floor": round(numeric_confidence_floor, 6),
            "profile_numeric_confidence_mode": str(profile_numeric_confidence_mode),
            "profile_numeric_confidence_blend_weight": round(profile_numeric_confidence_blend_weight, 6),
            "component_multiplier": {},
            "mean_adjusted_contribution": {},
            "mean_estimated_unadjusted_contribution": {},
            "mean_estimated_reduction": {},
            "total_numeric_adjusted_mean": 0.0,
            "total_numeric_estimated_unadjusted_mean": 0.0,
            "total_numeric_estimated_reduction": 0.0,
        }

    profile_factor = max(0.0, min(1.0, float(profile_numeric_confidence_factor)))
    component_multiplier = {
        component: round(max(0.0, min(1.0, float(confidence))) * profile_factor, 6)
        for component, confidence in numeric_confidence_by_feature.items()
    }

    def mean_of(key: str) -> float:
        return round(statistics.mean(_to_float(row.get(key, 0.0)) for row in scored_rows), 6)

    adjusted_by_component: dict[str, float] = {}
    estimated_unadjusted_by_component: dict[str, float] = {}
    estimated_reduction_by_component: dict[str, float] = {}
    for component, multiplier in component_multiplier.items():
        adjusted_mean = mean_of(f"{component}_contribution")
        adjusted_by_component[component] = adjusted_mean
        estimated_unadjusted = round(adjusted_mean / multiplier, 6) if multiplier > 0 else adjusted_mean
        estimated_unadjusted_by_component[component] = estimated_unadjusted
        estimated_reduction_by_component[component] = round(max(0.0, estimated_unadjusted - adjusted_mean), 6)

    total_adjusted = round(sum(adjusted_by_component.values()), 6)
    total_unadjusted = round(sum(estimated_unadjusted_by_component.values()), 6)
    return {
        "active": bool(component_multiplier),
        "profile_numeric_confidence_factor": round(profile_factor, 6),
        "numeric_confidence_floor": round(numeric_confidence_floor, 6),
        "profile_numeric_confidence_mode": str(profile_numeric_confidence_mode),
        "profile_numeric_confidence_blend_weight": round(profile_numeric_confidence_blend_weight, 6),
        "feature_confidence_by_name": {key: round(float(value), 6) for key, value in numeric_confidence_by_feature.items()},
        "component_multiplier": component_multiplier,
        "mean_adjusted_contribution": adjusted_by_component,
        "mean_estimated_unadjusted_contribution": estimated_unadjusted_by_component,
        "mean_estimated_reduction": estimated_reduction_by_component,
        "total_numeric_adjusted_mean": total_adjusted,
        "total_numeric_estimated_unadjusted_mean": total_unadjusted,
        "total_numeric_estimated_reduction": round(max(0.0, total_unadjusted - total_adjusted), 6),
    }


def build_semantic_precision_diagnostics(
    *,
    enabled: bool,
    overlap_strategy: str,
    alpha_mode: str,
    alpha_effective: float,
    alpha_fixed: float,
) -> dict[str, object]:
    return {
        "active": bool(enabled),
        "overlap_strategy": str(overlap_strategy),
        "semantic_precision_alpha_mode": str(alpha_mode),
        "semantic_precision_alpha_effective": round(float(alpha_effective), 6),
        "semantic_precision_alpha_fixed": round(float(alpha_fixed), 6),
    }


class ScoringStage:
    """Object-oriented BL-006 workflow shell over single-file helpers."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    def resolve_paths(self) -> ScoringPaths:
        return ScoringPaths(
            profile_path=self.root / "profile" / "outputs" / "bl004_preference_profile.json",
            filtered_candidates_path=self.root / "retrieval" / "outputs" / "bl005_filtered_candidates.csv",
            output_dir=self.root / "scoring" / "outputs",
            bl003_summary_path=self.root / "alignment" / "outputs" / "bl003_ds001_spotify_summary.json",
        )

    @staticmethod
    def load_inputs(paths: ScoringPaths) -> ScoringInputs:
        profile = load_json(paths.profile_path)
        if not isinstance(profile, dict):
            raise RuntimeError("BL-006 profile artifact is malformed; expected JSON object")
        _validate_profile_contract(profile)

        bl003_summary: dict[str, object] = {}
        if paths.bl003_summary_path is not None and paths.bl003_summary_path.exists():
            loaded_summary = load_json(paths.bl003_summary_path)
            if isinstance(loaded_summary, dict):
                bl003_summary = {str(k): v for k, v in loaded_summary.items()}

        candidates_raw = load_csv_rows(paths.filtered_candidates_path)
        if not candidates_raw:
            raise RuntimeError("No BL-005 filtered candidates found for BL-006")
        candidates = [{str(k): str(v) for k, v in row.items()} for row in candidates_raw]
        return ScoringInputs(profile=profile, bl003_summary=bl003_summary, candidates=candidates)

    @staticmethod
    def _extract_bl003_influence_contract(
        bl003_summary: dict[str, object] | None,
    ) -> tuple[bool, set[str], float]:
        summary = dict(bl003_summary or {})
        inputs_obj = summary.get("inputs")
        inputs = dict(inputs_obj) if isinstance(inputs_obj, dict) else {}
        influence_obj = inputs.get("influence_tracks")
        influence = dict(influence_obj) if isinstance(influence_obj, dict) else {}
        enabled = bool(influence.get("enabled", False))
        track_ids_raw = influence.get("track_ids")
        track_ids = {
            str(track_id).strip() for track_id in (track_ids_raw or []) if str(track_id).strip()
        } if isinstance(track_ids_raw, list) else set()
        preference_weight = _to_float(influence.get("preference_weight", 0.0), 0.0)
        return enabled, track_ids, max(0.0, preference_weight)

    @staticmethod
    def resolve_runtime_controls() -> ScoringControls:
        return controls_from_mapping(resolve_bl006_runtime_controls())

    @staticmethod
    def build_runtime_context(
        *,
        profile: dict[str, object],
        bl003_summary: dict[str, object] | None = None,
        runtime_controls: ScoringControls | dict[str, object],
    ) -> ScoringContext:
        controls = runtime_controls if isinstance(runtime_controls, ScoringControls) else controls_from_mapping(runtime_controls)
        effective_component_weights = dict(controls.component_weights)
        numeric_threshold_overrides = dict(controls.numeric_thresholds)
        effective_numeric_specs = {
            key: {
                **spec,
                "threshold": float(numeric_threshold_overrides.get(key, _to_float(spec.get("threshold", 0.0)))),
            }
            for key, spec in NUMERIC_FEATURE_SPECS.items()
        }

        profile_scoring_data = extract_profile_scoring_data(profile, effective_numeric_specs)
        numeric_centers_obj = profile_scoring_data.get("numeric_centers")
        numeric_centers = numeric_centers_obj if isinstance(numeric_centers_obj, dict) else {}
        lead_genre_weights = profile_scoring_data.get("lead_genre_weights")
        genre_weights = profile_scoring_data.get("genre_weights")
        tag_weights = profile_scoring_data.get("tag_weights")
        if not numeric_centers and not any(
            isinstance(weights, dict) and weights for weights in [lead_genre_weights, genre_weights, tag_weights]
        ):
            raise RuntimeError("BL-006 profile contains no usable numeric or semantic scoring signals")

        active_numeric_specs = {key: spec for key, spec in effective_numeric_specs.items() if key in numeric_centers}
        active_component_weights, weight_rebalance_diagnostics = build_active_component_weights(
            set(active_numeric_specs),
            effective_component_weights,
            NUMERIC_COMPONENTS,
        )
        if round(sum(active_component_weights.values()), 6) != 1.0:
            raise RuntimeError("BL-006 active component weights must sum to 1.0")

        numeric_confidence_by_feature_raw = profile_scoring_data.get("numeric_confidence_by_feature")
        numeric_confidence_by_feature = {
            str(k): _clamp_0_1(_to_float(v, 1.0))
            for k, v in dict(numeric_confidence_by_feature_raw or {}).items()
        } if isinstance(numeric_confidence_by_feature_raw, dict) else {}
        profile_numeric_confidence_factor_base = _clamp_0_1(_to_float(profile_scoring_data.get("profile_numeric_confidence_factor", 1.0), 1.0))
        semantic_precision_alpha_profile = max(0.0, _to_float(profile_scoring_data.get("semantic_precision_alpha", 0.35), 0.35))

        lead_genre_strategy_raw = controls.lead_genre_strategy.strip().lower()
        lead_genre_strategy = lead_genre_strategy_raw if lead_genre_strategy_raw in VALID_LEAD_GENRE_STRATEGIES else "weighted_top_lead_genres"
        semantic_overlap_strategy_raw = controls.semantic_overlap_strategy.strip().lower()
        semantic_overlap_strategy = semantic_overlap_strategy_raw if semantic_overlap_strategy_raw in VALID_SEMANTIC_OVERLAP_STRATEGIES else "precision_aware"
        semantic_precision_alpha_mode_raw = controls.semantic_precision_alpha_mode.strip().lower()
        semantic_precision_alpha_mode = semantic_precision_alpha_mode_raw if semantic_precision_alpha_mode_raw in VALID_SEMANTIC_ALPHA_MODES else "profile_adaptive"
        semantic_precision_alpha_fixed = _clamp_0_1(controls.semantic_precision_alpha_fixed)
        semantic_precision_alpha = semantic_precision_alpha_fixed if semantic_precision_alpha_mode == "fixed" else semantic_precision_alpha_profile

        profile_numeric_confidence_mode_raw = controls.profile_numeric_confidence_mode.strip().lower()
        profile_numeric_confidence_mode = profile_numeric_confidence_mode_raw if profile_numeric_confidence_mode_raw in {"direct", "blended"} else "direct"
        profile_numeric_confidence_blend_weight = _clamp_0_1(controls.profile_numeric_confidence_blend_weight)
        if profile_numeric_confidence_mode == "blended":
            profile_numeric_confidence_factor = (
                profile_numeric_confidence_blend_weight * profile_numeric_confidence_factor_base
            ) + ((1.0 - profile_numeric_confidence_blend_weight) * 1.0)
        else:
            profile_numeric_confidence_factor = profile_numeric_confidence_factor_base

        influence_enabled, influence_track_ids, influence_preference_weight = ScoringStage._extract_bl003_influence_contract(bl003_summary)
        apply_bl003_influence_tracks = bool(controls.apply_bl003_influence_tracks) and influence_enabled and bool(influence_track_ids)
        influence_track_bonus_scale = max(0.0, float(controls.influence_track_bonus_scale))
        return ScoringContext(
            signal_mode=dict(controls.signal_mode),
            effective_component_weights=effective_component_weights,
            active_numeric_specs=active_numeric_specs,
            profile_scoring_data=profile_scoring_data,
            active_component_weights=active_component_weights,
            weight_rebalance_diagnostics=weight_rebalance_diagnostics,
            numeric_confidence_by_feature=numeric_confidence_by_feature,
            profile_numeric_confidence_factor=profile_numeric_confidence_factor,
            semantic_precision_alpha=semantic_precision_alpha,
            lead_genre_strategy=lead_genre_strategy,
            semantic_overlap_strategy=semantic_overlap_strategy,
            semantic_precision_alpha_mode=semantic_precision_alpha_mode,
            semantic_precision_alpha_fixed=semantic_precision_alpha_fixed,
            enable_numeric_confidence_scaling=bool(controls.enable_numeric_confidence_scaling),
            numeric_confidence_floor=_clamp_0_1(controls.numeric_confidence_floor),
            profile_numeric_confidence_mode=profile_numeric_confidence_mode,
            profile_numeric_confidence_blend_weight=profile_numeric_confidence_blend_weight,
            emit_confidence_impact_diagnostics=bool(controls.emit_confidence_impact_diagnostics),
            emit_semantic_precision_diagnostics=bool(controls.emit_semantic_precision_diagnostics),
            apply_bl003_influence_tracks=apply_bl003_influence_tracks,
            influence_track_ids=set(influence_track_ids),
            influence_preference_weight=influence_preference_weight,
            influence_track_bonus_scale=influence_track_bonus_scale,
            spread_warn_threshold=max(0.0, min(1.0, float(controls.spread_warn_threshold))),
        )

    @staticmethod
    def score_candidates(
        *,
        candidates: list[dict[str, str]],
        runtime_context: ScoringContext | dict[str, object],
    ) -> list[dict[str, object]]:
        context = runtime_context if isinstance(runtime_context, ScoringContext) else context_from_mapping(runtime_context)
        scored_rows: list[dict[str, object]] = []
        active_numeric_confidence = {
            key: value for key, value in context.numeric_confidence_by_feature.items() if key in context.active_numeric_specs
        }
        for row in candidates:
            candidate_attrs = parse_candidate_attributes(row)
            component_scores = _compute_component_scores(
                candidate_attrs,
                context.profile_scoring_data,
                context.active_numeric_specs,
                lead_genre_strategy=context.lead_genre_strategy,
                overlap_strategy=context.semantic_overlap_strategy,
                semantic_precision_alpha=context.semantic_precision_alpha,
            )
            weighted_contributions = _compute_weighted_contributions(
                component_scores,
                context.active_component_weights,
                numeric_confidence_by_feature=active_numeric_confidence,
                profile_numeric_confidence_factor=context.profile_numeric_confidence_factor,
                enable_numeric_confidence_scaling=context.enable_numeric_confidence_scaling,
                numeric_confidence_floor=context.numeric_confidence_floor,
                profile_numeric_confidence_mode=context.profile_numeric_confidence_mode,
                profile_numeric_confidence_blend_weight=context.profile_numeric_confidence_blend_weight,
            )
            final_score = _compute_final_score(
                component_scores,
                context.active_component_weights,
                weighted_contributions=weighted_contributions,
            )
            if context.apply_bl003_influence_tracks and str(row.get("track_id", "")) in (context.influence_track_ids or set()):
                influence_bonus = context.influence_preference_weight * context.influence_track_bonus_scale
                final_score = round(_clamp_0_1(final_score + influence_bonus), 6)

            matched_genres_raw = component_scores.get("matched_genres")
            matched_tags_raw = component_scores.get("matched_tags")
            matched_genres = [str(v) for v in matched_genres_raw] if isinstance(matched_genres_raw, list) else []
            matched_tags = [str(v) for v in matched_tags_raw] if isinstance(matched_tags_raw, list) else []
            scored_rows.append(
                {
                    "track_id": row.get("track_id", ""),
                    "lead_genre": candidate_attrs.get("lead_genre", ""),
                    "matched_genres": "|".join(matched_genres),
                    "matched_tags": "|".join(matched_tags),
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
                    "popularity_similarity": component_scores.get("popularity_similarity", 0.0),
                    "popularity_contribution": weighted_contributions.get("popularity_contribution", 0.0),
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

        scored_rows.sort(key=lambda item: (-_to_float(item.get("final_score", 0.0)), str(item.get("track_id", ""))))
        for index, row in enumerate(scored_rows, start=1):
            row["rank"] = index
        return scored_rows

    @staticmethod
    def write_scored_csv(*, scored_rows: list[dict[str, object]], scored_path: Path) -> None:
        with open_text_write(scored_path, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=SCORED_CANDIDATE_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(scored_rows)

    @staticmethod
    def build_summary(
        *,
        run_id: str,
        elapsed_seconds: float,
        paths: ScoringPaths,
        runtime_context: ScoringContext | dict[str, object],
        scored_rows: list[dict[str, object]],
        distribution_diagnostics: dict[str, object],
        diagnostics_path: Path,
        scored_path: Path,
        confidence_impact_diagnostics: dict[str, object] | None = None,
    ) -> dict[str, object]:
        if not scored_rows:
            raise RuntimeError("BL-006 cannot build summary with zero scored rows")
        context = runtime_context if isinstance(runtime_context, ScoringContext) else context_from_mapping(runtime_context)
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
        score_values = [_to_float(row.get("final_score", 0.0)) for row in scored_rows]
        top_100_rows = scored_rows[:100]
        top_500_rows = scored_rows[:500]
        return {
            "run_id": run_id,
            "task": "BL-006",
            "generated_at_utc": utc_now(),
            "input_artifacts": {
                "profile_path": str(paths.profile_path),
                "profile_sha256": sha256_of_file(paths.profile_path),
                "bl003_summary_path": str(paths.bl003_summary_path) if paths.bl003_summary_path is not None else None,
                "bl003_summary_sha256": (
                    sha256_of_file(paths.bl003_summary_path)
                    if paths.bl003_summary_path is not None and paths.bl003_summary_path.exists()
                    else None
                ),
                "filtered_candidates_path": str(paths.filtered_candidates_path),
                "filtered_candidates_sha256": sha256_of_file(paths.filtered_candidates_path),
            },
            "config": {
                "signal_mode": dict(context.signal_mode),
                "numeric_thresholds": {
                    profile_column: spec["threshold"] for profile_column, spec in context.active_numeric_specs.items()
                },
                "numeric_feature_mapping": {
                    profile_column: spec.get("candidate_column", profile_column)
                    for profile_column, spec in context.active_numeric_specs.items()
                },
                "base_component_weights": context.effective_component_weights,
                "active_component_weights": {key: round(value, 6) for key, value in context.active_component_weights.items()},
                "numeric_confidence_by_feature": {key: round(value, 6) for key, value in context.numeric_confidence_by_feature.items()},
                "profile_numeric_confidence_factor": round(context.profile_numeric_confidence_factor, 6),
                "semantic_precision_alpha": round(context.semantic_precision_alpha, 6),
                "lead_genre_strategy": context.lead_genre_strategy,
                "semantic_overlap_strategy": context.semantic_overlap_strategy,
                "semantic_precision_alpha_mode": context.semantic_precision_alpha_mode,
                "semantic_precision_alpha_fixed": round(context.semantic_precision_alpha_fixed, 6),
                "enable_numeric_confidence_scaling": context.enable_numeric_confidence_scaling,
                "numeric_confidence_floor": round(context.numeric_confidence_floor, 6),
                "profile_numeric_confidence_mode": context.profile_numeric_confidence_mode,
                "profile_numeric_confidence_blend_weight": round(context.profile_numeric_confidence_blend_weight, 6),
                "apply_bl003_influence_tracks": context.apply_bl003_influence_tracks,
                "influence_track_bonus_scale": round(context.influence_track_bonus_scale, 6),
                "influence_preference_weight": round(context.influence_preference_weight, 6),
                "influence_track_count": len(context.influence_track_ids or set()),
                "inactive_components": sorted(set(context.effective_component_weights) - set(context.active_component_weights)),
                "weight_rebalance_diagnostics": context.weight_rebalance_diagnostics,
                "lead_genre_normalization": "weighted token overlap against BL-004 top_lead_genres",
                "genre_overlap_normalization": "weighted overlap with unmatched-label precision penalty",
                "tag_overlap_normalization": "weighted overlap with unmatched-label precision penalty",
                "semantic_source": "ds001_tags_and_genres_columns",
            },
            "counts": {"candidates_scored": len(scored_rows)},
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
            "confidence_impact_diagnostics": confidence_impact_diagnostics or {},
            "top_candidates": top_candidates,
            "elapsed_seconds": round(elapsed_seconds, 3),
            "output_files": {
                "scored_candidates_path": str(scored_path),
                "score_distribution_diagnostics_path": str(diagnostics_path),
            },
        }

    @staticmethod
    def write_run_store(
        *,
        run_id: str,
        summary: dict[str, object],
        scored_rows: list[dict[str, object]],
        scored_path: Path,
        diagnostics_path: Path,
        summary_path: Path,
    ) -> Path:
        pipeline_run_id = (os.getenv("BL_PIPELINE_RUN_ID") or "").strip()
        store_run_id = pipeline_run_id or run_id
        run_store_path = resolve_run_store_path(impl_root(), store_run_id)
        generated_at_utc = str(summary.get("generated_at_utc") or utc_now())
        diagnostics_payload = load_json(diagnostics_path)
        diagnostics = diagnostics_payload if isinstance(diagnostics_payload, dict) else {}

        with SQLiteRunStore(run_store_path) as run_store:
            run_store.upsert_run(
                run_id=store_run_id,
                created_at_utc=generated_at_utc,
                source_stage_id="BL-006",
            )
            stage_run_pk = run_store.insert_stage_run(
                run_id=store_run_id,
                stage_id="BL-006",
                stage_run_ref=run_id,
                generated_at_utc=generated_at_utc,
                status="pass",
                summary=summary,
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="scored_candidates",
                artifact_type="csv",
                artifact_path=str(scored_path),
                sha256=sha256_of_file(scored_path),
                rows=scored_rows,
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="score_distribution_diagnostics",
                artifact_type="json",
                artifact_path=str(diagnostics_path),
                sha256=sha256_of_file(diagnostics_path),
                payload=diagnostics,
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="score_summary",
                artifact_type="json",
                artifact_path=str(summary_path),
                sha256=sha256_of_file(summary_path),
                payload=summary,
            )

        return run_store_path

    def run(self) -> ScoringArtifacts:
        paths = self.resolve_paths()
        paths.output_dir.mkdir(parents=True, exist_ok=True)
        ensure_paths_exist([paths.profile_path, paths.filtered_candidates_path], stage_label="BL-006")
        inputs = self.load_inputs(paths)
        runtime_controls = self.resolve_runtime_controls()
        runtime_context = self.build_runtime_context(
            profile=inputs.profile,
            bl003_summary=inputs.bl003_summary,
            runtime_controls=runtime_controls,
        )

        start_time = time.time()
        run_id = f"BL006-SCORE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        scored_rows = self.score_candidates(candidates=inputs.candidates, runtime_context=runtime_context)
        if not scored_rows:
            raise RuntimeError("BL-006 produced zero scored rows; check profile inputs and runtime controls")

        scored_path = paths.output_dir / "bl006_scored_candidates.csv"
        self.write_scored_csv(scored_rows=scored_rows, scored_path=scored_path)

        distribution_diagnostics = build_score_distribution_diagnostics(
            scored_rows,
            spread_warn_threshold=runtime_context.spread_warn_threshold,
        )
        active_numeric_confidence = {
            key: value for key, value in runtime_context.numeric_confidence_by_feature.items() if key in runtime_context.active_numeric_specs
        }
        confidence_impact_diagnostics = build_confidence_impact_diagnostics(
            scored_rows,
            active_numeric_confidence,
            runtime_context.profile_numeric_confidence_factor,
            enabled=runtime_context.emit_confidence_impact_diagnostics,
            numeric_confidence_floor=runtime_context.numeric_confidence_floor,
            profile_numeric_confidence_mode=runtime_context.profile_numeric_confidence_mode,
            profile_numeric_confidence_blend_weight=runtime_context.profile_numeric_confidence_blend_weight,
        )
        semantic_precision_diagnostics = build_semantic_precision_diagnostics(
            enabled=runtime_context.emit_semantic_precision_diagnostics,
            overlap_strategy=runtime_context.semantic_overlap_strategy,
            alpha_mode=runtime_context.semantic_precision_alpha_mode,
            alpha_effective=runtime_context.semantic_precision_alpha,
            alpha_fixed=runtime_context.semantic_precision_alpha_fixed,
        )

        diagnostics_path = paths.output_dir / "bl006_score_distribution_diagnostics.json"
        with open_text_write(diagnostics_path) as handle:
            json.dump(distribution_diagnostics, handle, indent=2, ensure_ascii=True)

        summary = self.build_summary(
            run_id=run_id,
            elapsed_seconds=time.time() - start_time,
            paths=paths,
            runtime_context=runtime_context,
            scored_rows=scored_rows,
            distribution_diagnostics=distribution_diagnostics,
            confidence_impact_diagnostics=confidence_impact_diagnostics,
            diagnostics_path=diagnostics_path,
            scored_path=scored_path,
        )
        summary["semantic_precision_diagnostics"] = semantic_precision_diagnostics
        summary["bl003_summary_present"] = bool(inputs.bl003_summary)
        summary["influence_contract_source"] = "present" if bool(inputs.bl003_summary) else "missing"
        summary["output_hashes_sha256"] = {
            "bl006_scored_candidates.csv": sha256_of_file(scored_path),
            "bl006_score_distribution_diagnostics.json": sha256_of_file(diagnostics_path),
        }
        summary["summary_hash_note"] = "summary file hash collected separately in experiment logging to avoid recursive self-reference"
        summary_path = paths.output_dir / "bl006_score_summary.json"
        with open_text_write(summary_path) as handle:
            json.dump(summary, handle, indent=2, ensure_ascii=True)

        run_store_path = self.write_run_store(
            run_id=run_id,
            summary=summary,
            scored_rows=scored_rows,
            scored_path=scored_path,
            diagnostics_path=diagnostics_path,
            summary_path=summary_path,
        )
        output_files_obj = summary.get("output_files")
        output_files = dict(output_files_obj) if isinstance(output_files_obj, Mapping) else {}
        summary["output_files"] = {
            **{str(key): value for key, value in output_files.items()},
            "sqlite_run_store": str(run_store_path),
        }
        with open_text_write(summary_path) as handle:
            json.dump(summary, handle, indent=2, ensure_ascii=True)

        logger.info("BL-006 candidate scoring complete.")
        if runtime_context.weight_rebalance_diagnostics["rebalanced"]:
            logger.warning(
                "BL-006 rebalanced component weights. original_active_weight_sum=%s",
                runtime_context.weight_rebalance_diagnostics["active_weight_sum_pre_normalization"],
            )
        logger.info("scored_candidates=%s", scored_path)
        logger.info("score_summary=%s", summary_path)
        return ScoringArtifacts(scored_path=scored_path, diagnostics_path=diagnostics_path, summary_path=summary_path)


def main() -> None:
    ScoringStage().run()


if __name__ == "__main__":
    main()
