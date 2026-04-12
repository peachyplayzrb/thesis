"""BL-004: Build user preference profile from aligned seed data."""

from __future__ import annotations

import csv
import json
import logging
import math
import os
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from shared.io_utils import load_csv_rows, sha256_of_file, utc_now, open_text_write
from shared.path_utils import impl_root
from shared.run_store import SQLiteRunStore, resolve_run_store_path
from shared.env_utils import env_bool, env_float, env_int, env_str
from shared.coerce_utils import coerce_enum, coerce_float, coerce_int, parse_csv_labels, parse_float
from alignment import (
    ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION,
    ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION,
)
from run_config.stage_control_resolution import defaults_loader, resolve_stage_controls
from run_config.run_config_utils import (
    DEFAULT_INCLUDE_INTERACTION_TYPES as RUN_CONFIG_DEFAULT_INCLUDE_INTERACTION_TYPES,
    DEFAULT_INPUT_SCOPE as RUN_CONFIG_DEFAULT_INPUT_SCOPE,
    DEFAULT_PROFILE_CONTROLS as RUN_CONFIG_DEFAULT_PROFILE_CONTROLS,
)


DEFAULT_INCLUDE_INTERACTION_TYPES: list[str] = list(RUN_CONFIG_DEFAULT_INCLUDE_INTERACTION_TYPES)
DEFAULT_INPUT_SCOPE: dict[str, object] = deepcopy(RUN_CONFIG_DEFAULT_INPUT_SCOPE)
DEFAULT_PROFILE_CONTROLS: dict[str, object] = {
    **deepcopy(RUN_CONFIG_DEFAULT_PROFILE_CONTROLS),
    "input_scope": dict(DEFAULT_INPUT_SCOPE),
    "user_id": "unknown_user",
    "include_interaction_types": list(DEFAULT_INCLUDE_INTERACTION_TYPES),
}
VALID_CONFIDENCE_WEIGHTING_MODES: frozenset[str] = frozenset({"linear_half_bias", "direct_confidence", "none"})
VALID_INTERACTION_ATTRIBUTION_MODES: frozenset[str] = frozenset({"split_selected_types_equal_share", "primary_type_only"})


def bl003_required_paths(repo_root: Path) -> dict[str, Path]:
    return {
        "summary": repo_root / "alignment/outputs/bl003_ds001_spotify_summary.json",
        "seed_table": repo_root / "alignment/outputs/bl003_ds001_spotify_seed_table.csv",
        "matched_events": repo_root / "alignment/outputs/bl003_ds001_spotify_matched_events.jsonl",
        "trace": repo_root / "alignment/outputs/bl003_ds001_spotify_trace.csv",
        "unmatched": repo_root / "alignment/outputs/bl003_ds001_spotify_unmatched.csv",
        "source_scope_manifest": repo_root / "alignment/outputs/bl003_source_scope_manifest.json",
    }


logger = logging.getLogger(__name__)


NUMERIC_FEATURE_COLUMNS: list[str] = [
    "danceability",
    "energy",
    "valence",
    "tempo",
    "key",
    "mode",
    "popularity",
    "duration_ms",
    "release",
]

SUMMARY_FEATURE_COLUMNS: list[str] = [
    "danceability",
    "energy",
    "valence",
    "tempo",
]

BL004_REQUIRED_SEED_COLUMNS: list[str] = [
    "ds001_id",
    "spotify_track_ids",
    "interaction_types",
    "preference_weight_sum",
    "interaction_count_sum",
    "tags",
    "genres",
    "artist",
    "song",
    *NUMERIC_FEATURE_COLUMNS,
]

SEED_TRACE_FIELDNAMES: list[str] = [
    "event_id",
    "track_id",
    "spotify_track_id",
    "spotify_artist",
    "spotify_title",
    "interaction_type",
    "signal_source",
    "seed_rank",
    "interaction_count",
    "preference_weight",
    "effective_weight",
    "lead_genre",
    "top_tag",
    "numeric_feature_coverage",
    "lastfm_status",
]

BL004_PROFILE_SCHEMA_VERSION = "bl004-profile-v2"
BL004_SUMMARY_SCHEMA_VERSION = "bl004-summary-v2"
BL004_OUTPUT_CONTRACT_VERSION = "bl004-output-contract-v2"


@dataclass(frozen=True)
class ProfilePaths:
    seed_table_path: Path
    bl003_summary_path: Path
    bl003_manifest_path: Path
    output_dir: Path
    seed_trace_path: Path
    profile_path: Path
    summary_path: Path


@dataclass(frozen=True)
class ProfileControls:
    config_source: str
    run_config_path: str | None
    run_config_schema_version: str | None
    input_scope: dict[str, object]
    top_tag_limit: int
    top_genre_limit: int
    top_lead_genre_limit: int
    user_id: str
    include_interaction_types: list[str]
    confidence_weighting_mode: str = "linear_half_bias"
    confidence_bin_high_threshold: float = 0.90
    confidence_bin_medium_threshold: float = 0.50
    min_non_fallback_rate_warn_threshold: float = 0.50
    interaction_attribution_mode: str = "split_selected_types_equal_share"
    emit_profile_policy_diagnostics: bool = True

    def as_mapping(self) -> dict[str, object]:
        return {
            "config_source": self.config_source,
            "run_config_path": self.run_config_path,
            "run_config_schema_version": self.run_config_schema_version,
            "input_scope": dict(self.input_scope),
            "top_tag_limit": self.top_tag_limit,
            "top_genre_limit": self.top_genre_limit,
            "top_lead_genre_limit": self.top_lead_genre_limit,
            "confidence_weighting_mode": self.confidence_weighting_mode,
            "confidence_bin_high_threshold": self.confidence_bin_high_threshold,
            "confidence_bin_medium_threshold": self.confidence_bin_medium_threshold,
            "min_non_fallback_rate_warn_threshold": self.min_non_fallback_rate_warn_threshold,
            "interaction_attribution_mode": self.interaction_attribution_mode,
            "emit_profile_policy_diagnostics": self.emit_profile_policy_diagnostics,
            "user_id": self.user_id,
            "include_interaction_types": list(self.include_interaction_types),
        }


@dataclass(frozen=True)
class ProfileInputs:
    seed_rows: list[dict[str, object]]
    bl003_summary: dict[str, object]
    bl003_manifest: dict[str, object]
    bl003_seed_contract: dict[str, object]
    bl003_structural_contract: dict[str, object]
    bl003_seed_contract_hash: str
    bl003_structural_contract_hash: str
    bl003_quality: dict[str, int | float] = field(default_factory=dict)
    bl003_rows_selected: dict[str, int] = field(default_factory=dict)
    bl003_rows_available: dict[str, int] = field(default_factory=dict)
    bl003_coverage_rate_by_source: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ProfileAggregation:
    input_row_count: int
    seed_trace_rows: list[dict[str, object]]
    numeric_profile: dict[str, float]
    tag_weights: dict[str, float]
    genre_weights: dict[str, float]
    lead_genre_weights: dict[str, float]
    counts_by_type: dict[str, int]
    weight_by_type: dict[str, float]
    interaction_count_sum_by_type: dict[str, int]
    numeric_observations: dict[str, int]
    missing_numeric_track_ids: list[str]
    blank_track_id_row_count: int
    total_effective_weight: float
    confidence_adjusted_weight_sum: float
    confidence_bins: dict[str, int]
    match_method_counts: dict[str, int]
    history_preference_weight_sum: float
    influence_preference_weight_sum: float
    history_interaction_count_sum: int
    influence_interaction_count_sum: int
    matched_seed_count: int
    mixed_interaction_row_count: int = 0
    primary_type_attribution_row_count: int = 0
    attribution_weight_by_type: dict[str, float] = field(default_factory=lambda: {"history": 0.0, "influence": 0.0})
    attribution_interaction_count_by_type: dict[str, float] = field(default_factory=lambda: {"history": 0.0, "influence": 0.0})
    attribution_row_share_by_type: dict[str, float] = field(default_factory=lambda: {"history": 0.0, "influence": 0.0})
    confidence_fallback_count: int = 0
    confidence_fallback_track_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProfileArtifacts:
    profile_path: Path
    summary_path: Path
    seed_trace_path: Path


