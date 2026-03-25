# Commit Plan: Regression Follow-up (2026-03-25)

Run from repository root: thesis-main/thesis-main

1) Commit code and documentation changes first

git add -- 00_admin/change_log.md 00_admin/ops_logs/change_inventory_2026-03-25.txt 00_admin/ops_logs/commit_ledger_2026-03-25.txt 00_admin/ops_logs/high_risk_regression_checklist_2026-03-25.md 00_admin/ops_logs/high_risk_regression_run_2026-03-25.md 00_admin/ops_logs/commit_plan_2026-03-25_regression_followup.md 07_implementation/implementation_notes/ingestion/spotify_client.py 07_implementation/implementation_notes/ingestion/export_spotify_max_dataset.py 07_implementation/implementation_notes/profile/build_bl004_preference_profile.py

git commit -m "ops(regression): log fail-fast run and finalize high-risk checklist"

2) Commit regenerated runtime outputs separately

git add -A -- 07_implementation/implementation_notes/alignment/outputs 07_implementation/implementation_notes/entrypoint/outputs 07_implementation/implementation_notes/ingestion/outputs/spotify_api_export 07_implementation/implementation_notes/observability/outputs 07_implementation/implementation_notes/playlist/outputs 07_implementation/implementation_notes/profile/outputs 07_implementation/implementation_notes/quality/outputs 07_implementation/implementation_notes/reproducibility/outputs 07_implementation/implementation_notes/retrieval/outputs 07_implementation/implementation_notes/run_config/outputs 07_implementation/implementation_notes/scoring/outputs 07_implementation/implementation_notes/transparency/outputs 07_implementation/implementation_notes/controllability/outputs

git commit -m "chore(outputs): refresh BL002-BL014 artifacts after next-day regression validation"

3) Optional verification after commits

git status --short
git log -2 --oneline
