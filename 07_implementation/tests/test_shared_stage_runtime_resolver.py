"""Tests for shared_utils.stage_runtime_resolver.resolve_stage_controls."""

from shared_utils import stage_runtime_resolver as resolver


def test_resolve_stage_controls_uses_env_when_no_payload(monkeypatch) -> None:
    monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)

    result = resolver.resolve_stage_controls(
        load_from_env=lambda: {"source": "env", "v": 2},
        sanitize=lambda data: {**data, "sanitized": True},
    )

    assert result == {"source": "env", "v": 2, "sanitized": True}


def test_resolve_stage_controls_without_sanitize_returns_raw(monkeypatch) -> None:
    monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)

    result = resolver.resolve_stage_controls(
        load_from_env=lambda: {"source": "env"},
    )

    assert result == {"source": "env"}


def test_resolve_stage_controls_prefers_stage_payload_over_env(monkeypatch) -> None:
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", '{"controls": {"source": "payload", "v": 3}}')

    result = resolver.resolve_stage_controls(
        load_from_env=lambda: {"source": "env"},
        sanitize=lambda data: data,
    )

    assert result == {"source": "payload", "v": 3}


def test_resolve_stage_controls_invalid_payload_falls_back_to_env(monkeypatch) -> None:
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", "{not-json")

    result = resolver.resolve_stage_controls(
        load_from_env=lambda: {"source": "env", "fallback": True},
        sanitize=lambda data: data,
    )

    assert result == {"source": "env", "fallback": True}


def test_resolve_stage_controls_supports_payload_envelope(monkeypatch) -> None:
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        '{"stage_id":"BL-007","schema_version":"1.0","resolved_from":"defaults","controls":{"source":"payload","v":7}}',
    )

    result = resolver.resolve_stage_controls(
        load_from_env=lambda: {"source": "env"},
        sanitize=lambda data: data,
    )

    assert result == {"source": "payload", "v": 7}


def test_resolve_stage_controls_require_payload_raises_when_missing(monkeypatch) -> None:
    monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)

    try:
        resolver.resolve_stage_controls(
            load_from_env=lambda: {"source": "env"},
            require_payload=True,
        )
        assert False, "Expected RuntimeError when payload is required"
    except RuntimeError as exc:
        assert "BL_STAGE_CONFIG_JSON" in str(exc)
