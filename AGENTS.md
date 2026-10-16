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
- Data is 11 papers / 777 questions (`web/public/data/*.json` + `index.json`).
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
