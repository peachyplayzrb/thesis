"""Stage subprocess execution helpers for BL-013."""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from orchestration.stage_registry import BL003_SCRIPT


def run_stage(
    python_executable: str,
    stage_id: str,
    script_path: Path,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path | None,
    run_effective_config_path: Path | None,
    stage_config_payload: dict[str, object] | None = None,
    extra_args: list[str] | None = None,
) -> dict[str, object]:
    command = [python_executable, str(script_path)]
    if extra_args:
        command.extend(extra_args)
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
    if stage_config_payload is None:
        raise RuntimeError(f"Missing stage config payload for {stage_id}")
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


def build_missing_script_result(
    *,
    stage_id: str,
    script_relpath: str,
    python_executable: str,
    run_config_path: Path | None,
    run_intent_path: Path | None,
    run_effective_config_path: Path | None,
) -> dict[str, object]:
    return {
        "stage_id": stage_id,
        "script_path": script_relpath,
        "command": [python_executable, script_relpath],
        "run_config_path": str(run_config_path) if run_config_path else None,
        "run_intent_path": str(run_intent_path) if run_intent_path else None,
        "run_effective_config_path": str(run_effective_config_path) if run_effective_config_path else None,
        "return_code": 127,
        "status": "fail",
        "elapsed_seconds": 0.0,
        "stdout": "",
        "stderr": f"Missing stage script: {script_relpath}",
    }


def run_bl003_seed_refresh(
    python_executable: str,
    root: Path,
    run_config_path: Path | None,
    run_intent_path: Path | None,
    run_effective_config_path: Path | None,
    stage_config_payload: dict[str, object] | None = None,
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
        stage_config_payload=stage_config_payload,
    )
