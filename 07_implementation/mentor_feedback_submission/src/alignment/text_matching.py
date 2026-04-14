"""Compatibility shim for the BL-003 text helpers I moved into shared_utils."""
from __future__ import annotations

from shared_utils import text_matching as _shared_text_matching
from shared_utils.text_matching import (
    choose_best_duration_match,
    first_artist,
    fuzzy_find_candidate,
    normalize_text,
    resolve_fuzzy_controls,
    split_artists,
)

# Keep this alias so older tests and monkeypatches still hit the shared runtime implementation.
fuzz = _shared_text_matching.fuzz
