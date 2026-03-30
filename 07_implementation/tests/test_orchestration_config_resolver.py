"""Tests for orchestration.config_resolver."""

from __future__ import annotations

from pathlib import Path

from orchestration import config_resolver


class _FakeRunConfigUtils:
    def __init__(self) -> None:
        self.oc_calls: list[str | None] = []
        self.artifact_calls: list[tuple[str, str | None, str, str]] = []

    def resolve_bl013_orchestration_controls(self, run_config_path: str | None) -> dict[str, object]:
        self.oc_calls.append(run_config_path)
        return {
            "stage_order": ["BL-004", "BL-005"],
            "continue_on_error": False,
            "refresh_seed_policy": "auto_if_stale",
        }

    def write_run_config_artifact_pair(
        self,
        *,
        run_id: str,
        output_dir: Path,
        run_config_path: Path | None,
        generated_at_utc: str,
    ) -> dict[str, object]:
        self.artifact_calls.append(
            (run_id, str(run_config_path) if run_config_path else None, str(output_dir), generated_at_utc)
        )
        return {
            "run_intent": {"path": str(output_dir / "run_intent.json")},
            "run_effective_config": {"path": str(output_dir / "run_effective_config.json")},
        }


def test_resolve_orchestration_controls_uses_run_config_utils(monkeypatch) -> None:
    fake = _FakeRunConfigUtils()
    monkeypatch.setattr(config_resolver, "load_run_config_utils_module", lambda: fake)

    run_config_path = Path("config/profiles/run_config_ui013_tuning_v1f.json")
    controls = config_resolver.resolve_orchestration_controls(run_config_path)

    assert controls["stage_order"] == ["BL-004", "BL-005"]
    assert fake.oc_calls == [str(run_config_path)]


def test_emit_run_config_artifact_pair_delegates_to_run_config_utils(monkeypatch, tmp_path) -> None:
    fake = _FakeRunConfigUtils()
    monkeypatch.setattr(config_resolver, "load_run_config_utils_module", lambda: fake)

    run_config_path = tmp_path / "run_config.json"
    artifacts = config_resolver.emit_run_config_artifact_pair(
        run_id="BL013-ENTRYPOINT-TEST",
        run_config_path=run_config_path,
        artifact_dir=tmp_path,
        generated_at_utc="2026-03-30T12:00:00Z",
    )

    assert "run_intent" in artifacts
    assert "run_effective_config" in artifacts
    assert fake.artifact_calls == [
        (
            "BL013-ENTRYPOINT-TEST",
            str(run_config_path),
            str(tmp_path),
            "2026-03-30T12:00:00Z",
        )
    ]
