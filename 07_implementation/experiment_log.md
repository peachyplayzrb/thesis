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


