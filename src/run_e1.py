#!/usr/bin/env python
"""E1 — within-dataset leave-one-site-out baseline (+ one labelled random-CV run).

Grid (fixed a priori; config/config.yaml):
    feature variants : aal90 (primary), aal116, cc200 (robustness)
    samples          : primary (all subjects after coverage exclusion), qc_pass (rater-QC sensitivity)
    models           : lr, svm, rf  + control agesex_lr (demographics only)
    protocols        : losite (headline)  |  random10 (INFLATED — site leakage demo, primary variant only)

Outputs (results/e1/<dataset>/):
    e1_summary.csv        one row per (variant, sample, model, protocol) with pooled metrics + 95% bootstrap CI
    e1_per_site.csv       per held-out site metrics for every losite run
    oof_<...>.csv         out-of-fold predictions/scores per subject
    weights_<...>.npz     per-fold linear weights (E4 interpretation), primary sample only
    e1_report.md          human-readable summary
Usage: python src/run_e1.py --dataset abide|abide-filt_global [--variants aal90] [--models lr svm] [--n-boot 1000]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PROJECT_ROOT, load_config, set_seed  # noqa: E402
from src.evaluate import bootstrap_metrics, compute_metrics, fmt_ci  # noqa: E402
from src.models import CONTROL_NAMES, MODEL_NAMES, decision_scores, demographics_matrix, linear_weights, make_model  # noqa: E402
from src.protocols import leave_one_site_out, load_features, random_kfold  # noqa: E402


def run_splits(X, y, splits, model_name, seed, n_jobs, keep_weights=False):
    n = len(y)
    pred = np.full(n, -1, dtype=int)
    score = np.full(n, np.nan)
    fold_of = np.empty(n, dtype=object)
    weights = []
    for name, tr, te in splits:
        m = make_model(model_name, seed=seed, n_jobs=n_jobs)
        m.fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
        score[te] = decision_scores(m, X[te])
        fold_of[te] = name
        if keep_weights:
            w = linear_weights(m)
            if w is not None:
                weights.append(w.astype(np.float32))
    assert (pred >= 0).all(), "every subject must be predicted exactly once"
    return pred, score, fold_of, (np.vstack(weights) if weights else None)


def per_site_table(y, pred, score, site, fold_of) -> pd.DataFrame:
    rows = []
    for s in sorted(np.unique(site)):
        m = site == s
        d = compute_metrics(y[m], pred[m], score[m])
        d.update({"site": s, "n": int(m.sum()), "n_patients": int(y[m].sum())})
        rows.append(d)
    return pd.DataFrame(rows)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", default="abide")
    p.add_argument("--variants", nargs="+", default=None)
    p.add_argument("--models", nargs="+", default=None)
    p.add_argument("--samples", nargs="+", default=["primary", "qc_pass"])
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--n-jobs", type=int, default=2)
    p.add_argument("--skip-random", action="store_true")
    p.add_argument("--resume", action="store_true", help="keep rows of an existing e1_summary.csv and skip finished configs")
    args = p.parse_args()

    cfg = load_config()
    seed = cfg["seed"]
    set_seed(seed)
    variants = args.variants or cfg["atlas"]["variants"]
    models = args.models or (MODEL_NAMES + CONTROL_NAMES)
    out = PROJECT_ROOT / cfg["paths"]["results"] / "e1" / args.dataset
    out.mkdir(parents=True, exist_ok=True)
    feat_dir = PROJECT_ROOT / cfg["paths"]["results"] / "features"

    summary_rows, per_site_rows, done_tags = [], [], set()
    if args.resume and (out / "e1_summary.csv").exists():
        prev = pd.read_csv(out / "e1_summary.csv")
        summary_rows = prev.to_dict("records")
        done_tags = {f"{r['dataset']}_{r['variant']}_{r['sample']}_{r['protocol']}_{r['model']}" for r in summary_rows}
        if (out / "e1_per_site.csv").exists():
            per_site_rows = [pd.read_csv(out / "e1_per_site.csv")]
        print(f"[E1] resume: {len(done_tags)} configs already done")
    t_all = time.time()
    for variant in variants:
        F = load_features(feat_dir / f"{args.dataset}_{variant}.npz")
        for sample in args.samples:
            mask = np.ones(len(F["y"]), dtype=bool) if sample == "primary" else F["rater_qc_pass"].astype(bool)
            X, y, site = F["X"][mask], F["y"][mask].astype(int), F["site"][mask].astype(str)
            demo = demographics_matrix(F["age"][mask], F["sex"][mask])
            protocols = [("losite", list(leave_one_site_out(site)))]
            if not args.skip_random and variant == cfg["atlas"]["primary"] and sample == "primary":
                protocols.append(("random10_INFLATED", list(random_kfold(y, 10, seed))))
            for proto, splits in protocols:
                for model_name in models:
                    if model_name in CONTROL_NAMES and proto != "losite":
                        continue
                    tag = f"{args.dataset}_{variant}_{sample}_{proto}_{model_name}"
                    if tag in done_tags:
                        continue
                    Xm = demo if model_name in CONTROL_NAMES else X
                    t0 = time.time()
                    keep_w = (proto == "losite" and sample == "primary" and model_name in ("lr", "svm"))
                    pred, score, fold_of, W = run_splits(Xm, y, splits, model_name, seed, args.n_jobs, keep_w)
                    met = bootstrap_metrics(y, pred, score, n_boot=args.n_boot, seed=seed)
                    row = {"dataset": args.dataset, "variant": variant, "sample": sample, "protocol": proto,
                           "model": model_name, "n_sites": int(len(np.unique(site))), **met,
                           "seconds": round(time.time() - t0, 1)}
                    pd.DataFrame({"subject_id": F["subject_id"][mask], "site": site, "y": y, "pred": pred,
                                  "score": score, "fold": fold_of}).to_csv(out / f"oof_{tag}.csv", index=False)
                    if proto == "losite":
                        ps = per_site_table(y, pred, score, site, fold_of)
                        ps.insert(0, "model", model_name); ps.insert(0, "protocol", proto)
                        ps.insert(0, "sample", sample); ps.insert(0, "variant", variant); ps.insert(0, "dataset", args.dataset)
                        per_site_rows.append(ps)
                        row["site_bacc_median"] = float(ps["balanced_accuracy"].median())
                        row["site_bacc_iqr_low"] = float(ps["balanced_accuracy"].quantile(0.25))
                        row["site_bacc_iqr_high"] = float(ps["balanced_accuracy"].quantile(0.75))
                        row["site_bacc_min"] = float(ps["balanced_accuracy"].min())
                        row["site_bacc_max"] = float(ps["balanced_accuracy"].max())
                    if W is not None:
                        np.savez_compressed(out / f"weights_{tag}.npz", W=W, sites=np.array([s for s, _, _ in splits]),
                                            edge_i=F["edge_i"], edge_j=F["edge_j"], roi_labels=F["roi_labels"])
                    summary_rows.append(row)
                    print(f"[E1] {tag:55s} bAcc={fmt_ci(met, 'balanced_accuracy')}  "
                          f"AUC={fmt_ci(met, 'auc') if 'auc' in met else 'n/a'}  ({row['seconds']}s)", flush=True)
                    pd.DataFrame(summary_rows).to_csv(out / "e1_summary.csv", index=False)
                    if per_site_rows:
                        pd.concat(per_site_rows).to_csv(out / "e1_per_site.csv", index=False)

    summary = pd.DataFrame(summary_rows)
    write_report(summary, pd.concat(per_site_rows) if per_site_rows else None, out, cfg, args)
    print(f"[E1] done in {(time.time()-t_all)/60:.1f} min -> {out}")
    return 0


def write_report(summary: pd.DataFrame, per_site: pd.DataFrame | None, out: Path, cfg: dict, args) -> None:
    def row_fmt(r):
        auc = fmt_ci(r, "auc") if not np.isnan(r.get("auc", np.nan)) else "–"
        spread = (f"{r['site_bacc_median']:.3f} [{r['site_bacc_iqr_low']:.3f}–{r['site_bacc_iqr_high']:.3f}] "
                  f"(min {r['site_bacc_min']:.2f}, max {r['site_bacc_max']:.2f})") if r["protocol"] == "losite" else "–"
        return f"| {r['variant']} | {r['sample']} | {r['protocol']} | {r['model']} | {int(r['n'])} | " \
               f"{fmt_ci(r, 'balanced_accuracy')} | {auc} | {fmt_ci(r, 'accuracy')} | {spread} |"

    lines = [f"# E1 — within-{args.dataset.upper()} leave-one-site-out baseline", "",
             f"Seed {cfg['seed']}; bootstrap {args.n_boot} subject-level resamples; 95% percentile CI. "
             f"Models with a priori hyperparameters (LR C=1, linear SVM C=1, RF 500 trees), StandardScaler fitted on training sites only.",
             "", "| variant | sample | protocol | model | n | balanced acc. [95% CI] | AUC [95% CI] | accuracy [95% CI] | per-site bAcc median [IQR] |",
             "|---|---|---|---|---|---|---|---|---|"]
    for _, r in summary.iterrows():
        lines.append(row_fmt(r))
    lines += ["", "Notes:", "",
              "- `random10_INFLATED` = stratified 10-fold CV pooled across sites (site leakage); shown once for contrast, never as a headline number.",
              "- `agesex_lr` = control model on age + sex only; connectome models must beat it to claim signal beyond demographics.",
              "- `qc_pass` = rater-QC-passed subset (nilearn `quality_checked=True` criterion), sensitivity analysis."]
    if per_site is not None:
        prim = per_site[(per_site["variant"] == cfg["atlas"]["primary"]) & (per_site["sample"] == "primary") & (per_site["model"] == "lr")]
        if len(prim):
            lines += ["", f"## Per-site balanced accuracy — {cfg['atlas']['primary']}, primary sample, LR (leave-one-site-out)", "",
                      prim[["site", "n", "n_patients", "balanced_accuracy", "auc", "sensitivity", "specificity"]]
                      .round(3).to_markdown(index=False)]
    (out / "e1_report.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
