"""Input validation for BL-010 baseline snapshot - BL-010 baseline structure contract."""

from __future__ import annotations

from typing import Any

from shared_utils.validation_policy import normalize_validation_policy, resolve_policy_status

REQUIRED_BASELINE_SNAPSHOT_TOP_KEYS: tuple[str, ...] = (
    "stage_configs",
    "replay_count",
    "fixed_inputs",
    "stage_order",
)

REQUIRED_STAGE_CONFIGS_SUB_KEYS: tuple[str, ...] = (
    "profile",
    "retrieval",
    "scoring",
    "assembly",
)


def validate_bl010_baseline_snapshot(
    snapshot: Any,
    policy: str,
) -> dict[str, object]:
    """Validate BL-010 baseline snapshot structure.

    Returns:
        dict with keys: policy, status, violations, details
        - policy: normalized policy (allow|warn|strict)
        - status: pass|warn|fail
        - violations: list of violation strings
        - details: additional context
    """
    normalized_policy = normalize_validation_policy(policy)
    violations = []
    missing_top_keys = []
    missing_stage_config_keys = []

    # Check that snapshot is a dict
    if not isinstance(snapshot, dict):
        violations.append("baseline_snapshot_not_dict")
        status = resolve_policy_status(normalized_policy, violations)
        return {
            "policy": normalized_policy,
            "status": status,
            "violations": violations,
            "details": {
                "is_dict": False,
                "missing_top_keys": missing_top_keys,
                "missing_stage_config_sub_keys": missing_stage_config_keys,
            },
        }

    # Check for required top-level keys
    missing_top_keys = [
        key for key in REQUIRED_BASELINE_SNAPSHOT_TOP_KEYS
        if key not in snapshot
    ]
    if missing_top_keys:
        violations.append(f"missing_top_keys={missing_top_keys}")

    # Validate stage_configs sub-structure
    stage_configs = snapshot.get("stage_configs")
    if isinstance(stage_configs, dict):
        missing_stage_config_keys = [
            key for key in REQUIRED_STAGE_CONFIGS_SUB_KEYS
            if key not in stage_configs
        ]
        if missing_stage_config_keys:
            violations.append(f"missing_stage_configs_sub_keys={missing_stage_config_keys}")
    elif stage_configs is not None:
        violations.append("stage_configs_not_dict")

    # Determine status
    status = resolve_policy_status(normalized_policy, violations)

    return {
        "policy": normalized_policy,
        "status": status,
        "violations": violations,
        "details": {
            "is_dict": True,
            "has_stage_configs": "stage_configs" in snapshot,
            "missing_top_keys": missing_top_keys,
            "missing_stage_config_sub_keys": missing_stage_config_keys,
            "snapshot_top_keys": list(snapshot.keys()),
        },
    }
