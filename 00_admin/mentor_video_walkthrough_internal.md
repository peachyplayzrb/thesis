# Mentor Video Walkthrough Guide

This file is a calm, step-by-step script you can follow while recording a video for your mentor.

The goal is not to sound perfect. The goal is to show that:
- you know how to start the program,
- you understand the main files,
- you can explain the pipeline in order,
- and you can show where the outputs appear.

If you feel anxious, read this sentence out first:

"I am going to show the mentor review bundle, explain the main files, run the program from the wrapper entrypoint, and then show the generated outputs and validation report."

## 1. What To Have Open Before You Start Recording (Another Machine)

First do this in order:

1. Unzip `mentor_feedback_submission.zip`.
2. Open VS Code.
3. Click File -> Open Folder and select the unzipped `mentor_feedback_submission` folder.

Then open these inside VS Code before you start the video:

1. `README.md`
2. `main.py`
3. `config/profiles/run_config_ui013_tuning_v1f.json`
4. `src/`

Also keep these visible during the recording:

1. File Explorer open to the unzipped bundle folder.
2. VS Code integrated terminal open in that same folder.
3. VS Code terminal panel open so your mentor can see command output live.

## 2. Run It On Another Machine (One Section)

After opening the unzipped folder in VS Code, use the integrated terminal and run this exact sequence:

```powershell
Set-Location "C:\path\to\mentor_feedback_submission"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\main.py --validate-only
```

If your VS Code terminal already opens in the correct folder, you can skip `Set-Location`.

Why this is the best demo flow for another machine:
- it proves setup from scratch,
- it does not depend on your thesis repo root,
- and `--validate-only` still runs the pipeline first, then sanity checks at the end.

If you want to show a normal run without the final validation step, use:

```powershell
python .\main.py
```

If activation is blocked by policy on the other machine, use this once in that terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run:

```powershell
.\.venv\Scripts\Activate.ps1
```

You can read this out as:

"On any Windows machine: create a venv, activate it, install requirements, then run `python .\main.py --validate-only`."

## 3. A Good Recording Order

Use this order.

### Part A. Very short introduction

Say:

"This folder is the clean mentor-review bundle for my playlist generation artefact. It contains the runnable source code, one canonical configuration profile, the minimal dependencies, and the preserved input assets needed for the default run path."

### Part B. Show the top-level files

Click the bundle root and explain:

- `main.py`
  - This is the top-level wrapper entrypoint.
  - It resolves the config, sets up `PYTHONPATH`, runs the orchestration pipeline, and optionally runs validation.

- `README.md`
  - This explains the bundle purpose, setup, run commands, and what outputs are expected.

- `requirements.txt`
  - This is the minimal dependency list needed to run the bundle.

- `config/profiles/run_config_ui013_tuning_v1f.json`
  - This is the canonical run configuration used by default.
  - It defines scope, thresholds, weights, playlist rules, transparency controls, and observability settings.

- `src/`
  - This contains the implementation modules for each stage of the pipeline.

### Part C. Show `main.py`

Say this while pointing at `main.py`:

"The wrapper is intentionally simple. It chooses the canonical run config if I do not pass one manually, it runs BL-013 orchestration with seed refresh enabled, and if I add `--validate-only`, it then runs the BL-014 sanity checks. So this one file is the easiest way to demonstrate the full artefact."

Important details you can mention from the file:

- it defaults to `config/profiles/run_config_ui013_tuning_v1f.json`,
- it calls `src/orchestration/main.py`,
- it forces `--refresh-seed`,
- and validation is done by `src/quality/sanity_checks.py`.

### Part D. Show the config file

Open `config/profiles/run_config_ui013_tuning_v1f.json` and say:

"This file is the main control surface for the run. Instead of hardcoding behavior, the pipeline reads its thresholds and options from here."

Then point out these sections in order:

- `input_scope`
  - controls which Spotify-derived sources are included.

- `interaction_scope`
  - controls which interaction families are used.

- `influence_tracks`
  - allows manually important tracks to shape the profile.

- `seed_controls`
  - controls seed matching thresholds.

- `profile_controls`
  - controls top tag and genre extraction.

- `retrieval_controls`
  - controls candidate filtering behavior.

- `scoring_controls`
  - controls the weighted scoring model.

- `assembly_controls`
  - controls playlist size and rule constraints.

- `transparency_controls`
  - controls explanation behavior.

- `observability_controls`
  - controls logging and diagnostics.

## 4. What Each Main Source Folder Does

You do not need to explain every file. Explain the folders like this.

### Core runtime path used in the demo

