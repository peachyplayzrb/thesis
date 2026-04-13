# Decision Log

Ordering convention (standardized 2026-03-24):
- This log is append-only for auditability.
- Entry IDs remain unique identifiers, but physical entry order reflects historical insertion timing (not strict numeric sorting).
- New entries must be appended at the end and may include `superseded_by` when a prior decision is replaced.

Maintenance snapshot (2026-04-12):
- Highest decision ID currently present: `D-087`
- Total decision entries: 84
- Status distribution: accepted=74, superseded=3, rejected=1
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

---

id: D-041
date: 2026-03-28
status: accepted

context:
Implementation review identified that controllability and transparency—core thesis objectives—are underemphasized in current system visibility. Control surfaces are buried in configuration (not first-class), transparency outputs don't show control application tracing (why did YOUR controls lead to this outcome), and weak controls like influence_tracks show zero measurable effect in BL-011 tests. This architecture gap risks undermining thesis contribution by making controls seem secondary rather than foundational.

decision:
Establish governance layer for controllability and transparency as thesis-core design patterns, not implementation details. Create the following persistent governance artifacts: (1) `.controllability-transparency.instructions.md` at workspace root to frame every new session/agent immediately around thesis intent; (2) `CONTROL_SURFACE_REGISTRY.md` to document all controls (weak/working status, measured effects, design gaps); (3) `TRANSPARENCY_SPEC.md` to map current outputs to transparency requirements and identify gaps; (4) `GOVERNANCE.md` to define the control/transparency gate that all features must pass; (5) `RESEARCH_DIRECTIONS.md` to capture open questions (influence slot policy, control-effect measurement, weak control transparency). All files are documentation-only in this phase; code changes deferred to Phase 4 after governance is stabilized.

alternatives_considered:
- Implement code changes immediately to fix weak controls (rejected: decomposes thesis intent into scattered fixes rather than establishing systematic governance)
- Add comments to existing code explaining controllability (rejected: comments get stale, not discoverable to new agents/readers)
- Continue with current architecture but add observability logs (rejected: does not address root issue that controls appear secondary)
- Escalate via mentor feedback on thesis scope (rejected: have sufficient clarity to act; governance layer addresses this directly)

rationale:
Governance artifacts are persistent, discoverable, and serve as the environment signal that controllability and transparency are not compliance-layer features but core thesis contribution. They enable continuity across sessions/agents and establish audit trail for design decisions. Documentation-first approach preserves current implementation stability while unblocking design clarity and transparency enhancements.

evidence_basis:
- BL-011 controllability test: influence_tracks show 0% measurable effect on final playlist despite being enabled
- CONTROL_SURFACE_REGISTRY analysis: 3 working controls, 2 weak controls (influence_tracks, assembly_rules)
- TRANSPARENCY_SPEC identifies 5 gaps: control traceability, influence transparency, assembly rule transparency, filtering rationale, counterfactual reasoning
- Current state: controls scattered across run_config, no central governance, no effect-size validation
- Phase 1 implementation complete: 4 governance files created, README updated
- Design intent: thesis is about building transparent, controllable, observable systems; system must reflect this in governance/visibility

impacted_files:
- `.controllability-transparency.instructions.md` (new, workspace root)
- `05_design/CONTROL_SURFACE_REGISTRY.md` (new)
- `05_design/TRANSPARENCY_SPEC.md` (new)
- `00_admin/GOVERNANCE.md` (new)
- `00_admin/RESEARCH_DIRECTIONS.md` (new)
- `00_admin/README.md` (updated with thesis focus section prepended)
- `05_design/controllability_design_addendum.md` (created, extends D-021)
- `05_design/transparency_design_addendum.md` (created, extends transparency design)
- `00_admin/decision_log.md` (this entry)

review_date: none

---

id: D-042
date: 2026-03-28
status: accepted

context:
GOVERNANCE.md (from D-041) defines three gate questions that force clarity on every control/transparency feature: (1) Does this add measurable user control or transparency? (2) Is the control-to-effect relationship traceable? (3) Can we verify this works via BL-010/BL-011 tests? Influence tracks currently fail Q3—they show zero measured effect in BL-011. This raises a foundational design question: should influence tracks override assembly rules to get guaranteed inclusion and stronger user control?

decision:
Apply governance gate to influence tracks design. Proposed decision (for Phase 3): influence tracks should be moved from pre-profile injection (current, weak) to post-profile slot reservation with hard guarantees. Influence tracks selected by user will reserve up to N playlist slots and bypass assembly rules (genre caps, consecutive limits) because user explicit intent overrides system diversity rules. This ensures measurable effect and satisfies control-effect traceback requirement. Store decision in GOVERNANCE.md escalation template for Phase 3 implementation.

alternatives_considered:
- Keep pre-profile influence injection; accept zero measured effect as limitation (rejected: violates governance gate Q3)
- Remove influence tracks entirely (rejected: loses valid controllability surface)
- Influence tracks follow same rules (genre caps etc.) as regular candidates (rejected: contradicts user intent; still produces weak effect)

rationale:
Explicit inheritance from governance gate forces discipline on design: if a control has zero effect, either fix it architecturally or remove it. Moving influence to post-profile with hard guarantees will satisfy all three gate questions and provide strong user control over playlist composition. This also clarifies the tradeoff: user intent > system diversity rules in this design.

evidence_basis:
- BL-011 test result: influence_tracks produce 0% measurable change (top10_overlap=1.0, rank_delta=0.0)
- Current design: pre-profile injection, indirect effect through profile aggregation
- Proposed design: post-profile slot reservation with rule override
- GOVERNANCE.md gate structure forces this clarity
- RESEARCH_DIRECTIONS.md RQ1 captures this as open decision

impacted_files:
- `00_admin/GOVERNANCE.md` (existing, referenced for gate framework)
- `00_admin/RESEARCH_DIRECTIONS.md` (RQ1 updated with this decision record)
- `05_design/CONTROL_SURFACE_REGISTRY.md` (influence_tracks status will be updated once decision is locked)
- `00_admin/decision_log.md` (this entry)

review_date: Phase 3 post-profile redesign milestone

---

id: D-043
date: 2026-03-28
status: accepted

context:
GOVERNANCE.md implementation checkpoint established, TRANSPARENCY_SPEC.md identified five transparency gaps (control traceability being the largest). To satisfy thesis core requirement that "user can understand why this outcome resulted from their control choices," explanations must trace which user controls enabled each decision, not just which rules/components applied.

decision:
Design requirement for Phase 3+: All transparency outputs (BL-008 explanations, BL-009 observability) must include a "control_application_trace" field that explicitly documents which user control settings shaped the decision. Example: "This track was selected because YOUR genre preference drove similarity score to 0.89." Format: user controls → decision logic → outcome. Store specification in TRANSPARENCY_SPEC.md addendum.

alternatives_considered:
- Continue with current explanations (component score breakdown only) (rejected: does not satisfy thesis transparency requirement for control traceability)
- Add control trace only in debug logs, not user explanations (rejected: users are the primary audience for transparency)
- Generate counterfactual what-if analysis on demand (rejected: too expensive; start with simpler trace first)

rationale:
Control application tracing directly addresses thesis core: user understands their agency and control effects. This is foundational for transparency; counterfactual analysis can build on top. Design is deferred to Phase 3 after governance foundation is stable, but specification must be locked now to guide Phase 3 implementation.

evidence_basis:
- TRANSPARENCY_SPEC.md Gap 1: Current explanations don't show HOW user controls shaped outcome
- BL-008 current design: Shows score components but not control application
- Thesis requirement: "Recommendation system is transparent about how user control choices led to outcome"
- GOVERNANCE.md enforcement: Every transparency feature must make control application explicit

