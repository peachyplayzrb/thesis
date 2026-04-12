"""Tests for shared normalization helpers in shared_utils.parsing."""

from alignment.text_matching import normalize_text as alignment_normalize_text
from shared_utils.parsing import (
    normalize_ascii_text,
    normalize_candidate_row,
    normalize_text,
)


def test_normalize_text_collapses_whitespace_and_lowercases() -> None:
    assert normalize_text("  A   B   C  ") == "a b c"


def test_normalize_text_preserves_case_when_requested() -> None:
    assert normalize_text("  A   B  ", lowercase=False) == "A B"


def test_normalize_ascii_text_strips_accents_and_punctuation() -> None:
    assert normalize_ascii_text("Björk & Röyksopp!") == "bjork royksopp"


def test_alignment_wrapper_uses_shared_ascii_normalization() -> None:
    sample = "Rock & Roll!"
    assert alignment_normalize_text(sample) == normalize_ascii_text(sample)


def test_normalize_candidate_row_uses_cid_as_track_id_fallback() -> None:
    row = {"cid": "03Oc9WeMEmyLLQbj", "artist": "Shakira"}

    normalized = normalize_candidate_row(row)

    assert normalized["track_id"] == "03Oc9WeMEmyLLQbj"
