# Test Notes

- Historical note: detailed pre-2026-03-24 test records remain archived at `07_implementation/_archive_2026-03-23/test_notes.md`.
- This file re-establishes the active test log for current implementation changes.

## Test Case TC-BL005-HARDEN-001: Tightened Candidate Retrieval Selectivity

- Date: 2026-03-24
- Backlog link: `BL-005`
- Purpose: Verify that BL-005 rejects weak numeric-only matches, materially narrows the retained candidate set, and preserves BL-006 downstream continuity on the tightened output.

### Inputs
- Preference profile:
	- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
- Seed trace:
	- `07_implementation/implementation_notes/profile/outputs/bl004_seed_trace.csv`
- Candidate dataset:
	- `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_integrated_candidate_dataset.csv`
- Scripts:
	- `07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py`
	- `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`

### Expected Output
- BL-005 keep rule becomes semantic-first rather than numeric-only permissive.
- Retained candidate volume drops substantially from the previous 6,604 / 9,330 run.
- Decision outputs expose explicit keep/reject pathways.
- BL-006 rerun scores exactly the BL-005 retained set.

### Pass Criteria
- `kept_candidates` drops into a narrower range consistent with a real retrieval filter.
- `decision_path_counts.reject_numeric_without_semantic_support` is non-zero, proving numeric-only weak rows are now excluded.
- BL-006 `candidates_scored == BL-005 kept_candidates`.
- Output artifacts are regenerated with deterministic hashes.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-032`
- Observed metrics:
	- `bl005_run_id=BL005-FILTER-20260324-182142-419959`
	- `bl006_run_id=BL006-SCORE-20260324-182143-804380`
	- `candidate_rows_total=9330`
	- `kept_candidates=1938` (down from 6604; keep rate `20.77%`)
	- `rejected_non_seed_candidates=7392`
	- `decision_path.keep_strong_semantic=1654`
	- `decision_path.keep_semantic_numeric_supported=284`
	- `decision_path.reject_numeric_without_semantic_support=6877`
	- `decision_path.reject_semantic_without_numeric_support=15`
	- `decision_path.reject_no_signal=500`
	- `bl006_candidates_scored=1938`
	- `bl006_mean_score=0.250159`
	- `sha256.bl005_filtered_candidates=3B259A6471C0D9112C315723488487694B655513FBC2C7A4D842AAD5082E2DD0`
	- `sha256.bl005_candidate_decisions=878586AE36634E37B67BC5954E082DF6E8A2F4916C433F2AF79C255A9AE50DE7`
	- `sha256.bl005_candidate_diagnostics=4958523C42DA8C306EFCB8AAEDDDE1B1DA2F0A9796905E71849CDCE054EB9E99`
	- `sha256.bl006_scored_candidates=DF40DADF9F4E5F37D806B3DDD72D1E452B80215902554D8ED8A3D410B77D86A5`
	- `sha256.bl006_score_summary=CD8CA2BA81D12268B3A3A6743F0ABBB194CDB07811EF155FD079CD2944FED804`

## Test Case TC-BL006-RETUNE-001: Scoring Weight Rebalance

- Date: 2026-03-24
- Backlog link: `BL-006`
- Purpose: Verify that BL-006 scoring can be rebalanced toward numeric evidence while slightly reducing tag/genre double-counting pressure, without destabilizing the ranking pipeline.

### Inputs
- Preference profile:
	- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
- Tightened BL-005 candidate set:
	- `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`
- Script:
	- `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`

### Expected Output
- BL-006 uses the new bounded weight mix.
- Candidate scoring reruns successfully on the current 1,938 retained rows.
- Numeric contribution share in top-ranked results increases versus the prior BL-006 run.
- Output artifacts regenerate cleanly with new hashes.

### Pass Criteria
- `candidates_scored=1938`
- top-ranked set remains broadly stable
- top-100 average numeric contribution rises above the prior `0.162864`
- no static or runtime errors occur

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-033`
- Observed metrics:
	- `bl006_run_id=BL006-SCORE-20260324-182702-117298`
	- `candidates_scored=1938`
	- `max_score=0.68037`
	- `mean_score=0.247705`
	- `top100_mean_numeric=0.216824` (up from `0.162864`)
	- `top100_mean_semantic=0.338817` (down from `0.410939`)
	- `top10_overlap_with_prior_run=9/10`
	- `new_top10_entry=TRAAPPQ128F14961F5`
	- `sha256.bl006_scored_candidates=71FD79022EF93AB779989E1514E8107EF7F6222D1014C051EA89C8AB955A5F88`
	- `sha256.bl006_score_summary=448635ACD6D5CFE3996B1CCB784809D5B8FCD513234CF33B8997E6E1BE8538CA`

