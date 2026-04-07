"""Tests for playlist.runtime_controls."""

import json
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


def test_runtime_controls_payload_defaults_missing_sections(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "target_size": 12,
                    "max_per_genre": 5,
                }
            }
        ),
    )

    controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["target_size"] == 12
    assert controls["max_per_genre"] == 5
    assert controls["utility_weights"]["score_weight"] == 1.0
    assert controls["controlled_relaxation"]["enabled"] is False


def test_runtime_controls_payload_does_not_inherit_env_for_missing_keys(monkeypatch) -> None:
    monkeypatch.setenv("BL007_MIN_SCORE_THRESHOLD", "0.91")
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "target_size": 12,
                }
            }
        ),
    )

    controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["min_score_threshold"] == 0.35
