from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from alignment.constants import ALIGNMENT_OUTPUT_FILENAMES, SOURCE_SCOPE_SPECS, SOURCE_TYPES, SPOTIFY_EXPORT_FILENAMES
from alignment.aggregation import aggregate_matched_events
from alignment.influence import inject_influence_tracks
from alignment.index_builder import build_ds001_indices
from alignment.match_pipeline import match_events
from alignment.models import (
    AlignmentPaths,
    AlignmentRunArtifacts,
    AlignmentSourceRows,
    AlignmentStructuralContract,
    AlignmentSummaryContext,
    AlignmentSummaryMetrics,
)
from alignment.validation import validate_match_rate
from alignment.writers import (
    build_and_write_summary_from_context,
    build_seed_contract_payload,
    build_structural_contract_payload,
    write_alignment_outputs,
    write_source_scope_manifest,
)
from alignment.resolved_context import AlignmentResolvedContext, resolve_alignment_context
from alignment.runtime_scope import apply_input_scope_filters
from alignment.weighting import to_event_rows
from shared_utils.io_utils import load_csv_rows


class AlignmentStage:
    """Object-oriented BL-003 alignment workflow shell."""

    def __init__(
        self,
        *,
        ds001_path: Path,
        spotify_dir: Path,
        output_dir: Path,
        allow_missing_selected_sources: bool = False,
    ) -> None:
        self.ds001_path = ds001_path
        self.spotify_dir = spotify_dir
        self.output_dir = output_dir
        self.allow_missing_selected_sources = allow_missing_selected_sources

    def resolve_paths(self) -> AlignmentPaths:
        return AlignmentPaths(
            ds001_path=self.ds001_path,
            spotify_dir=self.spotify_dir,
            output_dir=self.output_dir,
            top_path=self.spotify_dir / SPOTIFY_EXPORT_FILENAMES["top_tracks"],
            saved_path=self.spotify_dir / SPOTIFY_EXPORT_FILENAMES["saved_tracks"],
            playlist_items_path=self.spotify_dir / SPOTIFY_EXPORT_FILENAMES["playlist_items"],
            recently_played_path=self.spotify_dir / SPOTIFY_EXPORT_FILENAMES["recently_played"],
            summary_path=self.output_dir / ALIGNMENT_OUTPUT_FILENAMES["summary_json"],
            source_scope_manifest_path=self.output_dir / ALIGNMENT_OUTPUT_FILENAMES["source_scope_manifest_json"],
        )

    @staticmethod
    def load_optional_csv(path: Path) -> tuple[list[dict[str, str]], bool]:
        if not path.exists():
            return [], False
        return load_csv_rows(path), True

    @staticmethod
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
                "BL-003 export summary missing required selection block: "
                f"{summary_path}"
            )
        return selection

    def load_source_rows(self, paths: AlignmentPaths) -> AlignmentSourceRows:
        top_rows, top_exists = self.load_optional_csv(paths.top_path)
        saved_rows, saved_exists = self.load_optional_csv(paths.saved_path)
        playlist_rows, playlist_exists = self.load_optional_csv(paths.playlist_items_path)
        recent_rows, recent_exists = self.load_optional_csv(paths.recently_played_path)

        return AlignmentSourceRows(
            top_rows=top_rows,
            saved_rows=saved_rows,
            playlist_rows=playlist_rows,
            recent_rows=recent_rows,
            top_exists=top_exists,
            saved_exists=saved_exists,
            playlist_exists=playlist_exists,
            recent_exists=recent_exists,
        )

    @staticmethod
    def resolve_expected_sources(
        *,
        runtime_scope: dict[str, object],
        input_scope: dict[str, object],
        export_selection: dict[str, object],
    ) -> dict[str, bool]:
        if runtime_scope["config_source"] == "run_config":
            return {
                source: bool(input_scope.get(str(SOURCE_SCOPE_SPECS[source]["input_scope_flag"]), True))
                for source in SOURCE_TYPES
            }
        return {
            source: bool(export_selection.get(str(SOURCE_SCOPE_SPECS[source]["export_selection_flag"]), False))
            for source in SOURCE_TYPES
        }

    @staticmethod
    def resolve_available_sources(rows: AlignmentSourceRows) -> dict[str, bool]:
        return {
            source: bool(getattr(rows, str(SOURCE_SCOPE_SPECS[source]["exists_attr"])))
            for source in SOURCE_TYPES
        }

    def enforce_selected_source_requirements(
        self,
        *,
        expected_sources: dict[str, bool],
        available_sources: dict[str, bool],
    ) -> list[str]:
        missing_selected_sources = [
            source
            for source, expected in expected_sources.items()
            if expected and not available_sources[source]
        ]
        if missing_selected_sources and not self.allow_missing_selected_sources:
            raise RuntimeError(
                "BL-003 strict selected-source check failed. Missing required source files from BL-002 selection: "
                f"{', '.join(missing_selected_sources)}. Re-run BL-002 export or pass "
                "--allow-missing-selected-sources to continue."
            )
        return missing_selected_sources

    @staticmethod
    def build_source_stats(
        source_rows: AlignmentSourceRows,
        selected_rows: dict[str, list[dict[str, str]]],
    ) -> dict[str, dict[str, int | bool]]:
        return {
            source: {
                "file_present": bool(getattr(source_rows, str(SOURCE_SCOPE_SPECS[source]["exists_attr"]))),
                "rows_available": len(getattr(source_rows, str(SOURCE_SCOPE_SPECS[source]["rows_attr"]))),
                "rows_selected": len(selected_rows[source]),
            }
            for source in SOURCE_TYPES
        }

    @staticmethod
    def build_event_rows(selected_rows: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
        events: list[dict[str, str]] = []
        for source in SOURCE_TYPES:
            events.extend(to_event_rows(source, selected_rows[source]))
        return events

    @staticmethod
    def build_by_ds001_id(ds001_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
        return {
            str(row.get("id", "")).strip(): row
            for row in ds001_rows
            if row.get("id", "").strip()
        }

    def _resolve_scope_selection(
        self,
        *,
        source_rows: AlignmentSourceRows,
        context: AlignmentResolvedContext,
        paths: AlignmentPaths,
    ) -> tuple[
        dict[str, list[dict[str, str]]],
        dict[str, Any],
        dict[str, object],
        dict[str, object],
        dict[str, object],
        dict[str, bool],
        dict[str, bool],
        list[str],
        dict[str, dict[str, int | bool]],
    ]:
        runtime_scope = context.runtime_scope
        input_scope = dict(context.behavior_controls.input_scope)
        selected_rows, scope_filter_stats = apply_input_scope_filters(
            source_rows.top_rows,
            source_rows.saved_rows,
            source_rows.playlist_rows,
            source_rows.recent_rows,
            context.behavior_controls,
        )

        export_selection = self.load_export_selection(paths.spotify_dir)
        expected_sources = self.resolve_expected_sources(
            runtime_scope=runtime_scope,
            input_scope=input_scope,
            export_selection=export_selection,
        )
        available_sources = self.resolve_available_sources(source_rows)
        missing_selected_sources = self.enforce_selected_source_requirements(
            expected_sources=expected_sources,
            available_sources=available_sources,
        )
        source_stats = self.build_source_stats(source_rows, selected_rows)
        return (
            selected_rows,
            scope_filter_stats,
            runtime_scope,
            input_scope,
            export_selection,
            expected_sources,
            available_sources,
            missing_selected_sources,
            source_stats,
        )

    def _run_matching_and_aggregation(
        self,
        *,
        paths: AlignmentPaths,
        selected_rows: dict[str, list[dict[str, str]]],
        context: AlignmentResolvedContext,
    ) -> tuple[
        list[dict[str, Any]],
        list[dict[str, Any]],
        list[dict[str, Any]],
        dict[str, int],
        dict[str, Any],
        dict[str, Any],
    ]:
        ds001_rows = load_csv_rows(paths.ds001_path)
        by_spotify_id, by_title_artist, by_artist = build_ds001_indices(ds001_rows)
        by_ds001_id = self.build_by_ds001_id(ds001_rows)
        events = self.build_event_rows(selected_rows)

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

        aggregated = aggregate_matched_events(
            matched_events,
            behavior_controls=context.behavior_controls,
        )
        return (
            trace_rows,
            matched_events,
            unmatched_rows,
            summary_counts,
            influence_contract,
            aggregated,
        )

    def _write_outputs_and_summary(
        self,
        *,
        elapsed_seconds: float,
        paths: AlignmentPaths,
        runtime_scope: dict[str, object],
        input_scope: dict[str, object],
        export_selection: dict[str, object],
        expected_sources: dict[str, bool],
        available_sources: dict[str, bool],
        missing_selected_sources: list[str],
        scope_filter_stats: dict[str, Any],
        source_stats: dict[str, dict[str, int | bool]],
        summary_counts: dict[str, int],
        trace_rows: list[dict[str, Any]],
        matched_events: list[dict[str, Any]],
        unmatched_rows: list[dict[str, Any]],
        influence_contract: dict[str, Any],
        aggregated: dict[str, Any],
        behavior_controls: Any,
        structural_contract_model: AlignmentStructuralContract,
    ) -> None:
        output_paths: dict[str, Path] = {}
        seed_contract = build_seed_contract_payload(behavior_controls)
        structural_contract = build_structural_contract_payload(structural_contract_model)

        validate_match_rate(summary_counts, float(behavior_controls.match_rate_min_threshold))

        summary_context = AlignmentSummaryContext(
            elapsed_seconds=elapsed_seconds,
            ds001_path=paths.ds001_path,
            spotify_dir=paths.spotify_dir,
            top_path=paths.top_path,
            saved_path=paths.saved_path,
            playlist_items_path=paths.playlist_items_path,
            recently_played_path=paths.recently_played_path,
            export_selection=export_selection,
            runtime_scope=runtime_scope,
            input_scope=input_scope,
            influence_contract=influence_contract,
            expected_sources=expected_sources,
            available_sources=available_sources,
            missing_selected_sources=missing_selected_sources,
            allow_missing_selected_sources=self.allow_missing_selected_sources,
            source_stats=source_stats,
            scope_filter_stats=scope_filter_stats,
            behavior_controls=behavior_controls,
            structural_contract=structural_contract_model,
            metrics=AlignmentSummaryMetrics(
                summary_counts=summary_counts,
                matched_events_rows=len(matched_events),
                seed_table_rows=len(aggregated),
                trace_rows=len(trace_rows),
                unmatched_rows=len(unmatched_rows),
            ),
            output_paths=output_paths,
            match_rate_min_threshold=float(behavior_controls.match_rate_min_threshold),
            fuzzy_matching_controls=dict(behavior_controls.fuzzy_matching_controls),
        )

        output_paths = write_alignment_outputs(
            paths.output_dir,
            matched_events,
            aggregated,
            trace_rows,
            unmatched_rows,
        )
        write_source_scope_manifest(
            paths.source_scope_manifest_path,
            runtime_scope,
            input_scope,
            scope_filter_stats,
            seed_contract=seed_contract,
            structural_contract=structural_contract,
        )
        output_paths["source_scope_manifest"] = paths.source_scope_manifest_path
        summary_context.output_paths.update(output_paths)
        build_and_write_summary_from_context(paths.summary_path, summary_context)

    def run(self) -> AlignmentRunArtifacts:
        t0 = time.time()
        paths = self.resolve_paths()
        if not paths.ds001_path.exists():
            raise FileNotFoundError(f"DS-001 working dataset not found: {paths.ds001_path}")

        source_rows = self.load_source_rows(paths)
        context: AlignmentResolvedContext = resolve_alignment_context()
        (
            selected_rows,
            scope_filter_stats,
            runtime_scope,
            input_scope,
            export_selection,
            expected_sources,
            available_sources,
            missing_selected_sources,
            source_stats,
        ) = self._resolve_scope_selection(
            source_rows=source_rows,
            context=context,
            paths=paths,
        )
        (
            trace_rows,
            matched_events,
            unmatched_rows,
            summary_counts,
            influence_contract,
            aggregated,
        ) = self._run_matching_and_aggregation(
            paths=paths,
            selected_rows=selected_rows,
            context=context,
        )

        paths.output_dir.mkdir(parents=True, exist_ok=True)
        elapsed_seconds = round(time.time() - t0, 3)
        self._write_outputs_and_summary(
            elapsed_seconds=elapsed_seconds,
            paths=paths,
            runtime_scope=runtime_scope,
            input_scope=input_scope,
            export_selection=export_selection,
            expected_sources=expected_sources,
            available_sources=available_sources,
            missing_selected_sources=missing_selected_sources,
            scope_filter_stats=scope_filter_stats,
            source_stats=source_stats,
            summary_counts=summary_counts,
            trace_rows=trace_rows,
            matched_events=matched_events,
            unmatched_rows=unmatched_rows,
            influence_contract=influence_contract,
            aggregated=aggregated,
            behavior_controls=context.behavior_controls,
            structural_contract_model=context.structural_contract,
        )

        return AlignmentRunArtifacts(
            summary_path=paths.summary_path,
            summary_counts=summary_counts,
            matched_events_rows=len(matched_events),
            seed_table_rows=len(aggregated),
            trace_rows=len(trace_rows),
            unmatched_rows=len(unmatched_rows),
        )
