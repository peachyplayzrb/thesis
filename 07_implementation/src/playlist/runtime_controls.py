"""Runtime control resolution for BL-007 playlist assembly."""

from __future__ import annotations

from shared_utils.env_utils import env_bool, env_float, env_int, env_str
from shared_utils.stage_runtime_resolver import resolve_stage_controls


DEFAULT_TARGET_SIZE = 10
DEFAULT_MIN_SCORE_THRESHOLD = 0.35
DEFAULT_MAX_PER_GENRE = 4
DEFAULT_MAX_CONSECUTIVE = 2
DEFAULT_UTILITY_STRATEGY = "rank_round_robin"


def _sanitize_bl007_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["target_size"] = max(1, int(controls["target_size"]))
    controls["min_score_threshold"] = max(
        0.0,
        min(1.0, float(controls["min_score_threshold"])),
    )
    controls["max_per_genre"] = max(1, int(controls["max_per_genre"]))
    controls["max_consecutive"] = max(1, int(controls["max_consecutive"]))

    utility_strategy = str(controls.get("utility_strategy") or DEFAULT_UTILITY_STRATEGY).strip().lower()
    controls["utility_strategy"] = (
        utility_strategy
        if utility_strategy in {"rank_round_robin", "utility_greedy"}
        else DEFAULT_UTILITY_STRATEGY
    )

    utility_weights_raw = controls.get("utility_weights")
    utility_weights = dict(utility_weights_raw) if isinstance(utility_weights_raw, dict) else {}
    controls["utility_weights"] = {
        "score_weight": max(0.0, float(utility_weights.get("score_weight", 1.0))),
        "novelty_weight": max(0.0, float(utility_weights.get("novelty_weight", 0.0))),
        "repetition_penalty_weight": max(0.0, float(utility_weights.get("repetition_penalty_weight", 0.0))),
    }

    adaptive_raw = controls.get("adaptive_limits")
    adaptive = dict(adaptive_raw) if isinstance(adaptive_raw, dict) else {}
    scale_min = max(0.0, float(adaptive.get("max_per_genre_scale_min", 0.75)))
    scale_max = max(scale_min, float(adaptive.get("max_per_genre_scale_max", 1.25)))
    controls["adaptive_limits"] = {
        "enabled": bool(adaptive.get("enabled", False)),
        "reference_top_k": max(1, int(adaptive.get("reference_top_k", 100))),
        "max_per_genre_scale_min": scale_min,
        "max_per_genre_scale_max": scale_max,
    }

    relax_raw = controls.get("controlled_relaxation")
    relax = dict(relax_raw) if isinstance(relax_raw, dict) else {}
    controls["controlled_relaxation"] = {
        "enabled": bool(relax.get("enabled", False)),
        "relax_consecutive_first": bool(relax.get("relax_consecutive_first", True)),
        "max_per_genre_increment": max(1, int(relax.get("max_per_genre_increment", 1))),
        "max_relaxation_rounds": max(1, int(relax.get("max_relaxation_rounds", 2))),
        "never_relax_score_threshold": bool(relax.get("never_relax_score_threshold", True)),
    }

    fallback_strategy = str(controls.get("lead_genre_fallback_strategy") or "none").strip().lower()
    controls["lead_genre_fallback_strategy"] = (
        fallback_strategy
        if fallback_strategy in {"none", "semantic_component_proxy"}
        else "none"
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
    controls["detail_log_top_k"] = max(1, int(controls.get("detail_log_top_k", 100)))
    return controls


def _load_bl007_controls_from_run_config(run_config_utils: object, run_config_path: str) -> dict[str, object]:
    controls = run_config_utils.resolve_bl007_controls(run_config_path)
    return {
        "config_source": "run_config",
        "run_config_path": controls.get("config_path"),
        "run_config_schema_version": controls.get("schema_version"),
        "target_size": int(controls["target_size"]),
        "min_score_threshold": float(controls["min_score_threshold"]),
        "max_per_genre": int(controls["max_per_genre"]),
        "max_consecutive": int(controls["max_consecutive"]),
        "utility_strategy": str(controls.get("utility_strategy") or DEFAULT_UTILITY_STRATEGY),
        "utility_weights": dict(controls.get("utility_weights") or {}),
        "adaptive_limits": dict(controls.get("adaptive_limits") or {}),
        "controlled_relaxation": dict(controls.get("controlled_relaxation") or {}),
        "lead_genre_fallback_strategy": str(controls.get("lead_genre_fallback_strategy") or "none"),
        "use_component_contributions_for_tiebreak": bool(
            controls.get("use_component_contributions_for_tiebreak", False)
        ),
        "use_semantic_strength_for_tiebreak": bool(
            controls.get("use_semantic_strength_for_tiebreak", False)
        ),
        "emit_opportunity_cost_metrics": bool(controls.get("emit_opportunity_cost_metrics", False)),
        "detail_log_top_k": int(controls.get("detail_log_top_k", 100)),
    }


def _load_bl007_controls_from_env() -> dict[str, object]:
    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "target_size": env_int("BL007_TARGET_SIZE", DEFAULT_TARGET_SIZE),
        "min_score_threshold": env_float(
            "BL007_MIN_SCORE_THRESHOLD",
            DEFAULT_MIN_SCORE_THRESHOLD,
        ),
        "max_per_genre": env_int("BL007_MAX_PER_GENRE", DEFAULT_MAX_PER_GENRE),
        "max_consecutive": env_int(
            "BL007_MAX_CONSECUTIVE",
            DEFAULT_MAX_CONSECUTIVE,
        ),
        "utility_strategy": env_str("BL007_UTILITY_STRATEGY", DEFAULT_UTILITY_STRATEGY),
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
            "BL007_USE_COMPONENT_CONTRIBUTIONS_FOR_TIEBREAK",
            False,
        ),
        "use_semantic_strength_for_tiebreak": env_bool(
            "BL007_USE_SEMANTIC_STRENGTH_FOR_TIEBREAK",
            False,
        ),
        "emit_opportunity_cost_metrics": env_bool("BL007_EMIT_OPPORTUNITY_COST_METRICS", False),
        "detail_log_top_k": env_int("BL007_DETAIL_LOG_TOP_K", 100),
    }


def resolve_bl007_runtime_controls() -> dict[str, object]:
    """Resolve BL-007 controls from run config first, then environment defaults."""
    return resolve_stage_controls(
        load_from_run_config=_load_bl007_controls_from_run_config,
        load_from_env=_load_bl007_controls_from_env,
        sanitize=_sanitize_bl007_controls,
    )
