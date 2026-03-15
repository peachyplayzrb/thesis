# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `08_writing\chapter2_citation_hardened_v1.md` against extracted text from mapped local PDFs.
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
  - claim_3_status: partially_supported
    score: 51.91740412979351
    claim: "Collaborative filtering takes a different route, inferring relevance from patterns of interaction across users and items (Adomavicius and Tuzhilin, 2005)."
    quote_candidate: "A statistical model for collaborative filtering was proposed in [105], and several different algorithms for estimating the model parameters were compared, including K-means clustering and Gibbs sampling."
    secondary_score: 51.824817518248175
    secondary_quote: "Note that both the content-based and the collaborative approaches use the same cosine measure from information retrieval literature."

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
    score: 61.96319018404908
    claim: "In this project, reproducibility claims follow framework-oriented guidance that stresses explicit configuration and repeatable experimental pipelines (Anelli et al., 2021)."
    quote_candidate: "Elliot is a comprehensive recommendation framework that aims to run and reproduce an entire experimental pipeline by processing a simple configuration file."
    secondary_score: 54.54545454545455
    secondary_quote: "It requires the user just to compile a flexible configuration file to conduct a rigorous and reproducible experimental evaluation."

## barlaug_neural_2021
- title: Neural Networks for Entity Matching: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Barlaug and Gulla - 2021 - Neural Networks for Entity Matching A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.0
    claim: "Neural methods are also a recognised line of work in entity matching and remain relevant comparator context for difficult linkage cases (Barlaug and Thorvaldsen, 2021)."
    quote_candidate: "We also discuss contributions from deep learning in entity matching compared to traditional methods, and propose a taxonomy of deep neural networks for entity matching."
    secondary_score: 53.7037037037037
    secondary_quote: "[17] specifically review entity matching techniques in the context of big data."

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

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.80722891566265
    claim: "Recent reproducibility papers explicitly report that missing preprocessing and protocol detail can obstruct independent replication of recommender results (Ferrari Dacrema et al., 2021; Bellogin et al., 2021; Zhu et al., 2022)."
    quote_candidate: "3.2 we provide a more general overview of trends and research works that have explicitly addressed reproducibility in the area."
    secondary_score: 50.74626865671642
    secondary_quote: "For that, we propose reproducibility guidelines, inspired by how recommendation systems are imple- mented and evaluated, and argue that these should improve accountability of the entire research field."

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
    score: 45.13064133016627
    claim: "Playlist-generation studies use multiple evaluation criteria, including sequence-sensitive and diversity-related measures, rather than a single objective (Bonnin and Jannach, 2015; Vall et al., 2019)."
    quote_candidate: "Moreover, depending on the available data and the chosen evaluation measure, it has been shown that very simple popularity-based algorithms can outperform sophisticated algorithms in more general music recommendation scenarios [McFee et al."
    secondary_score: 45.023696682464454
    secondary_quote: "(4) Finally, users can express their preferences by immediately rating (like/dislike) the tracks in the created playlist [Pauws and Eggen 2002] or by skipping individual tracks broadcasted by a personalized online radio station [Pampalk et al."

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
  - claim_2_status: partially_supported
    score: 51.41065830721003
    claim: "Neural and hybrid recommenders are established comparator families and can represent richer interactions in data-rich settings (Çano and Morisio, 2017; He et al., 2017)."
    quote_candidate: "Papers that report only abstracts or slides of presentation, lacking detailed information Grey literature RQ5 In what domains are hybrid recommenders applied?"
    secondary_score: 50.0
    secondary_quote: "Hybrid RSs represent a somehow newer family of recommender systems compared to other well known and widely used families such as CF or CBF."

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
    score: 47.956403269754766
    claim: "Entity-resolution surveys explicitly cover blocking and filtering steps used to reduce candidate comparisons before detailed matching (Papadakis et al., 2021; Elmagarmid et al., 2007)."
    quote_candidate: "Sarawagi and Bhamidipaty [15] designed ALIAS, a learning-based duplicate detection system, that uses the idea of a “reject region” (see Section 4.2.3) to significantly reduce the size of the training set."
    secondary_score: 47.794117647058826
    secondary_quote: "We examine some of the methods that can be used to reduce the cost of record comparison in Section 5.2."

