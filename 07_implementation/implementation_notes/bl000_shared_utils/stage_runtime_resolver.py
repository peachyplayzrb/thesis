"""
Shared stage runtime resolution helpers.

Centralizes stage selection behavior used by orchestration and API layers.
"""

from __future__ import annotations

from typing import Any, Dict, List


def resolve_stage_selection(
    config: Dict[str, Any],
    stage_specs: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Resolve and validate stage selection while preserving canonical order."""
    selected_raw = config.get("stage_ids", []) if isinstance(config, dict) else []
    all_ids = [spec["stage_id"] for spec in stage_specs]

    if not selected_raw:
        return [dict(spec) for spec in stage_specs]

    if not isinstance(selected_raw, list):
        raise RuntimeError("stage_ids must be an array of stage identifiers.")

    selected_set = {str(item).strip().lower() for item in selected_raw if str(item).strip()}
    if not selected_set:
        raise RuntimeError("At least one valid stage id is required.")

    unknown = sorted(selected_set.difference(all_ids))
    if unknown:
        raise RuntimeError(f"Unknown stage_ids: {', '.join(unknown)}")

    return [dict(spec) for spec in stage_specs if spec["stage_id"] in selected_set]
