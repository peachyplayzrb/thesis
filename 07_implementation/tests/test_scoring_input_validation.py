from __future__ import annotations

from scoring.input_validation import validate_bl005_bl006_handshake


def test_validate_bl005_bl006_handshake_warn_status_with_missing_fields() -> None:
    validation = validate_bl005_bl006_handshake(
        candidates=[{"track_id": "track_1", "song": "Song A"}],
        policy="warn",
    )

    assert validation["status"] == "warn"
    assert validation["policy"] == "warn"
    assert validation["control_constraint_violations"]


def test_validate_bl005_bl006_handshake_strict_status_fails_with_missing_track_id() -> None:
    validation = validate_bl005_bl006_handshake(
        candidates=[
            {
                "id": "cand_1",
                "track_id": "",
                "artist": "Artist A",
                "song": "Song A",
                "tags": "rock",
                "genres": "rock",
                "tempo": "120",
                "duration_ms": "180000",
                "key": "1",
                "mode": "1",
            }
        ],
        policy="strict",
    )

    assert validation["status"] == "fail"
    assert validation["rows_missing_track_id"] == 1


def test_validate_bl005_bl006_handshake_passes_when_contract_complete() -> None:
    validation = validate_bl005_bl006_handshake(
        candidates=[
            {
                "cid": "cand_1",
                "track_id": "track_1",
                "artist": "Artist A",
                "song": "Song A",
                "tags": "rock",
                "genres": "rock",
                "tempo": "120",
                "duration_ms": "180000",
                "key": "1",
                "mode": "1",
            }
        ],
        policy="strict",
    )

    assert validation["status"] == "pass"
    assert validation["control_constraint_violations"] == []
