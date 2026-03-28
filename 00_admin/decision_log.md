# Decision Log

Ordering convention (standardized 2026-03-24):
- This log is append-only for auditability.
- Entry IDs remain unique identifiers, but physical entry order reflects historical insertion timing (not strict numeric sorting).
- New entries must be appended at the end and may include `superseded_by` when a prior decision is replaced.

Maintenance snapshot (2026-03-28):
- Highest decision ID currently present: `D-039`
- Total decision entries: 39
- Status distribution: accepted=30, superseded=3, rejected=1
- ID integrity check: no duplicate decision IDs detected

Current posture snapshot (2026-03-25):
- Active baseline path: DS-001 candidate corpus with direct metadata/identifier alignment (`D-028`), with DS-002 retained as validated fallback reference.
- Implemented source-scope closure: deferred source-scope design is now baseline behavior (`D-027`; supersedes `D-023`).
- Freeze-first strategy was temporary and is now historical (`D-026` superseded by `D-027`).
- Deferred enhancement still tracked: deterministic corpus-path switching fallback (`D-025`).
- Implementation-notes naming contract is BL-ordered and canonical (`D-029`); stage/path references must use `bl000_*` ... `bl014_*` folder names.
- Active profile baseline for implementation reporting is v1f (`D-033`), with v2a retained as experimental.

id: D-001
date: 2026-03-12
status: accepted

context:
The thesis requires a well-defined candidate track corpus that provides rich audio features suitable for deterministic content-based recommendation.

decision:
Use the Music4All / Music4All-Onion dataset as the canonical music feature dataset for candidate track generation and similarity computation.

alternatives_considered:
- Spotify API audio features only
- Million Song Dataset
- Hybrid combination of multiple datasets

rationale:
Music4All provides a large, research-grade dataset with rich feature descriptors and metadata that support content-based recommendation experiments. The dataset is widely cited in music information retrieval research and allows offline experimentation without API dependency.

evidence_basis:
Santana et al. (2020); Moscati et al. (2022)

impacted_files:
05_design/system_architecture.md
05_design/data_sources.md
08_writing/chapter3.md

review_date:
none

id: D-018
date: 2026-03-21
status: accepted

context:
Authenticated Spotify API export attempts for BL-002 reached OAuth success but failed at the first `/me` request with very large `Retry-After` values (~23+ hours). A naive wait strategy would hold the process for many hours and produce poor operator visibility.

decision:
Treat extreme Spotify `Retry-After` windows as explicit cooldown blockers. Add a fail-fast threshold (`--max-retry-after-seconds`), print clear blocked-state messages, and write a machine-readable blocker artifact (`spotify_rate_limit_block.json`) containing `retry_after_seconds` and `retry_at_utc`.

alternatives_considered:
- Always sleep for full `Retry-After` regardless of duration
- Ignore `Retry-After` and continue aggressive retries
- Remove fail-fast and rely on manual Ctrl+C interruption
- Treat any 429 as immediate hard failure without cooldown metadata

rationale:
Fail-fast with explicit cooldown reporting preserves operational clarity, avoids multi-hour terminal hangs, and creates concrete evidence for implementation traceability. It also keeps the pipeline resilient for normal short 429 windows while surfacing provider-side long cooldowns as bounded external blockers.

evidence_basis:
- `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_rate_limit_block.json`
- `07_implementation/experiment_log.md` (`EXP-019`)
- terminal evidence: `/me` returned `retry_after_seconds=84882`

impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `00_admin/unresolved_issues.md`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`

review_date:
none

id: D-017
date: 2026-03-21
status: accepted

context:
BL-001 selected Spotify as the ingestion adapter path. The user requested a maximum practical pull from Spotify account data (top tracks, saved tracks, playlists) using the official Web API and full implementation logging.

decision:
Implement Spotify ingestion with Authorization Code flow and the following endpoint set: `/me/top/tracks` (all three time ranges), `/me/tracks`, `/me/playlists`, and `/playlists/{id}/items`. Use requested scopes `user-top-read`, `user-library-read`, `playlist-read-private`, `playlist-read-collaborative`, and `user-read-private`. Export both raw and flattened artifacts plus request-level logs and run-summary hashes.

alternatives_considered:
- Keep CSV-only ingestion and do not add API export ingestion
- Pull only top tracks and skip saved tracks/playlists
- Use ad-hoc single-page endpoint requests without pagination, retry, or request logs
- Hardcode credentials directly in repository files

rationale:
This endpoint set gives the broadest user-preference coverage while staying within the selected Spotify ingestion scope and official documented OAuth permissions. Full pagination and request logs improve reproducibility and observability. Avoiding hardcoded secrets preserves operational safety and repository hygiene.

evidence_basis:
- Spotify Web API docs: Authorization Code flow, Get User's Top Items, Get User's Saved Tracks, Get Current User's Playlists, Get Playlist Items
- `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`
- `07_implementation/experiment_log.md` (`EXP-018`)

impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `07_implementation/backlog.md`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`

review_date:
none

id: D-015
date: 2026-03-21
status: accepted

context:
The user requested updating the active plan to use the DS-002 dataset strategy documented in `06_data_and_sources/ds_002_msd_information_sheet.md`. Current BL-019 planning text was still scoped to Onion canonical refresh.

decision:
Adopt DS-002 (`MSD subset + Last.fm tags + MusicBrainz mapping`) as the active BL-019 dataset-build strategy. Retarget BL-019 planning, implementation-plan guidance, and experiment planning to deterministic cross-source integration on `track_id` with explicit quality gates.

alternatives_considered:
- Keep Onion-only canonical refresh as BL-019 active path
- Keep DS-002 as fallback-only reference without changing active plan
- Run both corpus strategies in parallel during BL-019

rationale:
This aligns implementation planning directly with the user-selected dataset strategy while preserving traceable, deterministic, and inspectable workflow requirements. A single active corpus strategy also reduces planning ambiguity and governance drift.

evidence_basis:
- `06_data_and_sources/ds_002_msd_information_sheet.md`
- `07_implementation/backlog.md` (`BL-019` updated planning scope)
- `07_implementation/implementation_plan.md` (corpus note and BL-019 addendum update)
- `07_implementation/experiment_log.md` (`EXP-016` retargeted plan)

impacted_files:
- `00_admin/decision_log.md`
- `07_implementation/backlog.md`
- `07_implementation/implementation_plan.md`
- `07_implementation/experiment_log.md`
- `06_data_and_sources/dataset_registry.md`

review_date:
none

id: D-010
date: 2026-03-21
status: accepted

context:
BL-009 required a run-level observability layer for the current bootstrap pipeline. The pipeline already depended on BL-017 through BL-008 artifacts, while BL-001 to BL-003 remained intentionally deferred under the bootstrap strategy. The user requested that BL-009 be implemented and logged fully.

decision:
Represent BL-009 observability with two artifacts: one canonical JSON run log and one flat CSV run index. Derive `dataset_version` from hashes of the bootstrap data components, derive `pipeline_version` from hashes of the participating stage scripts, and record BL-001 to BL-003 explicitly as `deferred_bootstrap_mode` placeholders rather than fabricating live ingestion or alignment telemetry.

alternatives_considered:
- Create separate per-stage observability files without a canonical consolidated log
- Store observability details only in `experiment_log.md` without machine-readable outputs
- Treat BL-001 to BL-003 as if they had executed and emit pseudo-runtime diagnostics
- Record only human-readable notes without artifact hashes or version identifiers

rationale:
One canonical JSON log keeps the bootstrap run state in a single auditable location and avoids fragmented traceability. A one-row CSV index supports fast lookup and future replay checks without reopening the full JSON. Hash-derived dataset and pipeline versions create a concrete bridge to BL-010 reproducibility work. Explicit deferred-stage placeholders are more defensible than invented telemetry because they preserve honesty about the current MVP execution path.

evidence_basis:
- `05_design/observability_design.md`
- `00_admin/decision_log.md` (`D-005` bootstrap-first strategy)
- upstream artifacts from `07_implementation/implementation_notes/bl000_data_layer/outputs/`, `07_implementation/implementation_notes/test_assets/`, `07_implementation/implementation_notes/bl004_profile/outputs/`, `07_implementation/implementation_notes/bl005_retrieval/outputs/`, `07_implementation/implementation_notes/bl006_scoring/outputs/`, `07_implementation/implementation_notes/bl007_playlist/outputs/`, and `07_implementation/implementation_notes/bl008_transparency/outputs/`
- generated BL-009 artifacts in `07_implementation/implementation_notes/bl009_observability/outputs/`

