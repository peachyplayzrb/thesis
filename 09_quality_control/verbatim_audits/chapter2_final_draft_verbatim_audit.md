# Chapter 2 Verbatim Claim Audit

Scope: sentence-level claim checks in `c:\Users\Timothy\Desktop\thesis-main\thesis-main\08_writing\chatper2_final_draft.md` against extracted text from mapped local PDFs.
Method note: automated lexical matching (RapidFuzz token-set ratio) with manual thresholding.

## adomavicius_toward_2005
- title: Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\381\Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.28947368421053
    claim: "Recommender systems emerged as a practical response to this information-overload condition by helping users discover items they are likely to value ."
    quote_candidate: "Since, as mentioned earlier, content-based systems are designed mostly to recommend text-based items, the content in these systems is usually described with keywords."
    secondary_score: 53.17220543806646
    secondary_quote: "An alternative approach is presented in [83], [109], where various techniques are explored for determining the best (i.e., most informative to a recommender system) items for a new user to rate."
  - claim_2_status: partially_supported
    score: 54.54545454545455
    claim: "The core problem is not to retrieve a known correct answer, but to infer likely user value from sparse evidence ."
    quote_candidate: "One way to explore the intrusiveness problem is to determine an optimal number of ratings the system should ask from a new user."
    secondary_score: 53.84615384615385
    secondary_quote: "Note that both the content-based and the collaborative approaches use the same cosine measure from information retrieval literature."
  - claim_3_status: partially_supported
    score: 51.03448275862069
    claim: "Play counts and sessions reflect engagement signals, but they do not fully encode why a user listened or what they wanted next ."
    quote_candidate: "3.5 Nonintrusiveness Many recommender systems are intrusive in the sense that they require explicit feedback from the user and often at a significant level of user involvement."
    secondary_score: 49.63503649635037
    secondary_quote: "Each element of the user space C can be defined with a profile that includes various user characteristics, such as age, gender, income, marital status, etc."
  - claim_4_status: supported
    score: 71.06598984771574
    claim: "Most recommender systems are discussed through three high-level families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "Toward the Next Generation of Recommender Systems: A Survey of the State-of-the-Art and Possible Extensions Gediminas Adomavicius, Member , IEEE, and Alexander Tuzhilin, Member , IEEE Abstract—This paper presents an overview of the field of recommender systems and describes the current generation of recommendation methods that are usually classified into the following three main categories: content-based, collaborative, and hybrid recommendation approaches."
    secondary_score: 67.21311475409837
    secondary_quote: "Therefore, function uij clearly subsumes the collaborative, content-based, and hybrid methods discussed in Section 2."
  - claim_5_status: partially_supported
    score: 51.36986301369863
    claim: "Their explanation burden often increases when decision logic is represented through latent interactions rather than explicit feature comparisons ."
    quote_candidate: "Another problem with limited content analysis is that, if two different items are represented by the same set of features, they are indistinguishable."
    secondary_score: 50.0
    secondary_quote: "However, nonintrusive ratings (such as time spent reading an article) are often inaccurate and cannot fully replace explicit ratings provided by the user."
  - claim_6_status: partially_supported
    score: 50.38167938931298
    claim: "The pipeline uses imported listening history as implicit preference evidence rather than explicit intent ."
    quote_candidate: "The profiling information can be elicited from users explicitly, e.g., through questionnaires, or implicitly—learned from their transactional behavior over time."
    secondary_score: 49.20634920634921
    secondary_quote: "However, nonintrusive ratings (such as time spent reading an article) are often inaccurate and cannot fully replace explicit ratings provided by the user."

## afroogh_trust_2024
- title: Trust in AI: progress, challenges, and future directions
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\428\Afroogh et al. - 2024 - Trust in AI progress, challenges, and future directions.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.35971223021583
    claim: "This usability requirement is well established in explanation-interface work ."
    quote_candidate: "The importance of trust in AI extends to other areas as well."
    secondary_score: 50.0
    secondary_quote: "Trust & explainability/transparency/interpretability ."

## allam_improved_2018
- title: Improved suffix blocking for record linkage and entity resolution
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Allam et al. - 2018 - Improved suffix blocking for record linkage and entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.994535519125684
    claim: "Entity-resolution literature commonly uses blocking/filtering stages before deeper matching steps ."
    quote_candidate: "These methods are per- formed in two stages, namely a blocking and a comparison stage."
    secondary_score: 46.927374301675975
    secondary_quote: "In Section 4, we present a novel blocking method for incremental record linkage."

## andjelkovic_moodplay_2019
- title: Moodplay: Interactive music recommendation based on Artists' mood similarity
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\415\Andjelkovic et al. - 2019 - Moodplay Interactive music recommendation based on Artists’ mood similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 57.25190839694657
    claim: "User controls can improve interaction outcomes, yet effects vary by user characteristics and context ."
    quote_candidate: "These characteristics can be demonstrated by comparing music to two types of content widely oﬀered to users via recommender systems: online movies and merchandise."
    secondary_score: 56.12244897959184
    secondary_quote: "Users construct proﬁles by entering names of artists via an interactive drop- down list ( Fig."
  - claim_2_status: partially_supported
    score: 51.56794425087108
    claim: "This aligns with control literature emphasizing explicit and testable user influence rather than unconstrained personalization claims ."
    quote_candidate: "We compute prediction error to compare against three traditional recommendation algorithms, which are only trained on a matrix of user and item ratings."
    secondary_score: 51.10132158590309
    secondary_quote: "Table 3 Statistics describing user interactions with the interface in diﬀerent condi- tions."

