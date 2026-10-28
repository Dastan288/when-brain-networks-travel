"""ComBat harmonization (Johnson, Li & Rabinovic 2007; Fortin et al. 2018) with an explicit
fit / apply separation so that no test-site or test-dataset information leaks into training.

    cb = ComBat(covariate_names=["age", "sex"]).fit(X_train, batch_train, covars_train)
    X_train_h = cb.transform(X_train, batch_train, covars_train)          # seen batches
    X_test_h  = cb.transform_new_batch(X_test, covars_test)              # unseen site/dataset,
                                                                          # unsupervised (no labels)
    X_test_r  = cb.reference_only(X_test, covars_test)                   # strict: no test-data statistics

Model (per feature g, batch i, subject j):  x_ijg = alpha_g + C_ij beta_g + gamma_ig + delta_ig * e_ijg
Empirical-Bayes shrinkage of gamma/delta across features within each batch (parametric priors),
exactly as in neuroCombat. Covariate effects (age, sex) are preserved.

Modes for held-out data:
* transform_new_batch — the usual "harmonize a new site" recipe: standardize with the training
  reference (alpha, beta, pooled variance), estimate the new batch's own location/scale from its
  UNLABELED features (EB across features), remove them. Transductive at the feature level, never
  uses labels or tunes anything; report it as such.
* reference_only — no statistics from the held-out data at all (only alpha/beta/sigma from training).
"""

from __future__ import annotations

import numpy as np


def _aprior(g):  # inverse-gamma prior hyperparameters from moments (neuroCombat)
    m, s2 = np.mean(g), np.var(g, ddof=1)
    return (2 * s2 + m ** 2) / s2


def _bprior(g):
    m, s2 = np.mean(g), np.var(g, ddof=1)
    return (m * s2 + m ** 3) / s2


def _postmean(g_hat, g_bar, n, d_star, t2):
    return (t2 * n * g_hat + d_star * g_bar) / (t2 * n + d_star)


def _postvar(sum2, n, a, b):
    return (0.5 * sum2 + b) / (n / 2.0 + a - 1)


def _it_sol(sdat, g_hat, d_hat, g_bar, t2, a, b, conv=1e-4, max_iter=500):
    """EB iteration for one batch: sdat (n_i x p) standardized data."""
    n = sdat.shape[0]
    g_old, d_old = g_hat.copy(), d_hat.copy()
    for _ in range(max_iter):
        g_new = _postmean(g_hat, g_bar, n, d_old, t2)
        sum2 = ((sdat - g_new[None, :]) ** 2).sum(axis=0)
        d_new = _postvar(sum2, n, a, b)
        change = max(np.max(np.abs(g_new - g_old) / np.abs(g_old + 1e-12)),
                     np.max(np.abs(d_new - d_old) / np.abs(d_old + 1e-12)))
        g_old, d_old = g_new, d_new
        if change < conv:
            break
    return g_new, d_new


def _eb_batch_params(sdat):
    """gamma*, delta*^2 for one batch from standardized data using parametric EB priors."""
    g_hat = sdat.mean(axis=0)
    d_hat = sdat.var(axis=0, ddof=1)
    d_hat = np.where(d_hat > 0, d_hat, 1e-8)
    g_bar, t2 = g_hat.mean(), g_hat.var(ddof=1)
    a, b = _aprior(d_hat), _bprior(d_hat)
    return _it_sol(sdat, g_hat, d_hat, g_bar, t2, a, b)


