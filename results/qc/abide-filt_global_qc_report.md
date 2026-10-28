# ABIDE I Preprocessed — QC table (Stage 1)

Derivative: C-PAC, strategy `filt_global`, ROI time series AAL-116 and CC200. Phenotypic file: `Phenotypic_V1_0b_preprocessed1.csv`.

## Counts

- Rows in phenotypic file: **1112**; without preprocessed outputs (`FILE_ID = no_filename`): **77**; with ROI series: **1035** (505 ASD / 530 TD, 48.8% ASD) across **17** sites (20 PCP SITE_IDs; UM/UCLA/LEUVEN sub-sites merged per config).
- Missing derivative files on disk: **0**.
- Subjects passing all rater QC flags (nilearn `quality_checked=True` criterion): **871** (403 ASD / 468 TD).
- Flags (thresholds from config): short series < 100 TP: 26; flat ROIs > 5: 24; mean FD > 0.5 mm: 29; any flag: 78.
- Age (all): 17.0 (8.0) y, range 6.5–64.0; male: 84.8%.
- Time points (AAL): min 78, median 176, max 316; ROIs: AAL 116, CC200 200.

## Per-site summary

| site     | sub_sites         |    n |   ASD |   TD |   ASD_% | age_mean_sd   |   male_% | n_timepoints         |   meanFD_median_mm |   rater_QC_pass |   flag_any |
|:---------|:------------------|-----:|------:|-----:|--------:|:--------------|---------:|:---------------------|-------------------:|----------------:|-----------:|
| CALTECH  |                   |   37 |    19 |   18 |    51.4 | 27.7 (10.4)   |     78.4 | 146                  |              0.065 |              15 |          7 |
| CMU      |                   |   27 |    14 |   13 |    51.9 | 26.6 (5.7)    |     77.8 | 202–316 (median 236) |              0.27  |              11 |         10 |
| KKI      |                   |   48 |    20 |   28 |    41.7 | 10.0 (1.3)    |     75   | 124–152 (median 152) |              0.107 |              33 |          1 |
| LEUVEN   | LEUVEN_1+LEUVEN_2 |   63 |    29 |   34 |    46   | 18.0 (5.0)    |     87.3 | 246                  |              0.081 |              56 |          0 |
| MAX_MUN  |                   |   52 |    24 |   28 |    46.2 | 25.3 (11.9)   |     92.3 | 116–196 (median 116) |              0.086 |              46 |          3 |
| NYU      |                   |  175 |    75 |  100 |    42.9 | 15.3 (6.6)    |     79.4 | 176                  |              0.051 |             172 |          0 |
| OHSU     |                   |   26 |    12 |   14 |    46.2 | 10.7 (1.8)    |    100   | 78                   |              0.061 |              25 |         26 |
| OLIN     |                   |   34 |    19 |   15 |    55.9 | 16.6 (3.5)    |     85.3 | 206                  |              0.128 |              28 |          1 |
| PITT     |                   |   56 |    29 |   27 |    51.8 | 18.9 (6.9)    |     85.7 | 196                  |              0.115 |              50 |          2 |
| SBL      |                   |   30 |    15 |   15 |    50   | 34.4 (8.6)    |    100   | 196                  |              0.141 |              26 |          3 |
| SDSU     |                   |   36 |    14 |   22 |    38.9 | 14.4 (1.8)    |     80.6 | 176                  |              0.056 |              27 |          4 |
| STANFORD |                   |   39 |    19 |   20 |    48.7 | 10.0 (1.6)    |     79.5 | 176–236 (median 236) |              0.089 |              25 |          0 |
| TRINITY  |                   |   47 |    22 |   25 |    46.8 | 17.0 (3.5)    |    100   | 146                  |              0.075 |              44 |          1 |
| UCLA     | UCLA_1+UCLA_2     |   98 |    54 |   44 |    55.1 | 13.0 (2.2)    |     87.8 | 116                  |              0.087 |              85 |          9 |
| UM       | UM_1+UM_2         |  140 |    66 |   74 |    47.1 | 14.0 (3.2)    |     80.7 | 296                  |              0.071 |             120 |          9 |
| USM      |                   |   71 |    46 |   25 |    64.8 | 22.7 (8.3)    |    100   | 232–236 (median 236) |              0.101 |              67 |          2 |
| YALE     |                   |   56 |    28 |   28 |    50   | 12.7 (2.9)    |     71.4 | 196                  |              0.084 |              41 |          0 |
| TOTAL    |                   | 1035 |   505 |  530 |    48.8 | 17.0 (8.0)    |     84.8 | 78–316 (median 176)  |              0.083 |             871 |         78 |

## Notes

- `n_timepoints` differs across sites because acquisition length differs (site-specific protocols); connectivity estimates from short runs are noisier — a candidate covariate/limitation.
- `rater_QC_pass` = nilearn's default filter (rater 1 OK; raters 2 OK/maybe; rater 3 OK). Not applied here; kept for a sensitivity analysis.
- Flat (zero-variance) ROIs mostly reflect atlas regions outside a site's field of view (cerebellum/temporal poles). They must be handled identically across datasets before FC.
- No subject is excluded by this script. Exclusion rules are decided once and recorded in PROGRESS.md.
