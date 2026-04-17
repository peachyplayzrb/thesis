# Chapter 6: Discussion and Bounded Contribution

Chapter objective: interpret the Chapter 5 evaluation evidence against the active research question and contribution claim, while keeping every conclusion bounded to explicit objective-linked evidence.

## 6.1 Interpretation Frame
The rebuilt research question asks how a deterministic playlist-generation pipeline can be engineered and evaluated so that preference inference, candidate generation, and playlist assembly remain transparent, controllable, and reproducible under cross-source uncertainty and multi-objective playlist trade-offs.

Chapter 6 therefore interprets results through three lenses that follow directly from the rebuild posture:

1. uncertainty handling,
2. controllable trade-off engineering,
3. mechanism-linked evidence quality.

This chapter is not a benchmark-positioning chapter. It does not argue that deterministic methods are universally preferable to hybrid, collaborative, or deep recommender families. Instead, it asks whether the implemented artefact now produces evidence strong enough to support the bounded engineering claim established in Chapters 1 to 3 [@jannach_measuring_2019; @bauer_exploring_2024; @ferrari_dacrema_troubling_2021].

## 6.2 Findings in Relation to the Research Question
The current evidence supports five main findings.

### 6.2.1 Explicit uncertainty handling is a design requirement, not a reporting afterthought
The rebuild confirms that cross-source preference inference should not be treated as if imported interaction traces were direct preference truth. BL-003 and BL-004 now surface match confidence, source coverage, attribution, and uncertainty-related diagnostics directly in the active output contract. This supports the claim that uncertainty visibility must be engineered into the profiling path itself rather than inferred later from failures [@allam_improved_2018; @papadakis_blocking_2021].

### 6.2.2 Candidate generation is first-order recommendation logic
The rebuild also confirms a Chapter 2 tension that was muted in the legacy framing: candidate shaping is not neutral preprocessing. BL-005 exclusion-path diagnostics and tranche-1 gate checks show that the eventual ranking and playlist outputs are strongly conditioned by which candidates survive filtering. This means explanation and evaluation claims that focus only on final ranking would understate an important part of causal behavior.

### 6.2.3 Deterministic scoring and assembly remain valuable because they keep trade-offs inspectable
BL-006 and BL-007 continue to support a strong engineering argument for deterministic methods in this thesis scope: score components, rule pressure, and assembly constraints remain directly inspectable. That does not prove that deterministic methods maximize recommendation quality in every setting, but it does show that they provide a practical substrate for auditable trade-off control under bounded scope [@roy_systematic_2022; @jannach_measuring_2019].

### 6.2.4 Explanation quality depends on mechanism linkage, not on narrative plausibility alone
The tranche-2 and tranche-3 evidence strengthens the discussion around transparency. BL-008 explanations are now more useful because they preserve both direct mechanism contributors and control-provenance snapshots. This matters because explanation fidelity in the thesis is treated as alignment with actual scoring and assembly behavior, not merely as the production of convincing natural-language rationale [@zhang_explainable_2020; @tintarev_evaluating_2012; @sotirou_musiclime_2025].

### 6.2.5 Bounded guidance becomes more credible when limits are part of the contract
The most important late-stage design improvement is that validity boundaries are now explicit, top-level, and test-enforced in BL-009. This changes the discussion posture: instead of adding caveats only in prose after evaluation, the artefact itself now emits scope, known limits, and run-specific caveats. That makes Chapter 6 conclusions more defensible because boundedness is operationalized rather than retrofitted [@beel_towards_2016; @bellogin_improving_2021; @cavenaghi_systematic_2023].

## 6.3 Contribution Interpretation
The contribution is best understood as an engineering-evidence contribution rather than a model-performance contribution.

What the thesis now demonstrates is not that one deterministic playlist pipeline is universally best, but that it is possible to co-engineer:

1. explicit uncertainty signaling during preference inference,
2. controllable candidate and assembly trade-offs,
3. mechanism-linked explanations,
4. executable reproducibility and controllability evidence,
5. explicit validity-boundary reporting.

Taken together, these give the thesis a clearer and more defensible contribution than the earlier pre-rebuild framing, which concentrated more on generic transparency/observability language than on explicit objective-to-evidence traceability [@balog_transparent_2019; @knijnenburg_explaining_2012; @afroogh_trust_2024].

## 6.4 Limits of the Current Evidence
The current evidence still has important limits.

1. Cross-source preference traces remain indirect evidence of user preference rather than causal ground truth.
2. Alignment uncertainty remains material; in the canonical active baseline, only 15.95% of imported Spotify history aligns to the offline corpus, so profile-level claims remain bounded to the matched subset rather than the full listening history.
3. Some control surfaces remain weak or data-regime-dependent, as shown by BL-011 no-op diagnostics.
4. Reproducibility claims are contract-bounded to declared fixed inputs, replay procedures, and stable-content comparisons.
5. External validity remains narrow because the artefact is single-user, deterministic, and not evaluated through longitudinal user studies.
6. Comparator depth remains limited because the thesis does not implement a matched hybrid or learning-based baseline.

These limits do not collapse the contribution. They bound it to auditable engineering evidence under explicit scope rather than broad recommender-performance claims [@flexer_problem_2016; @papadakis_blocking_2021; @jin_effects_2020].

## 6.5 Implications for Design Science Positioning
The rebuild also sharpens the methodological interpretation of the artefact. In Design Science terms, the value of the artefact lies not only in producing playlists, but in making design claims testable through explicit control and evidence contracts. The REB-M3 tranche gates are especially important here because they turn objective satisfaction into executable acceptance checks instead of relying only on narrative consistency across chapters.

This is a stronger DSR posture than the legacy chapter framing because it narrows the gap between design intent, implemented control surface, and reported evidence [@anelli_elliot_2021; @zhu_bars_2022].

## 6.6 Future Work
Future work should extend the artefact without breaking the evidence discipline established in the rebuild.

1. Deepen control-effect analysis by moving from one-factor-at-a-time tests to interaction-aware control studies.
2. Resolve open influence-track design questions, especially whether explicit user intent should override assembly constraints and how weak influence effects should be reported.
3. Add comparator pipelines only when they can be evaluated under the same objective-to-evidence discipline rather than as loosely matched benchmark context.
4. Strengthen alignment evaluation with dedicated ambiguity and error-analysis studies instead of relying only on aggregate unmatched-rate reporting.
5. Extend bounded-guidance outputs so Chapter 6 conclusions can reference richer failure-mode taxonomies generated directly from the artefact [@andjelkovic_moodplay_2019; @liu_aggregating_2025].

## 6.7 Chapter Summary
The rebuilt evidence suggests that the central engineering challenge is not simply to generate playlists deterministically, but to do so in a way that keeps uncertainty, trade-offs, mechanism linkage, and limits visible. The artefact now provides stronger support for that bounded claim than the pre-rebuild pipeline did, because its evaluation surfaces are more explicit, more executable, and more disciplined about what the evidence does and does not justify.
