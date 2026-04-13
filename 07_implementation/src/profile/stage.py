from __future__ import annotations

import csv
import json
import logging
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from alignment.constants import (
    ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION,
    ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION,
)
from profile.models import ProfileAggregation, ProfileArtifacts, ProfileControls, ProfileInputs, ProfilePaths
from profile.runtime_controls import resolve_bl004_runtime_controls
from shared_utils.artifact_registry import bl003_required_paths
from shared_utils.constants import (
    DEFAULT_INCLUDE_INTERACTION_TYPES,
)
from shared_utils.io_utils import load_csv_rows, open_text_write, parse_csv_labels, parse_float, sha256_of_file, utc_now
from shared_utils.path_utils import impl_root


NUMERIC_FEATURE_COLUMNS: list[str] = [
    "danceability",
    "energy",
    "valence",
    "tempo",
    "key",
    "mode",
    "popularity",
    "duration_ms",
    "release",
]

SUMMARY_FEATURE_COLUMNS: list[str] = [
    "danceability",
    "energy",
    "valence",
    "tempo",
]

BL004_REQUIRED_SEED_COLUMNS: list[str] = [
    "ds001_id",
    "spotify_track_ids",
    "interaction_types",
    "preference_weight_sum",
    "interaction_count_sum",
    "tags",
    "genres",
    "artist",
    "song",
    *NUMERIC_FEATURE_COLUMNS,
]

BL004_PROFILE_SCHEMA_VERSION = "bl004-profile-v2"
BL004_SUMMARY_SCHEMA_VERSION = "bl004-summary-v2"
BL004_OUTPUT_CONTRACT_VERSION = "bl004-output-contract-v2"


