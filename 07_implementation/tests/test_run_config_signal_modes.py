from __future__ import annotations

import json
from pathlib import Path

from run_config.run_config_utils import resolve_bl005_controls, resolve_bl006_controls, resolve_effective_run_config


def test_default_effective_run_config_is_v1f_compat() -> None:
    effective, resolved_path = resolve_effective_run_config(None)

    assert resolved_path is None
    assert effective["signal_mode"]["name"] == "v1f-compat"
    assert effective["signal_mode"]["semantic_profile"] == "binary_overlap"
    assert effective["signal_mode"]["numeric_profile"] == "pass_count_support"


def test_v1g_preset_resolves_to_enhanced_mode() -> None:
    config_path = Path(__file__).resolve().parents[1] / "src" / "run_config" / "configs" / "run_config_signal_v1g_enhanced.json"

    effective, resolved_path = resolve_effective_run_config(config_path)
    bl005_controls = resolve_bl005_controls(config_path)
    bl006_controls = resolve_bl006_controls(config_path)

    assert resolved_path == config_path.resolve()
    assert effective["signal_mode"]["name"] == "v1g-enhanced"
    assert bl005_controls["signal_mode"]["name"] == "v1g-enhanced"
    assert bl006_controls["signal_mode"]["name"] == "v1g-enhanced"
    assert effective["signal_mode"]["popularity_profile"]["scoring_enabled"] is True


def test_partial_feature_mix_resolves_to_custom_mode(tmp_path: Path) -> None:
    config_path = tmp_path / "custom_signal_config.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": "run-config-v1",
                "retrieval_controls": {
                    "use_weighted_semantics": True,
                    "use_continuous_numeric": False,
                    "enable_popularity_numeric": False,
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    effective, _ = resolve_effective_run_config(config_path)

    assert effective["signal_mode"]["name"] == "custom"
