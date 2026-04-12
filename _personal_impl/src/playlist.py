#!/usr/bin/env python3
"""BL-007: Rule-based playlist assembly."""

from __future__ import annotations

import csv
import json
import logging
import os
import time
from copy import deepcopy
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from run_config.stage_control_resolution import defaults_loader as _defaults_loader
from run_config.stage_control_resolution import resolve_stage_controls as _resolve_stage_controls
from run_config.run_config_utils import DEFAULT_ASSEMBLY_CONTROLS as RUN_CONFIG_DEFAULT_ASSEMBLY_CONTROLS
from shared.io_utils import (
    open_text_write,
    sha256_of_file,
    utc_now,
    write_json,
)
from shared.path_utils import impl_root
from shared.env_utils import env_bool, env_float, env_int, env_path, env_str
from shared.coerce_utils import coerce_dict, coerce_enum, coerce_float, coerce_int, safe_float, safe_int

DEFAULT_ASSEMBLY_CONTROLS: dict[str, object] = deepcopy(RUN_CONFIG_DEFAULT_ASSEMBLY_CONTROLS)
VALID_UTILITY_STRATEGIES: frozenset[str] = frozenset({"rank_round_robin", "utility_greedy"})
VALID_LEAD_GENRE_FALLBACK_STRATEGIES: frozenset[str] = frozenset({"none", "semantic_component_proxy"})


def ensure_paths_exist(
    paths: list[Path],
    *,
    stage_label: str,
    label: str = "input artifact(s)",
    root: Path | None = None,
) -> None:
    missing: list[str] = []
    for path in paths:
        if path.exists():
            continue
        if root is None:
            missing.append(str(path))
            continue
        try:
            missing.append(path.relative_to(root).as_posix())
        except ValueError:
            missing.append(str(path))
    if missing:
        raise FileNotFoundError(f"{stage_label} missing required {label}: {missing}")


DEFAULT_SCORED_CANDIDATES_PATH = Path("scoring/outputs/bl006_scored_candidates.csv")
DEFAULT_OUTPUT_DIR = Path("playlist/outputs")
REQUIRED_CANDIDATE_COLUMNS = ("rank", "track_id", "lead_genre", "final_score")
UNKNOWN_GENRE_BUCKET = "__unknown__"


@dataclass(frozen=True)
class PlaylistPaths:
    scored_candidates_path: Path
    output_dir: Path


@dataclass(frozen=True)
class PlaylistControls:
    target_size: int
    min_score_threshold: float
    max_per_genre: int
    max_consecutive: int
    utility_strategy: str
    utility_weights: dict[str, float]
    adaptive_limits: dict[str, object]
    controlled_relaxation: dict[str, object]
    lead_genre_fallback_strategy: str
    use_component_contributions_for_tiebreak: bool
    use_semantic_strength_for_tiebreak: bool
    emit_opportunity_cost_metrics: bool
    detail_log_top_k: int
    exclusion_ratio_warn_threshold: float = 0.3
    dominant_reason_share_warn_threshold: float = 0.7


@dataclass(frozen=True)
class PlaylistContext:
    target_size: int
    min_score_threshold: float
    max_per_genre: int
    max_consecutive: int
    utility_strategy: str
    utility_weights: dict[str, float]
    adaptive_limits: dict[str, object]
    controlled_relaxation: dict[str, object]
    lead_genre_fallback_strategy: str
    use_component_contributions_for_tiebreak: bool
    use_semantic_strength_for_tiebreak: bool
    emit_opportunity_cost_metrics: bool
    detail_log_top_k: int
    exclusion_ratio_warn_threshold: float = 0.3
    dominant_reason_share_warn_threshold: float = 0.7


@dataclass(frozen=True)
class PlaylistAggregation:
    playlist: list[dict[str, object]]
    trace_rows: list[dict[str, object]]
    rule_hits: dict[str, int]


