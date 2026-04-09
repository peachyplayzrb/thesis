"""Core OOP runtime objects for finalized thesis entrypoint."""

from core.app_config import AppConfig
from core.events import RunEvent, make_event, new_run_id
from core.observability import EventPublisher, RunObserver
from core.pipeline_orchestrator import OrchestrationPlan, PipelineOrchestrator, StageInput, StageResult
from core.stage_base import StageBase, StageRegistry
from core.terminal_observer import TerminalObserver

__all__ = [
    "AppConfig",
    "EventPublisher",
    "OrchestrationPlan",
    "PipelineOrchestrator",
    "RunEvent",
    "RunObserver",
    "StageBase",
    "StageInput",
    "StageRegistry",
    "StageResult",
    "TerminalObserver",
    "make_event",
    "new_run_id",
]
