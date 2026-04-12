from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from shared_utils.config_loader import load_run_config_utils_module
from shared_utils.stage_runtime_resolver import PAYLOAD_SCHEMA_VERSION


def _build_stage_payload(
    *,
    stage_id: str,
    run_config_path: Path | None,
    controls: Mapping[str, object],
) -> dict[str, object]:
    return {
        "stage_id": stage_id,
        "schema_version": PAYLOAD_SCHEMA_VERSION,
        "resolved_from": "run_config" if run_config_path else "defaults",
        "controls": dict(controls),
    }


def resolve_orchestration_controls(run_config_path: Path | None) -> dict[str, Any]:
    """Resolve BL-013 orchestration controls from run-config/defaults."""
    run_config_utils = load_run_config_utils_module()
    return run_config_utils.resolve_bl013_orchestration_controls(
        str(run_config_path) if run_config_path else None
    )


def emit_run_config_artifact_pair(
    *,
    run_id: str,
    run_config_path: Path | None,
    artifact_dir: Path,
    generated_at_utc: str,
) -> dict[str, object]:
    """Write run-intent and run-effective-config artifacts for BL-013."""
    run_config_utils = load_run_config_utils_module()
    return run_config_utils.write_run_config_artifact_pair(
        run_id=run_id,
        output_dir=artifact_dir,
        run_config_path=run_config_path,
        generated_at_utc=generated_at_utc,
    )


def resolve_stage_control_payload(stage_id: str, run_config_path: Path | None) -> dict[str, object]:
    """Resolve one stage's control payload for BL_STAGE_CONFIG_JSON handoff.

    This is additive/backward-compatible: stages may ignore this payload today.
    """
    run_config_utils = load_run_config_utils_module()
    rc_path = str(run_config_path) if run_config_path else None

    if stage_id == "BL-002":
        controls = {
            "ingestion_controls": dict(run_config_utils.resolve_ingestion_controls(rc_path)),
        }
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=controls,
        )
    if stage_id == "BL-003":
        input_scope = run_config_utils.resolve_input_scope_controls(rc_path)
        controls = {
            "input_scope_controls": dict(input_scope),
            "seed_controls": dict(run_config_utils.resolve_bl003_seed_controls(rc_path)),
            "weighting_policy": dict(run_config_utils.resolve_bl003_weighting_policy(rc_path)),
            "influence_controls": dict(run_config_utils.resolve_bl003_influence_controls(rc_path)),
        }
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=controls,
        )
    if stage_id == "BL-004":
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=dict(run_config_utils.resolve_bl004_controls(rc_path)),
        )
    if stage_id == "BL-005":
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=dict(run_config_utils.resolve_bl005_controls(rc_path)),
        )
    if stage_id == "BL-006":
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=dict(run_config_utils.resolve_bl006_controls(rc_path)),
        )
    if stage_id == "BL-007":
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=dict(run_config_utils.resolve_bl007_controls(rc_path)),
        )
    if stage_id == "BL-008":
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=dict(run_config_utils.resolve_bl008_controls(rc_path)),
        )
    if stage_id == "BL-009":
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=dict(run_config_utils.resolve_bl009_controls(rc_path)),
        )
    if stage_id == "BL-011":
        scenario_policy, scenario_definitions = run_config_utils.resolve_bl011_scenario_policy(rc_path)
        controls = dict(run_config_utils.resolve_bl011_controls(rc_path))
        controls["scenario_policy"] = scenario_policy
        controls["scenario_definitions"] = scenario_definitions
        return _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=controls,
        )
    return {}


def resolve_stage_control_payloads(
    stage_order: list[str],
    run_config_path: Path | None,
    *,
    include_stage_ids: list[str] | None = None,
) -> dict[str, dict[str, object]]:
    """Resolve controls for all stages in run order for orchestration handoff."""
    ordered_stage_ids: list[str] = []
    for stage_id in stage_order:
        if stage_id not in ordered_stage_ids:
            ordered_stage_ids.append(stage_id)
    for stage_id in include_stage_ids or []:
        if stage_id not in ordered_stage_ids:
            ordered_stage_ids.append(stage_id)

    return {
        stage_id: resolve_stage_control_payload(stage_id, run_config_path)
        for stage_id in ordered_stage_ids
    }
