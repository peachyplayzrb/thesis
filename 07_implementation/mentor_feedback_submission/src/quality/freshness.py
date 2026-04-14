#!/usr/bin/env python3

"""Freshness-mode wrapper for BL-014 quality checks."""

from __future__ import annotations

import sys

from suite import main as suite


def main() -> int:
    original_argv = sys.argv[:]
    try:
        sys.argv = [original_argv[0], "--mode", "freshness"]
        return suite()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
