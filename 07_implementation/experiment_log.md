# Experiment Log

Use this file to record each implementation run as soon as it happens. The goal is to make every build step produce thesis evidence that can later be cited in Chapter 4 and Chapter 5.

## Logging Rules
- Create one entry per meaningful implementation or evaluation run.
- Link each entry to a backlog item.
- Record both successful and failed runs.
- Prefer concrete artifact paths over narrative description.
- If a run changes your interpretation of the system, note which thesis chapter or foundation file should be updated.

## Quick Start Template

Copy the block below for each new run.

---

## EXP-XXX
- date:
- backlog_link:
- owner:
- status: planned|pass|fail|bounded-risk
- related_test_id:

### Objective
- What specific artefact slice is being built or evaluated?

### Scope Check
- In-scope confirmation:
- Protected items affected? yes/no
- If yes, which files:

### Inputs
- source_data:
- config_or_parameters:
- code_or_script_path:
- dependency assumptions:

### Expected Evidence
- primary_output_artifact:
- secondary_output_artifacts:
- success_condition:

### Run Record
- command_or_execution_method:
- run_id:
- start_state_summary:
- end_state_summary:

### Results
- outcome_summary:
- key_metrics:
- deterministic_repeat_checked: yes/no
- output_paths:

### Issues And Limits
- failures_or_anomalies:
- likely_cause:
- bounded_mvp_limitation_or_bug:

### Thesis Traceability
- chapter4_relevance:
- chapter5_relevance:
- quality_control_files_to_update:

### Next Action
- immediate_follow_up:
- backlog_status_recommendation:

---

---

## EXP-001
- date: 2026-03-13
- backlog_link: `BL-001`, `BL-002`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-001`

### Objective
- Implement and validate the deterministic ingestion parser that transforms raw listening-history CSV rows into normalized JSONL events, with validation flagging.

### Scope Check
- In-scope confirmation: BL-001 schema definition and BL-002 parser implementation are both P0 MVP items.
- Protected items affected? no

### Inputs
- source_data: `07_implementation/implementation_notes/test_assets/sample_listening_history.csv`
- config_or_parameters: `--ingest-run-id TC001-RUN1 --source-platform spotify_export`
- code_or_script_path: `07_implementation/implementation_notes/ingestion/ingest_history_parser.py`
- dependency assumptions: Python stdlib only; no external packages required.

### Expected Evidence
- primary_output_artifact: `run_outputs/tc001_normalized_events.jsonl`
- secondary_output_artifacts: `run_outputs/tc001_summary.json`, deterministic repeat outputs (`tc001_normalized_events_repeat.jsonl`, `tc001_summary_repeat.json`)
- success_condition: Parser completes without crash; summary metrics are consistent; repeat run produces matching output hash.

### Run Record
- command_or_execution_method: CLI via `python ingest_history_parser.py --input ... --output ... --summary ... --ingest-run-id TC001-RUN1 --source-platform spotify_export`
- run_id: `TC001-RUN1`
- start_state_summary: Raw CSV with 5 rows; mixed quality (valid, missing ISRC, bad timestamp, missing field, negative ms_played).
- end_state_summary: JSONL output produced; summary written; repeat run confirmed hash match.

### Results
- outcome_summary: Parser correctly normalized 2 valid rows, flagged 3 invalid rows with explicit quality flags. All expected flag types observed.
- key_metrics: `rows_total=5`, `rows_valid=2`, `rows_invalid=3`, `rows_missing_isrc=2`
- deterministic_repeat_checked: yes
- output_paths:
  - `07_implementation/implementation_notes/run_outputs/tc001_normalized_events.jsonl`
  - `07_implementation/implementation_notes/run_outputs/tc001_summary.json`
  - `07_implementation/implementation_notes/run_outputs/tc001_normalized_events_repeat.jsonl`
  - `07_implementation/implementation_notes/run_outputs/tc001_summary_repeat.json`

### Issues And Limits
- failures_or_anomalies: None.
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: Sample input is synthetic (5 rows). Real listening-history exports may have additional edge cases not covered by this test asset.

### Thesis Traceability
- chapter4_relevance: Ingestion validation evidence for the reproducibility and determinism evaluation section.
- chapter5_relevance: Supports bounded limitation claim that real-world export formats may vary beyond the tested schema.
- quality_control_files_to_update: `07_implementation/test_notes.md` (TC-001 already recorded)

### Next Action
- immediate_follow_up: BL-003 alignment implementation (EXP-002).
- backlog_status_recommendation: BL-001 and BL-002 marked done.

---

## EXP-002
- date: 2026-03-13
- backlog_link: `BL-003`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-002`

### Objective
- Implement and validate ISRC-first track alignment with deterministic metadata fallback. Confirm that valid events are matched, hard-invalid rows are skipped, and alignment results are reproducible.

### Scope Check
- In-scope confirmation: BL-003 is P0 MVP.
- Protected items affected? no

### Inputs
- source_data: `07_implementation/implementation_notes/run_outputs/tc001_normalized_events.jsonl`; `07_implementation/implementation_notes/test_assets/sample_music4all_candidates.csv`
- config_or_parameters: default (skip hard-invalid rows)
- code_or_script_path: `07_implementation/implementation_notes/alignment/align_tracks.py`
- dependency assumptions: Python stdlib only; normalized events from EXP-001 must exist.

### Expected Evidence
- primary_output_artifact: `run_outputs/tc002_alignment.jsonl`
- secondary_output_artifacts: `run_outputs/tc002_summary.json`, repeat run outputs (`tc002_alignment_repeat.jsonl`, `tc002_summary_repeat.json`)
- success_condition: Script executes without failure; summary reports `matched_isrc` and `matched_fallback`; repeat run yields same `alignment_output_hash`.

### Run Record
- command_or_execution_method: CLI via `python align_tracks.py --events tc001_normalized_events.jsonl --candidates sample_music4all_candidates.csv --output tc002_alignment.jsonl --summary tc002_summary.json`
- run_id: `TC002-RUN1`
- start_state_summary: 2 valid events from EXP-001; 4-row candidate corpus stub.
- end_state_summary: Both valid events aligned; 1 via ISRC, 1 via metadata fallback; 0 unmatched.

### Results
- outcome_summary: 100% match rate on valid events. ISRC match confirmed for Blinding Lights; metadata fallback confirmed for Numb (missing ISRC in event, matched by normalized name+artist). 3 hard-invalid rows correctly skipped.
- key_metrics: `rows_total=5`, `rows_considered=2`, `rows_skipped_invalid=3`, `matched_isrc=1`, `matched_fallback=1`, `unmatched=0`, `match_rate=1.0`
- deterministic_repeat_checked: yes
- output_paths:
  - `07_implementation/implementation_notes/run_outputs/tc002_alignment.jsonl`
  - `07_implementation/implementation_notes/run_outputs/tc002_summary.json`
  - `07_implementation/implementation_notes/run_outputs/tc002_alignment_repeat.jsonl`
  - `07_implementation/implementation_notes/run_outputs/tc002_summary_repeat.json`

### Issues And Limits
- failures_or_anomalies: None.
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: Candidate corpus is a 4-row stub. Real Music4All data is required for BL-004 onward. Metadata fallback uses exact normalized match only; will not recover from typos or alternate artist name spellings.

### Thesis Traceability
- chapter4_relevance: Alignment strategy validation and match-rate evidence for discussion of data alignment design.
- chapter5_relevance: Supports limitation claim about unmatched tracks and metadata fallback constraints.
- quality_control_files_to_update: `07_implementation/test_notes.md` (TC-002 already recorded)

### Next Action
- immediate_follow_up: BL-004 preference profile generator (EXP-003 to be created when that run executes).
- backlog_status_recommendation: BL-003 marked done.

---

### Objective
- Build the first deterministic user preference profile generator from aligned listening history.

### Scope Check
- In-scope confirmation: yes, this is part of the locked MVP preference-construction stage.
- Protected items affected? no
- If yes, which files:

### Inputs
- source_data: `07_implementation/implementation_notes/run_outputs/tc002_alignment.jsonl`
- config_or_parameters: initial manual weighting scheme for recency, play frequency, and optional influence tracks
- code_or_script_path: `07_implementation/...`
- dependency assumptions: no external ML dependency required

### Expected Evidence
- primary_output_artifact: deterministic profile artifact for one test user
- secondary_output_artifacts: profile summary metrics and field explanation note
- success_condition: same input and config produce the same profile output structure and values

### Run Record
- command_or_execution_method:
- run_id:
- start_state_summary: ingestion and alignment baseline already complete
- end_state_summary:

### Results
- outcome_summary:
- key_metrics:
- deterministic_repeat_checked: no
- output_paths:

### Issues And Limits
- failures_or_anomalies:
- likely_cause:
- bounded_mvp_limitation_or_bug:

### Thesis Traceability
- chapter4_relevance: implementation and reproducibility evidence for preference-profile stage
- chapter5_relevance: any limitations in profile expressiveness or data coverage
- quality_control_files_to_update: `09_quality_control/chapter_readiness_checks.md` if evidence closes a checklist gap

### Next Action
- immediate_follow_up: run deterministic repeat check and record hash or equivalent equality check
- backlog_status_recommendation: keep `BL-004` in progress until repeatable artifact exists

---

## EXP-DA-001 — Music4All-Onion Dataset Acquisition
- date: 2026-03-19
- backlog_link: DS-001 (dataset_registry.md)
- owner: Timothy
- status: in-progress (download started 2026-03-19)

### Objective
- Download the Music4All-Onion dataset (Moscati et al., 2022, RecSys) and the Music4All base dataset (Santana et al., 2020, ICMR) from Zenodo and place them at `10_resources/datasets/music4all/`.

### Confirmed Sources
- Music4All-Onion: zenodo.org/records/15394646 — use latest version (v2). Download in progress as of 2026-03-19.
- Music4All base: separate Zenodo record by Santana et al. — needed for track metadata and Spotify-derived features.
- Music4All A+A (Artist and Album): NOT required — no album/artist-level feature use in current pipeline design.

### Files to Download (minimal set)
From Music4All-Onion:
- `userid_trackid_timestamp.tsv.bz2` — 252,984,396 listening records, 119,140 users, 56,512 tracks
- `userid_trackid_count.tsv.bz2` — interaction counts (lighter, 50M entries)
- `id_essentia.tsv.bz2` — spectral, rhythm, tonal Essentia features

From Music4All base:
- Base metadata file (track_name, artist_name, ISRC, tempo, energy, valence, danceability, loudness, acousticness, instrumentalness)

Do NOT download: audio files (.mp3), id_incp/id_resnet/id_vgg19 (video features), or the full set of BLF/compare/emobase feature files — these are not needed for the thesis pipeline.

### Dataset Scale (confirmed from README)
- Tracks: 109,269
- Users: 119,140
- Listening records: 252,984,396

### Notes
- A Zenodo account may be required for gated access.
- Column names in Essentia file differ from Spotify-style names in DS-001 schema — mapping required before BL-004/BL-006.

