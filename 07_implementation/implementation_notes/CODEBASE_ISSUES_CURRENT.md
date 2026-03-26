# Implementation Information Sheet (Current Snapshot)

Last updated: 2026-03-26

## Purpose
This document explains how the active implementation currently works, what it is designed to do, how the pipeline is structured, which runtime controls govern it, what artifacts it produces, and what the latest validated execution evidence says about its current behavior.

It is intentionally implementation-facing rather than theoretical. The goal is to describe the live system as it exists in the codebase and outputs under `07_implementation/implementation_notes`.

## One-Sentence Summary
The current implementation is a deterministic single-user playlist generation pipeline that takes Spotify export data, aligns it to the active DS-001 candidate corpus, builds a hybrid semantic-plus-numeric preference profile, filters and scores candidates, assembles a constrained playlist, generates explanations, and emits structured observability and validation artifacts.

## Current System Identity

### System Type
- Deterministic
- Single-user
- Content-based
- Hybrid semantic + numeric feature pipeline
- Artifact-heavy and audit-oriented

### What The System Is Not
- Not collaborative filtering
- Not a learned ranking model
- Not an online serving system
- Not a multi-user production recommender
- Not dependent on stochastic inference at recommendation time

## Current Execution Posture
- Active orchestration entrypoint: BL-013
- Active validation harness: BL-014
- Active reproducibility harness: BL-010
- Active controllability harness: BL-011
- Active recommendation mode: deterministic hybrid ranking over DS-001 candidates
- Active config source in latest run: explicit run-config
- Latest run-config used: `run_config_ui013_tuning_v1f.json`

## Superseding Update - 2026-03-26 21:03 UTC

This section supersedes the older v1b/v1d snapshot details below when they conflict with the latest live state.

### Final Live Baseline
- BL-013 restore run: `BL013-ENTRYPOINT-20260326-210305-914179` (`pass`)
- BL-014 sanity run: `BL014-SANITY-20260326-210317-371524` (`pass`, `22/22`)
- active config: `run_config_ui013_tuning_v1f.json`
- key retrieval rule: `semantic_score >= 3 or (semantic_score >= 1 and numeric_pass_count >= 4)`
- active scoring components: `10`

### Current Live Runtime Counts
- input event rows: `11935`
- matched event rows: `1904`
- seed table rows: `1064`
- kept candidates: `46776`
- candidates scored: `46776`
- playlist length: `10/10`
- explanations generated: `10`

### Current Live Output Shape
- playlist genre mix: pop `4`, new wave `1`, classic rock `2`, rock `2`, singer-songwriter `1`
- explanation top-contributor distribution: lead genre match `4`, tag overlap `3`, genre overlap `3`
- BL-006 component balance: all-candidates numeric mean `0.046346`, semantic mean `0.196449`

### Evaluation And Freshness Note
- BL-010 latest rerun on disk: `BL010-REPRO-20260326-205834` (`deterministic_match=true`)
- BL-011 latest rerun on disk: `BL011-CTRL-20260326-205932` (`pass`)
- The latest active freshness suite report is `BL-FRESHNESS-SUITE-20260326-210015` (`fail`) because BL-010/BL-011 auto-refresh writes evaluation-baseline outputs, and the live pipeline was then restored to v1f. This is an evidence-contract mismatch, not a runtime failure in the live pipeline.

## Current High-Level Flow
1. Spotify export data is gathered through the active ingestion/export path.
2. Imported listening events are aligned to tracks present in the DS-001 working candidate dataset.
3. Matched listening evidence is converted into a weighted user preference profile.
4. The full candidate corpus is filtered into a smaller keep set using semantic evidence and numeric support rules.
5. Kept candidates are scored with a weighted hybrid similarity function.
6. A playlist is assembled under explicit rule constraints.
7. Track-level explanations are generated.
8. Observability artifacts record the run, configuration, hashes, and stage diagnostics.
9. Quality and evaluation harnesses validate structural coherence, freshness, reproducibility, and controllability.

## Core Runtime Control Layer

### BL-000 Run-Config Resolver
The active control layer is the canonical run-config system under BL-000. It resolves intent into an effective configuration used by downstream stages and writes two canonical artifacts:
- `run_intent_*.json`
- `run_effective_config_*.json`

