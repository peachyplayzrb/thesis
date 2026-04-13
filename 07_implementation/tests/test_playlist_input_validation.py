"""Tier-A unit tests for playlist.input_validation — BL-006↔BL-007 handshake validator."""

from playlist.input_validation import (
    REQUIRED_BL006_SCORED_FIELDS,
    BL006_SCORING_COMPONENT_INDICATORS,
    normalize_validation_policy,
    validate_bl006_bl007_handshake,
)


def _full_row() -> dict[str, str]:
    return {
        "rank": "1",
        "track_id": "track_1",
        "lead_genre": "rock",
        "final_score": "0.95",
        "matched_genres": "rock",
        "matched_tags": "guitar",
        "lead_genre_contribution": "0.3",
        "genre_overlap_contribution": "0.3",
        "tag_overlap_contribution": "0.35",
    }


# ---------------------------------------------------------------------------
# normalize_validation_policy
# ---------------------------------------------------------------------------


def test_normalize_validation_policy_known_values_pass_through() -> None:
    for policy in ("allow", "warn", "strict"):
        assert normalize_validation_policy(policy) == policy


def test_normalize_validation_policy_invalid_falls_back_to_warn() -> None:
    assert normalize_validation_policy("invalid") == "warn"


def test_normalize_validation_policy_none_falls_back_to_warn() -> None:
    assert normalize_validation_policy(None) == "warn"


def test_normalize_validation_policy_empty_string_falls_back_to_warn() -> None:
    assert normalize_validation_policy("") == "warn"


# ---------------------------------------------------------------------------
# validate_bl006_bl007_handshake — clean pass
# ---------------------------------------------------------------------------


def test_validate_bl006_bl007_handshake_pass_when_all_fields_present() -> None:
    result = validate_bl006_bl007_handshake(
        candidates=[_full_row()],
        policy="warn",
    )

    assert result["status"] == "pass"
    assert result["policy"] == "warn"
    assert result["missing_bl006_scored_fields"] == []
    assert result["scoring_component_fields_present"] != []
    assert result["rows_missing_track_id"] == 0
    assert result["rows_missing_final_score"] == 0
    assert result["control_constraint_violations"] == []


# ---------------------------------------------------------------------------
# validate_bl006_bl007_handshake — field violations
# ---------------------------------------------------------------------------


def test_validate_bl006_bl007_handshake_detects_missing_required_fields() -> None:
    row = _full_row()
    del row["matched_genres"]
    del row["matched_tags"]

    result = validate_bl006_bl007_handshake(candidates=[row], policy="warn")

    assert "matched_genres" in result["missing_bl006_scored_fields"]
    assert "matched_tags" in result["missing_bl006_scored_fields"]
    assert result["control_constraint_violations"] != []


def test_validate_bl006_bl007_handshake_detects_absent_scoring_components() -> None:
    row = {k: v for k, v in _full_row().items() if k not in BL006_SCORING_COMPONENT_INDICATORS}

    result = validate_bl006_bl007_handshake(candidates=[row], policy="warn")

    assert result["scoring_component_fields_present"] == []
    assert any("scoring_component" in v for v in result["control_constraint_violations"])


def test_validate_bl006_bl007_handshake_detects_rows_missing_track_id() -> None:
    row = _full_row()
    row["track_id"] = ""

    result = validate_bl006_bl007_handshake(candidates=[row], policy="warn")

    assert result["rows_missing_track_id"] == 1
    assert any("track_id" in v for v in result["control_constraint_violations"])


def test_validate_bl006_bl007_handshake_detects_rows_missing_final_score() -> None:
    row = _full_row()
    row["final_score"] = "nan"

    result = validate_bl006_bl007_handshake(candidates=[row], policy="warn")

    assert result["rows_missing_final_score"] == 1
    assert any("final_score" in v for v in result["control_constraint_violations"])


# ---------------------------------------------------------------------------
# validate_bl006_bl007_handshake — policy routing
# ---------------------------------------------------------------------------


def test_validate_bl006_bl007_handshake_warn_policy_yields_warn_status() -> None:
    row = _full_row()
    del row["matched_genres"]

    result = validate_bl006_bl007_handshake(candidates=[row], policy="warn")

    assert result["status"] == "warn"


def test_validate_bl006_bl007_handshake_strict_policy_yields_fail_status() -> None:
    row = _full_row()
    del row["matched_genres"]

    result = validate_bl006_bl007_handshake(candidates=[row], policy="strict")

    assert result["status"] == "fail"


def test_validate_bl006_bl007_handshake_allow_policy_yields_allow_status() -> None:
    row = _full_row()
    del row["matched_genres"]

    result = validate_bl006_bl007_handshake(candidates=[row], policy="allow")

    assert result["status"] == "allow"


# ---------------------------------------------------------------------------
# validate_bl006_bl007_handshake — edge cases
# ---------------------------------------------------------------------------


def test_validate_bl006_bl007_handshake_empty_candidates_has_no_row_violations() -> None:
    result = validate_bl006_bl007_handshake(candidates=[], policy="warn")

    assert result["rows_missing_track_id"] == 0
    assert result["rows_missing_final_score"] == 0
    # All required fields are missing (no rows → no fieldnames)
    for field in REQUIRED_BL006_SCORED_FIELDS:
        assert field in result["missing_bl006_scored_fields"]


def test_validate_bl006_bl007_handshake_invalid_policy_normalised_to_warn() -> None:
    result = validate_bl006_bl007_handshake(
        candidates=[_full_row()],
        policy="__bad_policy__",
    )

    assert result["policy"] == "warn"
    assert result["status"] == "pass"


def test_validate_bl006_bl007_handshake_sampled_violations_capped_at_ten() -> None:
    # Build a row that is missing all required fields and all scoring components —
    # that creates many violation entries.
    row: dict[str, str] = {}

    result = validate_bl006_bl007_handshake(candidates=[row], policy="allow")

    assert len(result["sampled_violations"]) <= 10
