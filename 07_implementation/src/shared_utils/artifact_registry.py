"""
Canonical artifact and stage script registry for the active implementation.

This module centralizes path contracts that were previously duplicated across
stage runners, observability utilities, and the website API layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


_STAGE_SPECS: List[Dict[str, str]] = [
    {
        "stage_id": "bl003",
        "label": "BL-003 Alignment",
        "script": "alignment/main.py",
        "description": "Align imported Spotify interactions to DS-001 seed tracks.",
    },
    {
        "stage_id": "bl004",
        "label": "BL-004 Profile",
        "script": "profile/main.py",
        "description": "Build deterministic preference profile from aligned seed data.",
    },
    {
        "stage_id": "bl005",
        "label": "BL-005 Retrieval",
        "script": "retrieval/main.py",
        "description": "Filter candidate corpus against profile signals and keep rules.",
    },
    {
        "stage_id": "bl006",
        "label": "BL-006 Scoring",
        "script": "scoring/main.py",
        "description": "Score retained candidates with weighted components.",
    },
    {
        "stage_id": "bl007",
        "label": "BL-007 Playlist",
        "script": "playlist/main.py",
        "description": "Assemble final playlist with deterministic rule checks.",
    },
    {
        "stage_id": "bl008",
        "label": "BL-008 Transparency",
        "script": "transparency/main.py",
        "description": "Generate explanation payloads and summary transparency outputs.",
    },
    {
        "stage_id": "bl009",
        "label": "BL-009 Observability",
        "script": "observability/main.py",
        "description": "Record run-chain observability metadata and index outputs.",
    },
]


_ARTIFACT_SUMMARY_RELATIVE_PATHS: Dict[str, str] = {
    "bl003_seed_table": "alignment/outputs/bl003_ds001_spotify_seed_table.csv",
    "bl003_summary": "alignment/outputs/bl003_ds001_spotify_summary.json",
    "bl004_profile": "profile/outputs/bl004_preference_profile.json",
    "bl005_candidates": "retrieval/outputs/bl005_filtered_candidates.csv",
    "bl006_scores": "scoring/outputs/bl006_scored_candidates.csv",
    "bl007_playlist": "playlist/outputs/playlist.json",
    "bl008_explanations": "transparency/outputs/bl008_explanation_payloads.json",
    "bl008_explanation_summary": "transparency/outputs/bl008_explanation_summary.json",
    "bl009_observability": "observability/outputs/bl009_run_observability_log.json",
}


_BL013_STABLE_ARTIFACT_RELATIVE_PATHS: Dict[str, str] = {
    "bl004_seed_trace": "profile/outputs/bl004_seed_trace.csv",
    "bl005_filtered_candidates": "retrieval/outputs/bl005_filtered_candidates.csv",
    "bl005_candidate_decisions": "retrieval/outputs/bl005_candidate_decisions.csv",
    "bl006_scored_candidates": "scoring/outputs/bl006_scored_candidates.csv",
    "bl007_assembly_trace": "playlist/outputs/bl007_assembly_trace.csv",
}


_BL014_FRESHNESS_INPUT_RELATIVE_PATHS: Dict[str, str] = {
    "bl010_snapshot": "reproducibility/outputs/reproducibility_config_snapshot.json",
    "bl010_report": "reproducibility/outputs/reproducibility_report.json",
    "bl011_snapshot": "controllability/outputs/controllability_config_snapshot.json",
    "bl011_report": "controllability/outputs/controllability_report.json",
}


def stage_specs() -> List[Dict[str, str]]:
    """Return stage metadata in deterministic execution order."""
    return [dict(spec) for spec in _STAGE_SPECS]


def artifact_summary_targets(src_root: Path) -> Dict[str, Path]:
    """Build absolute artifact paths used by API status and compare views."""
    return {
        key: src_root / relative_path
        for key, relative_path in _ARTIFACT_SUMMARY_RELATIVE_PATHS.items()
    }


def bl013_stage_script_map() -> Dict[str, str]:
    """Build BL-013 stage-to-script mapping for BL-004..BL-009."""
    mapping: Dict[str, str] = {}
    for spec in _STAGE_SPECS:
        stage_label = spec["label"].split()[0]
        mapping[stage_label] = f"{spec['script']}"
    return mapping


def bl013_default_stage_order() -> List[str]:
    """Return BL-013 default stage execution order."""
    return list(bl013_stage_script_map().keys())


def bl013_bl003_script_relpath() -> str:
    """Relative script path used by BL-013 seed refresh execution."""
    return "alignment/main.py"


def bl013_bl003_summary_relpath() -> str:
    """Relative BL-003 summary path used for seed freshness checks."""
    return "alignment/outputs/bl003_ds001_spotify_summary.json"


def bl013_stable_artifact_relpaths() -> Dict[str, str]:
    """Return deterministic artifact paths used by BL-013 hash checks."""
    return dict(_BL013_STABLE_ARTIFACT_RELATIVE_PATHS)


def bl014_freshness_input_paths(repo_root: Path) -> Dict[str, Path]:
    """Return canonical BL-014 freshness evidence input paths."""
    return {
        key: repo_root / relative_path
        for key, relative_path in _BL014_FRESHNESS_INPUT_RELATIVE_PATHS.items()
    }


def bl014_bl013_latest_summary_path(repo_root: Path) -> Path:
    """Return BL-013 latest summary path consumed by BL-014 active checks."""
    return repo_root / "orchestration/outputs/bl013_orchestration_run_latest.json"


def bl014_pipeline_script_paths(repo_root: Path) -> Dict[str, Path]:
    """Return canonical stage runner script paths used by BL-014 refresh flow."""
    return {
        "bl010_script": repo_root / "reproducibility/main.py",
        "bl011_script": repo_root / "controllability/main.py",
        "bl013_script": repo_root / "orchestration/main.py",
    }


def bl014_refinement_diagnostic_paths(repo_root: Path) -> Dict[str, Path]:
    """Return BL-006/BL-007 refinement diagnostic paths used by BL-014 active checks."""
    return {
        "bl006_distribution": repo_root / "scoring/outputs/bl006_score_distribution_diagnostics.json",
        "bl007_assembly_report": repo_root / "playlist/outputs/bl007_assembly_report.json",
    }


def bl010_required_paths(repo_root: Path) -> Dict[str, Path]:
    """Return canonical BL-010 required script and artifact paths."""
    return {
        "bl003_script": repo_root / "alignment/main.py",
        "bl004_script": repo_root / "profile/main.py",
        "bl005_script": repo_root / "retrieval/main.py",
        "bl006_script": repo_root / "scoring/main.py",
        "bl007_script": repo_root / "playlist/main.py",
        "bl008_script": repo_root / "transparency/main.py",
        "bl009_script": repo_root / "observability/main.py",
        "bl003_summary": repo_root / "alignment/outputs/bl003_ds001_spotify_summary.json",
        "bl003_seed_table": repo_root / "alignment/outputs/bl003_ds001_spotify_seed_table.csv",
        "profile": repo_root / "profile/outputs/bl004_preference_profile.json",
        "bl004_profile": repo_root / "profile/outputs/bl004_preference_profile.json",
        "bl004_summary": repo_root / "profile/outputs/profile_summary.json",
        "bl004_seed_trace": repo_root / "profile/outputs/bl004_seed_trace.csv",
        "bl005_filtered": repo_root / "retrieval/outputs/bl005_filtered_candidates.csv",
        "bl005_decisions": repo_root / "retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_diagnostics": repo_root / "retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl006_scored": repo_root / "scoring/outputs/bl006_scored_candidates.csv",
        "bl006_summary": repo_root / "scoring/outputs/bl006_score_summary.json",
        "playlist": repo_root / "playlist/outputs/playlist.json",
        "bl007_playlist": repo_root / "playlist/outputs/playlist.json",
        "bl007_trace": repo_root / "playlist/outputs/bl007_assembly_trace.csv",
        "bl007_report": repo_root / "playlist/outputs/bl007_assembly_report.json",
        "bl008_payloads": repo_root / "transparency/outputs/bl008_explanation_payloads.json",
        "bl008_summary": repo_root / "transparency/outputs/bl008_explanation_summary.json",
        "bl009_log": repo_root / "observability/outputs/bl009_run_observability_log.json",
        "bl009_index": repo_root / "observability/outputs/bl009_run_index.csv",
    }


def bl009_required_paths(repo_root: Path, bl009_script_path: Path | None = None) -> Dict[str, Path]:
    """Return canonical BL-009 required script and artifact paths."""
    script_path = bl009_script_path or (
        repo_root / "observability/main.py"
    )
    return {
        "bl003_summary": repo_root / "alignment/outputs/bl003_ds001_spotify_summary.json",
        "bl004_profile": repo_root / "profile/outputs/bl004_preference_profile.json",
        "bl004_summary": repo_root / "profile/outputs/profile_summary.json",
        "bl004_seed_trace": repo_root / "profile/outputs/bl004_seed_trace.csv",
        "bl005_diagnostics": repo_root / "retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl005_decisions": repo_root / "retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_filtered": repo_root / "retrieval/outputs/bl005_filtered_candidates.csv",
        "bl006_summary": repo_root / "scoring/outputs/bl006_score_summary.json",
        "bl006_scored": repo_root / "scoring/outputs/bl006_scored_candidates.csv",
        "bl007_report": repo_root / "playlist/outputs/bl007_assembly_report.json",
        "bl007_trace": repo_root / "playlist/outputs/bl007_assembly_trace.csv",
        "bl007_playlist": repo_root / "playlist/outputs/playlist.json",
        "bl008_summary": repo_root / "transparency/outputs/bl008_explanation_summary.json",
        "bl008_payloads": repo_root / "transparency/outputs/bl008_explanation_payloads.json",
        "bl004_script": repo_root / "profile/main.py",
        "bl005_script": repo_root / "retrieval/main.py",
        "bl006_script": repo_root / "scoring/main.py",
        "bl007_script": repo_root / "playlist/main.py",
        "bl008_script": repo_root / "transparency/main.py",
        "bl009_script": script_path,
    }
