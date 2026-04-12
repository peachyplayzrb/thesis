"""
Shared utilities package for all implementation stages.

Centralizes common functionality that was previously duplicated across
BL-003 through BL-014, including:
- File I/O operations (JSON, CSV, hashing)
- Path resolution and environment variable parsing
- Configuration loading
- Shared constants and type definitions

Usage:
    from shared_utils import io_utils, config_loader, constants
    from shared_utils.path_utils import impl_root
    from shared_utils.types import RunConfigControls
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import artifact_registry as artifact_registry
    from . import config_loader as config_loader
    from . import constants as constants
    from . import env_utils as env_utils
    from . import hashing as hashing
    from . import io_utils as io_utils
    from . import parsing as parsing
    from . import path_utils as path_utils
    from . import report_utils as report_utils
    from . import run_config_runtime as run_config_runtime
    from . import stage_runtime_resolver as stage_runtime_resolver
    from . import stage_utils as stage_utils
    from . import types as types

__all__ = [
    "artifact_registry",
    "config_loader",
    "constants",
    "env_utils",
    "hashing",
    "io_utils",
    "parsing",
    "path_utils",
    "report_utils",
    "run_config_runtime",
    "stage_utils",
    "stage_runtime_resolver",
    "types",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
