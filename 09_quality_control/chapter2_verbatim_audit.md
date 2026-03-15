# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `08_writing\chapter2_draft_v11.md` against extracted text from mapped local PDFs.
Method note: automated lexical matching (RapidFuzz token-set ratio) with manual thresholding.

## adomavicius_toward_2005
- title: Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\381\Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf
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
  - claim_3_status: weak_support
    score: 49.53703703703704
    claim: "That can work well with dense interaction histories, but interpretability tends to weaken when rankings are encoded in latent relationships rather than named feature comparisons (Adomavicius and Tuzhilin, 2005; Zhang and Chen, 2020)."
    quote_candidate: "In particular, since collaborative systems use other users’ recommendations (ratings), they can deal with any kind of content and recommend any items, even the ones that are dissimilar to those seen in the past."
    secondary_score: 48.0
    secondary_quote: "While information retrieval techniques work well in extracting features from text documents, some other domains have an inherent problem with automatic feature extraction."
  - claim_4_status: weak_support
    score: 49.88662131519274
    claim: "This project relies on imported listening history, which provides implicit preference evidence rather than a direct statement of what the user wants (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022)."
    quote_candidate: "Another way to overcome the differing uses of the rating scale is to deploy preference-based filtering [22], [35], [51], [52], which focuses on predicting the relative prefer- ences of users instead of absolute rating values, as was pointed out earlier in Section 2."
    secondary_score: 49.7737556561086
    secondary_quote: "As another example, a user can have significantly different preferences for the types of movies she wants to see when she is going out to a movie theater with a boyfriend on a Saturday night as opposed to watching a rental movie at home with her parents on a Wednesday evening."

## afroogh_trust_2024
- title: Trust in AI: progress, challenges, and future directions
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\428\Afroogh et al. - 2024 - Trust in AI progress, challenges, and future directions.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.130548302872064
    claim: "Usability work adds a separate pressure: even a technically faithful explanation still needs to be comprehensible to a non-expert audience (Knijnenburg et al., 2012; Afroogh et al., 2024)."
    quote_candidate: "From a different perspective, while interpersonal trust is associated with benevolence, integrity, and ability, trust in AI is less relevant to honesty and benevolence since AI systems lack intentionality (Asan et al., 2020a)."
    secondary_score: 49.56772334293948
    secondary_quote: "For an AI system to be perceived as trustworthy, ﬁve principles need to be ful ﬁlled, including bene ﬁcence, non-male ﬁcence, autonomy, justice, and explicability (Dosilovic et al., 2018)."

## andjelkovic_moodplay_2019
- title: Moodplay: Interactive music recommendation based on Artists' mood similarity
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf
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
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.44956772334294
    claim: "Claiming reproducibility means runs need to be captured through recorded configuration and stage-level diagnostics, not just described in prose (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "Elliot is a comprehensive recommendation framework that aims to run and reproduce an entire experimental pipeline by processing a simple configuration file."
    secondary_score: 47.79874213836478
    secondary_quote: "It requires the user just to compile a flexible configuration file to conduct a rigorous and reproducible experimental evaluation."
  - claim_2_status: weak_support
    score: 45.85635359116022
    claim: "Under-specified split definitions, preprocessing steps, and dependency versions routinely prevent results from being independently reconstructed (Ferrari Dacrema et al., 2021; Bellogin et al., 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "Elliot is a comprehensive recommendation framework that aims to run and reproduce an entire experimental pipeline by processing a simple configuration file."
    secondary_score: 44.94949494949495
    secondary_quote: "Moreover, machine learning (and recently also deep learn- ing) techniques are prominent in algorithmic research and require their hyperparameter optimization strategies and procedures [6, 92]."

