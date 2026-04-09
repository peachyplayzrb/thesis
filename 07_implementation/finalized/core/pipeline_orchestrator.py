from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from core.app_config import AppConfig
from core import events as ev

if TYPE_CHECKING:
    from core.observability import EventPublisher
    from core.stage_base import StageRegistry


@dataclass(frozen=True)
class StageInput:
    stage_id: str
    controls: dict[str, Any]
    secrets: dict[str, Any]


@dataclass(frozen=True)
class StageResult:
    stage_id: str
    status: str                  # "pass" | "fail"
    elapsed_seconds: float
    output: dict[str, Any]       # stage-specific artifacts/data
    error: str | None = None     # populated on failure


@dataclass(frozen=True)
class OrchestrationPlan:
    stage_inputs: list[StageInput]
    continue_on_error: bool


class PipelineOrchestrator:
    """Build stage-scoped inputs from one validated AppConfig."""

    def __init__(
        self,
        config: AppConfig,
        publisher: "EventPublisher | None" = None,
        run_id: str = "",
    ) -> None:
        self._config = config
        self._publisher = publisher
        self._run_id = run_id

    def _emit(self, event_type: str, message: str, stage_id: str | None = None, **details: Any) -> None:
        if self._publisher is not None:
            self._publisher.publish(
                ev.make_event(
                    event_type,
                    self._run_id,
                    message,
                    stage_id=stage_id,
                    details=details or None,
                )
            )

    def build_plan(self) -> OrchestrationPlan:
        stage_order = self._config.stage_order()
        self._emit(ev.PLAN_BUILD_STARTED, f"Building plan for {len(stage_order)} stages")

        stage_inputs: list[StageInput] = []
        shared_secrets = dict(self._config.secrets)

        for stage_id in stage_order:
            controls = self._config.controls_for(stage_id)
            stage_inputs.append(
                StageInput(
                    stage_id=stage_id,
                    controls=controls,
                    secrets=shared_secrets,
                )
            )
            self._emit(
                ev.STAGE_PLANNED,
                f"controls={len(controls)} secrets={len(shared_secrets)}",
                stage_id=stage_id,
            )

        plan = OrchestrationPlan(
            stage_inputs=stage_inputs,
            continue_on_error=self._config.continue_on_error(),
        )
        self._emit(ev.PLAN_BUILD_SUCCEEDED, f"Plan ready: {len(stage_inputs)} stages")
        return plan

    def execute(self, registry: "StageRegistry") -> list[StageResult]:
        """Run each planned stage through the registry and collect results."""
        plan = self.build_plan()
        results: list[StageResult] = []

        for stage_input in plan.stage_inputs:
            sid = stage_input.stage_id
            stage = registry.get(sid)

            if stage is None:
                result = StageResult(
                    stage_id=sid,
                    status="fail",
                    elapsed_seconds=0.0,
                    output={},
                    error="stage not yet implemented",
                )
                self._emit(ev.STAGE_STARTED, "Executing stage", stage_id=sid)
                self._emit(ev.STAGE_FAILED, result.error or "", stage_id=sid)
            else:
                self._emit(ev.STAGE_STARTED, "Executing stage", stage_id=sid)
                started = time.monotonic()
                result = stage.run(stage_input)
                elapsed = round(time.monotonic() - started, 3)
                # Honour the executor's timing if stage didn't set it.
                if result.elapsed_seconds == 0.0 and elapsed > 0:
                    result = StageResult(
                        stage_id=result.stage_id,
                        status=result.status,
                        elapsed_seconds=elapsed,
                        output=result.output,
                        error=result.error,
                    )
                if result.status == "pass":
                    self._emit(
                        ev.STAGE_SUCCEEDED,
                        f"elapsed={result.elapsed_seconds}s",
                        stage_id=sid,
                    )
                else:
                    self._emit(
                        ev.STAGE_FAILED,
                        result.error or "stage returned fail",
                        stage_id=sid,
                    )

            results.append(result)

            if result.status == "fail" and not plan.continue_on_error:
                self._emit(
                    ev.STAGE_FAILED,
                    "Halting pipeline (continue_on_error=false)",
                )
                break

        return results
