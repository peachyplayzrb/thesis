from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import time
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared.io_utils import load_json, sha256_of_file, utc_now
from shared.path_utils import impl_root

from alignment import (
    ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION,
    ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION,
    MATCH_STRATEGY_ORDER,
    AlignmentBehaviorControls,
    AlignmentStructuralContract,
    build_seed_contract_payload,
    build_structural_contract_payload,
    canonical_json_hash,
)


PAYLOAD_SCHEMA_VERSION = "1.0"

DEFAULT_SEED_CONTROLS: dict[str, Any] = {
    "match_rate_min_threshold": 0.0,
    "top_range_weights": {
        "short_term": 0.50,
        "medium_term": 0.30,
        "long_term": 0.20,
    },
    "source_base_weights": {
        "top_tracks": 1.00,
        "saved_tracks": 0.60,
        "playlist_items": 0.40,
        "recently_played": 0.50,
    },
    "decay_half_lives": {
        "recently_played": 90.0,
        "saved_tracks": 365.0,
    },
    "fuzzy_matching": {
        "enabled": False,
        "artist_threshold": 0.90,
        "title_threshold": 0.90,
        "combined_threshold": 0.90,
        "max_duration_delta_ms": 5000,
        "max_artist_candidates": 5,
    },
    "match_strategy": {
        "enable_spotify_id_match": True,
        "enable_metadata_match": True,
        "enable_fuzzy_match": True,
    },
    "match_strategy_order": [
        "spotify_id_exact",
        "metadata_fallback",
        "fuzzy_title_artist",
    ],
    "temporal_controls": {
        "reference_mode": "system",
        "reference_now_utc": None,
    },
    "aggregation_policy": {
        "preference_weight_mode": "sum",
        "preference_weight_cap_per_event": None,
    },
}


def load_run_config_utils_module() -> Any:
    module_path = impl_root() / "run_config" / "run_config_utils.py"
    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json_ascii(path: Path, payload: dict[str, object] | list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


STAGE_SCRIPT_MAP: dict[str, str] = {
    "BL-003": "alignment.py",
    "BL-004": "profile.py",
    "BL-005": "retrieval.py",
    "BL-006": "scoring.py",
    "BL-007": "playlist.py",
    "BL-008": "transparency.py",
    "BL-009": "observability.py",
}
BL003_SCRIPT: str = "alignment.py"
BL003_SUMMARY_PATH: str = "alignment/outputs/bl003_ds001_spotify_summary.json"
DEFAULT_STAGE_ORDER: list[str] = ["BL-003", "BL-004", "BL-005", "BL-006", "BL-007", "BL-008", "BL-009"]
STABLE_ARTIFACTS: dict[str, str] = {
    "bl004_seed_trace": "profile/outputs/bl004_seed_trace.csv",
    "bl005_filtered_candidates": "retrieval/outputs/bl005_filtered_candidates.csv",
    "bl005_candidate_decisions": "retrieval/outputs/bl005_candidate_decisions.csv",
    "bl006_scored_candidates": "scoring/outputs/bl006_scored_candidates.csv",
    "bl007_assembly_trace": "playlist/outputs/bl007_assembly_trace.csv",
}

SUMMARY_NOTES: dict[str, str] = {
    "purpose": "Lightweight wrapper to run BL-003..BL-009 scripts in one command.",
    "repeatability_check_guidance": (
        "Compare stable_artifact_hashes between repeated runs under unchanged inputs/config."
    ),
}


@dataclass
class StageResult:
    stage_id: str
    script_path: str
    command: list[str]
    run_config_path: str | None
    run_intent_path: str | None
    run_effective_config_path: str | None
    return_code: int
    status: str
    elapsed_seconds: float
    stdout: str
    stderr: str
    payload_source: str | None = None
    payload_resolved_from: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BL-013 lightweight orchestrator for bootstrap pipeline stages BL-004 to BL-009."
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        default=None,
        help="Ordered stage IDs to run (default: BL-004 BL-005 BL-006 BL-007 BL-008 BL-009)",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue executing remaining stages after a failure.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to run stage scripts.",
    )
    parser.add_argument(
        "--output-dir",
        default="orchestration/outputs",
        help="Directory for BL-013 orchestration run summaries.",
    )
    parser.add_argument(
        "--summary-prefix",
        default="bl013_orchestration_run",
        help="Filename prefix for summary JSON artifacts.",
    )
    parser.add_argument(
        "--run-config",
        default=None,
        help=(
            "Optional path to a canonical run-config JSON file used by orchestration "
            "to resolve stage payloads."
        ),
    )
    parser.add_argument(
        "--refresh-seed",
        action="store_true",
        help=(
            "Run BL-003 seed-table rebuild before BL-004..BL-009. "
            "Useful when run-config input_scope changes."
        ),
    )
    parser.add_argument(
        "--run-config-artifact-dir",
        default="run_config/outputs",
        help=(
            "Directory where canonical run_intent/run_effective_config artifacts "
            "are emitted for this BL-013 run."
        ),
    )
    parser.add_argument(
        "--strict-stage-payload",
        action="store_true",
        help=(
            "Enable strict stage payload mode by exporting BL_STRICT_STAGE_PAYLOAD=true "
            "to all stage subprocesses."
        ),
    )
    return parser.parse_args()


