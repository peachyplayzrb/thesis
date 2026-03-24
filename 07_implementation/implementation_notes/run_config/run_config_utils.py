from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

RUN_CONFIG_SCHEMA_VERSION = "run-config-v1"

DEFAULT_RUN_CONFIG: dict[str, Any] = {
    "schema_version": RUN_CONFIG_SCHEMA_VERSION,
    "user_context": {
        "user_id": None,
    },
    "input_scope": {
        "source_family": "spotify_api_export",
        "include_top_tracks": True,
        "top_time_ranges": ["short_term", "medium_term", "long_term"],
        "include_saved_tracks": True,
        "saved_tracks_limit": None,
        "include_playlists": True,
        "playlists_limit": None,
        "playlist_items_per_playlist_limit": None,
        "include_recently_played": True,
        "recently_played_limit": 50,
    },
    "interaction_scope": {
        "include_interaction_types": ["history", "influence"],
    },
    "influence_tracks": {
        "enabled": True,
        "track_ids": [],
        "source": None,
    },
    "profile_controls": {
        "top_tag_limit": 10,
        "top_genre_limit": 10,
        "top_lead_genre_limit": 10,
    },
    "retrieval_controls": {
        "profile_top_tag_limit": 10,
        "profile_top_genre_limit": 8,
        "profile_top_lead_genre_limit": 6,
        "semantic_strong_keep_score": 2,
        "semantic_min_keep_score": 1,
        "numeric_support_min_pass": 1,
        "numeric_thresholds": {
            "tempo": 20.0,
            "key": 2.0,
            "mode": 0.5,
            "duration_ms": 45000.0,
        },
    },
    "scoring_controls": {
        "component_weights": {
            "tempo": 0.20,
            "duration_ms": 0.13,
            "key": 0.13,
            "mode": 0.09,
            "lead_genre": 0.17,
            "genre_overlap": 0.12,
            "tag_overlap": 0.16,
        },
        "numeric_thresholds": {
            "tempo": 20.0,
            "key": 2.0,
            "mode": 0.5,
            "duration_ms": 45000.0,
        },
    },
    "assembly_controls": {
        "target_size": 10,
        "min_score_threshold": 0.35,
        "max_per_genre": 4,
        "max_consecutive": 2,
    },
    "transparency_controls": {
        "top_contributor_limit": 3,
    },
    "observability_controls": {
        "diagnostic_sample_limit": 5,
    },
}


