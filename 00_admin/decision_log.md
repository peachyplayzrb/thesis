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
