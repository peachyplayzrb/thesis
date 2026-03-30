"""BL-011 scenario filtering utilities.

Applies runtime ``scenario_policy`` to the scenario list consumed by ``main.py``.

Phase 2 capability:
    Scenario filtering by ``enabled_scenario_ids``.  Users can limit which
    of the built-in scenarios execute by setting this list in run-config.

Phase 3 extension point:
    When ``scenario_definitions`` is non-empty, patch-based scenarios loaded
    from config will be used to override or supplement the built-in set.
    That wiring is handled in the Phase 3 rule-engine refactor.
"""
from __future__ import annotations

from typing import Any


def filter_scenarios_by_policy(
    scenarios: list[dict[str, Any]],
    scenario_policy: dict[str, Any],
) -> list[dict[str, Any]]:
    """Filter the scenario list according to ``scenario_policy.enabled_scenario_ids``.

    Rules:
    - ``["all"]`` or missing → return all scenarios unchanged.
    - Explicit list → keep only scenarios whose ``scenario_id`` is in the
      list; ``"baseline"`` is always retained because comparisons require it.
    - Safety guard: if filtering produces only baseline (no variants), the
      full list is returned to avoid an unrunnable scenario set.

    Args:
        scenarios: Full built scenario list including baseline.
        scenario_policy: Policy dict from ``resolve_bl011_scenario_policy``.

    Returns:
        Filtered scenario list, always containing at least baseline + one variant.
    """
    enabled_ids = list(scenario_policy.get("enabled_scenario_ids") or ["all"])
    if "all" in enabled_ids:
        return scenarios

    enabled_set = set(enabled_ids)
    filtered = [
        s for s in scenarios
        if s["scenario_id"] == "baseline" or s["scenario_id"] in enabled_set
    ]
    # Guard: never return a list with only baseline — that produces an empty
    # comparison matrix and a trivially passing evaluation.
    if len(filtered) <= 1:
        return scenarios

    return filtered
