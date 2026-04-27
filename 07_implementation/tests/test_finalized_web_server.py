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


def test_pipeline_flow_payload_shape() -> None:
    module = _load_module()
    payload = module._pipeline_flow_payload()

    assert isinstance(payload, dict)
    assert "stages" in payload
    assert isinstance(payload["stages"], list)
    assert any(item.get("stage_id") == "bl003" for item in payload["stages"])
    assert any(item.get("stage_id") == "bl009" for item in payload["stages"])


def test_stage_explainer_payload_unknown_stage() -> None:
    module = _load_module()
    status_code, payload = module._stage_explainer_payload("bl999")

    assert status_code == 404
    assert "error" in payload


def test_stage_explainer_payload_known_stage_shape() -> None:
    module = _load_module()
    status_code, payload = module._stage_explainer_payload("bl005")

    assert status_code == 200
    assert payload["stage_id"] == "bl005"
    assert "metrics" in payload
    assert isinstance(payload["artifacts"], list)


def test_explanation_view_payload_shape() -> None:
    module = _load_module()
    status_code, payload = module._explanation_view_payload(limit=3)

    assert status_code == 200
    assert "tracks" in payload
    assert isinstance(payload["tracks"], list)
    assert payload["returned_track_count"] <= 3


def test_evidence_dashboard_payload_shape() -> None:
    module = _load_module()
    payload = module._evidence_dashboard_payload()

    assert isinstance(payload, dict)
    assert "bl013" in payload
    assert "bl014" in payload
    assert "bl009" in payload


def test_explanation_view_payload_missing_artifact(monkeypatch) -> None:
    module = _load_module()

    def _fake_loader(_path):
        return None

    monkeypatch.setattr(module, "_load_json_or_none", _fake_loader)
    status_code, payload = module._explanation_view_payload(limit=3)

    assert status_code == 404
    assert "error" in payload


def test_explanation_view_payload_malformed_explanations(monkeypatch) -> None:
    module = _load_module()

    def _fake_loader(_path):
        return {"explanations": "not-a-list"}

    monkeypatch.setattr(module, "_load_json_or_none", _fake_loader)
    status_code, payload = module._explanation_view_payload(limit=3)

    assert status_code == 500
    assert "error" in payload


def test_explanation_view_payload_clamps_large_limit(monkeypatch) -> None:
    module = _load_module()
    mock_rows = []
    for index in range(100):
        mock_rows.append(
            {
                "playlist_position": index + 1,
                "track_id": f"track-{index}",
                "final_score": 0.5,
                "why_selected": "reason",
                "narrative_driver": {"label": "Tag overlap"},
                "top_score_contributors": [{"label": "Tag overlap"}],
            }
        )

    def _fake_loader(_path):
        return {
            "run_id": "BL008-TEST",
            "generated_at_utc": "2026-04-13T00:00:00Z",
            "playlist_track_count": 100,
            "explanations": mock_rows,
        }

    monkeypatch.setattr(module, "_load_json_or_none", _fake_loader)
    status_code, payload = module._explanation_view_payload(limit=999)

    assert status_code == 200
    assert payload["returned_track_count"] == module.EXPLAINER_TRACK_LIMIT_MAX


def test_explanation_view_payload_driver_distribution(monkeypatch) -> None:
    module = _load_module()

    def _fake_loader(_path):
        return {
            "run_id": "BL008-TEST",
            "generated_at_utc": "2026-04-13T00:00:00Z",
            "playlist_track_count": 3,
            "explanations": [
                {
                    "playlist_position": 1,
                    "track_id": "t1",
                    "final_score": 0.9,
                    "why_selected": "x",
                    "narrative_driver": {"label": "Tag overlap"},
                    "top_score_contributors": [{"label": "Tag overlap"}],
                },
                {
                    "playlist_position": 2,
                    "track_id": "t2",
                    "final_score": 0.8,
                    "why_selected": "y",
                    "narrative_driver": {"label": "Genre overlap"},
                    "top_score_contributors": [{"label": "Genre overlap"}],
                },
                {
                    "playlist_position": 3,
                    "track_id": "t3",
                    "final_score": 0.7,
                    "why_selected": "z",
                    "narrative_driver": {"label": "Tag overlap"},
                    "top_score_contributors": [{"label": "Tag overlap"}],
                },
            ],
        }

    monkeypatch.setattr(module, "_load_json_or_none", _fake_loader)
    status_code, payload = module._explanation_view_payload(limit=10)

    assert status_code == 200
    assert payload["driver_distribution"]["Tag overlap"] == 2
    assert payload["driver_distribution"]["Genre overlap"] == 1


