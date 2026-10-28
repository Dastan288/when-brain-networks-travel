# E3b — connectome vs demographics control; pooled vs per-site diagonal

## Connectome model minus age+sex control (paired bootstrap on identical held-out subjects)

| source            | target            | harmonization   | model   | metric            |   connectome |   agesex |   delta |   ci_low |   ci_high |
|:------------------|:------------------|:----------------|:--------|:------------------|-------------:|---------:|--------:|---------:|----------:|
| abide-filt_global | abide-filt_global | none            | lr      | balanced_accuracy |        0.653 |    0.522 |   0.131 |    0.097 |     0.168 |
| abide-filt_global | abide-filt_global | none            | lr      | auc               |        0.704 |    0.5   |   0.204 |    0.156 |     0.251 |
| abide-filt_global | abide-filt_global | none            | svm     | balanced_accuracy |        0.631 |    0.522 |   0.109 |    0.073 |     0.144 |
| abide-filt_global | abide-filt_global | none            | svm     | auc               |        0.683 |    0.5   |   0.184 |    0.133 |     0.231 |
| abide-filt_global | adhd200           | none            | lr      | balanced_accuracy |        0.537 |    0.631 |  -0.094 |   -0.136 |    -0.053 |
| abide-filt_global | adhd200           | none            | lr      | auc               |        0.579 |    0.612 |  -0.033 |   -0.09  |     0.023 |
| abide-filt_global | adhd200           | none            | svm     | balanced_accuracy |        0.547 |    0.631 |  -0.084 |   -0.127 |    -0.044 |
| abide-filt_global | adhd200           | none            | svm     | auc               |        0.578 |    0.612 |  -0.033 |   -0.089 |     0.024 |
| adhd200           | abide-filt_global | none            | lr      | balanced_accuracy |        0.539 |    0.531 |   0.009 |   -0.031 |     0.05  |
| adhd200           | abide-filt_global | none            | lr      | auc               |        0.549 |    0.533 |   0.016 |   -0.027 |     0.063 |
| adhd200           | abide-filt_global | none            | svm     | balanced_accuracy |        0.535 |    0.531 |   0.004 |   -0.037 |     0.045 |
| adhd200           | abide-filt_global | none            | svm     | auc               |        0.544 |    0.533 |   0.01  |   -0.034 |     0.059 |
| adhd200           | adhd200           | none            | lr      | balanced_accuracy |        0.459 |    0.609 |  -0.149 |   -0.19  |    -0.107 |
| adhd200           | adhd200           | none            | lr      | auc               |        0.468 |    0.621 |  -0.153 |   -0.202 |    -0.102 |
| adhd200           | adhd200           | none            | svm     | balanced_accuracy |        0.469 |    0.609 |  -0.14  |   -0.182 |    -0.098 |
| adhd200           | adhd200           | none            | svm     | auc               |        0.471 |    0.621 |  -0.15  |   -0.198 |    -0.099 |

## Leave-one-site-out diagonal: pooled out-of-fold vs per-site averages

| view              | harmonization   | model     |   n_sites |   n_sites_two_class |   pooled_bacc |   persite_mean_bacc |   persite_median_bacc |   persite_n_weighted_bacc |   pooled_auc |   persite_mean_auc | sites_single_class   |
|:------------------|:----------------|:----------|----------:|--------------------:|--------------:|--------------------:|----------------------:|--------------------------:|-------------:|-------------------:|:---------------------|
| abide-filt_global | combat_new      | lr        |        17 |                  17 |         0.668 |               0.658 |                 0.662 |                     0.669 |        0.717 |              0.7   |                      |
| abide-filt_global | combat_new      | svm       |        17 |                  17 |         0.656 |               0.645 |                 0.649 |                     0.658 |        0.704 |              0.687 |                      |
| abide-filt_global | combat_ref      | lr        |        17 |                  17 |         0.666 |               0.647 |                 0.649 |                     0.664 |        0.712 |              0.701 |                      |
| abide-filt_global | combat_ref      | svm       |        17 |                  17 |         0.651 |               0.634 |                 0.643 |                     0.649 |        0.699 |              0.687 |                      |
| abide-filt_global | none            | agesex_lr |        17 |                  17 |         0.522 |               0.512 |                 0.505 |                     0.521 |        0.5   |              0.504 |                      |
| abide-filt_global | none            | lr        |        17 |                  17 |         0.653 |               0.636 |                 0.635 |                     0.651 |        0.704 |              0.681 |                      |
| abide-filt_global | none            | svm       |        17 |                  17 |         0.631 |               0.616 |                 0.602 |                     0.627 |        0.683 |              0.662 |                      |
| adhd200           | combat_new      | lr        |         7 |                   6 |         0.497 |               0.502 |                 0.517 |                     0.507 |        0.493 |              0.498 | WashU                |
| adhd200           | combat_new      | svm       |         7 |                   6 |         0.487 |               0.492 |                 0.501 |                     0.498 |        0.488 |              0.488 | WashU                |
| adhd200           | combat_ref      | lr        |         7 |                   6 |         0.466 |               0.492 |                 0.504 |                     0.497 |        0.468 |              0.498 | WashU                |
| adhd200           | combat_ref      | svm       |         7 |                   6 |         0.466 |               0.492 |                 0.497 |                     0.498 |        0.464 |              0.488 | WashU                |
| adhd200           | none            | agesex_lr |         7 |                   6 |         0.609 |               0.602 |                 0.618 |                     0.615 |        0.621 |              0.648 | WashU                |
| adhd200           | none            | lr        |         7 |                   6 |         0.459 |               0.503 |                 0.508 |                     0.501 |        0.468 |              0.514 | WashU                |
| adhd200           | none            | svm       |         7 |                   6 |         0.469 |               0.508 |                 0.502 |                     0.506 |        0.471 |              0.513 | WashU                |
