"""Runtime control resolution for BL-010 reproducibility."""

from __future__ import annotations

from typing import Mapping

from shared_utils.constants import (
    DEFAULT_BL010_BL009_VALIDATION_POLICY,
    DEFAULT_CONTROL_MODE,
    DEFAULT_INPUT_SCOPE,
)
from shared_utils.env_utils import env_str
from reproducibility.input_validation import normalize_validation_policy
from shared_utils.stage_runtime_resolver import resolve_run_config_path, resolve_stage_controls


DEFAULT_REPRODUCIBILITY_CONTROLS: dict[str, object] = {
    "config_source": "environment",
    "run_config_path": None,
    "run_config_schema_version": None,
    "control_mode": {},
    "input_scope": {},
    "bl009_bl010_handshake_validation_policy": DEFAULT_BL010_BL009_VALIDATION_POLICY,
}


def _load_bl010_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "control_mode": dict(DEFAULT_CONTROL_MODE),
        "input_scope": dict(DEFAULT_INPUT_SCOPE),
        "bl009_bl010_handshake_validation_policy": env_str(
            "BL010_BL009_HANDSHAKE_VALIDATION_POLICY",
            DEFAULT_BL010_BL009_VALIDATION_POLICY,
        ),
    }


def _sanitize_bl010_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["config_source"] = str(controls.get("config_source") or "environment")
    controls["run_config_path"] = (
        str(controls["run_config_path"]) if controls.get("run_config_path") else None
    )
    controls["run_config_schema_version"] = (
        str(controls["run_config_schema_version"])
        if controls.get("run_config_schema_version")
        else None
    )
    control_mode_raw = controls.get("control_mode")
    input_scope_raw = controls.get("input_scope")
    controls["control_mode"] = (
        dict(control_mode_raw) if isinstance(control_mode_raw, Mapping) else dict(DEFAULT_CONTROL_MODE)
    )
    controls["input_scope"] = (
        dict(input_scope_raw) if isinstance(input_scope_raw, Mapping) else dict(DEFAULT_INPUT_SCOPE)
    )
    controls["bl009_bl010_handshake_validation_policy"] = normalize_validation_policy(
        controls.get(
            "bl009_bl010_handshake_validation_policy",
            DEFAULT_BL010_BL009_VALIDATION_POLICY,
        )
    )
    return controls


def resolve_bl010_runtime_controls() -> dict[str, object]:
    run_intent_path = resolve_run_config_path("BL_RUN_INTENT_PATH")
    run_effective_config_path = resolve_run_config_path("BL_RUN_EFFECTIVE_CONFIG_PATH")
    controls = resolve_stage_controls(
        load_from_env=_load_bl010_controls_from_env,
        load_payload_defaults=lambda: dict(DEFAULT_REPRODUCIBILITY_CONTROLS),
        sanitize=_sanitize_bl010_controls,
    )
    controls["run_intent_path"] = run_intent_path
    controls["run_effective_config_path"] = run_effective_config_path
    return controls