## fkih_similarity_2022
- title: Similarity measures for Collaborative Filtering-based Recommender Systems: Review and experimental comparison
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\432\Fkih - 2022 - Similarity measures for Collaborative Filtering-based Recommender Systems Review and experimental c.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.7037037037037
    claim: "Evidence comparing similarity measures shows that these choices affect neighbour selection and score behaviour, so they should be treated as explicit design decisions (Fkih, 2022)."
    quote_candidate: "In fact, results show that ITR and IPWR are the most suitable similarity measures for a user-based RS while AMI is the best choice for an item-based RS."
    secondary_score: 52.26480836236934
    secondary_quote: "This process consists of three steps: similarity computation, neighborhood selection and rating prediction."
  - claim_2_status: partially_supported
    score: 52.87356321839081
    claim: "Similarity behavior depends on the selected distance function and related parameterization, and those choices matter in practice (Fkih, 2022)."
    quote_candidate: "Similarity measures: A review In this section, we outline the theoretical foundation of a set of selected similarity measures."
    secondary_score: 52.67175572519084
    secondary_quote: "While the second approach tries to build a model (a machine learning) describing the user behavior in order to predict his choices."

## he_neural_2017
- title: Neural Collaborative Filtering
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\436\He et al. - 2017 - Neural Collaborative Filtering.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.14942528735632
    claim: "Neural and hybrid recommenders are established comparator families and can represent richer interactions in data-rich settings (Çano and Morisio, 2017; He et al., 2017)."
    quote_candidate: "The key to a personalized recommender system is in modelling users’ preference on items based on their past interactions (e.g., ratings and clicks), known as collaborative ﬁltering [31, 46]."
    secondary_score: 49.824561403508774
    secondary_quote: "As such, we ﬁltered the dataset in the same way as the MovieLens data that retained only users with at least 20 interactions (pins)."

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
    score: 50.595238095238095
    claim: "In this thesis, controllability is treated as valid only when changing a control produces traceable downstream differences in logged pipeline behavior and outputs (Jin et al., 2020)."
    quote_candidate: "(2016), we previously devised different levels of user control (low, middle, and high) associated with various components of a recommender system (Jin et al."
    secondary_score: 49.29178470254958
    secondary_quote: "Previous research has shown many beneﬁts for supporting controllability and trans- parency in several application domains such as music recommendations (Bostandjiev et al."
  - claim_3_status: partially_supported
    score: 54.25867507886435
    claim: "This is consistent with controllability research that treats user influence as useful when it is explicit, bounded, and testable (Jin et al., 2020; Andjelkovic et al., 2019)."
    quote_candidate: "(2016), we previously devised different levels of user control (low, middle, and high) associated with various components of a recommender system (Jin et al."
    secondary_score: 51.52354570637119
    secondary_quote: "For example, when investigating inter- active user interfaces, users’ experience may be seen as their level of familiarity with computers (Zhang and Chignell 2001) or with visualizations (Carenini et al."

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
  - claim_1_status: partially_supported
    score: 52.348993288590606
    claim: "Explainability evaluations report cases where explanations improve perceived satisfaction without corresponding gains in verified understanding (Nauta et al., 2023)."
    quote_candidate: "Validating explanations with users can unintentionally combine the evaluation of explanation correctness with evaluating the correctness of the predictive model."
    secondary_score: 50.625
    secondary_quote: "Analysis of this set of papers provide quantitative insights into the extent and nature of research activity in XAI and the evaluation of the resulting explanations (Section5)."

