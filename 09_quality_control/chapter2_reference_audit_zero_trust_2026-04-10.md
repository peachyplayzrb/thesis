# Chapter 2 Zero-Trust PDF Reference Audit (Report-Only)

Date: 2026-04-10
Scope: `08_writing/chapter2.md` only
Mode: report-only (no chapter wording edits)
Evidence policy: manual PDF evidence is authoritative; automation is cross-check only.

## 1) Baseline Freeze

- Chapter file: `08_writing/chapter2.md`
  - SHA256: `17BCD164CE6ED708F0D496D57CEA14FAEC093AA81A1A550C8CD90E0426552ADA`
- Bibliography file: `08_writing/references.bib`
  - SHA256: `A26EBB2924D78C82A49DF9761B0B09F9C1F5B019BD0A180EDD8D8D48EBE8BBCE`

## 2) Zero-Trust Findings Against Existing QC Surfaces

### Critical trust finding A
Existing citation-control records are stale to draft-era contexts and cannot be treated as closure evidence for the current chapter state.

Evidence:
- `09_quality_control/citation_checks.md` still anchored to `Date: 2026-03-15`.
- `09_quality_control/citation_checks.md` references `chapter2_draft_v11.md` as active audit scope in multiple lines.

Impact:
- Prior pass/fail status is historical, not sufficient for current-state evidential integrity.

Action:
- Rebuild current-state report from the frozen baseline and manual PDF checks.

### High trust finding B
`09_quality_control/chapter2_verbatim_audit.md` is lexical-first and should not be used as authoritative semantic support.

Evidence:
- Method note explicitly states RapidFuzz token-set lexical matching with thresholding.
- High prevalence of `partially_supported` statuses indicates weak semantic certainty.

Impact:
- Useful as a discovery aid only; not sufficient as primary evidence for claim validity.

Action:
- Keep as secondary cross-check after manual PDF verification.

### High trust finding C
At least some claim strings in existing verbatim audits no longer appear in the current chapter text.

Evidence:
- Example audit claim strings such as "Recommender systems emerged to address this problem" are not present in current `08_writing/chapter2.md`.

Impact:
- Confirms artifact drift risk between historical audit outputs and current chapter wording.

Action:
- Re-audit from current frozen chapter text only.

## 3) Current In-Text Citation Register (Fresh Extraction)

Extracted from current `08_writing/chapter2.md`:

1. Adomavicius and Tuzhilin, 2005
2. Afroogh et al., 2024
3. Andjelkovic et al., 2019
4. Anelli et al., 2021
5. Bauer et al., 2024
6. Beel et al., 2016
7. Bellogin and Said, 2021
8. Bogdanov et al., 2013
9. Bonnin and Jannach, 2015
10. Cano and Morisio, 2017
11. Cavenaghi et al., 2023
12. Deldjoo et al., 2024
13. Elmagarmid et al., 2007
14. Ferrari Dacrema et al., 2021
15. Ferraro et al., 2018
16. Fkih, 2022
17. Herlocker et al., 2004
18. Jin et al., 2020
19. Knijnenburg et al., 2012
20. Lu et al., 2015
21. Papadakis et al., 2021
22. Pegoraro Santana et al., 2020
23. Roy and Dutta, 2022
24. Ru et al., 2023
25. Schweiger et al., 2025
26. Sotirou et al., 2025
27. Tintarev and Masthoff, 2007
28. Tintarev and Masthoff, 2012
29. Vall et al., 2019
30. Zamani et al., 2019
31. Zhu et al., 2022

## 4) Comprehensive Findings Matrix (Initial State)

Status legend:
- `pending_manual_pdf_check`
- `supported`
- `partially_supported`
- `unsupported`
- `misframed`

