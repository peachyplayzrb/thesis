"""
Setup script for the recommendation system standalone implementation.

This package is intended for academic review and reproduction of the
recommendation system research. It includes the complete pipeline and
supporting utilities for systematic playlist generation.
"""

from setuptools import find_packages, setup
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
    packages=find_packages(include=["src", "src.*"]),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "recommendation-impl=src.orchestration.main:main",
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
