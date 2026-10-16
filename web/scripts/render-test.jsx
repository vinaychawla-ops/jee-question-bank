// Render test: exercises the real Tex/SolutionView/QuestionCard components via
// react-dom/server and asserts clean KaTeX output (no error spans).
import React from 'react';
import { renderToString } from 'react-dom/server';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { Tex } from '../src/lib/tex.jsx';
import { SolutionView } from '../src/components/SolutionView.jsx';
import { QuestionCard } from '../src/components/QuestionCard.jsx';

// Run from the web/ directory: node scripts/__rt.cjs
const records = JSON.parse(
  readFileSync(join(process.cwd(), 'public', 'data', 'main2026-s2.json'), 'utf8')
);

let failures = 0;
const fail = (m) => { failures++; console.error('FAIL:', m); };
const noop = () => {};

function allTexts(q) {
  return [
    q.stem,
    ...Object.values(q.options ?? {}),
    ...(q.solution.formulas ?? []),
    ...(q.solution.steps ?? []).map((s) => s.text),
    ...(q.solution.pitfalls ?? []),
    q.solution.final_check ?? '',
  ].filter(Boolean);
}

for (const q of records) {
  // 1. Tex over every text field
  let html = '';
  try {
    html = renderToString(
      React.createElement('div', null, allTexts(q).map((t, i) => React.createElement(Tex, { key: i }, t)))
    );
  } catch (e) {
    fail(`${q.id}: Tex threw: ${e.message}`);
    continue;
  }
  if (html.includes('katex-error')) fail(`${q.id}: katex-error span in Tex output`);
  if (!html.includes('katex')) fail(`${q.id}: no katex markup rendered at all`);
  // Raw \ce must not leak outside the MathML source annotations KaTeX emits.
  const noAnnot = html.replace(/<annotation[\s\S]*?<\/annotation>/g, '');
  if (noAnnot.includes('\\ce{')) fail(`${q.id}: raw \\ce left unprocessed (mhchem not registered)`);

  // 2. SolutionView renders
  try {
    const s = renderToString(React.createElement(SolutionView, { q }));
    if (s.includes('katex-error')) fail(`${q.id}: katex-error in SolutionView`);
  } catch (e) {
    fail(`${q.id}: SolutionView threw: ${e.message}`);
  }

  // 3. QuestionCard renders
  try {
    const c = renderToString(
      React.createElement(QuestionCard, {
        q, paperTitle: 'Test Paper', bookmarked: false, onToggleBookmark: noop, onOpen: noop,
      })
    );
    if (c.includes('katex-error')) fail(`${q.id}: katex-error in QuestionCard`);
  } catch (e) {
    fail(`${q.id}: QuestionCard threw: ${e.message}`);
  }
}

// 4. Chemistry \ce spot-check: must render KaTeX markup with subscripts
const chemHtml = renderToString(React.createElement(Tex, null, '$\\ce{2H2 + O2 -> 2H2O}$'));
if (chemHtml.includes('katex-error')) fail('spot-check: katex-error for \\ce');
if (!chemHtml.includes('msubsup') && !chemHtml.includes('vlist')) {
  fail('spot-check: \\ce did not produce subscript markup');
}
console.log('chem spot-check html length:', chemHtml.length);

if (failures) { console.error(`\n${failures} FAILURE(S)`); process.exit(1); }
console.log(`\nRENDER TEST PASSED for ${records.length} records`);