### Status Update
- 2026-03-19: Onion ZIP downloaded at `10_resources/datasets/15394646.zip`.
- 2026-03-19: Extraction strategy updated: do not fully extract the archive yet; inspect in-place and selectively extract only chosen files after schema confirmation.
- 2026-03-19: In-place schema inspection completed for `id_essentia`, `id_lyrics_sentiment_functionals`, `id_tags_dict`, `id_genres_tf-idf`, `userid_trackid_count`, `userid_trackid_timestamp`, `id_gems`, `id_musicnn`, `id_bert`, `id_maest`, and `id_jukebox`.
- 2026-03-19: Confirmed extract-first set: `userid_trackid_count`, `id_essentia`, `id_lyrics_sentiment_functionals`, `id_tags_dict`, `id_genres_tf-idf` plus base Music4All metadata when acquired.
- 2026-03-19: Confirmed skip set from actual schemas: `id_bert`, `id_maest`, `id_jukebox`, BLF family, ComParE family, emobase family, I-vector family, MFCC family, chroma, video embeddings, lyrics tf-idf/word2vec, `id_tags_tf-idf`, `id_vad_bow`, `processed_lyrics.tar.gz`.
- 2026-03-19: Hold for later inspection only: `userid_trackid_timestamp`, `id_gems`, `id_musicnn`.
- 2026-03-19: Target folders created for selective extraction: `10_resources/datasets/music4all_onion/selected/`, `10_resources/datasets/music4all_onion/inspect_later/`, and `10_resources/datasets/music4all_base/`.
- 2026-03-19: Planned first extraction set: `userid_trackid_count.tsv.bz2`, `id_essentia.tsv.bz2`, `id_lyrics_sentiment_functionals.tsv.bz2`, `id_tags_dict.tsv.bz2`, `id_genres_tf-idf.tsv.bz2`.
- 2026-03-19: Full archive audit completed for 46 files. Machine-readable audit written to `tmp_onion_audit.json`.
- 2026-03-19: Selected extraction completed at `10_resources/datasets/music4all_onion/selected/` for `userid_trackid_count.tsv.bz2`, `id_essentia.tsv.bz2`, `id_lyrics_sentiment_functionals.tsv.bz2`, `id_tags_dict.tsv.bz2`, `id_genres_tf-idf.tsv.bz2`.
- 2026-03-19: Secondary extraction completed at `10_resources/datasets/music4all_onion/inspect_later/` for `userid_trackid_timestamp.tsv.bz2`, `id_gems.tsv.bz2`, `id_musicnn.tsv.bz2`.
- 2026-03-19: Extracted-file summary written to `tmp_onion_selected_summary.json`.
- 2026-03-19: Final checked decision after schema review: mainline-use files are `userid_trackid_count`, `id_essentia`, `id_lyrics_sentiment_functionals`, `id_tags_dict`, `id_genres_tf-idf`; deferred-use file is `userid_trackid_timestamp`; reviewed-but-skip files include `id_gems`, `id_musicnn`, `id_bert`, `id_maest`, `id_jukebox`, all BLF, ComParE, emobase, I-vector, MFCC, chroma, video, lyrics tf-idf/word2vec, tags tf-idf, VAD, and processed lyrics.
- 2026-03-19: Base dataset retrieval guidance prepared. Automated Zenodo fetch from this environment was blocked, so manual retrieval path is: search Zenodo for `Music4All Santana` or `Music4All dataset`, open the separate base record by Santana et al. (2020), download the metadata/features file only, and place it under `10_resources/datasets/music4all_base/`.
- 2026-03-19: Candidate source check completed for `https://github.com/zerodevelops/music4all` — rejected as base dataset source. Repository is a React/Tailwind Shazam API application (`src/`, `package.json`, `vite.config.js`) and does not host the official Music4All base metadata corpus.
- 2026-03-19: Base Music4All record remains inaccessible for the user; continue with Onion-only execution path as per D-006.
- 2026-03-19: New next todo created: `BL-017` build Onion-only canonical dataset layer (track_id joins + curated feature schema + quality checks) before BL-004.
- 2026-03-19: Alternative corpus proposal logged for review (`D-008`, `UI-004`, `BL-018`): evaluate `MSD subset + Last.fm tags + MusicBrainz mapping` before making further irreversible canonical-layer implementation choices.
- 2026-03-19: Feasibility review completed for `BL-018`. Verdict: do not switch to MSD subset. Keep Music4All-Onion as the active MVP corpus, and treat blocked base-Music4All access as a non-blocking limitation rather than a reason to replace Onion.
- 2026-03-19: Base dataset download still pending.
- end: (update when files confirmed present at `10_resources/datasets/music4all/`)

## EXP-003
- date: 2026-03-19
- backlog_link: `BL-018`
- owner: Timothy + AI
- status: pass
- related_test_id: n/a

### Objective
- Execute a bounded feasibility review comparing the active Music4All-Onion corpus path against the proposed `MSD subset + Last.fm Tag Dataset + MusicBrainz mapping` alternative before further canonical-layer implementation proceeds.

### Scope Check
- In-scope confirmation: yes, this directly resolves a P0 planning blocker before BL-017.
- Protected items affected? yes
- If yes, which files: corpus-related governance and planning files only; `00_admin/thesis_state.md` intentionally left unchanged because the review did not approve a corpus switch.

### Inputs
- source_data: `06_data_and_sources/dataset_registry.md`; `07_implementation/experiment_log.md` EXP-DA-001; user-provided dataset construction sheet
- config_or_parameters: review criteria = access, complexity, feature coverage, alignment support, candidate-pool adequacy, thesis-change cost
- code_or_script_path: n/a — document review only
- dependency assumptions: previously audited Onion files and current thesis-state constraints remain accurate

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
- secondary_output_artifacts: synchronized governance updates in `decision_log.md`, `change_log.md`, `unresolved_issues.md`, `dataset_registry.md`, and `backlog.md`
- success_condition: produce a documented keep/switch/fallback recommendation and remove corpus ambiguity before BL-017

### Run Record
- command_or_execution_method: structured document comparison and governance sync in-repo
- run_id: `BL018-REVIEW-2026-03-19`
- start_state_summary: active corpus ambiguity existed because base Music4All was blocked and MSD-based replacement was under consideration
- end_state_summary: review completed; recommendation issued; MSD switch rejected; Onion-only retained as active MVP path

### Results
- outcome_summary: The review found that the unusable part of the original plan is the base-Music4All dependency, not the Onion dataset. Onion-only already provides enough interpretable data for MVP implementation with less rework and less thesis churn than a switch to the MSD subset path.
- key_metrics: `recommended_option=keep_onion_only`, `switch_to_msd=no`, `protected_state_rewrite_required=no`
- deterministic_repeat_checked: yes
- output_paths:
  - `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
  - `00_admin/decision_log.md`
  - `06_data_and_sources/dataset_registry.md`

### Issues And Limits
- failures_or_anomalies: none
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: Onion-only weakens the original base-dependent metadata and ISRC parity assumptions; these remain explicit limitations for later writing and evaluation.

### Thesis Traceability
- chapter4_relevance: justifies why the implemented corpus path differs from the earlier combined base-plus-Onion assumption
- chapter5_relevance: supports limitation discussion about blocked external data dependencies and corpus trade-offs
- quality_control_files_to_update: `08_writing/chapter3.md`, `08_writing/chapter5.md` when corpus wording is refreshed

### Next Action
- immediate_follow_up: proceed to `BL-017` and build the Onion-only canonical dataset layer
- backlog_status_recommendation: mark `BL-018` done

---

## EXP-004
- date: 2026-03-19
- backlog_link: `BL-017`
- owner: Timothy + AI
- status: pass
- related_test_id: n/a

### Objective
- Implement and execute the Onion-only canonical dataset layer builder and produce required BL-017 evidence artifacts: canonical table, join-coverage report, and selected-column manifest.

### Scope Check
- In-scope confirmation: yes, BL-017 is the immediate P0 start item after BL-018.
- Protected items affected? no

### Inputs
- source_data:
  - `10_resources/datasets/music4all_onion/selected/userid_trackid_count.tsv.bz2`
  - `10_resources/datasets/music4all_onion/selected/id_essentia.tsv.bz2`
  - `10_resources/datasets/music4all_onion/selected/id_lyrics_sentiment_functionals.tsv.bz2`
  - `10_resources/datasets/music4all_onion/selected/id_tags_dict.tsv.bz2`
  - `10_resources/datasets/music4all_onion/selected/id_genres_tf-idf.tsv.bz2`
- config_or_parameters:
  - `top_tags=10`
  - `top_genres=8`
  - uncapped production run (full files)
- code_or_script_path: `07_implementation/implementation_notes/data_layer/build_onion_canonical_layer.py`
- dependency assumptions: Python stdlib only (`argparse`, `bz2`, `csv`, `json`, `ast`, etc.)

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/data_layer/outputs/onion_canonical_track_table.csv`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/data_layer/outputs/onion_join_coverage_report.json`
  - `07_implementation/implementation_notes/data_layer/outputs/onion_selected_column_manifest.json`
- success_condition: outputs are generated deterministically with stable schema and file hashes.

### Run Record
- command_or_execution_method: CLI via `python build_onion_canonical_layer.py --selected-dir ... --output-dir ...`
- run_id: `BL017-FULL-2026-03-19A`
- start_state_summary: BL-017 had no implementation script and no canonical-layer outputs.
- end_state_summary: builder script implemented; full uncapped outputs generated with hash-recorded artifacts.

### Execution Trace
- `2026-03-19` initial bounded smoke run executed with row caps to validate parsing/join logic quickly:
  - `--max-user-track-rows 200000`
  - `--max-track-rows-per-file 10000`
- Smoke-run artifacts were verified and then superseded by uncapped production outputs in the same folder.
- Uncapped production run metadata from output report:
  - `generated_at_utc=2026-03-19T04:42:52Z`
  - `elapsed_seconds=268.261`
- Environment observation recorded during execution:
  - long-running terminal stdout capture was inconsistent in this VS Code session, so validation was performed from generated artifact files directly.

### Results
- outcome_summary: BL-017 completed successfully. Script built a deterministic joined canonical table and wrote required diagnostics/manifest files for full selected Onion inputs.
- key_metrics:
  - `elapsed_seconds=268.261`
  - `track_id_universe_count=109269`
  - `source_track_counts.user_track_counts=56512`
  - `source_track_counts.essentia=109180`
  - `source_track_counts.lyrics=109269`
  - `source_track_counts.tags=108286`
  - `source_track_counts.genres=109269`
  - `join_intersections.all_sources=56106`
  - `canonical_table_logical_rows=109269` (equal to track_id universe)
  - `canonical_table_logical_line_count=109270` (header + data rows)
  - `canonical_table_column_count=33`
  - `sha256.onion_canonical_track_table.csv=cc8601d49f078226ac55636c2788386179f39bb2ad8474f094bdad4b813ee22a`
  - `sha256.onion_join_coverage_report.json=cc755e03f3ece9a6010dcefd069df0ff9ad6c16a03db5908f938a11f10c5dc7d`
  - `sha256.onion_selected_column_manifest.json=814a8e27fcea77e92743077f4e3521b69e59f966df993464e3c095d20a177bd3`
- deterministic_repeat_checked: no
- output_paths:
  - `07_implementation/implementation_notes/data_layer/outputs/onion_canonical_track_table.csv`
  - `07_implementation/implementation_notes/data_layer/outputs/onion_join_coverage_report.json`
  - `07_implementation/implementation_notes/data_layer/outputs/onion_selected_column_manifest.json`

### Validation Checks
- Coverage/missingness check:
  - selected Essentia and lyrics columns reported `0` missing values across available rows in the uncapped run.
- Join integrity check:
  - `all_sources=56106`
  - `counts_and_essentia=56463`
  - `counts_and_lyrics=56512`
  - `counts_and_tags=56155`
  - `counts_and_genres=56512`
- Scope consistency check:
  - BL-017 output set matches backlog evidence requirements exactly (canonical table + join coverage + selected column manifest).

### Issues And Limits
- failures_or_anomalies: terminal output capture for long-running commands was inconsistent in this environment, so artifact verification was done directly from generated files.
- likely_cause: VS Code terminal integration behavior under large-file batch processing.
- bounded_mvp_limitation_or_bug: no functional blocker in BL-017; reproducibility replay for this stage still pending.

### Thesis Traceability
- chapter4_relevance: provides first concrete evidence that Onion-only canonical-layer engineering is operational and reproducible in structure.
- chapter5_relevance: supports limitation discussion about partial cross-source coverage differences across Onion feature files (e.g., counts/tags/essentia coverage mismatch).
- quality_control_files_to_update: `07_implementation/test_notes.md` (optional addition if BL-017 receives a dedicated deterministic replay test case)

### Next Action
- immediate_follow_up: proceed to `BL-016` synthetic pre-aligned data assets, using `onion_canonical_track_table.csv` as candidate stub source.
- backlog_status_recommendation: mark `BL-017` done and schedule deterministic replay check as part of BL-014/BL-010 quality pass.

---

## EXP-005
- date: 2026-03-19
- backlog_link: `BL-016`
- owner: Timothy + AI
- status: pass
- related_test_id: n/a

### Objective
- Create deterministic synthetic pre-aligned assets that let BL-004 onward proceed without waiting for real ingestion and alignment.

### Scope Check
- In-scope confirmation: yes, BL-016 is the Phase A bootstrap step defined in `implementation_plan.md`.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/data_layer/outputs/onion_canonical_track_table.csv`
- config_or_parameters:
  - `full_coverage_required=True`
  - `history_target=8`
  - `influence_target=3`
  - `candidate_target=60`
  - `core_candidate_target=45`
  - `core_genres=[indie rock, indie pop, electronic, trip hop, alternative rock, pop]`
  - `contrast_genres=[rap, hip hop, hard rock, country, folk, pop punk]`
  - `sort_order=[playcount_sum desc, track_id asc]`
