"""BL-003 DS-001 matching helpers."""

from __future__ import annotations

from alignment.index_builder import build_ds001_indices
from alignment.match_pipeline import match_events
from alignment.text_matching import (
    choose_best_duration_match,
    first_artist,
    fuzzy_find_candidate,
    normalize_text,
    resolve_fuzzy_controls,
)
