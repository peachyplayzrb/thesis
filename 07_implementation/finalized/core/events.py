from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_run_id() -> str:
    """Generate a short unique run identifier."""
    return str(uuid.uuid4())[:8]


# ---------------------------------------------------------------------------
# Base event
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunEvent:
    event_type: str
    run_id: str
    timestamp: str
    message: str
    stage_id: str | None = None
    details: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------

def make_event(
    event_type: str,
    run_id: str,
    message: str,
    stage_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> RunEvent:
    return RunEvent(
        event_type=event_type,
        run_id=run_id,
        timestamp=_now(),
        message=message,
        stage_id=stage_id,
        details=details,
    )


# ---------------------------------------------------------------------------
# Event type constants
# ---------------------------------------------------------------------------

# Application lifecycle
APP_STARTED = "app_started"
APP_FINISHED = "app_finished"
APP_FAILED = "app_failed"

# Config loading
CONFIG_LOAD_STARTED = "config_load_started"
CONFIG_LOAD_SUCCEEDED = "config_load_succeeded"
CONFIG_LOAD_FAILED = "config_load_failed"

# Orchestration — planning
PLAN_BUILD_STARTED = "plan_build_started"
PLAN_BUILD_SUCCEEDED = "plan_build_succeeded"
STAGE_PLANNED = "stage_planned"

# Orchestration — execution
STAGE_STARTED = "stage_started"
STAGE_SUCCEEDED = "stage_succeeded"
STAGE_FAILED = "stage_failed"
RUN_SUMMARY = "run_summary"
