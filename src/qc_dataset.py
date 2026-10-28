#!/usr/bin/env python
"""QC tables for the non-ABIDE datasets (ADHD-200, UCLA-CNP) from the packed ROI series + phenotypes,
using the same loaders as src/features.py so that the QC table describes exactly the analysed sample.

Outputs: results/qc/<tag>_subjects_qc.csv, <tag>_site_summary.csv, <tag>_qc_report.md
Usage:   python src/qc_dataset.py --dataset adhd200 | ucla
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PROJECT_ROOT, load_config, set_seed  # noqa: E402
from src.features import LOADERS  # noqa: E402


def fmt_mean_sd(x: pd.Series, d: int = 1) -> str:
    x = x.dropna()
    return f"{x.mean():.{d}f} ({x.std(ddof=1):.{d}f})" if len(x) > 1 else "–"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["adhd200", "ucla"])
    args = ap.parse_args()
    cfg = load_config()
    set_seed(cfg["seed"])
    data = LOADERS[args.dataset](cfg)
    meta: pd.DataFrame = data["meta"].copy()
    ser = data["series"]["aal"]
    meta["n_rois"] = meta["file_id"].map(lambda f: ser[f].shape[1])
    meta["n_flat_rois"] = meta["file_id"].map(lambda f: int(np.sum(~(ser[f].std(axis=0) > 0))))
    meta["n_nan"] = meta["file_id"].map(lambda f: int(np.isnan(ser[f]).sum()))
    thr = cfg["qc"]["exclude_flat_fraction_gt"]
    meta["flag_excluded_flat"] = meta["n_flat_rois"] / meta["n_rois"] > thr
    meta["flag_short"] = meta["n_timepoints"] < cfg["qc"]["min_timepoints"]
    meta["flag_motion"] = meta["mean_fd"] > cfg["qc"]["max_mean_fd_mm"]
    out = PROJECT_ROOT / cfg["paths"]["qc"]
    tag = data["tag"]
    meta.to_csv(out / f"{tag}_subjects_qc.csv", index=False)

    rows = []
    for site, g in list(meta.groupby("site")) + [("TOTAL", meta)]:
        tps = g["n_timepoints"]
        rows.append({"site": site, "n": len(g), "patients": int(g["y"].sum()), "controls": int((g["y"] == 0).sum()),
                     "patient_%": round(100 * g["y"].mean(), 1), "dx_groups": ", ".join(f"{k}:{v}" for k, v in g["dx"].value_counts().items()),
                     "age_mean_sd": fmt_mean_sd(g["age"]), "age_min": round(g["age"].min(), 1), "age_max": round(g["age"].max(), 1),
                     "male_%": round(100 * (g["sex"] == "M").mean(), 1),
                     "n_timepoints": str(int(tps.iloc[0])) if tps.nunique() == 1 else f"{int(tps.min())}–{int(tps.max())} (median {int(tps.median())})",
                     "meanFD_median_mm": round(float(g["mean_fd"].median()), 3) if g["mean_fd"].notna().any() else np.nan,
                     "flat_rois_median": int(g["n_flat_rois"].median()), "excluded_flat": int(g["flag_excluded_flat"].sum()),
                     "flag_short": int(g["flag_short"].sum()), "flag_motion": int(g["flag_motion"].sum())})
    site = pd.DataFrame(rows)
    site.to_csv(out / f"{tag}_site_summary.csv", index=False)
    lines = [f"# {tag} — QC table", "",
             f"- Subjects with ROI series and a usable diagnosis: **{len(meta)}** ({int(meta['y'].sum())} patients / "
             f"{int((meta['y']==0).sum())} controls) across **{meta['site'].nunique()}** site(s); ROIs: {int(meta['n_rois'].mode().iloc[0])}.",
             f"- Time points: min {int(meta['n_timepoints'].min())}, median {int(meta['n_timepoints'].median())}, max {int(meta['n_timepoints'].max())}; "
             f"NaN values: {int(meta['n_nan'].sum())}.",
             f"- Age {fmt_mean_sd(meta['age'])} (range {meta['age'].min():.1f}–{meta['age'].max():.1f}); male {100*(meta['sex']=='M').mean():.1f} %.",
             f"- Flags: flat-ROI exclusion (> {int(100*thr)} %): {int(meta['flag_excluded_flat'].sum())}; short (< {cfg['qc']['min_timepoints']} TP): "
             f"{int(meta['flag_short'].sum())}; mean FD > {cfg['qc']['max_mean_fd_mm']} mm: {int(meta['flag_motion'].sum())}.",
             "", site.to_markdown(index=False)]
    (out / f"{tag}_qc_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
