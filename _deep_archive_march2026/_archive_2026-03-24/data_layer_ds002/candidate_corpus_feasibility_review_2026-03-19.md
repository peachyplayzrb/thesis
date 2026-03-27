# Candidate Corpus Feasibility Review (2026-03-19)

## Scope
This review compares the current accepted candidate corpus path:
- DS-001: Music4All-Onion with optional base-Music4All enrichments

against the proposed alternative:
- DS-002: Million Song Dataset subset + Last.fm tags + MusicBrainz mapping

The review is bounded to MVP feasibility, transparency, controllability, observability, reproducibility, and alignment with the current thesis wording.

## Review Criteria
1. Access and practical availability
2. Extraction and implementation complexity
3. Feature coverage for deterministic scoring and explanations
4. Cross-source alignment support
5. Candidate-pool adequacy for playlist generation
6. Impact on current thesis state and writing

## Comparison Summary

| Criterion | DS-001 Music4All-Onion | DS-002 MSD subset + Last.fm + MusicBrainz | Better fit |
| --- | --- | --- | --- |
| Access in current environment | Onion files are already downloaded, audited, and selectively extracted. Base Music4All is inaccessible. | Publicly documented route looks simpler, but acquisition and extraction have not yet been verified in this repo. | DS-001 for immediate execution |
| Implementation effort | Join path already inspected; selected files and columns are known. | Requires new `.h5` extraction workflow, schema confirmation, and multi-source join validation. | DS-001 |
| Transparent features | Strong on interpretable audio, lyrics sentiment, tags, and named genres. | Strong on core metadata, tempo/loudness/key/mode, and tags. Simpler but narrower. | DS-001 slightly |
| Alignment support | Weak for ISRC-first matching without base metadata, but still usable for track_id-centric internal pipeline work. | Proposed sheet does not confirm corpus-side ISRC, so current ISRC-first thesis wording weakens further. | DS-001 slightly |
| Candidate diversity | 109,269-track scale in Onion path. | 10,000-song subset in the proposed sheet. | DS-001 clearly |
| Thesis change cost | No protected-state rewrite required if Onion-only remains active. | Requires synchronized updates across thesis state, objectives, assumptions, limitations, and chapters. | DS-001 |

## Main Findings

### 1. Base Music4All is not usable here
The original combined plan assumed a base-Music4All metadata layer plus Onion enrichments. In the current environment that assumption fails because base access is blocked. That makes the original `base + Onion` design redundant for MVP execution and means the practical choice is between:
- Onion-only, using the assets already available, or
- a full switch to a new corpus.

### 2. Music4All-Onion is not itself redundant
Although the base dataset is unusable, Onion still provides substantial interpretable information already present in the workspace:
- listening-event tables
- Essentia audio descriptors
- lyrics sentiment summaries
- Last.fm tags
- named genre features

That is enough to support a deterministic, transparent MVP candidate layer with explicit limitations.

### 3. The MSD-based option is cleaner on paper but worse for the current MVP
The proposed MSD strategy has a neat Chapter 3 narrative and a smaller, easier-to-explain schema. But for this project state it introduces more rework than benefit:
- smaller active corpus
- new extraction code path
- new join-validation work
- no confirmed improvement to ISRC-first alignment
- immediate writing/governance churn

### 4. The best bounded interpretation is this
The redundant part is not Onion. The redundant part is the expectation that the MVP still needs base Music4All metadata in order to proceed.

## Recommendation
Do not switch the canonical MVP corpus to the MSD subset path.

Keep DS-001 active, but reinterpret it operationally as an Onion-only corpus for MVP implementation and evaluation.

Treat DS-002 as a fallback or future contingency only if one of the following happens:
- Onion-only join coverage proves too weak for usable candidate construction
- explanation quality is materially worse than expected after BL-017
- a later review shows the MSD path gives clearly better matching support without destabilizing thesis scope

## Required Follow-on Actions
1. Mark BL-018 complete with recommendation: keep Onion-only.
2. Update DS-001 notes so they explicitly state base access is unusable and the original combined base-plus-Onion plan is redundant for MVP.
3. Keep DS-002 registered as a reviewed fallback option, not the active corpus.
4. Proceed to BL-017 using the already extracted Onion files.

## Final Verdict
For this thesis, on this date, with this environment, the best decision is:

Keep Music4All-Onion as the active MVP corpus.

Do not switch to the proposed MSD subset path.

Base Music4All should be treated as unavailable and non-blocking rather than as a dependency that implementation still waits for.