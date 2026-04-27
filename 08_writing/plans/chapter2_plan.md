# Chapter 2 Plan (Viability-First)

Document status: active planning note  
Date: 2026-03-14  
Owner: AI + Tim

## 1) Planning Goal
Produce a high-quality Chapter 2 that:
- directly supports the locked RQ,
- avoids overclaiming,
- provides clear literature-to-design traceability,
- is ready for Chapter 3 and evaluation alignment.

Locked RQ reference:
What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

## 2) Viability Verdict To Respect
Source: `09_quality_control/rq_alignment_checks.md` (RQC-004)
- RQ status: aligned
- Viability status: `CAUTION-GO`
- Interpretation: proceed now; freeze only after closing or explicitly bounding residual evidence risks.

## 3) Chapter 2 Core Argument (One Sentence)
The literature supports a deterministic, inspectable, and controllable music playlist pipeline as a goal-aligned engineering choice under thesis constraints, while acknowledging that hybrid/neural methods can outperform on some metrics at the cost of complexity and reduced inspectability.

## 4) Section Blueprint (Aligned To Current Chapter 2)
Use this exact structure from `08_writing/chapter2.md`:

2.1 Foundations, Scope, and Thesis Positioning
- Position the thesis as engineering/design contribution, not benchmark-model novelty.
- Set contribution framing around transparency, controllability, observability, and reproducibility.

2.2 Core Recommendation Paradigms and Their Trade-offs
- Compare content-based, collaborative, and hybrid families with trade-off discipline.
- Keep feature/metric/weighting choices explicit and reviewable.

2.3 Transparency, Explainability, Controllability, Observability, and Evaluation
- Define terms clearly and separate mechanism-linked explanation from post-hoc rationalization.
- Establish process-plus-outcome evaluation framing used later in Chapter 4.

2.4 Preference Evidence, Profile Construction, and Candidate Shaping
- Treat profile construction and candidate shaping as first-class design choices.
- Link influence controls and candidate thresholds to controllability/auditability claims.

2.5 Music Recommendation and Playlist-Specific Challenges
- Cover sequence/coherence/diversity trade-offs and subjective-similarity limits.
- Bound claims about feature proxies and listener intent.

2.6 Deterministic Feature-Based Design Rationale with Comparator Context
- Justify deterministic design as scope- and objective-aligned.
- Keep neural/hybrid methods in comparator context without strawman framing.

2.7 Cross-Source Alignment Reliability, Reproducibility Governance, and Synthesis
- Present staged alignment rationale and run-level governance expectations.
- Close with integrated synthesis that defines the Chapter 3 handoff.

## 5) Evidence Targets (Must-Hit)
Mapped to viability actions in `09_quality_control/citation_checks.md`:
- V-ACT-001: Add or bound music-domain alignment reliability evidence.
- V-ACT-002: Add or bound playlist-oriented similarity-metric comparison evidence.
- V-ACT-003: Add or bound independent third-party Music4All usage evidence.
- V-ACT-004: Verify wording keeps deterministic choice goal-aligned (not universally superior).

If a target cannot be fully closed, add explicit limitation wording and cross-reference `09_quality_control/citation_checks.md`.

## 6) Claim Discipline Rules (No Overreach)
- Every major claim must map to `09_quality_control/claim_evidence_map.md`.
- Mark evidence vs interpretation explicitly in prose.
- Avoid words like "proves" or "best" for model-family claims.
- Keep deep/hybrid comparators present as trade-off context.

## 7) Literature-to-Design Traceability Output
For each Chapter 2 section (2.1 to 2.7), end with 1 short "design consequence" sentence that points forward to Chapter 3 architecture decisions.

Minimum forward links:
- transparency literature -> score-trace and explanation fidelity mechanisms
- controllability literature -> influence controls and parameter sensitivity
- playlist literature -> assembly-stage constraints and ordering logic
- alignment literature -> staged matching pipeline
- reproducibility and synthesis literature -> run-level config/logging controls plus explicit Chapter 3 handoff criteria

