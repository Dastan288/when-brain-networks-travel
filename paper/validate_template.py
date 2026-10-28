#!/usr/bin/env python
"""Check that the camera-ready docx (paper/PROCS_AIDA2026_Kapizov.docx) still IS the official Procedia template.

Compares the built file with paper/template.docx part by part and allows only the two
deliberate changes that were agreed in review:
  (1) the running-head placeholder field "Author name" is replaced by the first author et al.;
  (2) the template's running heads say "(2025)" while its masthead says "(2026)": one year, 2026, everywhere;
  (3) the outdated duplicate publication statement in the first-page footer ("1877-0509 (c) 2025 ...") is
      emptied; the conference-updated "(c) 2026 ..." block in the body is kept unchanged.
Everything that controls layout (styles, numbering, theme, settings, fonts, section geometry)
must be byte-identical. Usage: python paper/validate_template.py
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
IDENTICAL = ["word/styles.xml", "word/numbering.xml", "word/settings.xml", "word/fontTable.xml",
             "word/theme/theme1.xml"]
YEAR_ONLY = ["word/header1.xml", "word/header2.xml"]   # differ only by the filled running-head author
IDENTICAL += ["word/header3.xml", "word/footer1.xml", "word/footer2.xml"]
# the ScienceDirect / Procedia masthead lives in the first-page header (header3.xml); the
# publication statement lives in the body
FURNITURE_HEADER = ["sciencedirect", "Procedia"]
FURNITURE_BODY = ["© 2026 The Authors. Published by ELSEVIER B.V.",
                  "Peer-review under responsibility of the scientific committee of the CENTERIS"]


def text_of(xml: str) -> str:
    return "".join(re.findall(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", xml, re.S))


def main() -> int:
    tpl = zipfile.ZipFile(HERE / "template.docx")
    out = zipfile.ZipFile(HERE / "PROCS_AIDA2026_Kapizov.docx")
    fails: list[str] = []

    for part in IDENTICAL:
        if part not in tpl.namelist():
            continue
        if tpl.read(part) != out.read(part):
            fails.append(f"{part} differs from the template")

    for part in YEAR_ONLY:
        a, b = tpl.read(part).decode("utf-8"), out.read(part).decode("utf-8")
        ta, tb = text_of(a).replace("2025", "2026"), text_of(b).replace("Dastan Kapizov et al. ", "")
        if ta != tb:
            fails.append(f"{part}: text changed beyond the year ({ta[:60]!r} vs {tb[:60]!r})")
        if len(b) - len(a) > 400:
            fails.append(f"{part}: markup grew by {len(b) - len(a)} bytes")


    f3 = text_of(out.read("word/footer3.xml").decode("utf-8")).strip()
    if f3:
        fails.append(f"footer3.xml should be empty (outdated duplicate publication statement), found {f3[:60]!r}")
    for part in [n for n in out.namelist() if re.match(r"word/(header|footer)\d\.xml", n)] + ["word/document.xml"]:
        if "2025" in text_of(out.read(part).decode("utf-8")):
            fails.append(f"{part}: still mentions 2025")

    doc = out.read("word/document.xml").decode("utf-8")
    sect_t = re.search(r"<w:pgSz[^>]*/><w:pgMar[^>]*/>", tpl.read("word/document.xml").decode("utf-8"))
    sect_o = re.search(r"<w:pgSz[^>]*/><w:pgMar[^>]*/>", doc)
    if not sect_o or not sect_t or sect_o.group(0) != sect_t.group(0):
        fails.append("page geometry (pgSz/pgMar) differs from the template")
    body = text_of(doc)
    head1 = out.read("word/header3.xml").decode("utf-8").lower()
    for s in FURNITURE_HEADER:
        if s.lower() not in head1:
            fails.append(f"first-page masthead missing from header3.xml: {s!r}")
    for s in FURNITURE_BODY:
        if s not in body:
            fails.append(f"first-page furniture missing from the body: {s[:40]!r}")
    for leak in ("MACROBUTTON", "Click here", "First Author", "Keywords—", "withheld", "USERNAME", "{{", "TODO"):
        if leak in body:
            fails.append(f"template/anonymization placeholder left in the body: {leak}")
    for part in ("word/header1.xml", "word/header2.xml"):
        x = out.read(part).decode("utf-8")
        if "Author name" in x or "Dastan Kapizov et al." not in text_of(x):
            fails.append(f"{part}: running head does not name the first author")
    # camera-ready front matter
    for must in ("Dastan Kapizov", "Praveen Kumar", "Abilkhas Mukhtarov", "Astana IT University",
                 "L.N. Gumilyov Eurasian National University"):
        if must not in body:
            fails.append(f"camera-ready front matter missing: {must}")
    fn = text_of(out.read("word/footnotes.xml").decode("utf-8"))
    if "Corresponding author" not in fn or "242781@astanait.edu.kz" not in fn:
        fails.append("corresponding-author footnote incomplete")
    # every text paragraph in the body uses a named template style (no unstyled/Normal body text)
    allowed_unstyled = ("Peer-review under responsibility",)   # template's own copyright block
    for para in re.findall(r"<w:p[ >].*?</w:p>", doc, re.S):
        t = text_of(para).strip()
        if not t or "<w:tbl" in para:
            continue
        m = re.search(r'<w:pStyle w:val="([^"]+)"', para)
        if not m and not t.startswith(allowed_unstyled):
            fails.append(f"paragraph without a template style: {t[:50]!r}")
        elif m and not (m.group(1).startswith("Els-") or m.group(1) in ("DocHead", "HTMLPreformatted")):
            fails.append(f"paragraph in non-template style {m.group(1)}: {t[:50]!r}")
    # no review residue
    names = out.namelist()
    if "word/comments.xml" in names and text_of(out.read("word/comments.xml").decode("utf-8")).strip():
        fails.append("comments present")
    if re.search(r"<w:(ins|del) ", doc):
        fails.append("tracked changes present")

    # --- citation numbering: Elsevier numbered style requires the reference list to follow the
    # order of first appearance. Grouped brackets ("[7, 8]") and ranges ("[9-11]") count as
    # appearances of every number inside them, which a naive single-number scan misses.
    seq: list[int] = []
    body_only = body.split("References")[0]
    for m in re.finditer(r"\[(\d+(?:\s*[\u2013,-]\s*\d+)*)\]", body_only):
        for part in m.group(1).split(","):
            part = part.strip()
            rng = re.match(r"^(\d+)\s*[\u2013-]\s*(\d+)$", part)
            if rng:
                seq.extend(range(int(rng.group(1)), int(rng.group(2)) + 1))
            elif part.isdigit():
                seq.append(int(part))
    first: list[int] = []
    for n in seq:
        if n not in first:
            first.append(n)
    listed = [int(m.group(1)) for m in re.finditer(r"\[(\d+)\]\s", body) if int(m.group(1)) > 0]
    n_refs = max(listed) if listed else 0
    if first != sorted(first):
        fails.append(f"citations are not numbered in order of first appearance: {first}")
    if first and first != list(range(1, len(first) + 1)):
        fails.append(f"the cited numbers are not a gapless 1..N run: {first}")
    if n_refs and len(first) != n_refs:
        fails.append(f"{n_refs} entries in the list but {len(first)} distinct numbers cited")

    if fails:
        print("VALIDATION FAILED")
        for f in fails:
            print("  -", f)
        return 1
    print(f"All validations PASSED (styles/numbering/settings/theme byte-identical to the template; running heads "
          f"differ only by author and year; no 2025 anywhere; footer3 duplicate emptied; every paragraph in a template style; page geometry and first-page "
          f"furniture intact; {len(first)} references cited in first-appearance order 1..{len(first)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
