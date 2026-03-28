from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run baseline vs experiment profile and emit one A/B comparison JSON artifact."
    )
    parser.add_argument("--baseline-profile", required=True, help="Path to baseline run-config JSON")
    parser.add_argument("--experiment-profile", required=True, help="Path to experiment run-config JSON")
    parser.add_argument(
        "--stages",
        nargs="+",
        default=["BL-004", "BL-005", "BL-006", "BL-007", "BL-008", "BL-009"],
        help="Ordered BL-013 stages to execute for each profile",
    )
    parser.add_argument(
        "--python-exe",
        default=".venv/Scripts/python.exe",
        help="Python executable path relative to repo root or absolute path",
    )
    parser.add_argument(
        "--output",
        default="_scratch/ab_profile_comparison_latest.json",
        help="Output JSON path for A/B summary",
    )
    parser.add_argument(
        "--no-refresh-seed",
        action="store_true",
        help="Skip --refresh-seed when invoking BL-013",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_profile(repo_root: Path, python_exe: Path, profile_path: Path, stages: list[str], refresh_seed: bool) -> dict[str, Any]:
    entrypoint = repo_root / "07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py"
    cmd = [str(python_exe), str(entrypoint), "--run-config", str(profile_path), "--stages", *stages]
    if refresh_seed:
        cmd.insert(2, "--refresh-seed")

    run = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )

    summary_path = repo_root / "07_implementation/implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_latest.json"
    bl005_diag_path = repo_root / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json"
    bl006_summary_path = repo_root / "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json"
    bl007_report_path = repo_root / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json"
    bl008_summary_path = repo_root / "07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json"

    if run.returncode != 0:
        return {
            "status": "fail",
            "return_code": run.returncode,
            "stdout_tail": run.stdout.splitlines()[-20:],
            "stderr_tail": run.stderr.splitlines()[-20:],
        }

    summary = read_json(summary_path)
    bl005_diag = read_json(bl005_diag_path)
    bl006_summary = read_json(bl006_summary_path)
    bl007_report = read_json(bl007_report_path)
    bl008_summary = read_json(bl008_summary_path)

    return {
        "status": "pass",
        "return_code": run.returncode,
        "bl013_run_id": summary.get("run_id"),
        "run_config_path": summary.get("run_config_path"),
        "bl005": {
            "run_id": bl005_diag.get("run_id"),
            "kept_candidates": bl005_diag.get("counts", {}).get("kept_candidates"),
            "rejected_non_seed": bl005_diag.get("counts", {}).get("rejected_non_seed_candidates"),
            "rejected_by_language_filter": bl005_diag.get("counts", {}).get("rejected_by_language_filter", 0),
            "rejected_by_recency_gate": bl005_diag.get("counts", {}).get("rejected_by_recency_gate", 0),
            "decision_path_counts": bl005_diag.get("decision_path_counts", {}),
        },
        "bl006": {
            "run_id": bl006_summary.get("run_id"),
            "score_statistics": bl006_summary.get("score_statistics", {}),
        },
        "bl007": {
            "run_id": bl007_report.get("run_id"),
            "playlist_genre_mix": bl007_report.get("playlist_genre_mix", {}),
            "playlist_score_range": bl007_report.get("playlist_score_range", {}),
            "tracks_included": bl007_report.get("counts", {}).get("tracks_included"),
        },
        "bl008": {
            "run_id": bl008_summary.get("run_id"),
            "top_contributor_distribution": bl008_summary.get("top_contributor_distribution", {}),
        },
    }


def compute_delta(baseline: dict[str, Any], experiment: dict[str, Any]) -> dict[str, Any]:
    if baseline.get("status") != "pass" or experiment.get("status") != "pass":
        return {"available": False, "reason": "One or both profile runs failed"}

    b_bl005 = baseline["bl005"]
    e_bl005 = experiment["bl005"]
    b_mean = baseline["bl006"]["score_statistics"].get("mean_score")
    e_mean = experiment["bl006"]["score_statistics"].get("mean_score")

    return {
        "available": True,
        "kept_candidates_delta": (e_bl005.get("kept_candidates") or 0) - (b_bl005.get("kept_candidates") or 0),
        "rejected_by_language_filter_delta": (e_bl005.get("rejected_by_language_filter") or 0)
        - (b_bl005.get("rejected_by_language_filter") or 0),
        "rejected_by_recency_gate_delta": (e_bl005.get("rejected_by_recency_gate") or 0)
        - (b_bl005.get("rejected_by_recency_gate") or 0),
        "mean_score_delta": (e_mean or 0.0) - (b_mean or 0.0),
        "playlist_genre_mix_baseline": baseline["bl007"].get("playlist_genre_mix", {}),
        "playlist_genre_mix_experiment": experiment["bl007"].get("playlist_genre_mix", {}),
    }


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]

    python_exe = Path(args.python_exe)
    if not python_exe.is_absolute():
        python_exe = (repo_root / python_exe).resolve()

    baseline_profile = Path(args.baseline_profile)
    experiment_profile = Path(args.experiment_profile)
    if not baseline_profile.is_absolute():
        baseline_profile = (repo_root / baseline_profile).resolve()
    if not experiment_profile.is_absolute():
        experiment_profile = (repo_root / experiment_profile).resolve()

    refresh_seed = not args.no_refresh_seed

    baseline_result = run_profile(
        repo_root=repo_root,
        python_exe=python_exe,
        profile_path=baseline_profile,
        stages=args.stages,
        refresh_seed=refresh_seed,
    )
    experiment_result = run_profile(
        repo_root=repo_root,
        python_exe=python_exe,
        profile_path=experiment_profile,
        stages=args.stages,
        refresh_seed=refresh_seed,
    )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(repo_root),
        "inputs": {
            "baseline_profile": str(baseline_profile),
            "experiment_profile": str(experiment_profile),
            "stages": args.stages,
            "refresh_seed": refresh_seed,
        },
        "baseline": baseline_result,
        "experiment": experiment_result,
        "delta": compute_delta(baseline_result, experiment_result),
    }

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"A/B profile comparison written: {output_path}")
    print(f"baseline_status={baseline_result.get('status')} experiment_status={experiment_result.get('status')}")


if __name__ == "__main__":
    main()
