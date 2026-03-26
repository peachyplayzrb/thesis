from __future__ import annotations

"""
Legacy BL-006 entrypoint preserved for backward compatibility.

This shim delegates to the maintained BL-006 implementation so older scripts
that still invoke this filename keep working.
"""

from bl006_scoring.build_bl006_scored_candidates import main


if __name__ == "__main__":
    main()