## 8) Execution Plan (Fast, Practical)
Step 1: Stabilize structure (same day)
- Ensure section order matches blueprint above.
- Remove duplicated points and weakly supported side claims.

Step 2: Close evidence gaps (1 to 2 focused sessions)
- Insert strongest available sources for V-ACT-001..003.
- If unavailable, add explicit bounded limitation text and risk note.

Step 3: Overclaim pass (same day as Step 2)
- Check deterministic rationale language against V-ACT-004.
- Tighten comparator framing for hybrid/neural literature.

Step 4: Traceability pass (same day)
- Add explicit section-ending design consequences.

Step 5: Freeze gate check (final)
- Confirm all V-ACT items closed or bounded.
- Confirm chapter remains aligned with `00_admin/thesis_state.md`.

## 9) Definition of Done (Chapter 2 Ready)
- Chapter supports locked RQ without scope drift.
- Contradictory evidence is acknowledged and interpreted cautiously.
- Residual evidence risks are either closed or explicitly bounded.
- Literature-to-design bridge is explicit and usable by Chapter 3.
- Citation checks and RQ alignment logs are up to date.

## 10) Immediate Next Work Package
- Freeze and maintain Chapter 2 with bounded limitation wording intact in `08_writing/chapter2.md`.
- Keep the accepted V-ACT-002 bounded limitation synchronized with `09_quality_control/citation_checks.md`.
- Shift primary effort to Chapter 4 evidence production (reproducibility, controllability, inspectability, and rule-compliance outputs).

## 11) Progress Update (2026-03-14)
- Completed: V-ACT-004 wording reinforcement in `08_writing/chapter2.md`.
- Completed: targeted source pass and Chapter 2 updates for V-ACT-001..003 using existing processed notes.
- Completed: section-level literature-to-design traceability pass (explicit design-consequence lines added to Sections 2.1 to 2.6).
- Completed: Chapter 2 freeze gate check against citation and RQ alignment logs.
- Current status: freeze approved with one accepted bounded limitation (direct playlist-objective metric-comparison evidence remains limited in the current source set).

## 12) Progress Update (2026-03-15)
- Completed: integrated final Chapter 2 synthesis draft in `08_writing/chatper2_final draft.md` with readability and claim-discipline refinement.
- Completed: full cited-paper verbatim audit generation in `09_quality_control/chapter2_verbatim_audit.md` using local PDF extraction.
- Completed: iterative claim hardening pass until audit reported `weak_support=0` for Chapter 2 citation claims.
- Completed: QC synchronization across `09_quality_control/citation_checks.md`, `09_quality_control/chapter_readiness_checks.md`, and `09_quality_control/rq_alignment_checks.md`.
- Current status: Chapter 2 finalized in target length range (2.5k-3k words) and fully synced with active project controls.

## 13) Temp-Cycle Update (2026-03-15)
- Completed: created separate working variant `08_writing/chapter2_temp.md` for additional evidence-discipline hardening.
- Completed: repeated rerun/recheck loop until `09_quality_control/chapter2_temp_verbatim_audit.md` reported `weak_support=0`.
- Constraint honored: temp version is intentionally not frozen as replacement for `08_writing/chatper2_final draft.md`.

## 14) Canonical Draft Lock Update (2026-03-15)
- Completed: latest approved Chapter 2 text consolidated in `08_writing/chapter2_temp2.md` and promoted to canonical `08_writing/chapter2.md`.
- Completed: dated lock snapshot created as `08_writing/chapter2_draft_locked_2026-03-15.md` for auditability and rollback safety.
- Completed: project-control synchronization recorded in `00_admin/change_log.md`, `09_quality_control/rq_alignment_checks.md`, `09_quality_control/chapter_readiness_checks.md`, and `09_quality_control/citation_checks.md`.
