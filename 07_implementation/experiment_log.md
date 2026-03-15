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

## Minimal Example

## EXP-001
- date: 2026-03-15
- backlog_link: `BL-004`
- owner: Timothy
- status: planned
- related_test_id: `TC-PROFILE-001`

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

