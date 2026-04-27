from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_IMPLEMENTATION_ROOT = REPO_ROOT / "07_implementation" / "implementation_notes"
DEFAULT_RUN_CONFIG = (
    DEFAULT_IMPLEMENTATION_ROOT
    / "bl000_run_config"
    / "configs"
    / "profiles"
    / "run_config_ui013_tuning_v1f.json"
)
DEFAULT_BL013 = (
    DEFAULT_IMPLEMENTATION_ROOT
    / "bl013_entrypoint"
    / "run_bl013_pipeline_entrypoint.py"
)
DEFAULT_BL014 = (
    DEFAULT_IMPLEMENTATION_ROOT
    / "bl014_quality"
    / "run_bl014_sanity_checks.py"
)


@dataclass(frozen=True)
class RuntimePaths:
    implementation_root: Path
    bl013_script: Path
    bl014_script: Path
    run_config: Path


def _resolve_runtime_paths(args: argparse.Namespace) -> RuntimePaths:
    implementation_root = Path(args.implementation_root).resolve()
    run_config = Path(args.run_config).resolve()
    bl013_script = implementation_root / "bl013_entrypoint" / "run_bl013_pipeline_entrypoint.py"
    bl014_script = implementation_root / "bl014_quality" / "run_bl014_sanity_checks.py"
    return RuntimePaths(
        implementation_root=implementation_root,
        bl013_script=bl013_script,
        bl014_script=bl014_script,
        run_config=run_config,
    )


def _require_paths(paths: RuntimePaths) -> None:
    missing = []
    if not paths.implementation_root.exists():
        missing.append(f"implementation_root: {paths.implementation_root}")
    if not paths.bl013_script.exists():
        missing.append(f"BL013 script: {paths.bl013_script}")
    if not paths.bl014_script.exists():
        missing.append(f"BL014 script: {paths.bl014_script}")
    if not paths.run_config.exists():
        missing.append(f"run_config: {paths.run_config}")
    if missing:
        details = "\n".join(f"- {item}" for item in missing)
        raise SystemExit(f"Required path(s) missing:\n{details}")


def _run_subprocess(command: list[str], *, cwd: Path) -> int:
    print("Running:", " ".join(command))
    completed = subprocess.run(command, cwd=str(cwd), check=False)
    return int(completed.returncode)


def _run_bl013(args: argparse.Namespace, paths: RuntimePaths) -> int:
    command = [args.python, str(paths.bl013_script), "--run-config", str(paths.run_config)]
    if args.refresh_seed:
        command.append("--refresh-seed")
    if args.continue_on_error:
        command.append("--continue-on-error")
    return _run_subprocess(command, cwd=REPO_ROOT)


def _run_bl014(args: argparse.Namespace, paths: RuntimePaths) -> int:
    command = [args.python, str(paths.bl014_script)]
    return _run_subprocess(command, cwd=REPO_ROOT)


def command_run(args: argparse.Namespace) -> int:
    paths = _resolve_runtime_paths(args)
    _require_paths(paths)

    run_rc = _run_bl013(args, paths)
    if run_rc != 0:
        return run_rc

    if args.validate_only:
        return _run_bl014(args, paths)

    return 0


def command_validate(args: argparse.Namespace) -> int:
    paths = _resolve_runtime_paths(args)
    _require_paths(paths)
    return _run_bl014(args, paths)


def _copytree(src: Path, dst: Path, *, include_outputs: bool) -> None:
    def _ignore(path: str, names: list[str]) -> set[str]:
        ignored = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
        if not include_outputs and Path(path).name == "outputs":
            return set(names)
        return {name for name in names if name in ignored}

    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=_ignore)


