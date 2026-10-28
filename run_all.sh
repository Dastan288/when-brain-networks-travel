#!/usr/bin/env bash
# Regenerate everything from scratch. Run from the project root:  bash run_all.sh [--data-only]
# Stages: 0 env -> 1 downloads (ABIDE, ADHD-200, UCLA-CNP) -> 2 QC tables -> 3 features -> 4 experiments.
# Downloads need internet access to S3 (fcp-indi, openneuro) and NITRC; they are idempotent
# (already-downloaded files are skipped), so re-running is cheap.
set -euo pipefail
cd "$(dirname "$0")"

# ---- 0. interpreter: pinned deps need Python >= 3.11; use/create .venv ----
find_python() {
  for c in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$c" >/dev/null 2>&1; then
      if "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
        echo "$c"; return 0
      fi
    fi
  done
  return 1
}
if [ ! -x .venv/bin/python ]; then
  if PY=$(find_python); then
    echo "== [0] creating .venv with $($PY --version 2>&1)"; "$PY" -m venv .venv
  elif command -v conda >/dev/null 2>&1; then
    echo "== [0] no python>=3.11 found; creating conda env in ./.venv (python 3.12)"
    conda create -y -q -p ./.venv python=3.12 >/dev/null
  else
    echo "ERROR: need Python >= 3.11 (or conda). Install one, then re-run." >&2; exit 1
  fi
fi
PY=.venv/bin/python
echo "== using $($PY --version 2>&1) at $PY"
"$PY" -m pip install -q --upgrade pip
"$PY" -m pip install -q -r requirements.txt

echo "== [1a] ABIDE I Preprocessed: C-PAC filt_noglobal (primary) + filt_global (robustness), AAL + CC200"
"$PY" data/download_abide.py --strategy all
"$PY" data/pack_abide_series.py --strategy filt_noglobal
"$PY" data/pack_abide_series.py --strategy filt_global

echo "== [1b] ADHD-200 Preprocessed (Athena): AAL time courses + phenotypes (NITRC)"
# NITRC requires a (free) login for these files: download them manually into data/raw/ADHD200/
# (IDs 3419, 3595, 3916, 3917 via https://www.nitrc.org/frs/downloadlink.php/<ID> and
#  https://www.nitrc.org/frs/download.php/9024/adhd200_preprocessed_phenotypics.tsv), then this packs them.
"$PY" data/download_adhd200.py --skip-download || echo "   (ADHD-200 files not found yet — see comment above)"

echo "== [1c] UCLA-CNP ds000030: rest fMRIPrep derivatives -> AAL-116 time series (OpenNeuro S3)"
"$PY" data/download_ucla.py --workers 3

echo "== [1d] AIDA 2026 Procedia template -> paper/template.docx"
[ -f paper/template.docx ] || curl -fsSL -o paper/template.docx "https://aida.scika.org/CONTENTS/downloads/template.docx" || echo "   (template download failed; fetch it manually)"

echo "== [2] QC tables"
"$PY" src/qc_abide.py
"$PY" src/qc_abide.py --strategy filt_global
[ -f data/cache/adhd200_athena_rois_aal.npz ] && "$PY" src/qc_dataset.py --dataset adhd200
[ -f data/cache/ucla_rois_aal.npz ] && "$PY" src/qc_dataset.py --dataset ucla

if [ "${1:-}" = "--data-only" ]; then echo "== data stage done"; exit 0; fi

echo "== [3] features (AAL-90 primary; AAL-116 / CC200 robustness)"
"$PY" src/features.py --dataset abide
"$PY" src/features.py --dataset abide --strategy filt_global
[ -f data/cache/adhd200_athena_rois_aal.npz ] && "$PY" src/features.py --dataset adhd200
if [ -f data/cache/ucla_rois_aal.npz ]; then
  for d in ucla ucla-adhd ucla-schz ucla-bipolar; do "$PY" src/features.py --dataset "$d"; done
fi

echo "== [4] E1 within-dataset leave-one-site-out (ABIDE primary + GSR robustness, ADHD-200)"
"$PY" src/run_e1.py --dataset abide --resume
"$PY" src/run_e1.py --dataset abide-filt_global --variants aal90 --samples primary --skip-random --resume
[ -f results/features/adhd200_aal90.npz ] && "$PY" src/run_e1.py --dataset adhd200 --variants aal90 aal116 --resume

echo "== [5] E2/E3 cross-dataset transfer matrix + ComBat (raw / reference-only / new-batch)"
"$PY" src/run_e2.py --views abide adhd200 ucla ucla-adhd --resume
"$PY" src/run_e3b_controls.py
echo "== [5b] GSR-matched control: ABIDE filt_global <-> ADHD-200"
"$PY" src/run_e2.py --views abide-filt_global adhd200 --models lr svm agesex_lr \
      --pairs "abide-filt_global>adhd200" "adhd200>abide-filt_global" --out results/e2_gsr --resume
"$PY" src/run_e3b_controls.py --out results/e2_gsr --models lr svm

echo "== [6] E5 demographic adjustment (age+sex appended; edges residualized on age+sex, train-only)"
"$PY" src/run_e5_demographics.py --resume

echo "== [7] E6 repeated site-mixed CV (20 repeats) + site-level uncertainty (cluster bootstrap)"
"$PY" src/run_e6_resampling.py --views abide adhd200 ucla --models lr svm --repeats 20 --resume
"$PY" src/run_e6_resampling.py --views abide adhd200 ucla ucla-adhd --models lr svm rf --skip-cv --resume

echo "== [8] E4 interpretation (weight stability, top-100 overlaps, permutation nulls) + figures"
"$PY" src/run_e4.py --datasets abide adhd200 abide-filt_global
"$PY" src/figures.py --views abide adhd200 ucla ucla-adhd --e1-dataset abide
"$PY" src/figures.py --views abide adhd200 ucla ucla-adhd --e1-dataset adhd200

echo "== [9] manuscript -> paper/PROCS_AIDA2026_Kapizov.docx (tables built from the result CSVs)"
[ -f paper/template.docx ] && "$PY" paper/build_docx.py || echo "   (paper/template.docx missing; skipping the build)"

echo "== [10] guards: every value[CI] in the manuscript comes from a result table; template untouched"
"$PY" src/check_manuscript_numbers.py
[ -f paper/template.docx ] && "$PY" paper/validate_template.py
echo "== done"
