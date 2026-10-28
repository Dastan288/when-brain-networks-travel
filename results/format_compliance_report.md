# Format compliance report — AIDA 2026 (Elsevier Procedia Computer Science), revised 2026-09-11 (third review)

Artefact: `paper/wbnt_aida2026.docx`, built from `paper/manuscript.md` by `paper/build_docx.py` inside the official `paper/template.docx` (downloaded from aida.scika.org on 2026-09-09), and its LibreOffice rendering `paper/wbnt_aida2026.pdf` (**8 pages**).

Ground truth (aida.scika.org, verified 2026-09-01, PROGRESS.md §0): full paper 6–8 pages; double-blind (no author names or affiliations in the initial submission); Procedia CS proceedings; deadline 15 Sep 2026.

| # | item | status | evidence |
|---|---|---|---|
| 1 | Title: capitalization per template sample, no trailing period | PASS | Els-Title paragraph |
| 2 | Abstract: self-contained, no citations, concrete numbers | PASS | 219 words (cut from 240 to 205, then +14 for the precision fixes of the fourth review: "statistically supported advantage", "a reference model fitted on training data, evaluated both without target statistics and with unlabeled target-batch adjustment", "after the modeled linear age- and sex-related effects were regressed out"; the template states no abstract limit); 0.65 [0.62, 0.68], 0.46, 0.61, 0.58, 0.59→0.55, ≤ 0.05; ComBat described as "reference model fitted on training data only, evaluated both without target statistics and with unlabeled target-batch adjustment" |
| 3 | Keywords: italic "Keywords:" label, semicolon-separated | PASS | 8 keywords, Els-keywords style |
| 4 | Headings: 1., 2., … and 1.1, 1.2 … via the template's numbering; Introduction first, Conclusion last before References | PASS | 1 Introduction · 2 Related work · 3 Materials and methods (3.1–3.4) · 4 Results (4.1–4.3) · 5 Discussion · 6 Conclusion · References |
| 5 | Tables: Arabic numbering in order of first mention; caption ABOVE; cited as "Table N"; horizontal rules only; Els-table-text 8 pt; header row repeats when a table breaks | PASS | Table 1 (§3.1, §4.1), Table 2 (§4.3); both generated from the result CSVs. Table 2 spans the p6/p7 break with a repeated header row |
| 6 | Figure: Arabic numbering; caption BELOW; cited as "Fig. 1"; ≥ 300 dpi; grayscale-safe; legible type | PASS | redrawn for the second review: placed at 5.6 in ≈ 520 dpi, in-cell type ≈ 6.5 pt and axis type ≈ 6 pt on the printed page (it was ≈ 4 pt before); columns numbered 1–4 as in the rows so the labels no longer collide; all values printed in the cells, so the diverging map remains readable in grayscale |
| 7 | Equations | N/A | none displayed |
| 8 | References: Elsevier numbered brackets in order of first citation; template punctuation | PASS | 24 entries (the agreed maximum); first-appearance order verified on the built file by `paper/validate_template.py` (1…24, grouped brackets expanded); see `results/reference_integrity_report.md` (READY) |
| 9 | Length ≤ 8 pages including figures, tables and references | PASS | 8 pages in the LibreOffice rendering, with ≈ 13 empty lines left on page 8 after the abstract was shortened — re-check once in Word before upload |
| 10 | Language: en-US throughout; no IEEE or template leftovers | PASS | grep of the exported text finds no "Click here", "MACROBUTTON", "First Author", "Keywords—", "TABLE I"; en-US spellings verified (behavior, labeled, artifact, cataloged, analyzed) |
| 11 | Template untouched: page geometry, styles, headers/footers, copyright control | PASS | validator: "All validations PASSED" against the original. Two deliberate changes, both raised in review: (a) the shipped running heads and footers say "(2025)" while the title page says "(2026)" — only the year digits were rewritten to 2026; (b) the template carries the publication statement twice on page 1, in the body (conference-updated, © 2026) and again in the first-page footer (stale "1877-0509 © 2025 …"); the duplicated first-page footer is now emptied and the body statement kept. The conference header (CENTERIS / ProjMAN / HCist / AIDA / URBILITY 2026) is untouched |
| 12 | Nomenclature box / appendix / acknowledgements | N/A | not used; acknowledgements omitted for double-blind (restore at camera-ready) |
| 13 | PDF hygiene: fonts embedded, no author metadata | PASS | pdffonts: all embedded; pdfinfo: no Author; docProps creator/lastModifiedBy blanked |

## Double-blind anonymization

| item | status |
|---|---|
| Author block and affiliations replaced by "withheld for double-blind review" | PASS |
| Corresponding-author footnote (tel./e-mail) removed and blanked | PASS |
| Acknowledgements / funding absent | PASS |
| No repository URL; code "released upon acceptance" | PASS |
| No self-citations | PASS |
| Document and PDF metadata scrubbed | PASS |
| Submitted file name carries no author name (`wbnt_aida2026.docx/.pdf`) | PASS |

## Response to the reviewers' formatting points

*First review.* The "(2026)" vs "(2025)" mismatch between the title page and the running heads comes from the shipped template; the build rewrites only the year digits in `header1–3.xml` and `footer1–3.xml` and changes nothing else, so no Elsevier boilerplate was invented.

*Second review.* Page 1 showed two publication footers. The build now empties the stale first-page footer (`footer3.xml`, "1877-0509 © 2025 …") and keeps the body block the conference itself updated to 2026, leaving exactly one publication statement on page 1; the conference header is unchanged. The figure was redrawn so its type is legible at the printed size, and the page count stayed at 8 by compressing Related work, Discussion, the captions and two references — never fonts, margins or line spacing.

**Verdict: READY for submission** (all applicable items PASS; one item to re-confirm in Word: page count).