## Test Case TC-BL003-005-DS001-ONLY-001: DS-001-Only Semantic Path

- Date: 2026-03-24
- Backlog link: `BL-003`, `BL-005`, `BL-006`
- Purpose: Verify that selected BL-002 Spotify evidence is strictly validated at BL-003 and that BL-005/BL-006 semantic matching uses DS-001 `tags`/`genres` instead of DS-002 `tags_json`.

### Inputs
- BL-002 export summary:
	- `07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`
- DS-001 candidate dataset:
	- `07_implementation/implementation_notes/data_layer/outputs/ds001_working_candidate_dataset.csv`
- Scripts:
	- `07_implementation/implementation_notes/alignment/build_bl003_ds001_spotify_seed_table.py`
	- `07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py`
	- `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`

### Pass Criteria
- BL-003 completes with selected-source strict check enabled (default behavior).
- BL-005 diagnostics show DS-001 candidate input path and semantic source field.
- BL-006 summary shows `semantic_source=ds001_tags_and_genres_columns`.
- BL-006 `candidates_scored == BL-005 kept_candidates`.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-034`
- Observed metrics:
	- `bl003_input_event_rows=8997`
	- `bl003_matched_events_rows=2898`
	- `bl003_unmatched_rows=6099`
	- `bl005_run_id=BL005-FILTER-20260324-183958-225058`
	- `bl005_candidate_rows_total=109269`
	- `bl005_kept_candidates=56700`
	- `bl005_semantic_source=ds001_tags_and_genres_columns`
	- `bl006_run_id=BL006-SCORE-20260324-184028-117165`
	- `bl006_candidates_scored=56700`
	- `bl006_semantic_source=ds001_tags_and_genres_columns`
	- `sha256.bl005_filtered_candidates=ADF61C5EECBAD48A704C802EAE3441A7F09826A87C224D7F0A226253F2CCA679`
	- `sha256.bl006_scored_candidates=C822C15A2867BA9F9A9C044AF27561403FEE8A9AA4362586AF2AAC1A616CEDD9`

## Test Case TC-BL006-FINAL-001: BL-006 Closure Gate Before BL-007

- Date: 2026-03-24
- Backlog link: `BL-006`
- Purpose: Confirm BL-006 is finalized and handoff-ready by validating post-retune ranking stability, contribution-balance behavior, and complete artifact logging.

### Inputs
- BL-004 profile:
	- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
- BL-005 filtered candidates:
	- `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`
- BL-006 pre-retune baselines:
	- `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates_pre_retune.csv`
	- `07_implementation/implementation_notes/scoring/outputs/bl006_score_summary_pre_retune.json`
- Script:
	- `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`

### Pass Criteria
- BL-006 rerun completes with no runtime errors.
- `candidates_scored == 56700` (matches current BL-005 kept set).
- top-10 overlap against pre-retune baseline remains high (`>= 8/10`).
- Top-100 contribution balance is numeric-led.
- BL-006 state log and quality snapshot are present and consistent with run outputs.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-035`
- Observed metrics:
	- `bl006_run_id=BL006-SCORE-20260324-190145-197533`
	- `candidates_scored=56700`
	- `max_score=0.817654`
	- `mean_score=0.241022`
	- `top10_overlap_vs_pre_retune=9/10`
	- `top100_numeric_mean=0.384627`
	- `top100_semantic_mean=0.292601`
	- `top50_numeric_gt_semantic_count=41/50`
	- `sha256.bl006_scored_candidates=189C3DCF575D69736CFD855CE5D456AB5C391AD58EA20DEA803A216D35F8CE7C`
	- `sha256.bl006_score_summary=748755F1596205B3D0B46C88D71A5BF7DE3537C79AA32A9342A410A7B7E5F896`