| Citation | Bib entry mapped | Canonical PDF mapped | Manual page evidence | Support status | Severity if failing | Notes |
|---|---|---|---|---|---|---|
| Adomavicius and Tuzhilin, 2005 | adomavicius_toward_2005 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf | pp.1-2 (survey defines content-based/collaborative/hybrid families; formalizes recommendation as utility maximization under partial ratings evidence) | supported | Critical | Supports the chapter's foundational survey/taxonomy and utility-estimation framing. |
| Afroogh et al., 2024 | afroogh_trust_2024 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\428\Afroogh et al. - 2024 - Trust in AI progress, challenges, and future directions.pdf | pp.1-4 (supports trust outcomes as context-dependent across users and application settings in AI systems) | supported | High | Chapter wording was narrowed to broad trust-context dependence, removing recommender-interface-specific overreach. |
| Andjelkovic et al., 2019 | andjelkovic_moodplay_2019 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf | pp.1-2 (introduces an interactive mood-based music recommender with explicit mood-space exploration and a mood-influence control slider) | supported | High | Chapter wording now claims user-steerable adjustment mechanisms rather than guaranteed compensation for stale profiles. |
| Anelli et al., 2021 | anelli_elliot_2021 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf | pp.2-3 (documents evaluation complexity across algorithms/splits/metrics/tasks and introduces configuration-driven reproduction of the full experimental pipeline) | supported | Critical | Direct support for the chapter's argument that rigorous reproducible evaluation requires explicit pipeline and protocol control. |
| Bauer et al., 2024 | bauer_exploring_2024 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf | pp.2-3 (systematic review focuses on methodological evaluation issues and shows strong concentration in offline experiments plus uneven metric usage) | supported | High | Supports the chapter's claim that evaluation design choices materially shape reported conclusions. |
| Beel et al., 2016 | beel_towards_2016 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Beel et al. - 2016 - Towards reproducibility in recommender-systems research.pdf | pp.1-2 (shows large performance discrepancies under slight scenario/approach changes; identifies datasets, weighting schemes, timing, and user-model size as reproducibility determinants) | supported | High | Supports the chapter's reproducibility-fragility framing and sensitivity to seemingly small experimental differences. |
| Bellogin and Said, 2021 | bellogin_improving_2021 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf | pp.1-2 (argues reproducibility improves accountability/transparency; notes lack of agreement on evaluation procedures makes results hard to contextualize and gauge) | supported | Critical | Direct support for the chapter's claim that accountability degrades when evaluation assumptions and contexts are underreported. |
| Bogdanov et al., 2013 | bogdanov_semantic_2013 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\409\Bogdanov et al. - 2013 - Semantic audio content-based music recommendation and visualization based on user preference example.pdf | pp.1-2 (proposes content-based semantic user representations inferred from audio and explicit example tracks; builds a user model from high-level semantic descriptors) | supported | High | Supports the chapter's claim that content-based music profiles can be built from interpretable descriptors rather than latent-only embeddings. |
| Bonnin and Jannach, 2015 | bonnin_automated_2015 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf | pp.2-7 (treats playlists as ordered sequences, discusses quality beyond item-level scoring, and notes that diversity, smooth transitions, popularity effects, and evaluation design all materially affect playlist assessment) | supported | High | Supports the chapter's claim that playlist quality is multi-criteria and evaluation-sensitive rather than reducible to a single metric. |
| Cano and Morisio, 2017 | cano_hybrid_2017 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf | pp.1-3 (hybrid recommenders combine multiple strategies to reinforce complementary advantages and reduce disadvantages/limitations; review frames hybridization as established approach) | supported | High | Supports the chapter's claim that hybrid systems are presented as stronger combinations of multiple evidence sources. |
| Cavenaghi et al., 2023 | cavenaghi_systematic_2023 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Cavenaghi et al. - 2023 - A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems.pdf | p.2 (reproducibility review inspects missing dataset, preprocessing code, dependency/software, implementation, hyperparameter, and experiment-code support variables) | supported | High | Chapter wording now matches the source at software/implementation-detail level without stronger dependency-drift phrasing. |
| Deldjoo et al., 2024 | deldjoo_content-driven_2024 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf | pp.1-2 (survey defines layered content sources including metadata, user-generated content, and audio-derived features, and explicitly frames content-driven recommendation challenges) | supported | High | Chapter wording was reduced from decomposition-traceability claims to interpretable multi-layer content representation, aligning with located evidence. |
| Elmagarmid et al., 2007 | elmagarmid_duplicate_2007 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Elmagarmid et al. - 2007 - Duplicate Record Detection A Survey.pdf | pp.1-3 (surveys duplicate detection, highlights identity uncertainty / no common key / matching difficulty, and reviews field-matching techniques within a broader cleaning pipeline) | supported | High | Chapter wording now attributes explicit blocking/filtering formalization to Papadakis while using Elmagarmid for foundational uncertainty/matching difficulty context. |
| Ferrari Dacrema et al., 2021 | ferrari_dacrema_troubling_2021 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ferrari Dacrema et al. - 2021 - A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research.pdf | pp.2-4 (paper frames stagnation/reproducibility problem; reports only 12/26 papers reproducible with reasonable effort; 8/12 reproducible cases beaten by tuned simple baselines) | supported | Critical | Directly supports the chapter's claim that protocol/baseline choices can inflate apparent progress. |
| Ferraro et al., 2018 | ferraro_automatic_2018 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ferraro et al. - 2018 - Automatic playlist continuation using a hybrid recommender system combining features from text and a.pdf | pp.1-3 (presents a hybrid APC system using ranking fusion and reports performance-oriented evaluation on challenge playlists, especially to handle cold-start cases) | supported | High | Chapter wording now cites Ferraro for hybrid APC performance framing only and removes candidate-pool variance isolation language. |
| Fkih, 2022 | fkih_similarity_2022 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\432\Fkih - 2022 - Similarity measures for Collaborative Filtering-based Recommender Systems Review and experimental c.pdf | pp.1-3 (states CF is highly sensitive to the similarity measure and compares multiple measures on common datasets under the same prediction method) | supported | High | Direct support for the chapter's claim that metric choice is a first-order determinant of recommender behavior. |
| Herlocker et al., 2004 | herlocker_evaluating_2004 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Herlocker et al. - 2004 - Evaluating collaborative filtering recommender systems.pdf | pp.2-5 (evaluation depends on user tasks, metric choice, and prediction attributes beyond quality; small accuracy deltas and metric disagreement highlighted) | supported | High | Direct support for the chapter's claim that predictive-accuracy gains alone do not settle recommendation quality. |
| Jin et al., 2020 | jin_effects_2020 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\395\Jin et al. - 2020 - Effects of personal characteristics in control-oriented user interfaces for music recommender system.pdf | pp.1-4 (shows control-oriented interfaces in music recommenders are affected by individual differences; finds benefits from personalizing visualizations/controls and higher recommendation acceptance with multiple levels of control) | supported | High | Chapter wording now uses acceptance/perceived-usefulness findings with user-condition caveats, aligned with the located evidence. |
| Knijnenburg et al., 2012 | knijnenburg_explaining_2012 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\422\Knijnenburg et al. - 2012 - Explaining the user experience of recommender systems.pdf | pp.1-3 (accuracy only partially explains user experience; framework explicitly includes personal and situational characteristics as drivers of recommender user experience) | supported | High | Direct support for the chapter's claim that explanation utility depends on context beyond accuracy alone. |
| Lu et al., 2015 | lu_recommender_2015 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\383\Lu et al. - 2015 - Recommender system application developments A survey.pdf | p.1 (survey classifies recommender methods into collaborative, content-based, and knowledge-based/hybrid families and frames preference prediction as the task) | supported | High | Supports the chapter's dominant-paradigm taxonomy framing. |
| Papadakis et al., 2021 | papadakis_blocking_2021 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Papadakis et al. - 2021 - Blocking and Filtering Techniques for Entity Resolution A Survey.pdf | pp.2-3 (reviews blocking/filtering as dominant ER frameworks that restrict likely comparisons and quickly discard unlikely pairs under quadratic-complexity pressure) | supported | High | Direct support for the chapter's staged blocking/refinement framing for cross-source alignment. |
| Pegoraro Santana et al., 2020 | pegoraro_santana_music4all_2020 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Pegoraro Santana et al. - 2020 - Music4All A New Music Database and Its Applications (contact-site copy).pdf | pp.1-3 (introduces Music4All with metadata, tags, genre information, audio clips, lyrics, and MIR applications including recommendation) | supported | High | Direct support for the chapter's claim that Music4All affords reproducible multimodal music experimentation. |
| Roy and Dutta, 2022 | roy_systematic_2022 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\385\Roy and Dutta - 2022 - A systematic review and research perspective on recommender systems.pdf | pp.2-3,10-11 (supports that recommender inputs include implicit interaction/context data and that data-source characteristics matter) | supported | High | Chapter wording now stays at indirect/context-shaped evidence framing without stronger inflation causality claims. |
| Ru et al., 2023 | ru_improving_2023 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf | pp.1-3 (demonstrates utility of multimodal audio+lyrics+genre-correlation modeling for music genre classification) | supported | High | Supports the chapter's narrower claim that Music4All-like multimodal descriptors show utility in genre-related tasks, not direct preference fidelity. |
| Schweiger et al., 2025 | schweiger_impact_2025 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\rp\files\578\Schweiger et al. - 2025 - The impact of playlist characteristics on coherence in user-curated music playlists.pdf | pp.2-5 (shows coherence is sequential/order-dependent, varies with playlist characteristics and feature/distance choices, and relates non-trivially to diversity) | supported | High | Direct support for the chapter's claim that coherence depends on feature/distance definitions and playlist characteristics, not a single universal objective. |
| Sotirou et al., 2025 | sotirou_musiclime_2025 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf | pp.1-3 (introduces feature-importance explanations for multimodal music models, showing how audio and lyrical features interact and contribute to predictions, with local and aggregated global explanations) | supported | High | Direct support for the chapter's claim that feature-level mechanism explanations can be more informative for auditing than aggregate prediction outputs alone. |
| Tintarev and Masthoff, 2007 | tintarev_survey_2007 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\389\Tintarev and Masthoff - 2007 - A Survey of Explanations in Recommender Systems.pdf | pp.2-3 (surveys explanation goals including transparency, scrutability, trust, effectiveness, persuasiveness, and efficiency) | supported | High | Direct support for the chapter's multidimensional explanation-quality framing. |
| Tintarev and Masthoff, 2012 | tintarev_evaluating_2012 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf | pp.1-3 (identifies seven explanatory aims and explicitly discusses trade-offs, including effectiveness versus satisfaction) | supported | High | Direct support for the chapter's claim that explanation goals do not necessarily move together. |
| Vall et al., 2019 | vall_feature-combination_2019 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Vall et al. - 2019 - Feature-combination hybrid recommender systems for automated music playlist continuation.pdf | pp.1-3 (frames APC as a hybrid matrix-completion/expansion problem and reports that feature-combination hybrids compete with or outperform pure CF depending on data availability) | supported | High | Supports the chapter's broader trade-off framing around hybrid APC methods under different data conditions. |
| Zamani et al., 2019 | zamani_analysis_2019 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Zamani et al. - 2019 - An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Contin.pdf | pp.5,8,10-17 (performance varies materially by playlist scenario; top teams use multi-stage architectures, reranking, title-specific handling, and coherence/diversity-aware weak constraints) | supported | High | Direct support for the chapter's claim that method composition, scenario structure, and upstream handling choices materially affect APC outcomes. |
| Zhu et al., 2022 | zhu_bars_2022 | c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf | pp.2-3 (documents lack of benchmarking standards, ad-hoc evaluation settings, weak baselines, and proposes a standardized pipeline with datasets, code, hyperparameters, logs, and results) | supported | High | Direct support for the chapter's claim that standardized benchmark infrastructure improves comparability and reproducibility. |

