#!/usr/bin/env python3

from __future__ import annotations

from run_bl014_quality_suite import main as run_quality_suite


def main() -> int:
    return run_quality_suite(["--mode", "freshness"])


if __name__ == "__main__":
    raise SystemExit(main())