from __future__ import annotations

import sys

from core.events import (
    APP_FAILED,
    APP_FINISHED,
    APP_STARTED,
    CONFIG_LOAD_FAILED,
    CONFIG_LOAD_STARTED,
    CONFIG_LOAD_SUCCEEDED,
    PLAN_BUILD_STARTED,
    PLAN_BUILD_SUCCEEDED,
    RUN_SUMMARY,
    STAGE_FAILED,
    STAGE_PLANNED,
    STAGE_STARTED,
    STAGE_SUCCEEDED,
    RunEvent,
)
from core.observability import RunObserver

# Map event types to simple severity labels for terminal display.
_LEVEL: dict[str, str] = {
    APP_STARTED: "INFO",
    APP_FINISHED: "INFO",
    APP_FAILED: "ERROR",
    CONFIG_LOAD_STARTED: "INFO",
    CONFIG_LOAD_SUCCEEDED: "INFO",
    CONFIG_LOAD_FAILED: "ERROR",
    PLAN_BUILD_STARTED: "INFO",
    PLAN_BUILD_SUCCEEDED: "INFO",
    STAGE_PLANNED: "INFO",
    STAGE_STARTED: "INFO",
    STAGE_SUCCEEDED: "INFO",
    STAGE_FAILED: "ERROR",
    RUN_SUMMARY: "INFO",
}

_ERROR_TYPES = {APP_FAILED, CONFIG_LOAD_FAILED, STAGE_FAILED}


class TerminalObserver(RunObserver):
    """Renders RunEvents as stable one-line terminal records.

    Format:
        TIMESTAMP | LEVEL     | event_type          | [stage_id] message
    Example:
        2026-04-08T12:01:03Z | INFO  | stage_planned       | BL-004  controls=0 secrets=3
    """

    def on_event(self, event: RunEvent) -> None:
        level = _LEVEL.get(event.event_type, "INFO")
        stage_part = f"[{event.stage_id}] " if event.stage_id else ""
        line = (
            f"{event.timestamp} | {level:<5} | {event.event_type:<24} | "
            f"{stage_part}{event.message}"
        )
        if event.event_type in _ERROR_TYPES:
            print(line, file=sys.stderr, flush=True)
        else:
            print(line, flush=True)