## 5) Implementation Status (This Run)

Completed in this run:
1. Baseline freeze and reproducible hashes captured.
2. Fresh citation register extracted from current chapter text.
3. Zero-trust findings on stale artifacts documented.
4. Comprehensive findings matrix initialized for per-citation manual PDF checks.
5. Row-by-row bibliography key mapping completed for all currently extracted citations.
6. Canonical PDF candidate paths locked for all currently extracted citations.
7. Manual PDF verification batch 1 executed for 5 citations (Adomavicius and Tuzhilin, Lu, Roy and Dutta, Herlocker, Ferrari Dacrema) with page-numbered evidence seeds recorded.
8. Batch-1 evidence deepened to claim-level notes: Adomavicius and Tuzhilin, Lu, Herlocker, and Ferrari Dacrema now have direct support entries tied to specific methodological or survey passages; Roy and Dutta remains only partially supported because the stronger exposure-distortion wording in Chapter 2 was not directly located in the PDF during this pass.
9. Manual PDF verification batch 2 executed for 5 evaluation/reproducibility citations (Anelli, Bauer, Beel, Bellogin and Said, Cavenaghi) with direct page-scoped findings now recorded; four are directly supported and Cavenaghi is retained as partially supported because the located passage supports missing reproducibility metadata more clearly than explicit dependency drift.
10. Manual PDF verification batch 3 executed for 5 paradigm/explainability/benchmarking citations (Bogdanov, Deldjoo, Cano and Morisio, Fkih, Zhu). Bogdanov, Cano and Morisio, Fkih, and Zhu are directly supported; Deldjoo is retained as partially supported because the located passages support content layers and challenges more clearly than the chapter's stronger traceability wording.
11. Manual PDF verification batch 4 executed for 10 explanation/control/alignment/dataset citations (Afroogh, Andjelkovic, Elmagarmid, Jin, Knijnenburg, Papadakis, Pegoraro Santana, Ru, Tintarev 2007, Tintarev 2012). Knijnenburg, Papadakis, Pegoraro Santana, Ru, and the Tintarev pair are directly supported; Afroogh, Andjelkovic, Elmagarmid, and Jin are retained as partially supported because the located passages support the broader contextual or control framing more clearly than the chapter's stronger wording.
12. Manual PDF verification batch 5 executed for the final 6 pending citations (Bonnin and Jannach, Ferraro, Schweiger, Sotirou, Vall, Zamani). Bonnin and Jannach, Schweiger, Sotirou, Vall, and Zamani are directly supported; Ferraro is retained as partially supported because the paper clearly supports hybrid APC performance framing but does not directly isolate candidate-pool effects.

