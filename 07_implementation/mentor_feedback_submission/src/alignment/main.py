"""BL-003 entry point for aligning Spotify interaction history to DS-001 tracks."""

from __future__ import annotations

import argparse
from pathlib import Path

from alignment.constants import ALIGNMENT_DEFAULT_RELATIVE_PATHS
from alignment.stage import AlignmentStage


def parse_args() -> argparse.Namespace:
    from shared_utils.path_utils import impl_root

    impl_root_path = impl_root()

    parser = argparse.ArgumentParser(
        description="BL-003 DS-001: Build Spotify-aligned seed tables with full trace logging."
    )
    parser.add_argument(
        "--ds001-candidates",
        type=Path,
        default=impl_root_path / ALIGNMENT_DEFAULT_RELATIVE_PATHS["ds001_candidates"],
    )
    parser.add_argument(
        "--spotify-export-dir",
        type=Path,
        default=impl_root_path / ALIGNMENT_DEFAULT_RELATIVE_PATHS["spotify_export_dir"],
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=impl_root_path / ALIGNMENT_DEFAULT_RELATIVE_PATHS["output_dir"],
    )
    parser.add_argument(
        "--allow-missing-selected-sources",
        action="store_true",
        help="Do not fail when BL-002 selection indicates a source should exist but its flat CSV is missing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts = AlignmentStage(
        ds001_path=args.ds001_candidates,
        spotify_dir=args.spotify_export_dir,
        output_dir=args.output_dir,
        allow_missing_selected_sources=bool(args.allow_missing_selected_sources),
    ).run()

    print(f"input_event_rows={artifacts.summary_counts['input_event_rows']}")
    print(f"matched_by_spotify_id={artifacts.summary_counts['matched_by_spotify_id']}")
    print(f"matched_by_metadata={artifacts.summary_counts['matched_by_metadata']}")
    print(f"matched_by_fuzzy={artifacts.summary_counts.get('matched_by_fuzzy', 0)}")
    print(f"unmatched={artifacts.summary_counts['unmatched']}")
    print(f"matched_events_rows={artifacts.matched_events_rows}")
    print(f"seed_table_rows={artifacts.seed_table_rows}")
    print(f"trace_rows={artifacts.trace_rows}")
    print(f"unmatched_rows={artifacts.unmatched_rows}")
    print(f"summary_path={artifacts.summary_path}")


if __name__ == "__main__":
    main()
