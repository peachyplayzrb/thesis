"""Thesis pipeline entrypoint.

Accepts exactly one input: a config file path.
Emits structured lifecycle events to the terminal via the observer layer.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core.app_config import AppConfig
from core import events as ev
from core.observability import EventPublisher
from core.pipeline_orchestrator import PipelineOrchestrator
from core.stage_base import StageRegistry
from core.terminal_observer import TerminalObserver


def run(config_path: Path) -> int:
	run_id = ev.new_run_id()
	publisher = EventPublisher()
	publisher.subscribe(TerminalObserver())

	def emit(event_type: str, message: str) -> None:
		publisher.publish(ev.make_event(event_type, run_id, message))

	emit(ev.APP_STARTED, f"Run started | config={config_path}")

	try:
		config = AppConfig.load(config_path, publisher=publisher, run_id=run_id)
		orchestrator = PipelineOrchestrator(config, publisher=publisher, run_id=run_id)

		# Registry is empty until stage classes are registered here.
		registry = StageRegistry()
		results = orchestrator.execute(registry)

		passed = sum(1 for r in results if r.status == "pass")
		failed = sum(1 for r in results if r.status == "fail")
		emit(ev.RUN_SUMMARY, f"stages={len(results)} passed={passed} failed={failed}")
	except Exception:
		emit(ev.APP_FAILED, "Run aborted due to error (see above)")
		emit(ev.APP_FINISHED, "Run finished | exit=1")
		return 1

	exit_code = 0 if failed == 0 else 1
	emit(ev.APP_FINISHED, f"Run finished | exit={exit_code}")
	return exit_code


def main(argv: list[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description="Run thesis pipeline from a single config file.")
	parser.add_argument("config", type=Path, help="Path to config file")
	args = parser.parse_args(argv)
	return run(args.config)


if __name__ == "__main__":
	sys.exit(main())
