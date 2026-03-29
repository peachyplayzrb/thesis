"""Text normalization and candidate selection helpers for BL-003 matching."""
from __future__ import annotations

from typing import Any

from rapidfuzz import fuzz

from shared_utils.constants import DEFAULT_SEED_CONTROLS
from shared_utils.parsing import normalize_ascii_text, parse_int


def normalize_text(value: str) -> str:
    """Normalise a string to ASCII lower-case tokens for fuzzy key comparison."""
    return normalize_ascii_text(value)


def first_artist(artist_names: str) -> str:
    """Return the primary artist from a pipe-, semicolon-, or comma-separated string."""
    if "|" in artist_names:
        return artist_names.split("|", 1)[0].strip()
    if ";" in artist_names:
        return artist_names.split(";", 1)[0].strip()
    if "," in artist_names:
        return artist_names.split(",", 1)[0].strip()
    return artist_names.strip()


def choose_best_duration_match(
    candidates: list[dict[str, str]],
    target_duration_ms: int | None,
) -> tuple[dict[str, str], int | None]:
    """Select the candidate whose duration is closest to the target, falling back to first."""
    if not candidates:
        raise ValueError("candidates must not be empty")

    if target_duration_ms is None:
        return candidates[0], None

    best_row = candidates[0]
    best_delta: int | None = None

    for row in candidates:
        candidate_duration = parse_int(row.get("duration_ms", ""))
        if candidate_duration is None:
            continue
        delta = abs(candidate_duration - target_duration_ms)
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_row = row

    if best_delta is None:
        return candidates[0], None
    return best_row, best_delta


def resolve_fuzzy_controls(raw_controls: dict[str, Any] | None) -> dict[str, Any]:
    defaults: dict[str, Any] = dict(DEFAULT_SEED_CONTROLS.get("fuzzy_matching") or {})
    if not isinstance(raw_controls, dict):
        return defaults
    controls = dict(defaults)
    controls["enabled"] = bool(raw_controls.get("enabled", defaults["enabled"]))
    for key in ("artist_threshold", "title_threshold", "combined_threshold"):
        try:
            value = float(raw_controls.get(key, defaults[key]))
        except (TypeError, ValueError):
            value = float(defaults[key])
        controls[key] = min(1.0, max(0.0, value))
    for key in ("max_duration_delta_ms", "max_artist_candidates"):
        try:
            value = int(raw_controls.get(key, defaults[key]))
        except (TypeError, ValueError):
            value = int(defaults[key])
        controls[key] = max(1, value)
    return controls


def fuzzy_find_candidate(
    *,
    title_key: str,
    artist_key: str,
    event_duration: int | None,
    by_artist: dict[str, list[dict[str, str]]],
    fuzzy_controls: dict[str, Any],
) -> tuple[dict[str, str] | None, int | None, float | None, float | None, float | None]:
    artist_keys = sorted(by_artist.keys())
    if not artist_keys:
        return None, None, None, None, None

    artist_matches: list[tuple[str, float]] = []
    artist_cutoff = float(fuzzy_controls["artist_threshold"])
    for candidate_artist_key in artist_keys:
        artist_score = float(fuzz.ratio(artist_key, candidate_artist_key)) / 100.0
        if artist_score >= artist_cutoff:
            artist_matches.append((candidate_artist_key, artist_score))

    if not artist_matches:
        return None, None, None, None, None

    artist_matches = sorted(
        artist_matches,
        key=lambda match: (-float(match[1]), str(match[0])),
    )[: int(fuzzy_controls["max_artist_candidates"])]

    deduped_candidates: dict[str, tuple[dict[str, str], float]] = {}
    for artist_match_key, artist_score in artist_matches:
        for candidate in by_artist.get(artist_match_key, []):
            ds001_id = (candidate.get("id") or "").strip()
            if not ds001_id:
                continue
            previous = deduped_candidates.get(ds001_id)
            if previous is None or artist_score > previous[1]:
                deduped_candidates[ds001_id] = (candidate, artist_score)

    best_choice: tuple[dict[str, str], int | None, float, float, float] | None = None
    best_sort_key: tuple[float, float, float, int, str] | None = None
    for ds001_id in sorted(deduped_candidates.keys()):
        candidate, artist_score = deduped_candidates[ds001_id]
        candidate_title_key = normalize_text(candidate.get("song", ""))
        if not candidate_title_key:
            continue

        title_score = float(fuzz.ratio(title_key, candidate_title_key)) / 100.0
        if title_score < fuzzy_controls["title_threshold"]:
            continue

        combined_score = (artist_score + title_score) / 2.0
        if combined_score < fuzzy_controls["combined_threshold"]:
            continue

        duration_delta: int | None = None
        candidate_duration = parse_int(candidate.get("duration_ms", ""))
        if event_duration is not None and candidate_duration is not None:
            duration_delta = abs(candidate_duration - event_duration)
            if duration_delta > fuzzy_controls["max_duration_delta_ms"]:
                continue

        duration_sort = duration_delta if duration_delta is not None else 10**12
        sort_key = (-combined_score, -title_score, -artist_score, duration_sort, ds001_id)
        if best_sort_key is None or sort_key < best_sort_key:
            best_sort_key = sort_key
            best_choice = (candidate, duration_delta, title_score, artist_score, combined_score)

    if best_choice is None:
        return None, None, None, None, None
    return best_choice
