"""Text normalization and candidate selection helpers for BL-003 matching."""
from __future__ import annotations

from difflib import SequenceMatcher
from importlib import import_module
from typing import Any

from alignment.constants import ARTIST_NAME_DELIMITERS

from shared_utils.constants import DEFAULT_SEED_CONTROLS
from shared_utils.parsing import normalize_ascii_text, parse_int, safe_float


def _compute_ratio(left: str, right: str) -> float:
    try:
        fuzz_module = import_module("rapidfuzz.fuzz")
    except ModuleNotFoundError:
        return SequenceMatcher(None, left, right).ratio() * 100.0
    ratio_fn = getattr(fuzz_module, "ratio", None)
    if callable(ratio_fn):
        return safe_float(ratio_fn(left, right))
    return SequenceMatcher(None, left, right).ratio() * 100.0


class fuzz:
    @staticmethod
    def ratio(left: str, right: str) -> float:
        return _compute_ratio(left, right)


def normalize_text(value: str) -> str:
    """Normalise a string to ASCII lower-case tokens for fuzzy key comparison."""
    return normalize_ascii_text(value)


def first_artist(artist_names: str) -> str:
    """Return the primary artist from a pipe-, semicolon-, or comma-separated string."""
    for delimiter in ARTIST_NAME_DELIMITERS:
        if delimiter in artist_names:
            return artist_names.split(delimiter, 1)[0].strip()
    return artist_names.strip()


def split_artists(artist_names: str) -> list[str]:
    """Return ordered unique artist tokens from a multi-artist string."""
    flattened = artist_names
    for delimiter in ARTIST_NAME_DELIMITERS:
        flattened = flattened.replace(delimiter, "|")
    artists: list[str] = []
    seen: set[str] = set()
    for token in flattened.split("|"):
        artist = token.strip()
        key = artist.lower()
        if not artist or key in seen:
            continue
        seen.add(key)
        artists.append(artist)
    return artists


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
    for key in (
        "enable_album_scoring",
        "enable_secondary_artist_retry",
        "enable_relaxed_second_pass",
        "emit_fuzzy_diagnostics",
    ):
        controls[key] = bool(raw_controls.get(key, defaults.get(key, False)))
    for key in (
        "relaxed_second_pass_artist_threshold",
        "relaxed_second_pass_title_threshold",
        "relaxed_second_pass_combined_threshold",
    ):
        try:
            value = float(raw_controls.get(key, defaults.get(key, 0.8)))
        except (TypeError, ValueError):
            value = float(defaults.get(key, 0.8))
        controls[key] = min(1.0, max(0.0, value))
    return controls


def fuzzy_find_candidate(
    *,
    title_key: str,
    artist_key: str,
    event_duration: int | None,
    by_artist: dict[str, list[dict[str, str]]],
    fuzzy_controls: dict[str, Any],
    album_key: str = "",
) -> tuple[dict[str, str] | None, int | None, float | None, float | None, float | None, dict[str, Any]]:
    artist_keys = sorted(by_artist.keys())
    if not artist_keys:
        return None, None, None, None, None, {
            "album_score": None,
            "artist_match_count": 0,
            "candidate_count_after_artist_filter": 0,
            "failure_reason": "artist_threshold",
        }

    artist_matches: list[tuple[str, float]] = []
    artist_cutoff = float(fuzzy_controls["artist_threshold"])
    for candidate_artist_key in artist_keys:
        artist_score = fuzz.ratio(artist_key, candidate_artist_key) / 100.0
        if artist_score >= artist_cutoff:
            artist_matches.append((candidate_artist_key, artist_score))

    if not artist_matches:
        return None, None, None, None, None, {
            "album_score": None,
            "artist_match_count": 0,
            "candidate_count_after_artist_filter": 0,
            "failure_reason": "artist_threshold",
        }

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
    best_sort_key: tuple[float, float, float, float, int, str] | None = None
    best_album_score: float | None = None
    saw_title_threshold_failure = False
    saw_combined_threshold_failure = False
    saw_duration_rejection = False
    for ds001_id in sorted(deduped_candidates.keys()):
        candidate, artist_score = deduped_candidates[ds001_id]
        candidate_title_key = normalize_text(candidate.get("song", ""))
        if not candidate_title_key:
            continue

        title_score = fuzz.ratio(title_key, candidate_title_key) / 100.0
        if title_score < fuzzy_controls["title_threshold"]:
            saw_title_threshold_failure = True
            continue

        candidate_album_key = normalize_text(candidate.get("album_name", ""))
        if bool(fuzzy_controls.get("enable_album_scoring", True)) and album_key and candidate_album_key:
            album_score = fuzz.ratio(album_key, candidate_album_key) / 100.0
            combined_score = (artist_score + title_score + album_score) / 3.0
        else:
            album_score = 0.0
            combined_score = (artist_score + title_score) / 2.0

        if combined_score < fuzzy_controls["combined_threshold"]:
            saw_combined_threshold_failure = True
            continue

        duration_delta: int | None = None
        candidate_duration = parse_int(candidate.get("duration_ms", ""))
        if event_duration is not None and candidate_duration is not None:
            duration_delta = abs(candidate_duration - event_duration)
            if duration_delta > fuzzy_controls["max_duration_delta_ms"]:
                saw_duration_rejection = True
                continue

        duration_sort = duration_delta if duration_delta is not None else 10**12
        sort_key = (-combined_score, -title_score, -artist_score, -album_score, duration_sort, ds001_id)
        if best_sort_key is None or sort_key < best_sort_key:
            best_sort_key = sort_key
            best_choice = (candidate, duration_delta, title_score, artist_score, combined_score)
            best_album_score = album_score

    if best_choice is None:
        failure_reason = "combined_threshold"
        if saw_duration_rejection:
            failure_reason = "duration_rejected"
        elif saw_combined_threshold_failure:
            failure_reason = "combined_threshold"
        elif saw_title_threshold_failure:
            failure_reason = "title_threshold"
        return None, None, None, None, None, {
            "album_score": None,
            "artist_match_count": len(artist_matches),
            "candidate_count_after_artist_filter": len(deduped_candidates),
            "failure_reason": failure_reason,
        }
    return best_choice[0], best_choice[1], best_choice[2], best_choice[3], best_choice[4], {
        "album_score": best_album_score,
        "artist_match_count": len(artist_matches),
        "candidate_count_after_artist_filter": len(deduped_candidates),
        "failure_reason": "matched",
    }
