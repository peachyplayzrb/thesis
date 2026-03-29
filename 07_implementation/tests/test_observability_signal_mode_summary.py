from __future__ import annotations

from observability.main import build_signal_mode_calibration_summary


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
