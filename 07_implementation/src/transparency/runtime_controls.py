"""Runtime control resolution for BL-008 transparency."""

from __future__ import annotations

from shared_utils.constants import DEFAULT_TOP_CONTRIBUTOR_LIMIT
from shared_utils.env_utils import env_bool, env_float, env_int
from shared_utils.stage_runtime_resolver import resolve_stage_controls


def _sanitize_bl008_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["top_contributor_limit"] = max(1, int(controls["top_contributor_limit"]))
    controls["blend_primary_contributor_on_near_tie"] = bool(
        controls["blend_primary_contributor_on_near_tie"]
    )
    controls["primary_contributor_tie_delta"] = max(
        0.0,
        min(1.0, float(controls["primary_contributor_tie_delta"])),
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
    }


def resolve_bl008_runtime_controls() -> dict[str, object]:
    """Resolve BL-008 controls from run config first, then environment defaults."""
    return resolve_stage_controls(
        load_from_env=_load_bl008_controls_from_env,
        sanitize=_sanitize_bl008_controls,
    )
