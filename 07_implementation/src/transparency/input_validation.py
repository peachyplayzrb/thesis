"""Input validation for BL-008 transparency — BL-007↔BL-008 handshake."""

from __future__ import annotations

from typing import Any, Mapping


VALIDATION_POLICIES: tuple[str, ...] = ("allow", "warn", "strict")

# Required fields in each BL-007 playlist track entry that BL-008 depends on
# to produce a well-formed explanation payload.
REQUIRED_BL007_PLAYLIST_TRACK_FIELDS: tuple[str, ...] = (
    "track_id",
    "final_score",
    "playlist_position",
)

# Required columns in the BL-007 assembly trace CSV that BL-008 uses for
# per-track assembly context.
REQUIRED_BL007_TRACE_FIELDS: tuple[str, ...] = (
    "track_id",
    "decision",
    "score_rank",
)


def normalize_validation_policy(policy: Any, default: str = "warn") -> str:
    value = str(policy or default).strip().lower()
    if value in VALIDATION_POLICIES:
        return value
    return default


def validate_bl007_bl008_handshake(
    *,
    playlist_tracks: list[Mapping[str, object]],
    trace_header: list[str],
    policy: str,
) -> dict[str, object]:
    """Validate BL-007 outputs meet the BL-007↔BL-008 handshake contract.

    Checks:
    - Playlist tracks list is non-empty.
    - All required BL-007 playlist track fields are present in the first track.
    - All rows supply a non-empty track_id.
    - All rows supply a parseable final_score.
    - Assembly trace CSV header contains the required columns.

    Returns a diagnostics dict with policy, status, and violation details.
    """
    normalized_policy = normalize_validation_policy(policy)

    first_track_keys = list(playlist_tracks[0].keys()) if playlist_tracks else []

    playlist_is_empty = len(playlist_tracks) == 0
    missing_track_fields = [
        field for field in REQUIRED_BL007_PLAYLIST_TRACK_FIELDS if field not in first_track_keys
    ]
    missing_trace_fields = [
        field for field in REQUIRED_BL007_TRACE_FIELDS if field not in trace_header
    ]
    rows_missing_track_id = sum(
        1 for track in playlist_tracks if not str(track.get("track_id", "")).strip()
    )
    rows_missing_score = sum(
        1 for track in playlist_tracks
        if not str(track.get("final_score", "")).strip()
        or str(track.get("final_score", "")).strip().lower() in {"nan", "none"}
    )

    violations: list[str] = []
    if playlist_is_empty:
        violations.append("playlist_tracks_empty=true")
    if missing_track_fields:
        violations.append(f"missing_bl007_playlist_track_fields={missing_track_fields}")
    if missing_trace_fields:
        violations.append(f"missing_bl007_trace_fields={missing_trace_fields}")
    if rows_missing_track_id > 0:
        violations.append(f"playlist_rows_missing_track_id={rows_missing_track_id}")
    if rows_missing_score > 0:
        violations.append(f"playlist_rows_missing_final_score={rows_missing_score}")

    strict_failure = normalized_policy == "strict" and bool(violations)
    if strict_failure:
        status = "fail"
    elif violations and normalized_policy == "warn":
        status = "warn"
    elif violations and normalized_policy == "allow":
        status = "allow"
    else:
        status = "pass"

    return {
        "policy": normalized_policy,
        "status": status,
        "missing_bl007_playlist_track_fields": missing_track_fields,
        "missing_bl007_trace_fields": missing_trace_fields,
        "playlist_rows_missing_track_id": rows_missing_track_id,
        "playlist_rows_missing_final_score": rows_missing_score,
        "control_constraint_violations": violations,
        "sampled_violations": violations[:10],
    }
