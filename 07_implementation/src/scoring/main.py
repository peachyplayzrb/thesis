"""BL-006: Score candidates based on profile preference model."""

from __future__ import annotations

from scoring.stage import ScoringStage


def main() -> None:
    ScoringStage().run()


if __name__ == "__main__":
    main()
