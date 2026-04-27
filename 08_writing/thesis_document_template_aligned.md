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

### 1.1 Project Motivation

[Introduce the music discovery problem, information overload, recommender systems, and why playlist generation is an appropriate project context.]

### 1.2 Recommender Systems and Music Recommendation

[State the engineering problem clearly: many recommender systems optimize prediction utility, but transparency, controllability, observability, and reproducibility are often under-served in practical pipeline design.]

### 1.3 Cross-Source Data, Transparency, and Controllability

[Use current Chapter 1 content.]

### 1.4 Research Question, Aim, and Objectives

#### Research Question

What design considerations shape the engineering of a transparent, controllable, and observable automated playlist generation pipeline using cross-source music preference data?

#### Aim

[Use current Chapter 1 aim statement.]

#### Objectives

1. Design an automated pipeline that generates playlists from user listening histories.
2. Align cross-platform music data with the Music4All dataset using ISRC-based track matching.
3. Construct a deterministic user preference profile based on imported listening data and manually selected influence tracks.
4. Generate candidate tracks from the Music4All dataset using feature-based filtering.
5. Score candidate tracks using deterministic similarity functions and rule-based adjustments.
6. Assemble playlists using playlist-level rules that ensure diversity, coherence, and ordering.
7. Provide transparent explanations and observability mechanisms for recommendation decisions.
8. Evaluate the system with respect to transparency, controllability, inspectability, and reproducibility.

### 1.5 Scope and Boundaries

[Define the locked MVP scope: single-user, deterministic, content-based, one practical ingestion path, no collaborative/deep baseline in core scope, and no large-scale user study.]

### 1.6 Contribution of the Project

[State the contribution as engineering/design evidence, not model novelty. Summarize the artefact, traceability design, and evaluation contribution.]

### 1.7 Report Framework

[Give a short paragraph summarizing each chapter.]

### 1.8 Chapter Summary

[Close the chapter by linking the problem framing to the literature review.]

## Chapter 2: Literature Review

[Open with a short chapter-introduction paragraph explaining that the chapter builds the design rationale and evidence boundary for the artefact.]

### 2.1 Foundations and Scope of Recommender Systems

[Use current Chapter 2 content.]

### 2.2 Core Recommendation Paradigms and Their Trade-offs

[Use current Chapter 2 content.]

### 2.3 Transparency, Explainability, and User Control in Recommender Literature

[Use current Chapter 2 content.]

### 2.4 Preference Evidence, Profile Construction, and Candidate Generation

[Use current Chapter 2 content.]

### 2.5 Music Recommendation and Playlist-Specific Challenges

[Use current Chapter 2 content.]

### 2.6 Feature-Based and Latent Approaches: Comparative Strengths and Limits

[Use current Chapter 2 content.]

### 2.7 Cross-Source Alignment and Reproducibility

[Use current Chapter 2 content. End with the explicit handoff into Chapter 3.]

### 2.8 Research Gap and Thesis Positioning

[Summarize the literature-derived design implications and transition to design/methodology.]

### 2.9 Chapter Summary

[Use current Chapter 2 chapter summary.]

## Chapter 3: Design and Methodology

[Open with a short chapter-introduction paragraph stating that Chapter 3 converts literature consequences into explicit engineering commitments for later testing.]

### 3.1 Introduction

[Use current Chapter 3 content.]

### 3.2 Design Methodology

[Use current Chapter 3 content.]

### 3.3 Literature-Driven Design Requirements

[Use current Chapter 3 content.]

#### 3.3.1 Design Option Space and Selected-Design Rationale

[Use current Chapter 3 content.]

### 3.4 Design Scope and Overall Architecture

[Use current Chapter 3 content.]

#### 3.4.1 Assumptions and Boundaries

[Use current Chapter 3 content.]

### 3.5 Technology Choices and Realisation Context

[Use current Chapter 3 content.]

### 3.6 Cross-Source Preference Evidence and Alignment

[Use current Chapter 3 content.]

### 3.7 Preference Profiling

[Use current Chapter 3 content.]

### 3.8 Candidate Shaping

[Use current Chapter 3 content.]

### 3.9 Deterministic Scoring

[Use current Chapter 3 content.]

### 3.10 Playlist Assembly

[Use current Chapter 3 content.]

### 3.11 Explanation and Run-Level Observability

[Use current Chapter 3 content.]

### 3.12 Configuration and Experimental Control

[Use current Chapter 3 content.]

### 3.13 Chapter Summary

[Summarize the design commitments and state that Chapter 4 evaluates whether the implementation and evidence support them.]

## Chapter 4: Implementation Architecture and Evidence Surfaces

