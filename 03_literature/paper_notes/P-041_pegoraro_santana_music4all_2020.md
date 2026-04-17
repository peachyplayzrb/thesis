id: P-041
citation_key: pegoraro_santana_music4all_2020
full_reference: Music4All: A New Music Database and Its Applications. 2020 International Conference on Systems, Signals and Image Processing (IWSSIP) (2020). doi:10.1109/IWSSIP48289.2020.9145170.
document_status: processed_paper_note
source_index_status: screened_keep
confidence: medium

research_problem:
Provide a richer music dataset resource for MIR tasks with metadata, tags, lyrics, and audio clips.

method_or_system_type:
Dataset paper and resource description

key_findings:
- Music4All provides multimodal signals useful for multiple MIR and recommendation tasks.
- The paper positions dataset breadth and feature diversity as practical enablers for benchmarking.
- The resource supports cross-task experimentation rather than a single narrow task setup.

limitations:
- Primarily a dataset description paper, not a playlist-system engineering evaluation.
- Does not directly validate deterministic recommendation pipeline quality.

relevance_to_thesis:
Directly supports the canonical data-corpus choice and data-scope justification for candidate generation.

supported_architecture_layer:
- Data Ingestion Layer
- Candidate Generation Layer

theme_mapping:
- dataset_foundation
- music_data_scope

gap_implications:
Reduces risk around corpus suitability claims by grounding Music4All choice in peer-reviewed dataset documentation.

design_implications:
- Keep corpus assumptions explicit in design and evaluation chapters.
- Report feature availability constraints as part of reproducibility context.

chapter_use_cases:
- Chapter 2
- Chapter 3

linked_files:
- 03_literature/literature_gap_tracker.md
- 05_design/literature_architecture_mapping.md
