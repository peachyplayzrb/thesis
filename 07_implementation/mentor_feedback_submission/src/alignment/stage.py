from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alignment.aggregation import aggregate_matched_events
from alignment.constants import (
    ALIGNMENT_DEFAULT_RELATIVE_PATHS,
    ALIGNMENT_OUTPUT_FILENAMES,
    DEFAULT_SOURCE_RESILIENCE_POLICY,
    SOURCE_RESILIENCE_ALLOWED_MODES,
    SOURCE_RESILIENCE_REQUIRED,
    SOURCE_SCOPE_SPECS,
    SOURCE_TYPES,
    SPOTIFY_EXPORT_FILENAMES,
)
from alignment.influence import inject_influence_tracks
from alignment.match_pipeline import match_events
from alignment.models import (
    AlignmentPaths,
    AlignmentRunArtifacts,
    AlignmentSourceRows,
    AlignmentStructuralContract,
    AlignmentSummaryContext,
    AlignmentSummaryMetrics,
)
from alignment.resolved_context import AlignmentResolvedContext, resolve_alignment_context
from alignment.runtime_scope import apply_input_scope_filters
from alignment.user_csv_schema import normalize_user_csv_rows
from alignment.validation import validate_match_rate
from alignment.weighting import to_event_rows
from alignment.writers import (
    build_and_write_summary_from_context,
    build_seed_contract_payload,
    build_structural_contract_payload,
    write_alignment_outputs,
    write_source_scope_manifest,
)
from shared_utils.index_builder import build_ds001_indices, resolve_ds001_id
from shared_utils.io_utils import load_csv_rows
from shared_utils.path_utils import impl_root


@dataclass(frozen=True)
class _ScopeSelectionResult:
    selected_rows: dict[str, list[dict[str, str]]]
    scope_filter_stats: dict[str, Any]
    runtime_scope: dict[str, object]
    input_scope: dict[str, object]
    export_selection: dict[str, object]
    expected_sources: dict[str, bool]
    available_sources: dict[str, bool]
    source_resilience_policy: dict[str, str]
    missing_selected_sources: list[str]
    missing_required_sources: list[str]
    degraded_optional_sources: list[str]
    source_stats: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class _MatchAggregationResult:
    trace_rows: list[dict[str, Any]]
    matched_events: list[dict[str, Any]]
    unmatched_rows: list[dict[str, Any]]
    summary_counts: dict[str, int]
    unmatched_reason_counts: dict[str, int]
    influence_contract: dict[str, Any]
    aggregated: Any


