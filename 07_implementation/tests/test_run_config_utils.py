"""Tests for strict BL-003 run-config validation and resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from run_config.run_config_utils import (
    RunConfigError,
    resolve_bl003_influence_controls,
    resolve_bl003_seed_controls,
    resolve_bl003_weighting_policy,
    resolve_effective_run_config,
)


def _write_run_config(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "run_config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_bl003_resolvers_return_validated_overrides(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "seed_controls": {
                "match_rate_min_threshold": 0.35,
                "top_range_weights": {"short_term": 0.75},
                "source_base_weights": {"saved_tracks": 0.9},
                "decay_half_lives": {"saved_tracks": 120.0},
                "match_strategy": {
                    "enable_spotify_id_match": True,
                    "enable_metadata_match": False,
                    "enable_fuzzy_match": True,
                },
                "match_strategy_order": [
                    "spotify_id_exact",
                    "fuzzy_title_artist",
                ],
                "temporal_controls": {
                    "reference_mode": "fixed",
                    "reference_now_utc": "2026-02-01T10:30:00Z",
                },
                "aggregation_policy": {
                    "preference_weight_mode": "capped",
                    "preference_weight_cap_per_event": 0.7,
                },
                "fuzzy_matching": {
                    "enabled": True,
                    "combined_threshold": 0.82,
                    "max_duration_delta_ms": 0,
                    "max_artist_candidates": 7,
                },
                "weighting_policy": {
                    "top_tracks": {"scale_multiplier": 42.0},
                    "playlist_items": {"min_position_floor": 0.1},
                },
            },
            "influence_tracks": {
                "enabled": True,
                "track_ids": ["track_a", "track_b", "track_a", "  "],
                "preference_weight": 2.5,
                "source": "manual",
            },
        },
    )

    seed_controls = resolve_bl003_seed_controls(run_config_path)
    weighting_policy = resolve_bl003_weighting_policy(run_config_path)
    influence_controls = resolve_bl003_influence_controls(run_config_path)

    assert seed_controls["match_rate_min_threshold"] == 0.35
    assert seed_controls["top_range_weights"]["short_term"] == 0.75
    assert seed_controls["top_range_weights"]["medium_term"] == 0.3
    assert seed_controls["source_base_weights"]["saved_tracks"] == 0.9
    assert seed_controls["decay_half_lives"]["saved_tracks"] == 120.0
    assert seed_controls["fuzzy_matching"]["enabled"] is True
    assert seed_controls["fuzzy_matching"]["combined_threshold"] == 0.82
    assert seed_controls["fuzzy_matching"]["max_duration_delta_ms"] == 0
    assert seed_controls["fuzzy_matching"]["max_artist_candidates"] == 7
    assert seed_controls["match_strategy"] == {
        "enable_spotify_id_match": True,
        "enable_metadata_match": False,
        "enable_fuzzy_match": True,
    }
    assert seed_controls["match_strategy_order"] == [
        "spotify_id_exact",
        "fuzzy_title_artist",
    ]
    assert seed_controls["temporal_controls"] == {
        "reference_mode": "fixed",
        "reference_now_utc": "2026-02-01T10:30:00Z",
    }
    assert seed_controls["aggregation_policy"] == {
        "preference_weight_mode": "capped",
        "preference_weight_cap_per_event": 0.7,
    }
    assert weighting_policy["top_tracks_scale_multiplier"] == 42.0
    assert weighting_policy["top_tracks_min_rank_floor"] == 0.05
    assert weighting_policy["playlist_items_min_position_floor"] == 0.1
    assert influence_controls["influence_enabled"] is True
    assert influence_controls["influence_track_ids"] == ["track_a", "track_b"]
    assert influence_controls["influence_preference_weight"] == 2.5


@pytest.mark.parametrize(
    ("payload", "match_text"),
    [
        (
            {"seed_controls": {"unexpected": 1}},
            "run_config.seed_controls contains unsupported keys",
        ),
        (
            {"seed_controls": {"top_range_weights": {"ultra_term": 0.4}}},
            "run_config.seed_controls.top_range_weights contains unsupported keys",
        ),
        (
            {"seed_controls": {"fuzzy_matching": {"max_artist_candidates": 0}}},
            "run_config.seed_controls.fuzzy_matching.max_artist_candidates must be > 0",
        ),
        (
            {"seed_controls": {"match_strategy_order": []}},
            "run_config.seed_controls.match_strategy_order must include at least one method",
        ),
        (
            {"seed_controls": {"match_strategy_order": ["spotify_id_exact", "spotify_id_exact"]}},
            "run_config.seed_controls.match_strategy_order must not contain duplicates",
        ),
        (
            {"seed_controls": {"match_strategy_order": ["bad_method"]}},
            "run_config.seed_controls.match_strategy_order contains unsupported method",
        ),
        (
            {"seed_controls": {"match_strategy": {"extra": True}}},
            "run_config.seed_controls.match_strategy contains unsupported keys",
        ),
        (
            {"seed_controls": {"temporal_controls": {"reference_mode": "bad"}}},
            "run_config.seed_controls.temporal_controls.reference_mode must be one of",
        ),
        (
            {"seed_controls": {"temporal_controls": {"reference_mode": "fixed"}}},
            "run_config.seed_controls.temporal_controls.reference_now_utc is required when reference_mode='fixed'",
        ),
        (
            {"seed_controls": {"temporal_controls": {"reference_mode": "fixed", "reference_now_utc": "not-a-date"}}},
            "run_config.seed_controls.temporal_controls.reference_now_utc must be a valid ISO-8601 datetime",
        ),
        (
            {"seed_controls": {"aggregation_policy": {"preference_weight_mode": "bad"}}},
            "run_config.seed_controls.aggregation_policy.preference_weight_mode must be one of",
        ),
        (
            {"seed_controls": {"aggregation_policy": {"preference_weight_mode": "capped"}}},
            "run_config.seed_controls.aggregation_policy.preference_weight_cap_per_event is required when preference_weight_mode='capped'",
        ),
        (
            {"seed_controls": {"aggregation_policy": {"preference_weight_mode": "capped", "preference_weight_cap_per_event": -0.1}}},
            "run_config.seed_controls.aggregation_policy.preference_weight_cap_per_event must be >= 0",
        ),
        (
            {"influence_tracks": {"preference_weight": 0}},
            "run_config.influence_tracks.preference_weight must be positive",
        ),
    ],
)
def test_resolve_effective_run_config_rejects_invalid_bl003_contract(
    tmp_path: Path,
    payload: dict[str, object],
    match_text: str,
) -> None:
    run_config_path = _write_run_config(tmp_path, payload)

    with pytest.raises(RunConfigError, match=match_text):
        resolve_effective_run_config(run_config_path)
