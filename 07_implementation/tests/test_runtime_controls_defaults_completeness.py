"""Cross-stage defaults completeness tests for payload-based runtime control resolution."""

from __future__ import annotations

import importlib
import json

import pytest


def _resolver(module_name: str, function_name: str):
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


@pytest.mark.parametrize(
    (
        "module_name",
        "function_name",
        "env_key",
        "env_value",
        "expected_key",
        "expected_value",
    ),
    [
        ("profile.runtime_controls", "resolve_bl004_runtime_controls", "BL004_TOP_TAG_LIMIT", "99", "top_tag_limit", 10),
        ("retrieval.runtime_controls", "resolve_bl005_runtime_controls", "BL005_NUMERIC_SUPPORT_MIN_SCORE", "9", "numeric_support_min_score", 1.0),
        ("scoring.runtime_controls", "resolve_bl006_runtime_controls", "BL006_NUMERIC_CONFIDENCE_FLOOR", "0.9", "numeric_confidence_floor", 0.0),
        ("playlist.runtime_controls", "resolve_bl007_runtime_controls", "BL007_MIN_SCORE_THRESHOLD", "0.9", "min_score_threshold", 0.35),
        ("transparency.runtime_controls", "resolve_bl008_runtime_controls", "BL008_PRIMARY_CONTRIBUTOR_TIE_DELTA", "0.9", "primary_contributor_tie_delta", 0.02),
        ("observability.runtime_controls", "resolve_bl009_runtime_controls", "BL009_DIAGNOSTIC_SAMPLE_LIMIT", "99", "diagnostic_sample_limit", 5),
    ],
)
def test_payload_empty_controls_use_canonical_defaults_not_env(
    monkeypatch,
    module_name: str,
    function_name: str,
    env_key: str,
    env_value: str,
    expected_key: str,
    expected_value,
) -> None:
    monkeypatch.setenv(env_key, env_value)
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", json.dumps({"controls": {}}))

    controls = _resolver(module_name, function_name)()

    assert controls["config_source"] == "defaults"
    assert controls[expected_key] == expected_value


@pytest.mark.parametrize(
    ("module_name", "function_name", "stage_label"),
    [
        ("profile.runtime_controls", "resolve_bl004_runtime_controls", "BL-004"),
        ("retrieval.runtime_controls", "resolve_bl005_runtime_controls", "BL-005"),
        ("playlist.runtime_controls", "resolve_bl007_runtime_controls", "BL-007"),
        ("transparency.runtime_controls", "resolve_bl008_runtime_controls", "BL-008"),
        ("observability.runtime_controls", "resolve_bl009_runtime_controls", "BL-009"),
        ("reproducibility.runtime_controls", "resolve_bl010_runtime_controls", "BL-010"),
    ],
)
def test_malformed_stage_payload_fallback_is_reported(
    monkeypatch,
    module_name: str,
    function_name: str,
    stage_label: str,
) -> None:
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", "{not-json")

    controls = _resolver(module_name, function_name)()

    diagnostics = controls["runtime_control_resolution_diagnostics"]
    warnings = controls["runtime_control_validation_warnings"]
    assert diagnostics["payload_json_present"] is True
    assert diagnostics["payload_json_parse_error"] is True
    assert diagnostics["resolution_path"] == "environment"
    assert any(stage_label in str(item) for item in warnings)
