#!/usr/bin/env python3
"""BL-014 sanity checks for BL-020 artifacts.

This script validates:
1. Required artifact presence and schema shape
2. Cross-stage hash-link integrity
3. Basic count continuity across BL-004 to BL-009 outputs

Outputs are written to:
- quality/outputs/bl014_sanity_report.json
- quality/outputs/bl014_sanity_run_matrix.csv
- quality/outputs/bl014_sanity_config_snapshot.json
"""

from __future__ import annotations

import csv
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from controllability.input_validation import normalize_validation_policy
from shared_utils.artifact_registry import bl003_required_paths
from shared_utils.io_utils import format_utc_iso, sha256_of_file
from shared_utils.io_utils import load_json as load_json_shared
from shared_utils.parsing import safe_float
from shared_utils.path_utils import impl_root
from shared_utils.report_utils import write_csv_rows, write_json_ascii

REPO_ROOT = impl_root()
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"

BL004_HANDSHAKE_REQUIRED_SUMMARY_INPUT_KEYS: tuple[str, ...] = ("runtime_scope_diagnostics",)
BL004_HANDSHAKE_REQUIRED_SEED_FIELDS: tuple[str, ...] = ("match_confidence_score",)
BL005_HANDSHAKE_REQUIRED_PROFILE_KEYS: tuple[str, ...] = (
    "semantic_profile",
    "numeric_feature_profile",
    "numeric_confidence",
    "input_artifacts",
)
BL005_HANDSHAKE_REQUIRED_SEED_TRACE_FIELDS: tuple[str, ...] = (
    "track_id",
)
BL006_HANDSHAKE_REQUIRED_BL005_FILTERED_FIELDS: tuple[str, ...] = (
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
BL005_HANDSHAKE_WARN_MAX_VIOLATIONS_ADVISORY_THRESHOLD = 3
BL005_RUNTIME_CONTROL_FALLBACK_ADVISORY_THRESHOLD = 3
BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_DEFAULT = "warn"
BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_ENV_VAR = "BL014_BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY"
BL011_CONTROL_EFFECT_GATE_POLICY_DEFAULT = "warn"
BL011_CONTROL_EFFECT_GATE_POLICY_ENV_VAR = "BL014_BL011_CONTROL_EFFECT_GATE_POLICY"
BL008_CONTROL_CAUSALITY_GATE_POLICY_DEFAULT = "warn"
BL008_CONTROL_CAUSALITY_GATE_POLICY_ENV_VAR = "BL014_BL008_CONTROL_CAUSALITY_GATE_POLICY"
BL007_HANDSHAKE_REQUIRED_BL006_SCORED_FIELDS: tuple[str, ...] = (
    "rank",
    "track_id",
    "lead_genre",
    "final_score",
)
BL007_HANDSHAKE_SCORING_COMPONENT_INDICATORS: tuple[str, ...] = (
    "lead_genre_contribution",
    "genre_overlap_contribution",
    "tag_overlap_contribution",
)
BL008_HANDSHAKE_REQUIRED_PLAYLIST_TRACK_FIELDS: tuple[str, ...] = (
    "track_id",
    "final_score",
    "playlist_position",
)
BL009_HANDSHAKE_REQUIRED_BL008_SUMMARY_KEYS: tuple[str, ...] = (
    "run_id",
    "playlist_track_count",
    "top_contributor_distribution",
)


def sha256_file(path: Path) -> str:
    return sha256_of_file(path).upper()


def load_json(path: Path) -> dict[str, Any]:
    return load_json_shared(path)


def csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader)
        return sum(1 for _ in reader)


def bl005_filtered_has_required_columns(header: list[str]) -> bool:
    required = {
        "track_id",
        "artist",
        "song",
        "tags",
        "genres",
        "tempo",
        "duration_ms",
        "key",
        "mode",
    }
    header_set = set(header)
    return required.issubset(header_set) and ({"id", "cid"} & header_set) != set()


def bl003_bl004_handshake_contract_ok(
    bl003_summary: dict[str, Any],
    bl004_profile: dict[str, Any],
) -> tuple[bool, str]:
    inputs_raw = bl003_summary.get("inputs")
    summary_inputs = dict(inputs_raw) if isinstance(inputs_raw, dict) else {}

    missing_summary_keys = [
        key for key in BL004_HANDSHAKE_REQUIRED_SUMMARY_INPUT_KEYS if key not in summary_inputs
    ]

    structural_contract_raw = summary_inputs.get("structural_contract")
    structural_contract = (
        dict(structural_contract_raw) if isinstance(structural_contract_raw, dict) else {}
    )
    fieldnames_raw = structural_contract.get("seed_table_fieldnames")
    seed_fieldnames = [str(value) for value in fieldnames_raw] if isinstance(fieldnames_raw, list) else []
    missing_seed_fields = [
        field for field in BL004_HANDSHAKE_REQUIRED_SEED_FIELDS if field not in seed_fieldnames
    ]

    diagnostics_raw = bl004_profile.get("diagnostics")
    diagnostics = dict(diagnostics_raw) if isinstance(diagnostics_raw, dict) else {}
    validation_policies_raw = diagnostics.get("validation_policies")
    validation_policies = (
        dict(validation_policies_raw) if isinstance(validation_policies_raw, dict) else {}
    )
    has_policy = "bl003_handshake_validation_policy" in validation_policies

    if not missing_summary_keys and not missing_seed_fields and has_policy:
        return True, "BL-003↔BL-004 handshake contract fields and policy metadata are present"

    detail_parts: list[str] = []
    if missing_summary_keys:
        detail_parts.append(f"missing summary input keys={missing_summary_keys}")
    if missing_seed_fields:
        detail_parts.append(f"missing structural seed fields={missing_seed_fields}")
    if not has_policy:
        detail_parts.append("missing BL-004 diagnostics.validation_policies.bl003_handshake_validation_policy")

    return False, "BL-003↔BL-004 handshake contract incomplete: " + "; ".join(detail_parts)


def bl004_bl005_handshake_contract_ok(
    bl004_profile: dict[str, Any],
    bl005_diagnostics: dict[str, Any],
    bl004_seed_trace_header: list[str],
) -> tuple[bool, str]:
    missing_profile_keys = [
        key for key in BL005_HANDSHAKE_REQUIRED_PROFILE_KEYS if key not in bl004_profile
    ]
    missing_seed_fields = [
        field for field in BL005_HANDSHAKE_REQUIRED_SEED_TRACE_FIELDS if field not in bl004_seed_trace_header
    ]

    config_raw = bl005_diagnostics.get("config")
    config = dict(config_raw) if isinstance(config_raw, dict) else {}
    policies_raw = config.get("validation_policies")
    policies = dict(policies_raw) if isinstance(policies_raw, dict) else {}
    has_policy = "bl004_bl005_handshake_validation_policy" in policies

    if not missing_profile_keys and not missing_seed_fields and has_policy:
        return True, "BL-004↔BL-005 handshake contract fields and policy metadata are present"

    detail_parts: list[str] = []
    if missing_profile_keys:
        detail_parts.append(f"missing BL-004 profile keys={missing_profile_keys}")
    if missing_seed_fields:
        detail_parts.append(f"missing BL-004 seed trace fields={missing_seed_fields}")
    if not has_policy:
        detail_parts.append("missing BL-005 config.validation_policies.bl004_bl005_handshake_validation_policy")

    return False, "BL-004↔BL-005 handshake contract incomplete: " + "; ".join(detail_parts)


def bl006_bl007_handshake_contract_ok(
    bl006_scored_header: list[str],
    bl007_report: dict[str, Any],
) -> tuple[bool, str]:
    missing_scored_fields = [
        field
        for field in BL007_HANDSHAKE_REQUIRED_BL006_SCORED_FIELDS
        if field not in bl006_scored_header
    ]
    active_scoring_components = [
        field for field in BL007_HANDSHAKE_SCORING_COMPONENT_INDICATORS if field in bl006_scored_header
    ]
    scoring_components_absent = len(active_scoring_components) == 0

    config_raw = bl007_report.get("config")
    config = dict(config_raw) if isinstance(config_raw, dict) else {}
    policies_raw = config.get("validation_policies")
    policies = dict(policies_raw) if isinstance(policies_raw, dict) else {}
    has_policy = "bl006_bl007_handshake_validation_policy" in policies

    validation_raw = bl007_report.get("validation")
    validation = dict(validation_raw) if isinstance(validation_raw, dict) else {}
    has_validation_status = isinstance(validation.get("status"), str)

    if (
        not missing_scored_fields
        and not scoring_components_absent
        and has_policy
        and has_validation_status
    ):
        return True, "BL-006↔BL-007 handshake contract fields and policy metadata are present"

    detail_parts: list[str] = []
    if missing_scored_fields:
        detail_parts.append(f"missing BL-006 scored fields={missing_scored_fields}")
    if scoring_components_absent:
        detail_parts.append("missing BL-006 scoring component contribution columns")
    if not has_policy:
        detail_parts.append(
            "missing BL-007 config.validation_policies.bl006_bl007_handshake_validation_policy"
        )
    if not has_validation_status:
        detail_parts.append("missing BL-007 report validation.status")

    return False, "BL-006↔BL-007 handshake contract incomplete: " + "; ".join(detail_parts)


