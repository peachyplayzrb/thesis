


from __future__ import annotations

from reproducibility.main import build_interpretation_boundaries, build_signal_mode_calibration_snapshot


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


def test_build_interpretation_boundaries_has_schema_version() -> None:
    boundaries = build_interpretation_boundaries()

    assert boundaries["schema_version"] == "reproducibility-interpretation-v1"


def test_build_interpretation_boundaries_verdict_basis_mentions_artifact_level() -> None:
    boundaries = build_interpretation_boundaries()

    assert "artifact-level" in str(boundaries["verdict_basis"])


def test_build_interpretation_boundaries_non_claims_is_nonempty_list() -> None:
    boundaries = build_interpretation_boundaries()

    non_claims = boundaries["non_claims"]
    assert isinstance(non_claims, list)
    assert len(non_claims) >= 1


def test_build_interpretation_boundaries_consistency_domain_has_covered_and_not_covered() -> None:
    boundaries = build_interpretation_boundaries()

    domain = boundaries["consistency_domain"]
    assert isinstance(domain, dict)
    covered = domain["covered"]
    not_covered = domain["not_covered"]
    assert isinstance(covered, list) and len(covered) >= 1
    assert isinstance(not_covered, list) and len(not_covered) >= 1
