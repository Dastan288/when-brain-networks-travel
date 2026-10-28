# E6 — repeated site-mixed CV and site-level uncertainty

## (a) Repeated stratified 10-fold pooled across sites (20 repeats, seeds 42..61)

|                          |   mean |   std |   min |   max |   count |   auc_mean |   auc_sd |
|:-------------------------|-------:|------:|------:|------:|--------:|-----------:|---------:|
| ('abide', 'agesex_lr')   |  0.526 | 0.003 | 0.517 | 0.529 |      20 |      0.489 |    0.009 |
| ('abide', 'lr')          |  0.652 | 0.009 | 0.637 | 0.673 |      20 |      0.708 |    0.006 |
| ('abide', 'svm')         |  0.64  | 0.008 | 0.625 | 0.657 |      20 |      0.695 |    0.006 |
| ('adhd200', 'agesex_lr') |  0.626 | 0.004 | 0.62  | 0.632 |      20 |      0.644 |    0.002 |
| ('adhd200', 'lr')        |  0.575 | 0.008 | 0.563 | 0.589 |      20 |      0.606 |    0.009 |
| ('adhd200', 'svm')       |  0.567 | 0.007 | 0.552 | 0.58  |      20 |      0.6   |    0.01  |
| ('ucla', 'agesex_lr')    |  0.57  | 0.009 | 0.554 | 0.588 |      20 |      0.587 |    0.007 |
| ('ucla', 'lr')           |  0.606 | 0.016 | 0.578 | 0.64  |      20 |      0.638 |    0.017 |

## (b) Leave-one-site-out diagonal: subject-level vs site-level summaries

| view      | model     |   n_sites |   n_sites_two_class |   pooled_bacc |   site_cluster_ci_low |   site_cluster_ci_high |   macro_bacc |   macro_sd |   macro_min |   macro_max |   macro_ci_low |   macro_ci_high |
|:----------|:----------|----------:|--------------------:|--------------:|----------------------:|-----------------------:|-------------:|-----------:|------------:|------------:|---------------:|----------------:|
| abide     | lr        |        17 |                  17 |         0.649 |                 0.618 |                  0.678 |        0.642 |      0.079 |       0.5   |       0.761 |          0.605 |           0.676 |
| abide     | svm       |        17 |                  17 |         0.634 |                 0.599 |                  0.668 |        0.627 |      0.089 |       0.467 |       0.761 |          0.584 |           0.664 |
| abide     | rf        |        17 |                  17 |         0.649 |                 0.62  |                  0.672 |        0.647 |      0.073 |       0.536 |       0.767 |          0.614 |           0.679 |
| abide     | agesex_lr |        17 |                  17 |         0.522 |                 0.495 |                  0.542 |        0.512 |      0.038 |       0.442 |       0.601 |          0.494 |           0.53  |
| adhd200   | lr        |         7 |                   6 |         0.459 |                 0.416 |                  0.495 |        0.503 |      0.019 |       0.467 |       0.521 |          0.486 |           0.516 |
| adhd200   | svm       |         7 |                   6 |         0.469 |                 0.432 |                  0.498 |        0.508 |      0.013 |       0.498 |       0.532 |          0.5   |           0.519 |
| adhd200   | rf        |         7 |                   6 |         0.474 |                 0.43  |                  0.502 |        0.485 |      0.04  |       0.404 |       0.503 |          0.452 |           0.502 |
| adhd200   | agesex_lr |         7 |                   6 |         0.609 |                 0.508 |                  0.637 |        0.602 |      0.051 |       0.503 |       0.643 |          0.558 |           0.632 |
| ucla      | lr        |         2 |                   2 |         0.525 |                 0.525 |                  0.613 |        0.589 |      0.034 |       0.565 |       0.613 |          0.565 |           0.613 |
| ucla      | svm       |         2 |                   2 |         0.513 |                 0.513 |                  0.621 |        0.589 |      0.046 |       0.557 |       0.621 |          0.557 |           0.621 |
| ucla      | rf        |         2 |                   2 |         0.398 |                 0.398 |                  0.549 |        0.524 |      0.035 |       0.5   |       0.549 |          0.5   |           0.549 |
| ucla      | agesex_lr |         2 |                   2 |         0.558 |                 0.558 |                  0.576 |        0.567 |      0.013 |       0.558 |       0.576 |          0.558 |           0.576 |
| ucla-adhd | lr        |         2 |                   2 |         0.416 |                 0.416 |                  0.485 |        0.471 |      0.02  |       0.457 |       0.485 |          0.457 |           0.485 |
| ucla-adhd | svm       |         2 |                   2 |         0.387 |                 0.387 |                  0.445 |        0.438 |      0.009 |       0.432 |       0.445 |          0.432 |           0.445 |
| ucla-adhd | rf        |         2 |                   2 |         0.411 |                 0.411 |                  0.5   |        0.48  |      0.028 |       0.46  |       0.5   |          0.46  |           0.5   |
| ucla-adhd | agesex_lr |         2 |                   2 |         0.421 |                 0.421 |                  0.43  |        0.428 |      0.004 |       0.425 |       0.43  |          0.425 |           0.43  |

`pooled_bacc` = balanced accuracy of the pooled out-of-fold predictions (the headline number, with a subject-level bootstrap CI in Table 2); `site_cluster_*` = percentile CI from resampling SITES with replacement; `macro_*` = mean of per-site balanced accuracies (sites with both classes only) with a site-level bootstrap CI.
