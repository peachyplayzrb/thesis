"""Scenario-filtering helpers for BL-011 runtime policy controls."""
from __future__ import annotations

from typing import Any


def filter_scenarios_by_policy(
    scenarios: list[dict[str, Any]],
    scenario_policy: dict[str, Any],
) -> list[dict[str, Any]]:
    """Filter scenarios by enabled IDs while always retaining a runnable baseline set."""
    enabled_ids = list(scenario_policy.get("enabled_scenario_ids") or ["all"])
    if "all" in enabled_ids:
        return scenarios

    enabled_set = set(enabled_ids)
    filtered = [
        s for s in scenarios
        if s["scenario_id"] == "baseline" or s["scenario_id"] in enabled_set
    ]
    # Guard against returning only baseline, which would produce a trivial pass.
    if len(filtered) <= 1:
        return scenarios

    return filtered