- `src/data_layer/`
  - Checks the embedded DS-001 candidate dataset and confirms the dataset file is present and consistent.

- `src/ingestion/`
  - Holds Spotify export utilities and the preserved embedded Spotify export artifacts used as input data for the bundle.

- `src/alignment/`
  - Aligns user-side source data to the candidate dataset and produces the seed table used downstream.

- `src/profile/`
  - Builds the user preference profile from aligned listening history and influence tracks.

- `src/retrieval/`
  - Filters the candidate corpus down to a smaller relevant set of tracks.

- `src/scoring/`
  - Scores the kept candidates using deterministic semantic and numeric signals.

- `src/playlist/`
  - Builds the final playlist under explicit rules like target size, genre limits, and sequence constraints.

- `src/transparency/`
  - Produces explanation outputs for why tracks were selected.

- `src/observability/`
  - Produces the run log so the run is inspectable and auditable.

- `src/orchestration/`
  - Runs the stages in order and writes the BL-013 summary.

- `src/quality/`
  - Runs the BL-014 sanity checks over the generated outputs.

### Supporting packages you can mention briefly

- `src/controllability/`
  - Contains support for controllability analysis and runtime controls.

- `src/reproducibility/`
  - Contains support for reproducibility checks.

- `src/run_config/`
  - Contains config helpers, templates, and emitted config artifacts.

- `src/shared_utils/`
  - Shared helpers used across stages.

## 4A. Stage-By-Stage: What It Does + What Output To Show

Use this section if you want to explain each stage concretely during the demo.

1. BL-003 Alignment (`src/alignment/`)
   - What it does:
     - Aligns user-side listening events to DS-001 candidate tracks and builds seed artifacts.
   - Main outputs to show:
     - `src/alignment/outputs/bl003_ds001_spotify_seed_table.csv`
     - `src/alignment/outputs/bl003_ds001_spotify_summary.json`
     - `src/alignment/outputs/bl003_ds001_spotify_trace.csv`
     - `src/alignment/outputs/bl003_ds001_spotify_unmatched.csv`
     - `src/alignment/outputs/bl003_source_scope_manifest.json`

2. BL-004 Profile (`src/profile/`)
   - What it does:
     - Builds the deterministic user preference profile from BL-003 seed evidence.
   - Main outputs to show:
     - `src/profile/outputs/bl004_preference_profile.json`
     - `src/profile/outputs/profile_summary.json`
     - `src/profile/outputs/bl004_seed_trace.csv`

3. BL-005 Retrieval (`src/retrieval/`)
   - What it does:
     - Filters the full candidate corpus to a smaller candidate set likely to fit the profile.
   - Main outputs to show:
     - `src/retrieval/outputs/bl005_filtered_candidates.csv`
     - `src/retrieval/outputs/bl005_candidate_decisions.csv`
     - `src/retrieval/outputs/bl005_candidate_diagnostics.json`

4. BL-006 Scoring (`src/scoring/`)
   - What it does:
     - Applies weighted scoring across semantic and numeric components to rank retained candidates.
   - Main outputs to show:
     - `src/scoring/outputs/bl006_scored_candidates.csv`
     - `src/scoring/outputs/bl006_score_summary.json`
     - `src/scoring/outputs/bl006_score_distribution_diagnostics.json`

5. BL-007 Playlist Assembly (`src/playlist/`)
   - What it does:
     - Assembles the final playlist under deterministic rules and policy constraints.
   - Main outputs to show:
     - `src/playlist/outputs/playlist.json`
     - `src/playlist/outputs/bl007_assembly_trace.csv`
     - `src/playlist/outputs/bl007_assembly_report.json`
     - `src/playlist/outputs/bl007_assembly_detail_log.json`

6. BL-008 Transparency (`src/transparency/`)
   - What it does:
     - Builds mechanism-linked explanation payloads for selected playlist tracks.
   - Main outputs to show:
     - `src/transparency/outputs/bl008_explanation_payloads.json`
     - `src/transparency/outputs/bl008_explanation_summary.json`

7. BL-009 Observability (`src/observability/`)
   - What it does:
     - Records run-level chain evidence so the run is inspectable and reproducible.
   - Main outputs to show:
     - `src/observability/outputs/bl009_run_observability_log.json`
     - `src/observability/outputs/bl009_run_index.csv`

8. BL-013 Orchestration (`src/orchestration/`)
   - What it does:
     - Runs BL-003 through BL-009 in order and writes the overall run summary.
   - Main outputs to show:
     - `src/orchestration/outputs/bl013_orchestration_run_latest.json`
     - `src/orchestration/outputs/bl013_orchestration_run_<RUN_ID>.json`