- code_or_script_path: `07_implementation/implementation_notes/test_assets/build_bl016_synthetic_assets.py`
- dependency assumptions: Python stdlib only; BL-017 canonical output must already exist.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
  - `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`
- success_condition: synthetic aligned seeds and candidate stub are produced deterministically with manifest-recorded selection rules.

### Run Record
- command_or_execution_method: CLI via `python build_bl016_synthetic_assets.py`
- run_id: `BL016-GEN-2026-03-19A`
- start_state_summary: `test_assets/` was empty after clean restart.
- end_state_summary: generator script added; three BL-016 asset files created and validated.

### Execution Trace
- Source selection base: BL-017 canonical table at `07_implementation/implementation_notes/data_layer/outputs/onion_canonical_track_table.csv`
- Selection constraints applied before any seed choice:
  - full source coverage required for all seed tracks
  - sort by `playcount_sum desc`, then `track_id asc`
- Synthetic scenario structure created:
  - 8 history seeds
  - 3 influence seeds
  - 60 candidate rows total
  - 45 preference-aligned rows and 15 contrast rows
- Generated file footprint:
  - `bl016_synthetic_aligned_events.jsonl=3156 bytes`
  - `bl016_candidate_stub.csv=48976 bytes`
  - `bl016_asset_manifest.json=2791 bytes`

### Results
- outcome_summary: BL-016 completed successfully. A deterministic synthetic single-user bootstrap set was generated from fully covered canonical tracks, including 8 history seeds, 3 influence seeds, and a 60-track candidate stub with both preference-aligned and contrast examples.
- key_metrics:
  - `history_count=8`
  - `influence_count=3`
  - `synthetic_aligned_line_count=11`
  - `candidate_count=60`
  - `candidate_stub_line_count=61`
  - `core_candidate_count=45`
  - `contrast_candidate_count=15`
  - `synthetic_user_id=synthetic_user_001`
  - `history_seed_genres=[indie rock, indie pop, electronic, trip hop, alternative rock, pop, indie rock, indie rock]`
  - `influence_seed_genres=[indie pop, alternative rock, alternative rock]`
  - `sha256.bl016_synthetic_aligned_events.jsonl=F22C31F512CB9DC1708858419923C46E8D65895CB582BFE019F869CF34333771`
  - `sha256.bl016_candidate_stub.csv=66505924A3BC9A627122310B6C4108BD397F4DD3E5FF9924991977A4C9574678`
  - `sha256.bl016_asset_manifest.json=8D7BF7193777681DA9D9CD476EC2FE6D23B3541E29347F854413FD87ACF266EC`
- deterministic_repeat_checked: no
- output_paths:
  - `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
  - `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
  - `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`

### Validation Checks
- Asset-shape check:
  - aligned JSONL contains 11 rows total (`8 history + 3 influence`)
  - candidate stub contains 60 data rows plus header
- Selection-rule check:
  - all selected seeds come from full-coverage canonical rows
  - all seed track_ids are included inside the candidate stub
- Scenario-quality check:
  - stub intentionally mixes preference-aligned genres with contrast genres so BL-005 and BL-006 can test ranking separation rather than only same-cluster retrieval.
- Seed audit:
  - history track_ids: `0ng9VQtWuSjd0arq`, `lJKIbZNzpS6IsNgh`, `yfm7RER1PWTqgjIp`, `io7RYSOjKB4YpBKy`, `L4lGOjfg9lTLXh3U`, `zp4zYVjiH2Tm3gTM`, `lZDk11KaRskQqhWf`, `wQ4RdMXUKj1ry4p6`
  - influence track_ids: `cDf6FcmbzmqAMZXB`, `KxryDZFfi0mkMMiM`, `o2LcK38b4mFLa55g`
  - candidate composition is recorded fully in `bl016_asset_manifest.json`

### Issues And Limits
- failures_or_anomalies: none
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: the synthetic user profile is engineered from aggregate corpus-side signals and does not represent a real exported listening history.
- additional_note: seed selection favors high-playcount, high-coverage rows, so early pipeline behavior may look cleaner than later real-ingestion behavior.

### Thesis Traceability
- chapter4_relevance: documents the bootstrap step that enabled core pipeline implementation before real ingestion/alignment was restored.
- chapter5_relevance: supports limitation framing that early-stage pipeline behavior was first validated on synthetic pre-aligned inputs.
- quality_control_files_to_update: `07_implementation/test_notes.md` if BL-016 is later given a dedicated bootstrap-asset validation test case.

### Next Action
- immediate_follow_up: start `BL-004` using `bl016_synthetic_aligned_events.jsonl` as the preference seed input and `bl016_candidate_stub.csv` as the candidate pool.
- backlog_status_recommendation: mark `BL-016` done.

---

## EXP-006
- date: 2026-03-19
- backlog_link: `BL-004`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-PROFILE-001`

### Objective
- Build the first deterministic user preference profile from the BL-016 synthetic aligned events and candidate stub.

### Scope Check
- In-scope confirmation: yes, BL-004 is the first core-pipeline stage after the synthetic bootstrap assets.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
  - `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
- config_or_parameters:
  - `effective_weight_rule=preference_weight`
  - `top_tag_limit=10`
  - `top_genre_limit=10`
  - `top_lead_genre_limit=10`
  - numeric aggregation via weighted mean over matched seeds
  - semantic aggregation via weighted sums over tag weights and genre scores
- code_or_script_path: `07_implementation/implementation_notes/profile/build_bl004_preference_profile.py`
- dependency assumptions: Python stdlib only; BL-016 assets must already exist and contain one synthetic user.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/profile/outputs/bl004_profile_summary.json`
  - `07_implementation/implementation_notes/profile/outputs/bl004_seed_trace.csv`
- success_condition: all synthetic seeds match candidate rows and yield a stable, inspectable profile for one test user.

### Run Record
- command_or_execution_method: CLI via `python build_bl004_preference_profile.py`
- run_id: `BL004-PROFILE-20260319-045738`
- start_state_summary: BL-004 had no implementation script or profile outputs.
- end_state_summary: profile generator implemented; full profile, summary, and seed trace artifacts created successfully.

### Execution Trace
- Input join path: `aligned_events.track_id -> candidate_stub.track_id`
- Join result: all 11 synthetic events matched to candidate rows; no missing seeds.
- Effective weighting rule used in the run: `effective_weight = preference_weight`
- Output footprint:
  - `bl004_preference_profile.json=5346 bytes`
  - `bl004_profile_summary.json=2543 bytes`
  - `bl004_seed_trace.csv=1390 bytes`
  - `bl004_seed_trace.csv line_count=12` (header + 11 rows)
- Profile artifact timestamp:
  - `generated_at_utc=2026-03-19T04:57:38Z`

### Results
- outcome_summary: BL-004 completed successfully. The profile clearly centers on indie rock / indie pop / alternative rock with secondary electronic and trip-hop influence, matching the synthetic bootstrap design.
- key_metrics:
  - `events_total=11`
  - `matched_seed_count=11`
  - `missing_seed_count=0`
  - `candidate_rows_total=60`
  - `total_effective_weight=16.0276`
  - `weight_by_interaction_type.history=11.9776`
  - `weight_by_interaction_type.influence=4.05`
  - `feature_center.rhythm.bpm=117.84215`
  - `feature_center.rhythm.danceability=1.190363`
  - `feature_center.lowlevel.loudness_ebu128.integrated=-15.322141`
  - `feature_center.V_mean=5.741829`
  - `feature_center.A_mean=4.278339`
  - `feature_center.D_mean=5.371368`
  - `top_lead_genre_1=indie rock`
  - `top_lead_genre_2=alternative rock`
  - `top_lead_genre_3=indie pop`
  - `top_tag_1=indie`
  - `top_tag_2=alternative`
  - `top_tag_3=rock`
  - `top_genre_1=indie rock`
  - `top_genre_2=indie pop`
  - `top_genre_3=rock`
  - `sha256.bl004_preference_profile.json=8C9747BF5CF8A4CAC5C900D2346C54E82D1E24E9CAAF3AD0ADE6794AFFA3D10E`
  - `sha256.bl004_profile_summary.json=1685A266C61C68183DA6E97AAD1D571DC25DE3C2198496AC85A70C1CF68F29C7`
  - `sha256.bl004_seed_trace.csv=C47D4FBC6F0D9CCDD33699AF2D62AA37368FE335883FFCE96CEACC1D0DA55584`
- deterministic_repeat_checked: no
- output_paths:
  - `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
  - `07_implementation/implementation_notes/profile/outputs/bl004_profile_summary.json`
  - `07_implementation/implementation_notes/profile/outputs/bl004_seed_trace.csv`

### Validation Checks
- Join integrity check:
  - `matched_seed_count=11`
  - `missing_seed_count=0`
- Weighting-rule check:
  - profile uses the already-defined BL-016 `preference_weight` values directly; no additional hidden scaling was applied.
- Semantic consistency check:
  - dominant lead genres (`indie rock`, `alternative rock`, `indie pop`) match the synthetic seed design.
  - top tags (`indie`, `alternative`, `rock`, `pop`) are directionally consistent with the selected history and influence tracks.
- Expanded semantic profile snapshot:
  - top tags: `indie`, `alternative`, `rock`, `pop`, `alternative rock`, `indie rock`, `indie pop`, `electronic`, `female vocalists`, `imagine dragons`
  - top genres: `indie rock`, `indie pop`, `rock`, `pop`, `alternative rock`, `trip hop`, `electronic`, `grunge`
  - top lead genres: `indie rock`, `alternative rock`, `indie pop`, `electronic`, `trip hop`, `pop`
- Expanded numeric profile snapshot:
  - `lowlevel.average_loudness=0.910836`
  - `rhythm.onset_rate=3.656946`
  - `rhythm.beats_count=58.138573`
  - `lowlevel.spectral_centroid.mean=1098.959047`
  - `tonal.key_temperley.strength=0.688476`
  - `P_mean=0.070704`
- Artifact-shape check:
  - profile JSON contains config, diagnostics, numeric feature centers, and semantic summaries.
  - seed trace provides one row per matched seed.

### Issues And Limits
- failures_or_anomalies: none
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: the current profile generator uses `preference_weight` directly rather than combining it with a second interaction-count transform; this keeps behavior transparent, but may underuse the raw `interaction_count` field until later tuning.

### Thesis Traceability
- chapter4_relevance: provides the first direct evidence of how user preference representation is engineered from aligned inputs before candidate scoring begins.
- chapter5_relevance: supports later discussion of weighting-rule simplicity and the trade-off between transparency and richer weighting heuristics.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-PROFILE-001`.

### Next Action
- immediate_follow_up: start `BL-005` candidate retrieval and feature filtering using the profile artifact and the BL-016 candidate stub.
- backlog_status_recommendation: mark `BL-004` done.

---

## EXP-007
- date: 2026-03-19
- backlog_link: `BL-005`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-CAND-001`

### Objective
- Implement deterministic candidate retrieval and feature filtering so the BL-004 preference profile can narrow the BL-016 candidate stub before scoring.