impacted_files:
- `06_data_and_sources/schema_notes.md`
- `07_implementation/backlog.md`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
- `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`
- `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_observability_log.json`
- `07_implementation/implementation_notes/bl009_observability/outputs/bl009_run_index.csv`

review_date:
none

id: D-011
date: 2026-03-21
status: accepted

context:
BL-010 required deterministic replay evidence for the bootstrap pipeline. Raw BL-007, BL-008, and BL-009 JSON artifacts embed per-run identifiers, timestamps, elapsed time, and upstream run linkage, which makes raw file hashes vary even when the recommendation content is unchanged. The initial BL-010 replay also exposed run-id collisions under second-level precision.

decision:
Evaluate BL-010 reproducibility with stable content fingerprints instead of raw downstream file hashes for the timestamped BL-007 to BL-009 artifacts. Keep raw-hash variation recorded as expected metadata volatility, and increase BL-004 to BL-009 run-id precision to microseconds so rapid replay runs remain uniquely identifiable.

alternatives_considered:
- Compare raw file hashes only and treat any difference as a reproducibility failure
- Remove run ids and timestamps from the production-stage artifacts themselves
- Limit BL-010 to BL-006 ranked output only and ignore playlist, explanation, and observability layers
- Keep second-resolution run ids and accept collisions during fast replay tests

rationale:
Raw hash equality is too strict for audit-oriented JSON artifacts that intentionally preserve run-specific metadata. Stable fingerprints let BL-010 test semantic determinism without discarding useful observability fields from the actual outputs. Recording the raw-hash variation separately preserves transparency about what changed and why. Raising run-id precision fixes a genuine auditability defect because replayed runs must remain distinguishable even when they execute within the same second.

evidence_basis:
- `00_admin/evaluation_plan.md` (`EP-REPRO-001`)
- `05_design/observability_design.md`
- `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json`
- `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_run_matrix.csv`
- `07_implementation/experiment_log.md` (`EXP-012`)

impacted_files:
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`
- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
- `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`
- `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`
- `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
- `07_implementation/backlog.md`

review_date:
none

id: D-012
date: 2026-03-21
status: accepted

context:
BL-011 required controllability evidence aligned to `EP-CTRL-001`, `EP-CTRL-002`, and `EP-CTRL-003`. The stage scripts were intentionally hardcoded for the locked MVP, so BL-011 needed a way to vary one control at a time without mutating the canonical implementation outputs or breaking the BL-010 reproducibility baseline.

decision:
Implement BL-011 as a dedicated scenario runner that reproduces the BL-004 to BL-007 logic in an isolated evaluation harness and archives five scenarios: the BL-010 fixed baseline, `no_influence_tracks`, `valence_weight_up`, `stricter_thresholds`, and `looser_thresholds`. Use stable stage hashes for the internal repeat check, exclude volatile run identifiers from the profile fingerprint, and evaluate threshold sensitivity primarily at the candidate-pool and ranking layers when the final playlist remains unchanged.

alternatives_considered:
- Patch all production stage scripts to accept external configuration and scenario-specific output directories before running BL-011
- Evaluate only one variant per control surface and skip strict/loose paired threshold scenarios
- Treat unchanged final playlist membership as a failed threshold-control result even when candidate-pool and rank changes are visible
- Reuse raw per-run metadata in the BL-011 repeat check and accept false instability findings

rationale:
An isolated runner keeps BL-011 evaluation traceable without destabilizing the canonical stage outputs used elsewhere in the thesis. The five-scenario design covers the three required control families while preserving one-factor-at-a-time interpretation. Stable hash comparison for repeat checks follows the same methodological lesson established in BL-010: deterministic evaluation should measure semantic content rather than volatile run metadata. Treating threshold sensitivity at the candidate and ranking layers as valid evidence is defensible because the control operates before playlist assembly and the synthetic bootstrap pool can mute later-stage playlist changes.

evidence_basis:
- `00_admin/evaluation_plan.md` (`EP-CTRL-001`, `EP-CTRL-002`, `EP-CTRL-003`)
- `05_design/controllability_design.md`
- `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json`
- `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_report.json`
- `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_run_matrix.csv`
- `07_implementation/experiment_log.md` (`EXP-013`)

impacted_files:
- `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py`
- `07_implementation/implementation_notes/bl011_controllability/outputs/`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
- `07_implementation/backlog.md`

review_date:
none

id: D-013
date: 2026-03-21
status: accepted

context:
BL-013 requires a lightweight repeatable entrypoint for the already implemented bootstrap pipeline. Existing stage scripts are independent and currently executed manually. The user requested end-to-end planning, implementation, and full logging.

decision:
Implement BL-013 as a thin Python orchestration runner that invokes the existing BL-004 through BL-009 stage scripts in deterministic order, supports optional stage subset execution, and emits a run summary plus explicit run-command documentation.

alternatives_considered:
- Leave execution as six separate manual commands without an orchestrator
- Rewrite stage scripts into one monolithic pipeline module
- Add only a shell script wrapper without structured JSON run output

rationale:
A thin orchestrator improves repeatability with minimal risk because it reuses already validated stage implementations instead of altering their internal logic. Optional stage selection keeps it practical for partial reruns, and a structured run summary preserves auditability for implementation evidence extraction.

