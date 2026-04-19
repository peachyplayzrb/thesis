"""
Shared stage runtime resolution helpers.

Centralizes stage selection behavior used by orchestration and API layers.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any

PAYLOAD_SCHEMA_VERSION = "1.0"


def _parse_stage_payload(raw_payload: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def get_stage_payload() -> dict[str, Any] | None:
    """Load and parse BL_STAGE_CONFIG_JSON payload envelope from environment."""
    payload_raw = os.environ.get("BL_STAGE_CONFIG_JSON", "").strip()
    if not payload_raw:
        return None
    return _parse_stage_payload(payload_raw)


def get_stage_payload_controls(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract stage controls from payload envelope or legacy direct payload dict."""
    payload_controls = payload.get("controls")
    if isinstance(payload_controls, dict):
        return dict(payload_controls)
    return dict(payload)


def resolve_stage_selection(
    config: dict[str, Any],
    stage_specs: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Resolve and validate stage selection while preserving canonical order."""
    selected_raw = config.get("stage_ids", []) if isinstance(config, dict) else []
    all_ids = [spec["stage_id"] for spec in stage_specs]

    if not selected_raw:
        return [dict(spec) for spec in stage_specs]

    if not isinstance(selected_raw, list):
        raise RuntimeError("stage_ids must be an array of stage identifiers.")

    selected_set = {str(item).strip().lower() for item in selected_raw if str(item).strip()}
    if not selected_set:
        raise RuntimeError("At least one valid stage id is required.")

    unknown = sorted(selected_set.difference(all_ids))
    if unknown:
        raise RuntimeError(f"Unknown stage_ids: {', '.join(unknown)}")

    return [dict(spec) for spec in stage_specs if spec["stage_id"] in selected_set]


def resolve_run_config_path(env_var_name: str = "BL_RUN_CONFIG_PATH") -> str | None:
    """Resolve an optional run-config path from environment."""
    return os.environ.get(env_var_name, "").strip() or None


def load_positive_numeric_map_from_env(env_var_name: str) -> dict[str, float]:
    """
    Parse an environment JSON object and keep positive numeric values only.

    Returns an empty dictionary when the environment variable is missing,
    malformed, or not a JSON object.
    """
    raw = os.environ.get(env_var_name, "").strip()
    if not raw:
        return {}

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}

    if not isinstance(payload, dict):
        return {}

    return {
        str(k): float(v)
        for k, v in payload.items()
        if isinstance(v, (int, float)) and float(v) > 0
    }


def defaults_loader(controls_dict: dict[str, Any]) -> Callable[[], dict[str, Any]]:
    """Return a callable that yields clean payload defaults from a constants dict.

    Used as the ``load_payload_defaults`` argument to :func:`resolve_stage_controls`
    so that each stage no longer needs its own ``_load_blXXX_controls_defaults`` function.
    """
    def _load() -> dict[str, Any]:
        return {
            "config_source": "defaults",
            "run_config_path": None,
            "run_config_schema_version": None,
            **{k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
               for k, v in controls_dict.items()},
        }
    return _load


def resolve_stage_controls(
    *,
    load_from_env: Callable[[], dict[str, Any]],
    load_payload_defaults: Callable[[], dict[str, Any]] | None = None,
    sanitize: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    require_payload: bool = False,
) -> dict[str, Any]:
    """Resolve stage controls with payload-first precedence.

    Precedence:
    1) BL_STAGE_CONFIG_JSON (orchestration-injected payload)
    2) stage-local environment defaults
    """
    controls: dict[str, Any]
    payload = get_stage_payload()
    if payload is not None:
        payload_controls = get_stage_payload_controls(payload)
        if require_payload and not payload_controls:
            raise RuntimeError(
                "BL_STAGE_CONFIG_JSON payload does not contain stage controls"
            )
        payload_defaults_loader = load_payload_defaults or load_from_env
        controls = {**payload_defaults_loader(), **payload_controls}
    else:
        if require_payload:
            raise RuntimeError(
                "Missing or invalid BL_STAGE_CONFIG_JSON payload for strict stage execution"
            )
        controls = load_from_env()

    if sanitize is None:
        return controls
    return sanitize(controls)
