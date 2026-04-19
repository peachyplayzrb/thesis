# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `c:\Users\Timothy\Desktop\thesis-main\thesis-main\08_writing\chapter2.md` against extracted text from mapped local PDFs.
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
    score: 58.125
    claim: "Foundational recommender research frames this as utility estimation under partial information: from sparse preference evidence, infer which items are likely to be useful ."
    quote_candidate: "Intuitively, this estimation is usually based on the ratings given by this user to other items and on some other information that will be formally described below."
    secondary_score: 55.26315789473684
    secondary_quote: "It can be argued that the Grundy system [87] was the first recommender system, which proposed using stereotypes as a mechanism for building models of users based on a limited amount of information on each individual user."
  - claim_3_status: supported
    score: 84.26395939086294
    claim: "Recommender systems are usually grouped into three families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "Toward the Next Generation of Recommender Systems: A Survey of the State-of-the-Art and Possible Extensions Gediminas Adomavicius, Member , IEEE, and Alexander Tuzhilin, Member , IEEE Abstract—This paper presents an overview of the field of recommender systems and describes the current generation of recommendation methods that are usually classified into the following three main categories: content-based, collaborative, and hybrid recommendation approaches."
    secondary_score: 65.80086580086581
    secondary_quote: "Therefore, function uij clearly subsumes the collaborative, content-based, and hybrid methods discussed in Section 2."
  - claim_4_status: partially_supported
    score: 54.42176870748299
    claim: "They can perform very well at scale with rich histories, but direct interpretability may decrease when ranking logic is embedded in latent factors ."
    quote_candidate: "One problem with using the weighted sum, as in (10b), is that it does not take into account the fact that different users may use the rating scale differently."
    secondary_score: 48.669201520912544
    secondary_quote: "Once we can estimate ratings for the yet unrated items, we can recommend to the user the item(s) with the highest estimated rating(s)."

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
  - claim_2_status: partially_supported
    score: 50.57471264367816
    claim: "Alignment should report staged blocking/filtering and candidate-match paths ."
    quote_candidate: "Incremental record linkage In this section, we propose a blocking method for incremental record linkage."
    secondary_score: 48.80952380952381
    secondary_quote: "Record linkage In this paper, we consider su ﬃ x-based blocking methods for record linkage."

## andjelkovic_moodplay_2019
- title: Moodplay: Interactive music recommendation based on Artists' mood similarity
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.93258426966292
    claim: "User controls can improve experience, but effects vary by user profile and context ."
    quote_candidate: "Users construct proﬁles by entering names of artists via an interactive drop- down list ( Fig."
    secondary_score: 50.955414012738856
    secondary_quote: "In each of the conditions users create a proﬁle by entering artist names."

## anelli_elliot_2021
- title: Elliot: A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.55555555555556
    claim: "Recommender outcomes can vary substantially with protocol definitions, preprocessing decisions, and metric framing ."
    quote_candidate: "Bias in Search and Recommender Systems."
    secondary_score: 50.79365079365079
    secondary_quote: "Recommender systems with social regularization."
  - claim_2_status: weak_support
    score: 49.75124378109453
    claim: "Also, these dimensions are mostly tested with offline metrics, and those metrics do not always capture how listeners actually judge playlist quality, which makes direct method comparisons more difficult ."
    quote_candidate: "The simple_metrics field allows computing accuracy and beyond-accuracy metrics, with two top- 𝑘 cut-off values (5 and 10) by merely inserting the list of desired measures, e.g., [Precision, nDCG, ...] ."
    secondary_score: 48.43423799582463
    secondary_quote: "These dimensions are gaining attention, and several metrics addressing dif- ferent subtleties are being proposed, but no clear winner or standard definition emerged so far – as a consequence, the community lacks an established implementation of these novel evaluation dimensions."
  - claim_3_status: partially_supported
    score: 52.852852852852855
    claim: "Reproducibility literature reports recurring barriers: missing split details, incomplete hyperparameter reporting, hidden dependency constraints, and unclear configuration state ."
    quote_candidate: "Elliot is a comprehensive recommendation framework that aims to run and reproduce an entire experimental pipeline by processing a simple configuration file."
    secondary_score: 51.12359550561798
    secondary_quote: "It is worth noticing that, to the best of our knowledge,Elliot is the only framework able to run an extensive set of reproducible experiments by merely preparing a single configuration file."
  - claim_4_status: partially_supported
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
    score: 55.483870967741936
    claim: "Controllability means using explicit controls that can steer recommendation behaviour ."
    quote_candidate: "Users can then steer the recommendations by manipulating the tag clouds."
    secondary_score: 51.48514851485149
    secondary_quote: "Transparency provides insights into how the recommendation process works, and is closely related to explainability."

