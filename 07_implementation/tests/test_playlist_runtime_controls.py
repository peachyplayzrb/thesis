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
    assert controls["novelty_allowance"] == 0
    assert controls["utility_decay_factor"] == 0.0
    assert controls["opportunity_cost_top_k_examples"] == 10


def test_runtime_controls_environment_sanitizes_bounds(monkeypatch) -> None:
    monkeypatch.setenv("BL007_TARGET_SIZE", "0")
    monkeypatch.setenv("BL007_MIN_SCORE_THRESHOLD", "9")
    monkeypatch.setenv("BL007_MAX_PER_GENRE", "-2")
    monkeypatch.setenv("BL007_MAX_CONSECUTIVE", "-4")
    monkeypatch.setenv("BL007_NOVELTY_ALLOWANCE", "-3")
    monkeypatch.setenv("BL007_UTILITY_DECAY_FACTOR", "4.7")
    monkeypatch.setenv("BL007_OPPORTUNITY_COST_TOP_K_EXAMPLES", "-9")

    with patch("shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value=None):
        controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["target_size"] == 1
    assert controls["min_score_threshold"] == 1.0
    assert controls["max_per_genre"] == 1
    assert controls["max_consecutive"] == 1
    assert controls["novelty_allowance"] == 0
    assert controls["utility_decay_factor"] == 1.0
    assert controls["opportunity_cost_top_k_examples"] == 1


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


def test_runtime_controls_sanitizes_influence_policy_bounds(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "target_size": 5,
                    "influence_enabled": True,
                    "influence_track_ids": ["a", "", "a", "b"],
                    "influence_policy_mode": "invalid_mode",
                    "influence_reserved_slots": 99,
                    "influence_allow_genre_cap_override": True,
                    "influence_allow_consecutive_override": True,
                    "influence_allow_score_threshold_override": True,
                }
            }
        ),
    )

    controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["influence_enabled"] is True
    assert controls["influence_track_ids"] == ["a", "a", "b"]
    assert controls["influence_policy_mode"] == "competitive"
    assert controls["influence_reserved_slots"] == 5
    assert controls["influence_allow_genre_cap_override"] is True
    assert controls["influence_allow_consecutive_override"] is True
    assert controls["influence_allow_score_threshold_override"] is True


def test_runtime_controls_environment_includes_bl006_bl007_handshake_policy_default(
    monkeypatch,
) -> None:
    monkeypatch.delenv("BL007_BL006_HANDSHAKE_VALIDATION_POLICY", raising=False)

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value=None
    ):
        controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["bl006_bl007_handshake_validation_policy"] == "warn"


def test_runtime_controls_env_bl006_bl007_handshake_policy_is_picked_up(
    monkeypatch,
) -> None:
    monkeypatch.setenv("BL007_BL006_HANDSHAKE_VALIDATION_POLICY", "allow")

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value=None
    ):
        controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["bl006_bl007_handshake_validation_policy"] == "allow"


def test_runtime_controls_sanitizes_invalid_bl006_bl007_handshake_policy(
    monkeypatch,
) -> None:
    monkeypatch.setenv("BL007_BL006_HANDSHAKE_VALIDATION_POLICY", "invalid_value")

    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "shared_utils.stage_runtime_resolver.resolve_run_config_path", return_value=None
    ):
        controls = runtime_controls.resolve_bl007_runtime_controls()

    assert controls["bl006_bl007_handshake_validation_policy"] == "warn"
