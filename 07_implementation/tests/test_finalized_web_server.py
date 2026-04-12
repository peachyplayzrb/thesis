from __future__ import annotations

import importlib
from pathlib import Path


def _load_module():
    return importlib.import_module("finalized.web_server")


def test_config_choices_lists_profiles_json() -> None:
    module = _load_module()
    choices = module._config_choices()

    assert isinstance(choices, list)
    assert any(item.startswith("config/profiles/") for item in choices)


def test_resolve_config_path_rejects_path_traversal() -> None:
    module = _load_module()
    resolved, error = module._resolve_config_path("../../secrets.json")

    assert resolved is None
    assert error is not None


def test_resolve_config_path_accepts_known_profile() -> None:
    module = _load_module()
    resolved, error = module._resolve_config_path("run_config_ui013_tuning_v1f.json")

    assert error is None
    assert isinstance(resolved, Path)
    assert resolved.name == "run_config_ui013_tuning_v1f.json"


def test_build_run_command_uses_wrapper_and_flags() -> None:
    module = _load_module()
    config_path = module.IMPL_ROOT / "config" / "profiles" / "run_config_ui013_tuning_v1f.json"

    command = module._build_run_command(
        resolved_config=config_path,
        validate_only=True,
        continue_on_error=True,
    )

    assert command[0]
    assert command[1].endswith("main.py")
    assert "--run-config" in command
    assert "--validate-only" in command
    assert "--continue-on-error" in command


def test_artifact_preview_unknown_name_returns_404() -> None:
    module = _load_module()
    status_code, payload = module._artifact_preview("unknown_artifact")

    assert status_code == 404
    assert "error" in payload


def test_artifact_manifest_shape() -> None:
    module = _load_module()
    manifest = module._artifact_manifest()

    assert isinstance(manifest, list)
    assert manifest
    first = manifest[0]
    assert "name" in first
    assert "path" in first
    assert "exists" in first
