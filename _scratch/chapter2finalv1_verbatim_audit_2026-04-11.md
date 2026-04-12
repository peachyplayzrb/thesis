# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `08_writing\_versions\chapter2finalv1.md` against extracted text from mapped local PDFs.
Method note: automated lexical matching (RapidFuzz token-set ratio) with manual thresholding.

## adomavicius_toward_2005
- title: Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.66079295154185
    claim: "Foundational surveys define recommendation as utility estimation under uncertainty, rather than direct preference detection, because available evidence is partial, noisy, and context-dependent (Adomavicius and Tuzhilin, 2005; Lu et al., 2015)."
    quote_candidate: "Many real-life recommendation applications, including several business applications, such as the ones described above, are arguably more complex than a movie recommender system and would require taking more factors into the recommendation consideration."
    secondary_score: 49.26315789473684
    secondary_quote: "2.2 Collaborative Methods Unlike content-based recommendation methods, collabora- tive recommender systems (or collaborative filtering systems ) try to predict the utility of items for a particular user based on the items previously rated by other users."
  - claim_2_status: weak_support
    score: 48.157248157248155
    claim: "Content-based, collaborative, and hybrid systems constitute the primary paradigm families (Adomavicius and Tuzhilin, 2005; Lu et al., 2015), but this taxonomy masks significant disagreement about evidence reliability."
    quote_candidate: "Furthermore, among the latest developments, [109] pro- poses a probabilistic approach to collaborative filtering that constitutes yet another way to combine the memory-based and model-based techniques."
    secondary_score: 48.07692307692308
    secondary_quote: "In particular, since collaborative systems use other users’ recommendations (ratings), they can deal with any kind of content and recommend any items, even the ones that are dissimilar to those seen in the past."
  - claim_3_status: partially_supported
    score: 50.83798882681564
    claim: "Collaborative filtering estimates relevance from user-item interaction patterns and often performs well when behavioural matrices are dense (Adomavicius and Tuzhilin, 2005)."
    quote_candidate: "A statistical model for collaborative filtering was proposed in [105], and several different algorithms for estimating the model parameters were compared, including K-means clustering and Gibbs sampling."
    secondary_score: 49.35064935064935
    secondary_quote: "Collaborative rec ommendations :T h eu s e rw i l lb e recommended items that people with similar tastes and preferences liked in the past; ."
  - claim_4_status: weak_support
    score: 44.38202247191011
    claim: "Aggregating interaction history can reduce noise, yet it also embeds assumptions about recency, repetition, and signal reliability (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022)."
    quote_candidate: ";d n and also includes inter- action effects among these dimensions (i.e., interaction effects, as defined by matrixfxijg in (15), should be extended to include other dimensions)."
    secondary_score: 43.43163538873995
    secondary_quote: "For example, in a movie recommendation application, where S is a collection of movies, each movie can be represented not only by its ID, but also by its title, genre, director, year of release, leading actors, etc."

## afroogh_trust_2024
- title: Trust in AI: progress, challenges, and future directions
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\428\Afroogh et al. - 2024 - Trust in AI progress, challenges, and future directions.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.284671532846716
    claim: "Usability and trust studies (Knijnenburg et al., 2012; Afroogh et al., 2024) further show that user and application context shape outcomes."
    quote_candidate: "It was shown that the humanness of AI applications is an important basis for trusting bonds in human –machine interactions (Troshani et al., 2021)."
    secondary_score: 50.63291139240506
    secondary_quote: "Similarly, it is found that users tend to trust agents with values similar to their own (Mehrotra et al., 2021a)."

## andjelkovic_moodplay_2019
- title: Moodplay: Interactive music recommendation based on Artists' mood similarity
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.108108108108105
    claim: "Explicit user-correction mechanisms, such as influence track injection (Jin et al., 2020) and mood-based interactive filtering (Andjelkovic et al., 2019), are frequently cited as controllability support."
    quote_candidate: "Building on these aspects, this paper introduces MoodPlay , an interactive music-artists recommender system which integrates content and mood-based ﬁltering in a novel interface."
    secondary_score: 47.216035634743875
    secondary_quote: "Well established algorithms, such as Collaborative Filter- ing ( Ekstrand et al., 2011 ), Content-Based Filtering ( Pazzani and Bill- sus, 2007 ) and Matrix Factorization ( Koren et al., 2009 ), are used across a variety of domains to recommend digital content or merchandise."

