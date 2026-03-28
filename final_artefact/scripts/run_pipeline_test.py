#!/usr/bin/env python3
"""Lightweight smoke test for the BL-013 pipeline entrypoint."""

import subprocess
import sys
from pathlib import Path

def run_pipeline():
    """Run the pipeline entrypoint script and return its exit code."""
    # File is under 07_implementation/scripts; repo root is two levels up.
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "07_implementation" / "implementation_notes" / "bl013_entrypoint" / "run_bl013_pipeline_entrypoint.py"
    
    print(f"Running pipeline from: {script_path}")
    print(f"File exists: {script_path.exists()}")
    
    if not script_path.exists():
        print(f"ERROR: Pipeline script not found at {script_path}")
        return 1
    
    cmd = [sys.executable, str(script_path)]
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=repo_root)
    return result.returncode

if __name__ == "__main__":
    exit_code = run_pipeline()
    sys.exit(exit_code)