## barlaug_neural_2021
- title: Neural Networks for Entity Matching: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Barlaug and Gulla - 2021 - Neural Networks for Entity Matching A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.80701754385965
    claim: "Neural matching is a relevant alternative for difficult cases (Barlaug and Thorvaldsen, 2021), but neural approaches reduce traceability unless substantial logging infrastructure is built around them — a poor trade-off for a system whose primary claim is transparency."
    quote_candidate: "With this is in mind, we formulate the following research questions: —How do methods using neural networks for entity matching differ in what they solve, and how do the methods that address the same aspects differ in their approaches?"
    secondary_score: 45.14563106796116
    secondary_quote: "—We discuss the contributions of deep learning to entity matching compared to traditional approaches using a proposed reference model for a deep learning-based entity matching process."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: supported
    score: 69.06474820143885
    claim: "That distinction matters because recommender evaluation is sensitive to how experiments are set up — preprocessing decisions, metric framing, and protocol choices can all shift results substantially, and strong performance numbers under one set of conditions do not reliably transfer to a design context where inspectable engineering is the primary contribution (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024)."
    quote_candidate: "(d) The paper does not make a contribution regarding the evaluation of recommender systems."
    secondary_score: 67.9245283018868
    secondary_quote: "For example, Ferrari Dacrema et al."

## beel_towards_2016
- title: Towards reproducibility in recommender-systems research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Beel et al. - 2016 - Towards reproducibility in recommender-systems research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.876543209876544
    claim: "Claiming reproducibility means runs need to be captured through recorded configuration and stage-level diagnostics, not just described in prose (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "“Reproducibility” describes the case in which similar ideas lead to similar exper- imental results given similar evaluations and scenarios, where “similar results” are results that allow the same conclusions to be drawn (Casadevall and Fang 2010)."
    secondary_score: 48.333333333333336
    secondary_quote: "Bethard and Jurafsky (2010) reported that using citation counts in the recommenda- tion process strongly increased the effectiveness of their recommendation approach, 123 Towards reproducibility in recommender-systems research 71 Table 1 Results of different CBF and CF evaluations ( Beel 2015; Beel et al."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.411483253588514
    claim: "Under-specified split definitions, preprocessing steps, and dependency versions routinely prevent results from being independently reconstructed (Ferrari Dacrema et al., 2021; Bellogin et al., 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "(2019), very different actors are pointed out as being responsible (and accountable for) the actions and decisions of an Artificial Intelligence agent: developers, designers, institutions, or industry at large."
    secondary_score: 45.80152671755725
    secondary_quote: "We perform such an analysis, including experimental results and relying on recent research from adjacent fields to predict the potential challenges our field may witness in the near future."

## bogdanov_semantic_2013
- title: Semantic audio content-based music recommendation and visualization based on user preference examples
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\409\Bogdanov et al. - 2013 - Semantic audio content-based music recommendation and visualization based on user preference example.pdf
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
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.1139896373057
    claim: "Coherence, novelty, diversity, and ordering tend to pull against one another and rarely optimise together without deliberate trade-offs (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015)."
    quote_candidate: "Another potential problem is that not all types of metadata are objective, and annotations regarding, for example, the mood or the genre of a track can be imprecise or inconsistent [Celma 2010; Lee and Cho 2011]."
    secondary_score: 45.892351274787536
    secondary_quote: "2008], (c) a full list of tracks to be sorted or mixed with other tracks [Logan 2004], or (d) a list of tracks already contained in the playlist or recently played (playlist history) [Baur et al."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.41388174807198
    claim: "Hybrid systems can combine the strengths of both, but the combination adds reasoning complexity that makes audit and explanation harder unless interpretability is deliberately engineered in from the start (Çano and Morisio, 2017)."
    quote_candidate: "Morisio / Hybrid recommender systems: A systematic literature review 1497 authors in [P21] use a probabilistic model to extract latent features from item’s representation."
    secondary_score: 51.399491094147585
    secondary_quote: "Morisio / Hybrid recommender systems: A systematic literature review the extracted information was stored in Nvivo3 which was used to manage data extraction and synthesis process."
  - claim_2_status: weak_support
    score: 49.59128065395095
    claim: "Neural and hybrid recommenders can capture richer feature interactions and often achieve stronger predictive performance where training data is plentiful (Çano and Morisio, 2017; He et al., 2017; Liu et al., 2025)."
    quote_candidate: "Morisio / Hybrid recommender systems: A systematic literature review the extracted information was stored in Nvivo3 which was used to manage data extraction and synthesis process."
    secondary_score: 48.57142857142857
    secondary_quote: "We also explore the hybridization classes each hybrid recommender belongs to, the application domains, the evaluation process and proposed future research directions."

