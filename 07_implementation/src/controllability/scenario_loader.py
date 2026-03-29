"""BL-011 scenario loading and filtering.

Bridges the run-config ``scenario_policy`` and ``scenario_definitions`` blocks
into the runtime scenario list consumed by ``main.py``.

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


def _load_rc_utils() -> Any:
    from shared_utils.config_loader import load_run_config_utils_module
    return load_run_config_utils_module()


def load_scenario_policy(run_config_path: str | None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load scenario_policy and scenario_definitions from run config.

    Args:
        run_config_path: Path to run-config JSON, or None to use defaults.

    Returns:
        (scenario_policy, scenario_definitions)
        ``scenario_policy`` has keys: enabled_scenario_ids, repeat_count,
            stage_scope, comparison_mode.
        ``scenario_definitions`` is the list of definition dicts from config
            (empty list when not provided — built-in fallback applies).
    """
    rc_utils = _load_rc_utils()
    return rc_utils.resolve_bl011_scenario_policy(run_config_path)


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
