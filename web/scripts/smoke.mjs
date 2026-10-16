// Smoke test: schema conformance + KaTeX render check for all seed records.
// Run: node scripts/smoke.mjs  (from web/)
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import katex from 'katex/dist/katex.mjs';
import 'katex/dist/contrib/mhchem.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const pub = join(root, 'public', 'data');
let failures = 0;
const fail = (msg) => { failures++; console.error('FAIL:', msg); };

// ---- 1. index.json resolves ----
const index = JSON.parse(readFileSync(join(pub, 'index.json'), 'utf8'));
for (const p of index.papers ?? []) {
  if (!existsSync(join(pub, p.file))) fail(`index references missing file ${p.file}`);
}
console.log(`index.json OK: ${(index.papers ?? []).length} paper(s)`);

// ---- 2. schema conformance ----
const REQUIRED = ['id','exam','year','paper','session','shift','subject','section','qtype',
  'number_in_subject','stem','stem_images','options','parent_stem','marking','answer',
  'solution','taxonomy','verification','provenance'];
const records = [];
for (const p of index.papers ?? []) {
  const arr = JSON.parse(readFileSync(join(pub, p.file), 'utf8'));
  for (const q of arr) records.push(q);
}
const ids = new Set();
// Image refs must resolve under public/data (bare "img-*.png" -> data/images/).
function resolveImage(p) {
  if (/^(https?:|data:|blob:)/.test(p)) return null; // remote/data URIs: skip
  const clean = String(p).replace(/^\/+/, '').replace(/^data\//, '');
  const rel = clean.includes('/') ? clean : `images/${clean}`;
  return join(pub, rel);
}
let incompleteN = 0;
const INCOMPLETE_RE = /not captured|\[figures? not available\]|\[plot figure\]|\[figure option/i;
for (const q of records) {
  for (const k of REQUIRED) if (!(k in q)) fail(`${q.id ?? '?'}: missing field ${k}`);
  if (ids.has(q.id)) fail(`duplicate id ${q.id}`);
  ids.add(q.id);
  if (!['physics','chemistry','mathematics'].includes(q.subject)) fail(`${q.id}: bad subject`);
  if (!['single_correct','multi_correct','numerical','matrix_match','stem_numerical'].includes(q.qtype)) fail(`${q.id}: bad qtype`);
  if (!['easy','medium','hard'].includes(q.taxonomy?.difficulty)) fail(`${q.id}: bad difficulty`);
  if (['single_correct','multi_correct','matrix_match'].includes(q.qtype) && (q.options == null || Object.keys(q.options).length < 2))
    fail(`${q.id}: MCQ without options`);
  if (['numerical','stem_numerical'].includes(q.qtype) && q.options != null) fail(`${q.id}: numerical with options`);
  if (['numerical','stem_numerical'].includes(q.qtype) && Number.isNaN(Number(q.answer.value))) fail(`${q.id}: non-numeric numerical answer`);
  if (!Array.isArray(q.stem_images)) fail(`${q.id}: stem_images must be a list`);
  for (const img of q.stem_images ?? []) {
    if (typeof img !== 'string' || !img.trim()) { fail(`${q.id}: bad stem_images entry`); continue; }
    const full = resolveImage(img);
    if (full && !existsSync(full)) fail(`${q.id}: missing image file ${img} (looked in ${full})`);
  }
  if (q.parent_stem != null && (typeof q.parent_stem !== 'string' || !q.parent_stem.trim())) fail(`${q.id}: bad parent_stem`);
  if (q.option_images != null) {
    if (typeof q.option_images !== 'object' || Array.isArray(q.option_images)) fail(`${q.id}: bad option_images`);
    else for (const [k, v] of Object.entries(q.option_images)) {
      if (!['A','B','C','D'].includes(k) || typeof v !== 'string' || !v.trim()) { fail(`${q.id}: bad option_images[${k}]`); continue; }
      const full = resolveImage(v);
      if (full && !existsSync(full)) fail(`${q.id}: missing option image ${v}`);
    }
  }
  const sol = q.solution ?? {};
  for (const k of ['concepts','formulas','steps','pitfalls','final_check']) if (!(k in sol)) fail(`${q.id}: solution missing ${k}`);
  const hay = `${q.stem ?? ''}\n${Object.values(q.options ?? {}).join('\n')}`;
  if (INCOMPLETE_RE.test(hay)) incompleteN++;
}
console.log(`schema OK: ${records.length} record(s), ids unique, ${incompleteN} flagged incomplete`);

// ---- 3. KaTeX renders every math segment (strict: throw on error) ----
function segments(text) {
  const out = [];
  let i = 0;
  while (i < text.length) {
    if (text.startsWith('$$', i)) {
      const end = text.indexOf('$$', i + 2);
      if (end !== -1) { out.push([text.slice(i + 2, end), true]); i = end + 2; continue; }
    }
    if (text[i] === '$') {
      const end = text.indexOf('$', i + 1);
      if (end !== -1) { out.push([text.slice(i + 1, end), false]); i = end + 1; continue; }
    }
    i++;
  }
  return out;
}
function textsOf(q) {
  const t = [q.stem, ...(Object.values(q.options ?? {})), ...(q.solution.formulas ?? []),
    ...(q.solution.steps ?? []).map(s => s.text), ...(q.solution.pitfalls ?? []), q.solution.final_check ?? ''];
  return t.filter(Boolean);
}
let segCount = 0, ceCount = 0;
for (const q of records) {
  for (const t of textsOf(q)) {
    for (const [tex, display] of segments(String(t))) {
      segCount++;
      if (tex.includes('\\ce')) ceCount++;
      try {
        katex.renderToString(tex, { displayMode: display, throwOnError: true, strict: true, trust: false });
      } catch (e) {
        fail(`${q.id}: KaTeX error in "${tex.slice(0, 60)}…": ${e.message}`);
      }
    }
  }
}
console.log(`KaTeX OK: ${segCount} math segments rendered strict, ${ceCount} using \\ce{}`);

// ---- 4. dist output has data files ----
for (const p of index.papers ?? []) {
  if (!existsSync(join(root, 'dist', 'data', p.file))) fail(`dist missing data/${p.file}`);
  if (!existsSync(join(root, 'dist', 'data', 'index.json'))) fail('dist missing data/index.json');
}
console.log('dist data files OK');

if (failures) { console.error(`\n${failures} FAILURE(S)`); process.exit(1); }
console.log('\nALL SMOKE TESTS PASSED');
