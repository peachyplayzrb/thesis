# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `thesis-main\08_writing\chapter2_draft_v10.md` against extracted text from mapped local PDFs.
Method note: automated lexical matching (RapidFuzz token-set ratio) with manual thresholding.

## adomavicius_toward_2005
- title: Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\381\Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.71024734982332
    claim: "Recommender systems emerged as a practical response to this information-overload problem by helping users discover items they are likely to value ."
    quote_candidate: "In its most common formulation, the recommendation problem is reduced to the problem of estimating ratings for the items that have not been seen by a user."
    secondary_score: 53.70843989769821
    secondary_quote: "The interest in this area still remains high because it constitutes a problem-rich research area and because of the abundance of practical applications that help users to deal with information overload and provide personalized recommendations, content, and services to them."
  - claim_2_status: partially_supported
    score: 54.178674351585016
    claim: "Foundational recommender research frames this task as utility estimation under partial information: infer likely value from sparse and incomplete evidence rather than retrieve a fully known answer ."
    quote_candidate: "Intuitively, this estimation is usually based on the ratings given by this user to other items and on some other information that will be formally described below."
    secondary_score: 53.58090185676392
    secondary_quote: "That is, they make their recommendations based only on the user and item information and do not take into consideration additional contextual information that may be crucial in some applications."
  - claim_3_status: partially_supported
    score: 53.84615384615385
    claim: "Preference evidence in recommender systems may be explicit, such as ratings or likes, or implicit, such as clicks, playback history, or other behavioural traces ."
    quote_candidate: "Note that different recommender systems may take different approaches in order to imple- ment the user similarity calculations and rating estimations as efficiently as possible."
    secondary_score: 53.003533568904594
    secondary_quote: "3.4 Multcriteria Ratings Most of the current recommender systems deal with single- criterion ratings, such as ratings of movies and books."
  - claim_4_status: supported
    score: 83.13253012048193
    claim: "Recommender systems are commonly grouped into content-based, collaborative, and hybrid families ."
    quote_candidate: "Toward the Next Generation of Recommender Systems: A Survey of the State-of-the-Art and Possible Extensions Gediminas Adomavicius, Member , IEEE, and Alexander Tuzhilin, Member , IEEE Abstract—This paper presents an overview of the field of recommender systems and describes the current generation of recommendation methods that are usually classified into the following three main categories: content-based, collaborative, and hybrid recommendation approaches."
    secondary_score: 66.66666666666666
    secondary_quote: "Different ways to combine collaborative and content-based methods into a hybrid recommender system can be classified as follows: 1."
  - claim_5_status: partially_supported
    score: 51.038575667655785
    claim: "They can perform strongly at scale with rich histories, but direct interpretability may weaken when ranking logic is encoded in latent relationships rather than explicit feature comparisons ."
    quote_candidate: "One problem with using the weighted sum, as in (10b), is that it does not take into account the fact that different users may use the rating scale differently."
    secondary_score: 50.520833333333336
    secondary_quote: "For example, in a movie recommendation application, prefer- ence-based filtering techniques would focus on predicting the correct relative order of the movies, rather than their individual ratings."
  - claim_6_status: partially_supported
    score: 50.467289719626166
    claim: "Listening history provides implicit preference evidence rather than a fully specified user statement ."
    quote_candidate: "More formally, let ContentBasedP rofileðcÞ be the profile of user c containing tastes and preferences of this user."
    secondary_score: 50.0
    secondary_quote: "However, nonintrusive ratings (such as time spent reading an article) are often inaccurate and cannot fully replace explicit ratings provided by the user."

## afroogh_trust_2024
- title: Trust in AI: progress, challenges, and future directions
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\428\Afroogh et al. - 2024 - Trust in AI progress, challenges, and future directions.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.760330578512395
    claim: "Interface research adds an additional constraint: faithful explanations must still be understandable to non-experts ."
    quote_candidate: "Nevertheless, humans are still preferred to advise customers concerning complex ﬁnancial products such as equity derivatives."
    secondary_score: 48.4304932735426
    secondary_quote: "Another example of the role of trust as a driving factor for technology adoption is found in the ﬁnancial sector."

## allam_improved_2018
- title: Improved suffix blocking for record linkage and entity resolution
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Allam et al. - 2018 - Improved suffix blocking for record linkage and entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.47445255474452
    claim: "Entity-resolution research usually handles this with blocking and filtering to narrow the candidate set, followed by staged matching and refinement ."
    quote_candidate: "We start by considering the non-incremental variation of record linkage and present a su ﬃ x-based blocking method for this task."
    secondary_score: 52.38095238095238
    secondary_quote: "Given a dataset D, let L be the set of actual linked record pairs in D and let R be the set of record pairs that result in by the blocking stage."

## andjelkovic_moodplay_2019
- title: Moodplay: Interactive music recommendation based on Artists' mood similarity
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.943396226415096
    claim: "This matches the thesis assumption that influence tracks can complement imported history, and it aligns with controllability literature that treats user influence as useful when it is explicit, bounded, and testable rather than unconstrained ."
    quote_candidate: "3 , it has two main components: one for building the library of items with their metadata ( Dataset Con- struction ) and a second component that generates user recommendations ( Recommendation Framework )."
    secondary_score: 50.53191489361702
    secondary_quote: "In this investigation, we also explored whether there is a connection between users’ self- reported and the aﬀective proﬁle of the music that they listened to."