### Scope Check
- In-scope confirmation: yes, BL-005 is the immediate next P0 stage after profile construction.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
  - `07_implementation/implementation_notes/profile/outputs/bl004_seed_trace.csv`
  - `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
- config_or_parameters:
  - `top_lead_genre_limit=6`
  - `top_tag_limit=10`
  - `top_genre_limit=8`
  - `numeric_thresholds={bpm:20.0, danceability:0.4, loudness:6.0, V_mean:0.8, A_mean:0.9, D_mean:0.8}`
  - `keep_rule=keep if not seed and ((semantic_score >= 2 and numeric_pass_count >= 4) or (semantic_score == 3 and numeric_pass_count >= 3))`
- code_or_script_path: `07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py`
- dependency assumptions: Python stdlib only; BL-004 profile and BL-016 candidate stub must already exist.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_decisions.csv`
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_diagnostics.json`
- success_condition: seed tracks are excluded, filtered candidates are a proper subset of the stub, and all decisions are traceable.

### Run Record
- command_or_execution_method: CLI via `python build_bl005_candidate_filter.py`
- run_id: `BL005-FILTER-20260319-050329`
- start_state_summary: BL-005 had no implementation script or retrieval outputs.
- end_state_summary: retrieval/filter script implemented; final filtered candidate set, decision trace, and diagnostics created.

### Execution Trace
- Retrieval path:
  - read profile semantics and numeric centers from BL-004
  - read seed track ids from BL-004 seed trace
  - evaluate every BL-016 candidate row deterministically
- Candidate evaluation dimensions:
  - semantic overlap: lead genre match, genre overlap, tag overlap
  - numeric closeness: bpm, danceability, loudness, V_mean, A_mean, D_mean
- Same-day correction applied before final logging:
  - initial thresholds were too loose and kept almost all non-seed candidates
  - thresholds and keep rule were tightened
  - diagnostics hashing was corrected so the diagnostics file no longer stores a stale self-hash
- Output footprint:
  - `bl005_filtered_candidates.csv=34618 bytes`
  - `bl005_candidate_decisions.csv=9178 bytes`
  - `bl005_candidate_diagnostics.json=3077 bytes`
  - `bl005_filtered_candidates.csv line_count=43` (header + 42 kept rows)
  - `bl005_candidate_decisions.csv line_count=61` (header + 60 decision rows)

### Results
- outcome_summary: BL-005 completed successfully. The final filter removed all 11 seed tracks and rejected 7 additional non-seed candidates, mainly contrast-genre rows that were numerically plausible but semantically weak for the profile.
- key_metrics:
  - `candidate_rows_total=60`
  - `seed_tracks_excluded=11`
  - `kept_candidates=42`
  - `rejected_non_seed_candidates=7`
  - `semantic_rule_hits.lead_genre_match=45`
  - `semantic_rule_hits.genre_overlap=55`
  - `semantic_rule_hits.tag_overlap=59`
  - `numeric_rule_hits.rhythm.bpm=32`
  - `numeric_rule_hits.rhythm.danceability=49`
  - `numeric_rule_hits.lowlevel.loudness_ebu128.integrated=47`
  - `numeric_rule_hits.V_mean=56`
  - `numeric_rule_hits.A_mean=59`
  - `numeric_rule_hits.D_mean=60`
  - `sha256.bl005_filtered_candidates.csv=4C7341830731A285DBA71A7FDD34C983AD77A459B040A993A90880AA8F0971E1`
  - `sha256.bl005_candidate_decisions.csv=F814C1EBED4E145B4AD94BCE37D9DA42BBD9399A08187DFB8D515BC7FA1D49D0`
  - `sha256.bl005_candidate_diagnostics.json=867402AE26522A723D237F5755D30F66AF0811DEA665DB6DE580D9268EDA4686`
- deterministic_repeat_checked: no
- output_paths:
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_decisions.csv`
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_diagnostics.json`

### Validation Checks
- Subset check:
  - output candidate set is smaller than the 60-row stub
  - kept rows = 42, so BL-005 is doing real narrowing rather than passing through the full stub
- Seed exclusion check:
  - all 11 seed tracks are explicitly rejected with reason `seed track excluded from retrieval output`
- Decision-trace check:
  - one decision row exists for each of the 60 candidates
  - every candidate has semantic and numeric counts recorded
- Rejection-pattern check:
  - rejected non-seed examples include `hip hop`, `hard rock`, `country`, and `folk` leads where semantic alignment was too weak even when some numeric dimensions were close
  - examples: `BbjwoLBQtBZL1YfK` (`hip hop`, semantic_score=1, numeric_pass_count=6), `vKFHcHKZg3pclkXm` (`country`, semantic_score=0, numeric_pass_count=5), `QJidJKvG8eJcobww` (`folk`, semantic_score=1, numeric_pass_count=5)

### Issues And Limits
- failures_or_anomalies: initial BL-005 thresholds were too permissive and were tightened before final artifact logging.
- likely_cause: the BL-016 candidate stub is intentionally preference-heavy, so a very light filter does not separate enough candidates.
- bounded_mvp_limitation_or_bug: the current BL-005 stage still keeps 42 of 49 non-seed candidates, so most of the real discrimination will still occur in BL-006 scoring rather than here.

### Thesis Traceability
- chapter4_relevance: provides evidence for the candidate-narrowing stage and shows explicit engineering rules before scoring.
- chapter5_relevance: supports discussion of the trade-off between conservative retrieval recall and stricter pre-scoring pruning.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-CAND-001`.

### Next Action
- immediate_follow_up: start `BL-006` deterministic scoring over `bl005_filtered_candidates.csv` using the BL-004 profile.
- backlog_status_recommendation: mark `BL-005` done.

---

## EXP-008
- date: 2026-03-19
- backlog_link: `BL-006`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-SCORE-001`

### Objective
- Implement deterministic candidate scoring so each BL-005 retained candidate receives an explicit weighted score breakdown against the BL-004 profile.

### Scope Check
- In-scope confirmation: yes, BL-006 is the next P0 ranking stage after retrieval/filtering.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`
- config_or_parameters:
  - `numeric_thresholds={bpm:20.0, danceability:0.4, loudness:6.0, V_mean:0.8, A_mean:0.9, D_mean:0.8}`
  - `component_weights={bpm:0.10, danceability:0.10, loudness:0.08, V_mean:0.12, A_mean:0.08, D_mean:0.08, lead_genre:0.12, genre_overlap:0.16, tag_overlap:0.16}`
  - `numeric_similarity=max(0, 1 - abs(diff)/threshold)`
  - ranking order = `final_score desc`, then `track_id asc`
- code_or_script_path: `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`
- dependency assumptions: Python stdlib only; BL-004 profile and BL-005 filtered candidates must already exist.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/scoring/outputs/bl006_score_summary.json`
- success_condition: all BL-005 candidates are scored, ranked, and accompanied by transparent component contributions.

### Run Record
- command_or_execution_method: CLI via `python build_bl006_scored_candidates.py`
- run_id: `BL006-SCORE-20260319-050806`
- start_state_summary: BL-006 had no implementation script or scoring outputs.
- end_state_summary: scoring script implemented; ranked candidate table and summary artifact created successfully.

### Execution Trace
- Scoring path:
  - read numeric centers and semantic profile from BL-004
  - read 42 retained candidates from BL-005
  - compute per-feature numeric similarity and per-channel semantic similarity
  - apply fixed weights and emit descending ranked output
- Output footprint:
  - `bl006_scored_candidates.csv=10322 bytes`
  - `bl006_score_summary.json=4854 bytes`
  - `bl006_scored_candidates.csv line_count=43` (header + 42 scored rows)
- Run summary timestamp from artifact:
  - `generated_at_utc=2026-03-19T05:08:06Z`

### Results
- outcome_summary: BL-006 completed successfully. The scorer ranked all 42 retained candidates and clearly favored the intended indie-oriented profile, with top results dominated by `indie rock` and `indie pop` rows that combine strong semantic overlap with close numeric fit.
- key_metrics:
  - `candidates_scored=42`
  - `score.max=0.724318`
  - `score.min=0.20486`
  - `score.mean=0.490817`
  - `score.median=0.501178`
  - `top_candidate_1=jPv1Tj4Mgo4l2Oue|indie rock|0.724318`
  - `top_candidate_2=POdgTSLBnoFJaj2x|indie rock|0.702439`
  - `top_candidate_3=PvGcoMH6vGWBaoXh|indie rock|0.669177`
  - `top_candidate_4=1XZP3bEawLbWfSkM|indie rock|0.664076`
  - `top_candidate_5=hn1Z3OcZ4HM3hcIi|indie rock|0.655572`
  - `top10_lead_genre_mix.indie_rock=9`
  - `top10_lead_genre_mix.indie_pop=1`
  - `bottom_candidate_1=9EERk7bPIn9HNBvE|pop|0.20486`
  - `bottom_candidate_2=eNKt8Nt4qTpVT935|hard rock|0.296153`
  - `bottom_candidate_3=VjL805nl0oHFzqSt|hard rock|0.313157`
  - `sha256.bl006_scored_candidates.csv=BF9AB8A4FE27596276F8B1868FC1246BCA4B04B6315DFBB6FEF673DDF53E1AA2`
  - `sha256.bl006_score_summary.json=64CF9165AFB670E40E450C363A7DB61BA188A682226C1A73B2957077AA6F2A51`
- deterministic_repeat_checked: no
- output_paths:
  - `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
  - `07_implementation/implementation_notes/scoring/outputs/bl006_score_summary.json`

### Validation Checks
- Ranking-integrity check:
  - 42 scored data rows exist, matching the 42 BL-005 retained candidates.
  - CSV is sorted by `rank asc` and `final_score desc` as intended.
- Score-construction check:
  - component weights sum to `1.0`
  - each scored row contains raw similarity values and weighted contribution columns for all numeric and semantic channels
- Separation-pattern check:
  - top-ranked rows combine `lead_genre_similarity=1.0` with strong tag and genre overlap plus acceptable numeric fit
  - lowest-ranked rows are mostly semantically weaker `pop` or `hard rock` examples that survived BL-005 but could not compete once weighted scoring was applied
- Transparency check:
  - first ranked row (`jPv1Tj4Mgo4l2Oue`) exposes reconstructable contributions across bpm, danceability, loudness, valence, arousal, dominance, lead genre, genre overlap, and tag overlap

### Issues And Limits
- failures_or_anomalies: none in the final BL-006 run.
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: because the BL-016 candidate stub is synthetic and preference-heavy, the top of the ranked list is strongly clustered around indie-oriented leads; later real-corpus runs may show broader genre competition.

### Thesis Traceability
- chapter4_relevance: provides direct evidence for the deterministic weighted ranking stage and shows how transparent score composition works before playlist assembly.
- chapter5_relevance: supports later discussion of ranking concentration, weight sensitivity, and the limits of a synthetic bootstrap candidate pool.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-SCORE-001`.

### Next Action
- immediate_follow_up: start `BL-007` rule-based playlist assembly using the BL-006 ranked output as the ordered candidate source.
- backlog_status_recommendation: mark `BL-006` done.

---

## EXP-009
- date: 2026-03-19
- backlog_link: `BL-007`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-PLAYLIST-001`

### Objective
- Implement rule-based playlist assembly that selects a fixed-length, genre-diverse playlist from the BL-006 ranked candidates using explicit and traceable rule logic.

### Scope Check
- In-scope confirmation: yes, BL-007 is the next P0 pipeline stage and the first output a user would see.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
- config_or_parameters:
  - `target_size=10`
  - `min_score_threshold=0.35`
  - `max_per_genre=4`
  - `max_consecutive=2`
  - rule traversal order: R1 (score) → R2 (genre cap) → R3 (consecutive run) → R4 (length cap)
