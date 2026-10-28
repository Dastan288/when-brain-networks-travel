# E1 — within-ADHD200 leave-one-site-out baseline

Seed 42; bootstrap 1000 subject-level resamples; 95% percentile CI. Models with a priori hyperparameters (LR C=1, linear SVM C=1, RF 500 trees), StandardScaler fitted on training sites only.

| variant | sample | protocol | model | n | balanced acc. [95% CI] | AUC [95% CI] | accuracy [95% CI] | per-site bAcc median [IQR] |
|---|---|---|---|---|---|---|---|---|
| aal90 | primary | losite | lr | 939 | 0.459 [0.430, 0.492] | 0.468 [0.431, 0.507] | 0.510 [0.478, 0.540] | 0.508 [0.499–0.514] (min 0.47, max 0.52) |
| aal90 | primary | losite | agesex_lr | 939 | 0.609 [0.579, 0.639] | 0.621 [0.586, 0.656] | 0.583 [0.553, 0.613] | 0.618 [0.600–0.631] (min 0.50, max 0.64) |
| aal90 | primary | random10_INFLATED | lr | 939 | 0.582 [0.550, 0.614] | 0.616 [0.578, 0.651] | 0.603 [0.571, 0.634] | – |
| aal90 | primary | losite | svm | 939 | 0.469 [0.439, 0.499] | 0.471 [0.434, 0.510] | 0.521 [0.487, 0.553] | 0.502 [0.501–0.511] (min 0.50, max 0.53) |
| aal90 | primary | losite | rf | 939 | 0.474 [0.463, 0.483] | 0.400 [0.365, 0.434] | 0.586 [0.555, 0.617] | 0.500 [0.500–0.501] (min 0.40, max 0.50) |
| aal90 | primary | random10_INFLATED | svm | 939 | 0.562 [0.530, 0.594] | 0.609 [0.571, 0.644] | 0.586 [0.555, 0.617] | – |
| aal90 | primary | random10_INFLATED | rf | 939 | 0.529 [0.511, 0.547] | 0.610 [0.572, 0.649] | 0.632 [0.600, 0.661] | – |
| aal90 | qc_pass | losite | lr | 872 | 0.470 [0.438, 0.503] | 0.472 [0.431, 0.512] | 0.526 [0.494, 0.561] | 0.516 [0.496–0.531] (min 0.45, max 0.54) |
| aal90 | qc_pass | losite | svm | 872 | 0.483 [0.449, 0.514] | 0.477 [0.436, 0.517] | 0.539 [0.506, 0.572] | 0.525 [0.515–0.536] (min 0.47, max 0.54) |
| aal90 | qc_pass | losite | rf | 872 | 0.474 [0.464, 0.484] | 0.386 [0.349, 0.424] | 0.594 [0.562, 0.627] | 0.500 [0.500–0.500] (min 0.41, max 0.51) |
| aal90 | qc_pass | losite | agesex_lr | 872 | 0.612 [0.581, 0.644] | 0.625 [0.587, 0.663] | 0.585 [0.553, 0.615] | 0.619 [0.604–0.631] (min 0.50, max 0.65) |
| aal116 | primary | losite | lr | 939 | 0.461 [0.435, 0.490] | 0.462 [0.424, 0.501] | 0.520 [0.489, 0.553] | 0.501 [0.471–0.508] (min 0.45, max 0.54) |
| aal116 | primary | losite | svm | 939 | 0.458 [0.432, 0.487] | 0.463 [0.426, 0.502] | 0.518 [0.487, 0.550] | 0.502 [0.462–0.511] (min 0.44, max 0.52) |
| aal116 | primary | losite | rf | 939 | 0.483 [0.474, 0.492] | 0.371 [0.333, 0.408] | 0.597 [0.567, 0.628] | 0.500 [0.500–0.504] (min 0.43, max 0.51) |
| aal116 | primary | losite | agesex_lr | 939 | 0.609 [0.579, 0.639] | 0.621 [0.586, 0.656] | 0.583 [0.553, 0.613] | 0.618 [0.600–0.631] (min 0.50, max 0.64) |
| aal116 | qc_pass | losite | lr | 872 | 0.479 [0.449, 0.509] | 0.470 [0.432, 0.510] | 0.541 [0.509, 0.576] | 0.508 [0.502–0.516] (min 0.48, max 0.59) |
| aal116 | qc_pass | losite | svm | 872 | 0.477 [0.448, 0.507] | 0.473 [0.436, 0.513] | 0.538 [0.505, 0.572] | 0.504 [0.499–0.535] (min 0.46, max 0.59) |
| aal116 | qc_pass | losite | rf | 872 | 0.482 [0.474, 0.490] | 0.364 [0.327, 0.402] | 0.604 [0.570, 0.635] | 0.500 [0.500–0.500] (min 0.44, max 0.50) |
| aal116 | qc_pass | losite | agesex_lr | 872 | 0.612 [0.581, 0.644] | 0.625 [0.587, 0.663] | 0.585 [0.553, 0.615] | 0.619 [0.604–0.631] (min 0.50, max 0.65) |

Notes:

- `random10_INFLATED` = stratified 10-fold CV pooled across sites (site leakage); shown once for contrast, never as a headline number.
- `agesex_lr` = control model on age + sex only; connectome models must beat it to claim signal beyond demographics.
- `qc_pass` = rater-QC-passed subset (nilearn `quality_checked=True` criterion), sensitivity analysis.

## Per-site balanced accuracy — aal90, primary sample, LR (leave-one-site-out)

| site       |   n |   n_patients |   balanced_accuracy |     auc |   sensitivity |   specificity |
|:-----------|----:|-------------:|--------------------:|--------:|--------------:|--------------:|
| KKI        |  94 |           25 |               0.512 |   0.541 |         0.4   |         0.623 |
| NYU        | 257 |          147 |               0.496 |   0.516 |         0.238 |         0.755 |
| NeuroIMAGE |  73 |           36 |               0.515 |   0.547 |         0.139 |         0.892 |
| OHSU       | 113 |           43 |               0.467 |   0.549 |         0.349 |         0.586 |
| Peking     | 245 |          102 |               0.505 |   0.511 |         0.206 |         0.804 |
| Pittsburgh |  98 |            4 |               0.521 |   0.42  |         0.5   |         0.543 |
| WashU      |  59 |            0 |             nan     | nan     |       nan     |         0.424 |
