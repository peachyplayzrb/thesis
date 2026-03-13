# Ingestion Rules For Existing Materials

These inputs are reference material and are not authoritative thesis truth.

## 1) System Architecture Diagram

Store at: `05_design/system_architecture.md`

Required metadata header:
- `DOCUMENT STATUS: working design`
- `CONFIDENCE: medium`
- `ROLE: design candidate`
- `SOURCE: author concept`

Procedure:
1. Capture the current architecture description and assumptions.
2. Extract explicit components, flows, and constraints.
3. Link each major design claim to supporting literature or mark as unverified.
4. Log mismatches in `00_admin/unresolved_issues.md`.

Rules:
- Treat architecture as evolving.
- AI may critique/refine architecture proposals.
- AI must not treat architecture as final system definition.

## 2) Old Literature Review

Store source at: `10_resources/previous_drafts/old_literature_review.md`

Required metadata header:
- `DOCUMENT STATUS: legacy literature synthesis`
- `CONFIDENCE: variable`
- `ROLE: extraction source`

Procedure:
1. Preserve original text as historical input.
2. Extract paper-level evidence into structured paper notes.
3. Update thematic notes using extracted evidence only.
4. Update gap tracker with support/challenge evidence and confidence.
5. Flag unsupported assertions before reuse.

Rules:
- Do not inherit old conclusions without source support.
- Prefer direct paper evidence over legacy summary statements.

## 3) Chapter 3 Master Information Sheet

Store at: `05_design/chapter3_information_sheet.md`

Required metadata header:
- `DOCUMENT STATUS: conceptual design guide`
- `CONFIDENCE: medium`
- `ROLE: architecture explanation draft`

Procedure:
1. Extract proposed architecture logic and design rationale.
2. Cross-check against current literature themes and gap statement.
3. Record conflicts as change proposals or unresolved issues.
4. Reuse valid sections as drafting support, not as fixed truth.

Rules:
- AI may reference this for architecture discussion.
- Architecture remains allowed to evolve during implementation.

## Conflict Handling Rule
- If architecture, literature themes, and gap claim conflict: flag and log options; do not force consistency by assumption.
