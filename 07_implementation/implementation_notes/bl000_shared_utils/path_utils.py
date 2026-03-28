"""
Path utilities for consistent path resolution across implementation stages.

STANDALONE MODE: This module works in both repo and standalone contexts.
- In standalone: looks for implementation_notes directory and works relative to it
- In repo: can still use repo-relative paths if needed

Provides:
- impl_root(): Get the implementation_notes directory (works in standalone/repo)
- get_dataset_root(): Get music4all dataset path from env var IMPL_DATASET_ROOT or parameter
- Path construction helpers
"""

import os
from pathlib import Path


def impl_root(impl_root_override: str | None = None) -> Path:
    """
    Get the implementation_notes directory root.

    In standalone mode, searches for implementation_notes directory by walking up from this module.
    Can be overridden via impl_root_override parameter or IMPL_ROOT env var.

    Returns:
        Path to implementation_notes directory

    Raises:
        RuntimeError: If implementation_notes directory cannot be found
    """
    # Check for explicit override
    if impl_root_override:
        return Path(impl_root_override).resolve()

    # Check for env var
    if "IMPL_ROOT" in os.environ:
        return Path(os.environ["IMPL_ROOT"]).resolve()

    # Auto-detect: find implementation_notes directory by walking up from this module
    current = Path(__file__).resolve()

    # This module is at: implementation_notes/bl000_shared_utils/path_utils.py
    # So we can compute directly:
    # parents[0] = bl000_shared_utils
    # parents[1] = implementation_notes
    impl_notes = current.parents[1]

    # Verify it's actually named implementation_notes
    if impl_notes.name == "implementation_notes":
        return impl_notes

    # Fallback: search upward for implementation_notes directory
    search_dir = current.parent
    for _ in range(10):  # Search up to 10 levels
        if search_dir.name == "implementation_notes":
            return search_dir
        search_dir = search_dir.parent

    raise RuntimeError(
        f"Cannot find implementation_notes directory. "
        f"Set IMPL_ROOT env var or pass impl_root_override parameter. "
        f"(started from {current})"
    )


def get_dataset_root(dataset_root_override: str | None = None) -> Path:
    """
    Get the music4all dataset root directory.

    Priority:
    1. dataset_root_override parameter (if provided)
    2. IMPL_DATASET_ROOT env var
    3. Raises error

    Args:
        dataset_root_override: Explicit path to dataset root (overrides env var)

    Returns:
        Path to music4all dataset root

    Raises:
        RuntimeError: If dataset root not configured
    """
    if dataset_root_override:
        return Path(dataset_root_override).resolve()

    if "IMPL_DATASET_ROOT" in os.environ:
        return Path(os.environ["IMPL_DATASET_ROOT"]).resolve()

    raise RuntimeError(
        "Dataset root not configured. "
        "Set IMPL_DATASET_ROOT env var or pass dataset_root to functions that need it."
    )


def repo_root() -> Path:
    """
    Legacy: Get the thesis repository root directory.

    DEPRECATED for standalone mode. Only works in repo context where
    07_implementation/implementation_notes/ exists under thesis-main/.

    Returns:
        Path to thesis repository root
    """
    # Try the old path (3 parents up from this module)
    candidate = Path(__file__).resolve().parents[3]

    # Verify it exists and has expected structure
    if (candidate / "07_implementation" / "implementation_notes").exists():
        return candidate

    raise RuntimeError(
        "Cannot find repository root. "
        "Are you running in standalone mode? Use impl_root() instead of repo_root()."
    )


def impl_notes_root() -> Path:
    """
    Get the implementation_notes directory.

    Returns:
        Path to implementation_notes/
    """
    return impl_root()


def run_config_path() -> Path:
    """
    Get the path to the run_config module.

    Returns:
        Path to bl000_run_config/run_config_utils.py
    """
    return impl_root() / "bl000_run_config" / "run_config_utils.py"