## anelli_elliot_2021
- title: Elliot: A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Anelli et al. - 2021 - Elliot A Comprehensive and Rigorous Framework for Reproducible Recommender Systems Evaluation.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.961832061068705
    claim: "Reproducibility-oriented frameworks and surveys reinforce the same caution ."
    quote_candidate: "Reproducibility is the keystone of modern RSs research."
    secondary_score: 51.89873417721519
    secondary_quote: "Comparative recommender system evaluation: benchmarking recommendation frameworks."
  - claim_2_status: partially_supported
    score: 55.55555555555556
    claim: "Recommender literature repeatedly highlights comparability risks when split definitions, preprocessing details, and configuration state are weakly documented ."
    quote_candidate: "Bias in Search and Recommender Systems."
    secondary_score: 51.11821086261981
    secondary_quote: "Elliot is a comprehensive recommendation framework that aims to run and reproduce an entire experimental pipeline by processing a simple configuration file."

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
    score: 55.49738219895288
    claim: "Neural entity matching is relevant comparator context and can improve difficult linkage cases ."
    quote_candidate: "[23], Talburt [93] all introduce entity matching in the context of data quality and integration."
    secondary_score: 52.63157894736842
    secondary_quote: "Finally, we discuss challenges and opportunities for deep learning in entity matching in Section8."

## bauer_exploring_2024
- title: Exploring the Landscape of Recommender Systems Evaluation: Practices and Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bauer et al. - 2024 - Exploring the Landscape of Recommender Systems Evaluation Practices and Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.071005917159766
    claim: "Reproducibility-oriented frameworks and surveys reinforce the same caution ."
    quote_candidate: "Stepwise procedure for searching, filtering, categorizing, and analyzing the surveyed papers."
    secondary_score: 49.35064935064935
    secondary_quote: "(A.6) The paper contributes a framework for evaluation in the form of a toolkit."

## beel_towards_2016
- title: Towards reproducibility in recommender-systems research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Beel et al. - 2016 - Towards reproducibility in recommender-systems research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "It supports clearer debugging and sensitivity analysis because output changes can be connected to explicit parameter changes rather than hidden run-to-run variation ."
    quote_candidate: "Since minor variations in approaches and scenarios can lead to signiﬁcant changes in a recom- mendation approach’s performance, ensuring reproducibility of experimental results is difﬁcult."
    secondary_score: 47.05882352941177
    secondary_quote: "Hence, it is unknown, which of these two factors caused the change in outcome and to what extent."

## bellogin_improving_2021
- title: Improving accountability in recommender systems research through reproducibility
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Bellogín and Said - 2021 - Improving accountability in recommender systems research through reproducibility.pdf
- mapping_score: 86
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.72886297376093
    claim: "It supports clearer debugging and sensitivity analysis because output changes can be connected to explicit parameter changes rather than hidden run-to-run variation ."
    quote_candidate: "It does also show general techniques that could help in achieving reproducibility, mostly related to tracking all operations and actions related to an experiment and giving more importance to validation."
    secondary_score: 48.94259818731118
    secondary_quote: "Both works state that these aspects can be considered at different levels: the entire model, individual components (e.g., parameters), and a particular training algo- rithm."
  - claim_2_status: partially_supported
    score: 54.54545454545455
    claim: "Recommender literature repeatedly highlights comparability risks when split definitions, preprocessing details, and configuration state are weakly documented ."
    quote_candidate: "First, we revise the previously mentioned concepts (i.e., reproducibility, accountability, transparency) and their definitions for Recommender Systems research."
    secondary_score: 51.19453924914676
    secondary_quote: "Based on the definitions of those concepts, we propose to improve accountability of Recommender Systems research through reproducibility."

## betello_reproducible_2025
- title: A Reproducible Analysis of Sequential Recommender Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Betello et al. - 2025 - A Reproducible Analysis of Sequential Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.93167701863354
    claim: "Recommender literature repeatedly highlights comparability risks when split definitions, preprocessing details, and configuration state are weakly documented ."
    quote_candidate: "We present EasyRec, a novel library dedicated to Sequen- tial Recommender Systems (SRSs), designed to simplify data preprocessing and streamline model implementation."
    secondary_score: 50.205761316872426
    secondary_quote: "configurations are carefully documented and made available in our code repository 2."

## binette_almost_2022
- title: (Almost) all of entity resolution
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Binette and Steorts - 2022 - (Almost) all of entity resolution.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 48.53556485355649
    claim: "Entity-resolution literature commonly uses blocking/filtering stages before deeper matching steps ."
    quote_candidate: "A large portion of this literature uses clustering as a second step to probabilistic record linkage to enforce transitivity of the output (6, 83)."
    secondary_score: 47.80487804878049
    secondary_quote: "Here, the matching configuration matrix, or coreference matrix, indicates the linkage structure between two databases."

