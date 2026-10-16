"""Stage 1 — ingest: NTA JEE Main paper PDF -> raw per-question records.

The public NTA paper PDFs for JEE Main 2026 render question stems and option
text as *raster images*; ``pdftotext`` only recovers the NTA metadata
(``Question Number / Id / Type`` markers, section headers, option IDs).
This module therefore:

1. extracts text with ``pdftotext`` (layout mode),
2. parses question boundaries from the ``Question Number : N Question Id : X
   Question Type : MCQ|SA`` markers,
3. captures section context (``<Subject> Section <A|B>`` headers),
4. collects option IDs from the ``Options :`` block (option *text* is image-only,
   recorded as ``None``),
5. maps each question to the PDF page range it spans,
6. extracts the raster images per page range into ``content_images`` so the
   question content survives even though no text is available.

Every record carries ``text_available`` (False when stem/options are
image-only) and ``figure_references`` (regex hits for figure/diagram mentions
in whatever text exists). Records are plain dicts, JSON-serializable.
"""

import glob
import os
import re
import shutil
import subprocess

# ---------------------------------------------------------------------------
# patterns
# ---------------------------------------------------------------------------

MARKER_RE = re.compile(
    r"Question Number\s*:\s*(\d+)\s+"
    r"Question Id\s*:\s*(\d+)\s+"
    r"Question Type\s*:\s*(MCQ|SA)"
)
SECTION_RE = re.compile(
    r"^\s*(Mathematics|Physics|Chemistry)\s+Section\s+([AB])\s*$",
    re.MULTILINE,
)
OPTION_ID_RE = re.compile(r"^\s*(\d+)\.\s*$")
FIGURE_RE = re.compile(r"(?i)\b(?:figure|fig\.)\s*\d+|\bdiagram\b")

#: NTA metadata lines that may trail the question marker; stripped from stems.
_METADATA_KEYS = frozenset({
    "Option Shuffling", "Display Question Number", "Is Question Mandatory",
    "Question Mandatory", "Single Line Question Option", "Option Orientation",
    "Keyboard Layout", "Response Type", "Evaluation Required For SA",
    "Show Word Count", "Answers Type", "Text Areas", "Possible Answers",
    "Is Section Default", "Question Shuffling Allowed",
})


def _require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(
            f"Required CLI tool '{name}' not found. Install poppler-utils "
            f"(e.g. `apt install poppler-utils`)."
        )
    return path


def run_pdftotext(pdf_path: str, layout: bool = True,
                  first_page: int | None = None,
                  last_page: int | None = None) -> str:
    """Extract text from a PDF via ``pdftotext`` (stdout, UTF-8)."""
    _require_tool("pdftotext")
    cmd = ["pdftotext", "-enc", "UTF-8"]
    if layout:
        cmd.append("-layout")
    if first_page is not None:
        cmd += ["-f", str(first_page)]
    if last_page is not None:
        cmd += ["-l", str(last_page)]
    cmd += [pdf_path, "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {proc.stderr.strip()}")
    return proc.stdout


def _is_metadata_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or ":" not in stripped:
        return False
    key = stripped.split(":", 1)[0].strip()
    return key in _METADATA_KEYS


def _strip_leading_metadata(lines: list[str]) -> list[str]:
    out = list(lines)
    last_key: str | None = None
    while out:
        stripped = out[0].strip()
        if not stripped:
            out.pop(0)
            continue
        if _is_metadata_line(out[0]):
            last_key = stripped.split(":", 1)[0].strip()
            out.pop(0)
            continue
        break
    # the SA "Possible Answers :" count ("1") is not caught above
    if last_key == "Possible Answers" and out \
            and re.fullmatch(r"\d+", out[0].strip() or ""):
        out.pop(0)
    while out and not out[0].strip():
        out.pop(0)
    return out


def parse_questions(text: str) -> list[dict]:
    """Parse raw question records from ``pdftotext`` output.

    Returns a list of dicts with keys: ``question_number`` (int),
    ``question_id`` (str), ``question_type`` ("MCQ"|"SA"), ``subject``
    ("mathematics"|"physics"|"chemistry"|None), ``section`` ("A"|"B"|None),
    ``options`` (list of ``{"option_id": str, "text": None|str}``),
    ``stem_text`` (str, may be empty when image-only), ``figure_references``
    (list of matched snippets), ``text_available`` (bool).
    """
    sections = [(m.start(), m.group(1).lower(), m.group(2))
                for m in SECTION_RE.finditer(text)]
    markers = list(MARKER_RE.finditer(text))
    records: list[dict] = []

    for i, m in enumerate(markers):
        qnum = int(m.group(1))
        qid = m.group(2)
        qtype = m.group(3)
        chunk_start = m.end()
        chunk_end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        chunk = text[chunk_start:chunk_end]

        # section context: last header before this marker
        subject, section = None, None
        for pos, subj, sec in sections:
            if pos < m.start():
                subject, section = subj, sec
            else:
                break

        lines = _strip_leading_metadata(chunk.splitlines())

        # split off the Options block (MCQ only)
        opt_idx = next((j for j, ln in enumerate(lines)
                        if ln.strip() == "Options :"), None)
        if opt_idx is not None:
            stem_lines = lines[:opt_idx]
            options: list[dict] = []
            for ln in lines[opt_idx + 1:]:
                om = OPTION_ID_RE.match(ln)
                if om:
                    options.append({"option_id": om.group(1), "text": None})
                elif ln.strip():
                    # non-ID content under Options: keep as option text
                    if options:
                        prev = options[-1]
                        prev["text"] = ((prev["text"] or "") + " " + ln.strip()).strip()
                    else:
                        options.append({"option_id": "", "text": ln.strip()})
        else:
            stem_lines = lines
            options = []

        stem_text = "\n".join(stem_lines).strip()
        # drop any residual metadata lines embedded in the stem area
        stem_text = "\n".join(
            ln for ln in stem_text.splitlines() if not _is_metadata_line(ln)
        ).strip()

        records.append({
            "question_number": qnum,
            "question_id": qid,
            "question_type": qtype,
            "subject": subject,
            "section": section,
            "options": options,
            "stem_text": stem_text,
            "figure_references": FIGURE_RE.findall(stem_text),
            "text_available": bool(stem_text)
                               or any(o.get("text") for o in options),
            "content_images": [],
            "pages": [],
        })
    return records


