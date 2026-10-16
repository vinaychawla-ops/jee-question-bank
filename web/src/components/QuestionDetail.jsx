import React, { useState } from 'react';
import { Tex } from '../lib/tex';
import { SolutionView } from './SolutionView';
import { Badge } from './QuestionCard';
import { difficultyLabel, subjectLabel, typeGroupLabel } from '../lib/filters';

function formatAnswer(q) {
  const v = String(q.answer.value);
  if (q.answer.tolerance != null) return `${v} (± ${q.answer.tolerance})`;
  return v;
}

/** Study view: stem + options, answer & solution revealed on click. */
export function QuestionDetail({ q, paperTitle, bookmarked, onToggleBookmark, onBack }) {
  const [revealed, setRevealed] = useState(false);
  const diff = q.taxonomy?.difficulty ?? 'medium';

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-3 flex items-center justify-between">
        <button
          onClick={onBack}
          className="rounded-lg px-2 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          ← Back to bank
        </button>
        <button
          onClick={() => onToggleBookmark(q.id)}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-medium transition ${
            bookmarked
              ? 'border-amber-400 bg-amber-50 text-amber-600 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-300'
              : 'border-slate-300 text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'
          }`}
          aria-pressed={bookmarked}
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill={bookmarked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
          {bookmarked ? 'Saved' : 'Save'}
        </button>
      </div>

      <article className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 sm:p-6">
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <Badge className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900/60 dark:text-indigo-200">
            {subjectLabel(q.subject)}
          </Badge>
          <Badge className="bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {typeGroupLabel(q)}
          </Badge>
          <Badge className="bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {difficultyLabel(diff)}
          </Badge>
          {(q.taxonomy?.chapters ?? []).map((c) => (
            <Badge key={c} className="bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
              {c}
            </Badge>
          ))}
        </div>
        <p className="mt-2 text-xs text-slate-400 dark:text-slate-500">{paperTitle}</p>

        <div className="mt-4 text-[16px] leading-relaxed text-slate-900 dark:text-slate-100">
          <Tex>{q.stem}</Tex>
        </div>

        {q.options && (
          <div className="mt-5 space-y-2">
            {Object.entries(q.options).map(([letter, text]) => (
              <div
                key={letter}
                className="flex items-start gap-3 rounded-lg border border-slate-200 px-3 py-2.5 dark:border-slate-700"
              >
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                  {letter}
                </span>
                <div className="min-w-0 flex-1 text-[15px] text-slate-800 dark:text-slate-200">
                  <Tex>{text}</Tex>
                </div>
              </div>
            ))}
          </div>
        )}

        {q.qtype === 'numerical' || q.qtype === 'stem_numerical' ? (
          <p className="mt-5 rounded-lg bg-slate-50 px-3 py-2.5 text-sm text-slate-500 dark:bg-slate-800/70 dark:text-slate-400">
            Numerical value — enter your answer rounded to two decimal places.
          </p>
        ) : null}

        <div className="mt-6 border-t border-slate-200 pt-4 dark:border-slate-800">
          {!revealed ? (
            <button
              onClick={() => setRevealed(true)}
              className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 sm:w-auto"
            >
              Reveal answer &amp; solution
            </button>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">Answer:</span>
                <span className="rounded-lg bg-emerald-100 px-3 py-1 font-mono text-base font-bold text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300">
                  <Tex>{`$${formatAnswer(q)}$`}</Tex>
                </span>
              </div>
              <SolutionView q={q} />
              <button
                onClick={() => setRevealed(false)}
                className="text-sm font-medium text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
              >
                Hide solution
              </button>
            </div>
          )}
        </div>
      </article>
    </div>
  );
}
