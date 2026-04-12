"""Shared type coercion utilities unified from coerce_* and safe_* variants."""

from typing import Any, Mapping


def safe_float(value: object, default: float = 0.0) -> float:
    """Convert value to float, returning default on failure. Alias: coerce_float."""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def safe_int(value: object, default: int = 0) -> int:
    """Convert value to int, returning default on failure. Alias: coerce_int."""
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def coerce_float(value: object, default: float = 0.0) -> float:
    """Convert value to float, returning default on failure. Alias: safe_float."""
    if value is None:
        return default
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return default


def coerce_int(value: object, default: int = 0) -> int:
    """Convert value to int, returning default on failure. Alias: safe_int."""
    if value is None:
        return default
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return default


def coerce_dict(value: object) -> dict[str, object]:
    """Convert value to dict, returning empty dict on failure."""
    return dict(value) if isinstance(value, dict) else {}


def coerce_enum(value: object, valid: frozenset[str], default: str) -> str:
    """Convert value to enum member from valid set, returning default on failure."""
    normalized = str(value or default).strip().lower()
    return normalized if normalized in valid else default


def parse_float(value: str) -> float | None:
    """Parse string to float, returning None if empty or invalid."""
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_csv_labels(raw_value: str) -> list[str]:
    """Parse comma-separated labels string into deduplicated list of lowercase tokens."""
    if not raw_value:
        return []
    labels: list[str] = []
    seen: set[str] = set()
    for piece in raw_value.split(","):
        label = piece.strip().lower()
        if not label or label in seen:
            continue
        seen.add(label)
        labels.append(label)
    return labels


# Aliases for backwards compatibility (safe_* -> coerce_*)
coerce_float = coerce_float
coerce_int = coerce_int
