"""
Environment variable parsing utilities.

Provides type-safe functions for reading environment variables with defaults.
"""

import os
from pathlib import Path


def env_int(name: str, default: int) -> int:
    """
    Get an environment variable as an int, with a default.

    Returns the default if:
    - Variable is not set
    - Variable is empty string
    - Variable cannot be parsed as int

    Args:
        name: Environment variable name
        default: Default value if variable not set or invalid

    Returns:
        Int value from environment or default
    """
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    """
    Get an environment variable as a float, with a default.

    Returns the default if:
    - Variable is not set
    - Variable is empty string
    - Variable cannot be parsed as float

    Args:
        name: Environment variable name
        default: Default value if variable not set or invalid

    Returns:
        Float value from environment or default
    """
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def env_str(name: str, default: str) -> str:
    """
    Get an environment variable as a string, with a default.

    Returns the default if:
    - Variable is not set
    - Variable is empty string (after stripping whitespace)

    Args:
        name: Environment variable name
        default: Default value if variable not set or empty

    Returns:
        String value from environment or default
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = str(raw).strip()
    return value if value else default


def env_bool(name: str, default: bool) -> bool:
    """
    Get an environment variable as a boolean, with a default.

    Truthy values: 1, true, yes, on
    Falsy values:  0, false, no, off

    Args:
        name: Environment variable name
        default: Default value if variable not set or invalid

    Returns:
        Bool value from environment or default
    """
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
    """
    Get an environment variable as a Path, with a default.

    Returns the default if the variable is not set or is empty.
    """
    raw = env_str(name, "")
    if raw:
        return Path(raw)
    return default