def bl007_bl008_handshake_contract_ok(
    playlist_data: dict[str, Any],
    bl008_summary: dict[str, Any],
) -> tuple[bool, str]:
    tracks_raw = playlist_data.get("tracks")
    tracks = list(tracks_raw) if isinstance(tracks_raw, list) else []
    first_track = dict(tracks[0]) if (tracks and isinstance(tracks[0], dict)) else {}
    first_track_keys = list(first_track.keys())

    missing_track_fields = [
        field for field in BL008_HANDSHAKE_REQUIRED_PLAYLIST_TRACK_FIELDS
        if field not in first_track_keys
    ]
    playlist_is_empty = len(tracks) == 0

    config_raw = bl008_summary.get("config")
    config = dict(config_raw) if isinstance(config_raw, dict) else {}
    policies_raw = config.get("validation_policies")
    policies = dict(policies_raw) if isinstance(policies_raw, dict) else {}
    has_policy = "bl007_bl008_handshake_validation_policy" in policies

    validation_raw = bl008_summary.get("validation")
    validation = dict(validation_raw) if isinstance(validation_raw, dict) else {}
    has_validation_status = isinstance(validation.get("status"), str)

    if (
        not playlist_is_empty
        and not missing_track_fields
        and has_policy
        and has_validation_status
    ):
        return True, "BL-007↔BL-008 handshake contract fields and policy metadata are present"

    detail_parts: list[str] = []
    if playlist_is_empty:
        detail_parts.append("playlist tracks list is empty")
    if missing_track_fields:
        detail_parts.append(f"missing BL-007 playlist track fields={missing_track_fields}")
    if not has_policy:
        detail_parts.append(
            "missing BL-008 config.validation_policies.bl007_bl008_handshake_validation_policy"
        )
    if not has_validation_status:
        detail_parts.append("missing BL-008 summary validation.status")

    return False, "BL-007↔BL-008 handshake contract incomplete: " + "; ".join(detail_parts)


def _parse_track_count(raw: object) -> int | None:
    if raw is None:
        return None
    try:
        return int(str(raw))
    except (TypeError, ValueError):
        return None


def _bl008_bl009_check_logic(
    bl008_summary: dict[str, Any],
    bl008_payloads: dict[str, Any],
    bl009_log: dict[str, Any],
) -> tuple[bool, list[str]]:
    missing_summary_keys = [
        key for key in BL009_HANDSHAKE_REQUIRED_BL008_SUMMARY_KEYS if key not in bl008_summary
    ]
    explanations_raw = bl008_payloads.get("explanations")
    has_explanations = isinstance(explanations_raw, list)
    explanations_len = len(list(explanations_raw)) if isinstance(explanations_raw, list) else 0

    summary_track_count = _parse_track_count(bl008_summary.get("playlist_track_count"))
    payload_track_count = _parse_track_count(bl008_payloads.get("playlist_track_count"))
    count_mismatch = (
        summary_track_count is None
        or payload_track_count is None
        or summary_track_count != payload_track_count
        or summary_track_count != explanations_len
    )

    run_config_raw = bl009_log.get("run_config")
    run_config = dict(run_config_raw) if isinstance(run_config_raw, dict) else {}
    observability_raw = run_config.get("observability")
    observability = dict(observability_raw) if isinstance(observability_raw, dict) else {}
    policies_raw = observability.get("validation_policies")
    policies = dict(policies_raw) if isinstance(policies_raw, dict) else {}
    has_policy = "bl008_bl009_handshake_validation_policy" in policies

    validation_raw = bl009_log.get("validation")
    validation = dict(validation_raw) if isinstance(validation_raw, dict) else {}
    has_validation_status = isinstance(validation.get("status"), str)

    detail_parts: list[str] = []
    if missing_summary_keys:
        detail_parts.append(f"missing BL-008 summary keys={missing_summary_keys}")
    if not has_explanations:
        detail_parts.append("missing BL-008 payload explanations list")
    if count_mismatch:
        detail_parts.append("BL-008 summary/payload explanation counts are inconsistent")
    if not has_policy:
        detail_parts.append(
            "missing BL-009 run_config.observability.validation_policies.bl008_bl009_handshake_validation_policy"
        )
    if not has_validation_status:
        detail_parts.append("missing BL-009 log validation.status")

    ok = not missing_summary_keys and has_explanations and not count_mismatch and has_policy and has_validation_status
    return ok, detail_parts


def bl008_bl009_handshake_contract_ok(
    bl008_summary: dict[str, Any],
    bl008_payloads: dict[str, Any],
    bl009_log: dict[str, Any],
) -> tuple[bool, str]:
    ok, detail_parts = _bl008_bl009_check_logic(bl008_summary, bl008_payloads, bl009_log)
    if ok:
        return True, "BL-008↔BL-009 handshake contract fields and policy metadata are present"
    return False, "BL-008↔BL-009 handshake contract incomplete: " + "; ".join(detail_parts)


def bl009_bl010_handshake_contract_ok(
    bl010_snapshot: dict[str, Any],
) -> tuple[bool, str]:
    """Check BL-010 validation of BL-009 outputs recorded in reproducibility config snapshot."""
    # Auto-pass if BL-010 snapshot is empty (reproducibility stage not executed).
    if not bl010_snapshot:
        return True, "BL-010 reproducibility not executed (optional diagnostic stage)"

    validation_raw = bl010_snapshot.get("validation")
    validation = dict(validation_raw) if isinstance(validation_raw, dict) else {}

    # Backward compatibility: older BL-010 snapshots did not persist validation blocks.
    # Treat this as optional-stage legacy format instead of a hard contract failure.
    if not validation:
        return True, "BL-010 snapshot present in legacy format (no validation block); treated as optional-compatible"

    has_policy = isinstance(validation.get("policy"), str)
    has_status = isinstance(validation.get("status"), str)
    has_violations_list = isinstance(validation.get("violations"), list)
    has_details = isinstance(validation.get("details"), dict)

    if has_policy and has_status and has_violations_list and has_details:
        return True, "BL-009↔BL-010 handshake validation recorded in BL-010 snapshot"

    detail_parts: list[str] = []
    if not has_policy:
        detail_parts.append("missing BL-010 validation.policy")
    if not has_status:
        detail_parts.append("missing BL-010 validation.status")
    if not has_violations_list:
        detail_parts.append("missing BL-010 validation.violations")
    if not has_details:
        detail_parts.append("missing BL-010 validation.details")

    return False, "BL-009↔BL-010 handshake contract incomplete: " + "; ".join(detail_parts)


def bl010_bl011_handshake_contract_ok(
    bl011_snapshot: dict[str, Any],
) -> tuple[bool, str]:
    """Check BL-011 validation of BL-010 baseline snapshot recorded in controllability config snapshot."""
    # Auto-pass if BL-011 snapshot is empty (controllability stage not executed).
    if not bl011_snapshot:
        return True, "BL-011 controllability not executed (optional diagnostic stage)"

    validation_raw = bl011_snapshot.get("validation")
    validation = dict(validation_raw) if isinstance(validation_raw, dict) else {}

    # Backward compatibility: older BL-011 snapshots did not persist validation blocks.
    # Treat this as optional-stage legacy format instead of a hard contract failure.
    if not validation:
        return True, "BL-011 snapshot present in legacy format (no validation block); treated as optional-compatible"

    has_policy = isinstance(validation.get("policy"), str)
    has_status = isinstance(validation.get("status"), str)
    has_violations_list = isinstance(validation.get("violations"), list)
    has_details = isinstance(validation.get("details"), dict)

    if has_policy and has_status and has_violations_list and has_details:
        return True, "BL-010↔BL-011 handshake validation recorded in BL-011 snapshot"

    detail_parts: list[str] = []
    if not has_policy:
        detail_parts.append("missing BL-011 validation.policy")
    if not has_status:
        detail_parts.append("missing BL-011 validation.status")
    if not has_violations_list:
        detail_parts.append("missing BL-011 validation.violations")
    if not has_details:
        detail_parts.append("missing BL-011 validation.details")

    return False, "BL-010↔BL-011 handshake contract incomplete: " + "; ".join(detail_parts)


