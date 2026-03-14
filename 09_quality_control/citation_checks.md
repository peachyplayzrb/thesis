# Citation Checks

## Status
- Date: 2026-03-14
- Scope checked: Chapter 2 draft (`08_writing/chapter2.md`), Chapter 3 draft (`08_writing/chapter3.md`), Chapter 5 draft (`08_writing/chapter5.md`)
- Bibliography source: `08_writing/references.bib` (synchronized with legacy pack and subsequent vetted additions, including P-064 and P-065)

## Claim-Level Checks
| Claim ID | Chapter 2 claim summary | Evidence keys used | Support level | Risk / note |
| --- | --- | --- | --- | --- |
| CIT-001 | Accuracy-only evaluation is insufficient for explainable recommenders | `tintarev_survey_2007`, `tintarev_evaluating_2012`, `zhang_explainable_2020` | high | No material risk.
| CIT-002 | Explanation goals can conflict and must be evaluated explicitly | `tintarev_evaluating_2012` | high | Single primary source but strong direct fit.
| CIT-003 | User control effects in music RS are user-dependent | `jin_effects_2020`, `andjelkovic_moodplay_2019` | medium | More replication evidence would strengthen generalizability.
| CIT-004 | Music recommendation has sequence/context challenges beyond item ranking | `schedl_current_2018`, `deldjoo_content-driven_2024`, `neto_algorithmic_2023`, `schedl_investigating_2017`, `shakespeare_reframing_2025` | high | No material risk.
| CIT-005 | Similarity judgments in music have agreement limits and require metric-sensitive interpretation | `flexer_problem_2016`, `siedenburg_modeling_2017`, `bonnin_automated_2015`, `zamani_analysis_2019`, `schweiger_impact_2025`, `furini_social_2024` | medium-high | Playlist-objective support now includes direct music-domain metric evidence; limitation remains on broad deterministic similarity-function isolation studies across multiple ranking objectives.
| CIT-006 | Feature-based content approaches support interpretable design | `deldjoo_content-driven_2024`, `bogdanov_semantic_2013` | medium-high | Ensure chapter wording avoids claiming superior accuracy.
| CIT-007 | Hybrid/neural approaches are strong comparators but more complex | `he_neural_2017`, `cano_hybrid_2017`, `liu_multimodal_2025` | medium-high | Keep claim as trade-off framing, not universal rule.
| CIT-008 | Alignment should use staged entity-resolution pipeline | `allam_improved_2018`, `papadakis_blocking_2021`, `elmagarmid_duplicate_2007`, `binette_almost_2022`, `barlaug_neural_2021` | medium-high | Evidence base is stronger but still largely cross-domain rather than music-benchmark specific.
| CIT-009 | Recommender accountability requires reproducibility controls | `beel_towards_2016`, `bellogin_improving_2021`, `cavenaghi_systematic_2023`, `ferrari_dacrema_troubling_2021`, `zhu_bars_2022`, `anelli_elliot_2021`, `betello_reproducible_2025` | high | No material risk.
| CIT-010 | Benchmark comparability requires explicit protocol and metric reporting | `zhu_bars_2022`, `ferrari_dacrema_troubling_2021`, `herlocker_evaluating_2004`, `anelli_elliot_2021`, `betello_reproducible_2025` | high | Keep wording scoped to evaluation-process rigor, not absolute model superiority.
| CIT-011 | Music4All corpus choice is defensible for this thesis data scope | `pegoraro_santana_music4all_2020`, `deldjoo_content-driven_2024`, `ru_improving_2023` | medium-high | Third-party support added at comparator-context level; retain task-transfer caveat.
| CIT-012 | Modern music-model explainability/multimodal performance evidence should be framed as comparator context, not scope obligation | `sotirou_musiclime_2025`, `ru_improving_2023`, `moysis_music_2023`, `zhu_muq_2025`, `liu_aggregating_2025` | medium | Avoid implying that deep multimodal methods are required for MVP success criteria.
| CIT-013 | Recommender evaluation claims should connect protocol rigor and practical-value interpretation, not metric-only comparisons | `jannach_measuring_2019`, `bauer_exploring_2024`, `anelli_elliot_2021`, `ferrari_dacrema_troubling_2021` | high | Keep claims scoped to evaluation-governance and interpretation discipline; avoid asserting universal KPI transfer.
| CIT-014 | Playlist-continuation conclusions should be interpreted with protocol and method-composition awareness | `zamani_analysis_2019`, `teinemaa_composition_2018`, `ferraro_automatic_2018`, `vall_feature-combination_2019` | medium-high | Teinemaa source is a team report; maintain source-type caveat while using it as complementary implementation evidence.
| CIT-015 | Playlist-generation and music benchmark outcomes require protocol-aware, popularity-aware interpretation | `bonnin_automated_2015`, `mcfee_million_2012`, `zamani_analysis_2019` | medium-high | McFee is not playlist-continuation-specific; use as benchmark-method context support, not direct APC evidence.

