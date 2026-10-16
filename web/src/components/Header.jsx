import React from 'react';

const NAV = [
  { name: 'bank', label: 'Question Bank' },
  { name: 'practice', label: 'Practice' },
  { name: 'bookmarks', label: 'Bookmarks' },
];

export function Header({ route, go, theme, onToggleTheme, bookmarkCount }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
      <div className="mx-auto flex max-w-5xl items-center gap-2 px-3 py-2.5 sm:gap-4 sm:px-4">
        <button
          onClick={() => go({ name: 'bank' })}
          className="flex items-center gap-2 text-left"
          aria-label="JEE Question Bank home"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 font-bold text-white">
            J
          </span>
          <span className="hidden text-base font-bold text-slate-900 dark:text-white sm:inline">
            JEE Question Bank
          </span>
        </button>

        <nav className="ml-1 flex flex-1 items-center gap-1 sm:ml-4">
          {NAV.map((item) => {
            const active = route.name === item.name;
            return (
              <button
                key={item.name}
                onClick={() => go({ name: item.name })}
                className={`rounded-lg px-2.5 py-1.5 text-sm font-medium transition sm:px-3 ${
                  active
                    ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/60 dark:text-indigo-200'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                }`}
              >
                {item.label}
                {item.name === 'bookmarks' && bookmarkCount > 0 && (
                  <span className="ml-1.5 rounded-full bg-indigo-600 px-1.5 py-0.5 text-[11px] font-semibold text-white">
                    {bookmarkCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        <button
          onClick={onToggleTheme}
          className="rounded-lg border border-slate-200 p-2 text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
        >
          {theme === 'dark' ? (
            <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="4" />
              <path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
            </svg>
          ) : (
            <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
            </svg>
          )}
        </button>
      </div>
    </header>
  );
}
