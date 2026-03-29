#!/usr/bin/env python3
"""
BL-007: Rule-based playlist assembly.

Thin compatibility entrypoint wrapper over the class-based PlaylistStage.
"""

from playlist.stage import PlaylistStage


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    artifacts = PlaylistStage().run()
    print(
        f"BL-007 playlist assembly complete.  Playlist: "
        f"{artifacts.playlist_size}/{artifacts.target_size} tracks"
    )
    print(f"Run ID : {artifacts.run_id}")
    print(f"Genre mix : {dict(artifacts.genre_mix)}")
    if artifacts.undersized_diagnostics["is_undersized"]:
        print("WARNING: BL-007 produced an undersized playlist.")
        for reason in artifacts.undersized_diagnostics["reasons"]:
            print(f"  - {reason}")


if __name__ == "__main__":
    main()
