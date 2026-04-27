# Word UI Render Check Report

Date (UTC): 2026-04-27 21:53:48

## Inputs
- DOCX: C:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\reports\final_project_report_with_cover.docx
- PDF export: C:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\reports\final_project_report_with_cover_word_ui.pdf
- Filtered HTML export: C:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\reports\final_project_report_with_cover_word_ui_filtered.html
- Paragraph audit CSV: C:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\reports\word_ui_render_paragraph_audit_latest.csv

## Critical Checks
- PASS: No critical rendering defects detected in this audit pass.

## Diagnostic Counts
- Literal markdown heading markers: 0
- Blank O1 threshold lines: 0
- Blank O5 replay lines: 0
- Blank O5 acceptance lines: 0
- Duplicate figure-caption entries: 0
- Inline shapes audited: 8
- Oversized inline shapes: 0

## Figure Fit Audit
- Usable page width (pt): 468
- Usable page height (pt): 648
- Max width ratio: 0.98
- Max height ratio: 0.95
- PASS: All inline shapes fit within the configured page-fit thresholds.

| InlineShapeIndex | Type | WidthPoints | HeightPoints | WidthRatio | HeightRatio | AltText |
|---|---:|---:|---:|---:|---:|---|
| 1 | 3 | 420 | 90.8 | 0.897 | 0.14 |  |
| 2 | 3 | 420 | 22.9 | 0.897 | 0.035 |  |
| 3 | 3 | 123.7 | 33.5 | 0.264 | 0.052 |  |
| 4 | 3 | 357 | 18.2 | 0.763 | 0.028 | Figure 1.1. High-level pipeline logic: Cross-source listening evidence -> Alignment and uncertainty handling -> Preference profiling -> Candidate shaping -> Deterministic scoring -> Playlist assembly -> Explanation and observability outputs. |
| 5 | 3 | 344.4 | 19.6 | 0.736 | 0.03 | Figure 2.2. Uncertainty across recommendation stages in the reviewed literature. |
| 6 | 3 | 357 | 53.2 | 0.763 | 0.082 | Figure 3.1. Deterministic pipeline architecture with stage outputs and run-level observability linkage. |
| 7 | 3 | 344.4 | 321.5 | 0.736 | 0.496 | Figure 3.2. Alignment evidence-handling flow with matched, ambiguous, unmatched, and invalid pathways. |
| 8 | 3 | 344.4 | 37.7 | 0.736 | 0.058 | Figure 3.3. Scoring-to-assembly relationship with constraint checks, fallback recording, and observability output. |

## Numbered List Sample (Word Paragraph/List Metadata)

| ParagraphIndex | Style | ListType | ListString | Text |
|---|---|---:|---|---|
| 42 | Compact | 4 | 1. | Design a preference profiling approach from user listening history across different data sources. |
| 43 | Compact | 4 | 2. | Build cross-source alignment and candidate filtering with explicit uncertainty handling. |
| 44 | Compact | 4 | 3. | Build deterministic scoring and playlist assembly with controls for coherence, diversity, novelty, and ordering. |
| 45 | Compact | 4 | 4. | Produce explanation and logging outputs that show pipeline decision logic. |
| 46 | Compact | 4 | 5. | Assess how well the pipeline reproduces results and how playlist quality changes when settings change. |
| 47 | Compact | 4 | 6. | Identify the limits of the results and the conditions under which the conclusions apply. |
| 54 | Compact | 4 |  | Chapter 2 reviews the literature on recommender systems, music recommendation, transparency, implicit preference evidence, and cross-source data issues. |
| 55 | Compact | 4 |  | Chapter 3 presents the design approach and system architecture, grounded in the gaps and requirements identified in Chapter 2. |
| 56 | Compact | 4 |  | Chapter 4 describes the implementation of the pipeline artefact and the evidence it produces. |
| 57 | Compact | 4 |  | Chapter 5 presents the evaluation results, covering reproducibility, controllability, and playlist trade-off behaviour. |
| 58 | Compact | 4 |  | Chapter 6 discusses the findings, contribution boundaries, limitations, and directions for future work. |
| 211 | Compact | 4 | 1. | user interaction, |

## Figure Caption Frequency
- Figure 1.1. High-level pipeline logic: Cross-source listening evidence -> Alignment and uncertainty handling -> Preference profiling -> Candidate shaping -> Deterministic scoring -> Playlist assembly -> Explanation and observability outputs. => 1
- Figure 2.1. Trade-offs among content-based, collaborative, and hybrid paradigms in the reviewed literature. => 1
- Figure 2.2. Uncertainty across recommendation stages in the reviewed literature. => 1
- Figure 3.1. Deterministic pipeline architecture with stage outputs and run-level observability linkage. => 1
- Figure 3.2. Alignment evidence-handling flow with matched, ambiguous, unmatched, and invalid pathways. => 1
- Figure 3.3. Scoring-to-assembly relationship with constraint checks, fallback recording, and observability output. => 1
