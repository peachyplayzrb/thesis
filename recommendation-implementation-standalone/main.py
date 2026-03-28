"""
Standalone entry point for the recommendation system implementation.

This is the main entry point for reviewers/researchers who have extracted
the standalone implementation package. It orchestrates the full pipeline.

Usage:
    python main.py --dataset-root /path/to/music4all/ \\
        --run-config implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json
    
    python main.py --dataset-root /path/to/music4all/ --validate-only
    
    python main.py --dataset-root /path/to/music4all/ --refresh-seed
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _resolve_impl_root() -> Path:
    """Resolve the implementation_notes directory relative to this script."""
    script_dir = Path(__file__).resolve().parent
    impl_root = script_dir / "implementation_notes"
    if not impl_root.is_dir():
        raise RuntimeError(
            f"Cannot find implementation_notes directory at {impl_root}. "
            f"Are you running from the standalone package root?"
        )
    return impl_root


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Standalone recommendation system implementation orchestrator.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --dataset-root /path/to/music4all/
  python main.py --dataset-root /path/to/music4all/ --validate-only
  python main.py --dataset-root /path/to/music4all/ --refresh-seed
        """,
    )
    
    parser.add_argument(
        "--dataset-root",
        type=Path,
        required=True,
        help="Path to music4all dataset root (contains id_information.csv, id_metadata.csv, etc.)",
    )
    
    parser.add_argument(
        "--run-config",
        type=Path,
        default=None,
        help="Path to run_config JSON file (default: uses canonical v1f config)",
    )
    
    parser.add_argument(
        "--refresh-seed",
        action="store_true",
        help="Force refresh of BL-003 seed table even if run-config hasn't changed",
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
    dataset_root = args.dataset_root.resolve()
    
    if not dataset_root.is_dir():
        print(f"ERROR: Dataset root does not exist: {dataset_root}", file=sys.stderr)
        return 1
    
    # Validate dataset files
    required_files = [
        dataset_root / "id_information.csv",
        dataset_root / "id_metadata.csv",
        dataset_root / "id_tags.csv",
        dataset_root / "id_genres.csv",
    ]
    for path in required_files:
        if not path.exists():
            print(f"ERROR: Required dataset file missing: {path}", file=sys.stderr)
            return 1
    
    # Determine run config path
    if args.run_config:
        run_config_path = args.run_config.resolve()
    else:
        run_config_path = (
            impl_root / "bl000_run_config" / "configs" / "profiles" / "run_config_ui013_tuning_v1f.json"
        )
    
    if not run_config_path.exists():
        print(f"ERROR: Run config file not found: {run_config_path}", file=sys.stderr)
        return 1
    
    # Build BL-013 orchestrator command
    bl013_script = impl_root / "bl013_entrypoint" / "run_bl013_pipeline_entrypoint.py"
    if not bl013_script.exists():
        print(f"ERROR: BL-013 script not found: {bl013_script}", file=sys.stderr)
        return 1
    
    # Prepare environment variables
    env_vars = {
        "IMPL_ROOT": str(impl_root),
        "IMPL_DATASET_ROOT": str(dataset_root),
        "BL_RUN_CONFIG_PATH": str(run_config_path),
    }
    
    # Build BL-013 command
    bl013_command = [sys.executable, str(bl013_script), "--run-config", str(run_config_path)]
    if args.refresh_seed:
        bl013_command.append("--refresh-seed")
    if args.continue_on_error:
        bl013_command.append("--continue-on-error")
    
    # Run BL-013 pipeline
    print(f"Starting recommendation system pipeline...")
    print(f"  Implementation root: {impl_root}")
    print(f"  Dataset root: {dataset_root}")
    print(f"  Run config: {run_config_path}")
    
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
        bl014_script = impl_root / "bl014_quality" / "run_bl014_sanity_checks.py"
        if not bl014_script.exists():
            print(f"ERROR: BL-014 script not found: {bl014_script}", file=sys.stderr)
            return 1
        
        bl014_command = [sys.executable, str(bl014_script)]
        bl014_rc = _run_subprocess(bl014_command, cwd=impl_root, env_vars=env_vars)
        
        if bl014_rc != 0:
            print(f"\nWARNING: BL-014 validation reported issues (exit code {bl014_rc})", file=sys.stderr)
        else:
            print(f"\nSUCCESS: BL-014 validation passed")
    
    print(f"\n{'=' * 70}")
    print(f"Pipeline execution complete!")
    print(f"Output artifacts saved to: {impl_root / 'bl*' / 'outputs'}")
    print(f"{'=' * 70}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