This layer governs:
- input scope
- seed weighting
- profile limits
- retrieval thresholds
- scoring thresholds and component weights
- assembly constraints
- transparency behavior
- observability settings
- controllability sweep parameters

### Guardrails Currently Active
- strict validation profile
- threshold-coupling enforcement
- component-weight normalization control
- canonical config artifact emission
- seed freshness handling in BL-013 when run-config is used
- minimum BL-003 match-rate threshold
- deterministic stable-artifact hashing for repeatability checks

## Latest Live Run Snapshot

### Latest BL-013 Orchestration Run
- Run ID: `BL013-ENTRYPOINT-20260326-200502-414835`
- Status: `pass`
- Generated at: `2026-03-26T20:05:02Z`
- Elapsed time: `~11s`
- Config path: `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1d.json`
- Refresh-seed mode: enabled
- Note: v1d is the semantic-rebalanced config (numeric weights halved, semantic weights boosted). Tempo dropped from explanation outputs entirely.

### Stage Outcome Snapshot
- BL-003: pass, `1.932s`
- BL-004: pass, `0.138s`
- BL-005: pass, `3.042s`
- BL-006: pass, `2.692s`
- BL-007: pass, `0.720s`
- BL-008: pass, `0.589s`
- BL-009: pass, `0.902s`

### Latest Measured Runtime Counts
- Input event rows: `11935`
- Matched by Spotify ID: `1098`
- Matched by metadata: `806`
- Matched event rows: `1904`
- Seed table rows: `1064`
- Unmatched rows: `10031`
- Kept candidates: `54402`
- Candidates scored: `54402`
- Playlist length: `10/10`
- Explanations generated: `10`

### Latest Playlist Mix
- pop: `4`
- soundtrack: `1`
- singer-songwriter: `1`
- classic rock: `2`
- new wave: `1`
- rock: `1`

### Latest Explanation Top-Contributor Distribution
- Lead genre match: `4`
- Tag overlap: `3`
- Genre overlap: `3`
- Tempo (BPM): `0` (no longer a top contributor under v1d semantic-rebalanced weights)

## Active Effective Configuration In Latest Run

### Input Scope
- source family: `spotify_api_export`
- include top tracks: true
- include saved tracks: true
- include playlists: true
- include recently played: true
- top ranges: `short_term`, `medium_term`, `long_term`
- recently played limit: `50`

### Seed Controls
- minimum match-rate threshold: `0.15`
- source base weights:
  - top tracks: `1.0`
  - saved tracks: `0.6`
  - recently played: `0.5`
  - playlist items: `0.4`
- top range weights:
  - short term: `0.5`
  - medium term: `0.3`
  - long term: `0.2`

### Profile Controls
- top tag limit: `10`
- top genre limit: `10`
- top lead genre limit: `10`

### Retrieval Controls
- semantic minimum keep score: `1`
- semantic strong keep score: `3`
- numeric support minimum pass count: `2`
- numeric thresholds:
  - tempo: `15.0`
  - key: `1.5`
  - mode: `0.5`
  - duration_ms: `30000.0`

### Scoring Controls
- component weights (v1d — semantic-rebalanced):
  - tempo: `0.06` (was 0.12 in v1b)
  - duration_ms: `0.04` (was 0.08)
  - key: `0.04` (was 0.08)
  - mode: `0.04` (was 0.07)
  - lead_genre: `0.29` (was 0.23)
  - genre_overlap: `0.24` (was 0.19)
  - tag_overlap: `0.29` (was 0.23)
- numeric total: `0.18` (was 0.35 in v1b)
- semantic total: `0.82` (was 0.65 in v1b)
- weight auto-normalization override allowed: false

### Assembly Controls
- target size: `10`
- minimum score threshold: `0.35`
- max per genre: `4`
- max consecutive same-genre run: `2`

### Transparency Controls
- top contributor limit: `3`
- near-tie blending enabled: true
- primary contributor tie delta: `0.09`

## Implemented Pipeline Blocks

### BL-001 / BL-002 — Ingestion And Spotify Export Support
Status: implemented support layer

Role:
- Collect and normalize Spotify-side interaction data.
- Produce export artifacts used by the alignment stage.

What this part contributes:
- user interaction evidence
- active source scope for BL-003
- stable export path used by the current implementation

