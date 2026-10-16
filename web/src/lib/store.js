import { useCallback, useEffect, useState } from 'react';

const BOOKMARKS_KEY = 'jee-qb:bookmarks:v1';
const THEME_KEY = 'jee-qb:theme:v1';

function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

/** Set of bookmarked question ids, persisted to localStorage. */
export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState(() => new Set(readJson(BOOKMARKS_KEY, [])));

  useEffect(() => {
    try {
      localStorage.setItem(BOOKMARKS_KEY, JSON.stringify([...bookmarks]));
    } catch {
      /* storage unavailable */
    }
  }, [bookmarks]);

  const toggle = useCallback((id) => {
    setBookmarks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const has = useCallback((id) => bookmarks.has(id), [bookmarks]);

  return { bookmarks, toggle, has };
}

/** 'light' | 'dark', persisted; toggles the `dark` class on <html>. */
export function useTheme() {
  const [theme, setTheme] = useState(() => {
    const saved = readJson(THEME_KEY, null);
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    try {
      localStorage.setItem(THEME_KEY, JSON.stringify(theme));
    } catch {
      /* ignore */
    }
  }, [theme]);

  const toggle = useCallback(
    () => setTheme((t) => (t === 'dark' ? 'light' : 'dark')),
    []
  );

  return { theme, toggle };
}
