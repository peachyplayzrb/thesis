from __future__ import annotations

from abc import ABC, abstractmethod

from core.pipeline_orchestrator import StageInput, StageResult


class StageBase(ABC):
    """Abstract base class every stage must implement.

    Contract rules:
    - stage_id must return the canonical identifier (e.g. 'BL-003').
    - run() must never raise. Catch all internal errors and return
      StageResult(status='fail', error=<message>).
    - run() receives only its own StageInput slice (controls + secrets).
      No global config, no env variable access.
    """

    @property
    @abstractmethod
    def stage_id(self) -> str: ...

    @abstractmethod
    def run(self, stage_input: StageInput) -> StageResult: ...


class StageRegistry:
    """Maps stage IDs to StageBase instances.

    Register all stage instances at startup. The orchestrator calls
    get() for each planned stage ID to dispatch execution.
    """

    def __init__(self) -> None:
        self._stages: dict[str, StageBase] = {}

    def register(self, stage: StageBase) -> None:
        self._stages[stage.stage_id] = stage

    def get(self, stage_id: str) -> StageBase | None:
        return self._stages.get(stage_id)

    def registered_ids(self) -> list[str]:
        return list(self._stages.keys())
