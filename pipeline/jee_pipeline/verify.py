"""Stage 5 — verify: compare a blind solver's answer against the official key.

The solver never sees the key. :func:`verify` takes the solver's answer and
the key entry (from :mod:`jee_pipeline.keyparser`) and returns a verdict dict
with ``status`` in ``{"verified", "mismatch", "dropped", "needs_review"}``.

Supported question types (both Main labels ``MCQ``/``SA`` and schema labels):
- single-choice: key is an NTA option ID (Main) or a letter (Advanced style).
  The solver may answer with the option ID, a letter (A-D), or a 1-based
  index into the question's option list.
- multi-choice: letters are normalized (upper-cased, de-duplicated, sorted)
  before comparison, e.g. ``"CA"`` == ``"AC"``.
- numerical: floats compared with tolerance. The key may be a single value
  (``"232"``, ``"2.33"``) or a range (``"99 to 101"``, ``"[2.4 to 2.6]"``);
  a range implies value=midpoint, tolerance=half-width. Effective tolerance
  is ``max(key_tolerance, tolerance)``.
"""

import re

_QTYPE_CANON = {
    "MCQ": "single_correct",
    "SA": "numerical",
    "single_correct": "single_correct",
    "multi_correct": "multi_correct",
    "numerical": "numerical",
    "matrix_match": "matrix_match",
    "stem_numerical": "stem_numerical",
}

_RANGE_RE = re.compile(
    r"^\[?\s*(-?\d+(?:\.\d+)?)\s+to\s+(-?\d+(?:\.\d+)?)\s*\]?$")
_LETTERS_ONLY_RE = re.compile(r"^[A-Da-d]+$")


def normalize_letters(value: str) -> str:
    """Upper-case, de-duplicate and sort option letters (``"CA"`` -> ``"AC"``)."""
    s = re.sub(r"[^A-Za-z]", "", str(value)).upper()
    if not s or any(c not in "ABCD" for c in s):
        raise ValueError(f"not a valid option-letter answer: {value!r}")
    return "".join(sorted(set(s)))


def parse_key_numeric(value: str) -> tuple[float, float]:
    """Parse a key numeric value -> (value, implied_tolerance).

    Handles ``"232"``, ``"2.33"``, ``"-4"``, ``"99 to 101"`` and
    ``"[2.4 to 2.6]"`` (range -> midpoint, half-width tolerance).
    """
    s = str(value).strip()
    m = _RANGE_RE.match(s)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        return ((lo + hi) / 2.0, abs(hi - lo) / 2.0)
    return (float(s), 0.0)


def resolve_option_id(solver_answer: str,
                      options: list[dict] | None) -> str:
    """Resolve a solver's MCQ answer to an NTA option ID.

    Accepts the raw option ID, a letter (``"B"``), or a 1-based index
    (``"2"``) into ``options`` (each ``{"option_id": ...}``). Without
    ``options`` the answer is returned stripped, assumed to be an ID.
    """
    s = str(solver_answer).strip()
    if not options:
        return s
    ids = [o["option_id"] for o in options]
    if s in ids:
        return s
    if _LETTERS_ONLY_RE.fullmatch(s) and len(s) == 1:
        return ids["ABCD".index(s.upper())]
    if s.isdigit() and 1 <= int(s) <= len(ids):
        return ids[int(s) - 1]
    raise ValueError(f"cannot resolve MCQ answer {solver_answer!r} "
                     f"against {len(ids)} options")


def compare_answers(solver_answer: str, key: dict, qtype: str,
                    options: list[dict] | None = None,
                    tolerance: float = 0.01) -> dict:
    """Compare solver vs key. Returns ``{"match": bool, "detail": str}``.

    ``key`` is ``{"kind": "option_id"|"numeric", "value": str, "values": [...]}``
    as produced by :mod:`jee_pipeline.keyparser` (or ``{"kind": "letter", ...}``
    for Advanced-style letter keys). For ``option_id`` keys with several
    accepted values, matching any one of them counts as a match.
    """
    canon = _QTYPE_CANON.get(qtype, qtype)
    kind = key.get("kind", "option_id")
    key_values = [str(v).strip() for v in key.get("values", [key["value"]])]
    key_value = key_values[0]

    if canon in ("single_correct", "matrix_match"):
        if kind == "option_id":
            resolved = resolve_option_id(solver_answer, options)
            match = resolved in key_values
            detail = (f"solver option {resolved} vs key "
                      + ", ".join(key_values))
        else:  # letter key (Advanced style)
            a = normalize_letters(solver_answer)
            b = normalize_letters(key_value)
            match = a == b
            detail = f"solver {a} vs key {b}"
        return {"match": match, "detail": detail}

    if canon == "multi_correct":
        a = normalize_letters(solver_answer)
        b = normalize_letters(key_value)
        return {"match": a == b, "detail": f"solver {a} vs key {b}"}

    if canon in ("numerical", "stem_numerical"):
        s_val = float(str(solver_answer).strip())
        k_val, k_tol = parse_key_numeric(key_value)
        tol = max(tolerance, k_tol)
        match = abs(s_val - k_val) <= tol + 1e-9
        return {"match": match,
                "detail": f"solver {s_val} vs key {k_val} (tol {tol})"}

    raise ValueError(f"unsupported qtype: {qtype!r}")


def verify(solver_answer: str, key: dict, qtype: str,
           question_id: str | None = None,
           dropped_ids: tuple | list = (),
           options: list[dict] | None = None,
           tolerance: float = 0.01) -> dict:
    """Full verdict for one question.

    Returns ``{"status", "match", "detail", "question_id"}`` where status is
    ``verified`` | ``mismatch`` | ``dropped`` | ``needs_review``.
    Unparseable answers become ``needs_review``, never silent failures.
    """
    if question_id is not None and question_id in set(dropped_ids):
        return {"status": "dropped", "match": False,
                "detail": "question dropped per official key",
                "question_id": question_id}
    try:
        cmp_ = compare_answers(solver_answer, key, qtype,
                              options=options, tolerance=tolerance)
    except (ValueError, TypeError) as exc:
        return {"status": "needs_review", "match": False,
                "detail": f"unparseable answer: {exc}",
                "question_id": question_id}
    return {"status": "verified" if cmp_["match"] else "mismatch",
            "match": cmp_["match"], "detail": cmp_["detail"],
            "question_id": question_id}
