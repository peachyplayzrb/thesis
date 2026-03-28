"""Tests for observability.main resolve_bl009_runtime_controls."""

from unittest.mock import patch

from observability import main as observability_main


def test_runtime_controls_environment_defaults(monkeypatch) -> None:
    monkeypatch.delenv("BL009_DIAGNOSTIC_SAMPLE_LIMIT", raising=False)
    monkeypatch.delenv("BL009_BOOTSTRAP_MODE", raising=False)
    monkeypatch.delenv("BL_RUN_INTENT_PATH", raising=False)
    monkeypatch.delenv("BL_RUN_EFFECTIVE_CONFIG_PATH", raising=False)

    with patch("shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value=None):
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

    with patch("shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value=None):
        controls = observability_main.resolve_bl009_runtime_controls()

    assert controls["config_source"] == "environment"
    assert controls["diagnostic_sample_limit"] == 12
    assert controls["bootstrap_mode"] is False


def test_runtime_controls_run_config_precedence(monkeypatch) -> None:
    monkeypatch.setenv("BL009_DIAGNOSTIC_SAMPLE_LIMIT", "99")
    monkeypatch.setenv("BL_RUN_INTENT_PATH", "intent.json")
    monkeypatch.setenv("BL_RUN_EFFECTIVE_CONFIG_PATH", "effective.json")

    class StubRunConfigUtils:
        def resolve_bl009_controls(self, run_config_path: str) -> dict:
            assert run_config_path == "fake_config"
            return {
                "config_path": "fake_config",
                "schema_version": "run-config-v1",
                "control_mode": {},
                "diagnostic_sample_limit": 8,
                "bootstrap_mode": False,
            }

        def resolve_input_scope_controls(self, run_config_path: str) -> dict:
            return {"input_scope": {"include_top_tracks": True}}

    def fake_resolve_run_config_path(env_var: str = "BL_RUN_CONFIG_PATH") -> str | None:
        if env_var == "BL_RUN_CONFIG_PATH":
            return "fake_config"
        return monkeypatch._env.get(env_var, None) or None

    with patch("shared_utils.stage_runtime_resolver.resolve_run_config_path", side_effect=fake_resolve_run_config_path):
        with patch("shared_utils.config_loader.load_run_config_utils_module", return_value=StubRunConfigUtils()):
            controls = observability_main.resolve_bl009_runtime_controls()

    assert controls["config_source"] == "run_config"
    assert controls["diagnostic_sample_limit"] == 8
    assert controls["bootstrap_mode"] is False
    assert controls["run_config_path"] == "fake_config"
    assert controls["run_intent_path"] == "intent.json"
    assert controls["run_effective_config_path"] == "effective.json"
