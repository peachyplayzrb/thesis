"""
Shared stage runtime resolution helpers.

Centralizes stage selection behavior used by orchestration and API layers.
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List


def resolve_stage_selection(
    config: Dict[str, Any],
    stage_specs: List[Dict[str, str]],
) -> List[Dict[str, str]]:
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


def load_positive_numeric_map_from_env(env_var_name: str) -> Dict[str, float]:
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


def resolve_stage_controls(
    *,
    load_from_run_config: Callable[[Any, str], Dict[str, Any]],
    load_from_env: Callable[[], Dict[str, Any]],
    sanitize: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Resolve stage controls from run config when present, else environment defaults."""
    run_config_path = resolve_run_config_path()
    if run_config_path:
        from shared_utils.config_loader import load_run_config_utils_module

        run_config_utils = load_run_config_utils_module()
        controls = load_from_run_config(run_config_utils, run_config_path)
    else:
        controls = load_from_env()

    if sanitize is None:
        return controls
    return sanitize(controls)
