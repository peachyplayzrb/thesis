# Limitations

The limits below define the validity boundary for the rebuilt RQ/objective framing and are evidence-bounded rather than aspirational.

1. Implicit preference evidence remains causally ambiguous.
	Even with transparent processing, interaction traces can reflect exposure and context effects rather than stable preference intent.

2. Alignment confidence cannot eliminate all cross-source mismatch risk.
	Identifier-first matching with metadata fallback improves coverage but does not remove ambiguity for sparse or inconsistent metadata cases.

3. Candidate-generation decisions can dominate downstream quality interpretation.
	Score and playlist outcomes are conditional on which candidates survive thresholding and exclusion rules.

4. Playlist objectives are structurally competing rather than jointly optimizable.
	Improvements in one objective may degrade another, so single-metric quality claims remain limited.

5. Explanation usefulness is not equivalent to explanation fidelity.
	User-facing plausibility can improve without proving that explanations are tightly coupled to actual ranking mechanisms.

6. Reproducibility evidence is process-sensitive.
	Stable outputs alone are insufficient when preprocessing and stage-level choices are under-specified or weakly logged.

7. External validity remains BSc-bounded.
	Evaluation focuses on engineering evidence quality under constrained scope rather than long-horizon user studies or production-scale deployment.

## Failure Modes Relevant To This Scope

1. Confidence overstatement risk in profile interpretation.
	Transparent profiles can still overstate certainty when source-side evidence quality is weak.

2. Candidate-space pruning can masquerade as scoring improvement.
	Observed gains may partly come from exclusion behavior rather than stronger relevance modelling.

3. Control surfaces may be nominal without stable downstream effect.
	Available controls are not sufficient evidence unless behavioral shifts are measurable and repeatable.

4. Process documentation gaps can undermine independent reconstruction.
	Under-specified transformation steps can break reproducibility claims even when code itself is deterministic.

## Interpretation Note

These limits define the validity boundary for this thesis. Conclusions are design-evidence claims about transparent, controllable, and reproducible deterministic playlist engineering under cross-source uncertainty and explicit scope constraints.
