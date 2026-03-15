# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `08_writing/chatper2_final draft.md` against extracted text from mapped local PDFs.
Method note: automated lexical matching (RapidFuzz token-set ratio) with manual thresholding.

## adomavicius_toward_2005
- title: Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\381\Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.68627450980392
    claim: "Recommender systems emerged as a practical response to this information-overload problem by helping users discover items they are likely to value ."
    quote_candidate: "However, items that users choose to rate are likely to constitute a skewed sample, e.g., users may rate mostly the items that they like."
    secondary_score: 53.71024734982332
    secondary_quote: "In its most common formulation, the recommendation problem is reduced to the problem of estimating ratings for the items that have not been seen by a user."
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
    score: 53.73134328358209
    claim: "Interface research adds a practical constraint: faithful explanations still need to be understandable for non-expert users ."
    quote_candidate: "It is worth noting that a bad explanation for trust may fail to create trust."
    secondary_score: 52.20338983050848
    secondary_quote: "Their automated method operates by leveraging existing guidelines and incorporating user feedback to bridge the gap between research transparency and practical explainability."

## allam_improved_2018
- title: Improved suffix blocking for record linkage and entity resolution
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Allam et al. - 2018 - Improved suffix blocking for record linkage and entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Entity-resolution research supports blocking, filtering, and staged matching workflows as practical approaches for large-scale linkage ."
    quote_candidate: "In Section 4, we present a novel blocking method for incremental record linkage."
    secondary_score: 49.09090909090909
    secondary_quote: "These methods are per- formed in two stages, namely a blocking and a comparison stage."
  - claim_2_status: partially_supported
    score: 52.68292682926829
    claim: "Alignment should use staged blocking and filtering practices with explicit uncertainty reporting ."
    quote_candidate: "Given a dataset D, let L be the set of actual linked record pairs in D and let R be the set of record pairs that result in by the blocking stage."
    secondary_score: 49.760765550239235
    secondary_quote: "The selection of the blocking keys and parameter values are determined by experiments on a sample of records [ 4]."

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
    score: 57.142857142857146
    claim: "Reproducibility literature in recommender systems reinforces the same governance principle: weak reporting of protocol, preprocessing, and configuration can undermine claim credibility ."
    quote_candidate: "Reproducibility is the keystone of modern RSs research."
    secondary_score: 50.588235294117645
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
    score: 53.90070921985816
    claim: "Controllability refers to user influence through explicit inputs or parameters ."
    quote_candidate: "” We refer to Table 1 for the notation used throughout the paper."
    secondary_score: 51.49700598802395
    secondary_quote: "That is, the user can explicitly state a positive or negative preference for a given tag."

## barlaug_neural_2021
- title: Neural Networks for Entity Matching: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Barlaug and Gulla - 2021 - Neural Networks for Entity Matching A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.0
    claim: "Neural entity-matching work is relevant comparator context and can improve difficult cases ."
    quote_candidate: "—How can we categorize the different deep neural networks used for entity matching?"
    secondary_score: 47.77777777777778
    secondary_quote: "Neural Networks for Entity Matching: A Survey 52:3 different aspects of entity matching."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.81967213114754
    claim: "Recommender outcomes can be sensitive to protocol definitions, preprocessing choices, and metric framing ."
    quote_candidate: "Typical pre-processing steps include removing users, items, or sessions with a low number of ACM Transactions on Recommender Systems, Vol."
    secondary_score: 50.43478260869565
    secondary_quote: "Balog and Radlinski [11] propose how to measure the quality of explanations in ACM Transactions on Recommender Systems, Vol."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.19277108433735
    claim: "This can strengthen debugging clarity, support sensitivity analysis, and improve evidence quality because observed output changes can be attributed to explicit parameter changes ."
    quote_candidate: "2019), and in some cases the attempts have to be discarded because inquir - ies sent to the original authors related to code or data remain unanswered (Fer - rari Dacrema et al."
    secondary_score: 48.13559322033898
    secondary_quote: "In this toy example, we observe how the similarity score between users changes depending on how the users’ average ratings are computed."
  - claim_2_status: partially_supported
    score: 56.14035087719298
    claim: "Reproducibility literature in recommender systems reinforces the same governance principle: weak reporting of protocol, preprocessing, and configuration can undermine claim credibility ."
    quote_candidate: "4.1.2 Data splitting The data splitting procedure, taking place before recommendation, is an important step in the experimental configuration of a recommender system."
    secondary_score: 53.36927223719677
    secondary_quote: "This work surveys existing definitions of these concepts and proposes a coherent terminol- ogy for recommender systems research, with the goal to connect reproducibility to accountability."