## cavenaghi_systematic_2023
- title: A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Cavenaghi et al. - 2023 - A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.69565217391305
    claim: "Claiming reproducibility means runs need to be captured through recorded configuration and stage-level diagnostics, not just described in prose (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "[27], for instance, quantifies the state of reproducibility of empirical AI research by analysing a total of 400 research papers from the conference series IJCAI and AAAI."
    secondary_score: 48.593350383631716
    secondary_quote: "The hardware configuration used to run the experiments is not provided either in the paper or in the GitHub repository, while the software dependencies are reported in 12https://github.com/jiaqima/Off-Policy-2-Stage."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.42718446601942
    claim: "For a transparency-focused project, the practical advantage is that ranking depends on explicit features, and the reasoning behind any recommendation can usually be traced back to those same features (Deldjoo et al., 2024)."
    quote_candidate: "Automatic audio analysis algorithms aim to model some of these processes and represent perceived dimensions by extracting content features, which can be used in the recommendation process [33]."
    secondary_score: 51.041666666666664
    secondary_quote: "The intuitive idea behind this work is that music experts with better VM and MS may perceive the same music recommendation list more diverse than non-specialists with lower VM and MS."

## elmagarmid_duplicate_2007
- title: Duplicate Record Detection: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Elmagarmid et al. - 2007 - Duplicate Record Detection A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.43423799582463
    claim: "Standard entity-resolution practice addresses this through blocking to narrow candidate pairs before comparison, then staged matching with progressive refinement — making uncertainty progressively more visible rather than silently absorbing it (Elmagarmid et al., 2007; Papadakis et al., 2021)."
    quote_candidate: "It can also lead to an increased number of missed matches due to errors in the blocking step that placed entries in the wrong buckets, thereby preventing them from being compared to actual matching entries."
    secondary_score: 47.927927927927925
    secondary_quote: "The mapping transformation standardizes data, the matching transformation finds pairs of records that probably refer to the same real object, the clustering transformation groups together matching pairs with a high similarity value, and, finally, the merging transformation collapses each individual cluster into a tuple of the resulting data source."

## ferraro_automatic_2018
- title: Automatic playlist continuation using a hybrid recommender system combining features from text and audio
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ferraro et al. - 2018 - Automatic playlist continuation using a hybrid recommender system combining features from text and a.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 45.52845528455285
    claim: "Coherence, novelty, diversity, and ordering tend to pull against one another and rarely optimise together without deliberate trade-offs (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015)."
    quote_candidate: "To improv e this approach further, we combined it with another model which re c- ommends the most probable tracks based on co-occurrence and proximity of tracks in playlists in the training data."
    secondary_score: 45.27220630372493
    secondary_quote: "It is important to note that these results are not the same as t he ﬁnal scores published on July 13th, 2018, as they are only cal cu- lated using 50% of the Challenge Set."

## fkih_similarity_2022
- title: Similarity measures for Collaborative Filtering-based Recommender Systems: Review and experimental comparison
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\432\Fkih - 2022 - Similarity measures for Collaborative Filtering-based Recommender Systems Review and experimental c.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 47.05882352941177
    claim: "These are real design decisions, not implementation details (Fkih, 2022)."
    quote_candidate: "The standard devi- ation of the item i (SDi) is provided in Eq."
    secondary_score: 45.23809523809524
    secondary_quote: "By cons, Jester is a dense dataset (with a low sparsity) and its rating ranges between /C0 10 and 10."
  - claim_2_status: partially_supported
    score: 51.590106007067135
    claim: "How similarity behaves in feature space depends on specific distance-function choices, and those choices matter (Fkih, 2022; Schweiger et al., 2025)."
    quote_candidate: "Chebyshev distance The Chebyshev distance between two vectors is the greatest of their differences along any coordinate dimension ( Abello et al., 2002)."
    secondary_score: 51.245551601423486
    secondary_quote: "We have to mention that we used Python libraries to implement the Recommender System and the similarity measures (Pedregosa et al., 2011 )."