## anelli_elliot_2021
- title: Elliot: A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.55555555555556
    claim: "Recommender outcomes vary with protocol definitions, preprocessing decisions, and metric framing, so strong benchmark performance under one setup does not automatically make a method the best choice for a project whose main contribution is inspectable engineering ."
    quote_candidate: "Bias in Search and Recommender Systems."
    secondary_score: 50.79365079365079
    secondary_quote: "Recommender systems with social regularization."
  - claim_2_status: partially_supported
    score: 52.11267605633803
    claim: "If it claims observability and reproducibility, runs should be documented through recorded configuration and stage-level diagnostics ."
    quote_candidate: "Elliot is a comprehensive recommendation framework that aims to run and reproduce an entire experimental pipeline by processing a simple configuration file."
    secondary_score: 51.76470588235294
    secondary_quote: "It requires the user just to compile a flexible configuration file to conduct a rigorous and reproducible experimental evaluation."
  - claim_3_status: partially_supported
    score: 50.77399380804953
    claim: "Recommender-system literature repeatedly reports weak reproducibility when split definitions, preprocessing, dependencies, and configuration states are under-specified ."
    quote_candidate: "Elliot is a comprehensive recommendation framework that aims to run and reproduce an entire experimental pipeline by processing a simple configuration file."
    secondary_score: 48.97959183673469
    secondary_quote: "It requires the user just to compile a flexible configuration file to conduct a rigorous and reproducible experimental evaluation."

## balog_transparent_2019
- title: Transparent, Scrutable and Explainable User Models for Personalized Recommendation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\397\Balog et al. - 2019 - Transparent, Scrutable and Explainable User Models for Personalized Recommendation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.306748466257666
    claim: "Controllability means user influence through explicit inputs or parameters ."
    quote_candidate: "That is, the user can explicitly state a positive or negative preference for a given tag."
    secondary_score: 46.715328467153284
    secondary_quote: "” We refer to Table 1 for the notation used throughout the paper."

## barlaug_neural_2021
- title: Neural Networks for Entity Matching: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Barlaug and Gulla - 2021 - Neural Networks for Entity Matching A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.716981132075475
    claim: "Much of the alignment support is cross-domain rather than music-benchmark specific, and neural entity matching remains a relevant comparator for difficult cases ."
    quote_candidate: "We also discuss contributions from deep learning in entity matching compared to traditional methods, and propose a taxonomy of deep neural networks for entity matching."
    secondary_score: 53.02593659942363
    secondary_quote: "While earlier works mention or cover neural networks for entity matching to various degrees, we are to the best of our knowledge the first to present a dedicated, complete, and up-to-date survey."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.84615384615385
    claim: "Recommender outcomes vary with protocol definitions, preprocessing decisions, and metric framing, so strong benchmark performance under one setup does not automatically make a method the best choice for a project whose main contribution is inspectable engineering ."
    quote_candidate: "While the core contribution of ACM Transactions on Recommender Systems, Vol."
    secondary_score: 52.03252032520325
    secondary_quote: "(d) The paper does not make a contribution regarding the evaluation of recommender systems."

## beel_towards_2016
- title: Towards reproducibility in recommender-systems research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Beel et al. - 2016 - Towards reproducibility in recommender-systems research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.28185328185328
    claim: "If it claims observability and reproducibility, runs should be documented through recorded configuration and stage-level diagnostics ."
    quote_candidate: "and believe that ensuring reproducibility in recommender-system research is crucial, and should receive more attention in the community."
    secondary_score: 49.14675767918089
    secondary_quote: "However, while many of the ﬁndings in these papers are important with respect to reproducibility, the authors did not mention or discuss their ﬁndings in the context of reproducibility."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.79282868525896
    claim: "If it claims observability and reproducibility, runs should be documented through recorded configuration and stage-level diagnostics ."
    quote_candidate: "Starting with reproducibility and replicability, we want to bring attention to the fact that these terms are often confused."
    secondary_score: 50.87719298245614
    secondary_quote: "This is directly connected to the concepts of reproducibility and replicability mentioned earlier."
  - claim_2_status: partially_supported
    score: 53.495440729483285
    claim: "Recommender-system literature repeatedly reports weak reproducibility when split definitions, preprocessing, dependencies, and configuration states are under-specified ."
    quote_candidate: "First, we revise the previously mentioned concepts (i.e., reproducibility, accountability, transparency) and their definitions for Recommender Systems research."
    secondary_score: 52.14521452145215
    secondary_quote: "Based on the definitions of those concepts, we propose to improve accountability of Recommender Systems research through reproducibility."

## betello_reproducible_2025
- title: A Reproducible Analysis of Sequential Recommender Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Betello et al. - 2025 - A Reproducible Analysis of Sequential Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Recommender-system literature repeatedly reports weak reproducibility when split definitions, preprocessing, dependencies, and configuration states are under-specified ."
    quote_candidate: "We present EasyRec, a novel library dedicated to Sequen- tial Recommender Systems (SRSs), designed to simplify data preprocessing and streamline model implementation."
    secondary_score: 48.84488448844885
    secondary_quote: "Existing works exhibit shortcomings in reproducibility and replicability of results, leading to inconsistent statements across papers."

## binette_almost_2022
- title: (Almost) all of entity resolution
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Binette and Steorts - 2022 - (Almost) all of entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.71339563862929
    claim: "Entity-resolution research usually handles this with blocking and filtering to narrow the candidate set, followed by staged matching and refinement ."
    quote_candidate: "Deduplication is thus needed to obtain an accurate enumeration, with new methodology from the machine learning and statistical literature being recently proposed to this end (48)."
    secondary_score: 51.52542372881356
    secondary_quote: "While this increases the computational speed, uncertainty cannot be propagated exactly from the blocking stage to the entity resolution stage, as shown in Eq."

