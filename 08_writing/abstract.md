# Abstract

Cross-source playlist generation creates a practical engineering problem: user preference records and candidate-track metadata come from different systems, so recommendation outputs can become difficult to inspect, control, and reproduce. This thesis addresses that problem by asking how a deterministic playlist pipeline can remain transparent, controllable, and reproducible under cross-source conditions.

The work builds a single-user, configuration-driven artefact that links alignment, profiling, retrieval, scoring, assembly, explanation, observability, reproducibility, and controllability through explicit stage contracts. This design choice matters because it makes decision paths auditable at each stage rather than only in final outputs.

Evaluation shows two central findings. First, fixed-configuration replay produces consistent playlist outputs with run-level provenance and traceable score-contribution evidence. Second, control-surface changes produce observable downstream shifts in retrieval, scoring, and assembly behaviour, although some controls remain bounded or no-op under active data conditions. The study also confirms a key limitation: only a minority of listening events align cleanly across sources, which constrains downstream evidence strength.

This thesis contributes a bounded, evidence-backed engineering design for cross-source playlist generation that demonstrates how one deterministic pipeline can co-engineer transparency, controllability, and reproducibility. It does not claim performance superiority over learning-based recommenders or generalisation beyond single-user, artefact-level scope.