## he_neural_2017
- title: Neural Collaborative Filtering
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\436\He et al. - 2017 - Neural Collaborative Filtering.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.794520547945204
    claim: "Neural and hybrid recommenders can capture richer feature interactions and often achieve stronger predictive performance where training data is plentiful (Çano and Morisio, 2017; He et al., 2017; Liu et al., 2025)."
    quote_candidate: "As shown in Table 2, the NeuMF with pre- training achieves better performance in most cases; only for MovieLens with a small predictive factors of 8, the pre- training method performs slightly worse."
    secondary_score: 53.6144578313253
    secondary_quote: "First, we can see that with more iterations, the training loss of NCF models gradually decreases and the recommendation performance is improved."

## herlocker_evaluating_2004
- title: Evaluating collaborative filtering recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Herlocker et al. - 2004 - Evaluating collaborative filtering recommender systems.pdf
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
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\395\Jin et al. - 2020 - Effects of personal characteristics in control-oriented user interfaces for music recommender system.pdf
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
    score: 50.56818181818182
    claim: "Claiming controllability is not enough — changing a control needs to produce interpretable downstream effects, and those effects need to be documented (Jin et al., 2020; Nauta et al., 2023)."
    quote_candidate: "On the other hand, although controls empower users to inﬂuence the recommen- dation process to a greater extent, a high level of control may increase their cognitive load (Jin et al."
    secondary_score: 50.45592705167173
    secondary_quote: "In addition, users tend to be more satisﬁed when they have control over how recommender systems produce suggestions for them (Konstan and Riedl 2012)."
  - claim_3_status: partially_supported
    score: 54.25867507886435
    claim: "This is consistent with controllability research that treats user influence as useful when it is explicit, bounded, and testable (Jin et al., 2020; Andjelkovic et al., 2019)."
    quote_candidate: "(2016), we previously devised different levels of user control (low, middle, and high) associated with various components of a recommender system (Jin et al."
    secondary_score: 51.52354570637119
    secondary_quote: "For example, when investigating inter- active user interfaces, users’ experience may be seen as their level of familiarity with computers (Zhang and Chignell 2001) or with visualizations (Carenini et al."

## knijnenburg_explaining_2012
- title: Explaining the user experience of recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\422\Knijnenburg et al. - 2012 - Explaining the user experience of recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 45.97014925373134
    claim: "Usability work adds a separate pressure: even a technically faithful explanation still needs to be comprehensible to a non-expert audience (Knijnenburg et al., 2012; Afroogh et al., 2024)."
    quote_candidate: "An excellent overview of available algorithms can be found inBurke (2002) and inAdomavicius and Tuzhilin (2005); more recent approaches were presented in Koren et al."
    secondary_score: 44.936708860759495
    secondary_quote: "not measuring the SSA as a mediator between OSA and EXP) makes it hard to explain why in some experiments better algorithms do not lead to a better experience."

## liu_aggregating_2025
- title: Aggregating Contextual Information for Multi-Criteria Online Music Recommendations
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Liu - 2025 - Aggregating Contextual Information for Multi-Criteria Online Music Recommendations.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.696969696969695
    claim: "Neural and hybrid recommenders can capture richer feature interactions and often achieve stronger predictive performance where training data is plentiful (Çano and Morisio, 2017; He et al., 2017; Liu et al., 2025)."
    quote_candidate: "The performance comparison presented in Table 3 provides a detailed evaluation of various recommendation algorithms on the CAL500 dataset."
    secondary_score: 48.346055979643765
    secondary_quote: "High user coverage is essential, particularly for addressing the ‘‘cold start’’ problem, where users with limited interaction history may receive inadequate recommendations from traditional algorithms."

