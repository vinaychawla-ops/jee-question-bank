"""Stage 3 — schema: strict validator for the question record JSON.

Implements the record schema from the spec (section 2). Two entry points:

- :func:`validate_record` -> list of human-readable error strings (``[]`` = valid)
- :func:`validate_record_strict` -> raises :class:`SchemaError` on any problem

The validator is intentionally strict: it is the gate before ``publish``.
"""

import re

EXAMS = {"JEE Main", "JEE Advanced"}
SUBJECTS = {"physics", "chemistry", "mathematics"}
QTYPES = {"single_correct", "multi_correct", "numerical", "matrix_match",
          "stem_numerical"}
DIFFICULTIES = {"easy", "medium", "hard"}
VERIFICATION_STATUSES = {"verified", "mismatch", "dropped", "needs_review"}
OPTION_LETTERS = {"A", "B", "C", "D"}

_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)+$")


class SchemaError(ValueError):
    """Raised by :func:`validate_record_strict` when a record is invalid."""


def _is_num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_record(rec: dict) -> list[str]:
    """Return a list of validation errors; empty list means valid."""
    errors: list[str] = []
    if not isinstance(rec, dict):
        return ["record must be a dict"]

    # -- top-level scalars -------------------------------------------------
    rid = rec.get("id")
    if not isinstance(rid, str) or not rid:
        errors.append("id must be a non-empty string")
    elif not _ID_RE.match(rid):
        errors.append(f"id {rid!r} should be kebab-case (e.g. main2026-s2-phy-q01)")

    if rec.get("exam") not in EXAMS:
        errors.append(f"exam must be one of {sorted(EXAMS)}")
    if not isinstance(rec.get("year"), int) or rec.get("year") < 2000:
        errors.append("year must be a plausible int")
    for f in ("paper", "session", "shift"):
        if f in rec and rec[f] is not None and not isinstance(rec[f], str):
            errors.append(f"{f} must be a string or null")
    if rec.get("subject") not in SUBJECTS:
        errors.append(f"subject must be one of {sorted(SUBJECTS)}")

    qtype = rec.get("qtype")
    if qtype not in QTYPES:
        errors.append(f"qtype must be one of {sorted(QTYPES)}")

    if not isinstance(rec.get("number_in_subject"), int) \
            or rec.get("number_in_subject", 0) < 1:
        errors.append("number_in_subject must be a positive int")

    stem = rec.get("stem")
    if not isinstance(stem, str) or not stem.strip():
        errors.append("stem must be a non-empty string (LaTeX)")

    if not isinstance(rec.get("stem_images"), list) or not all(
            isinstance(x, str) for x in rec.get("stem_images", [])):
        errors.append("stem_images must be a list of strings")

    if "parent_stem" in rec and rec["parent_stem"] is not None \
            and not isinstance(rec["parent_stem"], str):
        errors.append("parent_stem must be a string or null")

    # -- section / marking --------------------------------------------------
    section = rec.get("section")
    if not isinstance(section, dict):
        errors.append("section must be a dict {name, max_marks}")
    else:
        if not isinstance(section.get("name"), str):
            errors.append("section.name must be a string")
        if not _is_num(section.get("max_marks")):
            errors.append("section.max_marks must be a number")

    marking = rec.get("marking")
    if not isinstance(marking, dict):
        errors.append("marking must be a dict")
    else:
        for k in ("correct", "wrong", "unanswered"):
            if not _is_num(marking.get(k)):
                errors.append(f"marking.{k} must be a number")
        if marking.get("partial") is not None and not _is_num(marking.get("partial")):
            errors.append("marking.partial must be a number or null")

    # -- options ------------------------------------------------------------
    options = rec.get("options")
    needs_options = qtype in {"single_correct", "multi_correct", "matrix_match"}
    if needs_options:
        if not isinstance(options, dict) or not options:
            errors.append(f"qtype {qtype} requires a non-empty options dict")
        else:
            bad = set(options) - OPTION_LETTERS
            if bad:
                errors.append(f"option keys must be A-D, got {sorted(bad)}")
            for k, v in options.items():
                if not isinstance(v, str) or not v.strip():
                    errors.append(f"options[{k}] must be a non-empty string")
    else:
        if options is not None:
            errors.append(f"qtype {qtype} must have options = null")

    # -- answer --------------------------------------------------------------
    answer = rec.get("answer")
    if not isinstance(answer, dict):
        errors.append("answer must be a dict {value, tolerance, source}")
    else:
        val = answer.get("value")
        tol = answer.get("tolerance")
        src = answer.get("source")
        if not isinstance(src, str) or not src:
            errors.append("answer.source must be a non-empty string")
        if qtype == "single_correct":
            if not (isinstance(val, str) and len(val) == 1 and val in OPTION_LETTERS):
                errors.append("single_correct answer.value must be one of A-D")
        elif qtype == "matrix_match":
            if not (isinstance(val, str) and len(val) == 1 and val in OPTION_LETTERS):
                errors.append("matrix_match answer.value must be one of A-D")
        elif qtype == "multi_correct":
            if not (isinstance(val, str) and 1 <= len(val) <= 4
                    and set(val) <= OPTION_LETTERS and len(set(val)) == len(val)
                    and list(val) == sorted(val)):
                errors.append("multi_correct answer.value must be sorted unique "
                              "letters from A-D, e.g. 'AC'")
        elif qtype in {"numerical", "stem_numerical"}:
            try:
                float(val)
            except (TypeError, ValueError):
                errors.append(f"{qtype} answer.value must be numeric, got {val!r}")
        if qtype in {"numerical", "stem_numerical"}:
            if tol is not None and not (_is_num(tol) and tol >= 0):
                errors.append("answer.tolerance must be a non-negative number or null")
        elif tol is not None:
            errors.append(f"qtype {qtype} must have answer.tolerance = null")

    # -- solution ------------------------------------------------------------
    sol = rec.get("solution")
    if not isinstance(sol, dict):
        errors.append("solution must be a dict")
    else:
        for k in ("concepts", "formulas", "pitfalls"):
            if not isinstance(sol.get(k), list) or not all(
                    isinstance(x, str) for x in sol.get(k, [])):
                errors.append(f"solution.{k} must be a list of strings")
        steps = sol.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append("solution.steps must be a non-empty list")
        else:
            for i, st in enumerate(steps, start=1):
                if not isinstance(st, dict) or st.get("n") != i \
                        or not isinstance(st.get("text"), str) \
                        or not st.get("text", "").strip():
                    errors.append(f"solution.steps[{i}] must be "
                                  f"{{n: {i}, text: non-empty string}}")
                    break
        if not isinstance(sol.get("final_check"), str) \
                or not sol.get("final_check", "").strip():
            errors.append("solution.final_check must be a non-empty string")

    # -- taxonomy --------------------------------------------------------------
    tax = rec.get("taxonomy")
    if not isinstance(tax, dict):
        errors.append("taxonomy must be a dict")
    else:
        if not isinstance(tax.get("chapters"), list) or not tax.get("chapters") \
                or not all(isinstance(x, str) for x in tax["chapters"]):
            errors.append("taxonomy.chapters must be a non-empty list of strings")
        if tax.get("difficulty") not in DIFFICULTIES:
            errors.append(f"taxonomy.difficulty must be one of "
                          f"{sorted(DIFFICULTIES)}")

    # -- verification ------------------------------------------------------------
    ver = rec.get("verification")
    if not isinstance(ver, dict):
        errors.append("verification must be a dict")
    else:
        if ver.get("status") not in VERIFICATION_STATUSES:
            errors.append(f"verification.status must be one of "
                          f"{sorted(VERIFICATION_STATUSES)}")
        if not isinstance(ver.get("match"), bool):
            errors.append("verification.match must be a bool")
        if not isinstance(ver.get("attempts"), int) or ver["attempts"] < 0:
            errors.append("verification.attempts must be a non-negative int")
        for k in ("solver_answer", "key_answer"):
            if k not in ver:
                errors.append(f"verification.{k} is required")

    # -- provenance --------------------------------------------------------------
    prov = rec.get("provenance")
    if not isinstance(prov, dict):
        errors.append("provenance must be a dict")
    else:
        for k in ("paper_pdf", "key_pdf", "extracted_at"):
            if not isinstance(prov.get(k), str) or not prov.get(k):
                errors.append(f"provenance.{k} must be a non-empty string")

    return errors


def validate_record_strict(rec: dict) -> dict:
    """Validate and return *rec*; raise :class:`SchemaError` on problems."""
    errors = validate_record(rec)
    if errors:
        raise SchemaError("invalid question record:\n- " + "\n- ".join(errors))
    return rec