- code_or_script_path: `07_implementation/implementation_notes/playlist/build_bl007_playlist.py`
- dependency assumptions: Python stdlib only; BL-006 scored candidates must already exist.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_trace.csv`
  - `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_report.json`
- success_condition: 10-track playlist assembled deterministically; every candidate has a decision trace row; genre mix is diversified away from a pure indie-rock list.

### Run Record
- command_or_execution_method: CLI via `python build_bl007_playlist.py`
- run_id: `BL007-ASSEMBLE-20260319-051947`
- start_state_summary: BL-007 had no implementation script or playlist outputs.
- end_state_summary: assembler script implemented; all three playlist artifacts created successfully.

### Execution Trace
- Assembly path:
  - iterate BL-006 candidates in score-descending order
  - apply R1–R4 per candidate; record decision and rule in trace
  - collect included tracks into ordered playlist until target reached
- Output footprint:
  - `bl007_playlist.json=2054 bytes`
  - `bl007_assembly_trace.csv=2808 bytes`
  - `bl007_assembly_report.json=1052 bytes`
  - `bl007_playlist.json line_count=84`
  - `bl007_assembly_trace.csv line_count=43` (header + 42 candidate rows)
- Run timestamp from artifact:
  - `generated_at_utc=2026-03-19T05:19:47Z`

### Results
- outcome_summary: BL-007 completed successfully. A 10-track playlist was assembled with 5 distinct genres, showing that the diversity rules successfully broke the pure indie-rock dominance that would exist without them.
- key_metrics:
  - `candidates_evaluated=42`
  - `tracks_included=10`
  - `tracks_excluded=32`
  - `R1_score_threshold_hits=0`
  - `R2_genre_cap_hits=5`
  - `R3_consecutive_run_hits=4`
  - `R4_length_cap_hits=23`
  - `playlist_genre_mix.indie_rock=4`
  - `playlist_genre_mix.indie_pop=2`
  - `playlist_genre_mix.alternative_rock=2`
  - `playlist_genre_mix.pop=1`
  - `playlist_genre_mix.folk=1`
  - `playlist_score_range.max=0.724318`
  - `playlist_score_range.min=0.510916`
  - `playlist_position_1=jPv1Tj4Mgo4l2Oue|indie rock|0.724318|score_rank=1`
  - `playlist_position_3=yUa5uu5wFCGwl2PK|indie pop|0.643423|score_rank=7`
  - `playlist_position_7=0X9aluHlz6iKWBMR|alternative rock|0.559544|score_rank=13`
  - `playlist_position_10=PZEgbQhTHMMrKRLv|folk|0.510916|score_rank=19`
  - `sha256.bl007_playlist.json=8B53B03D23F241EB102AD48E98395C34140356BCE3640348F2AF4C7EC44009FB`
  - `sha256.bl007_assembly_trace.csv=9F432BC31CCF158909F2488A2D3A85EB073E76FB562F924A1C51324B66C32193`
  - `sha256.bl007_assembly_report.json=9975141AF1C3E3A33D2298A07148E6584056588EE5CDD3884DA4C17B85DF2333`
- deterministic_repeat_checked: no
- output_paths:
  - `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json`
  - `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_trace.csv`
  - `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_report.json`

### Validation Checks
- Length check:
  - `playlist_length=10` matches `target_size=10`
- Diversity check:
  - 5 distinct genres in 10 tracks; no single genre exceeds 4 slots (genre cap enforced)
  - no two adjacent tracks share the same genre for more than 2 consecutive positions (consecutive run enforced)
- Score floor check:
  - all included tracks scored ≥ 0.510916, well above the 0.35 threshold; R1 was not triggered
  - this confirms the score floor was not the binding constraint — genre diversity rules did the real selection work
- Rule hit audit:
  - R2 (genre cap): 5 hits — primarily indie rock tracks that were crowded out after 4 slots filled
  - R3 (consecutive run): 4 hits — enforced genre breaks in the mid-ranking indie rock cluster
  - R4 (length cap): 23 hits — all remaining candidates after position 10 was reached
  - R1 (score threshold): 0 hits — all evaluated candidates scored above 0.35
- Trace completeness check:
  - 42 trace rows plus header = 43 lines; matches BL-006 candidate count exactly
- Full ordered playlist:
  - pos 1  | jPv1Tj4Mgo4l2Oue | indie rock        | score=0.724318 | rank=1
  - pos 2  | POdgTSLBnoFJaj2x | indie rock        | score=0.702439 | rank=2
  - pos 3  | yUa5uu5wFCGwl2PK | indie pop         | score=0.643423 | rank=7
  - pos 4  | j8qrlsfqWAPqzqD9 | indie rock        | score=0.631517 | rank=8
  - pos 5  | 8keAhBJumHlc8qe9 | indie rock        | score=0.606053 | rank=9
  - pos 6  | Nyb0YqqyaSvWThIG | indie pop         | score=0.592793 | rank=11
  - pos 7  | 0X9aluHlz6iKWBMR | alternative rock  | score=0.559544 | rank=13
  - pos 8  | ql2191d6uNCVM932 | alternative rock  | score=0.548263 | rank=15
  - pos 9  | 9ZtfD8gBZXonrJKX | pop               | score=0.51886  | rank=18
  - pos 10 | PZEgbQhTHMMrKRLv | folk              | score=0.510916 | rank=19
- Full exclusion trace (excluded candidates in score order):
  - R3 | rank=3  | PvGcoMH6vGWBaoXh | indie rock       | score=0.669177 | reason=consecutive_genre_run
  - R3 | rank=4  | 1XZP3bEawLbWfSkM | indie rock       | score=0.664076 | reason=consecutive_genre_run
  - R3 | rank=5  | hn1Z3OcZ4HM3hcIi | indie rock       | score=0.655572 | reason=consecutive_genre_run
  - R3 | rank=6  | nlgMHNZ0qCS2vdmV | indie rock       | score=0.646756 | reason=consecutive_genre_run
  - R2 | rank=10 | xr1HkbplUycZcEZX | indie rock       | score=0.602369 | reason=genre_cap_exceeded
  - R2 | rank=12 | CiLFjUJvYWGmyr2d | indie rock       | score=0.583893 | reason=genre_cap_exceeded
  - R2 | rank=14 | yKSK3z6kBv2YJfjx | indie rock       | score=0.558186 | reason=genre_cap_exceeded
  - R2 | rank=16 | ez35sBpNVUuM6emD | indie rock       | score=0.533993 | reason=genre_cap_exceeded
  - R2 | rank=17 | UD0DWvRMwWe8Swiw | indie rock       | score=0.532331 | reason=genre_cap_exceeded
  - R4 | rank=20 | B7SJXdcP0HhDMyfm | indie rock       | score=0.507858 | reason=length_cap_reached
  - R4 | rank=21 | GB9LkV8pTLXCCvX6 | folk             | score=0.503448 | reason=length_cap_reached
  - R4 | rank=22 | SezvoI7y9p6mDvB3 | pop              | score=0.498907 | reason=length_cap_reached
  - R4 | rank=23 | X4ws3hW4yKZyFPi6 | indie pop        | score=0.493248 | reason=length_cap_reached
  - R4 | rank=24 | X4fkzkyHslEut5Tc | indie rock       | score=0.486783 | reason=length_cap_reached
  - R4 | rank=25 | P3KEx5uCaRSiG2x2 | indie rock       | score=0.481406 | reason=length_cap_reached
  - R4 | rank=26 | 9CHzAeSHv9tWaIXW | electronic       | score=0.468893 | reason=length_cap_reached
  - R4 | rank=27 | zFFaxVMVqVtQMaRB | hard rock        | score=0.463347 | reason=length_cap_reached
  - R4 | rank=28 | axdv4kGugNPl0G69 | alternative rock | score=0.45615  | reason=length_cap_reached
  - R4 | rank=29 | ZroyniZj5TmQTEeg | pop              | score=0.426352 | reason=length_cap_reached
  - R4 | rank=30 | JdKYM8BZEjL8VmSe | pop punk         | score=0.408465 | reason=length_cap_reached
  - R4 | rank=31 | QhQahljQAwJIBXvA | electronic       | score=0.403581 | reason=length_cap_reached
  - R4 | rank=32 | VUwJpQjeH7lOujed | hard rock        | score=0.368217 | reason=length_cap_reached
  - R4 | rank=33 | t69cOklpskwuIzkN | hard rock        | score=0.359287 | reason=length_cap_reached
  - R4 | rank=34 | jmq9rFLdkgwkaqyV | electronic       | score=0.349015 | reason=length_cap_reached
  - R4 | rank=35 | 9z2L8uD3GjNoXSRs | pop              | score=0.341677 | reason=length_cap_reached
  - R4 | rank=36 | itO50SbHqR6xiK3t | hip hop          | score=0.338313 | reason=length_cap_reached
  - R4 | rank=37 | APCOA8vqweV4WMee | electronic       | score=0.329266 | reason=length_cap_reached
  - R4 | rank=38 | zs8HfoDBJLYAtDrU | pop              | score=0.316399 | reason=length_cap_reached
  - R4 | rank=39 | IYI6RFvYIFFg9Mi7 | trip hop         | score=0.315058 | reason=length_cap_reached
  - R4 | rank=40 | VjL805nl0oHFzqSt | hard rock        | score=0.313157 | reason=length_cap_reached
  - R4 | rank=41 | eNKt8Nt4qTpVT935 | hard rock        | score=0.296153 | reason=length_cap_reached
  - R4 | rank=42 | 9EERk7bPIn9HNBvE | pop              | score=0.20486  | reason=length_cap_reached
- Score gap analysis:
  - The jump from rank=2 (0.702) to rank=3 (0.669) reflects the first R3 block (pos 3 instead received the rank=7 indie pop track)
  - The largest score displacement is on the indie rock cluster ranks 3–6 and 10–17 — 9 indie rock tracks were excluded through R2 and R3 alone
  - Lowest included score (0.510916 at pos 10) sits between rank=19 (folk) and rank=20 (indie rock, cut by R4); the folk track entered only because the indie-dominant ranks ahead of it were already capped

### Issues And Limits
- failures_or_anomalies: none.
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: with a synthetic preference-heavy stub, all retained candidates already score above the 0.35 threshold, so R1 was inactive this run; on real corpus data with wider genre and score spread, R1 would become a meaningful filter.

### Thesis Traceability
- chapter4_relevance: provides direct pipeline evidence for the playlist assembly stage; demonstrates that rule-based diversity constraints produce genre variety rather than top-N pure similarity lists.
- chapter5_relevance: supports discussion of rule brittleness risk and the trade-off between strict genre caps and user preference coherence.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-PLAYLIST-001`.

### Next Action
- immediate_follow_up: start `BL-008` transparency outputs — attach per-track explanation payloads derived from the BL-006 and BL-007 artifacts.
- backlog_status_recommendation: mark `BL-007` done.

---

## EXP-010
- date: 2026-03-19
- backlog_link: `BL-008`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-EXPLAIN-001`

### Objective
- Generate per-track explanation payloads for every track in the BL-007 playlist, derived directly from BL-006 scoring and BL-007 assembly artifacts, with no new scoring logic applied.

### Scope Check
- In-scope confirmation: yes, BL-008 is the transparency output P0 requirement.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
  - `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json`
  - `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_trace.csv`
- config_or_parameters:
  - 9 named scoring components: bpm, danceability, loudness, V_mean (valence), A_mean (arousal), D_mean (dominance), lead_genre, genre_overlap, tag_overlap
  - top_contributors = top 3 by weighted contribution value
  - why_selected sentence derived from top 3 contributors and playlist position
- code_or_script_path: `07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py`
- dependency assumptions: Python stdlib only; BL-006 and BL-007 artifacts must already exist.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_payloads.json`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_summary.json`
- success_condition: one payload per playlist track (10 total); each payload contains score breakdown, top contributors, assembly context, and why_selected sentence; summary records input hashes and top-contributor distribution.

### Run Record
- command_or_execution_method: CLI via `python build_bl008_explanation_payloads.py`
- run_id: `BL008-EXPLAIN-20260319-052607`
- start_state_summary: BL-008 had no implementation script or transparency outputs.
- end_state_summary: explainer script implemented; both explanation artifacts created successfully.

### Execution Trace
- Explanation path:
  - load BL-006 score rows indexed by track_id
  - load BL-007 playlist tracks (10 entries)
  - load BL-007 assembly trace indexed by track_id
  - for each playlist track: build score_breakdown from 9 components, rank top 3 by contribution, generate why_selected sentence, record assembly_context
- Output footprint:
  - `bl008_explanation_payloads.json=29200 bytes`
  - `bl008_explanation_summary.json=748 bytes`
- Run timestamp from artifact:
  - `generated_at_utc=2026-03-19T05:26:07Z`

### Results
- outcome_summary: BL-008 completed successfully. All 10 playlist tracks have transparent, machine-readable explanation payloads with a reconstructable score breakdown and a human-readable selection sentence.
- key_metrics:
  - `playlist_track_count=10`
  - `top_contributor_distribution.lead_genre_match=5`
  - `top_contributor_distribution.tag_overlap=2`
  - `top_contributor_distribution.valence=3`
  - input hash check: `bl006_scored_candidates.csv` hash matches EXP-008 record
  - input hash check: `bl007_playlist.json` hash matches EXP-009 record
  - input hash check: `bl007_assembly_trace.csv` hash matches EXP-009 record
  - `sha256.bl008_explanation_payloads.json=C9AA6D930D11295E458C6C5B516AE9FFDF8AD2136E6057AD8A181C1BC0B50F24`
  - `sha256.bl008_explanation_summary.json=49CAC879496E1AEEA4821BF97A5FE09FE30FC16DEDBA629E4DD3861A7D0A431E`
- deterministic_repeat_checked: no
- output_paths:
  - `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_payloads.json`
  - `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_summary.json`

### Validation Checks
- Payload completeness check:
  - 10 payloads produced, one per playlist track — count matches `playlist_track_count` in BL-007
  - every payload contains `why_selected`, `top_score_contributors` (3 entries), `score_breakdown` (9 entries), `assembly_context`
- Fidelity check (pos 1 spot-check — `jPv1Tj4Mgo4l2Oue`):
  - `final_score=0.724318` matches BL-006 row rank=1
  - `top_score_contributors[0]=Lead genre match (similarity=1.0, contribution=0.12)`
  - `top_score_contributors[1]=Valence (similarity=0.972885, contribution=0.116746)`
  - `top_score_contributors[2]=Tag overlap (similarity=0.71644, contribution=0.11463)`
  - sum of all 9 contributions = 0.724318 (reconstructable to BL-006 final_score)
  - `assembly_context.admission_rule=Admitted on first evaluation`
  - `why_selected=Selected at playlist position 1 (score 0.7243) because it strongly matches the preference profile on Lead genre match, Valence, Tag overlap. Lead genre is 'indie rock'.`
- Top-contributor pattern:
  - Lead genre match is the dominant top contributor (5 of 10 tracks) — confirms semantic profile alignment is the primary selection signal
  - Valence is the top contributor for 3 tracks (pos 7, 9, 10) — mostly the outlier genre entries (alternative rock, pop, folk) where lead genre match was weaker
  - Tag overlap tops 2 tracks (pos 3, 6) — both indie pop entries where genre match was partial but tag coverage was strong
- Input hash integrity:
  - BL-006 input hash in summary matches EXP-008 `sha256.bl006_scored_candidates.csv`
  - BL-007 playlist hash in summary matches EXP-009 `sha256.bl007_playlist.json`
  - BL-007 trace hash in summary matches EXP-009 `sha256.bl007_assembly_trace.csv`

### Full Per-Track Top Contributor Summary
- pos=1  jPv1Tj4Mgo4l2Oue  indie rock        top=Lead genre match  (0.12)
- pos=2  POdgTSLBnoFJaj2x  indie rock        top=Lead genre match  (0.12)
- pos=3  yUa5uu5wFCGwl2PK  indie pop         top=Tag overlap       (0.116289)
- pos=4  j8qrlsfqWAPqzqD9  indie rock        top=Lead genre match  (0.12)
- pos=5  8keAhBJumHlc8qe9  indie rock        top=Lead genre match  (0.12)
- pos=6  Nyb0YqqyaSvWThIG  indie pop         top=Tag overlap       (0.133746)
- pos=7  0X9aluHlz6iKWBMR  alternative rock  top=Valence           (0.110234)
- pos=8  ql2191d6uNCVM932  alternative rock  top=Lead genre match  (0.107699)
- pos=9  9ZtfD8gBZXonrJKX  pop               top=Valence           (0.095868)
- pos=10 PZEgbQhTHMMrKRLv  folk              top=Valence           (0.11241)

### Issues And Limits
- failures_or_anomalies: none.
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: `why_selected` sentences are template-generated from component labels; they are accurate but not yet natural prose. A future refinement (BL-008+) could produce richer text, but this is out of MVP scope.

### Thesis Traceability
- chapter4_relevance: provides direct evidence for the transparency requirement — every recommended track has an auditable score breakdown and a human-readable selection rationale derived from pipeline artifacts.
- chapter5_relevance: supports discussion of transparency-by-design vs post-hoc explanation; the fact that scores are fully reconstructable from stored component contributions is the key transparency claim.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-EXPLAIN-001`.

