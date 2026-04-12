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
    score: 50.442477876106196
    claim: "Foundational surveys frame recommendation as utility estimation under uncertainty rather than direct preference detection, because available evidence is partial, noisy, and context-dependent (Adomavicius and Tuzhilin, 2005; Lu et al., 2015)."
    quote_candidate: "Many real-life recommendation applications, including several business applications, such as the ones described above, are arguably more complex than a movie recommender system and would require taking more factors into the recommendation consideration."
    secondary_score: 49.586776859504134
    secondary_quote: "The interest in this area still remains high because it constitutes a problem-rich research area and because of the abundance of practical applications that help users to deal with information overload and provide personalized recommendations, content, and services to them."
  - claim_2_status: partially_supported
    score: 51.18483412322275
    claim: "Content-based, collaborative, and hybrid systems remain the dominant paradigm families (Adomavicius and Tuzhilin, 2005; Lu et al., 2015), yet this taxonomy conceals substantive disagreement regarding evidential reliability."
    quote_candidate: "In particular, since collaborative systems use other users’ recommendations (ratings), they can deal with any kind of content and recommend any items, even the ones that are dissimilar to those seen in the past."
    secondary_score: 48.36601307189542
    secondary_quote: "discussed above, recommender systems can be categorized as being 1) content-based, collaborative,o r hybrid, based on the recommendation approach used, and 2) heuristic-based or model-based, based on the types of recommendation techni- ques used for the rating estimation."
  - claim_3_status: weak_support
    score: 49.46236559139785
    claim: "Collaborative filtering estimates relevance from user-item interaction patterns and often achieves strong performance when behavioural matrices are dense (Adomavicius and Tuzhilin, 2005)."
    quote_candidate: "A statistical model for collaborative filtering was proposed in [105], and several different algorithms for estimating the model parameters were compared, including K-means clustering and Gibbs sampling."
    secondary_score: 49.282296650717704
    secondary_quote: "Extrapolations from known to unknown ratings are usually done by 1) specifying heuristics that define the utility function and empirically validating its performance and 2) estimating the utility function that optimizes certain performance criterion, such as the mean square error."
  - claim_4_status: weak_support
    score: 43.888888888888886
    claim: "Aggregating interaction history can stabilise noise, but it also encodes assumptions about recency, repetition, and signal reliability (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022)."
    quote_candidate: ";d n and also includes inter- action effects among these dimensions (i.e., interaction effects, as defined by matrixfxijg in (15), should be extended to include other dimensions)."
    secondary_score: 43.47826086956522
    secondary_quote: "In addition, [43] argued that the inclusion of the knowledge about the user’s task into the recommendation algorithm in certain applications can lead to better recommendations."

## afroogh_trust_2024
- title: Trust in AI: progress, challenges, and future directions
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\428\Afroogh et al. - 2024 - Trust in AI progress, challenges, and future directions.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.51020408163265
    claim: "Broader AI trust literature similarly reinforces that user and application context shape trust outcomes (Afroogh et al., 2024)."
    quote_candidate: "Transparency is one of the fundamental ethical principles in creating trust in users toward AI decisions (Lockey et al., 2021)."
    secondary_score: 54.47761194029851
    secondary_quote: "It was shown that the humanness of AI applications is an important basis for trusting bonds in human –machine interactions (Troshani et al., 2021)."

## andjelkovic_moodplay_2019
- title: Moodplay: Interactive music recommendation based on Artists' mood similarity
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 49.14004914004914
    claim: "Explicit user-correction mechanisms — including influence track injection (Jin et al., 2020) and mood-based interactive filtering (Andjelkovic et al., 2019) — are proposed as pathways to introduce user-steerable profile adjustment signals."
    quote_candidate: "Building on these aspects, this paper introduces MoodPlay , an interactive music-artists recommender system which integrates content and mood-based ﬁltering in a novel interface."
    secondary_score: 47.0873786407767
    secondary_quote: "Parra et al., 2014; Verbert et al., 2013 ) demonstrate the importance of building interactive recommender interfaces, that go beyond the static- ranked list paradigm to improve user satisfaction."

