# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `08_writing\chapter2_temp.md` against extracted text from mapped local PDFs.
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
    score: 58.13953488372093
    claim: "Foundational recommender literature frames the task as utility estimation under partial information: given sparse evidence about user preferences, infer which items are most likely to be useful ."
    quote_candidate: "Intuitively, this estimation is usually based on the ratings given by this user to other items and on some other information that will be formally described below."
    secondary_score: 55.445544554455445
    secondary_quote: "It can be argued that the Grundy system [87] was the first recommender system, which proposed using stereotypes as a mechanism for building models of users based on a limited amount of information on each individual user."
  - claim_3_status: supported
    score: 73.6842105263158
    claim: "Recommender systems are commonly described through three families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "Toward the Next Generation of Recommender Systems: A Survey of the State-of-the-Art and Possible Extensions Gediminas Adomavicius, Member , IEEE, and Alexander Tuzhilin, Member , IEEE Abstract—This paper presents an overview of the field of recommender systems and describes the current generation of recommendation methods that are usually classified into the following three main categories: content-based, collaborative, and hybrid recommendation approaches."
    secondary_score: 66.66666666666666
    secondary_quote: "Therefore, function uij clearly subsumes the collaborative, content-based, and hybrid methods discussed in Section 2."
  - claim_4_status: partially_supported
    score: 51.282051282051285
    claim: "They can perform strongly at scale, especially with rich interaction histories, but they may reduce direct interpretability when decision logic is encoded in latent representations ."
    quote_candidate: "The interest in this area still remains high because it constitutes a problem-rich research area and because of the abundance of practical applications that help users to deal with information overload and provide personalized recommendations, content, and services to them."
    secondary_score: 51.21951219512195
    secondary_quote: "Another problem with limited content analysis is that, if two different items are represented by the same set of features, they are indistinguishable."

## afroogh_trust_2024
- title: Trust in AI: progress, challenges, and future directions
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\428\Afroogh et al. - 2024 - Trust in AI progress, challenges, and future directions.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.92250922509225
    claim: "Interface research adds a practical constraint: faithful explanations still need to be understandable for non-expert users ."
    quote_candidate: "In particular, factors such as access to knowledge, transparency, explainability, certiﬁcation, as well as self-imposed standards and guidelines are Fig."
    secondary_score: 50.625
    secondary_quote: "Discussion,a n a l y - tically discusses the major codes and key values and considerations related to trust in AI, as well as the address of the practical value conﬂicts and the probable tradeoff between the key values and considerations."

## allam_improved_2018
- title: Improved suffix blocking for record linkage and entity resolution
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Allam et al. - 2018 - Improved suffix blocking for record linkage and entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 56.70498084291188
    claim: "Entity-resolution literature widely uses blocking and filtering to generate candidate matches at scale, followed by staged matching/refinement ."
    quote_candidate: "To generate candidate matches for a given record, all matching su ﬃ xes are retrieved by querying the inverted index."
    secondary_score: 52.083333333333336
    secondary_quote: "INCENTRES uses INCSUFFBLOCK to identify the candidate matches (Line 1)."
  - claim_2_status: partially_supported
    score: 50.73170731707317
    claim: "Alignment should report blocking/filtering stages and resulting candidate-match paths explicitly ."
    quote_candidate: "Given a dataset D, let L be the set of actual linked record pairs in D and let R be the set of record pairs that result in by the blocking stage."
    secondary_score: 49.23076923076923
    secondary_quote: "Incremental record linkage In this section, we propose a blocking method for incremental record linkage."

## andjelkovic_moodplay_2019
- title: Moodplay: Interactive music recommendation based on Artists' mood similarity
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.13513513513514
    claim: "User control can improve experience, but effects vary by user characteristics and context ."
    quote_candidate: "Users construct proﬁles by entering names of artists via an interactive drop- down list ( Fig."
    secondary_score: 53.386454183266935
    secondary_quote: "These characteristics can be demonstrated by comparing music to two types of content widely oﬀered to users via recommender systems: online movies and merchandise."

## anelli_elliot_2021
- title: Elliot: A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.55555555555556
    claim: "Recommender outcomes can be sensitive to protocol definitions, preprocessing choices, and metric framing ."
    quote_candidate: "Bias in Search and Recommender Systems."
    secondary_score: 51.61290322580645
    secondary_quote: "Finally, depending on the recommendation task and main goal of the RS, several performance dimensions, sometimes contradict- ing, can be assessed."
  - claim_2_status: partially_supported
    score: 56.60377358490566
    claim: "Across recommender reproducibility studies, missing details on data splits, hyperparameters, software dependencies, and configuration are repeatedly reported as barriers to credible comparison ."
    quote_candidate: "Rival: a toolkit to foster reproducibility in recommender system evaluation."
    secondary_score: 54.02298850574713
    secondary_quote: "Elliot is a comprehensive recommendation framework that aims to run and reproduce an entire experimental pipeline by processing a simple configuration file."
  - claim_3_status: partially_supported
    score: 54.4
    claim: "Reproducibility should be treated as an evidence-quality requirement ."
    quote_candidate: "Reproducibility is the keystone of modern RSs research."
    secondary_score: 43.05555555555556
    secondary_quote: "Elliot reports can be directly analyzed and inserted into research papers."

