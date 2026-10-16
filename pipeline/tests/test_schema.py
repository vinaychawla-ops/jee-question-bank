"""Tests for jee_pipeline.schema."""

import copy

import pytest

from jee_pipeline.schema import (SchemaError, validate_record,
                                 validate_record_strict)


def valid_record():
    return {
        "id": "main2026-s2-8apr2-phy-q26",
        "exam": "JEE Main",
        "year": 2026,
        "paper": None,
        "session": "Session 2",
        "shift": "2026-04-08 Shift 2",
        "subject": "physics",
        "section": {"name": "Section A", "max_marks": 80},
        "qtype": "single_correct",
        "number_in_subject": 1,
        "stem": "A wire carries $I$ current. Find $B$.",
        "stem_images": ["q26_p007_img00.png"],
        "options": {"A": "$1$", "B": "$2$", "C": "$3$", "D": "$4$"},
        "parent_stem": None,
        "marking": {"correct": 4, "wrong": -1, "unanswered": 0, "partial": None},
        "answer": {"value": "C", "tolerance": None,
                   "source": "official_final_key"},
        "solution": {
            "concepts": ["Ampere's law"],
            "formulas": [r"$\oint \vec{B}\cdot d\vec{l} = \mu_0 I$"],
            "steps": [{"n": 1, "text": "Apply Ampere's law."},
                      {"n": 2, "text": "Solve for $B$."}],
            "pitfalls": ["Watch the sign."],
            "final_check": "Units check out.",
        },
        "taxonomy": {"chapters": ["Magnetism"], "difficulty": "medium"},
        "verification": {"solver_answer": "6911211908",
                         "key_answer": "6911211908",
                         "match": True, "status": "verified", "attempts": 1},
        "provenance": {"paper_pdf": "p.pdf", "key_pdf": "k.pdf",
                       "extracted_at": "2026-10-16T00:00:00Z"},
    }


def test_valid_record_passes():
    assert validate_record(valid_record()) == []
    assert validate_record_strict(valid_record())["id"].startswith("main2026")


def test_missing_and_bad_fields():
    rec = valid_record()
    del rec["stem"]
    rec["qtype"] = "essay"
    rec["taxonomy"]["difficulty"] = "extreme"
    errs = validate_record(rec)
    assert any("stem" in e for e in errs)
    assert any("qtype" in e for e in errs)
    assert any("difficulty" in e for e in errs)
    with pytest.raises(SchemaError):
        validate_record_strict(rec)


def test_options_required_for_mcq():
    rec = valid_record()
    rec["options"] = None
    assert any("options" in e for e in validate_record(rec))


def test_numerical_options_must_be_null_and_value_numeric():
    rec = valid_record()
    rec["qtype"] = "numerical"
    rec["options"] = {"A": "1"}
    rec["answer"] = {"value": "C", "tolerance": None, "source": "k"}
    errs = validate_record(rec)
    assert any("options = null" in e for e in errs)
    assert any("must be numeric" in e for e in errs)

    rec["options"] = None
    rec["answer"] = {"value": "2.33", "tolerance": 0.01, "source": "k"}
    assert validate_record(rec) == []


def test_tolerance_only_for_numerical():
    rec = valid_record()
    rec["answer"]["tolerance"] = 0.5
    assert any("tolerance" in e for e in validate_record(rec))


def test_multi_correct_letters_sorted_unique():
    rec = valid_record()
    rec["qtype"] = "multi_correct"
    rec["answer"] = {"value": "CA", "tolerance": None, "source": "k"}
    assert any("sorted unique" in e for e in validate_record(rec))
    rec["answer"]["value"] = "AC"
    assert validate_record(rec) == []


def test_steps_sequential():
    rec = valid_record()
    rec["solution"]["steps"] = [{"n": 1, "text": "a"}, {"n": 3, "text": "b"}]
    assert any("steps[2]" in e for e in validate_record(rec))


def test_non_dict_record():
    assert validate_record([1, 2]) == ["record must be a dict"]


def test_verification_status_enum():
    rec = valid_record()
    rec["verification"]["status"] = "maybe"
    assert any("verification.status" in e for e in validate_record(rec))
