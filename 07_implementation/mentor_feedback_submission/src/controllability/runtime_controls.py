"""Runtime-control resolution for BL-011 controllability scenarios."""
from __future__ import annotations

from controllability.input_validation import normalize_validation_policy
from shared_utils.constants import (
    DEFAULT_BL011_BL010_VALIDATION_POLICY,
    DEFAULT_CONTROLLABILITY_CONTROLS,
    DEFAULT_SCENARIO_DEFINITIONS,
    DEFAULT_SCENARIO_POLICY,
)
from shared_utils.stage_runtime_resolver import resolve_stage_controls


def _load_bl011_controls_from_env() -> dict[str, object]:
    """Build BL-011 default controls when no orchestration payload is provided."""
    return {
        "config_source": "defaults",
        "run_config_path": None,
        **DEFAULT_CONTROLLABILITY_CONTROLS,
        "scenario_policy": dict(DEFAULT_SCENARIO_POLICY),
        "scenario_definitions": list(DEFAULT_SCENARIO_DEFINITIONS),
        "bl010_bl011_handshake_validation_policy": DEFAULT_BL011_BL010_VALIDATION_POLICY,
    }


def resolve_bl011_runtime_controls() -> dict[str, object]:
    """Resolve BL-011 controls and normalize validation-policy behavior."""
    controls = resolve_stage_controls(
        load_from_env=_load_bl011_controls_from_env,
        require_payload=True,
    )
    controls.setdefault("config_source", "orchestration_payload")
    controls.setdefault("run_config_path", None)
    controls.setdefault("scenario_policy", dict(DEFAULT_SCENARIO_POLICY))
    controls.setdefault("scenario_definitions", list(DEFAULT_SCENARIO_DEFINITIONS))
    controls["bl010_bl011_handshake_validation_policy"] = normalize_validation_policy(
        controls.get("bl010_bl011_handshake_validation_policy", DEFAULT_BL011_BL010_VALIDATION_POLICY)
    )
    return controls
