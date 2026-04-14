"""
Helpers for loading the run-config module from disk.

The config utilities need to work both inside the repo and inside the bundle,
so I load them dynamically instead of relying on a normal import.
"""

import importlib.util
from pathlib import Path
from typing import Any

from .path_utils import run_config_path


def load_run_config_utils_module() -> Any:
    """
    Load `run_config_utils.py` directly from its file path.

    I do it this way because the active config module is resolved at runtime, so
    a normal import is less reliable here than loading the file explicitly.
    """
    module_path: Path = run_config_path()

    spec = importlib.util.spec_from_file_location("run_config_utils", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load run-config utilities from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
