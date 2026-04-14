"""CLI helpers for BL-013 orchestration entrypoints."""
from __future__ import annotations

import argparse
import sys

from orchestration.stage_registry import DEFAULT_STAGE_ORDER, STAGE_SCRIPT_MAP


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "BL-013 orchestration runner for the bootstrap stages BL-004 to BL-009."
        )
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        default=None,
        help="Ordered stage IDs to run (default: BL-004 BL-005 BL-006 BL-007 BL-008 BL-009)",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue executing remaining stages after a failure.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to run stage scripts.",
    )
    parser.add_argument(
        "--output-dir",
        default="orchestration/outputs",
        help="Directory for BL-013 orchestration run summaries.",
    )
    parser.add_argument(
        "--summary-prefix",
        default="bl013_orchestration_run",
        help="Filename prefix for summary JSON artifacts.",
    )
    parser.add_argument(
        "--run-config",
        default=None,
        help=(
            "Optional path to a canonical run-config JSON file used by orchestration "
            "to resolve stage payloads."
        ),
    )
    parser.add_argument(
        "--refresh-seed",
        action="store_true",
        help=(
            "Run BL-003 seed-table rebuild before BL-004..BL-009. "
            "Useful when run-config input_scope changes."
        ),
    )
    parser.add_argument(
        "--run-config-artifact-dir",
        default="run_config/outputs",
        help=(
            "Directory where canonical run_intent/run_effective_config artifacts "
            "are emitted for this BL-013 run."
        ),
    )
    return parser.parse_args()


def validate_stage_order(stage_ids: list[str]) -> list[str]:
    """Normalize and validate user-provided stage IDs."""
    normalized: list[str] = []
    for stage_id in stage_ids:
        token = stage_id.strip().upper()
        if token not in STAGE_SCRIPT_MAP:
            valid = ", ".join(DEFAULT_STAGE_ORDER)
            raise ValueError(f"Unsupported stage '{stage_id}'. Valid values: {valid}")
        normalized.append(token)
    return normalized
