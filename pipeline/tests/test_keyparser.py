"""Tests for jee_pipeline.keyparser."""

import os

import pytest

from jee_pipeline import keyparser as kp

KEY_PDF = os.path.expanduser(
    "~/workspace/goals/jee-question-bank-phase-1/hidden_files/source/"
    "main2026_s2_final_key.pdf")

SYNTHETIC_PAGE = """\
NATIONAL TESTING AGENCY
JEE (Main) - 2026 : SESSION - 2 FINAL ANSWER KEY OF B.E. / B.Tech ON WHICH RESULT COMPILED
(For Centers in India)
Exam Date : 08.04.2026         Exam Shift : Second
9 of 18
QUESTION ID CORRECT OPTION ID         QUESTION ID CORRECT OPTION ID
  ( MATHEMATICS )
691121526 6911211786
691121546 2
  ( PHYSICS )
691121551 6911211900
691121560 6911211907, 6911211908
695278261 Dropped
"""


def test_parse_page_meta():
    parsed = kp.parse_page(SYNTHETIC_PAGE)
    assert parsed["meta"]["exam_date"] == "08.04.2026"
    assert parsed["meta"]["exam_shift"] == "Second"
    assert parsed["meta"]["variant"] == "india"


def test_parse_page_rows_and_subjects():
    parsed = kp.parse_page(SYNTHETIC_PAGE)
    assert parsed["answers"]["691121526"] == "6911211786"
    assert parsed["answers"]["691121546"] == "2"
    assert parsed["answers"]["691121560"] == "6911211907, 6911211908"
    assert parsed["subjects"]["691121526"] == "mathematics"
    assert parsed["subjects"]["691121551"] == "physics"


def test_parse_page_dropped():
    parsed = kp.parse_page(SYNTHETIC_PAGE)
    assert parsed["dropped"] == ["695278261"]
    assert "695278261" not in parsed["answers"]


def test_parse_page_ignores_header_junk():
    parsed = kp.parse_page("9 of 18\nQUESTION ID CORRECT OPTION ID\n")
    assert parsed["answers"] == {}


def test_classify_value():
    assert kp.classify_value("6911211786") == "option_id"
    assert kp.classify_value("232") == "numeric"
    assert kp.classify_value("2.33") == "numeric"
    assert kp.classify_value("-4") == "numeric"


def test_valid_value_rejects_junk():
    assert kp._valid_value("of 18") is False
    assert kp._valid_value("6911211786") is True
    assert kp._valid_value("99 to 101") is True
    assert kp._valid_value("Dropped") is True


# ---------------------------------------------------------------------------
# integration against the real key PDF
# ---------------------------------------------------------------------------

needs_pdf = pytest.mark.skipif(
    not os.path.exists(KEY_PDF), reason="key PDF fixture not present")


@needs_pdf
def test_parse_real_shift():
    parsed = kp.parse_key(KEY_PDF, "08.04.2026", "Second", "india")
    assert len(parsed["answers"]) == 75
    assert parsed["dropped"] == []

    q1 = parsed["answers"]["691121526"]
    assert q1 == {"kind": "option_id", "value": "6911211786",
                  "values": ["6911211786"]}

    # multi-option key (Q35): NTA accepted two options
    q35 = parsed["answers"]["691121560"]
    assert q35["kind"] == "option_id"
    assert q35["values"] == ["6911211907", "6911211908"]

    # numeric SA answer (Q21)
    q21 = parsed["answers"]["691121546"]
    assert q21 == {"kind": "numeric", "value": "2", "values": ["2"]}

    assert parsed["subjects"]["691121526"] == "mathematics"
    assert parsed["subjects"]["691121576"] == "chemistry"


@needs_pdf
def test_outside_india_variant_differs():
    india = kp.parse_key(KEY_PDF, "08.04.2026", "Second", "india")
    outside = kp.parse_key(KEY_PDF, "08.04.2026", "Second", "outside-india")
    assert len(outside["answers"]) == 75
    # different ID space per NTA's centre variants
    assert set(outside["answers"]).isdisjoint(set(india["answers"]))


@needs_pdf
def test_unknown_shift_raises():
    with pytest.raises(ValueError, match="No key page found"):
        kp.parse_key(KEY_PDF, "01.01.2020", "First", "india")