### Closure Evidence Artifacts
- `07_implementation/implementation_notes/scoring/bl006_state_log_2026-03-24.md`
- `07_implementation/implementation_notes/scoring/bl006_top50_quality_snapshot_2026-03-24.md`

## Test Case TC-BL007-REFRESH-001: BL-007 Refresh on Finalized BL-006 Baseline

- Date: 2026-03-24
- Backlog link: `BL-007`
- Purpose: Verify BL-007 outputs are regenerated and aligned to the finalized BL-006 ranked candidates before downstream stages.

### Inputs
- BL-006 scored candidates:
	- `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
- Script:
	- `07_implementation/implementation_notes/playlist/build_bl007_playlist.py`

### Pass Criteria
- BL-007 run completes without errors.
- `tracks_included == target_size == 10`.
- BL-007 report input hash matches current BL-006 scored-candidates hash.
- Trace completeness holds (`trace_rows == candidates_evaluated`).
- Output artifacts regenerate with new hashes.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-036`
- Observed metrics:
	- `bl007_run_id=BL007-ASSEMBLE-20260324-195257-583625`
	- `candidates_evaluated=56700`
	- `tracks_included=10`
	- `tracks_excluded=56690`
	- `rule_hits.R2_genre_cap=5`
	- `rule_hits.R4_length_cap=56685`
	- `rule_hits.R1_score_threshold=0`
	- `rule_hits.R3_consecutive_run=0`
	- `playlist_genre_mix={classic rock:4,pop:4,rock:2}`
	- `playlist_score_range.max=0.817654`
	- `playlist_score_range.min=0.703525`
	- `trace_rows=56700`
	- `sha256.bl007_playlist=6E9E7D2CB82901E87CF64C13536E6469EAD9F8AF25B88C38331476B3E74A4473`
	- `sha256.bl007_assembly_trace=692A1F4DE6BD32DE0D785A3D5952D901CDF98966C264A1C8D72FF1926B6DDB9E`
	- `sha256.bl007_assembly_report=7F9B176E44AD29517F80D8904CB3A8E0E2B3111D217C5A64ED0FF67694489ADE`

### Closure Evidence Artifacts
- `07_implementation/implementation_notes/playlist/bl007_state_log_2026-03-24.md`
- `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json`
- `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_trace.csv`
- `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_report.json`

## Test Case TC-BL008-REFRESH-001: BL-008 Transparency Refresh on Current Pipeline Baseline

- Date: 2026-03-24
- Backlog link: `BL-008`
- Purpose: Verify BL-008 explanations are regenerated from current BL-006 and BL-007 outputs and that component mapping reflects active BL-006 scoring features.

### Inputs
- BL-006 scored candidates:
	- `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
- BL-006 score summary:
	- `07_implementation/implementation_notes/scoring/outputs/bl006_score_summary.json`
- BL-007 playlist and trace:
	- `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json`
	- `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_trace.csv`
- Script:
	- `07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py`

### Pass Criteria
- BL-008 run completes without runtime errors.
- `playlist_track_count == 10` in explanation outputs.
- Output summary input hashes match current BL-006 and BL-007 artifacts.
- Explanation breakdown includes active BL-006 components (`tempo`, `duration_ms`, `key`, `mode`, `lead_genre`, `genre_overlap`, `tag_overlap`).
- Output artifacts regenerate with new hashes.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-037`
- Observed metrics:
	- `bl008_run_id=BL008-EXPLAIN-20260324-195641-957331`
	- `playlist_track_count=10`
	- `top_contributor_distribution={Tempo (BPM):8, Lead genre match:2}`
	- `input_hash.bl006_scored_candidates=189C3DCF575D69736CFD855CE5D456AB5C391AD58EA20DEA803A216D35F8CE7C`
	- `input_hash.bl007_playlist=6E9E7D2CB82901E87CF64C13536E6469EAD9F8AF25B88C38331476B3E74A4473`
	- `sha256.bl008_explanation_payloads=BFAE7BBA70568DD3D0F25E20D4E1A496342C0D9A10D8C259EE9ADFB26AE59C4C`
	- `sha256.bl008_explanation_summary=3D841F3BD8E37F90AD43F4F3DD5BEF199849C40A2F3DF6E3F007633F59CDDE1D`

