"""Shared path resolution utilities consolidated from all stages."""

import os
from pathlib import Path


def impl_root(impl_root_override: str | None = None) -> Path:
    """Resolve implementation root directory from override, IMPL_ROOT env var, or file location."""
    if impl_root_override:
        return Path(impl_root_override).resolve()
    env_root = os.environ.get("IMPL_ROOT")
    if env_root:
        return Path(env_root).resolve()
    # Go up 2 levels from this file's parent: shared/ -> src/ -> repo root
    return Path(__file__).resolve().parents[2]


def stage_relpath(path: Path, root: Path) -> str:
    """Get relative path from root for display purposes."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)