@dataclass(frozen=True)
class PlaylistArtifacts:
    playlist_path: Path
    trace_path: Path
    report_path: Path
    detail_log_path: Path
    run_id: str
    target_size: int
    playlist_size: int
    genre_mix: dict[str, int]
    undersized_diagnostics: dict[str, object]


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _load_bl007_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "target_size": env_int("BL007_TARGET_SIZE", 10),
        "min_score_threshold": env_float("BL007_MIN_SCORE_THRESHOLD", 0.35),
        "max_per_genre": env_int("BL007_MAX_PER_GENRE", 4),
        "max_consecutive": env_int("BL007_MAX_CONSECUTIVE", 2),
        "utility_strategy": env_str("BL007_UTILITY_STRATEGY", "rank_round_robin"),
        "utility_weights": {
            "score_weight": env_float("BL007_UTILITY_SCORE_WEIGHT", 1.0),
            "novelty_weight": env_float("BL007_UTILITY_NOVELTY_WEIGHT", 0.0),
            "repetition_penalty_weight": env_float("BL007_UTILITY_REPETITION_PENALTY_WEIGHT", 0.0),
        },
        "adaptive_limits": {
            "enabled": env_bool("BL007_ADAPTIVE_LIMITS_ENABLED", False),
            "reference_top_k": env_int("BL007_ADAPTIVE_REFERENCE_TOP_K", 100),
            "max_per_genre_scale_min": env_float("BL007_ADAPTIVE_MAX_PER_GENRE_SCALE_MIN", 0.75),
            "max_per_genre_scale_max": env_float("BL007_ADAPTIVE_MAX_PER_GENRE_SCALE_MAX", 1.25),
        },
        "controlled_relaxation": {
            "enabled": env_bool("BL007_CONTROLLED_RELAXATION_ENABLED", False),
            "relax_consecutive_first": env_bool("BL007_RELAX_CONSECUTIVE_FIRST", True),
            "max_per_genre_increment": env_int("BL007_RELAX_MAX_PER_GENRE_INCREMENT", 1),
            "max_relaxation_rounds": env_int("BL007_MAX_RELAXATION_ROUNDS", 2),
            "never_relax_score_threshold": env_bool("BL007_NEVER_RELAX_SCORE_THRESHOLD", True),
        },
        "lead_genre_fallback_strategy": env_str("BL007_LEAD_GENRE_FALLBACK_STRATEGY", "none"),
        "use_component_contributions_for_tiebreak": env_bool(
            "BL007_USE_COMPONENT_CONTRIBUTIONS_FOR_TIEBREAK", False,
        ),
        "use_semantic_strength_for_tiebreak": env_bool(
            "BL007_USE_SEMANTIC_STRENGTH_FOR_TIEBREAK", False,
        ),
        "emit_opportunity_cost_metrics": env_bool("BL007_EMIT_OPPORTUNITY_COST_METRICS", False),
        "detail_log_top_k": env_int("BL007_DETAIL_LOG_TOP_K", 100),
        "pressure_diagnostics": {
            "exclusion_ratio_warn_threshold": env_float("BL007_EXCLUSION_RATIO_WARN_THRESHOLD", 0.3),
            "dominant_reason_share_warn_threshold": env_float("BL007_DOMINANT_REASON_SHARE_WARN_THRESHOLD", 0.7),
        },
    }


def _sanitize_bl007_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["target_size"] = max(1, coerce_int(controls.get("target_size"), 10))
    controls["min_score_threshold"] = max(
        0.0,
        min(1.0, coerce_float(controls.get("min_score_threshold"), 0.35)),
    )
    controls["max_per_genre"] = max(1, coerce_int(controls.get("max_per_genre"), 4))
    controls["max_consecutive"] = max(1, coerce_int(controls.get("max_consecutive"), 2))
    controls["utility_strategy"] = coerce_enum(
        controls.get("utility_strategy"),
        VALID_UTILITY_STRATEGIES,
        "rank_round_robin",
    )

    utility_weights = coerce_dict(controls.get("utility_weights"))
    controls["utility_weights"] = {
        "score_weight": max(0.0, coerce_float(utility_weights.get("score_weight"), 1.0)),
        "novelty_weight": max(0.0, coerce_float(utility_weights.get("novelty_weight"), 0.0)),
        "repetition_penalty_weight": max(
            0.0,
            coerce_float(utility_weights.get("repetition_penalty_weight"), 0.0),
        ),
    }

    adaptive = coerce_dict(controls.get("adaptive_limits"))
    scale_min = max(0.0, coerce_float(adaptive.get("max_per_genre_scale_min"), 0.75))
    scale_max = max(scale_min, coerce_float(adaptive.get("max_per_genre_scale_max"), 1.25))
    controls["adaptive_limits"] = {
        "enabled": bool(adaptive.get("enabled", False)),
        "reference_top_k": max(1, coerce_int(adaptive.get("reference_top_k"), 100)),
        "max_per_genre_scale_min": scale_min,
        "max_per_genre_scale_max": scale_max,
    }

    relax = coerce_dict(controls.get("controlled_relaxation"))
    controls["controlled_relaxation"] = {
        "enabled": bool(relax.get("enabled", False)),
        "relax_consecutive_first": bool(relax.get("relax_consecutive_first", True)),
        "max_per_genre_increment": max(1, coerce_int(relax.get("max_per_genre_increment"), 1)),
        "max_relaxation_rounds": max(1, coerce_int(relax.get("max_relaxation_rounds"), 2)),
        "never_relax_score_threshold": bool(relax.get("never_relax_score_threshold", True)),
    }

    controls["lead_genre_fallback_strategy"] = coerce_enum(
        controls.get("lead_genre_fallback_strategy"),
        VALID_LEAD_GENRE_FALLBACK_STRATEGIES,
        "none",
    )
    controls["use_component_contributions_for_tiebreak"] = bool(
        controls.get("use_component_contributions_for_tiebreak", False)
    )
    controls["use_semantic_strength_for_tiebreak"] = bool(
        controls.get("use_semantic_strength_for_tiebreak", False)
    )
    controls["emit_opportunity_cost_metrics"] = bool(
        controls.get("emit_opportunity_cost_metrics", False)
    )
    controls["detail_log_top_k"] = max(1, coerce_int(controls.get("detail_log_top_k"), 100))
    pressure_diagnostics = coerce_dict(controls.get("pressure_diagnostics"))
    controls["pressure_diagnostics"] = {
        "exclusion_ratio_warn_threshold": max(
            0.0,
            min(1.0, coerce_float(pressure_diagnostics.get("exclusion_ratio_warn_threshold"), 0.3)),
        ),
        "dominant_reason_share_warn_threshold": max(
            0.0,
            min(1.0, coerce_float(pressure_diagnostics.get("dominant_reason_share_warn_threshold"), 0.7)),
        ),
    }
    return controls


