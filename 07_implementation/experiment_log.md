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