Current closeout status:
1. Manual evidence collection is complete for all 31 citation rows extracted from the frozen Chapter 2 baseline.
2. Full-strength wording hardening is applied to the eight previously partial rows in `08_writing/chapter2.md`.
3. Post-reword evidence-fit review is complete for the changed rows.

Optional follow-on work:
1. Keep a future source-upgrade option for the Afroogh trust-context sentence if a recommender-specific trust-interface paper is later preferred.
2. Continue using lexical audit only as secondary drift detection.

## 6) Divergence Synthesis (Current Closeout State)

Current verdict totals across the 31 citation rows after full-strength wording hardening:
1. `supported`: 31
2. `partially_supported`: 0
3. `unsupported`: 0
4. `misframed`: 0

Primary divergence patterns observed:
1. The earlier divergence was primarily wording sharpness rather than citation absence.
2. The full-strength wording pass removed the previously overextended causal/scope phrasing in the eight flagged rows.
3. Residual risk is now low and limited to normal synthesis interpretation trade-offs, not citation-evidence mismatch.

Highest-risk rows for any future wording revision pass:
1. None currently require priority remediation under the zero-trust policy.

Closeout interpretation for this audit phase:
1. The evidence base for current Chapter 2 is directly supportable under manual PDF verification for all mapped citations.
2. Full-strength wording hardening resolved the previously partial rows without introducing unsupported claims.
3. No row currently requires an `unsupported`, `misframed`, or `partially_supported` verdict.

