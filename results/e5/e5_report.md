# E5 — connectome information beyond age and sex (aal90, logistic regression)

`conn+agesex` = connectome features with age and sex appended; `conn_resid` = every edge residualized on age and sex with coefficients fitted on the training set only. Diagonal = leave-one-site-out; off-diagonal = train on all of source, test on all of target. Bootstrap: 1000 subject-level resamples; paired deltas on identical held-out participants; p-values are two-sided bootstrap p-values, BH-corrected within each metric.

## Balanced accuracy by feature set

|                            |   agesex |   conn |   conn+agesex |   conn_resid |
|:---------------------------|---------:|-------:|--------------:|-------------:|
| ('abide', 'abide')         |    0.522 |  0.649 |         0.653 |        0.644 |
| ('abide', 'adhd200')       |    0.631 |  0.529 |         0.53  |        0.522 |
| ('abide', 'ucla')          |    0.547 |  0.589 |         0.581 |        0.545 |
| ('adhd200', 'adhd200')     |    0.609 |  0.459 |         0.475 |        0.479 |
| ('adhd200', 'ucla-adhd')   |    0.5   |  0.529 |         0.517 |        0.498 |
| ('ucla', 'ucla')           |    0.558 |  0.525 |         0.521 |        0.513 |
| ('ucla-adhd', 'adhd200')   |    0.5   |  0.523 |         0.523 |        0.502 |
| ('ucla-adhd', 'ucla-adhd') |    0.421 |  0.416 |         0.408 |        0.416 |

## Full metrics

