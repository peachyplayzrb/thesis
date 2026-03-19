# Thesis Document Template

## Cover Page

University of Wolverhampton

BSc (Hons) Computer Science

Final Project Report

Student Name: [Insert name]

Student Number: [Insert student number]

Location/Site: [Insert campus if required]

Module Code: [Insert module code]

Module Name: Project and Professionalism

Project Title: Engineering an Automated, Transparent, and Controllable Playlist Generation Pipeline Using Cross-Source Music Preference Data

Supervisor Name: [Insert supervisor]

Reader Name: [Insert if required]

Submission Date: [Insert date]

Award Title: BSc (Hons) Computer Science

## Declaration Sheet

Presented in partial fulfilment of the assessment requirements for the above award.

This work or any part thereof has not previously been presented in any form to the University or to any other institutional body whether for assessment or for other purposes. Save for any express acknowledgements, references and/or bibliographies cited in the work. I confirm that the intellectual contents of the work is the result of my own efforts and of no other person.

It is acknowledged that the author of any project work shall own the copyright. However, by submitting such copyright work for assessment, the author grants to the University a perpetual royalty-free licence to do all or any of those things referred to in section 16(i) of the Copyright Designs and Patents Act 1988. (viz: to copy work; to issue copies to the public; to perform or show or play the work in public; to broadcast the work or to make an adaptation of the work).

Student Name (Print): [Insert name]

Student Number: [Insert student number]

Signature: [Insert electronic signature if required]

Date: [Insert date]

(Must include the unedited statement above. Sign and date.)

Please use an electronic signature (scan and insert).

## Abstract

[Write 200 to 300 words covering: problem context, research question, artefact approach, core methodology, evaluation approach, and main findings.]

## Acknowledgements

[Optional short acknowledgements paragraph.]

## Table of Contents

[Auto-generated in Word.]

## List of Figures

[Auto-generated in Word.]

## List of Tables

[Auto-generated in Word.]

## List of Abbreviations

[Optional. Include only if the final document uses enough technical abbreviations to justify it, for example DSR, ISRC, and MVP.]

## Chapter 1: Introduction

### 1.1 Background and Context

[Introduce the music discovery problem, information overload, recommender systems, and why playlist generation is an appropriate project context.]

### 1.2 Problem Statement

[State the engineering problem clearly: many recommender systems optimize prediction utility, but transparency, controllability, observability, and reproducibility are often under-served in practical pipeline design.]

### 1.3 Research Question

What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

### 1.4 Research Objectives

1. Design an automated pipeline that generates playlists from user listening histories.
2. Align cross-platform music data with the Music4All dataset using ISRC-based track matching.
3. Construct a deterministic user preference profile based on imported listening data and manually selected influence tracks.
4. Generate candidate tracks from the Music4All dataset using feature-based filtering.
5. Score candidate tracks using deterministic similarity functions and rule-based adjustments.
6. Assemble playlists using playlist-level rules that ensure diversity, coherence, and ordering.
7. Provide transparent explanations and observability mechanisms for recommendation decisions.
8. Evaluate the system with respect to transparency, controllability, inspectability, and reproducibility.

### 1.5 Scope and Delimitations

[Define the locked MVP scope: single-user, deterministic, content-based, one practical ingestion path, no collaborative/deep baseline in core scope, and no large-scale user study.]

### 1.6 Research Contributions

[State the contribution as engineering/design evidence, not model novelty. Summarize the artefact, traceability design, and evaluation contribution.]

### 1.7 Thesis Structure

[Give a short paragraph summarizing each chapter.]

### 1.8 Chapter Summary

[Close the chapter by linking the problem framing to the literature review.]

## Chapter 2: Literature Review

[Open with a short chapter-introduction paragraph explaining that the chapter builds the design rationale and evidence boundary for the artefact.]

### 2.1 Foundations, Scope, and Thesis Positioning

[Use current Chapter 2 content.]

### 2.2 Core Recommendation Paradigms and Their Trade-offs

[Use current Chapter 2 content.]

### 2.3 Transparency, Explainability, Controllability, Observability, and Evaluation

[Use current Chapter 2 content.]

### 2.4 Preference Evidence, Profile Construction, and Candidate Shaping

[Use current Chapter 2 content.]

### 2.5 Music Recommendation and Playlist-Specific Challenges

[Use current Chapter 2 content.]

### 2.6 Deterministic Design Rationale and Comparator Context

[Use current Chapter 2 content.]

### 2.7 Cross-Source Alignment, Reproducibility Governance, and Synthesis

[Use current Chapter 2 content. End with the explicit handoff into Chapter 3.]

### 2.8 Chapter Summary

[Summarize the literature-derived design implications and transition to design/methodology.]

## Chapter 3: Design and Methodology

[Open with a short chapter-introduction paragraph stating that Chapter 3 converts literature consequences into explicit engineering commitments for later testing.]

### 3.1 Design Methodology

[Use current Chapter 3 content.]

### 3.2 Literature-Driven Design Requirements

[Use current Chapter 3 content.]

### 3.3 Overall System Architecture

[Use current Chapter 3 content.]

### 3.4 Data Ingestion and Alignment

[Use current Chapter 3 content.]

### 3.5 Preference Modelling and Candidate Preparation

[Use current Chapter 3 content.]

