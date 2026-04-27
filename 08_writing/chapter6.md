# Chapter 6: Discussion and Bounded Contribution

Chapter objective: interpret the Chapter 5 evaluation evidence against the active research question and contribution claim, while keeping every conclusion bounded to explicit objective-linked evidence.

## 6.1 Interpretation Frame
The research question asks how engineers can design and evaluate a deterministic playlist-generation pipeline so that preference inference, candidate generation, and playlist assembly remain transparent, controllable, and reproducible under cross-source uncertainty and multi-objective playlist trade-offs.

This discussion anchors to the explicit design-option comparison in Chapter 3.3.1. The question here is whether the selected deterministic staged option delivered the promised evidence quality under scope, not whether all other architecture families are inferior in general.

This chapter is organised around three lenses that follow directly from the thesis design posture:

1. uncertainty handling,
2. controllable trade-off engineering,
3. mechanism-linked evidence quality.

The core claim is this: under bounded single-user, cross-source conditions it is possible to engineer a playlist pipeline whose uncertainty, candidate-space decisions, scoring logic, explanation linkage, and reproducibility boundaries remain inspectable and auditable, even though controllability remains weaker than originally intended. This chapter explores what that claim now means given the evaluation evidence.

This chapter is not a benchmark-positioning chapter. It does not argue that deterministic methods are universally preferable to hybrid, collaborative, or deep recommender families. Instead, it asks whether the implemented artefact now produces evidence strong enough to support the bounded engineering claim established in Chapters 1 to 3 [@jannach_measuring_2019; @bauer_exploring_2024; @ferrari_dacrema_troubling_2021].

## 6.2 Findings in Relation to the Research Question
The current evidence supports five main findings.

### 6.2.1 Explicit uncertainty handling is a design requirement, not a reporting afterthought
Uncertainty visibility matters because cross-source alignment is always partial, and users making playlist decisions need to know where the data came from and how much confidence they should have. The implementation shows that preference inference should not treat imported interaction traces as direct preference truth, and it embeds this principle into the profiling path rather than retrofitting it as a post-hoc caveat. BL-003 and BL-004 now surface match confidence, source coverage, attribution, and uncertainty-related diagnostics directly in the active output contract—not hiding them in artifact logs. This supports the broader claim that uncertainty handling is a first-order design obligation for cross-source systems [@allam_improved_2018; @papadakis_blocking_2021].

### 6.2.2 Candidate generation is first-order recommendation logic
Candidate shaping determines which tracks can even reach the ranking stage, so it is not neutral preprocessing—it is an upstream design choice that the thesis must make explicit and defend. BL-005 evidence shows this directly: exclusion-path diagnostics and tranche-1 gate checks reveal that the eventual ranking and playlist outputs are strongly conditioned by which candidates survive filtering. This means any explanation and evaluation claims that focus only on final ranking would understate a critical part of causal behavior. By making the candidate path explicit—with named exclusion criteria and diagnostics—the thesis moves from hiding this upstream logic to defending it [@ferrari_dacrema_troubling_2021].

### 6.2.3 Deterministic scoring and assembly remain valuable because they keep trade-offs inspectable
Deterministic scoring and assembly remain valuable under this thesis scope because they keep trade-off pressure visible and adjustable throughout the ranking and selection process. BL-006 and BL-007 evidence shows this directly: score components, rule pressure, and assembly constraints remain directly inspectable rather than hidden in learned parameters. That does not prove that deterministic methods maximize recommendation quality in every setting, but it does show that they provide a practical substrate for auditable trade-off control under bounded scope, where engineering transparency and auditability are primary design goals rather than performance optimality [@roy_systematic_2022; @jannach_measuring_2019; @bonnin_automated_2015].

### 6.2.4 Explanation quality depends on mechanism linkage, not on narrative plausibility alone
This thesis defines explanation fidelity structurally—as alignment with actual scoring and assembly behavior—not as user-perceived persuasiveness or narrative plausibility. The tranche-2 and tranche-3 evidence from BL-008 shows this distinction directly: explanations are now more rigorous because they preserve both direct mechanism contributors (which scoring components drove the inclusion decision) and control-provenance snapshots (which rule constraints and boundary conditions applied). Reviewers can verify this mechanism-level fidelity at the artefact level by comparing the explanation payload against the actual scoring record [@zhang_explainable_2020; @tintarev_evaluating_2012; @sotirou_musiclime_2025]. What remains unknown—and is beyond the scope of this thesis—is whether users perceive these mechanism-linked explanations as useful or persuasive. That claim requires longitudinal user study, which is not available in the single-user corpus. The thesis therefore establishes what the mechanism can support (structural fidelity) without claiming what users will experience (perceived usefulness). The project completed the O4 structural cross-check for selected tracks within the submission window; the full 30-track sample including rejected and boundary-ranked tracks remains a confirmation item for post-submission verification. This thesis treats this partial result as a methodological boundary rather than an implementation failure, consistent with Chapter 5's O4 Partially Satisfied verdict.

