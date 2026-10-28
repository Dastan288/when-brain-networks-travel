# When Brain Networks Travel

Code, analysis scripts, environment specification and result tables for

> D. Kapizov, P. Kumar, A. Mukhtarov. **When Brain Networks Travel: Cross-Dataset Generalization of
> Connectome-Based Classifiers across ABIDE, ADHD-200 and UCLA-CNP.** AIDA 2026 – International Conference
> on AI and Data Analytics for Digital Transformation. *Procedia Computer Science* (2026, in press).

The study measures how far case-control information in resting-state connectomes transfers between
three open repositories (ABIDE I, ADHD-200, UCLA-CNP), using leave-one-site-out validation, an
age-and-sex baseline, demographic residualization, site-level uncertainty and leakage-aware ComBat
harmonization (reference-only and new-batch modes). It is an evaluation study, not a new classifier.

## Quick start

```bash
git clone https://github.com/Dastan288/when-brain-networks-travel.git
cd when-brain-networks-travel
bash run_all.sh            # creates .venv (Python >= 3.11), installs pinned deps, downloads, runs everything
bash run_all.sh --data-only   # downloads + QC tables only
```

* Python ≥ 3.11; exact package versions are pinned in `requirements.txt`.
* All random seeds come from `config/config.yaml` (`seed: 42`); paths, atlas choices and exclusion
  thresholds are also defined there.
* Runtime: about 1–2 h of downloads (≈ 2.6 GB of ROI time series; UCLA-CNP extraction temporarily
  needs ≈ 26 GB for fMRIPrep NIfTI files, deleted after extraction) and a few hours of CPU for all experiments.
* Every step is idempotent / resumable (`--resume`).

## Data (not redistributed)

Only released, already-preprocessed derivatives are used; no raw MRI is reprocessed. The data are
**not** included in this repository; the download scripts fetch them from the original providers, whose
terms of use apply. Please cite the data descriptors below if you use the data.

| Dataset | What is used | How it is obtained | Reference |
|---|---|---|---|
| ABIDE I Preprocessed | C-PAC `filt_noglobal` (primary) and `filt_global` ROI series, AAL + CC200 | automatic, `data/download_abide.py` (nilearn `fetch_abide_pcp`) | Di Martino et al. 2014; Craddock et al. 2013 |
| ADHD-200 Preprocessed (Athena) | `sfnwmrda*` AAL time courses, first rest run of session 1; phenotypes | **manual**: NITRC requires a free login. Download file IDs 3419, 3595, 3916, 3917 (`https://www.nitrc.org/frs/downloadlink.php/<ID>`) and `adhd200_preprocessed_phenotypics.tsv` (ID 9024) into `data/raw/ADHD200/`, then run `python data/download_adhd200.py --skip-download` | ADHD-200 Consortium 2012; Bellec et al. 2017 |
| UCLA-CNP (OpenNeuro ds000030 R1.0.5) | fMRIPrep resting-state derivatives → AAL-116 time series | automatic, `data/download_ucla.py` | Poldrack et al. 2016; Gorgolewski et al. 2017 |

Per-participant tables (QC tables with age/sex/diagnosis and out-of-fold predictions per participant)
are regenerated locally by `run_all.sh` and are deliberately not committed (see `.gitignore`).

### Cohorts and exclusions

* **ABIDE I**: 1035 participants with time series; 2 excluded (> 20 % zero-variance regions;
  `results/qc/abide_exclusions.csv`) → **1033 (504 ASD / 529 TD), 17 sites** (UM_1/UM_2, UCLA_1/UCLA_2,
  LEUVEN_1/LEUVEN_2 merged per institution; `config/config.yaml: abide.site_merge`).
* **ADHD-200**: 973 participants from 8 sites in the repository; 965 with time series; the 26 Brown
  participants (diagnostic labels never released) excluded → **939 (357 ADHD / 582 TDC), 7 analyzed sites**
  (`Site` phenotype code; Peking_1/2/3 = Peking).
* **UCLA-CNP**: 261 participants with a resting-state run; the two scanners (ScannerSerialNumber
  35343, 35426) serve as sites. ADHD subset: 40 ADHD vs 122 controls.
* Sensitivity subsets (rater QC for ABIDE, `QC_Athena` for ADHD-200) are flags, not exclusions.

## Pipeline

