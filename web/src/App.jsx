import React, { useEffect, useMemo, useState } from 'react';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { QuestionCard } from './components/QuestionCard';
import { QuestionDetail } from './components/QuestionDetail';
import { PracticeMode } from './components/PracticeMode';
import { BookmarksView } from './components/BookmarksView';
import { useBookmarks, useTheme } from './lib/store';
import { allChapters, allExams, allYears, applyFilters, emptyFilters, paperTitle } from './lib/filters';

async function loadData() {
  const indexRes = await fetch('data/index.json');
  if (!indexRes.ok) throw new Error(`index.json: HTTP ${indexRes.status}`);
  const index = await indexRes.json();
  const questions = [];
  for (const paper of index.papers ?? []) {
    const res = await fetch(`data/${paper.file}`);
    if (!res.ok) throw new Error(`${paper.file}: HTTP ${res.status}`);
    const records = await res.json();
    for (const q of records) questions.push({ ...q, _paper: paper });
  }
  return { index, questions };
}

function BankView({ questions, filters, setFilters, bookmarkedIds, onToggleBookmark, onOpen }) {
  const chapters = useMemo(() => allChapters(questions), [questions]);
  const exams = useMemo(() => allExams(questions), [questions]);
  const years = useMemo(() => allYears(questions), [questions]);
  const filtered = useMemo(
    () => applyFilters(questions, filters, bookmarkedIds),
    [questions, filters, bookmarkedIds]
  );
  const titleOf = (q) => paperTitle(q._paper);

  return (
    <div className="space-y-3">
      <FilterBar filters={filters} setFilters={setFilters} chapters={chapters} exams={exams} years={years} resultCount={filtered.length} />
      {filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center dark:border-slate-700">
          <p className="text-slate-500 dark:text-slate-400">No questions match these filters.</p>
          <button
            onClick={() => setFilters(emptyFilters())}
            className="mt-2 text-sm font-medium text-indigo-600 dark:text-indigo-300"
          >
            Clear filters
          </button>
        </div>
      ) : (
        <div className="space-y-2.5">
          {filtered.map((q) => (
            <QuestionCard
              key={q.id}
              q={q}
              paperTitle={titleOf(q)}
              bookmarked={bookmarkedIds.has(q.id)}
              onToggleBookmark={onToggleBookmark}
              onOpen={onOpen}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [route, setRoute] = useState({ name: 'bank' });
  const [filters, setFilters] = useState(emptyFilters());
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const { bookmarks, toggle, has } = useBookmarks();
  const { theme, toggle: toggleTheme } = useTheme();

  useEffect(() => {
    loadData().then(setData).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [route]);

  const go = (r) => setRoute(r);
  const openQuestion = (id) => setRoute({ name: 'question', id });

  const questions = data?.questions ?? [];
  const activeQuestion = route.name === 'question' ? questions.find((q) => q.id === route.id) : null;
  const titleOf = (q) => paperTitle(q._paper);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <Header
        route={route}
        go={go}
        theme={theme}
        onToggleTheme={toggleTheme}
        bookmarkCount={bookmarks.size}
      />

      <main className="mx-auto max-w-5xl px-3 py-4 sm:px-4 sm:py-6">
        {error && (
          <div className="rounded-xl border border-rose-300 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950/50 dark:text-rose-200">
            Failed to load question data: {error}
          </div>
        )}

        {!error && !data && (
          <div className="py-16 text-center text-slate-500 dark:text-slate-400">
            <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
            Loading question bank…
          </div>
        )}

        {!error && data && route.name === 'bank' && (
          <BankView
            questions={questions}
            filters={filters}
            setFilters={setFilters}
            bookmarkedIds={bookmarks}
            onToggleBookmark={toggle}
            onOpen={openQuestion}
          />
        )}

        {!error && data && route.name === 'question' && activeQuestion && (
          <QuestionDetail
            q={activeQuestion}
            paperTitle={titleOf(activeQuestion)}
            bookmarked={has(activeQuestion.id)}
            onToggleBookmark={toggle}
            onBack={() => go({ name: 'bank' })}
          />
        )}

        {!error && data && route.name === 'question' && !activeQuestion && (
          <div className="py-16 text-center">
            <p className="text-slate-500 dark:text-slate-400">Question not found.</p>
            <button onClick={() => go({ name: 'bank' })} className="mt-2 text-sm font-medium text-indigo-600 dark:text-indigo-300">
              ← Back to bank
            </button>
          </div>
        )}

        {!error && data && route.name === 'practice' && (
          <PracticeMode questions={questions} onExit={() => go({ name: 'bank' })} />
        )}

        {!error && data && route.name === 'bookmarks' && (
          <BookmarksView
            questions={questions}
            bookmarkedIds={bookmarks}
            paperTitleOf={titleOf}
            onToggleBookmark={toggle}
            onOpen={openQuestion}
            onBrowse={() => go({ name: 'bank' })}
          />
        )}
      </main>

      <footer className="mx-auto max-w-5xl px-4 pb-8 pt-2 text-center text-xs text-slate-400 dark:text-slate-600">
        JEE Question Bank · Phase 1 pilot · {questions.length} question{questions.length === 1 ? '' : 's'} ·
        solutions verified against official answer keys
      </footer>
    </div>
  );
}