def _env_truthy(name: str) -> bool:
    raw = os.environ.get(name, "")
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _bl007_require_payload() -> bool:
    return _env_truthy("BL007_STRICT_PAYLOAD") or _env_truthy("BL_STRICT_STAGE_PAYLOAD")


def resolve_bl007_runtime_controls() -> dict[str, object]:
    return _resolve_stage_controls(
        load_from_env=_load_bl007_controls_from_env,
        load_payload_defaults=_defaults_loader(DEFAULT_ASSEMBLY_CONTROLS),
        sanitize=_sanitize_bl007_controls,
        require_payload=_bl007_require_payload(),
    )


def controls_from_mapping(payload: Mapping[str, Any]) -> PlaylistControls:
    utility_weights_raw = payload.get("utility_weights")
    adaptive_raw = payload.get("adaptive_limits")
    controlled_relaxation_raw = payload.get("controlled_relaxation")
    pressure_diagnostics_raw = payload.get("pressure_diagnostics")
    pressure_diagnostics = dict(pressure_diagnostics_raw or {}) if isinstance(pressure_diagnostics_raw, dict) else {}
    return PlaylistControls(
        target_size=int(payload.get("target_size", 10)),
        min_score_threshold=float(payload.get("min_score_threshold", 0.35)),
        max_per_genre=int(payload.get("max_per_genre", 4)),
        max_consecutive=int(payload.get("max_consecutive", 2)),
        utility_strategy=str(payload.get("utility_strategy", "rank_round_robin")),
        utility_weights={str(k): float(v) for k, v in dict(utility_weights_raw or {}).items()},
        adaptive_limits={str(k): v for k, v in dict(adaptive_raw or {}).items()},
        controlled_relaxation={str(k): v for k, v in dict(controlled_relaxation_raw or {}).items()},
        lead_genre_fallback_strategy=str(payload.get("lead_genre_fallback_strategy", "none")),
        use_component_contributions_for_tiebreak=bool(
            payload.get("use_component_contributions_for_tiebreak", False)
        ),
        use_semantic_strength_for_tiebreak=bool(payload.get("use_semantic_strength_for_tiebreak", False)),
        emit_opportunity_cost_metrics=bool(payload.get("emit_opportunity_cost_metrics", False)),
        detail_log_top_k=int(payload.get("detail_log_top_k", 100)),
        exclusion_ratio_warn_threshold=float(pressure_diagnostics.get("exclusion_ratio_warn_threshold", 0.3)),
        dominant_reason_share_warn_threshold=float(pressure_diagnostics.get("dominant_reason_share_warn_threshold", 0.7)),
    )


def resolve_bl007_paths(root: Path) -> PlaylistPaths:
    scored_candidates_path = env_path(
        "BL007_SCORED_CANDIDATES_PATH",
        root / DEFAULT_SCORED_CANDIDATES_PATH,
    )
    output_dir = env_path("BL007_OUTPUT_DIR", root / DEFAULT_OUTPUT_DIR)
    return PlaylistPaths(
        scored_candidates_path=scored_candidates_path,
        output_dir=output_dir,
    )


