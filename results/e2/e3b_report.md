# E3b — connectome vs demographics control; pooled vs per-site diagonal

## Connectome model minus age+sex control (paired bootstrap on identical held-out subjects)

| source    | target    | harmonization   | model   | metric            |   connectome |   agesex |   delta |   ci_low |   ci_high |   p_boot |   p_fdr |
|:----------|:----------|:----------------|:--------|:------------------|-------------:|---------:|--------:|---------:|----------:|---------:|--------:|
| abide     | abide     | none            | lr      | balanced_accuracy |        0.649 |    0.522 |   0.127 |    0.093 |     0.162 |    0     |   0     |
| abide     | abide     | none            | lr      | auc               |        0.698 |    0.5   |   0.199 |    0.152 |     0.246 |    0     |   0     |
| abide     | abide     | none            | svm     | balanced_accuracy |        0.634 |    0.522 |   0.112 |    0.077 |     0.146 |    0     |   0     |
| abide     | abide     | none            | svm     | auc               |        0.685 |    0.5   |   0.186 |    0.139 |     0.232 |    0     |   0     |
| abide     | abide     | none            | rf      | balanced_accuracy |        0.649 |    0.522 |   0.127 |    0.088 |     0.165 |    0     |   0     |
| abide     | abide     | none            | rf      | auc               |        0.697 |    0.5   |   0.198 |    0.149 |     0.247 |    0     |   0     |
| abide     | adhd200   | none            | lr      | balanced_accuracy |        0.529 |    0.631 |  -0.102 |   -0.141 |    -0.062 |    0     |   0     |
| abide     | adhd200   | none            | lr      | auc               |        0.566 |    0.612 |  -0.046 |   -0.103 |     0.012 |    0.122 |   0.256 |
| abide     | adhd200   | none            | svm     | balanced_accuracy |        0.534 |    0.631 |  -0.097 |   -0.137 |    -0.055 |    0     |   0     |
| abide     | adhd200   | none            | svm     | auc               |        0.56  |    0.612 |  -0.051 |   -0.107 |     0.008 |    0.078 |   0.182 |
| abide     | adhd200   | none            | rf      | balanced_accuracy |        0.512 |    0.631 |  -0.119 |   -0.161 |    -0.074 |    0     |   0     |
| abide     | adhd200   | none            | rf      | auc               |        0.521 |    0.612 |  -0.09  |   -0.144 |    -0.035 |    0.002 |   0.006 |
| abide     | ucla      | none            | lr      | balanced_accuracy |        0.589 |    0.547 |   0.042 |   -0.034 |     0.12  |    0.282 |   0.576 |
| abide     | ucla      | none            | lr      | auc               |        0.627 |    0.594 |   0.033 |   -0.056 |     0.119 |    0.468 |   0.645 |
| abide     | ucla      | none            | svm     | balanced_accuracy |        0.587 |    0.547 |   0.041 |   -0.036 |     0.121 |    0.282 |   0.576 |
| abide     | ucla      | none            | svm     | auc               |        0.623 |    0.594 |   0.029 |   -0.061 |     0.116 |    0.504 |   0.662 |
| abide     | ucla      | none            | rf      | balanced_accuracy |        0.534 |    0.547 |  -0.012 |   -0.104 |     0.073 |    0.776 |   0.962 |
| abide     | ucla      | none            | rf      | auc               |        0.562 |    0.594 |  -0.032 |   -0.129 |     0.066 |    0.542 |   0.67  |
| adhd200   | abide     | none            | lr      | balanced_accuracy |        0.514 |    0.531 |  -0.016 |   -0.048 |     0.017 |    0.35  |   0.668 |
| adhd200   | abide     | none            | lr      | auc               |        0.558 |    0.533 |   0.025 |   -0.018 |     0.067 |    0.246 |   0.449 |
| adhd200   | abide     | none            | svm     | balanced_accuracy |        0.512 |    0.531 |  -0.018 |   -0.05  |     0.016 |    0.288 |   0.576 |
| adhd200   | abide     | none            | svm     | auc               |        0.556 |    0.533 |   0.023 |   -0.021 |     0.066 |    0.284 |   0.473 |
| adhd200   | abide     | none            | rf      | balanced_accuracy |        0.5   |    0.531 |  -0.031 |   -0.06  |     0     |    0.052 |   0.156 |
| adhd200   | abide     | none            | rf      | auc               |        0.524 |    0.533 |  -0.009 |   -0.055 |     0.035 |    0.718 |   0.809 |
| adhd200   | adhd200   | none            | lr      | balanced_accuracy |        0.459 |    0.609 |  -0.149 |   -0.19  |    -0.107 |    0     |   0     |
| adhd200   | adhd200   | none            | lr      | auc               |        0.468 |    0.621 |  -0.153 |   -0.202 |    -0.102 |    0     |   0     |
| adhd200   | adhd200   | none            | svm     | balanced_accuracy |        0.469 |    0.609 |  -0.14  |   -0.182 |    -0.098 |    0     |   0     |
| adhd200   | adhd200   | none            | svm     | auc               |        0.471 |    0.621 |  -0.15  |   -0.198 |    -0.099 |    0     |   0     |
| adhd200   | adhd200   | none            | rf      | balanced_accuracy |        0.474 |    0.609 |  -0.135 |   -0.166 |    -0.104 |    0     |   0     |
| adhd200   | adhd200   | none            | rf      | auc               |        0.4   |    0.621 |  -0.221 |   -0.266 |    -0.172 |    0     |   0     |
| adhd200   | ucla      | none            | lr      | balanced_accuracy |        0.474 |    0.5   |  -0.026 |   -0.083 |     0.033 |    0.382 |   0.676 |
| adhd200   | ucla      | none            | lr      | auc               |        0.448 |    0.472 |  -0.024 |   -0.122 |     0.078 |    0.664 |   0.775 |
| adhd200   | ucla      | none            | svm     | balanced_accuracy |        0.462 |    0.5   |  -0.038 |   -0.094 |     0.022 |    0.23  |   0.568 |
| adhd200   | ucla      | none            | svm     | auc               |        0.44  |    0.472 |  -0.032 |   -0.128 |     0.067 |    0.536 |   0.67  |
| adhd200   | ucla      | none            | rf      | balanced_accuracy |        0.5   |    0.5   |   0     |    0     |     0     |    1     |   1     |
| adhd200   | ucla      | none            | rf      | auc               |        0.512 |    0.472 |   0.041 |   -0.054 |     0.138 |    0.396 |   0.574 |
| adhd200   | ucla-adhd | none            | lr      | balanced_accuracy |        0.529 |    0.5   |   0.029 |   -0.057 |     0.121 |    0.52  |   0.84  |
| adhd200   | ucla-adhd | none            | lr      | auc               |        0.502 |    0.486 |   0.015 |   -0.131 |     0.171 |    0.808 |   0.867 |
| adhd200   | ucla-adhd | none            | svm     | balanced_accuracy |        0.512 |    0.5   |   0.012 |   -0.076 |     0.102 |    0.798 |   0.962 |
| adhd200   | ucla-adhd | none            | svm     | auc               |        0.49  |    0.486 |   0.003 |   -0.143 |     0.159 |    0.94  |   0.94  |
| adhd200   | ucla-adhd | none            | rf      | balanced_accuracy |        0.5   |    0.5   |   0     |    0     |     0     |    1     |   1     |
| adhd200   | ucla-adhd | none            | rf      | auc               |        0.491 |    0.486 |   0.005 |   -0.129 |     0.141 |    0.91  |   0.932 |
| ucla      | abide     | none            | lr      | balanced_accuracy |        0.514 |    0.513 |   0.002 |   -0.026 |     0.03  |    0.908 |   1     |
| ucla      | abide     | none            | lr      | auc               |        0.546 |    0.519 |   0.027 |   -0.018 |     0.072 |    0.258 |   0.452 |
| ucla      | abide     | none            | svm     | balanced_accuracy |        0.513 |    0.513 |   0.001 |   -0.028 |     0.028 |    0.96  |   1     |
| ucla      | abide     | none            | svm     | auc               |        0.544 |    0.519 |   0.024 |   -0.021 |     0.07  |    0.304 |   0.473 |
| ucla      | abide     | none            | rf      | balanced_accuracy |        0.509 |    0.513 |  -0.003 |   -0.025 |     0.018 |    0.746 |   0.962 |
| ucla      | abide     | none            | rf      | auc               |        0.537 |    0.519 |   0.017 |   -0.031 |     0.065 |    0.476 |   0.645 |
| ucla      | adhd200   | none            | lr      | balanced_accuracy |        0.502 |    0.5   |   0.002 |   -0.032 |     0.035 |    0.93  |   1     |
| ucla      | adhd200   | none            | lr      | auc               |        0.51  |    0.596 |  -0.085 |   -0.138 |    -0.03  |    0.002 |   0.006 |
| ucla      | adhd200   | none            | svm     | balanced_accuracy |        0.504 |    0.5   |   0.004 |   -0.03  |     0.037 |    0.788 |   0.962 |
| ucla      | adhd200   | none            | svm     | auc               |        0.511 |    0.596 |  -0.085 |   -0.138 |    -0.031 |    0.002 |   0.006 |
| ucla      | adhd200   | none            | rf      | balanced_accuracy |        0.505 |    0.5   |   0.005 |   -0.012 |     0.023 |    0.604 |   0.94  |
| ucla      | adhd200   | none            | rf      | auc               |        0.469 |    0.596 |  -0.126 |   -0.183 |    -0.072 |    0     |   0     |
| ucla      | ucla      | none            | lr      | balanced_accuracy |        0.525 |    0.558 |  -0.033 |   -0.108 |     0.041 |    0.386 |   0.676 |
| ucla      | ucla      | none            | lr      | auc               |        0.508 |    0.569 |  -0.061 |   -0.147 |     0.023 |    0.148 |   0.283 |
| ucla      | ucla      | none            | svm     | balanced_accuracy |        0.513 |    0.558 |  -0.045 |   -0.12  |     0.03  |    0.244 |   0.569 |
| ucla      | ucla      | none            | svm     | auc               |        0.499 |    0.569 |  -0.07  |   -0.154 |     0.016 |    0.104 |   0.23  |
| ucla      | ucla      | none            | rf      | balanced_accuracy |        0.398 |    0.558 |  -0.16  |   -0.232 |    -0.09  |    0     |   0     |
| ucla      | ucla      | none            | rf      | auc               |        0.354 |    0.569 |  -0.215 |   -0.305 |    -0.128 |    0     |   0     |
| ucla      | ucla      | none@random10   | lr      | balanced_accuracy |        0.578 |    0.564 |   0.014 |   -0.065 |     0.088 |    0.692 |   0.962 |
| ucla      | ucla      | none@random10   | lr      | auc               |        0.601 |    0.579 |   0.022 |   -0.061 |     0.106 |    0.62  |   0.744 |
| ucla      | ucla      | none@random10   | svm     | balanced_accuracy |        0.575 |    0.564 |   0.01  |   -0.074 |     0.086 |    0.796 |   0.962 |
| ucla      | ucla      | none@random10   | svm     | auc               |        0.593 |    0.579 |   0.014 |   -0.068 |     0.097 |    0.732 |   0.809 |
| ucla      | ucla      | none@random10   | rf      | balanced_accuracy |        0.554 |    0.564 |  -0.011 |   -0.09  |     0.065 |    0.784 |   0.962 |
| ucla      | ucla      | none@random10   | rf      | auc               |        0.589 |    0.579 |   0.009 |   -0.078 |     0.096 |    0.826 |   0.867 |
| ucla-adhd | adhd200   | none            | lr      | balanced_accuracy |        0.523 |    0.5   |   0.023 |   -0.003 |     0.048 |    0.096 |   0.269 |
| ucla-adhd | adhd200   | none            | lr      | auc               |        0.539 |    0.36  |   0.179 |    0.131 |     0.227 |    0     |   0     |
| ucla-adhd | adhd200   | none            | svm     | balanced_accuracy |        0.52  |    0.5   |   0.02  |   -0.005 |     0.044 |    0.134 |   0.352 |
| ucla-adhd | adhd200   | none            | svm     | auc               |        0.544 |    0.36  |   0.184 |    0.136 |     0.233 |    0     |   0     |
| ucla-adhd | adhd200   | none            | rf      | balanced_accuracy |        0.5   |    0.5   |   0     |    0     |     0     |    1     |   1     |
| ucla-adhd | adhd200   | none            | rf      | auc               |        0.46  |    0.36  |   0.1   |    0.047 |     0.152 |    0     |   0     |
| ucla-adhd | ucla-adhd | none            | lr      | balanced_accuracy |        0.416 |    0.421 |  -0.005 |   -0.119 |     0.1   |    0.862 |   1     |
| ucla-adhd | ucla-adhd | none            | lr      | auc               |        0.348 |    0.407 |  -0.059 |   -0.204 |     0.07  |    0.322 |   0.483 |
| ucla-adhd | ucla-adhd | none            | svm     | balanced_accuracy |        0.387 |    0.421 |  -0.034 |   -0.15  |     0.07  |    0.492 |   0.827 |
| ucla-adhd | ucla-adhd | none            | svm     | auc               |        0.345 |    0.407 |  -0.062 |   -0.206 |     0.069 |    0.296 |   0.473 |
| ucla-adhd | ucla-adhd | none            | rf      | balanced_accuracy |        0.411 |    0.421 |  -0.01  |   -0.13  |     0.102 |    0.802 |   0.962 |
| ucla-adhd | ucla-adhd | none            | rf      | auc               |        0.302 |    0.407 |  -0.105 |   -0.251 |     0.03  |    0.132 |   0.264 |
| ucla-adhd | ucla-adhd | none@random10   | lr      | balanced_accuracy |        0.464 |    0.301 |   0.163 |    0.056 |     0.255 |    0.006 |   0.019 |
| ucla-adhd | ucla-adhd | none@random10   | lr      | auc               |        0.477 |    0.267 |   0.21  |    0.067 |     0.337 |    0.006 |   0.016 |
| ucla-adhd | ucla-adhd | none@random10   | svm     | balanced_accuracy |        0.452 |    0.301 |   0.151 |    0.047 |     0.247 |    0.006 |   0.019 |
| ucla-adhd | ucla-adhd | none@random10   | svm     | auc               |        0.476 |    0.267 |   0.208 |    0.067 |     0.336 |    0.008 |   0.02  |
| ucla-adhd | ucla-adhd | none@random10   | rf      | balanced_accuracy |        0.5   |    0.301 |   0.199 |    0.111 |     0.27  |    0     |   0     |
| ucla-adhd | ucla-adhd | none@random10   | rf      | auc               |        0.52  |    0.267 |   0.252 |    0.097 |     0.391 |    0     |   0     |

