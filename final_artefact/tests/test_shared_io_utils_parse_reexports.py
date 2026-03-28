"""Compatibility tests for parse helper re-exports in shared_utils.io_utils."""

from shared_utils import io_utils, parsing


def test_parse_float_reexport_matches_parsing_function() -> None:
    assert io_utils.parse_float is parsing.parse_float


def test_parse_csv_labels_reexport_matches_parsing_function() -> None:
    assert io_utils.parse_csv_labels is parsing.parse_csv_labels
