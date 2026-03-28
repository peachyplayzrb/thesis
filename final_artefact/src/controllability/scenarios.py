from __future__ import annotations

import os
from pathlib import Path

from shared_utils.config_loader import load_run_config_utils_module
from shared_utils.stage_utils import relpath

from .weights import normalize_component_weight_keys, normalized_weights_with_override


def build_paths(root: Path) -> dict[str, Path]:
    return {
        "legacy_manifest": root / "test_assets" / "bl016_asset_manifest.json",
        "legacy_coverage": root / "data_layer" / "outputs" / "onion_join_coverage_report.json",
        "active_seed_trace": root / "profile" / "outputs" / "bl004_seed_trace.csv",
        "active_candidates": root / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv",
        "baseline_snapshot": root / "reproducibility" / "outputs" / "reproducibility_config_snapshot.json",
        "output_dir": root / "controllability" / "outputs",
    }


def resolve_bl011_runtime_controls() -> dict[str, object]:
    rc_utils = load_run_config_utils_module()
    controls: dict[str, object] = {
        "config_source": "defaults",
        "run_config_path": None,
        **rc_utils.resolve_bl011_controls(None),
    }
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    if run_config_path:
        resolved = rc_utils.resolve_bl011_controls(run_config_path)
        controls.update(resolved)
        controls["config_source"] = "run_config"
        controls["run_config_path"] = run_config_path
    return controls


def ensure_required_inputs(paths: dict[str, Path], root: Path) -> None:
    required = ["baseline_snapshot", "active_seed_trace", "active_candidates"]
    missing = [relpath(paths[key], root) for key in required if not paths[key].exists()]
    if missing:
        raise FileNotFoundError(f"BL-011 missing required inputs: {missing}")


def build_scenarios(baseline_snapshot: dict, runtime_controls: dict[str, object]) -> list[dict[str, object]]:
    base_profile = baseline_snapshot["stage_configs"]["profile"]
    base_retrieval = baseline_snapshot["stage_configs"]["retrieval"]
    base_scoring = baseline_snapshot["stage_configs"]["scoring"]
    base_assembly = baseline_snapshot["stage_configs"]["assembly"]
    scoring_weights = dict(
        base_scoring.get("component_weights")
        or base_scoring.get("active_component_weights")
        or base_scoring.get("base_component_weights")
        or {}
    )
    scoring_weights = normalize_component_weight_keys(scoring_weights)
    if not scoring_weights:
        raise RuntimeError("BL-011 could not resolve scoring component weights from baseline snapshot")
    override_if_present = float(runtime_controls["weight_override_value_if_component_present"])
    override_increment_fallback = float(runtime_controls["weight_override_increment_fallback"])
    override_cap_fallback = float(runtime_controls["weight_override_cap_fallback"])
    stricter_threshold_scale = float(runtime_controls["stricter_threshold_scale"])
    looser_threshold_scale = float(runtime_controls["looser_threshold_scale"])
    if "valence" in scoring_weights:
        override_component = "valence"
        override_raw_value = override_if_present
    elif "V_mean" in scoring_weights:
        override_component = "V_mean"
        override_raw_value = override_if_present
    else:
        override_component = next(iter(scoring_weights.keys()))
        override_raw_value = min(override_cap_fallback, float(scoring_weights[override_component]) + override_increment_fallback)

    return [
        {
            "scenario_id": "baseline",
            "test_id": "baseline",
            "control_surface": "fixed_bl010_baseline",
            "description": "BL-010 fixed baseline carried forward unchanged for BL-011 comparisons.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": 1.0,
            },
            "scoring": {
                **base_scoring,
                "weight_override_component": None,
                "raw_override_value": None,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "reference",
        },
        {
            "scenario_id": "no_influence_tracks",
            "test_id": "EP-CTRL-001",
            "control_surface": "influence_tracks",
            "description": "Disable influence-track interactions while keeping all other inputs and parameters fixed.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": 1.0,
            },
            "scoring": {
                **base_scoring,
                "weight_override_component": None,
                "raw_override_value": None,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "profile and ranking shift away from influence-steered indie/alternative emphasis",
        },
        {
            "scenario_id": "valence_weight_up",
            "test_id": "EP-CTRL-002",
            "control_surface": "feature_weight",
            "description": "Increase one score-component raw weight and renormalize all score weights to preserve a 1.0 total.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": 1.0,
            },
            "scoring": {
                **base_scoring,
                "component_weights": normalized_weights_with_override(scoring_weights, override_component, override_raw_value),
                "weight_override_component": override_component,
                "raw_override_value": override_raw_value,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "tracks with stronger fit on the boosted component should gain score contribution and rank position",
        },
        {
            "scenario_id": "stricter_thresholds",
            "test_id": "EP-CTRL-003",
            "control_surface": "candidate_threshold",
            "description": f"Tighten all numeric retrieval thresholds by multiplying them by {stricter_threshold_scale:.2f}.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": stricter_threshold_scale,
            },
            "scoring": {
                **base_scoring,
                "weight_override_component": None,
                "raw_override_value": None,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "candidate pool should shrink and playlist overlap should reduce or reorder",
        },
        {
            "scenario_id": "looser_thresholds",
            "test_id": "EP-CTRL-003",
            "control_surface": "candidate_threshold",
            "description": f"Loosen all numeric retrieval thresholds by multiplying them by {looser_threshold_scale:.2f}.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": looser_threshold_scale,
            },
            "scoring": {
                **base_scoring,
                "weight_override_component": None,
                "raw_override_value": None,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "candidate pool should expand and downstream ranking or playlist composition should change",
        },
    ]
