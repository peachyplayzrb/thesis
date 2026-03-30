"""Tests for observability.main resolve_bl009_runtime_controls."""

from unittest.mock import patch

from observability import main as observability_main


def test_runtime_controls_environment_defaults(monkeypatch) -> None:
    monkeypatch.delenv("BL009_DIAGNOSTIC_SAMPLE_LIMIT", raising=False)
    monkeypatch.delenv("BL009_BOOTSTRAP_MODE", raising=False)
    monkeypatch.delenv("BL_RUN_INTENT_PATH", raising=False)
    monkeypatch.delenv("BL_RUN_EFFECTIVE_CONFIG_PATH", raising=False)

    controls = observability_main.resolve_bl009_runtime_controls()

    assert controls["config_source"] == "environment"
    assert controls["diagnostic_sample_limit"] == 5
    assert controls["bootstrap_mode"] is True
    assert controls["run_intent_path"] is None
    assert controls["run_effective_config_path"] is None


def test_runtime_controls_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("BL009_DIAGNOSTIC_SAMPLE_LIMIT", "12")
    monkeypatch.setenv("BL009_BOOTSTRAP_MODE", "false")
    monkeypatch.delenv("BL_RUN_INTENT_PATH", raising=False)
    monkeypatch.delenv("BL_RUN_EFFECTIVE_CONFIG_PATH", raising=False)

    controls = observability_main.resolve_bl009_runtime_controls()

    assert controls["config_source"] == "environment"
    assert controls["diagnostic_sample_limit"] == 12
    assert controls["bootstrap_mode"] is False
