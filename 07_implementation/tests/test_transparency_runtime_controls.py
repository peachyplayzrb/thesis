"""Tests for transparency.runtime_controls."""

import json
from unittest.mock import patch

from transparency import runtime_controls


def test_runtime_controls_environment_defaults(monkeypatch) -> None:
    monkeypatch.delenv("BL008_TOP_CONTRIBUTOR_LIMIT", raising=False)
    monkeypatch.delenv("BL008_BLEND_PRIMARY_CONTRIBUTOR_ON_NEAR_TIE", raising=False)
    monkeypatch.delenv("BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA", raising=False)

    controls = runtime_controls.resolve_bl008_runtime_controls()

    assert controls["config_source"] == "environment"
    assert controls["top_contributor_limit"] == 3
    assert controls["blend_primary_contributor_on_near_tie"] is False
    assert controls["primary_contributor_tie_delta"] == 0.02


def test_runtime_controls_environment_sanitizes_bounds(monkeypatch) -> None:
    monkeypatch.setenv("BL008_TOP_CONTRIBUTOR_LIMIT", "0")
    monkeypatch.setenv("BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA", "9")

    controls = runtime_controls.resolve_bl008_runtime_controls()

    assert controls["top_contributor_limit"] == 1
    assert controls["primary_contributor_tie_delta"] == 1.0


def test_runtime_controls_payload_defaults_missing_sections(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "top_contributor_limit": 4,
                }
            }
        ),
    )

    controls = runtime_controls.resolve_bl008_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["top_contributor_limit"] == 4
    assert controls["blend_primary_contributor_on_near_tie"] is False
    assert controls["primary_contributor_tie_delta"] == 0.02


def test_runtime_controls_payload_does_not_inherit_env_for_missing_keys(monkeypatch) -> None:
    monkeypatch.setenv("BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA", "0.9")
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "top_contributor_limit": 4,
                }
            }
        ),
    )

    controls = runtime_controls.resolve_bl008_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["primary_contributor_tie_delta"] == 0.02
