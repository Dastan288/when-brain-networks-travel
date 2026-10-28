# E2/E3 — cross-dataset transfer matrix (aal90)

Bootstrap 1000 resamples of held-out subjects; 95 % percentile CI. Diagonal = leave-one-site-out (single-site views: stratified 10-fold, labelled). Off-diagonal = train on all of source, test on all of target.

## lr — none (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.649 [0.620, 0.677] | 0.529 [0.500, 0.554] | 0.589 [0.532, 0.646] | NA |
| adhd200 | 0.514 [0.498, 0.530] | 0.459 [0.430, 0.492] | 0.474 [0.417, 0.533] | 0.529 [0.443, 0.621] |
| ucla | 0.514 [0.491, 0.537] | 0.502 [0.468, 0.535] | 0.525 [0.469, 0.582] | NA |
| ucla-adhd | NA | 0.523 [0.497, 0.548] | NA | 0.416 [0.334, 0.497] |

## lr — combat_ref (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.648 [0.619, 0.678] | 0.539 [0.510, 0.565] | 0.592 [0.539, 0.648] | NA |
| adhd200 | 0.525 [0.496, 0.554] | 0.466 [0.437, 0.495] | 0.501 [0.449, 0.558] | 0.531 [0.450, 0.607] |
| ucla | 0.518 [0.496, 0.542] | 0.506 [0.471, 0.538] | NA | NA |
| ucla-adhd | NA | 0.524 [0.498, 0.549] | NA | NA |

## lr — combat_new (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.647 [0.620, 0.675] | 0.543 [0.511, 0.577] | 0.593 [0.535, 0.650] | NA |
| adhd200 | 0.517 [0.488, 0.547] | 0.497 [0.465, 0.529] | 0.467 [0.433, 0.499] | 0.476 [0.427, 0.530] |
| ucla | 0.532 [0.501, 0.560] | 0.498 [0.468, 0.528] | NA | NA |
| ucla-adhd | NA | 0.500 [0.476, 0.524] | NA | NA |

## svm — none (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.634 [0.605, 0.662] | 0.534 [0.506, 0.561] | 0.587 [0.530, 0.645] | NA |
| adhd200 | 0.512 [0.496, 0.528] | 0.469 [0.439, 0.499] | 0.462 [0.406, 0.522] | 0.512 [0.424, 0.602] |
| ucla | 0.513 [0.490, 0.537] | 0.504 [0.470, 0.537] | 0.513 [0.457, 0.567] | NA |
| ucla-adhd | NA | 0.520 [0.495, 0.544] | NA | 0.387 [0.309, 0.462] |

## svm — combat_ref (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.637 [0.609, 0.665] | 0.541 [0.512, 0.568] | 0.589 [0.537, 0.644] | NA |
| adhd200 | 0.537 [0.508, 0.566] | 0.466 [0.439, 0.493] | 0.509 [0.453, 0.565] | 0.526 [0.445, 0.598] |
| ucla | 0.512 [0.489, 0.535] | 0.506 [0.472, 0.537] | NA | NA |
| ucla-adhd | NA | 0.513 [0.487, 0.536] | NA | NA |

## svm — combat_new (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.643 [0.614, 0.672] | 0.534 [0.501, 0.567] | 0.585 [0.528, 0.641] | NA |
| adhd200 | 0.521 [0.492, 0.550] | 0.487 [0.457, 0.517] | 0.471 [0.435, 0.503] | 0.476 [0.427, 0.530] |
| ucla | 0.529 [0.499, 0.558] | 0.509 [0.477, 0.540] | NA | NA |
| ucla-adhd | NA | 0.502 [0.478, 0.525] | NA | NA |

## rf — none (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.649 [0.619, 0.677] | 0.512 [0.481, 0.544] | 0.534 [0.471, 0.595] | NA |
| adhd200 | 0.500 [0.500, 0.500] | 0.474 [0.463, 0.483] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] |
| ucla | 0.509 [0.495, 0.524] | 0.505 [0.488, 0.523] | 0.398 [0.348, 0.454] | NA |
| ucla-adhd | NA | 0.500 [0.500, 0.500] | NA | 0.411 [0.342, 0.485] |

## rf — combat_ref (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.619 [0.590, 0.648] | 0.484 [0.451, 0.518] | 0.565 [0.505, 0.624] | NA |
| adhd200 | 0.500 [0.500, 0.500] | 0.484 [0.474, 0.494] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] |
| ucla | 0.510 [0.496, 0.524] | 0.484 [0.456, 0.515] | NA | NA |
| ucla-adhd | NA | 0.500 [0.500, 0.500] | NA | NA |

