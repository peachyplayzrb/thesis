from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.observability import EventPublisher

from core import events as ev


@dataclass(frozen=True)
class AppConfig:
    """Validated single-file configuration for thesis runtime."""

    pipeline: dict[str, Any]
    controls: dict[str, Any]
    secrets: dict[str, Any]

    @classmethod
    def load(
        cls,
        config_path: Path,
        publisher: "EventPublisher | None" = None,
        run_id: str = "",
    ) -> "AppConfig":
        def emit(event_type: str, message: str, **details: Any) -> None:
            if publisher is not None:
                publisher.publish(
                    ev.make_event(
                        event_type,
                        run_id,
                        message,
                        details=details or None,
                    )
                )

        emit(ev.CONFIG_LOAD_STARTED, f"Loading config: {config_path}")

        if not config_path.exists() or not config_path.is_file():
            msg = f"Config file not found: {config_path}"
            emit(ev.CONFIG_LOAD_FAILED, msg)
            raise ValueError(msg)

        try:
            with config_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:
            msg = f"Failed to read config JSON: {exc}"
            emit(ev.CONFIG_LOAD_FAILED, msg)
            raise ValueError(msg) from exc

        if not isinstance(payload, dict):
            msg = "Config root must be a JSON object"
            emit(ev.CONFIG_LOAD_FAILED, msg)
            raise ValueError(msg)

        pipeline = payload.get("pipeline")
        controls = payload.get("controls")
        secrets = payload.get("secrets")

        if not isinstance(pipeline, dict):
            msg = "Missing or invalid key: pipeline (object required)"
            emit(ev.CONFIG_LOAD_FAILED, msg)
            raise ValueError(msg)
        if not isinstance(controls, dict):
            msg = "Missing or invalid key: controls (object required)"
            emit(ev.CONFIG_LOAD_FAILED, msg)
            raise ValueError(msg)
        if not isinstance(secrets, dict):
            msg = "Missing or invalid key: secrets (object required)"
            emit(ev.CONFIG_LOAD_FAILED, msg)
            raise ValueError(msg)

        stage_order = pipeline.get("stage_order")
        if not isinstance(stage_order, list) or not stage_order:
            msg = "pipeline.stage_order must be a non-empty array"
            emit(ev.CONFIG_LOAD_FAILED, msg)
            raise ValueError(msg)
        if not all(isinstance(item, str) and item.strip() for item in stage_order):
            msg = "pipeline.stage_order must contain non-empty strings"
            emit(ev.CONFIG_LOAD_FAILED, msg)
            raise ValueError(msg)

        for stage_id in stage_order:
            if stage_id not in controls:
                msg = f"controls is missing stage section: {stage_id}"
                emit(ev.CONFIG_LOAD_FAILED, msg)
                raise ValueError(msg)

        emit(
            ev.CONFIG_LOAD_SUCCEEDED,
            f"Config valid: {len(stage_order)} stages",
            stage_count=len(stage_order),
        )

        return cls(
            pipeline=dict(pipeline),
            controls=dict(controls),
            secrets=dict(secrets),
        )

    def stage_order(self) -> list[str]:
        return [str(item).strip() for item in self.pipeline.get("stage_order", [])]

    def continue_on_error(self) -> bool:
        return bool(self.pipeline.get("continue_on_error", False))

    def controls_for(self, stage_id: str) -> dict[str, Any]:
        controls = self.controls.get(stage_id, {})
        if not isinstance(controls, dict):
            raise ValueError(f"controls[{stage_id}] must be an object")
        return dict(controls)
