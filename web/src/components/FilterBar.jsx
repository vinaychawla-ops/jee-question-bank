import React from 'react';
import { DIFFICULTIES, SUBJECTS, TYPE_GROUPS, emptyFilters } from '../lib/filters';

function Select({ label, value, onChange, options, allLabel }) {
  return (
    <label className="flex min-w-0 flex-col gap-1">
      <span className="truncate whitespace-nowrap text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
        {label}
      </span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-900 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 sm:w-36"
      >
        <option value="">{allLabel}</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export function FilterBar({ filters, setFilters, chapters, exams, years, resultCount }) {
  const set = (key) => (value) => setFilters((f) => ({ ...f, [key]: value }));
  const activeCount = ['exam', 'year', 'subject', 'chapter', 'difficulty', 'typeGroup'].filter((k) => filters[k]).length
    + (filters.bookmarkedOnly ? 1 : 0)
    + (filters.search.trim() ? 1 : 0);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900 sm:p-4">
      <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-end sm:gap-3">
        <Select label="Exam" value={filters.exam} onChange={set('exam')} options={exams.map((e) => ({ value: e, label: e }))} allLabel="All exams" />
        <Select label="Year" value={filters.year} onChange={set('year')} options={years.map((y) => ({ value: y, label: y }))} allLabel="All years" />
        <Select label="Subject" value={filters.subject} onChange={set('subject')} options={SUBJECTS} allLabel="All subjects" />
        <Select
          label="Chapter"
          value={filters.chapter}
          onChange={set('chapter')}
          options={chapters.map((c) => ({ value: c, label: c }))}
          allLabel="All chapters"
        />
        <Select label="Difficulty" value={filters.difficulty} onChange={set('difficulty')} options={DIFFICULTIES} allLabel="All levels" />
        <Select label="Type" value={filters.typeGroup} onChange={set('typeGroup')} options={TYPE_GROUPS} allLabel="All types" />

        <label className="col-span-2 flex min-w-0 flex-col gap-1 sm:col-span-1 sm:flex-1">
          <span className="truncate whitespace-nowrap text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Search
          </span>
          <input
            value={filters.search}
            onChange={(e) => set('search')(e.target.value)}
            placeholder="Search questions…"
            className="w-full rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-900 placeholder:text-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
        </label>

        <div className="col-span-2 flex gap-2 sm:contents">
          <button
            onClick={() => setFilters((f) => ({ ...f, bookmarkedOnly: !f.bookmarkedOnly }))}
            className={`rounded-lg border px-3 py-2 text-sm font-medium transition ${
              filters.bookmarkedOnly
                ? 'border-indigo-600 bg-indigo-600 text-white'
                : 'border-slate-300 text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'
            }`}
            aria-pressed={filters.bookmarkedOnly}
          >
            ★ Saved
          </button>

          {activeCount > 0 && (
            <button
              onClick={() => setFilters(emptyFilters())}
              className="rounded-lg px-3 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 dark:text-indigo-300 dark:hover:bg-indigo-900/40"
            >
              Clear ({activeCount})
            </button>
          )}
        </div>
      </div>
      <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
        {resultCount} question{resultCount === 1 ? '' : 's'} match
      </p>
    </div>
  );
}
