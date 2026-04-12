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
    resolve_bl005_controls,
    resolve_bl006_controls,
    resolve_bl007_controls,
    resolve_bl008_controls,
    resolve_bl009_controls,
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
                "source_resilience_policy": {"saved_tracks": "required", "recently_played": "optional"},
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
    assert seed_controls["source_resilience_policy"]["saved_tracks"] == "required"
    assert seed_controls["source_resilience_policy"]["recently_played"] == "optional"
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


def test_resolve_bl007_controls_includes_influence_policy_contract(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "influence_tracks": {
                "enabled": True,
                "track_ids": ["x1", "x2"],
            },
            "assembly_controls": {
                "target_size": 4,
                "influence_policy_mode": "reserved_slots",
                "influence_reserved_slots": 10,
                "influence_allow_genre_cap_override": True,
                "influence_allow_consecutive_override": False,
                "influence_allow_score_threshold_override": True,
            },
        },
    )

    controls = resolve_bl007_controls(run_config_path)

    assert controls["influence_enabled"] is True
    assert controls["influence_track_ids"] == ["x1", "x2"]
    assert controls["influence_policy_mode"] == "reserved_slots"
    assert controls["influence_reserved_slots"] == 4
    assert controls["influence_allow_genre_cap_override"] is True
    assert controls["influence_allow_consecutive_override"] is False
    assert controls["influence_allow_score_threshold_override"] is True


def test_profile_controls_schema_coercion_and_fallback(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "profile_controls": {
                "top_tag_limit": "12",
                "top_genre_limit": "0",
                "confidence_weighting_mode": "unknown",
                "interaction_attribution_mode": "primary_type_only",
                "emit_profile_policy_diagnostics": "false",
            }
        },
    )

    effective, _ = resolve_effective_run_config(run_config_path)
    profile_controls = effective["profile_controls"]

    assert profile_controls["top_tag_limit"] == 12
    # Non-positive values fall back to canonical default.
    assert profile_controls["top_genre_limit"] == 8
    assert profile_controls["confidence_weighting_mode"] == "linear_half_bias"
    assert profile_controls["interaction_attribution_mode"] == "primary_type_only"
    assert profile_controls["emit_profile_policy_diagnostics"] is False


def test_profile_controls_schema_fraction_validation_error(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "profile_controls": {
                "confidence_bin_high_threshold": 1.2,
            }
        },
    )

    with pytest.raises(RunConfigError, match="profile_controls.confidence_bin_high_threshold"):
        resolve_effective_run_config(run_config_path)


def test_retrieval_controls_schema_fallback_and_enum_normalization(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "retrieval_controls": {
                "profile_top_tag_limit": "0",
                "profile_top_genre_limit": "8",
                "profile_numeric_confidence_mode": "blended",
                "numeric_support_score_mode": "unknown",
            }
        },
    )

    effective, _ = resolve_effective_run_config(run_config_path)
    retrieval_controls = effective["retrieval_controls"]

    assert retrieval_controls["profile_top_tag_limit"] == 10
    assert retrieval_controls["profile_top_genre_limit"] == 8
    assert retrieval_controls["profile_numeric_confidence_mode"] == "blended"
    assert retrieval_controls["numeric_support_score_mode"] == "weighted_absolute"


def test_retrieval_controls_schema_bool_like_validation_error(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "retrieval_controls": {
                "emit_profile_policy_diagnostics": "not_bool",
            }
        },
    )

    with pytest.raises(RunConfigError, match="retrieval_controls.emit_profile_policy_diagnostics"):
        resolve_effective_run_config(run_config_path)


def test_scoring_controls_schema_fallback_and_enum_normalization(tmp_path: Path) -> None:
    default_effective, _ = resolve_effective_run_config(None)
    default_scoring = default_effective["scoring_controls"]

    run_config_path = _write_run_config(
        tmp_path,
        {
            "scoring_controls": {
                "lead_genre_strategy": "unknown",
                "semantic_overlap_strategy": "PRECISION_AWARE",
                "profile_numeric_confidence_mode": "unsupported",
                "semantic_precision_alpha_fixed": "0.45",
                "emit_confidence_impact_diagnostics": "false",
                "influence_track_bonus_scale": -1,
            }
        },
    )

    effective, _ = resolve_effective_run_config(run_config_path)
    scoring_controls = effective["scoring_controls"]

    assert scoring_controls["lead_genre_strategy"] == default_scoring["lead_genre_strategy"]
    assert scoring_controls["semantic_overlap_strategy"] == "precision_aware"
    assert scoring_controls["profile_numeric_confidence_mode"] == default_scoring["profile_numeric_confidence_mode"]
    assert scoring_controls["semantic_precision_alpha_fixed"] == 0.45
    assert scoring_controls["emit_confidence_impact_diagnostics"] is False
    assert scoring_controls["influence_track_bonus_scale"] == default_scoring["influence_track_bonus_scale"]


def test_scoring_controls_schema_bool_like_validation_error(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "scoring_controls": {
                "emit_semantic_precision_diagnostics": "not_bool",
            }
        },
    )

    with pytest.raises(RunConfigError, match="scoring_controls.emit_semantic_precision_diagnostics"):
        resolve_effective_run_config(run_config_path)