class RunConfigError(RuntimeError):
    pass


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _coerce_optional_positive_int(value: Any, default: int | None) -> int | None:
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"1", "true", "yes", "on"}:
            return True
        if text in {"0", "false", "no", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _coerce_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def canonical_default_run_config() -> dict[str, Any]:
    return deepcopy(DEFAULT_RUN_CONFIG)


def load_run_config(run_config_path: str | Path | None) -> dict[str, Any] | None:
    if run_config_path is None:
        return None
    path = Path(run_config_path)
    if not path.exists():
        raise RunConfigError(f"Run config file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RunConfigError(f"Run config JSON is invalid: {path}") from exc
    if not isinstance(payload, dict):
        raise RunConfigError(f"Run config must be a JSON object: {path}")
    return payload


def resolve_effective_run_config(run_config_path: str | Path | None) -> tuple[dict[str, Any], Path | None]:
    path = Path(run_config_path).resolve() if run_config_path else None
    payload = load_run_config(path) if path else None
    if payload is None:
        effective = canonical_default_run_config()
    else:
        effective = _deep_merge(canonical_default_run_config(), payload)

    schema_version = effective.get("schema_version")
    if schema_version is None:
        effective["schema_version"] = RUN_CONFIG_SCHEMA_VERSION
    elif schema_version != RUN_CONFIG_SCHEMA_VERSION:
        raise RunConfigError(
            f"Unsupported run config schema_version '{schema_version}'. Expected '{RUN_CONFIG_SCHEMA_VERSION}'."
        )

    user_context = effective.setdefault("user_context", {})
    if not isinstance(user_context, dict):
        raise RunConfigError("run_config.user_context must be an object")
    user_context["user_id"] = _coerce_optional_str(user_context.get("user_id"))

    input_scope = effective.setdefault("input_scope", {})
    if not isinstance(input_scope, dict):
        raise RunConfigError("run_config.input_scope must be an object")
    input_defaults = DEFAULT_RUN_CONFIG["input_scope"]
    input_scope["source_family"] = _coerce_optional_str(
        input_scope.get("source_family")
    ) or str(input_defaults["source_family"])
    input_scope["include_top_tracks"] = _coerce_bool(
        input_scope.get("include_top_tracks"),
        bool(input_defaults["include_top_tracks"]),
    )
    raw_time_ranges = input_scope.get("top_time_ranges")
    if isinstance(raw_time_ranges, list):
        allowed = {"short_term", "medium_term", "long_term"}
        normalized = [
            str(item).strip()
            for item in raw_time_ranges
            if str(item).strip() in allowed
        ]
        input_scope["top_time_ranges"] = normalized or list(input_defaults["top_time_ranges"])
    else:
        input_scope["top_time_ranges"] = list(input_defaults["top_time_ranges"])
    input_scope["include_saved_tracks"] = _coerce_bool(
        input_scope.get("include_saved_tracks"),
        bool(input_defaults["include_saved_tracks"]),
    )
    input_scope["saved_tracks_limit"] = _coerce_optional_positive_int(
        input_scope.get("saved_tracks_limit"),
        input_defaults["saved_tracks_limit"],
    )
    input_scope["include_playlists"] = _coerce_bool(
        input_scope.get("include_playlists"),
        bool(input_defaults["include_playlists"]),
    )
    input_scope["playlists_limit"] = _coerce_optional_positive_int(
        input_scope.get("playlists_limit"),
        input_defaults["playlists_limit"],
    )
    input_scope["playlist_items_per_playlist_limit"] = _coerce_optional_positive_int(
        input_scope.get("playlist_items_per_playlist_limit"),
        input_defaults["playlist_items_per_playlist_limit"],
    )
    input_scope["include_recently_played"] = _coerce_bool(
        input_scope.get("include_recently_played"),
        bool(input_defaults["include_recently_played"]),
    )
    input_scope["recently_played_limit"] = _coerce_optional_positive_int(
        input_scope.get("recently_played_limit"),
        input_defaults["recently_played_limit"],
    )

    profile_controls = effective.setdefault("profile_controls", {})
    if not isinstance(profile_controls, dict):
        raise RunConfigError("run_config.profile_controls must be an object")
    profile_controls["top_tag_limit"] = _coerce_positive_int(
        profile_controls.get("top_tag_limit"),
        DEFAULT_RUN_CONFIG["profile_controls"]["top_tag_limit"],
    )
    profile_controls["top_genre_limit"] = _coerce_positive_int(
        profile_controls.get("top_genre_limit"),
        DEFAULT_RUN_CONFIG["profile_controls"]["top_genre_limit"],
    )
    profile_controls["top_lead_genre_limit"] = _coerce_positive_int(
        profile_controls.get("top_lead_genre_limit"),
        DEFAULT_RUN_CONFIG["profile_controls"]["top_lead_genre_limit"],
    )

    return effective, path


def resolve_bl004_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    user_context = effective["user_context"]
    profile_controls = effective["profile_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "user_id": user_context.get("user_id"),
        "input_scope": dict(effective["input_scope"]),
        "top_tag_limit": profile_controls["top_tag_limit"],
        "top_genre_limit": profile_controls["top_genre_limit"],
        "top_lead_genre_limit": profile_controls["top_lead_genre_limit"],
    }


def resolve_input_scope_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "input_scope": dict(effective["input_scope"]),
    }


def resolve_bl005_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    retrieval = effective["retrieval_controls"]
    defaults = DEFAULT_RUN_CONFIG["retrieval_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "profile_top_lead_genre_limit": _coerce_positive_int(
            retrieval.get("profile_top_lead_genre_limit"),
            defaults["profile_top_lead_genre_limit"],
        ),
        "profile_top_tag_limit": _coerce_positive_int(
            retrieval.get("profile_top_tag_limit"),
            defaults["profile_top_tag_limit"],
        ),
        "profile_top_genre_limit": _coerce_positive_int(
            retrieval.get("profile_top_genre_limit"),
            defaults["profile_top_genre_limit"],
        ),
        "semantic_strong_keep_score": _coerce_positive_int(
            retrieval.get("semantic_strong_keep_score"),
            defaults["semantic_strong_keep_score"],
        ),
        "semantic_min_keep_score": _coerce_positive_int(
            retrieval.get("semantic_min_keep_score"),
            defaults["semantic_min_keep_score"],
        ),
        "numeric_support_min_pass": _coerce_positive_int(
            retrieval.get("numeric_support_min_pass"),
            defaults["numeric_support_min_pass"],
        ),
        "numeric_thresholds": dict(
            retrieval.get("numeric_thresholds") or defaults["numeric_thresholds"]
        ),
    }


def resolve_bl006_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    scoring = effective["scoring_controls"]
    defaults = DEFAULT_RUN_CONFIG["scoring_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "component_weights": dict(
            scoring.get("component_weights") or defaults["component_weights"]
        ),
        "numeric_thresholds": dict(
            scoring.get("numeric_thresholds") or defaults["numeric_thresholds"]
        ),
    }


def resolve_bl007_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    assembly = effective["assembly_controls"]
    defaults = DEFAULT_RUN_CONFIG["assembly_controls"]
    min_threshold = assembly.get("min_score_threshold")
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "target_size": _coerce_positive_int(
            assembly.get("target_size"),
            defaults["target_size"],
        ),
        "min_score_threshold": float(
            min_threshold if min_threshold is not None else defaults["min_score_threshold"]
        ),
        "max_per_genre": _coerce_positive_int(
            assembly.get("max_per_genre"),
            defaults["max_per_genre"],
        ),
        "max_consecutive": _coerce_positive_int(
            assembly.get("max_consecutive"),
            defaults["max_consecutive"],
        ),
    }


def resolve_bl008_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    transparency = effective["transparency_controls"]
    defaults = DEFAULT_RUN_CONFIG["transparency_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "top_contributor_limit": _coerce_positive_int(
            transparency.get("top_contributor_limit"),
            defaults["top_contributor_limit"],
        ),
    }


def resolve_bl009_controls(run_config_path: str | Path | None) -> dict[str, Any]:
    effective, resolved_path = resolve_effective_run_config(run_config_path)
    observability = effective["observability_controls"]
    defaults = DEFAULT_RUN_CONFIG["observability_controls"]
    return {
        "config_path": str(resolved_path) if resolved_path else None,
        "schema_version": effective["schema_version"],
        "diagnostic_sample_limit": _coerce_positive_int(
            observability.get("diagnostic_sample_limit"),
            defaults["diagnostic_sample_limit"],
        ),
    }