### 3.6 Deterministic Scoring and Playlist Assembly

[Use current Chapter 3 content.]

### 3.7 Explanation, Observability, and Reproducibility

[Use current Chapter 3 content.]

### 3.8 Configuration and Execution Control

[Use current Chapter 3 content.]

### 3.9 Decision Traceability

[Use current Chapter 3 content.]

### 3.10 Literature-to-Design Traceability

[Use current Chapter 3 content.]

### 3.11 Requirement, Mechanism, and Evidence Mapping

[Use current Chapter 3 content.]

### 3.12 Core Decision Logic Diagrams

[Use current Chapter 3 content and final diagrams.]

### 3.13 Chapter Summary

[Summarize the design commitments and state that Chapter 4 evaluates whether the implementation and evidence support them.]

## Chapter 4: Implementation, Testing and Evaluation

[Open with a short chapter-introduction paragraph stating that this chapter reports implemented behaviour and evidence, not universal superiority claims.]

### 4.1 Chapter Aim and Scope

[Use current Chapter 4 content.]

### 4.2 Evaluation Criteria and Success Conditions

[Define the evaluation criteria used in this thesis and link each one to an operational success condition. Keep the criteria aligned to the locked evaluation plan: reproducibility, traceability, controllability, constraint compliance, and testing quality.]

### 4.3 Design-to-Evaluation Traceability

[Use current Chapter 4 content.]

### 4.4 Implementation Overview

[Describe the implemented pipeline stage by stage: ingestion and normalization, cross-source alignment, preference profile construction, candidate preparation, deterministic scoring, playlist assembly, explanation rendering, and run logging.]

### 4.5 Testing and Evaluation Procedure

[Set out the staged protocol used in Chapter 4, covering deterministic replay checks, alignment diagnostics, explanation-fidelity checks, one-factor-at-a-time controllability tests, and playlist-rule compliance checks.]

### 4.6 Evidence Package and Artefact Demonstration Basis

[Use current Chapter 4 content. Summarize how evidence is packaged for inspection and how the implemented artefact behaviour was demonstrated and verified.]

### 4.7 Evaluation Results Matrix

[Replace pending entries with actual results from test logs and experiment notes, using the evaluation-plan test IDs as the reporting contract.]

### 4.8 Reproducibility, Observability, and Alignment Results

[Insert replay results, run-schema checks, and observability completeness results.]

### 4.9 Controllability and Rule-Compliance Results

[Insert one-factor-at-a-time sensitivity results and playlist rule checks.]

### 4.10 Explanation Fidelity Results

[Insert reconstruction/error findings for explanation payloads.]

### 4.11 Evaluation Limits and Interpretation

[Use current Chapter 4 content and ensure any weak results are stated directly.]

### 4.12 Project Management and Process Evidence

[Summarize milestone control, supervisor engagement, replanning decisions, logbook continuity, and any material execution risks managed during the project. Keep this concise and evidence-linked.]

### 4.13 Chapter Summary

[Summarize what the evaluation supports, what remains limited, and how Chapter 5 will interpret the findings.]

## Chapter 5: Discussion, Critical Evaluation and Conclusion

[Open with a short chapter-introduction paragraph explaining that the chapter interprets results against the research question and scope constraints.]

### 5.1 Interpretation of Results and Comparator Framing

[Use current Chapter 5 content.]

### 5.2 Scope-Bounded Claims

[Use current Chapter 5 content.]

### 5.3 Findings in Relation to the Research Question

[Use current Chapter 5 content and revise once Chapter 4 is fully populated.]

### 5.4 Critical Evaluation

[Evaluate the artefact, method, evidence quality, design trade-offs, and what you would change in hindsight. Make strengths and weaknesses explicit rather than implied.]

### 5.5 Limitations

[State the limitations directly and concretely. At minimum consider artefact scope, alignment coverage, dependence on available feature descriptors, absence of collaborative or deep-model baselines, and the BSc-feasible evaluation boundary.]

### 5.6 Future Work

[Use current Chapter 5 content. Keep future work tightly connected to limitations and to the locked contribution focus rather than opening a new thesis.] 

### 5.7 Final Conclusion

[Add a short concluding section that directly answers the research question in one clear paragraph and closes the thesis.]

## References

[Harvard style. Ensure every in-text citation appears here and entries are consistently formatted.]

## Bibliography

[Optional. Include uncited background or supporting sources only if required or useful. If every listed source is cited in the text, this section can be omitted.]

## Appendices

### Appendix A: System Architecture Diagrams

[Insert full architecture diagrams and any expanded versions of Chapter 3 figures.]

### Appendix B: Configuration Profiles and Example Runs

[Insert representative configuration files, parameter sets, and run metadata examples.]

### Appendix C: Experiment Logs and Test Evidence

[Insert supporting logs, hashes, screenshots, and detailed result tables if too large for Chapter 4.]

### Appendix D: Extended Mapping Tables

[Insert any expanded requirement-mechanism-evidence tables or chapter handoff tables that are too large for the main body.]

### Appendix E: Additional Figures and Tables

[Insert supplementary tables, diagrams, or output examples.]

### Appendix F: Project Management Evidence Extracts

[Insert selected logbook pages, milestone snapshots, supervision record extracts, replanning evidence, or timeline artefacts if these are not already submitted separately and if including them strengthens the report evidence.] 