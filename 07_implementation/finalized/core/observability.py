from __future__ import annotations

import sys
from abc import ABC, abstractmethod

from core.events import RunEvent


class RunObserver(ABC):
    """Interface that all event observers must implement."""

    @abstractmethod
    def on_event(self, event: RunEvent) -> None: ...


class EventPublisher:
    """Fan-out publisher: emits RunEvents to all registered observers.

    A failing observer is silenced and its error printed to stderr so that
    one broken observer can never interrupt the pipeline run.
    """

    def __init__(self) -> None:
        self._observers: list[RunObserver] = []

    def subscribe(self, observer: RunObserver) -> None:
        self._observers.append(observer)

    def publish(self, event: RunEvent) -> None:
        for observer in self._observers:
            try:
                observer.on_event(event)
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[observer error] {type(observer).__name__}: {exc}",
                    file=sys.stderr,
                )
