"""Validation helpers for BL-010 baseline snapshots used by BL-011."""

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
    """Normalize policy into one of allow, warn, or strict."""
    value = str(policy or default).strip().lower()
    if value in VALIDATION_POLICIES:
        return value
    return default


def validate_bl010_baseline_snapshot(
    snapshot: Any,
    policy: str,
) -> dict[str, object]:
    """Validate the BL-010 baseline snapshot structure before scenario runs."""
    normalized_policy = normalize_validation_policy(policy)
    violations = []
    missing_top_keys = []
    missing_stage_config_keys = []

    # BL-011 requires a JSON object snapshot.
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

    # Validate required top-level fields first.
    missing_top_keys = [
        key for key in REQUIRED_BASELINE_SNAPSHOT_TOP_KEYS
        if key not in snapshot
    ]
    if missing_top_keys:
        violations.append(f"missing_top_keys={missing_top_keys}")

    # Then validate the stage_configs sub-structure.
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

    # Policy controls whether violations fail hard or only warn.
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
