#!/usr/bin/env python
"""Download ABIDE I Preprocessed ROI time series (C-PAC; strategy from config, default filt_noglobal) via nilearn.

Source: Preprocessed Connectomes Project, ABIDE I
        https://preprocessed-connectomes-project.org/abide/
        (S3 bucket fcp-indi, open access, no EULA; cite Craddock et al. 2013
        and Di Martino et al. 2014).

What is downloaded (and nothing else):
  * Phenotypic_V1_0b_preprocessed1.csv  (phenotypes + rater QC flags)
  * <FILE_ID>_rois_aal.1D and <FILE_ID>_rois_cc200.1D for every subject
    that has preprocessed outputs (FILE_ID != 'no_filename').

Raw files land in data/raw/ABIDE_pcp/ and are git-ignored.  A manifest with
checksums is written to results/qc/<tag>_download_manifest.json so the exact
data snapshot used for the paper is documented.

Usage (one command, from the project root):
    python data/download_abide.py                # primary strategy (config), ~1035 subjects
    python data/download_abide.py --strategy all # primary + robustness strategy
    python data/download_abide.py --n-subjects 20  # smoke test
    python data/download_abide.py --quality-checked  # nilearn's rater-QC subset only
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import nilearn
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import ABIDE_STRATEGIES, abide_dirs, load_config, md5sum, set_seed  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", default=None, help="override paths.raw from config/config.yaml")
    p.add_argument("--n-subjects", type=int, default=None, help="download only the first N subjects (smoke test)")
    p.add_argument("--quality-checked", action="store_true",
                   help="apply nilearn's default rater-QC filter at download time (default: keep all)")
    p.add_argument("--derivatives", nargs="+", default=None, help="override derivatives list from config")
    p.add_argument("--strategy", default=None, choices=list(ABIDE_STRATEGIES) + ["all"],
                   help="C-PAC strategy (default: config abide.strategy); 'all' = primary + robustness")
    p.add_argument("--verbose", type=int, default=1)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config()
    set_seed(cfg["seed"])
    if args.data_dir:
        cfg["paths"]["raw"] = str(Path(args.data_dir).resolve())
    if args.strategy == "all":
        strategies = [cfg["abide"]["strategy"], cfg["abide"]["robustness_strategy"]]
    else:
        strategies = [args.strategy or cfg["abide"]["strategy"]]
    rc = 0
    for s in strategies:
        rc = max(rc, download_one(cfg, args, s))
    return rc


def download_one(cfg: dict, args: argparse.Namespace, strategy: str) -> int:
    a = cfg["abide"]
    dirs = abide_dirs(cfg, strategy)
    derivatives = args.derivatives or a["derivatives"]
    quality_checked = args.quality_checked or a.get("quality_checked_at_download", False)

    from nilearn.datasets import fetch_abide_pcp

    print(f"[download_abide] nilearn {nilearn.__version__}; pipeline={a['pipeline']} strategy={dirs['strategy']}")
    print(f"[download_abide] derivatives={derivatives} quality_checked={quality_checked} n_subjects={args.n_subjects}")
    print(f"[download_abide] data_dir={cfg['paths']['raw']}")
    t0 = time.time()
    bunch = fetch_abide_pcp(
        data_dir=cfg["paths"]["raw"],
        n_subjects=args.n_subjects,
        pipeline=a["pipeline"],
        band_pass_filtering=dirs["band_pass_filtering"],
        global_signal_regression=dirs["global_signal_regression"],
        derivatives=derivatives,
        quality_checked=quality_checked,
        verbose=args.verbose,
    )
    elapsed = time.time() - t0

    pheno: pd.DataFrame = bunch.phenotypic
    if not isinstance(pheno, pd.DataFrame):  # older nilearn returned a recarray
        pheno = pd.DataFrame(pheno)
    n = len(pheno)
    print(f"[download_abide] fetched {n} subjects in {elapsed/60:.1f} min")

    # ---- manifest with checksums (provenance for the paper) ----
    files = {}
    for d in derivatives:
        ext = ".1D" if d.startswith("rois") else ".nii.gz"
        for fid in pheno["FILE_ID"]:
            fp = dirs["derivatives"] / f"{fid}_{d}{ext}"
            if fp.exists():
                files[fp.name] = {"bytes": fp.stat().st_size, "md5": md5sum(fp)}
            else:
                files[fp.name] = {"missing": True}
    n_missing = sum(1 for v in files.values() if v.get("missing"))

    manifest = {
        "dataset": "ABIDE I Preprocessed (PCP)",
        "source_url": "https://s3.amazonaws.com/fcp-indi/data/Projects/ABIDE_Initiative",
        "pipeline": a["pipeline"],
        "strategy": dirs["strategy"],
        "derivatives": derivatives,
        "quality_checked_at_download": bool(quality_checked),
        "n_subjects_requested": args.n_subjects,
        "n_subjects_fetched": int(n),
        "n_files": len(files),
        "n_files_missing": int(n_missing),
        "phenotypic_csv": str(dirs["phenotypic"]),
        "phenotypic_md5": md5sum(dirs["phenotypic"]) if dirs["phenotypic"].exists() else None,
        "nilearn_version": nilearn.__version__,
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(elapsed, 1),
        "files": files,
    }
    out = Path(cfg["paths"]["qc"])
    out.mkdir(parents=True, exist_ok=True)
    mpath = out / f"{dirs['tag']}_download_manifest.json"
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[download_abide] manifest -> {mpath}  (files={len(files)}, missing={n_missing})")
    return 0 if n_missing == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