def question_page_spans(pdf_path: str) -> dict[int, list[int]]:
    """Map each question number to the PDF page range it spans.

    A question spans from the page holding its marker up to (and including)
    the page holding the *next* question's marker.
    """
    _require_tool("pdfinfo")
    out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True)
    n_pages = int(re.search(r"Pages:\s+(\d+)", out.stdout).group(1))

    first_page_of: dict[int, int] = {}
    for p in range(1, n_pages + 1):
        txt = run_pdftotext(pdf_path, layout=False,
                             first_page=p, last_page=p)
        for m in MARKER_RE.finditer(txt):
            qnum = int(m.group(1))
            first_page_of.setdefault(qnum, p)

    ordered = sorted(first_page_of)
    spans: dict[int, list[int]] = {}
    for i, qnum in enumerate(ordered):
        start = first_page_of[qnum]
        if i + 1 < len(ordered):
            end = first_page_of[ordered[i + 1]]
            end = max(start, end)
        else:
            end = n_pages
        spans[qnum] = list(range(start, end + 1))
    return spans


def _parse_pdfimages_list(pdf_path: str, first_page: int | None = None,
                          last_page: int | None = None) -> list[dict]:
    _require_tool("pdfimages")
    cmd = ["pdfimages", "-list"]
    if first_page is not None:
        cmd += ["-f", str(first_page)]
    if last_page is not None:
        cmd += ["-l", str(last_page)]
    cmd.append(pdf_path)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pdfimages -list failed: {proc.stderr.strip()}")
    rows: list[dict] = []
    for ln in proc.stdout.splitlines()[2:]:  # skip 2 header lines
        parts = ln.split()
        if len(parts) < 14:
            continue
        try:
            rows.append({
                "page": int(parts[0]),
                "num": int(parts[1]),
                "type": parts[2],
                "width": int(parts[3]),
                "height": int(parts[4]),
            })
        except ValueError:
            continue
    return rows


def extract_images(pdf_path: str, out_dir: str,
                   first_page: int | None = None,
                   last_page: int | None = None,
                   prefix: str = "img") -> list[dict]:
    """Extract raster images with ``pdfimages -png``.

    Returns rows like ``{"page", "num", "type", "width", "height", "path"}``.
    The Nth row of ``pdfimages -list`` corresponds to the Nth extracted file
    (``<prefix>-NNN.png``), which is how page association is recovered.
    """
    _require_tool("pdfimages")
    os.makedirs(out_dir, exist_ok=True)
    rows = _parse_pdfimages_list(pdf_path, first_page, last_page)
    if not rows:
        return rows
    cmd = ["pdfimages", "-png"]
    if first_page is not None:
        cmd += ["-f", str(first_page)]
    if last_page is not None:
        cmd += ["-l", str(last_page)]
    cmd += [pdf_path, os.path.join(out_dir, prefix)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pdfimages failed: {proc.stderr.strip()}")
    files = sorted(glob.glob(os.path.join(out_dir, f"{prefix}-*.png")))
    for row, path in zip(rows, files):
        row["path"] = path
    return rows


def ingest_paper(pdf_path: str, work_dir: str,
                 extract_images_flag: bool = True,
                 image_first_page: int | None = None,
                 image_last_page: int | None = None) -> list[dict]:
    """Full ingest: text parse + page spans + image association."""
    text = run_pdftotext(pdf_path, layout=True)
    records = parse_questions(text)
    spans = question_page_spans(pdf_path)

    images: list[dict] = []
    if extract_images_flag:
        img_dir = os.path.join(work_dir, "images")
        images = extract_images(pdf_path, img_dir,
                                first_page=image_first_page,
                                last_page=image_last_page)

    by_page: dict[int, list[dict]] = {}
    for img in images:
        by_page.setdefault(img["page"], []).append(img)

    for rec in records:
        pages = spans.get(rec["question_number"], [])
        rec["pages"] = pages
        rec["content_images"] = [
            os.path.basename(img["path"])
            for p in pages for img in by_page.get(p, [])
        ]
    return records
