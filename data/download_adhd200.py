#!/usr/bin/env python
"""Download ADHD-200 Preprocessed (Athena pipeline) AAL regional time courses + phenotypes.

Source: The Neuro Bureau ADHD-200 Preprocessed repository, NITRC project
        "ADHD-200 Preprocessed" (group_id=383), open access, no EULA.
        Data descriptor: Bellec et al., NeuroImage 144(Pt B):275-286, 2017,
        doi:10.1016/j.neuroimage.2016.06.034
Athena preprocessing (Bellec et al. 2017): nuisance regression of mean WM, mean CSF,
6 motion parameters and a 3rd-order polynomial (NO global-signal regression),
band-pass 0.009-0.08 Hz ("corrected filtering" = filtfix release), 6 mm FWHM,
MNI152 4 mm. Regional time courses: AFNI .1D, tab-separated.

Files fetched (NITRC file-release IDs):
    3419  AAL time courses, corrected filtering (training release)
    3595  AAL time courses, test release
    3916  training-set phenotypic information
    3917  test-set phenotypic information
    9024  adhd200_preprocessed_phenotypics.tsv (consolidated phenotypes, 2016-05-26)

Everything lands in data/raw/ADHD200/ (git-ignored). The time courses are then
packed into data/cache/adhd200_athena_rois_aal.npz (key = "<site>/<subject>/<run>")
and a checksum manifest is written to results/qc/adhd200_download_manifest.json.

Usage:  python data/download_adhd200.py [--skip-download]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tarfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ADHD200"
CACHE = ROOT / "data" / "cache"
QC = ROOT / "results" / "qc"

NITRC = "https://www.nitrc.org/frs/downloadlink.php/{id}"
FILES = {
    "3419": "ADHD200_AAL_TCs_filtfix.tar.gz",
    "3595": "ADHD200_AAL_TCs_TestRelease.tar.gz",
    "3916": "allSubs_trainingSet_phenotypic.csv",
    "3917": "allSubs_testSet_phenotypic.csv",
    "9024": "adhd200_preprocessed_phenotypics.tsv",
}
# Expected names are only a fallback; the server's Content-Disposition name wins.


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def download(url: str, fallback_name: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "wbnt-downloader/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        cd = r.headers.get("Content-Disposition", "")
        m = re.search(r'filename="?([^";]+)"?', cd)
        name = m.group(1) if m else (Path(r.geturl()).name if "." in Path(r.geturl()).name else fallback_name)
        out = dest_dir / name
        if out.exists() and out.stat().st_size > 0:
            print(f"[adhd200] exists, skip: {out.name} ({out.stat().st_size/1e6:.1f} MB)")
            return out
        tmp = out.with_suffix(out.suffix + ".part")
        t0, n = time.time(), 0
        with open(tmp, "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                n += len(chunk)
        tmp.rename(out)
        print(f"[adhd200] downloaded {out.name}: {n/1e6:.1f} MB in {time.time()-t0:.0f}s")
        return out


def extract(tar_path: Path, dest: Path) -> None:
    marker = dest / f".extracted_{tar_path.name}"
    if marker.exists():
        print(f"[adhd200] already extracted: {tar_path.name}")
        return
    print(f"[adhd200] extracting {tar_path.name} ...")
    with tarfile.open(tar_path) as tf:
        try:
            tf.extractall(dest, filter="data")
        except TypeError:  # python < 3.12
            tf.extractall(dest)
    marker.touch()


def parse_tc_file(path: Path) -> tuple[np.ndarray, list[str], dict]:
    """Parse an Athena *_TCs.1D file. Returns (T x R array, roi column names, meta)."""
    with open(path) as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    header = lines[0].split("\t") if "\t" in lines[0] else lines[0].split()
    is_header = any(not _is_float(t) for t in header)
    meta = {}
    if is_header:
        roi_idx = [i for i, t in enumerate(header) if t.lower().startswith("mean")]
        if not roi_idx:  # unknown header: keep every column whose entries are numeric in row 2
            row = lines[1].split("\t") if "\t" in lines[1] else lines[1].split()
            roi_idx = [i for i, t in enumerate(row) if _is_float(t) and not header[i].lower() in ("sub", "session", "run")]
        names = [header[i] for i in roi_idx]
        rows = []
        for ln in lines[1:]:
            toks = ln.split("\t") if "\t" in ln else ln.split()
            rows.append([float(toks[i]) for i in roi_idx])
            if not meta:
                for key in ("File", "Sub", "Session", "Run"):
                    if key in header:
                        meta[key.lower()] = toks[header.index(key)]
        x = np.asarray(rows, dtype=np.float32)
    else:
        x = np.loadtxt(path, ndmin=2, dtype=np.float32)
        names = [f"Mean_{i+1}" for i in range(x.shape[1])]
    return x, names, meta


def _roi_code(name: str) -> str:
    """'Mean_2001  ' (Athena 3dROIstats header) -> '2001' (AAL code, same convention as the ABIDE/UCLA caches)."""
    s = name.strip()
    m = re.match(r"(?i)mean_?(\d+)$", s)
    return m.group(1) if m else s


def _is_float(t: str) -> bool:
    try:
        float(t)
        return True
    except ValueError:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-download", action="store_true", help="only (re)pack already downloaded files")
    ap.add_argument("--prefix", default="sfnwmrda",
                    help="Athena file-name prefix to pack. The filtfix/TestRelease tarballs ship two variants per run: "
                         "sfnwmrda* = band-pass filtered (0.009-0.08 Hz; project default, matches ABIDE filt_* and UCLA) "
                         "and snwmrda* = unfiltered. Both share the same subject/run key, so exactly one is packed.")
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    QC.mkdir(parents=True, exist_ok=True)

    t_all = time.time()
    got = {}
    if not args.skip_download:
        for fid, fallback in FILES.items():
            got[fid] = download(NITRC.format(id=fid), fallback, RAW)
    else:
        for fid, fallback in FILES.items():
            cands = [p for p in RAW.iterdir() if p.is_file() and not p.name.endswith(".part")]
            got[fid] = next((p for p in cands if p.name == fallback), None)
    tarballs = [p for p in RAW.iterdir()
                if p.is_file() and not p.name.startswith(".") and p.name.endswith((".tar.gz", ".tgz", ".tar"))]
    for tb in tarballs:
        extract(tb, RAW)

    # ---- pack every AAL time-course file we can find
    all_tc = sorted(p for p in RAW.rglob("*.1D") if "aal" in p.name.lower() or "aal" in str(p.parent).lower())
    if not all_tc:
        all_tc = sorted(RAW.rglob("*TCs*.1D"))
    print(f"[adhd200] found {len(all_tc)} time-course files")
    if not all_tc:
        print("[adhd200] no *_TCs.1D files under data/raw/ADHD200 — download the NITRC tarballs first "
              "(a free NITRC login is required; see docstring)", file=sys.stderr)
        return 2
    by_prefix = {}
    for p in all_tc:
        m = re.match(r"([a-z]+?)(\d{7})_", p.name)
        by_prefix.setdefault(m.group(1) if m else p.name, 0)
        by_prefix[m.group(1) if m else p.name] += 1
    print(f"[adhd200] file-name variants: {by_prefix}")
    tc_files = [p for p in all_tc if p.name.startswith(args.prefix)]
    print(f"[adhd200] packing prefix '{args.prefix}': {len(tc_files)} files "
          f"(skipping {len(all_tc) - len(tc_files)} other-variant / literal-glob files)")
    arrays, index, names_ref, skipped = {}, [], None, []
    for p in tc_files:
        x, names, meta = parse_tc_file(p)
        names = [_roi_code(n) for n in names]
        if x.ndim != 2 or x.shape[0] == 0:
            skipped.append({"file": str(p.relative_to(RAW)), "reason": f"no data rows (shape {x.shape})"})
            continue
        if names_ref is None:
            names_ref = names
            print(f"[adhd200] first file {p.relative_to(RAW)}: shape={x.shape}, cols={names[:3]}...{names[-1]}, meta={meta}")
        elif names != names_ref:
            skipped.append({"file": str(p.relative_to(RAW)), "reason": f"column mismatch {len(names)} vs {len(names_ref)}"})
            continue
        rel = p.relative_to(RAW)
        parts = rel.parts
        # layout: <release>/<site>/<subject>/<file>  (fallback: use the path itself)
        sub = meta.get("sub") or next((q for q in parts[::-1][1:] if q.isdigit()), rel.stem)
        site = parts[-3] if len(parts) >= 3 else "unknown"
        release = parts[0] if len(parts) >= 4 else "unknown"
        run = meta.get("run") or (re.search(r"rest_(\d+)", p.name).group(1) if re.search(r"rest_(\d+)", p.name) else "1")
        session = meta.get("session") or (re.search(r"session_(\d+)", p.name).group(1) if re.search(r"session_(\d+)", p.name) else "1")
        key = f"{site}/{sub}/s{session}r{run}"
        arrays[key] = x
        index.append({"key": key, "release": release, "site_dir": site, "subject": str(sub), "session": session, "run": run,
                      "n_timepoints": int(x.shape[0]), "n_rois": int(x.shape[1]), "file": str(rel),
                      "n_flat_rois": int(np.sum(~(x.std(axis=0) > 0)))})
    arrays["__roi_labels__"] = np.array(names_ref or [], dtype=str)
    out = CACHE / "adhd200_athena_rois_aal.npz"
    np.savez_compressed(out, **arrays)
    with open(QC / "adhd200_timeseries_index.json", "w") as f:
        json.dump({"prefix": args.prefix, "n_packed": len(index), "skipped": skipped, "runs": index}, f, indent=1)
    n_sub = len({r["subject"] for r in index})
    print(f"[adhd200] packed {len(index)} runs from {n_sub} subjects, {len(names_ref or [])} ROIs -> {out.name}; "
          f"skipped {len(skipped)} files (listed in results/qc/adhd200_timeseries_index.json)")

    manifest = {
        "dataset": "ADHD-200 Preprocessed (Athena)", "source": "https://www.nitrc.org/frs/?group_id=383",
        "descriptor_doi": "10.1016/j.neuroimage.2016.06.034",
        "files": {p.name: {"bytes": p.stat().st_size, "md5": md5sum(p)} for p in RAW.iterdir()
                  if p.is_file() and not p.name.startswith(".")},
        "n_timeseries_files": len(tc_files), "n_rois": len(names_ref or []),
        "packed": str(out), "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time() - t_all, 1),
    }
    with open(QC / "adhd200_download_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[adhd200] packed {len(index)} series -> {out} ({out.stat().st_size/1e6:.1f} MB); manifest written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