class ComBat:
    def __init__(self, eb: bool = True):
        self.eb = eb

    # ------------------------------------------------------------------ fit
    def fit(self, X: np.ndarray, batch: np.ndarray, covars: np.ndarray | None = None) -> "ComBat":
        X = np.asarray(X, dtype=np.float64)
        batch = np.asarray(batch).astype(str)
        n, p = X.shape
        self.batches_ = sorted(np.unique(batch))
        m = len(self.batches_)
        if m < 2:
            raise ValueError("ComBat needs >= 2 batches in the training data")
        B = np.column_stack([(batch == b).astype(float) for b in self.batches_])   # n x m
        C = None if covars is None else np.asarray(covars, dtype=np.float64)
        if C is not None and C.ndim == 1:
            C = C[:, None]
        self.n_cov_ = 0 if C is None else C.shape[1]
        design = B if C is None else np.hstack([B, C])
        beta_hat, *_ = np.linalg.lstsq(design, X, rcond=None)                     # (m+k) x p
        n_batches = B.sum(axis=0)
        self.alpha_ = (n_batches / n) @ beta_hat[:m]                                # grand mean, p
        self.beta_cov_ = beta_hat[m:] if C is not None else np.zeros((0, p))        # k x p
        stand_mean = self.alpha_[None, :] + (0 if C is None else C @ self.beta_cov_)
        resid = X - design @ beta_hat
        self.var_pooled_ = (resid ** 2).mean(axis=0)
        self.var_pooled_ = np.where(self.var_pooled_ > 0, self.var_pooled_, 1e-8)
        self.sigma_ = np.sqrt(self.var_pooled_)
        s = (X - stand_mean) / self.sigma_[None, :]
        self.gamma_star_, self.delta_star_ = {}, {}
        for bname in self.batches_:
            sb = s[batch == bname]
            if self.eb and sb.shape[0] > 1:
                g, d = _eb_batch_params(sb)
            else:
                g, d = sb.mean(axis=0), np.maximum(sb.var(axis=0, ddof=1) if sb.shape[0] > 1 else np.ones(p), 1e-8)
            self.gamma_star_[bname], self.delta_star_[bname] = g, d
        return self

    # -------------------------------------------------------------- helpers
    def _stand(self, X, covars):
        X = np.asarray(X, dtype=np.float64)
        C = None if covars is None else np.asarray(covars, dtype=np.float64)
        if C is not None and C.ndim == 1:
            C = C[:, None]
        if (C is None and self.n_cov_) or (C is not None and C.shape[1] != self.n_cov_):
            raise ValueError("covariate layout differs from fit()")
        stand_mean = self.alpha_[None, :] + (0 if C is None else C @ self.beta_cov_)
        return (X - stand_mean) / self.sigma_[None, :], stand_mean

    def _unstand(self, s, stand_mean):
        return s * self.sigma_[None, :] + stand_mean

    # ------------------------------------------------------------ transform
    def transform(self, X, batch, covars=None) -> np.ndarray:
        """Seen batches only (training sites)."""
        batch = np.asarray(batch).astype(str)
        s, stand_mean = self._stand(X, covars)
        out = np.empty_like(s)
        for bname in np.unique(batch):
            if bname not in self.gamma_star_:
                raise KeyError(f"batch {bname!r} not seen in fit(); use transform_new_batch")
            m = batch == bname
            out[m] = (s[m] - self.gamma_star_[bname][None, :]) / np.sqrt(self.delta_star_[bname])[None, :]
        return self._unstand(out, stand_mean).astype(np.float32)

    def transform_new_batch(self, X, covars=None, batch=None) -> np.ndarray:
        """Unseen site(s)/dataset: location/scale estimated from the held-out features themselves
        (unsupervised; no labels). If `batch` is given, each new batch is adjusted separately."""
        s, stand_mean = self._stand(X, covars)
        batch = np.zeros(len(s), dtype=int) if batch is None else np.asarray(batch).astype(str)
        out = np.empty_like(s)
        for bname in np.unique(batch):
            m = batch == bname
            sb = s[m]
            if sb.shape[0] < 3:  # too small to estimate scale: location only
                out[m] = sb - sb.mean(axis=0)[None, :]
                continue
            g, d = _eb_batch_params(sb) if self.eb else (sb.mean(axis=0), np.maximum(sb.var(axis=0, ddof=1), 1e-8))
            out[m] = (sb - g[None, :]) / np.sqrt(d)[None, :]
        return self._unstand(out, stand_mean).astype(np.float32)

    def reference_only(self, X, covars=None) -> np.ndarray:
        """Strict mode: only training alpha/beta/sigma are used; nothing is estimated on held-out data."""
        s, stand_mean = self._stand(X, covars)
        return self._unstand(s, stand_mean).astype(np.float32)


def covariate_matrix(age, sex) -> np.ndarray:
    """age (years) and sex (M=1, F=0) — the ComBat covariates used throughout the project."""
    sex_bin = (np.asarray(sex).astype(str) == "M").astype(float)
    return np.column_stack([np.asarray(age, dtype=float), sex_bin])
