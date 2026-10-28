#!/usr/bin/env python
"""Functional-connectivity features from ROI time series (identical for every dataset).

Pipeline (config: features.*):
    Pearson correlation matrix -> Fisher z (arctanh, r clipped) -> upper triangle (k=1)
    Edges touching a flat (zero-variance) ROI are undefined -> set to z = 0 and counted.

Exclusion (config: qc.exclude_flat_fraction_gt): a subject is dropped if more than
that fraction of regions is flat in any atlas (catastrophic coverage). The list of
excluded subjects is written to results/qc/<dataset>_exclusions.csv.

Outputs: results/features/<dataset>_<variant>.npz with
    X (n_subjects, n_edges) float32, y (1 = patient, 0 = control), site, sub_site,
    age, sex, subject_id, file_id, n_timepoints, rater_qc_pass, n_flat_rois,
    roi_labels, edge_i, edge_j (ROI indices of every feature column)

Usage: python src/features.py --dataset abide [--strategy filt_global]
Output file names use the dataset tag ('abide' = primary strategy, 'abide-<strategy>' otherwise).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import PROJECT_ROOT, abide_dirs, load_config, set_seed  # noqa: E402


# ----------------------------------------------------------------------------- core
def connectivity_vector(ts: np.ndarray, r_clip: float = 0.999999) -> tuple[np.ndarray, np.ndarray]:
    """ts: (n_timepoints, n_rois) -> (fisher-z upper triangle, flat-ROI mask)."""
    ts = np.asarray(ts, dtype=np.float64)
    sd = ts.std(axis=0)
    flat = ~(sd > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.corrcoef(ts, rowvar=False)
    r = np.clip(r, -r_clip, r_clip)
    z = np.arctanh(r)
    z[flat, :] = 0.0
    z[:, flat] = 0.0
    iu = np.triu_indices_from(z, k=1)
    return z[iu].astype(np.float32), flat


def atlas_columns(roi_labels: np.ndarray, variant: str, cfg: dict) -> np.ndarray:
    """Return column indices of the ROI series to keep for a feature variant."""
    labels = np.asarray(roi_labels)
    if variant == "aal90":
        keep = np.array([int(l) <= cfg["atlas"]["aal_cerebral_max_label"] for l in labels])
        if keep.sum() != 90:
            raise RuntimeError(f"aal90 expects 90 cerebral regions, got {keep.sum()}")
        return np.where(keep)[0]
    return np.arange(len(labels))


# ------------------------------------------------------------------------ datasets
def load_abide(cfg: dict, strategy: str | None = None) -> dict:
    """Return dict(meta=DataFrame, series={atlas: {file_id: array}}, labels={atlas: array}, tag=str)."""
    dirs = abide_dirs(cfg, strategy)
    qc = pd.read_csv(PROJECT_ROOT / cfg["paths"]["qc"] / f"{dirs['tag']}_subjects_qc.csv")
    series, labels = {}, {}
    for atlas in ("aal", "cc200"):
        z = np.load(dirs["cache"][atlas])
        labels[atlas] = z["__roi_labels__"]
        series[atlas] = {k: z[k] for k in z.files if k != "__roi_labels__"}
    meta = pd.DataFrame({
        "subject_id": qc["SUB_ID"].astype(str),
        "file_id": qc["FILE_ID"],
        "site": qc["site"],
        "sub_site": qc["SITE_ID"],
        "y": qc["label"].astype(int),
        "dx": qc["dx"],
        "age": qc["AGE_AT_SCAN"].astype(float),
        "sex": qc["sex"],
        "n_timepoints": qc["aal_n_tp"].astype(int),
        "rater_qc_pass": qc["rater_qc_pass"].astype(bool),
        "mean_fd": qc["func_mean_fd"],
    })
    return {"meta": meta, "series": series, "labels": labels, "tag": dirs["tag"],
            "variants": {"aal90": "aal", "aal116": "aal", "cc200": "cc200"}}


def load_adhd200(cfg: dict) -> dict:
    """ADHD-200 Athena AAL time courses (data/download_adhd200.py) + consolidated phenotypes.

    One run per subject: the first resting run (session 1, run 1) — decided a priori.
    Site coding of adhd200_preprocessed_phenotypics.tsv (Bellec et al. 2017): 1 Peking, 2 Brown,
    3 KKI, 4 NeuroIMAGE, 5 NYU, 6 OHSU, 7 Pittsburgh, 8 WashU. DX: 0 = TDC, 1/2/3 = ADHD subtypes.
    """
    a = cfg["adhd200"]
    raw = PROJECT_ROOT / cfg["paths"]["raw"] / "ADHD200"
    pheno_path = next(raw.glob(a["phenotypic_glob"]))
    ph = pd.read_csv(pheno_path, sep="\t" if pheno_path.suffix == ".tsv" else ",")
    ph.columns = [c.strip() for c in ph.columns]
    idc = next(c for c in ph.columns if c.lower().replace(" ", "") in ("scandirid", "scandir_id", "subject", "id", "participant_id"))
    ph["subject"] = ph[idc].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(7)
    z = np.load(PROJECT_ROOT / "data" / "cache" / "adhd200_athena_rois_aal.npz")
    labels = z["__roi_labels__"]
    keys = [k for k in z.files if k != "__roi_labels__"]
    # first run per subject
    first = {}
    for k in sorted(keys):
        site_dir, sub, run = k.split("/")
        sub7 = sub.zfill(7)
        if sub7 not in first or run < first[sub7][1]:
            first[sub7] = (k, run, site_dir)
    rows = []
    for sub7, (k, run, site_dir) in first.items():
        r = ph[ph["subject"] == sub7]
        if len(r) == 0:
            continue
        r = r.iloc[0]
        dx = pd.to_numeric(r.get(a["dx_col"]), errors="coerce")
        if pd.isna(dx):
            continue  # withheld diagnosis (test set of the competition) -> excluded, documented in QC
        site_code = str(r.get(a["site_col"])).replace(".0", "")
        rows.append({"subject_id": sub7, "file_id": k, "site": a["site_map"].get(site_code, site_dir), "sub_site": site_dir,
                     "y": int(dx > 0), "dx": "ADHD" if dx > 0 else "TDC", "age": float(r.get(a["age_col"], np.nan)),
                     "sex": {"1": "M", "0": "F", "M": "M", "F": "F"}.get(str(r.get(a["sex_col"])).replace(".0", ""), "U"),
                     "n_timepoints": int(z[k].shape[0]),
                     # QC_Athena (1 = pass) plays the role of ABIDE's rater QC -> sensitivity subset, never an exclusion
                     "rater_qc_pass": bool(pd.to_numeric(r.get("QC_Athena", 1), errors="coerce") == 1),
                     "mean_fd": np.nan})
    meta = pd.DataFrame(rows)
    series = {"aal": {k: z[k] for k in meta["file_id"]}}
    return {"meta": meta, "series": series, "labels": {"aal": labels}, "tag": "adhd200",
            "variants": {"aal90": "aal", "aal116": "aal"}}


def load_ucla(cfg: dict, subset: str | None = None) -> dict:
    """UCLA-CNP ds000030 rest AAL series (data/download_ucla.py) + participants.tsv.
    subset: None = all patients (SCHZ+BIPOLAR+ADHD) vs CONTROL; 'adhd' | 'schz' | 'bipolar' = one group vs CONTROL."""
    u = cfg["ucla"]
    raw = PROJECT_ROOT / cfg["paths"]["raw"] / "UCLA_CNP"
    part = pd.read_csv(raw / "participants.tsv", sep="\t")
    qc = pd.read_csv(PROJECT_ROOT / cfg["paths"]["qc"] / "ucla_extraction_qc.csv")
    z = np.load(PROJECT_ROOT / "data" / "cache" / "ucla_rois_aal.npz")
    labels = z["__roi_labels__"]
    rows = []
    for k in z.files:
        if k == "__roi_labels__":
            continue
        r = part[part["participant_id"] == k]
        if len(r) == 0:
            continue
        r = r.iloc[0]
        dxs = str(r["diagnosis"]).upper()
        if subset and dxs not in ("CONTROL", subset.upper()):
            continue
        q = qc[qc["subject"] == k]
        # two Siemens scanners (participants.tsv ScannerSerialNumber) = the natural "site" unit inside UCLA-CNP
        scanner = str(r.get("ScannerSerialNumber", "")).replace(".0", "")
        site = u.get("scanner_map", {}).get(scanner, "UCLA")
        rows.append({"subject_id": k, "file_id": k, "site": site, "sub_site": scanner or "UCLA", "y": int(dxs != "CONTROL"),
                     "dx": dxs, "age": float(r["age"]), "sex": str(r["gender"]).upper()[:1],
                     "n_timepoints": int(z[k].shape[0]), "rater_qc_pass": True,
                     "mean_fd": float(q["mean_fd"].iloc[0]) if len(q) else np.nan})
    meta = pd.DataFrame(rows)
    tag = "ucla" if subset is None else f"ucla-{subset.lower()}"
    return {"meta": meta, "series": {"aal": {k: z[k] for k in meta["file_id"]}}, "labels": {"aal": labels},
            "tag": tag, "variants": {"aal90": "aal", "aal116": "aal"}}


LOADERS = {"abide": load_abide, "adhd200": load_adhd200, "ucla": load_ucla,
           "ucla-adhd": lambda cfg: load_ucla(cfg, "adhd"), "ucla-schz": lambda cfg: load_ucla(cfg, "schz"),
           "ucla-bipolar": lambda cfg: load_ucla(cfg, "bipolar")}


# ----------------------------------------------------------------------------- main
def build(dataset: str, cfg: dict, strategy: str | None = None) -> None:
    data = LOADERS[dataset](cfg, strategy) if dataset == "abide" else LOADERS[dataset](cfg)
    tag = data.get("tag", dataset)
    dataset = tag
    meta: pd.DataFrame = data["meta"]
    thr = cfg["qc"]["exclude_flat_fraction_gt"]
    fcfg = cfg["features"]

    # 1) exclusion on catastrophic coverage (any atlas)
    flat_frac = {}
    for atlas, ser in data["series"].items():
        flat_frac[atlas] = meta["file_id"].map(lambda f: float((~(ser[f].std(axis=0) > 0)).mean())).values
    worst = np.max(np.vstack(list(flat_frac.values())), axis=0)
    excl = meta[worst > thr].copy()
    excl["worst_flat_fraction"] = worst[worst > thr]
    excl["reason"] = f"flat ROI fraction > {thr} in at least one atlas"
    out_qc = PROJECT_ROOT / cfg["paths"]["qc"]
    excl.to_csv(out_qc / f"{dataset}_exclusions.csv", index=False)
    keep = worst <= thr
    meta = meta[keep].reset_index(drop=True)
    print(f"[features:{dataset}] excluded {int((~keep).sum())} subject(s) (flat fraction > {thr}); kept {len(meta)}")

    # 2) features per variant
    out_dir = PROJECT_ROOT / cfg["paths"]["results"] / "features"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for variant in cfg["atlas"]["variants"]:
        if variant not in data["variants"]:
            continue
        atlas = data["variants"][variant]
        cols = atlas_columns(data["labels"][atlas], variant, cfg)
        roi_labels = np.asarray(data["labels"][atlas])[cols]
        X, n_flat = [], []
        for f in meta["file_id"]:
            vec, flat = connectivity_vector(data["series"][atlas][f][:, cols], fcfg["r_clip"])
            X.append(vec)
            n_flat.append(int(flat.sum()))
        X = np.vstack(X)
        n_roi = len(cols)
        ei, ej = np.triu_indices(n_roi, k=1)
        s = lambda col: np.asarray(meta[col].astype(str).tolist(), dtype=str)  # plain unicode arrays (no pickles)
        np.savez_compressed(
            out_dir / f"{dataset}_{variant}.npz",
            X=X, y=meta["y"].to_numpy().astype(np.int8), site=s("site"), sub_site=s("sub_site"),
            age=meta["age"].to_numpy().astype(np.float32), sex=s("sex"), subject_id=s("subject_id"),
            file_id=s("file_id"), n_timepoints=meta["n_timepoints"].to_numpy().astype(np.int32),
            rater_qc_pass=meta["rater_qc_pass"].to_numpy().astype(bool), n_flat_rois=np.array(n_flat, dtype=np.int16),
            roi_labels=np.asarray(roi_labels.tolist(), dtype=str), edge_i=ei.astype(np.int16), edge_j=ej.astype(np.int16),
        )
        zero_edges = float((X == 0).mean())
        summary[variant] = {
            "n_subjects": int(len(meta)), "n_patients": int(meta["y"].sum()), "n_controls": int((meta["y"] == 0).sum()),
            "n_rois": int(n_roi), "n_edges": int(X.shape[1]), "subjects_with_flat_rois": int(np.sum(np.array(n_flat) > 0)),
            "fraction_zeroed_edges": round(zero_edges, 5), "z_mean": round(float(X.mean()), 4), "z_sd": round(float(X.std()), 4),
        }
        print(f"[features:{dataset}] {variant}: X={X.shape}, flat-ROI subjects={summary[variant]['subjects_with_flat_rois']}, "
              f"zeroed edges={100*zero_edges:.3f}%")
    with open(out_dir / f"{dataset}_features_summary.json", "w") as f:
        json.dump(summary, f, indent=2)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", default="abide", choices=sorted(LOADERS))
    p.add_argument("--strategy", default=None, help="ABIDE only: C-PAC strategy (default: config abide.strategy)")
    args = p.parse_args()
    cfg = load_config()
    set_seed(cfg["seed"])
    build(args.dataset, cfg, args.strategy)
    return 0


if __name__ == "__main__":
    sys.exit(main())