## Overclaim Guardrails Applied
- Deterministic approach is positioned as scope/goal aligned, not universally superior.
- Entity-resolution support is explicitly marked as mostly domain-general.
- Control-related findings are treated as conditional on user differences.

## Residual Gaps To Monitor
- Add at least one music-specific alignment reliability source if found (still open despite stronger cross-domain ER support).
- Keep one bounded limitation note on deterministic similarity-function isolation evidence under playlist objectives.
- Preserve the existing Music4All task-transfer caveat (third-party support exists but is not playlist-task-equivalent evidence).
- Keep POI-domain evaluation survey evidence (`sanchez_pointofinterest_2022`) explicitly marked as transfer support, not music-core evidence.
- Preserve distinction between evidence statements and thesis interpretation in final edits.

## RQ Viability Audit Actions (2026-03-14)
- Audit verdict reference: `09_quality_control/rq_alignment_checks.md` (RQC-004, `CAUTION-GO`).
- Action V-ACT-001: close or explicitly bound music-domain alignment-reliability evidence risk.
- Action V-ACT-002: add playlist-oriented similarity-metric comparison evidence (or mark bounded limitation).
- Action V-ACT-003: add independent third-party Music4All usage/benchmark evidence (or justify closest substitute).
- Action V-ACT-004: verify Chapter 2 wording keeps deterministic approach as goal-aligned design choice, not universal performance claim.
- Action progress (2026-03-14): V-ACT-004 completed via wording reinforcement in `08_writing/chapter2.md`.
- Action progress (2026-03-14): V-ACT-001 explicitly bounded in `08_writing/chapter2.md` Section 2.5 (cross-domain ER support with music-specific uncertainty statement).
- Action progress (2026-03-14): V-ACT-002 further strengthened using newly ingested `furini_social_2024` and `schweiger_impact_2025` alongside existing `fkih_similarity_2022`, `siedenburg_modeling_2017`, `bonnin_automated_2015`, and `zamani_analysis_2019`; bounded limitation remains narrowed to limited broad isolation evidence for deterministic similarity-function effects across multiple playlist objectives.
- Action progress (2026-03-14): V-ACT-003 closed to comparator-context level by adding independent third-party Music4All benchmark usage support via `ru_improving_2023` in `08_writing/chapter2.md` Section 2.3.
- Freeze gate status: `freeze_ready_with_bounded_limitation`.
- Freeze disposition (2026-03-14): Chapter 2 is approved for freeze because V-ACT-001, V-ACT-003, and V-ACT-004 are closed, and V-ACT-002 is explicitly bounded in chapter text and QC logs.
- Accepted bounded limitation: the current set now includes initial direct music-domain metric-comparison evidence, but still lacks broad multi-dataset studies that isolate deterministic similarity-function effects across multiple playlist-objective metrics; this remains logged for future strengthening and does not block Chapter 2 freeze.

## Chapter 3 Citation Risk Notes
- Alignment pipeline claims are currently supported by entity-resolution surveys/method papers (`allam_improved_2018`, `papadakis_blocking_2021`, `barlaug_neural_2021`) and should be presented as cross-domain support with music-specific uncertainty.
- Reproducibility/accountability claims are strongly supported by recommender-specific evidence (`beel_towards_2016`, `bellogin_improving_2021`, `cavenaghi_systematic_2023`).
- Deterministic design rationale should remain framed as thesis-goal alignment (inspectability/replayability), not as a global performance claim versus hybrid/neural approaches.