## bogdanov_semantic_2013
- title: Semantic audio content-based music recommendation and visualization based on user preference examples
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\409\Bogdanov et al. - 2013 - Semantic audio content-based music recommendation and visualization based on user preference example.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.470588235294116
    claim: "Their practical advantage in a transparency-oriented project is mechanism visibility: if recommendations are driven by explicit features, the system can usually expose why an item scored well in terms of those same features ."
    quote_candidate: "Since retrieval based on a single example is just a particular case of using a recommender system, these approaches may not be directly suitable for music recommendation purposes in general."
    secondary_score: 51.36363636363637
    secondary_quote: "The results are promising: the recommendations were positively evaluated and close to those coming from state-of- the-art metadata-based systems, and the subjects judged the generated visualizations to capture their core preferences."
  - claim_2_status: partially_supported
    score: 55.08196721311475
    claim: "Semantic-content work shows that preference representations can be built from explicit, inspectable descriptors rather than opaque latent states ."
    quote_candidate: "In the present work we propose a content-based technique to automatically gen- erate a semantic representation of the user’s musical preferences directly from audio."
    secondary_score: 52.83018867924528
    secondary_quote: "With the described procedure we obtain 62 semantic descriptors, shown in Table 1, for each track in the user’s preference set."
  - claim_3_status: partially_supported
    score: 55.42857142857143
    claim: "The semantic-gap literature highlights the same limitation: low-level computable descriptors do not always map cleanly to higher-level human concepts such as mood, atmosphere, or nostalgia ."
    quote_candidate: "2 We use the term ‘‘semantic’’ to refer to the concepts that music listeners use to describe items within music collections, such as genres, moods, music al culture, and instrumentation."
    secondary_score: 54.36241610738255
    secondary_quote: "This information is low-level as it does not incorporate higher-level semantics in the description of music."
  - claim_4_status: partially_supported
    score: 56.540084388185655
    claim: "First, score contributors remain inspectable when preferences and candidates are represented through explicit descriptors ."
    quote_candidate: "First, we suppose that asking for explicit preference examples is an effective way to infer real user preferences."
    secondary_score: 56.27376425855513
    secondary_quote: "These semantic descriptors are computed from an explicit set of music tracks deﬁned by a given user as evidence of her/his musical preferences."

## bonnin_automated_2015
- title: Automated Generation of Music Playlists: Survey and Experiments
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\nw\files\569\Bonnin and Jannach - 2015 - Automated Generation of Music Playlists Survey and Experiments.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.111111111111114
    claim: "APC and challenge literature indicates that outcomes depend on component composition, including how candidates are prepared before final ranking ."
    quote_candidate: "In the literature, a number of such approaches have been proposed, including the types of sensors and information shown in Table I."
    secondary_score: 50.78125
    secondary_quote: "The constraints can concern various aspects including the desired genre, tempo, year of release, and so forth."
  - claim_2_status: partially_supported
    score: 51.77993527508091
    claim: "Playlist quality therefore depends on transitions, pacing, repetition control, and coherence over order, not only on independent item relevance ."
    quote_candidate: "To which extent labels allow artists to inﬂuence the selection and ordering or even recording of the tracks typically depends on the popularity of the artists [Baskerville and Baskerville 2010]."
    secondary_score: 50.0
    secondary_quote: "This information can include the genre, mood, or tempo of the tracks as well as the general or current popularity of the artist within the target audience."
  - claim_3_status: partially_supported
    score: 52.63157894736842
    claim: "Challenge and benchmark studies show that reported results depend on protocol choices and method composition ."
    quote_candidate: "Section 5) and that an optimized mixture of all models further enhances the results."
    secondary_score: 51.32743362831859
    secondary_quote: "Finally, we report the results of a comparative evaluation of typical playlist generation schemes based on historical data."
  - claim_4_status: partially_supported
    score: 55.23012552301255
    claim: "APC-related evidence indicates that comparative outcomes can shift with model composition and evaluation framing ."
    quote_candidate: "[2012] include a bigram model smoothed with the Witten-Bell discounting [Jurafsky and Martin 2009] in a comparative evaluation."
    secondary_score: 52.99145299145299
    secondary_quote: "Finally, we report the results of a comparative evaluation of typical playlist generation schemes based on historical data."

## cano_hybrid_2017
- title: Hybrid recommender systems: A systematic literature review
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\430\Çano and Morisio - 2017 - Hybrid recommender systems A systematic literature review.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 58.97435897435897
    claim: "Most recommender systems are discussed through three high-level families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "In recommender systems this conclusions are of the form"
    secondary_score: 52.91828793774319
    secondary_quote: "To this end, we deﬁned the following research questions: RQ1 What are the most relevant studies addressing hybrid recommender systems?"
  - claim_2_status: supported
    score: 68.42105263157895
    claim: "Hybrid systems combine signal families to exploit complementary strengths ."
    quote_candidate: "Hybrid recommender systems combine two or more recommendation strategies in differ- ent ways to beneﬁt from their complementary advantages."
    secondary_score: 51.48514851485149
    secondary_quote: "Hybrid RSs represent a somehow newer family of recommender systems compared to other well known and widely used families such as CF or CBF."
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
  - claim_1_status: weak_support
    score: 48.031496062992126
    claim: "Recommender literature repeatedly highlights comparability risks when split definitions, preprocessing details, and configuration state are weakly documented ."
    quote_candidate: "However, as mentioned earlier, we will use the termreproducibility according to the ACM definition."
    secondary_score: 47.01195219123506
    secondary_quote: "Following our request via e-mail, the authors did not reply with the missing preprocessing code."