| source    | target    | features    | protocol      |   balanced_accuracy |   balanced_accuracy_ci_low |   balanced_accuracy_ci_high |   auc |   auc_ci_low |   auc_ci_high |
|:----------|:----------|:------------|:--------------|--------------------:|---------------------------:|----------------------------:|------:|-------------:|--------------:|
| abide     | abide     | conn        | losite        |               0.649 |                      0.62  |                       0.677 | 0.698 |        0.665 |         0.729 |
| abide     | abide     | agesex      | losite        |               0.522 |                      0.499 |                       0.545 | 0.5   |        0.465 |         0.534 |
| abide     | abide     | conn+agesex | losite        |               0.653 |                      0.623 |                       0.68  | 0.698 |        0.665 |         0.729 |
| abide     | abide     | conn_resid  | losite        |               0.644 |                      0.614 |                       0.672 | 0.696 |        0.663 |         0.727 |
| adhd200   | adhd200   | conn        | losite        |               0.459 |                      0.43  |                       0.492 | 0.468 |        0.431 |         0.507 |
| adhd200   | adhd200   | agesex      | losite        |               0.609 |                      0.579 |                       0.639 | 0.621 |        0.586 |         0.656 |
| adhd200   | adhd200   | conn+agesex | losite        |               0.475 |                      0.448 |                       0.506 | 0.487 |        0.451 |         0.524 |
| adhd200   | adhd200   | conn_resid  | losite        |               0.479 |                      0.453 |                       0.508 | 0.471 |        0.435 |         0.51  |
| abide     | adhd200   | conn        | cross_dataset |               0.529 |                      0.5   |                       0.554 | 0.566 |        0.527 |         0.602 |
| abide     | adhd200   | agesex      | cross_dataset |               0.631 |                      0.603 |                       0.661 | 0.612 |        0.577 |         0.647 |
| abide     | adhd200   | conn+agesex | cross_dataset |               0.53  |                      0.501 |                       0.555 | 0.563 |        0.525 |         0.599 |
| abide     | adhd200   | conn_resid  | cross_dataset |               0.522 |                      0.493 |                       0.546 | 0.544 |        0.504 |         0.579 |
| ucla      | ucla      | conn        | losite        |               0.525 |                      0.469 |                       0.582 | 0.508 |        0.438 |         0.578 |
| ucla      | ucla      | agesex      | losite        |               0.558 |                      0.499 |                       0.62  | 0.569 |        0.501 |         0.638 |
| ucla      | ucla      | conn+agesex | losite        |               0.521 |                      0.464 |                       0.579 | 0.51  |        0.44  |         0.58  |
| ucla      | ucla      | conn_resid  | losite        |               0.513 |                      0.458 |                       0.57  | 0.463 |        0.397 |         0.535 |
| ucla-adhd | ucla-adhd | conn        | losite        |               0.416 |                      0.334 |                       0.497 | 0.348 |        0.244 |         0.448 |
| ucla-adhd | ucla-adhd | agesex      | losite        |               0.421 |                      0.341 |                       0.517 | 0.407 |        0.301 |         0.53  |
| ucla-adhd | ucla-adhd | conn+agesex | losite        |               0.408 |                      0.325 |                       0.492 | 0.349 |        0.245 |         0.448 |
| ucla-adhd | ucla-adhd | conn_resid  | losite        |               0.416 |                      0.337 |                       0.495 | 0.356 |        0.253 |         0.456 |
| abide     | ucla      | conn        | cross_dataset |               0.589 |                      0.532 |                       0.646 | 0.627 |        0.554 |         0.695 |
| abide     | ucla      | agesex      | cross_dataset |               0.547 |                      0.49  |                       0.606 | 0.594 |        0.527 |         0.661 |
| abide     | ucla      | conn+agesex | cross_dataset |               0.581 |                      0.525 |                       0.637 | 0.623 |        0.55  |         0.689 |
| abide     | ucla      | conn_resid  | cross_dataset |               0.545 |                      0.484 |                       0.606 | 0.598 |        0.523 |         0.664 |
| adhd200   | ucla-adhd | conn        | cross_dataset |               0.529 |                      0.443 |                       0.621 | 0.502 |        0.398 |         0.611 |
| adhd200   | ucla-adhd | agesex      | cross_dataset |               0.5   |                      0.5   |                       0.5   | 0.486 |        0.377 |         0.594 |
| adhd200   | ucla-adhd | conn+agesex | cross_dataset |               0.517 |                      0.428 |                       0.608 | 0.503 |        0.4   |         0.611 |
| adhd200   | ucla-adhd | conn_resid  | cross_dataset |               0.498 |                      0.416 |                       0.572 | 0.491 |        0.389 |         0.592 |
| ucla-adhd | adhd200   | conn        | cross_dataset |               0.523 |                      0.497 |                       0.548 | 0.539 |        0.501 |         0.577 |
| ucla-adhd | adhd200   | agesex      | cross_dataset |               0.5   |                      0.5   |                       0.5   | 0.36  |        0.327 |         0.395 |
| ucla-adhd | adhd200   | conn+agesex | cross_dataset |               0.523 |                      0.497 |                       0.549 | 0.537 |        0.499 |         0.575 |
| ucla-adhd | adhd200   | conn_resid  | cross_dataset |               0.502 |                      0.477 |                       0.525 | 0.516 |        0.477 |         0.555 |

## Paired differences (model minus baseline)

