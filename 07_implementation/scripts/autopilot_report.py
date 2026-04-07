from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        return data
    return {}


def _stage_status_counts(stage_results: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in stage_results:
        status = str(item.get("status", "unknown")).lower().strip() or "unknown"
        counts[status] = counts.get(status, 0) + 1
    return counts


def _render_markdown(
    *,
    generated_at_utc: str,
    mode: str,
    bl013: dict[str, Any],
    bl014: dict[str, Any],
    bl013_path: Path,
    bl014_path: Path,
) -> str:
    bl013_run_id = str(bl013.get("run_id", "missing"))
    bl013_status = str(bl013.get("overall_status", "missing")).lower()
    bl014_run_id = str(bl014.get("run_id", "missing"))
    bl014_status = str(bl014.get("overall_status", "missing")).lower()

    stage_results = bl013.get("stage_results", [])
    if not isinstance(stage_results, list):
        stage_results = []
    stage_counts = _stage_status_counts([x for x in stage_results if isinstance(x, dict)])

    checks = bl014.get("checks", [])
    if not isinstance(checks, list):
        checks = []
    failed_checks = [
        item
        for item in checks
        if isinstance(item, dict) and str(item.get("status", "")).lower() == "fail"
    ]

    lines: list[str] = []
    lines.append("# Autopilot Session Report")
    lines.append("")
    lines.append(f"- generated_at_utc: {generated_at_utc}")
    lines.append(f"- mode: {mode}")
    lines.append(f"- bl013_run_id: {bl013_run_id}")
    lines.append(f"- bl013_status: {bl013_status}")
    lines.append(f"- bl014_run_id: {bl014_run_id}")
    lines.append(f"- bl014_status: {bl014_status}")
    lines.append(f"- bl013_report_source: {bl013_path}")
    lines.append(f"- bl014_report_source: {bl014_path}")
    lines.append("")

    lines.append("## Stage Summary")
    if not stage_counts:
        lines.append("- stage_results: missing")
    else:
        for key in sorted(stage_counts.keys()):
            lines.append(f"- {key}: {stage_counts[key]}")
    lines.append("")

    lines.append("## BL-014 Gate Summary")
    lines.append(f"- checks_total: {bl014.get('checks_total', 'missing')}")
    lines.append(f"- checks_passed: {bl014.get('checks_passed', 'missing')}")
    lines.append(f"- checks_failed: {bl014.get('checks_failed', 'missing')}")
    lines.append("")

    lines.append("## Failed Checks")
    if not failed_checks:
        lines.append("- none")
    else:
        for item in failed_checks:
            check_id = str(item.get("id", "unknown"))
            details = str(item.get("details", ""))
            lines.append(f"- {check_id}: {details}")
    lines.append("")

    lines.append("## Operator Next Action")
    if bl014_status == "pass":
        lines.append("- Quality gate passed. Continue with logging and sign-off updates.")
    else:
        lines.append("- Quality gate failed. Resolve failed checks before sign-off.")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate autopilot session markdown report.")
    parser.add_argument("--impl-root", default=None, help="Absolute path to 07_implementation")
    parser.add_argument("--mode", default="unknown", help="Autopilot mode used for this session")
    parser.add_argument("--bl013-report", default=None, help="Override BL-013 report path")
    parser.add_argument("--bl014-report", default=None, help="Override BL-014 report path")
    parser.add_argument("--output", default=None, help="Output markdown path")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    default_impl_root = script_dir.parent
    impl_root = Path(args.impl_root).resolve() if args.impl_root else default_impl_root
    workspace_root = impl_root.parent

    bl013_path = (
        Path(args.bl013_report).resolve()
        if args.bl013_report
        else impl_root / "src" / "orchestration" / "outputs" / "bl013_orchestration_run_latest.json"
    )
    bl014_path = (
        Path(args.bl014_report).resolve()
        if args.bl014_report
        else impl_root / "src" / "quality" / "outputs" / "bl014_sanity_report.json"
    )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    output_path = (
        Path(args.output).resolve()
        if args.output
        else workspace_root / "00_admin" / f"autopilot_session_{timestamp}.md"
    )

    bl013 = _load_json(bl013_path)
    bl014 = _load_json(bl014_path)
    markdown = _render_markdown(
        generated_at_utc=generated_at,
        mode=str(args.mode),
        bl013=bl013,
        bl014=bl014,
        bl013_path=bl013_path,
        bl014_path=bl014_path,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"autopilot_report_path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
