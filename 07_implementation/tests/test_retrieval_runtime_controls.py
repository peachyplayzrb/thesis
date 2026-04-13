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
    diagnostics = cast(dict[str, object], controls["runtime_control_resolution_diagnostics"])
    assert diagnostics["resolution_path"] == "environment"
    assert diagnostics["payload_json_parse_error"] is False


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


def test_runtime_controls_emits_normalization_diagnostics(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "numeric_support_min_pass": "bad",
                    "profile_numeric_confidence_mode": "invalid",
                    "language_filter_codes": ["EN", "en", "", "FR"],
                }
            }
        ),
    )

    controls = resolve_bl005_runtime_controls()

    diagnostics = cast(dict[str, object], controls["runtime_control_resolution_diagnostics"])
    assert diagnostics["resolution_path"] == "orchestration_payload"
    assert diagnostics["normalization_event_count"]
    counts = cast(dict[str, int], diagnostics["normalization_event_counts_by_field"])
    assert counts["numeric_support_min_pass"] >= 1
    assert counts["profile_numeric_confidence_mode"] >= 1
    assert controls["language_filter_codes"] == ["en", "fr"]


def test_runtime_controls_payload_parse_error_warns_and_falls_back(monkeypatch) -> None:
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", "{not-json")

    controls = resolve_bl005_runtime_controls()

    diagnostics = cast(dict[str, object], controls["runtime_control_resolution_diagnostics"])
    warnings = cast(list[str], controls["runtime_control_validation_warnings"])

    assert diagnostics["payload_json_parse_error"] is True
    assert diagnostics["resolution_path"] == "environment"
    assert any("parse failed" in warning for warning in warnings)
