#!/usr/bin/env python3
"""BL-007: Rule-based playlist assembly."""

import logging

from playlist.stage import PlaylistStage

logger = logging.getLogger(__name__)


def main() -> None:
    artifacts = PlaylistStage().run()
    logger.info(
        "BL-007 playlist assembly complete. Playlist: %d/%d tracks",
        artifacts.playlist_size,
        artifacts.target_size,
    )
    logger.info("Run ID: %s", artifacts.run_id)
    logger.info("Genre mix: %s", dict(artifacts.genre_mix))
    if artifacts.undersized_diagnostics["is_undersized"]:
        logger.warning("BL-007 produced an undersized playlist.")
        for reason in artifacts.undersized_diagnostics["reasons"]:
            logger.warning("  - %s", reason)


if __name__ == "__main__":
    main()
