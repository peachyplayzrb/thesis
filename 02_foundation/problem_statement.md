# Problem Statement

Contemporary music recommender systems can generate useful suggestions, but they are often difficult for users and evaluators to inspect, tune, and reproduce. In many practical settings, recommendation outputs are produced by complex model pipelines where the contribution of individual factors is not easily visible, and where small configuration or data changes can alter outcomes without clear traceability.

This creates a problem for an artefact-focused undergraduate engineering project: it is difficult to produce recommendation evidence that is simultaneously automated, technically rigorous, and transparent enough to support critical evaluation. When recommendation behaviour cannot be clearly inspected or controlled, it becomes challenging to justify design decisions, diagnose errors, and connect results to explicit system rules.

The problem is further amplified when user preference data is collected from external music platforms and aligned to a separate feature corpus. Cross-source alignment introduces matching uncertainty and potential data loss, while recommendation quality depends on available feature descriptors in the target dataset. Without explicit engineering choices for alignment, scoring, and assembly, playlist generation can become opaque and inconsistent.

Accordingly, the thesis addresses the following engineering problem:

How can a deterministic single-user playlist generation pipeline be engineered and evaluated so that preference inference, candidate generation, and playlist assembly remain transparent, controllable, and reproducible under cross-source uncertainty and competing playlist objectives?

This problem is addressed within a bounded MVP scope:

- single-user recommendation context
- deterministic methods rather than machine-learning model novelty
- cross-source alignment with confidence-aware identifier and metadata handling
- one practical ingestion path within bounded project constraints
- explicit candidate-generation, scoring, and assembly controls with inspectable run evidence

Solving this problem contributes design and implementation evidence for building recommendation pipelines whose behaviour can be explained and audited, rather than only judged by output quality. The intended outcome is a defensible artefact and evaluation basis that aligns with the rebuilt research question on uncertainty-aware, controllable, and reproducible playlist engineering.
