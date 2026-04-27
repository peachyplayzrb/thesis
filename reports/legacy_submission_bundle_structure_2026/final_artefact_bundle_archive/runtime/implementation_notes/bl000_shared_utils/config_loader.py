"""
Configuration loading utilities for run_config_utils.py.

Centralizes the dynamic module loading logic that was duplicated across
BL-003, 004, 005, 006, 007, and 008.
"""

import importlib.util
from pathlib import Path
from typing import Any

from .path_utils import run_config_path


def load_run_config_utils_module() -> Any:
    """
    Dynamically load the run_config_utils module.
    
    This module is generated at runtime and cannot be imported normally.
    Uses importlib.util to load it from the bl000_run_config directory.
    
    Returns:
        The loaded run_config_utils module
        
    Raises:
        RuntimeError: If module cannot be loaded (missing file or loader error)
    """
    module_path: Path = run_config_path()
    
    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module
