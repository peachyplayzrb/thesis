from __future__ import annotations

import csv
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from profile.models import ProfileAggregation, ProfileArtifacts, ProfileControls, ProfileInputs, ProfilePaths
from shared_utils.config_loader import load_run_config_utils_module
from shared_utils.constants import (
    DEFAULT_INCLUDE_INTERACTION_TYPES,
    DEFAULT_INPUT_SCOPE,
    DEFAULT_PROFILE_TOP_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
    DEFAULT_PROFILE_TOP_TAG_LIMIT,
)
from shared_utils.env_utils import env_int, env_str
from shared_utils.io_utils import load_csv_rows, open_text_write, parse_csv_labels, parse_float, sha256_of_file, utc_now
from shared_utils.path_utils import impl_root
from shared_utils.stage_runtime_resolver import resolve_run_config_path


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
        top_tag_limit = max(1, int(str(controls["top_tag_limit"])))
        top_genre_limit = max(1, int(str(controls["top_genre_limit"])))
        top_lead_genre_limit = max(1, int(str(controls["top_lead_genre_limit"])))
        include_types_raw = controls.get("include_interaction_types")
        include_types_values = include_types_raw if isinstance(include_types_raw, list) else []
        include_types = [
            str(v).strip()
            for v in include_types_values
            if str(v).strip()
        ]
        input_scope_raw = controls.get("input_scope")
        input_scope_payload = (
            dict(input_scope_raw)
            if isinstance(input_scope_raw, Mapping)
            else dict(DEFAULT_INPUT_SCOPE)
        )
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
            input_scope={str(k): v for k, v in input_scope_payload.items()},
            top_tag_limit=top_tag_limit,
            top_genre_limit=top_genre_limit,
            top_lead_genre_limit=top_lead_genre_limit,
            user_id=str(controls.get("user_id") or "unknown_user"),
            include_interaction_types=include_types or list(DEFAULT_INCLUDE_INTERACTION_TYPES),
        )

    def resolve_runtime_controls(self) -> ProfileControls:
        run_config_path = resolve_run_config_path()
        env_user_id = env_str("BL004_USER_ID", "")
        env_interaction_types_raw = env_str("BL004_INCLUDE_INTERACTION_TYPES", "")
        inferred_user_id = self.infer_user_id_from_ingestion()

        env_interaction_types = [
            token.strip()
            for token in env_interaction_types_raw.split(",")
            if token.strip()
        ]

        def resolve_user_id(candidate: object) -> str:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
            if env_user_id:
                return env_user_id
            if inferred_user_id:
                return inferred_user_id
            return "unknown_user"

        if run_config_path:
            run_config_utils = load_run_config_utils_module()
            controls = run_config_utils.resolve_bl004_controls(run_config_path)
            user_id = resolve_user_id(controls.get("user_id"))
            return self._sanitize_controls(
                {
                    "config_source": "run_config",
                    "run_config_path": controls.get("config_path"),
                    "run_config_schema_version": controls.get("schema_version"),
                    "input_scope": dict(controls.get("input_scope") or DEFAULT_INPUT_SCOPE),
                    "top_tag_limit": int(controls["top_tag_limit"]),
                    "top_genre_limit": int(controls["top_genre_limit"]),
                    "top_lead_genre_limit": int(controls["top_lead_genre_limit"]),
                    "user_id": user_id,
                    "include_interaction_types": list(
                        env_interaction_types
                        or controls.get("include_interaction_types")
                        or DEFAULT_INCLUDE_INTERACTION_TYPES
                    ),
                }
            )

        return self._sanitize_controls(
            {
                "config_source": "environment",
                "run_config_path": None,
                "run_config_schema_version": None,
                "input_scope": dict(DEFAULT_INPUT_SCOPE),
                "top_tag_limit": env_int("BL004_TOP_TAG_LIMIT", DEFAULT_PROFILE_TOP_TAG_LIMIT),
                "top_genre_limit": env_int("BL004_TOP_GENRE_LIMIT", DEFAULT_PROFILE_TOP_GENRE_LIMIT),
                "top_lead_genre_limit": env_int(
                    "BL004_TOP_LEAD_GENRE_LIMIT",
                    DEFAULT_PROFILE_TOP_LEAD_GENRE_LIMIT,
                ),
                "user_id": resolve_user_id(None),
                "include_interaction_types": list(env_interaction_types or DEFAULT_INCLUDE_INTERACTION_TYPES),
            }
        )

    def resolve_paths(self) -> ProfilePaths:
        output_dir = self.root / "profile" / "outputs"
        return ProfilePaths(
            seed_table_path=self.root / "alignment" / "outputs" / "bl003_ds001_spotify_seed_table.csv",
            output_dir=output_dir,
            seed_trace_path=output_dir / "bl004_seed_trace.csv",
            profile_path=output_dir / "bl004_preference_profile.json",
            summary_path=output_dir / "profile_summary.json",
        )

    @staticmethod
    def load_inputs(paths: ProfilePaths) -> ProfileInputs:
        seed_rows = load_csv_rows(paths.seed_table_path)
        if not seed_rows:
            raise RuntimeError("No DS-001 seed rows found for BL-004 input")
        normalized_rows: list[dict[str, object]] = [
            {str(k): v for k, v in row.items()}
            for row in seed_rows
        ]
        return ProfileInputs(seed_rows=normalized_rows)

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
        key_circular_sum_x = 0.0
        key_circular_sum_y = 0.0

        for index, row in enumerate(inputs.seed_rows, start=1):
            track_id = str(row.get("ds001_id", "")).strip()
            spotify_ids = str(row.get("spotify_track_ids", "")).strip().split("|")
            spotify_id = next((item for item in spotify_ids if item), "")

            raw_itypes = str(row.get("interaction_types", "") or row.get("interaction_type", "")).strip()
            row_interaction_types = (
                {t.strip() for t in raw_itypes.split("|") if t.strip()}
                if raw_itypes
                else {"history"}
            )
            if not row_interaction_types.intersection(include_interaction_types):
                continue

            interaction_type = "influence" if "influence" in row_interaction_types else "history"
            preference_weight = parse_float(str(row.get("preference_weight_sum", ""))) or 0.0
            if preference_weight <= 0:
                continue

            effective_weight = preference_weight
            interaction_count = int(
                parse_float(str(row.get("interaction_count_sum", "")))
                or max(1, round(preference_weight * 10))
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

            row_has_numeric_value = False
            for column in NUMERIC_FEATURE_COLUMNS:
                parsed_value = parse_float(str(row.get(column, "")))
                if parsed_value is None:
                    continue
                row_has_numeric_value = True
                numeric_sums[column] += parsed_value * effective_weight
                numeric_weights[column] += effective_weight
                numeric_observations[column] += 1
                if column == "key":
                    angle = (parsed_value / 12.0) * 2.0 * math.pi
                    key_circular_sum_x += math.cos(angle) * effective_weight
                    key_circular_sum_y += math.sin(angle) * effective_weight

            if not row_has_numeric_value:
                missing_numeric_track_ids.append(track_id)

            lead_genre = ProfileStage.resolve_lead_genre(genres, tags)
            if lead_genre:
                lead_genre_weights[lead_genre] = lead_genre_weights.get(lead_genre, 0.0) + effective_weight

            seed_trace_rows.append(
                {
                    "event_id": f"ds001_seed_{index:06d}",
                    "track_id": track_id,
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
                    "numeric_feature_coverage": "1" if row_has_numeric_value else "0",
                    "lastfm_status": "not_applicable_ds001",
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
            total_effective_weight=total_effective_weight,
            matched_seed_count=matched_seed_count,
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
        aggregation: ProfileAggregation,
        elapsed_seconds: float,
    ) -> dict[str, object]:
        return {
            "run_id": run_id,
            "task": "BL-004",
            "generated_at_utc": utc_now(),
            "user_id": controls.user_id,
            "config_source": controls.config_source,
            "run_config_path": controls.run_config_path,
            "run_config_schema_version": controls.run_config_schema_version,
            "input_artifacts": {
                "seed_table_path": str(paths.seed_table_path),
                "seed_table_sha256": sha256_of_file(paths.seed_table_path),
            },
            "config": {
                "input_scope": controls.input_scope,
                "effective_weight_rule": "effective_weight = preference_weight",
                "numeric_feature_columns": NUMERIC_FEATURE_COLUMNS,
                "profile_mode": "hybrid_semantic_numeric_from_bl003_enriched_seed_table",
                "top_tag_limit": controls.top_tag_limit,
                "top_genre_limit": controls.top_genre_limit,
                "top_lead_genre_limit": controls.top_lead_genre_limit,
                "aggregation_rules": {
                    "numeric": "weighted mean over numeric columns embedded in the BL-003 enriched seed table; key uses weighted circular mean on the 12-semitone wheel",
                    "tags": "sum(preference_weight) over DS-001 tag labels",
                    "genres": "sum(preference_weight) over DS-001 genre labels",
                    "lead_genres": "sum(preference_weight)",
                },
            },
            "diagnostics": {
                "events_total": aggregation.input_row_count,
                "matched_seed_count": aggregation.matched_seed_count,
                "missing_seed_count": len(aggregation.missing_numeric_track_ids),
                "missing_track_ids": aggregation.missing_numeric_track_ids[:50],
                "candidate_rows_total": aggregation.input_row_count,
                "numeric_observations": aggregation.numeric_observations,
                "key_aggregation_method": "weighted_circular_mean",
                "total_effective_weight": round(aggregation.total_effective_weight, 6),
                "elapsed_seconds": round(elapsed_seconds, 3),
            },
            "seed_summary": {
                "counts_by_interaction_type": aggregation.counts_by_type,
                "weight_by_interaction_type": {
                    key: round(value, 6)
                    for key, value in aggregation.weight_by_type.items()
                },
                "interaction_count_sum_by_interaction_type": aggregation.interaction_count_sum_by_type,
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
        profile: dict[str, object],
        aggregation: ProfileAggregation,
    ) -> dict[str, object]:
        semantic_profile_obj = profile.get("semantic_profile")
        semantic_profile = semantic_profile_obj if isinstance(semantic_profile_obj, dict) else {}

        return {
            "run_id": run_id,
            "task": "BL-004",
            "user_id": controls.user_id,
            "config_source": controls.config_source,
            "run_config_path": controls.run_config_path,
            "run_config_schema_version": controls.run_config_schema_version,
            "input_scope": controls.input_scope,
            "matched_seed_count": aggregation.matched_seed_count,
            "total_effective_weight": round(aggregation.total_effective_weight, 6),
            "dominant_lead_genres": list(semantic_profile.get("top_lead_genres", []))[:5],
            "dominant_tags": list(semantic_profile.get("top_tags", []))[:5],
            "dominant_genres": list(semantic_profile.get("top_genres", []))[:5],
            "feature_centers": {
                column: aggregation.numeric_profile[column]
                for column in SUMMARY_FEATURE_COLUMNS
                if column in aggregation.numeric_profile
            },
            "artifact_paths": {
                "profile_path": str(paths.profile_path),
                "seed_trace_path": str(paths.seed_trace_path),
            },
            "input_hashes": profile["input_artifacts"],
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
            aggregation=aggregation,
            elapsed_seconds=time.time() - start_time,
        )
        self.write_json(paths.profile_path, profile)

        summary = self.build_summary_payload(
            run_id=run_id,
            controls=controls,
            paths=paths,
            profile=profile,
            aggregation=aggregation,
        )
        self.write_json(paths.summary_path, summary)

        print("BL-004 preference profile created.")
        print(f"profile={paths.profile_path}")
        print(f"summary={paths.summary_path}")
        print(f"seed_trace={paths.seed_trace_path}")

        return ProfileArtifacts(
            profile_path=paths.profile_path,
            summary_path=paths.summary_path,
            seed_trace_path=paths.seed_trace_path,
        )
