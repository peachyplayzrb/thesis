from __future__ import annotations

from observability.input_validation import (
    normalize_validation_policy,
    validate_bl008_bl009_handshake,
)


def _summary() -> dict[str, object]:
    return {
        "run_id": "BL008-EXPLAIN-TEST",
        "playlist_track_count": 1,
        "top_contributor_distribution": {"Lead genre match": 1},
    }


def _payloads() -> dict[str, object]:
    return {
        "playlist_track_count": 1,
        "explanations": [{"track_id": "track_1"}],
    }


def test_normalize_validation_policy_accepts_valid_values() -> None:
    assert normalize_validation_policy("allow") == "allow"
    assert normalize_validation_policy("warn") == "warn"
    assert normalize_validation_policy("strict") == "strict"


def test_normalize_validation_policy_falls_back_for_unknown() -> None:
    assert normalize_validation_policy("invalid") == "warn"


def test_handshake_passes_with_consistent_bl008_outputs() -> None:
    result = validate_bl008_bl009_handshake(
        bl008_summary=_summary(),
        bl008_payloads=_payloads(),
        policy="warn",
    )

    assert result["status"] == "pass"
    assert result["control_constraint_violations"] == []


def test_handshake_detects_missing_summary_keys() -> None:
    result = validate_bl008_bl009_handshake(
        bl008_summary={"run_id": "BL008-EXPLAIN-TEST"},
        bl008_payloads=_payloads(),
        policy="warn",
    )

    assert result["status"] == "warn"
    assert "missing_bl008_summary_keys=['playlist_track_count', 'top_contributor_distribution']" in result[
        "control_constraint_violations"
    ]


def test_handshake_detects_missing_payload_keys() -> None:
    result = validate_bl008_bl009_handshake(
        bl008_summary=_summary(),
        bl008_payloads={"playlist_track_count": 1},
        policy="warn",
    )

    assert result["status"] == "warn"
    assert "missing_bl008_payload_keys=['explanations']" in result["control_constraint_violations"]


def test_handshake_detects_count_mismatch() -> None:
    result = validate_bl008_bl009_handshake(
        bl008_summary=_summary(),
        bl008_payloads={
            "playlist_track_count": 2,
            "explanations": [{"track_id": "track_1"}],
        },
        policy="warn",
    )

    assert result["status"] == "warn"
    assert any(
        item.startswith("bl008_summary_payload_count_mismatch=")
        for item in result["control_constraint_violations"]
    )


def test_handshake_strict_fails_on_violations() -> None:
    result = validate_bl008_bl009_handshake(
        bl008_summary={},
        bl008_payloads={},
        policy="strict",
    )

    assert result["status"] == "fail"


def test_handshake_allow_mode_does_not_escalate_violations() -> None:
    result = validate_bl008_bl009_handshake(
        bl008_summary={},
        bl008_payloads={},
        policy="allow",
    )

    assert result["status"] == "allow"