## barlaug_neural_2021
- title: Neural Networks for Entity Matching: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Barlaug and Gulla - 2021 - Neural Networks for Entity Matching A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 57.89473684210526
    claim: "Neural entity matching remains a relevant comparator ."
    quote_candidate: "CCS Concepts: •Computing methodologies→ Neural networks; Natural language processing;• Infor- mation systems→ Entity resolution; Additional Key Words and Phrases: Deep learning, entity matching, entity resolution, record linkage, data matching ACM Reference format: Nils Barlaug and Jon Atle Gulla."
    secondary_score: 54.54545454545455
    secondary_quote: "Neural Networks for Entity Matching: A Survey.ACM Trans."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 49.166666666666664
    claim: "Recommender outcomes can vary substantially with protocol definitions, preprocessing decisions, and metric framing ."
    quote_candidate: "Balog and Radlinski [11] propose how to measure the quality of explanations in ACM Transactions on Recommender Systems, Vol."
    secondary_score: 46.263345195729535
    secondary_quote: "They compare the reported results of baselines with the results obtained through a re-run of the base- lines, revealing substantial divergences, particularly for the MovieLens 10M dataset."
  - claim_2_status: weak_support
    score: 48.25581395348837
    claim: "Also, these dimensions are mostly tested with offline metrics, and those metrics do not always capture how listeners actually judge playlist quality, which makes direct method comparisons more difficult ."
    quote_candidate: "Finally, Diaz and Ferraro [37] makes a metrics analysis and discussion leading into the proposal of an altogether metric-free evaluation method."
    secondary_score: 47.745358090185675
    secondary_quote: "[14, 15] surveyed evaluation approaches in the field of research paper recommender systems and found that 69% of the papers featured an offline evaluation while 21% do not provide an evaluation."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.12328767123287
    claim: "Reproducibility literature reports recurring barriers: missing split details, incomplete hyperparameter reporting, hidden dependency constraints, and unclear configuration state ."
    quote_candidate: "It is understood that the data splitting strategy may have a deep impact on the final results, making this an impor- tant aspect to take into account when reporting details about an experiment."
    secondary_score: 45.925925925925924
    secondary_quote: "Our driv - ing hypothesis is that advances on reproducible environments for recommendation could provide better accountability of Recommender Systems research, understood as appropriate mechanisms for reporting evaluation results."

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
    score: 55.072463768115945
    claim: "A major advantage is mechanism visibility: when scoring relies on explicit features, recommendation rationales can often be traced to those features ."
    quote_candidate: "Therefore, we recoded the user’s ratings into 3 main categories, referring to the type of the recommendation: hits, fails, and trusts."
    secondary_score: 55.05226480836237
    secondary_quote: "Logan (2004) proposes to generate recommendations based on an explicitly given set of music tracks, which represent a user’s preferences."
  - claim_2_status: partially_supported
    score: 55.670103092783506
    claim: "The semantic gap sharpens this point: low-level computable features do not fully capture human concepts such as mood, nostalgia, or atmosphere ."
    quote_candidate: "We use the described low-level features to infer semantic descriptors."
    secondary_score: 55.4054054054054
    secondary_quote: "These approaches apply the same ideas as the proposed semantic approaches, but operate on low-level timbral features, frequently used in the related literature."
  - claim_3_status: partially_supported
    score: 54.804270462633454
    claim: "When profiles and candidate scores are built from explicit descriptors, the system can report what contributed to each decision and by how much ."
    quote_candidate: "These semantic descriptors are computed from an explicit set of music tracks deﬁned by a given user as evidence of her/his musical preferences."
    secondary_score: 53.51170568561873
    secondary_quote: "In the present work, we focus on music recommender systems and consider explicit strategies to in- fer musical preferences of a user directly from the music audio data."

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
  - claim_3_status: partially_supported
    score: 50.57471264367816
    claim: "APC studies also indicate that outcomes vary with model composition and evaluation setup ."
    quote_candidate: "Section 5) and that an optimized mixture of all models further enhances the results."
    secondary_score: 49.30232558139535
    secondary_quote: "[2012] include a bigram model smoothed with the Witten-Bell discounting [Jurafsky and Martin 2009] in a comparative evaluation."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.75438596491228
    claim: "Recommender systems are usually grouped into three families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "The ﬁrst com- puterized RS prototypes also applied a collaborative ﬁltering approach and emerged in mid 90s [6,7]."
    secondary_score: 50.38167938931298
    secondary_quote: "Recommender systems are software tools used to generate and provide suggestions for items and other entities to the users by exploiting various strategies."
  - claim_2_status: supported
    score: 83.33333333333333
    claim: "Hybrid systems combine strategies to exploit complementary strengths ."
    quote_candidate: "Hybrid recommender systems combine two or more recommendation strategies in differ- ent ways to beneﬁt from their complementary advantages."
    secondary_score: 58.13953488372093
    secondary_quote: "Keywords: Hybrid recommendations, recommender systems, systematic review, recommendation strategies 1."
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
    score: 50.303030303030305
    claim: "Reproducibility literature reports recurring barriers: missing split details, incomplete hyperparameter reporting, hidden dependency constraints, and unclear configuration state ."
    quote_candidate: "A Systematic Study on Reproducibility of RL in Recommendation Systems 11:3 source code is published, it is sometimes incomplete or does not work properly."
    secondary_score: 48.80636604774536
    secondary_quote: "The hardware configuration used to run the experiments is not provided either in the paper or in the GitHub repository, while the software dependencies are reported in 12https://github.com/jiaqima/Off-Policy-2-Stage."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.81526104417671
    claim: "A major advantage is mechanism visibility: when scoring relies on explicit features, recommendation rationales can often be traced to those features ."
    quote_candidate: "Therefore, the same vocabulary is used to steer the recommendation process and to explain recommendations."
    secondary_score: 53.68421052631579
    secondary_quote: "To compute recommendations, for instance, one can compute the dot product of the content representation and a learnt user feature vector, utilize the user and content features in a classifier to estimate a preference, or utilize an attention mechanism for per- sonalized content."
  - claim_2_status: partially_supported
    score: 51.26353790613718
    claim: "The semantic gap sharpens this point: low-level computable features do not fully capture human concepts such as mood, nostalgia, or atmosphere ."
    quote_candidate: "While the discussion of content-based music features is relevant to the survey at hand, the authors do not focus on MRS tasks and challenges."
    secondary_score: 49.25373134328358
    secondary_quote: "The authors design a content-based MRS leveraging audio features which are obtained from pre-trained self-supervised models."
  - claim_3_status: partially_supported
    score: 53.38345864661654
    claim: "When profiles and candidate scores are built from explicit descriptors, the system can report what contributed to each decision and by how much ."
    quote_candidate: "• W hat are the main challenges in MRS research and how can they be successfully approached by leveraging music content data?"
    secondary_score: 53.291536050156736
    secondary_quote: "Levels of content Within the recommender systems research community, the term content can be found to refer to a variety of data sources that can be accessed to derive features describing the items to be recommended."

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
  - claim_1_status: weak_support
    score: 49.035812672176306
    claim: "Reproducibility literature reports recurring barriers: missing split details, incomplete hyperparameter reporting, hidden dependency constraints, and unclear configuration state ."
    quote_candidate: "The hyperparameters and similarity measures are the same as for ItemKNN, plus a parameterw that controls the relative importance of the content features with respect to the collaborative features."
    secondary_score: 48.20846905537459
    secondary_quote: "A number of hyperparameters can be tuned for the method, including the number of latent factors, the confidence scaling and the regularization factor."

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
    score: 50.23696682464455
    claim: "Playlist continuation studies repeatedly show tension among coherence, novelty, diversity, and ordering ."
    quote_candidate: "Automatic playlist continuation using a hybrid recommend er system combining features from text and audio."
    secondary_score: 47.88732394366197
    secondary_quote: "This system consists in combining the recommendat ions produced by two diﬀerent models using ranking fusion."

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
    claim: "Music-similarity research reports limited inter-rater agreement and framing sensitivity, indicating that similarity estimates are useful approximations rather than objective truth ."
    quote_candidate: "On inter-rater agreement in audio music similarity."
    secondary_score: 58.204334365325074
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
  - claim_1_status: weak_support
    score: 48.148148148148145
    claim: "Recommender outcomes can vary substantially with protocol definitions, preprocessing decisions, and metric framing ."
    quote_candidate: "This is the core recommendation task and it recurs in a wide variety of research and commercial systems."
    secondary_score: 48.148148148148145
    secondary_quote: "Recommenders are usually evaluated based on how well they help the user make a consumption decision."

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
    score: 64.0625
    claim: "Controllability means using explicit controls that can steer recommendation behaviour ."
    quote_candidate: "Controllability often allows users to steer the recommendation process to obtain sug- gestions that are better suited to them (He et al."
    secondary_score: 53.55191256830601
    secondary_quote: "Having more control can increase users’ per- ceived quality of recommendations (O’Donovan et al."
  - claim_2_status: weak_support
    score: 48.36065573770492
    claim: "User controls can improve experience, but effects vary by user profile and context ."
    quote_candidate: "RQ3: How does the complexity of the user interface (user controls / visualizations) inﬂuence user perception of recommendations (diversity, acceptance, and cognitive load)?"
    secondary_score: 48.275862068965516
    secondary_quote: "Personality traits can affect the performance and preference of a user (Aykin and Aykin 1991)."
  - claim_3_status: partially_supported
    score: 53.142857142857146
    claim: "Explanations should stay tightly linked to recommendation logic , and controls should be assessed through measurable downstream effects rather than interface presence alone ."
    quote_candidate: "RQ2: How do personal characteristicsmoderate the effect of the user interface (user controls / visualizations) on user perception of recommendations (diversity, accep- tance, and cognitive load)?"
    secondary_score: 52.976190476190474
    secondary_quote: "As a result, it may be more meaningful to recommend songs that ﬁt user’s temporal preferences and context rather than show- ing songs based on user search requests (Lee et al."

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
    score: 56.61764705882353
    claim: "Recommender systems are usually grouped into three families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "For example, the paper by Adomavicius and Tuzhilin [3] presented an overview of content-based, collaborative ﬁltering-based, and hybrid recommendation approaches."
    secondary_score: 53.63984674329502
    secondary_quote: "In the e-library recommender systems discussed above, the hybrid recommendation approaches which combine CB, CF and/or KB tech- niques are widely used."

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
  - claim_2_status: weak_support
    score: 47.50733137829912
    claim: "Explanations should stay tightly linked to recommendation logic , and controls should be assessed through measurable downstream effects rather than interface presence alone ."
    quote_candidate: "Many authors (e.g., [2, 111, 134, 143]) argue that relying on such anecdotal evidence alone is insufficient and that other aspects of the explanations should be evaluated as well."
    secondary_score: 47.20496894409938
    secondary_quote: "Letf be a predictive machine learning model, such as a neural network or decision tree, trained to take some data as input and predict the corresponding output."

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
    score: 55.063291139240505
    claim: "Foundational recommender research frames this as utility estimation under partial information: from sparse preference evidence, infer which items are likely to be useful ."
    quote_candidate: "In essence, recommender systems deal with two entities—users and items, where each user gives a rating (or preference value) to an item (or product)."
    secondary_score: 54.74860335195531
    secondary_quote: "Therefore, to make recommendations for a new user, the user profile must be added to the utility matrix, and the similarity matrix should be rec - omputed, which makes this technique computation heavy."

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
  - claim_3_status: partially_supported
    score: 50.0
    claim: "Playlist constraints should be explicitly engineered ."
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
    score: 51.01449275362319
    claim: "Music-similarity research reports limited inter-rater agreement and framing sensitivity, indicating that similarity estimates are useful approximations rather than objective truth ."
    quote_candidate: "(2013) devised an individual diﬀerences test that investigates diﬀerences in t he ability to extract information from short audio clips and to u se it for similarity comparisons."
    secondary_score: 50.72886297376093
    secondary_quote: "A computational model is necessary in order to create a test that is adaptive and homes in on the individual participant’s ability level for judging sound similarities."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.498338870431894
    claim: "Recent explainability work in music models supports the same broader principle: explanations should expose contribution structure, not only final outcomes ."
    quote_candidate: "Additionally, we provide global explanations by aggregating local explanations, offering a broader understanding of the model’s overall behavior."
    secondary_score: 50.41551246537396
    secondary_quote: "While existing XAI methods have advanced explainability in the music domain, there is a notable gap in approaches tailored to multimodal models, particularly in music, which combines both audio and lyrical data."

