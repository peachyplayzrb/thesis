#!/usr/bin/env python3
"""REB-M3 tranche-1 gate checks for O1 to O3 evidence surfaces.

This script validates that the current BL-003 to BL-006 outputs contain the
minimum objective-linked evidence fields required for REB-M3 tranche-1 start:
- O1 uncertainty-aware profiling evidence (BL-004)
- O2 confidence-aware alignment and exclusion evidence (BL-003, BL-005)
- O3 deterministic scoring trade-off control evidence (BL-006)

Outputs are written to:
- quality/outputs/reb_m3_tranche1_gate_report.json
- quality/outputs/reb_m3_tranche1_gate_matrix.csv
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from reb_gate_common import ensure_exists, finalize_gate_report, load_json, nested_get

from shared_utils.path_utils import impl_root

REPO_ROOT = impl_root()
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def main() -> int:
    started = datetime.now(UTC)
    run_id = f"REB-M3-TRANCHE1-GATE-{started.strftime('%Y%m%d-%H%M%S-%f')}"

    artifacts = {
        "bl003_summary": REPO_ROOT / "alignment/outputs/bl003_ds001_spotify_summary.json",
        "bl004_profile": REPO_ROOT / "profile/outputs/bl004_preference_profile.json",
        "bl005_diag": REPO_ROOT / "retrieval/outputs/bl005_candidate_diagnostics.json",
        "bl006_summary": REPO_ROOT / "scoring/outputs/bl006_score_summary.json",
    }
    for artifact_path in artifacts.values():
        ensure_exists(artifact_path)

    bl003_summary = load_json(artifacts["bl003_summary"])
    bl004_profile = load_json(artifacts["bl004_profile"])
    bl005_diag = load_json(artifacts["bl005_diag"])
    bl006_summary = load_json(artifacts["bl006_summary"])

    checks: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, details: str) -> None:
        checks.append(
            {
                "id": check_id,
                "status": "pass" if passed else "fail",
                "details": details,
            }
        )

    # O1: uncertainty-aware preference profiling evidence (BL-004)
    o1_required_top = {
        "numeric_confidence",
        "source_coverage",
        "interaction_attribution",
        "profile_signal_vector",
        "diagnostics",
    }
    check(
        "o1_profile_top_level_blocks",
        o1_required_top.issubset(set(bl004_profile.keys())),
        "BL-004 profile includes uncertainty and attribution evidence blocks",
    )
    check(
        "o1_profile_policy_effective",
        isinstance(nested_get(bl004_profile, ["diagnostics", "profile_policy_effective"]), dict),
        "BL-004 diagnostics include effective profile-policy block",
    )

    # O2: alignment confidence + exclusion logic evidence (BL-003, BL-005)
    check(
        "o2_bl003_seed_contract_present",
        isinstance(nested_get(bl003_summary, ["inputs", "seed_contract"]), dict),
        "BL-003 summary includes seed contract block for confidence/selection provenance",
    )
    check(
        "o2_bl003_match_counts_present",
        all(
            isinstance(nested_get(bl003_summary, ["counts", key]), int)
            for key in ("matched_by_spotify_id", "matched_by_metadata", "unmatched")
        ),
        "BL-003 summary includes match/unmatched counts for alignment risk visibility",
    )
    check(
        "o2_bl005_exclusion_paths_present",
        isinstance(bl005_diag.get("decision_path_counts"), dict) and len(bl005_diag.get("decision_path_counts", {})) > 0,
        "BL-005 diagnostics include decision-path exclusion counts",
    )
    check(
        "o2_bl005_rejection_counts_present",
        all(
            isinstance(nested_get(bl005_diag, ["counts", key]), int)
            for key in ("rejected_non_seed_candidates", "kept_candidates")
        ),
        "BL-005 diagnostics include kept/rejected candidate counts",
    )

    # O3: deterministic scoring trade-off controls (BL-006)
    check(
        "o3_bl006_active_weights_present",
        isinstance(nested_get(bl006_summary, ["config", "active_component_weights"]), dict)
        and len(nested_get(bl006_summary, ["config", "active_component_weights"]) or {}) > 0,
        "BL-006 summary exposes active scoring component weights",
    )
    check(
        "o3_bl006_strategy_controls_present",
        isinstance(nested_get(bl006_summary, ["config", "lead_genre_strategy"]), str)
        and isinstance(nested_get(bl006_summary, ["config", "semantic_overlap_strategy"]), str),
        "BL-006 summary exposes semantic strategy controls",
    )
    check(
        "o3_bl006_score_stats_present",
        isinstance(bl006_summary.get("score_statistics"), dict)
        and {"max_score", "min_score", "mean_score", "median_score"}.issubset(
            set((bl006_summary.get("score_statistics") or {}).keys())
        ),
        "BL-006 summary includes score distribution statistics",
    )

    return finalize_gate_report(
        run_id=run_id,
        task="REB-M3 tranche-1 O1-O3 gate",
        started=started,
        checks=checks,
        artifacts=artifacts,
        output_dir=OUTPUT_DIR,
        report_filename="reb_m3_tranche1_gate_report.json",
        matrix_filename="reb_m3_tranche1_gate_matrix.csv",
    )


if __name__ == "__main__":
    raise SystemExit(main())