## rf — combat_new (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.631 [0.603, 0.662] | 0.546 [0.512, 0.578] | 0.538 [0.485, 0.595] | NA |
| adhd200 | 0.500 [0.494, 0.506] | 0.487 [0.476, 0.498] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] |
| ucla | 0.536 [0.507, 0.568] | 0.495 [0.464, 0.526] | NA | NA |
| ucla-adhd | NA | 0.500 [0.500, 0.500] | NA | NA |

## agesex_lr — none (balanced accuracy)

| source \ target | abide | adhd200 | ucla | ucla-adhd |
|---|---|---|---|---|
| abide | 0.522 [0.499, 0.545] | 0.631 [0.603, 0.661] | 0.547 [0.490, 0.606] | NA |
| adhd200 | 0.531 [0.500, 0.560] | 0.609 [0.579, 0.639] | 0.500 [0.500, 0.500] | 0.500 [0.500, 0.500] |
| ucla | 0.513 [0.497, 0.529] | 0.500 [0.500, 0.500] | 0.558 [0.499, 0.620] | NA |
| ucla-adhd | NA | 0.500 [0.500, 0.500] | NA | 0.421 [0.341, 0.517] |

## E3 — ComBat minus raw (paired bootstrap, balanced accuracy)

| source    | target    | model   | harmonization   |   delta |   ci_low |   ci_high |
|:----------|:----------|:--------|:----------------|--------:|---------:|----------:|
| abide     | abide     | lr      | combat_new      |  -0.002 |   -0.018 |     0.014 |
| abide     | abide     | lr      | combat_ref      |  -0.001 |   -0.016 |     0.015 |
| abide     | adhd200   | lr      | combat_new      |   0.015 |   -0.016 |     0.045 |
| abide     | adhd200   | lr      | combat_ref      |   0.011 |   -0.005 |     0.024 |
| abide     | ucla      | lr      | combat_new      |   0.004 |   -0.039 |     0.046 |
| abide     | ucla      | lr      | combat_ref      |   0.004 |   -0.023 |     0.031 |
| adhd200   | abide     | lr      | combat_new      |   0.002 |   -0.024 |     0.031 |
| adhd200   | abide     | lr      | combat_ref      |   0.011 |   -0.016 |     0.037 |
| adhd200   | adhd200   | lr      | combat_new      |   0.038 |    0.015 |     0.061 |
| adhd200   | adhd200   | lr      | combat_ref      |   0.007 |   -0.014 |     0.026 |
| adhd200   | ucla      | lr      | combat_new      |  -0.006 |   -0.065 |     0.053 |
| adhd200   | ucla      | lr      | combat_ref      |   0.028 |   -0.028 |     0.078 |
| adhd200   | ucla-adhd | lr      | combat_new      |  -0.053 |   -0.147 |     0.035 |
| adhd200   | ucla-adhd | lr      | combat_ref      |   0.002 |   -0.071 |     0.076 |
| ucla      | abide     | lr      | combat_new      |   0.018 |   -0.013 |     0.046 |
| ucla      | abide     | lr      | combat_ref      |   0.004 |   -0.004 |     0.013 |
| ucla      | adhd200   | lr      | combat_new      |  -0.004 |   -0.027 |     0.019 |
| ucla      | adhd200   | lr      | combat_ref      |   0.004 |   -0.007 |     0.014 |
| ucla-adhd | adhd200   | lr      | combat_new      |  -0.023 |   -0.039 |    -0.006 |
| ucla-adhd | adhd200   | lr      | combat_ref      |   0.002 |   -0.004 |     0.008 |
| abide     | abide     | rf      | combat_new      |  -0.018 |   -0.046 |     0.009 |
| abide     | abide     | rf      | combat_ref      |  -0.03  |   -0.054 |    -0.008 |
| abide     | adhd200   | rf      | combat_new      |   0.033 |   -0.005 |     0.071 |
| abide     | adhd200   | rf      | combat_ref      |  -0.028 |   -0.065 |     0.012 |
| abide     | ucla      | rf      | combat_new      |   0.004 |   -0.048 |     0.063 |
| abide     | ucla      | rf      | combat_ref      |   0.031 |   -0.022 |     0.092 |
| adhd200   | abide     | rf      | combat_new      |   0     |   -0.006 |     0.006 |
| adhd200   | abide     | rf      | combat_ref      |   0     |    0     |     0     |
| adhd200   | adhd200   | rf      | combat_new      |   0.014 |    0.002 |     0.025 |
| adhd200   | adhd200   | rf      | combat_ref      |   0.01  |    0.002 |     0.018 |
| adhd200   | ucla      | rf      | combat_new      |   0     |    0     |     0     |
| adhd200   | ucla      | rf      | combat_ref      |   0     |    0     |     0     |
| adhd200   | ucla-adhd | rf      | combat_new      |   0     |    0     |     0     |
| adhd200   | ucla-adhd | rf      | combat_ref      |   0     |    0     |     0     |
| ucla      | abide     | rf      | combat_new      |   0.027 |   -0.006 |     0.061 |
| ucla      | abide     | rf      | combat_ref      |   0.001 |   -0.011 |     0.013 |
| ucla      | adhd200   | rf      | combat_new      |  -0.01  |   -0.043 |     0.019 |
| ucla      | adhd200   | rf      | combat_ref      |  -0.02  |   -0.048 |     0.008 |
| ucla-adhd | adhd200   | rf      | combat_new      |   0     |    0     |     0     |
| ucla-adhd | adhd200   | rf      | combat_ref      |   0     |    0     |     0     |
| abide     | abide     | svm     | combat_new      |   0.01  |   -0.008 |     0.029 |
| abide     | abide     | svm     | combat_ref      |   0.003 |   -0.012 |     0.019 |
| abide     | adhd200   | svm     | combat_new      |  -0     |   -0.029 |     0.029 |
| abide     | adhd200   | svm     | combat_ref      |   0.007 |   -0.009 |     0.021 |
| abide     | ucla      | svm     | combat_new      |  -0.002 |   -0.042 |     0.038 |
| abide     | ucla      | svm     | combat_ref      |   0.002 |   -0.03  |     0.033 |
| adhd200   | abide     | svm     | combat_new      |   0.009 |   -0.018 |     0.036 |
| adhd200   | abide     | svm     | combat_ref      |   0.024 |   -0.003 |     0.05  |
| adhd200   | adhd200   | svm     | combat_new      |   0.018 |   -0.006 |     0.044 |
| adhd200   | adhd200   | svm     | combat_ref      |  -0.003 |   -0.028 |     0.022 |
| adhd200   | ucla      | svm     | combat_new      |   0.009 |   -0.049 |     0.069 |
| adhd200   | ucla      | svm     | combat_ref      |   0.047 |   -0.012 |     0.103 |
| adhd200   | ucla-adhd | svm     | combat_new      |  -0.036 |   -0.128 |     0.054 |
| adhd200   | ucla-adhd | svm     | combat_ref      |   0.014 |   -0.058 |     0.09  |
| ucla      | abide     | svm     | combat_new      |   0.016 |   -0.014 |     0.045 |
| ucla      | abide     | svm     | combat_ref      |  -0.002 |   -0.012 |     0.008 |
| ucla      | adhd200   | svm     | combat_new      |   0.005 |   -0.014 |     0.025 |
| ucla      | adhd200   | svm     | combat_ref      |   0.002 |   -0.011 |     0.015 |
| ucla-adhd | adhd200   | svm     | combat_new      |  -0.018 |   -0.035 |    -0.001 |
| ucla-adhd | adhd200   | svm     | combat_ref      |  -0.007 |   -0.016 |     0.001 |

## Few-site views: stratified 10-fold diagonal (site leakage; for contrast only)

| source    | model     |   n_target |   balanced_accuracy |   balanced_accuracy_ci_low |   balanced_accuracy_ci_high |   auc |
|:----------|:----------|-----------:|--------------------:|---------------------------:|----------------------------:|------:|
| ucla      | lr        |        261 |               0.578 |                      0.524 |                       0.634 | 0.601 |
| ucla      | agesex_lr |        261 |               0.564 |                      0.506 |                       0.625 | 0.579 |
| ucla-adhd | lr        |        162 |               0.464 |                      0.41  |                       0.524 | 0.477 |
| ucla-adhd | agesex_lr |        162 |               0.301 |                      0.23  |                       0.389 | 0.267 |
| ucla      | svm       |        261 |               0.575 |                      0.514 |                       0.632 | 0.593 |
| ucla-adhd | svm       |        162 |               0.452 |                      0.396 |                       0.514 | 0.476 |
| ucla      | rf        |        261 |               0.554 |                      0.497 |                       0.617 | 0.589 |
| ucla-adhd | rf        |        162 |               0.5   |                      0.5   |                       0.5   | 0.52  |

NA cells: 1 (ComBat needs >= 2 training sites; control model has no harmonization).

