"""Classifier zoo with hyperparameters fixed a priori (no tuning on test data).

All models are sklearn Pipelines; any fitting (scaler, model) happens inside
`fit` on training subjects only. Linear models are primary (interpretable
weights -> which edges/networks transfer).
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

MODEL_NAMES = ["lr", "svm", "rf"]
CONTROL_NAMES = ["agesex_lr"]


def make_model(name: str, seed: int = 42, n_jobs: int = 2) -> Pipeline:
    if name == "lr":  # L2 logistic regression, C fixed at 1 (default)
        clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000, solver="lbfgs")  # L2 (default)
    elif name == "svm":  # linear-kernel SVM, C fixed at 1 (kernel form: n_subjects << n_edges -> fast, exact)
        clf = SVC(kernel="linear", C=1.0, class_weight="balanced", random_state=seed)
    elif name == "rf":
        clf = RandomForestClassifier(n_estimators=500, class_weight="balanced_subsample", min_samples_leaf=2,
                                     n_jobs=n_jobs, random_state=seed)
    elif name == "agesex_lr":  # control model: demographics only
        clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000)
    else:
        raise KeyError(name)
    return Pipeline([("scale", StandardScaler()), ("clf", clf)])


def decision_scores(model: Pipeline, X: np.ndarray) -> np.ndarray:
    """Continuous score for AUC: log-odds / margin / positive-class probability."""
    clf = model.named_steps["clf"]
    if hasattr(clf, "decision_function"):
        return model.decision_function(X)
    return model.predict_proba(X)[:, 1]


def linear_weights(model: Pipeline) -> np.ndarray | None:
    """Edge weights in standardized-feature space for linear models (E4 interpretation)."""
    clf = model.named_steps["clf"]
    return np.ravel(clf.coef_) if hasattr(clf, "coef_") else None


def demographics_matrix(age: np.ndarray, sex: np.ndarray) -> np.ndarray:
    """Age (years) and sex (M=1, F=0) as a 2-column design for the control model."""
    sex_bin = (np.asarray(sex).astype(str) == "M").astype(float)
    return np.column_stack([np.asarray(age, dtype=float), sex_bin])
