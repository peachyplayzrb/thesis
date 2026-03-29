"""BL-003 seed freshness checking for BL-013 orchestration."""
from __future__ import annotations

from pathlib import Path

from shared_utils.io_utils import load_json
from orchestration.stage_registry import BL003_SUMMARY_PATH


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

    fuzzy_matching = seed_controls.get("fuzzy_matching") or {}
    if not isinstance(fuzzy_matching, dict):
        fuzzy_matching = {}

    return {
        "input_scope": input_scope,
        "influence_tracks": {
            "enabled": bool(influence.get("enabled", False)),
            "track_ids": list(influence.get("track_ids") or []),
            "preference_weight": float(influence.get("preference_weight") or 1.0),
        },
        "fuzzy_matching": {
            "enabled": bool(fuzzy_matching.get("enabled", False)),
            "artist_threshold": float(fuzzy_matching.get("artist_threshold") or 0.90),
            "title_threshold": float(fuzzy_matching.get("title_threshold") or 0.90),
            "combined_threshold": float(fuzzy_matching.get("combined_threshold") or 0.90),
            "max_duration_delta_ms": int(fuzzy_matching.get("max_duration_delta_ms") or 5000),
            "max_artist_candidates": int(fuzzy_matching.get("max_artist_candidates") or 5),
        },
    }


def _normalized_contract_from_bl003_summary(summary_path: Path) -> dict[str, object]:
    payload = load_json(summary_path)
    inputs = payload.get("inputs") or {}
    if not isinstance(inputs, dict):
        raise RuntimeError("BL-003 summary malformed: inputs block missing")

    seed_contract = inputs.get("seed_contract") or {}
    if isinstance(seed_contract, dict) and seed_contract:
        input_scope = seed_contract.get("input_scope") or {}
        influence = seed_contract.get("influence_tracks") or {}
        fuzzy_matching = seed_contract.get("fuzzy_matching") or {}
    else:
        # Backward-compat for older summaries before seed_contract was introduced.
        input_scope = inputs.get("input_scope") or {}
        influence = inputs.get("influence_tracks") or {}
        fuzzy_matching = {}

    if not isinstance(input_scope, dict):
        input_scope = {}
    if not isinstance(influence, dict):
        influence = {}
    if not isinstance(fuzzy_matching, dict):
        fuzzy_matching = {}

    return {
        "config_source": str(inputs.get("config_source") or ""),
        "run_config_path": inputs.get("run_config_path"),
        "input_scope": input_scope,
        "influence_tracks": {
            "enabled": bool(influence.get("enabled", False)),
            "track_ids": list(influence.get("track_ids") or []),
            "preference_weight": float(influence.get("preference_weight") or 1.0),
        },
        "fuzzy_matching": {
            "enabled": bool(fuzzy_matching.get("enabled", False)),
            "artist_threshold": float(fuzzy_matching.get("artist_threshold") or 0.90),
            "title_threshold": float(fuzzy_matching.get("title_threshold") or 0.90),
            "combined_threshold": float(fuzzy_matching.get("combined_threshold") or 0.90),
            "max_duration_delta_ms": int(fuzzy_matching.get("max_duration_delta_ms") or 5000),
            "max_artist_candidates": int(fuzzy_matching.get("max_artist_candidates") or 5),
        },
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
    observed = _normalized_contract_from_bl003_summary(summary_path)

    if observed["config_source"] != "run_config":
        return False, "BL-003 seed was not built in run_config mode"

    observed_path = observed.get("run_config_path")
    if observed_path and str(Path(str(observed_path)).resolve()) != str(run_config_path.resolve()):
        return False, "BL-003 seed was built with a different run_config path"

    if observed["input_scope"] != expected["input_scope"]:
        return False, "BL-003 input_scope does not match current effective run_config"

    if observed["influence_tracks"] != expected["influence_tracks"]:
        return False, "BL-003 influence_tracks contract does not match current effective run_config"

    if observed.get("fuzzy_matching") != expected.get("fuzzy_matching"):
        return False, "BL-003 fuzzy_matching contract does not match current effective run_config"

    return True, "ok"