| Stage | Script | Output |
|---|---|---|
| Downloads + checksum manifests | `data/download_*.py`, `data/pack_abide_series.py` | `data/cache/`, `results/qc/*_manifest.json` |
| QC tables | `src/qc_abide.py`, `src/qc_dataset.py` | `results/qc/` |
| Connectome features (AAL-90 primary; AAL-116, CC200 robustness): Pearson → Fisher-z → upper triangle (4005 edges) | `src/features.py`, `src/aal.py` | `results/features/` |
| Within-repository leave-one-site-out + labelled random-CV contrast (E1) | `src/run_e1.py`, `src/protocols.py` | `results/e1/` |
| Cross-repository transfer matrix + ComBat reference-only / new-batch (E2/E3) | `src/run_e2.py`, `src/combat.py` | `results/e2/` |
| Connectome vs age-and-sex control, pooled vs per-site diagonals (E3b) | `src/run_e3b_controls.py` | `results/e2/e3b_*` |
| GSR-matched control (ABIDE `filt_global` ↔ ADHD-200) | `src/run_e2.py --out results/e2_gsr` | `results/e2_gsr/` |
| Demographic adjustment: `agesex`, `conn+agesex`, `conn_resid` (E5) | `src/run_e5_demographics.py` | `results/e5/` |
| Repeated site-mixed 10-fold CV (20 repeats) and site-level uncertainty (E6) | `src/run_e6_resampling.py` | `results/e6/` |
| Model interpretation: weight stability, top-100 overlap, permutation nulls (E4) | `src/run_e4.py` | `results/e4/` |
| Figures | `src/figures.py` | `results/figures/` |
| Manuscript build (tables generated from the CSVs) + guards | `paper/build_docx.py`, `src/check_manuscript_numbers.py`, `paper/validate_template.py` | — |

Key implementation points:

* **Leave-one-site-out** (`src/protocols.py: leave_one_site_out`): every preprocessing step that has
  parameters (standardization; ComBat; edge residualization in the `conn_resid` analysis) is fitted on
  the training sites only.
* **Cross-repository transfer**: a model fitted on 100 % of the source repository is applied unchanged
  to 100 % of the target repository; nothing about the target is used for fitting.
* **ComBat** (`src/combat.py`, reproduces neuroCombat to within 1e-7): the reference model is always
  fitted on training sites. `reference_only` uses no statistics from held-out data; `transform_new_batch`
  estimates the held-out batch's location/scale from its unlabeled features (transductive, cohort-level).
  ComBat is never fitted on pooled training + test data.
* **Models** (`src/models.py`): L2 logistic regression and linear SVM (C = 1, class-weighted), random
  forest (500 trees), age+sex logistic regression; hyperparameters fixed a priori.
* **Uncertainty** (`src/evaluate.py`): 1000 subject-level bootstrap resamples for 95 % CIs; paired
  bootstrap differences on identical held-out participants; Benjamini–Hochberg FDR within each
  experiment and metric (`bh_fdr`); site-level cluster bootstrap and site-macro averages (`run_e6_resampling.py`).

## Where each number in the paper comes from

| Paper element | Source file(s) |
|---|---|
| Table 1 | `results/e6/e6_site_uncertainty.csv` (site-macro), `results/e2/e2_summary.csv` (pooled OOF), `results/e2/e3b_control_deltas.csv` (Δ vs age + sex); cohort sizes/age/sex from the regenerated QC tables |
| Table 2 | `results/e2/e2_summary.csv`, `results/e2/e3_deltas.csv` (ComBat Δ), `results/e5/e5_summary.csv` (residualized edges) |
| Fig. 1 | `results/e2/transfer_balanced_accuracy_lr_{none,combat_ref,combat_new}.csv` → `results/figures/fig_transfer_matrix_lr.png` |
| Site-mixed CV (mean ± SD over 20 repeats) | `results/e6/e6_repeated_cv.csv` |
| Demographic adjustment and FDR | `results/e5/e5_deltas.csv` |
| GSR-matched control | `results/e2_gsr/e2_summary.csv` |
| Weight stability and overlap | `results/e4/` |

`src/check_manuscript_numbers.py` verifies that every "value [95 % CI]" and "mean ± SD" quoted in
`paper/manuscript.md` exists in these tables.

## Repository layout

```
config/    config.yaml – seed, paths, dataset/atlas choices, QC thresholds, site merges
data/      download scripts (raw data are git-ignored)
src/       QC, features, protocols, models, ComBat, evaluation, experiments E1–E6, figures
results/   aggregate result tables (CSV), reports (MD), figures (PNG/PDF), QC summaries and manifests
paper/     manuscript source (markdown) and the docx build/validation scripts
run_all.sh one-command reproduction
```

The docx build needs the official AIDA 2026 / Procedia template (`run_all.sh` downloads it to
`paper/template.docx`); it is not redistributed here.

## License and citation

Code: MIT (see `LICENSE`). Result tables and figures: CC BY 4.0. The datasets remain under their
providers' terms. Please cite the paper (see `CITATION.cff`) and the data descriptors listed above.