def bl005_bl006_handshake_contract_ok(
    bl005_filtered_header: list[str],
    bl006_summary: dict[str, Any],
) -> tuple[bool, str]:
    missing_bl005_filtered_fields = [
        field
        for field in BL006_HANDSHAKE_REQUIRED_BL005_FILTERED_FIELDS
        if field not in bl005_filtered_header
    ]
    has_source_identifier = "id" in bl005_filtered_header or "cid" in bl005_filtered_header

    config_raw = bl006_summary.get("config")
    config = dict(config_raw) if isinstance(config_raw, dict) else {}
    policies_raw = config.get("validation_policies")
    policies = dict(policies_raw) if isinstance(policies_raw, dict) else {}
    has_policy = "bl005_bl006_handshake_validation_policy" in policies

    validation_raw = bl006_summary.get("validation")
    validation = dict(validation_raw) if isinstance(validation_raw, dict) else {}
    has_validation_status = isinstance(validation.get("status"), str)

    if (
        not missing_bl005_filtered_fields
        and has_source_identifier
        and has_policy
        and has_validation_status
    ):
        return True, "BL-005↔BL-006 handshake contract fields and policy metadata are present"

    detail_parts: list[str] = []
    if missing_bl005_filtered_fields:
        detail_parts.append(
            f"missing BL-005 filtered fields={missing_bl005_filtered_fields}"
        )
    if not has_source_identifier:
        detail_parts.append("missing BL-005 source identifier field=id_or_cid")
    if not has_policy:
        detail_parts.append(
            "missing BL-006 config.validation_policies.bl005_bl006_handshake_validation_policy"
        )
    if not has_validation_status:
        detail_parts.append("missing BL-006 validation.status")

    return False, "BL-005↔BL-006 handshake contract incomplete: " + "; ".join(detail_parts)


def bl005_handshake_warning_volume_advisory(
    bl005_diagnostics: dict[str, Any],
    *,
    threshold: int = BL005_HANDSHAKE_WARN_MAX_VIOLATIONS_ADVISORY_THRESHOLD,
) -> dict[str, str] | None:
    config_raw = bl005_diagnostics.get("config")
    config = dict(config_raw) if isinstance(config_raw, dict) else {}
    policies_raw = config.get("validation_policies")
    policies = dict(policies_raw) if isinstance(policies_raw, dict) else {}
    policy = str(policies.get("bl004_bl005_handshake_validation_policy", "warn")).strip().lower()

    validation_raw = bl005_diagnostics.get("validation")
    validation = dict(validation_raw) if isinstance(validation_raw, dict) else {}
    status = str(validation.get("status", "pass")).strip().lower()

    violations_raw = validation.get("control_constraint_violations")
    violations = list(violations_raw) if isinstance(violations_raw, list) else []
    violation_count = len(violations)

    if policy != "warn" or status != "warn" or violation_count <= threshold:
        return None

    sampled_raw = validation.get("sampled_violations")
    sampled = list(sampled_raw) if isinstance(sampled_raw, list) else []
    return {
        "id": "advisory_bl005_handshake_warning_volume",
        "details": (
            f"BL-005 handshake validation is running in warn mode with elevated violation volume "
            f"({violation_count} > {threshold}); consider strict policy after remediation. "
            f"Sampled violations={sampled[:5]}"
        ),
    }


def bl005_control_resolution_fallback_volume_advisory(
    bl005_diagnostics: dict[str, Any],
    *,
    threshold: int = BL005_RUNTIME_CONTROL_FALLBACK_ADVISORY_THRESHOLD,
) -> dict[str, str] | None:
    config_raw = bl005_diagnostics.get("config")
    config = dict(config_raw) if isinstance(config_raw, dict) else {}
    runtime_resolution_raw = config.get("runtime_control_resolution")
    runtime_resolution = (
        dict(runtime_resolution_raw) if isinstance(runtime_resolution_raw, dict) else {}
    )

    fallback_event_count = int(runtime_resolution.get("normalization_event_count", 0) or 0)
    if fallback_event_count <= threshold:
        return None

    counts_raw = runtime_resolution.get("normalization_event_counts_by_field")
    counts_by_field = dict(counts_raw) if isinstance(counts_raw, dict) else {}
    sampled_raw = runtime_resolution.get("normalization_events_sampled")
    sampled = list(sampled_raw) if isinstance(sampled_raw, list) else []
    return {
        "id": "advisory_bl005_control_resolution_fallback_volume",
        "details": (
            f"BL-005 control resolution recorded elevated fallback/coercion volume "
            f"({fallback_event_count} > {threshold}). "
            f"Counts by field={counts_by_field}; sampled events={sampled[:5]}"
        ),
    }


def bl005_threshold_diagnostics_contract_advisory(
    bl005_diagnostics: dict[str, Any],
    *,
    policy: str = BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_DEFAULT,
) -> dict[str, str] | None:
    gate_result = bl005_threshold_diagnostics_contract_gate_result(
        bl005_diagnostics,
        policy=policy,
    )
    if gate_result is None or not gate_result["violations"] or gate_result["status"] == "fail":
        return None

    return {
        "id": "advisory_bl005_threshold_diagnostics_contract",
        "details": str(gate_result["details"]),
    }


def bl005_threshold_diagnostics_contract_missing_fields(
    bl005_diagnostics: dict[str, Any],
) -> list[str]:
    threshold_attribution_raw = bl005_diagnostics.get("threshold_attribution")
    threshold_attribution = (
        dict(threshold_attribution_raw)
        if isinstance(threshold_attribution_raw, dict)
        else {}
    )
    what_if_raw = bl005_diagnostics.get("bounded_what_if_estimates")
    bounded_what_if = dict(what_if_raw) if isinstance(what_if_raw, dict) else {}

    missing_fields: list[str] = []
    for field in (
        "rejected_threshold_candidates",
        "numeric_feature_fail_counts",
        "top_failure_features",
    ):
        if field not in threshold_attribution:
            missing_fields.append(f"threshold_attribution.{field}")
    for field in (
        "considered_candidates",
        "base_kept_candidates",
        "relaxed_estimate",
        "tightened_estimate",
    ):
        if field not in bounded_what_if:
            missing_fields.append(f"bounded_what_if_estimates.{field}")

    return missing_fields


def resolve_bl005_threshold_diagnostics_gate_policy(
    bl009_log: dict[str, Any],
) -> str:
    run_config_raw = bl009_log.get("run_config")
    run_config = dict(run_config_raw) if isinstance(run_config_raw, dict) else {}
    observability_raw = run_config.get("observability")
    observability = dict(observability_raw) if isinstance(observability_raw, dict) else {}
    validation_policies_raw = observability.get("validation_policies")
    validation_policies = (
        dict(validation_policies_raw)
        if isinstance(validation_policies_raw, dict)
        else {}
    )

    candidate_policy = (
        validation_policies.get("bl005_threshold_diagnostics_contract_policy")
        or os.environ.get(BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_ENV_VAR)
        or BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_DEFAULT
    )
    return normalize_validation_policy(
        candidate_policy,
        default=BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_DEFAULT,
    )


def bl005_threshold_diagnostics_contract_gate_result(
    bl005_diagnostics: dict[str, Any],
    *,
    policy: str = BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_DEFAULT,
) -> dict[str, Any] | None:
    normalized_policy = normalize_validation_policy(
        policy,
        default=BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_DEFAULT,
    )
    missing_fields = bl005_threshold_diagnostics_contract_missing_fields(bl005_diagnostics)

    if not missing_fields:
        return {
            "id": "gate_bl005_threshold_diagnostics_contract",
            "policy": normalized_policy,
            "status": "pass",
            "violations": [],
            "details": (
                "BL-005 threshold diagnostics contract is complete. "
                f"policy={normalized_policy}; missing_fields=0"
            ),
        }

    status = "fail" if normalized_policy == "strict" else "warn"
    return {
        "id": "gate_bl005_threshold_diagnostics_contract",
        "policy": normalized_policy,
        "status": status,
        "violations": [f"missing_fields={len(missing_fields)}"],
        "details": (
            "BL-005 diagnostics are missing threshold-attribution/what-if fields expected for "
            f"UNDO-I monitoring. policy={normalized_policy}, gate_status={status}, "
            f"missing={missing_fields}."
        ),
    }


def bl011_control_effect_gate_advisory(
    bl011_report: dict[str, Any],
    *,
    policy: str = BL011_CONTROL_EFFECT_GATE_POLICY_DEFAULT,
) -> dict[str, str] | None:
    gate_result = bl011_control_effect_gate_result(bl011_report, policy=policy)
    if gate_result is None or not gate_result["violations"] or gate_result["status"] == "fail":
        return None

    return {
        "id": "advisory_bl011_control_effect_gate",
        "details": str(gate_result["details"]),
    }