## binette_almost_2022
- title: (Almost) all of entity resolution
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Binette and Steorts - 2022 - (Almost) all of entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 56.2043795620438
    claim: "Entity-resolution research supports blocking, filtering, and staged matching workflows as practical approaches for large-scale linkage ."
    quote_candidate: "Rahm, Privacy-preserving record linkage for big data: Current approaches and research challenges, in Handbook of Big Data Technologies, A."
    secondary_score: 52.29681978798587
    secondary_quote: "In the remainder of our discussion, we highlight a few remaining topics that are the subject of active research and that have important practical implications."

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
    secondary_score: 54.91525423728814
    secondary_quote: "It should be noted that the same representation can be achieved if all normalized descriptor value s are set to 0.5 meaning no preference to any descriptor at all."

## bonnin_automated_2015
- title: Automated Generation of Music Playlists: Survey and Experiments
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 57.89473684210526
    claim: "This matters because playlist quality is a sequence property as much as it is an item-relevance property ."
    quote_candidate: "A playlist is a sequence of tracks (audio recordings)."
    secondary_score: 53.96825396825397
    secondary_quote: "As evaluation measures of playlist quality, we use hit rates and the average log like- lihood ALL."
  - claim_2_status: partially_supported
    score: 54.255319148936174
    claim: "Challenge and benchmark analyses show that outcomes can depend on protocol and method composition ."
    quote_candidate: "In the literature, two measures and protocols can be found that are based on such a strategy."
    secondary_score: 51.0
    secondary_quote: "3Notice that frequent pattern mining approaches can also be considered as statistical estimation methods."
  - claim_3_status: weak_support
    score: 49.152542372881356
    claim: "Playlist-level and APC evidence also indicates that protocol and metric framing can shift comparative conclusions ."
    quote_candidate: "[2012] include a bigram model smoothed with the Witten-Bell discounting [Jurafsky and Martin 2009] in a comparative evaluation."
    secondary_score: 49.01960784313726
    secondary_quote: "In the literature, two measures and protocols can be found that are based on such a strategy."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 58.71559633027523
    claim: "Recommender systems are commonly described through three families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "Reclusive methods are complementary to collaborative methods and are often combined with them to form hybrid RSs."
    secondary_score: 51.282051282051285
    secondary_quote: "The ﬁrst com- puterized RS prototypes also applied a collaborative ﬁltering approach and emerged in mid 90s [6,7]."
  - claim_2_status: partially_supported
    score: 53.7037037037037
    claim: "Hybrid approaches combine multiple signals and are often effective because they reduce weaknesses of single-family methods ."
    quote_candidate: "However, this systems are sensitive to the strengths and weaknesses of the composing techniques."
    secondary_score: 52.252252252252255
    secondary_quote: "Reclusive methods are complementary to collaborative methods and are often combined with them to form hybrid RSs."
  - claim_3_status: partially_supported
    score: 55.89519650655022
    claim: "Hybrid and neural recommenders can deliver strong predictive performance and capture richer interactions ."
    quote_candidate: "They illustrate their method by recommending hotels from TripAdvisor 4 and report performance improvements over traditional CF."
    secondary_score: 53.097345132743364
    secondary_quote: "The authors report that the integrated collaborative content has a signiﬁcant positive effect on recommendation performance."