## papadakis_blocking_2021
- title: Blocking and Filtering Techniques for Entity Resolution: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Papadakis et al. - 2021 - Blocking and Filtering Techniques for Entity Resolution A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.231511254019296
    claim: "Entity-resolution surveys explicitly cover blocking and filtering steps used to reduce candidate comparisons before detailed matching (Papadakis et al., 2021; Elmagarmid et al., 2007)."
    quote_candidate: "Entities sharing the same output for a particular blocking predicate are considered candidate matches (i.e., hash-based functionality)."
    secondary_score: 46.3855421686747
    secondary_quote: "This dataset is used to learn blocking predicates, i.e., combinations of an attribute name and a transformation function (e.g., {title ,First 3Characters})."

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
    score: 52.7027027027027
    claim: "This project relies on imported listening history, which is treated as implicit preference evidence rather than a direct statement of user intent (Roy and Dutta, 2022)."
    quote_candidate: "This technique starts with finding a group or collection of user X whose preferences, likes, and dislikes are similar to that of user A."
    secondary_score: 51.757188498402556
    secondary_quote: "In essence, recommender systems deal with two entities—users and items, where each user gives a rating (or preference value) to an item (or product)."

## ru_improving_2023
- title: Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Perspective
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.28901734104046
    claim: "Independent studies have also used Music4All in multimodal music tasks, which supports practical dataset reuse for this scope while not implying direct task equivalence (Ru et al., 2023)."
    quote_candidate: "Early studies [1, 2] on MGC task were based on digital signal processing and traditional machine learning methods, which use some hand-crafted features as inputs."
    secondary_score: 49.32249322493225
    secondary_quote: "Considering that Music4All dataset is noisy and contains mul- tiple languages in music lyrics, we filtered out music tracks with missing information or non-English lyrics in our exper- iment."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Recent music explainability work provides method-level examples of exposing contribution signals, supporting mechanism-linked explanation reporting in this project context (Sotirou et al., 2025)."
    quote_candidate: "Through this work, we contribute to improving the interpretability of multimodal music models, empowering users to make informed choices, and fostering more equitable, fair, and transparent music understanding systems."
    secondary_score: 49.246231155778894
    secondary_quote: "Multimodal explainability offers a significant advantage over unimodal methods by providing a more compre- hensive understanding of how different modalities interact within a model’s decision-making process."

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
    score: 46.733668341708544
    claim: "Playlist-generation studies use multiple evaluation criteria, including sequence-sensitive and diversity-related measures, rather than a single objective (Bonnin and Jannach, 2015; Vall et al., 2019)."
    quote_candidate: "2 Even though the process of listening to a playlist is inherently sequential, we found that considering the song order in curated music playlists is actually not crucial to extend such playlists (V all et al.2018b, 2019)."
    secondary_score: 46.557377049180324
    secondary_quote: "Previous research has mostly focused on playlist-neighbors CF systems (Bonnin and Jannach 2014;H a r i r i et al."

## zamani_analysis_2019
- title: An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Continuation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zamani et al. - 2019 - An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Contin.pdf
- mapping_score: 100
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.333333333333336
    claim: "APC challenge analyses report frequent use of two-stage playlist-continuation architectures (Zamani et al., 2019)."
    quote_candidate: "As shown in the table, several teams took advantage of a two-stage architecture for the playlist continuation task."
    secondary_score: 51.36612021857923
    secondary_quote: "However, the two-stage architecture can also improve the APC performance."

## zhang_explainable_2020
- title: Explainable Recommendation: A Survey and New Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\387\Zhang and Chen - 2020 - Explainable Recommendation A Survey and New Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
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
  - claim_1_status: partially_supported
    score: 51.66240409207161
    claim: "Recent reproducibility papers explicitly report that missing preprocessing and protocol detail can obstruct independent replication of recommender results (Ferrari Dacrema et al., 2021; Bellogin et al., 2021; Zhu et al., 2022)."
    quote_candidate: "In many cases, the reported results cannot be easily reproduced due to the lack of either data preprocessing details, model implementations, hyper-parameter configurations, or even all of them."
    secondary_score: 51.536643026004725
    secondary_quote: "It provides reusable dataset splits, detailed evaluation protocols, convenient open-source models and APIs, complete training logs, and well-tuned benchmarking results for reliable reproducibility of recommendation models."

## Summary
- total_claim_checks: 34
- supported: 2
- partially_supported: 28
- weak_support: 4
- no_match: 0