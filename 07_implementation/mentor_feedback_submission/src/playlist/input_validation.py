"""Validation helpers for the BL-006 to BL-007 handoff contract."""

from __future__ import annotations

from typing import Any


VALIDATION_POLICIES: tuple[str, ...] = ("allow", "warn", "strict")

# Required fields BL-006 must write before BL-007 can assemble from the scored CSV.
REQUIRED_BL006_SCORED_FIELDS: tuple[str, ...] = (
    "rank",
    "track_id",
    "lead_genre",
    "final_score",
    "matched_genres",
    "matched_tags",
)

# At least one contribution column must exist so BL-007 can confirm BL-006 ran a real scoring pass.
BL006_SCORING_COMPONENT_INDICATORS: tuple[str, ...] = (
    "lead_genre_contribution",
    "genre_overlap_contribution",
    "tag_overlap_contribution",
)


def normalize_validation_policy(policy: Any, default: str = "warn") -> str:
    value = str(policy or default).strip().lower()
    if value in VALIDATION_POLICIES:
        return value
    return default


def validate_bl006_bl007_handshake(
    *,
    candidates: list[dict[str, str]],
    policy: str,
) -> dict[str, object]:
    """Validate that BL-006 scored candidates satisfy the BL-006 to BL-007 handshake contract."""
    normalized_policy = normalize_validation_policy(policy)

    first_row = candidates[0] if candidates else {}
    fieldnames = [str(key) for key in first_row.keys()]

    missing_required_fields = [
        field for field in REQUIRED_BL006_SCORED_FIELDS if field not in fieldnames
    ]
    active_scoring_components = [
        field for field in BL006_SCORING_COMPONENT_INDICATORS if field in fieldnames
    ]
    scoring_components_absent = len(active_scoring_components) == 0

    missing_track_id_rows = sum(
        1 for row in candidates if not str(row.get("track_id", "")).strip()
    )
    missing_score_rows = sum(
        1 for row in candidates
        if not str(row.get("final_score", "")).strip()
        or str(row.get("final_score", "")).strip().lower() in {"nan", "none"}
    )

    violations: list[str] = []
    if missing_required_fields:
        violations.append(f"missing_bl006_scored_fields={missing_required_fields}")
    if scoring_components_absent:
        violations.append(
            "missing_bl006_scoring_component_fields=all_contribution_columns_absent"
        )
    if missing_track_id_rows > 0:
        violations.append(f"rows_missing_track_id={missing_track_id_rows}")
    if missing_score_rows > 0:
        violations.append(f"rows_missing_final_score={missing_score_rows}")

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
        "missing_bl006_scored_fields": missing_required_fields,
        "scoring_component_fields_present": active_scoring_components,
        "rows_missing_track_id": missing_track_id_rows,
        "rows_missing_final_score": missing_score_rows,
        "control_constraint_violations": violations,
        "sampled_violations": violations[:10],
    }
