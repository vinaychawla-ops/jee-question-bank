import React from 'react';
import { Tex } from '../lib/tex';
import { difficultyLabel, isIncomplete, subjectLabel, typeGroupLabel } from '../lib/filters';

const DIFF_STYLE = {
  easy: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300',
  medium: 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300',
  hard: 'bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-300',
};

export function Badge({ children, className }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold ${className}`}>
      {children}
    </span>
  );
}

export function QuestionCard({ q, paperTitle, bookmarked, onToggleBookmark, onOpen }) {
  const diff = q.taxonomy?.difficulty ?? 'medium';
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-3 transition hover:border-indigo-300 hover:shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:hover:border-indigo-700 sm:p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-1.5">
          <Badge className="bg-indigo-100 text-indigo-700 dark:bg-indigo-900/60 dark:text-indigo-200">
            {subjectLabel(q.subject)}
          </Badge>
          <Badge className="bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {typeGroupLabel(q)}
          </Badge>
          <Badge className={DIFF_STYLE[diff] ?? DIFF_STYLE.medium}>{difficultyLabel(diff)}</Badge>
          {(q.taxonomy?.chapters ?? []).slice(0, 2).map((c) => (
            <Badge key={c} className="bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
              {c}
            </Badge>
          ))}
          {isIncomplete(q) && (
            <Badge className="bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300">
              Needs figure
            </Badge>
          )}
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleBookmark(q.id);
          }}
          className={`shrink-0 rounded-lg p-1.5 transition ${
            bookmarked
              ? 'text-amber-500'
              : 'text-slate-300 hover:text-amber-400 dark:text-slate-600 dark:hover:text-amber-400'
          }`}
          aria-label={bookmarked ? 'Remove bookmark' : 'Bookmark question'}
          aria-pressed={bookmarked}
          title={bookmarked ? 'Remove bookmark' : 'Bookmark'}
        >
          <svg className="h-5 w-5" viewBox="0 0 24 24" fill={bookmarked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      </div>

      <button onClick={() => onOpen(q.id)} className="mt-2 block w-full text-left">
        <div className="line-clamp-3 text-[15px] leading-relaxed text-slate-800 dark:text-slate-200">
          <Tex>{q.stem}</Tex>
        </div>
        <div className="mt-2 flex items-center justify-between">
          <span className="truncate text-xs text-slate-400 dark:text-slate-500">{paperTitle}</span>
          <span className="shrink-0 text-sm font-medium text-indigo-600 dark:text-indigo-300">
            Open →
          </span>
        </div>
      </button>
    </article>
  );
}
