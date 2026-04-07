"""Tests for orchestration.stage_runner BL_STAGE_CONFIG_JSON handoff."""

from __future__ import annotations

import json
from pathlib import Path

from orchestration import stage_runner


class _FakeProcess:
    def __init__(self) -> None:
        self.returncode = 0
        self.stdout = "ok"
        self.stderr = ""


def test_run_stage_injects_stage_config_json(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def _fake_subprocess_run(command, *, cwd, env, capture_output, text, check):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["env"] = env
        captured["capture_output"] = capture_output
        captured["text"] = text
        captured["check"] = check
        return _FakeProcess()

    monkeypatch.setattr(stage_runner.subprocess, "run", _fake_subprocess_run)

    root = tmp_path
    script_path = tmp_path / "dummy_stage.py"
    script_path.write_text("print('ok')\n", encoding="utf-8")

    payload = {
        "schema_version": "stage-config-v1",
        "stage_id": "BL-007",
        "controls": {"target_size": 10},
    }

    result = stage_runner.run_stage(
        python_executable="python",
        stage_id="BL-007",
        script_path=script_path,
        root=root,
        run_config_path=None,
        run_intent_path=None,
        run_effective_config_path=None,
        stage_config_payload=payload,
    )

    assert result["status"] == "pass"
    assert "env" in captured
    env = captured["env"]
    assert isinstance(env, dict)
    assert "BL_STAGE_CONFIG_JSON" in env
    assert "PYTHONPATH" in env
    assert str(root) in str(env["PYTHONPATH"])
    decoded = json.loads(str(env["BL_STAGE_CONFIG_JSON"]))
    assert decoded["stage_id"] == "BL-007"
    assert decoded["controls"]["target_size"] == 10


def test_run_stage_requires_stage_payload(tmp_path: Path) -> None:
    script_path = tmp_path / "dummy_stage.py"
    script_path.write_text("print('ok')\n", encoding="utf-8")

    try:
        stage_runner.run_stage(
            python_executable="python",
            stage_id="BL-007",
            script_path=script_path,
            root=tmp_path,
            run_config_path=None,
            run_intent_path=None,
            run_effective_config_path=None,
            stage_config_payload=None,
        )
        assert False, "Expected RuntimeError when stage payload is missing"
    except RuntimeError as exc:
        assert "Missing stage config payload" in str(exc)


def test_run_stage_prefixes_existing_pythonpath(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def _fake_subprocess_run(command, *, cwd, env, capture_output, text, check):
        captured["env"] = env
        return _FakeProcess()

    monkeypatch.setattr(stage_runner.subprocess, "run", _fake_subprocess_run)
    monkeypatch.setenv("PYTHONPATH", "existing_path")

    script_path = tmp_path / "dummy_stage.py"
    script_path.write_text("print('ok')\n", encoding="utf-8")

    payload = {
        "schema_version": "stage-config-v1",
        "stage_id": "BL-007",
        "controls": {"target_size": 10},
    }

    stage_runner.run_stage(
        python_executable="python",
        stage_id="BL-007",
        script_path=script_path,
        root=tmp_path,
        run_config_path=None,
        run_intent_path=None,
        run_effective_config_path=None,
        stage_config_payload=payload,
    )

    env = captured["env"]
    assert isinstance(env, dict)
    pythonpath = str(env["PYTHONPATH"])
    assert str(tmp_path) in pythonpath
    assert "existing_path" in pythonpath
