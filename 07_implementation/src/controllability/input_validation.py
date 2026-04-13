"""Input validation for BL-010 baseline snapshot - BL-010 baseline structure contract."""

from __future__ import annotations

from typing import Any, Mapping


VALIDATION_POLICIES: tuple[str, ...] = ("allow", "warn", "strict")

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


def normalize_validation_policy(policy: Any, default: str = "warn") -> str:
    """Normalize policy string to one of: allow, warn, strict."""
    value = str(policy or default).strip().lower()
    if value in VALIDATION_POLICIES:
        return value
    return default


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
        status = "fail" if normalized_policy == "strict" else ("warn" if violations else "allow")
        return {
            "policy": normalized_policy,
            "status": "fail" if normalized_policy == "strict" else status,
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
    strict_failure = normalized_policy == "strict" and bool(violations)
    if strict_failure:
        status = "fail"
    elif violations and normalized_policy == "warn":
        status = "warn"
    elif violations and normalized_policy == "allow":
        status = "allow"
    else:
        status = "pass"

    return {
        "policy": normalized_policy,
        "status": status,
        "violations": violations,
        "details": {
            "is_dict": isinstance(snapshot, dict),
            "has_stage_configs": "stage_configs" in snapshot,
            "missing_top_keys": missing_top_keys,
            "missing_stage_config_sub_keys": missing_stage_config_keys,
            "snapshot_top_keys": list(snapshot.keys()) if isinstance(snapshot, dict) else [],
        },
    }
