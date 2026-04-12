from __future__ import annotations

import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from playlist.io_layer import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SCORED_CANDIDATES_PATH,
    read_scored_candidates,
    write_assembly_trace,
    write_detail_log,
    write_playlist,
    write_report,
)
from playlist.models import (
    PlaylistAggregation,
    PlaylistArtifacts,
    PlaylistContext,
    PlaylistControls,
    PlaylistInputs,
    PlaylistPaths,
    controls_from_mapping,
)
from playlist.reporting import (
    build_assembly_detail_log,
    build_assembly_pressure_diagnostics,
    build_opportunity_cost_diagnostics,
    build_rank_continuity_diagnostics,
    build_undersized_diagnostics,
)
from playlist.rules import assemble_bucketed
from playlist.runtime_controls import resolve_bl007_runtime_controls
from shared_utils.io_utils import sha256_of_file, utc_now
from shared_utils.env_utils import env_path
from shared_utils.path_utils import impl_root
from shared_utils.parsing import safe_float, safe_int
from shared_utils.stage_utils import ensure_paths_exist


class PlaylistStage:
    """Object-oriented BL-007 workflow shell over the existing playlist helpers."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    def resolve_paths(self) -> PlaylistPaths:
        scored_candidates_path = env_path(
            "BL007_SCORED_CANDIDATES_PATH",
            self.root / DEFAULT_SCORED_CANDIDATES_PATH,
        )
        output_dir = env_path("BL007_OUTPUT_DIR", self.root / DEFAULT_OUTPUT_DIR)
        return PlaylistPaths(
            scored_candidates_path=scored_candidates_path,
            output_dir=output_dir,
        )

    @staticmethod
    def load_inputs(paths: PlaylistPaths) -> PlaylistInputs:
        candidates = read_scored_candidates(paths.scored_candidates_path)
        return PlaylistInputs(candidates=candidates)

    @staticmethod
    def resolve_runtime_controls() -> PlaylistControls:
        return controls_from_mapping(resolve_bl007_runtime_controls())

    @staticmethod
    def build_runtime_context(controls: PlaylistControls) -> PlaylistContext:
        return PlaylistContext(
            target_size=controls.target_size,
            min_score_threshold=controls.min_score_threshold,
            max_per_genre=controls.max_per_genre,
            max_consecutive=controls.max_consecutive,
            utility_strategy=controls.utility_strategy,
            utility_weights=dict(controls.utility_weights),
            adaptive_limits=dict(controls.adaptive_limits),
            controlled_relaxation=dict(controls.controlled_relaxation),
            lead_genre_fallback_strategy=controls.lead_genre_fallback_strategy,
            use_component_contributions_for_tiebreak=controls.use_component_contributions_for_tiebreak,
            use_semantic_strength_for_tiebreak=controls.use_semantic_strength_for_tiebreak,
            emit_opportunity_cost_metrics=controls.emit_opportunity_cost_metrics,
            detail_log_top_k=controls.detail_log_top_k,
            influence_enabled=controls.influence_enabled,
            influence_track_ids=set(controls.influence_track_ids),
            influence_policy_mode=controls.influence_policy_mode,
            influence_reserved_slots=controls.influence_reserved_slots,
            influence_allow_genre_cap_override=controls.influence_allow_genre_cap_override,
            influence_allow_consecutive_override=controls.influence_allow_consecutive_override,
            influence_allow_score_threshold_override=controls.influence_allow_score_threshold_override,
        )

    @staticmethod
    def aggregate(*, candidates: list[dict[str, object]], context: PlaylistContext) -> PlaylistAggregation:
        rule_hits: Counter[str] = Counter()
        playlist, trace_rows = assemble_bucketed(
            candidates=candidates,
            target_size=context.target_size,
            min_score_threshold=context.min_score_threshold,
            max_per_genre=context.max_per_genre,
            max_consecutive=context.max_consecutive,
            rule_hits=rule_hits,
            utility_strategy=context.utility_strategy,
            utility_weights=dict(context.utility_weights),
            adaptive_limits=dict(context.adaptive_limits),
            controlled_relaxation=dict(context.controlled_relaxation),
            lead_genre_fallback_strategy=context.lead_genre_fallback_strategy,
            use_component_contributions_for_tiebreak=context.use_component_contributions_for_tiebreak,
            use_semantic_strength_for_tiebreak=context.use_semantic_strength_for_tiebreak,
            influence_enabled=context.influence_enabled,
            influence_track_ids=set(context.influence_track_ids),
            influence_policy_mode=context.influence_policy_mode,
            influence_reserved_slots=context.influence_reserved_slots,
            influence_allow_genre_cap_override=context.influence_allow_genre_cap_override,
            influence_allow_consecutive_override=context.influence_allow_consecutive_override,
            influence_allow_score_threshold_override=context.influence_allow_score_threshold_override,
        )
        return PlaylistAggregation(
            playlist=playlist,
            trace_rows=trace_rows,
            rule_hits=dict(rule_hits),
        )

    @staticmethod
    def _build_playlist_payload(
        *,
        run_id: str,
        elapsed_seconds: float,
        context: PlaylistContext,
        playlist: list[dict[str, object]],
    ) -> dict[str, object]:
        return {
            "run_id": run_id,
            "generated_at_utc": utc_now(),
            "elapsed_seconds": elapsed_seconds,
            "config": {
                "target_size": context.target_size,
                "min_score_threshold": context.min_score_threshold,
                "max_per_genre": context.max_per_genre,
                "max_consecutive": context.max_consecutive,
                "utility_strategy": context.utility_strategy,
                "utility_weights": dict(context.utility_weights),
                "adaptive_limits": dict(context.adaptive_limits),
                "controlled_relaxation": dict(context.controlled_relaxation),
                "lead_genre_fallback_strategy": context.lead_genre_fallback_strategy,
                "use_component_contributions_for_tiebreak": context.use_component_contributions_for_tiebreak,
                "use_semantic_strength_for_tiebreak": context.use_semantic_strength_for_tiebreak,
                "emit_opportunity_cost_metrics": context.emit_opportunity_cost_metrics,
                "detail_log_top_k": context.detail_log_top_k,
                "influence_enabled": context.influence_enabled,
                "influence_track_ids": sorted(context.influence_track_ids),
                "influence_policy_mode": context.influence_policy_mode,
                "influence_reserved_slots": context.influence_reserved_slots,
                "influence_allow_genre_cap_override": context.influence_allow_genre_cap_override,
                "influence_allow_consecutive_override": context.influence_allow_consecutive_override,
                "influence_allow_score_threshold_override": context.influence_allow_score_threshold_override,
            },
            "playlist_length": len(playlist),
            "tracks": playlist,
        }

    @staticmethod
    def _build_report_payload(
        *,
        run_id: str,
        elapsed_seconds: float,
        paths: PlaylistPaths,
        playlist_payload: dict[str, object],
        aggregation: PlaylistAggregation,
        candidates_evaluated: int,
        playlist_path: Path,
        trace_path: Path,
        detail_log_path: Path,
    ) -> tuple[dict[str, object], dict[str, object], dict[str, int], dict[str, object]]:
        included = [row for row in aggregation.trace_rows if row["decision"] == "included"]
        excluded = [row for row in aggregation.trace_rows if row["decision"] != "included"]
        config_obj = playlist_payload.get("config")
        config: dict[str, object] = config_obj if isinstance(config_obj, dict) else {}
        genre_mix = Counter(
            str(track.get("lead_genre", ""))
            for track in aggregation.playlist
            if str(track.get("lead_genre", ""))
        )

        undersized_diagnostics = build_undersized_diagnostics(
            target_size=safe_int(config.get("target_size"), 0),
            playlist_size=len(aggregation.playlist),
            candidates_evaluated=candidates_evaluated,
            trace_rows=aggregation.trace_rows,
        )
        rank_continuity_diagnostics = build_rank_continuity_diagnostics(aggregation.playlist)
        assembly_pressure_diagnostics = build_assembly_pressure_diagnostics(aggregation.trace_rows)
        output_artifact_hashes = {
            "playlist.json": sha256_of_file(playlist_path),
            "bl007_assembly_trace.csv": sha256_of_file(trace_path),
        }

        report: dict[str, object] = {
            "run_id": run_id,
            "generated_at_utc": playlist_payload["generated_at_utc"],
            "elapsed_seconds": elapsed_seconds,
            "config": config,
            "counts": {
                "candidates_evaluated": candidates_evaluated,
                "tracks_included": len(included),
                "tracks_excluded": len(excluded),
            },
            "rule_hits": dict(aggregation.rule_hits),
            "undersized_playlist_warning": undersized_diagnostics,
            "playlist_genre_mix": dict(genre_mix),
            "playlist_score_range": {
                "max": round(max(safe_float(track.get("final_score")) for track in aggregation.playlist), 6)
                if aggregation.playlist
                else None,
                "min": round(min(safe_float(track.get("final_score")) for track in aggregation.playlist), 6)
                if aggregation.playlist
                else None,
            },
            "rank_continuity_diagnostics": rank_continuity_diagnostics,
            "assembly_pressure_diagnostics": assembly_pressure_diagnostics,
            "input_artifact_hashes": {
                "bl006_scored_candidates.csv": sha256_of_file(paths.scored_candidates_path),
            },
            "output_artifact_hashes": output_artifact_hashes,
        }
        if bool(config.get("emit_opportunity_cost_metrics", False)):
            report["opportunity_cost_diagnostics"] = build_opportunity_cost_diagnostics(
                aggregation.trace_rows,
                top_k_examples=10,
            )
        detail_log = build_assembly_detail_log(
            aggregation.trace_rows,
            top_k=safe_int(config.get("detail_log_top_k"), 100),
        )
        return report, undersized_diagnostics, dict(genre_mix), detail_log

    def run(self) -> PlaylistArtifacts:
        start_time = time.time()
        paths = self.resolve_paths()
        paths.output_dir.mkdir(parents=True, exist_ok=True)

        ensure_paths_exist([paths.scored_candidates_path], stage_label="BL-007")
        inputs = self.load_inputs(paths)
        controls = self.resolve_runtime_controls()
        context = self.build_runtime_context(controls)

        aggregation = self.aggregate(
            candidates=[dict(candidate) for candidate in inputs.candidates],
            context=context,
        )

        elapsed_seconds = round(time.time() - start_time, 3)
        now = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        run_id = f"BL007-ASSEMBLE-{now}"

        playlist_payload = self._build_playlist_payload(
            run_id=run_id,
            elapsed_seconds=elapsed_seconds,
            context=context,
            playlist=aggregation.playlist,
        )

        playlist_path = paths.output_dir / "playlist.json"
        write_playlist(playlist_path, playlist_payload)

        trace_path = paths.output_dir / "bl007_assembly_trace.csv"
        write_assembly_trace(trace_path, aggregation.trace_rows)

        detail_log_path = paths.output_dir / "bl007_assembly_detail_log.json"
        report_path = paths.output_dir / "bl007_assembly_report.json"

        report, undersized_diagnostics, genre_mix, detail_log = self._build_report_payload(
            run_id=run_id,
            elapsed_seconds=elapsed_seconds,
            paths=paths,
            playlist_payload=playlist_payload,
            aggregation=aggregation,
            candidates_evaluated=len(inputs.candidates),
            playlist_path=playlist_path,
            trace_path=trace_path,
            detail_log_path=detail_log_path,
        )
        write_detail_log(detail_log_path, detail_log)
        output_hashes = report.get("output_artifact_hashes")
        if isinstance(output_hashes, dict):
            output_hashes["bl007_assembly_detail_log.json"] = sha256_of_file(detail_log_path)
        write_report(report_path, report)

        return PlaylistArtifacts(
            playlist_path=playlist_path,
            trace_path=trace_path,
            report_path=report_path,
            detail_log_path=detail_log_path,
            run_id=run_id,
            target_size=context.target_size,
            playlist_size=len(aggregation.playlist),
            genre_mix=genre_mix,
            undersized_diagnostics=undersized_diagnostics,
        )