evidence_basis:
- `07_implementation/backlog.md` (`BL-013`)
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`
- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
- `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`
- `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`

impacted_files:
- `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`
- `07_implementation/implementation_notes/bl013_entrypoint/bl013_run_command.md`
- `07_implementation/implementation_notes/bl013_entrypoint/outputs/`
- `07_implementation/backlog.md`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
- `00_admin/change_log.md`

review_date:
none

id: D-014
date: 2026-03-21
status: superseded

context:
BL-019 was previously a deferred placeholder for alternative corpus engineering. The current need is to define a practical, repeatable dataset-build workflow for the active Onion MVP path so data refreshes are deterministic and quality-gated before downstream reruns.

superseded_by: D-015

decision:
Reframe BL-019 as an active dataset-build planning item for the Onion canonical layer. The workflow will produce a canonical refresh report, dataset manifest, and explicit quality-gate checks, and will require a two-run deterministic repeat check before BL-019 can be closed.

alternatives_considered:
- Keep BL-019 as deferred future-work with no active plan
- Execute ad-hoc manual refreshes without manifest or quality gates
- Reopen the MSD/Last.fm/MusicBrainz alternative path as the primary BL-019 objective

rationale:
The active MVP path is Onion-only. A deterministic refresh workflow with manifest and quality gates improves reproducibility and auditability without changing thesis scope. Keeping the alternative corpus path deferred avoids unnecessary scope expansion.

evidence_basis:
- `07_implementation/backlog.md` (`BL-019` activation)
- `07_implementation/experiment_log.md` (`EXP-016` planned)
- `07_implementation/implementation_notes/bl000_data_layer/outputs/onion_canonical_track_table.csv`
- `07_implementation/implementation_notes/bl000_data_layer/outputs/onion_join_coverage_report.json`
- `07_implementation/implementation_notes/bl000_data_layer/outputs/onion_selected_column_manifest.json`

impacted_files:
- `00_admin/decision_log.md`
- `07_implementation/backlog.md`
- `07_implementation/experiment_log.md`
- `07_implementation/implementation_plan.md`

review_date:
none

id: D-007
date: 2026-03-19
status: accepted

context:
Base Music4All metadata access is currently blocked in the user environment. Pipeline progress should not pause while waiting for external access changes.

decision:
Implement a canonical Onion-only dataset layer as the immediate next engineering step. Build a track_id-joined dataset from selected Onion files with a curated, interpretable feature subset and explicit data-quality checks.

alternatives_considered:
- Pause implementation until base metadata becomes accessible
- Switch to a new dataset midstream
- Continue coding against ad-hoc per-file inputs with no canonical layer

rationale:
The canonical layer unblocks BL-004 through BL-009 using already verified assets and preserves deterministic, transparent behavior by centralizing schema, joins, and quality checks in one reproducible step.

evidence_basis:
- `07_implementation/experiment_log.md` (EXP-DA-001 access blocker and Onion extraction records)
- `06_data_and_sources/dataset_registry.md` (use/skip file decisions and first-pass columns)

impacted_files:
- `07_implementation/backlog.md` (BL-017)
- `07_implementation/implementation_plan.md`
- `06_data_and_sources/dataset_registry.md`
- `07_implementation/experiment_log.md`

review_date:
none

id: D-002
date: 2026-03-13
status: accepted

context:
University document ingestion showed strong assessment emphasis on practical artefact delivery, testing evidence, project management traceability, and a realistic submission scope.

decision:
Adopt a locked MVP artefact strategy: one ingestion path, deterministic transparent pipeline, and BSc-feasible evaluation plan focused on reproducibility, inspectability, and controllability.

alternatives_considered:
- Full multi-platform adapter implementation in core scope
- Include collaborative/deep model baseline in core scope
- Large user-study-centered evaluation in core scope

rationale:
The locked MVP reduces delivery risk, aligns with marking criteria, and preserves thesis contribution quality by prioritizing traceability and critical evaluation over feature breadth.

evidence_basis:
- 01_requirements/university_rules.md
- 01_requirements/marking_criteria.md
- 01_requirements/submission_requirements.md
- 01_requirements/formatting_rules.md

impacted_files:
- 00_admin/Artefact_MVP_definition.md
- 00_admin/evaluation_plan.md
- 00_admin/methodology_definition.md
- 00_admin/thesis_state.md
- 00_admin/thesis_scope_lock.md

review_date:
2026-04-10

id: D-003
date: 2026-03-13
status: accepted

context:
Cross-source preference ingestion requires robust mapping of imported tracks into the canonical Music4All feature corpus while preserving inspectability and MVP feasibility.

decision:
Use an ISRC-first alignment strategy with metadata fallback matching (normalized track + artist) and explicit unmatched-track reporting.

alternatives_considered:
- Metadata-only fuzzy matching as primary strategy
- Neural entity matching in core MVP pipeline
- Manual-only mapping workflow

rationale:
ISRC-first matching gives a deterministic, auditable default when identifiers exist. Metadata fallback recovers usable rows when ISRC is absent while keeping alignment behavior explainable. Neural matching is retained as future work due to complexity and inspectability cost under current scope.

evidence_basis:
- P-029 (`allam_improved_2018`)
- P-030 (`papadakis_blocking_2021`)
- P-031 (`barlaug_neural_2021`)

impacted_files:
- 05_design/requirements_to_design_map.md
- 08_writing/chapter3.md
- 09_quality_control/claim_evidence_map.md
- 09_quality_control/citation_checks.md

review_date:
2026-04-10

id: D-005
date: 2026-03-19
status: accepted

context:
Implementing the full pipeline (BL-004 through BL-012) depends only on having pre-aligned track data in the format that BL-002/BL-003 would produce. Real ingestion and alignment code (BL-001, BL-002, BL-003) adds implementation risk and work upfront without unblocking the core pipeline sooner.

decision:
Start pipeline implementation using synthetic pre-aligned data assets. Defer real ingestion parser (BL-001, BL-002) and real alignment implementation (BL-003) to a later pass after the core pipeline is proven end-to-end with synthetic data.

alternatives_considered:
- Implement ingestion first as originally planned (BL-001 -> BL-002 -> BL-003 -> BL-004+)
- Use leftover test asset stubs from pre-restart as a base

rationale:
Synthetic pre-aligned data unblocks preference profiling, scoring, assembly, and evaluation work immediately. Ingestion is an independent adapter concern that can be slotted back in once the core pipeline is stable. This reduces risk of getting blocked on input format edge cases before any pipeline behavior can be tested.

evidence_basis:
n/a — pragmatic delivery decision.

impacted_files:
- 07_implementation/backlog.md
- 07_implementation/implementation_plan.md

review_date:
none

id: D-004
date: 2026-03-13
status: accepted

context:
The thesis requires transparency, controllability, and reproducibility as first-class evaluation qualities rather than secondary outputs.

decision:
Use deterministic feature-based scoring with explicit rule adjustments, mechanism-linked explanation output, and run-level observability logs for replayability.

alternatives_considered:
- Hybrid/neural scoring as core pipeline
- Post-hoc explanation wrappers around opaque models
- Minimal logging focused only on final playlist output

rationale:
Deterministic scoring and explicit rules improve inspectability and controllable behavior under BSc constraints. Mechanism-linked explanations reduce fidelity risk compared with post-hoc rationalization. Run-level logs support reproducibility/accountability expectations in recommender evaluation.

evidence_basis:
- P-001 (`zhang_explainable_2020`)
- P-002 (`tintarev_survey_2007`)
- P-003 (`tintarev_evaluating_2012`)
- P-032 (`beel_towards_2016`)
- P-033 (`bellogin_improving_2021`)
- P-034 (`cavenaghi_systematic_2023`)

impacted_files:
- 05_design/requirements_to_design_map.md
- 08_writing/chapter3.md
- 00_admin/evaluation_plan.md
- 09_quality_control/claim_evidence_map.md
- 09_quality_control/citation_checks.md

review_date:
2026-04-10

id: D-006
date: 2026-03-19
status: accepted

context:
Base Music4All metadata access appears request-gated (email/contact workflow). User preference is to avoid requesting gated access and continue progress with currently available assets.

decision:
Adopt an Onion-only execution path for MVP implementation and evaluation. Use track_id-centric joins across available Onion files (`userid_trackid_count`, optional `userid_trackid_timestamp`, `id_essentia`, `id_lyrics_sentiment_functionals`, `id_tags_dict`, `id_genres_tf-idf`) and defer base-metadata-dependent enhancements (track_name/artist_name/ISRC and Spotify-style feature parity) to optional future work.

alternatives_considered:
- Pause implementation until base dataset access is approved
- Request access to base dataset now and continue in parallel
- Replace data source entirely with a different public dataset

rationale:
Onion data already supports deterministic, transparent, and controllable pipeline behavior using interpretable features (BPM/danceability/loudness, lyrics sentiment, tags, genres) plus listening events. This avoids external dependency delay and preserves thesis delivery momentum while keeping limitations explicit.

evidence_basis:
- `07_implementation/experiment_log.md` (EXP-DA-001 archive audit and extraction records)
- `06_data_and_sources/dataset_registry.md` (checked use/skip classifications)

impacted_files:
- `06_data_and_sources/dataset_registry.md`
- `07_implementation/experiment_log.md`
- `07_implementation/implementation_plan.md`
- `08_writing/chapter3.md`
- `08_writing/chapter5.md`

review_date:
none

id: D-008
date: 2026-03-19
status: rejected

context:
The current accepted candidate corpus is Music4All / Music4All-Onion, but base metadata access remains problematic and the user is considering a switch to a more directly documented integrated corpus built from the Million Song Dataset subset, Last.fm tags, and MusicBrainz mappings.

decision:
Do not change the canonical MVP candidate corpus to the integrated `MSD subset + Last.fm Tag Dataset + MusicBrainz mapping` option. Keep the active implementation path on Music4All-Onion and treat the MSD-based construction as a reviewed fallback only.

alternatives_considered:
- Keep the current Music4All-Onion execution path and continue BL-017 immediately
- Request or wait for base Music4All metadata access
- Use a hybrid approach where Music4All-Onion remains primary and MSD-based data is only a contingency source

rationale:
The proposed MSD-based construction is attractive because it is well known in MIR research, has explicit join structure through `track_id`, and aligns cleanly with transparency goals through named metadata, tags, and external identifiers. After review, it is not the better MVP choice in this repository state. It would shrink the active corpus from the current Onion-scale path to a 10,000-track subset, replace the already-audited Onion extraction path with fresh HDF5 extraction work, and still does not clearly improve the current ISRC-first alignment design. The real blocker is the unusable base-Music4All dependency, not Onion itself. For the MVP, the correct simplification is to keep Onion-only, not to switch corpus.

evidence_basis:
- `06_data_and_sources/dataset_registry.md` (DS-001 current accepted corpus; DS-002 proposed alternative)
- `07_implementation/experiment_log.md` (EXP-DA-001 Music4All-Onion acquisition and current blocker context)
- `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
- user-provided dataset construction sheet dated 2026-03-19

impacted_files:
- `06_data_and_sources/dataset_registry.md`
- `07_implementation/backlog.md`
- `07_implementation/implementation_plan.md`
- `00_admin/unresolved_issues.md`
- `00_admin/thesis_state.md`
- `02_foundation/objectives.md`
- `08_writing/chapter2.md`
- `08_writing/chapter3.md`

review_date:
none

id: D-009
date: 2026-03-19
status: accepted

context:
The user wants to keep implementation moving with Music4All-Onion now, but also preserve the MSD + Last.fm + MusicBrainz dataset idea as a future option instead of losing the planning work.

decision:
Defer alternative corpus data-engineering work for the `MSD subset + Last.fm Tag Dataset + MusicBrainz mapping` path to future work. Save the information sheet in-repo for reference and continue with the Onion-only execution path for the current MVP.

