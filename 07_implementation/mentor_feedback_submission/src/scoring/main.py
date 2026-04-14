"""BL-006 entry point for scoring retrieved candidates against the profile."""

from __future__ import annotations

from scoring.stage import ScoringStage


def main() -> None:
    ScoringStage().run()


if __name__ == "__main__":
    main()