[Open with a short chapter-introduction paragraph stating that this chapter reports implementation architecture, evidence contracts, and stage-level behaviour under bounded scope.]

### 4.1 Chapter Aim and Scope

[Use current Chapter 4 content.]

### 4.2 Design-to-Implementation Bridge

[Use current Chapter 4 content.]

### 4.3 BL-003: Cross-Source Alignment and Evidence Intake

[Use current Chapter 4 content.]

### 4.4 BL-004: Preference Profiling from Aligned Evidence

[Use current Chapter 4 content.]

### 4.5 BL-005: Candidate Shaping and Search-Space Definition

[Use current Chapter 4 content.]

### 4.6 BL-006: Deterministic Scoring with Decomposable Components

[Use current Chapter 4 content.]

### 4.7 BL-007: Playlist Assembly with Explicit Trade-offs

[Use current Chapter 4 content.]

### 4.8 BL-008: Mechanism-Linked Explanations

[Use current Chapter 4 content.]

### 4.9 BL-009: Run-Level Observability and Full Execution Footprint

[Use current Chapter 4 content.]

### 4.10 BL-010 and BL-011: Reproducibility and Controllability Instrumentation

[Use current Chapter 4 content.]

### 4.11 Evidence Packaging and Artefact Surface

[Use current Chapter 4 content.]

### 4.12 Chapter Summary

[Use current Chapter 4 content.]

## Chapter 5: Evaluation and Results

[Open with a short chapter-introduction paragraph stating that this chapter evaluates objective-linked evidence against pre-specified success criteria.]

### 5.1 Chapter Aim and Scope

[Use current Chapter 5 content.]

### 5.2 Evaluation Method and Locked Criteria

[Use current Chapter 5 content.]

### 5.3 O5 Evidence First: Reproducibility and Controllability

[Use current Chapter 5 content.]

#### 5.3.1 Control-Surface Ablation and Sensitivity Write-Through

[Use current Chapter 5 content.]

### 5.4 O1 Evidence: Uncertainty-Aware Profiling

[Use current Chapter 5 content.]

### 5.5 O2 Evidence: Confidence-Aware Alignment and Candidate Shaping

[Use current Chapter 5 content.]

### 5.6 O3 Evidence: Controllable Trade-Offs

[Use current Chapter 5 content.]

### 5.7 O4 Evidence: Mechanism-Linked Explanation Fidelity

[Use current Chapter 5 content.]

### 5.8 O6 Evidence: Bounded-Guidance Surfaces

[Use current Chapter 5 content.]

### 5.9 Control-Causality and Boundary Hardening Context

[Use current Chapter 5 content.]

### 5.10 Objective Synthesis and Acceptance Status

[Use current Chapter 5 content.]

### 5.11 Evaluation Boundaries, Non-Claims, and Chapter 6 Handoff

[Use current Chapter 5 content.]

### 5.12 Chapter Summary

[Use current Chapter 5 content.]

## Chapter 6: Conclusion

[Open with a short chapter-introduction paragraph that closes the thesis by directly answering the research question under the stated scope boundaries.]

### 6.1 Findings in Relation to the Research Question

[Use current Chapter 6 findings synthesis and make the answer to the research question explicit.]

### 6.2 Overall Contribution

[Use current Chapter 6 contribution interpretation, focused on what was achieved and evidenced.]

### 6.3 Scope-Bounded Claims and Limits

[Use current Chapter 6 limits material and non-claims in concise conclusion form.]

### 6.4 Future Work

[Use current Chapter 6 future work content and keep it directly tied to identified limits.]

### 6.5 Final Closing Statement

[Add one short final paragraph that states the thesis-level conclusion clearly and definitively.]

## Chapter 7: Critical Evaluation and Processes

[Open with a short chapter-introduction paragraph evaluating process quality, methodological rigor, and execution decisions across the project lifecycle.]

### 7.1 Critical Evaluation of Design Choices

[Evaluate strengths/weaknesses of the deterministic, transparency-first architecture and key trade-offs made.]

### 7.2 Critical Evaluation of Implementation and Evidence Quality

[Evaluate implementation robustness, evidence sufficiency, reproducibility posture, and any remaining evidence risks.]

### 7.3 Testing, Validation, and Error-Handling Reflection

[Summarize what testing strategy worked, what failed, and what would be improved in hindsight.]

### 7.4 Project Management and Process Reflection

[Summarize planning, replanning, supervision engagement, risk handling, and execution discipline.]

### 7.5 Lessons Learned and Improvement Priorities

[List the highest-value lessons and practical process improvements for future iterations.]

### 7.6 Chapter Summary

[Close the chapter by summarizing critical reflection outcomes and readiness of the final report package.]

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
