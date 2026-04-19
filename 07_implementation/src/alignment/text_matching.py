"""Compatibility shim for BL-003 text helpers now hosted in shared_utils."""
from __future__ import annotations

from shared_utils import text_matching as _shared_text_matching
from shared_utils.text_matching import choose_best_duration_match as choose_best_duration_match
from shared_utils.text_matching import first_artist as first_artist
from shared_utils.text_matching import fuzzy_find_candidate as fuzzy_find_candidate
from shared_utils.text_matching import normalize_text as normalize_text
from shared_utils.text_matching import resolve_fuzzy_controls as resolve_fuzzy_controls
from shared_utils.text_matching import split_artists as split_artists

# Keep this module-level alias so existing monkeypatches on alignment.text_matching.fuzz
# still affect the shared implementation used at runtime.
fuzz = _shared_text_matching.fuzz
