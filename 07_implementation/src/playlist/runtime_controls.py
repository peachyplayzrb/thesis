"""Runtime control resolution for BL-007 playlist assembly."""

from __future__ import annotations

from shared_utils.env_utils import env_float, env_int
from shared_utils.stage_runtime_resolver import resolve_stage_controls


DEFAULT_TARGET_SIZE = 10
DEFAULT_MIN_SCORE_THRESHOLD = 0.35
DEFAULT_MAX_PER_GENRE = 4
DEFAULT_MAX_CONSECUTIVE = 2


def _sanitize_bl007_controls(controls: dict[str, object]) -> dict[str, object]:
    controls["target_size"] = max(1, int(controls["target_size"]))
    controls["min_score_threshold"] = max(
        0.0,
        min(1.0, float(controls["min_score_threshold"])),
    )
    controls["max_per_genre"] = max(1, int(controls["max_per_genre"]))
    controls["max_consecutive"] = max(1, int(controls["max_consecutive"]))
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
    }


def resolve_bl007_runtime_controls() -> dict[str, object]:
    """Resolve BL-007 controls from run config first, then environment defaults."""
    return resolve_stage_controls(
        load_from_run_config=_load_bl007_controls_from_run_config,
        load_from_env=_load_bl007_controls_from_env,
        sanitize=_sanitize_bl007_controls,
    )