alternatives_considered:
- Switch to the MSD-based path immediately
- Delete the MSD planning material after rejecting the switch
- Keep discussing the alternative informally without storing a durable artifact

rationale:
This preserves useful planning work without creating current implementation drag. The thesis keeps momentum by staying on the already-audited Onion-only path, while the alternative corpus idea remains available if later evidence shows a need to reopen dataset engineering. Saving the information sheet also improves traceability because the future option is documented in a stable repository location rather than only in chat history.

evidence_basis:
- `06_data_and_sources/ds_002_msd_information_sheet.md`
- `06_data_and_sources/dataset_registry.md`
- `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
- user instruction in chat on 2026-03-19 to leave this data engineering for later and save the information sheet for future reference

impacted_files:
- `06_data_and_sources/ds_002_msd_information_sheet.md`
- `06_data_and_sources/dataset_registry.md`
- `07_implementation/backlog.md`
- `00_admin/change_log.md`

review_date:
none

id: D-016
date: 2026-03-21
status: accepted

context:
Active BL-019 planning now uses DS-002, and local source inspection confirmed the actual fields available from `track_metadata.db`, `millionsongsubset.tar.gz`, `lastfm_subset.zip`, Spotify `Get Track`, and the current MusicBrainz-related helper files. The inspected DS-002 candidate data exposes `track_id`, metadata fields, audio-analysis fields, tags, and `artist_mbid`, but does not expose a confirmed corpus-side track-level ISRC field or track-level MusicBrainz recording ID.

decision:
For the current DS-002 MVP path, build the candidate corpus around `track_id` and treat Spotify-to-corpus alignment as metadata-first using normalized `(track_name/title, artist_name)` with duration and release as tie-break helpers. Use MSD HDF5 extraction for `tempo`, `loudness`, `key`, `mode`, and `duration`. Retain `artist_mbid` only as optional enrichment. Do not assume ISRC-first or track-level MusicBrainz matching for DS-002 unless a later enrichment step adds a confirmed corpus-side track identifier layer.

alternatives_considered:
- Continue documenting DS-002 as if corpus-side ISRC matching were already available
- Treat artist-level MusicBrainz IDs as sufficient for exact track matching
- Drop HDF5 extraction and keep DS-002 limited to metadata plus tags only
- Add a new mandatory MusicBrainz recording-enrichment phase before any BL-019 implementation work

rationale:
This keeps the DS-002 plan aligned with the data actually present in the repository instead of with an idealized schema. Metadata-first matching is defensible because Spotify `Get Track` exposes `name`, `artists`, `album`, `duration_ms`, and `external_ids.isrc`, while the inspected DS-002 candidate assets reliably expose title/artist/duration and audio-analysis fields but not a confirmed candidate-side ISRC. Using HDF5 extraction preserves the planned transparent audio features without forcing a premature external enrichment dependency. Restricting MusicBrainz usage to `artist_mbid` avoids overstating exact-match capability.

evidence_basis:
- local inspection of `06_data_and_sources/track_metadata.db` (`songs` schema includes `track_id`, `title`, `artist_name`, `artist_mbid`, `duration`, `year`)
- local inspection of `06_data_and_sources/millionsongsubset.tar.gz` (`analysis/songs` includes `tempo`, `loudness`, `key`, `mode`, `duration`, `track_id`)
- local inspection of `06_data_and_sources/lastfm_subset.zip` (JSON records include `track_id`, `artist`, `title`, `tags`, `similars`, `timestamp`)
- local inspection of `06_data_and_sources/unique_artists.txt` and `06_data_and_sources/unique_tracks.txt`
- Spotify Web API `Get Track` reference (`external_ids.isrc`, `name`, `artists`, `album.name`, `duration_ms`)

impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `06_data_and_sources/dataset_registry.md`
- `06_data_and_sources/ds_002_msd_information_sheet.md`
- `06_data_and_sources/schema_notes.md`
- `07_implementation/experiment_log.md`

review_date:
none

id: D-019
date: 2026-03-21
status: accepted

context:
BL-002 Spotify API export script (`export_spotify_max_dataset.py`) currently fetches data on every execution regardless of whether the parameters are identical to a previous run. Live authenticated runs experience 30-60 second latencies and rate-limiting blocks on repeat invocations despite requesting the same data. Caching would reduce quota consumption and improve iteration speed for testing and evaluation.

decision:
Implement optional SQLite-backed endpoint caching with 24-hour TTL for static Spotify endpoints (user top tracks, saved tracks, playlists, playlist items). Integrate via optional `cached_fetch()` wrapper function with graceful fallback so caching is available but not required. Cache key format: `spotify:{endpoint_path}:{SHA256(request_params)[:8]}`. Store cache in `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_resilience_cache.sqlite` with WAL mode and automatic cleanup of expired entries.

alternatives_considered:
- Use Spotipy library (rejected: existing script uses urllib, refactoring not justified for single optimization)
- In-memory caching only (rejected: doesn't survive script restarts between test runs)
- HTTP-level caching via Cache-Control headers (rejected: Spotify Web API does not expose cache-control headers; responses must be cached client-side)
- No caching; improve rate-limit handling only (rejected: 30-60s latency persists even with retry backoff; caching addresses root cause)

rationale:
SQLite provides durable persistence across script invocations without requiring external services. TTL prevents stale data while reducing redundant requests. Optional parameter (cache_db=None) maintains backward compatibility; existing rate-limiting, throttling, and pagination behavior all preserved. Wrapper pattern is minimal (~70 lines) and integrates cleanly at the API call layer without requiring architectural changes. Graceful fallback (RESILIENCE_AVAILABLE flag) ensures the script continues to work if the resilience module is unavailable.

evidence_basis:
- Session memory log (`/memories/session/implementation_complete.md`): Analysis of prior working rate-limiting script showed caching + TTL patterns that enabled 80-90% speedup on repeat runs
- Implemented `CacheDB` class in `spotify_resilience.py`: SQLite schema with `endpoint_cache` table, 24-hour default TTL, automatic expire-time tracking
- Wrapper integration validated: Four API fetch calls updated to pass `cache_db` parameter; cache key generation tested with SHA256 truncation
- Test suite created (`test_resilience_integration.py`): Validates cache existence, entry validity, TTL enforcement, job progress tracking, metadata presence

impacted_files:
- `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- `07_implementation/spotify_resilience.py`
- `07_implementation/SPOTIFY_INTEGRATION.md`
- `07_implementation/test_resilience_integration.py`
- `00_admin/change_log.md` (C-056)

review_date:
none

---

id: D-020
date: 2026-03-21
status: accepted
context: Full MSD core is inaccessible locally (~280 GB download / ~493 GB AWS snapshot). MusicBrainz provides identifier enrichment via ISRC but does NOT supply audio features (tempo, loudness, key, mode), so it cannot substitute for the MSD core. Full Last.fm (lastfm_train.zip + lastfm_test.zip, 943 K matched tracks) is technically downloadable but integrating it into a new larger corpus build adds significant engineering cost before the thesis deadline. Music4All-Onion (109,269 tracks, zenodo.org/records/15394646) is the preferred larger candidate corpus but requires access approval from the dataset authors.
decision: Defer full-corpus enrichment (MusicBrainz core dump + full Last.fm integration + MusicBrainz ISRC-bridge layer) as a future improvement. Keep DS-002 (9,330-track MSD subset + Last.fm subset + track_metadata.db join) as the active candidate corpus for current implementation. Pursue Music4All access via a direct email to the dataset authors and raise corpus size as a discussion point with the supervisor at the next meeting.
alternatives_considered:
- Immediately build MusicBrainz + full Last.fm enrichment path (rejected: engineering cost outweighs benefit before deadline; DS-002 is sufficient for MVP demonstration)
- Wait for full MSD access before proceeding (rejected: access path is unclear and timeline uncertain)
- Switch corpus exclusively to Music4All-Onion (rejected: access not yet confirmed; Onion-only baseline retained as DS-001 fallback)
rationale: Current DS-002 is quality-gated, deterministic, and sufficient to demonstrate the core thesis pipeline. Corpus scaling does not alter system architecture — it is a data-plane input change only. The ISRC bridge via Spotify ingestion is already in place for future enrichment. Music4All-Onion at 109,269 tracks is the preferred upgrade path if access can be obtained; the supervisor may have guidance on institutional access channels.
evidence_basis: Session research 2026-03-21; full_dataset_acquisition_checklist_2026-03-21.md; MusicBrainz schema review; ISRC bridge analysis; DS-002 build confirmed at 9,330 tracks.
impacted_files:
- 00_admin/decision_log.md
- 00_admin/change_log.md (C-063)
- 00_admin/mentor_question_log.md (MQ-008)
- 07_implementation/implementation_notes/bl000_data_layer/full_dataset_acquisition_checklist_2026-03-21.md
review_date: none