Important practical note:
- The current system uses Spotify export data as its active user-signal source, but downstream numeric comparisons depend on candidate-side corpus features rather than live Spotify audio-feature responses.

### BL-003 — Alignment And Seed Construction
Script:
- `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`

Role:
- Align Spotify-derived listening events to the DS-001 candidate corpus.
- Produce the seed table used by BL-004.
- Record traceability for matched and unmatched events.

What BL-003 does:
- applies input-scope controls
- aligns imported events against DS-001 identifiers and metadata
- aggregates matched evidence into DS-001-aligned seed rows
- writes unmatched diagnostics
- writes source-scope manifest and summary outputs
- enforces match-rate guardrails

Key outputs:
- `bl003_ds001_spotify_seed_table.csv`
- `bl003_ds001_spotify_trace.csv`
- `bl003_ds001_spotify_unmatched.csv`
- `bl003_ds001_spotify_summary.json`
- `bl003_source_scope_manifest.json`

Current observed behavior in latest run:
- aligned matched events: `1904`
- resulting seed rows: `1064`
- unmatched rows remain significant, which means corpus coverage is still a practical boundary

Why it matters:
- BL-003 determines how much of the user’s interaction history becomes usable recommendation evidence.

### BL-004 — Preference Profile Construction
Script:
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`

Role:
- Convert aligned seed evidence into a deterministic preference profile.

What BL-004 builds:
- top tags
- top genres
- top lead genres
- numeric centers over candidate-comparable features
- seed trace artifacts used for downstream auditability

Important characteristic:
- BL-004 is hybrid, not semantic-only.
- The profile contains both semantic preference structure and numeric summaries derived from aligned candidate-side data.

Key outputs:
- `bl004_preference_profile.json`
- `bl004_profile_summary.json`
- `bl004_seed_trace.csv`

Why it matters:
- BL-004 is the canonical representation of user preference consumed by retrieval and scoring.

### BL-005 — Candidate Retrieval And Filtering
Script:
- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`

Role:
- Reduce the full candidate corpus to a defensible candidate pool before ranking.

What BL-005 does:
- excludes seed tracks from retrieval output
- measures semantic overlap against the profile
- checks numeric support against configured thresholds
- applies a semantic-first keep rule
- emits a full candidate decision trace

Active keep rule in current v1b run:
- keep if not seed and (`semantic_score >= 3` or (`semantic_score >= 1` and `numeric_pass_count >= 2`))

Implication:
- retrieval is semantic-first
- numeric evidence supports borderline semantic matches
- numeric-only candidates are not enough on their own

Key outputs:
- `bl005_filtered_candidates.csv`
- `bl005_candidate_decisions.csv`
- `bl005_candidate_diagnostics.json`

Current observed behavior:
- kept candidates: `54402`

Why it matters:
- BL-005 is the first hard boundary on what can ever appear in the final playlist.

### BL-006 — Candidate Scoring
Script:
- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`

Role:
- Rank retrieved candidates using a deterministic hybrid similarity function.

Scoring components:
- numeric:
  - tempo
  - duration_ms
  - key
  - mode
- semantic:
  - lead_genre
  - genre_overlap
  - tag_overlap

Important characteristic:
- BL-006 is the main hybrid scoring stage.
- Numeric and semantic components are both active in the latest run.

What BL-006 does:
- computes weighted component contributions
- respects active thresholds from run-config
- avoids invalid fallback paths through explicit validation
- records score summary artifacts and scored candidate output

Key outputs:
- `bl006_scored_candidates.csv`
- `bl006_score_summary.json`

Current observed behavior:
- candidates scored: `54402`
- active component count: `7`
- weight rebalance diagnostics in latest run: `rebalanced = false`

Why it matters:
- BL-006 defines the candidate ranking that BL-007 turns into a playlist.

### BL-007 — Playlist Assembly
Script:
- `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`

Role:
- Convert ranked candidates into a final playlist under explicit assembly rules.

Rules enforced:
- minimum score threshold
- maximum tracks per genre
- maximum consecutive same-genre run
- target playlist length cap

What BL-007 does:
- walks ranked candidates greedily
- decides keep/reject at assembly time
- records full assembly trace
- emits undersized-playlist diagnostics if target size cannot be met

Key outputs:
- `bl007_playlist.json`
- `bl007_assembly_trace.csv`
- `bl007_assembly_report.json`

Current observed behavior:
- final playlist length: `10/10`
- current genre mix shows meaningful diversity under the v1b config rather than pure tempo-dominance behavior

Why it matters:
- BL-007 is where ranking becomes a concrete recommendation artifact.

### BL-008 — Transparency And Explanation Generation
Script:
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`

