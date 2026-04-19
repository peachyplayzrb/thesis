"""Tests for controllability.scenarios."""

from pathlib import Path

import pytest

from controllability.scenarios import build_paths, build_scenarios, ensure_required_inputs


class TestBuildPaths:
    def test_build_paths_contains_expected_keys(self, tmp_path: Path):
        paths = build_paths(tmp_path)
        assert set(paths.keys()) == {
            "legacy_manifest",
            "legacy_coverage",
            "bl003_summary",
            "active_seed_trace",
            "active_candidates",
            "baseline_snapshot",
            "output_dir",
        }


class TestEnsureRequiredInputs:
    def test_raises_when_required_missing(self, tmp_path: Path):
        paths = build_paths(tmp_path)
        with pytest.raises(FileNotFoundError):
            ensure_required_inputs(paths, tmp_path)

    def test_passes_when_required_present(self, tmp_path: Path):
        paths = build_paths(tmp_path)
        for key in ["baseline_snapshot", "bl003_summary", "active_seed_trace", "active_candidates"]:
            paths[key].parent.mkdir(parents=True, exist_ok=True)
            paths[key].write_text("{}", encoding="utf-8")
        ensure_required_inputs(paths, tmp_path)


def _baseline_snapshot(component_weights: dict[str, float]) -> dict:
    return {
        "stage_configs": {
            "profile": {
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                "threshold_scale": 1.0,
                "numeric_thresholds": {"tempo": 20.0},
            },
            "scoring": {
                "component_weights": component_weights,
                "numeric_thresholds": {"tempo": 20.0},
            },
            "assembly": {"target_size": 10},
        }
    }


def _runtime_controls() -> dict[str, object]:
    return {
        "weight_override_value_if_component_present": 0.2,
        "weight_override_increment_fallback": 0.08,
        "weight_override_cap_fallback": 0.35,
        "stricter_threshold_scale": 0.75,
        "looser_threshold_scale": 1.25,
    }


class TestBuildScenarios:
    def test_builds_expected_scenarios(self):
        snapshot = _baseline_snapshot({"valence": 0.5, "tempo": 0.5})
        scenarios = build_scenarios(snapshot, _runtime_controls())
        ids = [s["scenario_id"] for s in scenarios]
        assert ids == [
            "baseline",
            "no_influence_tracks",
            "valence_weight_up",
            "stricter_thresholds",
            "looser_thresholds",
            "fuzzy_enabled_strict",
            "no_influence_plus_stricter_thresholds",
            "valence_up_plus_stricter_thresholds",
        ]

    def test_fuzzy_enabled_strict_scenario_declares_alignment_controls(self):
        snapshot = _baseline_snapshot({"valence": 0.5, "tempo": 0.5})
        scenarios = build_scenarios(snapshot, _runtime_controls())
        scenario = next(s for s in scenarios if s["scenario_id"] == "fuzzy_enabled_strict")
        fuzzy = scenario["alignment_seed_controls"]["fuzzy_matching"]
        assert fuzzy["enabled"] is True
        assert fuzzy["combined_threshold"] == 0.90

    def test_valence_override_uses_valence_component_when_present(self):
        snapshot = _baseline_snapshot({"valence": 0.4, "tempo": 0.6})
        scenarios = build_scenarios(snapshot, _runtime_controls())
        scenario = next(s for s in scenarios if s["scenario_id"] == "valence_weight_up")
        assert scenario["scoring"]["weight_override_component"] == "valence"

    def test_fallback_override_component_when_valence_absent(self):
        snapshot = _baseline_snapshot({"danceability": 0.7, "tempo": 0.3})
        scenarios = build_scenarios(snapshot, _runtime_controls())
        scenario = next(s for s in scenarios if s["scenario_id"] == "valence_weight_up")
        assert scenario["scoring"]["weight_override_component"] in {"danceability", "tempo"}

    def test_raises_when_no_scoring_weights_available(self):
        snapshot = _baseline_snapshot({})
        with pytest.raises(RuntimeError):
            build_scenarios(snapshot, _runtime_controls())

    def test_interaction_scenarios_include_axes_and_acceptance_bounds(self):
        snapshot = _baseline_snapshot({"valence": 0.5, "tempo": 0.5})
        scenarios = build_scenarios(snapshot, _runtime_controls())
        interaction = next(
            s for s in scenarios if s["scenario_id"] == "no_influence_plus_stricter_thresholds"
        )
        assert interaction["variation_mode"] == "interaction"
        assert interaction["interaction_axes"] == ["influence_tracks", "candidate_threshold"]
        bounds = interaction["acceptance_bounds"]
        assert isinstance(bounds, list)
        assert any(bound["metric"] == "observable_shift" for bound in bounds)