def resolve_bl011_control_effect_gate_policy(
    bl011_snapshot: dict[str, Any],
    bl011_report: dict[str, Any],
    bl009_log: dict[str, Any],
) -> str:
    run_config_raw = bl009_log.get("run_config")
    run_config = dict(run_config_raw) if isinstance(run_config_raw, dict) else {}
    observability_raw = run_config.get("observability")
    observability = dict(observability_raw) if isinstance(observability_raw, dict) else {}
    config_policies_raw = observability.get("validation_policies")
    config_policies = dict(config_policies_raw) if isinstance(config_policies_raw, dict) else {}

    config_raw = bl011_report.get("config")
    config = dict(config_raw) if isinstance(config_raw, dict) else {}
    report_policies_raw = config.get("validation_policies")
    report_policies = dict(report_policies_raw) if isinstance(report_policies_raw, dict) else {}

    validation_raw = bl011_snapshot.get("validation")
    validation = dict(validation_raw) if isinstance(validation_raw, dict) else {}
    snapshot_policies_raw = validation.get("validation_policies")
    snapshot_policies = (
        dict(snapshot_policies_raw) if isinstance(snapshot_policies_raw, dict) else {}
    )

    candidate_policy = (
        config_policies.get("bl011_control_effect_gate_policy")
        or
        snapshot_policies.get("bl011_control_effect_gate_policy")
        or validation.get("bl011_control_effect_gate_policy")
        or report_policies.get("bl011_control_effect_gate_policy")
        or os.environ.get(BL011_CONTROL_EFFECT_GATE_POLICY_ENV_VAR)
        or BL011_CONTROL_EFFECT_GATE_POLICY_DEFAULT
    )
    return normalize_validation_policy(
        candidate_policy,
        default=BL011_CONTROL_EFFECT_GATE_POLICY_DEFAULT,
    )


def bl011_control_effect_gate_result(
    bl011_report: dict[str, Any],
    *,
    policy: str = BL011_CONTROL_EFFECT_GATE_POLICY_DEFAULT,
) -> dict[str, Any] | None:
    if not bl011_report:
        return None

    normalized_policy = normalize_validation_policy(
        policy,
        default=BL011_CONTROL_EFFECT_GATE_POLICY_DEFAULT,
    )
    results_raw = bl011_report.get("results")
    results = dict(results_raw) if isinstance(results_raw, dict) else {}
    no_op_controls_count = int(results.get("no_op_controls_count", 0) or 0)
    all_variant_shifts_observable = bool(results.get("all_variant_shifts_observable", False))
    all_variant_directions_met = bool(results.get("all_variant_directions_met", False))

    if (
        no_op_controls_count == 0
        and all_variant_shifts_observable
        and all_variant_directions_met
    ):
        return {
            "id": "gate_bl011_control_effect",
            "policy": normalized_policy,
            "status": "pass",
            "violations": [],
            "details": (
                "BL-011 controllability control-effect gate passed. "
                f"policy={normalized_policy}; all_variant_shifts_observable={all_variant_shifts_observable}, "
                f"all_variant_directions_met={all_variant_directions_met}, "
                f"no_op_controls_count={no_op_controls_count}"
            ),
        }

    no_op_raw = results.get("no_op_control_diagnostics")
    no_op_control_diagnostics = list(no_op_raw) if isinstance(no_op_raw, list) else []
    violations: list[str] = []
    if not all_variant_shifts_observable:
        violations.append("all_variant_shifts_observable=false")
    if not all_variant_directions_met:
        violations.append("all_variant_directions_met=false")
    if no_op_controls_count > 0:
        violations.append(f"no_op_controls_count={no_op_controls_count}")

    status = "fail" if normalized_policy == "strict" else "warn"
    return {
        "id": "gate_bl011_control_effect",
        "policy": normalized_policy,
        "status": status,
        "violations": violations,
        "details": (
            "BL-011 controllability indicates weak or non-observable control effects. "
            f"policy={normalized_policy}, gate_status={status}, "
            f"all_variant_shifts_observable={all_variant_shifts_observable}, "
            f"all_variant_directions_met={all_variant_directions_met}, "
            f"no_op_controls_count={no_op_controls_count}, "
            f"sampled_no_op_controls={no_op_control_diagnostics[:5]}"
        ),
    }


def _score_band_phrase(final_score: float) -> str:
    if final_score >= 0.75:
        return "strong profile match"
    if final_score >= 0.5:
        return "moderate profile match"
    return "weaker but acceptable profile match"


def _check_score_breakdown_warnings(
    score_breakdown: list[Any],
    prefix: str,
) -> list[str]:
    warnings: list[str] = []
    positive_contributions = [
        max(0.0, safe_float(dict(item).get("contribution", 0.0)))
        for item in score_breakdown
        if isinstance(item, dict)
    ]
    total_positive = sum(positive_contributions)
    share_sum = sum(
        safe_float(dict(item).get("contribution_share_pct", 0.0))
        for item in score_breakdown
        if isinstance(item, dict)
    )
    if total_positive > 0.0 and abs(share_sum - 100.0) > 0.5:
        warnings.append(f"{prefix}: contribution_share_sum_out_of_bounds={share_sum}")

    negative_margin = any(
        safe_float(dict(item).get("margin_vs_next_contributor", 0.0)) < 0.0
        for item in score_breakdown
        if isinstance(item, dict)
    )
    if negative_margin:
        warnings.append(f"{prefix}: negative_margin_vs_next_contributor")

    return warnings


def _check_primary_driver_warning(
    payload: dict[str, Any],
    top_contributors: list[Any],
    prefix: str,
) -> list[str]:
    primary_driver_raw = payload.get("primary_explanation_driver")
    primary_driver = dict(primary_driver_raw) if isinstance(primary_driver_raw, dict) else {}
    primary_label = str(primary_driver.get("label", ""))
    top_labels = {
        str(dict(item).get("label", ""))
        for item in top_contributors
        if isinstance(item, dict)
    }
    if primary_label and top_labels and primary_label not in top_labels:
        return [f"{prefix}: primary_driver_not_in_top_contributors"]
    return []


def _check_driver_and_narrative_warnings(
    payload: dict[str, Any],
    score_breakdown: list[Any],
    prefix: str,
) -> list[str]:
    warnings: list[str] = []

    causal_driver_raw = payload.get("causal_driver")
    causal_driver = dict(causal_driver_raw) if isinstance(causal_driver_raw, dict) else {}
    causal_label = str(causal_driver.get("label", ""))
    sorted_breakdown = sorted(
        [dict(item) for item in score_breakdown if isinstance(item, dict)],
        key=lambda item: safe_float(item.get("contribution", 0.0)),
        reverse=True,
    )
    expected_causal = str(sorted_breakdown[0].get("label", "")) if sorted_breakdown else ""
    if causal_label and expected_causal and causal_label != expected_causal:
        warnings.append(f"{prefix}: causal_driver_mismatch_expected={expected_causal}")

    why_selected = str(payload.get("why_selected", ""))
    final_score = safe_float(payload.get("final_score", 0.0))
    required_phrase = _score_band_phrase(final_score)
    if required_phrase not in why_selected:
        warnings.append(f"{prefix}: why_selected_score_band_mismatch")

    assembly_context_raw = payload.get("assembly_context")
    assembly_context = dict(assembly_context_raw) if isinstance(assembly_context_raw, dict) else {}
    required_context_keys = {"decision", "admission_rule", "genre_at_position"}
    if not required_context_keys.issubset(set(assembly_context.keys())):
        warnings.append(f"{prefix}: assembly_context_incomplete")

    return warnings


def _bl008_explanation_payload_warnings(payload: dict[str, Any], idx: int) -> list[str]:
    prefix = f"payload_index={idx}"
    score_breakdown_raw = payload.get("score_breakdown")
    score_breakdown = list(score_breakdown_raw) if isinstance(score_breakdown_raw, list) else []
    top_contributors_raw = payload.get("top_score_contributors")
    top_contributors = list(top_contributors_raw) if isinstance(top_contributors_raw, list) else []

    if not score_breakdown:
        return [f"{prefix}: missing_score_breakdown"]

    return (
        _check_score_breakdown_warnings(score_breakdown, prefix)
        + _check_primary_driver_warning(payload, top_contributors, prefix)
        + _check_driver_and_narrative_warnings(payload, score_breakdown, prefix)
    )