Role:
- Generate machine-readable and human-readable explanations for playlist tracks.

What each explanation captures:
- playlist position
- score rank
- final score
- top contributors
- full score breakdown
- assembly context
- short why-selected explanation text

Key outputs:
- `bl008_explanation_payloads.json`
- `bl008_explanation_summary.json`

Current observed behavior:
- explanations produced: `10`
- top contributors are more distributed under v1b across lead genre, tag overlap, tempo, and genre overlap

Why it matters:
- BL-008 is the main interpretability surface for the recommendation outcome.

### BL-009 — Observability And Audit Logging
Script:
- `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`

Role:
- Consolidate a pipeline run into a structured audit log.

What BL-009 records:
- run metadata
- resolved config context
- stage run IDs
- pipeline and dataset hashes
- input and output artifact hashes
- exclusion and continuity diagnostics
- transparency distribution summaries

Key outputs:
- `bl009_run_observability_log.json`
- `bl009_run_index.csv`

Current observed behavior:
- config source: `run_config`
- total seed count: `1064`
- history track count: `1064`
- influence tracks included: false
- canonical config artifact pair available: true

Why it matters:
- BL-009 is the most compact single artifact for understanding what happened in one full run.

### BL-010 — Reproducibility Harness
Status: implemented evaluation layer

Role:
- Re-execute the deterministic pipeline path repeatedly and compare stable outputs.

Current stored evidence:
- latest report on disk: `BL010-REPRO-20260326-193206`
- overall result: `deterministic_match = true`
- replay count: `3`
- config_hash: `96DA63B0...`
- fixed input source: `active_pipeline_outputs`

What BL-010 demonstrates:
- replayed stage execution
- attempt history and retry awareness
- stable artifact comparison over repeated runs

Why it matters:
- BL-010 provides evidence for deterministic repeatability claims.

### BL-011 — Controllability Harness
Status: implemented evaluation layer

Role:
- Run controlled scenario changes and measure whether observable outputs shift in expected ways.

Current stored evidence:
- latest report on disk: `BL011-CTRL-20260326-193245`
- overall status: `pass`
- scenario count: `5`
- baseline_config_hash: `96DA63B0...`
- stage scope: BL-004 through BL-007

Scenario classes in the stored report:
- baseline
- no influence tracks
- valence weight up
- stricter thresholds
- looser thresholds

What BL-011 demonstrates:
- repeat consistency per scenario
- expected directional shifts
- measurable differences in candidate pool, ranking, and playlist behavior when parameters change

Why it matters:
- BL-011 provides evidence that the system is not only deterministic but intentionally steerable.

### BL-013 — End-To-End Orchestration Entry Point
Script:
- `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`

Role:
- Run the active implementation as one coordinated pipeline.

What BL-013 does:
- optionally refreshes BL-003
- resolves and records canonical config artifacts
- runs BL-004 through BL-009 in deterministic order
- emits orchestration summaries
- records stable artifact hashes for repeatability checks

Operational command pattern:
- default end-to-end run
- selected-stage execution
- continue-on-error mode
- refresh-seed plus explicit run-config mode

Why it matters:
- BL-013 is the practical entrypoint for seeing the current implementation behave as a system.

### BL-014 — Quality And Freshness Validation
Status: implemented validation layer

Role:
- Validate structural coherence of the active outputs.
- Validate freshness coupling around BL-010 and BL-011 evidence.

Current stored sanity report:
- run ID: `BL014-SANITY-20260326-193439-677029`
- overall status: `pass`
- checks passed: `22/22`

Current stored active freshness suite report:
- run ID: `BL-FRESHNESS-SUITE-20260326-193344`
- overall status: `pass`
- checks passed: `8/8`

What BL-014 checks:
- required artifact presence
- schema shape
- cross-stage hash linkage
- count continuity
- run ID continuity
- freshness and auto-refresh status for BL-010 and BL-011 evidence

