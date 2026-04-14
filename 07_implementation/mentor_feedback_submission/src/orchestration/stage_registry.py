"""Canonical stage and artifact constants used by BL-013 orchestration."""
from __future__ import annotations

from shared_utils.artifact_registry import (
    bl013_bl003_script_relpath,
    bl013_bl003_summary_relpath,
    bl013_default_stage_order,
    bl013_stage_script_map,
    bl013_stable_artifact_relpaths,
)

STAGE_SCRIPT_MAP: dict[str, str] = bl013_stage_script_map()

BL003_SCRIPT: str = bl013_bl003_script_relpath()

DEFAULT_STAGE_ORDER: list[str] = bl013_default_stage_order()

# These deterministic files are hashed to support repeatability checks.
STABLE_ARTIFACTS: dict[str, str] = bl013_stable_artifact_relpaths()

BL003_SUMMARY_PATH: str = bl013_bl003_summary_relpath()

SUMMARY_NOTES: dict[str, str] = {
    "purpose": "Lightweight wrapper to run BL-003..BL-009 scripts in one command.",
    "repeatability_check_guidance": "Compare stable_artifact_hashes between repeated runs under unchanged inputs/config.",
}
