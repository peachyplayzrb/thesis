from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


STAGES = {
    "BL-004": "07_implementation/implementation_notes/profile/build_bl004_preference_profile.py",
    "BL-005": "07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py",
    "BL-006": "07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py",
    "BL-007": "07_implementation/implementation_notes/playlist/build_bl007_playlist.py",
    "BL-008": "07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py",
    "BL-009": "07_implementation/implementation_notes/observability/build_bl009_observability_log.py",
}

BL003_SCRIPT = "07_implementation/implementation_notes/alignment/build_bl003_ds001_spotify_seed_table.py"

DEFAULT_STAGE_ORDER = ["BL-004", "BL-005", "BL-006", "BL-007", "BL-008", "BL-009"]

# Hash these deterministic files to support repeatability checks for BL-013 runs.
STABLE_ARTIFACTS = {
    "bl004_seed_trace": "07_implementation/implementation_notes/profile/outputs/bl004_seed_trace.csv",
    "bl005_filtered_candidates": "07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv",
    "bl005_candidate_decisions": "07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_decisions.csv",
    "bl006_scored_candidates": "07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv",
    "bl007_assembly_trace": "07_implementation/implementation_notes/playlist/outputs/bl007_assembly_trace.csv",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "BL-013 lightweight orchestrator for bootstrap pipeline stages BL-004 to BL-009."
        )
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        default=DEFAULT_STAGE_ORDER,
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
        default="07_implementation/implementation_notes/entrypoint/outputs",
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
        help="Optional path to a canonical run-config JSON file. Passed to stages via BL_RUN_CONFIG_PATH.",
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
        default="07_implementation/implementation_notes/run_config/outputs",
        help=(
            "Directory where canonical run_intent/run_effective_config artifacts "
            "are emitted for this BL-013 run."
        ),
    )
    return parser.parse_args()


def validate_stage_order(stage_ids: list[str]) -> list[str]:
    normalized: list[str] = []
    for stage_id in stage_ids:
        token = stage_id.strip().upper()
        if token not in STAGES:
            valid = ", ".join(DEFAULT_STAGE_ORDER)
            raise ValueError(f"Unsupported stage '{stage_id}'. Valid values: {valid}")
        normalized.append(token)
    return normalized


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def compute_stable_artifact_hashes(root: Path) -> tuple[dict[str, str], list[str]]:
    hashes: dict[str, str] = {}
    missing: list[str] = []

    for alias, relative_path in STABLE_ARTIFACTS.items():
        artifact_path = root / relative_path
        if not artifact_path.exists():
            missing.append(relative_path)
            continue
        hashes[alias] = sha256_of_file(artifact_path)

    return hashes, missing


def load_run_config_utils_module(root: Path):
    module_path = (
        root
        / "07_implementation"
        / "implementation_notes"
        / "run_config"
        / "run_config_utils.py"
    )
    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def emit_run_config_artifact_pair(
    root: Path,
    run_id: str,
    run_config_path: Path | None,
    artifact_dir: Path,
    generated_at_utc: str,
) -> dict[str, object]:
    run_config_utils = load_run_config_utils_module(root)
    return run_config_utils.write_run_config_artifact_pair(
        run_id=run_id,
        output_dir=artifact_dir,
        run_config_path=run_config_path,
        generated_at_utc=generated_at_utc,
    )


def run_stage(
    python_executable: str,
    stage_id: str,
    script_path: Path,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path | None,
    run_effective_config_path: Path | None,
) -> dict[str, object]:
    command = [python_executable, str(script_path)]
    stage_env = os.environ.copy()
    if run_config_path is not None:
        stage_env["BL_RUN_CONFIG_PATH"] = str(run_config_path)
    if run_intent_path is not None:
        stage_env["BL_RUN_INTENT_PATH"] = str(run_intent_path)
    if run_effective_config_path is not None:
        stage_env["BL_RUN_EFFECTIVE_CONFIG_PATH"] = str(run_effective_config_path)
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

    return {
        "stage_id": stage_id,
        "script_path": script_path.relative_to(root).as_posix(),
        "command": command,
        "run_config_path": str(run_config_path) if run_config_path else None,
        "run_intent_path": str(run_intent_path) if run_intent_path else None,
        "run_effective_config_path": str(run_effective_config_path) if run_effective_config_path else None,
        "return_code": process.returncode,
        "status": "pass" if process.returncode == 0 else "fail",
        "elapsed_seconds": elapsed,
        "stdout": process.stdout.strip(),
        "stderr": process.stderr.strip(),
    }


def run_bl003_seed_refresh(
    python_executable: str,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path | None,
    run_effective_config_path: Path | None,
) -> dict[str, object]:
    script_path = root / BL003_SCRIPT
    if not script_path.exists():
        return {
            "stage_id": "BL-003",
            "script_path": BL003_SCRIPT,
            "command": [python_executable, BL003_SCRIPT],
            "run_config_path": str(run_config_path) if run_config_path else None,
            "run_intent_path": str(run_intent_path) if run_intent_path else None,
            "run_effective_config_path": str(run_effective_config_path) if run_effective_config_path else None,
            "return_code": 127,
            "status": "fail",
            "elapsed_seconds": 0.0,
            "stdout": "",
            "stderr": f"Missing stage script: {BL003_SCRIPT}",
        }

    return run_stage(
        python_executable=python_executable,
        stage_id="BL-003",
        script_path=script_path,
        root=root,
        run_config_path=run_config_path,
        run_intent_path=run_intent_path,
        run_effective_config_path=run_effective_config_path,
    )


