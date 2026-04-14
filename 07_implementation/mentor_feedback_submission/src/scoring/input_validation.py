from __future__ import annotations

from typing import Any


VALIDATION_POLICIES: tuple[str, ...] = ("allow", "warn", "strict")

REQUIRED_BL005_FILTERED_FIELDS: tuple[str, ...] = (
    "track_id",
    "artist",
    "song",
    "tags",
    "genres",
    "tempo",
    "duration_ms",
    "key",
    "mode",
)


def normalize_validation_policy(policy: Any, default: str = "warn") -> str:
    value = str(policy or default).strip().lower()
    if value in VALIDATION_POLICIES:
        return value
    return default


def validate_bl005_bl006_handshake(
    *,
    candidates: list[dict[str, str]],
    policy: str,
) -> dict[str, object]:
    normalized_policy = normalize_validation_policy(policy)

    first_row = candidates[0] if candidates else {}
    fieldnames = [str(key) for key in first_row.keys()]
    missing_required_fields = [
        field for field in REQUIRED_BL005_FILTERED_FIELDS if field not in fieldnames
    ]

    has_source_identifier = "id" in fieldnames or "cid" in fieldnames

    missing_track_id_rows = 0
    for row in candidates:
        if not str(row.get("track_id", "")).strip():
            missing_track_id_rows += 1

    violations: list[str] = []
    if missing_required_fields:
        violations.append(f"missing_bl005_filtered_fields={missing_required_fields}")
    if not has_source_identifier:
        violations.append("missing_bl005_source_identifier_field=id_or_cid")
    if missing_track_id_rows > 0:
        violations.append(f"rows_missing_track_id={missing_track_id_rows}")

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
        "missing_bl005_filtered_fields": missing_required_fields,
        "source_identifier_present": has_source_identifier,
        "rows_missing_track_id": missing_track_id_rows,
        "control_constraint_violations": violations,
        "sampled_violations": violations[:10],
    }