## cavenaghi_systematic_2023
- title: A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Cavenaghi et al. - 2023 - A Systematic Study on Reproducibility of Reinforcement Learning in Recommendation Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.25816023738872
    claim: "Reproducibility literature in recommender systems reinforces the same governance principle: weak reporting of protocol, preprocessing, and configuration can undermine claim credibility ."
    quote_candidate: "A Systematic Study on Reproducibility of RL in Recommendation Systems 11:3 source code is published, it is sometimes incomplete or does not work properly."
    secondary_score: 48.50299401197605
    secondary_quote: "We found that the main missingness in the studied papers concerned the sharing of hardware configuration, software dependencies, and hyperparameters values."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 57.46268656716418
    claim: "A key strength is mechanism visibility: when the model relies on explicit features, recommendations can often be explained through those same features ."
    quote_candidate: "46 All of the target user’s features are concatenated and fed into a relevance classifier to create recommendations."
    secondary_score: 55.46875
    secondary_quote: "Here, some features in the onion model can be seen as more sensitive than others when considering items."
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
    score: 52.06349206349206
    claim: "Entity-resolution research supports blocking, filtering, and staged matching workflows as practical approaches for large-scale linkage ."
    quote_candidate: "A promising direction for future research is to devise techniques that can substantially improve the efficiency of approaches that rely on machine learning and probabilistic inference."
    secondary_score: 50.427350427350426
    secondary_quote: "This category includes (some) probabilistic approaches and supervised machine learning techniques."

## ferrari_dacrema_troubling_2021
- title: A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ferrari Dacrema et al. - 2021 - A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.863247863247864
    claim: "Recommender outcomes can be sensitive to protocol definitions, preprocessing choices, and metric framing ."
    quote_candidate: "A number of hyperparameters can be tuned for the method, including the number of latent factors, the confidence scaling and the regularization factor."
    secondary_score: 47.29064039408867
    secondary_quote: "A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research 20:15 Fig.2."
  - claim_2_status: partially_supported
    score: 50.70422535211268
    claim: "Reproducibility literature in recommender systems reinforces the same governance principle: weak reporting of protocol, preprocessing, and configuration can undermine claim credibility ."
    quote_candidate: "In pre-neural times, such comparisons were often enabled by the use of recommender systems libraries like MyMediaLite39 or LibRec,40 which also included evaluation code."
    secondary_score: 50.495049504950494
    secondary_quote: "Regarding the choice of the baselines, we found that in some cases researchers reuse the ex- perimental design that was used in previous studies, i.e., they use the same datasets, evaluation protocol, and metrics, to demonstrate progress."

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
    secondary_score: 51.68539325842696
    secondary_quote: "Will a metric be sensitive enough to detect real differences that exist?"

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
    score: 53.93258426966292
    claim: "Controllability refers to user influence through explicit inputs or parameters ."
    quote_candidate: "Interactions with the third component, algorithm parameters, grant users with con- trol over the algorithm."
    secondary_score: 48.958333333333336
    secondary_quote: "The circles at the connection points represent input entities such as other users, recom- mender agents or tags."
  - claim_2_status: partially_supported
    score: 56.69291338582677
    claim: "User control can improve experience, but effects vary by user characteristics and context ."
    quote_candidate: "However, a better understanding of the effects of personal characteristics in association with the three levels of user control on music recommender systems has yet to be realized."
    secondary_score: 53.333333333333336
    secondary_quote: "2.1.1 Level of experience Level of experience is one of the most commonly studied characteristics in the litera- ture (Toker et al."
  - claim_3_status: weak_support
    score: 49.523809523809526
    claim: "Controls should be judged by interpretable downstream effect rather than by interface presence alone ."
    quote_candidate: "3.2.4 Independent variables In each experiment, we varied the interface where users interact with recommenders."
    secondary_score: 48.83720930232558
    secondary_quote: "Based on the interactive recommendation framework proposed by Chen et al."

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