## teinemaa_composition_2018
- title: Automatic Playlist Continuation through a Composition of Collaborative Filters
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Teinemaa et al. - 2018 - Automatic Playlist Continuation through a Composition of Collaborative Filters.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.717514124293785
    claim: "Reported improvements depend on protocol choices and method composition ."
    quote_candidate: "Section 3 describes the proposed framework based on several collaborative filters and their combination."
    secondary_score: 46.35761589403973
    secondary_quote: "Results This subsection presents and discusses the results of our experiments."
  - claim_2_status: partially_supported
    score: 53.333333333333336
    claim: "APC studies also indicate that outcomes vary with model composition and evaluation setup ."
    quote_candidate: "The model with local weights and album completion is the best performing model and was the selected strategy for our final submission."
    secondary_score: 49.09090909090909
    secondary_quote: "Table 3 shows the optimized best sets of weights separately for each category (used in the local weights composition) and global weights (used in the global weights composition)."

## tintarev_evaluating_2012
- title: Evaluating the effectiveness of explanations for recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\391\Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 58.63192182410423
    claim: "Explainable recommender research has long argued that predictive quality alone is insufficient when users or evaluators need to understand and question system behaviour ."
    quote_candidate: "For example, suppose that in a particular recommender system users tend to select item A when no explanations are present, and item B when explanations are present."
    secondary_score: 56.05095541401274
    secondary_quote: "So, an explanation can be an item description that helps the user to understand the qualities of the item well enough to decide whether it is relevant to them or not."
  - claim_2_status: partially_supported
    score: 50.0
    claim: "Explanations may increase trust or satisfaction without improving genuine understanding ."
    quote_candidate: "We mea- sure objective effectiveness, as perceived effectiveness may overlap with satisfaction."
    secondary_score: 49.75124378109453
    secondary_quote: "Contrary to expectation, personalization was detrimental to effectiveness, though it may improve user satisfaction."
  - claim_3_status: partially_supported
    score: 59.01639344262295
    claim: "Explanations should stay tightly linked to recommendation logic , and controls should be assessed through measurable downstream effects rather than interface presence alone ."
    quote_candidate: "recommendation algorithm and explanations)."
    secondary_score: 52.84090909090909
    secondary_quote: "These metrics can be inﬂuenced by more than just the recommendations, such as by explanations, the way recommendations are presented, and the method of interacting with recommendations ( Tintarev and Masthoff 2010 )."