def bl008_explanation_fidelity_warnings(
    bl008_payloads: dict[str, Any],
) -> list[str]:
    explanations_raw = bl008_payloads.get("explanations")
    explanations = list(explanations_raw) if isinstance(explanations_raw, list) else []
    warnings: list[str] = []
    for idx, payload_raw in enumerate(explanations):
        payload = dict(payload_raw) if isinstance(payload_raw, dict) else {}
        warnings.extend(_bl008_explanation_payload_warnings(payload, idx))
    return warnings


def bl008_control_causality_contract_advisory(
    bl008_payloads: dict[str, Any],
    *,
    policy: str = BL008_CONTROL_CAUSALITY_GATE_POLICY_DEFAULT,
) -> dict[str, str] | None:
    gate_result = bl008_control_causality_contract_gate_result(
        bl008_payloads,
        policy=policy,
    )
    if gate_result is None or not gate_result["violations"] or gate_result["status"] == "fail":
        return None

    return {
        "id": "advisory_bl008_control_causality_contract",
        "details": str(gate_result["details"]),
    }


def resolve_bl008_control_causality_gate_policy(
    bl009_log: dict[str, Any],
) -> str:
    run_config_raw = bl009_log.get("run_config")
    run_config = dict(run_config_raw) if isinstance(run_config_raw, dict) else {}
    observability_raw = run_config.get("observability")
    observability = dict(observability_raw) if isinstance(observability_raw, dict) else {}
    validation_policies_raw = observability.get("validation_policies")
    validation_policies = (
        dict(validation_policies_raw)
        if isinstance(validation_policies_raw, dict)
        else {}
    )

    candidate_policy = (
        validation_policies.get("bl008_control_causality_contract_policy")
        or os.environ.get(BL008_CONTROL_CAUSALITY_GATE_POLICY_ENV_VAR)
        or BL008_CONTROL_CAUSALITY_GATE_POLICY_DEFAULT
    )
    return normalize_validation_policy(
        candidate_policy,
        default=BL008_CONTROL_CAUSALITY_GATE_POLICY_DEFAULT,
    )


def bl008_control_causality_contract_gate_result(
    bl008_payloads: dict[str, Any],
    *,
    policy: str = BL008_CONTROL_CAUSALITY_GATE_POLICY_DEFAULT,
) -> dict[str, Any] | None:
    explanations_raw = bl008_payloads.get("explanations")
    explanations = list(explanations_raw) if isinstance(explanations_raw, list) else []
    if not explanations:
        return None

    normalized_policy = normalize_validation_policy(
        policy,
        default=BL008_CONTROL_CAUSALITY_GATE_POLICY_DEFAULT,
    )
    required_keys = [
        "schema_version",
        "decision_outcome",
        "controlling_parameters",
        "effect_direction",
        "evidence_sources",
    ]
    missing_contract_tracks: list[dict[str, object]] = []
    for payload_raw in explanations:
        payload = dict(payload_raw) if isinstance(payload_raw, dict) else {}
        control_causality_raw = payload.get("control_causality")
        control_causality = (
            dict(control_causality_raw)
            if isinstance(control_causality_raw, dict)
            else {}
        )
        missing = [key for key in required_keys if key not in control_causality]
        if missing:
            missing_contract_tracks.append(
                {
                    "track_id": str(payload.get("track_id", "")),
                    "missing": missing,
                }
            )

    if not missing_contract_tracks:
        return {
            "id": "gate_bl008_control_causality_contract",
            "policy": normalized_policy,
            "status": "pass",
            "violations": [],
            "details": (
                "BL-008 control_causality contract is complete for all explanations. "
                f"policy={normalized_policy}; affected_tracks=0/{len(explanations)}"
            ),
        }

    status = "fail" if normalized_policy == "strict" else "warn"
    return {
        "id": "gate_bl008_control_causality_contract",
        "policy": normalized_policy,
        "status": status,
        "violations": [f"affected_tracks={len(missing_contract_tracks)}/{len(explanations)}"],
        "details": (
            "BL-008 explanations are missing control_causality contract fields expected for UNDO-H monitoring. "
            f"policy={normalized_policy}, gate_status={status}, "
            f"affected_tracks={len(missing_contract_tracks)}/{len(explanations)} "
            f"sampled={missing_contract_tracks[:5]}"
        ),
    }


def ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path}")


def resolve_existing_path(preferred: Path, fallback: Path) -> Path:
    if preferred.exists():
        return preferred
    if fallback.exists():
        return fallback
    return preferred


def _make_sanity_check(check_id: str, passed: bool, details: str) -> dict[str, Any]:
    return {"id": check_id, "status": "pass" if passed else "fail", "details": details}


def _build_artifact_paths(repo_root: Path) -> dict[str, Path]:
    bl003_paths = bl003_required_paths(repo_root)
    return {
        "bl003_summary": bl003_paths["summary"],
        "bl003_seed_table": bl003_paths["seed_table"],
        "profile": repo_root / "profile/outputs/bl004_preference_profile.json",
        "bl004_summary": repo_root / "profile/outputs/profile_summary.json",
        "bl005_filtered": repo_root / "retrieval/outputs/bl005_filtered_candidates.csv",
        "bl005_decisions": repo_root / "retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_diag": repo_root / "retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl006_scored": repo_root / "scoring/outputs/bl006_scored_candidates.csv",
        "bl006_summary": repo_root / "scoring/outputs/bl006_score_summary.json",
        "playlist": repo_root / "playlist/outputs/playlist.json",
        "bl007_trace": repo_root / "playlist/outputs/bl007_assembly_trace.csv",
        "bl007_report": repo_root / "playlist/outputs/bl007_assembly_report.json",
        "bl008_payloads": repo_root / "transparency/outputs/bl008_explanation_payloads.json",
        "bl008_summary": repo_root / "transparency/outputs/bl008_explanation_summary.json",
        "bl009_log": repo_root / "observability/outputs/bl009_run_observability_log.json",
        "bl009_index": repo_root / "observability/outputs/bl009_run_index.csv",
        "bl004_seed_trace": repo_root / "profile/outputs/bl004_seed_trace.csv",
    }


