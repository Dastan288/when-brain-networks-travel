#!/usr/bin/env python
"""E6 — two resampling analyses that the single-split, subject-level bootstrap of E1/E2 cannot give.

(a) Repeated site-mixed cross-validation. The optimism of pooling sites into random folds was
    estimated from ONE stratified 10-fold run in E1; with `--repeats 20` it is estimated from 20
    independent shuffles (seeds seed..seed+19), so the reported gap cannot be an artefact of one
    lucky split. Reported: mean, SD and range of the pooled out-of-fold balanced accuracy.

(b) Site-level uncertainty for the leave-one-site-out diagonal. Subject-level bootstrap treats
    participants as exchangeable and therefore estimates uncertainty CONDITIONAL on the sites that
    were held out; it says nothing about the population of possible acquisition sites. Two
    site-aware summaries are added from the saved out-of-fold predictions: the macro-average of
    per-site balanced accuracy, and a cluster bootstrap that resamples SITES (with replacement)
    rather than participants.

Usage: python src/run_e6_resampling.py [--views abide adhd200 ucla] [--models lr svm] [--repeats 20]
Outputs: results/e6/{e6_repeated_cv.csv, e6_site_uncertainty.csv, e6_report.md}
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PROJECT_ROOT, load_config, set_seed  # noqa: E402
from src.evaluate import compute_metrics  # noqa: E402
from src.models import decision_scores, demographics_matrix, make_model  # noqa: E402
from src.protocols import load_features, random_kfold  # noqa: E402


def repeated_cv(X, y, model_name, seed, repeats, n_jobs, k=10) -> list[dict]:
    out = []
    for r in range(repeats):
        s = seed + r
        pred, score = np.full(len(y), -1), np.full(len(y), np.nan)
        for _, tr, te in random_kfold(y, k, s):
            m = make_model(model_name, seed=s, n_jobs=n_jobs)
            m.fit(X[tr], y[tr])
            pred[te], score[te] = m.predict(X[te]), decision_scores(m, X[te])
        met = compute_metrics(y, pred, score)
        out.append({"repeat": r, "cv_seed": s, **met})
    return out


def site_uncertainty(oof: pd.DataFrame, n_boot: int, seed: int) -> dict:
    """Macro-average over sites and a cluster (site-level) bootstrap of pooled balanced accuracy."""
    y, pred, score, site = (oof["y"].to_numpy(), oof["pred"].to_numpy(),
                            oof["score"].to_numpy(), oof["site"].astype(str).to_numpy())
    sites = np.unique(site)
    per = {s: compute_metrics(y[site == s], pred[site == s], score[site == s])["balanced_accuracy"]
           for s in sites if len(np.unique(y[site == s])) == 2}
    vals = np.array(list(per.values()))
    rng = np.random.default_rng(seed)
    pooled, macro = [], []
    for _ in range(n_boot):
        draw = rng.choice(sites, size=len(sites), replace=True)
        idx = np.concatenate([np.where(site == s)[0] for s in draw])
        if len(np.unique(y[idx])) == 2:
            pooled.append(compute_metrics(y[idx], pred[idx], score[idx])["balanced_accuracy"])
        keep = [per[s] for s in draw if s in per]
        if keep:
            macro.append(float(np.mean(keep)))
    q = lambda a, p: float(np.percentile(a, p)) if len(a) else np.nan  # noqa: E731
    return {"n_sites": len(sites), "n_sites_two_class": len(per),
            "pooled_bacc": compute_metrics(y, pred, score)["balanced_accuracy"],
            "site_cluster_ci_low": q(pooled, 2.5), "site_cluster_ci_high": q(pooled, 97.5),
            "macro_bacc": float(vals.mean()), "macro_sd": float(vals.std(ddof=1)) if len(vals) > 1 else np.nan,
            "macro_min": float(vals.min()), "macro_max": float(vals.max()),
            "macro_ci_low": q(macro, 2.5), "macro_ci_high": q(macro, 97.5)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--views", nargs="+", default=["abide", "adhd200", "ucla"])
    ap.add_argument("--models", nargs="+", default=["lr", "svm"])
    ap.add_argument("--repeats", type=int, default=20)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-jobs", type=int, default=2)
    ap.add_argument("--variant", default=None)
    ap.add_argument("--skip-cv", action="store_true")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    seed = cfg["seed"]
    set_seed(seed)
    variant = args.variant or cfg["atlas"]["primary"]
    feat_dir = PROJECT_ROOT / cfg["paths"]["results"] / "features"
    e2 = PROJECT_ROOT / cfg["paths"]["results"] / "e2"
    out = PROJECT_ROOT / cfg["paths"]["results"] / "e6"
    out.mkdir(parents=True, exist_ok=True)

    # ---- (a) repeated site-mixed CV
    rows = []
    if args.resume and (out / "e6_repeated_cv.csv").exists():
        rows = pd.read_csv(out / "e6_repeated_cv.csv").to_dict("records")
    done = {(r["view"], r["model"]) for r in rows}
    if not args.skip_cv:
        for v in args.views:
            F = load_features(feat_dir / f"{v}_{variant}.npz")
            X, y = F["X"].astype(np.float32), F["y"].astype(int)
            demo = demographics_matrix(F["age"], F["sex"])
            for m in args.models + ["agesex_lr"]:
                if (v, m) in done:
                    continue
                t0 = time.time()
                res = repeated_cv(demo if m == "agesex_lr" else X, y, m, seed, args.repeats, args.n_jobs)
                for r in res:
                    rows.append({"view": v, "model": m, "variant": variant, "n": len(y), **r})
                b = np.array([r["balanced_accuracy"] for r in res])
                print(f"[E6a] {v:9s} {m:9s} repeated 10-fold bAcc = {b.mean():.3f} ± {b.std(ddof=1):.3f} "
                      f"(min {b.min():.3f}, max {b.max():.3f}, {args.repeats} repeats, {time.time()-t0:.0f}s)", flush=True)
                pd.DataFrame(rows).to_csv(out / "e6_repeated_cv.csv", index=False)
    cv = pd.DataFrame(rows)

    # ---- (b) site-level uncertainty on the leave-one-site-out diagonal
    site_rows = []
    for v in args.views:
        for m in args.models + ["agesex_lr"]:
            f = e2 / f"oof_{v}_to_{v}_none_{m}.csv"
            if not f.exists():
                continue
            oof = pd.read_csv(f)
            if oof["site"].nunique() < 2:
                continue
            d = site_uncertainty(oof, args.n_boot, seed)
            site_rows.append({"view": v, "model": m, **d})
            print(f"[E6b] {v:9s} {m:9s} pooled {d['pooled_bacc']:.3f} "
                  f"[site-cluster {d['site_cluster_ci_low']:.3f}, {d['site_cluster_ci_high']:.3f}]  "
                  f"macro {d['macro_bacc']:.3f} [{d['macro_ci_low']:.3f}, {d['macro_ci_high']:.3f}] "
                  f"(sites {d['n_sites_two_class']}/{d['n_sites']})", flush=True)
    su = pd.DataFrame(site_rows)
    su.to_csv(out / "e6_site_uncertainty.csv", index=False)

    with open(out / "e6_report.md", "w") as f:
        f.write("# E6 — repeated site-mixed CV and site-level uncertainty\n\n")
        if len(cv):
            f.write(f"## (a) Repeated stratified 10-fold pooled across sites ({args.repeats} repeats, seeds "
                    f"{seed}..{seed + args.repeats - 1})\n\n")
            g = cv.groupby(["view", "model"])["balanced_accuracy"].agg(["mean", "std", "min", "max", "count"])
            g2 = cv.groupby(["view", "model"])["auc"].agg(["mean", "std"]).rename(columns={"mean": "auc_mean", "std": "auc_sd"})
            f.write(g.join(g2).round(3).to_markdown() + "\n\n")
        if len(su):
            f.write("## (b) Leave-one-site-out diagonal: subject-level vs site-level summaries\n\n")
            f.write(su.round(3).to_markdown(index=False) + "\n\n")
            f.write("`pooled_bacc` = balanced accuracy of the pooled out-of-fold predictions (the headline number, "
                    "with a subject-level bootstrap CI in Table 2); `site_cluster_*` = percentile CI from resampling "
                    "SITES with replacement; `macro_*` = mean of per-site balanced accuracies (sites with both classes "
                    "only) with a site-level bootstrap CI.\n")
    print(f"[E6] -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