def _normalize_include_interaction_types(raw_value: object) -> list[str]:
    allowed = {"history", "influence"}
    normalized: list[str] = []
    seen: set[str] = set()
    if isinstance(raw_value, list):
        values = raw_value
    elif isinstance(raw_value, str):
        values = [token.strip() for token in raw_value.split(",")]
    else:
        values = []

    for item in values:
        token = str(item).strip().lower()
        if token in allowed and token not in seen:
            seen.add(token)
            normalized.append(token)
    return normalized


def _sanitize_bl004_controls(controls: dict[str, object]) -> dict[str, object]:
    defaults = DEFAULT_PROFILE_CONTROLS
    controls["top_tag_limit"] = max(1, coerce_int(controls.get("top_tag_limit", defaults["top_tag_limit"]), 10))
    controls["top_genre_limit"] = max(1, coerce_int(controls.get("top_genre_limit", defaults["top_genre_limit"]), 8))
    controls["top_lead_genre_limit"] = max(1, coerce_int(controls.get("top_lead_genre_limit", defaults["top_lead_genre_limit"]), 6))
    controls["confidence_weighting_mode"] = coerce_enum(
        controls.get("confidence_weighting_mode", defaults["confidence_weighting_mode"]),
        VALID_CONFIDENCE_WEIGHTING_MODES,
        str(defaults["confidence_weighting_mode"]),
    )

    high_threshold = max(0.0, min(1.0, coerce_float(controls.get("confidence_bin_high_threshold", defaults["confidence_bin_high_threshold"]), 0.90)))
    medium_threshold = max(0.0, min(1.0, coerce_float(controls.get("confidence_bin_medium_threshold", defaults["confidence_bin_medium_threshold"]), 0.50)))
    controls["confidence_bin_high_threshold"] = high_threshold
    controls["confidence_bin_medium_threshold"] = min(medium_threshold, high_threshold)
    controls["min_non_fallback_rate_warn_threshold"] = max(
        0.0,
        min(
            1.0,
            coerce_float(
                controls.get("min_non_fallback_rate_warn_threshold", defaults["confidence_input_health"]["min_non_fallback_rate_warn_threshold"]),
                0.5,
            ),
        ),
    )
    controls["interaction_attribution_mode"] = coerce_enum(
        controls.get("interaction_attribution_mode", defaults["interaction_attribution_mode"]),
        VALID_INTERACTION_ATTRIBUTION_MODES,
        str(defaults["interaction_attribution_mode"]),
    )
    controls["emit_profile_policy_diagnostics"] = bool(controls.get("emit_profile_policy_diagnostics", defaults["emit_profile_policy_diagnostics"]))

    raw_include_interaction_types = controls.get("include_interaction_types")
    normalized_include_interaction_types = _normalize_include_interaction_types(raw_include_interaction_types)
    if raw_include_interaction_types is None or raw_include_interaction_types == "":
        normalized_include_interaction_types = list(DEFAULT_INCLUDE_INTERACTION_TYPES)
    elif isinstance(raw_include_interaction_types, list) and not raw_include_interaction_types:
        raise RuntimeError("BL-004 include_interaction_types cannot be empty")
    elif not normalized_include_interaction_types:
        raise RuntimeError(
            "BL-004 include_interaction_types must contain at least one of: history, influence"
        )
    controls["include_interaction_types"] = normalized_include_interaction_types

    controls["user_id"] = str(controls.get("user_id") or "unknown_user").strip() or "unknown_user"
    input_scope_raw = controls.get("input_scope")
    input_scope_payload = dict(input_scope_raw) if isinstance(input_scope_raw, Mapping) else {}
    controls["input_scope"] = input_scope_payload or dict(DEFAULT_INPUT_SCOPE)
    return controls


def _load_bl004_controls_from_env() -> dict[str, object]:
    defaults = DEFAULT_PROFILE_CONTROLS
    include_interaction_types = env_str("BL004_INCLUDE_INTERACTION_TYPES", "").strip()
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope": {},
        "top_tag_limit": env_int("BL004_TOP_TAG_LIMIT", int(str(defaults["top_tag_limit"]))),
        "top_genre_limit": env_int("BL004_TOP_GENRE_LIMIT", int(str(defaults["top_genre_limit"]))),
        "top_lead_genre_limit": env_int("BL004_TOP_LEAD_GENRE_LIMIT", int(str(defaults["top_lead_genre_limit"]))),
        "confidence_weighting_mode": env_str("BL004_CONFIDENCE_WEIGHTING_MODE", str(defaults["confidence_weighting_mode"])),
        "confidence_bin_high_threshold": env_float("BL004_CONFIDENCE_BIN_HIGH_THRESHOLD", float(str(defaults["confidence_bin_high_threshold"]))),
        "confidence_bin_medium_threshold": env_float("BL004_CONFIDENCE_BIN_MEDIUM_THRESHOLD", float(str(defaults["confidence_bin_medium_threshold"]))),
        "min_non_fallback_rate_warn_threshold": env_float(
            "BL004_MIN_NON_FALLBACK_RATE_WARN_THRESHOLD",
            float(str(defaults["confidence_input_health"]["min_non_fallback_rate_warn_threshold"])),
        ),
        "interaction_attribution_mode": env_str("BL004_INTERACTION_ATTRIBUTION_MODE", str(defaults["interaction_attribution_mode"])),
        "emit_profile_policy_diagnostics": env_bool("BL004_EMIT_PROFILE_POLICY_DIAGNOSTICS", bool(defaults["emit_profile_policy_diagnostics"])),
        "user_id": env_str("BL004_USER_ID", "unknown_user"),
        "include_interaction_types": include_interaction_types or None,
    }


def resolve_bl004_runtime_controls(*, inferred_user_id: str | None = None) -> dict[str, object]:
    controls = resolve_stage_controls(
        load_from_env=_load_bl004_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_PROFILE_CONTROLS),
        sanitize=_sanitize_bl004_controls,
    )
    if controls.get("user_id") in {None, "", "unknown_user"} and inferred_user_id:
        controls["user_id"] = inferred_user_id
    return controls


def _resolve_lead_genre(genres: list[str], tags: list[str]) -> str:
    if genres:
        return genres[0]
    if tags:
        return tags[0]
    return ""


def _sorted_weight_map(weight_map: dict[str, float], limit: int) -> list[dict[str, float | str]]:
    ordered = sorted(weight_map.items(), key=lambda item: (-item[1], item[0]))
    return [{"label": label, "weight": round(weight, 6)} for label, weight in ordered[:limit]]


