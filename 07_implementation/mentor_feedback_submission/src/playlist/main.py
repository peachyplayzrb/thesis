#!/usr/bin/env python3
"""BL-007: Rule-based playlist assembly."""

import logging

from playlist.stage import PlaylistStage


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


logger = logging.getLogger(__name__)


def main() -> None:
    artifacts = PlaylistStage().run()
    logger.info(
        "BL-007 playlist assembly complete. Playlist: %d/%d tracks",
        artifacts.playlist_size,
        artifacts.target_size,
    )
    logger.info("Run ID: %s", artifacts.run_id)
    logger.info("Genre mix: %s", artifacts.genre_mix)
    undersized_diagnostics = artifacts.undersized_diagnostics if isinstance(artifacts.undersized_diagnostics, dict) else {}
    if bool(undersized_diagnostics.get("is_undersized", False)):
        logger.warning("BL-007 produced an undersized playlist.")
        for reason in _string_list(undersized_diagnostics.get("reasons")):
            logger.warning("  - %s", reason)


if __name__ == "__main__":
    main()