### 6.2.5 Bounded guidance becomes more credible when limits are part of the contract
The most important late-stage design improvement is that validity boundaries are now explicit, top-level, and test-enforced in BL-009. This changes the discussion posture: instead of adding caveats only in prose after evaluation, the artefact itself now emits scope, known limits, and run-specific caveats. That makes Chapter 6 conclusions more defensible because the artefact enforces boundedness rather than retrofitting it in narrative. This matters epistemologically: rather than being hedged in prose after the fact, the thesis conclusions are pre-specified as bounded claims before evaluation begins, which is a stronger form of intellectual honesty than retrospective limitation-adding [@beel_towards_2016; @bellogin_improving_2021; @cavenaghi_systematic_2023].

### 6.2.6 Controllability as an engineering finding, not a verdict collapse
Chapter 5 defines the O5 controllability objective through observable control-effect measurements under the BL-011 measurable-delta gate. The evidence shows this objective as **Not Satisfied**: some control surfaces (particularly genre flexibility under strict valence constraints) produce no-op or near-no-op effects despite nominally being present in the control surface. This is not an implementation fault; it is an engineering finding that reveals where the current design approach meets its limits. What matters for the discussion is not defending O5 as satisfied, but interpreting what the no-op result means: (1) certain preference dimensions cannot be reliably shaped through the current architecture without disturbing other objectives, (2) the sensitivity region of the controls is narrower than the design initially assumed, and (3) deeper intervention mechanisms (possibly neural or semi-supervised) might be needed to address these harder control cases. This is valuable negative evidence that bounds the thesis claim and informs future work [@jannach_measuring_2019].

### 6.2.7 Cross-source alignment as a scope boundary with practical consequences
The 15.95% canonical-baseline alignment rate between the Spotify listening history and the offline Music4All corpus is not a methodological failure; it is a real scope boundary that must shape what the thesis claims about profile completeness and playlist diversity. Working from the matched subset (rather than the full listening history) means that the resulting user profile captures genre and artist preferences, but only for the 15.95% slice that both sources record. This creates downstream consequences: (1) profile-level diversity metrics remain limited to candidates available in the matched subset, (2) representational coverage for rare genres or niche artists depends entirely on what the offline corpus contains, (3) serendipity and novelty recommendations depend on the alignment coverage rather than on the recommendation logic alone. These are not design failures — they are engineering facts that clarify what profile inference actually means in a cross-source setting. The thesis claim stays bounded: the pipeline can maintain uncertainty, controllability, and reproducibility for playlists built from the matched subset, but it cannot claim full listening-history fidelity or universal genre coverage [@lu_recommender_2015].

## 6.3 Contribution Interpretation
The contribution is best understood as an engineering-evidence contribution rather than a model-performance contribution. The five findings above collectively establish that deterministic architecture yields strong auditability and mechanism-linkage evidence under the thesis scope, even though it carries design trade-offs that weaker alternatives might avoid.

What the thesis now demonstrates is not that one deterministic playlist pipeline is universally best, but that it is possible to co-engineer:

1. explicit uncertainty signaling during preference inference,
2. controllable candidate and assembly trade-offs,
3. mechanism-linked explanations,
4. executable reproducibility and controllability evidence,
5. explicit validity-boundary reporting.

Taken together, these give the thesis a clearer and more defensible contribution than earlier design framings, which concentrated more on generic transparency/observability language than on explicit objective-to-evidence traceability [@balog_transparent_2019; @knijnenburg_explaining_2012; @afroogh_trust_2024].

The current evidence supports the selected deterministic path (relative to the option space in Section 3.3.1) because it yields the strongest mechanism-level traceability within this thesis scope. Interpret this as a bounded design-fit finding under current objectives and constraints, not as a verdict against hybrid or neural alternatives.

However, the cost side of this choice deserves explicit naming. Deterministic pipeline architecture prioritizes inspectability and replayability, but it likely sacrifices representational flexibility compared to neural or hybrid alternatives that can adjust their latent representations across runs. The fixed component weights and rule-based constraints that make the scoring and assembly logic transparent also make it harder to adapt to subtle preference shifts or to capture latent genre or mood structure that would require learned representations. Moreover, the BL-011 evidence on weak control surfaces suggests that some controllability hopes (particularly around genre flexibility under tight valence constraints) remain difficult even with explicit architectural support. The deterministic choice is not invalidated by these costs—they are the price of auditability—but they do bound what the thesis can claim about playlist quality or user adaptability.