## liu_multimodal_2025
- title: Multimodal Recommender Systems: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\411\Liu et al. - 2025 - Multimodal Recommender Systems A Survey.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Neural and hybrid recommenders can capture richer feature interactions and often achieve stronger predictive performance where training data is plentiful (Çano and Morisio, 2017; He et al., 2017; Liu et al., 2025)."
    quote_candidate: "—Challenge 2: For the feature interaction procedure, how to fuse the modality features in differ- ent semantic spaces and get various preferences for each modality."
    secondary_score: 49.62406015037594
    secondary_quote: "Based on MMGCN, GRCN [71] improves the performance of recommendations by adaptively modifying the graph’s structure during model training to delete incorrect interaction data (users clicked uninterested videos)."

## lu_recommender_2015
- title: Recommender system application developments: A survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\383\Lu et al. - 2015 - Recommender system application developments A survey.pdf
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
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\426\Nauta et al. - 2023 - From Anecdotal Evidence to Quantitative Evaluation Methods A Systematic Review on Evaluating Explai.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.0
    claim: "Research consistently shows that explanations may raise perceived satisfaction without improving genuine understanding (Nauta et al., 2023)."
    quote_candidate: "Note that a set of outcome explanations can collectively comprise a global explanation for model inspection (cf."
    secondary_score: 46.88644688644688
    secondary_quote: "Validating explanations with users can unintentionally combine the evaluation of explanation correctness with evaluating the correctness of the predictive model."
  - claim_2_status: weak_support
    score: 45.744680851063826
    claim: "Claiming controllability is not enough — changing a control needs to produce interpretable downstream effects, and those effects need to be documented (Jin et al., 2020; Nauta et al., 2023)."
    quote_candidate: "For collecting all evaluation methods, we review all 361 included papers, since 49 papers do not introduce a new XAI method, but could contain relevant evaluation metrics to compare and evaluate existing XAI methods."
    secondary_score: 45.67901234567901
    secondary_quote: "While interpretability and explainability are often presented as a subjectively validated binary property, we consider it a multi- faceted concept."

## papadakis_blocking_2021
- title: Blocking and Filtering Techniques for Entity Resolution: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Papadakis et al. - 2021 - Blocking and Filtering Techniques for Entity Resolution A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 45.63492063492063
    claim: "Standard entity-resolution practice addresses this through blocking to narrow candidate pairs before comparison, then staged matching with progressive refinement — making uncertainty progressively more visible rather than silently absorbing it (Elmagarmid et al., 2007; Papadakis et al., 2021)."
    quote_candidate: "Hash-Based Methods.Standard Blocking(SB)[ 49] involves the simplest functionality: an ex- pert selects the most suitable attributes, and a transformation function concatenates (parts of) their values to form blocking keys."
    secondary_score: 44.96402877697842
    secondary_quote: "They are grouped into three categories, depending on the criterion for moving the boundaries of the window [91]: 1) Key similarity strategy.The window size increases if the similarity of the blocking keys exceeds a predetermined threshold, which indicates that more similar entities should be expected [91]."

## roy_systematic_2022
- title: A systematic review and research perspective on recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\385\Roy and Dutta - 2022 - A systematic review and research perspective on recommender systems.pdf
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
    claim: "This project relies on imported listening history, which provides implicit preference evidence rather than a direct statement of what the user wants (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022)."
    quote_candidate: "This ensures the security and privacy of user data."
    secondary_score: 50.0
    secondary_quote: "These techniques also need two steps for prediction—the first step is to build the model, and the second step is to predict ratings using a function (f) which takes the model defined in the first step and the user profile as input."