## deldjoo_content-driven_2024
- title: Content-driven music recommendation: Evolution, state of the art, and challenges
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Deldjoo et al. - 2024 - Content-driven music recommendation Evolution, state of the art, and challenges.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.309734513274336
    claim: "Their practical advantage in a transparency-oriented project is mechanism visibility: if recommendations are driven by explicit features, the system can usually expose why an item scored well in terms of those same features ."
    quote_candidate: "To compute recommendations, for instance, one can compute the dot product of the content representation and a learnt user feature vector, utilize the user and content features in a classifier to estimate a preference, or utilize an attention mechanism for per- sonalized content."
    secondary_score: 54.81798715203426
    secondary_quote: "The former typically refers to unveiling the exact mode of operation and internal mechanisms of the recommendation algorithm or model, whereas the latter is concerned with creating (and presenting to the user) explanations of why the items in the recommendation list have been recommended."
  - claim_2_status: partially_supported
    score: 54.24657534246575
    claim: "Content-driven survey work similarly positions explicit content layers as valuable for transparent recommendation while acknowledging ongoing challenges in sequence quality and efficiency ."
    quote_candidate: "• Derivative Content (DC): Derivative content refers to new works based on the original content from the inner layers of the model, still providing information relevant for content analysis and rec- ommendation."
    secondary_score: 53.73737373737374
    secondary_quote: "Second, we identify six overarching challenges, according to which we organize our main discussion: increasing recommendation diversity and novelty, providing transparency and explanations, accomplishing context-awareness, recommending sequences of music, improving scalability and efficiency, and alleviating cold start."
  - claim_3_status: weak_support
    score: 47.6780185758514
    claim: "The semantic-gap literature highlights the same limitation: low-level computable descriptors do not always map cleanly to higher-level human concepts such as mood, atmosphere, or nostalgia ."
    quote_candidate: "While the discussion of content-based music features is relevant to the survey at hand, the authors do not focus on MRS tasks and challenges."
    secondary_score: 47.63860369609856
    secondary_quote: "Section 3 subsequently introduces our hierarchical model to describe the different levels of content, along the continuum between purely audio-based descriptors (‘‘content’’ in a narrow interpretation) and external data that is not part of the original signal, nevertheless descriptive or related to a music item."
  - claim_4_status: partially_supported
    score: 53.23741007194245
    claim: "First, score contributors remain inspectable when preferences and candidates are represented through explicit descriptors ."
    quote_candidate: "Data diversity: While the core of the model represents the item through one audio file, the remaining layers can consist of a broader spectrum of data from multiple sources."
    secondary_score: 52.21238938053097
    secondary_quote: "Therefore, it can separate the user’s preference by modality and deliver a more precise recommendation."

## elmagarmid_duplicate_2007
- title: Duplicate Record Detection: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Elmagarmid et al. - 2007 - Duplicate Record Detection A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.216748768472904
    claim: "Entity-resolution literature commonly uses blocking/filtering stages before deeper matching steps ."
    quote_candidate: "and introduced the notation that we use, which is also commonly used in duplicate d etection literature."
    secondary_score: 48.45360824742268
    secondary_quote: "[89] propose the use of a bootstrapping technique based on clustering to learn matching models."

## ferrari_dacrema_troubling_2021
- title: A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ferrari Dacrema et al. - 2021 - A Troubling Analysis of Reproducibility and Progress in Recommender Systems Research.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.48868778280543
    claim: "Evaluation literature warns that reported outcomes can vary with protocol design, preprocessing, and metric framing ."
    quote_candidate: "A wide variety of machine learning models were proposed fortop-n recommendation tasks in the literature."
    secondary_score: 48.36065573770492
    secondary_quote: "We generally found that the share of papers that can be reproduced based on the provided source code by the authors is still relatively low."
  - claim_2_status: weak_support
    score: 49.53560371517028
    claim: "Recommender literature repeatedly highlights comparability risks when split definitions, preprocessing details, and configuration state are weakly documented ."
    quote_candidate: "This variety of baselines (together with the variety of datasets) represents one of the underlying problems that we identified, because it limits the comparability of results across papers."
    secondary_score: 48.37758112094395
    secondary_quote: "In our experiments, we included a number of comparably basic models from the literature as representatives of which methods were often considered the state-of-the-art in pre-neural times."

## ferraro_automatic_2018
- title: Automatic playlist continuation using a hybrid recommender system combining features from text and audio
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ferraro et al. - 2018 - Automatic playlist continuation using a hybrid recommender system combining features from text and a.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.174216027874564
    claim: "Playlist continuation research repeatedly discusses trade-offs among coherence, novelty, diversity, and ordering ."
    quote_candidate: "Existing research on music recom- mender systems has considered a number of related tasks, inc lud- ing Automatic Playlist Generation (APG) and Automatic Play list Continuation (APC)."
    secondary_score: 46.08695652173913
    secondary_quote: "Given the time constraints of the challenge, we were not able to evaluate all combinations of audio features that we planned ."

## fkih_similarity_2022
- title: Similarity measures for Collaborative Filtering-based Recommender Systems: Review and experimental comparison
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\432\Fkih - 2022 - Similarity measures for Collaborative Filtering-based Recommender Systems Review and experimental c.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 52.91479820627803
    claim: "Metric definitions, normalization steps, and thresholding decisions shape candidate neighborhoods and ranking behavior ."
    quote_candidate: "This process consists of three steps: similarity computation, neighborhood selection and rating prediction."
    secondary_score: 48.739495798319325
    secondary_quote: "The correlation threshold technique sets a threshold and maintains items whose similarities, with the active item, exceed the threshold."
  - claim_2_status: weak_support
    score: 48.484848484848484
    claim: "Similarity behavior depends on explicit distance-function and scaling choices ."
    quote_candidate: "Vector Similarity (Cosine): formulas (5) and (6) ."
    secondary_score: 47.29064039408867
    secondary_quote: "While the second approach tries to build a model (a machine learning) describing the user behavior in order to predict his choices."

