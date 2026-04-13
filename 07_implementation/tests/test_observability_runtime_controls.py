"""Tests for observability.main resolve_bl009_runtime_controls."""

import json

from observability.runtime_controls import resolve_bl009_runtime_controls
from shared_utils.constants import DEFAULT_INPUT_SCOPE


def test_runtime_controls_environment_defaults(monkeypatch) -> None:
    monkeypatch.delenv("BL009_DIAGNOSTIC_SAMPLE_LIMIT", raising=False)
    monkeypatch.delenv("BL009_BOOTSTRAP_MODE", raising=False)
    monkeypatch.delenv("BL009_BL008_HANDSHAKE_VALIDATION_POLICY", raising=False)
    monkeypatch.delenv("BL_RUN_INTENT_PATH", raising=False)
    monkeypatch.delenv("BL_RUN_EFFECTIVE_CONFIG_PATH", raising=False)

    controls = resolve_bl009_runtime_controls()

    assert controls["config_source"] == "environment"
    assert controls["diagnostic_sample_limit"] == 5
    assert controls["bootstrap_mode"] is True
    assert controls["bl008_bl009_handshake_validation_policy"] == "warn"
    assert controls["run_intent_path"] is None
    assert controls["run_effective_config_path"] is None


def test_runtime_controls_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("BL009_DIAGNOSTIC_SAMPLE_LIMIT", "12")
    monkeypatch.setenv("BL009_BOOTSTRAP_MODE", "false")
    monkeypatch.setenv("BL009_BL008_HANDSHAKE_VALIDATION_POLICY", "strict")
    monkeypatch.delenv("BL_RUN_INTENT_PATH", raising=False)
    monkeypatch.delenv("BL_RUN_EFFECTIVE_CONFIG_PATH", raising=False)

    controls = resolve_bl009_runtime_controls()

    assert controls["config_source"] == "environment"
    assert controls["diagnostic_sample_limit"] == 12
    assert controls["bootstrap_mode"] is False
    assert controls["bl008_bl009_handshake_validation_policy"] == "strict"


def test_runtime_controls_payload_defaults_input_scope_when_missing(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "diagnostic_sample_limit": 7,
                    "bootstrap_mode": False,
                }
            }
        ),
    )

    controls = resolve_bl009_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["run_config_path"] is None
    assert controls["run_config_schema_version"] is None
    assert controls["diagnostic_sample_limit"] == 7
    assert controls["bootstrap_mode"] is False
    assert controls["bl008_bl009_handshake_validation_policy"] == "warn"
    assert controls["input_scope"] == dict(DEFAULT_INPUT_SCOPE)


def test_runtime_controls_payload_does_not_inherit_env_for_missing_keys(monkeypatch) -> None:
    monkeypatch.setenv("BL009_DIAGNOSTIC_SAMPLE_LIMIT", "99")
    monkeypatch.setenv("BL009_BL008_HANDSHAKE_VALIDATION_POLICY", "strict")
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "bootstrap_mode": False,
                }
            }
        ),
    )

    controls = resolve_bl009_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["diagnostic_sample_limit"] == 5
    assert controls["bootstrap_mode"] is False
    assert controls["bl008_bl009_handshake_validation_policy"] == "warn"
