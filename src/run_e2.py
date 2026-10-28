#!/usr/bin/env python
"""E2 + E3 — cross-dataset transfer matrix, raw and with ComBat harmonization.

Protocol (fixed a priori):
  * Views (feature tags): abide (ASD vs TD), adhd200 (ADHD vs TDC), ucla (any patient vs control),
    ucla-adhd (UCLA ADHD vs control = diagnosis-matched partner of adhd200).
  * Off-diagonal: train on 100 % of the source view, test on 100 % of the target view. The whole
    pipeline (ComBat, scaler, classifier) is fitted on the source only.
  * Diagonal: leave-one-site-out inside the view (single-site views: stratified 10-fold, labelled).
  * Harmonization modes (E3):
      none        StandardScaler on training data only
      combat_ref  ComBat(batch = training sites, covariates age+sex) fitted on the source; held-out
                  data standardized with the source reference only (no held-out statistics)
      combat_new  as combat_ref, plus the held-out site(s)/dataset adjusted as new batch(es) from
                  their own UNLABELED features (usual "harmonize a new site" recipe; transductive)
    Single-site sources cannot fit ComBat -> recorded as NA.
  * Models: lr (primary), svm, rf; control agesex_lr (demographics only, no harmonization).
  * Every metric: subject-level bootstrap 95 % CI on the held-out subjects; ComBat-vs-raw deltas
    with paired bootstrap CI.

Outputs (results/e2/): e2_summary.csv (long format), transfer_<metric>_<model>_<harm>.csv (matrices),
e2_per_site.csv, e3_deltas.csv, oof_*.csv (predictions), e2_report.md
Usage: python src/run_e2.py [--variant aal90] [--views abide adhd200 ucla ucla-adhd] [--models lr svm rf agesex_lr]
"""

from __future__ import annotations

import argparse
import itertools
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.combat import ComBat, covariate_matrix  # noqa: E402
from src.common import PROJECT_ROOT, load_config, set_seed  # noqa: E402
from src.evaluate import bh_fdr, bootstrap_metrics, compute_metrics, fmt_ci, paired_bootstrap_delta  # noqa: E402
from src.models import CONTROL_NAMES, decision_scores, demographics_matrix, make_model  # noqa: E402
from src.protocols import leave_one_site_out, load_features, random_kfold  # noqa: E402

HARMS = ["none", "combat_ref", "combat_new"]


def load_view(feat_dir: Path, tag: str, variant: str) -> dict:
    F = load_features(feat_dir / f"{tag}_{variant}.npz")
    return {"tag": tag, "X": F["X"].astype(np.float32), "y": F["y"].astype(int), "site": F["site"].astype(str),
            "cov": covariate_matrix(F["age"], F["sex"]), "demo": demographics_matrix(F["age"], F["sex"]),
            "id": F["subject_id"].astype(str), "roi": F["roi_labels"].astype(str), "n_sites": int(len(np.unique(F["site"])))}


def harmonize(harm: str, Xs, site_s, cov_s, Xt, site_t, cov_t):
    """Return (Xs_h, Xt_h) or None when the mode is not applicable (single-site source)."""
    if harm == "none":
        return Xs, Xt
    if len(np.unique(site_s)) < 2:
        return None
    cb = ComBat().fit(Xs, site_s, cov_s)
    Xs_h = cb.transform(Xs, site_s, cov_s)
    if harm == "combat_ref":
        Xt_h = cb.reference_only(Xt, cov_t)
    elif harm == "combat_new":
        Xt_h = cb.transform_new_batch(Xt, cov_t, batch=site_t)
    else:
        raise KeyError(harm)
    return Xs_h, Xt_h


def fit_predict(model_name, Xs, ys, Xt, seed, n_jobs):
    m = make_model(model_name, seed=seed, n_jobs=n_jobs)
    m.fit(Xs, ys)
    return m.predict(Xt), decision_scores(m, Xt)


def evaluate_pair(src: dict, tgt: dict, harm: str, model_name: str, seed: int, n_jobs: int, n_boot: int):
    """Off-diagonal: source -> target. Returns (row, pred, score, per_site_df) or None."""
    if model_name in CONTROL_NAMES:
        if harm != "none":
            return None
        pred, score = fit_predict(model_name, src["demo"], src["y"], tgt["demo"], seed, n_jobs)
    else:
        h = harmonize(harm, src["X"], src["site"], src["cov"], tgt["X"], tgt["site"], tgt["cov"])
        if h is None:
            return None
        pred, score = fit_predict(model_name, h[0], src["y"], h[1], seed, n_jobs)
    met = bootstrap_metrics(tgt["y"], pred, score, n_boot=n_boot, seed=seed)
    return met, pred, score