## 6.4 Limits of the Current Evidence
The current evidence still has important limits.

1. Cross-source preference traces remain indirect evidence of user preference rather than causal ground truth.
2. Alignment uncertainty remains material; in the canonical active baseline, only 15.95% of imported Spotify history aligns to the offline corpus, so profile-level claims remain bounded to the matched subset rather than the full listening history.
3. Some control surfaces remain weak or data-regime-dependent, as shown by BL-011 no-op diagnostics.
4. Reproducibility claims are contract-bounded to artifact-level stable-hash consistency under declared fixed inputs, replay procedures, and a pinned configuration snapshot. They do not extend to cross-environment behavioral invariance, output identity under different run configurations, or environmental runtime invariance beyond the fixed-input and configuration window used in replay.
5. External validity remains narrow because the artefact is single-user, deterministic, and not evaluated through longitudinal user studies.
6. Comparator depth remains bounded. No algorithmic baseline (e.g. popularity rank, BPM-sorted random, or collaborative-filter rerank) was implemented alongside the main artefact. Three grounds justify this exclusion. First, the thesis is positioned as Design Science Research, where the primary evaluation obligation is demonstrating that the artefact satisfies its own design objectives — not that it outperforms an arbitrary comparator on an offline metric [@hevner_design_2004]. Second, a fair algorithmic comparator would require shared offline evaluation data (playback logs with known preference outcomes) that are unavailable in the single-user Music4All + Spotify-export corpus used here; any comparator run on this corpus would produce noise, not signal. Third, the controllability and transparency objectives (RQ-B, RQ-C) have no natural mapping to a comparable baseline — popularity rank carries no influence model, and a BPM-sorted baseline has no explanation surface. The design scope and the data constraints jointly make a comparator study out of scope for the current contribution. Future work should introduce comparators only if a suitable multi-user evaluation corpus becomes available and if the comparator implements an equivalent transparency and controllability interface [@flexer_problem_2016].

These limits do not collapse the contribution. They bound it to auditable engineering evidence under explicit scope rather than broad recommender-performance claims [@flexer_problem_2016; @papadakis_blocking_2021; @jin_effects_2020].

## 6.5 Implications for Design Science Positioning
The implementation also sharpens the methodological interpretation of the artefact. In Design Science terms, the value of the artefact lies not only in producing playlists, but in making design claims testable through explicit control and evidence contracts. The REB-M3 tranche gates are especially important here because they turn objective satisfaction into executable acceptance checks instead of relying only on narrative consistency across chapters. This DSR posture explains why the thesis looks different from a conventional CS project report: the methodology requires the artefact to generate and verify design evidence, not add it through post-hoc narrative closure after implementation is complete.

This is a stronger DSR posture than the legacy chapter framing because it narrows the gap between design intent, implemented control surface, and reported evidence [@anelli_elliot_2021; @zhu_bars_2022].

## 6.6 Future Work
Future work should extend the artefact without breaking the evidence discipline established in the current implementation.

1. Deepen control-effect analysis by moving from one-factor-at-a-time tests to interaction-aware control studies.
2. Resolve open influence-track design questions, especially whether explicit user intent should override assembly constraints and how weak influence effects should be reported.
3. Add comparator pipelines only when they can be evaluated under the same objective-to-evidence discipline rather than as loosely matched benchmark context.
4. Strengthen alignment evaluation with dedicated ambiguity and error-analysis studies instead of relying only on aggregate unmatched-rate reporting.
5. Extend bounded-guidance outputs so Chapter 6 conclusions can reference richer failure-mode taxonomies generated directly from the artefact [@andjelkovic_moodplay_2019; @liu_aggregating_2025].

## 6.7 Chapter Summary
The implementation demonstrates that the central engineering challenge is not simply to generate playlists deterministically, but to do so in a way that keeps uncertainty, trade-offs, mechanism linkage, and limits visible. The current evidence indicates that under bounded single-user, deterministic, cross-source conditions, the project can engineer a playlist generation pipeline whose evidence surfaces remain transparent, whose controllability remains auditable, and whose reproducibility remains verifiable through explicit artefact contracts. The limits of controllability—particularly the sensitivity region of the tested control parameters—mark the clearest boundary on what the current thesis can claim. Yet within those bounds, the thesis has demonstrated that deterministic architecture yields stronger mechanism-level traceability and evidence discipline than earlier design iterations, because its evaluation surfaces are explicit, executable, and honest about what the evidence does and does not justify.