## balog_transparent_2019
- title: Transparent, Scrutable and Explainable User Models for Personalized Recommendation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\397\Balog et al. - 2019 - Transparent, Scrutable and Explainable User Models for Personalized Recommendation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 58.75
    claim: "Controllability refers to explicit user controls that can steer the recommendation process ."
    quote_candidate: "Users can then steer the recommendations by manipulating the tag clouds."
    secondary_score: 57.971014492753625
    secondary_quote: "Transparency provides insights into how the recommendation process works, and is closely related to explainability."

## barlaug_neural_2021
- title: Neural Networks for Entity Matching: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Barlaug and Gulla - 2021 - Neural Networks for Entity Matching A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 60.37735849056604
    claim: "Neural entity matching is an established comparator family in entity resolution ."
    quote_candidate: "Importantly, entity matching does not have to take into account a larger textual context, which is necessary in coreference resolution to find coreferring mentions across multiple sentences."
    secondary_score: 56.310679611650485
    secondary_quote: "Some of the Many Names that are Used for Entity Matching or Similar Variations of It Entity matching Entity resolution Record linkage Data matching Data linkage Reference reconciliation String matching Approximate string matching Fuzzy matching Fuzzy join Similarity join Deduplication Duplicate detection Merge-purge Object identification Re-identification The goal of entity matching is to find the largest possible binary relationM⊆A×B such that a and b refer to the same entity for all(a,b)∈M."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.43478260869565
    claim: "Recommender outcomes can be sensitive to protocol definitions, preprocessing choices, and metric framing ."
    quote_candidate: "Balog and Radlinski [11] propose how to measure the quality of explanations in ACM Transactions on Recommender Systems, Vol."
    secondary_score: 48.0
    secondary_quote: "The types as specified in Table2 (i.e., benchmark, framework, metrics, model, and survey) were inferred according to the description in Section2.3."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.54545454545455
    claim: "Across recommender reproducibility studies, missing details on data splits, hyperparameters, software dependencies, and configuration are repeatedly reported as barriers to credible comparison ."
    quote_candidate: "We have also considered recent works and trends on reproducibility in neighboring fields to extract more con- crete issues and guidelines for recommender systems."
    secondary_score: 51.62907268170426
    secondary_quote: "In today’s recommender systems-related literature, papers often state what datasets, algorithms, baselines, and other potential parameter values are used in order to (theoretically) ensure reproducibility."

## binette_almost_2022
- title: (Almost) all of entity resolution
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Binette and Steorts - 2022 - (Almost) all of entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.25
    claim: "Entity-resolution literature widely uses blocking and filtering to generate candidate matches at scale, followed by staged matching/refinement ."
    quote_candidate: "Deduplication is thus needed to obtain an accurate enumeration, with new methodology from the machine learning and statistical literature being recently proposed to this end (48)."
    secondary_score: 48.58044164037855
    secondary_quote: "This review is motivated by the long history of entity resolution, its active development in the scientific literature over the years, and its growing relevance throughout many scientific domains."

## bogdanov_semantic_2013
- title: Semantic audio content-based music recommendation and visualization based on user preference examples
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\409\Bogdanov et al. - 2013 - Semantic audio content-based music recommendation and visualization based on user preference example.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.89225589225589
    claim: "A key strength is mechanism visibility: when the model relies on explicit features, recommendations can often be explained through those same features ."
    quote_candidate: "In contrast to the proposed semantic methods, these algo- rithms use the same procedure for recommendation but operate on low-level timbral features."
    secondary_score: 54.67128027681661
    secondary_quote: "Logan (2004) proposes to generate recommendations based on an explicitly given set of music tracks, which represent a user’s preferences."
  - claim_2_status: partially_supported
    score: 55.670103092783506
    claim: "The semantic gap reinforces this: low-level computable features do not perfectly capture human concepts such as mood, nostalgia, or atmosphere ."
    quote_candidate: "We use the described low-level features to infer semantic descriptors."
    secondary_score: 54.054054054054056
    secondary_quote: "These approaches apply the same ideas as the proposed semantic approaches, but operate on low-level timbral features, frequently used in the related literature."
  - claim_3_status: partially_supported
    score: 58.63192182410423
    claim: "When preference profiles and candidate scores are built from explicit descriptors, the system can report what contributed to each decision and how much ."
    quote_candidate: "In the present work, we focus on music recommender systems and consider explicit strategies to in- fer musical preferences of a user directly from the music audio data."
    secondary_score: 54.47761194029851
    secondary_quote: "With the described procedure we obtain 62 semantic descriptors, shown in Table 1, for each track in the user’s preference set."

