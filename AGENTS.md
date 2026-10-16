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
  strict KaTeX rendering of every math segment, dist data files present.