## bogdanov_semantic_2013
- title: Semantic audio content-based music recommendation and visualization based on user preference examples
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\409\Bogdanov et al. - 2013 - Semantic audio content-based music recommendation and visualization based on user preference example.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 56.29139072847682
    claim: "Their main relevance here is mechanism visibility: when ranking depends on explicit features, the rationale for recommendation can often be traced back to those same features ."
    quote_candidate: "Therefore, we recoded the user’s ratings into 3 main categories, referring to the type of the recommendation: hits, fails, and trusts."
    secondary_score: 55.45171339563863
    secondary_quote: "In contrast to the proposed semantic methods, these algo- rithms use the same procedure for recommendation but operate on low-level timbral features."
  - claim_2_status: partially_supported
    score: 62.33766233766234
    claim: "show that user preference representations can be built from explicit preference examples using semantic audio descriptors ."
    quote_candidate: "With the described procedure we obtain 62 semantic descriptors, shown in Table 1, for each track in the user’s preference set."
    secondary_score: 60.633484162895925
    secondary_quote: "We describe the underlying procedure of gathering user preference examples and the process of descriptor extraction."
  - claim_3_status: partially_supported
    score: 54.09252669039146
    claim: "The semantic gap sharpens that limitation: low-level descriptors do not fully capture human concepts such as mood, nostalgia, or atmosphere ."
    quote_candidate: "Second, we assume that high-level semantic description outperforms common low-level feature information in the task of music recommendation."
    secondary_score: 53.15614617940199
    secondary_quote: "2 We use the term ‘‘semantic’’ to refer to the concepts that music listeners use to describe items within music collections, such as genres, moods, music al culture, and instrumentation."
  - claim_4_status: partially_supported
    score: 58.064516129032256
    claim: "When preference profiles and candidate scores are built from explicit descriptors, the system can report what contributed to each decision and by how much ."
    quote_candidate: "In the present work, we focus on music recommender systems and consider explicit strategies to in- fer musical preferences of a user directly from the music audio data."
    secondary_score: 55.47945205479452
    secondary_quote: "These semantic descriptors are computed from an explicit set of music tracks deﬁned by a given user as evidence of her/his musical preferences."

## bonnin_automated_2015
- title: Automated Generation of Music Playlists: Survey and Experiments
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.02040816326531
    claim: "Playlist quality therefore depends on sequence construction, not only item relevance ."
    quote_candidate: "A possible drawback is that the quality of the generated playlists depends on the number and quality of the playlists used for rule extraction."
    secondary_score: 49.72375690607735
    secondary_quote: "As we will see later on, artists can play an important role in the playlist generation process."
  - claim_2_status: weak_support
    score: 47.19101123595506
    claim: "Reported improvements depend on protocol choices and method composition ."
    quote_candidate: "3Notice that frequent pattern mining approaches can also be considered as statistical estimation methods."
    secondary_score: 45.833333333333336
    secondary_quote: "[2010], two models—the taste model and the session model— are proposed."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.23696682464455
    claim: "Recommender systems are commonly grouped into content-based, collaborative, and hybrid families ."
    quote_candidate: "The ﬁrst com- puterized RS prototypes also applied a collaborative ﬁltering approach and emerged in mid 90s [6,7]."
    secondary_score: 49.795918367346935
    secondary_quote: "Recommender systems are software tools used to generate and provide suggestions for items and other entities to the users by exploiting various strategies."
  - claim_2_status: partially_supported
    score: 53.513513513513516
    claim: "Hybrid systems combine signals to exploit complementary strengths, yet the combination itself introduces additional reasoning complexity that can make explanation and audit harder unless interpretability is designed in from the start ."
    quote_candidate: "Hybrid recommender systems combine two or more recommendation strategies in differ- ent ways to beneﬁt from their complementary advantages."
    secondary_score: 49.32975871313673
    secondary_quote: "Nvivo is a data analysis software tool that helps in automating the identiﬁcation and the labeling of the initial segments of text from the selected studies."
  - claim_3_status: partially_supported
    score: 51.55555555555556
    claim: "Hybrid and neural recommenders can capture richer interactions and often deliver strong predictive performance ."
    quote_candidate: "In the case of new users the system has no information about their preferences and thus fails to recommend anything to them."
    secondary_score: 51.012145748987855
    secondary_quote: "Hybrid recommender systems combine two or more recommendation strategies in differ- ent ways to beneﬁt from their complementary advantages."

## cavenaghi_systematic_2023
- title: A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Cavenaghi et al. - 2023 - A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "If it claims observability and reproducibility, runs should be documented through recorded configuration and stage-level diagnostics ."
    quote_candidate: "Regarding reproducibility, the authors report the results with a standard error over 20 runs, therefore we consider a result reproduced if our result is in the given interval."
    secondary_score: 49.586776859504134
    secondary_quote: "For the papers that do not report such an interval, we consider a result to be reproducible if the difference w.r.t."
  - claim_2_status: partially_supported
    score: 50.68119891008175
    claim: "Recommender-system literature repeatedly reports weak reproducibility when split definitions, preprocessing, dependencies, and configuration states are under-specified ."
    quote_candidate: "The hardware configuration used to run the experiments is not provided either in the paper or in the GitHub repository, while the software dependencies are reported in 12https://github.com/jiaqima/Off-Policy-2-Stage."
    secondary_score: 50.314465408805034
    secondary_quote: "We therefore studied the state of reproducibility support on the topic of Reinforcement Learning & Recommender Systems to analyse the situation in this context."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.172413793103445
    claim: "Their main relevance here is mechanism visibility: when ranking depends on explicit features, the rationale for recommendation can often be traced back to those same features ."
    quote_candidate: "To compute recommendations, for instance, one can compute the dot product of the content representation and a learnt user feature vector, utilize the user and content features in a classifier to estimate a preference, or utilize an attention mechanism for per- sonalized content."
    secondary_score: 54.54545454545455
    secondary_quote: "The intuitive idea behind this work is that music experts with better VM and MS may perceive the same music recommendation list more diverse than non-specialists with lower VM and MS."
  - claim_2_status: partially_supported
    score: 54.151624548736464
    claim: "frame content-driven systems around explicit content layers and note ongoing challenges in transparency, sequence recommendation, and efficiency ."
    quote_candidate: "Furthermore, articles are discussed in temporal order to shed light on the evolution of content-driven music recommendation strategies."
    secondary_score: 53.01204819277108
    secondary_quote: "Readers are referred to [5,22,23] for an overview of recent advances in content-driven recommender systems."
  - claim_3_status: weak_support
    score: 49.63503649635037
    claim: "The semantic gap sharpens that limitation: low-level descriptors do not fully capture human concepts such as mood, nostalgia, or atmosphere ."
    quote_candidate: "While the discussion of content-based music features is relevant to the survey at hand, the authors do not focus on MRS tasks and challenges."
    secondary_score: 48.5207100591716
    secondary_quote: "The authors conclude that leveraging negative preferences has great potential for explaining recommendations because knowing what users do not want to listen to could be as informative for them as knowing what they like."
  - claim_4_status: partially_supported
    score: 53.93939393939394
    claim: "When preference profiles and candidate scores are built from explicit descriptors, the system can report what contributed to each decision and by how much ."
    quote_candidate: "Levels of content Within the recommender systems research community, the term content can be found to refer to a variety of data sources that can be accessed to derive features describing the items to be recommended."
    secondary_score: 52.76872964169381
    secondary_quote: "Data diversity: While the core of the model represents the item through one audio file, the remaining layers can consist of a broader spectrum of data from multiple sources."

