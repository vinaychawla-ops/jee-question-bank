"""Tests for jee_pipeline.normalize."""

from jee_pipeline import normalize as nz


def test_sqrt():
    assert nz.unicode_to_latex("√21") == r"\sqrt{21}"
    assert nz.unicode_to_latex("area = √3 / 2") == r"area = \sqrt{3} / 2"


def test_superscripts_subscripts():
    assert nz.unicode_to_latex("x² + y³") == "x^{2} + y^{3}"
    assert nz.unicode_to_latex("H₂O") == "H_{2}O"
    assert nz.unicode_to_latex("x⁻¹") == "x^{-1}"


def test_arrows_and_relations():
    out = nz.unicode_to_latex("α → β, x ≤ y, a ≠ b, ±2")
    assert r"\alpha" in out and r"\to" in out
    assert r"\leq" in out and r"\neq" in out and r"\pm" in out


def test_greek_and_misc():
    out = nz.unicode_to_latex("θ = 45°, π ≈ 3.14, ∑x, ∫f, ∞")
    assert r"\theta" in out and r"^\circ" in out
    assert r"\pi" in out and r"\approx" in out
    assert r"\sum" in out and r"\int" in out and r"\infty" in out


def test_combining_vec():
    assert nz.unicode_to_latex("a⃗ + b⃗") == r"\vec{a} + \vec{b}"


def test_fractions():
    assert nz.unicode_to_latex("½ + ¼") == r"\frac{1}{2} + \frac{1}{4}"


def test_wrap_math_basic():
    out = nz.wrap_math("If x^{2} + 2x = 0 then x is")
    assert out == "If $x^{2} + 2x = 0$ then x is"


def test_wrap_math_leaves_prose_alone():
    out = nz.wrap_math("There are 5 questions in section A")
    assert out == "There are 5 questions in section A"  # lone numbers not wrapped


def test_wrap_math_preserves_existing():
    out = nz.wrap_math("Given $x^2$ find x^{2} + 1")
    assert "$x^2$" in out
    assert out.count("$") == 4  # no double wrapping


def test_normalize_record():
    rec = {"stem_text": "If x² = 4, find x.",
           "options": [{"option_id": "1", "text": None},
                       {"option_id": "2", "text": "√2"}]}
    out = nz.normalize_record(rec)
    assert out["stem_latex"] == "If $x^{2} = 4,$ find x."
    assert out["options"][1]["text_latex"] == r"$\sqrt{2}$"
    assert "text_latex" not in out["options"][0]
    # original untouched
    assert rec["options"][1].get("text_latex") is None