def read_scored_candidates(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("BL-007 scored candidates CSV has no header row.")
        missing_columns = [
            column for column in REQUIRED_CANDIDATE_COLUMNS if column not in set(reader.fieldnames)
        ]
        if missing_columns:
            raise ValueError(
                "BL-007 scored candidates CSV is missing required column(s): "
                + ", ".join(missing_columns)
            )
        return list(reader)


def write_assembly_trace(path: Path, trace_rows: list[dict[str, object]]) -> None:
    trace_fields = [
        "score_rank",
        "track_id",
        "lead_genre",
        "final_score",
        "decision",
        "playlist_position",
        "exclusion_reason",
    ]
    with open_text_write(path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=trace_fields)
        writer.writeheader()
        writer.writerows(trace_rows)


def write_playlist(path: Path, payload: dict[str, object]) -> None:
    write_json(path, payload)


def write_report(path: Path, payload: dict[str, object]) -> None:
    write_json(path, payload)


def write_detail_log(path: Path, payload: dict[str, object]) -> None:
    write_json(path, payload)


def last_n_genres(playlist: list[dict[str, object]], n: int) -> list[str]:
    return [str(track.get("_assembly_genre") or track.get("lead_genre", "")) for track in playlist[-n:]]


def decide_candidate(
    *,
    playlist: list[dict[str, object]],
    assembly_genre: str,
    target_size: int,
    max_per_genre: int,
    max_consecutive: int,
    rule_hits: Counter,
) -> tuple[str, str]:
    if len(playlist) >= target_size:
        rule_hits["R4_length_cap"] += 1
        return "excluded", "length_cap_reached"

    if sum(
        1
        for track in playlist
        if str(track.get("_assembly_genre", track.get("lead_genre", ""))) == assembly_genre
    ) >= max_per_genre:
        rule_hits["R2_genre_cap"] += 1
        return "excluded", "genre_cap_exceeded"

    if len(playlist) >= max_consecutive and all(
        genre == assembly_genre for genre in last_n_genres(playlist, max_consecutive)
    ):
        rule_hits["R3_consecutive_run"] += 1
        return "excluded", "consecutive_genre_run"

    return "included", ""


def _derive_assembly_genre(candidate: dict[str, object], strategy: str) -> str:
    lead_genre = str(candidate.get("lead_genre", "")).strip()
    if lead_genre:
        return lead_genre
    if strategy != "semantic_component_proxy":
        return UNKNOWN_GENRE_BUCKET

    lead_score = safe_float(candidate.get("lead_genre_contribution"), 0.0)
    genre_score = safe_float(candidate.get("genre_overlap_contribution"), 0.0)
    tag_score = safe_float(candidate.get("tag_overlap_contribution"), 0.0)
    strongest = max(lead_score, genre_score, tag_score)
    if strongest <= 0:
        return UNKNOWN_GENRE_BUCKET
    if strongest == genre_score:
        return "__semantic_genre__"
    if strongest == tag_score:
        return "__semantic_tag__"
    return "__semantic_lead__"


def _normalize_candidates(
    candidates: list[dict[str, object]],
    *,
    lead_genre_fallback_strategy: str,
) -> list[dict[str, object]]:
    normalized_candidates: list[dict[str, object]] = []
    for cand in candidates:
        semantic_strength = (
            safe_float(cand.get("lead_genre_contribution"), 0.0)
            + safe_float(cand.get("genre_overlap_contribution"), 0.0)
            + safe_float(cand.get("tag_overlap_contribution"), 0.0)
        )
        numeric_strength = (
            safe_float(cand.get("danceability_contribution"), 0.0)
            + safe_float(cand.get("energy_contribution"), 0.0)
            + safe_float(cand.get("valence_contribution"), 0.0)
            + safe_float(cand.get("tempo_contribution"), 0.0)
            + safe_float(cand.get("duration_ms_contribution"), 0.0)
            + safe_float(cand.get("popularity_contribution"), 0.0)
            + safe_float(cand.get("key_contribution"), 0.0)
            + safe_float(cand.get("mode_contribution"), 0.0)
        )
        lead_genre = str(cand.get("lead_genre", ""))
        assembly_genre = _derive_assembly_genre(cand, lead_genre_fallback_strategy)
        normalized_candidates.append(
            {
                "track_id": str(cand.get("track_id", "")),
                "lead_genre": lead_genre,
                "assembly_genre": assembly_genre,
                "final_score": round(safe_float(cand.get("final_score"), 0.0), 6),
                "score_rank": safe_int(cand.get("rank"), 0),
                "semantic_strength": round(semantic_strength, 6),
                "component_strength": round(semantic_strength + numeric_strength, 6),
            }
        )
    normalized_candidates.sort(key=lambda row: (safe_int(row["score_rank"], 0), str(row["track_id"])))
    return normalized_candidates


def _compute_effective_max_per_genre(
    candidates: list[dict[str, object]],
    base_max_per_genre: int,
    *,
    adaptive_limits: dict[str, object],
) -> int:
    if not bool(adaptive_limits.get("enabled", False)):
        return base_max_per_genre

    top_k = max(1, safe_int(adaptive_limits.get("reference_top_k"), 100))
    sample = candidates[:top_k]
    if not sample:
        return base_max_per_genre

    counts: Counter[str] = Counter(str(cand.get("assembly_genre", "")) for cand in sample)
    dominant_count = max(counts.values()) if counts else 0
    if dominant_count <= 0:
        return base_max_per_genre

    dominant_share = float(dominant_count) / float(len(sample))
    uniform_share = 1.0 / float(max(1, len(counts)))
    pressure = max(0.0, dominant_share - uniform_share)
    scale = 1.0 + pressure
    scale_min = max(0.0, safe_float(adaptive_limits.get("max_per_genre_scale_min"), 0.75))
    scale_max = max(scale_min, safe_float(adaptive_limits.get("max_per_genre_scale_max"), 1.25))
    scale = min(scale_max, max(scale_min, scale))
    return max(1, int(round(float(base_max_per_genre) * scale)))


def _apply_relaxation_round(
    *,
    current_max_per_genre: int,
    current_max_consecutive: int,
    base_max_consecutive: int,
    round_index: int,
    controlled_relaxation: dict[str, object],
) -> tuple[int, int]:
    relax_consecutive_first = bool(controlled_relaxation.get("relax_consecutive_first", True))
    increment = max(1, safe_int(controlled_relaxation.get("max_per_genre_increment"), 1))

    next_max_per_genre = current_max_per_genre
    next_max_consecutive = current_max_consecutive
    if relax_consecutive_first and round_index == 1:
        next_max_consecutive = max(current_max_consecutive, base_max_consecutive + 1)
    else:
        next_max_per_genre = current_max_per_genre + increment
    return next_max_per_genre, next_max_consecutive


def _candidate_utility(
    candidate: dict[str, object],
    *,
    playlist: list[dict[str, object]],
    utility_weights: dict[str, float],
    use_component_contributions_for_tiebreak: bool,
    use_semantic_strength_for_tiebreak: bool,
) -> float:
    score_weight = safe_float(utility_weights.get("score_weight"), 1.0)
    novelty_weight = safe_float(utility_weights.get("novelty_weight"), 0.0)
    repetition_penalty_weight = safe_float(utility_weights.get("repetition_penalty_weight"), 0.0)

    assembly_genre = str(candidate.get("assembly_genre", ""))
    genre_count = sum(
        1
        for track in playlist
        if str(track.get("_assembly_genre", track.get("lead_genre", ""))) == assembly_genre
    )
    novelty = 1.0 / float(1 + genre_count)
    repetition_penalty = 0.0
    if playlist:
        last_genre = str(playlist[-1].get("_assembly_genre", playlist[-1].get("lead_genre", "")))
        repetition_penalty = 1.0 if last_genre == assembly_genre else 0.0

    utility = (
        score_weight * safe_float(candidate.get("final_score"), 0.0)
        + novelty_weight * novelty
        - repetition_penalty_weight * repetition_penalty
    )
    if use_component_contributions_for_tiebreak:
        utility += safe_float(candidate.get("component_strength"), 0.0) * 0.0001
    if use_semantic_strength_for_tiebreak:
        utility += safe_float(candidate.get("semantic_strength"), 0.0) * 0.0001
    return round(utility, 9)


def _select_rank_round_robin_order(
    candidates: list[dict[str, object]],
    *,
    use_component_contributions_for_tiebreak: bool,
    use_semantic_strength_for_tiebreak: bool,
) -> list[dict[str, object]]:
    genre_buckets: dict[str, deque[dict[str, object]]] = {}
    for cand in candidates:
        genre = str(cand.get("assembly_genre", ""))
        genre_buckets.setdefault(genre, deque()).append(cand)

    for bucket in genre_buckets.values():
        sorted_rows = sorted(
            list(bucket),
            key=lambda row: (
                safe_int(row["score_rank"], 0),
                -safe_float(row.get("component_strength"), 0.0)
                if use_component_contributions_for_tiebreak
                else 0.0,
                -safe_float(row.get("semantic_strength"), 0.0)
                if use_semantic_strength_for_tiebreak
                else 0.0,
                str(row["track_id"]),
            ),
        )
        bucket.clear()
        bucket.extend(sorted_rows)

    genre_order = sorted(
        genre_buckets.keys(),
        key=lambda genre: (
            safe_int(genre_buckets[genre][0]["score_rank"], 0),
            str(genre),
        ),
    )
    ordered: list[dict[str, object]] = []
    while any(genre_buckets.values()):
        for genre in genre_order:
            bucket = genre_buckets.get(genre)
            if not bucket:
                continue
            ordered.append(bucket.popleft())
    return ordered


def assemble_bucketed(
    *,
    candidates: list[dict[str, object]],
    target_size: int,
    min_score_threshold: float,
    max_per_genre: int,
    max_consecutive: int,
    rule_hits: Counter,
    utility_strategy: str = "rank_round_robin",
    utility_weights: dict[str, float] | None = None,
    adaptive_limits: dict[str, object] | None = None,
    controlled_relaxation: dict[str, object] | None = None,
    lead_genre_fallback_strategy: str = "none",
    use_component_contributions_for_tiebreak: bool = False,
    use_semantic_strength_for_tiebreak: bool = False,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    utility_weights = utility_weights or {}
    adaptive_limits = adaptive_limits or {}
    controlled_relaxation = controlled_relaxation or {}

    normalized_candidates = _normalize_candidates(
        candidates,
        lead_genre_fallback_strategy=lead_genre_fallback_strategy,
    )

    playlist: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []

    eligible_by_rank: list[dict[str, object]] = []
    for cand in normalized_candidates:
        if safe_float(cand["final_score"], 0.0) < min_score_threshold:
            rule_hits["R1_score_threshold"] += 1
            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": cand["track_id"],
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": "excluded",
                    "playlist_position": "",
                    "exclusion_reason": "below_score_threshold",
                }
            )
            continue
        eligible_by_rank.append(cand)

    remaining: list[dict[str, object]] = list(eligible_by_rank)
    finalized_ids: set[str] = set()

    effective_max_per_genre = _compute_effective_max_per_genre(
        remaining,
        max_per_genre,
        adaptive_limits=adaptive_limits,
    )
    effective_max_consecutive = max_consecutive

    relaxation_enabled = bool(controlled_relaxation.get("enabled", False))
    max_relaxation_rounds = max(1, safe_int(controlled_relaxation.get("max_relaxation_rounds"), 2))
    relaxation_round = 0

    while len(playlist) < target_size and remaining:
        deferred: list[dict[str, object]] = []
        progressed = False

        if utility_strategy == "utility_greedy":
            ordered_candidates = sorted(
                remaining,
                key=lambda cand: (
                    -_candidate_utility(
                        cand,
                        playlist=playlist,
                        utility_weights=utility_weights,
                        use_component_contributions_for_tiebreak=use_component_contributions_for_tiebreak,
                        use_semantic_strength_for_tiebreak=use_semantic_strength_for_tiebreak,
                    ),
                    safe_int(cand["score_rank"], 0),
                    str(cand["track_id"]),
                ),
            )
        else:
            ordered_candidates = _select_rank_round_robin_order(
                remaining,
                use_component_contributions_for_tiebreak=use_component_contributions_for_tiebreak,
                use_semantic_strength_for_tiebreak=use_semantic_strength_for_tiebreak,
            )

        for cand in ordered_candidates:
            track_id = str(cand["track_id"])
            if track_id in finalized_ids:
                if cand in remaining:
                    remaining.remove(cand)
                continue
            if cand not in remaining:
                continue

            decision, exclusion_reason = decide_candidate(
                playlist=playlist,
                assembly_genre=str(cand["assembly_genre"]),
                target_size=target_size,
                max_per_genre=effective_max_per_genre,
                max_consecutive=effective_max_consecutive,
                rule_hits=rule_hits,
            )

            relaxable_exclusion = exclusion_reason in {"genre_cap_exceeded", "consecutive_genre_run"}
            if (
                decision == "excluded"
                and relaxable_exclusion
                and relaxation_enabled
                and relaxation_round < max_relaxation_rounds
            ):
                deferred.append(cand)
                continue

            playlist_position: int | str = ""
            if decision == "included":
                progressed = True
                playlist_position = len(playlist) + 1
                playlist.append(
                    {
                        "playlist_position": playlist_position,
                        "track_id": track_id,
                        "lead_genre": cand["lead_genre"],
                        "_assembly_genre": cand["assembly_genre"],
                        "final_score": cand["final_score"],
                        "score_rank": cand["score_rank"],
                    }
                )

            finalized_ids.add(track_id)
            remaining.remove(cand)
            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": track_id,
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": decision,
                    "playlist_position": playlist_position,
                    "exclusion_reason": exclusion_reason,
                }
            )

            if len(playlist) >= target_size:
                break

        if not progressed:
            if deferred and relaxation_enabled and relaxation_round < max_relaxation_rounds:
                relaxation_round += 1
                effective_max_per_genre, effective_max_consecutive = _apply_relaxation_round(
                    current_max_per_genre=effective_max_per_genre,
                    current_max_consecutive=effective_max_consecutive,
                    base_max_consecutive=max_consecutive,
                    round_index=relaxation_round,
                    controlled_relaxation=controlled_relaxation,
                )
                continue

            for cand in deferred:
                track_id = str(cand["track_id"])
                if track_id in finalized_ids or cand not in remaining:
                    continue
                _, final_reason = decide_candidate(
                    playlist=playlist,
                    assembly_genre=str(cand["assembly_genre"]),
                    target_size=target_size,
                    max_per_genre=effective_max_per_genre,
                    max_consecutive=effective_max_consecutive,
                    rule_hits=rule_hits,
                )
                finalized_ids.add(track_id)
                remaining.remove(cand)
                trace_rows.append(
                    {
                        "score_rank": cand["score_rank"],
                        "track_id": track_id,
                        "lead_genre": cand["lead_genre"],
                        "final_score": cand["final_score"],
                        "decision": "excluded",
                        "playlist_position": "",
                        "exclusion_reason": final_reason,
                    }
                )

            break

    if len(playlist) >= target_size:
        for cand in remaining:
            track_id = str(cand["track_id"])
            if track_id in finalized_ids:
                continue
            rule_hits["R4_length_cap"] += 1
            finalized_ids.add(track_id)
            trace_rows.append(
                {
                    "score_rank": cand["score_rank"],
                    "track_id": track_id,
                    "lead_genre": cand["lead_genre"],
                    "final_score": cand["final_score"],
                    "decision": "excluded",
                    "playlist_position": "",
                    "exclusion_reason": "length_cap_reached",
                }
            )

    for track in playlist:
        track.pop("_assembly_genre", None)

    trace_rows.sort(key=lambda row: (safe_int(row["score_rank"], 0), str(row["track_id"])))
    return playlist, trace_rows


