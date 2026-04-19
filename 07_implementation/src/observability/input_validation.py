"""Input validation for BL-009 observability - BL-008↔BL-009 handshake."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from shared_utils.validation_policy import normalize_validation_policy, resolve_policy_status

REQUIRED_BL008_SUMMARY_KEYS: tuple[str, ...] = (
    "run_id",
    "playlist_track_count",
    "top_contributor_distribution",
)

REQUIRED_BL008_PAYLOAD_KEYS: tuple[str, ...] = (
    "playlist_track_count",
    "explanations",
)


def _coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def validate_bl008_bl009_handshake(
    *,
    bl008_summary: Mapping[str, object],
    bl008_payloads: Mapping[str, object],
    policy: str,
) -> dict[str, object]:
    normalized_policy = normalize_validation_policy(policy)

    missing_summary_keys = [
        key for key in REQUIRED_BL008_SUMMARY_KEYS if key not in bl008_summary
    ]
    missing_payload_keys = [
        key for key in REQUIRED_BL008_PAYLOAD_KEYS if key not in bl008_payloads
    ]

    summary_track_count = _coerce_int(bl008_summary.get("playlist_track_count"))
    payload_track_count = _coerce_int(bl008_payloads.get("playlist_track_count"))
    explanations_raw = bl008_payloads.get("explanations")
    explanations = list(explanations_raw) if isinstance(explanations_raw, list) else []
    explanation_count = len(explanations)

    invalid_summary_track_count = (
        "playlist_track_count" in bl008_summary and summary_track_count is None
    )
    invalid_payload_track_count = (
        "playlist_track_count" in bl008_payloads and payload_track_count is None
    )
    explanations_not_list = (
        "explanations" in bl008_payloads and not isinstance(explanations_raw, list)
    )
    count_mismatch = (
        summary_track_count is not None
        and payload_track_count is not None
        and (
            summary_track_count != payload_track_count
            or summary_track_count != explanation_count
        )
    )

    violations: list[str] = []
    if missing_summary_keys:
        violations.append(f"missing_bl008_summary_keys={missing_summary_keys}")
    if missing_payload_keys:
        violations.append(f"missing_bl008_payload_keys={missing_payload_keys}")
    if invalid_summary_track_count:
        violations.append("invalid_bl008_summary_playlist_track_count")
    if invalid_payload_track_count:
        violations.append("invalid_bl008_payload_playlist_track_count")
    if explanations_not_list:
        violations.append("bl008_payloads_explanations_not_list=true")
    if count_mismatch:
        violations.append(
            "bl008_summary_payload_count_mismatch="
            f"summary:{summary_track_count};payload:{payload_track_count};explanations:{explanation_count}"
        )

    status = resolve_policy_status(normalized_policy, violations)

    return {
        "policy": normalized_policy,
        "status": status,
        "missing_bl008_summary_keys": missing_summary_keys,
        "missing_bl008_payload_keys": missing_payload_keys,
        "invalid_bl008_summary_playlist_track_count": invalid_summary_track_count,
        "invalid_bl008_payload_playlist_track_count": invalid_payload_track_count,
        "bl008_payloads_explanations_not_list": explanations_not_list,
        "sampled_violations": violations[:10],
        "control_constraint_violations": violations,
    }
