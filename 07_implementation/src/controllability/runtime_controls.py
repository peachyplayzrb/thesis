"""Runtime control resolution for BL-011 controllability."""
from __future__ import annotations

from shared_utils.constants import (
    DEFAULT_CONTROLLABILITY_CONTROLS,
    DEFAULT_SCENARIO_DEFINITIONS,
    DEFAULT_SCENARIO_POLICY,
)
from shared_utils.stage_runtime_resolver import resolve_stage_controls


def _load_bl011_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "defaults",
        "run_config_path": None,
        **DEFAULT_CONTROLLABILITY_CONTROLS,
        "scenario_policy": dict(DEFAULT_SCENARIO_POLICY),
        "scenario_definitions": list(DEFAULT_SCENARIO_DEFINITIONS),
    }


def resolve_bl011_runtime_controls() -> dict[str, object]:
    controls = resolve_stage_controls(
        load_from_env=_load_bl011_controls_from_env,
        require_payload=True,
    )
    controls.setdefault("config_source", "orchestration_payload")
    controls.setdefault("run_config_path", None)
    controls.setdefault("scenario_policy", dict(DEFAULT_SCENARIO_POLICY))
    controls.setdefault("scenario_definitions", list(DEFAULT_SCENARIO_DEFINITIONS))
    return controls