def validate_stage_order(stage_ids: list[str]) -> list[str]:
    normalized: list[str] = []
    for stage_id in stage_ids:
        token = stage_id.strip().upper()
        if token not in STAGE_SCRIPT_MAP:
            valid = ", ".join(DEFAULT_STAGE_ORDER)
            raise ValueError(f"Unsupported stage '{stage_id}'. Valid values: {valid}")
        normalized.append(token)
    return normalized


def _build_stage_payload(
    *,
    stage_id: str,
    run_config_path: Path | None,
    controls: dict[str, object],
) -> dict[str, object]:
    return {
        "stage_id": stage_id,
        "run_config_path": str(run_config_path) if run_config_path else None,
        "controls": controls,
    }


def resolve_stage_control_payload(stage_id: str, run_config_path: Path | None) -> dict[str, object]:
    run_config_utils = load_run_config_utils_module()
    rc_path = str(run_config_path) if run_config_path else None
    stage_bundle = run_config_utils.resolve_stage_control_bundle(rc_path)
    controls = stage_bundle.get(stage_id)
    if controls is None:
        raise ValueError(f"Unsupported stage for payload resolution: {stage_id}")
    return _build_stage_payload(
        stage_id=stage_id,
        run_config_path=run_config_path,
        controls=dict(controls),
    )


def resolve_stage_control_payloads(
    stage_order: list[str],
    run_config_path: Path | None,
    *,
    include_stage_ids: list[str] | None = None,
) -> dict[str, dict[str, object]]:
    run_config_utils = load_run_config_utils_module()
    rc_path = str(run_config_path) if run_config_path else None
    stage_bundle = run_config_utils.resolve_stage_control_bundle(rc_path)
    ordered_stage_ids: list[str] = []
    for stage_id in stage_order:
        if stage_id not in ordered_stage_ids:
            ordered_stage_ids.append(stage_id)
    for stage_id in include_stage_ids or []:
        if stage_id not in ordered_stage_ids:
            ordered_stage_ids.append(stage_id)
    payloads: dict[str, dict[str, object]] = {}
    for stage_id in ordered_stage_ids:
        controls = stage_bundle.get(stage_id)
        if controls is None:
            raise ValueError(f"Unsupported stage for payload resolution: {stage_id}")
        payloads[stage_id] = _build_stage_payload(
            stage_id=stage_id,
            run_config_path=run_config_path,
            controls=dict(controls),
        )
    return payloads


def validate_stage_payloads(
    stage_payloads: dict[str, dict[str, object]],
    required_stage_ids: list[str],
) -> tuple[bool, str]:
    missing_stage_ids = [stage_id for stage_id in required_stage_ids if stage_id not in stage_payloads]
    if missing_stage_ids:
        return (
            False,
            "Missing payload(s) for stage(s): " + ", ".join(sorted(missing_stage_ids)),
        )

    malformed: list[str] = []
    for stage_id in required_stage_ids:
        payload = stage_payloads.get(stage_id)
        if not isinstance(payload, dict):
            malformed.append(f"{stage_id}:payload_not_object")
            continue
        payload_stage_id = str(payload.get("stage_id") or "")
        if payload_stage_id != stage_id:
            malformed.append(f"{stage_id}:stage_id_mismatch")
        schema_version = str(payload.get("schema_version") or "")
        if schema_version != PAYLOAD_SCHEMA_VERSION:
            malformed.append(f"{stage_id}:invalid_schema_version")
        controls = payload.get("controls")
        if not isinstance(controls, dict) or not controls:
            malformed.append(f"{stage_id}:missing_controls")

    if malformed:
        return (
            False,
            "Malformed payload(s): " + ", ".join(malformed),
        )
    return True, "ok"