### Next Action
- immediate_follow_up: start `BL-009` observability logging — structured per-run metadata capturing config, seed params, input hashes, and run IDs in a single canonical log schema.
- backlog_status_recommendation: mark `BL-008` done.

---

## EXP-011
- date: 2026-03-21
- backlog_link: `BL-009`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-OBS-001`

### Objective
- Build a canonical run-level observability layer that records configuration, stage diagnostics, deferred-stage status, exclusions, and artifact hashes for the active bootstrap pipeline from BL-017 through BL-008.

### Scope Check
- In-scope confirmation: yes, BL-009 is the P0 observability evidence requirement.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/data_layer/outputs/onion_join_coverage_report.json`
  - `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`
  - `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
  - `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
  - `07_implementation/implementation_notes/profile/outputs/bl004_preference_profile.json`
  - `07_implementation/implementation_notes/profile/outputs/bl004_profile_summary.json`
  - `07_implementation/implementation_notes/profile/outputs/bl004_seed_trace.csv`
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_diagnostics.json`
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_candidate_decisions.csv`
  - `07_implementation/implementation_notes/retrieval/outputs/bl005_filtered_candidates.csv`
  - `07_implementation/implementation_notes/scoring/outputs/bl006_score_summary.json`
  - `07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv`
  - `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_report.json`
  - `07_implementation/implementation_notes/playlist/outputs/bl007_assembly_trace.csv`
  - `07_implementation/implementation_notes/playlist/outputs/bl007_playlist.json`
  - `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_summary.json`
  - `07_implementation/implementation_notes/transparency/outputs/bl008_explanation_payloads.json`
- config_or_parameters:
  - bootstrap mode = `true`
  - required top-level sections: `run_metadata`, `run_config`, `ingestion_alignment_diagnostics`, `stage_diagnostics`, `exclusion_diagnostics`, `output_artifacts`
  - `dataset_version` = deterministic combined hash of bootstrap data components
  - `pipeline_version` = deterministic combined hash of participating stage scripts
  - representative exclusion samples capped per reason group
- code_or_script_path: `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`
- dependency assumptions: Python stdlib only; all upstream BL-017 to BL-008 artifacts must exist.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/observability/outputs/bl009_run_index.csv`
- success_condition: one canonical run log is produced with complete required sections, linked upstream run ids, concrete artifact hashes, deferred BL-001 to BL-003 status, and a compact CSV index row for quick replay lookup.

### Run Record
- command_or_execution_method: CLI via `python 07_implementation/implementation_notes/observability/build_bl009_observability_log.py`
- run_id: `BL009-OBSERVE-20260320-232943`
- start_state_summary: BL-009 had no observability implementation, no run-level audit log, and no run index for the bootstrap artifact chain.
- end_state_summary: logger script implemented; run log and run index generated successfully.

### Execution Trace
- Observability build path:
  - load BL-017 coverage report and BL-016 bootstrap manifest
  - load BL-004 to BL-008 summary artifacts and trace files
  - compute combined `dataset_version` from bootstrap data-component hashes
  - compute combined `pipeline_version` from BL-017 to BL-009 script hashes
  - record BL-001 to BL-003 as `deferred_bootstrap_mode` with surrogate inputs
  - extract representative retrieval and assembly exclusion examples
  - validate required top-level sections before writing final JSON
  - write canonical run log JSON and one-row CSV index
- Output footprint:
  - `bl009_run_observability_log.json=23069 bytes`
  - `bl009_run_index.csv=830 bytes`
- Run timestamp from artifact:
  - `generated_at_utc=2026-03-20T23:29:43Z`

### Results
- outcome_summary: BL-009 completed successfully. The bootstrap pipeline now has a single structured observability log that ties together configs, diagnostics, exclusions, upstream run ids, and final output hashes across BL-017 to BL-008.
- key_metrics:
  - `bootstrap_mode=true`
  - `dataset_version=2648A3237AA62F9E4C667C93178D482A5ACCDA0461299472E4FC1697786A993B`
  - `pipeline_version=4863D9868F15E220FD329B8B68248E95C8A7DB689E9353D2E60218713541DD9F`
  - `upstream_run_count=5` (`BL-004` to `BL-008`)
  - `kept_candidates=42`
  - `candidates_scored=42`
  - `playlist_length=10`
  - `explanation_count=10`
  - `retrieval.rejected_non_seed_candidates=7`
  - `assembly.tracks_excluded=32`
  - `deferred_stage_count=3` (`BL-001`, `BL-002`, `BL-003`)
  - `sha256.bl009_run_observability_log.json=AD3C1E632EADA20696B0B26AE01D4971071C3A76F7560DCFF84970930E1B38C4`
  - `sha256.bl009_run_index.csv=EC5D3D72B1DE5D483E7EAA3C614075FD5CD2994C5304DC60520BFB7390A01811`
- deterministic_repeat_checked: no
- output_paths:
  - `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`
  - `07_implementation/implementation_notes/observability/outputs/bl009_run_index.csv`

### Validation Checks
- Structure check:
  - required top-level sections present: `run_metadata`, `run_config`, `ingestion_alignment_diagnostics`, `stage_diagnostics`, `exclusion_diagnostics`, `output_artifacts`
  - ingestion/alignment state explicitly recorded as `deferred_bootstrap_mode`
- Linkage check:
  - BL-004 through BL-008 run ids in the log match upstream artifact run ids
  - `playlist_sha256` in the CSV index matches BL-007 logged hash `8B53B03D23F241EB102AD48E98395C34140356BCE3640348F2AF4C7EC44009FB`
  - `explanation_payloads_sha256` in the CSV index matches BL-008 logged hash `C9AA6D930D11295E458C6C5B516AE9FFDF8AD2136E6057AD8A181C1BC0B50F24`
  - `observability_log_sha256` stored in the CSV index matches the actual JSON log hash
- Diagnostic usefulness check:
  - retrieval exclusion summary includes sample non-seed rejects with `decision_reason`
  - assembly exclusion summary includes grouped rule samples and first `length_cap_reached` boundary
  - final output section links primary outputs and deep trace artifacts in one record

### Issues And Limits
- failures_or_anomalies: none.
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: BL-009 logs the current bootstrap pipeline only; because BL-001 to BL-003 are deferred, ingestion and alignment diagnostics are recorded as explicit non-applicable placeholders rather than live execution telemetry.

### Thesis Traceability
- chapter4_relevance: provides direct observability evidence for trace completeness, diagnostic usefulness, and replay support claims in the evaluation chapter.
- chapter5_relevance: supports limitation discussion about bootstrap-mode observability covering deferred ingestion/alignment stages by declaration rather than execution.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-OBS-001`.

### Next Action
- immediate_follow_up: start `BL-010` reproducibility tests and replay selected stages to verify hash stability.
- backlog_status_recommendation: mark `BL-009` done.

---

## EXP-012
- date: 2026-03-21
- backlog_link: `BL-010`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-REPRO-001`

### Objective
- Verify that the active bootstrap pipeline produces identical stable outputs under identical inputs and configuration across three full replays of BL-004 through BL-009.

### Scope Check
- In-scope confirmation: yes, BL-010 is the P0 reproducibility evidence requirement.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
  - `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
  - `07_implementation/implementation_notes/test_assets/bl016_asset_manifest.json`
  - `07_implementation/implementation_notes/data_layer/outputs/onion_join_coverage_report.json`
- config_or_parameters:
  - replay count = `3`
  - bootstrap mode = `true`
  - stage order = `BL-004` -> `BL-005` -> `BL-006` -> `BL-007` -> `BL-008` -> `BL-009`
  - stable comparison artifacts = `profile_semantic_hash`, `seed_trace_hash`, `filtered_candidates_hash`, `candidate_decisions_hash`, `ranked_output_hash`, `assembly_trace_hash`, `playlist_output_hash`, `explanation_output_hash`, `observability_output_hash`
  - volatile raw artifacts tracked separately = `bl007_playlist.json`, `bl008_explanation_payloads.json`, `bl009_run_observability_log.json`
