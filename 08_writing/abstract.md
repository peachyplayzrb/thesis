# Abstract

This thesis investigates the research question: what design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data. The artefact is implemented as a deterministic, single-user pipeline that ingests Spotify listening history, aligns events to a DS-001 candidate corpus, builds a weighted preference profile, filters and scores candidates, assembles a rule-constrained playlist, and emits explanation and observability artifacts.

The final implementation is stabilized on the v1f run-configuration baseline. On the canonical run chain, BL-003 produces 1,064 seed rows from 11,935 input events, BL-005 retains 46,776 candidates from a 109,269-row corpus, BL-006 uses 10 active scoring components (7 numeric and 3 semantic), BL-007 outputs a full 10-track playlist, and BL-014 passes 22/22 sanity checks with 7/7 active freshness checks. Transparency outputs include per-track contributor traces, and BL-009 provides run-level artifact hashes, stage linkage, and configuration provenance.

Evaluation shows strong evidence for deterministic engineering goals under bounded scope: BL-010 reproducibility checks report deterministic replay match, BL-011 controllability scenarios report repeat-consistent and observable parameter effects, and quality checks remain green on the active baseline. The work also surfaces explicit limitations, including high alignment miss rate, corpus dependence, and bounded external validity due to single-user deterministic scope.

The contribution is therefore a validated engineering design for transparent and controllable playlist generation under BSc-feasible constraints, rather than a claim of universal recommendation superiority.