def build_missing_script_result(
    *,
    stage_id: str,
    script_relpath: str,
    python_executable: str,
    run_config_path: Path | None,
    run_intent_path: Path | None,
    run_effective_config_path: Path | None,
) -> StageResult:
    return StageResult(
        stage_id=stage_id,
        script_path=script_relpath,
        command=[python_executable, script_relpath],
        run_config_path=str(run_config_path) if run_config_path else None,
        run_intent_path=str(run_intent_path) if run_intent_path else None,
        run_effective_config_path=str(run_effective_config_path) if run_effective_config_path else None,
        return_code=127,
        status="fail",
        elapsed_seconds=0.0,
        stdout="",
        stderr=f"Missing stage script: {script_relpath}",
        payload_source="missing_script",
        payload_resolved_from=None,
    )


def run_stage(
    python_executable: str,
    stage_id: str,
    script_path: Path,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path | None,
    run_effective_config_path: Path | None,
    stage_config_payload: dict[str, object] | None = None,
    strict_stage_payload: bool = False,
) -> StageResult:
    if stage_config_payload is None:
        raise RuntimeError(f"Missing stage config payload for {stage_id}")

    command = [python_executable, str(script_path)]
    stage_env = os.environ.copy()
    existing_pythonpath = stage_env.get("PYTHONPATH", "").strip()
    stage_root = str(root)
    stage_env["PYTHONPATH"] = (
        stage_root
        if not existing_pythonpath
        else os.pathsep.join([stage_root, existing_pythonpath])
    )
    if run_intent_path is not None:
        stage_env["BL_RUN_INTENT_PATH"] = str(run_intent_path)
    if run_effective_config_path is not None:
        stage_env["BL_RUN_EFFECTIVE_CONFIG_PATH"] = str(run_effective_config_path)
    stage_env["BL_ORCHESTRATION_MODE"] = "true"
    if strict_stage_payload:
        stage_env["BL_STRICT_STAGE_PAYLOAD"] = "true"
    else:
        stage_env.pop("BL_STRICT_STAGE_PAYLOAD", None)

    stage_env["BL_STAGE_CONFIG_JSON"] = json.dumps(
        stage_config_payload,
        ensure_ascii=True,
        sort_keys=True,
    )
    started = time.time()
    process = subprocess.run(
        command,
        cwd=str(root),
        env=stage_env,
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed = round(time.time() - started, 3)

    return StageResult(
        stage_id=stage_id,
        script_path=script_path.relative_to(root).as_posix(),
        command=command,
        run_config_path=str(run_config_path) if run_config_path else None,
        run_intent_path=str(run_intent_path) if run_intent_path else None,
        run_effective_config_path=str(run_effective_config_path) if run_effective_config_path else None,
        return_code=process.returncode,
        status="pass" if process.returncode == 0 else "fail",
        elapsed_seconds=elapsed,
        stdout=process.stdout.strip(),
        stderr=process.stderr.strip(),
        payload_source="orchestration_payload",
        payload_resolved_from=str(stage_config_payload.get("resolved_from") or "unknown"),
    )


def run_bl003_seed_refresh(
    python_executable: str,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path | None,
    run_effective_config_path: Path | None,
    stage_config_payload: dict[str, object] | None = None,
    strict_stage_payload: bool = False,
) -> StageResult:
    script_path = root / BL003_SCRIPT
    if not script_path.exists():
        return build_missing_script_result(
            stage_id="BL-003",
            script_relpath=BL003_SCRIPT,
            python_executable=python_executable,
            run_config_path=run_config_path,
            run_intent_path=run_intent_path,
            run_effective_config_path=run_effective_config_path,
        )

    return run_stage(
        python_executable=python_executable,
        stage_id="BL-003",
        script_path=script_path,
        root=root,
        run_config_path=run_config_path,
        run_intent_path=run_intent_path,
        run_effective_config_path=run_effective_config_path,
        stage_config_payload=stage_config_payload,
        strict_stage_payload=strict_stage_payload,
    )


def _normalize_weighting_policy(seed_controls: dict[str, Any]) -> dict[str, float]:
    raw_policy = seed_controls.get("weighting_policy") or {}
    if not isinstance(raw_policy, dict):
        raw_policy = {}

    top_tracks = raw_policy.get("top_tracks") or {}
    playlist_items = raw_policy.get("playlist_items") or {}
    if not isinstance(top_tracks, dict):
        top_tracks = {}
    if not isinstance(playlist_items, dict):
        playlist_items = {}

    return {
        "top_tracks_min_rank_floor": float(top_tracks.get("min_rank_floor", 0.05)),
        "top_tracks_scale_multiplier": float(top_tracks.get("scale_multiplier", 100.0)),
        "top_tracks_default_time_range_weight": float(top_tracks.get("default_time_range_weight", 0.2)),
        "playlist_items_min_position_floor": float(playlist_items.get("min_position_floor", 0.05)),
        "playlist_items_scale_multiplier": float(playlist_items.get("scale_multiplier", 20.0)),
    }


def _build_behavior_controls(
    input_scope: dict[str, Any],
    influence: dict[str, Any],
    seed_controls: dict[str, Any],
) -> AlignmentBehaviorControls:
    fuzzy_defaults = dict(DEFAULT_SEED_CONTROLS.get("fuzzy_matching") or {})
    match_strategy_defaults = dict(DEFAULT_SEED_CONTROLS.get("match_strategy") or {})
    temporal_defaults = dict(DEFAULT_SEED_CONTROLS.get("temporal_controls") or {})
    aggregation_defaults = dict(DEFAULT_SEED_CONTROLS.get("aggregation_policy") or {})

    fuzzy_matching = seed_controls.get("fuzzy_matching") or {}
    match_strategy = seed_controls.get("match_strategy") or {}
    match_strategy_order = seed_controls.get("match_strategy_order") or []
    temporal_controls = seed_controls.get("temporal_controls") or {}
    aggregation_policy = seed_controls.get("aggregation_policy") or {}
    seed_aggregation_health = seed_controls.get("seed_aggregation_health") or {}

    if not isinstance(fuzzy_matching, dict):
        fuzzy_matching = {}
    if not isinstance(match_strategy, dict):
        match_strategy = {}
    if not isinstance(match_strategy_order, list):
        match_strategy_order = []
    if not isinstance(temporal_controls, dict):
        temporal_controls = {}
    if not isinstance(aggregation_policy, dict):
        aggregation_policy = {}
    if not isinstance(seed_aggregation_health, dict):
        seed_aggregation_health = {}

    return AlignmentBehaviorControls(
        input_scope=dict(input_scope),
        top_range_weights=dict(seed_controls.get("top_range_weights") or {}),
        source_base_weights=dict(seed_controls.get("source_base_weights") or {}),
        decay_half_lives=dict(seed_controls.get("decay_half_lives") or {}),
        match_rate_min_threshold=float(seed_controls.get("match_rate_min_threshold", 0.0)),
        fuzzy_matching_controls={
            "enabled": bool(fuzzy_matching.get("enabled", False)),
            "artist_threshold": float(fuzzy_matching.get("artist_threshold", fuzzy_defaults.get("artist_threshold", 0.90))),
            "title_threshold": float(fuzzy_matching.get("title_threshold", fuzzy_defaults.get("title_threshold", 0.90))),
            "combined_threshold": float(fuzzy_matching.get("combined_threshold", fuzzy_defaults.get("combined_threshold", 0.90))),
            "max_duration_delta_ms": int(fuzzy_matching.get("max_duration_delta_ms", fuzzy_defaults.get("max_duration_delta_ms", 5000))),
            "max_artist_candidates": int(fuzzy_matching.get("max_artist_candidates", fuzzy_defaults.get("max_artist_candidates", 5))),
        },
        match_strategy={
            "enable_spotify_id_match": bool(match_strategy.get("enable_spotify_id_match", match_strategy_defaults.get("enable_spotify_id_match", True))),
            "enable_metadata_match": bool(match_strategy.get("enable_metadata_match", match_strategy_defaults.get("enable_metadata_match", True))),
            "enable_fuzzy_match": bool(match_strategy.get("enable_fuzzy_match", match_strategy_defaults.get("enable_fuzzy_match", True))),
        },
        match_strategy_order=list(match_strategy_order or MATCH_STRATEGY_ORDER),
        temporal_controls={
            "reference_mode": str(temporal_controls.get("reference_mode", temporal_defaults.get("reference_mode", "system"))),
            "reference_now_utc": temporal_controls.get("reference_now_utc", temporal_defaults.get("reference_now_utc")),
        },
        aggregation_policy={
            "preference_weight_mode": str(aggregation_policy.get("preference_weight_mode", aggregation_defaults.get("preference_weight_mode", "sum"))),
            "preference_weight_cap_per_event": aggregation_policy.get("preference_weight_cap_per_event", aggregation_defaults.get("preference_weight_cap_per_event")),
        },
        seed_aggregation_health={
            "warn_min_ratio": float(seed_aggregation_health.get("warn_min_ratio", 0.01)),
            "collapse_max_rows": int(seed_aggregation_health.get("collapse_max_rows", 1)),
        },
        weighting_policy=_normalize_weighting_policy(seed_controls),
        influence_controls={
            "influence_enabled": bool(influence.get("enabled", False)),
            "influence_track_ids": list(influence.get("track_ids") or []),
            "influence_preference_weight": float(influence.get("preference_weight", 1.0)),
        },
    )


def _strip_contract_hash(contract: Any) -> tuple[dict[str, Any], str]:
    if not isinstance(contract, dict):
        return {}, ""
    payload = dict(contract)
    raw_hash = payload.pop("contract_hash", "")
    return payload, str(raw_hash or "")


def _normalized_contract_from_effective(run_effective_config_path: Path) -> dict[str, object]:
    payload = load_json(run_effective_config_path)
    effective = payload.get("effective_config") or {}
    if not isinstance(effective, dict):
        effective = {}

    input_scope = effective.get("input_scope") or {}
    influence = effective.get("influence_tracks") or {}
    seed_controls = effective.get("seed_controls") or {}
    if not isinstance(input_scope, dict):
        input_scope = {}
    if not isinstance(influence, dict):
        influence = {}
    if not isinstance(seed_controls, dict):
        seed_controls = {}

    behavior_controls = _build_behavior_controls(input_scope, influence, seed_controls)
    structural_contract_model = AlignmentStructuralContract.from_defaults()
    seed_contract = build_seed_contract_payload(behavior_controls)
    structural_contract = build_structural_contract_payload(structural_contract_model)

    return {
        "seed_contract": seed_contract,
        "seed_contract_hash": canonical_json_hash(seed_contract),
        "structural_contract": structural_contract,
        "structural_contract_hash": canonical_json_hash(structural_contract),
    }


def _normalized_contract_from_bl003_summary(summary_path: Path) -> dict[str, object]:
    payload = load_json(summary_path)
    inputs = payload.get("inputs") or {}
    if not isinstance(inputs, dict):
        raise RuntimeError("BL-003 summary malformed: inputs block missing")

    raw_seed_contract = inputs.get("seed_contract") or {}
    if raw_seed_contract and not isinstance(raw_seed_contract, dict):
        raise RuntimeError("BL-003 summary malformed: seed_contract must be an object")
    seed_contract, seed_contract_hash = _strip_contract_hash(raw_seed_contract)
    raw_structural_contract = inputs.get("structural_contract") or {}
    if raw_structural_contract and not isinstance(raw_structural_contract, dict):
        raise RuntimeError("BL-003 summary malformed: structural_contract must be an object")
    structural_contract, structural_contract_hash = _strip_contract_hash(raw_structural_contract)

    if not isinstance(seed_contract, dict):
        seed_contract = {}
    if not isinstance(structural_contract, dict):
        structural_contract = {}

    return {
        "config_source": str(inputs.get("config_source") or ""),
        "run_config_path": inputs.get("run_config_path"),
        "seed_contract": seed_contract,
        "seed_contract_hash": seed_contract_hash,
        "structural_contract": structural_contract,
        "structural_contract_hash": structural_contract_hash,
    }


def validate_bl003_seed_freshness(
    root: Path,
    run_config_path: Path,
    run_effective_config_path: Path,
) -> tuple[bool, str]:
    summary_path = root / BL003_SUMMARY_PATH
    if not summary_path.exists():
        return False, "BL-003 summary missing; cannot validate seed freshness"

    expected = _normalized_contract_from_effective(run_effective_config_path)
    try:
        observed = _normalized_contract_from_bl003_summary(summary_path)
    except RuntimeError as exc:
        return False, str(exc)

    if str(observed.get("config_source") or "") != "run_config":
        return False, "BL-003 seed was not built in run_config mode"

    observed_path = observed.get("run_config_path")
    if observed_path and str(Path(str(observed_path)).resolve()) != str(run_config_path.resolve()):
        return False, "BL-003 seed was built with a different run_config path"

    expected_seed_contract = dict(expected.get("seed_contract") or {})
    observed_seed_contract = dict(observed.get("seed_contract") or {})
    if not observed_seed_contract:
        return False, "BL-003 seed contract missing from summary"

    if str(observed_seed_contract.get("seed_contract_schema_version") or "") != ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION:
        return False, "BL-003 seed contract schema version does not match current contract"

    expected_seed_hash = str(expected.get("seed_contract_hash") or "")
    observed_seed_hash = str(observed.get("seed_contract_hash") or "")
    if observed_seed_hash and observed_seed_hash != expected_seed_hash:
        return False, "BL-003 seed contract hash does not match current effective run_config"

    if observed_seed_contract != expected_seed_contract:
        return False, "BL-003 seed contract does not match current effective run_config"

    expected_structural_contract = dict(expected.get("structural_contract") or {})
    observed_structural_contract = dict(observed.get("structural_contract") or {})
    if not observed_structural_contract:
        return False, "BL-003 structural contract missing from summary"

    if str(observed_structural_contract.get("structural_contract_schema_version") or "") != ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION:
        return False, "BL-003 structural contract schema version does not match current contract"

    expected_structural_hash = str(expected.get("structural_contract_hash") or "")
    observed_structural_hash = str(observed.get("structural_contract_hash") or "")
    if observed_structural_hash and observed_structural_hash != expected_structural_hash:
        return False, "BL-003 structural contract hash does not match current contract"

    if observed_structural_contract != expected_structural_contract:
        return False, "BL-003 structural contract does not match current contract"

    return True, "ok"


def compute_stable_artifact_hashes(root: Path) -> tuple[dict[str, str], list[str]]:
    hashes: dict[str, str] = {}
    missing: list[str] = []

    for alias, relative_path in STABLE_ARTIFACTS.items():
        artifact_path = root / relative_path
        if not artifact_path.exists():
            missing.append(relative_path)
            continue
        hashes[alias] = sha256_of_file(artifact_path, uppercase=True)

    return hashes, missing


def collect_refinement_diagnostics(root: Path) -> dict[str, object]:
    diagnostics: dict[str, object] = {
        "bl006_distribution": {"available": False},
        "bl007_assembly_pressure": {"available": False},
    }

    bl006_distribution_path = (
        root
        / "scoring"
        / "outputs"
        / "bl006_score_distribution_diagnostics.json"
    )
    if bl006_distribution_path.exists():
        bl006_distribution = load_json(bl006_distribution_path)
        diagnostics["bl006_distribution"] = {
            "available": True,
            "path": bl006_distribution_path.relative_to(root).as_posix(),
            "rank_cliff": bl006_distribution.get("rank_cliff", {}),
        }

    bl007_report_path = (
        root
        / "playlist"
        / "outputs"
        / "bl007_assembly_report.json"
    )
    if bl007_report_path.exists():
        bl007_report = load_json(bl007_report_path)
        diagnostics["bl007_assembly_pressure"] = {
            "available": True,
            "path": bl007_report_path.relative_to(root).as_posix(),
            "rank_continuity_diagnostics": bl007_report.get("rank_continuity_diagnostics", {}),
            "assembly_pressure_diagnostics": bl007_report.get("assembly_pressure_diagnostics", {}),
        }

    return diagnostics


class Orchestrator:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.root = impl_root()
        self.run_config_path = (self.root / args.run_config).resolve() if args.run_config else None
        if self.run_config_path is not None and not self.run_config_path.exists():
            raise FileNotFoundError(f"Run config file not found: {self.run_config_path}")

        self.stage_results: list[StageResult] = []
        self.output_dir = self.root / args.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.run_id = f"BL013-ENTRYPOINT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
        self.generated_at_utc = utc_now()
        self.pipeline_started = time.time()

        self.oc: dict[str, Any] = resolve_orchestration_controls(self.run_config_path)
        self.oc_stage_order: list[str] | None = self.oc.get("stage_order")  # type: ignore[assignment]
        self.oc_continue: bool = bool(self.oc.get("continue_on_error", False))
        self.oc_refresh_policy: str = str(self.oc.get("refresh_seed_policy") or "auto_if_stale")

        if args.stages is not None:
            self.stage_order = validate_stage_order(args.stages)
        elif self.oc_stage_order:
            self.stage_order = validate_stage_order(self.oc_stage_order)
        else:
            self.stage_order = list(DEFAULT_STAGE_ORDER)

        self.effective_continue_on_error: bool = bool(args.continue_on_error) or self.oc_continue
        if self.oc_refresh_policy == "always":
            self.effective_refresh_seed = True
        elif self.oc_refresh_policy == "never":
            self.effective_refresh_seed = False
        else:
            self.effective_refresh_seed = bool(args.refresh_seed)
        self.strict_stage_payload = bool(args.strict_stage_payload)

        self.stage_control_payloads = resolve_stage_control_payloads(
            self.stage_order,
            self.run_config_path,
            include_stage_ids=["BL-003"] if self.effective_refresh_seed else None,
        )

        run_config_artifact_dir = (self.root / args.run_config_artifact_dir).resolve()
        self.run_config_artifacts = emit_run_config_artifact_pair(
            run_id=self.run_id,
            run_config_path=self.run_config_path,
            artifact_dir=run_config_artifact_dir,
            generated_at_utc=self.generated_at_utc,
        )
        self.run_intent_path = Path(str(dict(self.run_config_artifacts["run_intent"])["path"]))
        self.run_effective_config_path = Path(
            str(dict(self.run_config_artifacts["run_effective_config"])["path"])
        )

    def _stage_order_for_execution(self) -> list[str]:
        # When seed refresh is enabled, BL-003 is executed in the refresh block.
        # Skip BL-003 in the normal stage loop to avoid duplicate execution.
        if not self.effective_refresh_seed:
            return list(self.stage_order)
        return [stage_id for stage_id in self.stage_order if stage_id != "BL-003"]

    def _append_guard_failure(self, reason: str) -> None:
        self.stage_results.append(
            StageResult(
                stage_id="BL-003-FRESHNESS-GUARD",
                script_path=BL003_SCRIPT,
                command=[self.args.python, BL003_SCRIPT],
                run_config_path=str(self.run_config_path) if self.run_config_path else None,
                run_intent_path=str(self.run_intent_path),
                run_effective_config_path=str(self.run_effective_config_path),
                return_code=2,
                status="fail",
                elapsed_seconds=0.0,
                stdout="",
                stderr=(
                    f"Seed freshness guard failed: {reason}. "
                    "Run BL-013 with --refresh-seed or set refresh_seed_policy=always in run-config."
                ),
                payload_source="preflight_guard",
                payload_resolved_from=None,
            )
        )

    def _append_payload_preflight_failure(self, reason: str) -> None:
        self.stage_results.append(
            StageResult(
                stage_id="BL-013-PAYLOAD-PREFLIGHT",
                script_path="<none>",
                command=[self.args.python, "<preflight>"],
                run_config_path=str(self.run_config_path) if self.run_config_path else None,
                run_intent_path=str(self.run_intent_path),
                run_effective_config_path=str(self.run_effective_config_path),
                return_code=2,
                status="fail",
                elapsed_seconds=0.0,
                stdout="",
                stderr=f"Payload preflight validation failed: {reason}",
                payload_source="preflight_guard",
                payload_resolved_from=None,
            )
        )

    def _finalize(self) -> tuple[dict[str, Any], Path, Path]:
        elapsed_pipeline = round(time.time() - self.pipeline_started, 3)
        failed = [item for item in self.stage_results if item.status == "fail"]
        expected_stage_count = len(self._stage_order_for_execution()) + (
            1 if self.effective_refresh_seed else 0
        )
        overall_status = "pass" if not failed and len(self.stage_results) == expected_stage_count else "fail"

        stable_hashes, missing_stable = compute_stable_artifact_hashes(self.root)
        stage_diagnostics = collect_refinement_diagnostics(self.root)
        payload_source_counts: dict[str, int] = {}
        payload_resolved_from_counts: dict[str, int] = {}
        executed_pipeline_stages: list[StageResult] = [
            item for item in self.stage_results if item.stage_id in STAGE_SCRIPT_MAP
        ]
        for item in executed_pipeline_stages:
            source = item.payload_source or "unknown"
            payload_source_counts[source] = payload_source_counts.get(source, 0) + 1
            resolved_from = item.payload_resolved_from or "unknown"
            payload_resolved_from_counts[resolved_from] = payload_resolved_from_counts.get(resolved_from, 0) + 1

        payload_adoption_rate = 0.0
        if executed_pipeline_stages:
            payload_adoption_rate = round(
                payload_source_counts.get("orchestration_payload", 0)
                / len(executed_pipeline_stages),
                6,
            )
        stages_with_orchestration_payload: list[str] = []
        for item in executed_pipeline_stages:
            if item.payload_source != "orchestration_payload":
                continue
            if item.stage_id in stages_with_orchestration_payload:
                continue
            stages_with_orchestration_payload.append(item.stage_id)

        summary: dict[str, Any] = {
            "run_id": self.run_id,
            "task": "BL-013",
            "generated_at_utc": self.generated_at_utc,
            "overall_status": overall_status,
            "continue_on_error": self.effective_continue_on_error,
            "python_executable": self.args.python,
            "run_config_path": str(self.run_config_path) if self.run_config_path else None,
            "canonical_run_config_artifacts": self.run_config_artifacts,
            "refresh_seed": self.effective_refresh_seed,
            "strict_stage_payload": self.strict_stage_payload,
            "requested_stage_order": self.stage_order,
            "executed_stage_count": len(self.stage_results),
            "failed_stage_count": len(failed),
            "elapsed_seconds": elapsed_pipeline,
            "stage_results": [item.to_dict() for item in self.stage_results],
            "control_source_summary": {
                "payload_source_counts": payload_source_counts,
                "payload_resolved_from_counts": payload_resolved_from_counts,
                "payload_adoption_rate": payload_adoption_rate,
                "stages_with_orchestration_payload": stages_with_orchestration_payload,
            },
            "stage_diagnostics": stage_diagnostics,
            "stable_artifact_hashes": stable_hashes,
            "missing_stable_artifacts": missing_stable,
            "notes": SUMMARY_NOTES,
        }

        summary_path = self.output_dir / f"{self.args.summary_prefix}_{self.run_id}.json"
        latest_path = self.output_dir / f"{self.args.summary_prefix}_latest.json"
        write_json_ascii(summary_path, summary)
        write_json_ascii(latest_path, summary)
        return summary, summary_path, latest_path

    def _abort(self) -> None:
        summary, summary_path, latest_path = self._finalize()
        print(f"BL-013 orchestration complete: status={summary['overall_status']}")
        print(f"run_id={self.run_id}")
        print(f"summary={summary_path}")
        print(f"latest={latest_path}")
        for item in self.stage_results:
            if item.status == "fail":
                print(f"failed_stage={item.stage_id} return_code={item.return_code}")
        raise SystemExit(1)

    def _run_stage_order(self) -> None:
        for stage_id in self._stage_order_for_execution():
            script_relpath = STAGE_SCRIPT_MAP[stage_id]
            script_path = self.root / script_relpath
            if not script_path.exists():
                self.stage_results.append(
                    build_missing_script_result(
                        stage_id=stage_id,
                        script_relpath=script_relpath,
                        python_executable=self.args.python,
                        run_config_path=self.run_config_path,
                        run_intent_path=self.run_intent_path,
                        run_effective_config_path=self.run_effective_config_path,
                    )
                )
                if not self.effective_continue_on_error:
                    break
                continue

            result = run_stage(
                self.args.python,
                stage_id,
                script_path,
                self.root,
                self.run_config_path,
                self.run_intent_path,
                self.run_effective_config_path,
                stage_config_payload=self.stage_control_payloads.get(stage_id),
                strict_stage_payload=self.strict_stage_payload,
            )
            self.stage_results.append(result)

            if result.status == "fail" and not self.effective_continue_on_error:
                break

    def run(self) -> None:
        required_stage_ids = list(self.stage_order)
        if self.effective_refresh_seed and "BL-003" not in required_stage_ids:
            required_stage_ids.append("BL-003")
        payloads_valid, payload_reason = validate_stage_payloads(
            self.stage_control_payloads,
            required_stage_ids,
        )
        if not payloads_valid:
            self._append_payload_preflight_failure(payload_reason)
            self._abort()

        if (
            self.oc_refresh_policy != "never"
            and self.run_config_path is not None
            and not self.effective_refresh_seed
        ):
            is_fresh, reason = validate_bl003_seed_freshness(
                root=self.root,
                run_config_path=self.run_config_path,
                run_effective_config_path=self.run_effective_config_path,
            )
            if not is_fresh:
                self._append_guard_failure(reason)
                self._abort()

        if self.effective_refresh_seed:
            if "BL-003" not in self.stage_control_payloads:
                self.stage_control_payloads["BL-003"] = resolve_stage_control_payload(
                    "BL-003",
                    self.run_config_path,
                )
            seed_result = run_bl003_seed_refresh(
                self.args.python,
                self.root,
                self.run_config_path,
                self.run_intent_path,
                self.run_effective_config_path,
                stage_config_payload=self.stage_control_payloads.get("BL-003"),
                strict_stage_payload=self.strict_stage_payload,
            )
            self.stage_results.append(seed_result)
            if seed_result.status == "fail" and not self.effective_continue_on_error:
                self._abort()

        self._run_stage_order()

        summary, summary_path, latest_path = self._finalize()
        print(f"BL-013 orchestration complete: status={summary['overall_status']}")
        print(f"run_id={self.run_id}")
        print(f"summary={summary_path}")
        print(f"latest={latest_path}")

        failed = [item for item in self.stage_results if item.status == "fail"]
        if failed:
            for item in failed:
                print(f"failed_stage={item.stage_id} return_code={item.return_code}")
            raise SystemExit(1)


def main() -> None:
    orchestrator = Orchestrator(parse_args())
    orchestrator.run()


if __name__ == "__main__":
    main()