## bonnin_automated_2015
- title: Automated Generation of Music Playlists: Survey and Experiments
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 60.23166023166023
    claim: "Playlist quality depends on treating playlists as sequences of tracks where order and transitions matter ."
    quote_candidate: "These playlists are basically sequences of tracks that traditionally are designed manually and whose organization is based on some underlying logic or theme."
    secondary_score: 60.18518518518518
    secondary_quote: "A possible drawback is that the quality of the generated playlists depends on the number and quality of the playlists used for rule extraction."
  - claim_2_status: partially_supported
    score: 51.0
    claim: "Challenge and benchmark analyses show that outcomes can depend on protocol and method composition ."
    quote_candidate: "3Notice that frequent pattern mining approaches can also be considered as statistical estimation methods."
    secondary_score: 48.78048780487805
    secondary_quote: "The constraints can concern various aspects including the desired genre, tempo, year of release, and so forth."
  - claim_3_status: partially_supported
    score: 52.11726384364821
    claim: "APC studies report that performance varies across model compositions and evaluation setups, so conclusions are tied to the selected protocol and metrics ."
    quote_candidate: "The difference between the two models is that the ﬁrst one only uses one latent cluster per listening session and can thus be considered as reﬂect- ing the user’s taste."
    secondary_score: 51.111111111111114
    secondary_quote: "Furthermore, we discuss the evaluation designs that are used today in research to assess the quality of the generated playlists."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.282051282051285
    claim: "Recommender systems are commonly described through three families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "The ﬁrst com- puterized RS prototypes also applied a collaborative ﬁltering approach and emerged in mid 90s [6,7]."
    secondary_score: 50.0
    secondary_quote: "Recommender systems are software tools used to generate and provide suggestions for items and other entities to the users by exploiting various strategies."
  - claim_2_status: supported
    score: 82.22222222222223
    claim: "Hybrid approaches combine two or more recommendation strategies to benefit from complementary advantages ."
    quote_candidate: "Hybrid recommender systems combine two or more recommendation strategies in differ- ent ways to beneﬁt from their complementary advantages."
    secondary_score: 61.43790849673203
    secondary_quote: "The author analyzes advantages and disadvantages of the different recommendation strategies and provides a comprehensive taxonomy for classifying the ways they combine with each other to form hybrid RSs."
  - claim_3_status: partially_supported
    score: 50.62240663900415
    claim: "Hybrid and neural recommenders can deliver strong predictive performance and capture richer interactions ."
    quote_candidate: "Hybrid recommender systems combine two or more recommendation strategies in differ- ent ways to beneﬁt from their complementary advantages."
    secondary_score: 50.22831050228311
    secondary_quote: "In the case of new users the system has no information about their preferences and thus fails to recommend anything to them."

## cavenaghi_systematic_2023
- title: A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Cavenaghi et al. - 2023 - A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.57142857142857
    claim: "Across recommender reproducibility studies, missing details on data splits, hyperparameters, software dependencies, and configuration are repeatedly reported as barriers to credible comparison ."
    quote_candidate: "The hardware configuration used to run the experiments is not provided either in the paper or in the GitHub repository, while the software dependencies are reported in 12https://github.com/jiaqima/Off-Policy-2-Stage."
    secondary_score: 53.49794238683128
    secondary_quote: "We collected a total of 60 papers and analysed them by defining a set of variables to inspect the most important aspects that enable reproducibility, such as dataset, pre-processing code, hardware specifica- tions, software dependencies, algorithm implementation, algorithm hyperparameters, and experiment code."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.033557046979865
    claim: "A key strength is mechanism visibility: when the model relies on explicit features, recommendations can often be explained through those same features ."
    quote_candidate: "Performing MLR on this representation results in optimizing the feature space such that the system can recommend more novel items based on audio content."
    secondary_score: 54.9800796812749
    secondary_quote: "Therefore, the same vocabulary is used to steer the recommendation process and to explain recommendations."
  - claim_2_status: partially_supported
    score: 51.492537313432834
    claim: "The semantic gap reinforces this: low-level computable features do not perfectly capture human concepts such as mood, nostalgia, or atmosphere ."
    quote_candidate: "The authors design a content-based MRS leveraging audio features which are obtained from pre-trained self-supervised models."
    secondary_score: 49.59349593495935
    secondary_quote: "This is notwithstanding other reasons, such as affective experiences, memories, or contextual factors."
  - claim_3_status: partially_supported
    score: 54.43425076452599
    claim: "When preference profiles and candidate scores are built from explicit descriptors, the system can report what contributed to each decision and how much ."
    quote_candidate: "Levels of content Within the recommender systems research community, the term content can be found to refer to a variety of data sources that can be accessed to derive features describing the items to be recommended."
    secondary_score: 52.63157894736842
    secondary_quote: "Data diversity: While the core of the model represents the item through one audio file, the remaining layers can consist of a broader spectrum of data from multiple sources."

## elmagarmid_duplicate_2007
- title: Duplicate Record Detection: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Elmagarmid et al. - 2007 - Duplicate Record Detection A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.3448275862069
    claim: "Entity-resolution literature widely uses blocking and filtering to generate candidate matches at scale, followed by staged matching/refinement ."
    quote_candidate: "Winkler and Thibaudeau [40] modified the Jaro metric to give higher weight to prefix matches since prefix matches are generally more important for surname matching."
    secondary_score: 48.201438848920866
    secondary_quote: "Then, Section 3 describes techniques used to match individual fields and Section 4 presents techniques for matching records that contain multiple fields."

