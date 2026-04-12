from __future__ import annotations

from observability.main import build_signal_mode_calibration_summary, build_source_resilience_diagnostics


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
