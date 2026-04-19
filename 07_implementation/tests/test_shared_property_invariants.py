from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from src.shared_utils.coerce import clamp
from src.shared_utils.coerce import to_int
from src.shared_utils.parsing import parse_csv_labels
from src.shared_utils.parsing import parse_float


@given(
    value=st.floats(allow_nan=False, allow_infinity=False, width=32),
    low=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    high=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_clamp_stays_within_closed_interval(value: float, low: float, high: float) -> None:
    lo = min(low, high)
    hi = max(low, high)

    bounded = clamp(value, lo, hi)

    assert lo <= bounded <= hi
    assert clamp(bounded, lo, hi) == bounded


@given(value=st.integers(min_value=-1_000_000, max_value=1_000_000))
def test_to_int_round_trip_for_integer_strings(value: int) -> None:
    assert to_int(str(value), default=999) == value


@given(value=st.floats(allow_nan=False, allow_infinity=False, width=32))
def test_parse_float_accepts_valid_float_strings(value: float) -> None:
    text = str(value)
    parsed = parse_float(text)

    assert parsed is not None
    assert parsed == float(text)


@given(values=st.lists(st.text(max_size=20), max_size=25))
def test_parse_csv_labels_outputs_lowercase_unique_tokens(values: list[str]) -> None:
    raw = ",".join(values)
    labels = parse_csv_labels(raw)

    assert labels == list(dict.fromkeys(labels))
    assert all(label == label.strip() for label in labels)
    assert all(label == label.lower() for label in labels)
    assert all(label for label in labels)
