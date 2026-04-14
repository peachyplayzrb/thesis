"""
Path helpers for finding the active `src/` tree and the files underneath it.

This works both in the full repo and in the standalone mentor bundle, which is
why the path resolution is a bit more careful than a simple relative join.
"""

import os
from pathlib import Path


def impl_root(impl_root_override: str | None = None) -> Path:
    """
    Return the active `src/` directory.

    I check an explicit override first, then an env var, and finally fall back
    to walking upward from this file so the same code works in bundle mode.
    """
    # Explicit override wins if the caller already knows the root.
    if impl_root_override:
        return Path(impl_root_override).resolve()

    # Environment override is the next-most explicit option.
    if "IMPL_ROOT" in os.environ:
        return Path(os.environ["IMPL_ROOT"]).resolve()

    # Otherwise infer it from this file location.
    current = Path(__file__).resolve()

    impl_notes = current.parents[1]

    if impl_notes.name == "src":
        return impl_notes

    # The direct assumption should hold, but keep a short upward search as backup.
    search_dir = current.parent
    for _ in range(10):
        if search_dir.name == "src":
            return search_dir
        search_dir = search_dir.parent

    raise RuntimeError(
        f"Cannot find src directory. "
        f"Set IMPL_ROOT env var or pass impl_root_override parameter. "
        f"(started from {current})"
    )


def get_dataset_root(dataset_root_override: str | None = None) -> Path:
    """Return the packaged `data_layer/outputs` directory, with optional override."""
    if dataset_root_override:
        return Path(dataset_root_override).resolve()
    return impl_root() / "data_layer" / "outputs"


def repo_root() -> Path:
    """
    Legacy helper for finding the thesis repo root.

    This only works in the full repo layout, so bundle code should use
    `impl_root()` instead.
    """
    # Keep the old repo-relative lookup for callers that still expect it.
    candidate = Path(__file__).resolve().parents[3]

    if (candidate / "07_implementation" / "implementation_notes").exists():
        return candidate

    raise RuntimeError(
        "Cannot find repository root. "
        "Are you running in standalone mode? Use impl_root() instead of repo_root()."
    )


def impl_notes_root() -> Path:
    """Return the same `src/` root as `impl_root()` for older callers."""
    return impl_root()


def run_config_path() -> Path:
    """Return the path to `run_config/run_config_utils.py`."""
    return impl_root() / "run_config" / "run_config_utils.py"
