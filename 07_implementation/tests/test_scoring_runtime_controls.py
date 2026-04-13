"""Tests for scoring.runtime_controls."""

import json

import pytest

from scoring.runtime_controls import (
    build_active_component_weights,
    resolve_bl006_runtime_controls,
)


def test_build_active_component_weights_drops_inactive_numeric_and_rebalances() -> None:
    component_weights = {
        "tempo_score": 0.2,
        "energy_score": 0.3,
        "tag_overlap_score": 0.5,
    }
    normalized, diagnostics = build_active_component_weights(
        active_numeric_components={"tempo"},
        component_weights=component_weights,
        numeric_components={"tempo", "energy"},
    )

    assert set(normalized.keys()) == {"tempo_score", "tag_overlap_score"}
    assert round(sum(normalized.values()), 6) == 1.0
    assert diagnostics["rebalanced"] is True
    assert diagnostics["inactive_components"] == ["energy_score"]


def test_resolve_bl006_runtime_controls_requires_component_weights(monkeypatch) -> None:
    monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)
    monkeypatch.delenv("BL006_COMPONENT_WEIGHTS_JSON", raising=False)

    with pytest.raises(RuntimeError, match="component_weights"):
        resolve_bl006_runtime_controls()


def test_resolve_bl006_runtime_controls_prefers_payload_over_env(monkeypatch) -> None:
    payload = {
        "controls": {
            "signal_mode": {"enable_label_boost": True},
            "component_weights": {"tag_overlap_score": 0.6, "genre_overlap_score": 0.4},
            "numeric_thresholds": {"tempo": 30.0},
            "lead_genre_strategy": "single_anchor",
            "semantic_overlap_strategy": "overlap_only",
            "semantic_precision_alpha_mode": "fixed",
            "semantic_precision_alpha_fixed": 0.8,
            "enable_numeric_confidence_scaling": False,
            "numeric_confidence_floor": 0.2,
            "profile_numeric_confidence_mode": "blended",
            "profile_numeric_confidence_blend_weight": 0.4,
            "emit_confidence_impact_diagnostics": False,
            "emit_semantic_precision_diagnostics": True,
            "apply_bl003_influence_tracks": True,
            "influence_track_bonus_scale": 0.15,
        }
    }
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", json.dumps(payload))
    monkeypatch.setenv("BL006_COMPONENT_WEIGHTS_JSON", '{"tag_overlap_score": 1.0}')

    resolved = resolve_bl006_runtime_controls()

    assert resolved["component_weights"] == {
        "tag_overlap_score": 0.6,
        "genre_overlap_score": 0.4,
    }
    assert resolved["lead_genre_strategy"] == "single_anchor"
    assert resolved["semantic_overlap_strategy"] == "overlap_only"
    assert resolved["semantic_precision_alpha_mode"] == "fixed"
    assert resolved["semantic_precision_alpha_fixed"] == 0.8
    assert resolved["numeric_confidence_floor"] == 0.2


def test_resolve_bl006_runtime_controls_sanitizes_invalid_values(monkeypatch) -> None:
    payload = {
        "controls": {
            "signal_mode": {},
            "component_weights": {"tag_overlap_score": 1.0},
            "lead_genre_strategy": "invalid_value",
            "semantic_overlap_strategy": "invalid_value",
            "semantic_precision_alpha_mode": "invalid_value",
            "semantic_precision_alpha_fixed": 9.0,
            "numeric_confidence_floor": -2.0,
            "profile_numeric_confidence_mode": "invalid_value",
            "profile_numeric_confidence_blend_weight": 3.0,
            "influence_track_bonus_scale": -1.0,
            "bl005_bl006_handshake_validation_policy": "invalid_value",
        }
    }
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", json.dumps(payload))

    resolved = resolve_bl006_runtime_controls()

    assert resolved["lead_genre_strategy"] == "weighted_top_lead_genres"
    assert resolved["semantic_overlap_strategy"] == "precision_aware"
    assert resolved["semantic_precision_alpha_mode"] == "profile_adaptive"
    assert resolved["semantic_precision_alpha_fixed"] == 1.0
    assert resolved["numeric_confidence_floor"] == 0.0
    assert resolved["profile_numeric_confidence_mode"] == "direct"
    assert resolved["profile_numeric_confidence_blend_weight"] == 1.0
    assert resolved["influence_track_bonus_scale"] == 0.0
    assert resolved["bl005_bl006_handshake_validation_policy"] == "warn"


def test_resolve_bl006_runtime_controls_parse_failure_emits_warning(monkeypatch) -> None:
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", "{not-json")
    monkeypatch.setenv("BL006_COMPONENT_WEIGHTS_JSON", '{"tag_overlap_score": 1.0}')

    resolved = resolve_bl006_runtime_controls()

    assert resolved["runtime_control_resolution_diagnostics"]["payload_json_parse_error"] is True
    assert resolved["runtime_control_resolution_diagnostics"]["resolution_path"] == "environment"
    assert resolved["runtime_control_validation_warnings"]
    assert "parse failed" in resolved["runtime_control_validation_warnings"][0].lower()


def test_resolve_bl006_runtime_controls_payload_missing_keys_use_defaults_not_env(monkeypatch) -> None:
    monkeypatch.setenv("BL006_NUMERIC_CONFIDENCE_FLOOR", "0.9")
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "component_weights": {
                        "tag_overlap_score": 1.0,
                    }
                }
            }
        ),
    )

    resolved = resolve_bl006_runtime_controls()

    assert resolved["config_source"] == "defaults"
    assert resolved["numeric_confidence_floor"] == 0.0