def test_observability_transparency_numeric_schema_fallback_and_bool_parity(tmp_path: Path) -> None:
    default_effective, _ = resolve_effective_run_config(None)
    default_observability = default_effective["observability_controls"]
    default_transparency = default_effective["transparency_controls"]

    run_config_path = _write_run_config(
        tmp_path,
        {
            "observability_controls": {
                "diagnostic_sample_limit": "0",
                "bootstrap_mode": "not_bool",
            },
            "transparency_controls": {
                "top_contributor_limit": 0,
                "primary_contributor_tie_delta": -0.1,
                "blend_primary_contributor_on_near_tie": "not_bool",
            },
        },
    )

    effective, _ = resolve_effective_run_config(run_config_path)
    observability_controls = effective["observability_controls"]
    transparency_controls = effective["transparency_controls"]

    assert observability_controls["diagnostic_sample_limit"] == default_observability["diagnostic_sample_limit"]
    assert observability_controls["bootstrap_mode"] == default_observability["bootstrap_mode"]
    assert transparency_controls["top_contributor_limit"] == default_transparency["top_contributor_limit"]
    assert transparency_controls["primary_contributor_tie_delta"] == default_transparency["primary_contributor_tie_delta"]
    assert (
        transparency_controls["blend_primary_contributor_on_near_tie"]
        == default_transparency["blend_primary_contributor_on_near_tie"]
    )


def test_bl005_bl006_resolvers_follow_effective_validated_controls(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "retrieval_controls": {
                "profile_top_tag_limit": "0",
                "numeric_support_score_mode": "unknown",
                "emit_profile_policy_diagnostics": "false",
            },
            "scoring_controls": {
                "lead_genre_strategy": "single_anchor",
                "semantic_overlap_strategy": "PRECISION_AWARE",
                "emit_confidence_impact_diagnostics": "false",
            },
        },
    )

    effective, _ = resolve_effective_run_config(run_config_path)
    bl005 = resolve_bl005_controls(run_config_path)
    bl006 = resolve_bl006_controls(run_config_path)

    assert bl005["profile_top_tag_limit"] == effective["retrieval_controls"]["profile_top_tag_limit"]
    assert bl005["numeric_support_score_mode"] == effective["retrieval_controls"]["numeric_support_score_mode"]
    assert (
        bl005["emit_profile_policy_diagnostics"]
        == effective["retrieval_controls"]["emit_profile_policy_diagnostics"]
    )
    assert bl006["lead_genre_strategy"] == effective["scoring_controls"]["lead_genre_strategy"]
    assert bl006["semantic_overlap_strategy"] == effective["scoring_controls"]["semantic_overlap_strategy"]
    assert (
        bl006["emit_confidence_impact_diagnostics"]
        == effective["scoring_controls"]["emit_confidence_impact_diagnostics"]
    )


def test_bl008_bl009_resolvers_follow_effective_validated_controls(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "transparency_controls": {
                "top_contributor_limit": "0",
                "primary_contributor_tie_delta": -0.1,
                "blend_primary_contributor_on_near_tie": "not_bool",
            },
            "observability_controls": {
                "diagnostic_sample_limit": "0",
                "bootstrap_mode": "not_bool",
            },
        },
    )

    effective, _ = resolve_effective_run_config(run_config_path)
    bl008 = resolve_bl008_controls(run_config_path)
    bl009 = resolve_bl009_controls(run_config_path)

    assert bl008["top_contributor_limit"] == effective["transparency_controls"]["top_contributor_limit"]
    assert (
        bl008["blend_primary_contributor_on_near_tie"]
        == effective["transparency_controls"]["blend_primary_contributor_on_near_tie"]
    )
    assert (
        bl008["primary_contributor_tie_delta"]
        == effective["transparency_controls"]["primary_contributor_tie_delta"]
    )
    assert bl009["diagnostic_sample_limit"] == effective["observability_controls"]["diagnostic_sample_limit"]
    assert bl009["bootstrap_mode"] == effective["observability_controls"]["bootstrap_mode"]


def test_bl003_weighting_policy_resolver_follows_effective_validated_controls(tmp_path: Path) -> None:
    run_config_path = _write_run_config(
        tmp_path,
        {
            "seed_controls": {
                "weighting_policy": {
                    "top_tracks": {"scale_multiplier": 42.0},
                    "playlist_items": {"min_position_floor": 0.1},
                }
            }
        },
    )

    effective, _ = resolve_effective_run_config(run_config_path)
    weighting_policy = effective["seed_controls"]["weighting_policy"]
    resolved = resolve_bl003_weighting_policy(run_config_path)

    assert resolved["top_tracks_min_rank_floor"] == weighting_policy["top_tracks"]["min_rank_floor"]
    assert resolved["top_tracks_scale_multiplier"] == weighting_policy["top_tracks"]["scale_multiplier"]
    assert (
        resolved["top_tracks_default_time_range_weight"]
        == weighting_policy["top_tracks"]["default_time_range_weight"]
    )
    assert (
        resolved["playlist_items_min_position_floor"]
        == weighting_policy["playlist_items"]["min_position_floor"]
    )
    assert resolved["playlist_items_scale_multiplier"] == weighting_policy["playlist_items"]["scale_multiplier"]
