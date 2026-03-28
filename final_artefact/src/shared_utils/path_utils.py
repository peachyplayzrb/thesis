"""
Path utilities for consistent path resolution across implementation stages.

STANDALONE MODE: This module works in both repo and standalone contexts.
- In standalone: looks for src directory and works relative to it
- In repo: can still use repo-relative paths if needed

Provides:
- impl_root(): Get the src directory (works in standalone/repo)
- get_dataset_root(): Get the packaged data-layer outputs directory
- Path construction helpers
"""

import os
from pathlib import Path


def impl_root(impl_root_override: str | None = None) -> Path:
    """
    Get the src directory root.

    In standalone mode, searches for src directory by walking up from this module.
    Can be overridden via impl_root_override parameter or IMPL_ROOT env var.

    Returns:
        Path to src directory

    Raises:
        RuntimeError: If src directory cannot be found
    """
    # Check for explicit override
    if impl_root_override:
        return Path(impl_root_override).resolve()

    # Check for env var
    if "IMPL_ROOT" in os.environ:
        return Path(os.environ["IMPL_ROOT"]).resolve()

    # Auto-detect: find src directory by walking up from this module
    current = Path(__file__).resolve()

    # This module is at: src/shared_utils/path_utils.py
    # So we can compute directly:
    # parents[0] = shared_utils
    # parents[1] = src
    impl_notes = current.parents[1]

    # Verify it's actually named src
    if impl_notes.name == "src":
        return impl_notes

    # Fallback: search upward for src directory
    search_dir = current.parent
    for _ in range(10):  # Search up to 10 levels
        if search_dir.name == "src":
            return search_dir
        search_dir = search_dir.parent

    raise RuntimeError(
        f"Cannot find src directory. "
        f"Set IMPL_ROOT env var or pass impl_root_override parameter. "
        f"(started from {current})"
    )


def get_dataset_root(dataset_root_override: str | None = None) -> Path:
    """
    Get the packaged data-layer outputs directory.

    Priority:
    1. dataset_root_override parameter (if provided)
    2. Default packaged data-layer outputs directory

    Args:
        dataset_root_override: Explicit path override

    Returns:
        Path to data_layer/outputs
    """
    if dataset_root_override:
        return Path(dataset_root_override).resolve()
    return impl_root() / "data_layer" / "outputs"


def repo_root() -> Path:
    """
    Legacy: Get the thesis repository root directory.

    DEPRECATED for standalone mode. Only works in repo context where
     exists under thesis-main/.

    Returns:
        Path to thesis repository root
    """
    # Try the old path (3 parents up from this module)
    candidate = Path(__file__).resolve().parents[3]

    # Verify it exists and has expected repo structure
    if (candidate / "07_implementation" / "implementation_notes").exists():
        return candidate

    raise RuntimeError(
        "Cannot find repository root. "
        "Are you running in standalone mode? Use impl_root() instead of repo_root()."
    )


def impl_notes_root() -> Path:
    """
    Get the src directory.

    Returns:
        Path to src/
    """
    return impl_root()


def run_config_path() -> Path:
    """
    Get the path to the run_config module.

    Returns:
        Path to run_config/run_config_utils.py
    """
    return impl_root() / "run_config" / "run_config_utils.py"
