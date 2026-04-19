"""BL-003 seed freshness checking for BL-013 orchestration."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from alignment.constants import (
    ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION,
    ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION,
    MATCH_STRATEGY_ORDER,
)
from alignment.models import AlignmentBehaviorControls, AlignmentStructuralContract
from alignment.writers import (
    build_seed_contract_payload,
    build_structural_contract_payload,
    canonical_json_hash,
)
from orchestration.stage_registry import BL003_SUMMARY_PATH
from shared_utils.constants import DEFAULT_SEED_CONTROLS
from shared_utils.io_utils import load_json


def _normalize_weighting_policy(seed_controls: dict[str, Any]) -> dict[str, float]:
    raw_policy = seed_controls.get("weighting_policy") or {}
    if not isinstance(raw_policy, dict):
        raw_policy = {}

    top_tracks = raw_policy.get("top_tracks") or {}
    playlist_items = raw_policy.get("playlist_items") or {}
    if not isinstance(top_tracks, dict):
        top_tracks = {}
    if not isinstance(playlist_items, dict):
        playlist_items = {}

    return {
        "top_tracks_min_rank_floor": float(top_tracks.get("min_rank_floor", 0.05)),
        "top_tracks_scale_multiplier": float(top_tracks.get("scale_multiplier", 100.0)),
        "top_tracks_default_time_range_weight": float(top_tracks.get("default_time_range_weight", 0.2)),
        "playlist_items_min_position_floor": float(playlist_items.get("min_position_floor", 0.05)),
        "playlist_items_scale_multiplier": float(playlist_items.get("scale_multiplier", 20.0)),
    }


def _dict_or_empty(value: object) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _list_or_empty(value: object) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _build_fuzzy_matching_controls(seed_controls: dict[str, Any], fuzzy_defaults: dict[str, Any]) -> dict[str, Any]:
    fuzzy_matching = _dict_or_empty(seed_controls.get("fuzzy_matching"))
    return {
        "enabled": bool(fuzzy_matching.get("enabled", False)),
        "artist_threshold": float(fuzzy_matching.get("artist_threshold", fuzzy_defaults.get("artist_threshold", 0.90))),
        "title_threshold": float(fuzzy_matching.get("title_threshold", fuzzy_defaults.get("title_threshold", 0.90))),
        "combined_threshold": float(fuzzy_matching.get("combined_threshold", fuzzy_defaults.get("combined_threshold", 0.90))),
        "max_duration_delta_ms": int(fuzzy_matching.get("max_duration_delta_ms", fuzzy_defaults.get("max_duration_delta_ms", 5000))),
        "max_artist_candidates": int(fuzzy_matching.get("max_artist_candidates", fuzzy_defaults.get("max_artist_candidates", 5))),
    }


def _build_match_strategy(seed_controls: dict[str, Any], defaults: dict[str, Any]) -> dict[str, bool]:
    match_strategy = _dict_or_empty(seed_controls.get("match_strategy"))
    return {
        "enable_spotify_id_match": bool(match_strategy.get("enable_spotify_id_match", defaults.get("enable_spotify_id_match", True))),
        "enable_metadata_match": bool(match_strategy.get("enable_metadata_match", defaults.get("enable_metadata_match", True))),
        "enable_fuzzy_match": bool(match_strategy.get("enable_fuzzy_match", defaults.get("enable_fuzzy_match", True))),
    }


def _build_temporal_controls(seed_controls: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    temporal_controls = _dict_or_empty(seed_controls.get("temporal_controls"))
    return {
        "reference_mode": str(temporal_controls.get("reference_mode", defaults.get("reference_mode", "system"))),
        "reference_now_utc": temporal_controls.get("reference_now_utc", defaults.get("reference_now_utc")),
    }


def _build_aggregation_policy(seed_controls: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    aggregation_policy = _dict_or_empty(seed_controls.get("aggregation_policy"))
    return {
        "preference_weight_mode": str(aggregation_policy.get("preference_weight_mode", defaults.get("preference_weight_mode", "sum"))),
        "preference_weight_cap_per_event": aggregation_policy.get("preference_weight_cap_per_event", defaults.get("preference_weight_cap_per_event")),
    }


def _build_behavior_controls(
    input_scope: dict[str, Any],
    influence: dict[str, Any],
    seed_controls: dict[str, Any],
) -> AlignmentBehaviorControls:
    fuzzy_defaults = dict(DEFAULT_SEED_CONTROLS.get("fuzzy_matching") or {})
    match_strategy_defaults = dict(DEFAULT_SEED_CONTROLS.get("match_strategy") or {})
    temporal_defaults = dict(DEFAULT_SEED_CONTROLS.get("temporal_controls") or {})
    aggregation_defaults = dict(DEFAULT_SEED_CONTROLS.get("aggregation_policy") or {})
    match_strategy_order = _list_or_empty(seed_controls.get("match_strategy_order"))

    return AlignmentBehaviorControls(
        input_scope=dict(input_scope),
        top_range_weights=dict(seed_controls.get("top_range_weights") or {}),
        source_base_weights=dict(seed_controls.get("source_base_weights") or {}),
        source_resilience_policy={
            str(key): str(value).strip().lower()
            for key, value in (seed_controls.get("source_resilience_policy") or {}).items()
        },
        decay_half_lives=dict(seed_controls.get("decay_half_lives") or {}),
        match_rate_min_threshold=float(seed_controls.get("match_rate_min_threshold", 0.0)),
        fuzzy_matching_controls=_build_fuzzy_matching_controls(seed_controls, fuzzy_defaults),
        match_strategy=_build_match_strategy(seed_controls, match_strategy_defaults),
        match_strategy_order=list(match_strategy_order or MATCH_STRATEGY_ORDER),
        temporal_controls=_build_temporal_controls(seed_controls, temporal_defaults),
        aggregation_policy=_build_aggregation_policy(seed_controls, aggregation_defaults),
        weighting_policy=_normalize_weighting_policy(seed_controls),
        influence_controls={
            "influence_enabled": bool(influence.get("enabled", False)),
            "influence_track_ids": list(influence.get("track_ids") or []),
            "influence_preference_weight": float(influence.get("preference_weight", 1.0)),
        },
    )


def _strip_contract_hash(contract: Any) -> tuple[dict[str, Any], str]:
    if not isinstance(contract, dict):
        return {}, ""
    payload = dict(contract)
    raw_hash = payload.pop("contract_hash", "")
    return payload, str(raw_hash or "")


def _as_dict(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _validate_observed_source(observed: dict[str, object], run_config_path: Path) -> str | None:
    if str(observed.get("config_source") or "") != "run_config":
        return "BL-003 seed was not built in run_config mode"

    observed_path = observed.get("run_config_path")
    if observed_path and str(Path(str(observed_path)).resolve()) != str(run_config_path.resolve()):
        return "BL-003 seed was built with a different run_config path"
    return None


def _validate_contract_payload(
    *,
    expected_contract: dict[str, Any],
    observed_contract: dict[str, Any],
    expected_hash: str,
    observed_hash: str,
    schema_key: str,
    expected_schema_version: str,
    label: str,
) -> str | None:
    if not observed_contract:
        return f"BL-003 {label} missing from summary"

    observed_schema = str(observed_contract.get(schema_key) or "")
    if observed_schema != expected_schema_version:
        return f"BL-003 {label} schema version does not match current contract"

    if observed_hash and observed_hash != expected_hash:
        return f"BL-003 {label} hash does not match current contract"

    if observed_contract != expected_contract:
        return f"BL-003 {label} does not match current contract"

    return None


def _normalized_contract_from_effective(run_effective_config_path: Path) -> dict[str, object]:
    payload = load_json(run_effective_config_path)
    effective = payload.get("effective_config") or {}
    if not isinstance(effective, dict):
        effective = {}

    input_scope = effective.get("input_scope") or {}
    influence = effective.get("influence_tracks") or {}
    seed_controls = effective.get("seed_controls") or {}
    if not isinstance(input_scope, dict):
        input_scope = {}
    if not isinstance(influence, dict):
        influence = {}
    if not isinstance(seed_controls, dict):
        seed_controls = {}

    behavior_controls = _build_behavior_controls(input_scope, influence, seed_controls)
    structural_contract_model = AlignmentStructuralContract.from_defaults()
    seed_contract = build_seed_contract_payload(behavior_controls)
    structural_contract = build_structural_contract_payload(structural_contract_model)

    return {
        "seed_contract": seed_contract,
        "seed_contract_hash": canonical_json_hash(seed_contract),
        "structural_contract": structural_contract,
        "structural_contract_hash": canonical_json_hash(structural_contract),
    }


def _normalized_contract_from_bl003_summary(summary_path: Path) -> dict[str, object]:
    payload = load_json(summary_path)
    inputs = payload.get("inputs") or {}
    if not isinstance(inputs, dict):
        raise RuntimeError("BL-003 summary malformed: inputs block missing")

    raw_seed_contract = inputs.get("seed_contract") or {}
    if raw_seed_contract and not isinstance(raw_seed_contract, dict):
        raise RuntimeError("BL-003 summary malformed: seed_contract must be an object")
    seed_contract, seed_contract_hash = _strip_contract_hash(raw_seed_contract)
    raw_structural_contract = inputs.get("structural_contract") or {}
    if raw_structural_contract and not isinstance(raw_structural_contract, dict):
        raise RuntimeError("BL-003 summary malformed: structural_contract must be an object")
    structural_contract, structural_contract_hash = _strip_contract_hash(raw_structural_contract)

    if not isinstance(seed_contract, dict):
        seed_contract = {}
    if not isinstance(structural_contract, dict):
        structural_contract = {}

    return {
        "config_source": str(inputs.get("config_source") or ""),
        "run_config_path": inputs.get("run_config_path"),
        "seed_contract": seed_contract,
        "seed_contract_hash": seed_contract_hash,
        "structural_contract": structural_contract,
        "structural_contract_hash": structural_contract_hash,
    }


def validate_bl003_seed_freshness(
    root: Path,
    run_config_path: Path,
    run_effective_config_path: Path,
) -> tuple[bool, str]:
    summary_path = root / BL003_SUMMARY_PATH
    if not summary_path.exists():
        return False, "BL-003 summary missing; cannot validate seed freshness"

    expected = _normalized_contract_from_effective(run_effective_config_path)
    try:
        observed = _normalized_contract_from_bl003_summary(summary_path)
    except RuntimeError as exc:
        return False, str(exc)

    source_reason = _validate_observed_source(observed, run_config_path)
    if source_reason is not None:
        return False, source_reason

    expected_seed_contract = _as_dict(expected.get("seed_contract"))
    observed_seed_contract = _as_dict(observed.get("seed_contract"))
    expected_seed_hash = str(expected.get("seed_contract_hash") or "")
    observed_seed_hash = str(observed.get("seed_contract_hash") or "")
    seed_reason = _validate_contract_payload(
        expected_contract=expected_seed_contract,
        observed_contract=observed_seed_contract,
        expected_hash=expected_seed_hash,
        observed_hash=observed_seed_hash,
        schema_key="seed_contract_schema_version",
        expected_schema_version=ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION,
        label="seed contract",
    )
    if seed_reason is not None:
        return False, seed_reason

    expected_structural_contract = _as_dict(expected.get("structural_contract"))
    observed_structural_contract = _as_dict(observed.get("structural_contract"))
    expected_structural_hash = str(expected.get("structural_contract_hash") or "")
    observed_structural_hash = str(observed.get("structural_contract_hash") or "")
    structural_reason = _validate_contract_payload(
        expected_contract=expected_structural_contract,
        observed_contract=observed_structural_contract,
        expected_hash=expected_structural_hash,
        observed_hash=observed_structural_hash,
        schema_key="structural_contract_schema_version",
        expected_schema_version=ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION,
        label="structural contract",
    )
    if structural_reason is not None:
        return False, structural_reason

    return True, "ok"
