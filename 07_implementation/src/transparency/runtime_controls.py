"""Runtime control resolution for BL-008 transparency."""

from __future__ import annotations

from shared_utils.constants import (
    DEFAULT_BL008_HANDSHAKE_VALIDATION_POLICY,
    DEFAULT_TOP_CONTRIBUTOR_LIMIT,
    DEFAULT_TRANSPARENCY_CONTROLS,
)
from shared_utils.env_utils import coerce_float, coerce_int, env_bool, env_float, env_int, env_str
from shared_utils.runtime_control_utils import (
    apply_payload_resolution_diagnostics,
    inspect_stage_payload_resolution,
)
from shared_utils.stage_runtime_resolver import defaults_loader, resolve_stage_controls
from transparency.input_validation import normalize_validation_policy


def _sanitize_bl008_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["top_contributor_limit"] = max(1, coerce_int(controls.get("top_contributor_limit"), 3))
    controls["blend_primary_contributor_on_near_tie"] = bool(
        controls.get("blend_primary_contributor_on_near_tie", False)
    )
    controls["primary_contributor_tie_delta"] = max(
        0.0, min(1.0, coerce_float(controls.get("primary_contributor_tie_delta"), 0.02)),
    )
    controls["include_per_track_control_provenance"] = bool(
        controls.get("include_per_track_control_provenance", True)
    )
    controls["emit_run_level_control_provenance_summary"] = bool(
        controls.get("emit_run_level_control_provenance_summary", True)
    )
    controls["max_rejected_track_control_causality"] = max(
        0,
        coerce_int(controls.get("max_rejected_track_control_causality"), 500),
    )
    controls["bl007_bl008_handshake_validation_policy"] = normalize_validation_policy(
        controls.get("bl007_bl008_handshake_validation_policy", DEFAULT_BL008_HANDSHAKE_VALIDATION_POLICY)
    )
    return controls


def _load_bl008_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "top_contributor_limit": max(
            1,
            env_int("BL008_TOP_CONTRIBUTOR_LIMIT", DEFAULT_TOP_CONTRIBUTOR_LIMIT),
        ),
        "blend_primary_contributor_on_near_tie": env_bool(
            "BL008_BLEND_PRIMARY_CONTRIBUTOR_ON_NEAR_TIE", False
        ),
        "primary_contributor_tie_delta": env_float(
            "BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA", 0.02
        ),
        "include_per_track_control_provenance": env_bool(
            "BL008_INCLUDE_PER_TRACK_CONTROL_PROVENANCE", True
        ),
        "emit_run_level_control_provenance_summary": env_bool(
            "BL008_EMIT_RUN_LEVEL_CONTROL_PROVENANCE_SUMMARY", True
        ),
        "max_rejected_track_control_causality": env_int(
            "BL008_MAX_REJECTED_TRACK_CONTROL_CAUSALITY", 500
        ),
        "bl007_bl008_handshake_validation_policy": env_str(
            "BL008_BL007_HANDSHAKE_VALIDATION_POLICY", DEFAULT_BL008_HANDSHAKE_VALIDATION_POLICY
        ),
    }


def resolve_bl008_runtime_controls() -> dict[str, object]:
    """Resolve BL-008 controls with payload-first precedence."""
    payload_status = inspect_stage_payload_resolution()

    controls = resolve_stage_controls(
        load_from_env=_load_bl008_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_TRANSPARENCY_CONTROLS),
        sanitize=_sanitize_bl008_controls,
    )
    return apply_payload_resolution_diagnostics(
        controls,
        stage_label="BL-008",
        payload_status=payload_status,
    )
