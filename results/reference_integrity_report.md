# Reference & cross-reference integrity report — AIDA 2026 (revised after the third peer review), 2026-09-11

Scope: `paper/manuscript.md` → `paper/wbnt_aida2026.docx` (built by `paper/build_docx.py`; citation numbers assigned by order of first appearance at build time; both tables generated from the result CSVs).

## Pass 1 — bibliographic accuracy (24 entries)

| # | key | claim supported in text | verified via | status |
|---|---|---|---|---|
| 1 | dimartino2014 | ABIDE I: 1112 scans, 539 ASD / 573 TC, 17 sites | PMID 23774715 | OK |
| 2 | adhd200consortium2012 | ADHD-200: 973 participants, 8 sites; competition won by a phenotype-only entry | OpenAlex W1560723556 | OK |
| 3 | poldrack2016 | UCLA-CNP: 130 HC / 50 SCHZ / 49 BP / 43 ADHD, ds000030 | PMID 27922632 | OK |
| 4 | yamashita2019 | site effects at least as large as disorder effects | PMID 30998673 | OK |
| 5 | kapoor2023 | leakage taxonomy incl. site leakage | PMID 37720327 | OK |
| 6 | rosenblatt2024 | leakage inflates connectome ML, incl. leaky site correction | PMID 38418819 | OK |
| 7 | nielsen2013 | ABIDE multi-site ~60 % vs single-site ~80 % | PMID 24093016 | OK |
| 8 | abraham2017 | 67 % inter-site prediction on ABIDE | PMID 27865923 | OK |
| 9 | woo2017 | external evaluation as the evidence standard for a biomarker | PMID 28230847 | OK |
| 10 | chekroud2024 | within-trial models at chance out of sample | PMID 38207039 | OK |
| 11 | johnson2007 | ComBat | PMID 16632515 | OK |
| 12 | fortin2018 | ComBat / neuroCombat for neuroimaging | PMID 29155184 | OK |
| 13 | marzi2024 | ComBat before the split leaks | nature.com page, 2026-09-09 (vol 11, art. 115) | OK |
| 14 | traut2022 | blinded ABIDE challenge: 0.80 internal vs 0.72 external AUC | PMID 35413445 | OK |
| 15 | cui2023 | GNN benchmark for brain networks | PMID 36318557 | OK |
| 16 | hu2023 | statistical and deep harmonization; evaluation metrics | PMID 37084926 | OK |
| 17 | craddock2013 | ABIDE Preprocessed / C-PAC derivatives | OpenAlex W2314945771 | OK |
| 18 | bellec2017 | ADHD-200 Preprocessed, Athena pipeline parameters | PMID 27423255 + bioRxiv full text | OK |
| 19 | esteban2019 | fMRIPrep, the pipeline behind the UCLA-CNP derivatives | PMID 30532080 | OK |
| 20 | gorgolewski2017 | UCLA-CNP fMRIPrep derivatives | OpenAlex W4252374256 | OK |
| 21 | tzourio2002 | AAL atlas | PMID 11771995 | OK |
| 22 | craddock2012 | CC200 functional parcellation (robustness check) | PMID 21769991 | OK |
| 23 | pedregosa2011 | scikit-learn (classifiers) | jmlr.org/papers/v12/pedregosa11a.html, checked 2026-09-11: JMLR 12, 2825–2830 | OK |
| 24 | abraham2014 | nilearn (time-series extraction, connectomes) | PMID 24600388 | OK |

All entries verified against PubMed / OpenAlex / publisher pages (2026-09-08, re-checked 2026-09-09/10/11). Five 2022–2026 references were added in the first revision (chekroud2024, traut2022, rosenblatt2024, hu2023); the second review added the two derivative/atlas sources it asked for (craddock2012 for CC200, esteban2019 for fMRIPrep), the third review added the software citations it asked for (pedregosa2011 for scikit-learn, abraham2014 for nilearn); cui2023 was restored once the shortened abstract freed space, and varoquaux2022 stays out to keep the list at the agreed maximum of 24 (the two sentences that cited it keep woo2017 and kapoor2023/rosenblatt2024). Entries not cited in the paper are listed at the end of `paper/references_verified.md` together with further verified recent works kept for the journal extension. DOIs are recorded in `references_verified.md` and omitted from the paper list to match the template sample.

## Pass 2 — numbering and usage

| check | result |
|---|---|
| order = first in-text appearance | PASS — assigned programmatically at build time and re-checked on the built file by `paper/validate_template.py`, which expands grouped brackets ([7, 8]) and ranges before testing the sequence: printed first-appearance order is 1, 2, …, 24. A check that scans only single-number brackets *appears* to find disorder, because the Introduction cites [7, 8] and [11, 12] as pairs and Related work later cites [7], [8], [11], [12] singly |
| every list entry cited ≥ 1 | PASS (build reports the unused set and prints only cited entries) |
| every in-text bracket resolves | PASS (an unknown key would be left as `[key]`; none in the exported text) |
| bracket style | [n]; consecutive runs as [9–11]; pairs as [6, 7] |
| self-citation / anonymity | PASS — no self-citations; author and affiliation lines withheld; corresponding-author footnote blanked; docProps creator/lastModifiedBy blanked; PDF has no Author field |

## Pass 3 — internal cross-references

| pointer | status |
|---|---|
| Table 1 (cited in §3.1 and §4.1), Fig. 1 (§4.2), Table 2 (§4.3) — consecutive, each cited before or at placement; table captions above, figure caption below | PASS |
| No equations, appendix or section-number pointers | N/A |
| Numbers in prose vs result files | PASS — an automated check matches all 28 'value [CI]' triples in the manuscript verbatim against every CSV under `results/` (`python src/check_manuscript_numbers.py`, exit 0); abstract values are correct roundings of the table values |
| Sample counts (1112/539/573/17; 1035/505/530; 973/965/26/939/357/582/7; 130/50/49/43/261/171/90; 40/122; 871/897) | PASS (checked against the QC tables and feature files) |
| Permutation/FDR claims (2 of 28 lobe pairs; 1 of 60 harmonization comparisons; 40 demographic-adjustment comparisons with p_FDR = 0.051 for ABIDE→UCLA-CNP; p = 0.71 cross-dataset overlap) | PASS (results/e4/*_lobe_pairs_permutation.csv, results/e2/e3_deltas.csv, results/e4/cross_dataset_weight_similarity.csv) |

**Verdict: READY** (0 critical, 0 open fixes).