## 6) Non-Edit Guarantee

This section is superseded for the full-strength pass.
Chapter 2 wording was intentionally updated to improve claim-evidence fit, and the audit ledger has been synchronized to that revised text.

## 7) Chapter2finalv1 Variant Trace (2026-04-11)

Scope:
1. Applied a targeted argument-depth hardening pass to `08_writing/_versions/chapter2finalv1.md` for mentor-gap categories: methodological critique of cited studies, direct arbitration of paper conflicts, multilateral comparison depth, and technical-assumption precision.
2. No citation inventory expansion was introduced in this pass.
3. Applied a follow-on arbitration-tightening pass to close the remaining mentor-feedback gaps in measurement-validity critique, controllability evidential ranking, candidate-generation methodological ranking, and the Zhu-versus-Bellogin reproducibility conflict.

Baseline trace:
1. `08_writing/_versions/chapter2finalv1.md` pre-edit SHA256: `F42EBD13036E86993FC491270C59A12E088F55FA8A6A0CC2672A668341E535D5`
2. `08_writing/_versions/chapter2finalv1.md` post-edit SHA256: `393F3A903D93BFC8966CF7CE83BE6AF7DA1FB3129C2140543EC7C8196C00F7DE`
3. `08_writing/references.bib` SHA256: `A26EBB2924D78C82A49DF9761B0B09F9C1F5B019BD0A180EDD8D8D48EBE8BBCE`
4. `08_writing/_versions/chapter2finalv1.md` post-follow-on-edit SHA256: `BBE877A0CED8A904C8D70272C1F430A8EE5C6ABAEA1DD5A3895FB03509DE99B6`
5. `08_writing/_versions/chapter2finalv1.md` post-coherence-pass SHA256: `312732A6FAAC2A33909691EDEBDC186FC606C72622990BE3502B71F54CC6168F`
6. `08_writing/_versions/chapter2finalv1.md` post-editorial-pass SHA256: `BEA8AD2DF36186F7719F1615D25D14472FD5A00FD426DEB7CC292A0D4B0C16AD`
7. `08_writing/_versions/chapter2finalv1.md` post-non-prescriptive-closeout SHA256: `C896DAB892EA0EEC6565E7525981D637AC2A0B168E3D2C41DF9DA3B2ED126950`
8. `08_writing/_versions/chapter2finalv1.md` post-micro-style-refinement SHA256: `6CB08E8BB46EFDA1EEF4FC6C30932475DC156580D9839DB77A2E4A2D711F7261`