def _circular_mean_key(sum_x: float, sum_y: float) -> float | None:
    magnitude = math.hypot(sum_x, sum_y)
    if magnitude == 0.0:
        return None
    normalized_x = sum_x / magnitude
    normalized_y = sum_y / magnitude
    angle = math.atan2(normalized_y, normalized_x)
    if angle < 0.0:
        angle += 2.0 * math.pi
    return (angle / (2.0 * math.pi)) * 12.0


def _load_required_json_object(path: Path, label: str) -> dict[str, object]:
    if not path.exists():
        raise RuntimeError(f"BL-004 missing required {label}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"BL-004 could not parse required {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"BL-004 expected object payload for {label}: {path}")
    return {str(key): value for key, value in payload.items()}


def _extract_contract_payload(
    summary_payload: dict[str, object],
    manifest_payload: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str, str]:
    inputs_raw = summary_payload.get("inputs")
    inputs = dict(inputs_raw) if isinstance(inputs_raw, dict) else {}
    seed_contract_raw = inputs.get("seed_contract")
    seed_contract = dict(seed_contract_raw) if isinstance(seed_contract_raw, dict) else {}
    structural_contract_raw = inputs.get("structural_contract")
    structural_contract = dict(structural_contract_raw) if isinstance(structural_contract_raw, dict) else {}

    manifest_seed_raw = manifest_payload.get("seed_contract")
    manifest_seed = dict(manifest_seed_raw) if isinstance(manifest_seed_raw, dict) else {}
    manifest_structural_raw = manifest_payload.get("structural_contract")
    manifest_structural = dict(manifest_structural_raw) if isinstance(manifest_structural_raw, dict) else {}

    if not seed_contract:
        seed_contract = dict(manifest_seed)
    if not structural_contract:
        structural_contract = dict(manifest_structural)
    if not seed_contract:
        raise RuntimeError("BL-004 expected BL-003 seed_contract in summary or manifest")
    if not structural_contract:
        raise RuntimeError("BL-004 expected BL-003 structural_contract in summary or manifest")

    seed_hash = str(seed_contract.get("contract_hash") or manifest_seed.get("contract_hash") or "")
    structural_hash = str(structural_contract.get("contract_hash") or manifest_structural.get("contract_hash") or "")
    if not seed_hash:
        raise RuntimeError("BL-004 expected BL-003 seed contract hash")
    if not structural_hash:
        raise RuntimeError("BL-004 expected BL-003 structural contract hash")

    seed_schema = str(seed_contract.get("seed_contract_schema_version") or "")
    structural_schema = str(structural_contract.get("structural_contract_schema_version") or "")
    if seed_schema != ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION:
        raise RuntimeError(
            "BL-004 BL-003 seed contract schema mismatch: "
            f"expected={ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION} observed={seed_schema}"
        )
    if structural_schema != ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION:
        raise RuntimeError(
            "BL-004 BL-003 structural contract schema mismatch: "
            f"expected={ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION} observed={structural_schema}"
        )
    return seed_contract, structural_contract, seed_hash, structural_hash


def _validate_seed_table_schema(seed_rows: list[dict[str, object]], structural_contract: dict[str, object]) -> None:
    if not seed_rows:
        raise RuntimeError("No DS-001 seed rows found for BL-004 input")

    fieldnames_raw = structural_contract.get("seed_table_fieldnames")
    expected_fieldnames = [str(value) for value in fieldnames_raw if str(value).strip()] if isinstance(fieldnames_raw, list) else []
    if not expected_fieldnames:
        raise RuntimeError("BL-004 expected structural_contract.seed_table_fieldnames")

    actual_columns = set(seed_rows[0].keys())
    missing_structural = [fieldname for fieldname in expected_fieldnames if fieldname not in actual_columns]
    if missing_structural:
        raise RuntimeError(
            "BL-004 seed table schema mismatch with BL-003 structural contract; missing columns: "
            + ", ".join(sorted(missing_structural))
        )

    missing_required = [fieldname for fieldname in BL004_REQUIRED_SEED_COLUMNS if fieldname not in actual_columns]
    if missing_required:
        raise RuntimeError(
            "BL-004 seed table missing required profile columns: " + ", ".join(sorted(missing_required))
        )


def _resolve_confidence(raw_value: object) -> tuple[float, bool]:
    parsed = parse_float(str(raw_value))
    if parsed is None:
        return 1.0, True
    return max(0.0, min(1.0, parsed)), False


def _safe_rate(numerator: float, denominator: float, precision: int = 6) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, precision)


def _normalize_int_mapping(raw_obj: object) -> dict[str, int]:
    if not isinstance(raw_obj, dict):
        return {}
    normalized: dict[str, int] = {}
    for key, value in raw_obj.items():
        parsed = parse_float(str(value))
        normalized[str(key)] = int(parsed) if parsed is not None else 0
    return normalized


def _extract_bl003_quality(summary_payload: dict[str, object]) -> dict[str, int | float]:
    counts_raw = summary_payload.get("counts")
    counts = dict(counts_raw) if isinstance(counts_raw, dict) else {}
    input_event_rows = int(parse_float(str(counts.get("input_event_rows", ""))) or 0)
    matched_by_spotify_id = int(parse_float(str(counts.get("matched_by_spotify_id", ""))) or 0)
    matched_by_metadata = int(parse_float(str(counts.get("matched_by_metadata", ""))) or 0)
    matched_by_fuzzy = int(parse_float(str(counts.get("matched_by_fuzzy", ""))) or 0)
    unmatched = int(parse_float(str(counts.get("unmatched", ""))) or 0)
    matched_total = matched_by_spotify_id + matched_by_metadata + matched_by_fuzzy
    match_rate = _safe_rate(matched_total, input_event_rows, precision=4)
    return {
        "input_event_rows": input_event_rows,
        "matched_by_spotify_id": matched_by_spotify_id,
        "matched_by_metadata": matched_by_metadata,
        "matched_by_fuzzy": matched_by_fuzzy,
        "unmatched": unmatched,
        "matched_total": matched_total,
        "match_rate": match_rate,
    }


def _compute_coverage_rate_by_source(rows_selected: dict[str, int], rows_available: dict[str, int]) -> dict[str, float]:
    rates: dict[str, float] = {}
    all_sources = set(rows_selected.keys()) | set(rows_available.keys())
    for source in sorted(all_sources):
        selected = float(rows_selected.get(source, 0))
        available = float(rows_available.get(source, 0))
        rates[source] = _safe_rate(selected, available, precision=6)
    return rates


def _compute_entropy(weight_map: dict[str, float]) -> float:
    positive_weights = [value for value in weight_map.values() if value > 0.0]
    if len(positive_weights) <= 1:
        return 0.0
    total_weight = sum(positive_weights)
    if total_weight <= 0.0:
        return 0.0
    probabilities = [weight / total_weight for weight in positive_weights]
    entropy = -sum(prob * math.log(prob) for prob in probabilities if prob > 0.0)
    max_entropy = math.log(len(probabilities))
    return _safe_rate(entropy, max_entropy, precision=6)


