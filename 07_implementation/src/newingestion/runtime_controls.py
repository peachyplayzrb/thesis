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
        if env_key in os.environ:
            env_controls[flag] = os.environ.get(env_key).lower() in ["true", "1", "yes"]

    # Integer limits
    for limit in ["max_top_tracks", "max_saved_tracks", "max_playlist_items", "max_recently_played"]:
        env_key = f"BL_NEWINGESTION_{limit.upper()}"
        if env_key in os.environ:
            try:
                env_controls[limit] = int(os.environ.get(env_key))
            except (ValueError, TypeError):
                pass

    # Float settings
    for setting in ["throttle_sleep_seconds", "base_backoff_delay_seconds"]:
        env_key = f"BL_NEWINGESTION_{setting.upper()}"
        if env_key in os.environ:
            try:
                env_controls[setting] = float(os.environ.get(env_key))
            except (ValueError, TypeError):
                pass

    # String settings
    for setting in ["source_type"]:
        env_key = f"BL_NEWINGESTION_{setting.upper()}"
        if env_key in os.environ:
            env_controls[setting] = os.environ.get(env_key)

    # OAuth settings
    if "BL_NEWINGESTION_ENABLE_INTERACTIVE_OAUTH" in os.environ:
        env_controls["enable_interactive_oauth"] = os.environ.get("BL_NEWINGESTION_ENABLE_INTERACTIVE_OAUTH").lower() in ["true", "1", "yes"]
    if "BL_NEWINGESTION_OAUTH_CLIENT_ID" in os.environ:
        env_controls["oauth_client_id"] = os.environ.get("BL_NEWINGESTION_OAUTH_CLIENT_ID")
    if "BL_NEWINGESTION_OAUTH_CLIENT_SECRET" in os.environ:
        env_controls["oauth_client_secret"] = os.environ.get("BL_NEWINGESTION_OAUTH_CLIENT_SECRET")
    if "BL_NEWINGESTION_OAUTH_REDIRECT_URI" in os.environ:
        env_controls["oauth_redirect_uri"] = os.environ.get("BL_NEWINGESTION_OAUTH_REDIRECT_URI")
    if "BL_NEWINGESTION_OAUTH_TIMEOUT_SECONDS" in os.environ:
        try:
            env_controls["oauth_timeout_seconds"] = int(os.environ.get("BL_NEWINGESTION_OAUTH_TIMEOUT_SECONDS"))
        except (ValueError, TypeError):
            pass
    if "BL_NEWINGESTION_OAUTH_NO_BROWSER" in os.environ:
        env_controls["oauth_no_browser"] = os.environ.get("BL_NEWINGESTION_OAUTH_NO_BROWSER").lower() in ["true", "1", "yes"]

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
