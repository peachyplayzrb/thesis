"""
Pytest configuration: add 07_implementation/src to sys.path so all stage
packages (alignment, shared_utils, …) are importable without an install step.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
