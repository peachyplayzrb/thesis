from __future__ import annotations

from observability.main import (
    build_cross_stage_influence_attribution_summary,
    build_feature_availability_summary,
    build_playlist_tradeoff_summary,
    build_reproducibility_interpretation,
    build_retrieval_fidelity_summary,
    build_signal_mode_calibration_summary,
    build_source_resilience_diagnostics,
    summarize_control_causality,
)
from run_config.control_registry import build_control_registry_snapshot


def test_build_signal_mode_calibration_summary_extracts_comparison_fields() -> None:
    bl005_diagnostics = {
        "config": {
            "signal_mode": {
                "name": "v1g-enhanced",
                "semantic_profile": "weighted_overlap",
                "numeric_profile": "continuous_support",
                "popularity_profile": {
                    "retrieval_enabled": True,
                    "scoring_enabled": True,
                },
            },
            "use_weighted_semantics": True,
            "use_continuous_numeric": True,
            "numeric_support_min_score": 1.8,
            "numeric_thresholds": {
                "tempo": 20.0,
                "popularity": 15.0,
            },
        }
    }
    bl006_summary = {
        "config": {
            "base_component_weights": {
                "tempo": 0.09,
                "popularity": 0.06,
            }
        }
    }

    summary = build_signal_mode_calibration_summary(bl005_diagnostics, bl006_summary)

    assert summary["mode_name"] == "v1g-enhanced"
    assert summary["semantic_profile"] == "weighted_overlap"
    assert summary["numeric_profile"] == "continuous_support"
    assert summary["retrieval"]["use_weighted_semantics"] is True
    assert summary["retrieval"]["use_continuous_numeric"] is True
    assert summary["retrieval"]["numeric_support_min_score"] == 1.8
    assert summary["retrieval"]["popularity_numeric_enabled"] is True
    assert summary["retrieval"]["numeric_feature_count"] == 2
    assert summary["scoring"]["popularity_weight"] == 0.06
    assert summary["scoring"]["popularity_scoring_enabled"] is True


def test_build_source_resilience_diagnostics_emits_reason_codes() -> None:
    bl003_summary = {
        "inputs": {
            "selected_sources_expected": {
                "top_tracks": True,
                "saved_tracks": True,
                "playlist_items": True,
                "recently_played": False,
            },
            "selected_sources_available": {
                "top_tracks": True,
                "saved_tracks": False,
                "playlist_items": False,
                "recently_played": True,
            },
            "source_resilience_policy": {
                "top_tracks": "required",
                "saved_tracks": "optional",
                "playlist_items": "optional",
                "recently_played": "advisory",
            },
            "missing_selected_sources": ["saved_tracks", "playlist_items"],
            "missing_required_sources": [],
            "degraded_optional_sources": ["saved_tracks", "playlist_items"],
        },
        "source_stats": {
            "saved_tracks": {
                "export_outcome_status": "zero_results",
                "degraded_missing": True,
                "missing_required": False,
            },
            "playlist_items": {
                "export_outcome_status": "forbidden",
                "degraded_missing": True,
                "missing_required": False,
            },
        },
    }

    diagnostics = build_source_resilience_diagnostics(bl003_summary)

    assert diagnostics["source_decisions"]["top_tracks"]["reason_code"] == "selected_and_available"
    assert diagnostics["source_decisions"]["saved_tracks"]["reason_code"] == "degraded_optional"
    assert diagnostics["source_decisions"]["playlist_items"]["reason_code"] == "degraded_optional"
    assert diagnostics["source_decisions"]["recently_played"]["reason_code"] == "not_selected"


def test_summarize_control_causality_counts_complete_payloads() -> None:
    summary = summarize_control_causality(
        [
            {
                "track_id": "t1",
                "control_causality": {
                    "schema_version": "bl008-control-causality-v1",
                    "decision_outcome": {},
                    "controlling_parameters": {},
                    "effect_direction": {},
                    "evidence_sources": {},
                },
            }
        ]
    )

    assert summary["tracks_total"] == 1
    assert summary["tracks_with_control_causality"] == 1
    assert summary["tracks_missing_control_causality"] == 0
    assert summary["tracks_missing_required_keys"] == 0
    assert summary["schema_versions"] == {"bl008-control-causality-v1": 1}


def test_summarize_control_causality_reports_missing_contract_fields() -> None:
    summary = summarize_control_causality(
        [
            {
                "track_id": "t1",
            },
            {
                "track_id": "t2",
                "control_causality": {
                    "schema_version": "bl008-control-causality-v1",
                },
            },
        ]
    )

    assert summary["tracks_total"] == 2
    assert summary["tracks_missing_control_causality"] == 1
    assert summary["tracks_missing_required_keys"] >= 1
    assert "t1" in summary["sample_missing_track_ids"]


def test_summarize_control_causality_handles_empty_rejected_section() -> None:
    summary = summarize_control_causality([])

    assert summary["tracks_total"] == 0
    assert summary["tracks_missing_control_causality"] == 0
    assert summary["schema_versions"] == {}


