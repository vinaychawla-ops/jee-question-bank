# JEE Question Bank

A web application and content pipeline that archives JEE (Main & Advanced)
question papers with accurate, step-by-step solutions — every solution written
from scratch and verified against the official answer key.

**Phase 1** (this repo): content pipeline + web app, seeded with one fully
solved pilot paper — **JEE Main 2026, Session 2, April 8 Shift 2**
(73 of 75 questions verified; 2 under human review).

## Layout

- `pipeline/` — Python content pipeline (`jee_pipeline` package):
  PDF ingest (question boundary detection, diagram flagging), unicode→LaTeX
  normalization, strict schema validation, NTA final-key parser, blind-solve
  verifier (letter/numeric/tolerance matching, dropped-question handling),
  heuristic chapter/difficulty tagger. 56 pytest tests.
- `web/` — React + Vite + Tailwind + KaTeX (with mhchem) question-bank app.
  Static JSON data, no backend. Study mode (reveal solutions), timed practice
  mode, filters (subject/chapter/difficulty/type), bookmarks, dark/light mode,
  mobile responsive.

## Verification methodology

1. Questions are extracted from the official NTA paper PDF.
2. Each question is solved **blind** (no access to the answer key) with a full
   step-by-step solution.
3. The blind answer is compared against the **NTA official final answer key**
   (Question ID → correct answer). Matches publish; mismatches get one careful
   re-solve; persistent mismatches go to a human review queue and are **never
   published**.
4. Pilot result: 71/75 verified on first pass; after re-solve, 73/75 verified.
   The 2 disputed questions (both chemistry judgment calls) are documented in
   the review queue.

## Quick start

```bash
# pipeline
cd pipeline && python3 -m pytest -q

# web app
cd web && npm install && npm run dev     # http://localhost:5173
cd web && npm run build                  # static dist/ output
```

## Data

`web/public/data/main2026-s2.json` — the 73 verified question records.
`web/public/data/index.json` — paper index. Phase 2 will add the remaining
papers across 5 years of JEE Main & Advanced.

## Sources

- Questions: official NTA/IIT paper PDFs (public releases).
- Answers: official NTA/IIT final answer keys.
- All solutions are original. Third-party solution content is never copied.