Why it matters:
- BL-014 is the fastest way to confirm that active outputs remain internally coherent after refactors or reruns.

## How Recommendation Logic Currently Works

### Short Answer
The live system is not semantics-only.

### More Precise Answer
- BL-004 builds a hybrid preference profile.
- BL-005 retrieval is semantic-first with numeric support.
- BL-006 scoring is hybrid semantic + numeric.
- BL-007 applies deterministic assembly rules after scoring.
- BL-008 exposes contributor-level explanation structure.

So the best description of the current implementation is:
- deterministic
- content-based
- hybrid semantic-plus-feature recommendation pipeline

## Determinism And Repeatability Status

### Stable Artifact Tracking In BL-013
BL-013 records stable hashes for:
- BL-004 seed trace
- BL-005 filtered candidates
- BL-005 candidate decisions
- BL-006 scored candidates
- BL-007 assembly trace

### Latest Verified Repeatability Result
The fresh v1b run on 2026-03-26 reproduced the earlier v1b stable artifact set exactly, which indicates deterministic behavior under unchanged inputs and config for the tracked stable outputs.

### Important Nuance
Some top-level JSON outputs such as playlist, explanation payloads, and observability logs are expected to change across reruns because they embed new run IDs and timestamps even when the stable recommendation state is unchanged.

## Operational Health Snapshot

### Live Pipeline State
- BL-013 latest orchestration run: pass (`BL013-ENTRYPOINT-20260326-210305-914179`)
- BL-003 refresh in latest orchestrated run: pass
- BL-004 through BL-009 in latest orchestrated run: all pass

### Validation State Recorded On Disk
- BL-014 sanity report: pass (`22/22`) — `BL014-SANITY-20260326-210317-371524`
- active freshness suite: fail (`6/8`) — `BL-FRESHNESS-SUITE-20260326-210015`
- BL-010 reproducibility: pass (`deterministic_match=true`, 3 replays) — `BL010-REPRO-20260326-205834`
- BL-011 controllability: pass (5 scenarios) — `BL011-CTRL-20260326-205932`

### Recent Refactor And Hardening Direction
The current codebase has already undergone a substantial hardening/refactor pass. Key outcomes include:
- shared Windows-safe text writing utilities
- removal of legacy surrogate branches from active runtime paths where no longer needed
- stronger required-artifact validation
- cleaner BL-013 orchestration control flow
- improved BL-009 observability metadata emission
- helper extraction and runtime guard strengthening across BL-003 through BL-011

## Main Strengths Of The Current Implementation
- deterministic stage structure
- explicit run-config control layer
- strong artifact traceability through JSON and CSV outputs
- integrated observability with config and hash capture
- evaluation harnesses for reproducibility and controllability
- quality harness for structural consistency and freshness validation
- explanation outputs that expose why tracks were selected

## Main Practical Boundaries And Limitations
- **Dataset alignment coverage (DS-001 limitation)**: BL-003 matched only 1,904 of 11,935 imported Spotify events (15.95%), yielding 1,064 unique seed tracks. The remaining 10,031 events (~84%) are unmatched because DS-001 does not contain those tracks. This is a dataset coverage constraint, not a pipeline defect. The recommendation profile is built from the matched 1,064 seeds only. Improving DS-001 corpus coverage is the only way to increase this yield.
- Recommendation quality is bounded by DS-001 metadata quality and coverage.
- The system is still single-user and content-based rather than collaborative.
- Numeric comparisons rely on candidate-side corpus features and aligned evidence, not a live end-user feature profile gathered directly at recommendation time.
- BL-010 and BL-011 evaluation harnesses were freshly rerun on 2026-03-26 and both confirmed passing. Because those harnesses execute their own evaluation baselines and write through active outputs, the live recommendation surface must be restored afterward. The final live state in this cycle is the v1f restore run at 21:03 UTC.

## Known Open Issues

### Blocking
None. The live pipeline is operational and the final live v1f baseline passes BL-013 and BL-014 sanity. The only current caveat is a non-blocking freshness-suite evidence mismatch between stored BL-010/BL-011 evaluation snapshots and the restored live v1f contract.

### High Priority — Data Coverage