## ferrari_dacrema_troubling_2021
- title: A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ferrari Dacrema et al. - 2021 - A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.79365079365079
    claim: "Across recommender reproducibility studies, missing details on data splits, hyperparameters, software dependencies, and configuration are repeatedly reported as barriers to credible comparison ."
    quote_candidate: "The hyperparameters and similarity measures are the same as for ItemKNN, plus a parameterw that controls the relative importance of the content features with respect to the collaborative features."
    secondary_score: 49.01960784313726
    secondary_quote: "To ensure the reproducibility of this study, we share all the data, the source code used for pre- processing, hyperparameter optimization, algorithms, and the evaluation as well as all hyperpa- rameter values and results online.5 3In case we encountered problems with the provided code, the data, or the reproduction of the results, we also contacted the authors for assistance."

## ferraro_automatic_2018
- title: Automatic playlist continuation using a hybrid recommender system combining features from text and audio
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ferraro et al. - 2018 - Automatic playlist continuation using a hybrid recommender system combining features from text and a.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.333333333333336
    claim: "A playlist with individually strong tracks can still feel poor if transitions are abrupt, artist repetition is excessive, or diversity disrupts coherence ."
    quote_candidate: "To this end, for each track in a playlis t we count the interactions with all other tracks within a tempor al win- dow including 10 previous and 10 posterior tracks."
    secondary_score: 51.77993527508091
    secondary_quote: "This means that when we need to continuate a playlist with a small number of se ed tracks (or no seed tracks at all), our model can make more accurate predictions."
  - claim_2_status: partially_supported
    score: 54.794520547945204
    claim: "Studies on playlist continuation consistently report tensions among coherence, novelty, diversity, and ordering ."
    quote_candidate: "Automatic playlist continuation using a hybrid recommend er system combining features from text and audio."
    secondary_score: 47.863247863247864
    secondary_quote: "The dataset contains one mi llion playlists created by the users of this service between Janua ry of 2010 and December of 2017."

## fkih_similarity_2022
- title: Similarity measures for Collaborative Filtering-based Recommender Systems: Review and experimental comparison
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\432\Fkih - 2022 - Similarity measures for Collaborative Filtering-based Recommender Systems Review and experimental c.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.833333333333336
    claim: "Similarity-measure choices, including metric definitions and threshold settings, can affect neighborhood selection and ranking behavior ."
    quote_candidate: "This process consists of three steps: similarity computation, neighborhood selection and rating prediction."
    secondary_score: 53.333333333333336
    secondary_quote: "As same as the User-based CF tech- nique, the Item-based CF process can be summarized into three steps: similarity computation, neighborhood selection and ratings prediction."
  - claim_2_status: partially_supported
    score: 51.724137931034484
    claim: "Similarity computation depends on explicit distance-function choices in feature space ."
    quote_candidate: "We mention that the similarity computation phase will be further detailed in Section 3."
    secondary_score: 51.64835164835165
    secondary_quote: "We have to mention that the similarity computation phase will be further detailed in Section 3."

## flexer_problem_2016
- title: The Problem of Limited Inter-rater Agreement in Modelling Music Similarity
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\401\Flexer and Grill - 2016 - The Problem of Limited Inter-rater Agreement in Modelling Music Similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 59.876543209876544
    claim: "Music-similarity research shows limited inter-rater agreement and sensitivity to framing, indicating that similarity estimates are useful approximations rather than objective truth ."
    quote_candidate: "Due to limited inter-rater agreement there exist upper bounds of performance in subjective evaluation of the respec- tive music similarity tasks."
    secondary_score: 58.333333333333336
    secondary_quote: "On inter-rater agreement in audio music similarity."

## furini_social_2024
- title: Social music discovery: an ethical recommendation system based on friend’s preferred songs
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\rp\files\577\Furini and Fragnelli - 2024 - Social music discovery an ethical recommendation system based on friend’s preferred songs.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Similarity computation depends on explicit distance-function choices in feature space ."
    quote_candidate: "The selection of analytical values to characterize each song in the listening history depends on the Fig."
    secondary_score: 47.863247863247864
    secondary_quote: "To compute the similarity, we measure the distance between the reference track and other songs in an 11- dimensional feature space, using the Euclidean distance metric."

## he_neural_2017
- title: Neural Collaborative Filtering
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\436\He et al. - 2017 - Neural Collaborative Filtering.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.37190082644628
    claim: "Hybrid and neural recommenders can deliver strong predictive performance and capture richer interactions ."
    quote_candidate: "First, we can see that with more iterations, the training loss of NCF models gradually decreases and the recommendation performance is improved."
    secondary_score: 54.148471615720524
    secondary_quote: "4.2 Performance Comparison (RQ1) Figure 4 shows the performance of HR@10 and NDCG@10 with respect to the number of predictive factors."

