# data/

Download scripts only. Raw derivatives go to `data/raw/` (git-ignored, ~2 GB for
ABIDE ROI series) and are documented by a checksum manifest in `results/qc/`.

| Script | Dataset | Status |
|---|---|---|
| `pack_abide_series.py` | packs the downloaded ABIDE ROI series into `data/cache/` | ready |
| `download_abide.py` | ABIDE I Preprocessed — C-PAC `filt_noglobal` (primary) and `filt_global`, `rois_aal` + `rois_cc200` (nilearn `fetch_abide_pcp`) | ready |
| `download_adhd200.py` | ADHD-200 Preprocessed (Athena) AAL time courses + phenotypes, NITRC (files downloaded manually after a free NITRC login; see the top-level README) | ready |
| `download_ucla.py` | UCLA-CNP ds000030 R1.0.5 fMRIPrep derivatives (OpenNeuro S3) → AAL-116 time series | ready |

Never run fMRIPrep / C-PAC here — only released derivatives are used.
