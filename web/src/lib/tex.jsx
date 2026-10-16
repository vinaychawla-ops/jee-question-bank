import React from 'react';
// ESM builds so the mhchem extension registers on this exact katex instance
// (mhchem.mjs imports ../katex.mjs).
import katex from 'katex/dist/katex.mjs';
// Registers \ce{} and friends (mhchem) on the katex instance.
import 'katex/dist/contrib/mhchem.mjs';

const KATEX_OPTS = { throwOnError: false, strict: false, trust: false };

/**
 * Split mixed prose+LaTeX into segments.
 * Supports $$...$$ (display) and $...$ (inline). Escaped \$ is left alone.
 */
function tokenize(input) {
  const text = String(input ?? '');
  const segments = [];
  let i = 0;
  let buf = '';
  const pushText = () => {
    if (buf) segments.push({ kind: 'text', value: buf });
    buf = '';
  };
  while (i < text.length) {
    if (text[i] === '\\' && text[i + 1] === '$') {
      buf += '$';
      i += 2;
      continue;
    }
    if (text.startsWith('$$', i)) {
      const end = text.indexOf('$$', i + 2);
      if (end !== -1) {
        pushText();
        segments.push({ kind: 'math', display: true, value: text.slice(i + 2, end) });
        i = end + 2;
        continue;
      }
    }
    if (text[i] === '$') {
      const end = text.indexOf('$', i + 1);
      if (end !== -1) {
        pushText();
        segments.push({ kind: 'math', display: false, value: text.slice(i + 1, end) });
        i = end + 1;
        continue;
      }
    }
    buf += text[i];
    i += 1;
  }
  pushText();
  return segments;
}

function renderMath(tex, display) {
  try {
    return katex.renderToString(tex, { ...KATEX_OPTS, displayMode: display });
  } catch {
    // throwOnError:false should prevent this, but stay safe.
    return `<span class="text-red-500">${tex}</span>`;
  }
}

function escapeHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Render a plain-text segment as HTML.
 * The pipeline stores newlines as literal "\n" (backslash + n) and uses
 * **double asterisks** for emphasis, so convert both here. Math segments
 * are untouched.
 */
function renderText(text) {
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Literal backslash-n sequences and any real newlines become line breaks.
  html = html.replace(/\\n/g, '<br/>').replace(/\r?\n/g, '<br/>');
  return html;
}

/**
 * Render a string that mixes plain text with $...$ / $$...$$ LaTeX,
 * including \ce{} chemistry via mhchem.
 */
export function Tex({ children, className }) {
  const segments = React.useMemo(() => tokenize(children), [children]);
  return (
    <span className={className}>
      {segments.map((seg, idx) =>
        seg.kind === 'text' ? (
          <span key={idx} dangerouslySetInnerHTML={{ __html: renderText(seg.value) }} />
        ) : (
          <span
            key={idx}
            className={seg.display ? 'katex-display block' : undefined}
            dangerouslySetInnerHTML={{ __html: renderMath(seg.value, seg.display) }}
          />
        )
      )}
    </span>
  );
}

/** Convenience block wrapper for display math paragraphs. */
export function TexBlock({ children, className }) {
  return (
    <div className={className}>
      <Tex>{children}</Tex>
    </div>
  );
}
