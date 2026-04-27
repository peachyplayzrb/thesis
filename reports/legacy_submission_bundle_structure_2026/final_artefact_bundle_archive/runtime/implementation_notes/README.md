# Implementation Notes Index (Active)

Last updated: 2026-03-28

## Purpose
This index keeps implementation notes lean by separating active operational docs from historical evidence snapshots.

## Authority Order
If guidance overlaps across documents, apply this precedence:
1. `../ACTIVE_BASELINE.md` for baseline evidence and posture authority.
2. `../RUN_GUIDE.md` for run/setup/troubleshooting authority.
3. `IMPLEMENTATION_CONTRACT.md` for stage input/output contract authority.
4. `ARTIFACT_LIFECYCLE_POLICY.md` for retention and archive authority.
5. `CODEBASE_ISSUES_CURRENT.md` for active implementation health/status narrative.

## Keep (Active Operational Contract)
- `../ACTIVE_BASELINE.md`
- `../RUN_GUIDE.md`
- `../ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md`
- `CODEBASE_ISSUES_CURRENT.md`
- `SETUP.md` (redirect to `../RUN_GUIDE.md`)
- `SUBMISSION_MANIFEST.md`
- `IMPLEMENTATION_CONTRACT.md`
- `ARTIFACT_LIFECYCLE_POLICY.md`
- `bl000_shared_utils/CURRENT_IMPLEMENTATION.md`
- `bl000_run_config/docs/RUN_CONFIG_UNIFIED_CONTRACT.md`
- `bl000_run_config/docs/semantic_control_map.md`
- `bl000_run_config/docs/run_config_profile_organization_guide.md`
- `bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`
- `bl001_bl002_ingestion/docs/spotify_schema_reference.md`
- `bl013_entrypoint/bl013_run_command.md` (redirect to `../RUN_GUIDE.md`)
- `bl000_data_layer/bl000_state_log_2026-03-25.md`
- `bl000_run_config/docs/bl000_run_config_state_log_2026-03-25.md`
- `bl001_bl002_ingestion/docs/bl001_state_log_2026-03-24.md`
- `bl001_bl002_ingestion/docs/bl002_state_log_2026-03-24.md`
- `bl003_alignment/bl003_state_log_2026-03-24.md`
- `bl004_profile/bl004_state_log_2026-03-24.md`
- `bl005_retrieval/bl005_state_log_2026-03-24.md`
- `bl006_scoring/bl006_state_log_2026-03-24.md`
- `bl007_playlist/bl007_state_log_2026-03-24.md`
- `bl008_transparency/bl008_state_log_2026-03-24.md`
- `bl009_observability/bl009_state_log_2026-03-24.md`
- `bl010_reproducibility/bl010_state_log_2026-03-24.md`
- `bl011_controllability/bl011_state_log_2026-03-24.md`
- `bl013_entrypoint/bl013_state_log_2026-03-24.md`
- `bl014_quality/bl014_state_log_2026-03-24.md`

## Keep (Stage Operational Summaries)
- `bl001_bl002_ingestion/README.md`
- `bl003_alignment/README.md`
- `bl004_profile/README.md`
- `bl005_retrieval/README.md`
- `bl006_scoring/README.md`
- `bl007_playlist/README.md`
- `bl008_transparency/README.md`
- `bl009_observability/README.md`
- `bl010_reproducibility/README.md`
- `bl011_controllability/README.md`
- `bl013_entrypoint/README.md`
- `bl014_quality/README.md`

## Keep (Active Scripts In Use)

### Core pipeline and orchestration
- `bl003_alignment/build_bl003_ds001_spotify_seed_table.py`
- `bl004_profile/build_bl004_preference_profile.py`
- `bl005_retrieval/build_bl005_candidate_filter.py`
- `bl006_scoring/build_bl006_scored_candidates.py`
- `bl007_playlist/build_bl007_playlist.py`
- `bl008_transparency/build_bl008_explanation_payloads.py`
- `bl009_observability/build_bl009_observability_log.py`
- `bl013_entrypoint/run_bl013_pipeline_entrypoint.py`

### Evaluation and quality
- `bl010_reproducibility/run_bl010_reproducibility_check.py`
- `bl011_controllability/run_bl011_controllability_check.py`
- `bl014_quality/run_bl014_sanity_checks.py`
- `bl014_quality/run_bl014_quality_suite.py`
- `bl014_quality/run_active_freshness_suite.py`
- `bl014_quality/check_bl010_bl011_freshness.py`

### Config and shared runtime utilities
- `bl000_run_config/run_config_utils.py`
- `bl000_shared_utils/config_loader.py`
- `bl000_shared_utils/constants.py`
- `bl000_shared_utils/env_utils.py`
- `bl000_shared_utils/hashing.py`
- `bl000_shared_utils/io_utils.py`
- `bl000_shared_utils/parsing.py`
- `bl000_shared_utils/path_utils.py`
- `bl000_shared_utils/report_utils.py`
- `bl000_shared_utils/types.py`

### Active ingestion path
- `bl001_bl002_ingestion/export_spotify_max_dataset.py`
- `bl001_bl002_ingestion/ingest_history_parser.py`
- `bl001_bl002_ingestion/spotify_auth.py`
- `bl001_bl002_ingestion/spotify_client.py`
- `bl001_bl002_ingestion/spotify_io.py`
- `bl001_bl002_ingestion/spotify_mapping.py`
- `bl001_bl002_ingestion/spotify_artifacts.py`
- `bl001_bl002_ingestion/spotify_resilience.py`

### Data layer utility in active tree
- `bl000_data_layer/build_ds001_working_dataset.py`

Note: these files are protected from cleanup deletion unless explicitly superseded and re-listed here.

## Keep (Historical Evidence; Do Not Use As Active Contract)
- `_archive_cleanup_2026-03-26/bl006_top50_quality_snapshot_2026-03-24.md`
- `_archive_cleanup_2026-03-26/build_bl006_scored_candidates_old.py`

## Cleanup Rules
1. Add new day-level evidence to stage state logs, not standalone ad hoc markdown snapshots.
2. Keep one active runbook per stage capability and one active implementation summary per scope.
3. If a note is superseded, mark it historical in this index or move it to an archive folder before deletion.
4. Treat `CODEBASE_ISSUES_CURRENT.md` as the only active implementation health and status summary.
5. Treat `../ACTIVE_BASELINE.md` as the only active baseline-evidence authority.