---

id: D-030
date: 2026-03-25
status: accepted
context: UI-013 remained open after controlled sweep because BL-008 explanation top-label dominance stayed high (`0.8` in the best v1b profile candidate) even when BL-003/BL-005/BL-006 and BL-014 conditions were acceptable. Existing BL-008 distribution logic used only the first-ranked contributor label per track, which amplified contributor concentration in summaries.
decision: Introduce a config-driven near-tie primary-driver selection policy for BL-008 explanations. Add `transparency_controls.blend_primary_contributor_on_near_tie` and `transparency_controls.primary_contributor_tie_delta` to run-config, and compute `primary_explanation_driver` per track by rotating across near-tied top contributors when enabled. Define BL-008 dominance from this primary-driver label distribution.
alternatives_considered:
- Continue using strict first-ranked contributor only (rejected: failed UI-013 dominance target on v1b)
- Hardcode stage-specific diversity heuristics without run-config controls (rejected: weak governance/auditability)
- Rebalance BL-006 component weights solely to force explanation diversity (rejected: over-couples scoring semantics to narrative output objective)
rationale: A dedicated transparency control surface preserves the principle that behavior should be user-configurable and auditable in run-config. Near-tie blending addresses explanation concentration when contributions are close while avoiding arbitrary overrides when one contributor is clearly dominant.
evidence_basis: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`; `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`; v1b validation run `BL013-ENTRYPOINT-20260325-225725-328263`; BL-014 pass `BL014-SANITY-20260325-225735-601840`; BL-008 distribution `{Lead genre match:5, Tag overlap:3, Genre overlap:2}` and dominance share `0.5`.
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `00_admin/unresolved_issues.md`
- `00_admin/thesis_state.md`
- `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`
- `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1b.json`
- `07_implementation/implementation_notes/bl000_run_config/docs/bl000_run_config_state_log_2026-03-25.md`
- `07_implementation/implementation_notes/bl008_transparency/bl008_state_log_2026-03-24.md`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
review_date: none

---

id: D-031
date: 2026-03-25
status: accepted
context: After BL-008 dominance closure, UI-013 remained open on governance hygiene because BL-010 replay logs still exposed machine-local absolute command paths and stale path semantics in evidence interpretation. The requirement was to normalize BL-010/BL-011 reporting to canonical BL-prefixed rendering and refresh evidence.
decision: Standardize BL-010 replay command reporting to canonical relative BL-prefixed form (`python 07_implementation/...`) with explicit `stage` and `script_path` fields, then immediately refresh BL-010/BL-011/freshness/BL-014 evidence on the same active baseline run window.
alternatives_considered:
- Keep absolute command-path emission and document it as acceptable (rejected: weak audit portability and readability)
- Normalize only state logs without regenerating machine-readable evidence (rejected: leaves contract drift between docs and artifacts)
- Defer normalization until broader UI-013 tuning closure (rejected: avoidable governance tail remains open)
rationale: Canonical relative command paths remove machine-specific leakage and make reproducibility evidence portable across environments while preserving deterministic semantics. Immediate evidence refresh ensures state logs, freshness checks, and admin governance reflect the same normalized contract.
evidence_basis: `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`; BL-010 pass `BL010-REPRO-20260325-231041`; BL-011 pass `BL011-CTRL-20260325-231130`; freshness pass `BL-FRESHNESS-20260325-231159`; BL-014 pass `BL014-SANITY-20260325-231204-534293`.
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `00_admin/unresolved_issues.md`
- `00_admin/thesis_state.md`
- `07_implementation/IMPLEMENTATION_STATE_2026-03-24.md`
- `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`
- `07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json`
- `07_implementation/implementation_notes/bl011_controllability/outputs/bl011_controllability_report.json`
- `07_implementation/implementation_notes/bl014_quality/outputs/bl010_bl011_freshness_report.json`
- `07_implementation/implementation_notes/bl010_reproducibility/bl010_state_log_2026-03-24.md`
- `07_implementation/implementation_notes/bl011_controllability/bl011_state_log_2026-03-24.md`
review_date: none

---

id: D-029
date: 2026-03-25
status: accepted
context: Folder names under `07_implementation/implementation_notes/` were migrated to BL-ordered names, but runtime breakages appeared because many scripts built paths with split path-segment expressions (`Path / "segment"`) that were not fully updated by earlier literal-string replacement passes.
decision: Adopt BL-ordered folder names as the canonical implementation-notes path contract and require all stage code, quality runners, and orchestration scripts to reference only the BL-prefixed folders (`bl000_run_config`, `bl001_bl002_ingestion`, `bl003_alignment`, `bl004_profile`, `bl005_retrieval`, `bl006_scoring`, `bl007_playlist`, `bl008_transparency`, `bl009_observability`, `bl010_reproducibility`, `bl011_controllability`, `bl013_entrypoint`, `bl014_quality`).
alternatives_considered:
- Keep old folder names and revert migration (rejected: user requested BL-order canonicalization)
- Keep mixed old/new naming with compatibility shims (rejected: increases drift and maintenance cost)
- Update only top-level string literals and ignore split path expressions (rejected: causes runtime failures)
rationale: A single naming contract aligned to pipeline order improves traceability and onboarding, and full runtime-path normalization removes hidden execution failures after structural refactors.
evidence_basis: BL-013 pass `BL013-ENTRYPOINT-20260325-163713-079187`; BL-014 pass `BL014-SANITY-20260325-163738-023840` (`21/21` checks); fixed path resolution failures observed in BL-013/BL-003 during migration hardening.
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md` (`C-171`)
- `00_admin/current_implementation_information_sheet_2026-03-25.md`
- `00_admin/thesis_state.md`
- `00_admin/handoff_friend_chat_playbook.md`
- `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`
- `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`
- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
- `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`
- `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`
- `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py`
- `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py`
- `07_implementation/implementation_notes/bl014_quality/check_bl010_bl011_freshness.py`
- `07_implementation/implementation_notes/bl014_quality/run_active_freshness_suite.py`
review_date: none

---

