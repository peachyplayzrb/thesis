# Assumptions

1. Recommendation modelling is performed for a single user profile rather than a multi-user population.
2. Deterministic algorithms are sufficient to support the thesis aim of engineering transparency, controllability, and observability.
3. DS-002 (MSD subset + Last.fm tags) provides enough feature coverage to support MVP-level candidate scoring and playlist assembly.
4. One practical ingestion path is adequate to evaluate core design considerations within BSc constraints.
5. ISRC-first matching with metadata fallback provides a workable strategy for cross-source track alignment.
6. Manually selected influence tracks can usefully complement imported listening history when constructing preference profiles.
7. Reproducibility can be meaningfully assessed by verifying that identical input data and configuration produce identical outputs.
8. Rule-based playlist assembly can express diversity, coherence, and ordering requirements without requiring model training.

## Boundary Note

These assumptions support an artefact-focused engineering evaluation. They do not assume universal recommendation superiority over machine-learning or collaborative approaches.

