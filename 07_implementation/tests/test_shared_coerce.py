from __future__ import annotations

from shared_utils.coerce import clamp, to_float, to_int, to_mapping, to_string_list


def test_clamp_bounds() -> None:
    assert clamp(-1.0) == 0.0
    assert clamp(0.25) == 0.25
    assert clamp(3.0) == 1.0


def test_to_float_uses_string_path() -> None:
    assert to_float("2.5", 0.0) == 2.5
    assert to_float(3, 0.0) == 3.0
    assert to_float(None, 1.5) == 1.5


def test_to_int_uses_string_path() -> None:
    assert to_int("7", 0) == 7
    assert to_int(4, 0) == 4
    assert to_int("bad", 9) == 9


def test_to_mapping_normalizes_keys() -> None:
    raw = {1: "a", "b": 2}
    assert to_mapping(raw) == {"1": "a", "b": 2}
    assert to_mapping(None) == {}


def test_to_string_list_options() -> None:
    assert to_string_list(["a", 2, ""], drop_empty=False) == ["a", "2", ""]
    assert to_string_list(["a", 2, ""], drop_empty=True) == ["a", "2"]
    assert to_string_list(("x", "y"), allow_tuple=False) == []
    assert to_string_list(("x", "y"), allow_tuple=True) == ["x", "y"]
