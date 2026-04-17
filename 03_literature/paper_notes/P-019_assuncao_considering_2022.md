id: P-019
citation_key: assuncao_considering_2022
full_reference: Considering emotions and contextual factors in music recommendation: a systematic literature review. Multimed Tools Appl (2022). doi:10.1007/s11042-022-12110-z.
document_status: processed_paper_note
confidence: medium

research_problem:
Identify approaches, gaps, and challenges in emotion/context-aware music recommendation.

method_or_system_type:
Systematic literature review on emotions/context in music recommendation

key_findings:
- Context and emotion factors can improve listening experience in many studies.
- Highlights unresolved issues including feedback, cognitive load, and cold-start interactions.
- Emphasizes complexity trade-offs for practical systems.

limitations:
- Context/emotion focus exceeds MVP scope for deterministic baseline.

relevance_to_thesis:
Helps define deliberate out-of-scope boundaries and future extension opportunities.

supported_architecture_layer:
- User Interaction Layer
- Configuration and Execution Layer

theme_mapping:
- music_recommenders
- evaluation_challenges

gap_implications:
Emotion-aware recommendation adds rich context coupling that complicates transparent reasoning and controllable behaviour; the thesis addresses this by deferring complex context modelling and focusing on a transparent core recommendation mechanism.

design_implications:
- Explicitly state context/emotion modelling as deferred feature beyond MVP.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md
