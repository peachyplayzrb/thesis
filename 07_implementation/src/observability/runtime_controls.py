"""Runtime control resolution for BL-009 observability."""

from __future__ import annotations

from observability.input_validation import normalize_validation_policy
from shared_utils.constants import (
    DEFAULT_BL009_HANDSHAKE_VALIDATION_POLICY,
    DEFAULT_CONTROL_MODE,
    DEFAULT_INPUT_SCOPE,
    DEFAULT_OBSERVABILITY_CONTROLS,
)
from shared_utils.env_utils import coerce_int, env_bool, env_int, env_str
from shared_utils.runtime_control_utils import (
    apply_payload_resolution_diagnostics,
    apply_run_config_paths,
    inspect_stage_payload_resolution,
    sanitize_runtime_control_context,
)
from shared_utils.stage_runtime_resolver import (
    defaults_loader,
    resolve_stage_controls,
)


def _load_bl009_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "control_mode": dict(DEFAULT_CONTROL_MODE),
        "input_scope": dict(DEFAULT_INPUT_SCOPE),
        "diagnostic_sample_limit": max(
            1,
            env_int(
                "BL009_DIAGNOSTIC_SAMPLE_LIMIT",
                int(DEFAULT_OBSERVABILITY_CONTROLS["diagnostic_sample_limit"]),
            ),
        ),
        "bootstrap_mode": env_bool(
            "BL009_BOOTSTRAP_MODE",
            bool(DEFAULT_OBSERVABILITY_CONTROLS["bootstrap_mode"]),
        ),
        "bl008_bl009_handshake_validation_policy": env_str(
            "BL009_BL008_HANDSHAKE_VALIDATION_POLICY",
            DEFAULT_BL009_HANDSHAKE_VALIDATION_POLICY,
        ),
    }


def _sanitize_bl009_controls(controls: dict[str, object]) -> dict[str, object]:
    controls = sanitize_runtime_control_context(
        controls,
        default_control_mode=DEFAULT_CONTROL_MODE,
        default_input_scope=DEFAULT_INPUT_SCOPE,
    )
    controls["diagnostic_sample_limit"] = max(
        1,
        coerce_int(
            controls.get("diagnostic_sample_limit", DEFAULT_OBSERVABILITY_CONTROLS["diagnostic_sample_limit"]),
            int(DEFAULT_OBSERVABILITY_CONTROLS["diagnostic_sample_limit"]),
        ),
    )
    controls["bootstrap_mode"] = bool(
        controls.get("bootstrap_mode", DEFAULT_OBSERVABILITY_CONTROLS["bootstrap_mode"])
    )
    controls["bl008_bl009_handshake_validation_policy"] = normalize_validation_policy(
        controls.get(
            "bl008_bl009_handshake_validation_policy",
            DEFAULT_BL009_HANDSHAKE_VALIDATION_POLICY,
        )
    )
    return controls


def resolve_bl009_runtime_controls() -> dict[str, object]:
    payload_status = inspect_stage_payload_resolution()

    controls = resolve_stage_controls(
        load_from_env=_load_bl009_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_OBSERVABILITY_CONTROLS),
        sanitize=_sanitize_bl009_controls,
    )
    controls = apply_payload_resolution_diagnostics(
        controls,
        stage_label="BL-009",
        payload_status=payload_status,
    )
    return apply_run_config_paths(controls)
