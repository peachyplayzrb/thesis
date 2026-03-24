# Paper PDF Resolution Checklist (2026-03-23)

Purpose: resolve remaining paper-note to PDF gaps after repository-wide audit.
Source audit: `03_literature/paper_note_pdf_audit_full_2026-03-23.md`

## Priority Order
1. P-011 `adomavicius_toward_2005` (missing PDF)
2. P-003 `tintarev_evaluating_2012` (ambiguous)
3. P-055 `jannach_measuring_2019` (ambiguous)
4. P-056 `sanchez_pointofinterest_2022` (ambiguous)

## Action Checklist

- [x] P-011 `adomavicius_toward_2005`
  - Required PDF title:
    - Toward the next generation of recommender systems: a survey of the state-of-the-art and possible extensions (2005)
  - Current status:
    - No matching local PDF detected in `10_resources/**`
  - Action:
    - Add PDF to `10_resources/papers/` (or canonical subfolder) with clear filename containing author/year keywords.
    - Re-run audit and verify status changes from `missing_pdf` to `matched`.

- [x] P-003 `tintarev_evaluating_2012`
  - Required PDF title:
    - Evaluating the effectiveness of explanations for recommender systems (2012)
  - Current status:
    - Best candidate currently maps to 2007 survey PDF (wrong paper).
  - Action:
    - Add exact 2012 PDF to `10_resources/papers/`.
    - Keep 2007 survey PDF as separate source for P-002.
    - Re-run audit and verify P-003 is `matched`.

- [x] P-055 `jannach_measuring_2019`
  - Required PDF title:
    - Measuring the Business Value of Recommender Systems (2019)
  - Current status:
    - Best candidate currently maps to Bonnin and Jannach (2015), not the 2019 paper.
  - Action:
    - Add exact 2019 PDF to `10_resources/papers/`.
    - Re-run audit and verify P-055 is `matched`.

- [x] P-056 `sanchez_pointofinterest_2022`
  - Required PDF title:
    - Point-of-Interest Recommender Systems Based on Location-Based Social Networks: A Survey from an Experimental Perspective (2022)
  - Current status:
    - Best candidate currently maps to Fkih (2022), not the Sanchez and Bellogin paper.
  - Action:
    - Add exact 2022 PDF to `10_resources/papers/`.
    - Re-run audit and verify P-056 is `matched`.

## Verification Step
After adding PDFs, re-run the generated audit process and confirm:
- `03_literature/paper_note_pdf_audit_full_2026-03-23.md` has:
  - `missing_pdf: 0`
  - `ambiguous: 0` (or only intentional non-standard filename matches)

## Completion Update (2026-03-23)
- Imported all four target PDFs from user-provided patch bundle.
- Re-ran full audit.
- Current summary (`03_literature/paper_note_pdf_audit_full_2026-03-23.md`):
  - `matched: 65`
  - `missing_pdf: 0`
  - `ambiguous: 0`

## Notes
- Canonical filenames were added for previously non-standard cases:
  - `Yu et al. - 2024 - Self-Supervised Learning for Recommender Systems A Survey.pdf`
  - `Bertin-Mahieux et al. - 2011 - The Million Song Dataset.pdf`