**BL-003 / DS-001 alignment coverage gap**
- 10,031 of 11,935 imported listening events remain unmatched to DS-001.
- Root cause: DS-001 corpus coverage is incomplete relative to the user's full Spotify listening history.
- Effect: a significant portion of the user's interaction evidence is discarded before profiling; profile is built on `1,064` matched seed tracks only.
- Match-rate enforcement is active (`min_threshold=0.15` in v1f config) and currently passing.
- Mitigation path: improve DS-001 corpus coverage and/or normalization to reduce unmatched volume.

### High Priority — Recommendation Quality

**BL-006 numeric feature dominance in scoring — RESOLVED in v1f live baseline**
- The originally missing numeric features `danceability`, `energy`, and `valence` are now implemented end to end in BL-005 and BL-006.
- The live v1f baseline uses ten active scoring components with semantic weights still dominant (`lead_genre=0.29`, `genre_overlap=0.24`, `tag_overlap=0.29`) and bounded numeric support across seven numeric dimensions.
- Current live component balance confirms the fix: all-candidates numeric mean `0.046346` vs semantic mean `0.196449`; top-100 numeric mean `0.06246` vs semantic mean `0.602234`.
- Config: `run_config_ui013_tuning_v1f.json`

**BL-008 explanation contributor concentration — RESOLVED in v1f live baseline**
- Current live explanation distribution is: Lead genre match `4`, Tag overlap `3`, Genre overlap `3`.
- No numeric contributor dominates the exposed rationale surface in the final live baseline.

### Medium Priority — Assembly Selectivity

**BL-007 min-score threshold not causing rejections (R1 inactive)**
- `min_score_threshold = 0.35` is not rejecting any candidates in current runs (R1 exclusion count = 0).
- Mechanism: BL-007 uses a greedy walk over score-sorted candidates and terminates once 10 tracks are selected; the remaining ~40,000 lower-scored candidates are pre-empted by R4 length cap before R1 evaluates them. The BL-006 corpus `min_score` of `0.014819` reflects the full scoring floor, which is never reached during assembly.
- Within the candidate prefix actually walked, all tracks score above 0.35, so R1 has no effect in the current config.
- Under v1f, R2 (genre cap) and R3 (consecutive run) remain active at 2,859 and 3,907 hits respectively, indicating assembly diversity rules are meaningfully engaged. R4 length cap remains the largest exclusion source (~40,000).
- Mitigation path for R1: raise `min_score_threshold` to a level that would cut into the walked prefix (estimated effective range: 0.45–0.50), or reduce upstream candidate breadth via BL-005 so lower-scoring candidates are reached by the walk.

**BL-005 candidate pool breadth**
- 46,776 candidates are retained after filtering, still a large share of the full non-seed corpus.
- Effect: large pool increases BL-006 scoring workload and broadens noise exposure in assembly.
- Mitigation path: tighten `semantic_strong_keep_score` threshold or switch to a stricter retrieval policy when available.

### Low Priority — Operational Evidence Alignment

**BL-014 active freshness suite currently fails after final live restore**
- Current report: `BL-FRESHNESS-SUITE-20260326-210015` (`6/8` pass).
- Root cause: BL-010 and BL-011 auto-refresh rerun their own evaluation baselines and rewrite active artifacts; after that, the live system was intentionally restored to v1f for the final baseline.
- Effect: stored BL-010/BL-011 freshness snapshots do not hash-match the restored live v1f contract.
- Impact: no live-pipeline breakage. BL-013 and BL-014 sanity still pass on the final v1f outputs.
- Mitigation path: either rerun a freshness mode that snapshots BL-010/BL-011 against the restored v1f contract, or keep documenting this as an expected post-restore evidence mismatch.

### Low Priority — Approved Backlog (Not Yet Implemented)

**BL-005 user-selectable retrieval policy modes**
- Approved as a backlog item: expose retrieval decision policy as a run-config control.
- Proposed policy modes: `semantic_first_current` (current behavior), `balanced_joint`, `strict_joint`.
- No implementation work has started. Current behavior is unchanged until explicitly authorized.

### Low Priority — Operational / Cosmetic

**BL-009 `bootstrap_mode` flag semantics are legacy-influenced**
- The `bootstrap_mode` flag in the observability log reflects legacy schema semantics and can blur interpretation of the current active operational mode.
- No functional impact. Interpretability issue only.

