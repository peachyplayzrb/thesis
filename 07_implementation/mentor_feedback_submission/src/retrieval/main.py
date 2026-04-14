"""BL-005 entry point for filtering the candidate corpus against the preference profile."""

from __future__ import annotations

from pathlib import Path

from retrieval.models import RetrievalContext, RetrievalControls, RetrievalInputs, RetrievalPaths
from retrieval.stage import RetrievalStage


def resolve_bl005_runtime_controls() -> RetrievalControls:
    return RetrievalStage().resolve_runtime_controls()


def resolve_bl005_paths(root: Path) -> RetrievalPaths:
    return RetrievalStage(root=root).resolve_paths()


def load_bl005_inputs(paths: RetrievalPaths) -> RetrievalInputs:
    return RetrievalStage.load_inputs(paths)


def build_bl005_runtime_context(
    *,
    profile: dict[str, object],
    candidate_rows: list[dict[str, str]],
    seed_trace_rows: list[dict[str, str]],
    runtime_controls: RetrievalControls,
) -> RetrievalContext:
    inputs = RetrievalInputs(
        profile=profile,
        candidate_rows=candidate_rows,
        seed_trace_rows=seed_trace_rows,
    )
    return RetrievalStage.build_runtime_context(inputs=inputs, controls=runtime_controls)


def main() -> None:
    RetrievalStage().run()


if __name__ == "__main__":
    main()