9. BL-014 Quality/Sanity (`src/quality/`)
   - What it does:
     - Validates artifact contracts and cross-stage continuity checks.
   - Main outputs to show:
     - `src/quality/outputs/bl014_sanity_report.json`
     - `src/quality/outputs/bl014_sanity_run_matrix.csv`
     - `src/quality/outputs/bl014_sanity_config_snapshot.json`

One sentence to read after showing these:

"Each stage writes its own artifacts, and BL-013 plus BL-014 provide run-level orchestration and validation evidence over that full chain."

## 5. The Actual Pipeline Story To Say Out Loud

If you want one simple explanation, say this:

"The program takes preserved user-side music data and an embedded candidate dataset, aligns them, builds a preference profile, retrieves relevant candidates, scores them deterministically, assembles a constrained playlist, generates explanations, and then records an observability log plus validation results."

If you want the more detailed stage-by-stage version, say this:

1. "First, the data layer confirms the embedded candidate dataset is available."
2. "Then alignment builds a seed representation from the user-side input artifacts."
3. "Profile construction turns those aligned signals into user preference features."
4. "Retrieval filters the candidate corpus to tracks that fit the profile."
5. "Scoring ranks those candidates using weighted semantic and numeric comparisons."
6. "Playlist assembly applies playlist-level rules and produces the final ordered list."
7. "Transparency generates explanation payloads for selected tracks."
8. "Observability records the run in a structured log."
9. "Finally, the quality layer checks that the expected artifacts and contracts are present."

## 6. Why Some Files Are Still Inside `outputs/`

If your mentor asks why there are still files inside some `outputs/` folders, say this:

"Most generated outputs are intentionally removed from the clean handoff package. The exceptions are the embedded dataset files in `src/data_layer/outputs/` and the preserved Spotify export assets in `src/ingestion/outputs/spotify_api_export/`, because the bundle uses those as inputs for the default runnable path."

That is the correct explanation.

## 7. What To Show After The Command Finishes

After the run completes, show these places:

1. `src/orchestration/outputs/`
   - explain that BL-013 writes the orchestration summary here.

2. `src/quality/outputs/bl014_sanity_report.json`
   - explain that this is the validation report produced by the quality checks.

3. `src/playlist/outputs/`
   - explain that this is where the generated playlist artifacts appear.

4. `src/transparency/outputs/`
   - explain that this is where explanation payloads appear.

5. `src/observability/outputs/`
   - explain that this is where the run log appears.

Say:

"These outputs are generated at runtime. In the clean mentor package they start empty, and after execution they are populated by the pipeline."

## 8. A Full Simple Script You Can Read Almost Word For Word

"This is the mentor review bundle for my deterministic playlist generation pipeline. At the top level I have a wrapper entrypoint in `main.py`, a README with setup and run instructions, a minimal requirements file, one canonical run configuration profile, and the source tree. The wrapper is the easiest way to run the artefact because it chooses the canonical config, triggers orchestration, and can also run validation.

Inside `src`, the pipeline is organized by stage. The data layer checks the embedded candidate dataset. The ingestion area contains the preserved Spotify-derived input artifacts. Alignment converts those inputs into matched seed data. Profile turns that into preference signals. Retrieval filters the corpus. Scoring ranks candidates deterministically. Playlist assembly produces the final ordered playlist. Transparency generates explanations, observability records the run, and the quality layer checks that the generated artifacts satisfy the expected contracts.

I will now run the wrapper on this machine using a fresh virtual environment with `--validate-only`, which means it will execute the pipeline and then run the validation checks. After it finishes, I will show the orchestration summary, the sanity report, and the generated output folders."

## 9. If You Freeze During The Recording

If you lose your place, go back to one of these lines:

- "This file is the wrapper entrypoint."
- "This config is the main control surface."
- "These folders represent the pipeline stages in order."
- "I am now running setup and then the full pipeline with validation checks."
- "These outputs show the result of the run."

That is enough. You do not need to explain every function.

## 10. Very Short Emergency Version

If you want the shortest possible usable recording, do only this:

1. Show the bundle root.
2. Open `main.py` and say it is the wrapper entrypoint.
3. Open `run_config_ui013_tuning_v1f.json` and say it is the canonical control file.
4. Run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\main.py --validate-only
```

5. Open `src/quality/outputs/bl014_sanity_report.json`.
6. Say: "The run completed and the validation report was generated successfully."

That is a valid demo.