**BL-010 / BL-011 `report_mtime_utc > generated_at_utc`**
- In QA report artifacts, `report_mtime_utc` can appear later than `generated_at_utc`, which can mislead audit readers.
- No functional impact. Display artifact caused by file-write timing.

**BL-014 no multi-run trend rollup**
- BL-014 validates each run snapshot individually. No cross-run trend summary or quality history rollup exists yet.
- No impact on current run validity. Affects long-term governance monitoring.

**BL-014 Windows path separators in config snapshot**
- `required_artifacts` paths in the BL-014 config snapshot use Windows-style backslash separators.
- Cosmetic consistency issue only. No functional impact.

---

## Most Important Runtime Artifacts To Read
- BL-013 orchestration summary:
  - `07_implementation/implementation_notes/bl013_entrypoint/outputs/bl013_orchestration_run_latest.json`
- BL-003 alignment summary:
  - `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json`

---

## Planned Next Steps

This section records the ordered action plan following the v1f baseline stabilization on 2026-03-26.

Last updated: 2026-03-26 21:03 UTC

### Immediate (Non-Blocking; Cleans Up Freshness Indicator)

**1. Freshness suite re-alignment**
- Goal: restore freshness suite from `6/8` to `8/8` by re-running BL-010 and BL-011 under the current live v1f contract.
- Reason: the current `BL-FRESHNESS-SUITE-20260326-210015` failure is an evidence-contract mismatch from the post-restore cycle, not a structural pipeline defect.
- Action:
  1. Run BL-010 reproducibility check (writes current v1f artifacts as evaluation baseline).
  2. Run BL-011 controllability check (same contract).
  3. Restore live pipeline with a fresh BL-013 v1f run (`--refresh-seed --run-config run_config_ui013_tuning_v1f.json`).
  4. Run BL-014 freshness suite to confirm 8/8 pass.
- Commands:
  ```powershell
  python 07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py
  python 07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py
  python 07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py --refresh-seed --run-config 07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json
  python 07_implementation/implementation_notes/bl014_quality/run_active_freshness_suite.py
  ```
- Risk: low. BL-010/BL-011 temporarily overwrite active artifacts during evaluation; the final BL-013 restore step ensures the live state returns to v1f.

**2. v1f supplementary acceptance record**
- Goal: append a v1f supplement note to the resolved UI-013 record to document the post-UI-013 refinement path.
- Reason: UI-013 was formally closed on the v1b profile. v1f activates three additional numeric dimensions but preserves semantic dominance and does not reopen acceptance gates.
- Action: add a brief v1f supplement to `00_admin/unresolved_issues.md` resolved-UI-013 block and log the change.

### High Priority (Thesis Submission Dependency)

**3. UI-003 citation package closure**
- Goal: complete the thesis-wide claim-citation matrix for Chapters 3–5, record support-strength verdicts, and produce chapter-targeted hardening notes.
- Current state: UI-003 remains open with synthesis closure pending. Recovery and PDF-audit phases are complete; remaining work is claim-level verdict recording and chapter-targeted insertion notes.
- Action plan:
  1. Extend claim-citation matrix to Chapter 3 (methodology and design decisions).
  2. Extend to Chapter 4 (implementation evidence and pipeline behavior claims).
  3. Extend to Chapter 5 (evaluation and discussion claims).
  4. Record verdicts (`supported`, `partially_supported`, `weak_support`, `mismatch`) for all open claims.
  5. Produce final chapter-targeted insertion / rewrite / citation-swap notes.
  6. Close the package once synthesis output is logged and cross-referenced in `00_admin/unresolved_issues.md`.
- Risk: high. This is the primary remaining submission-hardening dependency.
- Due window: 2026-03-19 to 2026-03-29.

### Medium Priority (Thesis Writing Quality)

**4. Chapter alignment to v1f artifact counts**
- Goal: review Chapter 4 and Chapter 5 for any references to v1b/v1d-era artifact counts and update them to the v1f baseline.
- Items to verify or update:
  - `bl005_kept_candidates`: now `46,776` (was `54,402` in v1b)
  - active BL-006 component count: now `10` (was `7` in v1b/v1d)
  - newly active numeric features: `danceability`, `energy`, `valence`
  - active config identifier: `run_config_ui013_tuning_v1f.json`
  - BL-007 rule hit counts: R2=`2,859`, R3=`3,907`, R4=`~40,000`