## flexer_problem_2016
- title: The Problem of Limited Inter-rater Agreement in Modelling Music Similarity
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\401\Flexer and Grill - 2016 - The Problem of Limited Inter-rater Agreement in Modelling Music Similarity.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 58.333333333333336
    claim: "Music-similarity studies report limited inter-rater agreement and framing sensitivity, indicating that similarity metrics are useful approximations rather than objective truth conditions ."
    quote_candidate: "On inter-rater agreement in audio music similarity."
    secondary_score: 57.57575757575758
    secondary_quote: "Due to limited inter-rater agreement there exist upper bounds of performance in subjective evaluation of the respec- tive music similarity tasks."

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
    score: 50.39370078740158
    claim: "Evaluation literature warns that reported outcomes can vary with protocol design, preprocessing, and metric framing ."
    quote_candidate: "Throughout our discussion, we separate out our review of what has been done before in the literature from the introduction of new tasks and methods."
    secondary_score: 50.0
    secondary_quote: "Re- searchers who survey the literature willﬁnd over a dozen quantitative metrics and additional qualitative evaluation techniques."

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
    score: 55.43859649122807
    claim: "User controls can improve interaction outcomes, yet effects vary by user characteristics and context ."
    quote_candidate: "RQ2: How do personal characteristicsmoderate the effect of the user interface (user controls / visualizations) on user perception of recommendations (diversity, accep- tance, and cognitive load)?"
    secondary_score: 54.148471615720524
    secondary_quote: "RQ1: How do personal characteristics inﬂuence user perception of recommenda- tions (diversity, acceptance, and cognitive load)?"
  - claim_3_status: partially_supported
    score: 53.21637426900585
    claim: "This aligns with control literature emphasizing explicit and testable user influence rather than unconstrained personalization claims ."
    quote_candidate: "These results allow us to extend the model for personalization in music recommender systems by providing guidelines for interactive visualization design for music recommender systems, with regard to both visualizations and user control."
    secondary_score: 52.398523985239855
    secondary_quote: "( 2011) also found that controlling recommendations can reduce the task time and error rate of users while increasing decision accuracy."

## knijnenburg_explaining_2012
- title: Explaining the user experience of recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\422\Knijnenburg et al. - 2012 - Explaining the user experience of recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: weak_support
    score: 47.77777777777778
    claim: "This usability requirement is well established in explanation-interface work ."
    quote_candidate: "These perceptions in turn cause an experiential evaluation in terms of appeal, pleasure and satisfaction."
    secondary_score: 47.31182795698925
    secondary_quote: "This paper reviews how current literature maps to the framework and identiﬁes several gaps in existing work."

## liu_aggregating_2025
- title: Aggregating Contextual Information for Multi-Criteria Online Music Recommendations
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Liu - 2025 - Aggregating Contextual Information for Multi-Criteria Online Music Recommendations.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.02325581395349
    claim: "User controls can improve interaction outcomes, yet effects vary by user characteristics and context ."
    quote_candidate: "However, incorporating context in the rating aggregation process did not necessarily improve prediction accuracy."
    secondary_score: 51.88284518828452
    secondary_quote: "By explicitly modeling interactions between user, item, and context variables, FM enhances the accuracy of context-aware recommendations."
  - claim_2_status: partially_supported
    score: 55.94405594405595
    claim: "This aligns with control literature emphasizing explicit and testable user influence rather than unconstrained personalization claims ."
    quote_candidate: "This approach balances variety and personalization, ensuring the playlist caters to the user’s context while encouraging exploration of new musical styles."
    secondary_score: 52.87356321839081
    secondary_quote: "This comprehensive evaluation allows us to understand how the algorithms perform with varying lengths of recommendation lists."

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
    score: 60.14492753623188
    claim: "Recommender systems emerged as a practical response to this information-overload condition by helping users discover items they are likely to value ."
    quote_candidate: "Recommender systems can be used in digital library applications to help users locate and select information and knowledge sources[95]."
    secondary_score: 53.608247422680414
    secondary_quote: "It utilizes context information to suggest appropriate items to drivers such as restaurants at meal times or nearby fuel stations when fuel is exhausted."
  - claim_2_status: partially_supported
    score: 62.77372262773723
    claim: "Most recommender systems are discussed through three high-level families: content-based, collaborative, and hybrid approaches ."
    quote_candidate: "In the e-library recommender systems discussed above, the hybrid recommendation approaches which combine CB, CF and/or KB tech- niques are widely used."
    secondary_score: 58.24561403508772
    secondary_quote: "For example, the paper by Adomavicius and Tuzhilin [3] presented an overview of content-based, collaborative ﬁltering-based, and hybrid recommendation approaches."

## mcfee_million_2012
- title: The million song dataset challenge
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\nw\files\570\McFee et al. - 2012 - The million song dataset challenge.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.370370370370374
    claim: "Challenge and benchmark studies show that reported results depend on protocol choices and method composition ."
    quote_candidate: "We explain the taste proﬁle data, our goals and design choices in creating the challenge, and present baseline results using simple, oﬀ-the-shelf recommendation algorithms."
    secondary_score: 50.18726591760299
    secondary_quote: "This is an opportunity for the MIR ﬁeld to show its strength on an industrial-size challenge and to merge the results from diﬀerent sub-ﬁelds into one system for one speciﬁc task."

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
  - claim_1_status: partially_supported
    score: 53.44827586206897
    claim: "Prior work shows that explanations can increase trust or perceived satisfaction without necessarily improving genuine understanding ."
    quote_candidate: "A feature is not necessarily an input feature to predictive model f, but it should be a feature in the explanation."
    secondary_score: 50.205761316872426
    secondary_quote: "Note that a set of outcome explanations can collectively comprise a global explanation for model inspection (cf."