def build_undersized_diagnostics(
    target_size: int,
    playlist_size: int,
    candidates_evaluated: int,
    trace_rows: list[dict[str, object]],
) -> dict[str, object]:
    is_undersized = playlist_size < target_size
    exclusion_counts = Counter(
        str(row.get("exclusion_reason") or "")
        for row in trace_rows
        if row.get("decision") == "excluded" and row.get("exclusion_reason")
    )

    reasons: list[str] = []
    if is_undersized:
        shortfall = target_size - playlist_size
        reasons.append(f"final playlist length is {playlist_size}/{target_size} (shortfall={shortfall})")
        if candidates_evaluated < target_size:
            reasons.append(
                f"candidate pool is smaller than target size ({candidates_evaluated} < {target_size})"
            )
        for reason, count in exclusion_counts.most_common(3):
            reasons.append(f"exclusion pressure: {reason} ({count} rows)")

    return {
        "is_undersized": is_undersized,
        "target_size": target_size,
        "actual_size": playlist_size,
        "shortfall": max(0, target_size - playlist_size),
        "exclusion_reason_counts": dict(exclusion_counts),
        "reasons": reasons,
    }


def build_rank_continuity_diagnostics(playlist: list[dict[str, object]]) -> dict[str, object]:
    selected_ranks = [safe_int(track["score_rank"], 0) for track in playlist]
    selected_scores = [safe_float(track["final_score"], 0.0) for track in playlist]
    max_selected_rank = max(selected_ranks) if selected_ranks else 0
    median_selected_rank = sorted(selected_ranks)[len(selected_ranks) // 2] if selected_ranks else 0
    rank_2_to_3_gap = 0.0
    if len(selected_scores) >= 3:
        rank_2_to_3_gap = round(selected_scores[1] - selected_scores[2], 6)

    return {
        "selected_ranks": selected_ranks,
        "max_selected_rank": max_selected_rank,
        "median_selected_rank": median_selected_rank,
        "rank_2_to_3_score_gap": rank_2_to_3_gap,
        "rank_cliff_detected": rank_2_to_3_gap >= 0.1,
    }


def build_assembly_pressure_diagnostics(
    trace_rows: list[dict[str, object]],
    *,
    exclusion_ratio_warn_threshold: float = 0.3,
    dominant_reason_share_warn_threshold: float = 0.7,
) -> dict[str, object]:
    top_100_rows = [row for row in trace_rows if safe_int(row["score_rank"], 0) <= 100]
    top_100_excluded = [row for row in top_100_rows if row["decision"] == "excluded"]
    reason_counts = Counter(
        str(row.get("exclusion_reason") or "")
        for row in top_100_excluded
        if row.get("exclusion_reason")
    )
    top_100_considered = len(top_100_rows)
    top_100_excluded_count = len(top_100_excluded)
    exclusion_ratio = round(
        (top_100_excluded_count / top_100_considered) if top_100_considered > 0 else 0.0,
        6,
    )
    dominant_reason = reason_counts.most_common(1)[0][0] if reason_counts else None
    dominant_reason_count = reason_counts.most_common(1)[0][1] if reason_counts else 0
    dominant_reason_share = round(
        (dominant_reason_count / top_100_excluded_count) if top_100_excluded_count > 0 else 0.0,
        6,
    )
    exclusion_ratio_warn_threshold = max(0.0, min(1.0, float(exclusion_ratio_warn_threshold)))
    dominant_reason_share_warn_threshold = max(0.0, min(1.0, float(dominant_reason_share_warn_threshold)))
    return {
        "top_100_considered": top_100_considered,
        "top_100_excluded": top_100_excluded_count,
        "top_100_exclusion_ratio": exclusion_ratio,
        "exclusion_ratio_warn_threshold": exclusion_ratio_warn_threshold,
        "exclusion_ratio_status": "warn" if exclusion_ratio >= exclusion_ratio_warn_threshold else "pass",
        "top_100_exclusion_reason_counts": dict(reason_counts),
        "dominant_top_100_exclusion_reason": dominant_reason,
        "dominant_top_100_exclusion_reason_share": dominant_reason_share,
        "dominant_reason_share_warn_threshold": dominant_reason_share_warn_threshold,
        "dominant_reason_share_status": "warn"
        if dominant_reason_share >= dominant_reason_share_warn_threshold
        else "pass",
    }


def build_assembly_detail_log(
    trace_rows: list[dict[str, object]],
    *,
    top_k: int = 100,
) -> dict[str, object]:
    top_window = max(1, int(top_k))
    top_rows = [row for row in trace_rows if safe_int(row["score_rank"], 0) <= top_window]
    included_ranks = sorted(
        safe_int(row["score_rank"], 0) for row in trace_rows if row["decision"] == "included"
    )

    detail_rows: list[dict[str, object]] = []
    for row in top_rows:
        current_rank = safe_int(row["score_rank"], 0)
        alternative_rank = next((rank for rank in included_ranks if rank > current_rank), None)
        detail_rows.append(
            {
                "score_rank": current_rank,
                "track_id": row["track_id"],
                "final_score": safe_float(row["final_score"], 0.0),
                "decision": row["decision"],
                "exclusion_reason": row.get("exclusion_reason", ""),
                "selected_alternative_rank": alternative_rank,
            }
        )

    return {"top_rank_window": top_window, "rows": detail_rows}


def build_opportunity_cost_diagnostics(
    trace_rows: list[dict[str, object]],
    *,
    top_k_examples: int = 10,
) -> dict[str, object]:
    excluded_rows = [row for row in trace_rows if row.get("decision") == "excluded"]
    top_examples_limit = max(1, int(top_k_examples))
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in excluded_rows:
        reason = str(row.get("exclusion_reason") or "unspecified")
        grouped.setdefault(reason, []).append(row)

    summary: dict[str, dict[str, object]] = {}
    for reason, rows in grouped.items():
        score_values = [safe_float(row.get("final_score"), 0.0) for row in rows]
        score_values.sort(reverse=True)
        sorted_rows = sorted(
            rows,
            key=lambda row: (
                -safe_float(row.get("final_score"), 0.0),
                safe_int(row.get("score_rank"), 0),
                str(row.get("track_id", "")),
            ),
        )
        summary[reason] = {
            "count": len(rows),
            "mean_score": round(sum(score_values) / max(1, len(score_values)), 6),
            "max_score": round(score_values[0], 6) if score_values else 0.0,
            "top_examples": [
                {
                    "track_id": row.get("track_id", ""),
                    "score_rank": safe_int(row.get("score_rank"), 0),
                    "final_score": round(safe_float(row.get("final_score"), 0.0), 6),
                }
                for row in sorted_rows[:top_examples_limit]
            ],
        }

    first_blocking_reason = None
    ranked_excluded = sorted(
        excluded_rows,
        key=lambda row: (safe_int(row.get("score_rank"), 0), str(row.get("track_id", ""))),
    )
    if ranked_excluded:
        first_blocking_reason = str(ranked_excluded[0].get("exclusion_reason") or "unspecified")

    return {
        "excluded_count": len(excluded_rows),
        "by_reason": summary,
        "fill_failure_frontier_reason": first_blocking_reason,
    }


class PlaylistStage:
    """Object-oriented BL-007 workflow shell over single-file helpers."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root if root is not None else impl_root()

    def resolve_paths(self) -> PlaylistPaths:
        return resolve_bl007_paths(self.root)

    @staticmethod
    def load_inputs(paths: PlaylistPaths) -> list[dict[str, str]]:
        return read_scored_candidates(paths.scored_candidates_path)

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
            exclusion_ratio_warn_threshold=controls.exclusion_ratio_warn_threshold,
            dominant_reason_share_warn_threshold=controls.dominant_reason_share_warn_threshold,
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
                "exclusion_ratio_warn_threshold": context.exclusion_ratio_warn_threshold,
                "dominant_reason_share_warn_threshold": context.dominant_reason_share_warn_threshold,
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
        assembly_pressure_diagnostics = build_assembly_pressure_diagnostics(
            aggregation.trace_rows,
            exclusion_ratio_warn_threshold=safe_float(config.get("exclusion_ratio_warn_threshold"), 0.3),
            dominant_reason_share_warn_threshold=safe_float(config.get("dominant_reason_share_warn_threshold"), 0.7),
        )
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
        candidates = self.load_inputs(paths)
        controls = self.resolve_runtime_controls()
        context = self.build_runtime_context(controls)

        aggregation = self.aggregate(
            candidates=[dict(candidate) for candidate in candidates],
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
            candidates_evaluated=len(candidates),
            playlist_path=playlist_path,
            trace_path=trace_path,
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


logger = logging.getLogger(__name__)


def main() -> None:
    artifacts = PlaylistStage().run()
    logger.info(
        "BL-007 playlist assembly complete. Playlist: %d/%d tracks",
        artifacts.playlist_size,
        artifacts.target_size,
    )
    logger.info("Run ID: %s", artifacts.run_id)
    logger.info("Genre mix: %s", artifacts.genre_mix)
    undersized_diagnostics = artifacts.undersized_diagnostics if isinstance(artifacts.undersized_diagnostics, dict) else {}
    if bool(undersized_diagnostics.get("is_undersized", False)):
        logger.warning("BL-007 produced an undersized playlist.")
        for reason in _string_list(undersized_diagnostics.get("reasons")):
            logger.warning("  - %s", reason)


if __name__ == "__main__":
    main()
