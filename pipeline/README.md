# JEE Pipeline

Content pipeline for the JEE question bank (Phase 1). Stages:

| Stage | Module | What it does |
|---|---|---|
| ingest | `jee_pipeline.ingest` | NTA paper PDF → raw per-question records (markers, option IDs, page images) |
| normalize | `jee_pipeline.normalize` | unicode math → LaTeX (`$…$`/`$$…$$`, KaTeX subset) |
| schema | `jee_pipeline.schema` | strict validator for the final question record JSON |
| keyparser | `jee_pipeline.keyparser` | NTA final-key PDF → `{question_id: answer}` for one shift |
| verify | `jee_pipeline.verify` | blind solver answer vs official key → verified/mismatch/dropped/needs_review |
| tag | `jee_pipeline.tag` | heuristic chapter + difficulty tagging (always flagged for review) |

Only the Python standard library is required. The PDF stages need the
poppler CLI tools: `pdftotext`, `pdfimages`, `pdfinfo`
(`apt install poppler-utils`).

## Usage

```python
from jee_pipeline import ingest, normalize, keyparser, verify, tag, schema

# 1. ingest a shift paper
records = ingest.ingest_paper("paper.pdf", "workdir/")
# records[0] -> {"question_number": 1, "question_id": "691121526",
#                "question_type": "MCQ", "subject": "mathematics", ...,
#                "content_images": ["img-000.png", ...], "text_available": False}

# 2. normalize text (when text exists)
rec = normalize.normalize_record(records[0])

# 3. heuristic tagging
print(tag.tag(rec))   # {"chapters": [...], "difficulty": "medium",
                      #  "heuristic": True, "needs_review": True, ...}

# 4. parse the official key for a shift
key = keyparser.parse_key("final_key.pdf", "08.04.2026", "Second", "india")
# key["answers"]["691121526"] -> {"kind": "option_id",
#                                 "value": "6911211786", "values": [...]}

# 5. verify a blind solver's answer
verdict = verify.verify(solver_answer="6911211786",
                        key=key["answers"]["691121526"],
                        qtype="MCQ",
                        question_id="691121526",
                        options=records[0]["options"],
                        dropped_ids=key["dropped"])
# -> {"status": "verified", "match": True, "detail": ..., "question_id": ...}

# 6. validate the final record before publishing
errors = schema.validate_record(final_record)   # [] == valid
```

Run the tests:

```bash
cd ~/workspace/jee-question-bank/pipeline
python3 -m pytest -q
```

## Notes from the pilot (JEE Main 2026, Session 2, Apr 8 Shift 2)

- The public NTA paper PDF renders stems and options as **raster images**;
  `pdftotext` recovers only the NTA metadata (Question Number/Id/Type markers,
  section headers, option IDs). `ingest` therefore attaches the question's
  page images as `content_images` and sets `text_available: False`.
  Transcription/OCR of stems is a later stage; the schema validator
  (`schema.py`) applies to the *final* record, where `stem` must be filled.
- The key PDF **must** be extracted with `pdftotext -raw`; `-layout` merges
  the ID columns and silently drops digits.
- The key has one page per (shift × centre-variant); India and outside-India
  variants use different ID spaces — pass `variant="india"` (default) or
  `"outside-india"`.
- Edge cases observed in real keys and handled: `"<qid> Dropped"` rows,
  multi-option keys (`"id1, id2"`), numeric answers, and `[lo to hi]` ranges.
