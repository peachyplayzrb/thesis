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
        "script": "bl003_alignment/build_bl003_ds001_spotify_seed_table.py",
        "description": "Align imported Spotify interactions to DS-001 seed tracks.",
    },
    {
        "stage_id": "bl004",
        "label": "BL-004 Profile",
        "script": "bl004_profile/build_bl004_preference_profile.py",
        "description": "Build deterministic preference profile from aligned seed data.",
    },
    {
        "stage_id": "bl005",
        "label": "BL-005 Retrieval",
        "script": "bl005_retrieval/build_bl005_candidate_filter.py",
        "description": "Filter candidate corpus against profile signals and keep rules.",
    },
    {
        "stage_id": "bl006",
        "label": "BL-006 Scoring",
        "script": "bl006_scoring/build_bl006_scored_candidates.py",
        "description": "Score retained candidates with weighted components.",
    },
    {
        "stage_id": "bl007",
        "label": "BL-007 Playlist",
        "script": "bl007_playlist/build_bl007_playlist.py",
        "description": "Assemble final playlist with deterministic rule checks.",
    },
    {
        "stage_id": "bl008",
        "label": "BL-008 Transparency",
        "script": "bl008_transparency/build_bl008_explanation_payloads.py",
        "description": "Generate explanation payloads and summary transparency outputs.",
    },
    {
        "stage_id": "bl009",
        "label": "BL-009 Observability",
        "script": "bl009_observability/build_bl009_observability_log.py",
        "description": "Record run-chain observability metadata and index outputs.",
    },
]


_ARTIFACT_SUMMARY_RELATIVE_PATHS: Dict[str, str] = {
    "bl003_seed_table": "bl003_alignment/outputs/bl003_ds001_spotify_seed_table.csv",
    "bl003_summary": "bl003_alignment/outputs/bl003_ds001_spotify_summary.json",
    "bl004_profile": "bl004_profile/outputs/bl004_preference_profile.json",
    "bl005_candidates": "bl005_retrieval/outputs/bl005_filtered_candidates.csv",
    "bl006_scores": "bl006_scoring/outputs/bl006_scored_candidates.csv",
    "bl007_playlist": "bl007_playlist/outputs/bl007_playlist.json",
    "bl008_explanations": "bl008_transparency/outputs/bl008_explanation_payloads.json",
    "bl008_explanation_summary": "bl008_transparency/outputs/bl008_explanation_summary.json",
    "bl009_observability": "bl009_observability/outputs/bl009_run_observability_log.json",
}


_BL013_STABLE_ARTIFACT_RELATIVE_PATHS: Dict[str, str] = {
    "bl004_seed_trace": "07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv",
    "bl005_filtered_candidates": "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv",
    "bl005_candidate_decisions": "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_decisions.csv",
    "bl006_scored_candidates": "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv",
    "bl007_assembly_trace": "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv",
}


_BL014_FRESHNESS_INPUT_RELATIVE_PATHS: Dict[str, str] = {
    "bl010_snapshot": "07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json",
    "bl010_report": "07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json",
    "bl011_snapshot": "07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_config_snapshot.json",
    "bl011_report": "07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_report.json",
}


def stage_specs() -> List[Dict[str, str]]:
    """Return stage metadata in deterministic execution order."""
    return [dict(spec) for spec in _STAGE_SPECS]


def artifact_summary_targets(implementation_notes_root: Path) -> Dict[str, Path]:
    """Build absolute artifact paths used by API status and compare views."""
    return {
        key: implementation_notes_root / relative_path
        for key, relative_path in _ARTIFACT_SUMMARY_RELATIVE_PATHS.items()
    }


def bl013_stage_script_map() -> Dict[str, str]:
    """Build BL-013 stage-to-script mapping for BL-004..BL-009."""
    mapping: Dict[str, str] = {}
    for spec in _STAGE_SPECS:
        stage_label = spec["label"].split()[0]
        mapping[stage_label] = f"07_implementation/implementation_notes/{spec['script']}"
    return mapping


def bl013_default_stage_order() -> List[str]:
    """Return BL-013 default stage execution order."""
    return list(bl013_stage_script_map().keys())


def bl013_bl003_script_relpath() -> str:
    """Relative script path used by BL-013 seed refresh execution."""
    return "07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py"


def bl013_bl003_summary_relpath() -> str:
    """Relative BL-003 summary path used for seed freshness checks."""
    return "07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json"


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
    return repo_root / "07_implementation/implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_latest.json"


def bl014_pipeline_script_paths(repo_root: Path) -> Dict[str, Path]:
    """Return canonical stage runner script paths used by BL-014 refresh flow."""
    return {
        "bl010_script": repo_root / "07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py",
        "bl011_script": repo_root / "07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py",
        "bl013_script": repo_root / "07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py",
    }


def bl014_refinement_diagnostic_paths(repo_root: Path) -> Dict[str, Path]:
    """Return BL-006/BL-007 refinement diagnostic paths used by BL-014 active checks."""
    return {
        "bl006_distribution": repo_root / "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_distribution_diagnostics.json",
        "bl007_assembly_report": repo_root / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json",
    }


def bl010_required_paths(repo_root: Path) -> Dict[str, Path]:
    """Return canonical BL-010 required script and artifact paths."""
    return {
        "bl004_script": repo_root / "07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py",
        "bl005_script": repo_root / "07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py",
        "bl006_script": repo_root / "07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py",
        "bl007_script": repo_root / "07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py",
        "bl008_script": repo_root / "07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py",
        "bl009_script": repo_root / "07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py",
        "bl004_profile": repo_root / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json",
        "bl004_summary": repo_root / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json",
        "bl004_seed_trace": repo_root / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv",
        "bl005_filtered": repo_root / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv",
        "bl005_decisions": repo_root / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_diagnostics": repo_root / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl006_scored": repo_root / "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv",
        "bl006_summary": repo_root / "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json",
        "bl007_playlist": repo_root / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json",
        "bl007_trace": repo_root / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv",
        "bl007_report": repo_root / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json",
        "bl008_payloads": repo_root / "07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_payloads.json",
        "bl008_summary": repo_root / "07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json",
        "bl009_log": repo_root / "07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json",
        "bl009_index": repo_root / "07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_index.csv",
    }


def bl009_required_paths(repo_root: Path, bl009_script_path: Path | None = None) -> Dict[str, Path]:
    """Return canonical BL-009 required script and artifact paths."""
    script_path = bl009_script_path or (
        repo_root / "07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py"
    )
    return {
        "bl004_profile": repo_root / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_preference_profile.json",
        "bl004_summary": repo_root / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json",
        "bl004_seed_trace": repo_root / "07_implementation/implementation_notes/bl004_profile/outputs/bl004_seed_trace.csv",
        "bl005_diagnostics": repo_root / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl005_decisions": repo_root / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_decisions.csv",
        "bl005_filtered": repo_root / "07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_filtered_candidates.csv",
        "bl006_summary": repo_root / "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json",
        "bl006_scored": repo_root / "07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv",
        "bl007_report": repo_root / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json",
        "bl007_trace": repo_root / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_trace.csv",
        "bl007_playlist": repo_root / "07_implementation/implementation_notes/bl007_playlist/outputs/bl007_playlist.json",
        "bl008_summary": repo_root / "07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json",
        "bl008_payloads": repo_root / "07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_payloads.json",
        "bl004_script": repo_root / "07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py",
        "bl005_script": repo_root / "07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py",
        "bl006_script": repo_root / "07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py",
        "bl007_script": repo_root / "07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py",
        "bl008_script": repo_root / "07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py",
        "bl009_script": script_path,
    }
