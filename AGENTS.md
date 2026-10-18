# AGENTS.md — jee-question-bank

## Repo conventions

- `pipeline/` is stdlib-only Python (poppler CLIs `pdftotext`/`pdfimages`/`pdfinfo`
  required). Run `python3 -m pytest -q` from `pipeline/` before any push.
- `web/` is React + Vite + Tailwind + KaTeX (`katex/dist/katex.mjs` ESM +
  `mhchem.mjs` on the same instance — never mix UMD and ESM builds).
- Content records follow the schema in the project spec
  (`../goals/jee-question-bank-phase-1/hidden_files/schema-and-pipeline.md` in
  the agent workspace). `pipeline/jee_pipeline/schema.py::validate_record_strict`
  is the publish gate — nothing ships without passing it.
- Solver outputs live under `solved/<subject>.json` in the agent workspace
  (NOT in this repo); only verified `pilot_final.json`-style records land in
  `web/public/data/`.
- Data is 32 papers / 2298 questions as of Oct 2026 (`web/public/data/*.json` + `index.json`; the smoke test prints the live count).
  Figures live in `web/public/data/images/`: official page renders
  (`<qid-prefix>-p<NN>.png`) and per-option crops (`<qid>-opt<A-D>.png`).
  `stem_images` entries use `images/<file>` paths (bare `img-*.png` filenames
  are legacy 404s — never add new ones). `option_images` is an optional
  `{A-D: path}` dict. `parent_stem` holds shared paragraph-setup text
  (never null for `stem_numerical`).
- Chapters must use the canonical taxonomy (`pipeline/jee_pipeline/taxonomy.py`,
  ~63 labels aligned with `tag.py`). Never introduce case variants or
  near-duplicate labels — run new chapters through `canonicalize()` first.
- No placeholder content in records: never `[plot figure]`,
  `[Figure option X — see paper]`, `not captured`, or `figures not available`.
  Figures that can't ship as images get a bracketed `[Figure: ...]` text
  description with all data needed to solve. The smoke test reports an
  `incomplete` count — it must be **0**.
- Web UI rules: the `isIncomplete()` warning (`web/src/lib/filters.js`) fires
  on placeholder text only — never on image presence. Never put `truncate`
  on filter labels. Search stays full-row (`sm:basis-full`). `paperTitle()`
  dedupes `session === paper` (Advanced shows `JEE Advanced · 2026 · Paper 2`).
- Secrets: Modal tokens live in untracked `.env` (gitignored). Never commit
  `.env`, `*_token*`, or credential output.

## Hard rules

- Solutions are written from scratch and verified against official keys.
  Review-queue items never publish. Never copy third-party solutions.
- Solvers work BLIND: no key PDF, no keyparser output, no `*key*` files.
- NTA key PDFs must be extracted with `pdftotext -raw` (`-layout` silently
  drops digits from ID columns). Enforced in `keyparser.py`.
- JSON hygiene: solver JSON must use doubled backslashes for LaTeX
  (`\\frac` in the file). Single `\t \b \n \r \f` sequences get silently
  converted to control characters by JSON parsers — see
  `fix_escapes.py` in the agent workspace.
- The web smoke test (`web/scripts/smoke.mjs`) must pass: schema fields,
  strict KaTeX rendering of every math segment, dist data files present,
  every `stem_images`/`option_images` path resolves, `incomplete` count is 0.
- Rebuild `web/dist` before every Modal deploy (`npm run build`); the deployed
  bundle hash must match local `dist/index.html`, or the deploy is stale.

## Performance

- The bank list shows 50 cards at a time with a "Show more (N remaining)" button
  (`web/src/App.jsx`). Rendering all cards at once does not scale: 1623 questions
  was ~331k DOM nodes (7.8 s, ~1.1 GB in a 2 GB headless Chrome); 2298 was ~470k
  nodes and did not finish in 100 s. Paginated: 51 cards, ~11k nodes, ~1 s.
  The "N questions match" count must still show the full filtered total.
  Do not remove pagination, and re-measure the first render when the bank grows.
- `web/dist` is not in git. Build it from the merged main right before every
  deploy (`cd web && npm run build`), run the smoke test, and check the deployed
  bundle hash matches local `dist/index.html`.
- Never deploy without Vinay's explicit go-ahead. He merges PRs himself; work
  goes on a branch plus PR, never straight to main.

## Answer sources and keys (lessons from the 2025 extension)

- The official NTA key PDF gives option IDs only, not letters. Map IDs to option
  text by question, never by position. Third-party "NTA Ans." labels are not
  NTA's own key.
- April 2025 papers were not checked against the official NTA key. Their answers
  match third-party printed keys only (Smartachievers, Allen, Getmarks, pyqbox,
  examplayground, exambro, askfilo, examside and similar). MCQs from those papers
  carry `needs_review`. Do not describe them as NTA-verified. The footer says
  "printed answer keys" for this reason.
- Printed keys, solutions and options have errors: garbled options, wrong key
  letters, dropped given data, a duplicate option. Re-derive every answer and
  match by question text, not by letter.
- When our answer differs from a key, check at least two other sources, use the
  most correct answer, and put a visible note in the solution listing the split
  (example: Apr 2 S1 Q24, 3 sources give 4949, 3 give 2477, we keep 2477).
  Never call a third-party key "NTA's answer".
- Disclose any solve that was not blind (printed answers visible, e.g. Apr 2 S2).
  Flag anything that could not be captured (figures, garbled text) in the note.
- Known source defects, flagged in their notes: Apr 8 Physics Q5 prints 0.36 K
  twice; Jan 23 S1 Chemistry Q1 has options C and D identical in the source.
  `adv2026-p1-phy-s4-p22.png` is an unreferenced image, harmless.

## Papers and dates

- 2025 April Main dates in the bank: Apr 2 (S1, S2), Apr 3, Apr 4, Apr 7, Apr 8. Apr 8 had a single shift (3-6 PM). Apr 9 was B.Arch/B.Planning
  only, so there is no B.Tech paper for it (NTA notice dated Mar 10, 2025:
  https://cdnbbsr.s3waas.gov.in/s3f8e59f4b2fe7c5705bf878bbd494ccdf/uploads/2025/03/2025031089.pdf).
  Do not chase a missing engineering paper for Apr 9.
- Record ids look like `main2025-0407-s1-mat-a-q01`.

## Workflow for adding a paper

- One paper (shift) per branch and PR. Add the paper JSON, its images, and an
  entry in `web/public/data/index.json`.
- Before pushing, merge `origin/main` into the branch (no force push). If
  `index.json` conflicts, keep the union of all entries, never drop one. Then
  run `node web/scripts/smoke.mjs` (it needs the new JSON in `web/dist` data, so
  build first) and push.
- Check images are real PNGs and return 200; every referenced file must exist.
