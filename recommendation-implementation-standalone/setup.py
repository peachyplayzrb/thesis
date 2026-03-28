"""
Setup script for the recommendation system standalone implementation.

This package is intended for academic review and reproduction of the
recommendation system research. It includes the complete pipeline and
supporting utilities for systematic playlist generation.
"""

from setuptools import setup
from pathlib import Path

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = [line.strip() for line in requirements_path.read_text().split("\n") if line.strip() and not line.startswith("#")]

setup(
    name="recommendation-implementation-standalone",
    version="1.0.0",
    description="Standalone, reproducible playlist recommendation system implementation",
    long_description="Complete implementation of a systematic music recommendation pipeline with full transparency and controllability for academic review",
    author="Research Implementation",
    python_requires=">=3.10",
    packages=[
        "implementation_notes",
        "implementation_notes.bl000_data_layer",
        "implementation_notes.bl000_run_config",
        "implementation_notes.bl000_shared_utils",
        "implementation_notes.bl001_bl002_ingestion",
        "implementation_notes.bl003_alignment",
        "implementation_notes.bl004_profile",
        "implementation_notes.bl005_retrieval",
        "implementation_notes.bl006_scoring",
        "implementation_notes.bl007_playlist",
        "implementation_notes.bl008_transparency",
        "implementation_notes.bl009_observability",
        "implementation_notes.bl010_reproducibility",
        "implementation_notes.bl011_controllability",
        "implementation_notes.bl013_entrypoint",
        "implementation_notes.bl014_quality",
    ],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "recommendation-impl=implementation_notes.bl013_entrypoint.run_bl013_pipeline_entrypoint:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Multimedia :: Sound/Audio",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
