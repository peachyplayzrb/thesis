"""Runtime control resolution for BL-010 reproducibility."""

from __future__ import annotations

from reproducibility.input_validation import normalize_validation_policy
from shared_utils.constants import (
    DEFAULT_BL010_BL009_VALIDATION_POLICY,
    DEFAULT_CONTROL_MODE,
    DEFAULT_INPUT_SCOPE,
)
from shared_utils.env_utils import env_str
from shared_utils.runtime_control_utils import (
    apply_run_config_paths,
    sanitize_runtime_control_context,
)
from shared_utils.stage_runtime_resolver import resolve_stage_controls

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
    controls = sanitize_runtime_control_context(
        controls,
        default_control_mode=DEFAULT_CONTROL_MODE,
        default_input_scope=DEFAULT_INPUT_SCOPE,
    )
    controls["bl009_bl010_handshake_validation_policy"] = normalize_validation_policy(
        controls.get(
            "bl009_bl010_handshake_validation_policy",
            DEFAULT_BL010_BL009_VALIDATION_POLICY,
        )
    )
    return controls


def resolve_bl010_runtime_controls() -> dict[str, object]:
    controls = resolve_stage_controls(
        load_from_env=_load_bl010_controls_from_env,
        load_payload_defaults=lambda: dict(DEFAULT_REPRODUCIBILITY_CONTROLS),
        sanitize=_sanitize_bl010_controls,
    )
    return apply_run_config_paths(controls)