## anelli_elliot_2021
- title: Elliot: A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 45.562130177514796
    claim: "Methodological reviews show that under-specified preprocessing, split logic, and implementation details can hinder independent reconstruction (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "Additionally, the user can design computationally expensive prefiltering and splitting procedures that can be stored and loaded to save future computation."
    secondary_score: 45.333333333333336
    secondary_quote: "The first section details the data loading, filter- ing, and splitting information as defined in Section 3.1."
  - claim_2_status: partially_supported
    score: 50.328227571115974
    claim: "Reproducibility failures in recommender research are frequently attributed to incomplete protocol specification, hidden preprocessing steps, and dependency drift (Ferrari Dacrema et al., 2021; Bellogin and Said, 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "In Proceedings of the International Workshop on Reproducibility and Replication in Recommender Systems Evaluation, RepSys 2013, Hong Kong, China, October 12, 2013, Alejandro Bellogín, Pablo Castells, Alan Said, and Domonkos Tikk (Eds.)."
    secondary_score: 45.146726862302486
    secondary_quote: "3.2 Recommendation Models After data loading and pre-elaborations,Recommendation module (Figure 1) provides the functionalities to train (and restore) theElliot recommendation models and the new ones integrated by users."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: supported
    score: 67.9245283018868
    claim: "Methodological analyses challenge this by showing that reported improvements are highly sensitive to preprocessing choices, data-splitting designs, and metric selection (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024)."
    quote_candidate: "For example, Ferrari Dacrema et al."
    secondary_score: 65.45454545454545
    secondary_quote: "[98] TOIS 2022 Ferrari Dacrema et al."

