from __future__ import annotations

import csv
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from scoring.candidate_parsed import parse_candidate_attributes
from scoring.diagnostics import (
    build_confidence_impact_diagnostics,
    build_semantic_precision_diagnostics,
    build_score_distribution_diagnostics,
    contribution_breakdown,
)
from scoring.models import (
    NUMERIC_COMPONENTS,
    NUMERIC_FEATURE_SPECS,
    SCORED_CANDIDATE_FIELDS,
    ScoringArtifacts,
    ScoringContext,
    ScoringControls,
    ScoringInputs,
    ScoringPaths,
    context_from_mapping,
    controls_from_mapping,
)
from scoring.profile_extractor import build_component_weights, extract_profile_scoring_data
from scoring.runtime_controls import build_active_component_weights, resolve_bl006_runtime_controls
from scoring.scoring_engine import (
    compute_component_scores,
    compute_final_score,
    compute_weighted_contributions,
)
from shared_utils.io_utils import load_csv_rows, load_json, open_text_write, sha256_of_file, utc_now
from shared_utils.path_utils import impl_root
from shared_utils.stage_utils import ensure_paths_exist


class ScoringStage:
    """Object-oriented BL-006 workflow shell over scoring helpers."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    @staticmethod
    def _to_float(value: object, default: float = 0.0) -> float:
        try:
            return float(str(value))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _clamp_0_1(value: float) -> float:
        return max(0.0, min(1.0, value))

    def resolve_paths(self) -> ScoringPaths:
        return ScoringPaths(
            profile_path=self.root / "profile" / "outputs" / "bl004_preference_profile.json",
            filtered_candidates_path=self.root / "retrieval" / "outputs" / "bl005_filtered_candidates.csv",
            output_dir=self.root / "scoring" / "outputs",
        )

    @staticmethod
    def load_inputs(paths: ScoringPaths) -> ScoringInputs:
        profile = load_json(paths.profile_path)
        if not isinstance(profile, dict):
            raise RuntimeError("BL-006 profile artifact is malformed; expected JSON object")
        candidates_raw = load_csv_rows(paths.filtered_candidates_path)
        if not candidates_raw:
            raise RuntimeError("No BL-005 filtered candidates found for BL-006")
        candidates: list[dict[str, str]] = [
            {str(k): str(v) for k, v in row.items()}
            for row in candidates_raw
        ]
        return ScoringInputs(profile=profile, candidates=candidates)

    @staticmethod
    def resolve_runtime_controls(default_weights: dict[str, float] | None = None) -> ScoringControls:
        effective_defaults = default_weights if default_weights is not None else build_component_weights()
        payload = resolve_bl006_runtime_controls(effective_defaults)
        return controls_from_mapping(payload)

    @staticmethod
    def build_runtime_context(
        *,
        profile: dict[str, object],
        runtime_controls: ScoringControls | dict[str, object],
    ) -> ScoringContext:
        controls = (
            runtime_controls
            if isinstance(runtime_controls, ScoringControls)
            else controls_from_mapping(runtime_controls)
        )

        effective_component_weights = dict(controls.component_weights)
        numeric_threshold_overrides = dict(controls.numeric_thresholds)
        effective_numeric_specs = {
            key: {
                **spec,
                "threshold": float(
                    numeric_threshold_overrides.get(
                        key,
                        ScoringStage._to_float(spec.get("threshold", 0.0)),
                    )
                ),
            }
            for key, spec in NUMERIC_FEATURE_SPECS.items()
        }

        profile_scoring_data = extract_profile_scoring_data(profile, effective_numeric_specs)
        numeric_centers_obj = profile_scoring_data.get("numeric_centers")
        numeric_centers = numeric_centers_obj if isinstance(numeric_centers_obj, dict) else {}

        active_numeric_specs = {
            key: spec
            for key, spec in effective_numeric_specs.items()
            if key in numeric_centers
        }

        active_component_weights, weight_rebalance_diagnostics = build_active_component_weights(
            set(active_numeric_specs),
            effective_component_weights,
            NUMERIC_COMPONENTS,
        )
        if round(sum(active_component_weights.values()), 6) != 1.0:
            raise RuntimeError("BL-006 active component weights must sum to 1.0")

        numeric_confidence_by_feature_raw = profile_scoring_data.get("numeric_confidence_by_feature")
        numeric_confidence_by_feature = {
            str(k): ScoringStage._clamp_0_1(ScoringStage._to_float(v, 1.0))
            for k, v in dict(numeric_confidence_by_feature_raw).items()
            if str(k) in active_numeric_specs
        } if isinstance(numeric_confidence_by_feature_raw, dict) else {}
        profile_numeric_confidence_factor_base = ScoringStage._clamp_0_1(
            ScoringStage._to_float(profile_scoring_data.get("profile_numeric_confidence_factor", 1.0), 1.0)
        )
        semantic_precision_alpha_profile = max(
            0.0,
            ScoringStage._to_float(profile_scoring_data.get("semantic_precision_alpha", 0.35), 0.35),
        )

        lead_genre_strategy_raw = controls.lead_genre_strategy.strip().lower()
        lead_genre_strategy = (
            lead_genre_strategy_raw
            if lead_genre_strategy_raw in {"single_anchor", "weighted_top_lead_genres"}
            else "weighted_top_lead_genres"
        )
        semantic_overlap_strategy_raw = controls.semantic_overlap_strategy.strip().lower()
        semantic_overlap_strategy = (
            semantic_overlap_strategy_raw
            if semantic_overlap_strategy_raw in {"overlap_only", "precision_aware"}
            else "precision_aware"
        )
        semantic_precision_alpha_mode_raw = controls.semantic_precision_alpha_mode.strip().lower()
        semantic_precision_alpha_mode = (
            semantic_precision_alpha_mode_raw
            if semantic_precision_alpha_mode_raw in {"profile_adaptive", "fixed"}
            else "profile_adaptive"
        )
        semantic_precision_alpha_fixed = ScoringStage._clamp_0_1(controls.semantic_precision_alpha_fixed)
        semantic_precision_alpha = (
            semantic_precision_alpha_fixed
            if semantic_precision_alpha_mode == "fixed"
            else semantic_precision_alpha_profile
        )

        profile_numeric_confidence_mode_raw = controls.profile_numeric_confidence_mode.strip().lower()
        profile_numeric_confidence_mode = (
            profile_numeric_confidence_mode_raw
            if profile_numeric_confidence_mode_raw in {"direct", "blended"}
            else "direct"
        )
        profile_numeric_confidence_blend_weight = ScoringStage._clamp_0_1(
            controls.profile_numeric_confidence_blend_weight
        )
        if profile_numeric_confidence_mode == "blended":
            profile_numeric_confidence_factor = (
                profile_numeric_confidence_blend_weight * profile_numeric_confidence_factor_base
            ) + ((1.0 - profile_numeric_confidence_blend_weight) * 1.0)
        else:
            profile_numeric_confidence_factor = profile_numeric_confidence_factor_base
        enable_numeric_confidence_scaling = bool(controls.enable_numeric_confidence_scaling)
        numeric_confidence_floor = ScoringStage._clamp_0_1(controls.numeric_confidence_floor)

        return ScoringContext(
            signal_mode=dict(controls.signal_mode),
            effective_component_weights=effective_component_weights,
            active_numeric_specs=active_numeric_specs,
            profile_scoring_data=profile_scoring_data,
            active_component_weights=active_component_weights,
            weight_rebalance_diagnostics=weight_rebalance_diagnostics,
            numeric_confidence_by_feature=numeric_confidence_by_feature,
            profile_numeric_confidence_factor=profile_numeric_confidence_factor,
            semantic_precision_alpha=semantic_precision_alpha,
            lead_genre_strategy=lead_genre_strategy,
            semantic_overlap_strategy=semantic_overlap_strategy,
            semantic_precision_alpha_mode=semantic_precision_alpha_mode,
            semantic_precision_alpha_fixed=semantic_precision_alpha_fixed,
            enable_numeric_confidence_scaling=enable_numeric_confidence_scaling,
            numeric_confidence_floor=numeric_confidence_floor,
            profile_numeric_confidence_mode=profile_numeric_confidence_mode,
            profile_numeric_confidence_blend_weight=profile_numeric_confidence_blend_weight,
            emit_confidence_impact_diagnostics=bool(controls.emit_confidence_impact_diagnostics),
            emit_semantic_precision_diagnostics=bool(controls.emit_semantic_precision_diagnostics),
        )

    @staticmethod
    def score_candidates(
        *,
        candidates: list[dict[str, str]],
        runtime_context: ScoringContext | dict[str, object],
    ) -> list[dict[str, object]]:
        context = (
            runtime_context
            if isinstance(runtime_context, ScoringContext)
            else context_from_mapping(runtime_context)
        )

        scored_rows: list[dict[str, object]] = []
        for row in candidates:
            candidate_attrs = parse_candidate_attributes(row)
            component_scores = compute_component_scores(
                candidate_attrs,
                context.profile_scoring_data,
                context.active_numeric_specs,
                lead_genre_strategy=context.lead_genre_strategy,
                overlap_strategy=context.semantic_overlap_strategy,
                semantic_precision_alpha=context.semantic_precision_alpha,
            )
            weighted_contributions = compute_weighted_contributions(
                component_scores,
                context.active_component_weights,
                numeric_confidence_by_feature=context.numeric_confidence_by_feature,
                profile_numeric_confidence_factor=context.profile_numeric_confidence_factor,
                enable_numeric_confidence_scaling=context.enable_numeric_confidence_scaling,
                numeric_confidence_floor=context.numeric_confidence_floor,
                profile_numeric_confidence_mode=context.profile_numeric_confidence_mode,
                profile_numeric_confidence_blend_weight=context.profile_numeric_confidence_blend_weight,
            )
            final_score = compute_final_score(
                component_scores,
                context.active_component_weights,
                weighted_contributions=weighted_contributions,
            )
            matched_genres_raw = component_scores.get("matched_genres")
            matched_tags_raw = component_scores.get("matched_tags")
            matched_genres = [str(v) for v in matched_genres_raw] if isinstance(matched_genres_raw, list) else []
            matched_tags = [str(v) for v in matched_tags_raw] if isinstance(matched_tags_raw, list) else []

            scored_rows.append(
                {
                    "track_id": row.get("track_id", ""),
                    "lead_genre": candidate_attrs.get("lead_genre", ""),
                    "matched_genres": "|".join(matched_genres),
                    "matched_tags": "|".join(matched_tags),
                    "final_score": final_score,
                    "danceability_similarity": component_scores.get("danceability_similarity", 0.0),
                    "danceability_contribution": weighted_contributions.get("danceability_contribution", 0.0),
                    "energy_similarity": component_scores.get("energy_similarity", 0.0),
                    "energy_contribution": weighted_contributions.get("energy_contribution", 0.0),
                    "valence_similarity": component_scores.get("valence_similarity", 0.0),
                    "valence_contribution": weighted_contributions.get("valence_contribution", 0.0),
                    "tempo_similarity": component_scores.get("tempo_similarity", 0.0),
                    "tempo_contribution": weighted_contributions.get("tempo_contribution", 0.0),
                    "duration_ms_similarity": component_scores.get("duration_ms_similarity", 0.0),
                    "duration_ms_contribution": weighted_contributions.get("duration_ms_contribution", 0.0),
                    "popularity_similarity": component_scores.get("popularity_similarity", 0.0),
                    "popularity_contribution": weighted_contributions.get("popularity_contribution", 0.0),
                    "key_similarity": component_scores.get("key_similarity", 0.0),
                    "key_contribution": weighted_contributions.get("key_contribution", 0.0),
                    "mode_similarity": component_scores.get("mode_similarity", 0.0),
                    "mode_contribution": weighted_contributions.get("mode_contribution", 0.0),
                    "lead_genre_similarity": component_scores.get("lead_genre_similarity", 0.0),
                    "lead_genre_contribution": weighted_contributions.get("lead_genre_contribution", 0.0),
                    "genre_overlap_similarity": component_scores.get("genre_overlap_similarity", 0.0),
                    "genre_overlap_contribution": weighted_contributions.get("genre_overlap_contribution", 0.0),
                    "tag_overlap_similarity": component_scores.get("tag_overlap_similarity", 0.0),
                    "tag_overlap_contribution": weighted_contributions.get("tag_overlap_contribution", 0.0),
                }
            )

        scored_rows.sort(
            key=lambda item: (
                -ScoringStage._to_float(item.get("final_score", 0.0)),
                str(item.get("track_id", "")),
            )
        )
        for index, row in enumerate(scored_rows, start=1):
            row["rank"] = index
        return scored_rows

    @staticmethod
    def write_scored_csv(*, scored_rows: list[dict[str, object]], scored_path: Path) -> None:
        with open_text_write(scored_path, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=SCORED_CANDIDATE_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(scored_rows)

    @staticmethod
    def build_summary(
        *,
        run_id: str,
        elapsed_seconds: float,
        paths: ScoringPaths,
        runtime_context: ScoringContext | dict[str, object],
        scored_rows: list[dict[str, object]],
        distribution_diagnostics: dict[str, object],
        diagnostics_path: Path,
        scored_path: Path,
        confidence_impact_diagnostics: dict[str, object] | None = None,
    ) -> dict[str, object]:
        context = (
            runtime_context
            if isinstance(runtime_context, ScoringContext)
            else context_from_mapping(runtime_context)
        )

        top_candidates = [
            {
                "rank": row["rank"],
                "track_id": row["track_id"],
                "lead_genre": row["lead_genre"],
                "final_score": row["final_score"],
                "matched_genres": row["matched_genres"],
                "matched_tags": row["matched_tags"],
            }
            for row in scored_rows[:10]
        ]
        score_values = [ScoringStage._to_float(row.get("final_score", 0.0)) for row in scored_rows]
        top_100_rows = scored_rows[:100]
        top_500_rows = scored_rows[:500]

        return {
            "run_id": run_id,
            "task": "BL-006",
            "generated_at_utc": utc_now(),
            "input_artifacts": {
                "profile_path": str(paths.profile_path),
                "profile_sha256": sha256_of_file(paths.profile_path),
                "filtered_candidates_path": str(paths.filtered_candidates_path),
                "filtered_candidates_sha256": sha256_of_file(paths.filtered_candidates_path),
            },
            "config": {
                "signal_mode": dict(context.signal_mode),
                "numeric_thresholds": {
                    profile_column: spec["threshold"]
                    for profile_column, spec in context.active_numeric_specs.items()
                },
                "numeric_feature_mapping": {
                    profile_column: spec.get("candidate_column", profile_column)
                    for profile_column, spec in context.active_numeric_specs.items()
                },
                "base_component_weights": context.effective_component_weights,
                "active_component_weights": {
                    key: round(value, 6)
                    for key, value in context.active_component_weights.items()
                },
                "numeric_confidence_by_feature": {
                    key: round(value, 6)
                    for key, value in context.numeric_confidence_by_feature.items()
                },
                "profile_numeric_confidence_factor": round(
                    context.profile_numeric_confidence_factor,
                    6,
                ),
                "semantic_precision_alpha": round(context.semantic_precision_alpha, 6),
                "lead_genre_strategy": context.lead_genre_strategy,
                "semantic_overlap_strategy": context.semantic_overlap_strategy,
                "semantic_precision_alpha_mode": context.semantic_precision_alpha_mode,
                "semantic_precision_alpha_fixed": round(context.semantic_precision_alpha_fixed, 6),
                "enable_numeric_confidence_scaling": context.enable_numeric_confidence_scaling,
                "numeric_confidence_floor": round(context.numeric_confidence_floor, 6),
                "profile_numeric_confidence_mode": context.profile_numeric_confidence_mode,
                "profile_numeric_confidence_blend_weight": round(
                    context.profile_numeric_confidence_blend_weight,
                    6,
                ),
                "inactive_components": sorted(
                    set(context.effective_component_weights) - set(context.active_component_weights)
                ),
                "weight_rebalance_diagnostics": context.weight_rebalance_diagnostics,
                "lead_genre_normalization": "weighted token overlap against BL-004 top_lead_genres",
                "genre_overlap_normalization": "weighted overlap with unmatched-label precision penalty",
                "tag_overlap_normalization": "weighted overlap with unmatched-label precision penalty",
                "semantic_source": "ds001_tags_and_genres_columns",
            },
            "counts": {
                "candidates_scored": len(scored_rows),
            },
            "score_statistics": {
                "max_score": round(max(score_values), 6),
                "min_score": round(min(score_values), 6),
                "mean_score": round(statistics.mean(score_values), 6),
                "median_score": round(statistics.median(score_values), 6),
            },
            "component_balance": {
                "all_candidates": contribution_breakdown(scored_rows),
                "top_100": contribution_breakdown(top_100_rows),
                "top_500": contribution_breakdown(top_500_rows),
            },
            "score_distribution_diagnostics": distribution_diagnostics,
            "confidence_impact_diagnostics": confidence_impact_diagnostics or {},
            "top_candidates": top_candidates,
            "elapsed_seconds": round(elapsed_seconds, 3),
            "output_files": {
                "scored_candidates_path": str(scored_path),
                "score_distribution_diagnostics_path": str(diagnostics_path),
            },
        }

    def run(self) -> ScoringArtifacts:
        paths = self.resolve_paths()
        paths.output_dir.mkdir(parents=True, exist_ok=True)

        ensure_paths_exist([paths.profile_path, paths.filtered_candidates_path], stage_label="BL-006")
        inputs = self.load_inputs(paths)

        runtime_controls = self.resolve_runtime_controls(build_component_weights())
        runtime_context = self.build_runtime_context(
            profile=inputs.profile,
            runtime_controls=runtime_controls,
        )

        start_time = time.time()
        run_id = f"BL006-SCORE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

        scored_rows = self.score_candidates(
            candidates=inputs.candidates,
            runtime_context=runtime_context,
        )

        scored_path = paths.output_dir / "bl006_scored_candidates.csv"
        self.write_scored_csv(scored_rows=scored_rows, scored_path=scored_path)

        distribution_diagnostics = build_score_distribution_diagnostics(scored_rows)
        confidence_impact_diagnostics = build_confidence_impact_diagnostics(
            scored_rows,
            runtime_context.numeric_confidence_by_feature,
            runtime_context.profile_numeric_confidence_factor,
            enabled=runtime_context.emit_confidence_impact_diagnostics,
            numeric_confidence_floor=runtime_context.numeric_confidence_floor,
            profile_numeric_confidence_mode=runtime_context.profile_numeric_confidence_mode,
            profile_numeric_confidence_blend_weight=runtime_context.profile_numeric_confidence_blend_weight,
        )
        semantic_precision_diagnostics = build_semantic_precision_diagnostics(
            enabled=runtime_context.emit_semantic_precision_diagnostics,
            overlap_strategy=runtime_context.semantic_overlap_strategy,
            alpha_mode=runtime_context.semantic_precision_alpha_mode,
            alpha_effective=runtime_context.semantic_precision_alpha,
            alpha_fixed=runtime_context.semantic_precision_alpha_fixed,
        )
        diagnostics_path = paths.output_dir / "bl006_score_distribution_diagnostics.json"
        with open_text_write(diagnostics_path) as handle:
            json.dump(distribution_diagnostics, handle, indent=2, ensure_ascii=True)

        summary = self.build_summary(
            run_id=run_id,
            elapsed_seconds=time.time() - start_time,
            paths=paths,
            runtime_context=runtime_context,
            scored_rows=scored_rows,
            distribution_diagnostics=distribution_diagnostics,
            confidence_impact_diagnostics=confidence_impact_diagnostics,
            diagnostics_path=diagnostics_path,
            scored_path=scored_path,
        )
        summary["semantic_precision_diagnostics"] = semantic_precision_diagnostics

        summary["output_hashes_sha256"] = {
            "bl006_scored_candidates.csv": sha256_of_file(scored_path),
            "bl006_score_distribution_diagnostics.json": sha256_of_file(diagnostics_path),
        }
        summary["summary_hash_note"] = (
            "summary file hash collected separately in experiment logging to avoid recursive self-reference"
        )
        summary_path = paths.output_dir / "bl006_score_summary.json"
        with open_text_write(summary_path) as handle:
            json.dump(summary, handle, indent=2, ensure_ascii=True)

        print("BL-006 candidate scoring complete.")
        if runtime_context.weight_rebalance_diagnostics["rebalanced"]:
            print("WARNING: BL-006 rebalanced component weights.")
            print(
                "  original_active_weight_sum="
                f"{runtime_context.weight_rebalance_diagnostics['active_weight_sum_pre_normalization']}"
            )
        print(f"scored_candidates={scored_path}")
        print(f"score_summary={summary_path}")

        return ScoringArtifacts(
            scored_path=scored_path,
            diagnostics_path=diagnostics_path,
            summary_path=summary_path,
        )
