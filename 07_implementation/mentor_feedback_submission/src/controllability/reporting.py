"""Report/text helpers for BL-011 scenario outputs."""
from __future__ import annotations

import json
from pathlib import Path

from shared_utils.report_utils import render_csv_text, write_text


def _mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def json_text(payload: object) -> str:
    """Serialize a JSON payload with stable indentation and ASCII output."""
    return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"


def csv_text(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    """Render rows to CSV text using shared formatting behavior."""
    return render_csv_text(fieldnames, rows)


def merge_stage_maps(*maps: dict[str, str]) -> dict[str, str]:
    """Merge stage output maps into one mapping for scenario archival."""
    merged: dict[str, str] = {}
    for item in maps:
        merged.update(item)
    return merged


def write_scenario_outputs(output_dir: Path, scenario_result: dict[str, object]) -> None:
    """Write scenario text artifacts and effective config into its archive folder."""
    scenario_dir = output_dir / "scenarios" / str(scenario_result["scenario_id"])
    scenario_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in _mapping(scenario_result.get("texts")).items():
        write_text(scenario_dir / filename, str(text))
    config_path = scenario_dir / "scenario_effective_config.json"
    write_text(config_path, json_text(scenario_result["effective_config"]))
