from __future__ import annotations

import json
from pathlib import Path

from shared_utils.report_utils import render_csv_text, write_text


def json_text(payload: object) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"


def csv_text(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    return render_csv_text(fieldnames, rows)


def merge_stage_maps(*maps: dict[str, str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for item in maps:
        merged.update(item)
    return merged


def write_scenario_outputs(output_dir: Path, scenario_result: dict[str, object]) -> None:
    scenario_dir = output_dir / "scenarios" / str(scenario_result["scenario_id"])
    scenario_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in scenario_result["texts"].items():
        write_text(scenario_dir / filename, text)
    config_path = scenario_dir / "scenario_effective_config.json"
    write_text(config_path, json_text(scenario_result["effective_config"]))
