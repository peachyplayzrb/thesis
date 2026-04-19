from __future__ import annotations

from orchestration.main import _build_execution_stage_order


def test_build_execution_stage_order_keeps_all_stages_without_refresh_seed() -> None:
    stage_order = ["BL-003", "BL-004", "BL-005"]

    result = _build_execution_stage_order(stage_order, refresh_seed=False)

    assert result == ["BL-003", "BL-004", "BL-005"]


def test_build_execution_stage_order_skips_bl003_when_refresh_seed_enabled() -> None:
    stage_order = ["BL-003", "BL-004", "BL-005"]

    result = _build_execution_stage_order(stage_order, refresh_seed=True)

    assert result == ["BL-004", "BL-005"]


def test_build_execution_stage_order_noop_when_bl003_absent() -> None:
    stage_order = ["BL-004", "BL-005"]

    result = _build_execution_stage_order(stage_order, refresh_seed=True)

    assert result == ["BL-004", "BL-005"]
