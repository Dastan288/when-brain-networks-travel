"""Evaluation protocols.

* leave_one_site_out(site): within-dataset headline protocol. Each held-out
  site is never seen during fitting (scaler, model, ComBat).
* random_kfold(y, k): stratified random K-fold ACROSS sites. Forbidden for
  headline numbers — used exactly once, labelled, to show the inflation that
  site leakage produces.
* Cross-dataset: no splitting function needed — train on 100 % of A, test on
  100 % of B (see run_e2.py).
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
from sklearn.model_selection import StratifiedKFold


def leave_one_site_out(site: np.ndarray) -> Iterator[tuple[str, np.ndarray, np.ndarray]]:
    site = np.asarray(site)
    for s in sorted(np.unique(site)):
        test = np.where(site == s)[0]
        train = np.where(site != s)[0]
        yield str(s), train, test


def random_kfold(y: np.ndarray, k: int = 10, seed: int = 42) -> Iterator[tuple[str, np.ndarray, np.ndarray]]:
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=seed)
    for i, (train, test) in enumerate(skf.split(np.zeros(len(y)), y)):
        yield f"fold{i}", train, test


def load_features(path) -> dict:
    z = np.load(path, allow_pickle=False)
    return {k: z[k] for k in z.files}
