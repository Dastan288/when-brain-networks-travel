#!/usr/bin/env python
"""E5 — is there predictive information in the connectome that age and sex do not already carry?

Beating an age+sex baseline does not prove it: functional connectivity itself encodes age and sex,
so a connectome classifier can win while using only demographic information encoded in the edges.
Two additional, stricter comparisons are computed here, all with training-only fitting:

  conn          connectome features (reference, same as E1/E2)
  agesex        age + sex only (control)
  conn+agesex   connectome features with age and sex appended  -> incremental value over demographics
  conn_resid    every edge residualized on age + sex with coefficients estimated on the TRAINING set
                only (X = b0 + b1*age + b2*sex + e; the model is trained on e)  -> demographic-free features

Reported: absolute metrics for all four, and paired subject-level bootstrap differences on identical
held-out participants: (conn - agesex), (conn+agesex - agesex), (conn_resid - agesex),
(conn+agesex - conn) -- the incremental value of demographics on top of the connectome -- and (conn_resid - conn).
The claim "the connectome adds information beyond age and sex" is supported only when the interval of
(conn+agesex - agesex) excludes zero and conn_resid stays above chance.

Usage: python src/run_e5_demographics.py [--views abide adhd200 ucla ucla-adhd] [--pairs "abide>ucla" ...]
Outputs: results/e5/{e5_summary.csv, e5_deltas.csv, e5_report.md, oof_*.csv}
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
from src.evaluate import bh_fdr, bootstrap_metrics, fmt_ci, paired_bootstrap_delta  # noqa: E402
from src.models import decision_scores, demographics_matrix, make_model  # noqa: E402
from src.protocols import leave_one_site_out, load_features, random_kfold  # noqa: E402

VARIANTS = ["conn", "agesex", "conn+agesex", "conn_resid"]


def load_view(feat_dir: Path, tag: str, variant: str) -> dict:
    """X kept in float32, exactly as in E1/E2, so absolute numbers are directly comparable."""
    F = load_features(feat_dir / f"{tag}_{variant}.npz")
    return {"tag": tag, "X": F["X"].astype(np.float32), "y": F["y"].astype(int), "site": F["site"].astype(str),
            "demo": demographics_matrix(F["age"], F["sex"]), "id": F["subject_id"].astype(str),
            "n_sites": int(len(np.unique(F["site"])))}


def design(demo: np.ndarray) -> np.ndarray:
    """[1, age, sex] design matrix for the per-edge demographic model."""
    return np.column_stack([np.ones(len(demo)), demo])


def residualize(X_tr: np.ndarray, demo_tr: np.ndarray, X_te: np.ndarray, demo_te: np.ndarray):
    """Remove the linear age+sex component from every edge; coefficients from the TRAINING set only."""
    D_tr = design(demo_tr)
    B, *_ = np.linalg.lstsq(D_tr, X_tr.astype(np.float64), rcond=None)      # (3, n_edges), double precision
    return (X_tr - (D_tr @ B).astype(X_tr.dtype), X_te - (design(demo_te) @ B).astype(X_te.dtype))


def features(kind: str, view: dict, tr: np.ndarray, te: np.ndarray):
    X, demo = view["X"], view["demo"]
    if kind == "conn":
        return X[tr], X[te]
    if kind == "agesex":
        return demo[tr], demo[te]
    if kind == "conn+agesex":
        return np.hstack([X[tr], demo[tr]]), np.hstack([X[te], demo[te]])
    if kind == "conn_resid":
        return residualize(X[tr], demo[tr], X[te], demo[te])
    raise KeyError(kind)


def features_pair(kind: str, src: dict, tgt: dict):
    n_s, n_t = len(src["y"]), len(tgt["y"])
    joint = {"X": np.vstack([src["X"], tgt["X"]]), "demo": np.vstack([src["demo"], tgt["demo"]])}
    return features(kind, joint, np.arange(n_s), np.arange(n_s, n_s + n_t))


def fit_predict(model_name, Xs, ys, Xt, seed, n_jobs):
    m = make_model(model_name, seed=seed, n_jobs=n_jobs)
    m.fit(Xs, ys)
    return m.predict(Xt), decision_scores(m, Xt)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--views", nargs="+", default=["abide", "adhd200", "ucla", "ucla-adhd"])
    ap.add_argument("--pairs", nargs="+", default=["abide>ucla", "abide>adhd200", "adhd200>ucla-adhd", "ucla-adhd>adhd200"])
    ap.add_argument("--model", default="lr")
    ap.add_argument("--variant", default=None)
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--n-jobs", type=int, default=2)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    seed = cfg["seed"]
    set_seed(seed)
    variant = args.variant or cfg["atlas"]["primary"]
    feat_dir = PROJECT_ROOT / cfg["paths"]["results"] / "features"
    out = PROJECT_ROOT / cfg["paths"]["results"] / "e5"
    out.mkdir(parents=True, exist_ok=True)
    views = {v: load_view(feat_dir, v, variant) for v in args.views}
    pairs = [tuple(p.split(">")) for p in args.pairs]

    rows, preds = [], {}
    if args.resume and (out / "e5_summary.csv").exists():
        rows = pd.read_csv(out / "e5_summary.csv").to_dict("records")
        for r in rows:
            f = out / f"oof_{r['source']}_to_{r['target']}_{r['features']}.csv"
            if f.exists():
                o = pd.read_csv(f)
                preds[f"{r['source']}>{r['target']}|{r['features']}"] = (o["y"].to_numpy(), o["pred"].to_numpy(), o["score"].to_numpy())
        print(f"[E5] resume: {len(rows)} rows")
    done = {f"{r['source']}>{r['target']}|{r['features']}" for r in rows}

    jobs = [(v, v) for v in views] + [p for p in pairs if p[0] in views and p[1] in views]
    for s_tag, t_tag in jobs:
        src, tgt = views[s_tag], views[t_tag]
        for kind in VARIANTS:
            key = f"{s_tag}>{t_tag}|{kind}"
            if key in done:
                continue
            t0 = time.time()
            if s_tag == t_tag:
                multi = src["n_sites"] >= 2
                splits = list(leave_one_site_out(src["site"])) if multi else list(random_kfold(src["y"], 10, seed))
                y = src["y"]
                pred, score = np.full(len(y), -1), np.full(len(y), np.nan)
                for _, tr, te in splits:
                    Xs, Xt = features(kind, src, tr, te)
                    pred[te], score[te] = fit_predict(args.model, Xs, y[tr], Xt, seed, args.n_jobs)
                proto = "losite" if multi else "random10_single_site"
                sites = src["site"]
            else:
                Xs, Xt = features_pair(kind, src, tgt)
                y = tgt["y"]
                pred, score = fit_predict(args.model, Xs, src["y"], Xt, seed, args.n_jobs)
                proto, sites = "cross_dataset", tgt["site"]
            met = bootstrap_metrics(y, pred, score, n_boot=args.n_boot, seed=seed)
            rows.append({"variant": variant, "source": s_tag, "target": t_tag, "features": kind, "model": args.model,
                         "protocol": proto, "n_source": len(src["y"]), "n_target": len(tgt["y"]), **met,
                         "seconds": round(time.time() - t0, 1)})
            preds[key] = (y, pred, score)
            pd.DataFrame({"subject_id": tgt["id"], "site": sites, "y": y, "pred": pred, "score": score}) \
                .to_csv(out / f"oof_{s_tag}_to_{t_tag}_{kind}.csv", index=False)
            print(f"[E5] {s_tag:9s}->{t_tag:9s} {kind:12s} bAcc={fmt_ci(met, 'balanced_accuracy')} "
                  f"AUC={fmt_ci(met, 'auc')} ({round(time.time() - t0, 1)}s)", flush=True)
            pd.DataFrame(rows).to_csv(out / "e5_summary.csv", index=False)

    # ---- paired deltas on identical held-out participants
    comparisons = [("agesex", "conn"), ("agesex", "conn+agesex"), ("agesex", "conn_resid"),
                   ("conn", "conn+agesex"), ("conn", "conn_resid")]
    deltas = []
    for s_tag, t_tag in jobs:
        for a, b in comparisons:
            ka, kb = f"{s_tag}>{t_tag}|{a}", f"{s_tag}>{t_tag}|{b}"
            if ka not in preds or kb not in preds:
                continue
            ya, pa, sa = preds[ka]
            yb, pb, sb = preds[kb]
            assert np.array_equal(ya, yb)
            for metric in ("balanced_accuracy", "auc"):
                d = paired_bootstrap_delta(ya, pa, sa, pb, sb, metric=metric, n_boot=args.n_boot, seed=seed)
                deltas.append({"source": s_tag, "target": t_tag, "baseline": a, "model_features": b,
                               "metric": metric, **d})
    dd = pd.DataFrame(deltas)
    if len(dd):
        for metric, g in dd.groupby("metric"):
            dd.loc[g.index, "p_fdr"] = bh_fdr(g["p_boot"].to_numpy())
        dd.to_csv(out / "e5_deltas.csv", index=False)

    summary = pd.DataFrame(rows)
    with open(out / "e5_report.md", "w") as f:
        f.write("# E5 — connectome information beyond age and sex (aal90, logistic regression)\n\n")
        f.write("`conn+agesex` = connectome features with age and sex appended; `conn_resid` = every edge "
                "residualized on age and sex with coefficients fitted on the training set only. "
                "Diagonal = leave-one-site-out; off-diagonal = train on all of source, test on all of target. "
                "Bootstrap: 1000 subject-level resamples; paired deltas on identical held-out participants; "
                "p-values are two-sided bootstrap p-values, BH-corrected within each metric.\n\n")
        f.write("## Balanced accuracy by feature set\n\n")
        piv = summary.pivot_table(index=["source", "target"], columns="features", values="balanced_accuracy")
        f.write(piv.round(3).to_markdown() + "\n\n")
        f.write("## Full metrics\n\n")
        cols = ["source", "target", "features", "protocol", "balanced_accuracy", "balanced_accuracy_ci_low",
                "balanced_accuracy_ci_high", "auc", "auc_ci_low", "auc_ci_high"]
        f.write(summary[cols].round(3).to_markdown(index=False) + "\n\n")
        if len(dd):
            f.write("## Paired differences (model minus baseline)\n\n")
            f.write(dd.round(4).to_markdown(index=False) + "\n")
    print(f"[E5] {len(summary)} rows, {len(dd)} deltas -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
