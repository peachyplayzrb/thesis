from __future__ import annotations

from shared_utils.constants import BL005_FILTERED_REQUIRED_FIELDS
from shared_utils.validation_policy import normalize_validation_policy, resolve_policy_status


def validate_bl005_bl006_handshake(
    *,
    candidates: list[dict[str, str]],
    policy: str,
) -> dict[str, object]:
    normalized_policy = normalize_validation_policy(policy)

    first_row = candidates[0] if candidates else {}
    fieldnames = [str(key) for key in first_row.keys()]
    missing_required_fields = [
        field for field in BL005_FILTERED_REQUIRED_FIELDS if field not in fieldnames
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

    status = resolve_policy_status(normalized_policy, violations)

    return {
        "policy": normalized_policy,
        "status": status,
        "missing_bl005_filtered_fields": missing_required_fields,
        "source_identifier_present": has_source_identifier,
        "rows_missing_track_id": missing_track_id_rows,
        "control_constraint_violations": violations,
        "sampled_violations": violations[:10],
    }