def main() -> None:
    args = parse_args()
    root = repo_root()

    stage_order = validate_stage_order(args.stages)
    output_dir = root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    run_config_path = (root / args.run_config).resolve() if args.run_config else None
    if run_config_path is not None and not run_config_path.exists():
        raise FileNotFoundError(f"Run config file not found: {run_config_path}")

    run_id = f"BL013-ENTRYPOINT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    generated_at_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_config_artifact_dir = (root / args.run_config_artifact_dir).resolve()
    run_config_artifacts = emit_run_config_artifact_pair(
        root=root,
        run_id=run_id,
        run_config_path=run_config_path,
        artifact_dir=run_config_artifact_dir,
        generated_at_utc=generated_at_utc,
    )
    run_intent_path = Path(run_config_artifacts["run_intent"]["path"])
    run_effective_config_path = Path(run_config_artifacts["run_effective_config"]["path"])

    stage_results: list[dict[str, object]] = []
    pipeline_started = time.time()

    if args.refresh_seed:
        seed_result = run_bl003_seed_refresh(
            args.python,
            root,
            run_config_path,
            run_intent_path,
            run_effective_config_path,
        )
        stage_results.append(seed_result)
        if seed_result["status"] == "fail" and not args.continue_on_error:
            elapsed_pipeline = round(time.time() - pipeline_started, 3)
            stable_hashes, missing_stable = compute_stable_artifact_hashes(root)
            summary = {
                "run_id": run_id,
                "task": "BL-013",
                "generated_at_utc": generated_at_utc,
                "overall_status": "fail",
                "continue_on_error": bool(args.continue_on_error),
                "python_executable": args.python,
                "run_config_path": str(run_config_path) if run_config_path else None,
                "canonical_run_config_artifacts": run_config_artifacts,
                "refresh_seed": bool(args.refresh_seed),
                "requested_stage_order": stage_order,
                "executed_stage_count": len(stage_results),
                "failed_stage_count": 1,
                "elapsed_seconds": elapsed_pipeline,
                "stage_results": stage_results,
                "stable_artifact_hashes": stable_hashes,
                "missing_stable_artifacts": missing_stable,
                "notes": {
                    "purpose": "Lightweight wrapper to run existing BL-004..BL-009 scripts in one command.",
                    "repeatability_check_guidance": "Compare stable_artifact_hashes between repeated runs under unchanged inputs/config.",
                },
            }
            summary_path = output_dir / f"{args.summary_prefix}_{run_id}.json"
            summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
            latest_path = output_dir / f"{args.summary_prefix}_latest.json"
            latest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
            print("BL-013 orchestration complete: status=fail")
            print(f"run_id={run_id}")
            print(f"summary={summary_path}")
            print(f"latest={latest_path}")
            print(f"failed_stage={seed_result['stage_id']} return_code={seed_result['return_code']}")
            raise SystemExit(1)

    for stage_id in stage_order:
        script_relpath = STAGES[stage_id]
        script_path = root / script_relpath
        if not script_path.exists():
            stage_results.append(
                {
                    "stage_id": stage_id,
                    "script_path": script_relpath,
                    "command": [args.python, script_relpath],
                    "return_code": 127,
                    "status": "fail",
                    "elapsed_seconds": 0.0,
                    "stdout": "",
                    "stderr": f"Missing stage script: {script_relpath}",
                }
            )
            if not args.continue_on_error:
                break
            continue

        result = run_stage(
            args.python,
            stage_id,
            script_path,
            root,
            run_config_path,
            run_intent_path,
            run_effective_config_path,
        )
        stage_results.append(result)

        if result["status"] == "fail" and not args.continue_on_error:
            break

    elapsed_pipeline = round(time.time() - pipeline_started, 3)
    failed = [item for item in stage_results if item["status"] == "fail"]
    expected_stage_count = len(stage_order) + (1 if args.refresh_seed else 0)
    overall_status = "pass" if not failed and len(stage_results) == expected_stage_count else "fail"

    stable_hashes, missing_stable = compute_stable_artifact_hashes(root)

    summary = {
        "run_id": run_id,
        "task": "BL-013",
        "generated_at_utc": generated_at_utc,
        "overall_status": overall_status,
        "continue_on_error": bool(args.continue_on_error),
        "python_executable": args.python,
        "run_config_path": str(run_config_path) if run_config_path else None,
        "canonical_run_config_artifacts": run_config_artifacts,
        "refresh_seed": bool(args.refresh_seed),
        "requested_stage_order": stage_order,
        "executed_stage_count": len(stage_results),
        "failed_stage_count": len(failed),
        "elapsed_seconds": elapsed_pipeline,
        "stage_results": stage_results,
        "stable_artifact_hashes": stable_hashes,
        "missing_stable_artifacts": missing_stable,
        "notes": {
            "purpose": "Lightweight wrapper to run existing BL-004..BL-009 scripts in one command.",
            "repeatability_check_guidance": "Compare stable_artifact_hashes between repeated runs under unchanged inputs/config.",
        },
    }

    summary_path = output_dir / f"{args.summary_prefix}_{run_id}.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")

    latest_path = output_dir / f"{args.summary_prefix}_latest.json"
    latest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")

    print(f"BL-013 orchestration complete: status={overall_status}")
    print(f"run_id={run_id}")
    print(f"summary={summary_path}")
    print(f"latest={latest_path}")

    if failed:
        for item in failed:
            print(f"failed_stage={item['stage_id']} return_code={item['return_code']}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