## ru_improving_2023
- title: Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Perspective
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.96969696969697
    claim: "It has also been used in independent multimodal recommendation work, which supports its practical suitability for this scope (Ru et al., 2023)."
    quote_candidate: "As we all know, BERT model [12] has a strong ability to extract text information, which has been confirmed in many NLP tasks."
    secondary_score: 46.02272727272727
    secondary_quote: "Santana’s model achieves the worst results because it only used audio informa- tion, which indicates that multi-modal information is crucial for improving the classification performance of multi-label MGC methods."

## schweiger_impact_2025
- title: The impact of playlist characteristics on coherence in user-curated music playlists
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\rp\files\578\Schweiger et al. - 2025 - The impact of playlist characteristics on coherence in user-curated music playlists.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 44.85981308411215
    claim: "How similarity behaves in feature space depends on specific distance-function choices, and those choices matter (Fkih, 2022; Schweiger et al., 2025)."
    quote_candidate: "For instance, [7] uses the term coherence to refer to the Schweigeretal."
    secondary_score: 43.51145038167939
    secondary_quote: "[8]p r o p o s e s a hybrid recommendation system that balances coherence and diversity based on given Schweigeretal."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
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
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\391\Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf
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
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Vall et al. - 2019 - Feature-combination hybrid recommender systems for automated music playlist continuation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 49.3573264781491
    claim: "Coherence, novelty, diversity, and ordering tend to pull against one another and rarely optimise together without deliberate trade-offs (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015)."
    quote_candidate: "2017b, 2019), and Bonnin and Jannach (2014) proposed a successful variation consisting in computing similarities between artists instead of between songs, even when the ultimate recommendations were at the song level."
    secondary_score: 44.390243902439025
    secondary_quote: "( 2012) also presented a latent- factor CF model tailored to mine Internet radio stations, accounting for song, artist, 123 Feature-combination hybrid recommender systems for automated… 531 time of the day, and song adjacency."

## zamani_analysis_2019
- title: An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Continuation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zamani et al. - 2019 - An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Contin.pdf
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
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\387\Zhang and Chen - 2020 - Explainable Recommendation A Survey and New Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 47.28132387706856
    claim: "That can work well with dense interaction histories, but interpretability tends to weaken when rankings are encoded in latent relationships rather than named feature comparisons (Adomavicius and Tuzhilin, 2005; Zhang and Chen, 2020)."
    quote_candidate: "The model-intrinsic approach develops interpretable models, whose decision mechanism is transparent, and thus, we can naturally provide explanations for the model decisions (Zhanget al., 2014a)."
    secondary_score: 46.8384074941452
    secondary_quote: "In a broader sense, the explainability of AI systems was already a core discussion in the 1980s era of “old” or logical AI research, when knowledge-based systems predicted (or diagnosed) well but could not explain why."
  - claim_2_status: partially_supported
    score: 56.06936416184971
    claim: "Post-hoc explanations can sound plausible while remaining only loosely connected to the mechanism that actually produced the ranking (Zhang and Chen, 2020)."
    quote_candidate: "The model-intrinsic approach develops interpretable models, whose decision mechanism is transparent, and thus, we can naturally provide explanations for the model decisions (Zhanget al., 2014a)."
    secondary_score: 52.22929936305732
    secondary_quote: "The model-agnostic approach (Wang et al., 2018d), or sometimes called the post-hoc explanation approach (Peake and Wang, 2018), allows the decision mechanism to be a blackbox."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 45.68527918781726
    claim: "Under-specified split definitions, preprocessing steps, and dependency versions routinely prevent results from being independently reconstructed (Ferrari Dacrema et al., 2021; Bellogin et al., 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "In many cases, the reported results cannot be easily reproduced due to the lack of either data preprocessing details, model implementations, hyper-parameter configurations, or even all of them."
    secondary_score: 45.30120481927711
    secondary_quote: "We believe that easy access to consistently split and pre- processed datasets with reusable baseline results could help the research community avoid reporting inconsistent or misleading results in their future work."

## Summary
- total_claim_checks: 46
- supported: 2
- partially_supported: 20
- weak_support: 24
- no_match: 0