"""Tests for jee_pipeline.verify."""

import pytest

from jee_pipeline import verify as vf

OPTIONS = [{"option_id": "6911211786", "text": None},
           {"option_id": "6911211787", "text": None},
           {"option_id": "6911211788", "text": None},
           {"option_id": "6911211789", "text": None}]
OPT_KEY = {"kind": "option_id", "value": "6911211786",
           "values": ["6911211786"]}


def test_mcq_option_id_exact_match():
    r = vf.verify("6911211786", OPT_KEY, "MCQ", question_id="q1",
                  options=OPTIONS)
    assert r["status"] == "verified" and r["match"] is True


def test_mcq_option_id_mismatch():
    r = vf.verify("6911211789", OPT_KEY, "MCQ", question_id="q1",
                  options=OPTIONS)
    assert r["status"] == "mismatch" and r["match"] is False


def test_mcq_letter_resolution():
    # "A" -> first option id -> matches key
    r = vf.verify("A", OPT_KEY, "MCQ", options=OPTIONS)
    assert r["status"] == "verified"
    # "B" -> second option id -> mismatch
    r = vf.verify("B", OPT_KEY, "MCQ", options=OPTIONS)
    assert r["status"] == "mismatch"
    # 1-based index
    r = vf.verify("1", OPT_KEY, "MCQ", options=OPTIONS)
    assert r["status"] == "verified"


def test_mcq_multi_option_key():
    key = {"kind": "option_id", "value": "6911211907, 6911211908",
           "values": ["6911211907", "6911211908"]}
    assert vf.verify("6911211908", key, "MCQ")["status"] == "verified"
    assert vf.verify("6911211909", key, "MCQ")["status"] == "mismatch"


def test_letter_key_advanced_style():
    key = {"kind": "letter", "value": "C", "values": ["C"]}
    assert vf.verify("C", key, "single_correct")["status"] == "verified"
    assert vf.verify("c", key, "single_correct")["status"] == "verified"
    assert vf.verify("D", key, "single_correct")["status"] == "mismatch"


def test_multi_correct_letter_sorting():
    key = {"kind": "letter", "value": "AC", "values": ["AC"]}
    assert vf.verify("CA", key, "multi_correct")["status"] == "verified"
    assert vf.verify("ACD", key, "multi_correct")["status"] == "mismatch"
    with pytest.raises(ValueError):
        vf.normalize_letters("AX")


def test_numerical_exact_and_tolerance():
    key = {"kind": "numeric", "value": "2", "values": ["2"]}
    assert vf.verify("2", key, "SA")["status"] == "verified"
    assert vf.verify("2.0", key, "numerical")["status"] == "verified"
    assert vf.verify("3", key, "SA")["status"] == "mismatch"


def test_numerical_default_tolerance():
    key = {"kind": "numeric", "value": "2.33", "values": ["2.33"]}
    assert vf.verify("2.335", key, "SA")["status"] == "verified"  # |d|=0.005
    assert vf.verify("2.35", key, "SA")["status"] == "mismatch"   # |d|=0.02


def test_numerical_key_range():
    key = {"kind": "numeric", "value": "[99 to 101]", "values": ["[99 to 101]"]}
    assert vf.verify("100", key, "SA")["status"] == "verified"
    assert vf.verify("100.5", key, "SA")["status"] == "verified"
    assert vf.verify("102", key, "SA")["status"] == "mismatch"


def test_dropped_question():
    r = vf.verify("anything", OPT_KEY, "MCQ", question_id="695278261",
                  dropped_ids=["695278261"])
    assert r["status"] == "dropped" and r["match"] is False


def test_unparseable_becomes_needs_review():
    r = vf.verify("not a number", {"kind": "numeric", "value": "2",
                                   "values": ["2"]}, "SA")
    assert r["status"] == "needs_review"
    r = vf.verify("Z", {"kind": "letter", "value": "C",
                        "values": ["C"]}, "MCQ")
    assert r["status"] == "needs_review"


def test_unsupported_qtype_raises_through_verify():
    r = vf.verify("x", OPT_KEY, "essay")
    assert r["status"] == "needs_review"
