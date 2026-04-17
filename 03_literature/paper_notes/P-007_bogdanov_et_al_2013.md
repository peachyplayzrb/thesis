id: P-007
citation_key: bogdanov_semantic_2013
full_reference: Bogdanov, D., Haro, M., Fuhrmann, F., Xambo, A., Gomez, E., and Herrera, P. (2013) Semantic audio content-based music recommendation and visualization based on user preference examples. Information Processing and Management, 49(1), 13-33. doi:10.1016/j.ipm.2012.06.004.
document_status: processed_paper_note
confidence: medium

research_problem:
How to model user musical preferences directly from audio descriptors and semantic representations for content-based recommendation.

method_or_system_type:
Content-based music recommendation approach with semantic descriptor inference and preliminary user evaluation.

key_findings:
- Constructs user preference representation from explicit preference examples using audio-derived semantic descriptors.
- Demonstrates feasible recommendation performance near metadata-based baselines in reported evaluation.
- Shows interpretable preference representation can support recommendation interfaces/visualization.

limitations:
- Small evaluation sample and older pipeline context.
- Not focused on modern cross-source identity alignment or reproducibility instrumentation.

relevance_to_thesis:
Supports feature-processing and preference-modelling decisions in a deterministic content-based architecture.

supported_architecture_layer:
- Feature Processing Layer
- Preference Modelling Layer
- Deterministic Candidate Scoring Engine

theme_mapping:
- feature_engineering_music
- content_based_profiles
- semantic_audio_descriptors

gap_implications:
Semantic audio preference modelling shows interpretable feature-based personalization remains viable; the thesis uses that opening to justify a transparent content-driven preference layer instead of opaque latent modelling.

design_implications:
- Feature normalization and semantic interpretability should be documented explicitly.
- Preference profile representation can remain interpretable without latent-only modelling.

chapter_use_cases:
- Chapter 2: audio-feature/semantic representation evidence.
- Chapter 3: preference-modelling and feature-processing rationale.

linked_files:
- 05_design/literature_architecture_mapping.md
- 05_design/requirements_to_design_map.md
- 09_quality_control/claim_evidence_map.md
