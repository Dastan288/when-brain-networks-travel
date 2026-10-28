#!/usr/bin/env python
"""Verify every "value [low, high]" triple in paper/manuscript.md against the result CSVs.

The manuscript is written by hand; this script is the guard that keeps it faithful to the
pipeline output. It collects every (metric, ci_low, ci_high) triple that appears anywhere in
results/**/*.csv (both absolute metrics and paired deltas), rounds to three decimals, and checks
that each triple quoted in the manuscript exists. Usage: python src/check_manuscript_numbers.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NUM = r"[-−+]?\d\.\d{3}"


def norm(x: str) -> float:
    return float(x.replace("−", "-").replace("+", ""))


def collect() -> set[tuple[float, float, float]]:
    out: set[tuple[float, float, float]] = set()
    for f in sorted((ROOT / "results").rglob("*.csv")):
        try:
            df = pd.read_csv(f)
        except Exception:
            continue
        cols = set(df.columns)
        pairs = [("balanced_accuracy", "balanced_accuracy_ci_low", "balanced_accuracy_ci_high"),
                 ("auc", "auc_ci_low", "auc_ci_high"),
                 ("delta", "ci_low", "ci_high"),
                 ("macro_bacc", "macro_ci_low", "macro_ci_high"),
                 ("pooled_bacc", "site_cluster_ci_low", "site_cluster_ci_high")]
        for v, lo, hi in pairs:
            if {v, lo, hi} <= cols:
                for _, r in df[[v, lo, hi]].dropna().iterrows():
                    out.add((round(r[v], 3), round(r[lo], 3), round(r[hi], 3)))
    return out


def main() -> int:
    known = collect()
    text = (ROOT / "paper" / "manuscript.md").read_text()
    triples = re.findall(rf"({NUM})\s*\[\s*({NUM})\s*,\s*({NUM})\s*\]", text)
    bad = []
    for v, lo, hi in triples:
        t = (round(norm(v), 3), round(norm(lo), 3), round(norm(hi), 3))
        if t not in known:
            bad.append(t)
    # "mean ± sd" of the repeated site-mixed CV (results/e6/e6_repeated_cv.csv)
    cv = pd.read_csv(ROOT / "results" / "e6" / "e6_repeated_cv.csv")
    g = cv.groupby(["view", "model"]).balanced_accuracy.agg(["mean", lambda x: x.std(ddof=1)])
    known_pm = {(round(a, 3), round(b, 3)) for a, b in g.to_numpy()}
    for v, sd in re.findall(r"(\d\.\d{3}) ± (\d\.\d{3})", text):
        if (float(v), float(sd)) not in known_pm:
            bad.append((float(v), float(sd), float("nan")))
    print(f"[check] {len(triples)} value[CI] triples and {len(re.findall(r'± ', text))} mean ± SD values in the manuscript, {len(known)} triples in the result CSVs")
    for t in bad:
        print(f"  MISMATCH {t[0]} [{t[1]}, {t[2]}] not found in any result table")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
