# E4 — interpretation (aal90, lr, top-k = 100)

## abide

- Fold stability (17 leave-one-site-out folds): Spearman(|w|) mean 0.752 (min 0.496); top-100 Jaccard mean 0.448 (min 0.190).
- Consensus top-100 edges present in the top-100 of ≥ 80 % of folds: 45.
- Sign split of top-100: 54 patient>control, 46 control>patient.

Top 15 edges:

|   rank | roi_a             | roi_b                |   weight_mean | sign            |   in_topk_fraction_of_folds |
|-------:|:------------------|:---------------------|--------------:|:----------------|----------------------------:|
|      1 | Olfactory_R       | Temporal_Pole_Sup_L  |       -0.3172 | control>patient |                      1      |
|      2 | Calcarine_R       | Cuneus_R             |        0.3149 | patient>control |                      1      |
|      3 | Cingulum_Post_L   | Cingulum_Post_R      |       -0.3122 | control>patient |                      1      |
|      4 | Precentral_R      | Frontal_Inf_Oper_R   |        0.2914 | patient>control |                      1      |
|      5 | Thalamus_L        | Thalamus_R           |       -0.2909 | control>patient |                      1      |
|      6 | Frontal_Sup_Orb_L | Cingulum_Post_R      |        0.2906 | patient>control |                      1      |
|      7 | Rectus_L          | Temporal_Mid_R       |       -0.2852 | control>patient |                      1      |
|      8 | Frontal_Sup_R     | Angular_L            |       -0.2829 | control>patient |                      1      |
|      9 | Occipital_Sup_R   | Occipital_Mid_R      |        0.2825 | patient>control |                      1      |
|     10 | Hippocampus_R     | Temporal_Mid_R       |        0.2735 | patient>control |                      1      |
|     11 | Frontal_Sup_R     | Frontal_Sup_Medial_R |        0.259  | patient>control |                      0.9412 |
|     12 | Cingulum_Post_R   | Thalamus_R           |       -0.2551 | control>patient |                      0.9412 |
|     13 | Cingulum_Post_L   | Paracentral_Lobule_R |        0.2508 | patient>control |                      0.9412 |
|     14 | Frontal_Sup_R     | Precuneus_L          |       -0.2481 | control>patient |                      1      |
|     15 | Olfactory_L       | Olfactory_R          |        0.2477 | patient>control |                      0.9412 |

Lobe-pair counts (upper triangle): `abide_lobe_pairs_count.csv` / `fig_abide_lobe_pairs.png`; enrichment vs. uniform selection (observed/expected): `abide_lobe_pairs_enrichment.csv`.

Lobe-pair enrichment (observed / expected, upper triangle):

|             |   Frontal |   Insula |   Limbic |   Occipital |   Parietal |   Subcortical |   Temporal |
|:------------|----------:|---------:|---------:|------------:|-----------:|--------------:|-----------:|
| Frontal     |      1.27 |     2.15 |     0.95 |        0.1  |       0.92 |          0.72 |       1.19 |
| Insula      |    nan    |     0    |     0    |        0    |       1.43 |          0    |       3.34 |
| Limbic      |    nan    |   nan    |     3.03 |        0.48 |       0.48 |          4.17 |       2.22 |
| Occipital   |    nan    |   nan    |   nan    |        2.64 |       0.61 |          0.72 |       0.72 |
| Parietal    |    nan    |   nan    |   nan    |      nan    |       0.88 |          0    |       0.72 |
| Subcortical |    nan    |   nan    |   nan    |      nan    |     nan    |          1.43 |       0.42 |
| Temporal    |    nan    |   nan    |   nan    |      nan    |     nan    |        nan    |       1.21 |

Permutation test (10000 random draws of 100 edges; two-sided, BH-corrected across lobe pairs) — top rows:

| lobe_a    | lobe_b      |   observed |   expected |   obs_over_exp |   p_perm |   p_fdr |
|:----------|:------------|-----------:|-----------:|---------------:|---------:|--------:|
| Limbic    | Subcortical |         10 |      2.394 |          4.177 |    0     |   0.006 |
| Frontal   | Occipital   |          1 |      9.768 |          0.102 |    0.001 |   0.011 |
| Limbic    | Limbic      |          5 |      1.665 |          3.003 |    0.048 |   0.309 |
| Occipital | Occipital   |          6 |      2.268 |          2.646 |    0.053 |   0.309 |
| Limbic    | Temporal    |          8 |      3.594 |          2.226 |    0.055 |   0.309 |
| Parietal  | Subcortical |          0 |      2.78  |          0     |    0.12  |   0.561 |
| Insula    | Temporal    |          2 |      0.615 |          3.251 |    0.251 |   1     |
| Frontal   | Insula      |          3 |      1.427 |          2.102 |    0.339 |   1     |

Lobe pairs with p_FDR < 0.05: 2 of 28.

## adhd200

- Fold stability (7 leave-one-site-out folds): Spearman(|w|) mean 0.486 (min 0.140); top-100 Jaccard mean 0.257 (min 0.058).
- Consensus top-100 edges present in the top-100 of ≥ 80 % of folds: 21.
- Sign split of top-100: 50 patient>control, 50 control>patient.

