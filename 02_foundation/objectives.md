# Objectives

## Primary Objective

Build and evaluate a playlist generation pipeline where every stage can be inspected, adjusted, and reproduced, even when user data and candidate tracks come from different sources.

## Specific Objectives

1. Design a preference profiling approach from user listening history across different data sources.
2. Implement cross-source alignment and candidate filtering with explicit uncertainty handling.
3. Implement deterministic scoring and playlist assembly with controls for coherence, diversity, novelty, and ordering.
4. Produce explanation and logging outputs that show how pipeline decisions were made.
5. Evaluate how well the pipeline reproduces results and how playlist quality changes when settings are adjusted.
6. Identify the limits of the results and the conditions under which the conclusions apply.

## Scope Note

These objectives are bounded to a single-user deterministic pipeline. Collaborative filtering, deep-learning model novelty, and large-scale user studies remain outside the core artefact scope.
