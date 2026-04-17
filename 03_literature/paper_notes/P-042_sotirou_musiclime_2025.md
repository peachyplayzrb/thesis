id: P-042
citation_key: sotirou_musiclime_2025
full_reference: MusicLIME: Explainable Multimodal Music Understanding. ICASSP 2025 (2025). doi:10.1109/ICASSP49660.2025.10889771.
document_status: processed_paper_note
source_index_status: screened_keep
confidence: medium

research_problem:
Improve explanation quality for multimodal music models by exposing cross-modal feature contributions.

method_or_system_type:
Explainability method paper (model-agnostic local and global explanations)

key_findings:
- Multimodal explanation requires modeling interactions across modalities, not isolated feature attributions.
- Local explanations can be aggregated into global behavior summaries for inspection.
- Explainability framing in modern music models emphasizes fairness/trust and user understanding.

limitations:
- Focuses on multimodal model explanation, not deterministic scoring pipelines.
- Does not directly evaluate user controllability mechanisms.

relevance_to_thesis:
Supports transparency-by-design and explanation faithfulness framing in music-domain context.

supported_architecture_layer:
- Explanation Layer
- Observability and Audit Layer

theme_mapping:
- transparency_and_scrutability
- explainability_in_music_models

gap_implications:
Adds modern music-domain support for explanation quality considerations beyond classical RS explanation surveys.

design_implications:
- Keep explanation outputs mechanism-linked and inspectable.
- Include both per-item and aggregate explanation diagnostics where feasible.

chapter_use_cases:
- Chapter 2
- Chapter 3
- Chapter 5

linked_files:
- 09_quality_control/claim_evidence_map.md
- 03_literature/literature_gap_tracker.md
