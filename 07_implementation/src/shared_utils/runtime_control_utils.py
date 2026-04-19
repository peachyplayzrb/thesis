"""Shared helpers for runtime-control normalization and resolution diagnostics."""

from __future__ import annotations

import os
from collections.abc import Mapping

from shared_utils.stage_runtime_resolver import get_stage_payload, resolve_run_config_path


def record_normalization_event(
    events: list[dict[str, object]],
    counts_by_field: dict[str, int],
    *,
    field: str,
    raw_value: object,
    normalized_value: object,
    reason: str,
) -> None:
    """Record a normalization event when a control value changes."""
    if raw_value == normalized_value:
        return
    counts_by_field[field] = counts_by_field.get(field, 0) + 1
    events.append(
        {
            "field": field,
            "reason": reason,
            "raw": raw_value,
            "normalized": normalized_value,
        }
    )


def apply_normalization_diagnostics(
    controls: dict[str, object],
    *,
    normalization_events: list[dict[str, object]],
    normalization_event_counts_by_field: dict[str, int],
) -> dict[str, object]:
    """Merge normalization diagnostics into a stage control payload."""
    diagnostics_existing = controls.get("runtime_control_resolution_diagnostics")
    diagnostics = dict(diagnostics_existing) if isinstance(diagnostics_existing, dict) else {}
    diagnostics.update(
        {
            "normalization_event_count": len(normalization_events),
            "normalization_event_counts_by_field": normalization_event_counts_by_field,
            "normalization_events_sampled": normalization_events[:10],
        }
    )
    controls["runtime_control_resolution_diagnostics"] = diagnostics
    return controls


def inspect_stage_payload_resolution() -> dict[str, object]:
    """Inspect BL_STAGE_CONFIG_JSON availability and parse status."""
    payload_json_raw = os.environ.get("BL_STAGE_CONFIG_JSON", "").strip()
    payload_present = False
    payload_json_parse_error = False
    if payload_json_raw:
        payload_present = get_stage_payload() is not None
        payload_json_parse_error = not payload_present
    return {
        "payload_json_raw": payload_json_raw,
        "payload_present": payload_present,
        "payload_json_parse_error": payload_json_parse_error,
        "resolution_path": "orchestration_payload" if payload_present else "environment",
    }


def apply_payload_resolution_diagnostics(
    controls: dict[str, object],
    *,
    stage_label: str,
    payload_status: dict[str, object],
) -> dict[str, object]:
    """Merge payload-resolution diagnostics and warnings into controls."""
    diagnostics_existing = controls.get("runtime_control_resolution_diagnostics")
    diagnostics = dict(diagnostics_existing) if isinstance(diagnostics_existing, dict) else {}
    diagnostics.update(
        {
            "payload_json_present": bool(payload_status.get("payload_json_raw")),
            "payload_json_parse_error": bool(payload_status.get("payload_json_parse_error")),
            "resolution_path": str(payload_status.get("resolution_path") or "environment"),
        }
    )
    controls["runtime_control_resolution_diagnostics"] = diagnostics

    warnings: list[str] = []
    warnings_existing = controls.get("runtime_control_validation_warnings")
    if isinstance(warnings_existing, list):
        warnings.extend(str(item) for item in warnings_existing)
    if payload_status.get("payload_json_parse_error"):
        warnings.append(
            f"BL_STAGE_CONFIG_JSON parse failed for {stage_label} controls; environment/default fallback path was used"
        )
    controls["runtime_control_validation_warnings"] = warnings
    return controls


def sanitize_runtime_control_context(
    controls: dict[str, object],
    *,
    default_control_mode: dict[str, object],
    default_input_scope: dict[str, object],
) -> dict[str, object]:
    """Normalize shared control-context keys for runtime-control payloads."""
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
        dict(control_mode_raw) if isinstance(control_mode_raw, Mapping) else dict(default_control_mode)
    )
    controls["input_scope"] = (
        dict(input_scope_raw) if isinstance(input_scope_raw, Mapping) else dict(default_input_scope)
    )
    return controls


def apply_run_config_paths(controls: dict[str, object]) -> dict[str, object]:
    """Attach optional run-intent and effective-config paths from environment."""
    controls["run_intent_path"] = resolve_run_config_path("BL_RUN_INTENT_PATH")
    controls["run_effective_config_path"] = resolve_run_config_path("BL_RUN_EFFECTIVE_CONFIG_PATH")
    return controls