## herlocker_evaluating_2004
- title: Evaluating collaborative filtering recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Herlocker et al. - 2004 - Evaluating collaborative filtering recommender systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.06122448979592
    claim: "Recommender outcomes can be sensitive to protocol definitions, preprocessing choices, and metric framing ."
    quote_candidate: "On a ﬁve-point rating scale, are users sensitive to a change in mean absolute error of 0.01?"
    secondary_score: 48.4304932735426
    secondary_quote: "We explore when evaluation can be completed off-line using existing datasets and when it requires on-line experimentation."

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
  - claim_1_status: supported
    score: 75.67567567567568
    claim: "Controllability refers to explicit user controls that can steer the recommendation process ."
    quote_candidate: "Controllability often allows users to steer the recommendation process to obtain sug- gestions that are better suited to them (He et al."
    secondary_score: 60.301507537688444
    secondary_quote: "From this initial list of recommendations, users then select an item that represent their desired outcomes."
  - claim_2_status: partially_supported
    score: 56.69291338582677
    claim: "User control can improve experience, but effects vary by user characteristics and context ."
    quote_candidate: "However, a better understanding of the effects of personal characteristics in association with the three levels of user control on music recommender systems has yet to be realized."
    secondary_score: 53.333333333333336
    secondary_quote: "2.1.1 Level of experience Level of experience is one of the most commonly studied characteristics in the litera- ture (Toker et al."
  - claim_3_status: partially_supported
    score: 50.0
    claim: "Controls should be evaluated through measurable downstream effects, not only by whether interface controls are present ."
    quote_candidate: "123 Effects of personal characteristics in control-oriented… 205 this reason, we did not further study the effect of demographic characteristics in this paper."
    secondary_score: 49.23076923076923
    secondary_quote: "Items located on the intersections are recommended by more than one method."

## knijnenburg_explaining_2012
- title: Explaining the user experience of recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\422\Knijnenburg et al. - 2012 - Explaining the user experience of recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Interface research adds a practical constraint: faithful explanations still need to be understandable for non-expert users ."
    quote_candidate: "its interaction and presentation style) are perceived in terms of pragmatic attributes (i.e."
    secondary_score: 49.411764705882355
    secondary_quote: "Moreover, SSAs provide a more thorough understanding of how and why certain features of a recommender system affect the user experience."

## liu_multimodal_2025
- title: Multimodal Recommender Systems: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\411\Liu et al. - 2025 - Multimodal Recommender Systems A Survey.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.525252525252526
    claim: "Hybrid and neural recommenders can deliver strong predictive performance and capture richer interactions ."
    quote_candidate: "Filtering out noisy data in multimodal recommendation tasks can usually improve the recommendation performance."
    secondary_score: 52.01793721973094
    secondary_quote: "Leveraging the information exchange between users and items, users’ preferences for different modalities can be captured."

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
    score: 56.83453237410072
    claim: "Recommender systems are commonly described through three families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "For example, the paper by Adomavicius and Tuzhilin [3] presented an overview of content-based, collaborative ﬁltering-based, and hybrid recommendation approaches."
    secondary_score: 53.18352059925093
    secondary_quote: "In the e-library recommender systems discussed above, the hybrid recommendation approaches which combine CB, CF and/or KB tech- niques are widely used."

## mcfee_million_2012
- title: The million song dataset challenge
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\nw\files\570\McFee et al. - 2012 - The million song dataset challenge.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.717703349282296
    claim: "Challenge and benchmark analyses show that outcomes can depend on protocol and method composition ."
    quote_candidate: "We acknowledge that there are aspects that can not be measured from the play counts and a ranked list of pre- dictions."
    secondary_score: 49.7737556561086
    secondary_quote: "The choice of the cutoﬀ τ will depend on the minimum quality of the recommenders being evaluated, which we at- tempt to assess Section 5."

## moysis_music_2023
- title: Music Deep Learning: Deep Learning Methods for Music Signal Processing - A Review of the State-of-the-Art
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Moysis et al. - 2023 - Music Deep Learning Deep Learning Methods for Music Signal Processing—A Review of the State-of-the-.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.54639175257732
    claim: "Hybrid and neural recommenders can deliver strong predictive performance and capture richer interactions ."
    quote_candidate: "(10) In practice, the aforementioned procedure is performed in matrix form and is depicted in Fig."
    secondary_score: 51.041666666666664
    secondary_quote: "The model outperformed other architectures and was seconded only by the real music tracks."

## nauta_anecdotal_2023
- title: From Anecdotal Evidence to Quantitative Evaluation Methods: A Systematic Review on Evaluating Explainable AI
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\426\Nauta et al. - 2023 - From Anecdotal Evidence to Quantitative Evaluation Methods A Systematic Review on Evaluating Explai.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.61290322580645
    claim: "An explanation may increase trust or satisfaction without improving true user understanding ."
    quote_candidate: "complexity Key idea:Human-understandable concepts in the explanation Presentation Compactness Describes the size of the explanation."
    secondary_score: 50.602409638554214
    secondary_quote: "The inclusiveor indicates that an explanation can satisfy multiple goals."
  - claim_2_status: partially_supported
    score: 50.43478260869565
    claim: "Controls should be evaluated through measurable downstream effects, not only by whether interface controls are present ."
    quote_candidate: "We apply this filter to analyze how introduced XAI methods are evaluated when they are first presented (Section5)."
    secondary_score: 50.370370370370374
    secondary_quote: "We also found that explainability is indeed not a binary property, and that various aspects of an explanation should be evaluated independently of each other."