def test_build_retrieval_fidelity_summary_surfaces_undo_c_fields() -> None:
    summary = build_retrieval_fidelity_summary(
        {
            "run_id": "BL005-FILTER-TEST",
            "counts": {
                "candidate_rows_total": 100,
                "kept_candidates": 24,
                "rejected_non_seed_candidates": 60,
            },
            "candidate_shaping_fidelity": {
                "pool_progression": {
                    "post_seed_exclusion_pool": 90,
                    "post_language_filter_pool": 80,
                    "post_recency_gate_pool": 70,
                },
                "exclusion_categories": {
                    "reject_language_filter": 10,
                    "reject_recency_gate": 10,
                    "reject_no_signal": 20,
                },
                "control_effect_observability": {
                    "language_filter_rejection_share": 0.111111,
                    "recency_gate_rejection_share": 0.125,
                    "threshold_rejection_share": 0.5,
                    "retained_share_after_gates": 0.342857,
                },
                "rejection_driver_contribution": {
                    "dominant_rejection_driver": "reject_no_signal",
                    "dominant_rejection_driver_share_of_total_rejections": 0.4,
                    "ranked_rejection_drivers": [
                        {"driver": "reject_no_signal", "count": 24},
                    ],
                },
                "threshold_effects": {
                    "threshold_attribution": {
                        "top_failure_features": [
                            {"feature": "tempo", "failed_count": 10},
                        ]
                    },
                    "directional_impact_summary": {
                        "relaxed_delta_vs_base": 4,
                        "tightened_delta_vs_base": -6,
                        "net_directional_span": 10,
                        "dominant_direction": "relaxation_dominant",
                    },
                },
            },
        }
    )

    assert summary["run_id"] == "BL005-FILTER-TEST"
    assert summary["pool_progression"]["candidate_rows_total"] == 100
    assert summary["pool_progression"]["post_recency_gate_pool"] == 70
    assert summary["control_effect_observability"]["threshold_rejection_share"] == 0.5
    assert summary["rejection_driver_contribution"]["dominant_rejection_driver"] == "reject_no_signal"
    assert summary["threshold_directional_impact"]["dominant_direction"] == "relaxation_dominant"
    assert summary["top_threshold_failure_features"][0]["feature"] == "tempo"


def test_build_playlist_tradeoff_summary_surfaces_undo_k_fields() -> None:
    summary = build_playlist_tradeoff_summary(
        {
            "run_id": "BL007-ASSEMBLE-TEST",
            "tradeoff_metrics_summary": {
                "playlist_size": 10,
                "diversity_distribution_summary": {
                    "unique_genre_count": 4,
                    "dominant_genre_share": 0.3,
                    "normalized_genre_entropy": 0.91,
                    "genre_switch_rate": 0.78,
                },
                "novelty_distance_summary": {
                    "transition_pair_count": 9,
                    "mean_adjacent_transition_distance": 0.34,
                    "max_adjacent_transition_distance": 0.71,
                },
                "ordering_pressure_summary": {
                    "mean_selected_rank": 17.4,
                    "median_selected_rank": 13,
                    "selected_rank_span": 42,
                    "top_100_exclusion_rate": 0.52,
                    "dominant_top_100_exclusion_reason": "genre_cap_exceeded",
                },
            },
        }
    )

    assert summary["run_id"] == "BL007-ASSEMBLE-TEST"
    assert summary["playlist_size"] == 10
    assert summary["diversity_distribution_summary"]["unique_genre_count"] == 4
    assert summary["novelty_distance_summary"]["mean_adjacent_transition_distance"] == 0.34
    assert summary["ordering_pressure_summary"]["dominant_top_100_exclusion_reason"] == "genre_cap_exceeded"