## elmagarmid_duplicate_2007
- title: Duplicate Record Detection: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Elmagarmid et al. - 2007 - Duplicate Record Detection A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.56794425087108
    claim: "Entity-resolution research usually handles this with blocking and filtering to narrow the candidate set, followed by staged matching and refinement ."
    quote_candidate: "In this section, we describe techniques that have been applied for matching fields with string data in the duplicate record detection context."
    secondary_score: 51.051051051051054
    secondary_quote: "Although blocking can substantially increase the speed of the comparison process, it can also lead to an increased number of false mismatches due to the failure of comparing records that do not agree on the blocking field."

## ferrari_dacrema_troubling_2021
- title: A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ferrari Dacrema et al. - 2021 - A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.73684210526316
    claim: "Recommender outcomes vary with protocol definitions, preprocessing decisions, and metric framing, so strong benchmark performance under one setup does not automatically make a method the best choice for a project whose main contribution is inspectable engineering ."
    quote_candidate: "To make our analyses and com- parisons as fair as possible, we decided to run our evaluations in exactly the same way as the authors of the originally proposed method did, i.e., using their datasets, their protocol, and their performance metrics."
    secondary_score: 50.8130081300813
    secondary_quote: "Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page."
  - claim_2_status: weak_support
    score: 49.30555555555556
    claim: "Recommender-system literature repeatedly reports weak reproducibility when split definitions, preprocessing, dependencies, and configuration states are under-specified ."
    quote_candidate: "One possible reason is that reproducibility in general is considered a positive point in the reviewing process, e.g., at KDD."
    secondary_score: 47.87234042553192
    secondary_quote: "For that reason, and to ensure that the results that we report here are reliable, we followed a conservative approach and limited ourselves to the papers where the original authors themselves provided an implementation of their method."

## ferraro_automatic_2018
- title: Automatic playlist continuation using a hybrid recommender system combining features from text and audio
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ferraro et al. - 2018 - Automatic playlist continuation using a hybrid recommender system combining features from text and a.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.42857142857143
    claim: "A playlist of individually strong tracks can still fail if transitions are abrupt, artist repetition is high, or diversity disrupts coherence ."
    quote_candidate: "| .| denotes the length of the list of tracks and rel i value is 1 if the track is the original playlist or 0 otherwise."
    secondary_score: 51.320754716981135
    secondary_quote: "We assume that the tracks lo cated closer to each other in playlists are more likely to be a good m atch for recommendations."
  - claim_2_status: partially_supported
    score: 50.0
    claim: "Playlist continuation studies repeatedly show tensions among coherence, novelty, diversity, and ordering ."
    quote_candidate: "Automatic playlist continuation using a hybrid recommend er system combining features from text and audio."
    secondary_score: 48.028673835125446
    secondary_quote: "Existing research on music recom- mender systems has considered a number of related tasks, inc lud- ing Automatic Playlist Generation (APG) and Automatic Play list Continuation (APC)."

## fkih_similarity_2022
- title: Similarity measures for Collaborative Filtering-based Recommender Systems: Review and experimental comparison
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\432\Fkih - 2022 - Similarity measures for Collaborative Filtering-based Recommender Systems Review and experimental c.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.148471615720524
    claim: "Metric definitions, normalization choices, and threshold settings all shape neighbourhood construction and ranking behaviour ."
    quote_candidate: "This process consists of three steps: similarity computation, neighborhood selection and rating prediction."
    secondary_score: 48.44290657439446
    secondary_quote: "As same as the User-based CF tech- nique, the Item-based CF process can be summarized into three steps: similarity computation, neighborhood selection and ratings prediction."
  - claim_2_status: partially_supported
    score: 50.717703349282296
    claim: "Similarity behaviour depends on explicit distance-function choices in feature space ."
    quote_candidate: "While the second approach tries to build a model (a machine learning) describing the user behavior in order to predict his choices."
    secondary_score: 45.19230769230769
    secondary_quote: "Similarity measures: A review In this section, we outline the theoretical foundation of a set of selected similarity measures."

## flexer_problem_2016
- title: The Problem of Limited Inter-rater Agreement in Modelling Music Similarity
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\401\Flexer and Grill - 2016 - The Problem of Limited Inter-rater Agreement in Modelling Music Similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 58.333333333333336
    claim: "Music-similarity studies show limited inter-rater agreement and sensitivity to framing, which means computational similarity is better treated as a useful approximation than as objective truth ."
    quote_candidate: "On inter-rater agreement in audio music similarity."
    secondary_score: 57.65765765765766
    secondary_quote: "Due to limited inter-rater agreement there exist upper bounds of performance in subjective evaluation of the respec- tive music similarity tasks."

## furini_social_2024
- title: Social music discovery: an ethical recommendation system based on friend’s preferred songs
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\rp\files\577\Furini and Fragnelli - 2024 - Social music discovery an ethical recommendation system based on friend’s preferred songs.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.53763440860215
    claim: "Similarity behaviour depends on explicit distance-function choices in feature space ."
    quote_candidate: "The selection of analytical values to characterize each song in the listening history depends on the Fig."
    secondary_score: 46.59090909090909
    secondary_quote: "The distance between two songs is calculated based on the differences between their audio features."