def _run_schema_and_handshake_checks(
    data: dict[str, Any],
    artifacts: dict[str, Path],
) -> list[dict[str, Any]]:
    bl003_summary = data["bl003_summary"]
    profile = data["profile"]
    bl004_summary = data["bl004_summary"]
    bl005_diag = data["bl005_diag"]
    bl006_summary = data["bl006_summary"]
    bl007_report = data["bl007_report"]
    bl008_summary = data["bl008_summary"]
    bl008_payloads = data["bl008_payloads"]
    playlist = data["playlist"]
    bl009_log = data["bl009_log"]
    bl010_snapshot = data["bl010_snapshot"]
    bl011_snapshot = data["bl011_snapshot"]

    bl003_required = {"inputs", "counts", "outputs"}
    profile_required = {
        "run_id", "task", "user_id", "matched_seed_count", "total_effective_weight",
        "dominant_lead_genres", "dominant_tags", "dominant_genres", "feature_centers",
        "input_hashes",
    }
    decisions_required_cols = {"track_id", "semantic_score", "decision", "decision_reason"}
    scored_required_cols = {
        "rank", "track_id", "lead_genre", "final_score",
        "lead_genre_contribution", "genre_overlap_contribution", "tag_overlap_contribution",
    }
    obs_required_sections = {
        "run_metadata", "run_config", "ingestion_alignment_diagnostics",
        "stage_diagnostics", "exclusion_diagnostics", "output_artifacts",
    }

    checks = [
        _make_sanity_check(
            "schema_bl003_summary",
            bl003_required.issubset(set(bl003_summary.keys())),
            "BL-003 summary contains required top-level keys",
        ),
        _make_sanity_check(
            "schema_bl004_summary",
            profile_required.issubset(set(bl004_summary.keys())),
            "BL-004 summary contains required top-level keys",
        ),
        _make_sanity_check(
            "schema_bl005_filtered_csv",
            bl005_filtered_has_required_columns(csv_header(artifacts["bl005_filtered"])),
            "BL-005 filtered candidates CSV contains required columns",
        ),
        _make_sanity_check(
            "schema_bl005_decisions_csv",
            decisions_required_cols.issubset(set(csv_header(artifacts["bl005_decisions"]))),
            "BL-005 decision trace CSV contains required columns",
        ),
        _make_sanity_check(
            "schema_bl006_scored_csv",
            scored_required_cols.issubset(set(csv_header(artifacts["bl006_scored"]))),
            "BL-006 scored candidates CSV contains required columns",
        ),
        _make_sanity_check(
            "schema_playlist_json",
            isinstance(playlist.get("tracks"), list)
            and playlist.get("playlist_length") == len(playlist.get("tracks", [])),
            "BL-007 playlist JSON tracks length matches playlist_length",
        ),
        _make_sanity_check(
            "schema_bl008_payloads_json",
            isinstance(bl008_payloads.get("explanations"), list)
            and bl008_payloads.get("playlist_track_count") == len(bl008_payloads.get("explanations", [])),
            "BL-008 payload JSON explanation count matches playlist_track_count",
        ),
        _make_sanity_check(
            "schema_observability_log",
            obs_required_sections.issubset(set(bl009_log.keys())),
            "BL-009 observability log contains required sections",
        ),
        _make_sanity_check(
            "schema_bl003_fuzzy_controls",
            isinstance((bl003_summary.get("inputs") or {}).get("fuzzy_matching"), dict),
            "BL-003 summary includes fuzzy matching control block",
        ),
    ]

    handshake_ok, handshake_details = bl003_bl004_handshake_contract_ok(bl003_summary, profile)
    checks.append(_make_sanity_check("schema_bl003_bl004_handshake_contract", handshake_ok, handshake_details))

    bl004_bl005_ok, bl004_bl005_details = bl004_bl005_handshake_contract_ok(
        profile, bl005_diag, csv_header(artifacts["bl004_seed_trace"]),
    )
    checks.append(_make_sanity_check("schema_bl004_bl005_handshake_contract", bl004_bl005_ok, bl004_bl005_details))

    bl005_bl006_ok, bl005_bl006_details = bl005_bl006_handshake_contract_ok(
        csv_header(artifacts["bl005_filtered"]), bl006_summary,
    )
    checks.append(_make_sanity_check("schema_bl005_bl006_handshake_contract", bl005_bl006_ok, bl005_bl006_details))

    bl006_bl007_ok, bl006_bl007_details = bl006_bl007_handshake_contract_ok(
        csv_header(artifacts["bl006_scored"]), bl007_report,
    )
    checks.append(_make_sanity_check("schema_bl006_bl007_handshake_contract", bl006_bl007_ok, bl006_bl007_details))

    bl007_bl008_ok, bl007_bl008_details = bl007_bl008_handshake_contract_ok(playlist, bl008_summary)
    checks.append(_make_sanity_check("schema_bl007_bl008_handshake_contract", bl007_bl008_ok, bl007_bl008_details))

    bl008_bl009_ok, bl008_bl009_details = bl008_bl009_handshake_contract_ok(
        bl008_summary, bl008_payloads, bl009_log,
    )
    checks.append(_make_sanity_check("schema_bl008_bl009_handshake_contract", bl008_bl009_ok, bl008_bl009_details))

    bl009_bl010_ok, bl009_bl010_details = bl009_bl010_handshake_contract_ok(bl010_snapshot)
    checks.append(_make_sanity_check(
        "schema_bl009_bl010_handshake_contract",
        bl009_bl010_ok if bl010_snapshot else True,
        bl009_bl010_details if bl010_snapshot else "BL-010 reproducibility not executed (optional)",
    ))

    bl010_bl011_ok, bl010_bl011_details = bl010_bl011_handshake_contract_ok(bl011_snapshot)
    checks.append(_make_sanity_check(
        "schema_bl010_bl011_handshake_contract",
        bl010_bl011_ok if bl011_snapshot else True,
        bl010_bl011_details if bl011_snapshot else "BL-011 controllability not executed (optional)",
    ))

    return checks