## tintarev_survey_2007
- title: A Survey of Explanations in Recommender Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\389\Tintarev and Masthoff - 2007 - A Survey of Explanations in Recommender Systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 56.86274509803921
    claim: "Explainable recommender research has long argued that predictive quality alone is insufficient when users or evaluators need to understand and question system behaviour ."
    quote_candidate: "We hope that the framework and survey presented in this paper will lead to more systematic research on explanations in recommender systems."
    secondary_score: 56.80473372781065
    secondary_quote: "The presence of longer descriptions of individual items has been found to be positively correlated with both the perceived usefulness and ease of use of the recommender system [31]."
  - claim_2_status: partially_supported
    score: 54.651162790697676
    claim: "Controllability means using explicit controls that can steer recommendation behaviour ."
    quote_candidate: "Consumer behavior in the inter- action with knowledge-based recommender applications."
    secondary_score: 53.25443786982248
    secondary_quote: "We do not claim that explanations can fully compen- sate for poor recommendations."

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
    score: 54.02298850574713
    claim: "Playlist continuation studies repeatedly show tension among coherence, novelty, diversity, and ordering ."
    quote_candidate: "1 Playlist continuation as a matrix completion and expansion problem."
    secondary_score: 53.84615384615385
    secondary_quote: "Sections 4 and 5 describe the proposed systems and the baselines for music playlist continuation, respectively."
  - claim_3_status: partially_supported
    score: 52.459016393442624
    claim: "Playlist constraints should be explicitly engineered ."
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
    score: 49.79253112033195
    claim: "Playlist continuation studies repeatedly show tension among coherence, novelty, diversity, and ordering ."
    quote_candidate: "[46] have recently identified the task of automatic music playlist continuation as one of the grand challenges in music recommender systems research."
    secondary_score: 49.074074074074076
    secondary_quote: "As shown in the table, several teams took advantage of a two-stage architecture for the playlist continuation task."
  - claim_2_status: weak_support
    score: 49.54128440366973
    claim: "APC studies also indicate that outcomes vary with model composition and evaluation setup ."
    quote_candidate: "Among which, neural networks and matrix factorization models are notable that predict the tracks in a playlist, given its title."
    secondary_score: 46.32768361581921
    secondary_quote: "This is due to the error of our evaluation script, which has been solved on 2018-06-01."

