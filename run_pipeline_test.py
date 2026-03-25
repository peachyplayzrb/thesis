#!/usr/bin/env python3
"""Quick test of the pipeline to validate Phase 1 refactoring."""

import subprocess
import sys
from pathlib import Path

def run_pipeline():
    """Run the pipeline entrypoint."""
    # Get absolute path to pipeline script
    script_path = Path(__file__).parent / "07_implementation" / "implementation_notes" / "bl013_entrypoint" / "run_bl013_pipeline_entrypoint.py"
    
    print(f"Running pipeline from: {script_path}")
    print(f"File exists: {script_path.exists()}")
    
    if not script_path.exists():
        print(f"ERROR: Pipeline script not found at {script_path}")
        return 1
    
    cmd = [sys.executable, str(script_path)]
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode

if __name__ == "__main__":
    exit_code = run_pipeline()
    sys.exit(exit_code)