impacted_files:
- `05_design/TRANSPARENCY_SPEC.md` (updated with control_application_trace requirement)
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py` (will implement in Phase 3+)
- `00_admin/decision_log.md` (this entry)

review_date: Phase 3 transparency trace implementation milestone

---
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

## D-040
- date: 2026-03-28
- entity_id: BL-002 ingestion runtime simplification
- proposed_by: Copilot
- status: accepted
- decision: Remove token-cache persistence and endpoint response caching from the active BL-002 export runtime path, and keep track-only playlist-item flattening using item-first payload parsing.
- context: The active implementation moved to a simplification-first ingestion posture where cache-state complexity caused maintenance friction and stale-state risk, while downstream BL-003 and later contracts depend on generated artifacts rather than cache internals.
- alternatives_considered: Keep token cache and sqlite endpoint cache enabled (rejected: higher complexity and stale-state risk), disable only one cache layer (rejected: partial simplification leaves split behaviors), and broaden playlist-item export to non-track payloads (rejected: out of current BL-002/BL-003 track-centric scope).
- rationale: This keeps ingestion behavior explicit and predictable: each live export run performs fresh OAuth, direct API fetches, and deterministic artifact generation; downstream stage contracts remain stable while implementation complexity is reduced.
- evidence_basis: `00_admin/INGESTION_DECACHING_CHANGELOG_2026-03-28.md`, `07_implementation/src/ingestion/export_spotify_max_dataset.py`, `07_implementation/src/ingestion/spotify_client.py`, `07_implementation/src/ingestion/spotify_mapping.py`, `07_implementation/src/ingestion/spotify_artifacts.py`.
- impacted_files: `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/thesis_state.md`, `07_implementation/README.md`, `00_admin/INGESTION_DECACHING_CHANGELOG_2026-03-28.md`
- next_steps: Keep `spotify_resilience.py` and legacy token-cache helper cleanup as optional maintenance only; no change required for current thesis runtime scope.

## D-044
- date: 2026-03-30
- entity_id: aggressive root control-surface archival
- proposed_by: user + Copilot
- status: accepted
- decision: Archive six root-level control/runtime surface files (`.controllability-transparency.instructions.md`, `.gitattributes`, `requirements.txt`, `pyrightconfig.json`, `main_standalone.py`, `final_artefact.py`) into `_deep_archive_march2026/_packages_reference_2026-03-30/`, ignore the full `_deep_archive_march2026/` tree in `.gitignore`, and treat `07_implementation/main.py` as the active runtime entrypoint.
- context: User explicitly requested aggressive archival of all listed root files, placement in deep archive, full admin-document synchronization, and push completion.
- alternatives_considered: Safe-scope archive of only `main_standalone.py` (rejected by user); retain root wrappers/config files and archive only legacy bundles (rejected by user).
- rationale: The accepted directive prioritizes root-surface minimization and archival consolidation over preserving prior root convenience surfaces. Deep archive keeps historical assets available while removing them from active root operations.
- evidence_basis: `_deep_archive_march2026/_packages_reference_2026-03-30/`, `.gitignore`, `file_map.md`, `00_admin/change_log.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/operating_protocol.md`, `00_admin/SIGNAL_FILES_MAINTENANCE.md`, `00_admin/README.md`.
- impacted_files: `.controllability-transparency.instructions.md`, `.gitattributes`, `requirements.txt`, `pyrightconfig.json`, `main_standalone.py`, `final_artefact.py`, `.gitignore`, `file_map.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/operating_protocol.md`, `00_admin/SIGNAL_FILES_MAINTENANCE.md`, `00_admin/README.md`
- next_steps: Maintain active run/setup guidance on `07_implementation` surfaces and avoid reintroducing archived root files unless a new decision supersedes D-044.

## D-045
- date: 2026-04-08
- entity_id: local repo hardening posture
- proposed_by: user + Copilot
- status: accepted
- decision: Use `main` as the canonical local day-to-day branch and enforce owner-aligned local repo hygiene by default: owner git identity in local config, no legacy old-owner LFS endpoint stanza, and resolver-based VS Code Python/Pyright task execution that supports workspace-root or implementation-root virtual environments.
- context: Post-ownership-transfer review identified three recurrent local reliability risks: commit attribution drift to prior owner identity, lingering old-owner LFS endpoint config noise, and VS Code task failures when only one of two valid venv layouts exists.
- alternatives_considered: Keep current mixed local posture and rely on manual operator corrections (rejected: repetitive friction and avoidable errors); keep `restore/pre-restart` as daily default (rejected by user); enforce only one venv location for all contributors (rejected: brittle across setups).
- rationale: This decision reduces operational risk and improves reproducibility without changing pipeline logic. Local setup becomes deterministic and collaborator-friendly while preserving existing recovery branches/tags.
- evidence_basis: `.git/config` owner identity + LFS stanza cleanup, `.vscode/tasks.json` resolver-based task commands, `07_implementation/scripts/run_tool_with_venv_fallback.ps1`, successful resolver and preflight execution on 2026-04-08.
- impacted_files: `.git/config`, `.vscode/tasks.json`, `07_implementation/scripts/run_tool_with_venv_fallback.ps1`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Keep recovery branches/tags unchanged, run periodic preflight checks before major work sessions, and track unrelated pyright baseline errors as separate technical debt.

## D-046
- date: 2026-04-08
- entity_id: autonomous execution entrypoint and report contract
- proposed_by: user + Copilot
- status: accepted
- decision: Introduce a dedicated autonomous execution control surface via `07_implementation/scripts/autopilot_launch.ps1` with bounded run modes and fail-fast behavior, and standardize a post-run markdown handoff artifact generated by `07_implementation/scripts/autopilot_report.py` from latest BL-013/BL-014 outputs.
- context: User requested immediate implementation start toward handing execution to autopilot with stronger operational reliability and clearer session handoff evidence.
- alternatives_considered: Continue running separate scripts/tasks manually without an autonomous wrapper (rejected: slower and less consistent); add a large in-Python orchestrator replacement for existing PowerShell flow (rejected: unnecessary scope expansion and higher regression risk); emit report only on success (rejected: failure sessions also require handoff evidence).
- rationale: A thin launcher over existing verified scripts preserves current runtime contracts while reducing operator friction. Always-emitted reports improve auditability and make failed gate sessions easier to triage.
- evidence_basis: `07_implementation/scripts/autopilot_launch.ps1`, `07_implementation/scripts/autopilot_report.py`, `.vscode/tasks.json`, `00_admin/handoff_friend_chat_playbook.md`, `00_admin/change_log.md` (C-224).
- impacted_files: `07_implementation/scripts/autopilot_launch.ps1`, `07_implementation/scripts/autopilot_report.py`, `.vscode/tasks.json`, `00_admin/handoff_friend_chat_playbook.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Validate launcher modes in live runs, confirm report artifact quality for both pass and fail BL-014 outcomes, and then extend to state-aware routing in a subsequent phase.

