"""Tests for playlist.runtime_controls."""

from unittest.mock import patch

from playlist import runtime_controls


def test_runtime_controls_environment_defaults(monkeypatch) -> None:
    monkeypatch.delenv("BL007_TARGET_SIZE", raising=False)
    monkeypatch.delenv("BL007_MIN_SCORE_THRESHOLD", raising=False)
    monkeypatch.delenv("BL007_MAX_PER_GENRE", raising=False)
    monkeypatch.delenv("BL007_MAX_CONSECUTIVE", raising=False)

    with patch("shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value=None):
        controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["config_source"] == "environment"
    assert controls["target_size"] == 10
    assert controls["min_score_threshold"] == 0.35
    assert controls["max_per_genre"] == 4
    assert controls["max_consecutive"] == 2


def test_runtime_controls_environment_sanitizes_bounds(monkeypatch) -> None:
    monkeypatch.setenv("BL007_TARGET_SIZE", "0")
    monkeypatch.setenv("BL007_MIN_SCORE_THRESHOLD", "9")
    monkeypatch.setenv("BL007_MAX_PER_GENRE", "-2")
    monkeypatch.setenv("BL007_MAX_CONSECUTIVE", "-4")

    with patch("shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value=None):
        controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["target_size"] == 1
    assert controls["min_score_threshold"] == 1.0
    assert controls["max_per_genre"] == 1
    assert controls["max_consecutive"] == 1


def test_runtime_controls_run_config_precedence(monkeypatch) -> None:
    class StubRunConfigUtils:
        def resolve_bl007_controls(self, run_config_path: str) -> dict[str, object]:
            assert run_config_path == "fake_config"
            return {
                "config_path": "fake_config",
                "schema_version": "run-config-v1",
                "target_size": 12,
                "min_score_threshold": 0.42,
                "max_per_genre": 5,
                "max_consecutive": 3,
            }

    monkeypatch.setenv("BL007_TARGET_SIZE", "99")

    with patch("shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value="fake_config"):
        with patch("shared_utils.config_loader.load_run_config_utils_module", return_value=StubRunConfigUtils()):
            controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["config_source"] == "run_config"
    assert controls["target_size"] == 12
    assert controls["min_score_threshold"] == 0.42
    assert controls["max_per_genre"] == 5
    assert controls["max_consecutive"] == 3
