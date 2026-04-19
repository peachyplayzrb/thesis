"""Input validation for BL-009 observability outputs - BL-009 output file contract."""

from __future__ import annotations

import json

from shared_utils.validation_policy import normalize_validation_policy, resolve_policy_status

REQUIRED_BL009_OUTPUT_ARTIFACTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("bl009_run_observability_log.json", ("observability/outputs/bl009_run_observability_log.json",)),
    ("bl009_run_index.csv", ("observability/outputs/bl009_run_index.csv",)),
    (
        "bl008_explanation_payloads.json",
        (
            "transparency/outputs/bl008_explanation_payloads.json",
            "observability/outputs/bl008_run_explanations_log.json",
        ),
    ),
    (
        "bl007_assembly_report.json",
        (
            "playlist/outputs/bl007_assembly_report.json",
            "observability/outputs/bl007_run_assembly_report.json",
        ),
    ),
    (
        "bl006_score_summary.json",
        (
            "scoring/outputs/bl006_score_summary.json",
            "observability/outputs/bl006_run_scores_log.json",
        ),
    ),
    (
        "bl005_candidate_diagnostics.json",
        (
            "retrieval/outputs/bl005_candidate_diagnostics.json",
            "observability/outputs/bl005_run_retrieval_diagnostics.json",
        ),
    ),
    (
        "profile_summary.json",
        (
            "profile/outputs/profile_summary.json",
            "observability/outputs/bl004_run_profile_diagnostics.json",
        ),
    ),
    (
        "bl003_ds001_spotify_summary.json",
        (
            "alignment/outputs/bl003_ds001_spotify_summary.json",
            "observability/outputs/bl003_run_summary.json",
        ),
    ),
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
    repo_root = output_path.parent.parent if output_path.name == "outputs" else output_path
    violations = []
    missing_files = []
    invalid_json = []
    missing_log_keys = []

    # Check for required output files
    for logical_name, candidate_paths in REQUIRED_BL009_OUTPUT_ARTIFACTS:
        if any((repo_root / candidate_path).exists() for candidate_path in candidate_paths):
            continue
        missing_files.append(logical_name)
        violations.append(f"missing_file={logical_name}")

    # Validate observability log JSON structure
    log_path = output_path / "bl009_run_observability_log.json"
    if log_path.exists():
        try:
            with open(log_path, encoding="utf-8") as f:
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
        except (OSError, json.JSONDecodeError) as e:
            violations.append(f"invalid_bl009_log_json={str(e)[:50]}")
            invalid_json.append("bl009_run_observability_log.json")

    # Determine status
    status = resolve_policy_status(normalized_policy, violations)

    return {
        "policy": normalized_policy,
        "status": status,
        "violations": violations,
        "details": {
            "missing_files": missing_files,
            "invalid_json": invalid_json,
            "missing_log_keys": missing_log_keys,
            "checked_output_dir": str(output_path),
            "file_count_expected": len(REQUIRED_BL009_OUTPUT_ARTIFACTS),
            "file_count_found": len(REQUIRED_BL009_OUTPUT_ARTIFACTS) - len(missing_files),
        },
    }
