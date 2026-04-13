from __future__ import annotations

from typing import cast

from retrieval.input_validation import validate_bl004_bl005_handshake


def test_validate_bl004_bl005_handshake_warn_mode_records_violations() -> None:
    report = validate_bl004_bl005_handshake(
        profile={
            "semantic_profile": {},
            "numeric_feature_profile": {"tempo": 120.0},
            "input_artifacts": {},
        },
        seed_trace_rows=[{"track_id": "seed_1", "match_confidence_score": "1.0"}],
        numeric_thresholds={"tempo": 20.0, "release_year": 8.0},
        policy="warn",
    )

    assert report["status"] == "warn"
    assert report["bl004_profile_schema_valid"] is False
    assert report["seed_trace_schema_valid"] is True
    assert report["control_constraints_valid"] is False
    assert "numeric_confidence" in cast(list[str], report["missing_profile_keys"])
    assert cast(list[str], report["missing_seed_fields"]) == []
    assert "release_year" in cast(list[str], report["numeric_thresholds_extra_keys"])


def test_validate_bl004_bl005_handshake_allow_mode_does_not_fail() -> None:
    report = validate_bl004_bl005_handshake(
        profile={"run_id": "BL004-PROFILE-TEST"},
        seed_trace_rows=[],
        numeric_thresholds={"tempo": 20.0},
        policy="allow",
    )

    assert report["status"] == "allow"
    assert report["sampled_violations"]


def test_validate_bl004_bl005_handshake_strict_mode_reports_fail() -> None:
    report = validate_bl004_bl005_handshake(
        profile={
            "semantic_profile": {},
            "numeric_feature_profile": {"tempo": 120.0},
            "input_artifacts": {},
        },
        seed_trace_rows=[{"track_id": "seed_1"}],
        numeric_thresholds={"tempo": 20.0},
        policy="strict",
    )

    assert report["status"] == "fail"
    assert report["control_constraint_violations"]


def test_validate_bl004_bl005_handshake_warn_mode_detects_malformed_confidence_rows() -> None:
    report = validate_bl004_bl005_handshake(
        profile={
            "semantic_profile": {},
            "numeric_feature_profile": {"tempo": 120.0},
            "numeric_confidence": {"confidence_by_feature": {"tempo": 1.0}},
            "input_artifacts": {},
        },
        seed_trace_rows=[
            {"track_id": "seed_1", "match_confidence_score": ""},
            {"track_id": "seed_2", "match_confidence_score": "bad"},
        ],
        numeric_thresholds={"tempo": 20.0},
        policy="warn",
    )

    assert report["status"] == "warn"
    assert report["seed_trace_schema_valid"] is False
    assert report["seed_confidence_field_present"] is True
    assert report["malformed_seed_confidence_rows"] == 2
    assert report["out_of_range_seed_confidence_rows"] == 0


def test_validate_bl004_bl005_handshake_strict_mode_fails_on_out_of_range_confidence() -> None:
    report = validate_bl004_bl005_handshake(
        profile={
            "semantic_profile": {},
            "numeric_feature_profile": {"tempo": 120.0},
            "numeric_confidence": {"confidence_by_feature": {"tempo": 1.0}},
            "input_artifacts": {},
        },
        seed_trace_rows=[
            {"track_id": "seed_1", "match_confidence_score": "1.2"},
            {"track_id": "seed_2", "match_confidence_score": "0.9"},
        ],
        numeric_thresholds={"tempo": 20.0},
        policy="strict",
    )

    assert report["status"] == "fail"
    assert report["seed_trace_schema_valid"] is False
    assert report["malformed_seed_confidence_rows"] == 0
    assert report["out_of_range_seed_confidence_rows"] == 1