### Closure Evidence Artifacts
- `07_implementation/implementation_notes/transparency/bl008_state_log_2026-03-24.md`
- `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_payloads.json`
- `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_summary.json`

## Test Case TC-BL009-REFRESH-001: BL-009 Observability Refresh on Current Run Chain

- Date: 2026-03-24
- Backlog link: `BL-009`
- Purpose: Verify BL-009 observability artifacts are regenerated and correctly reference the latest BL-006, BL-007, and BL-008 runs.

### Inputs
- BL-009 script:
	- `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`
- Upstream artifacts:
	- `07_implementation/implementation_notes/scoring/outputs/bl006_score_summary.json`
	- `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_report.json`
	- `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_summary.json`

### Pass Criteria
- BL-009 run completes without runtime errors.
- Run log and run-index artifacts are regenerated.
- Upstream run IDs in BL-009 log match current BL-006 to BL-008 runs.
- run-index row is internally consistent (`kept_candidates == candidates_scored`, playlist/explanation counts present).
- Output hashes are captured.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-038`
- Observed metrics:
	- `bl009_run_id=BL009-OBSERVE-20260324-195859-875091`
	- `upstream.BL006=BL006-SCORE-20260324-190145-197533`
	- `upstream.BL007=BL007-ASSEMBLE-20260324-195257-583625`
	- `upstream.BL008=BL008-EXPLAIN-20260324-195641-957331`
	- `kept_candidates=56700`
	- `candidates_scored=56700`
	- `playlist_length=10`
	- `explanation_count=10`
	- `sha256.bl009_run_observability_log=DA7ED442B963DE439342F7232AE1CE59123AFD760B2A9DBCEDF3663468DA09D6`
	- `sha256.bl009_run_index=840CA55DC9845A88157352EA9C5A011C7CA6C7D5EFBC72F61E3FF1D3A9F4F332`

### Closure Evidence Artifacts
- `07_implementation/implementation_notes/observability/bl009_state_log_2026-03-24.md`
- `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`
- `07_implementation/implementation_notes/observability/outputs/bl009_run_index.csv`

## Test Case TC-BL010-REFRESH-001: BL-010 Reproducibility Refresh on Current Run Chain

- Date: 2026-03-24
- Backlog link: `BL-010`
- Purpose: Verify BL-010 deterministic replay remains pass on the refreshed BL-006 through BL-009 baseline and that refreshed reproducibility evidence artifacts are generated.

### Inputs
- BL-010 script:
	- `07_implementation/implementation_notes/reproducibility/run_bl010_reproducibility_check.py`
- Upstream stage artifacts consumed by BL-010:
	- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
	- `07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_diagnostics.json`
	- `07_implementation/implementation_notes/scoring/outputs/bl006_score_summary.json`
	- `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_report.json`
	- `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_summary.json`
	- `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`

### Pass Criteria
- BL-010 run completes without runtime failure.
- `deterministic_match == true` across all replays.
- Stable hashes (`ranked_output_hash`, `playlist_output_hash`, `explanation_output_hash`, `observability_output_hash`) are identical for replay_01 through replay_03.
- Dataset and pipeline versions are constant across all replay rows.
- Report, run matrix, and config snapshot artifacts are regenerated with captured hashes.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-039`
- Observed metrics:
	- `bl010_run_id=BL010-REPRO-20260324-200214`
	- `deterministic_match=true`
	- `first_mismatch_artifact=null`
	- `replay_count=3`
	- `config_hash=72CCA053B8AB1EDCEED0E1D8A8B14C27309945AC2464A2AADDD5797C1AD64D78`
	- `stable.ranked_output_hash=189C3DCF575D69736CFD855CE5D456AB5C391AD58EA20DEA803A216D35F8CE7C`
	- `stable.playlist_output_hash=651F1F546BCD1C391A865AE25E85350E2081A06FF9ABA5827BDA4000496A64EB`
	- `stable.explanation_output_hash=A4830010E7F696FBDA5E35C73567A60DB0A72758BD2736E713AC810295B229B7`
	- `stable.observability_output_hash=02245616FB0434F39817EDC91858A5B282EDCB622E9C4BC0F3D246D5BB5D7FB6`
	- `dataset_version=2648A3237AA62F9E4C667C93178D482A5ACCDA0461299472E4FC1697786A993B`
	- `pipeline_version=4E90899F05BF270F8E6C614BDF96F64D8363674DB1F32E0796A7C3CB7F0DB613`
	- `sha256.bl010_reproducibility_report=A5B902E31DF2AE2D8A5FDEFFB0EF4E5DC5A20E1987E720DC2B7B3ED9391CB3A4`
	- `sha256.bl010_reproducibility_run_matrix=36CBDFEAE6C3B7AD766B10C73A9283D6B438C92EFE30485045B2487C4AACD679`
	- `sha256.bl010_reproducibility_config_snapshot=9D9EA949CE944AE75CE13F499FBDE1F6F2EAA017E39A67AB871353CFAF04BF98`