class ProfileStage:
    """Object-oriented BL-004 profile workflow shell."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    def infer_user_id_from_ingestion(self) -> str | None:
        profile_path = (
            self.root
            / "ingestion"
            / "outputs"
            / "spotify_api_export"
            / "spotify_profile.json"
        )
        if not profile_path.exists():
            return None
        try:
            payload = json.loads(profile_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        user_id = payload.get("id") if isinstance(payload, dict) else None
        if isinstance(user_id, str) and user_id.strip():
            return user_id.strip()
        return None

    @staticmethod
    def resolve_lead_genre(genres: list[str], tags: list[str]) -> str:
        if genres:
            return genres[0]
        if tags:
            return tags[0]
        return ""

    @staticmethod
    def sorted_weight_map(weight_map: dict[str, float], limit: int) -> list[dict[str, float | str]]:
        ordered = sorted(weight_map.items(), key=lambda item: (-item[1], item[0]))
        return [
            {"label": label, "weight": round(weight, 6)}
            for label, weight in ordered[:limit]
        ]

    @staticmethod
    def circular_mean_key(sum_x: float, sum_y: float) -> float | None:
        if sum_x == 0.0 and sum_y == 0.0:
            return None
        angle = math.atan2(sum_y, sum_x)
        if angle < 0.0:
            angle += 2.0 * math.pi
        return (angle / (2.0 * math.pi)) * 12.0

    @staticmethod
    def _sanitize_controls(controls: dict[str, object]) -> ProfileControls:
        return ProfileControls(
            config_source=str(controls.get("config_source") or "environment"),
            run_config_path=(
                str(controls["run_config_path"])
                if controls.get("run_config_path")
                else None
            ),
            run_config_schema_version=(
                str(controls["run_config_schema_version"])
                if controls.get("run_config_schema_version")
                else None
            ),
            input_scope=(
                {str(k): v for k, v in controls["input_scope"].items()}  # type: ignore[union-attr]
            ),
            top_tag_limit=int(str(controls["top_tag_limit"])),
            top_genre_limit=int(str(controls["top_genre_limit"])),
            top_lead_genre_limit=int(str(controls["top_lead_genre_limit"])),
            confidence_weighting_mode=str(controls["confidence_weighting_mode"]),
            confidence_bin_high_threshold=float(str(controls["confidence_bin_high_threshold"])),
            confidence_bin_medium_threshold=float(str(controls["confidence_bin_medium_threshold"])),
            interaction_attribution_mode=str(controls["interaction_attribution_mode"]),
            emit_profile_policy_diagnostics=bool(controls["emit_profile_policy_diagnostics"]),
            user_id=str(controls["user_id"]),
            include_interaction_types=list(
                controls["include_interaction_types"]  # type: ignore[arg-type]
            ),
        )

    def resolve_runtime_controls(self) -> ProfileControls:
        inferred_user_id = self.infer_user_id_from_ingestion()
        controls = resolve_bl004_runtime_controls(inferred_user_id=inferred_user_id)
        return self._sanitize_controls(controls)

    def resolve_paths(self) -> ProfilePaths:
        output_dir = self.root / "profile" / "outputs"
        bl003_paths = bl003_required_paths(self.root)
        return ProfilePaths(
            seed_table_path=bl003_paths["seed_table"],
            bl003_summary_path=bl003_paths["summary"],
            bl003_manifest_path=bl003_paths["source_scope_manifest"],
            output_dir=output_dir,
            seed_trace_path=output_dir / "bl004_seed_trace.csv",
            profile_path=output_dir / "bl004_preference_profile.json",
            summary_path=output_dir / "profile_summary.json",
        )

    @staticmethod
    def _load_required_json_object(path: Path, label: str) -> dict[str, object]:
        if not path.exists():
            raise RuntimeError(f"BL-004 missing required {label}: {path}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"BL-004 could not parse required {label}: {path}") from exc
        if not isinstance(payload, dict):
            raise RuntimeError(f"BL-004 expected object payload for {label}: {path}")
        return {str(key): value for key, value in payload.items()}

    @staticmethod
    def _extract_contract_payload(
        summary_payload: dict[str, object],
        manifest_payload: dict[str, object],
    ) -> tuple[dict[str, object], dict[str, object], str, str]:
        inputs_raw = summary_payload.get("inputs")
        inputs = dict(inputs_raw) if isinstance(inputs_raw, dict) else {}

        seed_contract_raw = inputs.get("seed_contract")
        seed_contract = dict(seed_contract_raw) if isinstance(seed_contract_raw, dict) else {}
        structural_contract_raw = inputs.get("structural_contract")
        structural_contract = (
            dict(structural_contract_raw)
            if isinstance(structural_contract_raw, dict)
            else {}
        )

        manifest_seed_raw = manifest_payload.get("seed_contract")
        manifest_seed = dict(manifest_seed_raw) if isinstance(manifest_seed_raw, dict) else {}
        manifest_structural_raw = manifest_payload.get("structural_contract")
        manifest_structural = (
            dict(manifest_structural_raw)
            if isinstance(manifest_structural_raw, dict)
            else {}
        )

        if not seed_contract:
            seed_contract = dict(manifest_seed)
        if not structural_contract:
            structural_contract = dict(manifest_structural)
        if not seed_contract:
            raise RuntimeError("BL-004 expected BL-003 seed_contract in summary or manifest")
        if not structural_contract:
            raise RuntimeError("BL-004 expected BL-003 structural_contract in summary or manifest")

        seed_hash = str(seed_contract.get("contract_hash") or manifest_seed.get("contract_hash") or "")
        structural_hash = str(
            structural_contract.get("contract_hash")
            or manifest_structural.get("contract_hash")
            or ""
        )
        if not seed_hash:
            raise RuntimeError("BL-004 expected BL-003 seed contract hash")
        if not structural_hash:
            raise RuntimeError("BL-004 expected BL-003 structural contract hash")

        seed_schema = str(seed_contract.get("seed_contract_schema_version") or "")
        structural_schema = str(
            structural_contract.get("structural_contract_schema_version") or ""
        )
        if seed_schema != ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION:
            raise RuntimeError(
                "BL-004 BL-003 seed contract schema mismatch: "
                f"expected={ALIGNMENT_SEED_CONTRACT_SCHEMA_VERSION} observed={seed_schema}"
            )
        if structural_schema != ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION:
            raise RuntimeError(
                "BL-004 BL-003 structural contract schema mismatch: "
                f"expected={ALIGNMENT_STRUCTURAL_CONTRACT_SCHEMA_VERSION} observed={structural_schema}"
            )

        return seed_contract, structural_contract, seed_hash, structural_hash

    @staticmethod
    def _validate_seed_table_schema(
        seed_rows: list[dict[str, object]],
        structural_contract: dict[str, object],
    ) -> None:
        if not seed_rows:
            raise RuntimeError("No DS-001 seed rows found for BL-004 input")

        fieldnames_raw = structural_contract.get("seed_table_fieldnames")
        expected_fieldnames = (
            [str(value) for value in fieldnames_raw if str(value).strip()]
            if isinstance(fieldnames_raw, list)
            else []
        )
        if not expected_fieldnames:
            raise RuntimeError("BL-004 expected structural_contract.seed_table_fieldnames")

        actual_columns = set(seed_rows[0].keys())
        missing_structural = [
            fieldname
            for fieldname in expected_fieldnames
            if fieldname not in actual_columns
        ]
        if missing_structural:
            raise RuntimeError(
                "BL-004 seed table schema mismatch with BL-003 structural contract; missing columns: "
                + ", ".join(sorted(missing_structural))
            )

        missing_required = [
            fieldname
            for fieldname in BL004_REQUIRED_SEED_COLUMNS
            if fieldname not in actual_columns
        ]
        if missing_required:
            raise RuntimeError(
                "BL-004 seed table missing required profile columns: "
                + ", ".join(sorted(missing_required))
            )

    @staticmethod
    def _clamp_confidence(raw_value: object) -> float:
        parsed = parse_float(str(raw_value))
        if parsed is None:
            return 1.0
        return max(0.0, min(1.0, parsed))

    @staticmethod
    def _safe_rate(numerator: float, denominator: float, precision: int = 6) -> float:
        if denominator <= 0:
            return 0.0
        return round(numerator / denominator, precision)

    @staticmethod
    def _normalize_int_mapping(raw_obj: object) -> dict[str, int]:
        if not isinstance(raw_obj, dict):
            return {}
        normalized: dict[str, int] = {}
        for key, value in raw_obj.items():
            parsed = parse_float(str(value))
            normalized[str(key)] = int(parsed) if parsed is not None else 0
        return normalized

    @staticmethod
    def _extract_bl003_quality(summary_payload: dict[str, object]) -> dict[str, int | float]:
        counts_raw = summary_payload.get("counts")
        counts = dict(counts_raw) if isinstance(counts_raw, dict) else {}
        input_event_rows = int(parse_float(str(counts.get("input_event_rows", ""))) or 0)
        matched_by_spotify_id = int(parse_float(str(counts.get("matched_by_spotify_id", ""))) or 0)
        matched_by_metadata = int(parse_float(str(counts.get("matched_by_metadata", ""))) or 0)
        matched_by_fuzzy = int(parse_float(str(counts.get("matched_by_fuzzy", ""))) or 0)
        unmatched = int(parse_float(str(counts.get("unmatched", ""))) or 0)
        matched_total = matched_by_spotify_id + matched_by_metadata + matched_by_fuzzy
        match_rate = ProfileStage._safe_rate(matched_total, input_event_rows, precision=4)
        return {
            "input_event_rows": input_event_rows,
            "matched_by_spotify_id": matched_by_spotify_id,
            "matched_by_metadata": matched_by_metadata,
            "matched_by_fuzzy": matched_by_fuzzy,
            "unmatched": unmatched,
            "matched_total": matched_total,
            "match_rate": match_rate,
        }

    @staticmethod
    def _compute_coverage_rate_by_source(
        rows_selected: dict[str, int],
        rows_available: dict[str, int],
    ) -> dict[str, float]:
        rates: dict[str, float] = {}
        all_sources = set(rows_selected.keys()) | set(rows_available.keys())
        for source in sorted(all_sources):
            selected = float(rows_selected.get(source, 0))
            available = float(rows_available.get(source, 0))
            rates[source] = ProfileStage._safe_rate(selected, available, precision=6)
        return rates

    @staticmethod
    def _compute_entropy(weight_map: dict[str, float]) -> float:
        positive_weights = [value for value in weight_map.values() if value > 0.0]
        if len(positive_weights) <= 1:
            return 0.0
        total_weight = sum(positive_weights)
        if total_weight <= 0.0:
            return 0.0
        probabilities = [weight / total_weight for weight in positive_weights]
        entropy = -sum(prob * math.log(prob) for prob in probabilities if prob > 0.0)
        max_entropy = math.log(len(probabilities))
        return ProfileStage._safe_rate(entropy, max_entropy, precision=6)

    @staticmethod
    def _build_numeric_confidence_block(
        numeric_observations: dict[str, int],
        matched_seed_count: int,
        missing_numeric_track_count: int,
    ) -> dict[str, object]:
        confidence_by_feature = {
            feature: ProfileStage._safe_rate(float(observed), float(matched_seed_count), precision=6)
            for feature, observed in numeric_observations.items()
        }
        return {
            "observations_by_feature": dict(numeric_observations),
            "confidence_by_feature": confidence_by_feature,
            "missing_numeric_track_count": int(missing_numeric_track_count),
        }

    @staticmethod
    def _build_interaction_attribution_block(
        aggregation: ProfileAggregation,
        controls: ProfileControls,
    ) -> dict[str, object]:
        contribution_by_type = {
            interaction_type: {
                "effective_weight": round(aggregation.attribution_weight_by_type.get(interaction_type, 0.0), 6),
                "interaction_count": round(
                    aggregation.attribution_interaction_count_by_type.get(interaction_type, 0.0),
                    6,
                ),
                "row_share": round(aggregation.attribution_row_share_by_type.get(interaction_type, 0.0), 6),
            }
            for interaction_type in sorted(aggregation.attribution_weight_by_type.keys())
        }
        return {
            "policy_name": controls.interaction_attribution_mode,
            "mixed_interaction_row_count": aggregation.mixed_interaction_row_count,
            "contribution_by_type": contribution_by_type,
            "filtered_types_requested": list(controls.include_interaction_types),
        }

    @staticmethod
    def _resolve_confidence_weight_multiplier(confidence: float, mode: str) -> float:
        if mode == "none":
            return 1.0
        if mode == "direct_confidence":
            return confidence
        return 0.5 + 0.5 * confidence

    @staticmethod
    def _resolve_attribution_shares(
        selected_interaction_types: list[str],
        primary_interaction_type: str,
        mode: str,
    ) -> dict[str, float]:
        if not selected_interaction_types:
            return {}
        if mode == "primary_type_only":
            return {primary_interaction_type: 1.0}
        split_fraction = 1.0 / float(len(selected_interaction_types))
        return {interaction_type: split_fraction for interaction_type in selected_interaction_types}

    @staticmethod
    def _build_profile_signal_vector(
        aggregation: ProfileAggregation,
        bl003_quality: dict[str, int | float],
    ) -> dict[str, float]:
        history_effective_weight = aggregation.attribution_weight_by_type.get("history", 0.0)
        influence_effective_weight = aggregation.attribution_weight_by_type.get("influence", 0.0)
        total_effective_weight = aggregation.total_effective_weight
        return {
            "total_effective_weight": round(total_effective_weight, 6),
            "history_weight_share": ProfileStage._safe_rate(
                history_effective_weight,
                total_effective_weight,
                precision=6,
            ),
            "influence_weight_share": ProfileStage._safe_rate(
                influence_effective_weight,
                total_effective_weight,
                precision=6,
            ),
            "alignment_match_rate": float(bl003_quality.get("match_rate", 0.0) or 0.0),
            "top_genre_entropy": ProfileStage._compute_entropy(aggregation.genre_weights),
            "top_tag_entropy": ProfileStage._compute_entropy(aggregation.tag_weights),
        }

    @staticmethod
    def _build_canonical_blocks(
        aggregation: ProfileAggregation,
        controls: ProfileControls,
        inputs: ProfileInputs,
    ) -> dict[str, object]:
        bl003_quality = dict(inputs.bl003_quality) or ProfileStage._extract_bl003_quality(inputs.bl003_summary)
        rows_selected = dict(inputs.bl003_rows_selected) or ProfileStage._normalize_int_mapping(
            inputs.bl003_manifest.get("rows_selected")
        )
        rows_available = dict(inputs.bl003_rows_available) or ProfileStage._normalize_int_mapping(
            inputs.bl003_manifest.get("rows_available")
        )
        coverage_rate_by_source = dict(inputs.bl003_coverage_rate_by_source) or ProfileStage._compute_coverage_rate_by_source(
            rows_selected,
            rows_available,
        )
        return {
            "bl003_quality": bl003_quality,
            "source_coverage": {
                "rows_selected": rows_selected,
                "rows_available": rows_available,
                "coverage_rate_by_source": coverage_rate_by_source,
            },
            "interaction_attribution": ProfileStage._build_interaction_attribution_block(
                aggregation,
                controls,
            ),
            "numeric_confidence": ProfileStage._build_numeric_confidence_block(
                aggregation.numeric_observations,
                aggregation.matched_seed_count,
                len(aggregation.missing_numeric_track_ids),
            ),
            "profile_signal_vector": ProfileStage._build_profile_signal_vector(
                aggregation,
                inputs.bl003_quality,
            ),
        }

    @staticmethod
    def _parse_selected_interaction_types(
        row: dict[str, object],
        include_interaction_types: set[str],
    ) -> list[str]:
        raw_itypes = str(row.get("interaction_types", "") or row.get("interaction_type", "")).strip()
        row_interaction_types = (
            {t.strip() for t in raw_itypes.split("|") if t.strip()}
            if raw_itypes
            else {"history"}
        )
        return sorted(row_interaction_types.intersection(include_interaction_types))

    @staticmethod
    def _resolve_primary_interaction_type(selected_interaction_types: list[str]) -> str:
        return "influence" if "influence" in selected_interaction_types else "history"

    @staticmethod
    def load_inputs(paths: ProfilePaths) -> ProfileInputs:
        seed_rows = load_csv_rows(paths.seed_table_path)
        summary_payload = ProfileStage._load_required_json_object(
            paths.bl003_summary_path,
            "BL-003 summary",
        )
        manifest_payload = ProfileStage._load_required_json_object(
            paths.bl003_manifest_path,
            "BL-003 source scope manifest",
        )
        (
            seed_contract,
            structural_contract,
            seed_contract_hash,
            structural_contract_hash,
        ) = ProfileStage._extract_contract_payload(summary_payload, manifest_payload)

        normalized_rows: list[dict[str, object]] = [
            {str(k): v for k, v in row.items()}
            for row in seed_rows
        ]
        ProfileStage._validate_seed_table_schema(normalized_rows, structural_contract)
        rows_selected = ProfileStage._normalize_int_mapping(manifest_payload.get("rows_selected"))
        rows_available = ProfileStage._normalize_int_mapping(manifest_payload.get("rows_available"))
        bl003_quality = ProfileStage._extract_bl003_quality(summary_payload)

        return ProfileInputs(
            seed_rows=normalized_rows,
            bl003_summary=summary_payload,
            bl003_manifest=manifest_payload,
            bl003_seed_contract=seed_contract,
            bl003_structural_contract=structural_contract,
            bl003_seed_contract_hash=seed_contract_hash,
            bl003_structural_contract_hash=structural_contract_hash,
            bl003_quality=bl003_quality,
            bl003_rows_selected=rows_selected,
            bl003_rows_available=rows_available,
            bl003_coverage_rate_by_source=ProfileStage._compute_coverage_rate_by_source(
                rows_selected,
                rows_available,
            ),
        )

    @staticmethod
    def aggregate_inputs(inputs: ProfileInputs, controls: ProfileControls) -> ProfileAggregation:
        include_interaction_types = set(controls.include_interaction_types)

        numeric_sums = {column: 0.0 for column in NUMERIC_FEATURE_COLUMNS}
        numeric_weights = {column: 0.0 for column in NUMERIC_FEATURE_COLUMNS}
        tag_weights: dict[str, float] = {}
        genre_weights: dict[str, float] = {}
        lead_genre_weights: dict[str, float] = {}
        seed_trace_rows: list[dict[str, object]] = []

        counts_by_type = {"history": 0, "influence": 0}
        weight_by_type = {"history": 0.0, "influence": 0.0}
        interaction_count_sum_by_type = {"history": 0, "influence": 0}
        numeric_observations = {column: 0 for column in NUMERIC_FEATURE_COLUMNS}
        missing_numeric_track_ids: list[str] = []
        blank_track_id_row_count = 0
        confidence_adjusted_weight_sum = 0.0
        confidence_bins = {
            "high_0_9_plus": 0,
            "medium_0_5_to_0_9": 0,
            "low_below_0_5": 0,
        }
        match_method_counts = {
            "spotify_id_exact": int(inputs.bl003_quality.get("matched_by_spotify_id", 0) or 0),
            "metadata_fallback": int(inputs.bl003_quality.get("matched_by_metadata", 0) or 0),
            "fuzzy_title_artist": int(inputs.bl003_quality.get("matched_by_fuzzy", 0) or 0),
        }
        history_preference_weight_sum = 0.0
        influence_preference_weight_sum = 0.0
        history_interaction_count_sum_value = 0.0
        influence_interaction_count_sum_value = 0.0
        mixed_interaction_row_count = 0
        primary_type_attribution_row_count = 0
        confidence_fallback_row_count = 0
        defaulted_interaction_type_row_count = 0
        synthetic_interaction_count_row_count = 0
        synthetic_history_weight_row_count = 0
        synthetic_influence_weight_row_count = 0
        attribution_weight_by_type = {"history": 0.0, "influence": 0.0}
        attribution_interaction_count_by_type = {"history": 0.0, "influence": 0.0}
        attribution_row_share_by_type = {"history": 0.0, "influence": 0.0}
        high_confidence_threshold = controls.confidence_bin_high_threshold
        medium_confidence_threshold = controls.confidence_bin_medium_threshold
        key_circular_sum_x = 0.0
        key_circular_sum_y = 0.0

        for index, row in enumerate(inputs.seed_rows, start=1):
            track_id = str(row.get("ds001_id", "")).strip()
            spotify_ids = str(row.get("spotify_track_ids", "")).strip().split("|")
            spotify_id = next((item for item in spotify_ids if item), "")
            trace_track_id = track_id or (spotify_id if spotify_id else f"missing_ds001_id_{index:06d}")
            raw_itypes = str(row.get("interaction_types", "") or row.get("interaction_type", "")).strip()

            selected_interaction_types = ProfileStage._parse_selected_interaction_types(
                row,
                include_interaction_types,
            )
            if raw_itypes and not selected_interaction_types:
                defaulted_interaction_type_row_count += 1
            if not selected_interaction_types:
                continue
            if len(selected_interaction_types) > 1:
                mixed_interaction_row_count += 1

            interaction_type = ProfileStage._resolve_primary_interaction_type(
                selected_interaction_types
            )
            attribution_shares = ProfileStage._resolve_attribution_shares(
                selected_interaction_types,
                interaction_type,
                controls.interaction_attribution_mode,
            )
            if len(selected_interaction_types) > 1 and controls.interaction_attribution_mode == "primary_type_only":
                primary_type_attribution_row_count += 1
            preference_weight = parse_float(str(row.get("preference_weight_sum", ""))) or 0.0
            if preference_weight <= 0:
                continue
            parsed_interaction_count = parse_float(str(row.get("interaction_count_sum", "")))
            if parsed_interaction_count is None:
                synthetic_interaction_count_row_count += 1
                interaction_count = max(1, round(preference_weight * 10))
            else:
                interaction_count = int(parsed_interaction_count)

            raw_confidence = str(row.get("match_confidence_score", "")).strip()
            if not raw_confidence or parse_float(raw_confidence) is None:
                confidence_fallback_row_count += 1
            confidence = ProfileStage._clamp_confidence(raw_confidence)
            confidence_adjusted_weight = preference_weight * ProfileStage._resolve_confidence_weight_multiplier(
                confidence,
                controls.confidence_weighting_mode,
            )
            effective_weight = confidence_adjusted_weight
            confidence_adjusted_weight_sum += confidence_adjusted_weight
            if confidence >= high_confidence_threshold:
                confidence_bins["high_0_9_plus"] += 1
            elif confidence >= medium_confidence_threshold:
                confidence_bins["medium_0_5_to_0_9"] += 1
            else:
                confidence_bins["low_below_0_5"] += 1

            history_weight_component = parse_float(
                str(row.get("history_preference_weight_sum", ""))
            )
            influence_weight_component = parse_float(
                str(row.get("influence_preference_weight_sum", ""))
            )
            if history_weight_component is None and "history" in selected_interaction_types:
                synthetic_history_weight_row_count += 1
                history_weight_component = preference_weight * attribution_shares.get("history", 0.0)
            if influence_weight_component is None and "influence" in selected_interaction_types:
                synthetic_influence_weight_row_count += 1
                influence_weight_component = preference_weight * attribution_shares.get("influence", 0.0)
            history_preference_weight_sum += max(0.0, history_weight_component or 0.0)
            influence_preference_weight_sum += max(0.0, influence_weight_component or 0.0)

            history_interaction_component = parse_float(
                str(row.get("history_interaction_count_sum", ""))
            )
            influence_interaction_component = parse_float(
                str(row.get("influence_interaction_count_sum", ""))
            )
            if history_interaction_component is None and "history" in selected_interaction_types:
                history_interaction_component = float(interaction_count) * attribution_shares.get("history", 0.0)
            if influence_interaction_component is None and "influence" in selected_interaction_types:
                influence_interaction_component = float(interaction_count) * attribution_shares.get("influence", 0.0)
            history_interaction_count_sum_value += max(0.0, history_interaction_component or 0.0)
            influence_interaction_count_sum_value += max(0.0, influence_interaction_component or 0.0)

            for selected_type, share in attribution_shares.items():
                attribution_weight_by_type[selected_type] = (
                    attribution_weight_by_type.get(selected_type, 0.0)
                    + (effective_weight * share)
                )
                attribution_interaction_count_by_type[selected_type] = (
                    attribution_interaction_count_by_type.get(selected_type, 0.0)
                    + (float(interaction_count) * share)
                )
                attribution_row_share_by_type[selected_type] = (
                    attribution_row_share_by_type.get(selected_type, 0.0)
                    + share
                )

            tags = parse_csv_labels(str(row.get("tags", "")))
            genres = parse_csv_labels(str(row.get("genres", "")))

            counts_by_type[interaction_type] = counts_by_type.get(interaction_type, 0) + 1
            weight_by_type[interaction_type] = (
                weight_by_type.get(interaction_type, 0.0) + effective_weight
            )
            interaction_count_sum_by_type[interaction_type] = (
                interaction_count_sum_by_type.get(interaction_type, 0) + interaction_count
            )

            for tag in tags:
                tag_weights[tag] = tag_weights.get(tag, 0.0) + effective_weight

            for genre in genres:
                genre_weights[genre] = genre_weights.get(genre, 0.0) + effective_weight

            has_numeric_features = False
            for column in NUMERIC_FEATURE_COLUMNS:
                parsed_value = parse_float(str(row.get(column, "")))
                if parsed_value is None:
                    continue
                has_numeric_features = True
                numeric_sums[column] += parsed_value * effective_weight
                numeric_weights[column] += effective_weight
                numeric_observations[column] += 1
                if column == "key":
                    angle = (parsed_value / 12.0) * 2.0 * math.pi
                    key_circular_sum_x += math.cos(angle) * effective_weight
                    key_circular_sum_y += math.sin(angle) * effective_weight

            if not has_numeric_features:
                if track_id:
                    missing_numeric_track_ids.append(track_id)
                else:
                    blank_track_id_row_count += 1

            lead_genre = ProfileStage.resolve_lead_genre(genres, tags)
            if lead_genre:
                lead_genre_weights[lead_genre] = lead_genre_weights.get(lead_genre, 0.0) + effective_weight

            seed_trace_rows.append(
                {
                    "event_id": f"ds001_seed_{index:06d}",
                    "track_id": trace_track_id,
                    "spotify_track_id": spotify_id,
                    "spotify_artist": str(row.get("artist", "")),
                    "spotify_title": str(row.get("song", "")),
                    "interaction_type": interaction_type,
                    "signal_source": "ds001_seed_table",
                    "seed_rank": index,
                    "interaction_count": interaction_count,
                    "preference_weight": round(preference_weight, 6),
                    "effective_weight": round(effective_weight, 6),
                    "lead_genre": lead_genre,
                    "top_tag": tags[0] if tags else "",
                }
            )

        total_effective_weight = sum(weight_by_type.values())
        matched_seed_count = len(seed_trace_rows)
        if not seed_trace_rows:
            requested_types = sorted(include_interaction_types)
            raise RuntimeError(
                "BL-004 produced no seed events after interaction-type filtering. "
                f"requested_include_interaction_types={requested_types}"
            )

        numeric_profile: dict[str, float] = {}
        for column in NUMERIC_FEATURE_COLUMNS:
            if numeric_weights[column] == 0:
                continue
            if column == "release":
                numeric_profile["release_year"] = round(
                    numeric_sums[column] / numeric_weights[column],
                    6,
                )
                continue
            if column == "key":
                circular_key = ProfileStage.circular_mean_key(key_circular_sum_x, key_circular_sum_y)
                if circular_key is None:
                    continue
                numeric_profile[column] = round(circular_key, 6)
                continue
            numeric_profile[column] = round(numeric_sums[column] / numeric_weights[column], 6)

        seed_trace_rows.sort(key=lambda row: int(str(row["seed_rank"])))

        return ProfileAggregation(
            input_row_count=len(inputs.seed_rows),
            seed_trace_rows=seed_trace_rows,
            numeric_profile=numeric_profile,
            tag_weights=tag_weights,
            genre_weights=genre_weights,
            lead_genre_weights=lead_genre_weights,
            counts_by_type=counts_by_type,
            weight_by_type=weight_by_type,
            interaction_count_sum_by_type=interaction_count_sum_by_type,
            numeric_observations=numeric_observations,
            missing_numeric_track_ids=missing_numeric_track_ids,
            blank_track_id_row_count=blank_track_id_row_count,
            total_effective_weight=total_effective_weight,
            confidence_adjusted_weight_sum=confidence_adjusted_weight_sum,
            confidence_bins=confidence_bins,
            match_method_counts=match_method_counts,
            history_preference_weight_sum=history_preference_weight_sum,
            influence_preference_weight_sum=influence_preference_weight_sum,
            history_interaction_count_sum=int(round(history_interaction_count_sum_value)),
            influence_interaction_count_sum=int(round(influence_interaction_count_sum_value)),
            matched_seed_count=matched_seed_count,
            confidence_fallback_row_count=confidence_fallback_row_count,
            defaulted_interaction_type_row_count=defaulted_interaction_type_row_count,
            synthetic_interaction_count_row_count=synthetic_interaction_count_row_count,
            synthetic_history_weight_row_count=synthetic_history_weight_row_count,
            synthetic_influence_weight_row_count=synthetic_influence_weight_row_count,
            mixed_interaction_row_count=mixed_interaction_row_count,
            primary_type_attribution_row_count=primary_type_attribution_row_count,
            attribution_weight_by_type=attribution_weight_by_type,
            attribution_interaction_count_by_type=attribution_interaction_count_by_type,
            attribution_row_share_by_type=attribution_row_share_by_type,
        )

    @staticmethod
    def write_seed_trace(seed_trace_path: Path, rows: list[dict[str, object]]) -> None:
        with open_text_write(seed_trace_path, newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def build_profile_payload(
        *,
        run_id: str,
        controls: ProfileControls,
        paths: ProfilePaths,
        inputs: ProfileInputs,
        aggregation: ProfileAggregation,
        elapsed_seconds: float,
    ) -> dict[str, object]:
        canonical_blocks = ProfileStage._build_canonical_blocks(
            aggregation,
            controls,
            inputs,
        )
        source_coverage = canonical_blocks["source_coverage"] if isinstance(canonical_blocks.get("source_coverage"), dict) else {}
        bl003_quality = canonical_blocks["bl003_quality"] if isinstance(canonical_blocks.get("bl003_quality"), dict) else {}
        diagnostics: dict[str, object] = {
            "events_total": aggregation.input_row_count,
            "matched_seed_count": aggregation.matched_seed_count,
            "missing_numeric_track_count": len(aggregation.missing_numeric_track_ids),
            "missing_numeric_track_ids": aggregation.missing_numeric_track_ids[:50],
            "blank_track_id_rows": aggregation.blank_track_id_row_count,
            "candidate_rows_total": aggregation.input_row_count,
            "numeric_observations": aggregation.numeric_observations,
            "key_aggregation_method": "weighted_circular_mean",
            "total_effective_weight": round(aggregation.total_effective_weight, 6),
            "confidence_adjusted_weight_sum": round(
                aggregation.confidence_adjusted_weight_sum,
                6,
            ),
            "confidence_bins": dict(aggregation.confidence_bins),
            "confidence_fallback_row_count": aggregation.confidence_fallback_row_count,
            "match_method_counts": dict(aggregation.match_method_counts),
            "defaulted_interaction_type_row_count": aggregation.defaulted_interaction_type_row_count,
            "synthetic_interaction_count_row_count": aggregation.synthetic_interaction_count_row_count,
            "synthetic_history_weight_row_count": aggregation.synthetic_history_weight_row_count,
            "synthetic_influence_weight_row_count": aggregation.synthetic_influence_weight_row_count,
            "bl003_source_rows_selected": dict(inputs.bl003_rows_selected),
            "bl003_source_rows_available": dict(inputs.bl003_rows_available),
            "elapsed_seconds": round(elapsed_seconds, 3),
        }
        if controls.emit_profile_policy_diagnostics:
            diagnostics["profile_policy_effective"] = {
                "confidence_weighting_mode": controls.confidence_weighting_mode,
                "confidence_bin_high_threshold": controls.confidence_bin_high_threshold,
                "confidence_bin_medium_threshold": controls.confidence_bin_medium_threshold,
                "interaction_attribution_mode": controls.interaction_attribution_mode,
            }
            diagnostics["profile_policy_impact"] = {
                "mixed_interaction_row_count": aggregation.mixed_interaction_row_count,
                "primary_type_attribution_row_count": aggregation.primary_type_attribution_row_count,
            }
        return {
            "run_id": run_id,
            "task": "BL-004",
            "profile_schema_version": BL004_PROFILE_SCHEMA_VERSION,
            "output_contract_version": BL004_OUTPUT_CONTRACT_VERSION,
            "generated_at_utc": utc_now(),
            "user_id": controls.user_id,
            "config_source": controls.config_source,
            "run_config_path": controls.run_config_path,
            "run_config_schema_version": controls.run_config_schema_version,
            "input_artifacts": {
                "seed_table_path": str(paths.seed_table_path),
                "seed_table_sha256": sha256_of_file(paths.seed_table_path),
                "bl003_summary_path": str(paths.bl003_summary_path),
                "bl003_manifest_path": str(paths.bl003_manifest_path),
                "bl003_seed_contract_hash": inputs.bl003_seed_contract_hash,
                "bl003_structural_contract_hash": inputs.bl003_structural_contract_hash,
            },
            "provenance": {
                "bl003_seed_contract": {
                    "schema_version": str(
                        inputs.bl003_seed_contract.get("seed_contract_schema_version")
                        or ""
                    ),
                    "contract_hash": inputs.bl003_seed_contract_hash,
                },
                "bl003_structural_contract": {
                    "schema_version": str(
                        inputs.bl003_structural_contract.get("structural_contract_schema_version")
                        or ""
                    ),
                    "contract_hash": inputs.bl003_structural_contract_hash,
                },
            },
            "config": {
                "input_scope": controls.input_scope,
                "effective_weight_rule": "effective_weight = preference_weight * (0.5 + 0.5 * clamp(match_confidence_score, 0, 1)); fallback confidence=1.0 when missing",
                "numeric_feature_columns": NUMERIC_FEATURE_COLUMNS,
                "profile_mode": "hybrid_semantic_numeric_from_bl003_enriched_seed_table",
                "top_tag_limit": controls.top_tag_limit,
                "top_genre_limit": controls.top_genre_limit,
                "top_lead_genre_limit": controls.top_lead_genre_limit,
                "profile_policy": {
                    "confidence_weighting_mode": controls.confidence_weighting_mode,
                    "confidence_bin_high_threshold": controls.confidence_bin_high_threshold,
                    "confidence_bin_medium_threshold": controls.confidence_bin_medium_threshold,
                    "interaction_attribution_mode": controls.interaction_attribution_mode,
                    "emit_profile_policy_diagnostics": controls.emit_profile_policy_diagnostics,
                },
                "aggregation_rules": {
                    "numeric": "weighted mean over numeric columns embedded in the BL-003 enriched seed table; key uses weighted circular mean on the 12-semitone wheel",
                    "tags": "sum(effective_weight) over DS-001 tag labels",
                    "genres": "sum(effective_weight) over DS-001 genre labels",
                    "lead_genres": "sum(effective_weight)",
                },
            },
            "diagnostics": diagnostics,
            "bl003_quality": canonical_blocks["bl003_quality"],
            "source_coverage": canonical_blocks["source_coverage"],
            "interaction_attribution": canonical_blocks["interaction_attribution"],
            "numeric_confidence": canonical_blocks["numeric_confidence"],
            "profile_signal_vector": canonical_blocks["profile_signal_vector"],
            "seed_summary": {
                "counts_by_interaction_type": aggregation.counts_by_type,
                "weight_by_interaction_type": {
                    key: round(value, 6)
                    for key, value in aggregation.weight_by_type.items()
                },
                "interaction_count_sum_by_interaction_type": aggregation.interaction_count_sum_by_type,
                "history_vs_influence": {
                    "preference_weight_sum": {
                        "history": round(aggregation.history_preference_weight_sum, 6),
                        "influence": round(aggregation.influence_preference_weight_sum, 6),
                    },
                    "interaction_count_sum": {
                        "history": aggregation.history_interaction_count_sum,
                        "influence": aggregation.influence_interaction_count_sum,
                    },
                },
                "seed_trace_path": str(paths.seed_trace_path),
            },
            "numeric_feature_profile": aggregation.numeric_profile,
            "semantic_profile": {
                "top_tags": ProfileStage.sorted_weight_map(
                    aggregation.tag_weights,
                    controls.top_tag_limit,
                ),
                "top_genres": ProfileStage.sorted_weight_map(
                    aggregation.genre_weights,
                    controls.top_genre_limit,
                ),
                "top_lead_genres": ProfileStage.sorted_weight_map(
                    aggregation.lead_genre_weights,
                    controls.top_lead_genre_limit,
                ),
            },
        }

    @staticmethod
    def build_summary_payload(
        *,
        run_id: str,
        controls: ProfileControls,
        paths: ProfilePaths,
        inputs: ProfileInputs,
        profile: dict[str, object],
        aggregation: ProfileAggregation,
    ) -> dict[str, object]:
        semantic_profile_obj = profile.get("semantic_profile")
        semantic_profile = semantic_profile_obj if isinstance(semantic_profile_obj, dict) else {}
        canonical_blocks = ProfileStage._build_canonical_blocks(
            aggregation,
            controls,
            inputs,
        )
        source_coverage_obj = canonical_blocks.get("source_coverage")
        source_coverage: dict[str, object] = (
            source_coverage_obj
            if isinstance(source_coverage_obj, dict)
            else {}
        )
        bl003_quality_obj = canonical_blocks.get("bl003_quality")
        bl003_quality: dict[str, object] = (
            bl003_quality_obj
            if isinstance(bl003_quality_obj, dict)
            else {}
        )

        return {
            "run_id": run_id,
            "task": "BL-004",
            "summary_schema_version": BL004_SUMMARY_SCHEMA_VERSION,
            "output_contract_version": BL004_OUTPUT_CONTRACT_VERSION,
            "user_id": controls.user_id,
            "config_source": controls.config_source,
            "run_config_path": controls.run_config_path,
            "run_config_schema_version": controls.run_config_schema_version,
            "input_scope": controls.input_scope,
            "profile_policy": {
                "confidence_weighting_mode": controls.confidence_weighting_mode,
                "confidence_bin_high_threshold": controls.confidence_bin_high_threshold,
                "confidence_bin_medium_threshold": controls.confidence_bin_medium_threshold,
                "interaction_attribution_mode": controls.interaction_attribution_mode,
                "emit_profile_policy_diagnostics": controls.emit_profile_policy_diagnostics,
            },
            "matched_seed_count": aggregation.matched_seed_count,
            "total_effective_weight": round(aggregation.total_effective_weight, 6),
            "confidence_adjusted_weight_sum": round(
                aggregation.confidence_adjusted_weight_sum,
                6,
            ),
            "match_method_counts": dict(aggregation.match_method_counts),
            "history_vs_influence": {
                "preference_weight_sum": {
                    "history": round(aggregation.history_preference_weight_sum, 6),
                    "influence": round(aggregation.influence_preference_weight_sum, 6),
                },
                "interaction_count_sum": {
                    "history": aggregation.history_interaction_count_sum,
                    "influence": aggregation.influence_interaction_count_sum,
                },
            },
            "dominant_lead_genres": list(semantic_profile.get("top_lead_genres", []))[:5],
            "dominant_tags": list(semantic_profile.get("top_tags", []))[:5],
            "dominant_genres": list(semantic_profile.get("top_genres", []))[:5],
            "feature_centers": {
                column: aggregation.numeric_profile[column]
                for column in SUMMARY_FEATURE_COLUMNS
                if column in aggregation.numeric_profile
            },
            "bl003_quality": canonical_blocks["bl003_quality"],
            "source_coverage": canonical_blocks["source_coverage"],
            "interaction_attribution": canonical_blocks["interaction_attribution"],
            "numeric_confidence": canonical_blocks["numeric_confidence"],
            "profile_signal_vector": canonical_blocks["profile_signal_vector"],
            "artifact_paths": {
                "profile_path": str(paths.profile_path),
                "seed_trace_path": str(paths.seed_trace_path),
                "bl003_summary_path": str(paths.bl003_summary_path),
                "bl003_manifest_path": str(paths.bl003_manifest_path),
            },
            "input_hashes": profile["input_artifacts"],
            "bl003_provenance": {
                "seed_contract_hash": inputs.bl003_seed_contract_hash,
                "structural_contract_hash": inputs.bl003_structural_contract_hash,
            },
            "bl003_coverage": {
                "rows_selected": ProfileStage._normalize_int_mapping(source_coverage.get("rows_selected")),
                "rows_available": ProfileStage._normalize_int_mapping(source_coverage.get("rows_available")),
                "match_counts": {
                    str(key): value
                    for key, value in bl003_quality.items()
                },
            },
        }

    @staticmethod
    def write_json(path: Path, payload: dict[str, object]) -> None:
        with open_text_write(path) as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True)

    def run(self) -> ProfileArtifacts:
        paths = self.resolve_paths()
        paths.output_dir.mkdir(parents=True, exist_ok=True)

        controls = self.resolve_runtime_controls()
        inputs = self.load_inputs(paths)

        start_time = time.time()
        run_id = f"BL004-PROFILE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

        aggregation = self.aggregate_inputs(inputs, controls)
        self.write_seed_trace(paths.seed_trace_path, aggregation.seed_trace_rows)

        profile = self.build_profile_payload(
            run_id=run_id,
            controls=controls,
            paths=paths,
            inputs=inputs,
            aggregation=aggregation,
            elapsed_seconds=time.time() - start_time,
        )
        self.write_json(paths.profile_path, profile)

        summary = self.build_summary_payload(
            run_id=run_id,
            controls=controls,
            paths=paths,
            inputs=inputs,
            profile=profile,
            aggregation=aggregation,
        )
        self.write_json(paths.summary_path, summary)

        logger.info("BL-004 preference profile created.")
        logger.info("profile=%s", paths.profile_path)
        logger.info("summary=%s", paths.summary_path)
        logger.info("seed_trace=%s", paths.seed_trace_path)

        return ProfileArtifacts(
            profile_path=paths.profile_path,
            summary_path=paths.summary_path,
            seed_trace_path=paths.seed_trace_path,
        )