def _build_numeric_confidence_block(
    numeric_observations: dict[str, int],
    matched_seed_count: int,
    missing_numeric_track_count: int,
) -> dict[str, object]:
    confidence_by_feature = {
        feature: _safe_rate(float(observed), float(matched_seed_count), precision=6)
        for feature, observed in numeric_observations.items()
    }
    return {
        "observations_by_feature": dict(numeric_observations),
        "confidence_by_feature": confidence_by_feature,
        "missing_numeric_track_count": int(missing_numeric_track_count),
    }


def _build_interaction_attribution_block(aggregation: ProfileAggregation, controls: ProfileControls) -> dict[str, object]:
    contribution_by_type = {
        interaction_type: {
            "effective_weight": round(aggregation.attribution_weight_by_type.get(interaction_type, 0.0), 6),
            "interaction_count": round(aggregation.attribution_interaction_count_by_type.get(interaction_type, 0.0), 6),
            "row_share": round(aggregation.attribution_row_share_by_type.get(interaction_type, 0.0), 6),
        }
        for interaction_type in sorted(aggregation.attribution_weight_by_type.keys())
    }
    return {
        "policy_name": controls.interaction_attribution_mode,
        "mixed_interaction_row_count": aggregation.mixed_interaction_row_count,
        "contribution_by_type": contribution_by_type,
        "filtered_types_requested": list(controls.include_interaction_types),
    }


def _resolve_confidence_weight_multiplier(confidence: float, mode: str) -> float:
    if mode == "none":
        return 1.0
    if mode == "direct_confidence":
        return confidence
    return 0.5 + 0.5 * confidence


def _resolve_attribution_shares(
    selected_interaction_types: list[str],
    primary_interaction_type: str,
    mode: str,
) -> dict[str, float]:
    if not selected_interaction_types:
        return {}
    if mode == "primary_type_only":
        return {primary_interaction_type: 1.0}
    split_fraction = 1.0 / float(len(selected_interaction_types))
    return {interaction_type: split_fraction for interaction_type in selected_interaction_types}


def _build_profile_signal_vector(aggregation: ProfileAggregation, bl003_quality: dict[str, int | float]) -> dict[str, float]:
    history_effective_weight = aggregation.attribution_weight_by_type.get("history", 0.0)
    influence_effective_weight = aggregation.attribution_weight_by_type.get("influence", 0.0)
    total_effective_weight = aggregation.total_effective_weight
    return {
        "total_effective_weight": round(total_effective_weight, 6),
        "history_weight_share": _safe_rate(history_effective_weight, total_effective_weight, precision=6),
        "influence_weight_share": _safe_rate(influence_effective_weight, total_effective_weight, precision=6),
        "alignment_match_rate": float(bl003_quality.get("match_rate", 0.0) or 0.0),
        "top_genre_entropy": _compute_entropy(aggregation.genre_weights),
        "top_tag_entropy": _compute_entropy(aggregation.tag_weights),
    }


def _build_canonical_blocks(aggregation: ProfileAggregation, controls: ProfileControls, inputs: ProfileInputs) -> dict[str, object]:
    bl003_quality = dict(inputs.bl003_quality) or _extract_bl003_quality(inputs.bl003_summary)
    rows_selected = dict(inputs.bl003_rows_selected) or _normalize_int_mapping(inputs.bl003_manifest.get("rows_selected"))
    rows_available = dict(inputs.bl003_rows_available) or _normalize_int_mapping(inputs.bl003_manifest.get("rows_available"))
    coverage_rate_by_source = dict(inputs.bl003_coverage_rate_by_source) or _compute_coverage_rate_by_source(rows_selected, rows_available)
    return {
        "bl003_quality": bl003_quality,
        "source_coverage": {
            "rows_selected": rows_selected,
            "rows_available": rows_available,
            "coverage_rate_by_source": coverage_rate_by_source,
        },
        "interaction_attribution": _build_interaction_attribution_block(aggregation, controls),
        "numeric_confidence": _build_numeric_confidence_block(
            aggregation.numeric_observations,
            aggregation.matched_seed_count,
            len(aggregation.missing_numeric_track_ids),
        ),
        "profile_signal_vector": _build_profile_signal_vector(aggregation, inputs.bl003_quality),
    }


def _parse_selected_interaction_types(row: dict[str, object], include_interaction_types: set[str]) -> list[str]:
    raw_itypes = str(row.get("interaction_types", "") or row.get("interaction_type", "")).strip()
    row_interaction_types = {token.strip() for token in raw_itypes.split("|") if token.strip()} if raw_itypes else {"history"}
    return sorted(row_interaction_types.intersection(include_interaction_types))


def _resolve_primary_interaction_type(selected_interaction_types: list[str]) -> str:
    return "influence" if "influence" in selected_interaction_types else "history"


