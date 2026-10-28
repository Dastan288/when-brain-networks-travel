#!/usr/bin/env python
"""E4 — interpretation of the linear models: which edges carry the signal, how stable they are
across leave-one-site-out folds, and whether the same edges matter in different datasets.

Inputs: results/e1/<dataset>/weights_<dataset>_<variant>_primary_losite_lr.npz (per-fold LR weights,
standardized-feature space) and results/features/<dataset>_<variant>.npz (edge -> ROI mapping).

Analyses:
  1. Fold stability: Spearman correlation of |w| between folds (mean / min), mean pairwise Jaccard of the
     top-k edge sets, and a consensus weight (mean over folds).
  2. Top-k consensus edges with ROI names and lobes; lobe-pair count matrix (+ signed weight sums).
  3. Cross-dataset similarity: Spearman correlation between consensus weight vectors of different datasets
     (only edges shared by construction: same AAL-90 ordering) and top-k Jaccard.

Outputs (results/e4/): <dataset>_stability.csv, <dataset>_top_edges.csv, <dataset>_lobe_pairs.csv,
fig_<dataset>_lobe_pairs.png, cross_dataset_weight_similarity.csv, e4_report.md
Usage: python src/run_e4.py [--datasets abide adhd200] [--variant aal90] [--top-k 100]
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.aal import LOBES, lobe, name  # noqa: E402
from src.evaluate import bh_fdr  # noqa: E402
from src.common import PROJECT_ROOT, load_config, set_seed  # noqa: E402


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else np.nan


def load_weights(cfg: dict, dataset: str, variant: str, model: str = "lr"):
    p = PROJECT_ROOT / cfg["paths"]["results"] / "e1" / dataset / f"weights_{dataset}_{variant}_primary_losite_{model}.npz"
    if not p.exists():
        return None
    z = np.load(p)
    return {"W": z["W"].astype(np.float64), "sites": z["sites"].astype(str), "edge_i": z["edge_i"], "edge_j": z["edge_j"],
            "roi": z["roi_labels"].astype(str)}


def stability(W: np.ndarray, k: int) -> dict:
    n = W.shape[0]
    rhos, jacs = [], []
    tops = [set(np.argsort(-np.abs(W[f]))[:k]) for f in range(n)]
    for a, b in itertools.combinations(range(n), 2):
        rhos.append(spearmanr(np.abs(W[a]), np.abs(W[b])).correlation)
        jacs.append(jaccard(tops[a], tops[b]))
    return {"n_folds": n, "spearman_abs_w_mean": float(np.mean(rhos)), "spearman_abs_w_min": float(np.min(rhos)),
            f"jaccard_top{k}_mean": float(np.mean(jacs)), f"jaccard_top{k}_min": float(np.min(jacs))}


def lobe_pair_matrix(edge_i, edge_j, roi, sel_idx, weights) -> tuple[pd.DataFrame, pd.DataFrame]:
    lobes_present = [l for l in LOBES if any(lobe(r) == l for r in roi)]
    cnt = pd.DataFrame(0, index=lobes_present, columns=lobes_present, dtype=int)
    sgn = pd.DataFrame(0.0, index=lobes_present, columns=lobes_present)
    for e in sel_idx:
        a, b = lobe(roi[edge_i[e]]), lobe(roi[edge_j[e]])
        a, b = sorted([a, b], key=lobes_present.index)
        cnt.loc[a, b] += 1
        sgn.loc[a, b] += float(weights[e])
    return cnt, sgn


def lobe_pair_permutation(edge_i, edge_j, roi, k: int, n_perm: int, seed: int) -> pd.DataFrame:
    """Null distribution of lobe-pair counts when k edges are drawn uniformly at random.

    Returns observed/expected, a two-sided permutation p-value and its BH-corrected value for every
    lobe pair. This replaces the informal use of the word "enrichment": a ratio above 1 means nothing
    without the null, because lobe blocks differ enormously in the number of edges they contain.
    """
    lobes_present = [l for l in LOBES if any(lobe(r) == l for r in roi)]
    idx = {l: i for i, l in enumerate(lobes_present)}
    n_l = len(lobes_present)
    pair_id = np.empty(len(edge_i), dtype=int)
    for e in range(len(edge_i)):
        a, b = idx[lobe(roi[edge_i[e]])], idx[lobe(roi[edge_j[e]])]
        a, b = min(a, b), max(a, b)
        pair_id[e] = a * n_l + b
    n_pairs = n_l * n_l
    rng = np.random.default_rng(seed)
    null = np.empty((n_perm, n_pairs), dtype=np.int32)
    for p_ in range(n_perm):
        sel = rng.choice(len(pair_id), size=k, replace=False)
        null[p_] = np.bincount(pair_id[sel], minlength=n_pairs)
    return lobes_present, pair_id, null


def permutation_table(lobes_present, pair_id, null, observed_idx, k: int) -> pd.DataFrame:
    n_l = len(lobes_present)
    obs = np.bincount(pair_id[observed_idx], minlength=n_l * n_l)
    exp = null.mean(axis=0)
    n_perm = null.shape[0]
    rows = []
    for a in range(n_l):
        for b in range(a, n_l):
            c = a * n_l + b
            if exp[c] == 0 and obs[c] == 0:
                continue
            p_hi = (np.sum(null[:, c] >= obs[c]) + 1) / (n_perm + 1)
            p_lo = (np.sum(null[:, c] <= obs[c]) + 1) / (n_perm + 1)
            rows.append({"lobe_a": lobes_present[a], "lobe_b": lobes_present[b], "observed": int(obs[c]),
                         "expected": float(exp[c]), "obs_over_exp": float(obs[c] / exp[c]) if exp[c] else np.nan,
                         "p_perm": float(min(1.0, 2 * min(p_hi, p_lo)))})
    df = pd.DataFrame(rows)
    df["p_fdr"] = bh_fdr(df["p_perm"].to_numpy())
    return df.sort_values("p_perm").reset_index(drop=True)


def jaccard_null(n_edges: int, k: int, n_perm: int, seed: int) -> np.ndarray:
    """Null distribution of the top-k Jaccard overlap between two independent random selections."""
    rng = np.random.default_rng(seed)
    out = np.empty(n_perm)
    for i in range(n_perm):
        a = set(rng.choice(n_edges, size=k, replace=False).tolist())
        b = set(rng.choice(n_edges, size=k, replace=False).tolist())
        out[i] = len(a & b) / len(a | b)
    return out


def plot_lobe_pairs(cnt: pd.DataFrame, out_png: Path, title: str) -> None:
    blue = "#2a78d6"
    M = cnt.values.astype(float)
    M = M + np.triu(M, 1).T  # symmetric display
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    im = ax.imshow(M, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#ffffff", blue]))
    ax.set_xticks(range(len(cnt))); ax.set_yticks(range(len(cnt)))
    ax.set_xticklabels(cnt.columns, rotation=45, ha="right", fontsize=8); ax.set_yticklabels(cnt.index, fontsize=8)
    for i in range(len(cnt)):
        for j in range(len(cnt)):
            if M[i, j] > 0:
                ax.text(j, i, int(M[i, j]), ha="center", va="center", fontsize=7, color="#0b0b0b" if M[i, j] < M.max() * 0.6 else "white")
    ax.set_title(title, fontsize=10, loc="left")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03).set_label("edges among top-k", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", nargs="+", default=["abide", "adhd200", "abide-filt_global"])
    ap.add_argument("--variant", default=None)
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--model", default="lr")
    ap.add_argument("--n-perm", type=int, default=10000)
    args = ap.parse_args()
    cfg = load_config()
    set_seed(cfg["seed"])
    variant = args.variant or cfg["atlas"]["primary"]
    out = PROJECT_ROOT / cfg["paths"]["results"] / "e4"
    out.mkdir(parents=True, exist_ok=True)
    k = args.top_k

    consensus, tops, report = {}, {}, [f"# E4 — interpretation ({variant}, {args.model}, top-k = {k})", ""]
    for ds in args.datasets:
        w = load_weights(cfg, ds, variant, args.model)
        if w is None:
            print(f"[E4] no weights for {ds} (run E1 first)"); continue
        W, ei, ej, roi = w["W"], w["edge_i"], w["edge_j"], w["roi"]
        st = stability(W, k)
        pd.DataFrame([{"dataset": ds, **st}]).to_csv(out / f"{ds}_stability.csv", index=False)
        cw = W.mean(axis=0)
        consensus[ds] = cw
        order = np.argsort(-np.abs(cw))[:k]
        tops[ds] = set(order.tolist())
        # fraction of folds in which each consensus top-k edge is also top-k
        fold_tops = [set(np.argsort(-np.abs(W[f]))[:k]) for f in range(W.shape[0])]
        rows = []
        for rank, e in enumerate(order, 1):
            rows.append({"rank": rank, "edge": int(e), "roi_a": name(roi[ei[e]]), "roi_b": name(roi[ej[e]]),
                         "lobe_a": lobe(roi[ei[e]]), "lobe_b": lobe(roi[ej[e]]), "weight_mean": float(cw[e]),
                         "weight_sd_folds": float(W[:, e].std(ddof=1)),
                         "sign": "patient>control" if cw[e] > 0 else "control>patient",
                         "in_topk_fraction_of_folds": float(np.mean([e in ft for ft in fold_tops]))})
        top = pd.DataFrame(rows)
        top.to_csv(out / f"{ds}_top_edges.csv", index=False)
        cnt, sgn = lobe_pair_matrix(ei, ej, roi, order, cw)
        possible, _ = lobe_pair_matrix(ei, ej, roi, np.arange(len(cw)), cw)   # all edges per lobe block
        enrich = (cnt / (k * possible / len(cw))).replace([np.inf], np.nan)  # observed / expected under uniform selection
        cnt.to_csv(out / f"{ds}_lobe_pairs_count.csv"); sgn.round(4).to_csv(out / f"{ds}_lobe_pairs_signed.csv")
        enrich.round(3).to_csv(out / f"{ds}_lobe_pairs_enrichment.csv")
        lobes_present, pair_id, null = lobe_pair_permutation(ei, ej, roi, k, args.n_perm, cfg["seed"])
        perm = permutation_table(lobes_present, pair_id, null, order, k)
        perm.round(4).to_csv(out / f"{ds}_lobe_pairs_permutation.csv", index=False)
        plot_lobe_pairs(cnt, out / f"fig_{ds}_lobe_pairs.png", f"{ds}: lobe pairs of the top-{k} edges ({args.model})")
        report += [f"## {ds}", "",
                   f"- Fold stability ({st['n_folds']} leave-one-site-out folds): Spearman(|w|) mean {st['spearman_abs_w_mean']:.3f} "
                   f"(min {st['spearman_abs_w_min']:.3f}); top-{k} Jaccard mean {st[f'jaccard_top{k}_mean']:.3f} (min {st[f'jaccard_top{k}_min']:.3f}).",
                   f"- Consensus top-{k} edges present in the top-{k} of ≥ 80 % of folds: {int((top['in_topk_fraction_of_folds'] >= 0.8).sum())}.",
                   f"- Sign split of top-{k}: {int((top['sign'] == 'patient>control').sum())} patient>control, "
                   f"{int((top['sign'] == 'control>patient').sum())} control>patient.",
                   "", "Top 15 edges:", "",
                   top.head(15)[["rank", "roi_a", "roi_b", "weight_mean", "sign", "in_topk_fraction_of_folds"]].round(4).to_markdown(index=False),
                   "", f"Lobe-pair counts (upper triangle): `{ds}_lobe_pairs_count.csv` / `fig_{ds}_lobe_pairs.png`; "
                   f"enrichment vs. uniform selection (observed/expected): `{ds}_lobe_pairs_enrichment.csv`.", "",
                   "Lobe-pair enrichment (observed / expected, upper triangle):", "",
                   enrich.round(2).to_markdown(), "",
                   f"Permutation test ({args.n_perm} random draws of {k} edges; two-sided, BH-corrected across "
                   f"lobe pairs) — top rows:", "",
                   perm.head(8).round(3).to_markdown(index=False), "",
                   f"Lobe pairs with p_FDR < 0.05: {int((perm['p_fdr'] < 0.05).sum())} of {len(perm)}.", ""]
        print(f"[E4] {ds}: {st}")

    # cross-dataset similarity (with a permutation null for the top-k overlap)
    sim_rows = []
    jnull = {n: jaccard_null(n, k, min(args.n_perm, 2000), cfg["seed"])
             for n in {len(v) for v in consensus.values()}}
    for a, b in itertools.combinations(consensus, 2):
        rho_abs = spearmanr(np.abs(consensus[a]), np.abs(consensus[b])).correlation
        rho_signed = spearmanr(consensus[a], consensus[b]).correlation
        sim_rows.append({"dataset_a": a, "dataset_b": b, "spearman_abs_w": float(rho_abs), "spearman_signed_w": float(rho_signed),
                         f"jaccard_top{k}": jaccard(tops[a], tops[b]),
                         f"expected_jaccard_random": k / (2 * len(consensus[a]) - k),
                         "jaccard_null_p": float((np.sum(jnull[len(consensus[a])] >= jaccard(tops[a], tops[b])) + 1)
                                                 / (len(jnull[len(consensus[a])]) + 1))})
    if sim_rows:
        sim = pd.DataFrame(sim_rows)
        sim.to_csv(out / "cross_dataset_weight_similarity.csv", index=False)
        report += ["## Cross-dataset similarity of consensus weights", "", sim.round(4).to_markdown(index=False), ""]
    (out / "e4_report.md").write_text("\n".join(report) + "\n")
    print(f"[E4] -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