def evaluate_within(view: dict, harm: str, model_name: str, seed: int, n_jobs: int, n_boot: int, force_random: bool = False):
    """Diagonal: leave-one-site-out (or stratified 10-fold for single-site views / when force_random)."""
    y, site = view["y"], view["site"]
    multi = view["n_sites"] >= 2 and not force_random
    if not multi and harm != "none":
        return None
    if model_name in CONTROL_NAMES and harm != "none":
        return None
    splits = list(leave_one_site_out(site)) if multi else list(random_kfold(y, 10, seed))
    pred, score = np.full(len(y), -1), np.full(len(y), np.nan)
    for _, tr, te in splits:
        if model_name in CONTROL_NAMES:
            Xs, Xt = view["demo"][tr], view["demo"][te]
        else:
            h = harmonize(harm, view["X"][tr], site[tr], view["cov"][tr], view["X"][te], site[te], view["cov"][te])
            if h is None:
                return None
            Xs, Xt = h
        p, s = fit_predict(model_name, Xs, y[tr], Xt, seed, n_jobs)
        pred[te], score[te] = p, s
    met = bootstrap_metrics(y, pred, score, n_boot=n_boot, seed=seed)
    met["protocol"] = "losite" if multi else ("random10_INFLATED" if view["n_sites"] >= 2 else "random10_single_site")
    return met, pred, score


