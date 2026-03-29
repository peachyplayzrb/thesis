"""
BL-006: Score candidates based on profile preference model.

Thin compatibility entrypoint wrappers over the class-based ScoringStage.
"""

from __future__ import annotations

from pathlib import Path

from scoring.models import (
    NUMERIC_COMPONENTS,
    NUMERIC_FEATURE_SPECS,
    SCORED_CANDIDATE_FIELDS,
    ScoringPaths,
    context_from_mapping,
    context_as_mapping,
    controls_from_mapping,
)
from scoring.profile_extractor import build_component_weights
from scoring.stage import ScoringStage


def resolve_bl006_paths(root: Path) -> dict[str, Path]:
    paths = ScoringStage(root=root).resolve_paths()
    return {
        "profile_path": paths.profile_path,
        "filtered_candidates_path": paths.filtered_candidates_path,
        "output_dir": paths.output_dir,
    }


def load_bl006_inputs(paths: dict[str, Path]) -> tuple[dict[str, object], list[dict[str, str]]]:
    typed_paths = ScoringPaths(
        profile_path=paths["profile_path"],
        filtered_candidates_path=paths["filtered_candidates_path"],
        output_dir=paths["output_dir"],
    )
    inputs = ScoringStage.load_inputs(typed_paths)
    return inputs.profile, inputs.candidates


def resolve_bl006_runtime_controls(default_weights: dict[str, float]) -> dict[str, object]:
    controls = ScoringStage.resolve_runtime_controls(default_weights)
    return controls.as_mapping()


def build_bl006_runtime_context(
    *,
    profile: dict[str, object],
    runtime_controls: dict[str, object],
) -> dict[str, object]:
    context = ScoringStage.build_runtime_context(
        profile=profile,
        runtime_controls=controls_from_mapping(runtime_controls),
    )
    return context_as_mapping(context)


def score_bl006_candidates(
    *,
    candidates: list[dict[str, object]],
    runtime_context: dict[str, object],
) -> list[dict[str, object]]:
    context = context_from_mapping(runtime_context)
    normalized_candidates: list[dict[str, str]] = [
        {str(k): str(v) for k, v in row.items()}
        for row in candidates
    ]
    return ScoringStage.score_candidates(candidates=normalized_candidates, runtime_context=context)


def write_bl006_scored_csv(*, scored_rows: list[dict[str, object]], scored_path: Path) -> None:
    ScoringStage.write_scored_csv(scored_rows=scored_rows, scored_path=scored_path)


def build_bl006_summary(
    *,
    run_id: str,
    elapsed_seconds: float,
    paths: dict[str, Path],
    runtime_context: dict[str, object],
    scored_rows: list[dict[str, object]],
    distribution_diagnostics: dict[str, object],
    diagnostics_path: Path,
    scored_path: Path,
) -> dict[str, object]:
    typed_paths = ScoringPaths(
        profile_path=paths["profile_path"],
        filtered_candidates_path=paths["filtered_candidates_path"],
        output_dir=paths["output_dir"],
    )
    context = context_from_mapping(runtime_context)
    return ScoringStage.build_summary(
        run_id=run_id,
        elapsed_seconds=elapsed_seconds,
        paths=typed_paths,
        runtime_context=context,
        scored_rows=scored_rows,
        distribution_diagnostics=distribution_diagnostics,
        diagnostics_path=diagnostics_path,
        scored_path=scored_path,
    )


def main() -> None:
    ScoringStage().run()


if __name__ == "__main__":
    main()
