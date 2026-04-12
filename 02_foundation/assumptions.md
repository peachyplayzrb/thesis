# Assumptions

1. Recommendation modelling is intentionally bounded to a single-user profile rather than a multi-user population.
2. Deterministic algorithms are sufficient for evaluating engineering evidence quality under the current thesis scope.
3. Cross-source preference traces are useful but uncertain signals, so profiling must treat them as bounded proxies rather than direct preference truth.
4. One practical ingestion/alignment path is adequate for evaluating traceability and controllability design choices within project constraints.
5. Confidence-aware identifier and metadata matching can provide a workable cross-source alignment basis when uncertainty is explicitly surfaced.
6. Candidate-generation rules are treated as first-order recommendation logic, not neutral preprocessing.
7. Reproducibility can be meaningfully assessed when both semantic output stability and process-trace completeness are measured.
8. Rule-based playlist assembly can expose and test objective trade-offs (coherence, diversity, novelty, ordering) without requiring model training.

## Boundary Note

These assumptions support an artefact-focused engineering evaluation. They do not assume universal recommendation superiority over machine-learning or collaborative approaches.