class AlignmentStage:
    """Object-oriented BL-003 alignment workflow shell."""

    def __init__(
        self,
        root: Path | None = None,
        *,
        ds001_path: Path | None = None,
        spotify_dir: Path | None = None,
        output_dir: Path | None = None,
        allow_missing_selected_sources: bool = False,
    ) -> None:
        self.root = root if root is not None else impl_root()
        self._ds001_path_override = ds001_path
        self._spotify_dir_override = spotify_dir
        self._output_dir_override = output_dir
        self.allow_missing_selected_sources = allow_missing_selected_sources

    def resolve_paths(self) -> AlignmentPaths:
        d = ALIGNMENT_DEFAULT_RELATIVE_PATHS
        ds001 = self._ds001_path_override or self.root / d["ds001_candidates"]
        spotify = self._spotify_dir_override or self.root / d["spotify_export_dir"]
        out = self._output_dir_override or self.root / d["output_dir"]
        return AlignmentPaths(
            ds001_path=ds001,
            spotify_dir=spotify,
            output_dir=out,
            top_path=spotify / SPOTIFY_EXPORT_FILENAMES["top_tracks"],
            saved_path=spotify / SPOTIFY_EXPORT_FILENAMES["saved_tracks"],
            playlist_items_path=spotify / SPOTIFY_EXPORT_FILENAMES["playlist_items"],
            recently_played_path=spotify / SPOTIFY_EXPORT_FILENAMES["recently_played"],
            user_csv_path=spotify / SPOTIFY_EXPORT_FILENAMES["user_csv"],
            summary_path=out / ALIGNMENT_OUTPUT_FILENAMES["summary_json"],
            source_scope_manifest_path=out / ALIGNMENT_OUTPUT_FILENAMES["source_scope_manifest_json"],
        )

    @staticmethod
    def _count_unmatched_reasons(unmatched_rows: list[dict[str, Any]]) -> dict[str, int]:
        reason_counts: dict[str, int] = {}
        for row in unmatched_rows:
            reason = str(row.get("reason", "")).strip() or "unspecified"
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        return dict(sorted(reason_counts.items(), key=lambda item: item[0]))

    @staticmethod
    def resolve_runtime_controls() -> AlignmentResolvedContext:
        return resolve_alignment_context()

    @staticmethod
    def _load_export_summary_payload(spotify_export_dir: Path) -> dict[str, object]:
        summary_path = spotify_export_dir / "spotify_export_run_summary.json"
        if not summary_path.exists():
            return {}
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"BL-003 could not parse BL-002 export summary: {summary_path}"
            ) from exc
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def load_export_selection(spotify_export_dir: Path) -> dict[str, object]:
        payload = AlignmentStage._load_export_summary_payload(spotify_export_dir)
        if not payload:
            return {}
        summary_path = spotify_export_dir / "spotify_export_run_summary.json"
        selection = payload.get("selection")
        if not isinstance(selection, dict):
            raise RuntimeError(
                "BL-003 export summary missing required selection block: "
                f"{summary_path}"
            )
        return selection

    @staticmethod
    def load_export_source_outcomes(spotify_export_dir: Path) -> dict[str, dict[str, object]]:
        payload = AlignmentStage._load_export_summary_payload(spotify_export_dir)
        if not payload:
            return {}
        raw_outcomes = payload.get("source_outcomes")
        if not isinstance(raw_outcomes, dict):
            return {}
        return {
            str(source): dict(outcome)
            for source, outcome in raw_outcomes.items()
            if isinstance(outcome, dict)
        }

    @staticmethod
    def resolve_expected_sources(
        *,
        runtime_scope: dict[str, object],
        input_scope: dict[str, object],
        export_selection: dict[str, object],
    ) -> dict[str, bool]:
        if runtime_scope.get("config_source") == "run_config":
            return {
                source: bool(input_scope.get(str(SOURCE_SCOPE_SPECS[source]["input_scope_flag"]), True))
                for source in SOURCE_TYPES
            }
        return {
            source: bool(export_selection.get(str(SOURCE_SCOPE_SPECS[source]["export_selection_flag"]), False))
            for source in SOURCE_TYPES
        }

    def enforce_selected_source_requirements(
        self,
        *,
        expected_sources: dict[str, bool],
        available_sources: dict[str, bool],
        source_resilience_policy: dict[str, str],
    ) -> tuple[list[str], list[str], list[str]]:
        missing_selected_sources = [
            source
            for source, expected in expected_sources.items()
            if expected and not available_sources.get(source, False)
        ]

        missing_required_sources = [
            source
            for source in missing_selected_sources
            if source_resilience_policy.get(source, SOURCE_RESILIENCE_REQUIRED) == SOURCE_RESILIENCE_REQUIRED
        ]
        degraded_optional_sources = [
            source
            for source in missing_selected_sources
            if source not in missing_required_sources
        ]

        if missing_required_sources and not self.allow_missing_selected_sources:
            raise RuntimeError(
                "BL-003 strict selected-source check failed. Missing required source files from BL-002 selection: "
                f"{', '.join(missing_required_sources)}. Re-run BL-002 export or pass "
                "--allow-missing-selected-sources to continue."
            )
        return missing_selected_sources, missing_required_sources, degraded_optional_sources

    @staticmethod
    def resolve_source_resilience_policy(source_resilience_policy: Mapping[str, object] | None) -> dict[str, str]:
        resolved = dict(DEFAULT_SOURCE_RESILIENCE_POLICY)
        if isinstance(source_resilience_policy, dict):
            for source in SOURCE_TYPES:
                raw_mode = source_resilience_policy.get(source)
                if raw_mode is None:
                    continue
                mode = str(raw_mode).strip().lower()
                if mode in SOURCE_RESILIENCE_ALLOWED_MODES:
                    resolved[source] = mode
        return resolved

    def load_source_rows(self, paths: AlignmentPaths) -> AlignmentSourceRows:
        def load_if_present(path: Path) -> tuple[list[dict[str, str]], bool]:
            if not path.exists():
                return [], False
            return load_csv_rows(path), True

        top_rows, top_exists = load_if_present(paths.top_path)
        saved_rows, saved_exists = load_if_present(paths.saved_path)
        playlist_rows, playlist_exists = load_if_present(paths.playlist_items_path)
        recent_rows, recent_exists = load_if_present(paths.recently_played_path)

        user_csv_raw, user_csv_exists = load_if_present(paths.user_csv_path)
        if user_csv_exists and user_csv_raw:
            user_csv_rows, schema_report = normalize_user_csv_rows(user_csv_raw, paths.user_csv_path)
            print(
                f"BL-003 user_csv schema report: "
                f"mapped={schema_report['mapped']}, "
                f"unmapped={schema_report['unmapped']}, "
                f"viable={schema_report['viable']}"
            )
        else:
            user_csv_rows = []

        return AlignmentSourceRows(
            top_rows=top_rows,
            saved_rows=saved_rows,
            playlist_rows=playlist_rows,
            recent_rows=recent_rows,
            user_csv_rows=user_csv_rows,
            top_exists=top_exists,
            saved_exists=saved_exists,
            playlist_exists=playlist_exists,
            recent_exists=recent_exists,
            user_csv_exists=user_csv_exists,
        )

    def _resolve_scope_selection(
        self,
        *,
        source_rows: AlignmentSourceRows,
        context: AlignmentResolvedContext,
        paths: AlignmentPaths,
    ) -> _ScopeSelectionResult:
        runtime_scope = context.runtime_scope
        input_scope = dict(context.behavior_controls.input_scope)
        selected_rows, scope_filter_stats = apply_input_scope_filters(
            source_rows.top_rows,
            source_rows.saved_rows,
            source_rows.playlist_rows,
            source_rows.recent_rows,
            context.behavior_controls,
            user_csv_rows=source_rows.user_csv_rows,
        )

        export_selection = self.load_export_selection(paths.spotify_dir)
        expected_sources = self.resolve_expected_sources(
            runtime_scope=runtime_scope,
            input_scope=input_scope,
            export_selection=export_selection,
        )
        export_source_outcomes = self.load_export_source_outcomes(paths.spotify_dir)
        source_resilience_policy = self.resolve_source_resilience_policy(
            context.behavior_controls.source_resilience_policy,
        )

        available_sources = {
            source: bool(getattr(source_rows, str(SOURCE_SCOPE_SPECS[source]["exists_attr"])))
            for source in SOURCE_TYPES
        }
        for source in SOURCE_TYPES:
            if available_sources.get(source, False):
                continue
            outcome = export_source_outcomes.get(source, {})
            status = str(outcome.get("status", "")).strip().lower()
            if status in {"zero_results", "forbidden"}:
                available_sources[source] = True

        missing_selected_sources, missing_required_sources, degraded_optional_sources = self.enforce_selected_source_requirements(
            expected_sources=expected_sources,
            available_sources=available_sources,
            source_resilience_policy=source_resilience_policy,
        )

        source_stats = {
            source: {
                "file_present": bool(getattr(source_rows, str(SOURCE_SCOPE_SPECS[source]["exists_attr"]))),
                "rows_available": len(getattr(source_rows, str(SOURCE_SCOPE_SPECS[source]["rows_attr"]))),
                "rows_selected": len(selected_rows[source]),
                "export_outcome_status": str(
                    export_source_outcomes.get(source, {}).get("status", "unknown")
                ),
                "resilience_policy": source_resilience_policy[source],
                "degraded_missing": source in degraded_optional_sources,
                "missing_required": source in missing_required_sources,
            }
            for source in SOURCE_TYPES
        }
        return _ScopeSelectionResult(
            selected_rows=selected_rows,
            scope_filter_stats=scope_filter_stats,
            runtime_scope=runtime_scope,
            input_scope=input_scope,
            export_selection=export_selection,
            expected_sources=expected_sources,
            available_sources=available_sources,
            source_resilience_policy=source_resilience_policy,
            missing_selected_sources=missing_selected_sources,
            missing_required_sources=missing_required_sources,
            degraded_optional_sources=degraded_optional_sources,
            source_stats=source_stats,
        )

    def _run_matching_and_aggregation(
        self,
        *,
        paths: AlignmentPaths,
        selected_rows: dict[str, list[dict[str, str]]],
        context: AlignmentResolvedContext,
    ) -> _MatchAggregationResult:
        ds001_rows = load_csv_rows(paths.ds001_path)
        by_spotify_id, by_title_artist, by_artist = build_ds001_indices(ds001_rows)
        by_ds001_id = {
            resolve_ds001_id(row): row
            for row in ds001_rows
            if resolve_ds001_id(row)
        }
        events: list[dict[str, str]] = []
        for source in SOURCE_TYPES:
            events.extend(to_event_rows(source, selected_rows[source]))

        trace_rows, matched_events, unmatched_rows, match_counts = match_events(
            events,
            by_spotify_id,
            by_title_artist,
            by_artist,
            context=context,
        )
        summary_counts = {"input_event_rows": len(events), **match_counts}
        unmatched_reason_counts = self._count_unmatched_reasons(unmatched_rows)

        influence_contract = inject_influence_tracks(
            matched_events,
            by_ds001_id,
            context=context,
        )

        aggregated = aggregate_matched_events(
            matched_events,
            behavior_controls=context.behavior_controls,
        )
        return _MatchAggregationResult(
            trace_rows=trace_rows,
            matched_events=matched_events,
            unmatched_rows=unmatched_rows,
            summary_counts=summary_counts,
            unmatched_reason_counts=unmatched_reason_counts,
            influence_contract=influence_contract,
            aggregated=aggregated,
        )

    def _write_outputs_and_summary(
        self,
        *,
        elapsed_seconds: float,
        paths: AlignmentPaths,
        scope_result: _ScopeSelectionResult,
        match_result: _MatchAggregationResult,
        behavior_controls: Any,
        structural_contract_model: AlignmentStructuralContract,
    ) -> None:
        output_paths: dict[str, Path] = {}
        seed_contract = build_seed_contract_payload(behavior_controls)
        structural_contract = build_structural_contract_payload(structural_contract_model)

        validate_match_rate(match_result.summary_counts, float(behavior_controls.match_rate_min_threshold))

        summary_context = AlignmentSummaryContext(
            elapsed_seconds=elapsed_seconds,
            ds001_path=paths.ds001_path,
            spotify_dir=paths.spotify_dir,
            top_path=paths.top_path,
            saved_path=paths.saved_path,
            playlist_items_path=paths.playlist_items_path,
            recently_played_path=paths.recently_played_path,
            export_selection=scope_result.export_selection,
            runtime_scope=scope_result.runtime_scope,
            input_scope=scope_result.input_scope,
            influence_contract=match_result.influence_contract,
            expected_sources=scope_result.expected_sources,
            available_sources=scope_result.available_sources,
            source_resilience_policy=scope_result.source_resilience_policy,
            missing_selected_sources=scope_result.missing_selected_sources,
            missing_required_sources=scope_result.missing_required_sources,
            degraded_optional_sources=scope_result.degraded_optional_sources,
            allow_missing_selected_sources=self.allow_missing_selected_sources,
            source_stats=scope_result.source_stats,
            scope_filter_stats=scope_result.scope_filter_stats,
            behavior_controls=behavior_controls,
            structural_contract=structural_contract_model,
            metrics=AlignmentSummaryMetrics(
                summary_counts=match_result.summary_counts,
                matched_events_rows=len(match_result.matched_events),
                seed_table_rows=len(match_result.aggregated),
                trace_rows=len(match_result.trace_rows),
                unmatched_rows=len(match_result.unmatched_rows),
                unmatched_reason_counts=match_result.unmatched_reason_counts,
            ),
            output_paths=output_paths,
            match_rate_min_threshold=float(behavior_controls.match_rate_min_threshold),
            fuzzy_matching_controls=dict(behavior_controls.fuzzy_matching_controls),
        )

        output_paths = write_alignment_outputs(
            paths.output_dir,
            match_result.matched_events,
            match_result.aggregated,
            match_result.trace_rows,
            match_result.unmatched_rows,
        )
        write_source_scope_manifest(
            paths.source_scope_manifest_path,
            scope_result.runtime_scope,
            scope_result.input_scope,
            scope_result.scope_filter_stats,
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
        context: AlignmentResolvedContext = self.resolve_runtime_controls()
        scope_result = self._resolve_scope_selection(
            source_rows=source_rows,
            context=context,
            paths=paths,
        )

        match_result = self._run_matching_and_aggregation(
            paths=paths,
            selected_rows=scope_result.selected_rows,
            context=context,
        )

        paths.output_dir.mkdir(parents=True, exist_ok=True)
        elapsed_seconds = round(time.time() - t0, 3)
        self._write_outputs_and_summary(
            elapsed_seconds=elapsed_seconds,
            paths=paths,
            scope_result=scope_result,
            match_result=match_result,
            behavior_controls=context.behavior_controls,
            structural_contract_model=context.structural_contract,
        )

        return AlignmentRunArtifacts(
            summary_path=paths.summary_path,
            summary_counts=match_result.summary_counts,
            matched_events_rows=len(match_result.matched_events),
            seed_table_rows=len(match_result.aggregated),
            trace_rows=len(match_result.trace_rows),
            unmatched_rows=len(match_result.unmatched_rows),
        )
