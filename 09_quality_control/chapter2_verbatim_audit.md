# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\08_writing\chapter2.md` against extracted text from mapped local PDFs.
Method note: automated lexical matching (RapidFuzz token-set ratio) with manual thresholding.

## adomavicius_toward_2005
- title: Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Recommender systems emerged to address this problem, and a substantial body of research has since built up around how to estimate what a user is likely to value from sparse, incomplete evidence (Adomavicius and Tuzhilin, 2005; Lu et al., 2015)."
    quote_candidate: "Recommender systems are usually classified according to their approach to rating estimation and, in the next section, we will present such a classification that was proposed in the literature and will provide a survey of different types of recommender systems."
    secondary_score: 48.53556485355649
    secondary_quote: "Although there has been some progress made on incorporating user and item profiles into some of the methods since the earlier days of recommender systems [13], [76], [79], these profiles still tend to be quite simple and do not utilize some of the more advanced profiling techniques."
  - claim_2_status: supported
    score: 71.81818181818181
    claim: "Recommender systems are broadly grouped into content-based, collaborative, and hybrid families (Adomavicius and Tuzhilin, 2005; Lu et al., 2015)."
    quote_candidate: "Toward the Next Generation of Recommender Systems: A Survey of the State-of-the-Art and Possible Extensions Gediminas Adomavicius, Member , IEEE, and Alexander Tuzhilin, Member , IEEE Abstract—This paper presents an overview of the field of recommender systems and describes the current generation of recommendation methods that are usually classified into the following three main categories: content-based, collaborative, and hybrid recommendation approaches."
    secondary_score: 59.23344947735192
    secondary_quote: "2.3.1 Combining Separate Recommenders One way to build hybrid recommender systems is to implement separate collaborative and content-based sys- tems."
  - claim_3_status: partially_supported
    score: 51.91740412979351
    claim: "Collaborative filtering takes a different route, inferring relevance from patterns of interaction across users and items (Adomavicius and Tuzhilin, 2005)."
    quote_candidate: "A statistical model for collaborative filtering was proposed in [105], and several different algorithms for estimating the model parameters were compared, including K-means clustering and Gibbs sampling."
    secondary_score: 51.824817518248175
    secondary_quote: "Note that both the content-based and the collaborative approaches use the same cosine measure from information retrieval literature."

## afroogh_trust_2024
- title: Trust in AI: progress, challenges, and future directions
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\428\Afroogh et al. - 2024 - Trust in AI progress, challenges, and future directions.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.95894428152493
    claim: "For systems intended to support user agency, these explanations must be designed with non-expert audiences in mind (Jin et al., 2020; Afroogh et al., 2024)."
    quote_candidate: "User biases might also affect their perceptions of trust in an explainable AI system: differences in user trust have been found between malignant and benign diagnoses of an AI system (Branley-Bell et al., 2020)."
    secondary_score: 53.674121405750796
    secondary_quote: "Moreover, empathy has links to expectation: if the AI system can act in accordance with its user ’ s expectations, the user will probably form a trust in the system (Gebhard et al., 2021)."

## allam_improved_2018
- title: Improved suffix blocking for record linkage and entity resolution
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Allam et al. - 2018 - Improved suffix blocking for record linkage and entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.98039215686274
    claim: "Entity resolution literature documents the effectiveness of staged approaches to matching: first blocking and filtering to create candidate blocks, then within-block comparison and progressive refinement (Papadakis et al., 2021; Allam et al., 2018)."
    quote_candidate: "Recent suﬃ x-based blocking methods, identify sets of records that correspond to blocks of su ﬃ xes in SortSuf (D) and use these sets to create the pairs that are forwarded to the comparison stage."
    secondary_score: 50.0
    secondary_quote: "To evaluate the accuracy of the blocking stage (discussed in Section 2)o ﬀered by INCSUFFBLOCK and MPB, we use the pairs com- pleteness metric deﬁned in Section 6.2 and the number of pairs for comparison metric which counts the total number of pairs outputted by the blocking stage and fed to the comparison stage."

