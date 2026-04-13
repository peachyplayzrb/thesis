"""Input validation for BL-009 observability outputs - BL-009 output file contract."""

from __future__ import annotations

import json

from typing import Any, Mapping


VALIDATION_POLICIES: tuple[str, ...] = ("allow", "warn", "strict")

REQUIRED_BL009_OUTPUT_FILES: tuple[str, ...] = (
    "bl009_run_observability_log.json",
    "bl009_run_index.csv",
    "bl008_run_explanations_log.json",
    "bl007_run_assembly_report.json",
    "bl006_run_scores_log.json",
    "bl005_run_retrieval_diagnostics.json",
    "bl004_run_profile_diagnostics.json",
    "bl003_run_summary.json",
    "bl003_run_seed_diagnostics.json",
)

REQUIRED_BL009_LOG_KEYS: tuple[str, ...] = (
    "run_metadata",
    "execution_scope_summary",
    "run_config",
    "ingestion_alignment_diagnostics",
    "stage_diagnostics",
    "exclusion_diagnostics",
    "validity_boundaries",
    "output_artifacts",
)


def normalize_validation_policy(policy: Any, default: str = "warn") -> str:
    """Normalize policy string to one of: allow, warn, strict."""
    value = str(policy or default).strip().lower()
    if value in VALIDATION_POLICIES:
        return value
    return default


def validate_bl009_outputs(
    bl009_output_dir: str,
    policy: str,
) -> dict[str, object]:
    """Validate BL-009 output files and observability log structure.

    Returns:
        dict with keys: policy, status, violations, details
        - policy: normalized policy (allow|warn|strict)
        - status: pass|warn|fail
        - violations: list of violation strings
        - details: additional context
    """
    normalized_policy = normalize_validation_policy(policy)

    from pathlib import Path

    output_path = Path(bl009_output_dir)
    violations = []
    missing_files = []
    invalid_json = []
    missing_log_keys = []

    # Check for required output files
    for filename in REQUIRED_BL009_OUTPUT_FILES:
        file_path = output_path / filename
        if not file_path.exists():
            missing_files.append(filename)
            violations.append(f"missing_file={filename}")

    # Validate observability log JSON structure
    log_path = output_path / "bl009_run_observability_log.json"
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                log_data = json.load(f)

            if not isinstance(log_data, dict):
                violations.append("bl009_observability_log_not_dict")
                invalid_json.append("bl009_run_observability_log.json")
            else:
                # Check for required top-level keys in observability log
                missing_keys = [
                    key for key in REQUIRED_BL009_LOG_KEYS
                    if key not in log_data
                ]
                if missing_keys:
                    missing_log_keys = missing_keys
                    violations.append(f"missing_log_keys={missing_keys}")
        except (json.JSONDecodeError, IOError) as e:
            violations.append(f"invalid_bl009_log_json={str(e)[:50]}")
            invalid_json.append("bl009_run_observability_log.json")

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
            "missing_files": missing_files,
            "invalid_json": invalid_json,
            "missing_log_keys": missing_log_keys,
            "checked_output_dir": str(output_path),
            "file_count_expected": len(REQUIRED_BL009_OUTPUT_FILES),
            "file_count_found": len(REQUIRED_BL009_OUTPUT_FILES) - len(missing_files),
        },
    }
