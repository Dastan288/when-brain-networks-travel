#!/usr/bin/env python
"""E3b — two post-hoc summaries computed from the saved E2 predictions (no new model fitting).

1. Connectome model minus demographics-only control (age + sex logistic regression) on identical
   held-out subjects, paired subject-level bootstrap (balanced accuracy and AUC). A connectome
   classifier only "carries signal beyond demographics" when this delta's CI excludes 0.
2. Pooled-vs-averaged diagonal: the headline leave-one-site-out number pools out-of-fold
   predictions across held-out sites (fixed a priori). When held-out sites have very different
   class priors (ADHD-200: WashU 0 % patients, Pittsburgh 4 %, NYU 57 %), the pooled balanced
   accuracy can differ from the mean of per-site balanced accuracies, so both are reported.

Usage: python src/run_e3b_controls.py [--out results/e2] [--n-boot 1000]
Outputs: <out>/e3b_control_deltas.csv, <out>/e3b_diag_pooled_vs_persite.csv, <out>/e3b_report.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PROJECT_ROOT, load_config, set_seed  # noqa: E402
from src.evaluate import bh_fdr, compute_metrics, paired_bootstrap_delta  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--models", nargs="+", default=["lr", "svm", "rf"])
    args = ap.parse_args()
    cfg = load_config()
    set_seed(cfg["seed"])
    out = Path(args.out) if args.out else PROJECT_ROOT / cfg["paths"]["results"] / "e2"
    summ = pd.read_csv(out / "e2_summary.csv")
    summ = summ[summ["status"] == "ok"]

    # ---- 1. connectome minus age/sex control (raw features, harmonization == none / none@random10)
    rows = []
    for (s, t, h), g in summ.groupby(["source", "target", "harmonization"]):
        if not h.startswith("none"):
            continue
        ctrl = out / f"oof_{s}_to_{t}_{h}_agesex_lr.csv"
        if not ctrl.exists():
            continue
        c = pd.read_csv(ctrl)
        for m in args.models:
            f = out / f"oof_{s}_to_{t}_{h}_{m}.csv"
            if not f.exists():
                continue
            o = pd.read_csv(f)
            assert (o["subject_id"].to_numpy() == c["subject_id"].to_numpy()).all(), (s, t, m)
            y = o["y"].to_numpy()
            for metric in ("balanced_accuracy", "auc"):
                d = paired_bootstrap_delta(y, c["pred"].to_numpy(), c["score"].to_numpy(),
                                           o["pred"].to_numpy(), o["score"].to_numpy(),
                                           metric=metric, n_boot=args.n_boot, seed=cfg["seed"])
                rows.append({"source": s, "target": t, "harmonization": h, "model": m, "metric": metric,
                             "connectome": compute_metrics(y, o["pred"], o["score"])[metric],
                             "agesex": compute_metrics(y, c["pred"], c["score"])[metric], **d})
    ctrl_df = pd.DataFrame(rows)
    if len(ctrl_df):   # BH across all cells of the same metric (many paired comparisons)
        for metric, g in ctrl_df.groupby("metric"):
            ctrl_df.loc[g.index, "p_fdr"] = bh_fdr(g["p_boot"].to_numpy())
    ctrl_df.to_csv(out / "e3b_control_deltas.csv", index=False)

    # ---- 2. pooled vs per-site averaged diagonal
    ps = pd.read_csv(out / "e2_per_site.csv")
    diag = ps[(ps["source"] == ps["target"]) & (ps["protocol"] == "losite")]
    rows = []
    for (v, h, m), g in diag.groupby(["source", "harmonization", "model"]):
        pooled = summ[(summ["source"] == v) & (summ["target"] == v) & (summ["harmonization"] == h) & (summ["model"] == m)]
        if len(pooled) == 0:
            continue
        valid = g.dropna(subset=["balanced_accuracy"])
        rows.append({"view": v, "harmonization": h, "model": m, "n_sites": len(g), "n_sites_two_class": len(valid),
                     "pooled_bacc": float(pooled["balanced_accuracy"].iloc[0]),
                     "persite_mean_bacc": float(valid["balanced_accuracy"].mean()),
                     "persite_median_bacc": float(valid["balanced_accuracy"].median()),
                     "persite_n_weighted_bacc": float(np.average(valid["balanced_accuracy"], weights=valid["n"])),
                     "pooled_auc": float(pooled["auc"].iloc[0]),
                     "persite_mean_auc": float(valid["auc"].mean()),
                     "sites_single_class": ", ".join(g[g["balanced_accuracy"].isna()]["site"].astype(str))})
    diag_df = pd.DataFrame(rows)
    diag_df.to_csv(out / "e3b_diag_pooled_vs_persite.csv", index=False)

    with open(out / "e3b_report.md", "w") as f:
        f.write("# E3b — connectome vs demographics control; pooled vs per-site diagonal\n\n")
        f.write("## Connectome model minus age+sex control (paired bootstrap on identical held-out subjects)\n\n")
        f.write(ctrl_df.round(3).to_markdown(index=False) + "\n\n")
        f.write("## Leave-one-site-out diagonal: pooled out-of-fold vs per-site averages\n\n")
        f.write(diag_df.round(3).to_markdown(index=False) + "\n")
    print(f"[E3b] {len(ctrl_df)} control deltas, {len(diag_df)} diagonal rows -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
