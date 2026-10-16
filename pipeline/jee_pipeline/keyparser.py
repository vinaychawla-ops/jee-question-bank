"""Stage 4a — keyparser: NTA final answer-key PDF -> per-shift answer map.

The NTA key PDF is one document with one page per (shift x centre-variant).
Each page header carries ``Exam Date : DD.MM.YYYY`` and
``Exam Shift : First|Second`` plus either ``(For Centers in India)`` or
``(For Centers Outside India)``. The body is ``QUESTION ID  CORRECT OPTION ID``
rows, three column-groups per page (Mathematics / Physics / Chemistry).

Row value kinds:
- a long digit string (7+ digits, e.g. ``6911211786``) -> ``option_id``
- anything else (``232``, ``2.33``, ``-4``) -> ``numeric``
- the literal word ``Dropped`` -> recorded in ``dropped``, not in answers
- comma-separated IDs (``6911211907, 6911211908``) -> ``option_id`` with
  several accepted ``values`` (NTA accepted multiple options)

Subject context is recovered from the ``( MATHEMATICS )`` / ``( PHYSICS )`` /
``( CHEMISTRY )`` group headers.

IMPORTANT: text must be extracted with ``pdftotext -raw`` (not ``-layout``);
layout mode merges the ID columns and silently drops digits.
"""

import re
import subprocess

from .ingest import _require_tool  # reuse the poppler check

DATE_RE = re.compile(r"Exam Date\s*:\s*(\d{2}\.\d{2}\.\d{4})")
SHIFT_RE = re.compile(r"Exam Shift\s*:\s*([A-Za-z]+)")
SUBJECT_RE = re.compile(r"\(\s*(MATHEMATICS|PHYSICS|CHEMISTRY)\s*\)")
ROW_RE = re.compile(r"^(\d+)\s+(.+?)\s*$")

_SUBJECT_MAP = {"MATHEMATICS": "mathematics", "PHYSICS": "physics",
                "CHEMISTRY": "chemistry"}

_VALUE_PART_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
_RANGE_RE = re.compile(r"^-?\d+(?:\.\d+)?\s+to\s+-?\d+(?:\.\d+)?$")


def _valid_value(raw: str) -> bool:
    """True if *raw* looks like a key value (not a stray header line)."""
    if raw == "Dropped":
        return True
    if _RANGE_RE.match(raw):
        return True
    parts = [p.strip() for p in raw.split(",")]
    return bool(parts) and all(_VALUE_PART_RE.match(p) for p in parts)


def extract_text_raw(pdf_path: str) -> str:
    """Extract text with ``pdftotext -raw`` (preserves the ID columns)."""
    _require_tool("pdftotext")
    proc = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", "-raw", pdf_path, "-"],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pdftotext -raw failed: {proc.stderr.strip()}")
    return proc.stdout


def split_pages(text: str) -> list[str]:
    """Split extracted text into pages on form-feed characters."""
    return text.split("\f")


def parse_page(page_text: str) -> dict:
    """Parse one key page -> {meta, answers, dropped, subjects}.

    ``answers`` maps question-id -> raw value string; ``dropped`` is a list
    of question-ids; ``subjects`` maps question-id -> subject slug.
    """
    meta: dict = {}
    m = DATE_RE.search(page_text)
    if m:
        meta["exam_date"] = m.group(1)
    m = SHIFT_RE.search(page_text)
    if m:
        meta["exam_shift"] = m.group(1)
    if "For Centers Outside India" in page_text:
        meta["variant"] = "outside-india"
    elif "For Centers in India" in page_text:
        meta["variant"] = "india"

    answers: dict[str, str] = {}
    dropped: list[str] = []
    subjects: dict[str, str] = {}
    current_subject: str | None = None
    for line in page_text.splitlines():
        subs = SUBJECT_RE.findall(line)
        if subs:
            current_subject = _SUBJECT_MAP[subs[-1]]
            continue
        rm = ROW_RE.match(line.strip())
        if not rm or not _valid_value(rm.group(2)):
            continue
        qid, raw_val = rm.group(1), rm.group(2)
        if raw_val == "Dropped":
            dropped.append(qid)
        else:
            answers[qid] = raw_val
            if current_subject:
                subjects[qid] = current_subject
    return {"meta": meta, "answers": answers, "dropped": dropped,
            "subjects": subjects}


def classify_value(value: str) -> str:
    """Return ``"option_id"`` for long digit strings, else ``"numeric"``."""
    if value.isdigit() and len(value) >= 7:
        return "option_id"
    return "numeric"


def parse_key(pdf_path: str, exam_date: str, exam_shift: str,
              variant: str = "india") -> dict:
    """Parse the final-key PDF for one shift.

    Args:
        pdf_path: path to the NTA final answer-key PDF.
        exam_date: e.g. ``"08.04.2026"``.
        exam_shift: e.g. ``"Second"`` (matches ``Exam Shift : Second``).
        variant: ``"india"`` or ``"outside-india"``.

    Returns ``{"meta", "answers": {qid: {"kind", "value", "values"}},
    "dropped": [qid...], "subjects": {qid: subject}}``. ``values`` is the
    list of accepted values (usually one; several when NTA accepted multiple
    options, e.g. ``"6911211907, 6911211908"``).
    Raises :class:`ValueError` if the shift page is not found.
    """
    text = extract_text_raw(pdf_path)
    for page in split_pages(text):
        parsed = parse_page(page)
        meta = parsed["meta"]
        if (meta.get("exam_date") == exam_date
                and meta.get("exam_shift") == exam_shift
                and meta.get("variant") == variant):
            answers = {}
            for qid, raw in parsed["answers"].items():
                values = [p.strip() for p in raw.split(",")]
                answers[qid] = {
                    "kind": classify_value(values[0]),
                    "value": raw,
                    "values": values,
                }
            return {
                "meta": {**meta, "source_pdf": pdf_path},
                "answers": answers,
                "dropped": parsed["dropped"],
                "subjects": parsed["subjects"],
            }
    raise ValueError(
        f"No key page found for date={exam_date} shift={exam_shift} "
        f"variant={variant}")