### Closure Evidence Artifacts
- `07_implementation/implementation_notes/reproducibility/bl010_state_log_2026-03-24.md`
- `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json`
- `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_run_matrix.csv`
- `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_config_snapshot.json`
- `07_implementation/implementation_notes/reproducibility/outputs/replay_01/`
- `07_implementation/implementation_notes/reproducibility/outputs/replay_02/`
- `07_implementation/implementation_notes/reproducibility/outputs/replay_03/`

## Test Case TC-BL021-R2-001: Source-Scope Contract Persistence Probe

- Date: 2026-03-24
- Backlog link: `BL-021`
- Purpose: Verify that a canonical run-config `input_scope` override is carried through BL-013 execution and persisted in BL-004 and BL-009 outputs.

### Inputs
- Probe run config:
	- `07_implementation/implementation_notes/run_config/run_config_bl021_probe_v1.json`
- Entrypoint:
	- `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`
- Target evidence outputs:
	- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
	- `07_implementation/implementation_notes/profile/outputs/bl004_profile_summary.json`
	- `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`

### Pass Criteria
- BL-013 completes pass with `--run-config` probe file.
- BL-004 profile config includes `input_scope` matching probe values.
- BL-004 summary includes `config_source=run_config`, run-config path, schema version, and `input_scope`.
- BL-009 run metadata includes run-config provenance and BL-009 run_config includes matching `input_scope`.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-040`
- Observed metrics:
	- `bl013_run_id=BL013-ENTRYPOINT-20260324-220254-870418`
	- `bl013_overall_status=pass`
	- `bl004_run_id=BL004-PROFILE-20260324-220254-972377`
	- `bl009_run_id=BL009-OBSERVE-20260324-220302-492033`
	- `bl004.config.input_scope.top_time_ranges=["short_term"]`
	- `bl004.config.input_scope.include_saved_tracks=false`
	- `bl004.config.input_scope.saved_tracks_limit=25`
	- `bl009.run_metadata.config_source=run_config`
	- `bl009.run_metadata.run_config_schema_version=run-config-v1`
	- `bl009.run_config.input_scope.playlists_limit=3`
	- `bl009.run_config.input_scope.playlist_items_per_playlist_limit=20`
	- `bl009.run_config.input_scope.recently_played_limit=15`

### Closure Evidence Artifacts
- `07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_latest.json`
- `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
- `07_implementation/implementation_notes/profile/outputs/bl004_profile_summary.json`
- `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`

## Test Case TC-BL021-R2-002: Source-Scope A/B Probe Comparison

- Date: 2026-03-24
- Backlog link: `BL-021`
- Purpose: Compare probe-A and probe-B source-scope runs to verify persisted scope deltas and measure whether current BL-004 profile metrics change.

### Inputs
- Probe-A config:
	- `07_implementation/implementation_notes/run_config/run_config_bl021_probe_v1.json`
- Probe-B config:
	- `07_implementation/implementation_notes/run_config/run_config_bl021_probe_v2.json`
- Entrypoint:
	- `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`
