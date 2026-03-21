# Decision Log

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
- upstream artifacts from `07_implementation/implementation_notes/data_layer/outputs/`, `07_implementation/implementation_notes/test_assets/`, `07_implementation/implementation_notes/profile/outputs/`, `07_implementation/implementation_notes/retrieval/outputs/`, `07_implementation/implementation_notes/scoring/outputs/`, `07_implementation/implementation_notes/playlist/outputs/`, and `07_implementation/implementation_notes/transparency/outputs/`
- generated BL-009 artifacts in `07_implementation/implementation_notes/observability/outputs/`

impacted_files:
- `06_data_and_sources/schema_notes.md`
- `07_implementation/backlog.md`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
- `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`
- `07_implementation/implementation_notes/observability/outputs/bl009_run_observability_log.json`
- `07_implementation/implementation_notes/observability/outputs/bl009_run_index.csv`

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
- `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_report.json`
- `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_run_matrix.csv`
- `07_implementation/experiment_log.md` (`EXP-012`)

impacted_files:
- `07_implementation/implementation_notes/profile/build_bl004_preference_profile.py`
- `07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py`
- `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`
- `07_implementation/implementation_notes/playlist/build_bl007_playlist.py`
- `07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py`
- `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`
- `07_implementation/implementation_notes/reproducibility/run_bl010_reproducibility_check.py`
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
- `07_implementation/implementation_notes/reproducibility/outputs/bl010_reproducibility_config_snapshot.json`
- `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_report.json`
- `07_implementation/implementation_notes/controllability/outputs/bl011_controllability_run_matrix.csv`
- `07_implementation/experiment_log.md` (`EXP-013`)

impacted_files:
- `07_implementation/implementation_notes/controllability/run_bl011_controllability_check.py`
- `07_implementation/implementation_notes/controllability/outputs/`
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
- `07_implementation/implementation_notes/profile/build_bl004_preference_profile.py`
- `07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py`
- `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`
- `07_implementation/implementation_notes/playlist/build_bl007_playlist.py`
- `07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py`
- `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`

impacted_files:
- `07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py`
- `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`
- `07_implementation/implementation_notes/entrypoint/outputs/`
- `07_implementation/backlog.md`
- `07_implementation/experiment_log.md`
- `07_implementation/test_notes.md`
- `00_admin/change_log.md`

review_date:
none

id: D-014
date: 2026-03-21
status: accepted

context:
BL-019 was previously a deferred placeholder for alternative corpus engineering. The current need is to define a practical, repeatable dataset-build workflow for the active Onion MVP path so data refreshes are deterministic and quality-gated before downstream reruns.

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
- `07_implementation/implementation_notes/data_layer/outputs/onion_canonical_track_table.csv`
- `07_implementation/implementation_notes/data_layer/outputs/onion_join_coverage_report.json`
- `07_implementation/implementation_notes/data_layer/outputs/onion_selected_column_manifest.json`

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
- `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
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
- `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`
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
