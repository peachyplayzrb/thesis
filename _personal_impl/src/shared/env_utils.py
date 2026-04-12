"""Shared environment variable parsing utilities consolidated from all stages."""

import os
from pathlib import Path


def env_str(name: str, default: str = "") -> str:
    """Get environment variable as string, return default if empty/missing."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = str(raw).strip()
    return value if value else default


def env_int(name: str, default: int = 0) -> int:
    """Get environment variable as integer, return default on failure."""
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def env_float(name: str, default: float = 0.0) -> float:
    """Get environment variable as float, return default on failure."""
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def env_bool(name: str, default: bool = False) -> bool:
    """Get environment variable as boolean, return default on unparseable value."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    token = str(raw).strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return default


def env_path(name: str, default: Path | None = None) -> Path:
    """Get environment variable as Path, return default if empty/missing."""
    raw = os.environ.get(name)
    if raw is None:
        return default if default is not None else Path(".")
    value = str(raw).strip()
    return Path(value) if value else (default if default is not None else Path("."))