def _resolve_gates_and_advisories(
    data: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    bl005_diag = data["bl005_diag"]
    bl011_snapshot = data["bl011_snapshot"]
    bl011_report = data["bl011_report"]
    bl008_payloads = data["bl008_payloads"]
    bl009_log = data["bl009_log"]

    gate_results: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []

    handshake_warning_advisory = bl005_handshake_warning_volume_advisory(bl005_diag)
    if handshake_warning_advisory is not None:
        advisories.append(handshake_warning_advisory)

    control_resolution_advisory = bl005_control_resolution_fallback_volume_advisory(bl005_diag)
    if control_resolution_advisory is not None:
        advisories.append(control_resolution_advisory)

    bl005_threshold_diagnostics_policy = resolve_bl005_threshold_diagnostics_gate_policy(bl009_log)
    bl005_threshold_diagnostics_gate = bl005_threshold_diagnostics_contract_gate_result(
        bl005_diag, policy=bl005_threshold_diagnostics_policy,
    )
    if bl005_threshold_diagnostics_gate is not None:
        gate_results.append(bl005_threshold_diagnostics_gate)

    threshold_diagnostics_advisory = bl005_threshold_diagnostics_contract_advisory(
        bl005_diag, policy=bl005_threshold_diagnostics_policy,
    )
    if threshold_diagnostics_advisory is not None:
        advisories.append(threshold_diagnostics_advisory)

    bl011_control_effect_gate_policy = resolve_bl011_control_effect_gate_policy(
        bl011_snapshot, bl011_report, bl009_log,
    )
    bl011_control_effect_gate = bl011_control_effect_gate_result(
        bl011_report, policy=bl011_control_effect_gate_policy,
    )
    if bl011_control_effect_gate is not None:
        gate_results.append(bl011_control_effect_gate)

    bl008_control_causality_policy = resolve_bl008_control_causality_gate_policy(bl009_log)
    bl008_control_causality_gate = bl008_control_causality_contract_gate_result(
        bl008_payloads, policy=bl008_control_causality_policy,
    )
    if bl008_control_causality_gate is not None:
        gate_results.append(bl008_control_causality_gate)

    control_effect_gate_advisory = bl011_control_effect_gate_advisory(
        bl011_report, policy=bl011_control_effect_gate_policy,
    )
    if control_effect_gate_advisory is not None:
        advisories.append(control_effect_gate_advisory)

    control_causality_advisory = bl008_control_causality_contract_advisory(
        bl008_payloads, policy=bl008_control_causality_policy,
    )
    if control_causality_advisory is not None:
        advisories.append(control_causality_advisory)

    bl008_fidelity_warnings = bl008_explanation_fidelity_warnings(bl008_payloads)
    if bl008_fidelity_warnings:
        advisories.append({
            "id": "advisory_bl008_explanation_fidelity",
            "details": (
                "BL-008 explanation fidelity warnings detected in warn-safe mode; "
                f"warning_count={len(bl008_fidelity_warnings)} "
                f"sampled={bl008_fidelity_warnings[:5]}"
            ),
        })

    ctx: dict[str, Any] = {
        "bl005_threshold_diagnostics_policy": bl005_threshold_diagnostics_policy,
        "bl011_control_effect_gate_policy": bl011_control_effect_gate_policy,
        "bl008_control_causality_policy": bl008_control_causality_policy,
        "bl011_control_effect_gate": bl011_control_effect_gate,
        "bl005_threshold_diagnostics_gate": bl005_threshold_diagnostics_gate,
        "bl008_control_causality_gate": bl008_control_causality_gate,
    }
    return gate_results, advisories, ctx


def _run_hash_integrity_checks(
    data: dict[str, Any],
    artifacts: dict[str, Path],
    hashes: dict[str, str],
    candidate_stub_hash: str,
    bl009_index: dict[str, str],
) -> list[dict[str, Any]]:
    profile = data["profile"]
    bl005_diag = data["bl005_diag"]
    bl006_summary = data["bl006_summary"]
    bl007_report = data["bl007_report"]
    bl008_summary = data["bl008_summary"]

    profile_seed_table_path = resolve_existing_path(
        Path(profile["input_artifacts"]["seed_table_path"]),
        artifacts["bl003_seed_table"],
    )
    ensure_exists(profile_seed_table_path)

    return [
        _make_sanity_check(
            "hash_bl004_input_seed_table",
            profile["input_artifacts"]["seed_table_sha256"].upper() == sha256_file(profile_seed_table_path),
            "BL-004 profile links to the seed table hash recorded in its input artifacts",
        ),
        _make_sanity_check(
            "hash_bl005_input_profile",
            bl005_diag["input_artifacts"]["profile_sha256"].upper() == hashes["profile"],
            "BL-005 references BL-004 profile hash correctly",
        ),
        _make_sanity_check(
            "hash_bl005_input_seed_trace",
            bl005_diag["input_artifacts"]["seed_trace_sha256"].upper() == hashes["bl004_seed_trace"],
            "BL-005 references BL-004 seed trace hash correctly",
        ),
        _make_sanity_check(
            "hash_bl005_input_dataset",
            bl005_diag["input_artifacts"]["candidate_stub_sha256"].upper() == candidate_stub_hash,
            "BL-005 references candidate dataset hash correctly",
        ),
        _make_sanity_check(
            "hash_bl005_outputs",
            bl005_diag["output_hashes_sha256"]["bl005_filtered_candidates.csv"].upper() == hashes["bl005_filtered"]
            and bl005_diag["output_hashes_sha256"]["bl005_candidate_decisions.csv"].upper() == hashes["bl005_decisions"],
            "BL-005 output hashes match actual files",
        ),
        _make_sanity_check(
            "hash_bl006_inputs",
            bl006_summary["input_artifacts"]["profile_sha256"].upper() == hashes["profile"]
            and bl006_summary["input_artifacts"]["filtered_candidates_sha256"].upper() == hashes["bl005_filtered"],
            "BL-006 input hashes match BL-004 and BL-005 outputs",
        ),
        _make_sanity_check(
            "hash_bl006_output",
            bl006_summary["output_hashes_sha256"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"],
            "BL-006 output hash matches actual scored CSV",
        ),
        _make_sanity_check(
            "hash_bl007_links",
            bl007_report["input_artifact_hashes"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"]
            and bl007_report["output_artifact_hashes"]["playlist.json"].upper() == hashes["playlist"]
            and bl007_report["output_artifact_hashes"]["bl007_assembly_trace.csv"].upper() == hashes["bl007_trace"],
            "BL-007 report links to BL-006 input and BL-007 outputs correctly",
        ),
        _make_sanity_check(
            "hash_bl008_links",
            bl008_summary["input_artifact_hashes"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"]
            and bl008_summary["input_artifact_hashes"]["bl006_score_summary.json"].upper() == hashes["bl006_summary"]
            and bl008_summary["input_artifact_hashes"]["playlist.json"].upper() == hashes["playlist"]
            and bl008_summary["input_artifact_hashes"]["bl007_assembly_trace.csv"].upper() == hashes["bl007_trace"]
            and bl008_summary["output_artifact_hashes"]["bl008_explanation_payloads.json"].upper() == hashes["bl008_payloads"],
            "BL-008 summary links to upstream inputs and output hash correctly",
        ),
        _make_sanity_check(
            "hash_bl009_index",
            bl009_index["playlist_sha256"].upper() == hashes["playlist"]
            and bl009_index["explanation_payloads_sha256"].upper() == hashes["bl008_payloads"]
            and bl009_index["observability_log_sha256"].upper() == hashes["bl009_log"],
            "BL-009 index hashes match playlist, explanation payloads, and observability log",
        ),
    ]


def _run_continuity_and_count_checks(
    data: dict[str, Any],
    artifacts: dict[str, Path],
    bl009_index: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None, dict[str, Any]]:
    bl003_summary = data["bl003_summary"]
    bl004_summary = data["bl004_summary"]
    bl005_diag = data["bl005_diag"]
    bl006_summary = data["bl006_summary"]
    bl007_report = data["bl007_report"]
    bl008_summary = data["bl008_summary"]
    bl008_payloads = data["bl008_payloads"]
    bl009_log = data["bl009_log"]
    playlist = data["playlist"]

    bl003_fuzzy = dict((bl003_summary.get("inputs") or {}).get("fuzzy_matching") or {})
    bl003_counts = dict(bl003_summary.get("counts") or {})
    bl009_fuzzy = dict(
        ((bl009_log.get("run_config") or {}).get("alignment_seed_controls") or {}).get("fuzzy_matching") or {}
    )
    bl009_alignment_counts = dict(
        ((bl009_log.get("stage_diagnostics") or {}).get("alignment") or {}).get("counts") or {}
    )

    fuzzy_enabled = bool(bl003_fuzzy.get("enabled", False))
    matched_by_fuzzy = int(bl003_counts.get("matched_by_fuzzy", 0))
    bl005_kept = int(bl005_diag["counts"]["kept_candidates"])
    bl005_rows = csv_row_count(artifacts["bl005_filtered"])
    bl006_scored_count = int(bl006_summary["counts"]["candidates_scored"])
    bl006_rows = csv_row_count(artifacts["bl006_scored"])
    playlist_len = int(playlist["playlist_length"])
    bl007_target_size = int((playlist.get("config") or {}).get("target_size", playlist_len))
    undersized_shortfall = max(0, bl007_target_size - playlist_len)
    undersized_playlist = undersized_shortfall > 0
    explanations_len = int(bl008_payloads["playlist_track_count"])

    checks = [
        _make_sanity_check(
            "continuity_bl009_fuzzy_controls",
            bl009_fuzzy == bl003_fuzzy,
            "BL-009 run_config alignment fuzzy controls mirror BL-003 summary",
        ),
        _make_sanity_check(
            "continuity_bl009_fuzzy_count",
            int(bl009_alignment_counts.get("matched_by_fuzzy", 0)) == int(bl003_counts.get("matched_by_fuzzy", 0)),
            "BL-009 alignment diagnostics matched_by_fuzzy aligns with BL-003 summary",
        ),
        _make_sanity_check(
            "continuity_bl003_fuzzy_enabled_consistency",
            matched_by_fuzzy == 0 if not fuzzy_enabled else matched_by_fuzzy >= 0,
            "BL-003 matched_by_fuzzy is zero when fuzzy is disabled",
        ),
        _make_sanity_check(
            "continuity_bl005_count",
            bl005_kept == bl005_rows,
            f"BL-005 kept_candidates ({bl005_kept}) equals filtered CSV rows ({bl005_rows})",
        ),
        _make_sanity_check(
            "continuity_bl006_count",
            bl006_scored_count == bl006_rows,
            f"BL-006 candidates_scored ({bl006_scored_count}) equals scored CSV rows ({bl006_rows})",
        ),
        _make_sanity_check(
            "continuity_bl007_bl008_counts",
            playlist_len == len(playlist["tracks"]) == explanations_len == len(bl008_payloads["explanations"]),
            "BL-007 playlist length and BL-008 explanation count are aligned",
        ),
        _make_sanity_check(
            "quality_bl007_target_size_met",
            playlist_len >= bl007_target_size,
            f"BL-007 playlist length ({playlist_len}) meets target_size ({bl007_target_size})",
        ),
        _make_sanity_check(
            "continuity_bl009_index_counts",
            int(bl009_index["kept_candidates"]) == bl005_kept
            and int(bl009_index["candidates_scored"]) == bl006_scored_count
            and int(bl009_index["playlist_length"]) == playlist_len
            and int(bl009_index["explanation_count"]) == explanations_len,
            "BL-009 index counts match BL-005/006/007/008 outputs",
        ),
        _make_sanity_check(
            "continuity_bl009_run_ids",
            bl009_index["profile_run_id"] == bl004_summary["run_id"]
            and bl009_index["retrieval_run_id"] == bl005_diag["run_id"]
            and bl009_index["scoring_run_id"] == bl006_summary["run_id"]
            and bl009_index["assembly_run_id"] == bl007_report["run_id"]
            and bl009_index["transparency_run_id"] == bl008_summary["run_id"],
            "BL-009 index run_ids match upstream stage run_ids",
        ),
    ]

    undersized_advisory: dict[str, Any] | None = None
    if undersized_playlist:
        undersized_advisory = {
            "id": "advisory_bl007_undersized_playlist",
            "details": (
                f"BL-007 produced {playlist_len}/{bl007_target_size} tracks "
                f"(shortfall={undersized_shortfall}). Review BL-007 assembly report "
                "undersized_playlist_warning for exclusion pressures."
            ),
        }

    counts: dict[str, Any] = {
        "bl005_kept": bl005_kept,
        "bl006_scored_count": bl006_scored_count,
        "playlist_len": playlist_len,
        "bl007_target_size": bl007_target_size,
        "undersized_playlist": undersized_playlist,
        "undersized_shortfall": undersized_shortfall,
        "explanations_len": explanations_len,
        "fuzzy_enabled": fuzzy_enabled,
        "matched_by_fuzzy": matched_by_fuzzy,
    }
    return checks, undersized_advisory, counts


def _load_sanity_data(artifacts: dict[str, Path], repo_root: Path) -> dict[str, Any]:
    bl010_path = repo_root / "reproducibility/outputs/reproducibility_config_snapshot.json"
    bl011_path = repo_root / "controllability/outputs/controllability_config_snapshot.json"
    bl011_report_path = repo_root / "controllability/outputs/controllability_report.json"
    return {
        "bl003_summary": load_json(artifacts["bl003_summary"]),
        "profile": load_json(artifacts["profile"]),
        "bl004_summary": load_json(artifacts["bl004_summary"]),
        "bl005_diag": load_json(artifacts["bl005_diag"]),
        "bl006_summary": load_json(artifacts["bl006_summary"]),
        "bl007_report": load_json(artifacts["bl007_report"]),
        "bl008_summary": load_json(artifacts["bl008_summary"]),
        "bl008_payloads": load_json(artifacts["bl008_payloads"]),
        "playlist": load_json(artifacts["playlist"]),
        "bl009_log": load_json(artifacts["bl009_log"]),
        "bl010_snapshot": load_json(bl010_path) if bl010_path.exists() else {},
        "bl011_snapshot": load_json(bl011_path) if bl011_path.exists() else {},
        "bl011_report": load_json(bl011_report_path) if bl011_report_path.exists() else {},
    }


def _gate_status(gate: dict[str, Any] | None) -> str:
    return str(gate.get("status")) if gate is not None else "not_executed"


def _build_matrix_row(
    run_id: str,
    report: dict[str, Any],
    gate_ctx: dict[str, Any],
    counts: dict[str, Any],
    bl009_index: dict[str, str],
    hashes: dict[str, str],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "generated_at_utc": report["generated_at_utc"],
        "overall_status": report["overall_status"],
        "checks_total": report["checks_total"],
        "checks_passed": report["checks_passed"],
        "checks_failed": report["checks_failed"],
        "bl005_kept_candidates": counts["bl005_kept"],
        "bl006_candidates_scored": counts["bl006_scored_count"],
        "playlist_length": counts["playlist_len"],
        "bl007_target_size": counts["bl007_target_size"],
        "undersized_playlist": str(counts["undersized_playlist"]).lower(),
        "undersized_shortfall": counts["undersized_shortfall"],
        "explanation_count": counts["explanations_len"],
        "bl003_fuzzy_enabled": str(counts["fuzzy_enabled"]).lower(),
        "bl003_matched_by_fuzzy": counts["matched_by_fuzzy"],
        "bl011_control_effect_gate_policy": gate_ctx["bl011_control_effect_gate_policy"],
        "bl011_control_effect_gate_status": _gate_status(gate_ctx["bl011_control_effect_gate"]),
        "bl005_threshold_diagnostics_contract_policy": gate_ctx["bl005_threshold_diagnostics_policy"],
        "bl005_threshold_diagnostics_contract_status": _gate_status(gate_ctx["bl005_threshold_diagnostics_gate"]),
        "bl008_control_causality_contract_policy": gate_ctx["bl008_control_causality_policy"],
        "bl008_control_causality_contract_status": _gate_status(gate_ctx["bl008_control_causality_gate"]),
        "bl009_run_id": bl009_index["run_id"],
        "playlist_sha256": hashes["playlist"],
        "bl008_payloads_sha256": hashes["bl008_payloads"],
        "bl009_log_sha256": hashes["bl009_log"],
    }


def main() -> int:
    started = datetime.now(UTC)
    run_id = f"BL014-SANITY-{started.strftime('%Y%m%d-%H%M%S-%f')}"

    artifacts = _build_artifact_paths(REPO_ROOT)
    for artifact_path in artifacts.values():
        if artifact_path.exists():
            continue
        # BL-010 and BL-011 diagnostic outputs are optional (only required if tests executed)
        if "bl010_snapshot" in str(artifact_path) or "bl011_snapshot" in str(artifact_path):
            continue
        ensure_exists(artifact_path)

    data = _load_sanity_data(artifacts, REPO_ROOT)

    with artifacts["bl009_index"].open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        bl009_index_rows = list(reader)
    if len(bl009_index_rows) != 1:
        raise RuntimeError("Expected exactly one row in bl009_run_index.csv")
    bl009_index = bl009_index_rows[0]

    hashes = {name: sha256_file(path) for name, path in artifacts.items()}
    candidate_stub_path = resolve_existing_path(
        Path(data["bl005_diag"]["input_artifacts"]["candidate_stub_path"]),
        REPO_ROOT / "data_layer/outputs/ds001_working_candidate_dataset.csv",
    )
    ensure_exists(candidate_stub_path)
    candidate_stub_hash = sha256_file(candidate_stub_path)

    checks: list[dict[str, Any]] = _run_schema_and_handshake_checks(data, artifacts)
    gate_results, advisories, gate_ctx = _resolve_gates_and_advisories(data)
    checks += _run_hash_integrity_checks(data, artifacts, hashes, candidate_stub_hash, bl009_index)
    continuity_checks, undersized_advisory, counts = _run_continuity_and_count_checks(
        data, artifacts, bl009_index,
    )
    checks += continuity_checks
    if undersized_advisory is not None:
        advisories.append(undersized_advisory)

    passed = sum(1 for item in checks if item["status"] == "pass")
    failed = len(checks) - passed
    gate_failures = sum(1 for item in gate_results if item.get("status") == "fail")
    overall_status = "pass" if failed == 0 and gate_failures == 0 else "fail"

    finished = datetime.now(UTC)
    elapsed_seconds = round((finished - started).total_seconds(), 3)

    report = {
        "run_id": run_id,
        "task": "BL-014",
        "generated_at_utc": format_utc_iso(finished),
        "elapsed_seconds": elapsed_seconds,
        "overall_status": overall_status,
        "checks_total": len(checks),
        "checks_passed": passed,
        "checks_failed": failed,
        "advisories_total": len(advisories),
        "advisories": advisories,
        "gate_results_total": len(gate_results),
        "gate_failures_total": gate_failures,
        "gate_results": gate_results,
        "artifact_hashes_sha256": {k: v for k, v in hashes.items()},
        "checks": checks,
    }

    config_snapshot = {
        "task": "BL-014",
        "description": "Automated sanity checks for BL-020 artifact schema, hash linkage, and count continuity",
        "run_id": run_id,
        "required_artifacts": {k: str(v.relative_to(REPO_ROOT)) for k, v in artifacts.items()},
        "schema_checks": [
            "BL-003 summary top-level keys",
            "BL-004 summary top-level keys",
            "BL-005 filtered CSV required columns",
            "BL-005 decisions CSV required columns",
            "BL-006 scored CSV required columns",
            "BL-007 playlist length consistency",
            "BL-008 explanation count consistency",
            "BL-009 required top-level observability sections",
            "BL-003 fuzzy control block presence",
            "BL-003↔BL-004 handshake contract fields and policy metadata",
            "BL-005↔BL-006 handshake contract fields and policy metadata",
        ],
        "integrity_checks": [
            "BL-004 seed table hash links to BL-003 seed table",
            "BL-005 input/output hashes",
            "BL-006 input/output hashes",
            "BL-007 input/output hashes",
            "BL-008 input/output hashes",
            "BL-009 index hash linkage",
        ],
        "continuity_checks": [
            "BL-003 fuzzy enabled consistency against matched_by_fuzzy",
            "BL-009 fuzzy controls mirror BL-003 controls",
            "BL-009 fuzzy count mirrors BL-003 count",
            "BL-005 kept count matches filtered rows",
            "BL-006 scored count matches scored rows",
            "BL-007 playlist count aligns with BL-008 explanations",
            "BL-007 playlist meets configured target size",
            "BL-009 index counts align with upstream stage outputs",
            "BL-009 run_id linkage aligns with upstream stage summaries",
        ],
        "advisory_thresholds": {
            "bl005_handshake_warn_max_violations": BL005_HANDSHAKE_WARN_MAX_VIOLATIONS_ADVISORY_THRESHOLD,
            "bl005_control_resolution_fallback_max_events": BL005_RUNTIME_CONTROL_FALLBACK_ADVISORY_THRESHOLD,
        },
        "validation_policies": {
            "bl005_threshold_diagnostics_contract_policy": gate_ctx["bl005_threshold_diagnostics_policy"],
            "bl005_threshold_diagnostics_contract_policy_env_var": BL005_THRESHOLD_DIAGNOSTICS_GATE_POLICY_ENV_VAR,
            "bl011_control_effect_gate_policy": gate_ctx["bl011_control_effect_gate_policy"],
            "bl011_control_effect_gate_policy_env_var": BL011_CONTROL_EFFECT_GATE_POLICY_ENV_VAR,
            "bl008_control_causality_contract_policy": gate_ctx["bl008_control_causality_policy"],
            "bl008_control_causality_contract_policy_env_var": BL008_CONTROL_CAUSALITY_GATE_POLICY_ENV_VAR,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "bl014_sanity_report.json"
    config_path = OUTPUT_DIR / "bl014_sanity_config_snapshot.json"
    matrix_path = OUTPUT_DIR / "bl014_sanity_run_matrix.csv"

    write_json_ascii(report_path, report)
    write_json_ascii(config_path, config_snapshot)
    write_csv_rows(matrix_path, [_build_matrix_row(run_id, report, gate_ctx, counts, bl009_index, hashes)])

    print(f"[BL-014] run_id={run_id}")
    print(f"[BL-014] overall_status={overall_status} checks_passed={passed}/{len(checks)}")
    print(f"[BL-014] report={report_path}")
    print(f"[BL-014] run_matrix={matrix_path}")
    print(f"[BL-014] config_snapshot={config_path}")

    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
