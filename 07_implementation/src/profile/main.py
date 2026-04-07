"""BL-004: Build user preference profile from aligned seed data."""

from __future__ import annotations

from profile.stage import ProfileStage


def main() -> None:
    ProfileStage().run()


if __name__ == "__main__":
    main()
