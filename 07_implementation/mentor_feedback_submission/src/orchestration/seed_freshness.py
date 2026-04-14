"""Seed freshness checks used by BL-013 orchestration."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from alignment.constants import ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION, ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION, MATCH_STRATEGY_ORDER
from alignment.models import AlignmentBehaviorControls, AlignmentStructuralContract
from alignment.writers import build_seed_contract_payload, build_structural_contract_payload, canonical_json_hash
from shared_utils.constants import DEFAULT_SEED_CONTROLS
from shared_utils.io_utils import load_json
from orchestration.stage_registry import BL003_SUMMARY_PATH


def _normalize_weighting_policy(seed_controls: dict[str, Any]) -> dict[str, float]:
    """Coerce weighting-policy controls into a stable numeric mapping."""
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


def _build_behavior_controls(
    input_scope: dict[str, Any],
    influence: dict[str, Any],
    seed_controls: dict[str, Any],
) -> AlignmentBehaviorControls:
    """Build behavior controls from effective run-config sections."""
    fuzzy_defaults = dict(DEFAULT_SEED_CONTROLS.get("fuzzy_matching") or {})
    match_strategy_defaults = dict(DEFAULT_SEED_CONTROLS.get("match_strategy") or {})
    temporal_defaults = dict(DEFAULT_SEED_CONTROLS.get("temporal_controls") or {})
    aggregation_defaults = dict(DEFAULT_SEED_CONTROLS.get("aggregation_policy") or {})

    fuzzy_matching = seed_controls.get("fuzzy_matching") or {}
    match_strategy = seed_controls.get("match_strategy") or {}
    match_strategy_order = seed_controls.get("match_strategy_order") or []
    temporal_controls = seed_controls.get("temporal_controls") or {}
    aggregation_policy = seed_controls.get("aggregation_policy") or {}

    if not isinstance(fuzzy_matching, dict):
        fuzzy_matching = {}
    if not isinstance(match_strategy, dict):
        match_strategy = {}
    if not isinstance(match_strategy_order, list):
        match_strategy_order = []
    if not isinstance(temporal_controls, dict):
        temporal_controls = {}
    if not isinstance(aggregation_policy, dict):
        aggregation_policy = {}

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
        fuzzy_matching_controls={
            "enabled": bool(fuzzy_matching.get("enabled", False)),
            "artist_threshold": float(fuzzy_matching.get("artist_threshold", fuzzy_defaults.get("artist_threshold", 0.90))),
            "title_threshold": float(fuzzy_matching.get("title_threshold", fuzzy_defaults.get("title_threshold", 0.90))),
            "combined_threshold": float(fuzzy_matching.get("combined_threshold", fuzzy_defaults.get("combined_threshold", 0.90))),
            "max_duration_delta_ms": int(fuzzy_matching.get("max_duration_delta_ms", fuzzy_defaults.get("max_duration_delta_ms", 5000))),
            "max_artist_candidates": int(fuzzy_matching.get("max_artist_candidates", fuzzy_defaults.get("max_artist_candidates", 5))),
        },
        match_strategy={
            "enable_spotify_id_match": bool(match_strategy.get("enable_spotify_id_match", match_strategy_defaults.get("enable_spotify_id_match", True))),
            "enable_metadata_match": bool(match_strategy.get("enable_metadata_match", match_strategy_defaults.get("enable_metadata_match", True))),
            "enable_fuzzy_match": bool(match_strategy.get("enable_fuzzy_match", match_strategy_defaults.get("enable_fuzzy_match", True))),
        },
        match_strategy_order=list(match_strategy_order or MATCH_STRATEGY_ORDER),
        temporal_controls={
            "reference_mode": str(temporal_controls.get("reference_mode", temporal_defaults.get("reference_mode", "system"))),
            "reference_now_utc": temporal_controls.get("reference_now_utc", temporal_defaults.get("reference_now_utc")),
        },
        aggregation_policy={
            "preference_weight_mode": str(aggregation_policy.get("preference_weight_mode", aggregation_defaults.get("preference_weight_mode", "sum"))),
            "preference_weight_cap_per_event": aggregation_policy.get("preference_weight_cap_per_event", aggregation_defaults.get("preference_weight_cap_per_event")),
        },
        weighting_policy=_normalize_weighting_policy(seed_controls),
        influence_controls={
            "influence_enabled": bool(influence.get("enabled", False)),
            "influence_track_ids": list(influence.get("track_ids") or []),
            "influence_preference_weight": float(influence.get("preference_weight", 1.0)),
        },
    )


def _strip_contract_hash(contract: Any) -> tuple[dict[str, Any], str]:
    """Split a contract object into payload and optional hash."""
    if not isinstance(contract, dict):
        return {}, ""
    payload = dict(contract)
    raw_hash = payload.pop("contract_hash", "")
    return payload, str(raw_hash or "")


def _as_dict(value: object) -> dict[str, Any]:
    """Return a shallow dict copy when the input is a mapping."""
    if isinstance(value, dict):
        return dict(value)
    return {}


def _normalized_contract_from_effective(run_effective_config_path: Path) -> dict[str, object]:
    """Rebuild expected contracts from the effective run-config artifact."""
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
    """Read observed contracts from the BL-003 summary artifact."""
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
    """Compare observed BL-003 contracts against current effective controls."""
    summary_path = root / BL003_SUMMARY_PATH
    if not summary_path.exists():
        return False, "BL-003 summary missing; cannot validate seed freshness"

    expected = _normalized_contract_from_effective(run_effective_config_path)
    try:
        observed = _normalized_contract_from_bl003_summary(summary_path)
    except RuntimeError as exc:
        return False, str(exc)

    if str(observed.get("config_source") or "") != "run_config":
        return False, "BL-003 seed was not built in run_config mode"

    observed_path = observed.get("run_config_path")
    if observed_path and str(Path(str(observed_path)).resolve()) != str(run_config_path.resolve()):
        return False, "BL-003 seed was built with a different run_config path"

    expected_seed_contract = _as_dict(expected.get("seed_contract"))
    observed_seed_contract = _as_dict(observed.get("seed_contract"))
    if not observed_seed_contract:
        return False, "BL-003 seed contract missing from summary"

    if str(observed_seed_contract.get("seed_contract_schema_version") or "") != ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION:
        return False, "BL-003 seed contract schema version does not match current contract"

    expected_seed_hash = str(expected.get("seed_contract_hash") or "")
    observed_seed_hash = str(observed.get("seed_contract_hash") or "")
    if observed_seed_hash and observed_seed_hash != expected_seed_hash:
        return False, "BL-003 seed contract hash does not match current effective run_config"

    if observed_seed_contract != expected_seed_contract:
        return False, "BL-003 seed contract does not match current effective run_config"

    expected_structural_contract = _as_dict(expected.get("structural_contract"))
    observed_structural_contract = _as_dict(observed.get("structural_contract"))
    if not observed_structural_contract:
        return False, "BL-003 structural contract missing from summary"

    if str(observed_structural_contract.get("structural_contract_schema_version") or "") != ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION:
        return False, "BL-003 structural contract schema version does not match current contract"

    expected_structural_hash = str(expected.get("structural_contract_hash") or "")
    observed_structural_hash = str(observed.get("structural_contract_hash") or "")
    if observed_structural_hash and observed_structural_hash != expected_structural_hash:
        return False, "BL-003 structural contract hash does not match current contract"

    if observed_structural_contract != expected_structural_contract:
        return False, "BL-003 structural contract does not match current contract"

    return True, "ok"
