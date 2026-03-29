from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from shared_utils.io_utils import load_csv_rows
from shared_utils.env_utils import env_bool
from alignment.runtime_scope import apply_input_scope_filters
from alignment.resolved_context import resolve_alignment_context
from alignment.matching import build_ds001_indices, match_events
from alignment.weighting import to_event_rows
from alignment.influence import inject_influence_tracks
from alignment.aggregation import aggregate_matched_events
from alignment.reporting import (
    build_and_write_summary,
    validate_match_rate,
    write_alignment_outputs,
    write_source_scope_manifest,
)


def parse_args() -> argparse.Namespace:
    from shared_utils.path_utils import impl_root

    impl_root_path = impl_root()

    parser = argparse.ArgumentParser(
        description="BL-003 DS-001: Build Spotify-aligned seed tables with full trace logging."
    )
    parser.add_argument(
        "--ds001-candidates",
        type=Path,
        default=impl_root_path / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv",
    )
    parser.add_argument(
        "--spotify-export-dir",
        type=Path,
        default=impl_root_path / "ingestion" / "outputs" / "spotify_api_export",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=impl_root_path / "alignment" / "outputs",
    )
    parser.add_argument(
        "--allow-missing-selected-sources",
        action="store_true",
        default=env_bool("BL003_ALLOW_MISSING_SELECTED_SOURCES", False),
        help="Do not fail when BL-002 selection indicates a source should exist but its flat CSV is missing.",
    )
    return parser.parse_args()


def load_optional_csv(path: Path) -> tuple[list[dict[str, str]], bool]:
    if not path.exists():
        return [], False
    return load_csv_rows(path), True


def load_export_selection(spotify_export_dir: Path) -> dict[str, object]:
    summary_path = spotify_export_dir / "spotify_export_run_summary.json"
    if not summary_path.exists():
        return {}
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"BL-003 could not parse BL-002 export summary: {summary_path}"
        ) from exc
    selection = payload.get("selection")
    if not isinstance(selection, dict):
        raise RuntimeError(
            f"BL-003 export summary missing required selection block: {summary_path}"
        )
    return selection