## zhang_explainable_2020
- title: Explainable Recommendation: A Survey and New Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\387\Zhang and Chen - 2020 - Explainable Recommendation A Survey and New Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "They can perform very well at scale with rich histories, but direct interpretability may decrease when ranking logic is embedded in latent factors ."
    quote_candidate: "The explanations may either be post-hoc or directly come from an explainable model (also called interpretable or transparent model in some contexts)."
    secondary_score: 47.39884393063584
    secondary_quote: "In a broader sense, the explainability of AI systems was already a core discussion in the 1980s era of “old” or logical AI research, when knowledge-based systems predicted (or diagnosed) well but could not explain why."
  - claim_2_status: partially_supported
    score: 57.43073047858942
    claim: "Explainable recommender research has long argued that predictive quality alone is insufficient when users or evaluators need to understand and question system behaviour ."
    quote_candidate: "Explainable recommendation tries to address the problem of why: by providing explanations to users or system design- ers, it helps humans to understand why certain items are recommended by the algorithm, where the human can either be users or system designers."
    secondary_score: 54.889589905362776
    secondary_quote: "With this section, we will introduce not only the explainable recom- mendation problem, but also a big picture of the recommender system research area."
  - claim_3_status: partially_supported
    score: 53.211009174311926
    claim: "A related distinction concerns post-hoc versus directly explainable mechanisms ."
    quote_candidate: "The explanations may either be post-hoc or directly come from an explainable model (also called interpretable or transparent model in some contexts)."
    secondary_score: 51.36612021857923
    secondary_quote: "Classiﬁcation of the Methods 9 T able 1.1: A classiﬁcation of existing explainable recommendation methods."
  - claim_4_status: partially_supported
    score: 50.98039215686274
    claim: "Explanations should stay tightly linked to recommendation logic , and controls should be assessed through measurable downstream effects rather than interface presence alone ."
    quote_candidate: "Explainable recommendation helps to improve the transparency, persuasiveness, eﬀective- ness, trustworthiness, and satisfaction of recommendation systems."
    secondary_score: 50.90909090909091
    secondary_quote: "It will help readers to understand what is unique about the explainable recommendation problem, what is the position of ex- plainable recommendation in the research area, and why explainable recommendation is important to the area."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.794520547945204
    claim: "Reproducibility literature reports recurring barriers: missing split details, incomplete hyperparameter reporting, hidden dependency constraints, and unclear configuration state ."
    quote_candidate: "In many cases, the reported results cannot be easily reproduced due to the lack of either data preprocessing details, model implementations, hyper-parameter configurations, or even all of them."
    secondary_score: 54.285714285714285
    secondary_quote: "To promote reproducible research, our benchmark- ing work aims to record detailed hyper-parameter configurations for each experiment and demonstrate the reproducing steps."

## Summary
- total_claim_checks: 82
- supported: 2
- partially_supported: 61
- weak_support: 19
- no_match: 0