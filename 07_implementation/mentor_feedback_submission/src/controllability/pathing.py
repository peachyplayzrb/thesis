"""Path resolution helpers for BL-011 controllability inputs and outputs."""
from __future__ import annotations

from pathlib import Path

from shared_utils.artifact_registry import bl003_required_paths
from shared_utils.stage_utils import relpath


def build_paths(root: Path) -> dict[str, Path]:
    bl003_paths = bl003_required_paths(root)
    return {
        "legacy_manifest": root / "test_assets" / "bl016_asset_manifest.json",
        "legacy_coverage": root / "data_layer" / "outputs" / "onion_join_coverage_report.json",
        "bl003_summary": bl003_paths["summary"],
        "active_seed_trace": root / "profile" / "outputs" / "bl004_seed_trace.csv",
        "active_candidates": root / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv",
        "baseline_snapshot": root / "reproducibility" / "outputs" / "reproducibility_config_snapshot.json",
        "output_dir": root / "controllability" / "outputs",
    }


def ensure_required_inputs(paths: dict[str, Path], root: Path) -> None:
    required = ["baseline_snapshot", "bl003_summary", "active_seed_trace", "active_candidates"]
    missing = [relpath(paths[key], root) for key in required if not paths[key].exists()]
    if missing:
        raise FileNotFoundError(f"BL-011 missing required inputs: {missing}")