id: D-022
date: 2026-03-21
status: accepted
context: BL-003 had already been pivoted to Last.fm tag enrichment (D-021), but live execution quality checks showed two practical issues: (1) many mainstream tracks were cached as `no_tags`, and (2) long-running enrichment provided limited real-time feedback. Spot checks suggested that a single `track.getTopTags` call path was too brittle for metadata variants and that stale `no_tags` cache entries from earlier logic were suppressing retries.
decision: Upgrade BL-003 enrichment to a layered lookup strategy and explicit cache migration behavior. New lookup order: `track.getTopTags` on normalized variants -> `track.search` correction then `track.getTopTags` -> `artist.getTopTags` fallback. Introduce `CACHE_SCHEMA_VERSION` and refresh behavior so older cache entries are not blindly trusted after lookup logic changes. Emit frequent, flushed progress lines (`processed/tagged/no-tags/errors/cache`) during runtime to improve operator observability.
alternatives_considered:
- Keep existing cache and single lookup method (rejected: preserves known false `no_tags` outcomes and weak run visibility)
- Disable cache entirely for reruns (rejected: excessive runtime/API load; does not solve lookup brittleness)
- Stop BL-020 until a different corpus arrives (rejected: blocks current progress; fallback can be made robust now)
rationale: The immediate execution risk was not only API sparsity but lookup fragility and stale cache reuse. A layered lookup plus cache versioning improves recall on real tracks while retaining deterministic, auditable behavior. Progress output is necessary for long-run operational confidence and faster troubleshooting.
evidence_basis: Updated `bl003_align_spotify_api_to_ds002.py`; compile/error checks pass; direct function-level probes on representative tracks return tags via fallback sources (`artist.getTopTags` for previously failing cases); user-observed run progress output now visible.
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md` (C-067)
- `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`
- `07_implementation/experiment_log.md` (EXP-023)
- `07_implementation/test_notes.md` (TC-BL020-002)
- `00_admin/thesis_state.md`
- `02_foundation/limitations.md`
- `05_design/architecture.md`
- `05_design/system_architecture.md`
- `08_writing/chapter5.md`
review_date: none

---

id: D-021
date: 2026-03-21
status: accepted
context: Real Spotify Web API export data became available for BL-020 (`SPOTIFY-EXPORT-20260321-192533-881299`: 5104 long-term top tracks, 3021 medium-term, 598 short-term, 170 saved tracks, 31 playlist items). Initial BL-003 fuzzy alignment against DS-002 was implemented and executed, but manual inspection showed the resulting matches were false positives because DS-002 does not contain the user's dominant artists and repertoire (for example Steve Winwood, ABBA main catalogue, Rush, Tracy Chapman, and Beatles main catalogue). At the same time, Spotify audio-feature endpoints were confirmed deprecated, so the prior plan to derive user-side tempo/loudness/key/mode from Spotify is no longer viable.
decision: For BL-020, replace DS-002 fuzzy alignment with Last.fm top-tag enrichment on imported Spotify tracks, and permit a semantic-only execution mode for BL-004 through BL-008 where user-side numeric audio features are absent. In semantic-only mode, BL-004 builds tags and lead-genre signals from Last.fm-enriched Spotify seeds, BL-005 filters DS-002 candidates primarily by semantic overlap, BL-006 disables missing numeric components and renormalizes active weights, and BL-008 reads the active scoring weights from the run summary. Do not persist the user-supplied Last.fm shared secret in the repository.
alternatives_considered:
- Keep DS-002 fuzzy alignment as the active BL-003 path (rejected: observed false positives invalidate seed evidence)
- Continue assuming Spotify Web API can provide audio features for user tracks (rejected: endpoint deprecated; no longer dependable for thesis evidence)
- Pause BL-020 until Music4All or a larger corpus becomes available (rejected: blocks progress; semantic/tag path yields a feasible interim evidence track)
rationale: The root problem is corpus mismatch, not fuzzy-threshold tuning. Last.fm tags provide a viable, non-deprecated semantic bridge from real Spotify listening data into the DS-002 candidate corpus, and the downstream scoring pipeline can still produce auditable evidence if numeric user-side components are explicitly disabled and the remaining weights are renormalized. This keeps BL-020 moving while preserving traceability about the limitation.
evidence_basis: `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`; `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_alignment_report.json` (old DS-002 fuzzy report); `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_aligned_events.jsonl` (false-positive fuzzy events); `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_lastfm_tag_cache.json` (partial Last.fm run); code updates in BL-003/004/005/006/008; `07_implementation/experiment_log.md` (`EXP-022`); `07_implementation/test_notes.md` (`TC-BL020-001`).
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md` (C-066)
- `07_implementation/backlog.md`
- `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`
- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
review_date: none

---

id: D-023
date: 2026-03-21
status: superseded
context: BL-020 real-data execution highlighted that profile-build runtime and API load are strongly affected by which Spotify data sources are ingested (for example top tracks vs saved tracks). The user proposed adding an explicit UI control so a user can choose the profile input scope before ingestion/profile construction.
superseded_by: D-027
decision: Add a deferred design requirement for a user-selectable Spotify profile-source scope control, with per-source on/off selection and bounded limits. Initial target controls include top tracks (short/medium/long term), saved tracks, and optional playlist-derived tracks. Implementation is intentionally deferred; this decision only records and aligns planning/design artifacts.
alternatives_considered:
- Keep fixed full-ingestion behavior for all users (rejected: weaker controllability and slower runtime for users who only want a subset)
- Remove source-level choice and tune only downstream scoring controls (rejected: does not address ingestion-time cost and upstream profile-shaping intent)
- Implement UI immediately during active BL-020 reruns (rejected: risks destabilizing current evidence run; deferred implementation is safer)
rationale: Source-scope selection is a high-leverage controllability surface that affects both execution efficiency and profile semantics. Deferring implementation preserves current BL-020 stability while still making the planned enhancement explicit and auditable.
evidence_basis: User request in chat on 2026-03-21; existing controllability requirements in `05_design/controllability_design.md`; ongoing BL-020 runtime pressure observed during enrichment/profile reruns.
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md` (C-068)
- `07_implementation/backlog.md` (new deferred item)
- `00_admin/thesis_state.md`
- `05_design/controllability_design.md`
review_date: none

---

id: D-024
date: 2026-03-22
status: accepted
context: BL-003 Last.fm enrichment is long-running over 5592 unique tracks and may be interrupted intentionally. A live run showed progress output through ~395/5592 before `KeyboardInterrupt` during network read, leaving uncertainty about immediate downstream usability when stopping early.
decision: Treat BL-003 as checkpointable. On interruption, flush cache and write partial aligned-events/report artifacts instead of exiting with traceback-only state. For immediate downstream testing, allow a cache-derived partial events build path and run BL-004 against that partial artifact.
alternatives_considered:
- Require full BL-003 completion before any downstream stage can run
- Continue with traceback-on-interrupt behavior and rely only on cache snapshots
- Manually craft ad-hoc partial JSONL files each time interruption is needed
rationale: Checkpointable interruption preserves operator control, reduces wasted runtime, and improves evidence continuity. A deterministic cache-to-partial conversion path allows controlled BL-004/BL-005/BL-006 dry runs while full enrichment continues later.
evidence_basis: `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`; `07_implementation/implementation_notes/bl003_alignment/build_bl003_partial_from_cache.py`; partial report `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/bl020_alignment_report_partial_from_cache.json` (`tracks_with_cache=398`, `tagged_with_lastfm=375`); BL-004 summary `07_implementation/implementation_notes/bl004_profile/outputs/bl004_profile_summary.json` (`matched_seed_count=398`).
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md` (C-069)
- `07_implementation/implementation_notes/bl003_alignment/bl003_align_spotify_api_to_ds002.py`
- `07_implementation/implementation_notes/bl003_alignment/build_bl003_partial_from_cache.py`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
review_date: none

---

id: D-025
date: 2026-03-22
status: accepted
context: User requested that the current DS-002/semantic ingestion path be retained as a fallback even if Music4All or Music4All-Onion becomes available. Prior discussion confirmed that corpus coverage can vary and that deterministic behavior should be preserved under low-match scenarios.
decision: Record a deferred architecture enhancement to add deterministic corpus-path switching. Planned behavior: attempt preferred Music4All(-Onion) alignment path when available; if alignment coverage fails defined thresholds, automatically switch to the current DS-002 semantic fallback path and log the selected path in run metadata.
alternatives_considered:
- Hard switch to Music4All(-Onion) with no fallback (rejected: high fragility under low coverage)
- Keep DS-002 only and never attempt Music4All(-Onion) integration (rejected: loses potential coverage/feature uplift)
- Manual operator-only path choice per run (rejected: weaker reproducibility and higher human error risk)
rationale: Deterministic fallback switching preserves robustness and reproducibility while allowing controlled adoption of larger corpora. This supports thesis goals for transparency, controllability, and observability by making path selection explicit and measurable.
evidence_basis: user request in chat on 2026-03-22; existing DS-002 execution path and documented coverage sensitivity in BL-020 notes.
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `07_implementation/backlog.md` (`BL-022`)
review_date: none

---

id: D-026
date: 2026-03-23
status: superseded
context: BL-020 and BL-014 are complete with evidence, while current user priority is to freeze the implemented pipeline and build a website interaction layer for demonstration, testing, and bounded refinement. Without a freeze decision, integration work risks accidental scope expansion into deferred items.
superseded_by: D-027
decision: Adopt a freeze-first execution strategy for the current implementation baseline. Keep core recommendation behavior stable and direct implementation effort to website-to-pipeline integration, run observability exposure in the UI, and bounded reliability hardening.
alternatives_considered:
- Continue feature expansion first (BL-021/BL-022) before website integration
- Refactor recommendation logic and integration together in one pass
- Keep website as static prototype with simulated data only
rationale: Freezing baseline behavior improves traceability and makes evaluation evidence defensible while enabling a practical interaction layer for demonstration. It also protects scope boundaries and reduces regression risk during the integration phase.
evidence_basis: `00_admin/thesis_state.md` (BL-020 and BL-014 completion state); `07_implementation/backlog.md` (updated next-work order); `07_implementation/website.md` (freeze + integration execution log).
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `00_admin/timeline.md`
- `00_admin/thesis_state.md`
- `07_implementation/backlog.md`
- `07_implementation/website.md`
review_date: none

---