## anelli_elliot_2021
- title: Elliot: A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.06741573033708
    claim: "Methodological reviews indicate that under-specified preprocessing, split logic, and software or implementation detail can undermine independent reconstruction (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "Additionally, the user can design computationally expensive prefiltering and splitting procedures that can be stored and loaded to save future computation."
    secondary_score: 44.83627204030227
    secondary_quote: "Moreover, machine learning (and recently also deep learn- ing) techniques are prominent in algorithmic research and require their hyperparameter optimization strategies and procedures [6, 92]."
  - claim_2_status: partially_supported
    score: 50.77262693156733
    claim: "Reproducibility failures in recommender research are repeatedly linked to incomplete protocol specification, hidden preprocessing steps, and dependency drift (Ferrari Dacrema et al., 2021; Bellogin and Said, 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "In Proceedings of the International Workshop on Reproducibility and Replication in Recommender Systems Evaluation, RepSys 2013, Hong Kong, China, October 12, 2013, Alejandro Bellogín, Pablo Castells, Alan Said, and Domonkos Tikk (Eds.)."
    secondary_score: 45.30120481927711
    secondary_quote: "Moreover, machine learning (and recently also deep learn- ing) techniques are prominent in algorithmic research and require their hyperparameter optimization strategies and procedures [6, 92]."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: supported
    score: 67.9245283018868
    claim: "However, methodological analyses challenge this claim by showing that reported improvements are highly sensitive to preprocessing, split design, and metric framing (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024)."
    quote_candidate: "For example, Ferrari Dacrema et al."
    secondary_score: 65.45454545454545
    secondary_quote: "[98] TOIS 2022 Ferrari Dacrema et al."
  - claim_2_status: weak_support
    score: 45.848375451263536
    claim: "The accountability-oriented critique is currently better evidenced, because documented reproducibility failures and protocol fragility are repeatedly observed across recommender evaluations (Ferrari Dacrema et al., 2021; Bauer et al., 2024), whereas many accuracy-centered claims still depend on tightly controlled benchmark assumptions."
    quote_candidate: "that work is a recommendation model, it also contributes to evaluation, because the experiments demonstrate that performance measurements may heavily depend on statistical properties of the input data, which the authors discuss in detail."
    secondary_score: 44.70938897168406
    secondary_quote: "Moreover, as our article aims to cover research that revolves around methodological issues of evaluation, we identified that a search with the keywordsreproducible or reproducibility has strong overlaps with a search for the keywordevaluation but also yields additionalhits.Similarly,usingthekeywords method ormethodology hasprovenusefultoidentify additional works."