## neto_algorithmic_2023
- title: The algorithmic nature of song-sequencing: statistical regularities in music albums
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\403\Neto et al. - 2023 - The algorithmic nature of song-sequencing statistical regularities in music albums.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.19847328244275
    claim: "Sequencing analyses further highlight that music collections are perceived as ordered sequences rather than isolated items ."
    quote_candidate: "From sequences of movements to sequences of tracks The idea that music is globally perceived as a coher- ent sequence of acoustic events is a common one 412 P."
    secondary_score: 51.92307692307692
    secondary_quote: "If analysed together, these studies reveal that APG researchers generally agree upon the idea that a track is not perceived as an independent musical unit, but rather as a member of a broader context."

## pegoraro_santana_music4all_2020
- title: Music4All: A New Music Database and Its Applications
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Pegoraro Santana et al. - 2020 - Music4All A New Music Database and Its Applications.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 56.594724220623505
    claim: "Music4All is defensible here because it provides a multi-signal dataset with metadata, tags, lyrics, and audio-related attributes suitable for content-driven experimentation ."
    quote_candidate: "Aiming at contributing to the MIR community, in this paper we present Music4All, a new music database which contains metadata, tags, genre information, audio clips, lyrics, and so on which are essentials for the research and development of new digital music systems."
    secondary_score: 54.54545454545455
    secondary_quote: "In order to contribute to the MIR community, we present Music4AII, a new music database which contains metadata, tags, genre information, 30-seconds audio clips, lyrics, and so on."

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
    score: 55.65217391304348
    claim: "Foundational recommender literature frames the task as utility estimation under partial information: given sparse evidence about user preferences, infer which items are most likely to be useful ."
    quote_candidate: "The new items which are liked by most of the users in X are then recommended to user A."
    secondary_score: 53.439153439153436
    secondary_quote: "Finally, we provide researchers and practitioners with insight into the most promising directions for further investigation in the field of recommender systems under various applications."

## ru_improving_2023
- title: Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Perspective
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.42960288808664
    claim: "Independent third-party usage in multimodal music experiments provides additional context support, while task-transfer limits remain explicit ."
    quote_candidate: "In order to improve the performance of multi-label MGC, in addition to using the multi-modality nature of music, we can also start from the nature of the multi-label problem."
    secondary_score: 48.734177215189874
    secondary_quote: "In addition, it is notable that additional GCEM brings considerable improvement in the relevant abla- tion experiments, justifying the exploration of the correlation between genres."

## schedl_current_2018
- title: Current challenges and visions in music recommender systems research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\399\Schedl et al. - 2018 - Current challenges and visions in music recommender systems research.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Listening is often session-based and sequential, and users evaluate not only individual songs but also transitions, pacing, repetition, and overall flow ."
    quote_candidate: "in [92], in which users identiﬁed song order as being the second but last impor- tant criterion for playlist quality."
    secondary_score: 49.02723735408561
    secondary_quote: "High sparsity translates into low rating coverage, since most users tend to rate only a tiny fraction of items."
  - claim_2_status: partially_supported
    score: 56.33802816901409
    claim: "Playlist quality depends on treating playlists as sequences of tracks where order and transitions matter ."
    quote_candidate: "On the other hand, the authors argue that order does matter when creating playlists with tracks from the long tail."
    secondary_score: 52.72727272727273
    secondary_quote: "in [92], in which users identiﬁed song order as being the second but last impor- tant criterion for playlist quality."
  - claim_3_status: partially_supported
    score: 50.0
    claim: "Playlist constraints should be engineered explicitly ."
    quote_candidate: "This should be taken into account when building a MRS."
    secondary_score: 46.666666666666664
    secondary_quote: "Therefore, the cumulative gain for each user should be normalized."

## siedenburg_modeling_2017
- title: Modeling Timbre Similarity of Short Music Clips
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Siedenburg and Müllensiefen - 2017 - Modeling Timbre Similarity of Short Music Clips.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.60115606936416
    claim: "Music-similarity research shows limited inter-rater agreement and sensitivity to framing, indicating that similarity estimates are useful approximations rather than objective truth ."
    quote_candidate: "(2013) devised an individual diﬀerences test that investigates diﬀerences in t he ability to extract information from short audio clips and to u se it for similarity comparisons."
    secondary_score: 51.74418604651163
    secondary_quote: "A computational model is necessary in order to create a test that is adaptive and homes in on the individual participant’s ability level for judging sound similarities."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.94805194805195
    claim: "Recent explainability work in music models supports the same broader principle: explanations should expose contribution structure rather than only final outcomes ."
    quote_candidate: "Additionally, we provide global explanations by aggregating local explanations, offering a broader understanding of the model’s overall behavior."
    secondary_score: 50.3448275862069
    secondary_quote: "For text- based models, LIME assigns importance scores to individual words, indicating their contribution to the final prediction."