## andjelkovic_moodplay_2019
- title: Moodplay: Interactive music recommendation based on Artists' mood similarity
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.204819277108435
    claim: "This is consistent with controllability research that treats user influence as useful when it is explicit, bounded, and testable (Jin et al., 2020; Andjelkovic et al., 2019)."
    quote_candidate: "Therefore, we allow users to adjust the mood inﬂuence via a slider control which dynamically re-sizes a catchment area around the current avatar position (Figure 2.1 and 2.2)."
    secondary_score: 50.24630541871921
    secondary_quote: "This trend is further supported by results showing that user satisfaction does not depend on recommendation accuracy only, but on factors such as serendipity, nov- elty, control and transparency as well ( Konstan and Riedl, 2012; Mc- Nee et al., 2006 )."

## anelli_elliot_2021
- title: Elliot: A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 45.876288659793815
    claim: "Claiming reproducibility means preserving sufficient run context (configuration, preprocessing, and protocol details) so results can be independently checked rather than only described in prose (Anelli et al., 2021; Bellogin et al., 2021; Ferrari Dacrema et al., 2021)."
    quote_candidate: "On the other hand, in a re- cent study [22], it has been shown that only one-third of the published experimental results are, in fact, reproducible."
    secondary_score: 45.75471698113208
    secondary_quote: "RS evaluation is an active, ever-growing research topic related to reproducibility, which is a cornerstone of the scien- tific process as identified by Konstan and Adomavicius[53]."
  - claim_2_status: partially_supported
    score: 50.799289520426285
    claim: "Multiple reviews of recommender systems research document that absent or under-specified preprocessing steps, configuration choices, and dependency declarations can reduce the practical feasibility of independent result verification (Ferrari Dacrema et al., 2021; Bellogin et al., 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "The core idea is to feed the system with a simple and straightforward configuration file that drives the framework through the experimental setting choices.Elliot natively provides for widespread research evaluation features, like the analysis of multiple cut-offs and several RSs (50)."
    secondary_score: 49.12280701754386
    secondary_quote: "Rethinking the recommender research ecosystem: reproducibility, openness, and LensKit."

