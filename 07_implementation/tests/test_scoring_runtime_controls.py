"""Tests for scoring.runtime_controls."""

from scoring.runtime_controls import (
    build_active_component_weights,
    load_component_weight_overrides,
)


def test_load_component_weight_overrides_ignores_invalid_values(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL006_COMPONENT_WEIGHTS_JSON",
        '{"tempo_score": 0.5, "unknown": 0.8, "energy_score": -1}',
    )
    defaults = {
        "tempo_score": 0.2,
        "energy_score": 0.3,
        "tag_overlap_score": 0.5,
    }

    merged = load_component_weight_overrides(defaults)

    assert merged["tempo_score"] == 0.5
    assert merged["energy_score"] == 0.3
    assert merged["tag_overlap_score"] == 0.5
    assert "unknown" not in merged


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
