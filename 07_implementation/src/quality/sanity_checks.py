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
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


from shared_utils.artifact_registry import bl003_required_paths
from shared_utils.io_utils import load_json as load_json_shared
from shared_utils.io_utils import sha256_of_file, format_utc_iso
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
BL005_HANDSHAKE_WARN_MAX_VIOLATIONS_ADVISORY_THRESHOLD = 3
BL005_RUNTIME_CONTROL_FALLBACK_ADVISORY_THRESHOLD = 3


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


def ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path}")


def resolve_existing_path(preferred: Path, fallback: Path) -> Path:
    if preferred.exists():
        return preferred
    if fallback.exists():
        return fallback
    return preferred


def main() -> int:
    started = datetime.now(UTC)
    run_id = f"BL014-SANITY-{started.strftime('%Y%m%d-%H%M%S-%f')}"

    bl003_paths = bl003_required_paths(REPO_ROOT)
    artifacts = {
        "bl003_summary": bl003_paths["summary"],
        "bl003_seed_table": bl003_paths["seed_table"],
        "profile": REPO_ROOT / "profile/outputs/bl004_preference_profile.json",
        "bl004_summary": REPO_ROOT / "profile/outputs/profile_summary.json",
        "bl005_filtered": REPO_ROOT / "retrieval/outputs/bl005_filtered_candidates.csv",
        "bl005_decisions": REPO_ROOT / "retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_diag": REPO_ROOT / "retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl006_scored": REPO_ROOT / "scoring/outputs/bl006_scored_candidates.csv",
        "bl006_summary": REPO_ROOT / "scoring/outputs/bl006_score_summary.json",
        "playlist": REPO_ROOT / "playlist/outputs/playlist.json",
        "bl007_trace": REPO_ROOT / "playlist/outputs/bl007_assembly_trace.csv",
        "bl007_report": REPO_ROOT / "playlist/outputs/bl007_assembly_report.json",
        "bl008_payloads": REPO_ROOT / "transparency/outputs/bl008_explanation_payloads.json",
        "bl008_summary": REPO_ROOT / "transparency/outputs/bl008_explanation_summary.json",
        "bl009_log": REPO_ROOT / "observability/outputs/bl009_run_observability_log.json",
        "bl009_index": REPO_ROOT / "observability/outputs/bl009_run_index.csv",
        "bl004_seed_trace": REPO_ROOT / "profile/outputs/bl004_seed_trace.csv",
    }

    for artifact_path in artifacts.values():
        ensure_exists(artifact_path)

    bl003_summary = load_json(artifacts["bl003_summary"])
    profile = load_json(artifacts["profile"])
    bl004_summary = load_json(artifacts["bl004_summary"])
    bl005_diag = load_json(artifacts["bl005_diag"])
    bl006_summary = load_json(artifacts["bl006_summary"])
    bl007_report = load_json(artifacts["bl007_report"])
    bl008_summary = load_json(artifacts["bl008_summary"])
    bl008_payloads = load_json(artifacts["bl008_payloads"])
    playlist = load_json(artifacts["playlist"])
    bl009_log = load_json(artifacts["bl009_log"])

    with artifacts["bl009_index"].open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        bl009_index_rows = list(reader)
    if len(bl009_index_rows) != 1:
        raise RuntimeError("Expected exactly one row in bl009_run_index.csv")
    bl009_index = bl009_index_rows[0]

    hashes = {name: sha256_file(path) for name, path in artifacts.items()}

    checks: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, details: str) -> None:
        checks.append({"id": check_id, "status": "pass" if passed else "fail", "details": details})

    # Schema checks
    bl003_required = {"inputs", "counts", "outputs"}
    check(
        "schema_bl003_summary",
        bl003_required.issubset(set(bl003_summary.keys())),
        "BL-003 summary contains required top-level keys",
    )

    profile_required = {
        "run_id",
        "task",
        "user_id",
        "matched_seed_count",
        "total_effective_weight",
        "dominant_lead_genres",
        "dominant_tags",
        "dominant_genres",
        "feature_centers",
        "input_hashes",
    }
    check(
        "schema_bl004_summary",
        profile_required.issubset(set(bl004_summary.keys())),
        "BL-004 summary contains required top-level keys",
    )

    candidate_stub_path = resolve_existing_path(
        Path(bl005_diag["input_artifacts"]["candidate_stub_path"]),
        REPO_ROOT / "data_layer/outputs/ds001_working_candidate_dataset.csv",
    )
    ensure_exists(candidate_stub_path)
    candidate_stub_hash = sha256_file(candidate_stub_path)

    check(
        "schema_bl005_filtered_csv",
        bl005_filtered_has_required_columns(csv_header(artifacts["bl005_filtered"])),
        "BL-005 filtered candidates CSV contains required columns",
    )

    decisions_required_cols = {
        "track_id",
        "semantic_score",
        "decision",
        "decision_reason",
    }
    check(
        "schema_bl005_decisions_csv",
        decisions_required_cols.issubset(set(csv_header(artifacts["bl005_decisions"]))),
        "BL-005 decision trace CSV contains required columns",
    )

    scored_required_cols = {
        "rank",
        "track_id",
        "lead_genre",
        "final_score",
        "lead_genre_contribution",
        "genre_overlap_contribution",
        "tag_overlap_contribution",
    }
    check(
        "schema_bl006_scored_csv",
        scored_required_cols.issubset(set(csv_header(artifacts["bl006_scored"]))),
        "BL-006 scored candidates CSV contains required columns",
    )

    check(
        "schema_playlist_json",
        isinstance(playlist.get("tracks"), list)
        and playlist.get("playlist_length") == len(playlist.get("tracks", [])),
        "BL-007 playlist JSON tracks length matches playlist_length",
    )

    check(
        "schema_bl008_payloads_json",
        isinstance(bl008_payloads.get("explanations"), list)
        and bl008_payloads.get("playlist_track_count") == len(bl008_payloads.get("explanations", [])),
        "BL-008 payload JSON explanation count matches playlist_track_count",
    )

    obs_required_sections = {
        "run_metadata",
        "run_config",
        "ingestion_alignment_diagnostics",
        "stage_diagnostics",
        "exclusion_diagnostics",
        "output_artifacts",
    }
    check(
        "schema_observability_log",
        obs_required_sections.issubset(set(bl009_log.keys())),
        "BL-009 observability log contains required sections",
    )
    check(
        "schema_bl003_fuzzy_controls",
        isinstance((bl003_summary.get("inputs") or {}).get("fuzzy_matching"), dict),
        "BL-003 summary includes fuzzy matching control block",
    )
    handshake_ok, handshake_details = bl003_bl004_handshake_contract_ok(
        bl003_summary,
        profile,
    )
    check(
        "schema_bl003_bl004_handshake_contract",
        handshake_ok,
        handshake_details,
    )
    bl004_bl005_ok, bl004_bl005_details = bl004_bl005_handshake_contract_ok(
        profile,
        bl005_diag,
        csv_header(artifacts["bl004_seed_trace"]),
    )
    check(
        "schema_bl004_bl005_handshake_contract",
        bl004_bl005_ok,
        bl004_bl005_details,
    )
    handshake_warning_advisory = bl005_handshake_warning_volume_advisory(bl005_diag)
    if handshake_warning_advisory is not None:
        advisories.append(handshake_warning_advisory)
    control_resolution_advisory = bl005_control_resolution_fallback_volume_advisory(
        bl005_diag
    )
    if control_resolution_advisory is not None:
        advisories.append(control_resolution_advisory)

    # Hash-link integrity checks
    profile_seed_table_path = resolve_existing_path(
        Path(profile["input_artifacts"]["seed_table_path"]),
        artifacts["bl003_seed_table"],
    )
    ensure_exists(profile_seed_table_path)
    check(
        "hash_bl004_input_seed_table",
        profile["input_artifacts"]["seed_table_sha256"].upper() == sha256_file(profile_seed_table_path),
        "BL-004 profile links to the seed table hash recorded in its input artifacts",
    )

    check(
        "hash_bl005_input_profile",
        bl005_diag["input_artifacts"]["profile_sha256"].upper() == hashes["profile"],
        "BL-005 references BL-004 profile hash correctly",
    )
    check(
        "hash_bl005_input_seed_trace",
        bl005_diag["input_artifacts"]["seed_trace_sha256"].upper() == hashes["bl004_seed_trace"],
        "BL-005 references BL-004 seed trace hash correctly",
    )
    check(
        "hash_bl005_input_dataset",
        bl005_diag["input_artifacts"]["candidate_stub_sha256"].upper() == candidate_stub_hash,
        "BL-005 references candidate dataset hash correctly",
    )
    check(
        "hash_bl005_outputs",
        bl005_diag["output_hashes_sha256"]["bl005_filtered_candidates.csv"].upper() == hashes["bl005_filtered"]
        and bl005_diag["output_hashes_sha256"]["bl005_candidate_decisions.csv"].upper() == hashes["bl005_decisions"],
        "BL-005 output hashes match actual files",
    )

    check(
        "hash_bl006_inputs",
        bl006_summary["input_artifacts"]["profile_sha256"].upper() == hashes["profile"]
        and bl006_summary["input_artifacts"]["filtered_candidates_sha256"].upper() == hashes["bl005_filtered"],
        "BL-006 input hashes match BL-004 and BL-005 outputs",
    )
    check(
        "hash_bl006_output",
        bl006_summary["output_hashes_sha256"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"],
        "BL-006 output hash matches actual scored CSV",
    )

    check(
        "hash_bl007_links",
        bl007_report["input_artifact_hashes"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"]
        and bl007_report["output_artifact_hashes"]["playlist.json"].upper() == hashes["playlist"]
        and bl007_report["output_artifact_hashes"]["bl007_assembly_trace.csv"].upper() == hashes["bl007_trace"],
        "BL-007 report links to BL-006 input and BL-007 outputs correctly",
    )

    check(
        "hash_bl008_links",
        bl008_summary["input_artifact_hashes"]["bl006_scored_candidates.csv"].upper() == hashes["bl006_scored"]
        and bl008_summary["input_artifact_hashes"]["bl006_score_summary.json"].upper() == hashes["bl006_summary"]
        and bl008_summary["input_artifact_hashes"]["playlist.json"].upper() == hashes["playlist"]
        and bl008_summary["input_artifact_hashes"]["bl007_assembly_trace.csv"].upper() == hashes["bl007_trace"]
        and bl008_summary["output_artifact_hashes"]["bl008_explanation_payloads.json"].upper() == hashes["bl008_payloads"],
        "BL-008 summary links to upstream inputs and output hash correctly",
    )

    check(
        "hash_bl009_index",
        bl009_index["playlist_sha256"].upper() == hashes["playlist"]
        and bl009_index["explanation_payloads_sha256"].upper() == hashes["bl008_payloads"]
        and bl009_index["observability_log_sha256"].upper() == hashes["bl009_log"],
        "BL-009 index hashes match playlist, explanation payloads, and observability log",
    )

    bl003_fuzzy = dict((bl003_summary.get("inputs") or {}).get("fuzzy_matching") or {})
    bl003_counts = dict(bl003_summary.get("counts") or {})
    bl009_fuzzy = dict((((bl009_log.get("run_config") or {}).get("alignment_seed_controls") or {}).get("fuzzy_matching") or {}))
    bl009_alignment_counts = dict((((bl009_log.get("stage_diagnostics") or {}).get("alignment") or {}).get("counts") or {}))

    check(
        "continuity_bl009_fuzzy_controls",
        bl009_fuzzy == bl003_fuzzy,
        "BL-009 run_config alignment fuzzy controls mirror BL-003 summary",
    )

    check(
        "continuity_bl009_fuzzy_count",
        int(bl009_alignment_counts.get("matched_by_fuzzy", 0)) == int(bl003_counts.get("matched_by_fuzzy", 0)),
        "BL-009 alignment diagnostics matched_by_fuzzy aligns with BL-003 summary",
    )

    fuzzy_enabled = bool(bl003_fuzzy.get("enabled", False))
    matched_by_fuzzy = int(bl003_counts.get("matched_by_fuzzy", 0))
    check(
        "continuity_bl003_fuzzy_enabled_consistency",
        matched_by_fuzzy == 0 if not fuzzy_enabled else matched_by_fuzzy >= 0,
        "BL-003 matched_by_fuzzy is zero when fuzzy is disabled",
    )

    # Count/run-id continuity checks
    bl005_kept = int(bl005_diag["counts"]["kept_candidates"])
    bl005_rows = csv_row_count(artifacts["bl005_filtered"])
    check(
        "continuity_bl005_count",
        bl005_kept == bl005_rows,
        f"BL-005 kept_candidates ({bl005_kept}) equals filtered CSV rows ({bl005_rows})",
    )

    bl006_scored_count = int(bl006_summary["counts"]["candidates_scored"])
    bl006_rows = csv_row_count(artifacts["bl006_scored"])
    check(
        "continuity_bl006_count",
        bl006_scored_count == bl006_rows,
        f"BL-006 candidates_scored ({bl006_scored_count}) equals scored CSV rows ({bl006_rows})",
    )

    playlist_len = int(playlist["playlist_length"])
    bl007_target_size = int((playlist.get("config") or {}).get("target_size", playlist_len))
    undersized_shortfall = max(0, bl007_target_size - playlist_len)
    undersized_playlist = undersized_shortfall > 0
    explanations_len = int(bl008_payloads["playlist_track_count"])
    check(
        "continuity_bl007_bl008_counts",
        playlist_len == len(playlist["tracks"]) == explanations_len == len(bl008_payloads["explanations"]),
        "BL-007 playlist length and BL-008 explanation count are aligned",
    )

    check(
        "quality_bl007_target_size_met",
        playlist_len >= bl007_target_size,
        f"BL-007 playlist length ({playlist_len}) meets target_size ({bl007_target_size})",
    )

    check(
        "continuity_bl009_index_counts",
        int(bl009_index["kept_candidates"]) == bl005_kept
        and int(bl009_index["candidates_scored"]) == bl006_scored_count
        and int(bl009_index["playlist_length"]) == playlist_len
        and int(bl009_index["explanation_count"]) == explanations_len,
        "BL-009 index counts match BL-005/006/007/008 outputs",
    )

    check(
        "continuity_bl009_run_ids",
        bl009_index["profile_run_id"] == bl004_summary["run_id"]
        and bl009_index["retrieval_run_id"] == bl005_diag["run_id"]
        and bl009_index["scoring_run_id"] == bl006_summary["run_id"]
        and bl009_index["assembly_run_id"] == bl007_report["run_id"]
        and bl009_index["transparency_run_id"] == bl008_summary["run_id"],
        "BL-009 index run_ids match upstream stage run_ids",
    )

    if undersized_playlist:
        advisories.append(
            {
                "id": "advisory_bl007_undersized_playlist",
                "details": (
                    f"BL-007 produced {playlist_len}/{bl007_target_size} tracks "
                    f"(shortfall={undersized_shortfall}). Review BL-007 assembly report "
                    "undersized_playlist_warning for exclusion pressures."
                ),
            }
        )

    passed = sum(1 for item in checks if item["status"] == "pass")
    failed = len(checks) - passed
    overall_status = "pass" if failed == 0 else "fail"

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
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "bl014_sanity_report.json"
    config_path = OUTPUT_DIR / "bl014_sanity_config_snapshot.json"
    matrix_path = OUTPUT_DIR / "bl014_sanity_run_matrix.csv"

    write_json_ascii(report_path, report)
    write_json_ascii(config_path, config_snapshot)
    write_csv_rows(
        matrix_path,
        [
            {
                "run_id": run_id,
                "generated_at_utc": report["generated_at_utc"],
                "overall_status": overall_status,
                "checks_total": len(checks),
                "checks_passed": passed,
                "checks_failed": failed,
                "bl005_kept_candidates": bl005_kept,
                "bl006_candidates_scored": bl006_scored_count,
                "playlist_length": playlist_len,
                "bl007_target_size": bl007_target_size,
                "undersized_playlist": str(undersized_playlist).lower(),
                "undersized_shortfall": undersized_shortfall,
                "explanation_count": explanations_len,
                "bl003_fuzzy_enabled": str(fuzzy_enabled).lower(),
                "bl003_matched_by_fuzzy": matched_by_fuzzy,
                "bl009_run_id": bl009_index["run_id"],
                "playlist_sha256": hashes["playlist"],
                "bl008_payloads_sha256": hashes["bl008_payloads"],
                "bl009_log_sha256": hashes["bl009_log"],
            }
        ],
    )

    print(f"[BL-014] run_id={run_id}")
    print(f"[BL-014] overall_status={overall_status} checks_passed={passed}/{len(checks)}")
    print(f"[BL-014] report={report_path}")
    print(f"[BL-014] run_matrix={matrix_path}")
    print(f"[BL-014] config_snapshot={config_path}")

    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
