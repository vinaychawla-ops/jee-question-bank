"""Stage 2 — normalize: unicode math -> LaTeX (KaTeX-compatible subset).

Per the spec (section 3): inline ``$...$``, display ``$$...$$``; unicode
symbols become LaTeX commands; superscripts/subscripts become ``^{}``/``_{}``;
chemistry uses ``\\ce{}`` (mhchem).

Two entry points:

- :func:`unicode_to_latex` — pure character-level conversion, no math-mode
  wrapping. Idempotent for its own output.
- :func:`wrap_math` — heuristic segmentation: after conversion, maximal runs
  of "mathy" tokens are wrapped in ``$...$``. Existing ``$...$``/``$$...$$``
  segments are left untouched. This is intentionally heuristic (plain-text
  extraction cannot know author intent); every wrapped segment should be
  eyeballed before publishing.

- :func:`normalize_record` — applies both to a raw ingest record, filling
  ``stem_latex`` (and per-option ``text_latex`` when option text exists).
"""

import re

# ---------------------------------------------------------------------------
# 1. character maps
# ---------------------------------------------------------------------------

_SIMPLE_MAP = {
    "→": r"\to", "←": r"\leftarrow", "⇒": r"\Rightarrow",
    "⇔": r"\Leftrightarrow", "↔": r"\leftrightarrow",
    "≤": r"\leq", "≥": r"\geq", "≠": r"\neq", "±": r"\pm",
    "×": r"\times", "·": r"\cdot", "÷": r"\div", "∞": r"\infty",
    "≈": r"\approx", "≡": r"\equiv", "∈": r"\in", "∉": r"\notin",
    "⊂": r"\subset", "⊆": r"\subseteq", "∪": r"\cup", "∩": r"\cap",
    "∅": r"\emptyset", "∑": r"\sum", "∏": r"\prod", "∫": r"\int",
    "∂": r"\partial", "∇": r"\nabla", "…": r"\ldots",
    "′": "'", "″": "''",
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "ε": r"\epsilon", "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta",
    "ι": r"\iota", "κ": r"\kappa", "λ": r"\lambda", "μ": r"\mu",
    "ν": r"\nu", "ξ": r"\xi", "π": r"\pi", "ρ": r"\rho",
    "σ": r"\sigma", "τ": r"\tau", "φ": r"\phi", "χ": r"\chi",
    "ψ": r"\psi", "ω": r"\omega",
    "Γ": r"\Gamma", "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda",
    "Ξ": r"\Xi", "Π": r"\Pi", "Σ": r"\Sigma", "Φ": r"\Phi",
    "Ψ": r"\Psi", "Ω": r"\Omega",
    "½": r"\frac{1}{2}", "¼": r"\frac{1}{4}", "¾": r"\frac{3}{4}",
    "⅓": r"\frac{1}{3}", "⅔": r"\frac{2}{3}",
    "√": None,  # handled specially (takes an argument)
    "°": None,  # handled specially -> ^\circ
}

_SUPERSCRIPT_MAP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
                    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
                    "⁻": "-", "⁺": "+"}
_SUBSCRIPT_MAP = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
                  "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
                  "₋": "-", "₊": "+"}

#: combining diacritic -> LaTeX accent command (applied to preceding char)
_COMBINING_MAP = {
    "⃗": "vec",   # U+20D7 combining right arrow above
    "\u0305": "bar",
    "\u0302": "hat",
    "\u0303": "tilde",
    "\u0307": "dot",
    "\u0308": "ddot",
    "\u0304": "bar",
}

_SUP_RE = re.compile(
    r"([A-Za-z0-9\)\]\}])((?:" + "|".join(re.escape(c) for c in _SUPERSCRIPT_MAP) + r")+)"
)
_SUB_RE = re.compile(
    r"([A-Za-z0-9\)\]\}])((?:" + "|".join(re.escape(c) for c in _SUBSCRIPT_MAP) + r")+)"
)
_SQRT_RE = re.compile(r"√\s*(\S+)")
_COMBINING_RE = re.compile(
    r"(.)(" + "|".join(re.escape(c) for c in _COMBINING_MAP) + r")"
)


def _map_superscript(m: re.Match) -> str:
    base, marks = m.group(1), m.group(2)
    digits = "".join(_SUPERSCRIPT_MAP[c] for c in marks)
    return f"{base}^{{{digits}}}"


def _map_subscript(m: re.Match) -> str:
    base, marks = m.group(1), m.group(2)
    digits = "".join(_SUBSCRIPT_MAP[c] for c in marks)
    return f"{base}_{{{digits}}}"


