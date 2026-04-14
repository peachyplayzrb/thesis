"""
Helpers for reading environment variables without having to repeat the same
fallback logic in every stage.
"""

import os
from pathlib import Path


def env_int(name: str, default: int) -> int:
    """Read an env var as an int, using the default if it is missing or invalid."""
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    """Read an env var as a float, using the default if it is missing or invalid."""
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def env_str(name: str, default: str) -> str:
    """Read an env var as a string, falling back when it is missing or blank."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = str(raw).strip()
    return value if value else default


def env_bool(name: str, default: bool) -> bool:
    """Read an env var as a bool using the usual true/false string variants."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    token = str(raw).strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return default


def coerce_int(value: object, default: int) -> int:
    """Safely coerce any value to int, falling back to default."""
    if value is None:
        return default
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return default


def coerce_float(value: object, default: float) -> float:
    """Safely coerce any value to float, falling back to default."""
    if value is None:
        return default
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return default


def coerce_dict(value: object) -> dict[str, object]:
    """Safely coerce a value to dict, returning empty dict on failure."""
    return dict(value) if isinstance(value, dict) else {}


def coerce_enum(value: object, valid: frozenset[str], default: str) -> str:
    """Validate a string value against a set of allowed values."""
    normalized = str(value or default).strip().lower()
    return normalized if normalized in valid else default


def env_path(name: str, default: Path) -> Path:
    """Read an env var as a path, using the default when it is missing or blank."""
    raw = env_str(name, "")
    if raw:
        return Path(raw)
    return default
