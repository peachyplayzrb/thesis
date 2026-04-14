"""Validation helpers for the BL-004 to BL-005 handoff."""

from __future__ import annotations

from typing import Any

from shared_utils.parsing import parse_float


REQUIRED_BL004_PROFILE_KEYS: tuple[str, ...] = (
    "semantic_profile",
    "numeric_feature_profile",
    "numeric_confidence",
    "input_artifacts",
)

REQUIRED_BL004_SEED_TRACE_FIELDS: tuple[str, ...] = (
    "track_id",
)
BL004_SEED_TRACE_CONFIDENCE_FIELD = "match_confidence_score"

VALIDATION_POLICIES: tuple[str, ...] = ("allow", "warn", "strict")


def normalize_validation_policy(policy: Any, default: str = "warn") -> str:
    value = str(policy or default).strip().lower()
    if value in VALIDATION_POLICIES:
        return value
    return default


def validate_bl004_bl005_handshake(
    *,
    profile: dict[str, object],
    seed_trace_rows: list[dict[str, str]],
    numeric_thresholds: dict[str, float],
    policy: str,
) -> dict[str, object]:
    normalized_policy = normalize_validation_policy(policy)

    missing_profile_keys = [
        key for key in REQUIRED_BL004_PROFILE_KEYS if key not in profile
    ]

    first_seed_row = seed_trace_rows[0] if seed_trace_rows else {}
    seed_trace_fieldnames = [str(key) for key in first_seed_row.keys()]
    missing_seed_fields = [
        field
        for field in REQUIRED_BL004_SEED_TRACE_FIELDS
        if field not in seed_trace_fieldnames
    ]

    confidence_field_present = BL004_SEED_TRACE_CONFIDENCE_FIELD in seed_trace_fieldnames
    confidence_field_missing = not confidence_field_present
    malformed_confidence_rows = 0
    out_of_range_confidence_rows = 0
    if confidence_field_present:
        for row in seed_trace_rows:
            raw_confidence = str(row.get(BL004_SEED_TRACE_CONFIDENCE_FIELD, "")).strip()
            parsed_confidence = parse_float(raw_confidence)
            if not raw_confidence or parsed_confidence is None:
                malformed_confidence_rows += 1
                continue
            if parsed_confidence < 0.0 or parsed_confidence > 1.0:
                out_of_range_confidence_rows += 1

    numeric_profile_raw = profile.get("numeric_feature_profile")
    numeric_profile = numeric_profile_raw if isinstance(numeric_profile_raw, dict) else {}
    profile_numeric_features_available = sorted(str(key) for key in numeric_profile.keys())
    numeric_threshold_keys = sorted(str(key) for key in numeric_thresholds.keys())
    numeric_thresholds_extra_keys = [
        key for key in numeric_threshold_keys if key not in profile_numeric_features_available
    ]

    violations: list[str] = []
    if missing_profile_keys:
        violations.append(f"missing_profile_keys={missing_profile_keys}")
    if missing_seed_fields:
        violations.append(f"missing_seed_fields={missing_seed_fields}")
    if confidence_field_missing:
        violations.append(f"missing_seed_confidence_field={BL004_SEED_TRACE_CONFIDENCE_FIELD}")
    if malformed_confidence_rows > 0:
        violations.append(f"malformed_seed_confidence_rows={malformed_confidence_rows}")
    if out_of_range_confidence_rows > 0:
        violations.append(f"out_of_range_seed_confidence_rows={out_of_range_confidence_rows}")
    if numeric_thresholds_extra_keys:
        violations.append(f"numeric_thresholds_extra_keys={numeric_thresholds_extra_keys}")

    schema_ok = not missing_profile_keys
    seed_trace_ok = (
        not missing_seed_fields
        and not confidence_field_missing
        and malformed_confidence_rows == 0
        and out_of_range_confidence_rows == 0
    )
    constraints_ok = not numeric_thresholds_extra_keys

    strict_failure = normalized_policy == "strict" and bool(violations)
    status = "pass"
    if strict_failure:
        status = "fail"
    elif violations and normalized_policy == "warn":
        status = "warn"
    elif violations and normalized_policy == "allow":
        status = "allow"

    return {
        "policy": normalized_policy,
        "status": status,
        "bl004_profile_schema_valid": schema_ok,
        "seed_trace_schema_valid": seed_trace_ok,
        "control_constraints_valid": constraints_ok,
        "missing_profile_keys": missing_profile_keys,
        "missing_seed_fields": missing_seed_fields,
        "seed_confidence_field_present": confidence_field_present,
        "malformed_seed_confidence_rows": malformed_confidence_rows,
        "out_of_range_seed_confidence_rows": out_of_range_confidence_rows,
        "numeric_thresholds_extra_keys": numeric_thresholds_extra_keys,
        "profile_numeric_features_available": profile_numeric_features_available,
        "numeric_threshold_keys": numeric_threshold_keys,
        "control_constraint_violations": violations,
        "sampled_violations": violations[:10],
    }
