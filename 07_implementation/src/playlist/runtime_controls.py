"""Runtime control resolution for BL-007 playlist assembly."""

from __future__ import annotations

from shared_utils.constants import (
    DEFAULT_ASSEMBLY_CONTROLS,
    VALID_LEAD_GENRE_FALLBACK_STRATEGIES,
    VALID_UTILITY_STRATEGIES,
)
from shared_utils.env_utils import (
    coerce_dict,
    coerce_enum,
    coerce_float,
    coerce_int,
    env_bool,
    env_float,
    env_int,
    env_str,
)
from shared_utils.stage_runtime_resolver import defaults_loader, resolve_stage_controls


def _sanitize_bl007_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["target_size"] = max(1, coerce_int(controls.get("target_size"), 10))
    controls["min_score_threshold"] = max(
        0.0, min(1.0, coerce_float(controls.get("min_score_threshold"), 0.35)),
    )
    controls["max_per_genre"] = max(1, coerce_int(controls.get("max_per_genre"), 4))
    controls["max_consecutive"] = max(1, coerce_int(controls.get("max_consecutive"), 2))

    controls["utility_strategy"] = coerce_enum(
        controls.get("utility_strategy"), VALID_UTILITY_STRATEGIES, "rank_round_robin"
    )

    utility_weights = coerce_dict(controls.get("utility_weights"))
    controls["utility_weights"] = {
        "score_weight": max(0.0, coerce_float(utility_weights.get("score_weight"), 1.0)),
        "novelty_weight": max(0.0, coerce_float(utility_weights.get("novelty_weight"), 0.0)),
        "repetition_penalty_weight": max(0.0, coerce_float(utility_weights.get("repetition_penalty_weight"), 0.0)),
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
        controls.get("lead_genre_fallback_strategy"), VALID_LEAD_GENRE_FALLBACK_STRATEGIES, "none"
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
    return controls


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
    }


def resolve_bl007_runtime_controls() -> dict[str, object]:
    """Resolve BL-007 controls with payload-first precedence."""
    return resolve_stage_controls(
        load_from_env=_load_bl007_controls_from_env,
        load_payload_defaults=defaults_loader(DEFAULT_ASSEMBLY_CONTROLS),
        sanitize=_sanitize_bl007_controls,
    )
