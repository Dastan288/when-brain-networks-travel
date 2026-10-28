#!/usr/bin/env python
"""Paper figures (matplotlib, no grid clutter, colour-safe).

Fig. 1  Transfer matrix heat-maps: raw vs ComBat (reference-only) vs ComBat (new-batch), one model.
        Cells = balanced accuracy on the target with 95 % CI; diverging colour centred at chance (0.5).
Fig. 2  E1 protocol comparison: leave-one-site-out vs random 10-fold per model with CI bars,
        plus per-site spread.

Usage: python src/figures.py [--model lr] [--views abide adhd200 ucla ucla-adhd]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PROJECT_ROOT, load_config  # noqa: E402

BLUE, ORANGE, INK, MUTED, RULE = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#c3c2b7"
DIVERGING = LinearSegmentedColormap.from_list("chance", [ORANGE, "#f4f3f0", BLUE])
PRETTY = {"abide": "ABIDE\n(ASD)", "adhd200": "ADHD-200\n(ADHD)", "ucla": "UCLA-CNP\n(any dx)", "ucla-adhd": "UCLA-CNP\n(ADHD)",
          "abide-filt_global": "ABIDE (GSR)"}
# rows carry the full names, numbered 1..4; the columns repeat the same order and are labelled by
# those numbers, which is the only way four names fit under one panel at a legible size
DIAGNOSIS_MATCHED = {("adhd200", "ucla-adhd"), ("ucla-adhd", "adhd200")}
HARM_TITLE = {"none": "(a) raw", "combat_ref": "(b) ComBat, reference-only", "combat_new": "(c) ComBat, new-batch"}


def transfer_heatmap(summary: pd.DataFrame, views: list[str], model: str, out_png: Path, metric: str = "balanced_accuracy",
                     harms=("none", "combat_ref", "combat_new")) -> None:
    ok = summary[(summary["status"] == "ok") & (summary["model"] == model) & (summary["harmonization"].isin(harms))]
    harms = [h for h in harms if (ok["harmonization"] == h).any()]
    vmax = max(0.75, float(np.nanmax(ok[metric])) + 0.02)
    norm = TwoSlopeNorm(vmin=1 - vmax, vcenter=0.5, vmax=vmax)
    n = len(views)
    # compact layout: the figure is placed at ~5.9 in in the paper, so the natural size is kept small
    # enough that the in-cell annotations stay legible (>= 6 pt) at that scale
    fig, axes = plt.subplots(1, len(harms), figsize=(2.5 * len(harms) + 1.0, 0.44 * n + 0.9), squeeze=False)
    for ax, harm in zip(axes[0], harms):
        g = ok[ok["harmonization"] == harm]
        M = np.full((n, n), np.nan)
        txt = [["" for _ in range(n)] for _ in range(n)]
        for i, s in enumerate(views):
            for j, t in enumerate(views):
                r = g[(g["source"] == s) & (g["target"] == t)]
                if len(r):
                    r = r.iloc[0]
                    M[i, j] = r[metric]
                    lo, hi = f"{r[metric+'_ci_low']:.2f}".lstrip("0"), f"{r[metric+'_ci_high']:.2f}".lstrip("0")
                    txt[i][j] = f"{r[metric]:.2f}\n{lo}–{hi}"
                else:
                    txt[i][j] = "n/a"
        ax.imshow(np.where(np.isnan(M), 0.5, M), cmap=DIVERGING, norm=norm)
        for i in range(n):
            for j in range(n):
                dark = not np.isnan(M[i, j]) and abs(M[i, j] - 0.5) > 0.12
                ax.text(j, i, txt[i][j], ha="center", va="center", fontsize=8.5, color="white" if dark else INK)
                if i == j:
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=INK, linewidth=1.2))
                elif (views[i], views[j]) in DIAGNOSIS_MATCHED:
                    # the only off-diagonal cells with the SAME diagnostic task on both sides
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=ORANGE,
                                               linewidth=1.6, linestyle=(0, (2.5, 1.5))))
        ax.set_xticks(range(n)); ax.set_yticks(range(n))
        ax.set_xticklabels([str(k + 1) for k in range(n)], fontsize=9)
        ax.set_yticklabels([f"{k + 1} " + PRETTY.get(v, v) for k, v in enumerate(views)] if ax is axes[0][0] else [], fontsize=8)
        ax.set_xlabel("test dataset", fontsize=8.5, color=MUTED)
        if ax is axes[0][0]:
            ax.set_ylabel("training dataset", fontsize=8.5, color=MUTED)
        ax.set_title(HARM_TITLE.get(harm, harm), fontsize=9.5, loc="left", color=INK)
        ax.tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
    fig.subplots_adjust(wspace=0.08)
    sm = plt.cm.ScalarMappable(cmap=DIVERGING, norm=norm)
    cb = fig.colorbar(sm, ax=axes[0].tolist(), fraction=0.02, pad=0.02)
    cb.set_label("balanced accuracy (0.5 = chance)", fontsize=8.5)
    cb.ax.tick_params(labelsize=7)
    fig.savefig(out_png, dpi=400, bbox_inches="tight")
    fig.savefig(out_png.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def e1_protocol_figure(e1: pd.DataFrame, per_site: pd.DataFrame, variant: str, out_png: Path) -> None:
    g = e1[(e1["variant"] == variant) & (e1["sample"] == "primary")]
    models = [m for m in ["lr", "svm", "rf", "agesex_lr"] if (g["model"] == m).any()]
    labels = {"lr": "LR", "svm": "linear SVM", "rf": "RF", "agesex_lr": "age+sex\n(control)"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.2), gridspec_kw={"width_ratios": [1.1, 1.4]})
    x = np.arange(len(models)); w = 0.36
    for k, (proto, col, lab) in enumerate([("losite", BLUE, "leave-one-site-out"), ("random10_INFLATED", ORANGE, "random 10-fold (site leakage)")]):
        vals, lo, hi = [], [], []
        for m in models:
            r = g[(g["model"] == m) & (g["protocol"] == proto)]
            vals.append(r["balanced_accuracy"].iloc[0] if len(r) else np.nan)
            lo.append(r["balanced_accuracy_ci_low"].iloc[0] if len(r) else np.nan)
            hi.append(r["balanced_accuracy_ci_high"].iloc[0] if len(r) else np.nan)
        vals, lo, hi = map(np.asarray, (vals, lo, hi))
        ax1.bar(x + (k - 0.5) * w, vals, width=w, color=col, label=lab, edgecolor="white", linewidth=1)
        ax1.errorbar(x + (k - 0.5) * w, vals, yerr=[vals - lo, hi - vals], fmt="none", ecolor=INK, elinewidth=0.8, capsize=2)
    ax1.axhline(0.5, color=MUTED, linewidth=0.8, linestyle=":")
    ax1.set_xticks(x); ax1.set_xticklabels([labels[m] for m in models], fontsize=8)
    ax1.set_ylim(0.4, 0.8); ax1.set_ylabel("balanced accuracy", fontsize=8)
    ax1.set_title("(a) within-dataset protocol", fontsize=9, loc="left")
    ax1.legend(frameon=False, fontsize=7, loc="upper right")
    ps = per_site[(per_site["variant"] == variant) & (per_site["sample"] == "primary") & (per_site["model"] == "lr")]
    ps = ps.sort_values("balanced_accuracy")
    y = np.arange(len(ps))
    ax2.scatter(ps["balanced_accuracy"], y, s=np.clip(ps["n"] / 3, 8, 60), color=BLUE, alpha=0.8, linewidths=0)
    ax2.axvline(0.5, color=MUTED, linewidth=0.8, linestyle=":")
    ax2.set_yticks(y); ax2.set_yticklabels(ps["site"], fontsize=7)
    ax2.set_xlabel("balanced accuracy of the held-out site (LR)", fontsize=8)
    ax2.set_title("(b) per-site spread (marker size ∝ n)", fontsize=9, loc="left")
    for ax in (ax1, ax2):
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.spines["left"].set_color(RULE); ax.spines["bottom"].set_color(RULE)
        ax.tick_params(colors=MUTED, labelsize=7)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300); fig.savefig(out_png.with_suffix(".pdf"))
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="lr")
    ap.add_argument("--views", nargs="+", default=["abide", "adhd200", "ucla", "ucla-adhd"])
    ap.add_argument("--e1-dataset", default="abide")
    args = ap.parse_args()
    cfg = load_config()
    res = PROJECT_ROOT / cfg["paths"]["results"]
    out = res / "figures"; out.mkdir(parents=True, exist_ok=True)
    e2 = res / "e2" / "e2_summary.csv"
    if e2.exists():
        summary = pd.read_csv(e2)
        views = [v for v in args.views if v in set(summary["source"])]
        transfer_heatmap(summary, views, args.model, out / f"fig_transfer_matrix_{args.model}.png")
        print(f"[figures] transfer matrix -> {out}/fig_transfer_matrix_{args.model}.png")
    e1 = res / "e1" / args.e1_dataset / "e1_summary.csv"
    if e1.exists():
        e1_protocol_figure(pd.read_csv(e1), pd.read_csv(res / "e1" / args.e1_dataset / "e1_per_site.csv"),
                           cfg["atlas"]["primary"], out / f"fig_e1_protocols_{args.e1_dataset}.png")
        print(f"[figures] E1 protocol figure -> {out}/fig_e1_protocols_{args.e1_dataset}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
