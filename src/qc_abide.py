#!/usr/bin/env python
"""QC table for ABIDE I Preprocessed ROI time series (Stage 1 deliverable).

Reads the phenotypic file + every downloaded *_rois_aal.1D / *_rois_cc200.1D,
and writes:
  results/qc/abide_subjects_qc.csv   one row per subject (phenotypes, rater QC,
                                     motion, time-series length, NaN / flat ROIs)
  results/qc/abide_site_summary.csv  one row per site (+ TOTAL)
  results/qc/abide_qc_report.md      human-readable report (tables + notes)
  results/qc/fig_abide_qc.png        per-site counts and time-series lengths

Nothing is excluded here: subjects are FLAGGED using the thresholds in
config/config.yaml; the exclusion decision is made (and documented) later.

Usage:  python src/qc_abide.py [--strategy filt_global]   (after data/download_abide.py)
Outputs are prefixed with the dataset tag: 'abide' (primary strategy) or 'abide-<strategy>'.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import abide_dirs, load_config, set_seed  # noqa: E402

PHENO_COLS = [
    "SUB_ID", "FILE_ID", "SITE_ID", "DX_GROUP", "DSM_IV_TR", "AGE_AT_SCAN", "SEX",
    "HANDEDNESS_CATEGORY", "FIQ", "EYE_STATUS_AT_SCAN",
    "func_mean_fd", "func_perc_fd", "func_num_fd", "func_quality", "anat_cnr", "func_fber",
    "qc_rater_1", "qc_anat_rater_2", "qc_func_rater_2", "qc_anat_rater_3", "qc_func_rater_3",
]

# Same criterion nilearn applies when quality_checked=True (fetch_abide_pcp).
def rater_qc_pass(row: pd.Series) -> bool:
    return (
        row.get("qc_rater_1") == "OK"
        and row.get("qc_anat_rater_2") in ("OK", "maybe")
        and row.get("qc_func_rater_2") in ("OK", "maybe")
        and row.get("qc_anat_rater_3") == "OK"
        and row.get("qc_func_rater_3") == "OK"
    )


def load_1d(path: Path) -> np.ndarray:
    """C-PAC ROI .1D: whitespace-separated, optional '#' header line(s)."""
    return np.loadtxt(path, comments="#", ndmin=2)


def series_stats(path: Path) -> dict:
    if not path.exists():
        return {"n_tp": np.nan, "n_roi": np.nan, "n_nan": np.nan, "n_zero_var": np.nan, "exists": False}
    x = load_1d(path)
    n_tp, n_roi = x.shape
    n_nan = int(np.isnan(x).sum())
    with np.errstate(invalid="ignore"):
        sd = np.nanstd(x, axis=0)
    n_zero_var = int(np.sum(~(sd > 0)))  # flat (all-zero) ROIs, e.g. outside the field of view
    return {"n_tp": n_tp, "n_roi": n_roi, "n_nan": n_nan, "n_zero_var": n_zero_var, "exists": True}


def fmt_mean_sd(x: pd.Series, d: int = 1) -> str:
    x = x.dropna()
    return f"{x.mean():.{d}f} ({x.std(ddof=1):.{d}f})" if len(x) > 1 else (f"{x.mean():.{d}f}" if len(x) else "–")


def build_subject_table(cfg: dict, dirs: dict) -> pd.DataFrame:
    a = cfg["abide"]
    pheno = pd.read_csv(dirs["phenotypic"])
    n_pheno_total = len(pheno)
    pheno = pheno[pheno["FILE_ID"] != "no_filename"].copy()
    keep = [c for c in PHENO_COLS if c in pheno.columns]
    df = pheno[keep].copy()
    df["label"] = df["DX_GROUP"].map({int(k): v for k, v in a["label_map"].items()})
    df["dx"] = df["DX_GROUP"].map({1: "ASD", 2: "TD"})
    df["sex"] = df["SEX"].map({int(k): v for k, v in a["sex_map"].items()})
    df["rater_qc_pass"] = df.apply(rater_qc_pass, axis=1)
    merge = a.get("site_merge", {}) or {}
    df["site"] = df["SITE_ID"].map(lambda x: merge.get(x, x))  # LoSiteO unit = institution

    have_series = dirs["derivatives"].exists() and any(dirs["derivatives"].glob("*_rois_aal.1D"))
    for atlas in ("aal", "cc200"):
        if have_series:
            stats = [series_stats(dirs["derivatives"] / f"{fid}_rois_{atlas}.1D") for fid in df["FILE_ID"]]
        else:  # phenotypic-only preview (derivatives not downloaded yet)
            stats = [{"n_tp": np.nan, "n_roi": np.nan, "n_nan": np.nan, "n_zero_var": np.nan, "exists": False}] * len(df)
        s = pd.DataFrame(stats, index=df.index)
        for c in ("n_tp", "n_roi", "n_nan", "n_zero_var", "exists"):
            df[f"{atlas}_{c}"] = s[c]

    q = cfg["qc"]
    df["flag_missing_file"] = (
        ~(df["aal_exists"].astype(bool) & df["cc200_exists"].astype(bool)) if have_series else False
    )
    df["flag_short"] = df["aal_n_tp"].fillna(np.inf) < q["min_timepoints"]
    df["flag_zero_var"] = df["aal_n_zero_var"].fillna(0) > q["max_zero_variance_rois"]
    df["flag_nan"] = (df["aal_n_nan"].fillna(0) + df["cc200_n_nan"].fillna(0)) > 0
    df["flag_motion"] = df["func_mean_fd"] > q["max_mean_fd_mm"]
    df["flag_any"] = df[["flag_missing_file", "flag_short", "flag_zero_var", "flag_nan", "flag_motion"]].any(axis=1)
    attrs = {"n_pheno_total": n_pheno_total, "n_no_filename": n_pheno_total - len(df), "have_series": bool(have_series)}
    df = df.sort_values(["site", "SITE_ID", "SUB_ID"]).reset_index(drop=True)
    df.attrs.update(attrs)
    return df


def site_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    groups = list(df.groupby("site", sort=True)) + [("TOTAL", df)]
    for site, g in groups:
        n = len(g)
        sub = sorted(g["SITE_ID"].unique().tolist())
        n_asd = int((g["dx"] == "ASD").sum())
        n_td = int((g["dx"] == "TD").sum())
        tps = g["aal_n_tp"].dropna().astype(int)
        tp_vals = sorted(tps.unique().tolist())
        rows.append({
            "site": site,
            "sub_sites": "" if site == "TOTAL" or sub == [site] else "+".join(sub),
            "n": n,
            "ASD": n_asd,
            "TD": n_td,
            "ASD_%": round(100 * n_asd / n, 1) if n else np.nan,
            "age_mean_sd": fmt_mean_sd(g["AGE_AT_SCAN"]),
            "age_min": round(g["AGE_AT_SCAN"].min(), 1),
            "age_max": round(g["AGE_AT_SCAN"].max(), 1),
            "male_%": round(100 * (g["sex"] == "M").mean(), 1),
            "n_timepoints": (
                "–" if len(tp_vals) == 0 else
                str(tp_vals[0]) if len(tp_vals) == 1 else f"{tps.min()}–{tps.max()} (median {int(tps.median())})"
            ),
            "n_tp_unique": ", ".join(map(str, tp_vals)) if len(tp_vals) <= 6 else f"{len(tp_vals)} values",
            "meanFD_median_mm": round(g["func_mean_fd"].median(), 3),
            "rater_QC_pass": int(g["rater_qc_pass"].sum()),
            "flag_short": int(g["flag_short"].sum()),
            "flag_zero_var": int(g["flag_zero_var"].sum()),
            "flag_motion": int(g["flag_motion"].sum()),
            "flag_any": int(g["flag_any"].sum()),
            "missing_files": int(g["flag_missing_file"].sum()),
        })
    return pd.DataFrame(rows)


def make_figure(df: pd.DataFrame, out_png: Path) -> None:
    """Two panels: (a) subjects per site split by diagnosis; (b) time-series length per site."""
    blue, orange, ink, muted = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
    counts = df.groupby(["site", "dx"]).size().unstack(fill_value=0)
    counts["n"] = counts.sum(axis=1)
    counts = counts.sort_values("n", ascending=True)
    sites = counts.index.tolist()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 0.32 * len(sites) + 1.8), sharey=True)
    y = np.arange(len(sites))
    xmax = float(counts["n"].max())
    ax1.barh(y, counts.get("ASD", 0), color=blue, height=0.62, label="ASD", edgecolor="white", linewidth=1)
    ax1.barh(y, counts.get("TD", 0), left=counts.get("ASD", 0), color=orange, height=0.62, label="TD",
             edgecolor="white", linewidth=1)
    for yi, n in zip(y, counts["n"]):
        ax1.text(n + 0.012 * xmax, yi, str(n), va="center", ha="left", fontsize=8, color=muted, clip_on=True)
    ax1.set_xlim(0, xmax * 1.12)
    ax1.set_yticks(y)
    ax1.set_yticklabels(sites, fontsize=8)
    ax1.set_xlabel("Subjects with C-PAC filt_global ROI series", fontsize=9)
    ax1.set_title("(a) Subjects per site", loc="left", fontsize=10, color=ink)
    ax1.legend(frameon=False, fontsize=8, loc="center right")

    data = [df.loc[df["site"] == s, "aal_n_tp"].dropna().values for s in sites]
    rng = np.random.default_rng(0)
    if df.attrs.get("have_series", True):
        for yi, d in zip(y, data):
            jitter = rng.uniform(-0.18, 0.18, size=len(d))
            ax2.scatter(d, yi + jitter, s=7, color=blue, alpha=0.45, linewidths=0)
        ax2.set_xlabel("Time points per run (AAL series)", fontsize=9)
    else:
        ax2.text(0.5, 0.5, "ROI time series not downloaded yet\n(run data/download_abide.py)",
                 ha="center", va="center", fontsize=9, color=muted, transform=ax2.transAxes)
        ax2.set_xticks([])
    ax2.set_title("(b) Time-series length per site", loc="left", fontsize=10, color=ink)

    for ax in (ax1, ax2):
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.spines["left"].set_color("#c3c2b7")
        ax.spines["bottom"].set_color("#c3c2b7")
        ax.tick_params(colors=muted, labelsize=8)
        ax.grid(False)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def write_report(df: pd.DataFrame, site: pd.DataFrame, cfg: dict, dirs: dict, out_md: Path) -> None:
    q = cfg["qc"]
    tot = site[site["site"] == "TOTAL"].iloc[0]
    n_pass = int(df["rater_qc_pass"].sum())
    n_sites = df["site"].nunique()
    n_subsites = df["SITE_ID"].nunique()
    lines = [
        "# ABIDE I Preprocessed — QC table (Stage 1)"
        + ("" if df.attrs.get("have_series", True) else " — PHENOTYPIC-ONLY PREVIEW"),
        "",
        f"Derivative: C-PAC, strategy `{dirs['strategy']}`, ROI time series AAL-116 and CC200. "
        f"Phenotypic file: `{dirs['phenotypic'].name}`.",
        "",
        "## Counts",
        "",
        f"- Rows in phenotypic file: **{df.attrs['n_pheno_total']}**; without preprocessed outputs "
        f"(`FILE_ID = no_filename`): **{df.attrs['n_no_filename']}**; with ROI series: **{len(df)}** "
        f"({int(tot['ASD'])} ASD / {int(tot['TD'])} TD, {tot['ASD_%']}% ASD) across **{n_sites}** sites "
        f"({n_subsites} PCP SITE_IDs; UM/UCLA/LEUVEN sub-sites merged per config).",
        (f"- Missing derivative files on disk: **{int(tot['missing_files'])}**."
         if df.attrs.get("have_series", True) else
         "- Derivative files on disk: **none yet** (counts below are from the phenotypic file: subjects with `FILE_ID`)."),
        f"- Subjects passing all rater QC flags (nilearn `quality_checked=True` criterion): **{n_pass}** "
        f"({int((df['rater_qc_pass'] & (df['dx']=='ASD')).sum())} ASD / {int((df['rater_qc_pass'] & (df['dx']=='TD')).sum())} TD).",
        f"- Flags (thresholds from config): short series < {q['min_timepoints']} TP: {int(tot['flag_short'])}; "
        f"flat ROIs > {q['max_zero_variance_rois']}: {int(tot['flag_zero_var'])}; "
        f"mean FD > {q['max_mean_fd_mm']} mm: {int(tot['flag_motion'])}; any flag: {int(tot['flag_any'])}.",
        f"- Age (all): {fmt_mean_sd(df['AGE_AT_SCAN'])} y, range {df['AGE_AT_SCAN'].min():.1f}–{df['AGE_AT_SCAN'].max():.1f}; "
        f"male: {100*(df['sex']=='M').mean():.1f}%.",
        (f"- Time points (AAL): min {int(df['aal_n_tp'].min())}, median {int(df['aal_n_tp'].median())}, "
         f"max {int(df['aal_n_tp'].max())}; ROIs: AAL {int(df['aal_n_roi'].dropna().mode().iloc[0])}, "
         f"CC200 {int(df['cc200_n_roi'].dropna().mode().iloc[0])}.")
        if df.attrs.get("have_series", True) else
        "- Time points / ROI counts: **not available yet** — ROI series not downloaded (phenotypic-only preview).",
        "",
        "## Per-site summary",
        "",
    ]
    cols = ["site", "sub_sites", "n", "ASD", "TD", "ASD_%", "age_mean_sd", "male_%", "n_timepoints",
            "meanFD_median_mm", "rater_QC_pass", "flag_any"]
    lines.append(site[cols].to_markdown(index=False))
    lines += [
        "",
        "## Notes",
        "",
        "- `n_timepoints` differs across sites because acquisition length differs (site-specific protocols); "
        "connectivity estimates from short runs are noisier — a candidate covariate/limitation.",
        "- `rater_QC_pass` = nilearn's default filter (rater 1 OK; raters 2 OK/maybe; rater 3 OK). "
        "Not applied here; kept for a sensitivity analysis.",
        "- Flat (zero-variance) ROIs mostly reflect atlas regions outside a site's field of view "
        "(cerebellum/temporal poles). They must be handled identically across datasets before FC.",
        "- No subject is excluded by this script. Exclusion rules are decided once and recorded in PROGRESS.md.",
    ]
    out_md.write_text("\n".join(lines) + "\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", default=None)
    p.add_argument("--strategy", default=None, help="C-PAC strategy (default: config abide.strategy)")
    args = p.parse_args()
    cfg = load_config()
    set_seed(cfg["seed"])
    if args.data_dir:
        cfg["paths"]["raw"] = str(Path(args.data_dir).resolve())
    dirs = abide_dirs(cfg, args.strategy)
    tag = dirs["tag"]
    if not dirs["phenotypic"].exists():
        print(f"[qc_abide] phenotypic file not found: {dirs['phenotypic']}\n"
              f"           run: python data/download_abide.py", file=sys.stderr)
        return 1
    out = Path(cfg["paths"]["qc"])
    out.mkdir(parents=True, exist_ok=True)

    df = build_subject_table(cfg, dirs)
    site = site_summary(df)
    df.to_csv(out / f"{tag}_subjects_qc.csv", index=False)
    site.to_csv(out / f"{tag}_site_summary.csv", index=False)
    make_figure(df, out / f"fig_{tag}_qc.png")
    write_report(df, site, cfg, dirs, out / f"{tag}_qc_report.md")
    print((out / f"{tag}_qc_report.md").read_text())
    print(f"[qc_abide] wrote {out}/{tag}_subjects_qc.csv, {tag}_site_summary.csv, {tag}_qc_report.md, fig_{tag}_qc.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