def test_build_cross_stage_influence_attribution_summary_surfaces_undo_q_fields() -> None:
    summary = build_cross_stage_influence_attribution_summary(
        profile={
            "interaction_attribution": {
                "policy_name": "split_selected_types_equal_share",
                "filtered_types_requested": ["history", "influence"],
                "contribution_by_type": {
                    "history": {"row_share": 0.8, "effective_weight": 12.0},
                    "influence": {"row_share": 0.2, "effective_weight": 3.5},
                },
            }
        },
        bl005_diagnostics={
            "candidate_shaping_fidelity": {
                "control_effect_observability": {
                    "language_filter_rejection_share": 0.125,
                },
                "threshold_effects": {
                    "directional_impact_summary": {
                        "dominant_direction": "relaxation_dominant",
                    }
                },
            },
            "bounded_what_if_estimates": {
                "per_control_family_scenarios": {
                    "language_filter": {
                        "delta_vs_base": 4,
                    }
                }
            },
        },
        bl006_summary={
            "counts": {"candidate_count": 50, "scored_rows": 50},
            "score_statistics": {"mean_final_score": 0.73, "mean_raw_final_score": 0.69},
            "influence_contract_source": "present",
        },
        bl007_report={
            "config": {
                "influence_enabled": True,
                "influence_policy_mode": "reserved_slots",
                "influence_reserved_slots": 2,
            },
            "influence_effectiveness_diagnostics": {
                "effectiveness_rate": 0.5,
            },
        },
        control_causality_summary={
            "tracks_total": 10,
            "tracks_with_control_causality": 8,
            "tracks_missing_control_causality": 2,
        },
        influence_track_diagnostics=[
            {"track_id": "t1", "included_in_playlist": True},
            {"track_id": "t2", "included_in_playlist": False},
        ],
    )

    assert summary["schema_version"] == "cross-stage-influence-attribution-v1"
    assert summary["stage_chain"] == ["BL-004", "BL-005", "BL-006", "BL-007", "BL-009"]
    assert summary["bl004_profile_influence"]["interaction_attribution_mode"] == "split_selected_types_equal_share"
    assert summary["bl005_retrieval_effects"]["language_filter_disabled_delta_vs_base"] == 4
    assert summary["bl006_scoring_context"]["influence_contract_source"] == "present"
    assert summary["bl006_scoring_context"]["mean_raw_final_score"] == 0.69
    assert summary["bl007_assembly_effects"]["requested_influence_tracks"] == 2
    assert summary["bl007_assembly_effects"]["included_influence_tracks"] == 1
    assert summary["bl009_explanation_linkage"]["tracks_missing_control_causality"] == 2
    assert summary["bl009_explanation_linkage"]["control_causality_coverage"] == 0.8


def test_build_feature_availability_summary_surfaces_undo_m_fields() -> None:
    summary = build_feature_availability_summary(
        {
            "feature_availability_summary": {
                "matched_seed_count": 20,
                "missing_numeric_track_count": 3,
                "missing_numeric_track_ratio": 0.15,
                "no_numeric_signal_row_count": 2,
                "malformed_numeric_row_count": 1,
                "numeric_feature_coverage_by_feature": {
                    "tempo": 0.9,
                },
            }
        },
        {
            "feature_availability_summary": {
                "candidate_count": 100,
                "rows_with_all_numeric_features": 80,
                "rows_with_no_numeric_features": 10,
                "rows_with_no_semantic_signal": 5,
                "numeric_feature_coverage_by_feature": {
                    "tempo": 0.95,
                },
                "lead_genre_source_counts": {
                    "genres": 88,
                    "tags": 7,
                    "missing": 5,
                },
            }
        },
    )

    assert summary["profile"]["missing_numeric_track_ratio"] == 0.15
    assert summary["candidates"]["candidate_count"] == 100
    assert summary["candidates"]["lead_genre_source_counts"]["genres"] == 88
    assert summary["boundary_indicators"]["status"] == "within-expected-bounds"


def test_build_control_registry_snapshot_emits_undo_n_fields() -> None:
    snapshot = build_control_registry_snapshot()

    assert snapshot["schema_version"] == "control-registry-v1"
    assert snapshot["entry_count"] >= 20
    assert "BL-005" in snapshot["stages"]
    assert "BL-007" in snapshot["stages"]
    controls_by_name = {entry["name"]: entry for entry in snapshot["controls"]}
    assert "confidence_weighting_mode" in controls_by_name
    assert "component_weights" in controls_by_name
    assert "target_size" in controls_by_name
    weight_entry = controls_by_name["confidence_weighting_mode"]
    assert weight_entry["stage"] == "BL-004"
    assert weight_entry["section"] == "profile_controls"
    assert "linear_half_bias" in weight_entry["valid_values"]
    target_entry = controls_by_name["target_size"]
    assert target_entry["type"] == "positive_int"
    assert target_entry["default"] == 10
def test_build_control_registry_snapshot_emits_undo_n_fields() -> None:
    snapshot = build_control_registry_snapshot()

    assert snapshot["schema_version"] == "control-registry-v1"
    assert snapshot["entry_count"] >= 20
    assert "BL-005" in snapshot["stages"]
    assert "BL-007" in snapshot["stages"]
    controls_by_name = {entry["name"]: entry for entry in snapshot["controls"]}
    assert "confidence_weighting_mode" in controls_by_name
    assert "component_weights" in controls_by_name
    assert "target_size" in controls_by_name
    weight_entry = controls_by_name["confidence_weighting_mode"]
    assert weight_entry["stage"] == "BL-004"
    assert weight_entry["section"] == "profile_controls"
    assert "linear_half_bias" in weight_entry["valid_values"]
    target_entry = controls_by_name["target_size"]
    assert target_entry["type"] == "positive_int"
    assert target_entry["default"] == 10


def test_build_reproducibility_interpretation_emits_undo_o_fields() -> None:
    interp = build_reproducibility_interpretation()

    assert interp["schema_version"] == "reproducibility-interpretation-v1"
    assert "artifact-level" in str(interp["verdict_basis"])
    non_claims = interp["non_claims"]
    assert isinstance(non_claims, list)
    assert len(non_claims) >= 1
    assert any("cross-environment" in item for item in non_claims)
