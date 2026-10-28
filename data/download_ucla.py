#!/usr/bin/env python
"""UCLA Consortium for Neuropsychiatric Phenomics (OpenNeuro ds000030) — resting-state
AAL-116 time series from the RELEASED fMRIPrep derivatives (no fMRIPrep run here).

Source: OpenNeuro ds000030, release R1.0.5, public S3 bucket "openneuro" (no login, CC0).
        Data descriptors: Poldrack et al., Sci Data 3:160110 (2016); Gorgolewski et al.,
        F1000Research 6:1262 (2017) — the preprocessed derivatives.
Per subject we download from
    ds000030/ds000030_R1.0.5/uncompressed/derivatives/fmriprep/sub-XXXXX/func/
        sub-XXXXX_task-rest_bold_space-MNI152NLin2009cAsym_preproc.nii.gz   (~100 MB)
        sub-XXXXX_task-rest_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz
        sub-XXXXX_task-rest_bold_confounds.tsv
and extract mean AAL-116 time series with nilearn (NiftiLabelsMasker):
    confounds = mean WM, mean CSF (or, when the release has no CSF column, the first aCompCor
                component as WM/CSF-noise proxy), 6 motion parameters (NO global signal), linear detrend,
    band-pass 0.009-0.08 Hz (TR from the NIfTI header, nominally 2 s)
— i.e. the closest feasible match to ADHD-200 Athena and ABIDE C-PAC filt_noglobal.
The NIfTI files are deleted after extraction (--keep-nifti to keep them); the
time series (TSV, header = AAL region codes), confounds, participants.tsv and a
checksum manifest are kept. Then everything is packed into
data/cache/ucla_rois_aal.npz (key = subject id) for the pipeline.

Usage:  python data/download_ucla.py [--workers 3] [--subjects sub-10159 sub-10171] [--keep-nifti]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "UCLA_CNP"
TS_DIR = RAW / "timeseries"
NII_DIR = RAW / "nifti_tmp"
CACHE = ROOT / "data" / "cache"
QC = ROOT / "results" / "qc"

BUCKET = "https://openneuro.s3.amazonaws.com"
PREFIX = "ds000030/ds000030_R1.0.5/uncompressed/"
FMRIPREP = PREFIX + "derivatives/fmriprep/"
S3NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

CONFOUND_NAMES = {  # old fMRIPrep (<1.1) names -> new names; we accept either
    "WhiteMatter": "white_matter", "CSF": "csf", "aCompCor00": "a_comp_cor_00",
    "X": "trans_x", "Y": "trans_y", "Z": "trans_z", "RotX": "rot_x", "RotY": "rot_y", "RotZ": "rot_z",
    "FramewiseDisplacement": "framewise_displacement",
}


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def s3_list(prefix: str, delimiter: str | None = None) -> tuple[list[str], list[str]]:
    """Return (keys, common prefixes) under prefix in the public bucket (handles pagination)."""
    keys, prefixes, token = [], [], None
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if delimiter:
            q["delimiter"] = delimiter
        if token:
            q["continuation-token"] = token
        url = f"{BUCKET}/?{urllib.parse.urlencode(q)}"
        with urllib.request.urlopen(url, timeout=60) as r:
            root = ET.fromstring(r.read())
        keys += [e.text for e in root.findall("s3:Contents/s3:Key", S3NS)]
        prefixes += [e.text for e in root.findall("s3:CommonPrefixes/s3:Prefix", S3NS)]
        trunc = root.findtext("s3:IsTruncated", default="false", namespaces=S3NS)
        token = root.findtext("s3:NextContinuationToken", default=None, namespaces=S3NS)
        if trunc != "true" or not token:
            break
    return keys, prefixes


def fetch(key: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(f"{BUCKET}/{urllib.parse.quote(key)}", timeout=300) as r, open(tmp, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    tmp.rename(dest)
    return dest


def load_confounds(path: Path) -> tuple[np.ndarray, list[str], float]:
    df = pd.read_csv(path, sep="\t")
    cols = {}
    for old, new in CONFOUND_NAMES.items():
        if old in df.columns:
            cols[new] = old
        elif new in df.columns:
            cols[new] = new
    # The ds000030 R1.0.5 fMRIPrep (1.0-era) confounds carry WhiteMatter but NO mean-CSF column;
    # the first aCompCor component (WM+CSF noise PC) is used as the CSF/WM noise proxy in that case.
    csf_col = "csf" if "csf" in cols else ("a_comp_cor_00" if "a_comp_cor_00" in cols else None)
    wanted = ["white_matter"] + ([csf_col] if csf_col else []) + ["trans_x", "trans_y", "trans_z", "rot_x", "rot_y", "rot_z"]
    missing = [w for w in wanted if w not in cols]
    if missing:
        raise RuntimeError(f"confounds missing {missing}; columns = {list(df.columns)[:30]}")
    C = df[[cols[w] for w in wanted]].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    C = np.nan_to_num(C, nan=0.0)  # first-row n/a for derivatives
    fd = pd.to_numeric(df[cols["framewise_displacement"]], errors="coerce") if "framewise_displacement" in cols else pd.Series(dtype=float)
    return C, wanted, float(fd.mean()) if len(fd) else float("nan")


def process_subject(sub: str, aal, keep_nifti: bool) -> dict:
    """Download rest derivatives, extract AAL series, clean up. Never raises: returns a QC row with status."""
    try:
        return _process_subject(sub, aal, keep_nifti)
    except Exception as e:  # noqa: BLE001
        return {"subject": sub, "status": f"failed: {type(e).__name__}: {e}"}


def _process_subject(sub: str, aal, keep_nifti: bool) -> dict:
    import nibabel as nib
    from nilearn.maskers import NiftiLabelsMasker

    base = f"{FMRIPREP}{sub}/func/{sub}_task-rest_bold"
    k_pre = base + "_space-MNI152NLin2009cAsym_preproc.nii.gz"
    k_msk = base + "_space-MNI152NLin2009cAsym_brainmask.nii.gz"
    k_cnf = base + "_confounds.tsv"
    out_ts = TS_DIR / f"{sub}_task-rest_aal116.tsv"
    row = {"subject": sub, "status": "ok"}
    if out_ts.exists():
        x = np.loadtxt(out_ts, delimiter="\t", skiprows=1, ndmin=2)
        row.update({"n_timepoints": int(x.shape[0]), "n_rois": int(x.shape[1]),
                    "n_flat_rois": int(np.sum(~(x.std(axis=0) > 0))), "status": "cached"})
        cnf = TS_DIR / f"{sub}_task-rest_confounds.tsv"
        if cnf.exists():
            row["mean_fd"] = load_confounds(cnf)[2]
        return row
    t0 = time.time()
    try:
        p_pre = fetch(k_pre, NII_DIR / Path(k_pre).name)
        p_msk = fetch(k_msk, NII_DIR / Path(k_msk).name)
        p_cnf = fetch(k_cnf, TS_DIR / f"{sub}_task-rest_confounds.tsv")
    except Exception as e:  # noqa: BLE001
        return {"subject": sub, "status": f"download_failed: {e}"}
    try:
        row["md5_preproc"] = md5sum(p_pre)
        row["bytes_preproc"] = p_pre.stat().st_size
        img = nib.load(p_pre)
        tr = float(img.header.get_zooms()[3])
        C, cnames, mean_fd = load_confounds(p_cnf)
        n_vol = img.shape[3]
        if len(C) != n_vol:
            return {"subject": sub, "status": f"confound_length_mismatch: {len(C)} vs {n_vol}"}
        masker = NiftiLabelsMasker(labels_img=aal["maps"], mask_img=str(p_msk), standardize=None, detrend=True,
                                   low_pass=0.08, high_pass=0.009, t_r=tr, resampling_target="data", verbose=0)
        X = masker.fit_transform(img, confounds=C).astype(np.float32)
        ids = [v for k, v in masker.region_ids_.items() if k != "background"]
        if len(ids) != X.shape[1]:
            return {"subject": sub, "status": "region_id_mismatch"}
        # guarantee the full AAL-116 column set in canonical (sorted code) order; absent regions -> zeros (flat)
        full = np.zeros((X.shape[0], len(aal["indices"])), dtype=np.float32)
        pos = {int(code): j for j, code in enumerate(aal["indices"])}
        for col, rid in enumerate(ids):
            full[:, pos[int(rid)]] = X[:, col]
        header = "\t".join(str(c) for c in aal["indices"])
        np.savetxt(out_ts, full, delimiter="\t", header=header, comments="", fmt="%.6f")
        row.update({"n_timepoints": int(full.shape[0]), "n_rois": int(full.shape[1]), "tr": tr,
                    "n_flat_rois": int(np.sum(~(full.std(axis=0) > 0))), "mean_fd": mean_fd,
                    "confounds": ",".join(cnames), "seconds": round(time.time() - t0, 1)})
        return row
    finally:
        if not keep_nifti and out_ts.exists():  # keep the NIfTI only while the subject is unresolved
            p_pre.unlink(missing_ok=True)
            p_msk.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--subjects", nargs="+", default=None, help="subset (smoke test)")
    ap.add_argument("--keep-nifti", action="store_true")
    args = ap.parse_args()
    for d in (RAW, TS_DIR, NII_DIR, CACHE, QC):
        d.mkdir(parents=True, exist_ok=True)
    t_all = time.time()

    # participants + fmriprep description
    fetch(PREFIX + "participants.tsv", RAW / "participants.tsv")
    for k in ("dataset_description.json",):
        try:
            fetch(FMRIPREP + k, RAW / f"fmriprep_{k}")
        except Exception as e:  # noqa: BLE001
            print(f"[ucla] no {k} in derivatives ({e})")
    part = pd.read_csv(RAW / "participants.tsv", sep="\t")
    print(f"[ucla] participants.tsv: {len(part)} rows; columns={list(part.columns)[:12]}")

    # subjects with released rest fMRIPrep derivatives
    _, prefixes = s3_list(FMRIPREP, delimiter="/")
    subs = sorted(p.rstrip("/").split("/")[-1] for p in prefixes if "/sub-" in p)
    print(f"[ucla] fmriprep subject folders: {len(subs)}")
    if args.subjects:
        subs = [s for s in subs if s in set(args.subjects)]
    have_rest = []
    for s in subs:
        keys, _ = s3_list(f"{FMRIPREP}{s}/func/{s}_task-rest_bold_space-MNI152NLin2009cAsym_preproc.nii.gz")
        if keys:
            have_rest.append(s)
    print(f"[ucla] subjects with rest preproc in MNI space: {len(have_rest)}")

    from nilearn.datasets import fetch_atlas_aal
    aal_b = fetch_atlas_aal(version="SPM12", data_dir=str(ROOT / "data" / "raw" / "atlases"))
    # nilearn >= 0.13 lists the background (code 0, "Background") first: drop it -> 116 regions, codes 2001..9170
    pairs = [(int(i), str(l)) for i, l in zip(aal_b.indices, aal_b.labels) if int(i) != 0 and str(l).lower() != "background"]
    aal = {"maps": aal_b.maps, "indices": [i for i, _ in pairs], "labels": [l for _, l in pairs]}
    if len(aal["indices"]) != 116:
        raise RuntimeError(f"expected 116 AAL regions, got {len(aal['indices'])}: {aal['indices'][:5]}...")
    print(f"[ucla] AAL atlas: {len(aal['indices'])} regions, first={aal['indices'][:3]}, last={aal['indices'][-1]}")

    if not args.keep_nifti:  # leftovers from an interrupted run whose series already exist
        for p in NII_DIR.glob("*.nii.gz*"):
            sub = p.name.split("_")[0]
            if (TS_DIR / f"{sub}_task-rest_aal116.tsv").exists() or p.name.endswith(".part"):
                p.unlink(missing_ok=True)

    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(process_subject, s, aal, args.keep_nifti): s for s in have_rest}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            rows.append(r)
            print(f"[ucla] {i}/{len(have_rest)} {r['subject']}: {r.get('status')} "
                  f"tp={r.get('n_timepoints')} flat={r.get('n_flat_rois')} fd={r.get('mean_fd', float('nan')):.3f}", flush=True)
    qc = pd.DataFrame(rows).sort_values("subject")
    qc.to_csv(QC / "ucla_extraction_qc.csv", index=False)

    # pack
    arrays = {}
    for p in sorted(TS_DIR.glob("*_task-rest_aal116.tsv")):
        arrays[p.name.split("_")[0]] = np.loadtxt(p, delimiter="\t", skiprows=1, ndmin=2, dtype=np.float32)
    arrays["__roi_labels__"] = np.array([str(c) for c in aal["indices"]], dtype=str)
    out = CACHE / "ucla_rois_aal.npz"
    np.savez_compressed(out, **arrays)
    manifest = {
        "dataset": "UCLA-CNP ds000030 R1.0.5 fMRIPrep derivatives (rest, MNI152NLin2009cAsym)",
        "source": f"{BUCKET}/{FMRIPREP}", "n_subjects_fmriprep": len(subs), "n_subjects_rest": len(have_rest),
        "n_series_packed": len(arrays) - 1, "extraction": "nilearn NiftiLabelsMasker, AAL SPM12 116, detrend, "
        "band-pass 0.009-0.08 Hz, confounds WM+CSF+6 motion, no GSR",
        "per_subject": {r["subject"]: {k: v for k, v in r.items() if k != "subject"} for r in rows},
        "participants_md5": md5sum(RAW / "participants.tsv"),
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time() - t_all, 1),
    }
    with open(QC / "ucla_download_manifest.json", "w") as f:
        json.dump(manifest, f, indent=1, default=str)
    print(f"[ucla] packed {len(arrays)-1} subjects -> {out} ({out.stat().st_size/1e6:.1f} MB) in {(time.time()-t_all)/60:.1f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
