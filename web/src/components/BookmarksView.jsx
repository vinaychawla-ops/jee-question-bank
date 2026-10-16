import React from 'react';
import { QuestionCard } from './QuestionCard';

export function BookmarksView({ questions, bookmarkedIds, paperTitleOf, onToggleBookmark, onOpen, onBrowse }) {
  const saved = questions.filter((q) => bookmarkedIds.has(q.id));

  if (saved.length === 0) {
    return (
      <div className="mx-auto max-w-xl rounded-xl border border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <p className="text-3xl">🔖</p>
        <h2 className="mt-2 font-bold text-slate-900 dark:text-white">No bookmarks yet</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Tap the bookmark icon on any question to save it here for revision.
        </p>
        <button
          onClick={onBrowse}
          className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          Browse questions
        </button>
      </div>
    );
  }

  return (
    <div>
      <h2 className="mb-3 text-lg font-bold text-slate-900 dark:text-white">
        Saved questions <span className="text-sm font-medium text-slate-400">({saved.length})</span>
      </h2>
      <div className="space-y-2.5">
        {saved.map((q) => (
          <QuestionCard
            key={q.id}
            q={q}
            paperTitle={paperTitleOf(q)}
            bookmarked
            onToggleBookmark={onToggleBookmark}
            onOpen={onOpen}
          />
        ))}
      </div>
    </div>
  );
}
