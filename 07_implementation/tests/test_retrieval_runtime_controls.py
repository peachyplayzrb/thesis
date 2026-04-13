"""Tests for retrieval.runtime_controls."""

import json
from typing import cast

from retrieval.runtime_controls import resolve_bl005_runtime_controls


def test_runtime_controls_environment_defaults(monkeypatch) -> None:
    monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)

    controls = resolve_bl005_runtime_controls()

    assert controls["config_source"] == "environment"
    assert controls["signal_mode"] == {}
    assert controls["language_filter_enabled"] is False
    assert controls["bl004_bl005_handshake_validation_policy"] == "warn"


def test_runtime_controls_payload_defaults_missing_sections(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "profile_top_tag_limit": 8,
                    "profile_top_genre_limit": 7,
                }
            }
        ),
    )

    controls = resolve_bl005_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["signal_mode"] == {}
    assert controls["language_filter_enabled"] is False
    numeric_thresholds = cast(dict[str, float], controls["numeric_thresholds"])
    assert numeric_thresholds["danceability"] == 0.2
    assert controls["profile_top_tag_limit"] == 8
    assert controls["profile_top_genre_limit"] == 7


def test_runtime_controls_payload_does_not_inherit_env_for_missing_keys(monkeypatch) -> None:
    monkeypatch.setenv("BL005_NUMERIC_SUPPORT_MIN_SCORE", "9")
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "profile_top_tag_limit": 8,
                }
            }
        ),
    )

    controls = resolve_bl005_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["numeric_support_min_score"] == 1.0


def test_runtime_controls_handshake_policy_normalized(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "bl004_bl005_handshake_validation_policy": "STRICT",
                }
            }
        ),
    )

    controls = resolve_bl005_runtime_controls()

    assert controls["bl004_bl005_handshake_validation_policy"] == "strict"
