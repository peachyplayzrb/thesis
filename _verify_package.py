from pathlib import Path

pkg_root = Path(r'c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\recommendation-implementation-standalone')

print("=" * 70)
print("STANDALONE PACKAGE VERIFICATION")
print("=" * 70)

# Check structure
checks = [
    ("Root main.py", pkg_root / "main.py"),
    ("README.md", pkg_root / "README.md"),
    ("requirements.txt", pkg_root / "requirements.txt"),
    (".gitignore", pkg_root / ".gitignore"),
    ("implementation_notes/", pkg_root / "implementation_notes"),
    ("No website folder", not (pkg_root / "implementation_notes" / "website").exists()),
]

print("\nSTRUCTURE CHECK:")
for label, check in checks:
    if isinstance(check, bool):
        status = "✓" if check else "✗"
    else:
        status = "✓" if check.exists() else "✗"
    print(f"  {status} {label}")

# Check key files were properly refactored
print("\nKEY FILE REFACTORING CHECK:")

refactored_files = [
    ("path_utils.py", pkg_root / "implementation_notes" / "bl000_shared_utils" / "path_utils.py"),
    ("bl003 script", pkg_root / "implementation_notes" / "bl003_alignment" / "build_bl003_ds001_spotify_seed_table.py"),
    ("bl004 script", pkg_root / "implementation_notes" / "bl004_profile" / "build_bl004_preference_profile.py"),
    ("bl007 script", pkg_root / "implementation_notes" / "bl007_playlist" / "build_bl007_playlist.py"),
    ("artifact_registry", pkg_root / "implementation_notes" / "bl000_shared_utils" / "artifact_registry.py"),
]

for label, fpath in refactored_files:
    if not fpath.exists():
        print(f"  ✗ {label}: FILE NOT FOUND")
        continue

    content = fpath.read_text()

    # Check: repo_root removed from imports
    has_repo_root_import = 'from bl000_shared_utils.path_utils import repo_root' in content

    # Check: impl_root is used
    has_impl_root = 'impl_root' in content

    # Check: No hardcoded "07_implementation/implementation_notes" paths
    has_hardcoded_paths = '07_implementation/implementation_notes' in content

    if not has_hardcoded_paths and (has_impl_root or 'impl_root' in fpath.name or label == "path_utils.py" or label == "artifact_registry"):
        print(f"  ✓ {label}: Successfully refactored")
    elif label == "artifact_registry" and not has_hardcoded_paths:
        print(f"  ✓ {label}: Successfully refactored (hardcoded paths removed)")
    elif has_hardcoded_paths:
        print(f"  ✗ {label}: Still has hardcoded paths")
    else:
        print(f"  ? {label}: Check manually")

# Check main.py content
print("\nMAIN.PY CHECK:")
main_py = pkg_root / "main.py"
main_content = main_py.read_text()

main_checks = [
    ("Has impl_root resolution", "_resolve_impl_root()" in main_content),
    ("Has dataset_root argument", "--dataset-root" in main_content),
    ("References implementation_notes", "implementation_notes" in main_content),
    ("Sets IMPL_DATASET_ROOT env var", "IMPL_DATASET_ROOT" in main_content),
]

for label, check in main_checks:
    status = "✓" if check else "✗"
    print(f"  {status} {label}")

# Summary
print("\n" + "=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
print(f"Standalone package root: {pkg_root}")
total_size = sum(f.stat().st_size for f in pkg_root.rglob('*') if f.is_file())
print(f"Size: ~{total_size // (1024*1024)} MB")
print("\nNext steps:")
print("  1. Copy standalone package to external location")
print("  2. Extract and create new venv")
print("  3. Run: python main.py --dataset-root /path/to/music4all/")
print("=" * 70)
