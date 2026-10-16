# JEE Question Bank — Web App (Phase 1)

React + Vite + Tailwind CSS + KaTeX (with the mhchem extension for `\ce{}` chemistry).
No backend — question data is static JSON in `public/data/`.

## Run

```bash
npm install
npm run dev      # → http://localhost:5173
npm run build    # production build → dist/
```

## Features

- **Question bank**: filter by subject, chapter, difficulty, question type (MCQ / Numerical), full-text search, bookmark-only view
- **Study mode**: question detail with KaTeX-rendered stem/options; answer + step-by-step solution (concepts, formulas, pitfalls, final check) revealed on click
- **Practice mode**: timed session (configurable questions, minutes/question, subject), question palette, auto-submit on timeout, JEE Main marking (+4 / −1), score summary with per-question review
- **Bookmarks**: persisted in `localStorage`
- **Dark / light mode** toggle; mobile responsive

## Data contract

- `public/data/index.json` → `{ papers: [{ id, file, exam, year, paper, session, shift, question_count }] }`
- `public/data/<paper-id>.json` → array of question records per
  `~/workspace/goals/jee-question-bank-phase-1/hidden_files/schema-and-pipeline.md`
  (section 2). Seed: 4 hand-written Main 2026 Session 2 records.

## Tests

```bash
node scripts/smoke.mjs      # schema conformance + strict KaTeX render of all seed math
```

`scripts/render-test.jsx` (via esbuild + `react-dom/server`) exercises the real
`Tex`, `SolutionView`, and `QuestionCard` components; run:

```bash
./node_modules/.bin/esbuild scripts/render-test.jsx --bundle --platform=node \
  --format=cjs --loader:.jsx=jsx --outfile=scripts/__rt.cjs && node scripts/__rt.cjs
```
