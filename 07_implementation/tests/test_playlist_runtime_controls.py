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