## liu_aggregating_2025
- title: Aggregating Contextual Information for Multi-Criteria Online Music Recommendations
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Liu - 2025 - Aggregating Contextual Information for Multi-Criteria Online Music Recommendations.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.96153846153846
    claim: "User control can improve experience, but effects vary by user characteristics and context ."
    quote_candidate: "Zaina, ‘‘From user context to tailored playlists: A user centered approach to improve music recommendation system,’’ in Proc."
    secondary_score: 49.549549549549546
    secondary_quote: "Diversity is crucial to avoid nar- rowing the user experience, thereby enhancing engagement by presenting a broad range of options."

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
    secondary_score: 54.140127388535035
    secondary_quote: "Peleteiro, A hybrid content-based and item-based collaborative ﬁltering approach to recommend TV programs enhanced with singular value de- composition, Information Sciences 180 (2010) 4290–4311."

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
    score: 51.724137931034484
    claim: "An explanation may increase trust or satisfaction without improving true user understanding ."
    quote_candidate: "[202] use a random forest and compare the explanation ACM Computing Surveys, Vol."
    secondary_score: 51.61290322580645
    secondary_quote: "complexity Key idea:Human-understandable concepts in the explanation Presentation Compactness Describes the size of the explanation."
  - claim_2_status: weak_support
    score: 48.484848484848484
    claim: "Controls should be judged by interpretable downstream effect rather than by interface presence alone ."
    quote_candidate: "A feature is not necessarily an input feature to predictive model f, but it should be a feature in the explanation."
    secondary_score: 46.82539682539682
    secondary_quote: "Those terms, together withexplainability and interpretability (and to some extent alsointelligibility) are often used interchangeably [29,32,93,167,172]."

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
    secondary_score: 53.278688524590166
    secondary_quote: "W i t ho u rc o m p u t a t i o n a la p p r o a c h ,w eh a v en od i r e c t means for drawing conclusions about how album- sequences are perceived."