def _map_sqrt(m: re.Match) -> str:
    token = m.group(1)
    # strip trailing punctuation that is clearly not part of the radicand
    token = token.rstrip(",;.")
    return r"\sqrt{" + token + "}"


def unicode_to_latex(text: str) -> str:
    """Convert unicode math in *text* to LaTeX commands (no $ wrapping)."""
    if not text:
        return text
    # combining accents: a⃗ -> \vec{a}
    text = _COMBINING_RE.sub(
        lambda m: "\\%s{%s}" % (_COMBINING_MAP[m.group(2)], m.group(1)), text)
    # superscripts / subscripts
    text = _SUP_RE.sub(_map_superscript, text)
    text = _SUB_RE.sub(_map_subscript, text)
    # square roots (before the generic single-char map)
    text = _SQRT_RE.sub(_map_sqrt, text)
    text = text.replace("√", r"\sqrt{}")
    # degrees: 45° -> 45^\circ
    text = text.replace("°", r"^\circ")
    for ch, cmd in _SIMPLE_MAP.items():
        if cmd is None or ch in ("√", "°"):
            continue
        text = text.replace(ch, cmd + " ")
    # tidy: collapse accidental double spaces, strip trailing spaces per line
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"[ \t]+(\n|$)", r"\1", text)
    return text


# ---------------------------------------------------------------------------
# 2. math-mode wrapping (heuristic)
# ---------------------------------------------------------------------------

_MATH_SEGMENT_RE = re.compile(r"\$\$.*?\$\$|\$[^$]*?\$", re.DOTALL)
_MATHY_OPS = set("+-*/=<>")


def _is_mathy(token: str) -> bool:
    t = token.strip(",;:.!?")
    if re.search(r"[\\_^]", t):
        return True
    if re.search(r"\d", t) and re.search(r"[A-Za-z]", t):
        return True  # e.g. 2x, x1
    if t in _MATHY_OPS:
        return True
    if re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", t):
        return True  # pure number (only wrapped inside a run)
    if ("(" in t or ")" in t) and (
            re.search(r"[\\_^]", t)
            or (re.search(r"\d", t) and re.search(r"[A-Za-z]", t))):
        return True
    return False


def _run_has_core(tokens: list[str]) -> bool:
    """A wrap-worthy run needs at least one token with real math content."""
    return any(
        re.search(r"[\\_^]", t)
        or (re.search(r"\d", t) and re.search(r"[A-Za-z]", t))
        for t in tokens
    )


def _wrap_plain_segment(segment: str) -> str:
    tokens = segment.split()
    out: list[str] = []
    i = 0
    while i < len(tokens):
        if _is_mathy(tokens[i]):
            j = i
            while j < len(tokens) and _is_mathy(tokens[j]):
                j += 1
            run = tokens[i:j]
            if _run_has_core(run):
                out.append("$" + " ".join(run) + "$")
            else:
                out.extend(run)  # lone numbers etc.: leave alone
            i = j
        else:
            out.append(tokens[i])
            i += 1
    return " ".join(out)


def wrap_math(text: str) -> str:
    """Wrap heuristic math runs in ``$...$``; existing math left alone."""
    if not text:
        return text
    parts = _MATH_SEGMENT_RE.split(text)
    segs = _MATH_SEGMENT_RE.findall(text)
    out: list[str] = []
    for k, part in enumerate(parts):
        # a whole line that is one math run -> display math
        lines = part.split("\n")
        new_lines = []
        for line in lines:
            stripped = line.strip()
            toks = stripped.split()
            if (len(stripped) > 40 and toks
                    and all(_is_mathy(t) for t in toks)
                    and _run_has_core(toks)):
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f"{indent}$${stripped}$$")
            else:
                new_lines.append(_wrap_plain_segment(line))
        out.append("\n".join(new_lines))
        if k < len(segs):
            out.append(segs[k])
    return "".join(out)


def normalize_text(text: str) -> str:
    """Full text normalization: unicode -> LaTeX, then math wrapping."""
    return wrap_math(unicode_to_latex(text))


def normalize_record(record: dict) -> dict:
    """Return a copy of a raw ingest record with ``stem_latex`` added."""
    rec = dict(record)
    rec["stem_latex"] = normalize_text(rec.get("stem_text") or "")
    options = []
    for opt in rec.get("options", []):
        opt = dict(opt)
        if opt.get("text"):
            opt["text_latex"] = normalize_text(opt["text"])
        options.append(opt)
    rec["options"] = options
    return rec