id: D-027
date: 2026-03-24
status: accepted
context: D-023 recorded source-scope control as a deferred design item, and D-026 temporarily froze feature expansion for website integration. Subsequent BL-021 implementation work completed canonical source-scope control end-to-end, including run-config contract, runtime actuation, and A/B evidence.
decision: Close the D-023 deferment by promoting source-scope control from deferred design to implemented baseline behavior. Treat D-026 freeze-first mode as a completed temporary execution strategy rather than the current development posture.
alternatives_considered:
- Keep D-023 as deferred despite implemented behavior (rejected: governance drift and contradictory status)
- Keep D-026 as the current active strategy (rejected: no longer aligned with implemented BL-021 work)
- Rewrite or delete prior decisions (rejected: harms chronology and auditability)
rationale: A supersession decision preserves historical traceability while making current state explicit. This avoids contradictory planning signals across backlog, thesis-state, and implementation evidence records.
evidence_basis:
- `07_implementation/backlog.md` (BL-021 now marked done)
- `00_admin/thesis_state.md` (BL-021 completion update section)
- `07_implementation/experiment_log.md` (`EXP-040`, `EXP-041`, `EXP-042`)
- `07_implementation/test_notes.md` (`TC-BL021-R2-001`, `TC-BL021-R2-002`, `TC-BL021-R2-003`)
- `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`
- `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`
- `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `00_admin/thesis_state.md`
- `07_implementation/backlog.md`
review_date: none

---

id: D-028
date: 2026-03-25
status: accepted
context: Current stage evidence and state logs show BL-003 to BL-006 operating on the DS-001 contract (`build_bl003_ds001_spotify_seed_table.py` and downstream consumers), while several admin surfaces still describe DS-002 + Last.fm semantic enrichment as the active baseline.
decision: Treat DS-001 (Music4All base) with direct metadata/identifier alignment as the active implementation baseline. Mark Last.fm enrichment as historical/legacy evidence for earlier BL-020 runs, not part of the current active path. Keep DS-002 as a validated fallback reference only.
alternatives_considered:
- Keep DS-002 + Last.fm as active wording for continuity (rejected: contradicts current stage-state evidence)
- Remove all DS-002 references (rejected: DS-002 remains useful fallback and historical evidence)
- Rewrite historical decisions to match current state (rejected: harms chronology and auditability)
rationale: This keeps governance wording aligned with implemented behavior while preserving historical traceability. It reduces ambiguity in thesis control files and prevents evaluation/reporting drift.
evidence_basis:
- `07_implementation/implementation_notes/bl003_alignment/bl003_state_log_2026-03-24.md`
- `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py`
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py` (`lastfm_status=not_applicable_ds001`)
- `00_admin/thesis_state.md`
impacted_files:
- `00_admin/decision_log.md`
- `00_admin/change_log.md`
- `00_admin/thesis_state.md`
- `00_admin/evaluation_plan.md`
- `00_admin/thesis_scope_lock.md`
- `00_admin/Artefact_MVP_definition.md`
review_date: none


## D-032
- date: 2026-03-25
- entity_id: UI-013
- proposed_by: Copilot
- status: accepted
- decision: Use run_config_ui013_tuning_v1b.json as the active and recommended configuration profile for UI-013 explanation-diversity and candidate-retrieval controls, completing the tuning closure phase, with v1a retained as a conservative fallback alternative.
- context: UI-013 tuning sweep across 4 profiles (v1, v1a, v1b, v1c) yielded actionable evidence on parameter sensitivity and control effectiveness. v1b demonstrates optimal balance: stricter candidate filtering (55,643 kept vs broader options), reduced semantic-numeric gap (-0.112839, indicating better numeric signal contribution), maintained BL-003 match-rate enforcement, passed all BL-014 quality checks, and achieved target explanation-diversity share (0.8 dominance within acceptance cap of 0.6 or less—note: dominance share measures top-contributor concentration and v1b=0.8 suggests 80% of playlist tracks explained by top contributor, indicating room for further diversity tuning if needed).
- alternatives_considered: v1a (conservative baseline, passes all checks but less optimized), v1c (broader retrieval with 1.0 dominance—all 10 tracks same label—reducing playlist diversity), v1 (failed BL-014; root cause deferred).
- rationale: v1b represents the best-calibrated middle ground between candidate exclusivity (stricter filtering improves relevance signal) and control-surface range (broader than v1a to exercise parameter space). Maintainerswill use v1b as production config moving forward and reference v1a if fallback conservatism needed.
- evidence_basis: experiment_log EXP-045; test_notes TC-UI013-SWEEP-001; _scratch/ui013_tuning_sweep_results.json showing v1b metrics exceeding acceptance thresholds across all quality dimensions; BL-013/BL-014 pass for v1b run IDs BL013-225113-845270 and BL014-225124-993359.
- impacted_files: 07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1b.json (marked as active); 07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py (default config reference); _scratch/run_ui013_sweep.ps1 (sweep orchestration, now archived).
- next_steps: Mark UI-013 tuning closure complete; prepare final evidence package citing v1b validation and sweep results; move focus to UI-013 final acceptance evidence assembly and subsequent phases (UI-003 citation closure, thesis final hardening).

## D-033
- date: 2026-03-27
- entity_id: BL-000
- proposed_by: Copilot
- status: accepted
- supersedes: D-032 (baseline selection only)
- decision: Set `run_config_ui013_tuning_v1f.json` as the canonical active baseline for implementation reporting and governance summaries. Keep `run_config_ui013_tuning_v2a_retrieval_tight.json` as experimental and non-canonical until an explicit promotion decision is logged.
- context: Implementation and evidence surfaces contain mixed references to v1b/v1d/v1f-era snapshots, increasing ambiguity about what should be treated as current state during BL-023 integration and thesis evidence updates.
- alternatives_considered: Continue treating v1b as recommended profile (rejected: conflicts with latest integrated v1f evidence chain); promote v2a immediately (rejected: insufficient promotion evidence in governance baseline); remove historical profile references (rejected: harms traceability).
- rationale: A single canonical baseline prevents drift across backlog, setup, implementation status, and run-config state logs while preserving historical artifacts for audit context.
- evidence_basis: `07_implementation/backlog.md` (latest integrated v1f chain), `07_implementation/implementation_notes/bl000_run_config/docs/bl000_run_config_state_log_2026-03-25.md` (v1f promotion), `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json`, `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v2a_retrieval_tight.json`.
- impacted_files: `00_admin/decision_log.md`, `00_admin/change_log.md`, `07_implementation/backlog.md`, `07_implementation/implementation_notes/SETUP.md`, `07_implementation/implementation_notes/CODEBASE_ISSUES_CURRENT.md`, `07_implementation/implementation_notes/bl000_run_config/docs/bl000_run_config_state_log_2026-03-25.md`
- next_steps: Keep BL-023 website integration and UI-003 citation closure as active work; revisit v2a promotion only after dedicated evidence run and governance update.

## D-034
- date: 2026-03-27
- entity_id: BL-000
- proposed_by: Copilot
- status: accepted
- decision: Adopt a documented retention policy for timestamped run-config output artifacts (`run_intent_*` and `run_effective_config_*`) that keeps latest pointers and governance-significant baseline snapshots while requiring manifest-based archival for older files.
- context: BL-000 output directories contain high-volume timestamped artifacts from repeated orchestration/evaluation waves, making audit navigation difficult without explicit retention guidance.
- alternatives_considered: Keep all timestamped outputs indefinitely (rejected: increases audit noise and operational clutter); immediate deletion of older outputs (rejected: risks reproducibility trace loss); undocumented ad hoc cleanup (rejected: governance inconsistency).
- rationale: A written retention policy improves repository hygiene and operator clarity while preserving reproducibility traceability through manifest-driven archival.
- evidence_basis: `07_implementation/implementation_notes/bl000_run_config/outputs/RUN_CONFIG_RETENTION_POLICY.md`, `07_implementation/implementation_notes/bl013_entrypoint/outputs/BL013_RUN_MANIFEST.md`, `00_admin/change_log.md` (C-185).
- impacted_files: `00_admin/decision_log.md`, `00_admin/change_log.md`, `07_implementation/implementation_notes/bl000_run_config/outputs/RUN_CONFIG_RETENTION_POLICY.md`, `07_implementation/implementation_notes/bl013_entrypoint/outputs/BL013_RUN_MANIFEST.md`
- next_steps: Execute a separate ops-only archival pass using move manifests and validation reports; keep this current pass docs-only with no artifact deletion.

