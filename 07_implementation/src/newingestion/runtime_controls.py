"""
Runtime control resolution for the newingestion stage.

Follows payload-first precedence:
1. BL_STAGE_CONFIG_JSON (orchestration payload)
2. Run-config file (from BL_RUN_CONFIG_PATH)
3. Environment defaults
4. Hardcoded defaults

This enables environment-aware tuning without modifying code.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .models import NewingestionControls, DEFAULT_NEWINGESTION_CONTROLS
from shared_utils.parsing import safe_float, safe_int


def _env_text(key: str) -> str | None:
    value = os.environ.get(key)
    return value if isinstance(value, str) else None


def _env_bool(key: str) -> Optional[bool]:
    value = _env_text(key)
    if value is None:
        return None
    return value.lower() in ["true", "1", "yes"]


def get_newingestion_payload() -> Optional[Dict[str, Any]]:
    """
    Extract newingestion control payload from BL_STAGE_CONFIG_JSON environment variable.

    Returns:
        Parsed payload dict, or None if not set.
    """
    payload_json = os.environ.get("BL_STAGE_CONFIG_JSON")
    if not payload_json:
        return None

    try:
        payload = json.loads(payload_json)
        # If payload has a stage-specific key, extract it
        if "newingestion" in payload:
            return payload["newingestion"]
        return payload
    except (json.JSONDecodeError, TypeError):
        return None


def load_newingestion_controls_from_runconfig(run_config_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load newingestion controls from a run-config file.

    Expected run-config structure includes a 'newingestion' key with control fields.

    Args:
        run_config_path: Path to run-config JSON or YAML

    Returns:
        Parsed controls dict, or None if not found/readable.
    """
    if not run_config_path.exists():
        return None

    try:
        if run_config_path.suffix == ".json":
            with open(run_config_path, "r") as f:
                run_config = json.load(f)
        elif run_config_path.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                with open(run_config_path, "r") as f:
                    run_config = yaml.safe_load(f)
            except ImportError:
                # YAML not available; skip
                return None
        else:
            return None

        return run_config.get("newingestion")
    except Exception:
        return None


def load_newingestion_controls_from_env() -> Dict[str, Any]:
    """
    Load newingestion controls from environment variables.

    Looks for BL_NEWINGESTION_* prefixed variables.

    Returns:
        Dict of environment-derived controls (may be empty).
    """
    env_controls = {}

    # Boolean flags
    for flag in ["include_top_tracks", "include_saved_tracks", "include_playlists", "include_recently_played"]:
        env_key = f"BL_NEWINGESTION_{flag.upper()}"
        parsed = _env_bool(env_key)
        if parsed is not None:
            env_controls[flag] = parsed

    # Integer limits
    for limit in ["max_top_tracks", "max_saved_tracks", "max_playlist_items", "max_recently_played"]:
        env_key = f"BL_NEWINGESTION_{limit.upper()}"
        value = _env_text(env_key)
        if value is not None:
            try:
                env_controls[limit] = safe_int(value)
            except (ValueError, TypeError):
                pass

    # Float settings
    for setting in ["throttle_sleep_seconds", "base_backoff_delay_seconds"]:
        env_key = f"BL_NEWINGESTION_{setting.upper()}"
        value = _env_text(env_key)
        if value is not None:
            try:
                env_controls[setting] = safe_float(value)
            except (ValueError, TypeError):
                pass

    # String settings
    for setting in ["source_type"]:
        env_key = f"BL_NEWINGESTION_{setting.upper()}"
        value = _env_text(env_key)
        if value is not None:
            env_controls[setting] = value

    # OAuth settings
    parsed_interactive = _env_bool("BL_NEWINGESTION_ENABLE_INTERACTIVE_OAUTH")
    if parsed_interactive is not None:
        env_controls["enable_interactive_oauth"] = parsed_interactive
    oauth_client_id = _env_text("BL_NEWINGESTION_OAUTH_CLIENT_ID")
    if oauth_client_id is not None:
        env_controls["oauth_client_id"] = oauth_client_id
    oauth_client_secret = _env_text("BL_NEWINGESTION_OAUTH_CLIENT_SECRET")
    if oauth_client_secret is not None:
        env_controls["oauth_client_secret"] = oauth_client_secret
    oauth_redirect_uri = _env_text("BL_NEWINGESTION_OAUTH_REDIRECT_URI")
    if oauth_redirect_uri is not None:
        env_controls["oauth_redirect_uri"] = oauth_redirect_uri
    oauth_timeout_seconds = _env_text("BL_NEWINGESTION_OAUTH_TIMEOUT_SECONDS")
    if oauth_timeout_seconds is not None:
        env_controls["oauth_timeout_seconds"] = safe_int(oauth_timeout_seconds)
    oauth_no_browser = _env_bool("BL_NEWINGESTION_OAUTH_NO_BROWSER")
    if oauth_no_browser is not None:
        env_controls["oauth_no_browser"] = oauth_no_browser

    return env_controls


def _sanitize_newingestion_controls(controls_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize controls dict.

    Clamps values to acceptable ranges and rejects invalid combinations.

    Args:
        controls_dict: Raw controls dict from any source

    Returns:
        Sanitized controls dict
    """
    sanitized = controls_dict.copy()

    # Clamp numeric values to valid ranges
    if "cache_ttl_seconds" in sanitized:
        sanitized["cache_ttl_seconds"] = max(1, min(86400, sanitized["cache_ttl_seconds"]))

    if "throttle_sleep_seconds" in sanitized:
        sanitized["throttle_sleep_seconds"] = max(0.01, min(10.0, sanitized["throttle_sleep_seconds"]))

    if "max_retries" in sanitized:
        sanitized["max_retries"] = max(0, min(10, sanitized["max_retries"]))

    if "base_backoff_delay_seconds" in sanitized:
        sanitized["base_backoff_delay_seconds"] = max(0.1, min(60.0, sanitized["base_backoff_delay_seconds"]))

    # Validate source_type
    VALID_SOURCES = ["spotify_api", "csv_history"]
    if "source_type" in sanitized and sanitized["source_type"] not in VALID_SOURCES:
        sanitized["source_type"] = "spotify_api"

    return sanitized


def resolve_newingestion_runtime_controls(
    run_config_path: Optional[Path] = None,
) -> NewingestionControls:
    """
    Resolve runtime controls for newingestion stage.

    Follows payload-first precedence:
    1. BL_STAGE_CONFIG_JSON (orchestration payload)
    2. Run-config file
    3. Environment variables
    4. Hardcoded defaults

    Args:
        run_config_path: Optional path to run-config file

    Returns:
        Resolved NewingestionControls
    """
    # Start with defaults
    merged = DEFAULT_NEWINGESTION_CONTROLS.as_mapping().copy()

    # Layer 3: Environment variables
    env_controls = load_newingestion_controls_from_env()
    merged.update(env_controls)

    # Layer 2: Run-config file
    if run_config_path:
        runconfig_controls = load_newingestion_controls_from_runconfig(run_config_path)
        if runconfig_controls:
            merged.update(runconfig_controls)

    # Layer 1: Orchestration payload (highest priority)
    payload_controls = get_newingestion_payload()
    if payload_controls:
        merged.update(payload_controls)

    # Sanitize
    sanitized = _sanitize_newingestion_controls(merged)

    # Construct typed object
    return NewingestionControls(**{k: v for k, v in sanitized.items() if k in NewingestionControls.__dataclass_fields__})