def main() -> None:
    args = parse_args()
    t0 = time.time()

    ds001_path = args.ds001_candidates
    spotify_dir = args.spotify_export_dir
    output_dir = args.output_dir

    if not ds001_path.exists():
        raise FileNotFoundError(f"DS-001 working dataset not found: {ds001_path}")

    top_path = spotify_dir / "spotify_top_tracks_flat.csv"
    saved_path = spotify_dir / "spotify_saved_tracks_flat.csv"
    playlist_items_path = spotify_dir / "spotify_playlist_items_flat.csv"
    recently_played_path = spotify_dir / "spotify_recently_played_flat.csv"

    top_rows, top_exists = load_optional_csv(top_path)
    saved_rows, saved_exists = load_optional_csv(saved_path)
    playlist_rows, playlist_exists = load_optional_csv(playlist_items_path)
    recent_rows, recent_exists = load_optional_csv(recently_played_path)

    context = resolve_alignment_context()
    runtime_scope = context.runtime_scope
    input_scope = context.input_scope

    selected_rows, scope_filter_stats = apply_input_scope_filters(
        top_rows, saved_rows, playlist_rows, recent_rows, input_scope,
    )

    export_selection = load_export_selection(spotify_dir)
    if runtime_scope["config_source"] == "run_config":
        expected_sources = {
            "top_tracks": bool(input_scope.get("include_top_tracks", True)),
            "saved_tracks": bool(input_scope.get("include_saved_tracks", True)),
            "playlist_items": bool(input_scope.get("include_playlists", True)),
            "recently_played": bool(input_scope.get("include_recently_played", True)),
        }
    else:
        expected_sources = {
            "top_tracks": bool(export_selection.get("include_top_tracks", False)),
            "saved_tracks": bool(export_selection.get("include_saved_tracks", False)),
            "playlist_items": bool(export_selection.get("include_playlists", False)),
            "recently_played": bool(export_selection.get("include_recently_played", False)),
        }
    available_sources = {
        "top_tracks": top_exists,
        "saved_tracks": saved_exists,
        "playlist_items": playlist_exists,
        "recently_played": recent_exists,
    }
    missing_selected_sources = [
        src for src, expected in expected_sources.items()
        if expected and not available_sources[src]
    ]
    if missing_selected_sources and not args.allow_missing_selected_sources:
        raise RuntimeError(
            "BL-003 strict selected-source check failed. Missing required source files from BL-002 selection: "
            f"{', '.join(missing_selected_sources)}. Re-run BL-002 export or pass "
            "--allow-missing-selected-sources to continue."
        )

    ds001_rows = load_csv_rows(ds001_path)
    by_spotify_id, by_title_artist, by_artist = build_ds001_indices(ds001_rows)
    by_ds001_id: dict[str, dict[str, str]] = {
        str(r.get("id", "")).strip(): r for r in ds001_rows if r.get("id", "").strip()
    }

    events: list[dict[str, str]] = []
    events.extend(to_event_rows("top_tracks", selected_rows["top_tracks"]))
    events.extend(to_event_rows("saved_tracks", selected_rows["saved_tracks"]))
    events.extend(to_event_rows("playlist_items", selected_rows["playlist_items"]))
    events.extend(to_event_rows("recently_played", selected_rows["recently_played"]))

    source_stats = {
        "top_tracks": {"file_present": top_exists, "rows_available": len(top_rows), "rows_selected": len(selected_rows["top_tracks"])},
        "saved_tracks": {"file_present": saved_exists, "rows_available": len(saved_rows), "rows_selected": len(selected_rows["saved_tracks"])},
        "playlist_items": {"file_present": playlist_exists, "rows_available": len(playlist_rows), "rows_selected": len(selected_rows["playlist_items"])},
        "recently_played": {"file_present": recent_exists, "rows_available": len(recent_rows), "rows_selected": len(selected_rows["recently_played"])},
    }

    trace_rows, matched_events, unmatched_rows, match_counts = match_events(
        events,
        by_spotify_id,
        by_title_artist,
        by_artist,
        context=context,
    )
    summary_counts = {"input_event_rows": len(events), **match_counts}

    influence_contract = inject_influence_tracks(
        matched_events,
        by_ds001_id,
        context=context,
    )

    aggregated = aggregate_matched_events(matched_events)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = write_alignment_outputs(
        output_dir, matched_events, aggregated, trace_rows, unmatched_rows
    )
    manifest_path = output_dir / "bl003_source_scope_manifest.json"
    write_source_scope_manifest(manifest_path, runtime_scope, input_scope, scope_filter_stats)
    output_paths["source_scope_manifest"] = manifest_path

    validate_match_rate(summary_counts, context.match_rate_min_threshold)

    summary_path = output_dir / "bl003_ds001_spotify_summary.json"
    elapsed_seconds = round(time.time() - t0, 3)
    build_and_write_summary(
        summary_path,
        elapsed_seconds=elapsed_seconds,
        ds001_path=ds001_path,
        spotify_dir=spotify_dir,
        top_path=top_path,
        saved_path=saved_path,
        playlist_items_path=playlist_items_path,
        recently_played_path=recently_played_path,
        export_selection=export_selection,
        runtime_scope=runtime_scope,
        input_scope=input_scope,
        influence_contract=influence_contract,
        expected_sources=expected_sources,
        available_sources=available_sources,
        missing_selected_sources=missing_selected_sources,
        allow_missing_selected_sources=bool(args.allow_missing_selected_sources),
        source_stats=source_stats,
        scope_filter_stats=scope_filter_stats,
        summary_counts=summary_counts,
        matched_events=matched_events,
        aggregated=aggregated,
        trace_rows=trace_rows,
        unmatched_rows=unmatched_rows,
        output_paths=output_paths,
        match_rate_min_threshold=context.match_rate_min_threshold,
        fuzzy_matching_controls=context.fuzzy_matching_controls,
    )

    print(f"input_event_rows={summary_counts['input_event_rows']}")
    print(f"matched_by_spotify_id={summary_counts['matched_by_spotify_id']}")
    print(f"matched_by_metadata={summary_counts['matched_by_metadata']}")
    print(f"matched_by_fuzzy={summary_counts.get('matched_by_fuzzy', 0)}")
    print(f"unmatched={summary_counts['unmatched']}")
    print(f"matched_events_rows={len(matched_events)}")
    print(f"seed_table_rows={len(aggregated)}")
    print(f"trace_rows={len(trace_rows)}")
    print(f"unmatched_rows={len(unmatched_rows)}")
    print(f"summary_path={summary_path}")


if __name__ == "__main__":
    main()
