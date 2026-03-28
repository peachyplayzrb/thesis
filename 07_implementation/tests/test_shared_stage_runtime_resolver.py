"""Tests for shared_utils.stage_runtime_resolver.resolve_stage_controls."""

from unittest.mock import patch

from shared_utils import stage_runtime_resolver as resolver


class _RunConfigUtilsStub:
    pass


def test_resolve_stage_controls_uses_env_when_no_run_config(monkeypatch) -> None:
    monkeypatch.setattr(resolver, "resolve_run_config_path", lambda: None)

    result = resolver.resolve_stage_controls(
        load_from_run_config=lambda _utils, _path: {"source": "run_config"},
        load_from_env=lambda: {"source": "env", "v": 2},
        sanitize=lambda data: {**data, "sanitized": True},
    )

    assert result == {"source": "env", "v": 2, "sanitized": True}


def test_resolve_stage_controls_uses_run_config_when_present(monkeypatch) -> None:
    monkeypatch.setattr(resolver, "resolve_run_config_path", lambda: "cfg.json")

    with patch("shared_utils.config_loader.load_run_config_utils_module", return_value=_RunConfigUtilsStub()):
        result = resolver.resolve_stage_controls(
            load_from_run_config=lambda _utils, path: {"source": "run_config", "path": path},
            load_from_env=lambda: {"source": "env"},
            sanitize=lambda data: data,
        )

    assert result == {"source": "run_config", "path": "cfg.json"}


def test_resolve_stage_controls_without_sanitize_returns_raw(monkeypatch) -> None:
    monkeypatch.setattr(resolver, "resolve_run_config_path", lambda: None)

    result = resolver.resolve_stage_controls(
        load_from_run_config=lambda _utils, _path: {"source": "run_config"},
        load_from_env=lambda: {"source": "env"},
    )

    assert result == {"source": "env"}
