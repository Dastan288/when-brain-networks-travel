# E2/E3 — cross-dataset transfer matrix (aal90)

Bootstrap 1000 resamples of held-out subjects; 95 % percentile CI. Diagonal = leave-one-site-out (single-site views: stratified 10-fold, labelled). Off-diagonal = train on all of source, test on all of target.

## lr — none (balanced accuracy)

| source \ target | abide-filt_global | adhd200 |
|---|---|---|
| abide-filt_global | 0.653 [0.625, 0.680] | 0.537 [0.510, 0.565] |
| adhd200 | 0.539 [0.509, 0.569] | 0.459 [0.430, 0.492] |

## lr — combat_ref (balanced accuracy)

| source \ target | abide-filt_global | adhd200 |
|---|---|---|
| abide-filt_global | 0.666 [0.638, 0.693] | 0.545 [0.518, 0.570] |
| adhd200 | 0.524 [0.494, 0.554] | 0.466 [0.437, 0.495] |

## lr — combat_new (balanced accuracy)

| source \ target | abide-filt_global | adhd200 |
|---|---|---|
| abide-filt_global | 0.668 [0.639, 0.696] | 0.548 [0.517, 0.581] |
| adhd200 | 0.529 [0.498, 0.558] | 0.497 [0.465, 0.529] |

## svm — none (balanced accuracy)

| source \ target | abide-filt_global | adhd200 |
|---|---|---|
| abide-filt_global | 0.631 [0.601, 0.659] | 0.547 [0.518, 0.572] |
| adhd200 | 0.535 [0.505, 0.565] | 0.469 [0.439, 0.499] |

## svm — combat_ref (balanced accuracy)

| source \ target | abide-filt_global | adhd200 |
|---|---|---|
| abide-filt_global | 0.651 [0.622, 0.679] | 0.549 [0.519, 0.578] |
| adhd200 | 0.522 [0.492, 0.552] | 0.466 [0.439, 0.493] |

## svm — combat_new (balanced accuracy)

| source \ target | abide-filt_global | adhd200 |
|---|---|---|
| abide-filt_global | 0.656 [0.627, 0.684] | 0.544 [0.512, 0.576] |
| adhd200 | 0.526 [0.495, 0.555] | 0.487 [0.457, 0.517] |

## agesex_lr — none (balanced accuracy)

| source \ target | abide-filt_global | adhd200 |
|---|---|---|
| abide-filt_global | 0.522 [0.499, 0.545] | 0.631 [0.603, 0.661] |
| adhd200 | 0.531 [0.500, 0.560] | 0.609 [0.579, 0.639] |

## E3 — ComBat minus raw (paired bootstrap, balanced accuracy)

| source            | target            | model   | harmonization   |   delta |   ci_low |   ci_high |
|:------------------|:------------------|:--------|:----------------|--------:|---------:|----------:|
| abide-filt_global | abide-filt_global | lr      | combat_new      |   0.014 |   -0.004 |     0.033 |
| abide-filt_global | abide-filt_global | lr      | combat_ref      |   0.013 |   -0.003 |     0.027 |
| abide-filt_global | adhd200           | lr      | combat_new      |   0.012 |   -0.015 |     0.039 |
| abide-filt_global | adhd200           | lr      | combat_ref      |   0.008 |   -0.005 |     0.021 |
| adhd200           | abide-filt_global | lr      | combat_new      |  -0.01  |   -0.031 |     0.01  |
| adhd200           | abide-filt_global | lr      | combat_ref      |  -0.016 |   -0.036 |     0.004 |
| adhd200           | adhd200           | lr      | combat_new      |   0.038 |    0.015 |     0.061 |
| adhd200           | adhd200           | lr      | combat_ref      |   0.007 |   -0.014 |     0.026 |
| abide-filt_global | abide-filt_global | svm     | combat_new      |   0.025 |    0.006 |     0.046 |
| abide-filt_global | abide-filt_global | svm     | combat_ref      |   0.021 |    0.004 |     0.036 |
| abide-filt_global | adhd200           | svm     | combat_new      |  -0.003 |   -0.028 |     0.023 |
| abide-filt_global | adhd200           | svm     | combat_ref      |   0.003 |   -0.013 |     0.019 |
| adhd200           | abide-filt_global | svm     | combat_new      |  -0.01  |   -0.033 |     0.014 |
| adhd200           | abide-filt_global | svm     | combat_ref      |  -0.013 |   -0.036 |     0.009 |
| adhd200           | adhd200           | svm     | combat_new      |   0.018 |   -0.006 |     0.044 |
| adhd200           | adhd200           | svm     | combat_ref      |  -0.003 |   -0.028 |     0.022 |

NA cells: 5 (ComBat needs >= 2 training sites; control model has no harmonization).

