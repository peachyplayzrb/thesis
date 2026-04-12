"""Compatibility shim for BL-003 text helpers now hosted in shared_utils."""
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

# Keep this module-level alias so existing monkeypatches on alignment.text_matching.fuzz
# still affect the shared implementation used at runtime.
fuzz = _shared_text_matching.fuzz
