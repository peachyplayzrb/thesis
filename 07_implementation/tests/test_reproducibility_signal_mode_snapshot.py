from __future__ import annotations

from reproducibility.main import build_signal_mode_calibration_snapshot


def test_build_signal_mode_calibration_snapshot_extracts_mode_and_activation() -> None:
    bl005_diagnostics = {
        "config": {
            "signal_mode": {
                "name": "v1f-compat",
                "semantic_profile": "binary_overlap",
                "numeric_profile": "pass_count_support",
                "popularity_profile": {
                    "retrieval_enabled": False,
                    "scoring_enabled": False,
                },
            },
            "use_weighted_semantics": False,
            "use_continuous_numeric": False,
            "numeric_support_min_score": 1.0,
        }
    }
    bl006_summary = {
        "config": {
            "base_component_weights": {
                "tempo": 0.1,
                "popularity": 0.0,
            }
        }
    }

    snapshot = build_signal_mode_calibration_snapshot(bl005_diagnostics, bl006_summary)

    assert snapshot["mode_name"] == "v1f-compat"
    assert snapshot["semantic_profile"] == "binary_overlap"
    assert snapshot["numeric_profile"] == "pass_count_support"
    assert snapshot["retrieval_numeric_support_min_score"] == 1.0
    assert snapshot["retrieval_use_weighted_semantics"] is False
    assert snapshot["retrieval_use_continuous_numeric"] is False
    assert snapshot["retrieval_popularity_numeric_enabled"] is False
    assert snapshot["scoring_popularity_weight"] == 0.0
    assert snapshot["scoring_popularity_enabled"] is False