| source    | target    | baseline   | model_features   | metric            |   delta |   ci_low |   ci_high |   p_boot |   p_fdr |
|:----------|:----------|:-----------|:-----------------|:------------------|--------:|---------:|----------:|---------:|--------:|
| abide     | abide     | agesex     | conn             | balanced_accuracy |  0.127  |   0.0929 |    0.1618 |    0     |  0      |
| abide     | abide     | agesex     | conn             | auc               |  0.1989 |   0.1515 |    0.2462 |    0     |  0      |
| abide     | abide     | agesex     | conn+agesex      | balanced_accuracy |  0.1307 |   0.097  |    0.1641 |    0     |  0      |
| abide     | abide     | agesex     | conn+agesex      | auc               |  0.1987 |   0.1511 |    0.2458 |    0     |  0      |
| abide     | abide     | agesex     | conn_resid       | balanced_accuracy |  0.1219 |   0.083  |    0.1574 |    0     |  0      |
| abide     | abide     | agesex     | conn_resid       | auc               |  0.1963 |   0.1479 |    0.2439 |    0     |  0      |
| abide     | abide     | conn       | conn+agesex      | balanced_accuracy |  0.0037 |  -0.004  |    0.0114 |    0.336 |  0.6618 |
| abide     | abide     | conn       | conn+agesex      | auc               | -0.0001 |  -0.0017 |    0.0013 |    0.874 |  0.91   |
| abide     | abide     | conn       | conn_resid       | balanced_accuracy | -0.0051 |  -0.0197 |    0.0097 |    0.548 |  0.8119 |
| abide     | abide     | conn       | conn_resid       | auc               | -0.0026 |  -0.0102 |    0.0047 |    0.506 |  0.68   |
| adhd200   | adhd200   | agesex     | conn             | balanced_accuracy | -0.1494 |  -0.1897 |   -0.1065 |    0     |  0      |
| adhd200   | adhd200   | agesex     | conn             | auc               | -0.1526 |  -0.2017 |   -0.1017 |    0     |  0      |
| adhd200   | adhd200   | agesex     | conn+agesex      | balanced_accuracy | -0.1336 |  -0.1714 |   -0.0922 |    0     |  0      |
| adhd200   | adhd200   | agesex     | conn+agesex      | auc               | -0.1345 |  -0.1809 |   -0.0856 |    0     |  0      |
| adhd200   | adhd200   | agesex     | conn_resid       | balanced_accuracy | -0.1291 |  -0.1702 |   -0.0871 |    0     |  0      |
| adhd200   | adhd200   | agesex     | conn_resid       | auc               | -0.1496 |  -0.1976 |   -0.0938 |    0     |  0      |
| adhd200   | adhd200   | conn       | conn+agesex      | balanced_accuracy |  0.0158 |   0.0026 |    0.0296 |    0.02  |  0.0667 |
| adhd200   | adhd200   | conn       | conn+agesex      | auc               |  0.0182 |   0.0127 |    0.0236 |    0     |  0      |
| adhd200   | adhd200   | conn       | conn_resid       | balanced_accuracy |  0.0203 |  -0.0005 |    0.0408 |    0.058 |  0.1785 |
| adhd200   | adhd200   | conn       | conn_resid       | auc               |  0.003  |  -0.0152 |    0.0207 |    0.736 |  0.8886 |
| ucla      | ucla      | agesex     | conn             | balanced_accuracy | -0.033  |  -0.1081 |    0.0415 |    0.386 |  0.6633 |
| ucla      | ucla      | agesex     | conn             | auc               | -0.0615 |  -0.1468 |    0.0235 |    0.148 |  0.2574 |
| ucla      | ucla      | agesex     | conn+agesex      | balanced_accuracy | -0.0366 |  -0.1126 |    0.0377 |    0.364 |  0.6618 |
| ucla      | ucla      | agesex     | conn+agesex      | auc               | -0.0595 |  -0.1449 |    0.0242 |    0.164 |  0.2733 |
| ucla      | ucla      | agesex     | conn_resid       | balanced_accuracy | -0.0443 |  -0.1249 |    0.0371 |    0.29  |  0.6105 |
| ucla      | ucla      | agesex     | conn_resid       | auc               | -0.1061 |  -0.1963 |   -0.0131 |    0.028 |  0.0622 |
| ucla      | ucla      | conn       | conn+agesex      | balanced_accuracy | -0.0036 |  -0.0203 |    0.0132 |    0.806 |  0.9529 |
| ucla      | ucla      | conn       | conn+agesex      | auc               |  0.0019 |  -0.0007 |    0.0048 |    0.138 |  0.2509 |
| ucla      | ucla      | conn       | conn_resid       | balanced_accuracy | -0.0113 |  -0.0491 |    0.033  |    0.644 |  0.8883 |
| ucla      | ucla      | conn       | conn_resid       | auc               | -0.0446 |  -0.0736 |   -0.0141 |    0.004 |  0.01   |
| ucla-adhd | ucla-adhd | agesex     | conn             | balanced_accuracy | -0.0051 |  -0.1195 |    0.1001 |    0.862 |  0.9644 |
| ucla-adhd | ucla-adhd | agesex     | conn             | auc               | -0.059  |  -0.2038 |    0.0704 |    0.322 |  0.5108 |
| ucla-adhd | ucla-adhd | agesex     | conn+agesex      | balanced_accuracy | -0.0133 |  -0.1294 |    0.0962 |    0.756 |  0.9529 |
| ucla-adhd | ucla-adhd | agesex     | conn+agesex      | auc               | -0.0582 |  -0.2008 |    0.0713 |    0.332 |  0.5108 |
| ucla-adhd | ucla-adhd | agesex     | conn_resid       | balanced_accuracy | -0.0049 |  -0.1182 |    0.1063 |    0.868 |  0.9644 |
| ucla-adhd | ucla-adhd | agesex     | conn_resid       | auc               | -0.0508 |  -0.1958 |    0.0821 |    0.402 |  0.5956 |
| ucla-adhd | ucla-adhd | conn       | conn+agesex      | balanced_accuracy | -0.0082 |  -0.0208 |    0      |    0.28  |  0.6105 |
| ucla-adhd | ucla-adhd | conn       | conn+agesex      | auc               |  0.0008 |  -0.0032 |    0.0051 |    0.684 |  0.855  |
| ucla-adhd | ucla-adhd | conn       | conn_resid       | balanced_accuracy |  0.0002 |  -0.0609 |    0.0675 |    0.996 |  0.996  |
| ucla-adhd | ucla-adhd | conn       | conn_resid       | auc               |  0.0082 |  -0.0241 |    0.0432 |    0.612 |  0.7897 |
| abide     | ucla      | agesex     | conn             | balanced_accuracy |  0.0422 |  -0.0337 |    0.1196 |    0.282 |  0.6105 |
| abide     | ucla      | agesex     | conn             | auc               |  0.0328 |  -0.0564 |    0.1186 |    0.468 |  0.6686 |
| abide     | ucla      | agesex     | conn+agesex      | balanced_accuracy |  0.034  |  -0.0433 |    0.1102 |    0.398 |  0.6633 |
| abide     | ucla      | agesex     | conn+agesex      | auc               |  0.0288 |  -0.0614 |    0.1153 |    0.51  |  0.68   |
| abide     | ucla      | agesex     | conn_resid       | balanced_accuracy | -0.0013 |  -0.0859 |    0.0834 |    0.97  |  0.996  |
| abide     | ucla      | agesex     | conn_resid       | auc               |  0.0043 |  -0.0943 |    0.0944 |    0.902 |  0.91   |
| abide     | ucla      | conn       | conn+agesex      | balanced_accuracy | -0.0082 |  -0.0205 |    0      |    0.272 |  0.6105 |
| abide     | ucla      | conn       | conn+agesex      | auc               | -0.004  |  -0.0093 |    0.0008 |    0.128 |  0.2438 |
| abide     | ucla      | conn       | conn_resid       | balanced_accuracy | -0.0435 |  -0.0767 |   -0.0099 |    0.014 |  0.0509 |
| abide     | ucla      | conn       | conn_resid       | auc               | -0.0284 |  -0.0504 |   -0.0101 |    0.004 |  0.01   |
| abide     | adhd200   | agesex     | conn             | balanced_accuracy | -0.1025 |  -0.1413 |   -0.0623 |    0     |  0      |
| abide     | adhd200   | agesex     | conn             | auc               | -0.0458 |  -0.1026 |    0.0121 |    0.122 |  0.2438 |
| abide     | adhd200   | agesex     | conn+agesex      | balanced_accuracy | -0.1014 |  -0.1426 |   -0.0617 |    0     |  0      |
| abide     | adhd200   | agesex     | conn+agesex      | auc               | -0.0481 |  -0.1052 |    0.0097 |    0.1   |  0.2105 |
| abide     | adhd200   | agesex     | conn_resid       | balanced_accuracy | -0.1088 |  -0.1503 |   -0.0693 |    0     |  0      |
| abide     | adhd200   | agesex     | conn_resid       | auc               | -0.068  |  -0.1264 |   -0.0095 |    0.026 |  0.0612 |
| abide     | adhd200   | conn       | conn+agesex      | balanced_accuracy |  0.0011 |  -0.0045 |    0.0073 |    0.802 |  0.9529 |
| abide     | adhd200   | conn       | conn+agesex      | auc               | -0.0023 |  -0.0036 |   -0.001  |    0     |  0      |
| abide     | adhd200   | conn       | conn_resid       | balanced_accuracy | -0.0063 |  -0.0214 |    0.0083 |    0.36  |  0.6618 |
| abide     | adhd200   | conn       | conn_resid       | auc               | -0.0222 |  -0.0293 |   -0.0152 |    0     |  0      |
| adhd200   | ucla-adhd | agesex     | conn             | balanced_accuracy |  0.0291 |  -0.0568 |    0.1209 |    0.52  |  0.8    |
| adhd200   | ucla-adhd | agesex     | conn             | auc               |  0.0153 |  -0.1309 |    0.1707 |    0.808 |  0.8886 |
| adhd200   | ucla-adhd | agesex     | conn+agesex      | balanced_accuracy |  0.0168 |  -0.0717 |    0.1078 |    0.714 |  0.952  |
| adhd200   | ucla-adhd | agesex     | conn+agesex      | auc               |  0.0169 |  -0.1227 |    0.163  |    0.766 |  0.8886 |
| adhd200   | ucla-adhd | agesex     | conn_resid       | balanced_accuracy | -0.002  |  -0.0838 |    0.0724 |    0.984 |  0.996  |
| adhd200   | ucla-adhd | agesex     | conn_resid       | auc               |  0.0042 |  -0.1591 |    0.1861 |    0.91  |  0.91   |
| adhd200   | ucla-adhd | conn       | conn+agesex      | balanced_accuracy | -0.0123 |  -0.0582 |    0.027  |    0.574 |  0.82   |
| adhd200   | ucla-adhd | conn       | conn+agesex      | auc               |  0.0016 |  -0.0192 |    0.0213 |    0.822 |  0.8886 |
| adhd200   | ucla-adhd | conn       | conn_resid       | balanced_accuracy | -0.0311 |  -0.1072 |    0.0472 |    0.448 |  0.7168 |
| adhd200   | ucla-adhd | conn       | conn_resid       | auc               | -0.0111 |  -0.0742 |    0.0497 |    0.78  |  0.8886 |
| ucla-adhd | adhd200   | agesex     | conn             | balanced_accuracy |  0.0227 |  -0.0034 |    0.0483 |    0.096 |  0.256  |
| ucla-adhd | adhd200   | agesex     | conn             | auc               |  0.1788 |   0.1307 |    0.2274 |    0     |  0      |
| ucla-adhd | adhd200   | agesex     | conn+agesex      | balanced_accuracy |  0.0233 |  -0.003  |    0.0489 |    0.088 |  0.2514 |
| ucla-adhd | adhd200   | agesex     | conn+agesex      | auc               |  0.1764 |   0.1283 |    0.2254 |    0     |  0      |
| ucla-adhd | adhd200   | agesex     | conn_resid       | balanced_accuracy |  0.0017 |  -0.0227 |    0.0245 |    0.934 |  0.996  |
| ucla-adhd | adhd200   | agesex     | conn_resid       | auc               |  0.1555 |   0.1089 |    0.2028 |    0     |  0      |
| ucla-adhd | adhd200   | conn       | conn+agesex      | balanced_accuracy |  0.0006 |  -0.0056 |    0.0069 |    0.81  |  0.9529 |
| ucla-adhd | adhd200   | conn       | conn+agesex      | auc               | -0.0024 |  -0.0036 |   -0.0013 |    0     |  0      |
| ucla-adhd | adhd200   | conn       | conn_resid       | balanced_accuracy | -0.0209 |  -0.0352 |   -0.0076 |    0.002 |  0.008  |
| ucla-adhd | adhd200   | conn       | conn_resid       | auc               | -0.0233 |  -0.0299 |   -0.0171 |    0     |  0      |