def command_bundle(args: argparse.Namespace) -> int:
    destination = Path(args.destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)

    bundle_root = destination / "final_artefact_bundle"
    if bundle_root.exists() and any(bundle_root.iterdir()):
        raise SystemExit(
            f"Bundle destination is not empty: {bundle_root}. Use an empty folder or remove it first."
        )
    bundle_root.mkdir(parents=True, exist_ok=True)

    artefact_runtime = bundle_root / "runtime"
    artefact_runtime.mkdir(parents=True, exist_ok=True)

    implementation_src = REPO_ROOT / "07_implementation" / "implementation_notes"
    implementation_dst = artefact_runtime / "implementation_notes"
    _copytree(implementation_src, implementation_dst, include_outputs=args.include_outputs)

    for extra_doc in [
        REPO_ROOT / "07_implementation" / "RUN_GUIDE.md",
        REPO_ROOT / "07_implementation" / "ACTIVE_BASELINE.md",
        REPO_ROOT / "07_implementation" / "ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md",
    ]:
        if extra_doc.exists():
            shutil.copy2(extra_doc, bundle_root / extra_doc.name)

    this_script = Path(__file__).resolve()
    shutil.copy2(this_script, bundle_root / "final_artefact.py")

    if (REPO_ROOT / "final_artefact").exists():
        _copytree(REPO_ROOT / "final_artefact", bundle_root / "final_artefact", include_outputs=True)

    manifest_payload = {
        "bundle_root": str(bundle_root),
        "include_outputs": bool(args.include_outputs),
        "copied": [
            "final_artefact.py",
            "final_artefact/",
            "runtime/implementation_notes/",
            "RUN_GUIDE.md",
            "ACTIVE_BASELINE.md",
            "ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md",
        ],
        "entry_command": (
            "python final_artefact.py run --implementation-root "
            "runtime/implementation_notes --run-config "
            "runtime/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json "
            "--refresh-seed"
        ),
    }
    (bundle_root / "BUNDLE_MANIFEST.json").write_text(
        json.dumps(manifest_payload, indent=2), encoding="utf-8"
    )

    print(f"Standalone bundle created at: {bundle_root}")
    return 0


def command_show_paths(args: argparse.Namespace) -> int:
    paths = _resolve_runtime_paths(args)
    payload = {
        "repo_root": str(REPO_ROOT),
        "implementation_root": str(paths.implementation_root),
        "bl013_script": str(paths.bl013_script),
        "bl014_script": str(paths.bl014_script),
        "run_config": str(paths.run_config),
    }
    print(json.dumps(payload, indent=2))
    return 0


def _base_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Standalone entrypoint for thesis artefact execution and packaging."
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable for running stage scripts (default: current interpreter).",
    )
    parser.add_argument(
        "--implementation-root",
        default=str(DEFAULT_IMPLEMENTATION_ROOT),
        help="Path to implementation_notes root (default: repository implementation path).",
    )
    parser.add_argument(
        "--run-config",
        default=str(DEFAULT_RUN_CONFIG),
        help="Path to run-config profile JSON.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = _base_parser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run BL-013 orchestration.")
    run_parser.add_argument("--refresh-seed", action="store_true", help="Pass --refresh-seed to BL-013.")
    run_parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Pass --continue-on-error to BL-013.",
    )
    run_parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run BL-014 sanity checks after BL-013 succeeds.",
    )
    run_parser.set_defaults(handler=command_run)

    validate_parser = subparsers.add_parser("validate", help="Run BL-014 sanity checks only.")
    validate_parser.set_defaults(handler=command_validate)

    bundle_parser = subparsers.add_parser(
        "bundle", help="Create a portable bundle containing runtime code and launcher."
    )
    bundle_parser.add_argument(
        "--destination",
        required=True,
        help="Directory where the bundle folder will be created.",
    )
    bundle_parser.add_argument(
        "--include-outputs",
        action="store_true",
        help="Include stage outputs folders in copied implementation tree.",
    )
    bundle_parser.set_defaults(handler=command_bundle)

    paths_parser = subparsers.add_parser("show-paths", help="Print resolved runtime paths.")
    paths_parser.set_defaults(handler=command_show_paths)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
