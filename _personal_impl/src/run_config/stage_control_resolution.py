from __future__ import annotations

import json
import os
from typing import Any, Callable


def defaults_loader(controls_dict: dict[str, object]):
    def _load() -> dict[str, object]:
        return {
            "config_source": "defaults",
            "run_config_path": None,
            "run_config_schema_version": None,
            **{
                key: (dict(value) if isinstance(value, dict) else list(value) if isinstance(value, list) else value)
                for key, value in controls_dict.items()
            }
        }

    return _load


def _parse_stage_payload(raw_payload: str) -> dict[str, object] | None:
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return {str(key): value for key, value in payload.items()}


def _get_stage_payload() -> dict[str, object] | None:
    payload_raw = os.environ.get("BL_STAGE_CONFIG_JSON", "").strip()
    if not payload_raw:
        return None
    return _parse_stage_payload(payload_raw)


def resolve_stage_controls(
    *,
    load_from_env: Callable[[], dict[str, object]],
    load_payload_defaults: Callable[[], dict[str, object]] | None = None,
    sanitize: Callable[[dict[str, object]], dict[str, object]] | None = None,
    require_payload: bool = False,
) -> dict[str, object]:
    payload = _get_stage_payload()
    if payload is not None:
        payload_controls = payload.get("controls")
        if isinstance(payload_controls, dict):
            payload_controls_dict = {str(key): value for key, value in payload_controls.items()}
        else:
            payload_controls_dict = dict(payload)
        if require_payload and not payload_controls_dict:
            raise RuntimeError("BL_STAGE_CONFIG_JSON payload does not contain stage controls")
        defaults_loader_fn = load_payload_defaults or load_from_env
        controls = {**defaults_loader_fn(), **payload_controls_dict}
    else:
        if require_payload:
            raise RuntimeError("Missing or invalid BL_STAGE_CONFIG_JSON payload for strict stage execution")
        controls = load_from_env()
    return sanitize(controls) if sanitize is not None else controls