## he_neural_2017
- title: Neural Collaborative Filtering
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\436\He et al. - 2017 - Neural Collaborative Filtering.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.645161290322584
    claim: "Hybrid and neural recommenders can capture richer interactions and often deliver strong predictive performance ."
    quote_candidate: "First, we can see that with more iterations, the training loss of NCF models gradually decreases and the recommendation performance is improved."
    secondary_score: 55.319148936170215
    secondary_quote: "4.2 Performance Comparison (RQ1) Figure 4 shows the performance of HR@10 and NDCG@10 with respect to the number of predictive factors."

## herlocker_evaluating_2004
- title: Evaluating collaborative filtering recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Herlocker et al. - 2004 - Evaluating collaborative filtering recommender systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.031894934333955
    claim: "Recommender outcomes vary with protocol definitions, preprocessing decisions, and metric framing, so strong benchmark performance under one setup does not automatically make a method the best choice for a project whose main contribution is inspectable engineering ."
    quote_candidate: "Permission to make digital or hard copies of part or all of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for proﬁt or direct commercial advantage and that copies show this notice on the ﬁrst page or initial screen of a display along with the full citation."
    secondary_score: 50.10989010989011
    secondary_quote: "Clearly identifying the best algorithm for a given purpose has proven challenging, in part because researchers disagree on which attributes should be measured, and on which metrics should be used for each attribute."

## jannach_measuring_2019
- title: Measuring the Business Value of Recommender Systems
- mapped_pdf: NOT_FOUND
- mapping_score: 43
- mapping_method: no_confident_match
- result: no extractable text for this source

## jin_effects_2020
- title: Effects of personal characteristics in control-oriented user interfaces for music recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\395\Jin et al. - 2020 - Effects of personal characteristics in control-oriented user interfaces for music recommender system.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Controllability means user influence through explicit inputs or parameters ."
    quote_candidate: "The systems that support control of recommendations initially produce one or more recommendations based on user preferences."
    secondary_score: 47.57281553398058
    secondary_quote: "Controllability often allows users to steer the recommendation process to obtain sug- gestions that are better suited to them (He et al."
  - claim_2_status: partially_supported
    score: 50.5338078291815
    claim: "If the thesis claims controllability, it is not enough to expose a control in the interface; changing that control should create interpretable downstream effects ."
    quote_candidate: "Controllability often allows users to steer the recommendation process to obtain sug- gestions that are better suited to them (He et al."
    secondary_score: 50.17667844522968
    secondary_quote: "123 Effects of personal characteristics in control-oriented… 205 this reason, we did not further study the effect of demographic characteristics in this paper."
  - claim_3_status: partially_supported
    score: 50.76923076923077
    claim: "This matches the thesis assumption that influence tracks can complement imported history, and it aligns with controllability literature that treats user influence as useful when it is explicit, bounded, and testable rather than unconstrained ."
    quote_candidate: "As a result, it may be more meaningful to recommend songs that ﬁt user’s temporal preferences and context rather than show- ing songs based on user search requests (Lee et al."
    secondary_score: 50.6265664160401
    secondary_quote: "In this paper, we propose a comprehensive version of the framework which exhibits the most common interaction and visualization elements, and their association with the three levels of control."

## knijnenburg_explaining_2012
- title: Explaining the user experience of recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\422\Knijnenburg et al. - 2012 - Explaining the user experience of recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 47.53363228699551
    claim: "Interface research adds an additional constraint: faithful explanations must still be understandable to non-experts ."
    quote_candidate: "Another problem with behavioral data is that their interpretation is often trouble- some (V an V elsen et al."
    secondary_score: 47.014925373134325
    secondary_quote: "Not surprisingly, a significant part of the research on recommender systems concerns creating and evaluating better prediction algorithms (McNee et al."

## liu_aggregating_2025
- title: Aggregating Contextual Information for Multi-Criteria Online Music Recommendations
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Liu - 2025 - Aggregating Contextual Information for Multi-Criteria Online Music Recommendations.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.35356200527705
    claim: "This matches the thesis assumption that influence tracks can complement imported history, and it aligns with controllability literature that treats user influence as useful when it is explicit, bounded, and testable rather than unconstrained ."
    quote_candidate: "This assumption aligns with the structure of the collected MusiClef and CAL500 datasets, where each contextual dimension value contains a single rating from each user."
    secondary_score: 50.2262443438914
    secondary_quote: "This indicates that while CAMCMusic effectively captures primary genre preferences, there is room for improvement in aligning secondary recommendations with individual user tastes, especially in complex contextual scenarios."

## liu_multimodal_2025
- title: Multimodal Recommender Systems: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\411\Liu et al. - 2025 - Multimodal Recommender Systems A Survey.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.96078431372549
    claim: "Hybrid and neural recommenders can capture richer interactions and often deliver strong predictive performance ."
    quote_candidate: "Filtering out noisy data in multimodal recommendation tasks can usually improve the recommendation performance."
    secondary_score: 51.91489361702128
    secondary_quote: "They show that introducing multimodal data without updating encoder parameters can also improve the recommendation performance."

## lu_recommender_2015
- title: Recommender system application developments: A survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\383\Lu et al. - 2015 - Recommender system application developments A survey.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 59.12408759124087
    claim: "Recommender systems emerged as a practical response to this information-overload problem by helping users discover items they are likely to value ."
    quote_candidate: "Recommender systems can be used in digital library applications to help users locate and select information and knowledge sources[95]."
    secondary_score: 53.225806451612904
    secondary_quote: "Recommender systems can overcome this problem and have been adopted in e-government applications[74,75]."
  - claim_2_status: partially_supported
    score: 52.7363184079602
    claim: "Recommender systems are commonly grouped into content-based, collaborative, and hybrid families ."
    quote_candidate: "Recommender systems can overcome this problem and have been adopted in e-government applications[74,75]."
    secondary_score: 52.549019607843135
    secondary_quote: "For example, the paper by Adomavicius and Tuzhilin [3] presented an overview of content-based, collaborative ﬁltering-based, and hybrid recommendation approaches."