def per_site(y, pred, score, site) -> list[dict]:
    rows = []
    for s in sorted(np.unique(site)):
        m = site == s
        if len(np.unique(y[m])) < 2:
            d = {"balanced_accuracy": np.nan, "accuracy": float((y[m] == pred[m]).mean()), "auc": np.nan}
        else:
            d = compute_metrics(y[m], pred[m], score[m])
        d.update({"site": s, "n": int(m.sum()), "n_patients": int(y[m].sum())})
        rows.append(d)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", default=None)
    ap.add_argument("--views", nargs="+", default=["abide", "adhd200", "ucla", "ucla-adhd"])
    ap.add_argument("--pairs", nargs="*", default=None, help="explicit 'src>tgt' pairs (default: all ordered pairs "
                    "among abide/adhd200/ucla + ucla-adhd<->adhd200)")
    ap.add_argument("--models", nargs="+", default=["lr", "svm", "rf", "agesex_lr"])
    ap.add_argument("--harms", nargs="+", default=HARMS)
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--n-jobs", type=int, default=2)
    ap.add_argument("--out", default=None)
    ap.add_argument("--resume", action="store_true", help="reuse rows/predictions already in <out>/e2_summary.csv")
    args = ap.parse_args()
    cfg = load_config()
    seed = cfg["seed"]
    set_seed(seed)
    variant = args.variant or cfg["atlas"]["primary"]
    feat_dir = PROJECT_ROOT / cfg["paths"]["results"] / "features"
    out = Path(args.out) if args.out else PROJECT_ROOT / cfg["paths"]["results"] / "e2"
    out.mkdir(parents=True, exist_ok=True)

    views = {v: load_view(feat_dir, v, variant) for v in args.views if (feat_dir / f"{v}_{variant}.npz").exists()}
    missing = [v for v in args.views if v not in views]
    if missing:
        print(f"[E2] views without features (skipped): {missing}")
    roi_ref = next(iter(views.values()))["roi"]
    for v in views.values():
        if not np.array_equal(v["roi"], roi_ref):
            raise RuntimeError(f"ROI label mismatch between views ({v['tag']}) — features are not comparable")
    if args.pairs:
        pairs = [tuple(p.split(">")) for p in args.pairs]
    else:
        main_views = [v for v in ("abide", "adhd200", "ucla") if v in views]
        pairs = list(itertools.permutations(main_views, 2))
        if "ucla-adhd" in views and "adhd200" in views:
            pairs += [("ucla-adhd", "adhd200"), ("adhd200", "ucla-adhd")]
    diag = [(v, v) for v in views]
    few_site = [v for v in views if views[v]["n_sites"] <= 2]   # extra labelled random-CV diagonal for these
    print(f"[E2] variant={variant} views={list(views)} pairs={len(pairs)} diag={len(diag)} harms={args.harms} models={args.models}")

    rows, site_rows, preds = [], [], {}
    if args.resume and (out / "e2_summary.csv").exists():
        prev = pd.read_csv(out / "e2_summary.csv")
        prev = prev[prev["variant"] == variant]
        rows = prev.to_dict("records")
        for r in rows:
            key = f"{r['source']}>{r['target']}|{r['harmonization']}|{r['model']}"
            f = out / f"oof_{r['source']}_to_{r['target']}_{r['harmonization']}_{r['model']}.csv"
            if r["status"] == "ok" and f.exists():
                o = pd.read_csv(f)
                preds[key] = (o["pred"].to_numpy(), o["score"].to_numpy())
        if (out / "e2_per_site.csv").exists():
            site_rows = pd.read_csv(out / "e2_per_site.csv").to_dict("records")
        print(f"[E2] resume: {len(rows)} rows, {len(preds)} prediction sets loaded")
    done_keys = {f"{r['source']}>{r['target']}|{r['harmonization']}|{r['model']}" for r in rows}
    t_all = time.time()
    jobs = [(s, t, False) for s, t in diag] + [(v, v, True) for v in few_site] + [(s, t, False) for s, t in pairs]
    for (s_tag, t_tag, force_random) in jobs:
        src, tgt = views[s_tag], views[t_tag]
        for harm in args.harms:
            for model_name in args.models:
                key_harm = harm if not force_random else f"{harm}@random10"
                if f"{s_tag}>{t_tag}|{key_harm}|{model_name}" in done_keys:
                    continue
                if force_random and harm != "none":
                    continue
                t0 = time.time()
                if s_tag == t_tag:
                    res = evaluate_within(src, harm, model_name, seed, args.n_jobs, args.n_boot, force_random=force_random)
                    proto = None if res is None else res[0].pop("protocol")
                else:
                    res = evaluate_pair(src, tgt, harm, model_name, seed, args.n_jobs, args.n_boot)
                    proto = "cross_dataset"
                base = {"variant": variant, "source": s_tag, "target": t_tag, "harmonization": key_harm, "model": model_name,
                        "protocol": proto, "n_source": len(src["y"]), "n_target": len(tgt["y"]),
                        "source_sites": src["n_sites"], "target_sites": tgt["n_sites"]}
                if res is None:
                    rows.append({**base, "status": "NA"})
                    continue
                met, pred, score = res
                rows.append({**base, "status": "ok", **met, "seconds": round(time.time() - t0, 1)})
                key = f"{s_tag}>{t_tag}|{key_harm}|{model_name}"
                preds[key] = (pred, score)
                pd.DataFrame({"subject_id": tgt["id"], "site": tgt["site"], "y": tgt["y"], "pred": pred, "score": score}) \
                    .to_csv(out / f"oof_{s_tag}_to_{t_tag}_{key_harm}_{model_name}.csv", index=False)
                for r in per_site(tgt["y"], pred, score, tgt["site"]):
                    site_rows.append({**base, **r})
                print(f"[E2] {s_tag:9s}->{t_tag:9s} {key_harm:15s} {model_name:9s} bAcc={fmt_ci(met, 'balanced_accuracy')} "
                      f"AUC={fmt_ci(met, 'auc')} ({round(time.time()-t0, 1)}s)", flush=True)
                pd.DataFrame(rows).to_csv(out / "e2_summary.csv", index=False)
                pd.DataFrame(site_rows).to_csv(out / "e2_per_site.csv", index=False)  # checkpoint for --resume

    summary = pd.DataFrame(rows)
    pd.DataFrame(site_rows).to_csv(out / "e2_per_site.csv", index=False)

    # ---- E3 deltas: ComBat vs none on identical held-out subjects
    deltas = []
    for (s_tag, t_tag) in diag + pairs:
        for model_name in args.models:
            k0 = f"{s_tag}>{t_tag}|none|{model_name}"
            if k0 not in preds:
                continue
            for harm in [h for h in args.harms if h != "none"]:
                k1 = f"{s_tag}>{t_tag}|{harm}|{model_name}"
                if k1 not in preds:
                    continue
                y = views[t_tag]["y"]
                for metric in ("balanced_accuracy", "auc"):
                    d = paired_bootstrap_delta(y, preds[k0][0], preds[k0][1], preds[k1][0], preds[k1][1],
                                               metric=metric, n_boot=args.n_boot, seed=seed)
                    deltas.append({"source": s_tag, "target": t_tag, "model": model_name, "harmonization": harm,
                                   "metric": metric, **d})
    dd = pd.DataFrame(deltas)
    if len(dd):
        # 60 paired harmonization comparisons per metric (3 classifiers x 10 evaluable cells x 2 ComBat
        # modes): Benjamini-Hochberg jointly across all cells of the same metric, so that a single
        # interval excluding zero is not read as a discovery.
        for metric, g in dd.groupby("metric"):
            dd.loc[g.index, "p_fdr"] = bh_fdr(g["p_boot"].to_numpy())
    dd.to_csv(out / "e3_deltas.csv", index=False)

    # ---- matrices
    ok = summary[(summary["status"] == "ok") & (~summary["harmonization"].astype(str).str.contains("@random10"))]
    for metric in ("balanced_accuracy", "auc"):
        for (model_name, harm), g in ok.groupby(["model", "harmonization"]):
            order = [v for v in args.views if v in views]
            M = pd.DataFrame(index=order, columns=order, dtype=object)
            for _, r in g.iterrows():
                M.loc[r["source"], r["target"]] = f"{r[metric]:.3f} [{r[metric+'_ci_low']:.3f}, {r[metric+'_ci_high']:.3f}]"
            M.index.name = "source \\ target"
            M.to_csv(out / f"transfer_{metric}_{model_name}_{harm}.csv")
    write_report(summary, pd.DataFrame(deltas), out, variant, args)
    print(f"[E2] done in {(time.time()-t_all)/60:.1f} min -> {out}")
    return 0


