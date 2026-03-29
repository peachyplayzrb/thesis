"""Runtime control resolution for BL-011 controllability."""
from __future__ import annotations

import os

from shared_utils.config_loader import load_run_config_utils_module


def resolve_bl011_runtime_controls() -> dict[str, object]:
    rc_utils = load_run_config_utils_module()
    run_config_path: str | None = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    controls: dict[str, object] = {
        "config_source": "run_config" if run_config_path else "defaults",
        "run_config_path": run_config_path,
        **rc_utils.resolve_bl011_controls(run_config_path),
    }
    scenario_policy, scenario_definitions = rc_utils.resolve_bl011_scenario_policy(run_config_path)
    controls["scenario_policy"] = scenario_policy
    controls["scenario_definitions"] = scenario_definitions
    return controls
