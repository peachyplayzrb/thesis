"""
Path utilities for consistent path resolution across implementation stages.

Provides:
- repo_root(): Get the thesis repository root directory
- Path construction helpers
"""

from pathlib import Path


def repo_root() -> Path:
    """
    Get the thesis repository root directory.
    
    Computes based on the location of this module:
    - This module: bl000_shared_utils/path_utils.py
    - Parents: [0]=bl000_shared_utils, [1]=implementation_notes, [2]=07_implementation, [3]=thesis_root
    
    Returns:
        Path to the thesis repository root directory
    """
    return Path(__file__).resolve().parents[3]


def impl_notes_root() -> Path:
    """
    Get the implementation_notes directory.
    
    Returns:
        Path to 07_implementation/implementation_notes/
    """
    return repo_root() / "07_implementation" / "implementation_notes"


def run_config_path() -> Path:
    """
    Get the path to the run_config module.
    
    Returns:
        Path to bl000_run_config/run_config_utils.py
    """
    return impl_notes_root() / "bl000_run_config" / "run_config_utils.py"