## teinemaa_composition_2018
- title: Automatic Playlist Continuation through a Composition of Collaborative Filters
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Teinemaa et al. - 2018 - Automatic Playlist Continuation through a Composition of Collaborative Filters.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.666666666666664
    claim: "Challenge and benchmark analyses show that outcomes can depend on protocol and method composition ."
    quote_candidate: "Table 3 shows the optimized best sets of weights separately for each category (used in the local weights composition) and global weights (used in the global weights composition)."
    secondary_score: 49.473684210526315
    secondary_quote: "Note that in all cases, the composed collaborative model performs better than the popularity model."
  - claim_2_status: partially_supported
    score: 54.074074074074076
    claim: "APC studies report that performance varies across model compositions and evaluation setups, so conclusions are tied to the selected protocol and metrics ."
    quote_candidate: "The model with local weights and album completion is the best performing model and was the selected strategy for our final submission."
    secondary_score: 52.5974025974026
    secondary_quote: "Section 4 further details the model optimization and selection procedures to combine the collaborative filers, and discusses some results on internal validation sets."

## tintarev_evaluating_2012
- title: Evaluating the effectiveness of explanations for recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\391\Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 60.450160771704184
    claim: "Explainable recommender research has long argued that predictive quality alone is not enough when users or evaluators need to understand and question system behavior ."
    quote_candidate: "So, an explanation can be an item description that helps the user to understand the qualities of the item well enough to decide whether it is relevant to them or not."
    secondary_score: 59.86842105263158
    secondary_quote: "For example, suppose that in a particular recommender system users tend to select item A when no explanations are present, and item B when explanations are present."
  - claim_2_status: partially_supported
    score: 52.79187817258883
    claim: "An explanation may increase trust or satisfaction without improving true user understanding ."
    quote_candidate: "An effective explanation may be formulated along the lines of “You might (not) like this item because…”."
    secondary_score: 51.47679324894515
    secondary_quote: "So, an explanation can be an item description that helps the user to understand the qualities of the item well enough to decide whether it is relevant to them or not."
  - claim_3_status: partially_supported
    score: 55.483870967741936
    claim: "Explanations should remain linked to recommendation logic as closely as possible ."
    quote_candidate: "We also did not use a real recommender algorithm to provide recommendations."
    secondary_score: 49.70414201183432
    secondary_quote: "Keywords Recommender systems · Metrics · Item descriptions · Explanations · Empirical studies N."

## tintarev_survey_2007
- title: A Survey of Explanations in Recommender Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\389\Tintarev and Masthoff - 2007 - A Survey of Explanations in Recommender Systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 57.42574257425743
    claim: "Explainable recommender research has long argued that predictive quality alone is not enough when users or evaluators need to understand and question system behavior ."
    quote_candidate: "We hope that the framework and survey presented in this paper will lead to more systematic research on explanations in recommender systems."
    secondary_score: 56.71641791044776
    secondary_quote: "The presence of longer descriptions of individual items has been found to be positively correlated with both the perceived usefulness and ease of use of the recommender system [31]."
  - claim_2_status: partially_supported
    score: 58.604651162790695
    claim: "Controllability refers to explicit user controls that can steer the recommendation process ."
    quote_candidate: "A recommender system can also offer recommendations in a social context, taking into account users that are similar to you."
    secondary_score: 56.38297872340426
    secondary_quote: "4.1 Top item Perhaps the simplest way to present a recommendation is by offering the user the best item."

## tsai_explaining_2018
- title: Explaining Social Recommendations to Casual Users: Design Principles and Opportunities
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\393\Tsai and Brusilovsky - 2018 - Explaining Social Recommendations to Casual Users Design Principles and Opportunities.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.30769230769231
    claim: "Interface research adds a practical constraint: faithful explanations still need to be understandable for non-expert users ."
    quote_candidate: "There is limited understanding of how to design the explanation interfaces in different explanatory goals for casual (non-expert) users."
    secondary_score: 49.6124031007752
    secondary_quote: "35% of respondents preferred to trust a system with reliable and informative explanations: a wrong explanation hurt the reliability (..."

