import { readFileSync } from 'fs';
import katex from 'katex/dist/katex.mjs';
import 'katex/dist/contrib/mhchem.mjs';
const segs = JSON.parse(readFileSync('/tmp/segments.json', 'utf8'));
let fail = 0;
const failures = [];
for (const [rid, where, tex] of segs) {
  try {
    katex.renderToString(tex, { throwOnError: true, displayMode: false, trust: true, strict: true });
  } catch (e) {
    fail++;
    if (failures.length < 20) failures.push([rid, where, tex.slice(0, 100), String(e.message || e).slice(0, 140)]);
  }
}
console.log(`rendered ${segs.length}, failures: ${fail}`);
for (const f of failures) console.log('FAIL', f[0], f[1], '\n  tex:', f[2], '\n  err:', f[3]);