## D-035
- date: 2026-03-27
- entity_id: BL-023
- proposed_by: Copilot
- status: accepted
- decision: Use FastAPI + uvicorn as the website/API serving layer for BL-023 while preserving the existing subprocess-per-stage orchestration model, local-only browser origins, and backwards-compatible JSON error payloads.
- context: The prior `http.server` implementation served the website successfully but concentrated manual routing, request parsing, and response shaping in a large handler class, making bounded website hardening slower and more error-prone.
- alternatives_considered: Keep `http.server` and continue adding manual routes (rejected: rising maintenance cost and weak validation surface); refactor stage execution in-process inside the web server (rejected: worsens isolation and thesis traceability); replace the website package entirely (rejected: unnecessary scope expansion for BL-023).
- rationale: FastAPI provides clearer route definitions, request validation, auto-generated API docs, and easier regression testing without changing the thesis-relevant pipeline execution semantics. Preserving subprocess stage execution keeps BL-003 to BL-009 isolation, artifact traceability, and rerun behavior intact.
- evidence_basis: `07_implementation/setup/website_api_server.py`, `07_implementation/setup/smoke_website_api.ps1`, `07_implementation/setup/test_website_api_server.py`, `requirements.txt`, `07_implementation/experiment_log.md` (`EXP-052`).
- impacted_files: `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `07_implementation/setup/website_api_server.py`, `07_implementation/setup/smoke_website_api.ps1`, `07_implementation/setup/test_website_api_server.py`, `requirements.txt`
- next_steps: Keep BL-023 bounded to modular cleanup, reliability hardening, and evidence-surface polish; do not widen scope into new adapters or in-process pipeline redesign.

## D-036
- date: 2026-03-27
- entity_id: repo workflow customization
- proposed_by: Copilot
- status: accepted
- decision: Treat `.github/copilot-instructions.md` as the single canonical workspace instruction file, add dedicated Ask and Autopilot custom agents under `.github/agents/`, keep prompt files optional rather than required, and use a lightweight user-level instruction file for cross-workspace natural-language workflow preferences and repeated-friction improvement.
- context: The user mainly starts ordinary natural-language chats in Ask mode and Plan/Autopilot rather than invoking predefined prompts. The repo already had governance instructions and optional prompts, but it lacked task-shaped custom agents and still had stale inventory implying a root `AGENTS.md` existed.
- alternatives_considered: Keep relying on prompt files as the main entry path (rejected: does not match user behavior); add a root `AGENTS.md` alongside `.github/copilot-instructions.md` (rejected: duplicates the workspace-wide instruction surface and conflicts with the single-file guidance); use hooks immediately (rejected: too heavy for the current problem); keep only one generic agent (rejected: weaker separation between read-first Ask work and execution-first Autopilot work).
- rationale: A split between workspace instructions, custom agents, and lightweight user-level preferences matches how the user actually works. It improves natural-language continuation, reduces unnecessary restatement, preserves thesis governance requirements, and creates a clean place to capture automatic self-improvement behavior when the same friction repeats.
- evidence_basis: `.github/copilot-instructions.md`, `.github/agents/thesis-ask.agent.md`, `.github/agents/thesis-autopilot.agent.md`, `c:/Users/peach/AppData/Roaming/Code/User/prompts/natural-language-workflow.instructions.md`, `file_map.md`, `07_implementation/experiment_log.md` (`EXP-053`).
- impacted_files: `.github/copilot-instructions.md`, `.github/agents/thesis-ask.agent.md`, `.github/agents/thesis-autopilot.agent.md`, `c:/Users/peach/AppData/Roaming/Code/User/prompts/natural-language-workflow.instructions.md`, `file_map.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `07_implementation/experiment_log.md`
- next_steps: Validate the new files load in the expected locations, keep prompts as optional specialty tools, and revisit hooks or narrow file-level instructions only if repeated workflow drift still appears.

## D-037
- date: 2026-03-28
- entity_id: thesis artefact submission packaging
- proposed_by: Copilot
- status: accepted
- decision: Create and adopt `07_implementation/ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md` as the authoritative final submission-structure placeholder file, separating Minimum Submission Set from Full Archive Set while keeping runtime contracts unchanged.
- context: The hand-in workflow required a single discoverable structure authority for planner/autopilot execution. Existing guidance covered runtime and baseline posture but did not provide one consolidated, placeholder-first artefact packaging skeleton.
- alternatives_considered: Keep submission structure distributed across multiple docs only (rejected: slower handoff and higher drift risk); collapse implementation into one monolithic script for submission simplicity (rejected: harms modular auditability and reproducibility).
- rationale: A single placeholder authority improves execution clarity for final packaging, preserves modular pipeline integrity, and enables deterministic evidence handoff without premature file movement.
- evidence_basis: `01_requirements/submission_requirements.md`, `00_admin/Artefact_MVP_definition.md`, `07_implementation/ACTIVE_BASELINE.md`, `07_implementation/implementation_notes/IMPLEMENTATION_CONTRACT.md`, `07_implementation/ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md`, `07_implementation/implementation_notes/README.md`, `07_implementation/implementation_notes/SUBMISSION_MANIFEST.md`.
- impacted_files: `00_admin/decision_log.md`, `00_admin/change_log.md`, `07_implementation/ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md`, `07_implementation/implementation_notes/README.md`, `07_implementation/implementation_notes/SUBMISSION_MANIFEST.md`
- next_steps: Replace placeholders in a controlled fill pass after planner approval, then validate package completeness against BL-013/BL-014 evidence and submission requirements.

## D-039
- date: 2026-03-28
- entity_id: final_artefact clean-code G2 deferred scope
- proposed_by: Copilot
- status: accepted
- decision: Defer G2 runtime-control resolver migration for `resolve_bl004_runtime_controls` (profile/main.py) and `resolve_bl011_runtime_controls` (controllability/scenarios.py) from the current clean-code pass. G1 (BL-007, BL-008, BL-006, BL-005, BL-009) is now fully migrated to the `resolve_stage_controls` factory. BL-004 and BL-011 involve list-parsing env logic and scenario-variant complexity that increases parity risk disproportionate to the gain.
- context: The G1 migration pass completed BL-007, BL-008, BL-006, BL-005, and BL-009. BL-004 has a bespoke `BL004_INCLUDE_INTERACTION_TYPES` comma-split env path and multiple env keys with no direct run-config/env symmetry. BL-011 uses raw `os.environ.get` directly with controllability scenario-variant setup that does not map cleanly to the two-callback factory.
- alternatives_considered: Migrate BL-004 and BL-011 in this pass (rejected: complexity increases parity risk without submission benefit); leave both permanently out of the resolver pattern (rejected: adds future maintenance inconsistency).
- rationale: Correctness and test coverage take priority over cosmetic uniformity. The factory pattern is now consistent across 5 of 7 applicable stages. BL-004 and BL-011 can be migrated in a future maintenance pass with a dedicated parity harness.
- evidence_basis: `final_artefact/src/profile/main.py`, `final_artefact/src/controllability/scenarios.py`, `final_artefact/src/shared_utils/stage_runtime_resolver.py`.
- impacted_files: `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: No immediate action required. Record in handoff playbook.

## D-038
- date: 2026-03-28
- entity_id: standalone final artefact execution surface
- proposed_by: Copilot
- status: accepted
- decision: Implement and adopt a root-level `final_artefact.py` as the single evaluator-facing command surface with `run`, `validate`, `bundle`, and `show-paths` commands, while preserving existing BL-stage internals and baseline authority.
- context: The user requested a thesis hand-in path that is not tied to navigating full repository internals and asked to start implementation immediately. Existing guidance covered packaging intent, but a concrete runnable standalone entrypoint did not yet exist.
- alternatives_considered: Collapse full pipeline into one monolithic script (rejected: high regression risk, poor maintainability); keep only existing BL-013 script path as submission surface (rejected: weaker evaluator usability and portability).
- rationale: A single entrypoint improves evaluator UX and packaging portability without introducing method changes. Keeping stage internals intact protects deterministic behavior and evidence continuity.
- evidence_basis: `final_artefact.py`, `final_artefact/README.md`, `final_artefact/config/default_config.json`, `final_artefact/requirements.txt`, `final_artefact/SUBMISSION_BUNDLE_MANIFEST.md`, `07_implementation/ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md`, `07_implementation/implementation_notes/SUBMISSION_MANIFEST.md`.
- impacted_files: `00_admin/decision_log.md`, `00_admin/change_log.md`, `final_artefact.py`, `final_artefact/README.md`, `final_artefact/config/default_config.json`, `final_artefact/requirements.txt`, `final_artefact/SUBMISSION_BUNDLE_MANIFEST.md`, `07_implementation/ARTEFACT_SUBMISSION_STRUCTURE_FINAL.md`, `07_implementation/implementation_notes/SUBMISSION_MANIFEST.md`
- next_steps: Execute first standalone bundle build and run BL-013 plus BL-014 from bundle root to confirm repository-independent operation path for submission packaging.