## vall_feature-combination_2019
- title: Feature-combination hybrid recommender systems for automated music playlist continuation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Vall et al. - 2019 - Feature-combination hybrid recommender systems for automated music playlist continuation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "A playlist with individually strong tracks can still feel poor if transitions are abrupt, artist repetition is excessive, or diversity disrupts coherence ."
    quote_candidate: "For songs occurring in few training playlists, the recommendations predicted by CF could be boosted with content information."
    secondary_score: 49.645390070921984
    secondary_quote: "The majority of songs occur only in few playlists and, as a consequence, they are poorly represented by collaborative ﬁltering."
  - claim_2_status: partially_supported
    score: 53.266331658291456
    claim: "Studies on playlist continuation consistently report tensions among coherence, novelty, diversity, and ordering ."
    quote_candidate: "Our own previous works on music playlist continuation focused on two main research lines."
    secondary_score: 53.21888412017167
    secondary_quote: "Not strictly applied to music playlist continuation but to music understanding and recommendation in general, van den Oord et al."
  - claim_3_status: partially_supported
    score: 52.459016393442624
    claim: "Playlist constraints should be engineered explicitly ."
    quote_candidate: "This system should be used to recommend songs to stable user playlists."
    secondary_score: 48.78048780487805
    secondary_quote: "1 Playlist continuation as a matrix completion and expansion problem."

## yu_self_supervised_2024
- title: Self-Supervised Learning for Recommender Systems: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Self-Supervised_Learning_for_Recommender_Systems_A_Survey.pdf
- mapping_score: 66
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.94117647058823
    claim: "Hybrid and neural recommenders can deliver strong predictive performance and capture richer interactions ."
    quote_candidate: "The bidirectional training can bridge the gap between the reverse augmentation and the forward recommendation."
    secondary_score: 50.23255813953488
    secondary_quote: "iii) The self-supervised task is designed to enhance recom- mendation performance, rather than being an end goal."

## zamani_analysis_2019
- title: An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Continuation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zamani et al. - 2019 - An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Contin.pdf
- mapping_score: 100
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.208835341365464
    claim: "Studies on playlist continuation consistently report tensions among coherence, novelty, diversity, and ordering ."
    quote_candidate: "[46] have recently identified the task of automatic music playlist continuation as one of the grand challenges in music recommender systems research."
    secondary_score: 50.892857142857146
    secondary_quote: "As shown in the table, several teams took advantage of a two-stage architecture for the playlist continuation task."
  - claim_2_status: partially_supported
    score: 52.805280528052805
    claim: "APC studies report that performance varies across model compositions and evaluation setups, so conclusions are tied to the selected protocol and metrics ."
    quote_candidate: "Therefore, random tracks would provide more useful information to better understand the focus of the playlist, and thus more accurate APC performance is achieved."
    secondary_score: 52.51798561151079
    secondary_quote: "Among which, neural networks and matrix factorization models are notable that predict the tracks in a playlist, given its title."

## zhang_explainable_2020
- title: Explainable Recommendation: A Survey and New Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\387\Zhang and Chen - 2020 - Explainable Recommendation A Survey and New Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.93167701863354
    claim: "They can perform strongly at scale, especially with rich interaction histories, but they may reduce direct interpretability when decision logic is encoded in latent representations ."
    quote_candidate: "The explanations may either be post-hoc or directly come from an explainable model (also called interpretable or transparent model in some contexts)."
    secondary_score: 50.526315789473685
    secondary_quote: "In a broader sense, the explainability of AI systems was already a core discussion in the 1980s era of “old” or logical AI research, when knowledge-based systems predicted (or diagnosed) well but could not explain why."
  - claim_2_status: partially_supported
    score: 56.85279187817259
    claim: "Explainable recommender research has long argued that predictive quality alone is not enough when users or evaluators need to understand and question system behavior ."
    quote_candidate: "Explainable recommendation tries to address the problem of why: by providing explanations to users or system design- ers, it helps humans to understand why certain items are recommended by the algorithm, where the human can either be users or system designers."
    secondary_score: 56.15141955835962
    secondary_quote: "Signiﬁcant research eﬀorts in user behavior analysis and human- computer interaction community aim to understand how users interact with explanations."
  - claim_3_status: supported
    score: 65.41353383458647
    claim: "A further distinction is critical for thesis design: post-hoc explanations versus directly explainable or transparent models ."
    quote_candidate: "The explanations may either be post-hoc or directly come from an explainable model (also called interpretable or transparent model in some contexts)."
    secondary_score: 55.14705882352941
    secondary_quote: "The scope of explainable recommendation not only includes de- veloping transparent machine learning, information retrieval, or data mining models."
  - claim_4_status: partially_supported
    score: 53.84615384615385
    claim: "Explanations should remain linked to recommendation logic as closely as possible ."
    quote_candidate: "46 3.7 Rule Mining for Explainable Recommendation ."
    secondary_score: 53.25443786982248
    secondary_quote: "(2014a) deﬁned the explainable recommendationproblem, and proposed an Explicit Factor 1.3."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 57.534246575342465
    claim: "Across recommender reproducibility studies, missing details on data splits, hyperparameters, software dependencies, and configuration are repeatedly reported as barriers to credible comparison ."
    quote_candidate: "To promote reproducible research, our benchmark- ing work aims to record detailed hyper-parameter configurations for each experiment and demonstrate the reproducing steps."
    secondary_score: 55.78947368421053
    secondary_quote: "In many cases, the reported results cannot be easily reproduced due to the lack of either data preprocessing details, model implementations, hyper-parameter configurations, or even all of them."

## Summary
- total_claim_checks: 79
- supported: 4
- partially_supported: 75
- weak_support: 0
- no_match: 0