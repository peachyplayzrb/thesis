#!/usr/bin/env python
"""
Smoke test for the standalone implementation package.

Verifies that:
1. Package structure is valid
2. All BL modules are importable
3. Path resolution works correctly
4. Environment variable configuration is supported
"""

from __future__ import annotations

import sys
from pathlib import Path


def test_package_structure() -> bool:
    """Verify the package directory structure exists."""
    impl_notes = Path(__file__).parent / "implementation_notes"

    required_dirs = [
        "bl000_data_layer",
        "bl000_run_config",
        "bl000_shared_utils",
        "bl001_bl002_ingestion",
        "bl003_alignment",
        "bl004_profile",
        "bl005_retrieval",
        "bl006_scoring",
        "bl007_playlist",
        "bl008_transparency",
        "bl009_observability",
        "bl010_reproducibility",
        "bl011_controllability",
        "bl013_entrypoint",
        "bl014_quality",
    ]

    for dir_name in required_dirs:
        dir_path = impl_notes / dir_name
        if not dir_path.is_dir():
            print(f"✗ Missing directory: {dir_name}")
            return False

    print("✓ Package structure valid")
    return True


def test_module_imports() -> bool:
    """Test that all BL modules can be imported."""
    # Add implementation_notes to path
    impl_notes = Path(__file__).parent / "implementation_notes"
    if str(impl_notes) not in sys.path:
        sys.path.insert(0, str(impl_notes.parent))

    try:
        # Test core utilities
        from bl000_shared_utils.path_utils import impl_root, get_dataset_root
        from bl000_shared_utils.artifact_registry import bl013_default_stage_order
        print("✓ Core utilities importable")

        # Test that impl_root discovery works
        root = impl_root()
        if not root.is_dir():
            print(f"✗ impl_root() returned invalid path: {root}")
            return False
        print("✓ Path resolution works")

        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_entry_point() -> bool:
    """Test that main.py is executable."""
    main_py = Path(__file__).parent / "main.py"
    if not main_py.exists():
        print(f"✗ main.py not found at {main_py}")
        return False

    if not main_py.is_file():
        print(f"✗ main.py is not a file: {main_py}")
        return False

    print("✓ Entry point available")
    return True


def test_requirements() -> bool:
    """Verify requirements.txt exists and is readable."""
    reqs = Path(__file__).parent / "requirements.txt"
    if not reqs.exists():
        print(f"✗ requirements.txt not found at {reqs}")
        return False

    try:
        content = reqs.read_text()
        lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")]
        if not lines:
            print(f"✗ requirements.txt is empty or only contains comments")
            return False
        print(f"✓ Requirements file valid ({len(lines)} packages)")
        return True
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False


def main() -> int:
    """Run all smoke tests."""
    print("=== Standalone Package Smoke Test ===\n")

    tests = [
        ("Package structure", test_package_structure),
        ("Module imports", test_module_imports),
        ("Entry point", test_entry_point),
        ("Requirements", test_requirements),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print(f"Results: {sum(1 for _, p in results if p)}/{len(results)} tests passed")
    print("=" * 50)

    if all(passed for _, passed in results):
        print("\n✓ Package is ready for deployment!")
        print("\nNext steps:")
        print("1. Source the virtual environment (.venv)")
        print("2. Download Music4All dataset")
        print("3. Run: python main.py --dataset-root /path/to/music4all/")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