Top 15 edges:

|   rank | roi_a              | roi_b                |   weight_mean | sign            |   in_topk_fraction_of_folds |
|-------:|:-------------------|:---------------------|--------------:|:----------------|----------------------------:|
|      1 | Frontal_Inf_Oper_L | Temporal_Pole_Sup_L  |       -0.2662 | control>patient |                      1      |
|      2 | Frontal_Inf_Oper_R | SupraMarginal_R      |        0.2576 | patient>control |                      1      |
|      3 | Occipital_Inf_R    | Temporal_Inf_R       |       -0.2076 | control>patient |                      1      |
|      4 | Occipital_Inf_R    | Putamen_L            |       -0.2026 | control>patient |                      1      |
|      5 | Occipital_Inf_R    | Temporal_Sup_R       |        0.2002 | patient>control |                      1      |
|      6 | Hippocampus_R      | Thalamus_R           |        0.1973 | patient>control |                      0.8571 |
|      7 | Frontal_Sup_R      | Frontal_Sup_Medial_L |        0.1973 | patient>control |                      0.8571 |
|      8 | Frontal_Sup_R      | Frontal_Sup_Orb_R    |       -0.1936 | control>patient |                      0.8571 |
|      9 | Cingulum_Ant_R     | SupraMarginal_L      |       -0.1928 | control>patient |                      0.8571 |
|     10 | Frontal_Inf_Tri_R  | Temporal_Mid_L       |       -0.1916 | control>patient |                      0.7143 |
|     11 | Calcarine_L        | Occipital_Mid_L      |       -0.1882 | control>patient |                      0.8571 |
|     12 | Cingulum_Ant_R     | Cuneus_L             |        0.1876 | patient>control |                      0.8571 |
|     13 | Precentral_L       | Hippocampus_R        |       -0.1853 | control>patient |                      0.8571 |
|     14 | Frontal_Inf_Orb_R  | Temporal_Mid_R       |        0.1848 | patient>control |                      0.8571 |
|     15 | Precentral_R       | Frontal_Mid_Orb_L    |       -0.1822 | control>patient |                      0.8571 |

Lobe-pair counts (upper triangle): `adhd200_lobe_pairs_count.csv` / `fig_adhd200_lobe_pairs.png`; enrichment vs. uniform selection (observed/expected): `adhd200_lobe_pairs_enrichment.csv`.

Lobe-pair enrichment (observed / expected, upper triangle):

|             |   Frontal |   Insula |   Limbic |   Occipital |   Parietal |   Subcortical |   Temporal |
|:------------|----------:|---------:|---------:|------------:|-----------:|--------------:|-----------:|
| Frontal     |      2.01 |     0.72 |     1.31 |        0.61 |       1.12 |          0.72 |       0.83 |
| Insula      |    nan    |     0    |     0    |        0    |       0    |          0    |       0    |
| Limbic      |    nan    |   nan    |     0    |        0.48 |       1.67 |          0.83 |       0.28 |
| Occipital   |    nan    |   nan    |   nan    |        0.88 |       0.61 |          0.72 |       1.43 |
| Parietal    |    nan    |   nan    |   nan    |      nan    |       0.44 |          1.07 |       0.95 |
| Subcortical |    nan    |   nan    |   nan    |      nan    |     nan    |          0    |       2.09 |
| Temporal    |    nan    |   nan    |   nan    |      nan    |     nan    |        nan    |       1.82 |

Permutation test (10000 random draws of 100 edges; two-sided, BH-corrected across lobe pairs) — top rows:

| lobe_a      | lobe_b    |   observed |   expected |   obs_over_exp |   p_perm |   p_fdr |
|:------------|:----------|-----------:|-----------:|---------------:|---------:|--------:|
| Frontal     | Frontal   |         19 |      9.445 |          2.012 |    0.005 |   0.146 |
| Subcortical | Temporal  |          5 |      2.395 |          2.088 |    0.188 |   1     |
| Limbic      | Temporal  |          1 |      3.594 |          0.278 |    0.247 |   1     |
| Limbic      | Parietal  |          7 |      4.198 |          1.668 |    0.257 |   1     |
| Frontal     | Occipital |          6 |      9.768 |          0.614 |    0.26  |   1     |
| Limbic      | Limbic    |          0 |      1.665 |          0     |    0.353 |   1     |
| Limbic      | Occipital |          2 |      4.181 |          0.478 |    0.412 |   1     |
| Frontal     | Limbic    |         11 |      8.409 |          1.308 |    0.437 |   1     |

Lobe pairs with p_FDR < 0.05: 0 of 28.

## abide-filt_global

- Fold stability (17 leave-one-site-out folds): Spearman(|w|) mean 0.753 (min 0.481); top-100 Jaccard mean 0.441 (min 0.250).
- Consensus top-100 edges present in the top-100 of ≥ 80 % of folds: 43.
- Sign split of top-100: 50 patient>control, 50 control>patient.

Top 15 edges:

|   rank | roi_a             | roi_b                |   weight_mean | sign            |   in_topk_fraction_of_folds |
|-------:|:------------------|:---------------------|--------------:|:----------------|----------------------------:|
|      1 | Frontal_Sup_R     | Angular_L            |       -0.2407 | control>patient |                      1      |
|      2 | Rectus_L          | Temporal_Mid_R       |       -0.2346 | control>patient |                      1      |
|      3 | Frontal_Sup_Orb_L | Caudate_L            |       -0.2077 | control>patient |                      1      |
|      4 | Calcarine_R       | Cuneus_R             |        0.2047 | patient>control |                      1      |
|      5 | Cingulum_Post_L   | Cingulum_Post_R      |       -0.2032 | control>patient |                      1      |
|      6 | Cingulum_Mid_L    | Occipital_Mid_L      |        0.1931 | patient>control |                      0.9412 |
|      7 | Frontal_Inf_Tri_L | Temporal_Inf_R       |        0.1928 | patient>control |                      0.9412 |
|      8 | Frontal_Sup_R     | Precuneus_L          |       -0.1924 | control>patient |                      1      |
|      9 | Cuneus_R          | Paracentral_Lobule_R |        0.1924 | patient>control |                      1      |
|     10 | Caudate_L         | Temporal_Pole_Sup_R  |        0.1897 | patient>control |                      1      |
|     11 | Frontal_Sup_Orb_L | Cingulum_Post_R      |        0.1891 | patient>control |                      0.9412 |
|     12 | Thalamus_L        | Thalamus_R           |       -0.1882 | control>patient |                      0.9412 |
|     13 | Insula_L          | Temporal_Sup_L       |        0.1878 | patient>control |                      0.9412 |
|     14 | Supp_Motor_Area_L | Hippocampus_R        |       -0.1869 | control>patient |                      1      |
|     15 | Precentral_R      | Frontal_Inf_Oper_R   |        0.1867 | patient>control |                      0.9412 |

Lobe-pair counts (upper triangle): `abide-filt_global_lobe_pairs_count.csv` / `fig_abide-filt_global_lobe_pairs.png`; enrichment vs. uniform selection (observed/expected): `abide-filt_global_lobe_pairs_enrichment.csv`.

Lobe-pair enrichment (observed / expected, upper triangle):

|             |   Frontal |   Insula |   Limbic |   Occipital |   Parietal |   Subcortical |   Temporal |
|:------------|----------:|---------:|---------:|------------:|-----------:|--------------:|-----------:|
| Frontal     |      0.64 |        0 |     1.31 |        1.12 |       1.02 |          0.72 |       1.19 |
| Insula      |    nan    |        0 |     0    |        0    |       0    |          0    |       1.67 |
| Limbic      |    nan    |      nan |     1.82 |        1.19 |       0.95 |          1.67 |       1.11 |
| Occipital   |    nan    |      nan |   nan    |        1.76 |       1.02 |          0.72 |       0.72 |
| Parietal    |    nan    |      nan |   nan    |      nan    |       1.32 |          0.72 |       1.19 |
| Subcortical |    nan    |      nan |   nan    |      nan    |     nan    |          1.43 |       0.83 |
| Temporal    |    nan    |      nan |   nan    |      nan    |     nan    |        nan    |       0    |

Permutation test (10000 random draws of 100 edges; two-sided, BH-corrected across lobe pairs) — top rows:

| lobe_a    | lobe_b      |   observed |   expected |   obs_over_exp |   p_perm |   p_fdr |
|:----------|:------------|-----------:|-----------:|---------------:|---------:|--------:|
| Frontal   | Frontal     |          6 |      9.445 |          0.635 |    0.297 |       1 |
| Temporal  | Temporal    |          0 |      1.668 |          0     |    0.363 |       1 |
| Occipital | Occipital   |          4 |      2.268 |          1.764 |    0.379 |       1 |
| Limbic    | Subcortical |          4 |      2.394 |          1.671 |    0.432 |       1 |
| Frontal   | Limbic      |         11 |      8.409 |          1.308 |    0.437 |       1 |
| Frontal   | Insula      |          0 |      1.427 |          0     |    0.456 |       1 |
| Limbic    | Limbic      |          3 |      1.665 |          1.802 |    0.461 |       1 |
| Frontal   | Temporal    |         10 |      8.406 |          1.19  |    0.648 |       1 |

Lobe pairs with p_FDR < 0.05: 0 of 28.

## Cross-dataset similarity of consensus weights

| dataset_a   | dataset_b         |   spearman_abs_w |   spearman_signed_w |   jaccard_top100 |   expected_jaccard_random |   jaccard_null_p |
|:------------|:------------------|-----------------:|--------------------:|-----------------:|--------------------------:|-----------------:|
| abide       | adhd200           |           0.022  |              0.0269 |           0.0101 |                    0.0126 |           0.7076 |
| abide       | abide-filt_global |           0.6274 |              0.8568 |           0.3072 |                    0.0126 |           0.0005 |
| adhd200     | abide-filt_global |           0.0223 |              0.0156 |           0.0101 |                    0.0126 |           0.7076 |