## neto_algorithmic_2023
- title: The algorithmic nature of song-sequencing: statistical regularities in music albums
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\403\Neto et al. - 2023 - The algorithmic nature of song-sequencing statistical regularities in music albums.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.62240663900415
    claim: "Sequencing studies reinforce that playlists are experienced as ordered structures rather than unordered sets ."
    quote_candidate: "The view that music is experienced as a coherent sequence of acoustic events is not an idiosyncrasy of music theorists and classical composers."
    secondary_score: 47.651006711409394
    secondary_quote: "If analysed together, these studies reveal that APG researchers generally agree upon the idea that a track is not perceived as an independent musical unit, but rather as a member of a broader context."

## papadakis_blocking_2021
- title: Blocking and Filtering Techniques for Entity Resolution: A Survey
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Papadakis et al. - 2021 - Blocking and Filtering Techniques for Entity Resolution A Survey.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 46.15384615384615
    claim: "Entity-resolution literature commonly uses blocking/filtering stages before deeper matching steps ."
    quote_candidate: "Entities sharing the same output for a particular blocking predicate are considered candidate matches (i.e., hash-based functionality)."
    secondary_score: 45.04504504504504
    secondary_quote: "Disjunctions of conjunctions of predicates, i.e., composite blocking schemes, are learned by optimizing an objective function."

## pegoraro_santana_music4all_2020
- title: Music4All: A New Music Database and Its Applications
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Pegoraro Santana et al. - 2020 - Music4All A New Music Database and Its Applications.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 55.23255813953488
    claim: "Music4All is suitable for this scope because it provides metadata, tags, lyrics, and audio-related attributes that support reproducible content-driven experimentation ."
    quote_candidate: "By this way, in this work we try to contribute in this sense, introducing a novel music database that offers hundreds of thousands of music pieces assigned to metadata, tags, labels, lyrics, and so on."
    secondary_score: 53.91304347826087
    secondary_quote: "In order to contribute to the MIR community, we present Music4AII, a new music database which contains metadata, tags, genre information, 30-seconds audio clips, lyrics, and so on."

## roy_systematic_2022
- title: A systematic review and research perspective on recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\385\Roy and Dutta - 2022 - A systematic review and research perspective on recommender systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 57.4468085106383
    claim: "Recommender systems emerged as a practical response to this information-overload condition by helping users discover items they are likely to value ."
    quote_candidate: "In this era of big data, more and more items and users are rapidly getting added to the system and this problem is becoming common in recommender systems."
    secondary_score: 56.0
    secondary_quote: "Recommender systems primarily aim to reduce the user’s effort and time required for searching relevant information over the internet."
  - claim_2_status: partially_supported
    score: 55.51020408163265
    claim: "The core problem is not to retrieve a known correct answer, but to infer likely user value from sparse evidence ."
    quote_candidate: "Cold start problem The cold start problem appears when the recommender system cannot draw any infer - ence from the existing data, which is insufficient."
    secondary_score: 54.7085201793722
    secondary_quote: "One solution to this problem is to detect the attackers quickly and remove the fake ratings and fake user pro- files from the system."
  - claim_3_status: partially_supported
    score: 50.199203187250994
    claim: "Play counts and sessions reflect engagement signals, but they do not fully encode why a user listened or what they wanted next ."
    quote_candidate: "This technique starts with finding a group or collection of user X whose preferences, likes, and dislikes are similar to that of user A."
    secondary_score: 50.17667844522968
    secondary_quote: "Cold start refers to a condition when the system cannot produce efficient recommendations for the cold (or new) users who have not rated any item or have rated a very few items."
  - claim_4_status: partially_supported
    score: 51.54639175257732
    claim: "The pipeline uses imported listening history as implicit preference evidence rather than explicit intent ."
    quote_candidate: "Most recommender systems gather user ratings through both explicit and implicit methods."
    secondary_score: 51.08695652173913
    secondary_quote: "User ratings are gener - ally collected by using implicit or explicit methods."

## ru_improving_2023
- title: Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Perspective
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Ru et al. - 2023 - Improving Music Genre Classification from multi-modal Properties of Music and Genre Correlations Per.pdf
- mapping_score: 99
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "It has also been used in independent multimodal recommendation experiments, with explicit task-transfer caveats ."
    quote_candidate: "The comparison results with other multi-modal methods are shown in Table 1."
    secondary_score: 49.26470588235294
    secondary_quote: "In all ablation experiments, we find that the most complete model achieves the best results, indicating that the three components can be combined flexibly without conflict."

## schedl_current_2018
- title: Current challenges and visions in music recommender systems research
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\399\Schedl et al. - 2018 - Current challenges and visions in music recommender systems research.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.82233502538071
    claim: "Listening is session-based and sequential, and users evaluate flow properties in addition to item relevance ."
    quote_candidate: "This is done by generating a user proﬁle by requesting the user to rate a set of selected items [ 30]."
    secondary_score: 54.54545454545455
    secondary_quote: "In more detail, spread is the entropy of the distribution of the items recommended to the users in the test set."
  - claim_2_status: partially_supported
    score: 51.383399209486164
    claim: "Playlist quality therefore depends on transitions, pacing, repetition control, and coherence over order, not only on independent item relevance ."
    quote_candidate: "High sparsity translates into low rating coverage, since most users tend to rate only a tiny fraction of items."
    secondary_score: 51.07913669064748
    secondary_quote: "Such evaluation met- rics can consider the ranking order of the recommendations or the internal coherence or diversity of the recommended list as a whole."
  - claim_3_status: partially_supported
    score: 55.172413793103445
    claim: "The same listener may prefer very different playlists across focus, commute, exercise, and social contexts, even with the same catalog ."
    quote_candidate: "In other works, playlists are created based on the context of the listener, either as single source [ 157] or in combination with content-based similarity [ 35,149]."
    secondary_score: 52.32974910394265
    secondary_quote: "Similarly, different criteria were mentioned when listeners judged the coherence of songs in a playlist, including lyrical content, tempo, and mood."

