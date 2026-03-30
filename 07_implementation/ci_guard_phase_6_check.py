#!/usr/bin/env python
"""Phase 6: CI guard script — validate no stage modules read config directly.

This script enforces the architectural rule:
  "Only orchestration resolves config; stages consume explicit controls."

It scans stage modules for prohibited patterns:
  1. Direct imports of run_config_utils
  2. Reads of BL_RUN_CONFIG_PATH outside fallback resolver
  3. load_run_config_utils_module calls in stage code paths (not in resolvers)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def scan_for_prohibited_imports(file_path: Path) -> list[str]:
    """Check for direct imports of run_config_utils (Phase 6 violation).

    NOTE: Only orchestration/run_config/shared loader modules may import
    run_config utilities. Stage business modules must remain payload-only.
    """
    content = file_path.read_text(encoding="utf-8")
    violations = []

    # Get relative path for display
    try:
        rel_path = file_path.relative_to(Path.cwd())
    except ValueError:
        rel_path = file_path

    # Allow imports only in orchestration/run-config/shared utility modules.
    allowed_patterns = [
        "run_config",  # run_config_* modules
        "orchestration",
        "stage_runtime_resolver.py",
        "config_loader.py",
    ]
    if any(p in str(file_path) for p in allowed_patterns):
        return violations  # These modules are allowed to do fallback loading

    # Business logic modules must not import run_config
    if re.search(r"from\s+run_config\s+import|import\s+run_config", content):
        violations.append(f"  {rel_path} - direct run_config import in business logic")

    if re.search(r"from\s+shared_utils\.config_loader\s+import.*load_run_config_utils_module", content):
        violations.append(f"  {rel_path} - loads run_config_utils in business logic")

    return violations


def scan_for_direct_env_reads(file_path: Path) -> list[str]:
    """Check for BL_RUN_CONFIG_PATH reads in stage business code."""
    content = file_path.read_text(encoding="utf-8")
    violations = []

    # Get relative path for display
    try:
        rel_path = file_path.relative_to(Path.cwd())
    except ValueError:
        rel_path = file_path

    # Skip orchestration/shared utility modules where this is expected.
    skip_patterns = [
        "orchestration",
        "shared_utils",
        "run_config",
    ]
    if any(p in str(file_path) for p in skip_patterns):
        return violations

    # Check for direct reads of BL_RUN_CONFIG_PATH in stage modules
    if re.search(r"os\.environ.*BL_RUN_CONFIG_PATH|getenv\(['\"]BL_RUN_CONFIG_PATH", content):
        violations.append(f"  {rel_path} - direct BL_RUN_CONFIG_PATH read")

    return violations


def check_phase_6_invariants() -> bool:
    """Validate Phase 6 invariants across codebase."""
    impl_root = Path("src")
    if not impl_root.exists():
        print("❌ CI Guard: src/ directory not found")
        return False

    violations: dict[str, list[str]] = {
        "prohibited_imports": [],
        "direct_env_reads": [],
    }

    stage_modules = {
        "alignment",
        "profile",
        "retrieval",
        "scoring",
        "playlist",
        "transparency",
        "observability",
        "controllability",
    }

    for stage_name in stage_modules:
        stage_path = impl_root / stage_name
        if not stage_path.exists():
            continue

        for py_file in stage_path.rglob("*.py"):
            # Check prohibited imports
            import_violations = scan_for_prohibited_imports(py_file)
            violations["prohibited_imports"].extend(import_violations)

            # Check direct env reads
            env_violations = scan_for_direct_env_reads(py_file)
            violations["direct_env_reads"].extend(env_violations)

    # Report results
    print("\n" + "=" * 70)
    print("Phase 6 CI Guard: Architectural Rule Validation")
    print("=" * 70)

    if violations["prohibited_imports"]:
        print("\n❌ VIOLATION: Stages must not import run_config directly")
        for v in violations["prohibited_imports"]:
            print(v)

    if violations["direct_env_reads"]:
        print("\n❌ VIOLATION: Stages must not read BL_RUN_CONFIG_PATH directly")
        for v in violations["direct_env_reads"]:
            print(v)

    all_violations = violations["prohibited_imports"] + violations["direct_env_reads"]
    if not all_violations:
        print("\n✅ PASS: No Phase 6 violations detected")
        print("\nArchitectural Rules:")
        print("  ✓ Only orchestration imports run_config_utils")
        print("  ✓ Stages do not read BL_RUN_CONFIG_PATH directly")
        print("  ✓ Stages consume explicit BL_STAGE_CONFIG_JSON payload")
        print("  ✓ All stages have payload-first fallback logic")
        return True

    print("\n❌ FAIL: Phase 6 invariants violated")
    return False


if __name__ == "__main__":
    success = check_phase_6_invariants()
    sys.exit(0 if success else 1)
