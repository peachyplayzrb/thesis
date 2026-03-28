"""
Shared stage helper utilities.

These helpers centralize small cross-stage behaviors that were previously
redefined in multiple stage entrypoints.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def relpath(path: Path, root: Path) -> str:
    """Return a POSIX-style relative path from root to path."""
    return path.relative_to(root).as_posix()


def safe_relpath(path: Path, root: Path) -> str:
    """Return a relative POSIX path where possible, falling back to the raw path."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def load_required_json(path: Path, *, label: str, stage_label: str) -> dict[str, Any] | list[Any]:
    """Load a required JSON file and raise a stage-specific RuntimeError on failure."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"{stage_label} could not read {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{stage_label} could not parse {label} as valid JSON: {path}") from exc


def load_required_json_object(path: Path, *, label: str, stage_label: str) -> dict[str, Any]:
    """Load a required JSON object and validate that the decoded payload is a dict."""
    payload = load_required_json(path, label=label, stage_label=stage_label)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{stage_label} expected {label} to be a JSON object: {path}")
    return payload


def ensure_required_keys(
    payload: Mapping[str, Any],
    keys: list[str],
    *,
    label: str,
    stage_label: str,
) -> None:
    """Validate that a payload contains all required top-level keys."""
    missing = [key for key in keys if key not in payload]
    if missing:
        raise RuntimeError(f"{stage_label} {label} missing required keys: {missing}")


def ensure_paths_exist(
    paths: list[Path],
    *,
    stage_label: str,
    label: str = "input artifact(s)",
    root: Path | None = None,
) -> None:
    """Validate that a list of required file paths exists."""
    missing = [safe_relpath(path, root) if root is not None else str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"{stage_label} missing required {label}: {missing}")


def ensure_named_paths_exist(
    paths: Mapping[str, Path],
    *,
    stage_label: str,
    label: str = "input artifacts",
) -> None:
    """Validate that a mapping of named required paths exists."""
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        details = ", ".join(f"{name}={paths[name]}" for name in missing)
        raise FileNotFoundError(f"{stage_label} missing required {label}: {details}")