Evidence policy:
1. Manual PDF findings in Sections 4 to 6 remain authoritative.
2. Variant edits are constrained to source-grounded interpretations already supported in the manual matrix (`supported=31`, `partially_supported=0`, `unsupported=0`, `misframed=0` for the current chapter baseline).
3. No assumption-only claim inflation is permitted under this trace.
4. Direct PDF verification was added for `nauta_anecdotal_2023` using the mapped local PDF (pp.2-6). This verification supports the narrower claim that explanation assessment should move beyond anecdotal evidence toward quantitative evaluation methods, but it does not elevate Nauta et al. (2023) to direct evidence of music-recommender control behavior.
5. A secondary lexical cross-check was then run specifically against `08_writing/_versions/chapter2finalv1.md` via `09_quality_control/verbatim_audits/run_ch2_verbatim_audit.py --chapter ... --out _scratch/chapter2finalv1_verbatim_audit_2026-04-11.md`. The output (`total_claim_checks=37`, `supported=1`, `partially_supported=16`, `weak_support=20`) was retained as advisory only: it reflects conservative lexical matching on paraphrased synthesis prose and does not override the manual PDF-grounded support matrix or require further wording changes in the four revised mentor-feedback zones.
6. A final bounded coherence pass was then applied to the same variant to correct internal evidential alignment without expanding the citation set: Jin et al. (2020) remain the direct music-domain controllability evidence, Nauta et al. (2023) remain the stricter methodological standard, the Ferraro-versus-Schweiger arbitration is now stated explicitly in the playlist-objectives discussion, and the Bellogin-versus-Zhu reproducibility contrast now transitions directly into the Sotirou et al. (2025) mechanism-explanation point.
7. The lexical cross-check was rerun again after this coherence pass. Scratch output `_scratch/chapter2finalv1_verbatim_audit_2026-04-11.md` reported `total_claim_checks=41`, `supported=1`, `partially_supported=16`, `weak_support=24`, `no_match=0`. This remains non-authoritative and is interpreted as conservative lexical drift on paraphrased synthesis prose rather than a manual-evidence regression.
8. A final mentor-requested editorial polish pass was then applied to correct three isolated quality issues: (1) removed the duplicate playlist-objectives paragraph, retaining the version with Schweiger arbitration and "On evidential ranking..." reasoning; (2) restored (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023) citations to the reproducibility section's reconstruction-failure claim for stronger attribution across opening and supporting sentences; (3) reframed the closing synthesis from enumeration to argumentation, emphasizing that the literature collectively lacks an integrated joint-evaluation framework and explaining why each gap reinforces this core finding. No citation set expansion and no deviation from manual PDF authority.
9. No post-editorial lexical rerun was executed for the simple polish pass; the changes preserve citation authority and evidence-grounding established in items 1-7 above.
10. A final one-sentence closeout refinement removed prescriptive forward-looking wording from the chapter-ending synthesis and replaced it with descriptive evidence-gap language (field has not yet established a methodological standard for joint evaluation). This is a rhetoric-restraint change only and does not alter citation grounding, arbitration logic, or claim-support basis.
11. A bounded micro-style refinement pass then varied repeated evidential-ranking phrase forms, split overlong sentences in the specified controllability and final synthesis paragraphs, and removed the duplicate second reproducibility parenthetical citation while preserving the first instance. This was a readability/wording normalization only and does not modify citation inventory, claim scope, or manual-PDF authority.
