"""
Standalone entry point for the recommendation system implementation.

This is the main entry point for reviewers/researchers who have extracted
the standalone implementation package. It orchestrates the full pipeline.

Usage:
    python main.py

    python main.py --validate-only

    python main.py --run-config config/profiles/run_config_ui013_tuning_v1f.json
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _resolve_impl_root() -> Path:
    """Resolve the src directory relative to this script."""
    script_dir = Path(__file__).resolve().parent
    impl_root = script_dir / "src"
    if not impl_root.is_dir():
        raise RuntimeError(
            f"Cannot find src directory at {impl_root}. "
            f"Are you running from the standalone package root?"
        )
    return impl_root


def _resolve_embedded_candidate_dataset(impl_root: Path) -> Path:
    """Resolve the embedded DS-001 candidate dataset bundled with the artefact."""
    dataset_path = impl_root / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv"
    if not dataset_path.is_file():
        raise RuntimeError(
            f"Cannot find embedded candidate dataset at {dataset_path}. "
            "The standalone package is incomplete."
        )
    return dataset_path


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Standalone recommendation system implementation orchestrator.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --validate-only
  python main.py --run-config config/profiles/run_config_ui013_tuning_v1f.json
        """,
    )

    parser.add_argument(
        "--run-config",
        type=Path,
        default=None,
        help="Path to run_config JSON file (default: uses canonical v1f config)",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run validation checks (BL-014) after pipeline completes",
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue pipeline even if individual stages report non-fatal errors",
    )

    return parser.parse_args()


def _run_subprocess(command: list[str], *, cwd: Path, env_vars: dict[str, str] | None = None) -> int:
    """Run a subprocess and return exit code."""
    print(f"\n{'=' * 70}")
    print(f"Running: {' '.join(command)}")
    print(f"{'=' * 70}\n")

    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    completed = subprocess.run(command, cwd=str(cwd), check=False, env=env)
    return int(completed.returncode)


def main() -> int:
    """Main entry point."""
    args = _parse_args()

    # Resolve paths
    impl_root = _resolve_impl_root()
    try:
        embedded_dataset_path = _resolve_embedded_candidate_dataset(impl_root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Determine run config path
    if args.run_config:
        run_config_path = args.run_config.resolve()
    else:
        run_config_path = (
            Path(__file__).resolve().parent / "config" / "profiles" / "run_config_ui013_tuning_v1f.json"
        )

    if not run_config_path.exists():
        print(f"ERROR: Run config file not found: {run_config_path}", file=sys.stderr)
        return 1

    # Build orchestration command
    bl013_script = impl_root / "orchestration" / "main.py"
    if not bl013_script.exists():
        print(f"ERROR: orchestration script not found: {bl013_script}", file=sys.stderr)
        return 1

    # Prepare environment variables
    existing_pythonpath = os.environ.get("PYTHONPATH", "")
    pythonpath_parts = [str(impl_root)]
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)

    env_vars = {
        "IMPL_ROOT": str(impl_root),
        "BL_RUN_CONFIG_PATH": str(run_config_path),
        "PYTHONPATH": os.pathsep.join(pythonpath_parts),
    }

    # Build BL-013 command
    bl013_command = [
        sys.executable,
        str(bl013_script),
        "--run-config",
        str(run_config_path),
        "--refresh-seed",
    ]
    if args.continue_on_error:
        bl013_command.append("--continue-on-error")

    # Run BL-013 pipeline
    print(f"Starting recommendation system pipeline...")
    print(f"  Implementation root: {impl_root}")
    print(f"  Embedded candidate dataset: {embedded_dataset_path}")
    print(f"  Run config: {run_config_path}")
    print("  Seed refresh: forced (embedded DS-001 dataset mode)")

    bl013_rc = _run_subprocess(bl013_command, cwd=impl_root, env_vars=env_vars)

    if bl013_rc != 0:
        print(f"\nERROR: BL-013 pipeline failed with exit code {bl013_rc}", file=sys.stderr)
        if not args.continue_on_error:
            return bl013_rc
        else:
            print("Continuing to validation (--continue-on-error was set)")
    else:
        print(f"\nSUCCESS: BL-013 pipeline completed without errors")

    # Run validation if requested
    if args.validate_only:
        print(f"\nRunning validation checks...")
        bl014_script = impl_root / "quality" / "sanity_checks.py"
        if not bl014_script.exists():
            print(f"ERROR: quality validation script not found: {bl014_script}", file=sys.stderr)
            return 1

        bl014_command = [sys.executable, str(bl014_script)]
        bl014_rc = _run_subprocess(bl014_command, cwd=impl_root, env_vars=env_vars)

        if bl014_rc != 0:
            print(f"\nWARNING: BL-014 validation reported issues (exit code {bl014_rc})", file=sys.stderr)
        else:
            print(f"\nSUCCESS: BL-014 validation passed")

    print(f"\n{'=' * 70}")
    print(f"Pipeline execution complete!")
    print(f"Output artifacts saved under: {impl_root}")
    print(f"{'=' * 70}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
