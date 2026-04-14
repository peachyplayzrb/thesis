"""Small coercion helpers for values coming from env vars, JSON, or loose dicts."""

from __future__ import annotations


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a float into the inclusive range between low and high."""
    return max(low, min(high, value))


def to_float(value: object, default: float = 0.0) -> float:
    """Try to coerce a value to float and fall back to the default if it fails."""
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def to_int(value: object, default: int = 0) -> int:
    """Try to coerce a value to int and fall back to the default if it fails."""
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def to_mapping(value: object) -> dict[str, object]:
    """Return a string-key dict when the input is mapping-like, otherwise empty."""
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def to_string_list(
    value: object,
    *,
    allow_tuple: bool = False,
    drop_empty: bool = False,
) -> list[str]:
    """Turn list-like values into `list[str]`, with optional empty-value filtering."""
    allowed_types: tuple[type, ...] = (list, tuple) if allow_tuple else (list,)
    if not isinstance(value, allowed_types):
        return []

    items = [str(item) for item in value]
    if not drop_empty:
        return items
    return [item for item in items if item]