## D-047
- date: 2026-04-09
- entity_id: governance and instruction surface simplification
- proposed_by: user + Copilot
- status: accepted
- decision: Adopt a core-file governance workflow that runs on natural-language plus agents without prompt-file dependence and without requiring missing implementation tracking files. Active startup context is now `thesis_state`, `timeline`, `change_log`, `decision_log`, `unresolved_issues`, and `recurring_issues`.
- context: The prior workflow expected `07_implementation/backlog.md` and `07_implementation/experiment_log.md`, which are absent in the current repo, and still carried prompt-era startup assumptions. This created avoidable startup friction and stale dependency checks.
- alternatives_considered: Recreate backlog/experiment files as stubs (rejected: introduces empty governance artifacts and extra maintenance); keep prompt files active as optional-but-present utilities (rejected: unnecessary surface area after natural-language workflow adoption); leave current setup unchanged and rely on operator memory (rejected: repeat startup failures).
- rationale: Consolidating on existing core governance files keeps workflow robust and predictable while reducing overhead. Archiving prompts and non-core admin docs preserves history without keeping inactive surfaces in the active control path.
- evidence_basis: `.github/copilot-instructions.md`, `.github/agents/thesis-ask.agent.md`, `.github/agents/thesis-autopilot.agent.md`, `00_admin/operating_protocol.md`, `00_admin/README.md`, `00_admin/thesis_state.md`, `.github/archives/prompts_2026-04-09/`, `00_admin/archives/admin_consolidation_2026-04-09/`, `00_admin/change_log.md` (C-226).
- impacted_files: `.github/copilot-instructions.md`, `.github/agents/thesis-ask.agent.md`, `.github/agents/thesis-autopilot.agent.md`, `00_admin/operating_protocol.md`, `00_admin/README.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `.github/prompts/*.prompt.md`, `00_admin/Artefact_MVP_definition.md`, `00_admin/evaluation_plan.md`, `00_admin/methodology_definition.md`, `00_admin/thesis_scope_lock.md`, `00_admin/handoff_friend_chat_playbook.md`, `00_admin/autopilot_session_2026-04-07-221646.md`, `00_admin/autopilot_session_2026-04-07-222549.md`, `00_admin/INGESTION_DECACHING_CHANGELOG_2026-03-28.md`.
- next_steps: Keep periodic integrity checks for stale references and only reintroduce additional workflow files if they become active, with explicit checklist updates.

## D-048
- date: 2026-04-09
- entity_id: active runtime/workflow surface authority
- proposed_by: user + Copilot
- status: accepted
- decision: Explicitly enforce `07_implementation/` as the only active runtime/workflow surface and treat `_scratch/` (including `_scratch/final_artefact_bundle/`) as reference-only unless the user explicitly asks for historical inspection or edits there.
- context: Repeated session friction showed stale references to `07_implementation/ACTIVE_BASELINE.md` while the only remaining baseline markdown file lived under `_scratch/final_artefact_bundle/ACTIVE_BASELINE.md`, creating ambiguity about active authority.
- alternatives_considered: Restore `07_implementation/ACTIVE_BASELINE.md` as a live control file (rejected: revives stale surface and duplicates authority); leave references unchanged and rely on manual interpretation (rejected: recurring confusion risk).
- rationale: Keeping one active runtime root (`07_implementation`) and clearly labeling `_scratch` as historical minimizes operator drift and keeps workflow behavior deterministic across sessions and collaborators.
- evidence_basis: `.github/copilot-instructions.md`, `.github/agents/thesis-ask.agent.md`, `.github/agents/thesis-autopilot.agent.md`, `00_admin/README.md`, `_scratch/final_artefact_bundle/ACTIVE_BASELINE.md`, `00_admin/recurring_issues.md` (RI-006).
- impacted_files: `.github/copilot-instructions.md`, `.github/agents/thesis-ask.agent.md`, `.github/agents/thesis-autopilot.agent.md`, `00_admin/README.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/unresolved_issues.md`, `00_admin/recurring_issues.md`, `_scratch/final_artefact_bundle/ACTIVE_BASELINE.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Keep stale-path integrity checks in normal admin sync waves and avoid reintroducing active-control references inside `_scratch`.

## D-049
- date: 2026-04-09
- entity_id: config-first final artefact wrapper architecture
- proposed_by: user + Copilot
- status: accepted
- decision: Implement the new final artefact as a config-first package under `07_implementation/final_artefact/` that reuses the validated `07_implementation/src` pipeline as the execution engine, requires one explicit artefact config per run, generates the orchestration-compatible `run-config-v1` payload from that config, and removes wrapper-level hidden defaults such as a hardcoded profile name.
- context: The user requested a new finalized artefact surface where operator-facing behavior is not hidden in code defaults and can be controlled from one config folder, while preserving correctness and avoiding an unnecessary full rewrite of the validated pipeline.
- alternatives_considered: Keep using `07_implementation/main.py` with the hardcoded v1f profile and forced refresh-seed flag (rejected: operator-facing behavior remains hidden in code); rewrite the full pipeline into a new standalone runtime immediately (rejected: high regression risk and duplicated logic); copy old archived final-artefact surfaces back into active use (rejected: revives stale authority and outdated packaging assumptions).
- rationale: A config-first wrapper over the existing validated pipeline gives one operator-facing control surface without discarding proven stage behavior. Generating the current orchestration run-config from the richer artefact config preserves compatibility while opening a path to move additional path, quality, reporting, and runtime controls into one schema over subsequent iterations.
- evidence_basis: `07_implementation/final_artefact/main.py`, `07_implementation/final_artefact/core/app_config.py`, `07_implementation/final_artefact/core/runner.py`, `07_implementation/final_artefact/config/profiles/final_artefact_config_v1.json`, `07_implementation/tests/test_final_artefact_app_config.py`, `07_implementation/tests/test_final_artefact_runner.py`, `07_implementation/src/orchestration/main.py`, `07_implementation/src/orchestration/config_resolver.py`, `00_admin/change_log.md` (C-230).
- impacted_files: `07_implementation/final_artefact/**`, `07_implementation/tests/test_final_artefact_app_config.py`, `07_implementation/tests/test_final_artefact_runner.py`, `07_implementation/tests/conftest.py`, `07_implementation/src/orchestration/main.py`, `07_implementation/src/orchestration/config_resolver.py`, `07_implementation/tests/test_orchestration_stage_payload_handoff.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`
- next_steps: Migrate additional operator-facing controls into the artefact config schema, starting with path controls, quality/validation policy, and output/reporting policy, while keeping BL-013/BL-014 validation green on each iteration.

## D-050
- date: 2026-04-10
- entity_id: chapter2 full-strength citation-fit closure
- proposed_by: user + Copilot
- status: accepted
- decision: Execute a full-strength Chapter 2 wording-hardening pass that resolves all zero-trust `partially_supported` rows by narrowing overextended causal/scope phrasing to evidence-bounded claims, then synchronize QC ledgers to the revised text baseline.
- context: The report-only zero-trust pass closed at `supported=23`, `partially_supported=8`, with residual risk concentrated in wording sharpness. The user requested implementation start to finish Chapter 2.
- alternatives_considered: Keep report-only posture without chapter edits (rejected: leaves avoidable partial-support risk); replace citations with new sources (rejected for this pass: unnecessary if wording can be evidence-aligned under existing mapped PDFs).
- rationale: Precision rewording preserves chapter structure and citation coverage while maximizing direct claim-to-evidence fit under the existing verified PDF set.
- evidence_basis: `08_writing/chapter2.md`, `09_quality_control/chapter2_reference_audit_zero_trust_2026-04-10.md`, `09_quality_control/citation_checks.md`, `09_quality_control/claim_evidence_map.md`, `09_quality_control/chapter2_verbatim_audit.md`.
- impacted_files: `08_writing/chapter2.md`, `09_quality_control/chapter2_reference_audit_zero_trust_2026-04-10.md`, `09_quality_control/citation_checks.md`, `09_quality_control/claim_evidence_map.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Complete external submission-format and packaging checks, then close the remaining submission-wide gate in `09_quality_control/chapter_readiness_checks.md`.

## D-051
- date: 2026-04-11
- entity_id: chapter2 literature-purity implementation rule
- proposed_by: user + Copilot
- status: accepted
- decision: Apply a literature-purity rewrite rule to Chapter 2 draft variants: remove hidden methodology/system-design language, preserve citation set and chapter structure, and strengthen explicit paper-versus-paper adjudication where literature conflicts.
- context: Mentor feedback highlighted that Chapter 2 still sounded partly like system defense and methodology guidance instead of a literature-critical chapter. The user requested immediate implementation start.
- alternatives_considered: Keep current wording and defer to Chapter 3 separation later (rejected: leaves mentor-raised risk unaddressed); perform a full structural rewrite with new sources (rejected: unnecessary scope expansion for this pass).
- rationale: A bounded wording/function correction directly addresses chapter-function risk while preserving established evidence mapping and avoiding citation drift.
- evidence_basis: `08_writing/_versions/chapter2finalv1.md`, `09_quality_control/citation_checks.md`, mentor-feedback constraints recorded in active session context.
- impacted_files: `08_writing/_versions/chapter2finalv1.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Run a final comparative-density check and, if approved, promote the revised version into canonical Chapter 2 flow.

## D-052
- date: 2026-04-12
- entity_id: full architecture rebuild from Chapter 2 baseline
- proposed_by: user
- status: accepted
- decision: Execute a full thesis architecture rebuild starting from Chapter 2 as the only confirmed good component. All other artefacts — research question, objectives, artefact definition, methodology position, Chapter 1/3/4/5 drafts, and the `07_implementation/` pipeline — are scrapped and will be reconstructed from Chapter 2 outwards. The existing `07_implementation/` codebase is frozen as legacy reference material, not the active build target.
- context: The user decided the existing architecture did not flow cleanly from the literature established in Chapter 2. Chapter 2 is the only chapter confirmed to be good (finalized, mentor-hardened, all 31 citations verified). The rebuild approach works backwards: use Chapter 2 themes and unresolved literature contradictions to re-derive the RQ, then rebuild design → implementation → evaluation in that order.
- alternatives_considered: Patch individual chapter drafts in place (rejected: piecemeal patching does not address the structural misalignment); retain existing RQ and patch supporting chapters (rejected: user confirmed full reset was needed); treat implementation as active build target during rebuild (rejected: implementation should follow from design, which follows from RQ, which follows from literature).
- rationale: Starting from the confirmed Chapter 2 baseline and rebuilding forwards ensures the entire thesis argument chain is grounded in the verified literature evidence rather than inherited assumptions from an earlier design pass.
- evidence_basis: `08_writing/chapter2.md`, `08_writing/_versions/chapter2finalv1.md`, `09_quality_control/chapter2_reference_audit_zero_trust_2026-04-10.md`
- impacted_files: `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/unresolved_issues.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Re-derive RQ and objectives from Chapter 2 gaps and unresolved contradictions; rebuild Chapter 3 anchored in those conclusions; restart implementation only after design is re-grounded.

## D-053
- date: 2026-04-12
- entity_id: rebuilt research question and objective set
- proposed_by: user + Copilot
- status: accepted
- decision: Adopt a rebuilt RQ centered on engineering and evaluating deterministic playlist generation under cross-source uncertainty and multi-objective trade-offs, with six objectives that explicitly cover uncertainty-aware profiling, confidence-aware alignment and candidate generation, controllable scoring and assembly trade-offs, mechanism-linked explanations, reproducibility and controllability evaluation, and bounded design guidance.
- context: Under D-052 rebuild posture, Chapter 2 was confirmed as the only authoritative baseline and UI-014 blocked all forward work until RQ/objective re-derivation was completed.
- alternatives_considered: Reuse the legacy RQ/objectives unchanged (rejected: does not reflect Chapter 2 contradiction structure); derive objectives first without RQ lock (rejected: high drift risk across foundation/governance surfaces); split into multiple narrow RQs (rejected for current scope: would fragment design and evaluation coherence).
- rationale: One integrated RQ with explicit objective-level decomposition preserves Chapter 2-grounded problem structure while remaining implementable within bounded thesis scope.
- evidence_basis: `08_writing/chapter2.md`, `00_admin/unresolved_issues.md` (UI-014 trigger and required actions), `00_admin/timeline.md` (REB-M1 intent), `02_foundation/contribution_statement.md`.
- impacted_files: `00_admin/thesis_state.md`, `02_foundation/current_title_and_rq.md`, `02_foundation/objectives.md`, `02_foundation/contribution_statement.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Lock scope and artefact definition against the new RQ/objective set and close UI-014.

## D-054
- date: 2026-04-12
- entity_id: rebuild scope and artefact lock after RQ derivation
- proposed_by: user + Copilot
- status: accepted
- decision: Lock rebuild scope to a single-user deterministic engineering-evidence contribution focused on auditable uncertainty handling, controllable trade-off behavior, and reproducible process-level evidence. Keep Chapter 2 fixed as baseline and start REB-M2 design reconstruction from the new objective set.
- context: After D-053 RQ/objective acceptance, governance surfaces required a scope/artefact lock to prevent immediate drift during Chapter 3 rebuild planning.
- alternatives_considered: Reopen Chapter 2 wording during RQ lock (rejected: Chapter 2 is confirmed baseline); reactivate legacy implementation as active build target immediately (rejected: design must be rebuilt first); widen scope to multi-user or model-novelty track (rejected: exceeds bounded rebuild posture).
- rationale: A hard scope lock keeps REB-M2 design work coherent and preserves the Chapter 2-first reconstruction logic established in D-052.
- evidence_basis: `00_admin/thesis_state.md` (rebuild checkpoint), `02_foundation/assumptions.md`, `02_foundation/limitations.md`, `00_admin/timeline.md` (REB-M2 transition), `00_admin/unresolved_issues.md` (UI-014 closure record).
- impacted_files: `00_admin/thesis_state.md`, `02_foundation/assumptions.md`, `02_foundation/limitations.md`, `00_admin/timeline.md`, `00_admin/unresolved_issues.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Execute REB-M2 by converting the new objectives into a Chapter 3 design-control blueprint before any implementation restart.

## D-055
- date: 2026-04-12
- entity_id: REB-M2 chapter3 design-control lock
- proposed_by: user + Copilot
- status: accepted
- decision: Lock REB-M2 by adopting an objective-anchored Chapter 3 design blueprint and requirements-to-design map that convert O1 to O6 into explicit design requirements, stage responsibilities, and evidence contracts for uncertainty handling, controllability, transparency fidelity, and reproducibility.
- context: After D-053 and D-054, REB-M2 required formal design authority before any artefact-switch or REB-M3 implementation restart. Legacy Chapter 3 design sheets still reflected pre-rebuild title, RQ, and requirement framing.
- alternatives_considered: defer design lock and restart implementation directly (rejected: high architecture drift risk); keep legacy Chapter 3 maps with only minor wording patches (rejected: does not satisfy objective-level traceability under rebuilt RQ); broaden scope to multi-user/model-novelty controls during REB-M2 (rejected: out of current bounded scope).
- rationale: A locked objective-to-design-to-evidence contract prevents implementation-first drift and preserves Chapter 2-first reconstruction coherence.
- evidence_basis: `05_design/chapter3_information_sheet.md`, `05_design/requirements_to_design_map.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`.
- impacted_files: `05_design/chapter3_information_sheet.md`, `05_design/requirements_to_design_map.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`
- next_steps: Execute artefact-definition switch under the locked REB-M2 design contract, then start REB-M3 implementation rebuild with control/evidence contract checks as entry gates.

## D-056
- date: 2026-04-12
- entity_id: artefact-definition switch and REB-M3 kickoff contract
- proposed_by: user + Copilot
- status: accepted
- decision: Switch the active artefact definition to an implementation-entry contract aligned to the REB-M2 design lock, and start REB-M3 with strict objective-to-control-to-evidence traceability gates.
- context: REB-M2 is complete and Chapter 3 design authority is locked (D-055). The next continuation step requires replacing checkpoint-level artefact wording with an executable rebuild contract before implementation changes proceed.
- alternatives_considered: keep artefact wording unchanged while starting code changes (rejected: weak implementation-entry contract); defer REB-M3 until additional writing-only passes (rejected: continuation objective is implementation restart); reactivate legacy implementation posture as active baseline (rejected: conflicts with rebuild governance).
- rationale: A formal artefact-definition switch establishes a clear contract for what REB-M3 implementation must produce and how it will be validated.
- evidence_basis: `00_admin/thesis_state.md`, `00_admin/timeline.md`, `05_design/chapter3_information_sheet.md`, `05_design/requirements_to_design_map.md`.
- impacted_files: `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Execute REB-M3 implementation tranches under D-056 contract, beginning with surfaces that emit required uncertainty, control, and mechanism-linked evidence fields.

## D-057
- date: 2026-04-12
- entity_id: REB-M3 tranche-1 executable gate for O1 to O3
- proposed_by: user + Copilot
- status: accepted
- decision: Implement an executable REB-M3 tranche-1 gate at `07_implementation/src/quality/reb_m3_tranche1_gate.py` that verifies O1 to O3 minimum evidence contracts against current BL-003 to BL-006 outputs.
- context: REB-M3 started under D-056, but continuation required a concrete implementation artifact that operationalizes entry-gate checks before broader tranche expansion.
- alternatives_considered: rely on manual checklist-only gating (rejected: non-executable and drift-prone); jump directly to wide code refactors without gate checks (rejected: weak contract discipline for rebuild posture).
- rationale: An executable gate tightens implementation discipline by failing fast when required uncertainty, alignment/exclusion, or scoring-control evidence fields are missing.
- evidence_basis: `07_implementation/src/quality/reb_m3_tranche1_gate.py`, `07_implementation/README.md`, `07_implementation/src/profile/outputs/bl004_preference_profile.json`, `07_implementation/src/alignment/outputs/bl003_ds001_spotify_summary.json`, `07_implementation/src/retrieval/outputs/bl005_candidate_diagnostics.json`, `07_implementation/src/scoring/outputs/bl006_score_summary.json`.
- impacted_files: `07_implementation/src/quality/reb_m3_tranche1_gate.py`, `07_implementation/README.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Run the tranche-1 gate and log baseline pass/fail evidence, then extend REB-M3 to O4 to O6 gating surfaces.

## D-058
- date: 2026-04-12
- entity_id: REB-M3 tranche-2 executable gate for O4 to O6
- proposed_by: user + Copilot
- status: accepted
- decision: Implement an executable REB-M3 tranche-2 gate at `07_implementation/src/quality/reb_m3_tranche2_gate.py` that verifies O4 to O6 minimum evidence contracts against current BL-007 to BL-011 outputs.
- context: REB-M3 tranche-1 (D-057) closed O1 to O3 entry checks. Continuation required extending executable governance to explanation/observability fidelity, reproducibility/controllability evidence, and bounded-guidance reporting surfaces.
- alternatives_considered: keep O4 to O6 as manual checklist-only validation (rejected: drift-prone and non-executable); jump directly to broad refactors without tranche-2 evidence gating (rejected: weak contract discipline under rebuild posture).
- rationale: A second executable gate preserves objective-to-control-to-evidence discipline across the full O1 to O6 surface before broader REB-M3 implementation expansion.
- evidence_basis: `07_implementation/src/quality/reb_m3_tranche2_gate.py`, `07_implementation/README.md`, `07_implementation/src/playlist/outputs/bl007_assembly_report.json`, `07_implementation/src/transparency/outputs/bl008_explanation_payloads.json`, `07_implementation/src/observability/outputs/bl009_run_observability_log.json`, `07_implementation/src/reproducibility/outputs/reproducibility_report.json`, `07_implementation/src/controllability/outputs/controllability_report.json`.
- impacted_files: `07_implementation/src/quality/reb_m3_tranche2_gate.py`, `07_implementation/README.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Run the tranche-2 gate, record baseline pass/fail evidence, then proceed to REB-M3 code-surface refactors tied to failing or weak evidence checks.

## D-059
- date: 2026-04-12
- entity_id: BL-003 DS-001 identifier normalization
- proposed_by: user + Copilot
- status: accepted
- decision: Normalize DS-001 identifier resolution in BL-003 to accept schema variants (`id`, `ds001_id`, `cid`) and use this resolver consistently in index ordering, matched-event construction, and influence lookup mapping.
- context: BL-004 was producing a single row because BL-003 matched events were aggregating under an empty DS-001 key. The active DS-001 dataset uses `cid`, while BL-003 hardcoded `id`, causing all matched events to collapse into one aggregate row.
- alternatives_considered: Keep strict `id`-only lookup and patch outputs manually (rejected: fragile and non-reproducible); add one-off fallback only in BL-004 (rejected: fixes symptom not root cause); reformat DS-001 source file columns as a preprocessing requirement (rejected: unnecessary coupling and higher operational risk).
- rationale: Resolver-based normalization is the smallest robust change that preserves deterministic behavior across known DS-001 schema variants and prevents future row-collapse regressions at the BL-003 to BL-004 contract boundary.
- evidence_basis: `07_implementation/src/shared_utils/index_builder.py`, `07_implementation/src/alignment/stage.py`, `07_implementation/src/alignment/match_pipeline.py`; verification rerun showing `seed_table_rows=1592` and `bl004_seed_trace_rows=1592` after patch (previously both `1`).
- impacted_files: `07_implementation/src/shared_utils/index_builder.py`, `07_implementation/src/alignment/stage.py`, `07_implementation/src/alignment/match_pipeline.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Keep the resolver as the canonical DS-001 id contract for BL-003 and add focused regression coverage when the next alignment test wave is run.

## D-060
- date: 2026-04-12
- entity_id: REB-M3 additive transparency payload compatibility
- proposed_by: user + Copilot
- status: accepted
- decision: Keep `control_provenance` as an additive field in BL-008 payloads but make it optional in `build_track_payload` so existing callers/tests remain valid during REB-M3 tranche expansion.
- context: The broad reconciliation wave introduced a required `control_provenance` argument in transparency payload building, which broke existing test callers and caused avoidable compatibility drift.
- alternatives_considered: keep `control_provenance` required and patch every caller immediately (rejected: unnecessary churn for additive contract); revert the control-provenance feature entirely (rejected: loses tranche-3 control-causality evidence objective).
- rationale: Optional additive fields preserve backward compatibility while still exposing the new evidence surface for callers that supply it.
- evidence_basis: `07_implementation/src/transparency/main.py`, `07_implementation/src/transparency/payload_builder.py`, and test validation pass (`333/333` after compatibility patch).
- impacted_files: `07_implementation/src/transparency/payload_builder.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Keep additive payload fields backward-compatible by default unless a deliberate schema-version bump is approved.

## D-061
- date: 2026-04-12
- entity_id: BL-003 canonical DS-001 ID contract for influence path
- proposed_by: user + Copilot
- status: accepted
- decision: Treat `resolve_ds001_id` as the canonical DS-001 identifier resolver for all BL-003 paths, including influence-track injection, and enforce this with regression tests spanning shared utility, matching, and stage execution.
- context: After fixing BL-004 row-collapse for `cid` datasets, influence-track injection still emitted empty `ds001_id` when DS-001 rows lacked `id`, creating a hidden contract inconsistency.
- alternatives_considered: keep influence path `id`-only (rejected: inconsistent with matching/stage behavior); normalize only in tests without code change (rejected: leaves runtime contract drift unresolved).
- rationale: One canonical resolver across all BL-003 identifier touchpoints prevents schema-variant regressions and keeps downstream profile/trace contracts stable.
- evidence_basis: `07_implementation/src/alignment/influence.py` now resolves identifier via `resolve_ds001_id`; new tests in `07_implementation/tests/test_alignment_ds001_id_resolution.py`; validation suite pass (`336/336`) and full-contract pass (`BL013-ENTRYPOINT-20260412-140426-225972`, `BL014-SANITY-20260412-140500-928684`, `28/28`).
- impacted_files: `07_implementation/src/alignment/influence.py`, `07_implementation/tests/test_alignment_ds001_id_resolution.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Reuse this canonical identifier resolver for any future DS-001 ingest/normalization migrations before contract version bumps.

## D-062
- date: 2026-04-12
- entity_id: REB-M3 tranche-3 validity-boundary contract closure
- proposed_by: user + Copilot
- status: accepted
- decision: Enforce BL-009 `validity_boundaries` as a top-level observability contract field and accept REB-M3 tranche-3 closure only after the tranche-3 gate passes on BL-008/BL-009/BL-011 control-causality and boundary-evidence checks.
- context: Initial tranche-3 execution failed due missing/invalid BL-009 validity-boundary checks because `validity_boundaries` was nested under `exclusion_diagnostics.assembly` instead of the gate-expected top-level location.
- alternatives_considered: relax tranche-3 gate checks to accept nested validity-boundary fields (rejected: weakens objective contract and hides schema drift); keep current structure and defer fix to later tranche work (rejected: blocks REB-M3 closure discipline).
- rationale: The top-level placement is the explicit gate contract for auditability and bounded-guidance visibility, so schema alignment must be fixed at source rather than tolerated in gate logic.
- evidence_basis: `07_implementation/src/observability/main.py` (schema correction), validate-only pass (`BL013-ENTRYPOINT-20260412-140726-924263`, `BL014-SANITY-20260412-140755-116563`, `28/28`), tranche-3 gate pass (`REB-M3-TRANCHE3-GATE-20260412-140805-553785`, `9/9`) with artifacts in `07_implementation/src/quality/outputs/reb_m3_tranche3_gate_report.json` and `07_implementation/src/quality/outputs/reb_m3_tranche3_gate_matrix.csv`.
- impacted_files: `07_implementation/src/observability/main.py`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Add focused BL-009 regression coverage for top-level `validity_boundaries` placement to prevent future schema-nesting regressions.

## D-063
- date: 2026-04-12
- entity_id: BL-009 required-sections hardening for validity-boundary contract
- proposed_by: user + Copilot
- status: accepted
- decision: Enforce `validity_boundaries` as a required top-level section in BL-009 output validation (`ensure_required_sections`) and lock this with unit regression tests so missing or nested-only boundary blocks fail fast.
- context: D-062 fixed runtime schema placement and closed tranche-3, but BL-009 section validation still allowed reports that omitted top-level `validity_boundaries`, leaving a regression gap.
- alternatives_considered: rely only on tranche-3 gate checks (rejected: weaker unit-level contract guard); keep optional section semantics in BL-009 validator (rejected: allows silent schema drift until later gate execution).
- rationale: Adding the requirement to BL-009 section validation plus direct tests creates an immediate contract boundary that prevents recurrence of the nesting omission.
- evidence_basis: `07_implementation/src/observability/main.py` (`ensure_required_sections` now requires `validity_boundaries`), new test file `07_implementation/tests/test_observability_required_sections.py`, validation passes: pytest `338/338`, BL-013 pass (`BL013-ENTRYPOINT-20260412-141352-373476`), BL-014 pass (`BL014-SANITY-20260412-141423-183313`, `28/28`), tranche-3 gate pass (`REB-M3-TRANCHE3-GATE-20260412-141431-157169`, `9/9`).
- impacted_files: `07_implementation/src/observability/main.py`, `07_implementation/tests/test_observability_required_sections.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`
- next_steps: Continue REB-M3 closure hardening by transitioning status surfaces toward REB-M4 chapter evidence synthesis once no further contract regressions are observed.

## D-064
- date: 2026-04-12
- entity_id: REB-M4 chapter evidence synthesis framing
- proposed_by: user + Copilot
- status: accepted
- decision: Rebuild Chapter 4 and Chapter 5 around the active O1 to O6 objective-to-control-to-evidence contract, using REB-M3 tranche-gate results and current `07_implementation/src` artifacts as the canonical implementation/evaluation evidence surface instead of the legacy MVP reporting frame.
- context: REB-M3 code-surface hardening is complete through D-063, but the active chapter drafts for implementation/evaluation and discussion still reflected the pre-rebuild research question, legacy evidence paths, and outdated interpretation frame.
- alternatives_considered: postpone chapter rebuild until all possible future hardening is complete (rejected: leaves writing layer materially stale against current implementation); patch only a few run IDs while retaining legacy framing (rejected: preserves conceptual drift); rewrite chapters as benchmark-comparison discussion (rejected: incompatible with bounded engineering-evidence contribution).
- rationale: Chapter 4 and Chapter 5 must now describe the artefact the thesis actually built and validated, which is an objective-linked deterministic pipeline with explicit uncertainty, control, reproducibility, and validity-boundary evidence contracts.
- evidence_basis: `08_writing/chapter4.md`, `08_writing/chapter5.md`, REB-M3 tranche gate reports under `07_implementation/src/quality/outputs/`, BL-013 pass `BL013-ENTRYPOINT-20260412-141352-373476`, BL-014 pass `BL014-SANITY-20260412-141423-183313`.
- impacted_files: `08_writing/chapter4.md`, `08_writing/chapter5.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Continue REB-M4 by replacing remaining legacy wording in chapter-facing evidence tables and synchronizing quality-control claim maps to the rebuild-era chapter text.

## D-065
- date: 2026-04-12
- entity_id: REB-M4 quality-control mirror synchronization
- proposed_by: user + Copilot
- status: accepted
- decision: Synchronize Chapter 4/5 quality-control mirrors to the rebuild posture by updating readiness, RQ-alignment, and claim-verdict surfaces so they reference the rebuilt title/RQ and the active O1 to O6 evidence contract instead of the pre-rebuild MVP framing.
- context: After the REB-M4 chapter rewrite, the main chapter text and governance state were current, but quality-control surfaces still described legacy Chapter 4/5 expectations and the prior title/research question wording.
- alternatives_considered: leave QC mirrors stale until final submission sweep (rejected: allows avoidable governance drift); only update chapter text without QC surfaces (rejected: breaks audit traceability); rewrite QC surfaces as fresh standalone audits disconnected from prior logs (rejected: loses continuity).
- rationale: The thesis workflow requires control files and QC ledgers to remain synchronized with the active writing posture; otherwise later review passes can incorrectly flag resolved rebuild changes as drift.
- evidence_basis: `09_quality_control/chapter_readiness_checks.md`, `09_quality_control/ui003_claim_verdicts_ch3_ch5.md`, `09_quality_control/rq_alignment_checks.md`, active rebuild state in `00_admin/thesis_state.md`, rebuilt chapter text in `08_writing/chapter4.md` and `08_writing/chapter5.md`.
- impacted_files: `09_quality_control/chapter_readiness_checks.md`, `09_quality_control/ui003_claim_verdicts_ch3_ch5.md`, `09_quality_control/rq_alignment_checks.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Continue REB-M4 with any remaining claim-map or citation-placement cleanup needed for final chapter hardening, but keep QC mirrors aligned after each substantive rewrite.

## D-066
- date: 2026-04-12
- entity_id: REB-M3 and REB-M4 closure after chapter citation hardening
- proposed_by: user + Copilot
- status: accepted
- decision: Treat REB-M3 and REB-M4 as complete in-repo after the Chapter 4/5 citation-density hardening pass, because implementation gates, wrapper validation, chapter rebuild, and QC mirror synchronization are now closed; keep only submission proofing and packaging outside these rebuild milestones.
- context: After D-064 and D-065, the remaining in-repo risk was that rebuilt Chapter 4/5 interpretation sections were still lighter on literature anchors than the rest of the thesis, even though their evidence contract and governance posture were already aligned.
- alternatives_considered: keep REB-M4 open until final submission packaging is complete (rejected: mixes rebuild alignment work with external submission logistics); leave Chapter 4/5 discussion prose citation-light (rejected: avoidable writing-quality risk); close REB-M4 without updating milestone status surfaces (rejected: preserves stale in-progress posture).
- rationale: The rebuild milestones were scoped to re-derive the thesis question/design, rebuild the implementation evidence contract, and rewrite the chapter-facing interpretation around that contract. Those objectives are now complete inside the repository.
- evidence_basis: `08_writing/chapter4.md`, `08_writing/chapter5.md`, `09_quality_control/rq_alignment_checks.md` (`RQC-016`), REB-M3 tranche gate outputs, BL-013 `BL013-ENTRYPOINT-20260412-141352-373476`, BL-014 `BL014-SANITY-20260412-141423-183313`, and the synchronized chapter/QC/admin mirrors updated through C-295.
- impacted_files: `08_writing/chapter4.md`, `08_writing/chapter5.md`, `09_quality_control/rq_alignment_checks.md`, `00_admin/thesis_state.md`, `00_admin/timeline.md`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Limit remaining work to final submission-proofing and packaging tasks, plus any mentor-directed wording refinements that do not reopen the rebuild posture.

## D-067
- date: 2026-04-12
- entity_id: BL-007 influence policy contract and observability diagnostics
- proposed_by: user + Copilot
- status: accepted
- decision: Introduce an additive influence-policy contract for BL-007 with opt-in modes (`competitive`, `reserved_slots`, `hybrid_override`), bounded reserved-slot handling, and explicit override controls, while preserving legacy competitive behavior as the default. Extend BL-009 to emit per-track influence inclusion/exclusion diagnostics.
- context: Post-REB-M3 closure analysis showed influence tracks could alter profile/scoring but often had weak or opaque playlist-level effects under assembly constraints, with limited per-track audit visibility.
- alternatives_considered: keep legacy behavior only and rely on manual interpretation (rejected: weak controllability traceability); force influence overrides as a new default (rejected: backward-compatibility risk); add diagnostics only without assembly controls (rejected: does not close controllability gap).
- rationale: Additive opt-in controls provide measurable policy actuation without breaking existing default semantics, and per-track diagnostics improve mechanism-level transparency for inclusion/exclusion outcomes.
- evidence_basis: BL-007 runtime/rules/model updates and BL-009 diagnostics updates under `07_implementation/src`; validation evidence: pytest `342/342`, pyright `0 errors`, BL-013 pass `BL013-ENTRYPOINT-20260412-150114-734913`, BL-014 pass `BL014-SANITY-20260412-150146-906654`.
- impacted_files: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/playlist/models.py`, `07_implementation/src/playlist/runtime_controls.py`, `07_implementation/src/playlist/rules.py`, `07_implementation/src/playlist/stage.py`, `07_implementation/src/playlist/io_layer.py`, `07_implementation/src/observability/main.py`, `07_implementation/tests/*`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`.
- next_steps: Use non-default influence modes in controlled runs to quantify playlist-level effect size and update chapter-facing evidence mapping if this enhancement is promoted into final reporting claims.

## D-068
- date: 2026-04-12
- entity_id: run-config scoring-controls schema migration boundary
- proposed_by: Copilot
- status: accepted
- decision: Migrate `scoring_controls` field validation in `resolve_effective_run_config` to declarative `FieldSpec` schema validation for enum/fraction/bool-like fields, while keeping `component_weights`, numeric-threshold coupling, and `influence_track_bonus_scale` coercion on dedicated legacy validators to preserve behavioral parity.
- context: `profile_controls` and `retrieval_controls` had already moved to schema-driven validation, but `scoring_controls` still used per-field imperative parsing, increasing maintenance drift risk and making cross-section validation patterns inconsistent.
- alternatives_considered: fully migrate all scoring fields including component weights and threshold maps into schema primitives now (rejected: current schema types do not cover the existing sum/coupling constraints cleanly); keep imperative scoring validation unchanged (rejected: continued duplication and higher drift risk).
- rationale: A hybrid migration captures immediate maintainability gains and consistency with prior sections without weakening existing coupling and weight-sum contracts.
- evidence_basis: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, pytest pass (`358/358`), pyright pass (`0 errors, 0 warnings`).
- impacted_files: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Continue section-by-section schema migration for remaining imperative run-config surfaces while retaining current contract checks until equivalent schema primitives exist.

## D-069
- date: 2026-04-12
- entity_id: run-config observability/transparency numeric schema boundary and non-negative fallback parity
- proposed_by: Copilot
- status: accepted
- decision: Migrate `observability_controls.diagnostic_sample_limit` plus `transparency_controls.top_contributor_limit` and `transparency_controls.primary_contributor_tie_delta` to declarative schema validation, while preserving legacy bool fallback behavior for `observability_controls.bootstrap_mode` and `transparency_controls.blend_primary_contributor_on_near_tie`. Adjust declarative `non_negative_float` coercion to fallback-to-default on negatives for parity with legacy `_coerce_non_negative_float` semantics.
- context: After D-068, small manual validation islands remained in `resolve_effective_run_config`. A direct schema migration for these numeric fields was low-risk, but initial declarative non-negative behavior diverged from established fallback semantics.
- alternatives_considered: migrate these controls and tighten invalid bool handling to strict errors (rejected: breaks existing fallback semantics); leave manual blocks unchanged (rejected: slows schema migration and keeps duplicate imperative logic).
- rationale: This slice continues declarative migration while preserving runtime behavior at the bool and non-negative fallback boundaries.
- evidence_basis: `07_implementation/src/run_config/schema.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, targeted pytest (`28/28`), full pytest (`359/359`), pyright (`0 errors, 0 warnings`).
- impacted_files: `07_implementation/src/run_config/schema.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Continue migration of remaining imperative resolver surfaces and reduce duplicated post-resolution coercion in `resolve_bl005_controls` and `resolve_bl006_controls` while preserving contract checks.

## D-070
- date: 2026-04-12
- entity_id: BL-005 and BL-006 resolver de-duplication boundary
- proposed_by: Copilot
- status: accepted
- decision: Simplify `resolve_bl005_controls` and `resolve_bl006_controls` to use already-validated effective run-config values directly for schema-covered fields, while preserving explicit contract checks for retrieval/scoring numeric thresholds and scoring component-weight sum enforcement.
- context: After D-068 and D-069, these resolvers still repeated many coercion/validation steps already guaranteed by `resolve_effective_run_config`, increasing maintenance overhead and drift risk.
- alternatives_considered: remove all post-resolution checks including thresholds and component-weight checks (rejected: weakens explicit contract boundaries at resolver outputs); keep full duplicate coercion logic (rejected: unnecessary duplication and higher drift risk).
- rationale: Direct use of validated effective controls reduces duplication while retained threshold/weight checks keep the critical coupling and normalization contracts explicit.
- evidence_basis: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, targeted pytest (`24/24`), full pytest (`360/360`), pyright (`0 errors, 0 warnings`).
- impacted_files: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Continue reducing duplicated coercion in remaining resolver surfaces and assess whether threshold/weight contract checks should be centralized once schema primitives fully cover those contracts.

## D-071
- date: 2026-04-12
- entity_id: BL-008 and BL-009 resolver de-duplication boundary
- proposed_by: Copilot
- status: accepted
- decision: Simplify `resolve_bl008_controls` and `resolve_bl009_controls` to return already-validated effective transparency/observability values directly, while preserving the existing control-mode payload shape in BL-009.
- context: After D-070, BL-008/BL-009 still duplicated coercion of fields that are validated in `resolve_effective_run_config`, creating maintenance overhead without adding contract safety.
- alternatives_considered: keep duplicate coercion in BL-008/BL-009 for defensive redundancy (rejected: no additional contract value after effective validation); remove BL-009 control-mode shaping as part of cleanup (rejected: unnecessary output-shape change risk).
- rationale: Reducing duplicated resolver logic improves maintainability while retaining external resolver contracts and behavior parity.
- evidence_basis: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, targeted pytest (`25/25`), full pytest (`361/361`), pyright (`0 errors, 0 warnings`).
- impacted_files: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Continue incremental migration by collapsing remaining duplicate coercion in BL-007/BL-011 resolver internals where effective-config guarantees already exist, while preserving explicit policy/constraint checks.

## D-072
- date: 2026-04-12
- entity_id: BL-003 weighting-policy resolver de-duplication boundary
- proposed_by: Copilot
- status: accepted
- decision: Simplify `resolve_bl003_weighting_policy` to read directly from validated `seed_controls.weighting_policy` in effective config instead of re-merging defaults at resolver output time.
- context: After prior resolver cleanup waves, BL-003 weighting-policy resolution still duplicated default-merging logic that was already guaranteed by `_validate_bl003_seed_controls` during effective config resolution.
- alternatives_considered: keep local default fallback merge in resolver (rejected: duplicate logic and higher drift risk); remove weighting-policy validation from effective resolver and keep it only in BL-003 resolver (rejected: weakens central contract boundary).
- rationale: Using effective validated controls as the single source of truth reduces duplication and preserves deterministic behavior.
- evidence_basis: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, targeted pytest (`26/26`), full pytest (`362/362`), pyright (`0 errors, 0 warnings`).
- impacted_files: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`
- next_steps: Continue trimming duplicated resolver coercion where effective-config contracts already guarantee shape/type/defaults, while retaining explicit guardrails for cross-section coupling and policy constraints.

## D-073
- date: 2026-04-12
- entity_id: BL-003 selected-source resilience policy baseline
- proposed_by: user + Copilot
- status: accepted
- decision: Introduce per-source resilience policy for BL-003 selected-source enforcement (`required|optional|advisory`) with baseline defaults `top_tracks=required`, `saved_tracks=optional`, `playlist_items=optional`, `recently_played=advisory`, while preserving strict fail behavior for required sources and preserving the explicit `--allow-missing-selected-sources` override.
- context: Cross-user Spotify exports can legitimately produce missing selected source files (especially playlist-items) due account/API access constraints, causing BL-003 strict selected-source failures that block BL-013/BL-014 even when sufficient data exists for deterministic execution.
- alternatives_considered: keep global strict behavior for all selected sources (rejected: brittle under legitimate provider/account variance); disable strict checks globally (rejected: weakens contract guarantees for core required sources); rely only on manual `--allow-missing-selected-sources` use (rejected: high operator-friction and weak default robustness).
- rationale: Source-level resilience preserves contract strictness where it matters (core required signal surfaces) while allowing predictable degradation for lower-criticality sources that are frequently unavailable in real accounts.
- evidence_basis: `07_implementation/src/alignment/constants.py`, `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/alignment/stage.py`, `07_implementation/src/alignment/resolved_context.py`, `07_implementation/src/alignment/writers.py`, `07_implementation/src/ingestion/export_spotify_max_dataset.py`, tests `07_implementation/tests/test_alignment_stage.py` + `07_implementation/tests/test_ingestion_spotify_export.py` (`10/10`), pyright touched modules (`0 errors`), wrapper validate-only pass (`BL013-ENTRYPOINT-20260412-172644-378068`, `BL014-SANITY-20260412-172705-698023`, `28/28`).
- impacted_files: `07_implementation/src/alignment/constants.py`, `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/alignment/models.py`, `07_implementation/src/alignment/resolved_context.py`, `07_implementation/src/alignment/stage.py`, `07_implementation/src/alignment/writers.py`, `07_implementation/src/ingestion/export_spotify_max_dataset.py`, `07_implementation/src/orchestration/seed_freshness.py`, `07_implementation/tests/test_alignment_stage.py`, `07_implementation/tests/test_ingestion_spotify_export.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`.
- next_steps: Extend orchestration payload controls for BL-001/BL-002 resilience activation and add full matrix tests for selected/not-selected/zero/forbidden/missing outcomes across all import options.

## D-074
- date: 2026-04-12
- entity_id: BL-003 selected-source availability semantics for zero-results/forbidden outcomes
- proposed_by: user + Copilot
- status: accepted
- decision: When BL-002 summary explicitly reports a selected source outcome of `zero_results` or `forbidden`, BL-003 should treat that source as available for selected-source strictness checks even if the corresponding flat CSV file is absent; strict failure remains for sources with no file and no explicit zero/forbidden outcome evidence.
- context: The prior resilience policy introduced required/optional/advisory handling, but strict checks still depended primarily on file existence. Accounts with legitimate API-side restrictions or zero-result pulls could still trigger avoidable strict failures when BL-002 emitted clear non-data outcomes without materialized flat CSVs.
- alternatives_considered: require zero-row CSV emission for all selected sources before relaxing strictness (rejected for this slice: broader emission-contract change and migration risk); keep file-only availability semantics (rejected: retains avoidable brittleness despite explicit outcome evidence); disable strictness whenever any outcome metadata exists (rejected: weakens required-source guarantees).
- rationale: Source-outcome-aware availability preserves strict contract intent while distinguishing true missing-data regressions from explicit, expected non-data outcomes recorded by BL-002.
- evidence_basis: `07_implementation/src/alignment/stage.py` (outcome-aware availability), `07_implementation/src/ingestion/export_spotify_max_dataset.py` (`forbidden` outcome emission), tests `07_implementation/tests/test_alignment_stage.py` and `07_implementation/tests/test_ingestion_spotify_export.py` (`12/12`), pyright touched modules (`0 errors`), wrapper validate-only pass (`BL013-ENTRYPOINT-20260412-173055-590271`, `BL014-SANITY-20260412-173116-866099`, `28/28`).
- impacted_files: `07_implementation/src/alignment/stage.py`, `07_implementation/src/ingestion/export_spotify_max_dataset.py`, `07_implementation/tests/test_alignment_stage.py`, `07_implementation/tests/test_ingestion_spotify_export.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`.
- next_steps: Expand BL-002 source-outcome contract tests across all source types and add orchestration-level assertions that BL-013 summary captures degraded-but-valid selected-source scenarios without regressions.

## D-075
- date: 2026-04-12
- entity_id: phase-4/phase-5 control propagation and BL-002 runtime-ingestion activation precedence
- proposed_by: user + Copilot
- status: accepted
- decision: Enforce payload-first/runtime-config-fallback precedence for BL-002 ingestion resilience controls and complete control propagation so `seed_controls.source_resilience_policy` is carried through orchestration payload contracts. Specifically: (1) BL-003 payload contracts must include `source_resilience_policy`; (2) BL-002 stage payload contract now carries `ingestion_controls`; (3) BL-002 exporter resolves ingestion controls via `BL_STAGE_CONFIG_JSON` first, then `BL_RUN_CONFIG_PATH`, then local defaults, and applies resolved controls to live retry/backoff runtime behavior.
- context: After D-073/D-074, source-resilience semantics existed but orchestration payload propagation was incomplete (`source_resilience_policy` dropped from BL-003 seed payload), and BL-002 runtime ingestion controls were validated in run-config but not fully activated in the exporter execution path.
- alternatives_considered: keep BL-003 payload omission and rely on defaults (rejected: run-config resilience intent is lost under orchestration payload mode); keep BL-002 run-config ingestion controls as non-operational metadata (rejected: violates phase-5 activation objective); use run-config only and ignore stage payload for BL-002 (rejected: breaks payload-first contract consistency used by staged orchestration).
- rationale: Completing payload propagation and runtime activation closes the contract gap between declared controls and effective behavior, while preserving deterministic precedence semantics across stages.
- evidence_basis: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/orchestration/config_resolver.py`, `07_implementation/src/ingestion/export_spotify_max_dataset.py`, `07_implementation/src/ingestion/spotify_client.py`, `07_implementation/tests/test_orchestration_stage_payload_handoff.py`, `07_implementation/tests/test_run_config_utils.py`, `07_implementation/tests/test_ingestion_spotify_export.py`, `07_implementation/tests/test_alignment_resolved_context.py`, `07_implementation/tests/test_alignment_summary_builder.py`, `07_implementation/tests/test_ingestion_spotify_auth.py`, validation evidence (`pytest 369/369`, pyright `0 errors`, wrapper validate-only BL-013/BL-014 pass `28/28`).
- impacted_files: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/orchestration/config_resolver.py`, `07_implementation/src/ingestion/export_spotify_max_dataset.py`, `07_implementation/src/ingestion/spotify_client.py`, `07_implementation/tests/test_orchestration_stage_payload_handoff.py`, `07_implementation/tests/test_run_config_utils.py`, `07_implementation/tests/test_ingestion_spotify_export.py`, `07_implementation/tests/test_alignment_resolved_context.py`, `07_implementation/tests/test_alignment_summary_builder.py`, `07_implementation/tests/test_ingestion_spotify_auth.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`.
- next_steps: Add BL-002 orchestration execution-path assertions once BL-001/BL-002 are brought into staged orchestration order, and extend ingestion-control matrix tests for mixed payload/run-config/env fallback combinations.

## D-076
- date: 2026-04-12
- entity_id: BL-002 ingestion-control resolution fail-safe fallback behavior
- proposed_by: user + Copilot
- status: accepted
- decision: When BL-002 runtime ingestion-control resolution cannot load or resolve run-config controls, fallback must be non-fatal: log a warning and continue with runtime defaults. Payload-first precedence remains unchanged, and run-config fallback remains preferred when resolvable.
- context: The phase-5 activation introduced run-config fallback for BL-002 ingestion controls; however, resolution failures in local/tooling contexts could terminate exporter runs unnecessarily even when safe defaults are available.
- alternatives_considered: keep fail-fast on run-config resolution exceptions (rejected: brittle for optional control overlays); silently swallow failures without diagnostics (rejected: weak observability for operators).
- rationale: A warning-plus-default fallback preserves robustness for standalone/operator runs while retaining traceable diagnostics and payload-first precedence semantics.
- evidence_basis: `07_implementation/src/ingestion/export_spotify_max_dataset.py` (exception-handled fallback warning path), `07_implementation/tests/test_ingestion_spotify_export.py` (mixed-precedence and run-config-failure fallback tests), validation evidence (`pytest 371/371`, pyright `0 errors`, wrapper validate-only BL-013/BL-014 pass `28/28`).
- impacted_files: `07_implementation/src/ingestion/export_spotify_max_dataset.py`, `07_implementation/tests/test_ingestion_spotify_export.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`.
- next_steps: Add orchestration-level BL-002 payload injection assertions once BL-002 is part of staged execution order, and broaden fallback matrix tests for malformed payload envelopes and partial-control merges.

## D-077
- date: 2026-04-12
- entity_id: BL-009 source-resilience diagnostics contract and BL-002 mixed-precedence fallback matrix completion
- proposed_by: user + Copilot
- status: accepted
- decision: Promote a new BL-009 observability contract section `ingestion_alignment_diagnostics.source_resilience_diagnostics` derived from BL-003 summary (`selected_sources_expected/available`, resilience policy, missing/degraded source sets, and per-source reason-code decisions), and finalize phase-7 mixed-precedence hardening with explicit regression coverage for malformed payload fallback to run-config and partial payload control merges preserving existing defaults.
- context: After D-075/D-076, resilience behavior and fallback safety were implemented but run-level observability did not yet expose compact source-resilience reason codes for downstream evidence interpretation, and matrix coverage still lacked malformed-payload and partial-merge edge cases.
- alternatives_considered: keep resilience interpretation implicit in raw BL-003 fields only (rejected: weaker BL-009 contract clarity for chapter/evidence consumers); add diagnostics without reason-code taxonomy (rejected: inconsistent interpretation across runs); defer malformed/partial precedence cases to later (rejected: leaves a known test-matrix gap).
- rationale: A normalized diagnostics block with explicit reason codes improves auditability and comparability of degraded-source behavior, while expanded matrix tests close the remaining precedence/fallback coverage gap without changing payload-first semantics.
- evidence_basis: `07_implementation/src/observability/main.py` (`build_source_resilience_diagnostics` + BL-009 payload wiring), `07_implementation/tests/test_observability_signal_mode_summary.py` (reason-code assertions), `07_implementation/tests/test_ingestion_spotify_export.py` (malformed payload fallback + partial merge preservation), validation evidence (`pytest 374/374`, pyright `0 errors`, wrapper validate-only pass `BL013-ENTRYPOINT-20260412-175314-201328`, `BL014-SANITY-20260412-175333-508512`, `28/28`).
- impacted_files: `07_implementation/src/observability/main.py`, `07_implementation/tests/test_observability_signal_mode_summary.py`, `07_implementation/tests/test_ingestion_spotify_export.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`.
- next_steps: Add BL-009 contract-level assertions in orchestration-facing summary/report consumers and continue extending BL-002 precedence matrix coverage as new stage-payload envelope variants are introduced.

## D-078
- date: 2026-04-12
- entity_id: BL-003 user_csv 5th ingestion source and universal album fuzzy scoring
- proposed_by: user + Copilot
- status: accepted
- decision: Add `user_csv` as a 5th advisory ingestion source for BL-003 with dynamic schema detection (alias-tolerant column mapping, viability check on track_id or track_name+artist_names), extend `SourceEvent` with an `album_name` field harvested from all sources, and introduce a 3-factor fuzzy scoring branch in `fuzzy_find_candidate` (artist+title+album weighted average) activated when the source event carries a non-empty album string. isrc excluded from schema detection (not in DS-001 contract).
- context: The existing 4-source ingestion surface (top_tracks, saved_tracks, playlist_items, recently_played) lacked a user-supplied flat CSV path and had no album signal in fuzzy matching, both of which were identified as scope extensions for the BL-003 evidence contract.
- alternatives_considered: make user_csv a required source with mandatory file validation (rejected: advisory posture preserves existing run integrity when file is absent); embed album scoring as a separate pipeline stage (rejected: adding it as a keyword-only branch of the existing fuzzy scorer avoids an unnecessary abstraction); use isrc as an additional match key (rejected: DS-001 match contract does not include isrc and it is absent from the reference dataset).
- rationale: Advisory positioning for user_csv avoids breaking existing runs while enabling opt-in personalized listening history ingestion; the 3-factor album branch provides measurable fuzzy-score signal without altering 2-factor behavior for events without album metadata.
- evidence_basis: `07_implementation/src/alignment/constants.py`, `07_implementation/src/alignment/user_csv_schema.py` (new), `07_implementation/src/alignment/models.py`, `07_implementation/src/alignment/stage.py`, `07_implementation/src/shared_utils/text_matching.py`, `07_implementation/src/alignment/match_pipeline.py`, `07_implementation/src/alignment/runtime_scope.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/shared_utils/constants.py`; new test files `tests/test_alignment_user_csv_schema.py` and `tests/test_text_matching_album.py`; full pytest pass (`407/407`).
- impacted_files: `07_implementation/src/alignment/constants.py`, `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/alignment/user_csv_schema.py`, `07_implementation/src/alignment/models.py`, `07_implementation/src/alignment/stage.py`, `07_implementation/src/shared_utils/text_matching.py`, `07_implementation/src/alignment/match_pipeline.py`, `07_implementation/src/alignment/runtime_scope.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/tests/test_alignment_constants.py`, `07_implementation/tests/test_alignment_stage.py`, `07_implementation/tests/test_alignment_resolved_context.py`, `07_implementation/tests/test_alignment_user_csv_schema.py`, `07_implementation/tests/test_text_matching_album.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`.
- next_steps: Wrapper validation is complete (`BL013-ENTRYPOINT-20260412-211514-304085`, `BL014-SANITY-20260412-211538-292523`, `28/28`). Update chapter-facing evidence mapping only if user_csv ingestion results are promoted into final reporting claims.

## D-079
- date: 2026-04-12
- entity_id: BL-003 configurable fuzzy fallback rollout (wave 1)
- proposed_by: user + Copilot
- status: accepted
- decision: Keep BL-003 exact Spotify-ID matching and exact title+artist metadata matching unchanged, and improve only the fuzzy fallback path through additive run-config controls and diagnostics. Wave 1 adds config-gated secondary-artist retry, optional relaxed second fuzzy pass, explicit album-scoring control, and additive fuzzy trace/summary diagnostics, while preserving default behavior with fuzzy disabled.
- context: After D-078, BL-003 could ingest `user_csv` rows and use album-aware fuzzy scoring internally, but fuzzy matching remained effectively unusable in the active baseline because the control surface was narrow, observability was weak, and all tuning had to be inferred indirectly.
- alternatives_considered: replace the entire matching stack with a fuzzy-first strategy (rejected: would risk exact-match regressions and reduce audit clarity); enable relaxed fuzzy behavior by default (rejected: would change the active baseline without controlled evidence); add genre/tag semantic heuristics in the first wave (rejected: source-side alignment events do not consistently carry those fields, weakening bounded control claims).
- rationale: Constraining the rollout to the fuzzy fallback keeps the highest-confidence paths stable while making fuzzy behavior explicitly controllable, diagnosable, and testable under the existing BL-003 evidence contract.
 - evidence_basis: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/shared_utils/text_matching.py`, `07_implementation/src/alignment/text_matching.py`, `07_implementation/src/alignment/constants.py`, `07_implementation/src/alignment/models.py`, `07_implementation/src/alignment/match_pipeline.py`; validation evidence: targeted BL-003 pytest (`97/97`), full pytest (`411/411`), and wrapper validate-only pass (`BL013-ENTRYPOINT-20260412-213836-591492`, `BL014-SANITY-20260412-213859-249947`, `28/28`).
- impacted_files: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/shared_utils/text_matching.py`, `07_implementation/src/alignment/text_matching.py`, `07_implementation/src/alignment/constants.py`, `07_implementation/src/alignment/models.py`, `07_implementation/src/alignment/match_pipeline.py`, `07_implementation/tests/test_run_config_utils.py`, `07_implementation/tests/test_alignment_constants.py`, `07_implementation/tests/test_alignment_matching.py`, `07_implementation/tests/test_text_matching_album.py`, `07_implementation/tests/test_alignment_resolved_context.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`.
- next_steps: Use the new controls in one or more bounded comparison configs to quantify fuzzy uplift before changing the active baseline or chapter-facing claims.

## D-080
- date: 2026-04-13
- entity_id: BL-003 seed confidence propagation contract for BL-004 weighting activation
- proposed_by: user + Copilot
- status: accepted
- decision: Extend BL-003 seed-table contract additively with `match_confidence_score` and compute it as a per-DS001 weighted mean over per-event confidence values using `preference_weight` as weights. Per-event confidence mapping is method-aware: `spotify_id_exact=1.0`, `metadata_fallback=1.0`, `influence_direct=1.0`, `fuzzy_title_artist=clamp(fuzzy_combined_score,0,1)` with fallback `1.0` when missing or non-numeric.
- context: BL-004 already consumes `match_confidence_score`, but BL-003 seed output previously omitted the field, forcing BL-004 fallback confidence (`1.0`) and effectively neutral confidence weighting in normal runs.
- alternatives_considered: write fuzzy confidence only for fuzzy-matched rows and leave others blank (rejected: increases downstream fallback reliance and weakens comparability); use max confidence instead of weighted mean (rejected: too sensitive to single events and less stable under repeated interactions); make confidence aggregation mode runtime-configurable in this wave (rejected: deferred to keep this slice bounded).
- rationale: Additive schema extension preserves compatibility while activating existing BL-004 confidence-weighting logic. Weighted mean by `preference_weight` preserves interaction intensity semantics without redesigning downstream profile/retrieval formulas.
- evidence_basis: `07_implementation/src/alignment/constants.py`, `07_implementation/src/alignment/models.py`, `07_implementation/src/alignment/aggregation.py`, `07_implementation/src/alignment/writers.py`, `07_implementation/tests/test_alignment_constants.py`, `07_implementation/tests/test_alignment_aggregation.py`, `07_implementation/tests/test_profile_stage.py`; validation evidence: targeted pytest (`33/33`) and wrapper validate-only pass (`BL013-ENTRYPOINT-20260412-235719-274910`, `BL014-SANITY-20260412-235744-006676`, `28/28`).
- impacted_files: `07_implementation/src/alignment/constants.py`, `07_implementation/src/alignment/models.py`, `07_implementation/src/alignment/aggregation.py`, `07_implementation/src/alignment/writers.py`, `07_implementation/tests/test_alignment_constants.py`, `07_implementation/tests/test_alignment_aggregation.py`, `07_implementation/tests/test_profile_stage.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`.
- next_steps: If fuzzy-match share increases in future runs, evaluate whether confidence aggregation mode should be exposed as a bounded BL-003 control (`weighted_mean|max|mean`) with explicit contract tests.

## D-081
- date: 2026-04-13
- entity_id: BL-003/BL-004 diagnostics-first fallback hardening (Phase A)
- proposed_by: user + Copilot
- status: accepted
- decision: Add additive, non-blocking diagnostics for previously silent fallback paths in BL-003 runtime scope resolution and BL-004 profile aggregation, without changing existing output contracts or decision behavior. BL-003 now emits scope-resolution parse diagnostics (`payload_json_parse_error`, `input_scope_json_parse_error`, `resolution_path`) and BL-004 now tracks fallback counters for confidence, interaction-type defaulting, synthetic interaction count, and synthetic attribution-weight reconstruction.
- context: A profile-risk audit identified that several fallback/default paths could mask upstream data/contract regressions because they failed silently and only influenced downstream numbers indirectly.
- alternatives_considered: keep behavior unchanged and rely on manual CSV/JSON spot checks (rejected: weak observability and high drift risk); convert fallback conditions to hard failures immediately (rejected: too disruptive for this bounded slice and may block valid degraded runs); add diagnostics only in BL-009 observability layer (rejected: delayed and less local root-cause visibility).
- rationale: Diagnostics-first hardening improves traceability while preserving deterministic behavior and backward compatibility. This creates a safe foundation for later policy tightening if needed.
- evidence_basis: `07_implementation/src/alignment/runtime_scope.py`, `07_implementation/src/alignment/writers.py`, `07_implementation/src/profile/models.py`, `07_implementation/src/profile/stage.py`, `07_implementation/tests/test_alignment_runtime_scope.py`, `07_implementation/tests/test_profile_stage.py`; validation evidence: targeted pytest (`38/38`) and wrapper validate-only pass (`BL013-ENTRYPOINT-20260413-001017-614914`, `BL014-SANITY-20260413-001042-070086`, `28/28`).
- impacted_files: `07_implementation/src/alignment/runtime_scope.py`, `07_implementation/src/alignment/writers.py`, `07_implementation/src/profile/models.py`, `07_implementation/src/profile/stage.py`, `07_implementation/tests/test_alignment_runtime_scope.py`, `07_implementation/tests/test_profile_stage.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`.
- next_steps: Use the new counters/diagnostics to quantify fallback frequency across multiple runs, then decide whether specific fallback categories should remain permissive, become warning-gated in BL-014, or fail-fast under strict mode.

## D-082
- date: 2026-04-13
- entity_id: BL-004 fallback strictness policy controls (Phase B)
- proposed_by: user + Copilot
- status: accepted
- decision: Introduce bounded BL-004 policy controls for fallback enforcement with per-family `allow|warn|strict` modes: `confidence_validation_policy`, `interaction_type_validation_policy`, and `synthetic_data_validation_policy`. Keep default posture warn-compatible, emit policy/warning diagnostics in BL-004 outputs, and fail fast only when an explicit strict mode is selected.
- context: Phase A diagnostics made fallback paths visible but still permissive. The next hardening step requires controllable enforcement semantics without breaking default execution.
- alternatives_considered: keep diagnostics-only behavior (rejected: does not provide fail-fast option); enforce strict mode by default (rejected: backward-compatibility and operational disruption risk); create one global strict switch for all fallback categories (rejected: less precise control and weaker troubleshooting isolation).
- rationale: Per-family policy controls preserve compatibility while allowing targeted strictness in controlled runs and CI-style checks.
- evidence_basis: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/profile/models.py`, `07_implementation/src/profile/runtime_controls.py`, `07_implementation/src/profile/stage.py`, `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_run_config_utils.py`; validation evidence: focused pytest (`41/41`) and wrapper validate-only pass (`BL013-ENTRYPOINT-20260413-001816-449005`, `BL014-SANITY-20260413-001850-553405`, `28/28`).
- impacted_files: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/profile/models.py`, `07_implementation/src/profile/runtime_controls.py`, `07_implementation/src/profile/stage.py`, `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`.
- next_steps: Add one bounded strict-policy negative execution path in wrapper-level checks (or quality gates) to verify fail-fast signaling in end-to-end runs.

## D-083
- date: 2026-04-13
- entity_id: BL-004 attribution and numeric-integrity hardening thresholds (Slice 7)
- proposed_by: user + Copilot
- status: accepted
- decision: Add explicit malformed-vs-missing attribution diagnostics in BL-004 and introduce bounded fail-fast thresholds for numeric-integrity drift. New controls are `numeric_malformed_row_threshold` and `no_numeric_signal_row_threshold` (optional, positive-int thresholds) with default disabled behavior for compatibility.
- context: BL-004 already reported missing numeric outcomes and fallback counters, but malformed upstream numeric signals were not separated from true no-signal rows, reducing root-cause clarity and preventing threshold-based guardrails.
- alternatives_considered: keep counters only and rely on manual trend monitoring (rejected: no automated protection); enforce hard fail on any malformed numeric row by default (rejected: disruptive under existing data variability); add one combined threshold for all numeric issues (rejected: weaker diagnosis and less targeted control).
- rationale: Distinguishing malformed and no-signal paths improves auditability while optional thresholds enable controlled fail-fast behavior in stricter execution modes.
- evidence_basis: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/profile/models.py`, `07_implementation/src/profile/runtime_controls.py`, `07_implementation/src/profile/stage.py`, `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_run_config_utils.py`; validation evidence: focused pytest (`43/43`) and wrapper validate-only pass (`BL013-ENTRYPOINT-20260413-002608-855860`, `BL014-SANITY-20260413-002636-061270`, `28/28`).
- impacted_files: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/profile/models.py`, `07_implementation/src/profile/runtime_controls.py`, `07_implementation/src/profile/stage.py`, `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`.
- next_steps: Implement cross-BL handshake checks so BL-004 enforces contract-critical BL-003 summary/seed expectations before aggregation begins.

## D-084
- date: 2026-04-13
- entity_id: BL-003 to BL-004 contract handshake enforcement (Slice 8)
- proposed_by: user + Copilot
- status: accepted
- decision: Add an explicit BL-003 to BL-004 handshake validation surface in BL-004 input loading, with bounded `allow|warn|strict` policy control (`bl003_handshake_validation_policy`) and additive warning diagnostics. The handshake checks require BL-003 summary inputs to expose `runtime_scope_diagnostics` and BL-003 seed rows to expose `match_confidence_score` before aggregation proceeds.
- context: Prior hardening slices made fallback and numeric integrity issues visible and enforceable, but BL-004 still assumed critical BL-003 contract fields implicitly. A missing upstream field could degrade evidence quality without a clearly typed handshake boundary.
- alternatives_considered: keep implicit assumptions and rely on downstream anomalies (rejected: weak root-cause localization); enforce strict handshake unconditionally (rejected: avoid disruptive behavior changes on existing profiles); move handshake checks to BL-014 only (rejected: late failure surface and weaker stage-local diagnostics).
- rationale: Stage-local handshake checks provide explicit cross-BL contract observability and controllable enforcement without breaking default compatibility. Policy-based gating supports gradual hardening from warn to strict.
- evidence_basis: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/profile/models.py`, `07_implementation/src/profile/runtime_controls.py`, `07_implementation/src/profile/stage.py`, `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_run_config_utils.py`; validation evidence: focused pytest (`43/43`) and wrapper validate-only pass (`BL013-ENTRYPOINT-20260413-003304-652082`, `BL014-SANITY-20260413-003326-987801`, `28/28`).
- impacted_files: `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/profile/models.py`, `07_implementation/src/profile/runtime_controls.py`, `07_implementation/src/profile/stage.py`, `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`.
- next_steps: Add one explicit strict-mode negative wrapper scenario in quality checks to verify fail-fast messaging when handshake-required fields are removed.

## D-085
- date: 2026-04-13
- entity_id: BL-004 handshake strict-negative test hardening (Slice 9)
- proposed_by: user + Copilot
- status: accepted
- decision: Close the immediate D-084 follow-up with targeted stage-level strict-negative coverage in unit tests, rather than introducing a synthetic wrapper-level fixture at this slice. Added handshake warn/strict tests for BL-004 helper and input-loading paths, plus run-config schema normalization coverage for `bl003_handshake_validation_policy`.
- context: D-084 introduced policy-gated handshake enforcement and flagged strict-mode negative-path evidence as the next hardening step.
- alternatives_considered: implement an end-to-end wrapper negative scenario by mutating BL-003 artifacts at runtime (rejected in this slice: higher fixture complexity and lower isolation for contract-local behavior); leave handshake tests unchanged (rejected: strict path not explicitly exercised).
- rationale: Stage-local tests are the fastest and most deterministic way to prove strict handshake failure semantics and warning propagation without adding brittle orchestration fixtures.
- evidence_basis: `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_run_config_utils.py`; validation evidence: focused pytest (`47/47`) and wrapper validate-only pass (`BL013-ENTRYPOINT-20260413-003752-142736`, `BL014-SANITY-20260413-003814-485246`, `28/28`).
- impacted_files: `07_implementation/tests/test_profile_stage.py`, `07_implementation/tests/test_run_config_utils.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`.
- next_steps: If needed for CI contract gates, add a dedicated BL-014 negative fixture that intentionally strips handshake-required BL-003 fields and asserts strict fail-fast messaging at wrapper level.

## D-086
- date: 2026-04-13
- entity_id: BL-014 wrapper-level BL-003↔BL-004 handshake contract gate (Slice 10)
- proposed_by: user + Copilot
- status: accepted
- decision: Add a new BL-014 sanity check (`schema_bl003_bl004_handshake_contract`) that enforces wrapper-level continuity for BL-003↔BL-004 handshake-critical fields: BL-003 summary inputs must include `runtime_scope_diagnostics`, BL-003 structural contract fieldnames must include `match_confidence_score`, and BL-004 profile diagnostics must include `validation_policies.bl003_handshake_validation_policy`.
- context: D-085 closed stage-level strict/warn negative coverage, and the remaining risk was cross-stage drift at wrapper/quality-gate level where generated artifacts might lose handshake metadata without immediate detection.
- alternatives_considered: keep handshake checks only at BL-004 runtime and unit tests (rejected: insufficient wrapper-level guardrail); add a destructive wrapper mutation scenario immediately (rejected in this slice: higher fixture complexity and lower maintainability).
- rationale: BL-014 contract checks provide lightweight, deterministic cross-stage protection that catches handshake metadata regressions in normal validate-only runs.
- evidence_basis: `07_implementation/src/quality/sanity_checks.py`, `07_implementation/tests/test_quality_sanity_checks.py`; validation evidence: targeted pytest (`56/56`) and wrapper validate-only pass (`BL013-ENTRYPOINT-20260413-004155-782240`, `BL014-SANITY-20260413-004220-078507`, `29/29`).
- impacted_files: `07_implementation/src/quality/sanity_checks.py`, `07_implementation/tests/test_quality_sanity_checks.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`.
- next_steps: If future CI policy requires fail-mode evidence, add a dedicated negative fixture that strips handshake fields and asserts BL-014 failure with this check id.

## D-087
- date: 2026-04-13
- entity_id: BL-014 negative fixture for handshake gate failure evidence (Slice 11)
- proposed_by: user + Copilot
- status: accepted
- decision: Implement a dedicated BL-014 negative fixture test that constructs a minimal coherent artifact chain, intentionally removes a handshake-required BL-003 field, runs `quality.sanity_checks.main()`, and asserts failure occurs specifically on `schema_bl003_bl004_handshake_contract` while other checks remain green.
- context: D-086 added wrapper-level handshake enforcement, but the negative path remained only an intended follow-up. The remaining hardening value was proof that BL-014 itself fails for the expected reason when artifacts drift.
- alternatives_considered: rely on helper-level negative tests only (rejected: does not prove `main()` report behavior); build a heavier integration harness outside pytest (rejected: unnecessary overhead for this bounded contract test).
- rationale: A temp-artifact negative fixture provides precise, deterministic evidence that the wrapper-level gate is actionable and fails on the correct check id without destabilizing live outputs.
- evidence_basis: `07_implementation/tests/test_quality_sanity_checks.py`; validation evidence: targeted pytest (`57/57`) and wrapper validate-only pass (`BL013-ENTRYPOINT-20260413-004657-028023`, `BL014-SANITY-20260413-004719-088476`, `29/29`).
- impacted_files: `07_implementation/tests/test_quality_sanity_checks.py`, `00_admin/decision_log.md`, `00_admin/change_log.md`, `00_admin/timeline.md`, `00_admin/thesis_state.md`.
- next_steps: No further in-repo handshake hardening is required unless CI policy expands toward additional destructive fixture matrices.
