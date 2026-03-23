DOCUMENT STATUS: working design
CONFIDENCE: medium
ROLE: design candidate
SOURCE: author concept

# System Architecture

Treat this as an evolving design hypothesis.

## Layer Stack
1. User interaction
2. Data ingestion
3. Track alignment
4. Preference modelling
5. Candidate generation
6. Feature processing
7. Deterministic scoring
8. Playlist assembly
9. Output and explanation
10. Observability and audit
11. Configuration and execution

## Core Flow
External listening data + influence tracks -> normalized metadata + semantic enrichment -> preference profile -> candidate pool (with DS-002 audio features) -> deterministic scoring -> playlist assembly -> explanations + logs.

## Hypothesis Constraint
This architecture is provisional.
If literature evidence or implementation results conflict with current assumptions, propose refinement instead of forcing consistency.
