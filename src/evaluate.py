"""Metrics with subject-level bootstrap 95% confidence intervals.

Every number reported in the paper goes through `bootstrap_metrics`:
    point estimate on the full set of out-of-fold predictions +
    percentile CI from >= 1000 resamples of SUBJECTS (not folds).
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import balanced_accuracy_score, roc_auc_score


def _safe_auc(y: np.ndarray, s: np.ndarray) -> float:
    return float(roc_auc_score(y, s)) if len(np.unique(y)) == 2 else np.nan


def sensitivity(y: np.ndarray, p: np.ndarray) -> float:
    m = y == 1
    return float((p[m] == 1).mean()) if m.any() else np.nan


def specificity(y: np.ndarray, p: np.ndarray) -> float:
    m = y == 0
    return float((p[m] == 0).mean()) if m.any() else np.nan


def compute_metrics(y: np.ndarray, pred: np.ndarray, score: np.ndarray | None) -> dict:
    y, pred = np.asarray(y).astype(int), np.asarray(pred).astype(int)
    out = {
        # undefined when only one class is present (e.g. a controls-only held-out site such as ADHD-200 WashU);
        # sklearn would silently return the recall of the single class, which is not a balanced accuracy
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else np.nan,
        "accuracy": float((y == pred).mean()),
        "sensitivity": sensitivity(y, pred),
        "specificity": specificity(y, pred),
    }
    if score is not None:
        out["auc"] = _safe_auc(y, np.asarray(score))
    return out


def bootstrap_metrics(y, pred, score=None, n_boot: int = 1000, seed: int = 42, alpha: float = 0.05) -> dict:
    """Return {metric: value, metric_ci_low, metric_ci_high} with percentile CIs."""
    y, pred = np.asarray(y), np.asarray(pred)
    score = None if score is None else np.asarray(score)
    point = compute_metrics(y, pred, score)
    rng = np.random.default_rng(seed)
    n = len(y)
    boots = {k: [] for k in point}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y[idx])) < 2:
            continue
        m = compute_metrics(y[idx], pred[idx], None if score is None else score[idx])
        for k, v in m.items():
            boots[k].append(v)
    out = {}
    for k, v in point.items():
        b = np.asarray(boots[k], dtype=float)
        b = b[~np.isnan(b)]
        out[k] = v
        out[f"{k}_ci_low"] = float(np.percentile(b, 100 * alpha / 2)) if len(b) else np.nan
        out[f"{k}_ci_high"] = float(np.percentile(b, 100 * (1 - alpha / 2))) if len(b) else np.nan
    out["n"] = int(n)
    out["n_boot"] = int(n_boot)
    return out


def paired_bootstrap_delta(y, pred_a, score_a, pred_b, score_b, metric: str = "balanced_accuracy",
                           n_boot: int = 1000, seed: int = 42) -> dict:
    """CI for metric(B) - metric(A) on the same subjects (e.g., ComBat vs raw)."""
    y = np.asarray(y)
    rng = np.random.default_rng(seed)
    n = len(y)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y[idx])) < 2:
            continue
        ma = compute_metrics(y[idx], np.asarray(pred_a)[idx], None if score_a is None else np.asarray(score_a)[idx])
        mb = compute_metrics(y[idx], np.asarray(pred_b)[idx], None if score_b is None else np.asarray(score_b)[idx])
        deltas.append(mb[metric] - ma[metric])
    d = np.asarray(deltas)
    full = compute_metrics(y, np.asarray(pred_b), score_b)[metric] - compute_metrics(y, np.asarray(pred_a), score_a)[metric]
    # two-sided bootstrap p-value (proportion of resamples on the wrong side of 0, doubled)
    p_boot = float(min(1.0, 2 * min(float(np.mean(d <= 0)), float(np.mean(d >= 0)))))
    return {"delta": float(full), "ci_low": float(np.percentile(d, 2.5)), "ci_high": float(np.percentile(d, 97.5)),
            "p_boot": p_boot}


def bh_fdr(pvals) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (same order as the input)."""
    p = np.asarray(pvals, dtype=float)
    ok = ~np.isnan(p)
    out = np.full(p.shape, np.nan)
    ps = p[ok]
    n = len(ps)
    if n == 0:
        return out
    order = np.argsort(ps)
    ranked = ps[order] * n / (np.arange(n) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(n)
    adj[order] = np.minimum(ranked, 1.0)
    out[ok] = adj
    return out


def fmt_ci(d: dict, metric: str, digits: int = 3) -> str:
    return f"{d[metric]:.{digits}f} [{d[f'{metric}_ci_low']:.{digits}f}, {d[f'{metric}_ci_high']:.{digits}f}]"
