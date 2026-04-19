from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_VALID_STAGE_IDS = {"BL-004", "BL-005", "BL-006", "BL-007", "BL-008", "BL-009"}


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
        "--stages",
        nargs="+",
        default=None,
        help=(
            "Ordered BL-013 stage IDs to run (BL-004..BL-009). "
            "When omitted, BL-013 default stage order is used."
        ),
    )
    parser.add_argument(
        "--no-refresh-seed",
        action="store_true",
        help=(
            "Do not force BL-003 seed refresh before BL-013 stage execution. "
            "Default wrapper behavior is to force seed refresh."
        ),
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
    parser.add_argument(
        "--verify-determinism",
        action="store_true",
        help="Run BL-010 reproducibility replay after successful BL-013 execution.",
    )
    parser.add_argument(
        "--verify-determinism-replay-count",
        type=int,
        default=None,
        help="Replay count for deterministic verification (used with --verify-determinism).",
    )
    return parser.parse_args()


def _normalize_stage_ids(stage_ids: list[str] | None) -> list[str] | None:
    if stage_ids is None:
        return None

    normalized: list[str] = []
    for stage_id in stage_ids:
        token = stage_id.strip().upper()
        if token not in _VALID_STAGE_IDS:
            valid = ", ".join(sorted(_VALID_STAGE_IDS))
            raise ValueError(f"Unsupported stage '{stage_id}'. Valid values: {valid}")
        normalized.append(token)
    return normalized


def _build_bl013_command(
    *,
    bl013_script: Path,
    run_config_path: Path,
    continue_on_error: bool,
    refresh_seed: bool,
    stages: list[str] | None,
    verify_determinism: bool,
    verify_determinism_replay_count: int | None,
) -> list[str]:
    command = [
        sys.executable,
        str(bl013_script),
        "--run-config",
        str(run_config_path),
    ]

    if refresh_seed:
        command.append("--refresh-seed")
    if continue_on_error:
        command.append("--continue-on-error")
    if stages:
        command.extend(["--stages", *stages])
    if verify_determinism:
        command.append("--verify-determinism")
    if verify_determinism_replay_count is not None:
        command.extend(["--verify-determinism-replay-count", str(verify_determinism_replay_count)])

    return command


def _validate_determinism_args(
    *,
    verify_determinism: bool,
    verify_determinism_replay_count: int | None,
) -> str | None:
    if verify_determinism_replay_count is None:
        return None
    if not verify_determinism:
        return "--verify-determinism-replay-count requires --verify-determinism"
    if verify_determinism_replay_count <= 0:
        return "--verify-determinism-replay-count must be a positive integer"
    return None


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
    determinism_error = _validate_determinism_args(
        verify_determinism=args.verify_determinism,
        verify_determinism_replay_count=args.verify_determinism_replay_count,
    )
    if determinism_error is not None:
        print(f"ERROR: {determinism_error}", file=sys.stderr)
        return 1

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

    try:
        normalized_stages = _normalize_stage_ids(args.stages)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Keep PYTHONPATH for robust imports when running entry scripts directly.
    existing_pythonpath = os.environ.get("PYTHONPATH", "")
    pythonpath_parts = [str(impl_root)]
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    env_vars = {"PYTHONPATH": os.pathsep.join(pythonpath_parts)}

    bl013_command = _build_bl013_command(
        bl013_script=bl013_script,
        run_config_path=run_config_path,
        continue_on_error=args.continue_on_error,
        refresh_seed=not args.no_refresh_seed,
        stages=normalized_stages,
        verify_determinism=args.verify_determinism,
        verify_determinism_replay_count=args.verify_determinism_replay_count,
    )

    print("Starting recommendation system pipeline...")
    print("  Implementation root:", impl_root)
    print("  Run config:", run_config_path)
    print("  Seed refresh:", "forced" if not args.no_refresh_seed else "disabled")
    if args.verify_determinism:
        print(
            "  Determinism verify:",
            f"enabled ({args.verify_determinism_replay_count or 'default'} replays)",
        )
    if normalized_stages:
        print("  Stage override:", ", ".join(normalized_stages))

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