## Leave-one-site-out diagonal: pooled out-of-fold vs per-site averages

| view      | harmonization   | model     |   n_sites |   n_sites_two_class |   pooled_bacc |   persite_mean_bacc |   persite_median_bacc |   persite_n_weighted_bacc |   pooled_auc |   persite_mean_auc | sites_single_class   |
|:----------|:----------------|:----------|----------:|--------------------:|--------------:|--------------------:|----------------------:|--------------------------:|-------------:|-------------------:|:---------------------|
| abide     | combat_new      | lr        |        17 |                  17 |         0.647 |               0.642 |                 0.657 |                     0.649 |        0.705 |              0.688 |                      |
| abide     | combat_new      | rf        |        17 |                  17 |         0.631 |               0.623 |                 0.658 |                     0.637 |        0.697 |              0.682 |                      |
| abide     | combat_new      | svm       |        17 |                  17 |         0.643 |               0.638 |                 0.655 |                     0.645 |        0.691 |              0.677 |                      |
| abide     | combat_ref      | lr        |        17 |                  17 |         0.648 |               0.636 |                 0.653 |                     0.649 |        0.702 |              0.69  |                      |
| abide     | combat_ref      | rf        |        17 |                  17 |         0.619 |               0.615 |                 0.638 |                     0.627 |        0.679 |              0.684 |                      |
| abide     | combat_ref      | svm       |        17 |                  17 |         0.637 |               0.631 |                 0.636 |                     0.635 |        0.69  |              0.676 |                      |
| abide     | none            | agesex_lr |        17 |                  17 |         0.522 |               0.512 |                 0.505 |                     0.521 |        0.5   |              0.504 |                      |
| abide     | none            | lr        |        17 |                  17 |         0.649 |               0.642 |                 0.655 |                     0.649 |        0.698 |              0.687 |                      |
| abide     | none            | rf        |        17 |                  17 |         0.649 |               0.647 |                 0.658 |                     0.657 |        0.697 |              0.705 |                      |
| abide     | none            | svm       |        17 |                  17 |         0.634 |               0.627 |                 0.642 |                     0.632 |        0.685 |              0.671 |                      |
| adhd200   | combat_new      | lr        |         7 |                   6 |         0.497 |               0.502 |                 0.517 |                     0.507 |        0.493 |              0.498 | WashU                |
| adhd200   | combat_new      | rf        |         7 |                   6 |         0.487 |               0.493 |                 0.5   |                     0.498 |        0.478 |              0.588 | WashU                |
| adhd200   | combat_new      | svm       |         7 |                   6 |         0.487 |               0.492 |                 0.501 |                     0.498 |        0.488 |              0.488 | WashU                |
| adhd200   | combat_ref      | lr        |         7 |                   6 |         0.466 |               0.492 |                 0.504 |                     0.497 |        0.468 |              0.498 | WashU                |
| adhd200   | combat_ref      | rf        |         7 |                   6 |         0.484 |               0.491 |                 0.502 |                     0.497 |        0.437 |              0.57  | WashU                |
| adhd200   | combat_ref      | svm       |         7 |                   6 |         0.466 |               0.492 |                 0.497 |                     0.498 |        0.464 |              0.488 | WashU                |
| adhd200   | none            | agesex_lr |         7 |                   6 |         0.609 |               0.602 |                 0.618 |                     0.615 |        0.621 |              0.648 | WashU                |
| adhd200   | none            | lr        |         7 |                   6 |         0.459 |               0.503 |                 0.508 |                     0.501 |        0.468 |              0.514 | WashU                |
| adhd200   | none            | rf        |         7 |                   6 |         0.474 |               0.485 |                 0.5   |                     0.491 |        0.4   |              0.512 | WashU                |
| adhd200   | none            | svm       |         7 |                   6 |         0.469 |               0.508 |                 0.502 |                     0.506 |        0.471 |              0.513 | WashU                |
| ucla      | none            | agesex_lr |         2 |                   2 |         0.558 |               0.567 |                 0.567 |                     0.564 |        0.569 |              0.574 |                      |
| ucla      | none            | lr        |         2 |                   2 |         0.525 |               0.589 |                 0.589 |                     0.581 |        0.508 |              0.584 |                      |
| ucla      | none            | rf        |         2 |                   2 |         0.398 |               0.524 |                 0.524 |                     0.517 |        0.354 |              0.509 |                      |
| ucla      | none            | svm       |         2 |                   2 |         0.513 |               0.589 |                 0.589 |                     0.579 |        0.499 |              0.581 |                      |
| ucla-adhd | none            | agesex_lr |         2 |                   2 |         0.421 |               0.428 |                 0.428 |                     0.429 |        0.407 |              0.43  |                      |
| ucla-adhd | none            | lr        |         2 |                   2 |         0.416 |               0.471 |                 0.471 |                     0.478 |        0.348 |              0.437 |                      |
| ucla-adhd | none            | rf        |         2 |                   2 |         0.411 |               0.48  |                 0.48  |                     0.47  |        0.302 |              0.391 |                      |
| ucla-adhd | none            | svm       |         2 |                   2 |         0.387 |               0.438 |                 0.438 |                     0.442 |        0.345 |              0.432 |                      |