- code_or_script_path: `07_implementation/implementation_notes/reproducibility/run_bl010_reproducibility_check.py`
- dependency assumptions: Python stdlib only; BL-016 and BL-017 inputs already present; BL-004 to BL-009 stage scripts executable from repo root.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_run_matrix.csv`
  - `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_config_snapshot.json`
  - archived replay directories `07_implementation/implementation_notes/reproducibility/outputs/replay_01/`, `replay_02/`, `replay_03/`
- success_condition: all three replays produce identical stable output hashes and matching playlist/explanation content under one fixed config hash, while any raw-hash variation caused by run metadata is explicitly recorded.

### Run Record
- command_or_execution_method: CLI via `python 07_implementation/implementation_notes/reproducibility/run_bl010_reproducibility_check.py`
- run_id: `BL010-REPRO-20260320-233937`
- start_state_summary: BL-010 had no reproducibility runner, no replay matrix, and no normalized comparison layer for timestamped BL-007 to BL-009 artifacts.
- end_state_summary: replay runner implemented; stage run-id precision hardened; three archived replays completed; stable hashes matched across all replays.

### Execution Trace
- Initial BL-010 implementation:
  - added replay runner that executes BL-004 to BL-009 three times
  - archives each replay output set under `replay_01/` to `replay_03/`
  - computes a config snapshot and stable output fingerprints for replay comparison
- Defect discovered during validation:
  - BL-004 to BL-009 run ids used second-level precision and collided under fast replay
  - observability fingerprint initially leaked a volatile `elapsed_seconds` field from BL-004 profile diagnostics
- Corrections applied before final evidence:
  - increased BL-004 to BL-009 run-id precision to include microseconds
  - tightened BL-010 observability normalization to exclude variable timing fields
  - reran BL-010 to produce the final passing report
- Final replay path:
  - replay 1: `BL004-PROFILE-20260320-233937-128253` -> `BL009-OBSERVE-20260320-233937-515683`
  - replay 2: `BL004-PROFILE-20260320-233937-625219` -> `BL009-OBSERVE-20260320-233938-006085`
  - replay 3: `BL004-PROFILE-20260320-233938-114198` -> `BL009-OBSERVE-20260320-233938-519108`

### Results
- outcome_summary: BL-010 completed successfully. Three identical replays produced matching stable hashes for ranked candidates, playlist content, explanation content, and normalized observability content under one fixed config hash. Raw JSON file hashes for BL-007 to BL-009 differed as expected because those artifacts embed run-specific metadata.
- key_metrics:
  - `deterministic_match=true`
  - `replay_count=3`
  - `config_hash=B259CD10A428DD8DC5CF2EA8255807D28B6E771BDEDC24C32733982A6D47386F`
  - `ranked_output_hash=BF9AB8A4FE27596276F8B1868FC1246BCA4B04B6315DFBB6FEF673DDF53E1AA2`
  - `playlist_output_hash=589920D4EB9C862F010F9C516BF7199D187F82A88265ACCC0B26FFD03E85A651`
  - `explanation_output_hash=568D6099CF8D7B035B67309143EF783E54B102505909A0EE2D01E22ECF6B4161`
  - `observability_output_hash=FA765EFEAEB7A0B49AC3DF3DC87A4DF8504FCF866731AE1F6872820CB2CAC2E0`
  - `dataset_version=2648A3237AA62F9E4C667C93178D482A5ACCDA0461299472E4FC1697786A993B`
  - `pipeline_version=E622A5784035EAEA845636DFA9C9991A8096D39ECCE18D9DBFA071832158FCB8`
  - `unique_stage_run_ids=18`
  - `raw_playlist_hash_match=false`
  - `raw_explanation_hash_match=false`
  - `raw_observability_hash_match=false`
  - `bl010_reproducibility_report.json=34044 bytes`
  - `bl010_reproducibility_run_matrix.csv=2929 bytes`
  - `bl010_reproducibility_config_snapshot.json=4743 bytes`
  - `sha256.bl010_reproducibility_report.json=E222B832E97CE1FA1C8EC2C76528C583E7CFFDBC301E1D849CB0522B7350678C`
  - `sha256.bl010_reproducibility_run_matrix.csv=2458924F133CE1363FB8D9BD95448402650D160339F39FDE732F18682BB6B594`
  - `sha256.bl010_reproducibility_config_snapshot.json=0A3737348AAE95960D52AF0671A62530A2CDAC3B148A75DDB2DBD8354315428F`
- deterministic_repeat_checked: yes
- output_paths:
  - `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json`
  - `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_run_matrix.csv`
  - `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_config_snapshot.json`

### Validation Checks
- Stable replay check:
  - all three `ranked_output_hash` values matched
  - all three `playlist_output_hash` values matched
  - all three `explanation_output_hash` values matched
  - all three `observability_output_hash` values matched after volatile timing fields were removed from the normalization layer
- Content identity check:
  - playlist track-id order matched across all three replays
  - explanation track-id order matched across all three replays
  - `dataset_version` and `pipeline_version` matched across all three replays
- Identifier integrity check:
  - all stage run ids were unique after increasing BL-004 to BL-009 run-id precision to microseconds
- Metadata volatility check:
  - raw BL-007 playlist hash, BL-008 payload hash, and BL-009 log hash varied across replays as expected because those files embed run ids, timestamps, elapsed seconds, and upstream run linkage

### Issues And Limits
- failures_or_anomalies:
  - initial BL-010 replay revealed second-level run-id collisions in BL-004 to BL-009
  - initial observability normalization incorrectly included a volatile elapsed-seconds field
- likely_cause:
  - stage scripts used second-resolution timestamps for run ids
  - normalized observability comparison included one timing field that does not represent semantic output differences
- bounded_mvp_limitation_or_bug: raw file hash equality is not a valid replay criterion for BL-007 to BL-009 because those artifacts intentionally record per-run metadata. BL-010 therefore evaluates deterministic replay using stable content fingerprints and documents raw-hash variation separately.

### Thesis Traceability
- chapter4_relevance: provides the direct reproducibility evidence required for `EP-REPRO-001`, including fixed-input replay, stable output hashes, and a documented reason why raw metadata hashes differ for later-stage JSON artifacts.
- chapter5_relevance: supports a limitation discussion distinguishing semantic determinism from expected per-run metadata variability in audit-oriented outputs.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-REPRO-001`.

### Next Action
- immediate_follow_up: start `BL-011` controllability tests using the now-verified replay baseline and fixed config snapshot.
- backlog_status_recommendation: mark `BL-010` done.

---

## EXP-013
- date: 2026-03-21
- backlog_link: `BL-011`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-005`, `TC-006`, `TC-007`

### Objective
- Execute BL-011 controllability tests as one-factor-at-a-time sensitivity checks anchored to the BL-010 fixed baseline.

### Scope Check
- In-scope confirmation: yes, BL-011 is the P0 controllability evidence requirement in the locked MVP evaluation plan.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/implementation_notes/test_assets/bl016_synthetic_aligned_events.jsonl`
  - `07_implementation/implementation_notes/test_assets/bl016_candidate_stub.csv`
  - `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_config_snapshot.json`
  - current BL-004 to BL-009 stage scripts and baseline outputs
- config_or_parameters:
  - one-factor-at-a-time variants for `EP-CTRL-001`, `EP-CTRL-002`, and `EP-CTRL-003`
  - baseline fixed from BL-010 config snapshot
  - scenario outputs archived under `07_implementation/implementation_notes/controllability/outputs/`
- code_or_script_path: `07_implementation/implementation_notes/controllability/run_bl011_controllability_check.py`
- dependency assumptions: Python stdlib only; BL-010 baseline artifacts remain valid and stage semantics remain unchanged outside targeted parameter overrides.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_report.json`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_run_matrix.csv`
  - per-scenario archived outputs under `07_implementation/implementation_notes/controllability/outputs/scenarios/`
  - optional config snapshot for the BL-011 scenario plan
- success_condition: each targeted control change produces an interpretable downstream effect while non-target parameters remain fixed and all scenario differences remain traceable to profile, retrieval, scoring, or playlist evidence.

### Run Record
- command_or_execution_method: CLI via `python 07_implementation/implementation_notes/controllability/run_bl011_controllability_check.py`
- run_id: `BL011-CTRL-20260320-235345`
- start_state_summary: BL-011 has no controllability runner, no comparative run matrix, and no archived parameter-sensitivity evidence.
- end_state_summary: controllability runner implemented; baseline plus four archived OFAT scenarios executed successfully; each scenario repeated twice with matching stable hashes.

### Results
- outcome_summary: BL-011 completed successfully. All controllability scenarios produced deterministic repeat-consistent outputs, and each targeted control generated an interpretable downstream effect aligned with its intended mechanism path.
- key_metrics:
  - `all_scenarios_repeat_consistent=true`
  - `all_variant_shifts_observable=true`
  - `all_variant_directions_met=true`
  - `baseline_config_hash=B259CD10A428DD8DC5CF2EA8255807D28B6E771BDEDC24C32733982A6D47386F`
  - `baseline_candidate_pool_size=42`
  - `baseline_ranked_output_hash=BF9AB8A4FE27596276F8B1868FC1246BCA4B04B6315DFBB6FEF673DDF53E1AA2`
  - `baseline_playlist_output_hash=589920D4EB9C862F010F9C516BF7199D187F82A88265ACCC0B26FFD03E85A651`
  - `EP-CTRL-001.no_influence_tracks.candidate_pool_size_delta=5`
  - `EP-CTRL-001.no_influence_tracks.top10_overlap_count=9`
  - `EP-CTRL-001.no_influence_tracks.playlist_overlap_count=7`
  - `EP-CTRL-001.no_influence_tracks.mean_abs_rank_delta=2.619`
  - `EP-CTRL-002.valence_weight_up.candidate_pool_size_delta=0`
  - `EP-CTRL-002.valence_weight_up.top10_overlap_count=9`
  - `EP-CTRL-002.valence_weight_up.playlist_overlap_count=10`
  - `EP-CTRL-002.valence_weight_up.mean_abs_rank_delta=1.048`
  - `EP-CTRL-002.valence_weight_up.mean_component_delta.V_mean=0.038908`
  - `EP-CTRL-003.stricter_thresholds.candidate_pool_size_delta=-2`
  - `EP-CTRL-003.stricter_thresholds.mean_abs_rank_delta=0.25`
  - `EP-CTRL-003.looser_thresholds.candidate_pool_size_delta=2`
  - `EP-CTRL-003.looser_thresholds.mean_abs_rank_delta=0.024`
  - `bl011_controllability_report.json=47572 bytes`
  - `bl011_controllability_run_matrix.csv=2467 bytes`
  - `bl011_controllability_config_snapshot.json=18025 bytes`
  - `sha256.bl011_controllability_report.json=0F74409402ED8DA2A948963980563A6FF8AD5F928DB448451F463B03BD1D1B5E`
  - `sha256.bl011_controllability_run_matrix.csv=74042438462C1E84389868425C5080B03E8236D774FF6F9429FAECF99AAAD451`
  - `sha256.bl011_controllability_config_snapshot.json=B92CDB560D9600E0059E66A72B433C0D454F90A496E7CB87AB308C0D3A9725C1`
- deterministic_repeat_checked: yes
- output_paths:
  - `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_report.json`
  - `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_run_matrix.csv`
  - `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_config_snapshot.json`
  - `07_implementation/implementation_notes/controllability/outputs/scenarios/`

### Issues And Limits
- failures_or_anomalies:
  - initial BL-011 runner incorrectly treated per-run profile metadata as part of the repeat-consistency fingerprint, producing a false `bounded-risk` result on the first execution
- likely_cause:
  - the first BL-011 profile semantic hash still included volatile run-level metadata in a summary block, which is not valid for deterministic repeat checks
- bounded_mvp_limitation_or_bug: threshold sensitivity is clearly visible at candidate-pool and low-level rank positions, but under the current synthetic candidate stub it does not change the final 10-track playlist membership. This is an accepted limitation of the preference-heavy bootstrap data rather than a control-path defect.

### Thesis Traceability
- chapter4_relevance: provides the direct controllability evidence required for `EP-CTRL-001`, `EP-CTRL-002`, and `EP-CTRL-003`, including profile shifts, rank shifts, candidate-pool changes, and playlist overlap outcomes under one-factor-at-a-time variation.
- chapter5_relevance: supports the limitations discussion that some controls show strong ranking/composition effects (`EP-CTRL-001`, `EP-CTRL-002`) while threshold changes remain weaker at the final playlist layer under the synthetic bootstrap corpus.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with final `TC-005`, `TC-006`, and `TC-007` results.

### Next Action
- immediate_follow_up: start `BL-012` limitations documentation using the BL-010 and BL-011 findings as the current evidence base.
- backlog_status_recommendation: mark `BL-011` done.

---

