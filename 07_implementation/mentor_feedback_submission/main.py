from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _resolve_impl_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    impl_root = script_dir / "src"
    if not impl_root.is_dir():
        raise RuntimeError(f"Cannot find src directory at {impl_root}")
    return impl_root


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Standalone recommendation system implementation orchestrator."
    )
    parser.add_argument(
        "--run-config",
        type=Path,
        default=None,
        help="Path to run_config JSON file (default: canonical v1f config)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run validation checks after pipeline completes",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue pipeline even if individual stages report non-fatal errors",
    )
    return parser.parse_args()


def _run_subprocess(command: list[str], *, cwd: Path, env_vars: dict[str, str] | None = None) -> int:
    print("\n" + "=" * 70)
    print("Running:", " ".join(command))
    print("=" * 70 + "\n")

    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    completed = subprocess.run(command, cwd=str(cwd), check=False, env=env)
    return int(completed.returncode)


def main() -> int:
    args = _parse_args()
    impl_root = _resolve_impl_root()

    run_config_path = (
        args.run_config.resolve()
        if args.run_config
        else Path(__file__).resolve().parent / "config" / "profiles" / "run_config_ui013_tuning_v1f.json"
    )
    if not run_config_path.exists():
        print(f"ERROR: Run config file not found: {run_config_path}", file=sys.stderr)
        return 1

    bl013_script = impl_root / "orchestration" / "main.py"
    if not bl013_script.exists():
        print(f"ERROR: orchestration script not found: {bl013_script}", file=sys.stderr)
        return 1

    existing_pythonpath = os.environ.get("PYTHONPATH", "")
    pythonpath_parts = [str(impl_root)]
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    env_vars = {"PYTHONPATH": os.pathsep.join(pythonpath_parts)}

    bl013_command = [
        sys.executable,
        str(bl013_script),
        "--run-config",
        str(run_config_path),
        "--refresh-seed",
    ]
    if args.continue_on_error:
        bl013_command.append("--continue-on-error")

    print("Starting recommendation system pipeline...")
    print("  Implementation root:", impl_root)
    print("  Run config:", run_config_path)
    print("  Seed refresh: forced")

    bl013_rc = _run_subprocess(bl013_command, cwd=impl_root, env_vars=env_vars)

    if bl013_rc != 0:
        print(f"\nERROR: BL-013 pipeline failed with exit code {bl013_rc}", file=sys.stderr)
        if not args.continue_on_error:
            return bl013_rc
        print("Continuing to validation (--continue-on-error was set)")
    else:
        print("\nSUCCESS: BL-013 pipeline completed without errors")

    if args.validate_only:
        print("\nRunning validation checks...")
        bl014_script = impl_root / "quality" / "sanity_checks.py"
        if not bl014_script.exists():
            print(f"ERROR: quality validation script not found: {bl014_script}", file=sys.stderr)
            return 1

        bl014_command = [sys.executable, str(bl014_script)]
        bl014_rc = _run_subprocess(bl014_command, cwd=impl_root, env_vars=env_vars)

        if bl014_rc != 0:
            print(f"\nWARNING: BL-014 validation reported issues (exit code {bl014_rc})", file=sys.stderr)
        else:
            print("\nSUCCESS: BL-014 validation passed")

    print("\n" + "=" * 70)
    print("Pipeline execution complete!")
    print("Output artifacts saved under:", impl_root)
    print("=" * 70 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
