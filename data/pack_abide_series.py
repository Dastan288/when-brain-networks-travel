#!/usr/bin/env python
"""Pack downloaded ABIDE ROI time series (.1D) into one compressed .npz per atlas.

Purely a convenience/caching step (numpy only, no other deps): the .1D files are
the source of truth; the .npz files are regenerated from them and git-ignored.

Output: data/cache/abide_<strategy>_rois_aal.npz, data/cache/abide_<strategy>_rois_cc200.npz
        keys = FILE_ID, values = float32 array (n_timepoints, n_rois)
        plus key "__roi_labels__" (atlas column labels from the .1D header)
Usage:  python data/pack_abide_series.py [--strategy filt_noglobal|filt_global]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ABIDE_pcp"
OUT = ROOT / "data" / "cache"


def read_1d(path: Path) -> tuple[np.ndarray, list[str]]:
    with open(path) as f:
        first = f.readline()
    labels = [t.lstrip("#") for t in first.strip().split()] if first.startswith("#") else []
    x = np.loadtxt(path, comments="#", ndmin=2, dtype=np.float32)
    return x, labels


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strategy", default="filt_noglobal",
                    choices=["filt_noglobal", "filt_global", "nofilt_noglobal", "nofilt_global"])
    args = ap.parse_args()
    strategy_dir = RAW / "cpac" / args.strategy
    pheno = RAW / "Phenotypic_V1_0b_preprocessed1.csv"
    with open(pheno, newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["FILE_ID"] != "no_filename"]
    file_ids = [r["FILE_ID"] for r in rows]
    OUT.mkdir(parents=True, exist_ok=True)
    for atlas in ("aal", "cc200"):
        arrays, labels_ref, missing = {}, None, []
        for fid in file_ids:
            p = strategy_dir / f"{fid}_rois_{atlas}.1D"
            if not p.exists():
                missing.append(fid)
                continue
            x, labels = read_1d(p)
            if labels_ref is None:
                labels_ref = labels
            elif labels and labels != labels_ref:
                raise RuntimeError(f"ROI label order differs in {p.name}")
            arrays[fid] = x
        arrays["__roi_labels__"] = np.array(labels_ref or [], dtype=str)
        out = OUT / f"abide_{args.strategy}_rois_{atlas}.npz"
        np.savez_compressed(out, **arrays)
        n_tp = [a.shape[0] for k, a in arrays.items() if k != "__roi_labels__"]
        print(f"[pack] {atlas}: {len(arrays)-1} subjects, missing={len(missing)}, "
              f"n_rois={len(labels_ref or [])}, n_tp min/max={min(n_tp)}/{max(n_tp)} -> {out} "
              f"({out.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