class ProfileStage:
    """Object-oriented BL-004 profile workflow shell."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    def infer_user_id_from_ingestion(self) -> str | None:
        profile_path = self.root / "ingestion" / "outputs" / "spotify_api_export" / "spotify_profile.json"
        if not profile_path.exists():
            return None
        try:
            payload = json.loads(profile_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        user_id = payload.get("id") if isinstance(payload, dict) else None
        if isinstance(user_id, str) and user_id.strip():
            return user_id.strip()
        return None

    @staticmethod
    def _sanitize_controls(controls: dict[str, object]) -> ProfileControls:
        return ProfileControls(
            config_source=str(controls.get("config_source") or "environment"),
            run_config_path=(str(controls["run_config_path"]) if controls.get("run_config_path") else None),
            run_config_schema_version=(str(controls["run_config_schema_version"]) if controls.get("run_config_schema_version") else None),
            input_scope={str(k): v for k, v in controls["input_scope"].items()},
            top_tag_limit=int(str(controls["top_tag_limit"])),
            top_genre_limit=int(str(controls["top_genre_limit"])),
            top_lead_genre_limit=int(str(controls["top_lead_genre_limit"])),
            confidence_weighting_mode=str(controls["confidence_weighting_mode"]),
            confidence_bin_high_threshold=float(str(controls["confidence_bin_high_threshold"])),
            confidence_bin_medium_threshold=float(str(controls["confidence_bin_medium_threshold"])),
            min_non_fallback_rate_warn_threshold=float(str(controls["min_non_fallback_rate_warn_threshold"])),
            interaction_attribution_mode=str(controls["interaction_attribution_mode"]),
            emit_profile_policy_diagnostics=bool(controls["emit_profile_policy_diagnostics"]),
            user_id=str(controls["user_id"]),
            include_interaction_types=list(controls["include_interaction_types"]),
        )

    def resolve_runtime_controls(self) -> ProfileControls:
        inferred_user_id = self.infer_user_id_from_ingestion()
        controls = resolve_bl004_runtime_controls(inferred_user_id=inferred_user_id)
        return self._sanitize_controls(controls)

    def resolve_paths(self) -> ProfilePaths:
        output_dir = self.root / "profile" / "outputs"
        bl003_paths = bl003_required_paths(self.root)
        paths = ProfilePaths(
            seed_table_path=bl003_paths["seed_table"],
            bl003_summary_path=bl003_paths["summary"],
            bl003_manifest_path=bl003_paths["source_scope_manifest"],
            output_dir=output_dir,
            seed_trace_path=output_dir / "bl004_seed_trace.csv",
            profile_path=output_dir / "bl004_preference_profile.json",
            summary_path=output_dir / "profile_summary.json",
        )
        missing_required_paths = [
            str(path)
            for path in (paths.seed_table_path, paths.bl003_summary_path, paths.bl003_manifest_path)
            if not path.exists()
        ]
        if missing_required_paths:
            raise RuntimeError(
                "BL-004 missing required BL-003 input artifact(s): " + ", ".join(missing_required_paths)
            )
        return paths

    @staticmethod
    def load_inputs(paths: ProfilePaths) -> ProfileInputs:
        seed_rows = load_csv_rows(paths.seed_table_path)
        summary_payload = _load_required_json_object(paths.bl003_summary_path, "BL-003 summary")
        manifest_payload = _load_required_json_object(paths.bl003_manifest_path, "BL-003 source scope manifest")
        seed_contract, structural_contract, seed_contract_hash, structural_contract_hash = _extract_contract_payload(
            summary_payload,
            manifest_payload,
        )

        normalized_rows = [{str(k): v for k, v in row.items()} for row in seed_rows]
        _validate_seed_table_schema(normalized_rows, structural_contract)
        rows_selected = _normalize_int_mapping(manifest_payload.get("rows_selected"))
        rows_available = _normalize_int_mapping(manifest_payload.get("rows_available"))
        bl003_quality = _extract_bl003_quality(summary_payload)
        return ProfileInputs(
            seed_rows=normalized_rows,
            bl003_summary=summary_payload,
            bl003_manifest=manifest_payload,
            bl003_seed_contract=seed_contract,
            bl003_structural_contract=structural_contract,
            bl003_seed_contract_hash=seed_contract_hash,
            bl003_structural_contract_hash=structural_contract_hash,
            bl003_quality=bl003_quality,
            bl003_rows_selected=rows_selected,
            bl003_rows_available=rows_available,
            bl003_coverage_rate_by_source=_compute_coverage_rate_by_source(rows_selected, rows_available),
        )

    @staticmethod
    def aggregate_inputs(inputs: ProfileInputs, controls: ProfileControls) -> ProfileAggregation:
        include_interaction_types = set(controls.include_interaction_types)

        numeric_sums = {column: 0.0 for column in NUMERIC_FEATURE_COLUMNS}
        numeric_weights = {column: 0.0 for column in NUMERIC_FEATURE_COLUMNS}
        tag_weights: dict[str, float] = {}
        genre_weights: dict[str, float] = {}
        lead_genre_weights: dict[str, float] = {}
        seed_trace_rows: list[dict[str, object]] = []

        counts_by_type = {"history": 0, "influence": 0}
        weight_by_type = {"history": 0.0, "influence": 0.0}
        interaction_count_sum_by_type = {"history": 0, "influence": 0}
        numeric_observations = {column: 0 for column in NUMERIC_FEATURE_COLUMNS}
        missing_numeric_track_ids: list[str] = []
        blank_track_id_row_count = 0
        confidence_adjusted_weight_sum = 0.0
        confidence_bins = {
            "high_0_9_plus": 0,
            "medium_0_5_to_0_9": 0,
            "low_below_0_5": 0,
        }
        match_method_counts = {
            "spotify_id_exact": int(inputs.bl003_quality.get("matched_by_spotify_id", 0) or 0),
            "metadata_fallback": int(inputs.bl003_quality.get("matched_by_metadata", 0) or 0),
            "fuzzy_title_artist": int(inputs.bl003_quality.get("matched_by_fuzzy", 0) or 0),
        }
        history_preference_weight_sum = 0.0
        influence_preference_weight_sum = 0.0
        history_interaction_count_sum_value = 0.0
        influence_interaction_count_sum_value = 0.0
        mixed_interaction_row_count = 0
        primary_type_attribution_row_count = 0
        attribution_weight_by_type = {"history": 0.0, "influence": 0.0}
        attribution_interaction_count_by_type = {"history": 0.0, "influence": 0.0}
        attribution_row_share_by_type = {"history": 0.0, "influence": 0.0}
        high_confidence_threshold = controls.confidence_bin_high_threshold
        medium_confidence_threshold = controls.confidence_bin_medium_threshold
        key_circular_sum_x = 0.0
        key_circular_sum_y = 0.0
        confidence_fallback_count = 0
        confidence_fallback_track_ids: list[str] = []

        for index, row in enumerate(inputs.seed_rows, start=1):
            track_id = str(row.get("ds001_id", "")).strip()
            spotify_ids = str(row.get("spotify_track_ids", "")).strip().split("|")
            spotify_id = next((item for item in spotify_ids if item), "")
            trace_track_id = track_id or (spotify_id if spotify_id else f"missing_ds001_id_{index:06d}")

            selected_interaction_types = _parse_selected_interaction_types(row, include_interaction_types)
            if not selected_interaction_types:
                continue
            if len(selected_interaction_types) > 1:
                mixed_interaction_row_count += 1

            interaction_type = _resolve_primary_interaction_type(selected_interaction_types)
            attribution_shares = _resolve_attribution_shares(
                selected_interaction_types,
                interaction_type,
                controls.interaction_attribution_mode,
            )
            if len(selected_interaction_types) > 1 and controls.interaction_attribution_mode == "primary_type_only":
                primary_type_attribution_row_count += 1

            preference_weight = parse_float(str(row.get("preference_weight_sum", ""))) or 0.0
            if preference_weight <= 0:
                continue
            interaction_count = int(parse_float(str(row.get("interaction_count_sum", ""))) or max(1, round(preference_weight * 10)))

            confidence, used_confidence_fallback = _resolve_confidence(row.get("match_confidence_score", ""))
            if used_confidence_fallback:
                confidence_fallback_count += 1
                if len(confidence_fallback_track_ids) < 50:
                    confidence_fallback_track_ids.append(trace_track_id)
            confidence_adjusted_weight = preference_weight * _resolve_confidence_weight_multiplier(
                confidence,
                controls.confidence_weighting_mode,
            )
            effective_weight = confidence_adjusted_weight
            confidence_adjusted_weight_sum += confidence_adjusted_weight
            if confidence >= high_confidence_threshold:
                confidence_bins["high_0_9_plus"] += 1
            elif confidence >= medium_confidence_threshold:
                confidence_bins["medium_0_5_to_0_9"] += 1
            else:
                confidence_bins["low_below_0_5"] += 1

            history_weight_component = parse_float(str(row.get("history_preference_weight_sum", "")))
            influence_weight_component = parse_float(str(row.get("influence_preference_weight_sum", "")))
            if history_weight_component is None and "history" in selected_interaction_types:
                history_weight_component = preference_weight * attribution_shares.get("history", 0.0)
            if influence_weight_component is None and "influence" in selected_interaction_types:
                influence_weight_component = preference_weight * attribution_shares.get("influence", 0.0)
            history_preference_weight_sum += max(0.0, history_weight_component or 0.0)
            influence_preference_weight_sum += max(0.0, influence_weight_component or 0.0)

            history_interaction_component = parse_float(str(row.get("history_interaction_count_sum", "")))
            influence_interaction_component = parse_float(str(row.get("influence_interaction_count_sum", "")))
            if history_interaction_component is None and "history" in selected_interaction_types:
                history_interaction_component = float(interaction_count) * attribution_shares.get("history", 0.0)
            if influence_interaction_component is None and "influence" in selected_interaction_types:
                influence_interaction_component = float(interaction_count) * attribution_shares.get("influence", 0.0)
            history_interaction_count_sum_value += max(0.0, history_interaction_component or 0.0)
            influence_interaction_count_sum_value += max(0.0, influence_interaction_component or 0.0)

            for selected_type, share in attribution_shares.items():
                attribution_weight_by_type[selected_type] = attribution_weight_by_type.get(selected_type, 0.0) + (effective_weight * share)
                attribution_interaction_count_by_type[selected_type] = attribution_interaction_count_by_type.get(selected_type, 0.0) + (float(interaction_count) * share)
                attribution_row_share_by_type[selected_type] = attribution_row_share_by_type.get(selected_type, 0.0) + share

            tags = parse_csv_labels(str(row.get("tags", "")))
            genres = parse_csv_labels(str(row.get("genres", "")))

            counts_by_type[interaction_type] = counts_by_type.get(interaction_type, 0) + 1
            weight_by_type[interaction_type] = weight_by_type.get(interaction_type, 0.0) + effective_weight
            interaction_count_sum_by_type[interaction_type] = interaction_count_sum_by_type.get(interaction_type, 0) + interaction_count

            for tag in tags:
                tag_weights[tag] = tag_weights.get(tag, 0.0) + effective_weight
            for genre in genres:
                genre_weights[genre] = genre_weights.get(genre, 0.0) + effective_weight

            row_has_numeric_value = False
            for column in NUMERIC_FEATURE_COLUMNS:
                parsed_value = parse_float(str(row.get(column, "")))
                if parsed_value is None:
                    continue
                row_has_numeric_value = True
                numeric_sums[column] += parsed_value * effective_weight
                numeric_weights[column] += effective_weight
                numeric_observations[column] += 1
                if column == "key":
                    angle = (parsed_value / 12.0) * 2.0 * math.pi
                    key_circular_sum_x += math.cos(angle) * effective_weight
                    key_circular_sum_y += math.sin(angle) * effective_weight

            if not row_has_numeric_value:
                if track_id:
                    missing_numeric_track_ids.append(track_id)
                else:
                    blank_track_id_row_count += 1

            lead_genre = _resolve_lead_genre(genres, tags)
            if lead_genre:
                lead_genre_weights[lead_genre] = lead_genre_weights.get(lead_genre, 0.0) + effective_weight

            seed_trace_rows.append(
                {
                    "event_id": f"ds001_seed_{index:06d}",
                    "track_id": trace_track_id,
                    "spotify_track_id": spotify_id,
                    "spotify_artist": str(row.get("artist", "")),
                    "spotify_title": str(row.get("song", "")),
                    "interaction_type": interaction_type,
                    "signal_source": "ds001_seed_table",
                    "seed_rank": index,
                    "interaction_count": interaction_count,
                    "preference_weight": round(preference_weight, 6),
                    "effective_weight": round(effective_weight, 6),
                    "lead_genre": lead_genre,
                    "top_tag": tags[0] if tags else "",
                    "numeric_feature_coverage": "1" if row_has_numeric_value else "0",
                    "lastfm_status": "not_applicable_ds001",
                }
            )

        total_effective_weight = sum(weight_by_type.values())
        matched_seed_count = len(seed_trace_rows)
        if not seed_trace_rows:
            requested_types = sorted(include_interaction_types)
            raise RuntimeError(
                "BL-004 produced no seed events after interaction-type filtering. "
                f"requested_include_interaction_types={requested_types}"
            )

        if sum(confidence_bins.values()) != matched_seed_count:
            raise RuntimeError(
                "BL-004 confidence bin accounting mismatch: "
                f"binned={sum(confidence_bins.values())} matched_seed_count={matched_seed_count}"
            )

        numeric_profile: dict[str, float] = {}
        for column in NUMERIC_FEATURE_COLUMNS:
            if numeric_weights[column] == 0:
                continue
            if column == "release":
                numeric_profile["release_year"] = round(numeric_sums[column] / numeric_weights[column], 6)
                continue
            if column == "key":
                circular_key = _circular_mean_key(key_circular_sum_x, key_circular_sum_y)
                if circular_key is None:
                    continue
                numeric_profile[column] = round(circular_key, 6)
                continue
            numeric_profile[column] = round(numeric_sums[column] / numeric_weights[column], 6)

        seed_trace_rows.sort(key=lambda row: int(str(row["seed_rank"])))
        return ProfileAggregation(
            input_row_count=len(inputs.seed_rows),
            seed_trace_rows=seed_trace_rows,
            numeric_profile=numeric_profile,
            tag_weights=tag_weights,
            genre_weights=genre_weights,
            lead_genre_weights=lead_genre_weights,
            counts_by_type=counts_by_type,
            weight_by_type=weight_by_type,
            interaction_count_sum_by_type=interaction_count_sum_by_type,
            numeric_observations=numeric_observations,
            missing_numeric_track_ids=missing_numeric_track_ids,
            blank_track_id_row_count=blank_track_id_row_count,
            total_effective_weight=total_effective_weight,
            confidence_adjusted_weight_sum=confidence_adjusted_weight_sum,
            confidence_bins=confidence_bins,
            match_method_counts=match_method_counts,
            history_preference_weight_sum=history_preference_weight_sum,
            influence_preference_weight_sum=influence_preference_weight_sum,
            history_interaction_count_sum=int(round(history_interaction_count_sum_value)),
            influence_interaction_count_sum=int(round(influence_interaction_count_sum_value)),
            matched_seed_count=matched_seed_count,
            mixed_interaction_row_count=mixed_interaction_row_count,
            primary_type_attribution_row_count=primary_type_attribution_row_count,
            attribution_weight_by_type=attribution_weight_by_type,
            attribution_interaction_count_by_type=attribution_interaction_count_by_type,
            attribution_row_share_by_type=attribution_row_share_by_type,
            confidence_fallback_count=confidence_fallback_count,
            confidence_fallback_track_ids=confidence_fallback_track_ids,
        )

    @staticmethod
    def write_seed_trace(seed_trace_path: Path, rows: list[dict[str, object]]) -> None:
        with open_text_write(seed_trace_path, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=SEED_TRACE_FIELDNAMES, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def build_profile_payload(
        *,
        run_id: str,
        controls: ProfileControls,
        paths: ProfilePaths,
        inputs: ProfileInputs,
        aggregation: ProfileAggregation,
        elapsed_seconds: float,
    ) -> dict[str, object]:
        canonical_blocks = _build_canonical_blocks(aggregation, controls, inputs)
        confidence_fallback_rate = _safe_rate(float(aggregation.confidence_fallback_count), float(aggregation.matched_seed_count), precision=6)
        diagnostics: dict[str, object] = {
            "events_total": aggregation.input_row_count,
            "matched_seed_count": aggregation.matched_seed_count,
            "missing_numeric_track_count": len(aggregation.missing_numeric_track_ids),
            "missing_numeric_track_ids": aggregation.missing_numeric_track_ids[:50],
            "blank_track_id_rows": aggregation.blank_track_id_row_count,
            "candidate_rows_total": aggregation.input_row_count,
            "numeric_observations": aggregation.numeric_observations,
            "key_aggregation_method": "weighted_circular_mean",
            "total_effective_weight": round(aggregation.total_effective_weight, 6),
            "confidence_adjusted_weight_sum": round(aggregation.confidence_adjusted_weight_sum, 6),
            "confidence_bins": dict(aggregation.confidence_bins),
            "match_method_counts": dict(aggregation.match_method_counts),
            "confidence_fallback_rows": aggregation.confidence_fallback_count,
            "confidence_fallback_rate": confidence_fallback_rate,
            "confidence_fallback_dominant": confidence_fallback_rate > 0.5,
            "confidence_fallback_track_ids": aggregation.confidence_fallback_track_ids,
            "bl003_source_rows_selected": dict(inputs.bl003_rows_selected),
            "bl003_source_rows_available": dict(inputs.bl003_rows_available),
            "elapsed_seconds": round(elapsed_seconds, 3),
        }
        if controls.emit_profile_policy_diagnostics:
            diagnostics["profile_policy_effective"] = {
                "confidence_weighting_mode": controls.confidence_weighting_mode,
                "confidence_bin_high_threshold": controls.confidence_bin_high_threshold,
                "confidence_bin_medium_threshold": controls.confidence_bin_medium_threshold,
                "interaction_attribution_mode": controls.interaction_attribution_mode,
            }
            diagnostics["profile_policy_impact"] = {
                "mixed_interaction_row_count": aggregation.mixed_interaction_row_count,
                "primary_type_attribution_row_count": aggregation.primary_type_attribution_row_count,
            }
        return {
            "run_id": run_id,
            "task": "BL-004",
            "profile_schema_version": BL004_PROFILE_SCHEMA_VERSION,
            "output_contract_version": BL004_OUTPUT_CONTRACT_VERSION,
            "generated_at_utc": utc_now(),
            "user_id": controls.user_id,
            "config_source": controls.config_source,
            "run_config_path": controls.run_config_path,
            "run_config_schema_version": controls.run_config_schema_version,
            "input_artifacts": {
                "seed_table_path": str(paths.seed_table_path),
                "seed_table_sha256": sha256_of_file(paths.seed_table_path),
                "bl003_summary_path": str(paths.bl003_summary_path),
                "bl003_manifest_path": str(paths.bl003_manifest_path),
                "bl003_seed_contract_hash": inputs.bl003_seed_contract_hash,
                "bl003_structural_contract_hash": inputs.bl003_structural_contract_hash,
            },
            "provenance": {
                "bl003_seed_contract": {
                    "schema_version": str(inputs.bl003_seed_contract.get("seed_contract_schema_version") or ""),
                    "contract_hash": inputs.bl003_seed_contract_hash,
                },
                "bl003_structural_contract": {
                    "schema_version": str(inputs.bl003_structural_contract.get("structural_contract_schema_version") or ""),
                    "contract_hash": inputs.bl003_structural_contract_hash,
                },
            },
            "config": {
                "input_scope": controls.input_scope,
                "effective_weight_rule": "effective_weight = preference_weight * (0.5 + 0.5 * clamp(match_confidence_score, 0, 1)); fallback confidence=1.0 when missing",
                "numeric_feature_columns": NUMERIC_FEATURE_COLUMNS,
                "profile_mode": "hybrid_semantic_numeric_from_bl003_enriched_seed_table",
                "top_tag_limit": controls.top_tag_limit,
                "top_genre_limit": controls.top_genre_limit,
                "top_lead_genre_limit": controls.top_lead_genre_limit,
                "profile_policy": {
                    "confidence_weighting_mode": controls.confidence_weighting_mode,
                    "confidence_bin_high_threshold": controls.confidence_bin_high_threshold,
                    "confidence_bin_medium_threshold": controls.confidence_bin_medium_threshold,
                    "interaction_attribution_mode": controls.interaction_attribution_mode,
                    "emit_profile_policy_diagnostics": controls.emit_profile_policy_diagnostics,
                },
                "aggregation_rules": {
                    "numeric": "weighted mean over numeric columns embedded in the BL-003 enriched seed table; key uses weighted circular mean on the 12-semitone wheel",
                    "tags": "sum(effective_weight) over DS-001 tag labels; weights are cumulative signal, not normalized probabilities",
                    "genres": "sum(effective_weight) over DS-001 genre labels; weights are cumulative signal, not normalized probabilities",
                    "lead_genres": "sum(effective_weight); weights are cumulative signal, not normalized probabilities",
                },
            },
            "diagnostics": diagnostics,
            "bl003_quality": canonical_blocks["bl003_quality"],
            "source_coverage": canonical_blocks["source_coverage"],
            "interaction_attribution": canonical_blocks["interaction_attribution"],
            "numeric_confidence": canonical_blocks["numeric_confidence"],
            "profile_signal_vector": canonical_blocks["profile_signal_vector"],
            "seed_summary": {
                "counts_by_interaction_type": aggregation.counts_by_type,
                "weight_by_interaction_type": {key: round(value, 6) for key, value in aggregation.weight_by_type.items()},
                "interaction_count_sum_by_interaction_type": aggregation.interaction_count_sum_by_type,
                "history_vs_influence": {
                    "preference_weight_sum": {
                        "history": round(aggregation.history_preference_weight_sum, 6),
                        "influence": round(aggregation.influence_preference_weight_sum, 6),
                    },
                    "interaction_count_sum": {
                        "history": aggregation.history_interaction_count_sum,
                        "influence": aggregation.influence_interaction_count_sum,
                    },
                },
                "seed_trace_path": str(paths.seed_trace_path),
            },
            "numeric_feature_profile": aggregation.numeric_profile,
            "semantic_profile": {
                "top_tags": _sorted_weight_map(aggregation.tag_weights, controls.top_tag_limit),
                "top_genres": _sorted_weight_map(aggregation.genre_weights, controls.top_genre_limit),
                "top_lead_genres": _sorted_weight_map(aggregation.lead_genre_weights, controls.top_lead_genre_limit),
            },
        }

    @staticmethod
    def build_summary_payload(
        *,
        run_id: str,
        controls: ProfileControls,
        paths: ProfilePaths,
        inputs: ProfileInputs,
        profile: dict[str, object],
        aggregation: ProfileAggregation,
    ) -> dict[str, object]:
        semantic_profile_obj = profile.get("semantic_profile")
        semantic_profile = semantic_profile_obj if isinstance(semantic_profile_obj, dict) else {}
        canonical_blocks = _build_canonical_blocks(aggregation, controls, inputs)
        source_coverage_obj = canonical_blocks.get("source_coverage")
        source_coverage: dict[str, object] = source_coverage_obj if isinstance(source_coverage_obj, dict) else {}
        bl003_quality_obj = canonical_blocks.get("bl003_quality")
        bl003_quality: dict[str, object] = bl003_quality_obj if isinstance(bl003_quality_obj, dict) else {}
        confidence_fallback_rate = _safe_rate(
            float(aggregation.confidence_fallback_count),
            float(aggregation.matched_seed_count),
            precision=6,
        )
        confidence_non_fallback_rate = round(1.0 - confidence_fallback_rate, 6)
        min_non_fallback_rate_warn_threshold = round(controls.min_non_fallback_rate_warn_threshold, 6)
        return {
            "run_id": run_id,
            "task": "BL-004",
            "summary_schema_version": BL004_SUMMARY_SCHEMA_VERSION,
            "output_contract_version": BL004_OUTPUT_CONTRACT_VERSION,
            "user_id": controls.user_id,
            "config_source": controls.config_source,
            "run_config_path": controls.run_config_path,
            "run_config_schema_version": controls.run_config_schema_version,
            "input_scope": controls.input_scope,
            "profile_policy": {
                "confidence_weighting_mode": controls.confidence_weighting_mode,
                "confidence_bin_high_threshold": controls.confidence_bin_high_threshold,
                "confidence_bin_medium_threshold": controls.confidence_bin_medium_threshold,
                "interaction_attribution_mode": controls.interaction_attribution_mode,
                "emit_profile_policy_diagnostics": controls.emit_profile_policy_diagnostics,
            },
            "matched_seed_count": aggregation.matched_seed_count,
            "total_effective_weight": round(aggregation.total_effective_weight, 6),
            "confidence_adjusted_weight_sum": round(aggregation.confidence_adjusted_weight_sum, 6),
            "match_method_counts": dict(aggregation.match_method_counts),
            "history_vs_influence": {
                "preference_weight_sum": {
                    "history": round(aggregation.history_preference_weight_sum, 6),
                    "influence": round(aggregation.influence_preference_weight_sum, 6),
                },
                "interaction_count_sum": {
                    "history": aggregation.history_interaction_count_sum,
                    "influence": aggregation.influence_interaction_count_sum,
                },
            },
            "dominant_lead_genres": list(semantic_profile.get("top_lead_genres", []))[:5],
            "dominant_tags": list(semantic_profile.get("top_tags", []))[:5],
            "dominant_genres": list(semantic_profile.get("top_genres", []))[:5],
            "feature_centers": {
                column: aggregation.numeric_profile[column]
                for column in SUMMARY_FEATURE_COLUMNS
                if column in aggregation.numeric_profile
            },
            "bl003_quality": canonical_blocks["bl003_quality"],
            "source_coverage": canonical_blocks["source_coverage"],
            "interaction_attribution": canonical_blocks["interaction_attribution"],
            "numeric_confidence": canonical_blocks["numeric_confidence"],
            "confidence_diagnostics": {
                "confidence_fallback_rows": aggregation.confidence_fallback_count,
                "confidence_fallback_rate": confidence_fallback_rate,
                "confidence_fallback_dominant": confidence_fallback_rate > 0.5,
                "confidence_fallback_warn_threshold": 0.5,
                "confidence_fallback_track_ids_sample": list(aggregation.confidence_fallback_track_ids[:10]),
            },
            "confidence_input_health": {
                "matched_seed_count": aggregation.matched_seed_count,
                "confidence_non_fallback_rate": confidence_non_fallback_rate,
                "min_non_fallback_rate_warn_threshold": min_non_fallback_rate_warn_threshold,
                "status": "warn" if confidence_non_fallback_rate < min_non_fallback_rate_warn_threshold else "pass",
            },
            "profile_signal_vector": canonical_blocks["profile_signal_vector"],
            "artifact_paths": {
                "profile_path": str(paths.profile_path),
                "seed_trace_path": str(paths.seed_trace_path),
                "bl003_summary_path": str(paths.bl003_summary_path),
                "bl003_manifest_path": str(paths.bl003_manifest_path),
            },
            "input_hashes": profile["input_artifacts"],
            "bl003_provenance": {
                "seed_contract_hash": inputs.bl003_seed_contract_hash,
                "structural_contract_hash": inputs.bl003_structural_contract_hash,
            },
            "bl003_coverage": {
                "rows_selected": _normalize_int_mapping(source_coverage.get("rows_selected")),
                "rows_available": _normalize_int_mapping(source_coverage.get("rows_available")),
                "match_counts": {str(key): value for key, value in bl003_quality.items()},
            },
        }

    @staticmethod
    def write_json(path: Path, payload: dict[str, object]) -> None:
        with open_text_write(path) as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True)

    @staticmethod
    def write_run_store(
        *,
        paths: ProfilePaths,
        run_id: str,
        profile: dict[str, object],
        summary: dict[str, object],
        seed_trace_rows: list[dict[str, object]],
    ) -> Path:
        pipeline_run_id = (os.getenv("BL_PIPELINE_RUN_ID") or "").strip()
        store_run_id = pipeline_run_id or run_id
        run_store_path = resolve_run_store_path(impl_root(), store_run_id)
        generated_at_utc = str(profile.get("generated_at_utc") or summary.get("generated_at_utc") or utc_now())

        with SQLiteRunStore(run_store_path) as run_store:
            run_store.upsert_run(
                run_id=store_run_id,
                created_at_utc=generated_at_utc,
                source_stage_id="BL-004",
            )
            stage_run_pk = run_store.insert_stage_run(
                run_id=store_run_id,
                stage_id="BL-004",
                stage_run_ref=run_id,
                generated_at_utc=generated_at_utc,
                status="pass",
                summary=summary,
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="seed_trace",
                artifact_type="csv",
                artifact_path=str(paths.seed_trace_path),
                sha256=sha256_of_file(paths.seed_trace_path),
                rows=seed_trace_rows,
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="profile",
                artifact_type="json",
                artifact_path=str(paths.profile_path),
                sha256=sha256_of_file(paths.profile_path),
                payload=profile,
            )
            run_store.insert_artifact(
                stage_run_pk=stage_run_pk,
                artifact_key="summary",
                artifact_type="json",
                artifact_path=str(paths.summary_path),
                sha256=sha256_of_file(paths.summary_path),
                payload=summary,
            )

        return run_store_path

    def run(self) -> ProfileArtifacts:
        paths = self.resolve_paths()
        paths.output_dir.mkdir(parents=True, exist_ok=True)
        controls = self.resolve_runtime_controls()
        inputs = self.load_inputs(paths)

        start_time = time.time()
        run_id = f"BL004-PROFILE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        aggregation = self.aggregate_inputs(inputs, controls)
        self.write_seed_trace(paths.seed_trace_path, aggregation.seed_trace_rows)

        profile = self.build_profile_payload(
            run_id=run_id,
            controls=controls,
            paths=paths,
            inputs=inputs,
            aggregation=aggregation,
            elapsed_seconds=time.time() - start_time,
        )
        self.write_json(paths.profile_path, profile)

        summary = self.build_summary_payload(
            run_id=run_id,
            controls=controls,
            paths=paths,
            inputs=inputs,
            profile=profile,
            aggregation=aggregation,
        )
        self.write_json(paths.summary_path, summary)

        run_store_path = self.write_run_store(
            paths=paths,
            run_id=run_id,
            profile=profile,
            summary=summary,
            seed_trace_rows=aggregation.seed_trace_rows,
        )
        summary["artifact_paths"] = {
            **{str(key): value for key, value in _mapping(summary.get("artifact_paths")).items()},
            "sqlite_run_store": str(run_store_path),
        }
        self.write_json(paths.summary_path, summary)

        confidence_fallback_rate = _safe_rate(float(aggregation.confidence_fallback_count), float(aggregation.matched_seed_count), precision=6)
        if confidence_fallback_rate > 0.5:
            logger.warning(
                "BL-004 confidence fallback dominated matched seeds: fallback_rows=%s matched_seed_count=%s",
                aggregation.confidence_fallback_count,
                aggregation.matched_seed_count,
            )

        logger.info("BL-004 preference profile created.")
        logger.info("profile=%s", paths.profile_path)
        logger.info("summary=%s", paths.summary_path)
        logger.info("seed_trace=%s", paths.seed_trace_path)
        return ProfileArtifacts(
            profile_path=paths.profile_path,
            summary_path=paths.summary_path,
            seed_trace_path=paths.seed_trace_path,
        )


def main() -> None:
    ProfileStage().run()


if __name__ == "__main__":
    main()