def write_report(summary: pd.DataFrame, deltas: pd.DataFrame, out: Path, variant: str, args) -> None:
    lines = [f"# E2/E3 — cross-dataset transfer matrix ({variant})", "",
             f"Bootstrap {args.n_boot} resamples of held-out subjects; 95 % percentile CI. Diagonal = leave-one-site-out "
             "(single-site views: stratified 10-fold, labelled). Off-diagonal = train on all of source, test on all of target.", ""]
    ok = summary[summary["status"] == "ok"]
    model_order = [m for m in ["lr", "svm", "rf", "agesex_lr"] if (ok["model"] == m).any()]
    for model_name in model_order:
        for harm in HARMS:
            g = ok[(ok["model"] == model_name) & (ok["harmonization"] == harm)]
            if not len(g):
                continue
            lines += [f"## {model_name} — {harm} (balanced accuracy)", "", "| source \\ target | " + " | ".join(args.views) + " |",
                      "|---|" + "---|" * len(args.views)]
            for s in args.views:
                cells = []
                for t in args.views:
                    r = g[(g["source"] == s) & (g["target"] == t)]
                    cells.append(fmt_ci(r.iloc[0], "balanced_accuracy") if len(r) else "NA")
                lines.append(f"| {s} | " + " | ".join(cells) + " |")
            lines.append("")
    if len(deltas):
        deltas = deltas.sort_values(["model", "source", "target", "harmonization"])
        lines += ["## E3 — ComBat minus raw (paired bootstrap, balanced accuracy)", "",
                  deltas[deltas["metric"] == "balanced_accuracy"][["source", "target", "model", "harmonization", "delta", "ci_low", "ci_high"]]
                  .round(3).to_markdown(index=False), ""]
    rnd = summary[(summary["status"] == "ok") & (summary["harmonization"].astype(str).str.contains("@random10"))]
    if len(rnd):
        lines += ["## Few-site views: stratified 10-fold diagonal (site leakage; for contrast only)", "",
                  rnd[["source", "model", "n_target", "balanced_accuracy", "balanced_accuracy_ci_low", "balanced_accuracy_ci_high", "auc"]]
                  .round(3).to_markdown(index=False), ""]
    na = summary[summary["status"] == "NA"]
    if len(na):
        lines += [f"NA cells: {len(na)} (ComBat needs >= 2 training sites; control model has no harmonization).", ""]
    (out / "e2_report.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