## barlaug_neural_2021
- title: Neural Networks for Entity Matching: A Survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Barlaug and Gulla - 2021 - Neural Networks for Entity Matching A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.01512287334594
    claim: "Neural entity-matching approaches can address cases where rule-based or fuzzy matching fails (Barlaug and Thorvaldsen, 2021), but for a transparency-focused system, they present a fundamental challenge: building fully transparent neural components requires substantial logging infrastructure to expose how decisions were reached."
    quote_candidate: "With this is in mind, we formulate the following research questions: —How do methods using neural networks for entity matching differ in what they solve, and how do the methods that address the same aspects differ in their approaches?"
    secondary_score: 46.484375
    secondary_quote: "While earlier works mention or cover neural networks for entity matching to various degrees, we are to the best of our knowledge the first to present a dedicated, complete, and up-to-date survey."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: supported
    score: 69.06474820143885
    claim: "That distinction matters because recommender evaluation is sensitive to how experiments are set up — preprocessing decisions, metric framing, and protocol choices can all shift results substantially, and strong performance numbers under one set of conditions do not reliably transfer to a design context where inspectable engineering is the primary contribution (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024)."
    quote_candidate: "(d) The paper does not make a contribution regarding the evaluation of recommender systems."
    secondary_score: 67.9245283018868
    secondary_quote: "For example, Ferrari Dacrema et al."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.961630695443645
    claim: "Claiming reproducibility means preserving sufficient run context (configuration, preprocessing, and protocol details) so results can be independently checked rather than only described in prose (Anelli et al., 2021; Bellogin et al., 2021; Ferrari Dacrema et al., 2021)."
    quote_candidate: "1.2 Contributions We review concepts related to accountability and reproducibility, in particular in the context of Recommender Systems research, but also in adjacent contexts."
    secondary_score: 47.30831973898858
    secondary_quote: "Analogously, in a series of prior works focusing on the evaluation, replication, and reproducibility of Recommender Systems algo- rithms and evaluation results, we have identified a set of aspects that need to be taken into consideration when comparing the results of recommender systems from different research papers, software frameworks, or evaluation contexts (Said and Bellogín 2014; Said et al."
  - claim_2_status: partially_supported
    score: 54.3247344461305
    claim: "Multiple reviews of recommender systems research document that absent or under-specified preprocessing steps, configuration choices, and dependency declarations can reduce the practical feasibility of independent result verification (Ferrari Dacrema et al., 2021; Bellogin et al., 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "Analogously, in a series of prior works focusing on the evaluation, replication, and reproducibility of Recommender Systems algo- rithms and evaluation results, we have identified a set of aspects that need to be taken into consideration when comparing the results of recommender systems from different research papers, software frameworks, or evaluation contexts (Said and Bellogín 2014; Said et al."
    secondary_score: 53.10077519379845
    secondary_quote: "A critical analysis is necessary in order to ensure an 947 1 3 Improving accountability in recommender systems research… advance in the field, not just marginal effects based on strategic design choices (Fer - rari Dacrema et al."

## bogdanov_semantic_2013
- title: Semantic audio content-based music recommendation and visualization based on user preference examples
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\409\Bogdanov et al. - 2013 - Semantic audio content-based music recommendation and visualization based on user preference example.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 61.6822429906542
    claim: "When preference profiles and candidate scores are computed from explicit descriptors, the system can report what drove each decision and roughly by how much (Bogdanov et al., 2013)."
    quote_candidate: "For each subject, we computed the user model from the provided preference set."
    secondary_score: 56.15141955835962
    secondary_quote: "These semantic descriptors are computed from an explicit set of music tracks deﬁned by a given user as evidence of her/his musical preferences."

## bonnin_automated_2015
- title: Automated Generation of Music Playlists: Survey and Experiments
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.08988764044944
    claim: "Playlist-generation studies commonly evaluate coherence, novelty, diversity, and ordering together, and report that improving one dimension can reduce another unless trade-offs are made explicit (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015)."
    quote_candidate: "Another potential problem is that not all types of metadata are objective, and annotations regarding, for example, the mood or the genre of a track can be imprecise or inconsistent [Celma 2010; Lee and Cho 2011]."
    secondary_score: 47.963800904977376
    secondary_quote: "When there are tracks that frequently appear together in such playlists, the assumption can be made that the tracks have something in common and that they both fulﬁll the target characteristics that the creator of the playlist had in mind."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.47679324894515
    claim: "Hybrid systems can combine strengths from multiple approaches, but the semantic integration adds layers of complexity to reasoning and audit unless interpretability is deliberately engineered as a first-class design concern (Çano and Morisio, 2017)."
    quote_candidate: "Morisio / Hybrid recommender systems: A systematic literature review 1489 The continuously growing industrial interest in the recent and promising domains of mobile and social web has been followed by a similar increase of academic interest in RSs."
    secondary_score: 51.20967741935484
    secondary_quote: "Papers from conferences and journals Papers published from 2005 to 2015 Papers written in English language only Exclusion criteria Papers not addressing recommender systems at all Papers addressing RSs but not implying any hybridization or combination of different approaches or data mining techniques."
  - claim_2_status: partially_supported
    score: 64.19753086419753
    claim: "Neural and hybrid recommender systems remain strong comparator families, with literature reports of higher predictive performance in data-rich conditions, though such performance gains are often measured on specific benchmarks and may not transfer across different application domains or data characteristics (Çano and Morisio, 2017; He et al., 2017; Liu et al., 2025)."
    quote_candidate: "In recommender systems this conclusions are of the form"
    secondary_score: 59.310344827586206
    secondary_quote: "This systematic literature review presents the state of the art in hybrid recommender systems of the last decade."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.42718446601942
    claim: "For a transparency-focused project, the practical advantage is that ranking depends on explicit features, and the reasoning behind any recommendation can usually be traced back to those same features (Deldjoo et al., 2024)."
    quote_candidate: "Automatic audio analysis algorithms aim to model some of these processes and represent perceived dimensions by extracting content features, which can be used in the recommendation process [33]."
    secondary_score: 51.041666666666664
    secondary_quote: "The intuitive idea behind this work is that music experts with better VM and MS may perceive the same music recommendation list more diverse than non-specialists with lower VM and MS."

## ferraro_automatic_2018
- title: Automatic playlist continuation using a hybrid recommender system combining features from text and audio
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ferraro et al. - 2018 - Automatic playlist continuation using a hybrid recommender system combining features from text and a.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 46.22222222222222
    claim: "Playlist-generation studies commonly evaluate coherence, novelty, diversity, and ordering together, and report that improving one dimension can reduce another unless trade-offs are made explicit (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015)."
    quote_candidate: "The score of all the metrics improved by combin ing the models for almost all playlist categories (except for th e case when a playlist does not have seed tracks) and we can conclude that using fusion approach was beneﬁcial."
    secondary_score: 43.627450980392155
    secondary_quote: "It is important to note that these results are not the same as t he ﬁnal scores published on July 13th, 2018, as they are only cal cu- lated using 50% of the Challenge Set."

## fkih_similarity_2022
- title: Similarity measures for Collaborative Filtering-based Recommender Systems: Review and experimental comparison
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\432\Fkih - 2022 - Similarity measures for Collaborative Filtering-based Recommender Systems Review and experimental c.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 47.61904761904762
    claim: "Metric selection should be treated as an explicit configurable choice rather than a hidden implementation default (Fkih, 2022)."
    quote_candidate: "Spearman rank-order correlation coefﬁcient The Spearman correlation ( Spearman, 2010 ) evaluates the monotonic relationship between two variables."
    secondary_score: 47.61904761904762
    secondary_quote: "Methodology In this section, we carried out an experimental comparative study between the thirteen correlation measures described in the Section 3: 1."
  - claim_2_status: partially_supported
    score: 54.054054054054056
    claim: "The choice of distance function fundamentally shapes how similarity is computed in feature space (Fkih, 2022)."
    quote_candidate: "The Euclidean distance should be normalized to become a similarity measure."
    secondary_score: 52.79187817258883
    secondary_quote: "We mention that the similarity computation phase will be further detailed in Section 3."

## he_neural_2017
- title: Neural Collaborative Filtering
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\436\He et al. - 2017 - Neural Collaborative Filtering.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.94505494505494
    claim: "Neural and hybrid recommender systems remain strong comparator families, with literature reports of higher predictive performance in data-rich conditions, though such performance gains are often measured on specific benchmarks and may not transfer across different application domains or data characteristics (Çano and Morisio, 2017; He et al., 2017; Liu et al., 2025)."
    quote_candidate: "The characteristics of the two datasets are summarized in Table 1."
    secondary_score: 49.23076923076923
    secondary_quote: "the number of predictive factors on the two datasets."

## herlocker_evaluating_2004
- title: Evaluating collaborative filtering recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Herlocker et al. - 2004 - Evaluating collaborative filtering recommender systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 60.714285714285715
    claim: "That distinction matters because recommender evaluation is sensitive to how experiments are set up — preprocessing decisions, metric framing, and protocol choices can all shift results substantially, and strong performance numbers under one set of conditions do not reliably transfer to a design context where inspectable engineering is the primary contribution (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024)."
    quote_candidate: "usability evaluation of the interfaces."
    secondary_score: 47.878787878787875
    secondary_quote: "—When evaluating a recommender in a new domain where there is signiﬁcant research on the structure of user preferences, but no data sets, it may be ap- propriate to ﬁrst evaluate algorithms against synthetic data sets to identify the promising ones for further study."

## jin_effects_2020
- title: Effects of personal characteristics in control-oriented user interfaces for music recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\395\Jin et al. - 2020 - Effects of personal characteristics in control-oriented user interfaces for music recommender system.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.58964143426295
    claim: "Controllability means the user can actively influence behaviour through explicit parameters or inputs (Jin et al., 2020)."
    quote_candidate: "Controllability often allows users to steer the recommendation process to obtain sug- gestions that are better suited to them (He et al."
    secondary_score: 49.28909952606635
    secondary_quote: "Personality traits can affect the performance and preference of a user (Aykin and Aykin 1991)."
  - claim_2_status: partially_supported
    score: 50.75757575757576
    claim: "For systems intended to support user agency, these explanations must be designed with non-expert audiences in mind (Jin et al., 2020; Afroogh et al., 2024)."
    quote_candidate: "The UI elements of existing recommender systems allow users to interact with three distinct components of the systems (see Fig."
    secondary_score: 49.66887417218543
    secondary_quote: "(2016), we previously devised different levels of user control (low, middle, and high) associated with various components of a recommender system (Jin et al."
  - claim_3_status: partially_supported
    score: 53.21637426900585
    claim: "For controllability to be meaningful, control mechanisms must be deliberately designed with consideration for user characteristics and interface complexity (Jin et al., 2020)."
    quote_candidate: "However, a better understanding of the effects of personal characteristics in association with the three levels of user control on music recommender systems has yet to be realized."
    secondary_score: 52.147239263803684
    secondary_quote: "(2016), we previously devised different levels of user control (low, middle, and high) associated with various components of a recommender system (Jin et al."
  - claim_4_status: partially_supported
    score: 54.25867507886435
    claim: "This is consistent with controllability research that treats user influence as useful when it is explicit, bounded, and testable (Jin et al., 2020; Andjelkovic et al., 2019)."
    quote_candidate: "(2016), we previously devised different levels of user control (low, middle, and high) associated with various components of a recommender system (Jin et al."
    secondary_score: 51.52354570637119
    secondary_quote: "For example, when investigating inter- active user interfaces, users’ experience may be seen as their level of familiarity with computers (Zhang and Chignell 2001) or with visualizations (Carenini et al."

## knijnenburg_explaining_2012
- title: Explaining the user experience of recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\422\Knijnenburg et al. - 2012 - Explaining the user experience of recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.641909814323604
    claim: "User-experience research indicates that understanding and trust in recommender explanations depends on factors beyond the underlying algorithm, including explanation design and interface characteristics (Knijnenburg et al., 2012)."
    quote_candidate: "Not surprisingly, a significant part of the research on recommender systems concerns creating and evaluating better prediction algorithms (McNee et al."
    secondary_score: 52.916666666666664
    secondary_quote: "3.5 Personal and situational characteristics in context The user experience cannot be entirely attributed to the recommender system itself, it may also depend on characteristics of the user (Personal Characteristics, or PC) and the situation in which the user is using the system (Situational Characteristics, or SC) (Chin 2001 )."

## liu_aggregating_2025
- title: Aggregating Contextual Information for Multi-Criteria Online Music Recommendations
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Liu - 2025 - Aggregating Contextual Information for Multi-Criteria Online Music Recommendations.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.95522388059702
    claim: "Neural and hybrid recommender systems remain strong comparator families, with literature reports of higher predictive performance in data-rich conditions, though such performance gains are often measured on specific benchmarks and may not transfer across different application domains or data characteristics (Çano and Morisio, 2017; He et al., 2017; Liu et al., 2025)."
    quote_candidate: "Stereotypes, in this context, capture general user preferences within similar contexts, enabling the system to deliver relevant recommendations without relying on extensive individual user data.Our prediction model is built on a Context-Genre Matrix, which maps contextual situations to preferred music genres by aggregating data from a broad user base."
    secondary_score: 48.8734835355286
    secondary_quote: "Unlike traditional MRSs that rely on explicit user preference data, our approach leverages pre-collected data to bootstrap the system, addressing issues such as the cold start problem, diversity of recommended playlists, and scalability concerns."

## liu_multimodal_2025
- title: Multimodal Recommender Systems: A Survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\411\Liu et al. - 2025 - Multimodal Recommender Systems A Survey.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.58156028368794
    claim: "Neural and hybrid recommender systems remain strong comparator families, with literature reports of higher predictive performance in data-rich conditions, though such performance gains are often measured on specific benchmarks and may not transfer across different application domains or data characteristics (Çano and Morisio, 2017; He et al., 2017; Liu et al., 2025)."
    quote_candidate: "Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page."
    secondary_score: 46.69479606188467
    secondary_quote: "We take the movie recommendation as an example to illustrate the general procedures as follows: Raw Feature Representation.Each movie possesses two types of features: tabular features that describe its important characteristics using numerical values or classifications (such as genera or year), and multimodal features that depict the movie across various modalities of representation (such as poster images and textual introduction)."

## lu_recommender_2015
- title: Recommender system application developments: A survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\383\Lu et al. - 2015 - Recommender system application developments A survey.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Recommender systems emerged to address this problem, and a substantial body of research has since built up around how to estimate what a user is likely to value from sparse, incomplete evidence (Adomavicius and Tuzhilin, 2005; Lu et al., 2015)."
    quote_candidate: "A systematic algorithm, TidalTrust, was proposed by Golbeck [54] to address the trust-based rating prediction problem and is considered to be effective in the forming process of numeric trust net- works in several systems."
    secondary_score: 49.152542372881356
    secondary_quote: "Early research in recommender systems grew out of information re- trieval and ﬁltering research [4], and recommender systems emerged as an independent research area in the mid-1990s when researchers started to focus on recommendation problems that explicitly rely on the rating structure [3]."
  - claim_2_status: partially_supported
    score: 61.53846153846154
    claim: "Recommender systems are broadly grouped into content-based, collaborative, and hybrid families (Adomavicius and Tuzhilin, 2005; Lu et al., 2015)."
    quote_candidate: "For example, the paper by Adomavicius and Tuzhilin [3] presented an overview of content-based, collaborative ﬁltering-based, and hybrid recommendation approaches."
    secondary_score: 49.44649446494465
    secondary_quote: "Recommender systems can be used in digital library applications to help users locate and select information and knowledge sources[95]."

## nauta_anecdotal_2023
- title: From Anecdotal Evidence to Quantitative Evaluation Methods: A Systematic Review on Evaluating Explainable AI
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\426\Nauta et al. - 2023 - From Anecdotal Evidence to Quantitative Evaluation Methods A Systematic Review on Evaluating Explai.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.04602510460251
    claim: "Research in the explanation literature shows that explanations can enhance perceived satisfaction in some settings, though the relationship between explanation design and genuine user understanding remains nuanced and is sensitive to context (Nauta et al., 2023)."
    quote_candidate: "•Readers interested in theory of XAI evaluation:Section 2 is recommended as back- ground reading, as it summarizes related work, presents pros and cons of evaluating with users, and discusses the discrepancy between objective and subjective evaluation."
    secondary_score: 50.450450450450454
    secondary_quote: "[10] argue that user studies imply a strong bias towards simpler explanations that are closer to the user’s expectations, “at the cost of penalizing those methods that might more closely reflect the network behavior” [10]."
  - claim_2_status: weak_support
    score: 47.66839378238342
    claim: "Evaluation of control-oriented systems must systematically document how parameter changes affect recommendation outputs—behavioral shifts should be demonstrable and measurable, not anecdotal (Nauta et al., 2023)."
    quote_candidate: "Many authors (e.g., [2, 111, 134, 143]) argue that relying on such anecdotal evidence alone is insufficient and that other aspects of the explanations should be evaluated as well."
    secondary_score: 45.65217391304348
    secondary_quote: "They argue that the lack of quantitative evaluation impedes interpretability research, since anecdotal inspection is not sufficient for robust verification."

## papadakis_blocking_2021
- title: Blocking and Filtering Techniques for Entity Resolution: A Survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Papadakis et al. - 2021 - Blocking and Filtering Techniques for Entity Resolution A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.37027707808564
    claim: "Entity resolution literature documents the effectiveness of staged approaches to matching: first blocking and filtering to create candidate blocks, then within-block comparison and progressive refinement (Papadakis et al., 2021; Allam et al., 2018)."
    quote_candidate: "The window slides by one position at a time until reaching the oth entity of the next block, executing all pairwise comparisons between entities from different blocks."
    secondary_score: 48.75
    secondary_quote: "Thus, it intersects Duplicate Pairs, such that the area of their intersection is inversely proportional to the duplicates that are missed by Blocking, while the relative complement of the Duplicate Pairs in Blocking is analogous to the executed comparisons between nonmatching entities."

## roy_systematic_2022
- title: A systematic review and research perspective on recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\385\Roy and Dutta - 2022 - A systematic review and research perspective on recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.74626865671642
    claim: "Acting on that evidence still requires deliberate choices about how to aggregate it, what to filter out, and how to account for what it cannot tell you (Roy and Dutta, 2022)."
    quote_candidate: "Then, the algorithmic analysis on various recom- mender systems is performed and a taxonomy is framed that accounts for various components required for developing an effective recommender system."
    secondary_score: 47.491638795986624
    secondary_quote: "Using content-based filtering may resolve this issue, but it may introduce overspeciali - zation and decrease the computing time and system performance."
  - claim_2_status: partially_supported
    score: 56.33802816901409
    claim: "This project relies on imported listening history, which provides implicit preference evidence rather than a direct statement of what the user wants (Roy and Dutta, 2022)."
    quote_candidate: "This ensures the security and privacy of user data."
    secondary_score: 52.17391304347826
    secondary_quote: "This technique starts with finding a group or collection of user X whose preferences, likes, and dislikes are similar to that of user A."

## ru_improving_2023
- title: Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Perspective
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.30434782608695
    claim: "Music4All remains an important historical baseline and literature anchor for multi-signal music recommendation corpora (Pegoraro et al., 2020), and related multimodal music recommendation work provides supporting evidence for the practical suitability of this corpus family under this project's scope constraints (Ru et al., 2023)."
    quote_candidate: "CONCLUSION In this paper, we improve multi-label music genre classifica- tion from multi-modal properties of music and genre corre- lations perspective and have presented a novel multi-modal method leveraging audio-lyrics contrastive loss and two sym- metric cross-modal attention, to align and fuse features from audio and lyrics."
    secondary_score: 47.01030927835052
    secondary_quote: "Music Representation Learning Module The music representation learning module consists of an audio encoder and a lyrics encoder, which takes audio and lyrics as input and outputs corresponding features respec- tively."

## schweiger_impact_2025
- title: The impact of playlist characteristics on coherence in user-curated music playlists
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\rp\files\578\Schweiger et al. - 2025 - The impact of playlist characteristics on coherence in user-curated music playlists.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 45.32374100719424
    claim: "This is especially important in music recommendation, where different distance-metric choices produce demonstrably different playlist-level objectives (Schweiger et al., 2025)."
    quote_candidate: "2.1 Researchcontribution The importance of coherence is evaluated with varying relevance in existing literature."
    secondary_score: 45.16129032258065
    secondary_quote: "[8]p r o p o s e s a hybrid recommendation system that balances coherence and diversity based on given Schweigeretal."
  - claim_2_status: weak_support
    score: 49.249249249249246
    claim: "In music recommendation specifically, playlist-level objectives like coherence are directly affected by distance-metric selection, with different distance-feature combinations producing different outcomes (Schweiger et al., 2025)."
    quote_candidate: "[8]p r o p o s e s a hybrid recommendation system that balances coherence and diversity based on given Schweigeretal."
    secondary_score: 49.18032786885246
    secondary_quote: "Example 3 Understanding coherence and its relationship with other playlist character- istics can be applied to tasks beyond track recommendations."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.72677595628415
    claim: "Recent music explainability work supports the same underlying principle — that explanations should expose how a decision was reached, not just what the outcome was (Sotirou et al., 2025)."
    quote_candidate: "Additionally, we will investigate alternative explanation methods, such as counter- factual explanations, and assess their applicability in a multimodal framework for music understanding."
    secondary_score: 49.31506849315068
    secondary_quote: "However, as these models become more prevalent, the need for explainability grows—understanding how these systems make decisions is vital for ensuring fairness, reducing bias, and fostering trust."

## tintarev_evaluating_2012
- title: Evaluating the effectiveness of explanations for recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.57142857142857
    claim: "Their later evaluation work showed that these goals do not always move together, and that systems capable of generating convincing explanations may not actually support genuine user understanding (Tintarev and Masthoff, 2012)."
    quote_candidate: "Three types of explanations were used: 1."
    secondary_score: 53.1578947368421
    secondary_quote: "If an explanation helps users make good decisions, getting more (accurate and balanced) information or trying the product should not change their valuation of the product greatly."

## vall_feature-combination_2019
- title: Feature-combination hybrid recommender systems for automated music playlist continuation
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Vall et al. - 2019 - Feature-combination hybrid recommender systems for automated music playlist continuation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 47.32142857142857
    claim: "Playlist-generation studies commonly evaluate coherence, novelty, diversity, and ordering together, and report that improving one dimension can reduce another unless trade-offs are made explicit (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015)."
    quote_candidate: "2017b, 2019), and Bonnin and Jannach (2014) proposed a successful variation consisting in computing similarities between artists instead of between songs, even when the ultimate recommendations were at the song level."
    secondary_score: 45.43429844097996
    secondary_quote: "2 Even though the process of listening to a playlist is inherently sequential, we found that considering the song order in curated music playlists is actually not crucial to extend such playlists (V all et al.2018b, 2019)."

## zamani_analysis_2019
- title: An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Continuation
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Zamani et al. - 2019 - An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Contin.pdf
- mapping_score: 100
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 41.61849710982659
    claim: "Outcomes depend heavily on how candidates are handled (Zamani et al., 2019)."
    quote_candidate: "In other words, either the track list or the artist list was randomly deactivated in the input of the autoencoder."
    secondary_score: 40.69767441860465
    secondary_quote: "As depicted, the United States has the highest number of active teams followed by Austria and Italy."

## zhang_explainable_2020
- title: Explainable Recommendation: A Survey and New Perspectives
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\387\Zhang and Chen - 2020 - Explainable Recommendation A Survey and New Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.342465753424655
    claim: "In practice, this can reduce direct feature-level inspectability unless additional explanation mechanisms are engineered around the ranking process (Zhang and Chen, 2020)."
    quote_candidate: "The model-intrinsic approach develops interpretable models, whose decision mechanism is transparent, and thus, we can naturally provide explanations for the model decisions (Zhanget al., 2014a)."
    secondary_score: 50.450450450450454
    secondary_quote: "The model-agnostic approach (Wang et al., 2018d), or sometimes called the post-hoc explanation approach (Peake and Wang, 2018), allows the decision mechanism to be a blackbox."
  - claim_2_status: partially_supported
    score: 56.06936416184971
    claim: "Post-hoc explanations can sound plausible while remaining only loosely connected to the mechanism that actually produced the ranking (Zhang and Chen, 2020)."
    quote_candidate: "The model-intrinsic approach develops interpretable models, whose decision mechanism is transparent, and thus, we can naturally provide explanations for the model decisions (Zhanget al., 2014a)."
    secondary_score: 52.22929936305732
    secondary_quote: "The model-agnostic approach (Wang et al., 2018d), or sometimes called the post-hoc explanation approach (Peake and Wang, 2018), allows the decision mechanism to be a blackbox."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.810810810810814
    claim: "Multiple reviews of recommender systems research document that absent or under-specified preprocessing steps, configuration choices, and dependency declarations can reduce the practical feasibility of independent result verification (Ferrari Dacrema et al., 2021; Bellogin et al., 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "By setting up an open benchmarking leaderboard, together with the freely available benchmarking artifacts (e.g., datasets, code, configurations, results, and reproducing steps), we hope that the BARS project could benefit all researchers, practitioners, and edu- cators in the community."
    secondary_score: 49.37759336099585
    secondary_quote: "We also call for generous contributions from the whole community to improve this open benchmarking project and to keep healthy development with the rapid evolution of recommender systems research."

## Summary
- total_claim_checks: 46
- supported: 2
- partially_supported: 28
- weak_support: 16
- no_match: 0