## papadakis_blocking_2021
- title: Blocking and Filtering Techniques for Entity Resolution: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Papadakis et al. - 2021 - Blocking and Filtering Techniques for Entity Resolution A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.708487084870846
    claim: "Entity-resolution research supports blocking, filtering, and staged matching workflows as practical approaches for large-scale linkage ."
    quote_candidate: "Entities sharing the same output for a particular blocking predicate are considered candidate matches (i.e., hash-based functionality)."
    secondary_score: 46.79245283018868
    secondary_quote: "The task of Entity Resolu- tion (ER) is to find all matching entities within an entity collection or across two or more entity collections."
  - claim_2_status: partially_supported
    score: 51.707317073170735
    claim: "Alignment should use staged blocking and filtering practices with explicit uncertainty reporting ."
    quote_candidate: "Their most important parameter is the definition of the blocking keys, which requires fine-tuning by an expert."
    secondary_score: 51.30890052356021
    secondary_quote: "The ER process terminates when all blocks have been processed without finding new duplicates."

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
    secondary_score: 49.66442953020134
    secondary_quote: "This deﬁnition accounts for the individual differences in people’s emotional, interper- sonal, experiential, attitudinal, and motivational styles [ 95]."
  - claim_2_status: weak_support
    score: 49.729729729729726
    claim: "This matters because playlist quality is a sequence property as much as it is an item-relevance property ."
    quote_candidate: "This can be highly beneﬁcial and increase the chance of acquiring ratings of higher quality [57]."
    secondary_score: 49.51456310679612
    secondary_quote: "This vector describes aspects such as spectral patterns, recurring beats, and correlations between frequency bands."
  - claim_3_status: partially_supported
    score: 50.0
    claim: "Playlist constraints should be engineered explicitly ."
    quote_candidate: "This should be taken into account when building a MRS."
    secondary_score: 47.61904761904762
    secondary_quote: "An analysis of music listening behavior in context."

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
  - claim_2_status: weak_support
    score: 48.372093023255815
    claim: "Playlist-level and APC evidence also indicates that protocol and metric framing can shift comparative conclusions ."
    quote_candidate: "Section 3 describes the proposed framework based on several collaborative filters and their combination."
    secondary_score: 47.57281553398058
    secondary_quote: "Note that in all cases, the composed collaborative model performs better than the popularity model."

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
    score: 54.976303317535546
    claim: "An explanation may increase trust or satisfaction without improving true user understanding ."
    quote_candidate: "This suggests that explanations such as our baseline without cover images could damage user satisfaction considerably."
    secondary_score: 53.59477124183007
    secondary_quote: "Are users more satisﬁed with personalized explanations (H2)?"
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
    score: 55.34591194968554
    claim: "Controllability refers to user influence through explicit inputs or parameters ."
    quote_candidate: "Rating may be explicitly inputted by the user, or inferred from usage patterns."
    secondary_score: 53.01204819277108
    secondary_quote: "Scrutability is related to the established us- ability principle of User Control [25]."

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
    score: 52.3961661341853
    claim: "A playlist with individually strong tracks can still feel poor if transitions are abrupt, artist repetition is excessive, or diversity disrupts coherence ."
    quote_candidate: "The songs that are not present in the MSD are dropped from both playlist collections because we can not extract feature vectors without their song-level descriptions."
    secondary_score: 50.88339222614841
    secondary_quote: "For the strong generalization setting, we split each playlist collection into 5 disjoint sub-collections for cross val- idation."
  - claim_2_status: partially_supported
    score: 54.29864253393665
    claim: "Studies on playlist continuation consistently report tensions among coherence, novelty, diversity, and ordering ."
    quote_candidate: "We believe that either approach conditions the type of patterns that playlist continuation systems will identify."
    secondary_score: 54.08163265306123
    secondary_quote: "The playlists in the collection P are used to train a playlist continuation system."
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
    score: 55.04587155963303
    claim: "Hybrid and neural recommenders can deliver strong predictive performance and capture richer interactions ."
    quote_candidate: "His research interests include data min- ing, recommender systems, user behavior modelling and predictive analytics."
    secondary_score: 54.629629629629626
    secondary_quote: "In contrast, predictive SSR methods in this scenario are disappointing and even drastically lower the performance."

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
  - claim_2_status: weak_support
    score: 46.829268292682926
    claim: "Playlist-level and APC evidence also indicates that protocol and metric framing can shift comparative conclusions ."
    quote_candidate: "The results also demonstrate that ACM Transactions on Intelligent Systems and Technology, Vol."
    secondary_score: 46.666666666666664
    secondary_quote: "However, the two-stage architecture can also improve the APC performance."

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
  - claim_3_status: partially_supported
    score: 51.141552511415526
    claim: "A further distinction is critical for thesis design: post-hoc explanation versus transparency-by-design ."
    quote_candidate: "A conventional paradigm for feature-based explanation is to show users with the features that match the user’s proﬁle."
    secondary_score: 48.16326530612245
    secondary_quote: "The explanations may either be post-hoc or directly come from an explainable model (also called interpretable or transparent model in some contexts)."
  - claim_4_status: partially_supported
    score: 57.142857142857146
    claim: "Explanations should remain linked to recommendation logic as closely as possible ."
    quote_candidate: "Figure 2.1 shows several representative recommendation explanations."
    secondary_score: 57.0
    secondary_quote: "2.2 Feature-based Explanation The feature-based explanation is closely related to content-based rec- ommendation methods."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 61.15702479338843
    claim: "Reproducibility literature in recommender systems reinforces the same governance principle: weak reporting of protocol, preprocessing, and configuration can undermine claim credibility ."
    quote_candidate: "7 CONCLUSION Reproducibility is an open issue in the field of recommender sys- tems."
    secondary_score: 54.36893203883495
    secondary_quote: "In Proceedings of the International Workshop on Reproducibility and Replication in Recommender Systems Evaluation (RepSys)."

## Summary
- total_claim_checks: 84
- supported: 1
- partially_supported: 72
- weak_support: 11
- no_match: 0