## mcfee_million_2012
- title: The million song dataset challenge
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\nw\files\570\McFee et al. - 2012 - The million song dataset challenge.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.246231155778894
    claim: "Reported improvements depend on protocol choices and method composition ."
    quote_candidate: "The choice of the cutoﬀ τ will depend on the minimum quality of the recommenders being evaluated, which we at- tempt to assess Section 5."
    secondary_score: 48.75
    secondary_quote: "This work’s goal is to clearly describe our motivations and implementa- tion decisions."

## moysis_music_2023
- title: Music Deep Learning: Deep Learning Methods for Music Signal Processing - A Review of the State-of-the-Art
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Moysis et al. - 2023 - Music Deep Learning Deep Learning Methods for Music Signal Processing—A Review of the State-of-the-.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.515151515151516
    claim: "Hybrid and neural recommenders can capture richer interactions and often deliver strong predictive performance ."
    quote_candidate: "The model outperformed other architectures and was seconded only by the real music tracks."
    secondary_score: 51.18483412322275
    secondary_quote: "The model was evaluated by profes- sional and casual users and received overall neutral to positive scores."

## nauta_anecdotal_2023
- title: From Anecdotal Evidence to Quantitative Evaluation Methods: A Systematic Review on Evaluating Explainable AI
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\426\Nauta et al. - 2023 - From Anecdotal Evidence to Quantitative Evaluation Methods A Systematic Review on Evaluating Explai.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 49.735449735449734
    claim: "Explanations may increase trust or satisfaction without improving genuine understanding ."
    quote_candidate: "1.1 Definitions and Terminology Explanations have been discussed for decades in many research areas."
    secondary_score: 47.22222222222222
    secondary_quote: "Other Explanation that does not fit any other category."
  - claim_2_status: partially_supported
    score: 51.2
    claim: "If the thesis claims controllability, it is not enough to expose a control in the interface; changing that control should create interpretable downstream effects ."
    quote_candidate: "A feature is not necessarily an input feature to predictive model f, but it should be a feature in the explanation."
    secondary_score: 50.498338870431894
    secondary_quote: "We also found that explainability is indeed not a binary property, and that various aspects of an explanation should be evaluated independently of each other."

## neto_algorithmic_2023
- title: The algorithmic nature of song-sequencing: statistical regularities in music albums
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\403\Neto et al. - 2023 - The algorithmic nature of song-sequencing statistical regularities in music albums.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.2092050209205
    claim: "Sequencing analyses reinforce that users perceive playlists as ordered structures, not isolated items ."
    quote_candidate: "In order to incorporate the notions of absolute posi- tioning and overall trajectory, we used Spearman’sρas a penalty term to Equation (1)."
    secondary_score: 48.13278008298755
    secondary_quote: "From sequences of movements to sequences of tracks The idea that music is globally perceived as a coher- ent sequence of acoustic events is a common one 412 P."

## papadakis_blocking_2021
- title: Blocking and Filtering Techniques for Entity Resolution: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Papadakis et al. - 2021 - Blocking and Filtering Techniques for Entity Resolution A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.61290322580645
    claim: "Entity-resolution research usually handles this with blocking and filtering to narrow the candidate set, followed by staged matching and refinement ."
    quote_candidate: "In this survey, we focus on the candidate selection step, which is the crucial part of ER with respect to time efficiency and scalability."
    secondary_score: 50.714285714285715
    secondary_quote: "Entities sharing the same output for a particular blocking predicate are considered candidate matches (i.e., hash-based functionality)."

## pegoraro_santana_music4all_2020
- title: Music4All: A New Music Database and Its Applications
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Pegoraro Santana et al. - 2020 - Music4All A New Music Database and Its Applications.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.01929260450161
    claim: "Music4All is suitable here because it offers metadata, tags, lyrics, and audio-related attributes for content-driven experimentation ."
    quote_candidate: "In order to contribute to the MIR community, we present Music4AII, a new music database which contains metadata, tags, genre information, 30-seconds audio clips, lyrics, and so on."
    secondary_score: 53.54838709677419
    secondary_quote: "By this way, in this work we try to contribute in this sense, introducing a novel music database that offers hundreds of thousands of music pieces assigned to metadata, tags, labels, lyrics, and so on."

## roy_systematic_2022
- title: A systematic review and research perspective on recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\385\Roy and Dutta - 2022 - A systematic review and research perspective on recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 58.57142857142857
    claim: "Recommender systems emerged as a practical response to this information-overload problem by helping users discover items they are likely to value ."
    quote_candidate: "In this era of big data, more and more items and users are rapidly getting added to the system and this problem is becoming common in recommender systems."
    secondary_score: 57.142857142857146
    secondary_quote: "Recommender systems primarily aim to reduce the user’s effort and time required for searching relevant information over the internet."
  - claim_2_status: partially_supported
    score: 53.07125307125307
    claim: "Foundational recommender research frames this task as utility estimation under partial information: infer likely value from sparse and incomplete evidence rather than retrieve a fully known answer ."
    quote_candidate: "This can be further understood by the fact that research papers on recommender systems are scattered across various journals such as computer science, management, marketing, information technology and information science."
    secondary_score: 52.493438320209975
    secondary_quote: "Finally, we provide researchers and practitioners with insight into the most promising directions for further investigation in the field of recommender systems under various applications."
  - claim_3_status: partially_supported
    score: 55.08474576271186
    claim: "Preference evidence in recommender systems may be explicit, such as ratings or likes, or implicit, such as clicks, playback history, or other behavioural traces ."
    quote_candidate: "Most recommender systems gather user ratings through both explicit and implicit methods."
    secondary_score: 51.515151515151516
    secondary_quote: "The nature of research in recommender systems is such that it is difficult to confine each paper to a specific discipline."
  - claim_4_status: partially_supported
    score: 50.526315789473685
    claim: "Listening history provides implicit preference evidence rather than a fully specified user statement ."
    quote_candidate: "Most recommender systems gather user ratings through both explicit and implicit methods."
    secondary_score: 49.54128440366973
    secondary_quote: "The nature of research in recommender systems is such that it is difficult to confine each paper to a specific discipline."