def test_evidence_dashboard_payload_extracts_failed_checks(monkeypatch) -> None:
    module = _load_module()
    path_map = module.ARTIFACT_PATHS

    def _fake_loader(path):
        if path == path_map["bl013_latest"]:
            return {
                "run_id": "BL013-TEST",
                "overall_status": "pass",
                "executed_stage_count": 2,
                "failed_stage_count": 0,
                "stage_results": [{"stage_id": "BL-003", "status": "pass", "elapsed_seconds": 1.2, "return_code": 0}],
            }
        if path == path_map["bl014_latest"]:
            return {
                "run_id": "BL014-TEST",
                "overall_status": "fail",
                "checks_total": 2,
                "checks_passed": 1,
                "checks_failed": 1,
                "advisories_total": 0,
                "checks": [
                    {"id": "check_a", "status": "pass", "details": "ok"},
                    {"id": "check_b", "status": "fail", "details": "bad"},
                ],
            }
        if path == path_map["bl009_log"]:
            return {
                "run_metadata": {
                    "run_id": "BL009-TEST",
                    "dataset_version": "d",
                    "pipeline_version": "p",
                    "signal_mode_name": "v1",
                },
                "validity_boundaries": {"summary": "bounded"},
            }
        return None

    monkeypatch.setattr(module, "_load_json_or_none", _fake_loader)
    payload = module._evidence_dashboard_payload()

    assert payload["bl013"]["run_id"] == "BL013-TEST"
    assert len(payload["bl014"]["failed_checks"]) == 1
    assert payload["bl014"]["failed_checks"][0]["id"] == "check_b"
    assert payload["bl009"]["validity_boundaries"]["summary"] == "bounded"


def test_explanation_view_payload_clamps_min_limit(monkeypatch) -> None:
    module = _load_module()

    def _fake_loader(_path):
        return {
            "run_id": "BL008-TEST",
            "generated_at_utc": "2026-04-13T00:00:00Z",
            "playlist_track_count": 3,
            "explanations": [
                {"playlist_position": 1, "track_id": "a", "narrative_driver": {"label": "Tag overlap"}},
                {"playlist_position": 2, "track_id": "b", "narrative_driver": {"label": "Genre overlap"}},
                {"playlist_position": 3, "track_id": "c", "narrative_driver": {"label": "Lead genre match"}},
            ],
        }

    monkeypatch.setattr(module, "_load_json_or_none", _fake_loader)
    status_code, payload = module._explanation_view_payload(limit=0)

    assert status_code == 200
    assert payload["returned_track_count"] == 1


def test_evidence_dashboard_payload_missing_artifacts(monkeypatch) -> None:
    module = _load_module()

    def _fake_loader(_path):
        return None

    monkeypatch.setattr(module, "_load_json_or_none", _fake_loader)
    payload = module._evidence_dashboard_payload()

    assert payload["bl013"]["available"] is False
    assert payload["bl014"]["available"] is False
    assert payload["bl009"]["available"] is False
    assert payload["bl014"]["failed_checks"] == []


def test_guide_payload_shape() -> None:
    module = _load_module()
    payload = module._guide_payload()

    assert isinstance(payload, dict)
    assert "summary" in payload
    assert "steps" in payload
    assert isinstance(payload["steps"], list)
    assert any(step.get("id") == "run_pipeline" for step in payload["steps"])


def test_guide_payload_missing_artifacts(monkeypatch) -> None:
    module = _load_module()

    def _fake_loader(_path):
        return None

    monkeypatch.setattr(module, "_load_json_or_none", _fake_loader)
    payload = module._guide_payload()

    assert payload["summary"]["next_step"] == "run_pipeline"
    assert len(payload["steps"]) == 4
    assert payload["steps"][0]["status"] == "pending"


def test_config_builder_schema_payload_shape() -> None:
    module = _load_module()
    payload = module._config_builder_schema_payload()

    assert isinstance(payload, dict)
    assert "settings" in payload
    assert isinstance(payload["settings"], list)
    assert any(item.get("path") == "control_mode.validation_profile" for item in payload["settings"])


def test_config_builder_profile_payload_unknown() -> None:
    module = _load_module()
    status_code, payload = module._config_builder_profile_payload("does_not_exist.json")

    assert status_code == 404
    assert "error" in payload


def test_config_builder_validate_accepts_default_payload() -> None:
    module = _load_module()
    ok, payload = module._validate_run_config_payload(module._load_default_run_config_payload())

    assert ok is True
    assert payload["ok"] is True
    assert payload["errors"] == []


def test_config_builder_validate_rejects_non_object_payload() -> None:
    module = _load_module()
    ok, payload = module._validate_run_config_payload(["not", "an", "object"])

    assert ok is False
    assert payload["ok"] is False
    assert "Config must be a JSON object" in payload["errors"]


def test_normalize_config_save_name_rejects_unsafe_names() -> None:
    module = _load_module()
    safe_name, error = module._normalize_config_save_name("bad name.json")

    assert safe_name is None
    assert error is not None


def test_save_config_builder_profile_writes_under_profiles(tmp_path, monkeypatch) -> None:
    module = _load_module()
    config_dir = tmp_path / "config" / "profiles"
    config_dir.mkdir(parents=True)
    monkeypatch.setattr(module, "IMPL_ROOT", tmp_path)
    monkeypatch.setattr(module, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(
        module,
        "_validate_run_config_payload",
        lambda _payload: (True, {"ok": True, "errors": [], "warnings": []}),
    )

    status_code, payload = module._save_config_builder_profile("custom_profile", {"schema_version": "run-config-v1"})

    assert status_code == 200
    assert payload["path"] == "config/profiles/custom_profile.json"
    assert (config_dir / "custom_profile.json").is_file()
