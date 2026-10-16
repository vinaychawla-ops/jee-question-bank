"""Tests for jee_pipeline.ingest."""

import glob
import os

import pytest

from jee_pipeline import ingest

PAPER_PDF = os.path.expanduser(
    "~/workspace/goals/jee-question-bank-phase-1/hidden_files/source/"
    "main2026_s2_8apr_s2_paper.pdf")

SYNTHETIC = """\
                                        National Testing Agency

Question Paper Name : B Tech 8th Apr 2026 Shift 2

                                           Mathematics Section A
Section Id : 69112143

Question Number : 1 Question Id : 691121526 Question Type : MCQ Option Shuffling : Yes Display Question Number : Yes Is
Question Mandatory : No Single Line Question Option : No Option Orientation : Vertical

If $x$ is real, the value of the expression is shown in figure 1.

Options :

6911211786.

6911211787.

6911211788.

6911211789.
Question Number : 2 Question Id : 691121527 Question Type : MCQ Option Shuffling : Yes Display Question Number : Yes Is
Question Mandatory : No Single Line Question Option : No Option Orientation : Vertical




Options :

6911211790.

6911211791.

6911211792.

6911211793.
                                           Mathematics Section B

Question Number : 21 Question Id : 691121546 Question Type : SA Display Question Number : Yes Keyboard Layout : Inscript
Response Type : Numeric
Evaluation Required For SA : Yes
Show Word Count : Yes
Answers Type : Equal
Text Areas : PlainText
Possible Answers :
1
"""


def test_parse_question_count_and_markers():
    recs = ingest.parse_questions(SYNTHETIC)
    assert len(recs) == 3
    assert [r["question_number"] for r in recs] == [1, 2, 21]
    assert [r["question_id"] for r in recs] == ["691121526", "691121527", "691121546"]
    assert [r["question_type"] for r in recs] == ["MCQ", "MCQ", "SA"]


def test_parse_options_ids_only():
    recs = ingest.parse_questions(SYNTHETIC)
    opts = recs[0]["options"]
    assert [o["option_id"] for o in opts] == [
        "6911211786", "6911211787", "6911211788", "6911211789"]
    assert all(o["text"] is None for o in opts)


def test_sa_has_no_options_and_clean_stem():
    recs = ingest.parse_questions(SYNTHETIC)
    sa = recs[2]
    assert sa["options"] == []
    assert sa["stem_text"] == ""  # metadata incl. "Possible Answers: 1" stripped
    assert sa["text_available"] is False


def test_section_context():
    recs = ingest.parse_questions(SYNTHETIC)
    assert (recs[0]["subject"], recs[0]["section"]) == ("mathematics", "A")
    assert (recs[2]["subject"], recs[2]["section"]) == ("mathematics", "B")


def test_figure_reference_flagged():
    recs = ingest.parse_questions(SYNTHETIC)
    assert recs[0]["figure_references"]  # "figure 1" in stem
    assert "figure 1" in recs[0]["figure_references"][0].lower()
    assert recs[1]["figure_references"] == []


def test_stem_text_kept_when_present():
    recs = ingest.parse_questions(SYNTHETIC)
    assert "If $x$ is real" in recs[0]["stem_text"]
    assert recs[0]["text_available"] is True


# ---------------------------------------------------------------------------
# integration against the real pilot PDF
# ---------------------------------------------------------------------------

needs_pdf = pytest.mark.skipif(
    not os.path.exists(PAPER_PDF), reason="pilot PDF fixture not present")


@needs_pdf
def test_integration_full_paper_parse(tmp_path):
    recs = ingest.ingest_paper(
        PAPER_PDF, str(tmp_path),
        extract_images_flag=True, image_first_page=1, image_last_page=2)
    assert len(recs) == 75

    q1 = recs[0]
    assert q1["question_number"] == 1
    assert q1["question_id"] == "691121526"
    assert q1["question_type"] == "MCQ"
    assert q1["subject"] == "mathematics" and q1["section"] == "A"
    assert [o["option_id"] for o in q1["options"]] == [
        "6911211786", "6911211787", "6911211788", "6911211789"]
    assert q1["text_available"] is False  # stems are raster images in this PDF
    assert q1["pages"][0] == 1
    assert q1["content_images"]  # page-1 images attached

    q21 = recs[20]
    assert (q21["question_number"], q21["question_id"], q21["question_type"]) == \
        (21, "691121546", "SA")
    assert q21["options"] == []
    assert (q21["subject"], q21["section"]) == ("mathematics", "B")

    assert recs[25]["subject"] == "physics" and recs[25]["section"] == "A"
    assert recs[50]["subject"] == "chemistry" and recs[50]["section"] == "A"
    assert recs[74]["question_number"] == 75

    # every question got a page span and the numbers are sequential
    assert [r["question_number"] for r in recs] == list(range(1, 76))

    extracted = glob.glob(str(tmp_path / "images" / "*.png"))
    assert extracted  # images really were written to disk


@needs_pdf
def test_extract_images_bounded(tmp_path):
    rows = ingest.extract_images(PAPER_PDF, str(tmp_path), 1, 2)
    assert rows
    assert {r["page"] for r in rows} <= {1, 2}
    assert all(os.path.exists(r["path"]) for r in rows)