## schweiger_impact_2025
- title: The impact of playlist characteristics on coherence in user-curated music playlists
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\rp\files\578\Schweiger et al. - 2025 - The impact of playlist characteristics on coherence in user-curated music playlists.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 47.92626728110599
    claim: "A bounded limitation should remain explicit: broad multi-dataset isolation studies focused specifically on deterministic similarity-function effects across multiple playlist objectives are still limited in the current source set ."
    quote_candidate: "The coherent playlist might be diverse in the selected property under observation, but it can still deliver a smooth lis- teningexperience(similarlytoaconsistentplaylist)ifthetracksarearrangedaccordingly."
    secondary_score: 46.53739612188366
    secondary_quote: "4 CPs can lead to playlists containing more diverse music, as the musical tastes of multiple users feed into one playlist [24, 40]."

## siedenburg_modeling_2017
- title: Modeling Timbre Similarity of Short Music Clips
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Siedenburg and Müllensiefen - 2017 - Modeling Timbre Similarity of Short Music Clips.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 51.13636363636363
    claim: "Music-similarity studies report limited inter-rater agreement and framing sensitivity, indicating that similarity metrics are useful approximations rather than objective truth conditions ."
    quote_candidate: "(2013) devised an individual diﬀerences test that investigates diﬀerences in t he ability to extract information from short audio clips and to u se it for similarity comparisons."
    secondary_score: 50.857142857142854
    secondary_quote: "A computational model is necessary in order to create a test that is adaptive and homes in on the individual participant’s ability level for judging sound similarities."

## sotirou_musiclime_2025
- title: MusicLIME: Explainable Multimodal Music Understanding
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Sotirou et al. - 2025 - MusicLIME Explainable Multimodal Music Understanding.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.02593659942363
    claim: "Recent work on explainability in music models supports the broader principle that useful explanations should expose contribution structure, not only final labels ."
    quote_candidate: "It is noteworthy that the multimodal explanations produced by MUSIC LIME are consistent with the observations and assumptions that a user makes based on the performance metrics outlined in Table I."
    secondary_score: 52.5974025974026
    secondary_quote: "Additionally, we provide global explanations by aggregating local explanations, offering a broader understanding of the model’s overall behavior."

## teinemaa_composition_2018
- title: Automatic Playlist Continuation through a Composition of Collaborative Filters
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Teinemaa et al. - 2018 - Automatic Playlist Continuation through a Composition of Collaborative Filters.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.526315789473685
    claim: "APC and challenge literature indicates that outcomes depend on component composition, including how candidates are prepared before final ranking ."
    quote_candidate: "Figure 1: Performance of different models on validation set The results of the final model on both the validation set (Dval) and the challenge set are presented in Table 5."
    secondary_score: 49.27536231884058
    secondary_quote: "Table 3 shows the optimized best sets of weights separately for each category (used in the local weights composition) and global weights (used in the global weights composition)."
  - claim_2_status: partially_supported
    score: 53.389830508474574
    claim: "Challenge and benchmark studies show that reported results depend on protocol choices and method composition ."
    quote_candidate: "Table 3 shows the optimized best sets of weights separately for each category (used in the local weights composition) and global weights (used in the global weights composition)."
    secondary_score: 50.45871559633027
    secondary_quote: "For example, the recommended songs for the continuation of a playlist that consists of Christmas songs should be other Christmas songs."
  - claim_3_status: partially_supported
    score: 52.63157894736842
    claim: "APC-related evidence indicates that comparative outcomes can shift with model composition and evaluation framing ."
    quote_candidate: "Note that in all cases, the composed collaborative model performs better than the popularity model."
    secondary_score: 51.37614678899082
    secondary_quote: "Section 3 describes the proposed framework based on several collaborative filters and their combination."

## tintarev_evaluating_2012
- title: Evaluating the effectiveness of explanations for recommender systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\391\Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 56.426332288401255
    claim: "Explainable recommender research consistently argues that predictive quality alone is insufficient when users or evaluators need to understand, challenge, or influence system behavior ."
    quote_candidate: "For example, suppose that in a particular recommender system users tend to select item A when no explanations are present, and item B when explanations are present."
    secondary_score: 52.78592375366569
    secondary_quote: "Actual com- petence was established by comparing the item features used by the recommender system with the item features mentioned by users when asked why they had chosen their top items."
  - claim_2_status: partially_supported
    score: 55.55555555555556
    claim: "Prior work shows that explanations can increase trust or perceived satisfaction without necessarily improving genuine understanding ."
    quote_candidate: "So, we wanted to know whether the decision to personalize the explanations (DA) and the way this was done (AA) would indeed lead to increased effectiveness and satisfaction."
    secondary_score: 54.19847328244275
    secondary_quote: "Partici- pants were asked how useful (and understandable) they perceived the explanations to be, and to rank explanations in order of usefulness."

## tintarev_survey_2007
- title: A Survey of Explanations in Recommender Systems
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\389\Tintarev and Masthoff - 2007 - A Survey of Explanations in Recommender Systems.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 54.857142857142854
    claim: "Explainable recommender research consistently argues that predictive quality alone is insufficient when users or evaluators need to understand, challenge, or influence system behavior ."
    quote_candidate: "The presence of longer descriptions of individual items has been found to be positively correlated with both the perceived usefulness and ease of use of the recommender system [31]."
    secondary_score: 54.69168900804289
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
    score: 52.4822695035461
    claim: "This usability requirement is well established in explanation-interface work ."
    quote_candidate: "Trust-inspiring explanation interfaces for recommender systems."
    secondary_score: 51.21951219512195
    secondary_quote: "The need to design and build explainable recommender interfaces is increasing rapidly."

