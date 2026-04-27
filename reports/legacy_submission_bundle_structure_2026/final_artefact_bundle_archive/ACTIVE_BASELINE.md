# Active Baseline Authority

> Status note (2026-04-09): This file is retained for historical/reference use under `_scratch` and is **not** the active runtime/workflow authority.
> Active runtime surface is `07_implementation/` (entrypoint: `07_implementation/main.py`).

Last updated: 2026-03-27 20:36 UTC

## Purpose
This document is the single source of truth for active implementation execution posture and baseline evidence references.

If this file conflicts with run-status summaries elsewhere, this file takes precedence.

## Baseline Status
- Canonical reporting baseline: run_config_ui013_tuning_v1f.json
- Experimental baseline: run_config_ui013_tuning_v2a_retrieval_tight.json
- Active execution corpus: DS-001
- DS-002 posture: validated fallback reference, not active execution path

## Canonical v1f Evidence Chain
- BL-013 orchestration: BL013-ENTRYPOINT-20260327-201712-508978
- BL-010 reproducibility: BL010-REPRO-20260327-201949
- BL-011 controllability: BL011-CTRL-20260327-202057
- BL-014 sanity: BL014-SANITY-20260327-201731-408637 (22/22)
- BL freshness suite: BL-FRESHNESS-SUITE-20260327-201942 (19/19)

## Post-Refactor Validation Wave (BL-006 Decomposition)
- BL-013 orchestration: BL013-ENTRYPOINT-20260327-203411-538709
- BL-014 sanity: BL014-SANITY-20260327-203424-640876 (22/22)
- BL-010 reproducibility: BL010-REPRO-20260327-203439 (deterministic_match=True)
- BL-011 controllability: BL011-CTRL-20260327-203517 (pass)

## Experimental v2a Evidence Chain (Non-Canonical)
- BL-013 orchestration: BL013-ENTRYPOINT-20260327-002121-545346
- BL-010 reproducibility: BL010-REPRO-20260327-001916
- BL-011 controllability: BL011-CTRL-20260327-002019
- BL-014 sanity: BL014-SANITY-20260327-002035-164549 (22/22)
- BL freshness suite: BL-FRESHNESS-SUITE-20260327-002136 (19/19)

## Additional Same-Day Website/Server Wave (Non-Canonical)
- BL-009 observability: BL009-OBSERVE-20260327-165412-004409
- Upstream chain: BL004-PROFILE-20260327-165357-389471 -> BL005-FILTER-20260327-165358-293711 -> BL006-SCORE-20260327-165402-861535 -> BL007-ASSEMBLE-20260327-165409-663614 -> BL008-EXPLAIN-20260327-165410-986323
- Observed metrics: kept_candidates=70680, BL-008 top contributors: Lead genre match=4, Tag overlap=3, Danceability=2, Tempo=1

## Invariants
- Stable artifact names and stage output contracts remain unchanged unless versioned explicitly.
- Determinism checks must pass for unchanged code+inputs+config.
- Canonical reporting should cite run-specific artifacts first and latest pointers second.

## Referencing Rules
- Backlog, implementation status sheets, and admin status pages should link here for baseline evidence chains.
- Do not duplicate the full run table in multiple docs unless required for submission snapshots.

## Related Documents
- Backlog control board: 07_implementation/backlog.md
- Current implementation sheet: 07_implementation/implementation_notes/CODEBASE_ISSUES_CURRENT.md
- Submission scope and retained outputs: 07_implementation/implementation_notes/SUBMISSION_MANIFEST.md
- BL-013 run manifest and output retention details: 07_implementation/implementation_notes/bl013_entrypoint/outputs/BL013_RUN_MANIFEST.md
