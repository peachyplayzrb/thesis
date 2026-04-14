#!/usr/bin/env python3

"""Active-suite wrapper that runs BL-014 checks in active mode."""

from __future__ import annotations

import sys

from suite import main as suite


def main() -> int:
    original_argv = sys.argv[:]
    try:
        sys.argv = [original_argv[0], "--mode", "active"]
        return suite()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
