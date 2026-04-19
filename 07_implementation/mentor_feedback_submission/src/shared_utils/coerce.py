"""Shared coercion helpers for stage/runtime surfaces."""

from __future__ import annotations


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a float value to a bounded inclusive range."""
    return max(low, min(high, value))


def to_float(value: object, default: float = 0.0) -> float:
    """Parse a float using the stage-safe string conversion pattern."""
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def to_int(value: object, default: int = 0) -> int:
    """Parse an int using the stage-safe string conversion pattern."""
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def to_mapping(value: object) -> dict[str, object]:
    """Normalize mapping-like values to string-key dictionaries."""
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def to_string_list(
    value: object,
    *,
    allow_tuple: bool = False,
    drop_empty: bool = False,
) -> list[str]:
    """Normalize list/tuple values to list[str] with optional empty filtering."""
    allowed_types: tuple[type, ...] = (list, tuple) if allow_tuple else (list,)
    if not isinstance(value, allowed_types):
        return []

    items = [str(item) for item in value]
    if not drop_empty:
        return items
    return [item for item in items if item]