## ru_improving_2023
- title: Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Perspective
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.45054945054945
    claim: "Third-party usage in multimodal studies provides additional support while transfer limits remain explicit ."
    quote_candidate: "The comparison results with other multi-modal methods are shown in Table 1."
    secondary_score: 48.13278008298755
    secondary_quote: "In order to improve the performance of multi-label MGC, in addition to using the multi-modality nature of music, we can also start from the nature of the multi-label problem."

## schedl_current_2018
- title: Current challenges and visions in music recommender systems research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\399\Schedl et al. - 2018 - Current challenges and visions in music recommender systems research.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 48.96265560165975
    claim: "Listening is often session-based and sequential, and users judge not only individual tracks but transitions, pacing, repetition, and overall flow ."
    quote_candidate: "Listening intent and purpose Music serves various purposes for people and hence shapes their intent to listen to it."
    secondary_score: 48.8
    secondary_quote: "High sparsity translates into low rating coverage, since most users tend to rate only a tiny fraction of items."
  - claim_2_status: weak_support
    score: 48.31460674157304
    claim: "Playlist quality therefore depends on sequence construction, not only item relevance ."
    quote_candidate: "This is done by generating a user proﬁle by requesting the user to rate a set of selected items [ 30]."
    secondary_score: 48.275862068965516
    secondary_quote: "For this reason, there sometimes exist a variety of different deﬁnitions to quantify the same beyond-accuracy aspect."

## schweiger_impact_2025
- title: The impact of playlist characteristics on coherence in user-curated music playlists
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\rp\files\578\Schweiger et al. - 2025 - The impact of playlist characteristics on coherence in user-curated music playlists.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.002849002849004
    claim: "Music-domain studies strengthen the case for treating those choices as consequential, while broad multi-dataset isolation evidence across playlist objectives remains limited ."
    quote_candidate: "During a session, the user can make multiple changes to theplaylistwithoutincreasingtheeditscore.Anediting session endsiftheuserdoesnot make any modiﬁcations for at least two hours."
    secondary_score: 48.598130841121495
    secondary_quote: "Example 3 Understanding coherence and its relationship with other playlist character- istics can be applied to tasks beyond track recommendations."

## siedenburg_modeling_2017
- title: Modeling Timbre Similarity of Short Music Clips
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Siedenburg and Müllensiefen - 2017 - Modeling Timbre Similarity of Short Music Clips.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.257790368271955
    claim: "Music-similarity studies show limited inter-rater agreement and sensitivity to framing, which means computational similarity is better treated as a useful approximation than as objective truth ."
    quote_candidate: "A computational model is necessary in order to create a test that is adaptive and homes in on the individual participant’s ability level for judging sound similarities."
    secondary_score: 51.50684931506849
    secondary_quote: "The present contribution is the ﬁrst study to systematically quantify the extent to which similarity d ata of short musical excerpts can be explained by acoustic timbre descriptors."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.33112582781457
    claim: "Recent music explainability work supports the same broader principle that explanations should expose contribution structure rather than only final outcomes ."
    quote_candidate: "Additionally, we provide global explanations by aggregating local explanations, offering a broader understanding of the model’s overall behavior."
    secondary_score: 50.0
    secondary_quote: "Additionally, we will investigate alternative explanation methods, such as counter- factual explanations, and assess their applicability in a multimodal framework for music understanding."

## teinemaa_composition_2018
- title: Automatic Playlist Continuation through a Composition of Collaborative Filters
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Teinemaa et al. - 2018 - Automatic Playlist Continuation through a Composition of Collaborative Filters.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.12781954887218
    claim: "Challenge analyses and implementation reports show that outcomes depend on method composition, candidate handling, and evaluation protocol ."
    quote_candidate: "Table 3 shows the optimized best sets of weights separately for each category (used in the local weights composition) and global weights (used in the global weights composition)."
    secondary_score: 46.42857142857143
    secondary_quote: "1Note that the overall scores are slightly different than in the above, since this detailed evaluation was executed with training on 400k playlists and a total of 100k tracks only, to reduce the computations."
  - claim_2_status: weak_support
    score: 49.717514124293785
    claim: "Reported improvements depend on protocol choices and method composition ."
    quote_candidate: "Section 3 describes the proposed framework based on several collaborative filters and their combination."
    secondary_score: 46.35761589403973
    secondary_quote: "Results This subsection presents and discusses the results of our experiments."

## tintarev_evaluating_2012
- title: Evaluating the effectiveness of explanations for recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\391\Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 60.40268456375839
    claim: "Explainable recommender research argues that predictive quality alone is insufficient when users or evaluators need to understand and question system behaviour ."
    quote_candidate: "For example, suppose that in a particular recommender system users tend to select item A when no explanations are present, and item B when explanations are present."
    secondary_score: 55.73770491803279
    secondary_quote: "So, an explanation can be an item description that helps the user to understand the qualities of the item well enough to decide whether it is relevant to them or not."
  - claim_2_status: partially_supported
    score: 50.0
    claim: "Explanations may increase trust or satisfaction without improving genuine understanding ."
    quote_candidate: "We mea- sure objective effectiveness, as perceived effectiveness may overlap with satisfaction."
    secondary_score: 49.75124378109453
    secondary_quote: "Contrary to expectation, personalization was detrimental to effectiveness, though it may improve user satisfaction."

## tintarev_survey_2007
- title: A Survey of Explanations in Recommender Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\389\Tintarev and Masthoff - 2007 - A Survey of Explanations in Recommender Systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 56.56565656565657
    claim: "Explainable recommender research argues that predictive quality alone is insufficient when users or evaluators need to understand and question system behaviour ."
    quote_candidate: "We hope that the framework and survey presented in this paper will lead to more systematic research on explanations in recommender systems."
    secondary_score: 56.25
    secondary_quote: "In the recommender systems community it is increas- ingly recognized that accuracy metrics such as mean av- erage error (MAE), precision and recall, can only partially evaluate a recommender system [23]."
  - claim_2_status: partially_supported
    score: 60.645161290322584
    claim: "Controllability means user influence through explicit inputs or parameters ."
    quote_candidate: "Rating may be explicitly inputted by the user, or inferred from usage patterns."
    secondary_score: 50.64935064935065
    secondary_quote: "A persuasive explanation may also inﬂuence previous evaluations of items [10]."