- Comparison artifact output:
	- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl021_probe_comparison_summary.json`

### Pass Criteria
- Probe-B BL-013 run passes with explicit run-config provenance.
- A/B input-scope differences are captured in a persisted comparison artifact.
- BL-004 and BL-009 run IDs differ between probes, proving rerun execution.
- Comparison includes profile delta metrics and states whether deltas are zero/non-zero.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-041`
- Observed metrics:
	- `probeA.bl004_run_id=BL004-PROFILE-20260324-220254-972377`
	- `probeB.bl004_run_id=BL004-PROFILE-20260324-220502-403111`
	- `probeA.bl009_run_id=BL009-OBSERVE-20260324-220302-492033`
	- `probeB.bl009_run_id=BL009-OBSERVE-20260324-220509-565736`
	- `top_time_ranges: ["short_term"] -> ["short_term", "medium_term", "long_term"]`
	- `include_saved_tracks: false -> true`
	- `saved_tracks_limit: 25 -> 200`
	- `playlists_limit: 3 -> 12`
	- `playlist_items_per_playlist_limit: 20 -> 100`
	- `recently_played_limit: 15 -> 50`
	- `matched_seed_count_delta=0`
	- `total_effective_weight_delta=0.0`
	- `feature_center_deltas={danceability:0.0, energy:0.0, valence:0.0, tempo:0.0}`

### Interpretation
- Scope persistence and observability contract are working as intended.
- Behavioral profile deltas are currently zero under this pipeline path, consistent with source-scope actuation not yet wired into upstream ingestion/alignment selection.

### Closure Evidence Artifacts
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl004_profile_summary_probeA.json`
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl004_preference_profile_probeA.json`
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl009_run_observability_log_probeA.json`
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl021_probe_comparison_summary.json`
- `07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_latest.json`

## Test Case TC-BL021-R2-003: Source-Scope Actuation A/B Verification

- Date: 2026-03-24
- Backlog link: `BL-021`
- Purpose: Verify that source-scope is not only persisted but actively changes BL-003 seed construction and downstream BL-004 profile outputs.

### Inputs
- Probe-A config:
	- `07_implementation/implementation_notes/run_config/run_config_bl021_probe_v1.json`
- Probe-B config:
	- `07_implementation/implementation_notes/run_config/run_config_bl021_probe_v2.json`
- Scripts:
	- `07_implementation/implementation_notes/alignment/build_bl003_ds001_spotify_seed_table.py`
	- `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`
- Comparison artifact:
	- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl021_probe_comparison_actuated_summary.json`

### Pass Criteria
- BL-003 run metrics differ between probe-A and probe-B in line with scope limits.
- BL-004 profile summary shows non-zero deltas between probes.
- BL-009 continues to record run-config provenance and effective input_scope.

### Actual Result
- Status: pass
- Run evidence: `experiment_log.md` `EXP-042`
- Observed metrics:
	- `probeA.BL003.input_event_rows=637`
	- `probeB.BL003.input_event_rows=8997`
	- `BL003.input_event_rows_delta=8360`
	- `BL003.matched_events_rows_delta=2674`
	- `BL003.seed_table_rows_delta=1342`
	- `BL004.matched_seed_count_delta=1342`
	- `BL004.total_effective_weight_delta=3183.151003`
	- `BL004.feature_center_delta.tempo=-1.541983`
	- `BL009.run_metadata.config_source=run_config` (both probes)

### Interpretation
- BL-021 source-scope actuation is now behaviorally effective: changing scope controls materially changes BL-003 inputs and BL-004 outputs.
- Remaining gap is orchestration convenience: BL-003 must currently be invoked before BL-013 when scope changes.

### Closure Evidence Artifacts
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl003_summary_probeA_actuated.json`
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl003_source_scope_manifest_probeA_actuated.json`
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl004_profile_summary_probeA_actuated.json`
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl009_run_observability_log_probeA_actuated.json`
- `07_implementation/implementation_notes/run_config/probe_comparison_outputs/bl021_probe_comparison_actuated_summary.json`
- `07_implementation/implementation_notes/alignment/outputs/bl003_source_scope_manifest.json`