## vall_feature-combination_2019
- title: Feature-combination hybrid recommender systems for automated music playlist continuation
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Vall et al. - 2019 - Feature-combination hybrid recommender systems for automated music playlist continuation.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 53.191489361702125
    claim: "Playlist continuation research repeatedly discusses trade-offs among coherence, novelty, diversity, and ordering ."
    quote_candidate: "1 Playlist continuation as a matrix completion and expansion problem."
    secondary_score: 50.69124423963134
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
  - claim_1_status: partially_supported
    score: 50.0
    claim: "APC and challenge literature indicates that outcomes depend on component composition, including how candidates are prepared before final ranking ."
    quote_candidate: "The reason might be that adding external resources increases the complexity of the models and given the amount of training data, the models could not take advantage of external resources, effectively."
    secondary_score: 47.74193548387097
    secondary_quote: "Note that the test set for both tracks are the same and the only difference is that the teams were allowed to use external resources (other than the MPD training set) in the creative track."
  - claim_2_status: partially_supported
    score: 50.4
    claim: "Playlist continuation research repeatedly discusses trade-offs among coherence, novelty, diversity, and ordering ."
    quote_candidate: "[46] have recently identified the task of automatic music playlist continuation as one of the grand challenges in music recommender systems research."
    secondary_score: 46.44549763033175
    secondary_quote: "In other words, either the track list or the artist list was randomly deactivated in the input of the autoencoder."
  - claim_3_status: weak_support
    score: 46.42857142857143
    claim: "APC-related evidence indicates that comparative outcomes can shift with model composition and evaluation framing ."
    quote_candidate: "The reason might be that adding external resources increases the complexity of the models and given the amount of training data, the models could not take advantage of external resources, effectively."
    secondary_score: 46.28099173553719
    secondary_quote: "Among which, neural networks and matrix factorization models are notable that predict the tracks in a playlist, given its title."

## zhang_explainable_2020
- title: Explainable Recommendation: A Survey and New Perspectives
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\previous_drafts\lit_review_resource_pack\files\387\Zhang and Chen - 2020 - Explainable Recommendation A Survey and New Perspectives.pdf
- mapping_score: 1000
- mapping_method: bib_attachment_exact_stem
- claim_checks:
  - claim_1_status: partially_supported
    score: 50.0
    claim: "Their explanation burden often increases when decision logic is represented through latent interactions rather than explicit feature comparisons ."
    quote_candidate: "Instead, it develops an explanation model to generate explanations after a decision has been made."
    secondary_score: 49.87277353689567
    secondary_quote: "The classiﬁcation is based on two dimensions, i.e., the type of model for explainable recommendation (e.g., matrix factorization, topic modeling, deep learning, etc.) and the information/style of the generated explanation (e.g., textual sentence explanation, etc.)."
  - claim_2_status: partially_supported
    score: 55.74572127139364
    claim: "Explainable recommender research consistently argues that predictive quality alone is insufficient when users or evaluators need to understand, challenge, or influence system behavior ."
    quote_candidate: "Explainable recommendation tries to address the problem of why: by providing explanations to users or system design- ers, it helps humans to understand why certain items are recommended by the algorithm, where the human can either be users or system designers."
    secondary_score: 54.59057071960298
    secondary_quote: "This lack of model explainability also makes it challenging to provide intuitive explanations to users, since it is hardly acceptable to tell users that we recommend an item only because it gets higher prediction scores by the model."
  - claim_3_status: partially_supported
    score: 60.08230452674897
    claim: "The distinction between post-hoc explanation and directly explainable mechanisms is therefore central ."
    quote_candidate: "The explanations may either be post-hoc or directly come from an explainable model (also called interpretable or transparent model in some contexts)."
    secondary_score: 52.83018867924528
    secondary_quote: "Table 1.1 shows how representative explainable recommendation research is classiﬁed into diﬀerent categories."

## zhu_bars_2022
- title: BARS
- mapped_pdf: c:\Users\Timothy\Desktop\thesis-main\thesis-main\10_resources\papers\Zhu et al. - 2022 - BARS Towards Open Benchmarking for Recommender Systems.pdf
- mapping_score: 105
- mapping_method: fuzzy_title_author_year
- claim_checks:
  - claim_1_status: weak_support
    score: 49.85507246376812
    claim: "Recommender literature repeatedly highlights comparability risks when split definitions, preprocessing details, and configuration state are weakly documented ."
    quote_candidate: "In many cases, the reported results cannot be easily reproduced due to the lack of either data preprocessing details, model implementations, hyper-parameter configurations, or even all of them."
    secondary_score: 49.645390070921984
    secondary_quote: "In Proceedings of the International Workshop on Reproducibility and Replication in Recommender Systems Evaluation (RepSys)."
  - claim_2_status: partially_supported
    score: 54.26829268292683
    claim: "BARS-style benchmarking work makes the reporting issue explicit by emphasizing missing preprocessing and configuration details as a reproducibility barrier ."
    quote_candidate: "To promote reproducible research, our benchmark- ing work aims to record detailed hyper-parameter configurations for each experiment and demonstrate the reproducing steps."
    secondary_score: 53.06122448979592
    secondary_quote: "In many cases, the reported results cannot be easily reproduced due to the lack of either data preprocessing details, model implementations, hyper-parameter configurations, or even all of them."

## Summary
- total_claim_checks: 89
- supported: 2
- partially_supported: 76
- weak_support: 11
- no_match: 0