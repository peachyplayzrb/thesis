# High-Risk Regression Checklist (2026-03-25)

Purpose: verify that profile-switch hardening did not break other artifact surfaces.

Scope anchor:
- Active code deltas: ingestion cache scoping + BL-004 user_id inference
- Active run context: temporary threshold run config (0.15)
- Prior A/B harness work: reverted (should not be active)

## 1) Code Risk Surface

### 1.1 Profile-scoped cache keys
Files:
- 07_implementation/implementation_notes/ingestion/spotify_client.py
- 07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py

Risk:
- Cross-profile cache reuse can leak stale /me and endpoint pages between accounts.

Check:
1. Run BL-002 ingestion on profile A, then profile B, then profile A again.
2. Confirm logs and summaries reflect each account correctly.
3. Confirm cache keys include profile namespace uid:<spotify_user_id> (or refresh-token fallback).

Pass criteria:
- profile user_id changes when profile changes.
- no stale carry-over in exported top/saved/playlist counts between profiles beyond normal API drift.

Fail indicators:
- same cached payload reused across different spotify_user_id values.
- profile B run writes profile A user metadata.

### 1.2 BL-004 user_id metadata inference
File:
- 07_implementation/implementation_notes/profile/build_bl004_preference_profile.py

Risk:
- output metadata can silently report legacy/wrong user_id if config and env are unset.

Check:
1. Clear BL004_USER_ID env variable.
2. Run BL-004 from latest ingestion artifacts.
3. Confirm BL-004 summary user_id matches ingestion profile id.

Pass criteria:
- user_id in BL-004 outputs equals ingestion outputs spotify_user_id.

Fail indicators:
- user_id appears as unrelated static id.
- user_id resolves to unknown_user when spotify_profile.json exists and is valid.

## 2) Configuration Risk Surface

### 2.1 Temporary threshold drift
Files:
- 07_implementation/implementation_notes/run_config/outputs/run_config_profile_test_threshold_015.json
- 07_implementation/implementation_notes/run_config/run_config_template_v1.json

Risk:
- forgetting temporary 0.15 threshold can create invalid comparability vs canonical 0.30 baseline.

Check:
1. Confirm which config path is used in BL-013 latest summary.
2. Confirm match_rate_min_threshold in effective config and BL-003 summary.

Pass criteria:
- run artifacts clearly show the exact active threshold and config path.

Fail indicators:
- reports interpreted as canonical while actually using temporary config.

### 2.2 Missing selected source behavior
File:
- 07_implementation/implementation_notes/alignment/outputs/bl003_ds001_spotify_summary.json

Risk:
- recently_played source can be absent; strict mode may fail unexpectedly.

Check:
1. Inspect selected_sources_expected/available.
2. Inspect allow_missing_selected_sources and missing_selected_sources.

Pass criteria:
- behavior is explicit and consistent with intended mode (strict or allow-missing).

Fail indicators:
- hidden source drop without manifest/summary evidence.

## 3) Pipeline Integrity Surface

### 3.1 Stage coverage and run continuity
File:
- 07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_latest.json

Risk:
- partial stage execution can look like full pass.

Check:
1. Confirm requested stage order includes BL-004..BL-009.
2. Confirm executed_stage_count = 6 and failed_stage_count = 0.
3. Confirm each stage references same run config path.

Pass criteria:
- complete stage set executed and all pass.

Fail indicators:
- missing stage entry, mixed config paths, or nonzero failed stages.

### 3.2 Quality gate continuity
Files:
- 07_implementation/implementation_notes/quality/outputs/bl014_sanity_report.json
- 07_implementation/implementation_notes/quality/outputs/bl_active_freshness_suite_report.json
- 07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json
- 07_implementation/implementation_notes/controllability/outputs/bl011_controllability_report.json

Risk:
- ingestion/profile fixes regress downstream guarantees.

Check:
1. BL-014 overall pass.
2. Active freshness suite overall pass.
3. BL-010 deterministic pass.
4. BL-011 controllability pass.

Pass criteria:
- all four surfaces report pass.

Fail indicators:
- any report status != pass, or contract/hash mismatches in freshness surfaces.

## 4) Revert Integrity Surface

### 4.1 A/B harness remains reverted
Reference commit ledger:
- 00_admin/ops_logs/commit_ledger_2026-03-25.txt

Risk:
- reverted A/B runner or env-profile scaffold accidentally reintroduced.

Check:
1. Confirm revert commits for A/B harness and A/B outputs exist in ledger.
2. Confirm no active dependency in current run path requires removed A/B scripts.

Pass criteria:
- only retained hardening fixes are active; A/B scaffolding is absent from active path.

Fail indicators:
- pipeline scripts reference removed A/B runner or template.

## 5) Fast Execution Commands (tomorrow)

From repository root thesis-main/thesis-main:

```powershell
$py = ".venv/Scripts/python.exe"

# BL-002 ingestion
& $py "07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py" --force-auth

# BL-003 (use intended mode)
& $py "07_implementation/implementation_notes/alignment/build_bl003_ds001_spotify_seed_table.py" --allow-missing-selected-sources

# BL-013 orchestration
& $py "07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py" --run-config "07_implementation/implementation_notes/run_config/outputs/run_config_profile_test_threshold_015.json"

# BL-014 + freshness
& $py "07_implementation/implementation_notes/quality/run_bl014_sanity_checks.py"
& $py "07_implementation/implementation_notes/quality/run_active_freshness_suite.py"
```

## 6) Decision Log For Tomorrow

If all checks pass:
- keep retained code fixes; decide whether to keep temporary 0.15 config as explicit profile exception.

If any high-risk check fails:
- freeze outputs,
- capture failing summary/report paths,
- open targeted fix against corresponding risk surface above.