## tsai_explaining_2018
- title: Explaining Social Recommendations to Casual Users: Design Principles and Opportunities
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\393\Tsai and Brusilovsky - 2018 - Explaining Social Recommendations to Casual Users Design Principles and Opportunities.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.70422535211268
    claim: "Interface research adds an additional constraint: faithful explanations must still be understandable to non-experts ."
    quote_candidate: "7) Satisfaction: The feedback on how an explanation can help the user satisfy the system was varied."
    secondary_score: 50.370370370370374
    secondary_quote: "One respondent proposed an interesting idea to have a “mutual explanation” among users, say ( we both see the explanation and reason why we should connect)."

## vall_feature-combination_2019
- title: Feature-combination hybrid recommender systems for automated music playlist continuation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Vall et al. - 2019 - Feature-combination hybrid recommender systems for automated music playlist continuation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.51194539249147
    claim: "A playlist of individually strong tracks can still fail if transitions are abrupt, artist repetition is high, or diversity disrupts coherence ."
    quote_candidate: "Additional details of each playlist con- tinuation system, additional song feature types, and additional results are provided in Appendices A, B and C, respectively."
    secondary_score: 50.0
    secondary_quote: "A common limitation of all pure CF systems is that they are only aware of the songs occurring in training playlists."
  - claim_2_status: partially_supported
    score: 53.714285714285715
    claim: "Playlist continuation studies repeatedly show tensions among coherence, novelty, diversity, and ordering ."
    quote_candidate: "1 Playlist continuation as a matrix completion and expansion problem."
    secondary_score: 53.588516746411486
    secondary_quote: "Sections 4 and 5 describe the proposed systems and the baselines for music playlist continuation, respectively."

## yu_self_supervised_2024
- title: Self-Supervised Learning for Recommender Systems: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Self-Supervised_Learning_for_Recommender_Systems_A_Survey.pdf
- mapping_score: 66
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.38095238095238
    claim: "Hybrid and neural recommenders can capture richer interactions and often deliver strong predictive performance ."
    quote_candidate: "The bidirectional training can bridge the gap between the reverse augmentation and the forward recommendation."
    secondary_score: 50.17921146953405
    secondary_quote: "The SSR model is pre-trained on the original data, and potential informative samples for the recommendation task are predicted using the pre- trained parameters as augmented data."

## zamani_analysis_2019
- title: An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Continuation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zamani et al. - 2019 - An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Contin.pdf
- mapping_score: 100
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.019867549668874
    claim: "Challenge analyses and implementation reports show that outcomes depend on method composition, candidate handling, and evaluation protocol ."
    quote_candidate: "The reason might be that adding external resources increases the complexity of the models and given the amount of training data, the models could not take advantage of external resources, effectively."
    secondary_score: 45.418326693227094
    secondary_quote: "This means that most users can find a relevant track in the top 10 recommended list and do not need to reload the recommended track list."
  - claim_2_status: weak_support
    score: 49.76958525345622
    claim: "Playlist continuation studies repeatedly show tensions among coherence, novelty, diversity, and ordering ."
    quote_candidate: "As shown in the table, several teams took advantage of a two-stage architecture for the playlist continuation task."
    secondary_score: 49.586776859504134
    secondary_quote: "[46] have recently identified the task of automatic music playlist continuation as one of the grand challenges in music recommender systems research."

## zhang_explainable_2020
- title: Explainable Recommendation: A Survey and New Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\387\Zhang and Chen - 2020 - Explainable Recommendation A Survey and New Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.755287009063444
    claim: "They can perform strongly at scale with rich histories, but direct interpretability may weaken when ranking logic is encoded in latent relationships rather than explicit feature comparisons ."
    quote_candidate: "The explanations may either be post-hoc or directly come from an explainable model (also called interpretable or transparent model in some contexts)."
    secondary_score: 49.152542372881356
    secondary_quote: "It will help readers to understand what is unique about the explainable recommendation problem, what is the position of ex- plainable recommendation in the research area, and why explainable recommendation is important to the area."
  - claim_2_status: partially_supported
    score: 56.70103092783505
    claim: "Explainable recommender research argues that predictive quality alone is insufficient when users or evaluators need to understand and question system behaviour ."
    quote_candidate: "Explainable recommendation tries to address the problem of why: by providing explanations to users or system design- ers, it helps humans to understand why certain items are recommended by the algorithm, where the human can either be users or system designers."
    secondary_score: 54.662379421221864
    secondary_quote: "Signiﬁcant research eﬀorts in user behavior analysis and human- computer interaction community aim to understand how users interact with explanations."
  - claim_3_status: partially_supported
    score: 50.76142131979695
    claim: "Post-hoc explanations can be persuasive yet weakly coupled to the mechanism that produced the ranking ."
    quote_candidate: "Instead, it develops an explanation model to generate explanations after a decision has been made."
    secondary_score: 48.35164835164835
    secondary_quote: "For example, the items recommended by user-based CF can be explained as “users that are similar to you loved this item”, while item-based CF can be explained as “the item is similar to your previously loved items”."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.76470588235294
    claim: "Recommender-system literature repeatedly reports weak reproducibility when split definitions, preprocessing, dependencies, and configuration states are under-specified ."
    quote_candidate: "To promote reproducible research, our benchmark- ing work aims to record detailed hyper-parameter configurations for each experiment and demonstrate the reproducing steps."
    secondary_score: 48.63013698630137
    secondary_quote: "In Proceedings of the International Workshop on Reproducibility and Replication in Recommender Systems Evaluation (RepSys)."

## Summary
- total_claim_checks: 87
- supported: 1
- partially_supported: 72
- weak_support: 14
- no_match: 0