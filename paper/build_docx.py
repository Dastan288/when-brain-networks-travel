#!/usr/bin/env python
"""Build paper/wbnt_aida2026.docx from paper/manuscript.md inside the official Procedia CS template.

The template's first-page furniture (conference line, title/author/abstract/keyword styles, copyright
content control, headers/footers, page geometry, numbering definitions) is kept verbatim; the body is
generated. Tables are generated from the result CSVs, so no number is retyped by hand.

Usage: python paper/build_docx.py            (writes paper/wbnt_aida2026.docx)
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
RES = ROOT / "results"
TEMPLATE = PAPER / "template.docx"
OUT = PAPER / "PROCS_AIDA2026_Kapizov.docx"
FIG1 = RES / "figures" / "fig_transfer_matrix_lr.png"
TEXT_WIDTH_DXA = 10886 - 794 - 737   # page width minus margins (template sectPr) = 9355

# --------------------------------------------------------------------------- references (template style)
REFS = {
    "dimartino2014": 'Di Martino, A., C.-G. Yan, Q. Li, et al. (2014) "The autism brain imaging data exchange: towards a large-scale evaluation of the intrinsic brain architecture in autism." *Molecular Psychiatry* **19** (6): 659–667.',
    "craddock2013": 'Craddock, C., Y. Benhajali, C. Chu, et al. (2013) "The Neuro Bureau Preprocessing Initiative: open sharing of preprocessed neuroimaging data and derivatives." *Frontiers in Neuroinformatics* **7** (Conference Abstract: Neuroinformatics 2013).',
    "bellec2017": 'Bellec, P., C. Chu, F. Chouinard-Decorte, et al. (2017) "The Neuro Bureau ADHD-200 Preprocessed repository." *NeuroImage* **144** (Pt B): 275–286.',
    "adhd200consortium2012": 'The ADHD-200 Consortium. (2012) "The ADHD-200 Consortium: a model to advance the translational potential of neuroimaging in clinical neuroscience." *Frontiers in Systems Neuroscience* **6**: 62.',
    "poldrack2016": 'Poldrack, R.A., E. Congdon, W. Triplett, et al. (2016) "A phenome-wide examination of neural and cognitive function." *Scientific Data* **3**: 160110.',
    "gorgolewski2017": 'Gorgolewski, K.J., J. Durnez, and R.A. Poldrack. (2017) "Preprocessed Consortium for Neuropsychiatric Phenomics dataset." *F1000Research* **6**: 1262.',
    "esteban2019": 'Esteban, O., C.J. Markiewicz, R.W. Blair, et al. (2019) "fMRIPrep: a robust preprocessing pipeline for functional MRI." *Nature Methods* **16** (1): 111–116.',
    "tzourio2002": 'Tzourio-Mazoyer, N., B. Landeau, D. Papathanassiou, et al. (2002) "Automated anatomical labeling of activations in SPM using a macroscopic anatomical parcellation of the MNI MRI single-subject brain." *NeuroImage* **15** (1): 273–289.',
    "craddock2012": 'Craddock, R.C., G.A. James, P.E. Holtzheimer, et al. (2012) "A whole brain fMRI atlas generated via spatially constrained spectral clustering." *Human Brain Mapping* **33** (8): 1914–1928.',
    "johnson2007": 'Johnson, W.E., C. Li, and A. Rabinovic. (2007) "Adjusting batch effects in microarray expression data using empirical Bayes methods." *Biostatistics* **8** (1): 118–127.',
    "fortin2017": 'Fortin, J.-P., D. Parker, B. Tunç, et al. (2017) "Harmonization of multi-site diffusion tensor imaging data." *NeuroImage* **161**: 149–170.',
    "fortin2018": 'Fortin, J.-P., N. Cullen, Y.I. Sheline, et al. (2018) "Harmonization of cortical thickness measurements across scanners and sites." *NeuroImage* **167**: 104–120.',
    "yamashita2019": 'Yamashita, A., N. Yahata, T. Itahashi, et al. (2019) "Harmonization of resting-state functional MRI data across multiple imaging sites via the separation of site differences into sampling bias and measurement bias." *PLoS Biology* **17** (4): e3000042.',
    "marzi2024": 'Marzi, C., M. Giannelli, A. Barucci, et al. (2024) "Efficacy of MRI data harmonization in the age of machine learning: a multicenter study across 36 datasets." *Scientific Data* **11**: 115.',
    "abraham2017": 'Abraham, A., M.P. Milham, A. Di Martino, et al. (2017) "Deriving reproducible biomarkers from multi-site resting-state data: an autism-based example." *NeuroImage* **147**: 736–745.',
    "heinsfeld2018": 'Heinsfeld, A.S., A.R. Franco, R.C. Craddock, A. Buchweitz, and F. Meneguzzi. (2018) "Identification of autism spectrum disorder using deep learning and the ABIDE dataset." *NeuroImage: Clinical* **17**: 16–23.',
    "nielsen2013": 'Nielsen, J.A., B.A. Zielinski, P.T. Fletcher, et al. (2013) "Multisite functional connectivity MRI classification of autism: ABIDE results." *Frontiers in Human Neuroscience* **7**: 599.',
    "varoquaux2018": 'Varoquaux, G. (2018) "Cross-validation failure: small sample sizes lead to large error bars." *NeuroImage* **180** (Pt A): 68–77.',
    "woo2017": 'Woo, C.-W., L.J. Chang, M.A. Lindquist, and T.D. Wager. (2017) "Building better biomarkers: brain models in translational neuroimaging." *Nature Neuroscience* **20** (3): 365–377.',
    "kapoor2023": 'Kapoor, S., and A. Narayanan. (2023) "Leakage and the reproducibility crisis in machine-learning-based science." *Patterns* **4** (9): 100804.',
    "murphy2017": 'Murphy, K., and M.D. Fox. (2017) "Towards a consensus regarding global signal regression for resting state functional connectivity MRI." *NeuroImage* **154**: 169–173.',
    "chekroud2024": 'Chekroud, A.M., M. Hawrilenko, H. Loho, et al. (2024) "Illusory generalizability of clinical prediction models." *Science* **383** (6679): 164–167.',
    "traut2022": 'Traut, N., K. Heuer, G. Lemaître, et al. (2022) "Insights from an autism imaging biomarker challenge: promises and threats to biomarker discovery." *NeuroImage* **255**: 119171.',
    "rosenblatt2024": 'Rosenblatt, M., L. Tejavibulya, R. Jiang, et al. (2024) "Data leakage inflates prediction performance in connectome-based machine learning models." *Nature Communications* **15** (1): 1829.',
    "marek2022": 'Marek, S., B. Tervo-Clemmens, F.J. Calabro, et al. (2022) "Reproducible brain-wide association studies require thousands of individuals." *Nature* **603** (7902): 654–660.',
    "spisak2023": 'Spisak, T., U. Bingel, and T.D. Wager. (2023) "Multivariate BWAS can be replicable with moderate sample sizes." *Nature* **615** (7951): E4–E7.',
    "hu2023": 'Hu, F., A.A. Chen, H. Horng, et al. (2023) "Image harmonization: a review of statistical and deep learning methods for removing batch effects and evaluation metrics for effective harmonization." *NeuroImage* **274**: 120125.',
    "dimartino2017": 'Di Martino, A., D. O\'Connor, B. Chen, et al. (2017) "Enhancing studies of the connectome in autism using the autism brain imaging data exchange II." *Scientific Data* **4**: 170010.',
    "dosenbach2010": 'Dosenbach, N.U.F., B. Nardos, A.L. Cohen, et al. (2010) "Prediction of individual brain maturity using fMRI." *Science* **329** (5997): 1358–1361.',
    "varoquaux2022": 'Varoquaux, G., and V. Cheplygina. (2022) "Machine learning for medical imaging: methodological failures and recommendations for the future." *npj Digital Medicine* **5** (1): 48.',
    "cui2023": 'Cui, H., W. Dai, Y. Zhu, et al. (2023) "BrainGB: a benchmark for brain network analysis with graph neural networks." *IEEE Transactions on Medical Imaging* **42** (2): 493–506.',
    "pedregosa2011": 'Pedregosa, F., G. Varoquaux, A. Gramfort, et al. (2011) "Scikit-learn: machine learning in Python." *Journal of Machine Learning Research* **12**: 2825–2830.',
    "abraham2014": 'Abraham, A., F. Pedregosa, M. Eickenberg, et al. (2014) "Machine learning for neuroimaging with scikit-learn." *Frontiers in Neuroinformatics* **8**: 14.',
}

# --------------------------------------------------------------------------- camera-ready front matter
# Double-blind review is over: names, affiliations and the corresponding-author footnote are restored.
AUTHORS = [("Dastan Kapizov", "a", True), ("Praveen Kumar", "a", False), ("Abilkhas Mukhtarov", "b", False)]
AFFILIATIONS = [("a", "School of Software Engineering, Astana IT University, Astana 010000, Kazakhstan"),
                ("b", "L.N. Gumilyov Eurasian National University, Astana 010008, Kazakhstan")]
CORRESPONDING_EMAIL = "242781@astanait.edu.kz"
RUNNING_AUTHOR = "Dastan Kapizov et al."
CORRESPONDING_PHONE = ""          # optional in the template ("Tel.:"); left out when empty
# Public code repository; set WBNT_REPO_URL or edit here. The build refuses to finish a camera-ready
# file while the placeholder is still in the text unless --draft is given.
import os
REPO_URL = os.environ.get("WBNT_REPO_URL", "https://github.com/Dastan288/when-brain-networks-travel")
DRAFT = "--draft" in sys.argv


# --------------------------------------------------------------------------- xml helpers
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def runs(text: str, base_rpr: str = "") -> str:
    """Inline markup -> runs: **bold**, *italic*, ^sup^. Citations must already be resolved."""
    out = []
    pos = 0
    pat = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|\^(.+?)\^|~(.+?)~")
    for m in pat.finditer(text):
        if m.start() > pos:
            out.append(run(text[pos:m.start()], base_rpr))
        if m.group(1) is not None:
            out.append(run(m.group(1), base_rpr + "<w:b/>"))
        elif m.group(2) is not None:
            out.append(run(m.group(2), base_rpr + "<w:i/>"))
        elif m.group(3) is not None:
            out.append(run(m.group(3), base_rpr + '<w:vertAlign w:val="superscript"/>'))
        else:
            out.append(run(m.group(4), base_rpr + '<w:vertAlign w:val="subscript"/>'))
        pos = m.end()
    if pos < len(text):
        out.append(run(text[pos:], base_rpr))
    return "".join(out)


def run(text: str, rpr: str = "") -> str:
    if not text:
        return ""
    r = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return f'<w:r>{r}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def para(text: str, style: str, extra_ppr: str = "", base_rpr: str = "") -> str:
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{extra_ppr}</w:pPr>{runs(text, base_rpr)}</w:p>'


def heading(text: str, level: int, extra_ppr: str = "") -> str:
    style = "Els-1storder-head" if level == 1 else "Els-2ndorder-head"
    numpr = f'<w:numPr><w:ilvl w:val="{level - 1}"/><w:numId w:val="22"/></w:numPr>'
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{numpr}{extra_ppr}</w:pPr>{runs(text)}</w:p>'


def table_xml(header: list[str], rows: list[list[str]], widths: list[int], align: list[str] | None = None,
              keep_together: bool = True) -> str:
    assert abs(sum(widths) - TEXT_WIDTH_DXA) <= 60, (sum(widths), TEXT_WIDTH_DXA)
    align = align or ["left"] * len(header)
    top_bottom = '<w:tcBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:tcBorders>'
    bottom = '<w:tcBorders><w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:tcBorders>'

    def cell(txt, w, borders, jc, keep):
        jcx = f'<w:jc w:val="{jc}"/>' if jc != "left" else ""
        kn = "<w:keepNext/>" if keep else ""
        return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{borders}</w:tcPr>'
                f'<w:p><w:pPr><w:pStyle w:val="Els-table-text"/>{kn}{jcx}</w:pPr>{runs(txt)}</w:p></w:tc>')

    trpr = "<w:trPr><w:cantSplit/></w:trPr>"   # rows never split; keepNext (optional) chains the rows onto one page
    trpr_head = "<w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>"   # header row repeats if the table breaks
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    trs = ["<w:tr>" + trpr_head + "".join(cell(h, w, top_bottom, a, True) for h, w, a in zip(header, widths, align)) + "</w:tr>"]
    for i, r in enumerate(rows):
        last = i == len(rows) - 1
        b = bottom if last else ""
        trs.append("<w:tr>" + trpr + "".join(cell(c, w, b, a, keep_together and not last) for c, w, a in zip(r, widths, align)) + "</w:tr>")
    tblpr = ('<w:tblPr><w:tblW w:w="0" w:type="auto"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/>'
             '<w:tblLook w:val="01E0" w:firstRow="1" w:lastRow="1" w:firstColumn="1" w:lastColumn="1" w:noHBand="0" w:noVBand="0"/></w:tblPr>')
    return f"<w:tbl>{tblpr}<w:tblGrid>{grid}</w:tblGrid>{''.join(trs)}</w:tbl>"


def caption(text: str, kind: str) -> str:
    if kind == "table":
        return para(text, "Els-caption", '<w:keepNext/>')   # keep the caption on the page of its table
    return para(text, "Els-caption")


def figure_xml(rid: str, width_in: float, aspect: float, docpr_id: int = 101) -> str:
    cx = int(width_in * 914400)
    cy = int(width_in * aspect * 914400)
    return (f'<w:p><w:pPr><w:spacing w:before="120" w:after="0"/><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:noProof/></w:rPr><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:docPr id="{docpr_id}" name="Figure 1" descr="fig_transfer_matrix_lr"/><wp:cNvGraphicFramePr>'
            f'<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="fig1.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')


def fig1_aspect() -> float:
    """height/width of the figure file, so the placed image is never distorted."""
    with open(FIG1, "rb") as f:
        head = f.read(32)
    w = int.from_bytes(head[16:20], "big")
    h = int.from_bytes(head[20:24], "big")
    return h / w


# --------------------------------------------------------------------------- numbers -> tables
def ci(row, m="balanced_accuracy", d=3):
    return f"{row[m]:.{d}f} [{row[m + '_ci_low']:.{d}f}, {row[m + '_ci_high']:.{d}f}]"


def delta_ci(r, d=3):
    s = f"{r['delta']:+.{d}f} [{r['ci_low']:+.{d}f}, {r['ci_high']:+.{d}f}]"
    return s.replace("-", "−")


def cohort(tag):
    """Analyzed cohort = participants with out-of-fold predictions; age/sex from the QC subject tables."""
    o = pd.read_csv(RES / "e5" / f"oof_{tag}_to_{tag}_conn.csv", dtype={"subject_id": str})
    if tag == "abide":
        q = pd.read_csv(RES / "qc" / "abide_subjects_qc.csv")
        q = q.assign(subject_id=q.SUB_ID.astype(str), age=q.AGE_AT_SCAN)
    else:
        q = pd.read_csv(RES / "qc" / f"{'ucla' if tag.startswith('ucla') else tag}_subjects_qc.csv", dtype={"subject_id": str})
    m = o.merge(q[["subject_id", "age", "sex"]], on="subject_id", how="left", validate="one_to_one")
    assert len(m) == len(o) and m.age.notna().all() and m.sex.notna().all(), tag
    return m.y.to_numpy(), m.age.to_numpy(float), m.sex.to_numpy()


def table1():
    """Samples and within-repository baselines in one table (primary model + demographic control)."""
    e2 = pd.read_csv(RES / "e2" / "e2_summary.csv")
    ctrl = pd.read_csv(RES / "e2" / "e3b_control_deltas.csv")
    su = pd.read_csv(RES / "e6" / "e6_site_uncertainty.csv")
    cv = pd.read_csv(RES / "e6" / "e6_repeated_cv.csv")
    spec = [("abide", "ABIDE I (ASD)", "17"), ("adhd200", "ADHD-200 (ADHD)", "7"),
            ("ucla", "UCLA-CNP (any dx)", "2 sc."), ("ucla-adhd", "UCLA-CNP (ADHD)", "2 sc.")]
    rows = []
    for tag, label, sites in spec:
        y, age, sex = cohort(tag)
        d = e2[(e2.source == tag) & (e2.target == tag) & (e2.harmonization == "none") & (e2.model == "lr")].iloc[0]
        a = e2[(e2.source == tag) & (e2.target == tag) & (e2.harmonization == "none") & (e2.model == "agesex_lr")].iloc[0]
        u = su[(su.view == tag) & (su.model == "lr")]
        # a site-level bootstrap over two scanners is degenerate -> report the macro value without a CI
        if not len(u):
            macro = "–"
        elif int(u.iloc[0]["n_sites"]) < 3:
            # two scanners: the macro value is reported, but a site-level CI is not estimated
            macro = f"{u.iloc[0]['macro_bacc']:.3f} (2 sc.; no CI)"
        else:
            macro = f"{u.iloc[0]['macro_bacc']:.3f} [{u.iloc[0]['macro_ci_low']:.3f}, {u.iloc[0]['macro_ci_high']:.3f}]"
        c = cv[(cv.view == tag) & (cv.model == "lr")]["balanced_accuracy"]
        mixed = f"{c.mean():.3f} ± {c.std(ddof=1):.3f}" if len(c) > 1 else "–"
        cc = ctrl[(ctrl.source == tag) & (ctrl.target == tag) & (ctrl.harmonization == "none")
                  & (ctrl.model == "lr") & (ctrl.metric == "balanced_accuracy")]
        rows.append([label, f"{len(y)} ({int(y.sum())}/{int((y == 0).sum())})", sites,
                     f"{np.nanmean(age):.1f} ({np.nanstd(age, ddof=1):.1f})", f"{100 * np.mean(sex == 'M'):.0f}",
                     macro, ci(d), delta_ci(cc.iloc[0]) if len(cc) else "–"])
        assert mixed  # reported in the text
    header = ["Repository (task)", "n (pat./ctrl)", "Sites", "Age (SD)", "M %", "Site-macro bAcc [95 % CI]",
              "Pooled OOF bAcc [95 % CI]", "Pooled Δ vs age + sex [95 % CI]"]
    widths = [1300, 1000, 550, 800, 450, 1700, 1700, 1855]
    return table_xml(header, rows, widths, ["left", "center", "center", "center", "center", "left", "left", "left"],
                     keep_together=True)


def table3():
    """Transfer cells with both adjustments: ComBat (paired deltas) and demographic residualization."""
    e2 = pd.read_csv(RES / "e2" / "e2_summary.csv")
    e3 = pd.read_csv(RES / "e2" / "e3_deltas.csv")
    e3 = e3[(e3.model == "lr") & (e3.metric == "balanced_accuracy")]
    e5 = pd.read_csv(RES / "e5" / "e5_summary.csv")
    label = {"abide": "ABIDE", "adhd200": "ADHD-200", "ucla": "UCLA-CNP", "ucla-adhd": "UCLA-ADHD"}
    matched = {("adhd200", "ucla-adhd"), ("ucla-adhd", "adhd200")}
    # the cells for which the demographic adjustment was run (all four diagonals and the four
    # discussed pairs); the remaining ComBat cells are in Fig. 1(b, c) and in the repository
    order = [("abide", "abide"), ("adhd200", "adhd200"), ("ucla", "ucla"), ("ucla-adhd", "ucla-adhd"),
             ("abide", "adhd200"), ("abide", "ucla"), ("adhd200", "ucla-adhd"), ("ucla-adhd", "adhd200")]
    rows = []
    for s_, t_ in order:
        raw = e2[(e2.source == s_) & (e2.target == t_) & (e2.harmonization == "none") & (e2.model == "lr")]
        if not len(raw):
            continue
        name = f"{label[s_]} → {label[t_]}" + (" (LoSiteO)" if s_ == t_ else ("†" if (s_, t_) in matched else ""))
        cells = [name, ci(raw.iloc[0])]
        for h in ["combat_ref", "combat_new"]:
            r = e3[(e3.source == s_) & (e3.target == t_) & (e3.harmonization == h)]
            cells.append(delta_ci(r.iloc[0]) if len(r) else "n/a")
        rr = e5[(e5.source == s_) & (e5.target == t_) & (e5.features == "conn_resid")]
        cells.append(ci(rr.iloc[0]) if len(rr) else "–")
        rows.append(cells)
    header = ["Training → test", "bAcc, no adjustment [95 % CI]", "ComBat reference-only: Δ bAcc",
              "ComBat new-batch: Δ bAcc", "Age/sex-residualized edges: bAcc [95 % CI]"]
    widths = [2200, 1900, 1600, 1600, 2055]
    return table_xml(header, rows, widths, keep_together=False)


CAPTIONS = {
    "t1": "Table 1. Analyzed samples and within-repository leave-one-site-out results (AAL-90, logistic regression). "
          "Sites = analyzed sites (ADHD-200 repository: 8; Brown excluded). Site-macro = mean per-site balanced "
          "accuracy over sites with both classes, site-bootstrap CI (needs ≥ 3 sites); primary site-aware summary. "
          "Pooled OOF = pooled out-of-fold predictions, subject-bootstrap CI. Δ = paired difference from the age-and-sex "
          "control. sc. = scanners.",
    "t3": "Table 2. The two adjustments (logistic regression, AAL-90). ComBat columns: paired differences in balanced "
          "accuracy versus no harmonization (reference-only: no held-out statistics; new-batch: held-out set adjusted as "
          "its own batch from unlabeled features); other cells in Fig. 1(b, c). Last column: every edge residualized on "
          "age and sex with training-set coefficients. Diagonals are pooled out-of-fold. † = diagnosis-matched pair. "
          "Only ADHD-200 → ADHD-200 new-batch survives BH correction over 60 comparisons (p~FDR~ < 0.001).",
    "f1": "Fig. 1. Cross-repository transfer matrix: balanced accuracy of logistic regression (AAL-90); rows = training "
          "set, columns = test set (same numbering); 95 % bootstrap CI below each value. Solid boxes = leave-one-site-out "
          "diagonal (pooled out-of-fold); dashed boxes = diagnosis-matched ADHD transfer stress test (Question B), which "
          "still differs in age and preprocessing; other off-diagonal cells change the diagnostic task. n/a = not "
          "evaluated or ComBat undefined.",
}


# --------------------------------------------------------------------------- manuscript parsing
def parse_manuscript(path: Path):
    txt = path.read_text(encoding="utf-8")
    meta = {}
    for key in ("title", "abstract", "keywords"):
        m = re.search(rf"^%% {key}\n(.*?)(?=^%% |^# )", txt, flags=re.S | re.M)
        meta[key] = m.group(1).strip()
    body = txt[txt.index("\n# ") + 1:]
    blocks = []
    for chunk in re.split(r"\n\s*\n", body):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith("#! "):
            blocks.append(("h_unnumbered", chunk[3:].strip()))
        elif chunk.startswith("## "):
            blocks.append(("h2", chunk[3:].strip()))
        elif chunk.startswith("# "):
            blocks.append(("h1", chunk[2:].strip()))
        elif chunk.startswith("- "):
            blocks.append(("bullets", [ln[2:].strip() for ln in chunk.splitlines() if ln.startswith("- ")]))
        elif re.fullmatch(r"\[(TABLE|FIGURE):(\w+)\]", chunk):
            m = re.fullmatch(r"\[(TABLE|FIGURE):(\w+)\]", chunk)
            blocks.append((m.group(1).lower(), m.group(2)))
        else:
            blocks.append(("p", " ".join(ln.strip() for ln in chunk.splitlines())))
    return meta, blocks


def number_citations(meta, blocks):
    """Assign numbers in order of first appearance (abstract has no citations); rewrite [key, key] -> [n, m] / [n–m]."""
    order: list[str] = []
    cite_pat = re.compile(r"\[([a-z0-9]+(?:\s*,\s*[a-z0-9]+)*)\]")

    def repl(m):
        keys = [k.strip() for k in m.group(1).split(",")]
        if not all(k in REFS for k in keys):
            return m.group(0)
        nums = []
        for k in keys:
            if k not in order:
                order.append(k)
            nums.append(order.index(k) + 1)
        nums = sorted(set(nums))
        # compress consecutive runs
        parts, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
                j += 1
            parts.append(f"{nums[i]}–{nums[j]}" if j > i + 1 else (f"{nums[i]}, {nums[j]}" if j == i + 1 else f"{nums[i]}"))
            i = j + 1
        return "[" + ", ".join(parts) + "]"

    out = []
    for kind, content in blocks:
        if kind in ("p", "h1", "h2", "h_unnumbered"):
            out.append((kind, cite_pat.sub(repl, content)))
        elif kind == "bullets":
            out.append((kind, [cite_pat.sub(repl, b) for b in content]))
        else:
            out.append((kind, content))
    return out, order


# --------------------------------------------------------------------------- assembly
def build():
    work = PAPER / "_build"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    with zipfile.ZipFile(TEMPLATE) as z:
        z.extractall(work)
    doc = (work / "word" / "document.xml").read_text(encoding="utf-8")
    head, body = doc[:doc.index("<w:body>") + len("<w:body>")], doc[doc.index("<w:body>") + len("<w:body>"):]
    sect = body[body.rindex("<w:sectPr"):]
    # first-page paragraphs before the copyright content control, then the (nested) sdt by balanced matching
    pre = body[:body.index("<w:sdt>")]
    paras = re.findall(r"<w:p[ >].*?</w:p>", pre, flags=re.S)
    docline, p_title, p_author, p_aff1, p_aff2, p_abshead, p_abstext = paras[:7]
    i = body.index("<w:sdt>")
    depth, j = 0, i
    for m in re.finditer(r"<w:sdt>|</w:sdt>", body[i:]):
        depth += 1 if m.group(0) == "<w:sdt>" else -1
        if depth == 0:
            j = i + m.end()
            break
    sdt_copyright = body[i:j]
    p_keywords = re.search(r"<w:p[ >].*?</w:p>", body[j:], flags=re.S).group(0)
    assert "Els-keywords" in p_keywords and "Els-Title" in p_title and "Els-Abstract-text" in p_abstext

    meta, blocks = parse_manuscript(PAPER / "manuscript.md")
    blocks = [(k, c.replace("{{REPO_URL}}", REPO_URL) if isinstance(c, str) else c) for k, c in blocks]
    if "USERNAME" in REPO_URL and not DRAFT:
        sys.exit("[build] REPO_URL is still a placeholder: set WBNT_REPO_URL or pass --draft")
    blocks, order = number_citations(meta, blocks)

    # ---- first page furniture (camera-ready: authors, affiliations, corresponding-author footnote)
    sup = '<w:vertAlign w:val="superscript"/>'
    p_title = re.sub(r"<w:r[ >].*</w:r>", runs(meta["title"]), p_title, flags=re.S)
    a_runs = []
    for k, (name, aff, corr) in enumerate(AUTHORS):
        a_runs.append(run(("" if k == 0 else ", ") + name))
        a_runs.append(run(aff + ("," if corr else ""), sup))
        if corr:   # footnote mark rendered by the template's footnote numbering (chicago: *)
            a_runs.append(f'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteReference w:id="1"/></w:r>')
    p_author = re.sub(r"<w:r[ >].*</w:r>", "".join(a_runs), p_author, flags=re.S)
    p_aff1 = re.sub(r"<w:r[ >].*</w:r>", run(AFFILIATIONS[0][0], sup) + run(AFFILIATIONS[0][1]), p_aff1, flags=re.S)
    p_aff2 = re.sub(r"<w:r[ >].*</w:r>", run(AFFILIATIONS[1][0], sup) + run(AFFILIATIONS[1][1]), p_aff2, flags=re.S)
    p_abstext = re.sub(r"<w:r[ >].*</w:r>", runs(meta["abstract"]), p_abstext, flags=re.S)
    p_keywords = re.sub(r"<w:r[ >].*</w:r>", run("Keywords:", "<w:i/>") + run(" " + meta["keywords"]), p_keywords, flags=re.S)

    # ---- body
    out = []
    first_bullet = True
    for kind, content in blocks:
        if kind == "h1":
            # the first heading follows the keywords block on page 1: without keepNext LibreOffice/Word
            # may otherwise push it (and the empty rest of page 1) to page 2
            out.append(heading(content, 1)); first_bullet = True
        elif kind == "h2":
            out.append(heading(content, 2)); first_bullet = True
        elif kind == "h_unnumbered":
            out.append(para(content, "Els-acknowledgement"))
        elif kind == "p":
            out.append(para(content, "Els-body-text"))
        elif kind == "bullets":
            for i, b in enumerate(content):
                sp = '<w:spacing w:before="120"/>' if i == 0 else ""
                out.append(para(b, "Els-bulletlist", sp + '<w:ind w:left="245" w:hanging="245"/>'))
        elif kind == "table":
            out.append(caption(CAPTIONS[content], "table"))
            out.append({"t1": table1, "t2": table3, "t3": table3}[content]())
        elif kind == "figure":
            out.append(figure_xml("rId901", 6.4, fig1_aspect()))
            out.append(caption(CAPTIONS[content], "figure"))
    # references
    out.append(para("References", "Els-reference-head"))
    for i, key in enumerate(order, 1):
        out.append(para(f"[{i}] {REFS[key]}", "Els-reference"))
    unused = sorted(set(REFS) - set(order))

    new_body = "".join([docline, p_title, p_author, p_aff1, p_aff2, p_abshead, p_abstext, sdt_copyright, p_keywords] + out) + sect
    (work / "word" / "document.xml").write_text(head + new_body, encoding="utf-8")

    # ---- figure relationship + media
    shutil.copy(FIG1, work / "word" / "media" / "fig1.png")
    rels_p = work / "word" / "_rels" / "document.xml.rels"
    rels = rels_p.read_text(encoding="utf-8")
    rels = rels.replace("</Relationships>", '<Relationship Id="rId901" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/fig1.png"/></Relationships>')
    rels_p.write_text(rels, encoding="utf-8")

    # ---- running heads: the template's "Author name" placeholder -> first author et al.; the template's
    # running heads say "(2025)" while its first-page masthead says "(2026)" -> one year (2026) everywhere.
    for name in ("header1.xml", "header2.xml"):   # footer1/2 carry no text and stay byte-identical
        hp = work / "word" / name
        if not hp.exists():
            continue
        x = hp.read_text(encoding="utf-8")
        x, n_ah = re.subn(r'<w:r[^>]*>\s*<w:fldChar w:fldCharType="begin"/>\s*</w:r>\s*<w:r[^>]*>\s*<w:instrText[^>]*>\s*MACROBUTTON NoMacro Author name\s*</w:instrText>\s*</w:r>\s*<w:r[^>]*>\s*<w:fldChar w:fldCharType="end"/>\s*</w:r>',
                          run(RUNNING_AUTHOR + " "), x, flags=re.S)
        assert n_ah == 1, name
        # the year is split across runs ("20" + "2" + "5"), so patch the digits run by run
        x = re.sub(r'(<w:t[^>]*>)20(</w:t>)(\s*</w:r>\s*<w:r[^>]*>(?:<w:rPr>.*?</w:rPr>)?<w:t[^>]*>)2(</w:t>)'
                   r'(\s*</w:r>\s*<w:r[^>]*>(?:<w:rPr>.*?</w:rPr>)?<w:t[^>]*>)5(</w:t>)',
                   r'\g<1>20\g<2>\g<3>2\g<4>\g<5>6\g<6>', x, flags=re.S)
        x = x.replace("(2025)", "(2026)")
        hp.write_text(x, encoding="utf-8")

    # ---- the template carries the publication statement twice on page 1: the conference-updated
    # "(c) 2026 ..." block in the body, and an outdated "1877-0509 (c) 2025 ..." block in the first-page
    # footer. Keep the body block and empty the outdated footer duplicate.
    f3 = work / "word" / "footer3.xml"
    if f3.exists():
        x = f3.read_text(encoding="utf-8")
        a = x.index(">", x.index("<w:ftr")) + 1
        b = x.index("</w:ftr>")
        f3.write_text(x[:a] + '<w:p><w:pPr><w:pStyle w:val="Footer"/></w:pPr></w:p>' + x[b:], encoding="utf-8")

    # ---- corresponding-author footnote: the template's two paragraphs, placeholders filled
    fn_p = work / "word" / "footnotes.xml"
    fn = fn_p.read_text(encoding="utf-8")
    line1 = " Corresponding author." + (f" Tel.: {CORRESPONDING_PHONE}." if CORRESPONDING_PHONE else "")
    # the "*" is the footnote's own reference mark (template numbering: chicago), not typed text
    note = ('<w:p><w:pPr><w:pStyle w:val="Els-footnote"/><w:ind w:firstLine="120"/></w:pPr>'
            '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/><w:vertAlign w:val="baseline"/></w:rPr><w:footnoteRef/></w:r>'
            + run(line1) + '</w:p>'
            '<w:p><w:pPr><w:pStyle w:val="Els-footnote"/><w:ind w:firstLine="240"/></w:pPr>'
            + run("E-mail address:", "<w:i/><w:iCs/>") + run(" " + CORRESPONDING_EMAIL) + '</w:p>')
    fn = re.sub(r'(<w:footnote w:id="1">).*?(</w:footnote>)', lambda m: m.group(1) + note + m.group(2), fn, flags=re.S)
    fn_p.write_text(fn, encoding="utf-8")
    core_p = work / "docProps" / "core.xml"
    if core_p.exists():
        core = core_p.read_text(encoding="utf-8")
        core = re.sub(r"<dc:creator>.*?</dc:creator>", f"<dc:creator>{esc('; '.join(a[0] for a in AUTHORS))}</dc:creator>", core, flags=re.S)
        core = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>", "<cp:lastModifiedBy></cp:lastModifiedBy>", core, flags=re.S)
        core = re.sub(r"<dc:title>.*?</dc:title>", f"<dc:title>{esc(meta['title'])}</dc:title>", core, flags=re.S)
        core_p.write_text(core, encoding="utf-8")
    # remove the template's comments part if present (instructions), keep everything else
    # ---- zip
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(work.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(work).as_posix())
    shutil.rmtree(work)
    n_words = len(re.findall(r"\w+", " ".join(c if isinstance(c, str) else " ".join(c) for k, c in blocks if k in ("p", "bullets"))))
    print(f"[build] {OUT.name}: {len(order)} references cited (unused: {unused}); body ≈ {n_words} words; abstract {len(meta['abstract'].split())} words")
    return 0


if __name__ == "__main__":
    sys.exit(build())