## beel_towards_2016
- title: Towards reproducibility in recommender-systems research
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Beel et al. - 2016 - Towards reproducibility in recommender-systems research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.953216374269005
    claim: "Methodological reviews indicate that under-specified preprocessing, split logic, and software or implementation detail can undermine independent reconstruction (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "A “recommender system” is a fully functional software system that applies at least one implementation for generating recommendations."
    secondary_score: 46.96569920844327
    secondary_quote: "Apparently, one or more unidentiﬁed contextual determinants are interacting in a way that leads to different levels of effectiveness for the selected document ﬁelds (e.g."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.333333333333336
    claim: "Reproducibility failures in recommender research are repeatedly linked to incomplete protocol specification, hidden preprocessing steps, and dependency drift (Ferrari Dacrema et al., 2021; Bellogin and Said, 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "A critical analysis is necessary in order to ensure an 947 1 3 Improving accountability in recommender systems research… advance in the field, not just marginal effects based on strategic design choices (Fer - rari Dacrema et al."
    secondary_score: 50.212765957446805
    secondary_quote: "Reproducibility is a cornerstone of scientific process and is one of two critical issues to achieve progress, as identified by Kon- stan and Adomavicius (2013), and one of the priorities that should be reflected in experimental methodologies according to Ferro et al."

## bogdanov_semantic_2013
- title: Semantic audio content-based music recommendation and visualization based on user preference examples
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\409\Bogdanov et al. - 2013 - Semantic audio content-based music recommendation and visualization based on user preference example.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.11267605633803
    claim: "Content-based music studies support explicit profile representations built from interpretable descriptors (Bogdanov et al., 2013; Deldjoo et al., 2024)."
    quote_candidate: "These semantic descriptors are computed from an explicit set of music tracks deﬁned by a given user as evidence of her/his musical preferences."
    secondary_score: 49.375
    secondary_quote: "Start- ing from an explicit set of music tracks provided by the user as evidence of his/her preferences, we infer high-level semantic descriptors for each track obtaining a user model."
  - claim_2_status: weak_support
    score: 46.95259593679458
    claim: "Feature-based scoring pipelines support descriptor-level attribution of rank variation, and this can improve post-hoc inspectability of observed outputs (Bogdanov et al., 2013; Deldjoo et al., 2024)."
    quote_candidate: "As the procedure of the low-level signal analysis and the details of semantic descriptor extraction are out of the scope of this paper, we refer the interested reader to the aforecited literature on low-level features, and to ( Bogdanov et al., 2009, 2011), and references therein, for details on the SVM implementation."
    secondary_score: 46.103896103896105
    secondary_quote: "The latter hypothesis is based on similar evidence in the case of music similarity estimation ( Bogdanov et al., 2009 )."

## bonnin_automated_2015
- title: Automated Generation of Music Playlists: Survey and Experiments
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.829268292682926
    claim: "Playlist studies show that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "Another potential problem is that not all types of metadata are objective, and annotations regarding, for example, the mood or the genre of a track can be imprecise or inconsistent [Celma 2010; Lee and Cho 2011]."
    secondary_score: 45.063291139240505
    secondary_quote: "Specifying Target Characteristics for Playlists Automating the playlist generation process requires that the desired target character- istics are speciﬁed in a machine-interpretable form."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.23728813559322
    claim: "Hybrid systems are often presented as resolving the weaknesses of individual paradigms by combining complementary evidence sources (Cano and Morisio, 2017)."
    quote_candidate: "Hybrid recommender systems combine two or more recommendation strategies in differ- ent ways to beneﬁt from their complementary advantages."
    secondary_score: 51.42857142857143
    secondary_quote: "Morisio / Hybrid recommender systems: A systematic literature review 1489 The continuously growing industrial interest in the recent and promising domains of mobile and social web has been followed by a similar increase of academic interest in RSs."

## cavenaghi_systematic_2023
- title: A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Cavenaghi et al. - 2023 - A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.90419161676647
    claim: "Methodological reviews indicate that under-specified preprocessing, split logic, and software or implementation detail can undermine independent reconstruction (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "We collected a total of 60 papers and analysed them by defining a set of variables to inspect the most important aspects that enable reproducibility, such as dataset, pre-processing code, hardware specifica- tions, software dependencies, algorithm implementation, algorithm hyperparameters, and experiment code."
    secondary_score: 46.63865546218487
    secondary_quote: "However, we marked aswithout artifactstwo candidates: [76]b e c a u s et h e shared implementation only implements a simplified version of the algorithm and [67]b e c a u s e the shared repository2 did not report the implementation of the algorithm presented in the paper, but proposed a benchmark to evaluate RL algorithms applied to RSs."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.13533834586466
    claim: "Content-based recommendation in music relies on metadata, tags, lyrics, and audio descriptors, enabling interpretable feature-level modelling across multiple content layers (Deldjoo et al., 2024)."
    quote_candidate: "In contrast, leveraging the expressive power of descriptive features extracted from the audio and other multi- media signals (e.g., music video clips) can generate more informed and less trivial recommendations."
    secondary_score: 53.46534653465346
    secondary_quote: "[26] provide a survey on context-aware music recommendation and retrieval."
  - claim_2_status: partially_supported
    score: 50.40650406504065
    claim: "Content-based music studies support explicit profile representations built from interpretable descriptors (Bogdanov et al., 2013; Deldjoo et al., 2024)."
    quote_candidate: "[93] adopt AudioLIME [139] to create listenable explanations of content-based music recommenda- tions."
    secondary_score: 47.83861671469741
    secondary_quote: "This also reflects a continuum from strictly objective and numeric item descriptors (inner) to more subjective and semantically charged content data stemming from cultural practices of dealing with music (outer)."
  - claim_3_status: weak_support
    score: 45.69892473118279
    claim: "Feature-based scoring pipelines support descriptor-level attribution of rank variation, and this can improve post-hoc inspectability of observed outputs (Bogdanov et al., 2013; Deldjoo et al., 2024)."
    quote_candidate: "According to [5], extended memory-based CF and extended model- based CF are two paradigms for integrating content as side information, and this may be applied to any sort of content described by the onion model."
    secondary_score: 45.59270516717325
    secondary_quote: "We collected all resulting papers since the first edition of the RecSys conference and ISMIR, and those published between 2010 and 2020 for the other venues."

## elmagarmid_duplicate_2007
- title: Duplicate Record Detection: A Survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Elmagarmid et al. - 2007 - Duplicate Record Detection A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.524752475247524
    claim: "Entity-resolution literature supports matching pipelines that manage combinatorial search and uncertainty, with blocking and filtering explicitly formalized in later survey work (Elmagarmid et al., 2007; Papadakis et al., 2021)."
    quote_candidate: "Although blocking can substantially increase the speed of the comparison process, it can also lead to an increased number of false mismatches due to the failure of comparing records that do not agree on the blocking field."
    secondary_score: 47.432762836185816
    secondary_quote: "It can also lead to an increased number of missed matches due to errors in the blocking step that placed entries in the wrong buckets, thereby preventing them from being compared to actual matching entries."

## ferraro_automatic_2018
- title: Automatic playlist continuation using a hybrid recommender system combining features from text and audio
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ferraro et al. - 2018 - Automatic playlist continuation using a hybrid recommender system combining features from text and a.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 43.63636363636363
    claim: "Playlist studies show that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "Existing research on music recom- mender systems has considered a number of related tasks, inc lud- ing Automatic Playlist Generation (APG) and Automatic Play list Continuation (APC)."
    secondary_score: 43.47826086956522
    secondary_quote: "In order to generate new recommendations for a playlist that we want to continue, we add this incomplete playlist when tra in- ing the model to get its latent representation."

## fkih_similarity_2022
- title: Similarity measures for Collaborative Filtering-based Recommender Systems: Review and experimental comparison
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\432\Fkih - 2022 - Similarity measures for Collaborative Filtering-based Recommender Systems Review and experimental c.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.50498338870432
    claim: "Similarity functions, normalisation schemes, and thresholds are model-defining choices that reshape neighbourhood geometry and rank outcomes (Fkih, 2022)."
    quote_candidate: "To reach this purpose, we used the methodology described in the Section 2: we computed the similarity matrix, we selected the neighborhood and we predicted the missing ratings."
    secondary_score: 48.249027237354085
    secondary_quote: "This process consists of three steps: similarity computation, neighborhood selection and rating prediction."
  - claim_2_status: weak_support
    score: 48.333333333333336
    claim: "Distance functions define local structure in feature space and therefore shape neighbour selection and final rank behaviour (Fkih, 2022)."
    quote_candidate: "This process consists of three steps: similarity computation, neighborhood selection and rating prediction."
    secondary_score: 48.0
    secondary_quote: "As same as the User-based CF tech- nique, the Item-based CF process can be summarized into three steps: similarity computation, neighborhood selection and ratings prediction."

## herlocker_evaluating_2004
- title: Evaluating collaborative filtering recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Herlocker et al. - 2004 - Evaluating collaborative filtering recommender systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 45.78313253012048
    claim: "However, methodological analyses challenge this claim by showing that reported improvements are highly sensitive to preprocessing, split design, and metric framing (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024)."
    quote_candidate: "Clearly identifying the best algorithm for a given purpose has proven challenging, in part because researchers disagree on which attributes should be measured, and on which metrics should be used for each attribute."
    secondary_score: 44.66501240694789
    secondary_quote: "Once the proper tasks have been identi ﬁed, the evaluator must select a dataset to which evaluation methods can be applied, a process that will most likely be constrained by the user tasks identiﬁed."

## jin_effects_2020
- title: Effects of personal characteristics in control-oriented user interfaces for music recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\395\Jin et al. - 2020 - Effects of personal characteristics in control-oriented user interfaces for music recommender system.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 49.86449864498645
    claim: "Transparency concerns visibility of system logic, explainability concerns intelligibility of specific outputs, controllability concerns user influence over behaviour (Jin et al., 2020), and observability concerns run-level diagnostic visibility."
    quote_candidate: "(2016), we previously devised different levels of user control (low, middle, and high) associated with various components of a recommender system (Jin et al."
    secondary_score: 47.82608695652174
    secondary_quote: "2018a) and Experiment 2 (Jin et al."
  - claim_2_status: partially_supported
    score: 50.0
    claim: "Explicit user-correction mechanisms — including influence track injection (Jin et al., 2020) and mood-based interactive filtering (Andjelkovic et al., 2019) — are proposed as pathways to introduce user-steerable profile adjustment signals."
    quote_candidate: "2018), b V enn dia- grams (Andjelkovic et al."
    secondary_score: 47.916666666666664
    secondary_quote: "Based on the interactive recommendation framework proposed by Chen et al."

## knijnenburg_explaining_2012
- title: Explaining the user experience of recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\422\Knijnenburg et al. - 2012 - Explaining the user experience of recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 57.6
    claim: "(2020) report that control-oriented interfaces are associated with higher recommendation acceptance and perceived usefulness under some user-characteristic conditions, whereas usability-oriented studies suggest that explanation utility depends on user and situational characteristics (Knijnenburg et al., 2012)."
    quote_candidate: "It also includes personal and in situational characteristics that moderate these effects."
    secondary_score: 54.752851711026615
    secondary_quote: "if they perceive differences in recommendation quality for these different algorithms), and how these perceptions, together with per- sonal and situational characteristics, result in speciﬁc user experience and interac- tion with the system (e.g."

## lu_recommender_2015
- title: Recommender system application developments: A survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\383\Lu et al. - 2015 - Recommender system application developments A survey.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.12658227848101
    claim: "Foundational surveys frame recommendation as utility estimation under uncertainty rather than direct preference detection, because available evidence is partial, noisy, and context-dependent (Adomavicius and Tuzhilin, 2005; Lu et al., 2015)."
    quote_candidate: "For example, the paper by Adomavicius and Tuzhilin [3] presented an overview of content-based, collaborative ﬁltering-based, and hybrid recommendation approaches."
    secondary_score: 48.792270531400966
    secondary_quote: "In addition, users often need to be educated about the product-space, especially if they are to understand what is available and why certain options are recommended by the sales assistant."
  - claim_2_status: partially_supported
    score: 50.92838196286472
    claim: "Content-based, collaborative, and hybrid systems remain the dominant paradigm families (Adomavicius and Tuzhilin, 2005; Lu et al., 2015), yet this taxonomy conceals substantive disagreement regarding evidential reliability."
    quote_candidate: "For example, the paper by Adomavicius and Tuzhilin [3] presented an overview of content-based, collaborative ﬁltering-based, and hybrid recommendation approaches."
    secondary_score: 49.12280701754386
    secondary_quote: "In the systems developed by Garﬁnkel et al."

## papadakis_blocking_2021
- title: Blocking and Filtering Techniques for Entity Resolution: A Survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Papadakis et al. - 2021 - Blocking and Filtering Techniques for Entity Resolution A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.568627450980394
    claim: "Entity-resolution literature supports matching pipelines that manage combinatorial search and uncertainty, with blocking and filtering explicitly formalized in later survey work (Elmagarmid et al., 2007; Papadakis et al., 2021)."
    quote_candidate: "So far, though, they have been developed independently of one another: their combination and, more generally, their relation have been overlooked in the literature, with the exception of very few works (e.g., [82])."
    secondary_score: 46.3768115942029
    secondary_quote: "The task of Entity Resolu- tion (ER) is to find all matching entities within an entity collection or across two or more entity collections."

## roy_systematic_2022
- title: A systematic review and research perspective on recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\385\Roy and Dutta - 2022 - A systematic review and research perspective on recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.95522388059702
    claim: "Interaction logs such as play counts and session traces are frequently interpreted as behavioural indicators of preference, yet they remain indirect and interpretation-dependent (Roy and Dutta, 2022)."
    quote_candidate: "Latency problem The latency problem is specific to collaborative filtering approaches and occurs when new items are frequently inserted into the database."
    secondary_score: 48.0
    secondary_quote: "This hybrid incorporation of different techniques generally results in increased performance and increased accuracy in many recommender applications."
  - claim_2_status: weak_support
    score: 44.19475655430712
    claim: "Aggregating interaction history can stabilise noise, but it also encodes assumptions about recency, repetition, and signal reliability (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022)."
    quote_candidate: "Hence, this paper can demonstrate its validity and reliability as a literature review."
    secondary_score: 42.19653179190752
    secondary_quote: "The images or other third party material in this article are included in the article’s Creative Commons licence, unless indicated otherwise in a credit line to the mate- rial."

## ru_improving_2023
- title: Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Perspective
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.02549575070822
    claim: "Music4All supports reproducible multimodal experimentation through metadata, tags, lyrics, and audio-related attributes (Pegoraro Santana et al., 2020), and subsequent work shows utility in multimodal genre-related tasks (Ru et al., 2023)."
    quote_candidate: "Pandeya’s model uses both audio informa- tion and lyrics information as input and shows the state-of-art performance in multi-label MGC task."
    secondary_score: 45.22613065326633
    secondary_quote: "Considering that Music4All dataset is noisy and contains mul- tiple languages in music lyrics, we filtered out music tracks with missing information or non-English lyrics in our exper- iment."

## schweiger_impact_2025
- title: The impact of playlist characteristics on coherence in user-curated music playlists
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\rp\files\578\Schweiger et al. - 2025 - The impact of playlist characteristics on coherence in user-curated music playlists.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 44.30769230769231
    claim: "Playlist studies show that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "[8]p r o p o s e s a hybrid recommendation system that balances coherence and diversity based on given Schweigeretal."
    secondary_score: 43.42857142857143
    secondary_quote: "The remainder of the paper is structured as follows: Sect.2presents previous research on track order, coherence, and other related topics."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.131147540983605
    claim: "While result-focused reporting remains common, recent explainability work in music contexts demonstrates that feature-level mechanism explanations, showing which specific modalities and attributes drive individual outputs, provide more informative auditing than aggregate prediction scores alone (Sotirou et al., 2025)."
    quote_candidate: "Additionally, genre prediction proved more accurate than emotion prediction, which may be attributed to the inherently subjective nature of human emotions [28] on one side, but also to the distinctive features of various genres, whether in lyrics (e.g., hip hop) or audio (e.g., vocals and drums in punk music)."
    secondary_score: 51.14503816793893
    secondary_quote: "While the aforementioned approaches provide useful explanations for unimodal models, the multimodal nature of music requires an adaptation that can capture the intricate interplay between its different modalities."

## tintarev_survey_2007
- title: A Survey of Explanations in Recommender Systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\389\Tintarev and Masthoff - 2007 - A Survey of Explanations in Recommender Systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 59.701492537313435
    claim: "Explanation research has long argued that recommendation quality is multidimensional, extending beyond predictive utility to include transparency, trust, effectiveness, and scrutability (Tintarev and Masthoff, 2007, 2012)."
    quote_candidate: "transparency, user trust, as well as satisfaction."
    secondary_score: 50.95890410958904
    secondary_quote: "A system that can explain to the user in their own terms why items are recommended is likely to increase user trust, as well as system transparency and scrutability."

## vall_feature-combination_2019
- title: Feature-combination hybrid recommender systems for automated music playlist continuation
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Vall et al. - 2019 - Feature-combination hybrid recommender systems for automated music playlist continuation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 49.39467312348668
    claim: "Playlist studies show that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "2017b, 2019), and Bonnin and Jannach (2014) proposed a successful variation consisting in computing similarities between artists instead of between songs, even when the ultimate recommendations were at the song level."
    secondary_score: 45.539906103286384
    secondary_quote: "Still, playlist-neighbors CF systems require a careful implementation to efﬁciently compute the similarity between out-of-set playlists and large training playlist collections (Bon- nin and Jannach 2014, Appendix A.1)."