## EXP-014
- date: 2026-03-21
- backlog_link: `BL-012`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-LIMIT-001`

### Objective
- Document limitations and observed failure modes from completed BL-010 and BL-011 outcomes, and integrate those limits into both foundation and thesis-writing artifacts.

### Scope Check
- In-scope confirmation: yes, BL-012 is the final P0 documentation step for converting test outcomes into explicit validity boundaries.
- Protected items affected? no

### Inputs
- source_data:
  - `07_implementation/experiment_log.md` (`EXP-012`, `EXP-013`)
  - `07_implementation/test_notes.md` (`TC-REPRO-001`, `TC-005`, `TC-006`, `TC-007`)
  - `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json`
  - `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_report.json`
- config_or_parameters:
  - synthesis rule: include only limitations grounded in executed evidence or locked scope constraints
  - wording rule: each limitation must state its effect on interpretation
- code_or_script_path: n/a (documentation-synthesis run)
- dependency assumptions: BL-010 and BL-011 evidence remains valid and is not modified during BL-012.

### Expected Evidence
- primary_output_artifact: `02_foundation/limitations.md`
- secondary_output_artifacts:
  - `08_writing/chapter5.md` (Sections 5.4 and 5.5)
  - `07_implementation/backlog.md` BL-012 done status
  - `00_admin/change_log.md` BL-012 governance entry
- success_condition: documented limitations/failure modes are consistent with BL-010 and BL-011 results and are reflected in both foundation and writing artifacts.

### Run Record
- command_or_execution_method: structured manual synthesis and traceability update across governance files
- run_id: `BL012-LIMIT-20260321`
- start_state_summary: BL-012 marked todo; limitations text existed but did not explicitly capture BL-010/BL-011 failure-mode details.
- end_state_summary: BL-012 marked done; evidence-grounded limitation and failure-mode synthesis applied to foundation and Chapter 5.

### Results
- outcome_summary: BL-012 completed successfully. The thesis now documents observed replay/control failure modes (run-id collisions, volatile metadata in repeat checks, muted playlist-level threshold effects) and clarifies how they bound interpretation of results.
- key_metrics:
  - `limitations_entries_updated=7`
  - `failure_modes_logged=3`
  - `chapter5_sections_updated=2`
  - `backlog_item_transition=BL-012:todo->done`
- deterministic_repeat_checked: no
- output_paths:
  - `02_foundation/limitations.md`
  - `08_writing/chapter5.md`
  - `07_implementation/backlog.md`
  - `00_admin/change_log.md`

### Issues And Limits
- failures_or_anomalies: none in the BL-012 documentation run.
- likely_cause: n/a
- bounded_mvp_limitation_or_bug: BL-012 remains a documentation-stage synthesis and does not itself add new runtime experiments.

### Thesis Traceability
- chapter4_relevance: consolidates how BL-010 and BL-011 experimental behavior should be interpreted when cited in results discussion.
- chapter5_relevance: directly updates limitation framing and future-work targeting using observed failure modes rather than generic caveats.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-LIMIT-001`.

### Next Action
- immediate_follow_up: begin `BL-013` lightweight CLI entrypoint and keep the same evidence-first logging pattern.
- backlog_status_recommendation: mark `BL-012` done.

---

## EXP-015
- date: 2026-03-21
- backlog_link: `BL-013`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-CLI-001`

### Objective
- Add a lightweight repeatable CLI/script entrypoint that executes the current bootstrap pipeline stages (`BL-004` through `BL-009`) in one command and writes run-command documentation.

### Scope Check
- In-scope confirmation: yes, BL-013 is a P1 quality-improvement item that strengthens repeatable execution and evidence reuse.
- Protected items affected? no

### Inputs
- source_data:
  - existing stage scripts under `07_implementation/implementation_notes/profile/`, `retrieval/`, `scoring/`, `playlist/`, `transparency/`, and `observability/`
  - current bootstrap assets from `07_implementation/implementation_notes/test_assets/`
- config_or_parameters:
  - default stage order: BL-004 -> BL-005 -> BL-006 -> BL-007 -> BL-008 -> BL-009
  - fail-fast orchestration with optional stage subset support
- code_or_script_path:
  - planned new orchestrator: `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`
  - planned run-command documentation: `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`
- dependency assumptions: Python runtime available; required upstream scripts and bootstrap inputs exist.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`
  - one orchestration run summary under `07_implementation/implementation_notes/entrypoint/outputs/`
- success_condition: a single command executes configured stages in order, stops on stage failure, and emits a machine-readable run summary.

### Run Record
- command_or_execution_method: CLI via `python 07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py` (executed twice)
- run_id: `BL013-ENTRYPOINT-20260321-001004-434656`
- start_state_summary: BL-013 changed to in-progress; no unified pipeline entrypoint exists yet.
- end_state_summary: new lightweight orchestrator implemented; both execution runs completed all six stages (`BL-004` to `BL-009`) with zero failures and matching stable artifact hashes.

### Results
- outcome_summary: BL-013 completed successfully. A thin orchestration runner now executes the bootstrap pipeline in one command, writes per-stage execution details, and supports repeatability verification via stable artifact hashes in summary output.
- key_metrics:
  - `executed_stage_count=6`
  - `failed_stage_count=0`
  - `run_1_id=BL013-ENTRYPOINT-20260321-000958-043140`
  - `run_2_id=BL013-ENTRYPOINT-20260321-001004-434656`
  - `stable_hash_match.bl004_seed_trace=yes`
  - `stable_hash_match.bl005_filtered_candidates=yes`
  - `stable_hash_match.bl005_candidate_decisions=yes`
  - `stable_hash_match.bl006_scored_candidates=yes`
  - `stable_hash_match.bl007_assembly_trace=yes`
  - `sha256.run_bl013_pipeline_entrypoint.py=D3846BA755B54AA9AE38EE659C2A28D4E8A51EA774AC708D1DE58D61EDF283B5`
  - `sha256.bl013_run_command.md=6F9F0810F651EBB363CB28D3A9189DF3EFFA8CC0B8DF0A304A7644644F888A5B`
  - `sha256.run_summary_1=56585FF293F39C088F0700ACA5B7573E4CF37A9399FBA0B04D24E34F127B1DD2`
  - `sha256.run_summary_2=E98D5B905546B3D31CC23A5E1E99BB40487FD4DAE36AD5E668F76730811B5CB7`
- deterministic_repeat_checked: yes
- output_paths:
  - `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`
  - `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`
  - `07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_BL013-ENTRYPOINT-20260321-000958-043140.json`
  - `07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_BL013-ENTRYPOINT-20260321-001004-434656.json`
  - `07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_latest.json`

### Issues And Limits
- failures_or_anomalies:
  - first terminal command attempted an unnecessary `Set-Location thesis-main` from an already-correct working directory; command still executed and BL-013 run succeeded.
- likely_cause:
  - interactive shell cwd was already `.../thesis-main/thesis-main`.
- bounded_mvp_limitation_or_bug: BL-013 orchestrates existing stage scripts and does not add new recommendation logic; volatile-metadata JSON outputs (for example BL-007 to BL-009) can still differ by raw hash across runs by design.

### Thesis Traceability
- chapter4_relevance: improves reproducible execution procedure and evidence refresh workflow.
- chapter5_relevance: reduces operational friction but does not change interpretation boundaries.
- quality_control_files_to_update: `07_implementation/test_notes.md` updated with `TC-CLI-001`.

### Next Action
- immediate_follow_up: proceed to `BL-014` automated sanity checks for schema validation and deterministic hash verification.
- backlog_status_recommendation: mark `BL-013` done.

---

## EXP-016
- date: 2026-03-21
- backlog_link: `BL-019`
- owner: Timothy + AI
- status: pass
- related_test_id: `TC-DATASET-001`

### Objective
- Plan the BL-019 dataset-build workflow so DS-002 integration runs (`MSD subset + Last.fm tags + MusicBrainz mapping`) are deterministic, quality-gated, and directly reusable by downstream pipeline stages.

### Scope Check
- In-scope confirmation: yes, this is a planning and execution-readiness step for dataset refresh quality and repeatability.
- Protected items affected? no

### Inputs
- source_data:
  - `06_data_and_sources/ds_002_msd_information_sheet.md`
  - `06_data_and_sources/track_metadata.db`
  - `06_data_and_sources/millionsongsubset.tar.gz`
  - `06_data_and_sources/lastfm_subset.zip`
  - `06_data_and_sources/unique_tracks.txt`
  - `06_data_and_sources/unique_artists.txt`
- config_or_parameters:
  - planned quality gates: join coverage threshold, unmatched-track caps, null-rate caps for selected fields, stable row-count sanity window
  - planned determinism check: two integration runs with stable content hash comparison
  - planned Spotify alignment policy for DS-002: metadata-first on normalized title + artist with duration/release tie-breaks; no corpus-side ISRC dependency assumed
- code_or_script_path:
  - planned: `07_implementation/implementation_notes/data_layer/build_bl019_ds002_dataset.py`
- dependency assumptions: confirmed local assets can be joined deterministically on `track_id`; HDF5 extraction is now available in the environment (`h5py` installed); candidate-side track-level ISRC is not currently assumed.

### Expected Evidence
- primary_output_artifact: `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_integration_report.json`
- secondary_output_artifacts:
  - `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_dataset_manifest.json`
  - `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_quality_checks.csv`
- success_condition: planned workflow can be executed end to end with deterministic repeat behavior, explicit pass/fail quality gates, and clear join diagnostics across all three DS-002 sources.

### Run Record
- command_or_execution_method: `python 07_implementation/implementation_notes/data_layer/build_bl019_ds002_dataset.py` (two identical runs)
- run_1_id: `BL019-RUN1-20260321-014520`
- run_2_id: `BL019-RUN2-20260321-014922`
- start_state_summary: DS-002 corpus sources confirmed locally (10k HDF5, 1M SQLite rows, 9330 Last.fm JSON). Intersection join mode, streaming tar.gz extraction.
- end_state_summary: Both runs completed in ~27 seconds each. All output files written. Hashes stable across runs.

### Results
- outcome_summary: pass — intersection dataset built, all quality gates passed, determinism confirmed
- key_metrics:
  - rows: 9330 (intersection of 10000 HDF5 tracks ∩ 9330 Last.fm JSON records)
  - tracks_excluded: 670 (no Last.fm record)
  - metadata_coverage: 1.0 (100%)
  - lastfm_coverage: 1.0 (100%)
  - musicbrainz_coverage: 0.936 (8732 / 9330 have artist_mbid)
  - duration_null_rate: 0.0
  - tempo_null_rate: 0.0
  - loudness_null_rate: 0.0
  - key_null_rate: 0.0
  - mode_null_rate: 0.0
  - year_null_rate: 0.0
  - elapsed_seconds: 26.984
  - all_quality_gates_pass: true
- deterministic_repeat_checked: yes
  - run_1.csv_sha256: `b9c729a2b0fc1ab9e533ca5126402f4aff7c2b1ee8357a16e773a7837ad40b9f`
  - run_2.csv_sha256: `b9c729a2b0fc1ab9e533ca5126402f4aff7c2b1ee8357a16e773a7837ad40b9f`
  - run_1.quality_sha256: `e5600eb881788e7565ef95c343b0c418e525e362340bc8065c03f836af066540`
  - run_2.quality_sha256: `e5600eb881788e7565ef95c343b0c418e525e362340bc8065c03f836af066540`
  - hash_match: yes
- source_hashes_sha256:
  - metadata_db: `a29aff0bca1ccac8a9ba699ba6f4d41509a64ced6d6dcfd5573567244db375b4`
  - msd_tar: `2591a85c097a5d4ca6590f7496bdbf724e7fa5d36f79c8fcdf031219445a77b7`
  - lastfm_zip: `fdf41ed3741ea736947e870abadc65f91681768f362204454e428d0bf0cd6d5b`
- output_paths:
  - `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_integrated_candidate_dataset.csv`
  - `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_dataset_manifest.json`
  - `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_quality_checks.csv`
  - `07_implementation/implementation_notes/data_layer/outputs/bl019_ds002_integration_report.json`

### Issues And Limits
- failures_or_anomalies: source inspection showed no confirmed corpus-side track-level ISRC field and no confirmed track-level MusicBrainz recording ID in the currently available DS-002 assets.
- likely_cause: the currently available MSD helper data exposes `artist_mbid` but not a clean per-track MusicBrainz/ISRC layer.
- bounded_mvp_limitation_or_bug: Spotify-to-corpus alignment for DS-002 should currently be treated as metadata-first with duration/release tie-breaks unless a later enrichment step adds candidate-side ISRCs.

### Thesis Traceability
- chapter4_relevance: provides a dataset-refresh evidence path to support reproducibility and data-quality reporting.
- chapter5_relevance: provides bounded-risk documentation for cross-dataset join coverage, data drift, and schema-stability assumptions.
- quality_control_files_to_update: `07_implementation/test_notes.md` (when `TC-DATASET-001` is executed).

### Next Action
- immediate_follow_up: none — BL-019 complete. Dataset is ready for downstream pipeline stages.
- backlog_status_recommendation: mark `BL-019` done.


