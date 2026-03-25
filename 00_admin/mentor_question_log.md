# Mentor Question Log

Status checkpoint (2026-03-25):
- Open: MQ-001, MQ-002, MQ-003, MQ-004, MQ-007
- Deferred: MQ-005, MQ-006, MQ-008

id: MQ-001
date: 2026-03-13
topic: Pass requirements interpretation
question: Do both component 1 (professionalism) and component 2 (project/artefact) require independent pass thresholds in this academic year, and what are the exact rules?
why_it_matters: Affects risk management and prioritization of writing, artefact, and professionalism tasks.
affected_files:
- 01_requirements/marking_criteria.md
- 01_requirements/ambiguity_flags.md
urgency: high
status: open

id: MQ-002
date: 2026-03-13
topic: Viva must-pass consequence
question: If the viva/demo performance is below expected threshold, what is the exact reassessment path and impact on module outcome?
why_it_matters: Directly impacts evaluation planning and demo preparation timeline.
affected_files:
- 01_requirements/submission_requirements.md
- 01_requirements/ambiguity_flags.md
urgency: high
status: open

id: MQ-003
date: 2026-03-13
topic: Current-year document precedence
question: Is Projects Handbook v4.6 still the definitive source, or are there newer module-specific overrides in Canvas announcements?
why_it_matters: Avoids planning against outdated constraints.
affected_files:
- 01_requirements/university_rules.md
- 01_requirements/ambiguity_flags.md
urgency: high
status: open

id: MQ-004
date: 2026-03-13
topic: Report size expectation
question: Should the project report target exactly around 10,000 words, and how strict is the 8,000-12,000 range in current marking practice?
why_it_matters: Influences chapter depth and scope control.
affected_files:
- 01_requirements/formatting_rules.md
- 08_writing/chapter1.md
- 08_writing/chapter2.md
- 08_writing/chapter3.md
urgency: medium
status: open

id: MQ-005
date: 2026-03-13
topic: Scope feasibility
question: For assessment success, what minimum viable artefact scope is expected for this project type (cross-source ingestion + deterministic pipeline + explanations + observability)?
why_it_matters: Prevents over-ambitious implementation and supports realistic planning.
affected_files:
- 00_admin/thesis_scope_lock.md
- 07_implementation/implementation_plan.md
- 01_requirements/ambiguity_flags.md
urgency: high
status: deferred
deferred_reason: Internally bounded for execution by `00_admin/thesis_scope_lock.md`, `00_admin/Artefact_MVP_definition.md`, and `00_admin/thesis_state.md`. Keep for next mentor checkpoint as external validation, not as an active blocker.

id: MQ-006
date: 2026-03-13
topic: Data availability feasibility
question: Is one ingestion path plus curated/manual input acceptable for demonstrating cross-source design considerations, or is multi-platform ingestion mandatory for high marks?
why_it_matters: Determines whether MVP scope is sufficient or requires additional adapter complexity.
affected_files:
- 00_admin/Artefact_MVP_definition.md
- 00_admin/thesis_state.md
- 01_requirements/ambiguity_flags.md
urgency: high
status: deferred
deferred_reason: Implementation posture is now locked to one practical ingestion path within MVP boundaries; retain this as a mentor-validation question during review rather than an active execution blocker.

id: MQ-007
date: 2026-03-14
topic: Evidence acceptability for alignment claims
question: For literature support in this module, is cross-domain entity-resolution evidence acceptable as primary support for music track-alignment design, provided music-specific uncertainty is explicitly stated?
why_it_matters: Determines whether Chapter 2 and Chapter 3 alignment rationale is assessment-safe or requires additional music-domain benchmark evidence before freeze.
affected_files:
- 08_writing/chapter2.md
- 08_writing/chapter3.md
- 09_quality_control/citation_checks.md
- 03_literature/literature_gap_tracker.md
urgency: medium
status: open

---

id: MQ-008
date: 2026-03-21
topic: Candidate corpus size and Music4All access
question: The active candidate corpus is now DS-001 (Music4All base, 109,269 tracks). Is this corpus size and coverage sufficient for a convincing and well-marked thesis demonstration, and are there any institutional restrictions we should explicitly document in the report regarding dataset usage, retention, and redistribution?
why_it_matters: Determines whether current DS-001 corpus posture is assessment-safe and whether any mentor-specified governance constraints should be added before submission hardening.
affected_files:
- 06_data_and_sources/dataset_registry.md
- 00_admin/thesis_state.md
- 00_admin/decision_log.md (D-028)
urgency: medium
status: deferred
deferred_reason: Access route is closed operationally (credentials released and DS-001 active). Remaining mentor input concerns corpus-sufficiency and governance-interpretation judgment, which is review-stage rather than run-stage blocking.
