"""Tests for jee_pipeline.tag (heuristic classifier)."""

from jee_pipeline import tag as tg


def test_classify_physics_kinematics():
    out = tg.classify_chapters(
        "A projectile is launched with velocity 20 m/s at an angle.", "physics")
    assert out and out[0] == "Kinematics"


def test_classify_chemistry_organic():
    out = tg.classify_chapters(
        "Benzene undergoes nitration; the aromatic ring is stable.", "chemistry")
    assert "Hydrocarbons" in out


def test_classify_maths_probability():
    out = tg.classify_chapters(
        "Find the probability that a dice shows six.", "mathematics")
    assert out[0] == "Probability"


def test_classify_empty_or_unknown():
    assert tg.classify_chapters("", "physics") == []
    assert tg.classify_chapters("some text", "biology") == []
    assert tg.classify_chapters("zzz qqq", "physics") == []


def test_difficulty_baselines():
    assert tg.heuristic_difficulty("MCQ") == "medium"
    assert tg.heuristic_difficulty("multi_correct") == "hard"
    assert tg.heuristic_difficulty("matrix_match") == "hard"
    assert tg.heuristic_difficulty("SA", "x") == "medium"


def test_difficulty_length_bump():
    long_text = "word " * 200
    assert tg.heuristic_difficulty("MCQ", long_text) == "hard"


def test_tag_marks_heuristic_and_review():
    q = {"subject": "physics", "question_type": "MCQ",
         "stem_latex": "A projectile is launched."}
    out = tg.tag(q)
    assert out["heuristic"] is True
    assert out["needs_review"] is True
    assert out["chapters"] == ["Kinematics"]
    assert out["difficulty"] in ("easy", "medium", "hard")


def test_tag_empty_stem():
    q = {"subject": "mathematics", "question_type": "SA", "stem_text": ""}
    out = tg.tag(q)
    assert out["chapters"] == []
    assert out["difficulty"] == "medium"
    assert out["needs_review"] is True