## zamani_analysis_2019
- title: An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Continuation
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Zamani et al. - 2019 - An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Contin.pdf
- mapping_score: 100
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 45.58404558404558
    claim: "Recommendation behaviour is strongly conditioned by pre-scoring pool composition, and playlist-continuation studies show high sensitivity to candidate handling decisions (Zamani et al., 2019)."
    quote_candidate: "These models mostly create an incomplete playlist-track matrix and use matrix fac- torization to learn a low-dimensional dense representation for each playlist and track."
    secondary_score: 44.96124031007752
    secondary_quote: "linearly combined the results produced by two dif- ferentmodels:anautoencodermodelandaconvolutionalneuralnetwork.Theautoencodermodel tries to reconstruct track lists and artist lists for each playlist."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.63157894736842
    claim: "Reproducibility failures in recommender research are repeatedly linked to incomplete protocol specification, hidden preprocessing steps, and dependency drift (Ferrari Dacrema et al., 2021; Bellogin and Said, 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "7 CONCLUSION Reproducibility is an open issue in the field of recommender sys- tems."
    secondary_score: 49.094567404426556
    secondary_quote: "The pipeline and required artifacts for open benchmarking specified in Section 3 are new to the community and allow researchers to easily expand the benchmarks to more tasks (e.g., re-ranking, sequential recommendation) and vertical scenarios (e.g., news recommenda- tion, music recommendation)."

## Summary
- total_claim_checks: 40
- supported: 1
- partially_supported: 16
- weak_support: 23
- no_match: 0