## beel_towards_2016
- title: Towards reproducibility in recommender-systems research
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Beel et al. - 2016 - Towards reproducibility in recommender-systems research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.10126582278481
    claim: "Methodological reviews show that under-specified preprocessing, split logic, and implementation details can hinder independent reconstruction (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "(2011b) believe that variations in algorithms and implementations are a major reason for results being difﬁcult to reproduce."
    secondary_score: 45.91029023746702
    secondary_quote: "In 2013, Plista hosted the RecSys News Challenge where participating teams received recommendation requests from Plista, including information about the current users and potential recommendation candidates."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.30396475770925
    claim: "Reproducibility failures in recommender research are frequently attributed to incomplete protocol specification, hidden preprocessing steps, and dependency drift (Ferrari Dacrema et al., 2021; Bellogin and Said, 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "A critical analysis is necessary in order to ensure an 947 1 3 Improving accountability in recommender systems research… advance in the field, not just marginal effects based on strategic design choices (Fer - rari Dacrema et al."
    secondary_score: 49.78902953586498
    secondary_quote: "Reproducibility is a cornerstone of scientific process and is one of two critical issues to achieve progress, as identified by Kon- stan and Adomavicius (2013), and one of the priorities that should be reflected in experimental methodologies according to Ferro et al."

## bogdanov_semantic_2013
- title: Semantic audio content-based music recommendation and visualization based on user preference examples
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\409\Bogdanov et al. - 2013 - Semantic audio content-based music recommendation and visualization based on user preference example.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.075268817204304
    claim: "Content-based music recommendation relies on metadata, tags, lyrics, and audio descriptors, enabling interpretable feature-level modelling across multiple content layers (Deldjoo et al., 2024; Bogdanov et al., 2013)."
    quote_candidate: "Moreover, current systems also provide basic means for music recommendation and personalization, which are not re- lated to the audio content, i.e., using metadata."
    secondary_score: 49.865951742627345
    secondary_quote: "Related work in music recommendation In this section we review the most important studies in music recommendation, considering both audio content-based and hybrid approaches."
  - claim_2_status: partially_supported
    score: 52.11267605633803
    claim: "Content-based music studies support explicit profile representations built from interpretable descriptors (Bogdanov et al., 2013; Deldjoo et al., 2024)."
    quote_candidate: "These semantic descriptors are computed from an explicit set of music tracks deﬁned by a given user as evidence of her/his musical preferences."
    secondary_score: 49.375
    secondary_quote: "Start- ing from an explicit set of music tracks provided by the user as evidence of his/her preferences, we infer high-level semantic descriptors for each track obtaining a user model."
  - claim_3_status: partially_supported
    score: 50.19607843137255
    claim: "Feature-based scoring pipelines support descriptor-level attribution of rank variation (Bogdanov et al., 2013; Deldjoo et al., 2024), but descriptor transparency does not guarantee behavioural adequacy when contextual and affective factors are weakly represented."
    quote_candidate: "As the procedure of the low-level signal analysis and the details of semantic descriptor extraction are out of the scope of this paper, we refer the interested reader to the aforecited literature on low-level features, and to ( Bogdanov et al., 2009, 2011), and references therein, for details on the SVM implementation."
    secondary_score: 48.34710743801653
    secondary_quote: "In turn, implicit listening behavior statistics based on track counts might not represent real preferences in particular since it ignores the difference between track durations or users’ activities when listening the music ( Jawaheer et al., 2010 )."

## bonnin_automated_2015
- title: Automated Generation of Music Playlists: Survey and Experiments
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.85990338164251
    claim: "Playlist studies indicate that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "Another potential problem is that not all types of metadata are objective, and annotations regarding, for example, the mood or the genre of a track can be imprecise or inconsistent [Celma 2010; Lee and Cho 2011]."
    secondary_score: 45.11278195488722
    secondary_quote: "Specifying Target Characteristics for Playlists Automating the playlist generation process requires that the desired target character- istics are speciﬁed in a machine-interpretable form."
  - claim_2_status: weak_support
    score: 46.85990338164251
    claim: "Playlist studies indicate that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "Another potential problem is that not all types of metadata are objective, and annotations regarding, for example, the mood or the genre of a track can be imprecise or inconsistent [Celma 2010; Lee and Cho 2011]."
    secondary_score: 45.11278195488722
    secondary_quote: "Specifying Target Characteristics for Playlists Automating the playlist generation process requires that the desired target character- istics are speciﬁed in a machine-interpretable form."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 58.18181818181818
    claim: "Hybrid systems are frequently presented as remedies for weaknesses in single-paradigm approaches (Cano and Morisio, 2017), primarily as a performance remedy that improves aggregate predictive metrics through combined signal sources."
    quote_candidate: "The most frequent are presented in Fig."
    secondary_score: 50.99009900990099
    secondary_quote: "Morisio / Hybrid recommender systems: A systematic literature review the extracted information was stored in Nvivo3 which was used to manage data extraction and synthesis process."

## cavenaghi_systematic_2023
- title: A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Cavenaghi et al. - 2023 - A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 45.851528384279476
    claim: "Methodological reviews show that under-specified preprocessing, split logic, and implementation details can hinder independent reconstruction (Beel et al., 2016; Anelli et al., 2021; Cavenaghi et al., 2023)."
    quote_candidate: "However, we marked aswithout artifactstwo candidates: [76]b e c a u s et h e shared implementation only implements a simplified version of the algorithm and [67]b e c a u s e the shared repository2 did not report the implementation of the algorithm presented in the paper, but proposed a benchmark to evaluate RL algorithms applied to RSs."
    secondary_score: 44.270833333333336
    secondary_quote: "Leveraging the user model as a simulator, they develop a newCascading Deep Q-Network (DQN) algorithm to obtain a rec- ommendation policy that can efficiently handle a large number of candidate items."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.46534653465346
    claim: "Content-based music recommendation relies on metadata, tags, lyrics, and audio descriptors, enabling interpretable feature-level modelling across multiple content layers (Deldjoo et al., 2024; Bogdanov et al., 2013)."
    quote_candidate: "[26] provide a survey on context-aware music recommendation and retrieval."
    secondary_score: 53.04136253041362
    secondary_quote: "In contrast, leveraging the expressive power of descriptive features extracted from the audio and other multi- media signals (e.g., music video clips) can generate more informed and less trivial recommendations."
  - claim_2_status: partially_supported
    score: 50.40650406504065
    claim: "Content-based music studies support explicit profile representations built from interpretable descriptors (Bogdanov et al., 2013; Deldjoo et al., 2024)."
    quote_candidate: "[93] adopt AudioLIME [139] to create listenable explanations of content-based music recommenda- tions."
    secondary_score: 47.83861671469741
    secondary_quote: "This also reflects a continuum from strictly objective and numeric item descriptors (inner) to more subjective and semantically charged content data stemming from cultural practices of dealing with music (outer)."
  - claim_3_status: weak_support
    score: 47.201946472019465
    claim: "Feature-based scoring pipelines support descriptor-level attribution of rank variation (Bogdanov et al., 2013; Deldjoo et al., 2024), but descriptor transparency does not guarantee behavioural adequacy when contextual and affective factors are weakly represented."
    quote_candidate: "Here, we organize our review according to the major categories of context factors we identified in the relevant literature: spatial context , affective context , and social context."
    secondary_score: 46.08294930875576
    secondary_quote: "While we notice a certain level of vagueness and ambiguity when it comes to an exact terminology of such aspects, most often they can be categorized into transparency and explainability."

## elmagarmid_duplicate_2007
- title: Duplicate Record Detection: A Survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Elmagarmid et al. - 2007 - Duplicate Record Detection A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.88279301745636
    claim: "Entity-resolution literature supports matching pipelines that address combinatorial search and uncertainty, with blocking and filtering explicitly formalised in later surveys (Elmagarmid et al., 2007; Papadakis et al., 2021)."
    quote_candidate: "Although blocking can substantially increase the speed of the comparison process, it can also lead to an increased number of false mismatches due to the failure of comparing records that do not agree on the blocking field."
    secondary_score: 46.79802955665025
    secondary_quote: "It can also lead to an increased number of missed matches due to errors in the blocking step that placed entries in the wrong buckets, thereby preventing them from being compared to actual matching entries."

## ferraro_automatic_2018
- title: Automatic playlist continuation using a hybrid recommender system combining features from text and audio
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ferraro et al. - 2018 - Automatic playlist continuation using a hybrid recommender system combining features from text and a.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 45.09283819628647
    claim: "Playlist studies indicate that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "It is important to note that these results are not the same as t he ﬁnal scores published on July 13th, 2018, as they are only cal cu- lated using 50% of the Challenge Set."
    secondary_score: 44.086021505376344
    secondary_quote: "In order to generate new recommendations for a playlist that we want to continue, we add this incomplete playlist when tra in- ing the model to get its latent representation."
  - claim_2_status: weak_support
    score: 45.09283819628647
    claim: "Playlist studies indicate that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "It is important to note that these results are not the same as t he ﬁnal scores published on July 13th, 2018, as they are only cal cu- lated using 50% of the Challenge Set."
    secondary_score: 44.086021505376344
    secondary_quote: "In order to generate new recommendations for a playlist that we want to continue, we add this incomplete playlist when tra in- ing the model to get its latent representation."

## herlocker_evaluating_2004
- title: Evaluating collaborative filtering recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Herlocker et al. - 2004 - Evaluating collaborative filtering recommender systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.661800486618006
    claim: "Methodological analyses challenge this by showing that reported improvements are highly sensitive to preprocessing choices, data-splitting designs, and metric selection (Herlocker et al., 2004; Ferrari Dacrema et al., 2021; Bauer et al., 2024)."
    quote_candidate: "In such an evaluation, the algorithm is used to predict certain withheld values from a dataset, and the results are analyzed using one or more of the metrics dis- cussed in the following section."
    secondary_score: 46.48910411622276
    secondary_quote: "Thus, Section 2 describes the selec- tion of appropriate user tasks, Section 3 discusses the selection of a dataset, and Sections 4 and 5 discuss the alternative metrics that may be applied to the dataset chosen."

## jin_effects_2020
- title: Effects of personal characteristics in control-oriented user interfaces for music recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\395\Jin et al. - 2020 - Effects of personal characteristics in control-oriented user interfaces for music recommender system.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.94736842105263
    claim: "Transparency is typically framed as visibility of system logic, explainability as intelligibility of specific outputs, and controllability as user influence over behaviour (Jin et al., 2020)."
    quote_candidate: "For example, when investigating inter- active user interfaces, users’ experience may be seen as their level of familiarity with computers (Zhang and Chignell 2001) or with visualizations (Carenini et al."
    secondary_score: 48.80952380952381
    secondary_quote: "(2016), we previously devised different levels of user control (low, middle, and high) associated with various components of a recommender system (Jin et al."
  - claim_2_status: partially_supported
    score: 51.239669421487605
    claim: "Explicit user-correction mechanisms, such as influence track injection (Jin et al., 2020) and mood-based interactive filtering (Andjelkovic et al., 2019), are frequently cited as controllability support."
    quote_candidate: "Previous research has shown many beneﬁts for supporting controllability and trans- parency in several application domains such as music recommendations (Bostandjiev et al."
    secondary_score: 50.0
    secondary_quote: "2018), b V enn dia- grams (Andjelkovic et al."

## knijnenburg_explaining_2012
- title: Explaining the user experience of recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\422\Knijnenburg et al. - 2012 - Explaining the user experience of recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 46.728971962616825
    claim: "Usability and trust studies (Knijnenburg et al., 2012; Afroogh et al., 2024) further show that user and application context shape outcomes."
    quote_candidate: "In a music recommender experiment, Hu and Pu (2010) show that expert users perceive 123"
    secondary_score: 46.20938628158845
    secondary_quote: "An essential aspect of any recommender system is the algorithm that provides per- sonalized recommendations based on the user’s preferences ( Burke 2002)."

## lu_recommender_2015
- title: Recommender system application developments: A survey
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\383\Lu et al. - 2015 - Recommender system application developments A survey.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 49.87405541561713
    claim: "Foundational surveys define recommendation as utility estimation under uncertainty, rather than direct preference detection, because available evidence is partial, noisy, and context-dependent (Adomavicius and Tuzhilin, 2005; Lu et al., 2015)."
    quote_candidate: "For example, the paper by Adomavicius and Tuzhilin [3] presented an overview of content-based, collaborative ﬁltering-based, and hybrid recommendation approaches."
    secondary_score: 49.074074074074076
    secondary_quote: "[9] used fuzzy set techniques to deal with linguistic ratings and calculate the fuzzy CF sim- ilarities, to provide a solution for handling uncertainty in a telecom product/service recommendation process."
  - claim_2_status: partially_supported
    score: 52.2911051212938
    claim: "Content-based, collaborative, and hybrid systems constitute the primary paradigm families (Adomavicius and Tuzhilin, 2005; Lu et al., 2015), but this taxonomy masks significant disagreement about evidence reliability."
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
    score: 47.953216374269005
    claim: "Entity-resolution literature supports matching pipelines that address combinatorial search and uncertainty, with blocking and filtering explicitly formalised in later surveys (Elmagarmid et al., 2007; Papadakis et al., 2021)."
    quote_candidate: "The task of Entity Resolu- tion (ER) is to find all matching entities within an entity collection or across two or more entity collections."
    secondary_score: 45.97701149425287
    secondary_quote: "Entities sharing the same output for a particular blocking predicate are considered candidate matches (i.e., hash-based functionality)."

## roy_systematic_2022
- title: A systematic review and research perspective on recommender systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\385\Roy and Dutta - 2022 - A systematic review and research perspective on recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.297213622291025
    claim: "Interaction logs, such as play counts and session traces, are commonly interpreted as behavioural indicators of preference, but they remain indirect and open to interpretation (Roy and Dutta, 2022)."
    quote_candidate: "In this era of big data, more and more items and users are rapidly getting added to the system and this problem is becoming common in recommender systems."
    secondary_score: 47.901234567901234
    secondary_quote: "[1 ] developed a “NEuro-fuzzy WEb Recommendation (NEWER)” system for exploiting the possibility of combining computational intel - ligence and user preference for suggesting interesting web pages to the user in a dynamic environment."
  - claim_2_status: weak_support
    score: 47.36842105263158
    claim: "Aggregating interaction history can reduce noise, yet it also embeds assumptions about recency, repetition, and signal reliability (Adomavicius and Tuzhilin, 2005; Roy and Dutta, 2022)."
    quote_candidate: "Shilling attacks greatly reduce the reliability of the system."
    secondary_score: 44.106463878327
    secondary_quote: "Hence, this paper can demonstrate its validity and reliability as a literature review."

## ru_improving_2023
- title: Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Perspective
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.31043256997455
    claim: "Music4All enables reproducible multimodal experimentation using metadata, tags, lyrics, and audio-related attributes (Pegoraro Santana et al., 2020), and later studies show utility for multimodal genre-related tasks (Ru et al., 2023)."
    quote_candidate: "Considering that Music4All dataset is noisy and contains mul- tiple languages in music lyrics, we filtered out music tracks with missing information or non-English lyrics in our exper- iment."
    secondary_score: 46.19164619164619
    secondary_quote: "Music Representation Learning Module The music representation learning module consists of an audio encoder and a lyrics encoder, which takes audio and lyrics as input and outputs corresponding features respec- tively."

## schweiger_impact_2025
- title: The impact of playlist characteristics on coherence in user-curated music playlists
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\rp\files\578\Schweiger et al. - 2025 - The impact of playlist characteristics on coherence in user-curated music playlists.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.601941747572816
    claim: "Playlist studies indicate that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "User studies [2, 4] indicate that coherence is perceived as an impor- tant quality criterion."
    secondary_score: 43.683083511777305
    secondary_quote: "3) Proposals for automatic playlist generation (APG) and continuation (APC) that use sequential or order-aware models, thereby indirectly claiming that track order (and coherence) are important cri- teria.4)Researchanalyzingdatasetsforevidence ofcoherence."
  - claim_2_status: weak_support
    score: 46.601941747572816
    claim: "Playlist studies indicate that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "User studies [2, 4] indicate that coherence is perceived as an impor- tant quality criterion."
    secondary_score: 43.683083511777305
    secondary_quote: "3) Proposals for automatic playlist generation (APG) and continuation (APC) that use sequential or order-aware models, thereby indirectly claiming that track order (and coherence) are important cri- teria.4)Researchanalyzingdatasetsforevidence ofcoherence."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.270207852194
    claim: "Recent music explainability work also indicates that feature-level mechanism explanations can provide clearer accounts of which attributes influence specific outputs than aggregate prediction scores alone (Sotirou et al., 2025)."
    quote_candidate: "While the aforementioned approaches provide useful explanations for unimodal models, the multimodal nature of music requires an adaptation that can capture the intricate interplay between its different modalities."
    secondary_score: 51.10663983903421
    secondary_quote: "The language model showed limited accuracy in predicting emotions but performed really well at identifying specific genres, such as hip hop and heavy music , likely due to recurring thematic elements in the lyrics, as further elucidated by our explanations (see Figures 2 and 3)."

## tintarev_survey_2007
- title: A Survey of Explanations in Recommender Systems
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\389\Tintarev and Masthoff - 2007 - A Survey of Explanations in Recommender Systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 59.701492537313435
    claim: "Explanation research has consistently argued that recommendation quality is multidimensional, encompassing transparency, trust, effectiveness, and scrutability alongside predictive utility (Tintarev and Masthoff, 2007, 2012)."
    quote_candidate: "transparency, user trust, as well as satisfaction."
    secondary_score: 48.91304347826087
    secondary_quote: "A system that can explain to the user in their own terms why items are recommended is likely to increase user trust, as well as system transparency and scrutability."

## vall_feature-combination_2019
- title: Feature-combination hybrid recommender systems for automated music playlist continuation
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Vall et al. - 2019 - Feature-combination hybrid recommender systems for automated music playlist continuation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.44124700239808
    claim: "Playlist studies indicate that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "2017b, 2019), and Bonnin and Jannach (2014) proposed a successful variation consisting in computing similarities between artists instead of between songs, even when the ultimate recommendations were at the song level."
    secondary_score: 45.933014354066984
    secondary_quote: "2 Even though the process of listening to a playlist is inherently sequential, we found that considering the song order in curated music playlists is actually not crucial to extend such playlists (V all et al.2018b, 2019)."
  - claim_2_status: weak_support
    score: 48.44124700239808
    claim: "Playlist studies indicate that coherence, diversity, novelty, and order operate as competing objectives rather than jointly maximisable targets (Ferraro et al., 2018; Vall et al., 2019; Bonnin and Jannach, 2015; Schweiger et al., 2025)."
    quote_candidate: "2017b, 2019), and Bonnin and Jannach (2014) proposed a successful variation consisting in computing similarities between artists instead of between songs, even when the ultimate recommendations were at the song level."
    secondary_score: 45.933014354066984
    secondary_quote: "2 Even though the process of listening to a playlist is inherently sequential, we found that considering the song order in curated music playlists is actually not crucial to extend such playlists (V all et al.2018b, 2019)."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\peach\Desktop\thesis-main (3)\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.63157894736842
    claim: "Reproducibility failures in recommender research are frequently attributed to incomplete protocol specification, hidden preprocessing steps, and dependency drift (Ferrari Dacrema et al., 2021; Bellogin and Said, 2021; Zhu et al., 2022; Anelli et al., 2021)."
    quote_candidate: "7 CONCLUSION Reproducibility is an open issue in the field of recommender sys- tems."
    secondary_score: 46.30738522954092
    secondary_quote: "The pipeline and required artifacts for open benchmarking specified in Section 3 are new to the community and allow researchers to easily expand the benchmarks to more tasks (e.g., re-ranking, sequential recommendation) and vertical scenarios (e.g., news recommenda- tion, music recommendation)."

## Summary
- total_claim_checks: 41
- supported: 1
- partially_supported: 16
- weak_support: 24
- no_match: 0