- Risk: medium. Any still-present v1b counts cited as the final delivered result would misrepresent the live baseline.

**5. Evaluation evidence packaging**
- Goal: consolidate BL-010 and BL-011 reports into a final evaluation evidence artifact set for Chapter 5 discussion.
- Items:
  - BL-010 reproducibility: run `BL010-REPRO-20260326-205834`, `deterministic_match=true`, 3 replays, config hash `99C9672FE67C112A4679F900CD8904792EF69C7E6970C03B6CA8D495E12BFFA2`
  - BL-011 controllability: run `BL011-CTRL-20260326-205932`, 5 scenarios, `status=pass`, baseline config hash same as BL-010
  - Scenario classes: baseline, no_influence_tracks, valence_weight_up, stricter_thresholds, looser_thresholds
  - Document in Chapter 5 evaluation section with explicit run IDs, scenario classes, and result summary.
- Risk: low. The evidence is already on disk; work is writing and synthesis only.

### Low Priority (Optional Refinement)

**6. BL-005 candidate pool reduction**
- Goal: tighten the retrieval boundary to reduce the 46,776-candidate pool, improve BL-006 scoring efficiency, and potentially activate the R1 gate in BL-007 assembly.
- Options:
  - Raise `semantic_strong_keep_score` from `3` to `4` in the v1f config.
  - Increase `numeric_pass_count` minimum from `4` to `5` or `6`.
  - Create a new config variant (e.g. v1g) if changes alter downstream behavior materially.
- Expected effect: smaller candidate pool, higher minimum score in walked prefix, R1 may become effective.
- Risk: any config change will alter BL-005 and BL-006 output hashes; BL-010 and BL-011 evidence must be re-run after applying.

**7. BL-007 R1 threshold tuning**
- Goal: make `min_score_threshold` usefully selective rather than inert.
- Context: currently R1 is inactive because BL-007's greedy walk terminates via R4 before reaching low-scoring candidates. Raising the threshold to 0.45–0.50 would narrow the effective walk domain and activate R1 for the upper candidate prefix.
- Dependency: more meaningful if done in conjunction with BL-005 pool reduction (step 6).
- Risk: conservative adjustment is safe; aggressive values could over-reject and reduce playlist quality.

**8. BL-009 `bootstrap_mode` flag cleanup**
- Goal: remove legacy-influenced `bootstrap_mode` semantics from the observability log schema.
- Current state: the flag works but its meaning is blurred by historical schema design.
- Risk: low. Cosmetic schema improvement only; no functional impact on any downstream consumer.

**9. BL-014 multi-run trend rollup**
- Goal: extend BL-014 to maintain a cross-run quality history CSV alongside the per-run snapshot.
- Current state: BL-014 validates each run individually with no cumulative trend tracking.
- Risk: low scope addition; no impact on current run validity or submission state.
- BL-004 profile summary:
  - `07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json`
- BL-005 diagnostics:
  - `07_implementation/implementation_notes/bl005_retrieval/outputs/bl005_candidate_diagnostics.json`
- BL-006 score summary:
  - `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_score_summary.json`
- BL-007 assembly report:
  - `07_implementation/implementation_notes/bl007_playlist/outputs/bl007_assembly_report.json`
- BL-008 explanation summary:
  - `07_implementation/implementation_notes/bl008_transparency/outputs/bl008_explanation_summary.json`
- BL-009 observability log:
  - `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json`
- BL-014 sanity report:
  - `07_implementation/implementation_notes/bl014_quality/outputs/bl014_sanity_report.json`
- active freshness suite report:
  - `07_implementation/implementation_notes/bl014_quality/outputs/bl_active_freshness_suite_report.json`

## Best Command To See The Current System Working
For the current explicit v1f configuration, the most representative command is:

```powershell
python 07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py --refresh-seed --run-config 07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json
```

## Final Interpretation
The current implementation is not just a partial prototype. It is an operational deterministic pipeline with explicit control surfaces, stage-level traceability, explanation outputs, observability artifacts, and dedicated validation/evaluation harnesses. Its main remaining constraint is not missing structure; it is the bounded quality and coverage of the user-history signal after alignment to the active candidate corpus.
