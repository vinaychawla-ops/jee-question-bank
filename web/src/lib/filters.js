/** Filter helpers shared by the bank list and practice-mode setup. */

export const SUBJECTS = [
  { value: 'physics', label: 'Physics' },
  { value: 'chemistry', label: 'Chemistry' },
  { value: 'mathematics', label: 'Maths' },
];

export const DIFFICULTIES = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

/** Broad UI grouping: the filter bar offers MCQ vs Numerical. */
export const TYPE_GROUPS = [
  { value: 'mcq', label: 'MCQ' },
  { value: 'numerical', label: 'Numerical' },
];

const MCQ_TYPES = new Set(['single_correct', 'multi_correct', 'matrix_match']);
const NUMERICAL_TYPES = new Set(['numerical', 'stem_numerical']);

export function typeGroup(q) {
  if (MCQ_TYPES.has(q.qtype)) return 'mcq';
  if (NUMERICAL_TYPES.has(q.qtype)) return 'numerical';
  return 'mcq';
}

export function typeGroupLabel(q) {
  return typeGroup(q) === 'mcq' ? 'MCQ' : 'Numerical';
}

export function subjectLabel(value) {
  return SUBJECTS.find((s) => s.value === value)?.label ?? value;
}

export function difficultyLabel(value) {
  return DIFFICULTIES.find((d) => d.value === value)?.label ?? value;
}

export function emptyFilters() {
  return { exam: '', year: '', subject: '', chapter: '', difficulty: '', typeGroup: '', bookmarkedOnly: false, search: '' };
}

/** All distinct chapter names across the loaded questions, sorted. */
export function allChapters(questions) {
  const set = new Set();
  for (const q of questions) for (const c of q.taxonomy?.chapters ?? []) set.add(c);
  return [...set].sort((a, b) => a.localeCompare(b));
}

/** All distinct exam names across the loaded questions, in a stable order. */
export function allExams(questions) {
  const set = new Set();
  for (const q of questions) if (q.exam) set.add(q.exam);
  const preferred = ['JEE Main', 'JEE Advanced'];
  return [...set].sort((a, b) => {
    const ia = preferred.indexOf(a);
    const ib = preferred.indexOf(b);
    if (ia !== -1 || ib !== -1) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    return a.localeCompare(b);
  });
}

/** All distinct years across the loaded questions, newest first. */
export function allYears(questions) {
  const set = new Set();
  for (const q of questions) if (q.year != null) set.add(String(q.year));
  return [...set].sort((a, b) => Number(b) - Number(a));
}

export function applyFilters(questions, filters, bookmarkedIds) {
  const needle = filters.search.trim().toLowerCase();
  return questions.filter((q) => {
    if (filters.exam && q.exam !== filters.exam) return false;
    if (filters.year && String(q.year) !== String(filters.year)) return false;
    if (filters.subject && q.subject !== filters.subject) return false;
    if (filters.difficulty && q.taxonomy?.difficulty !== filters.difficulty) return false;
    if (filters.typeGroup && typeGroup(q) !== filters.typeGroup) return false;
    if (filters.chapter && !(q.taxonomy?.chapters ?? []).includes(filters.chapter)) return false;
    if (filters.bookmarkedOnly && !bookmarkedIds?.has(q.id)) return false;
    if (needle) {
      const hay = `${q.stem} ${(q.taxonomy?.chapters ?? []).join(' ')} ${q.id}`.toLowerCase();
      if (!hay.includes(needle)) return false;
    }
    return true;
  });
}

/** Numerical answer check honoring the record's tolerance (default 0.01). */
export function checkNumerical(q, rawInput) {
  const given = Number(String(rawInput).trim());
  if (!Number.isFinite(given)) return { valid: false, correct: false };
  const expected = Number(q.answer.value);
  const tol = q.answer.tolerance ?? 0.01;
  return { valid: true, correct: Math.abs(given - expected) <= tol + 1e-12 };
}

/** MCQ answer check. Multi-correct expects the sorted letter set. */
export function checkMcq(q, selected) {
  const key = String(q.answer.value).toUpperCase().replace(/[^A-D]/g, '');
  if (q.qtype === 'single_correct' || q.qtype === 'matrix_match') {
    return selected.length === 1 && selected[0] === key;
  }
  const got = [...selected].sort().join('');
  return got.length > 0 && got === key;
}

/** Marks earned for one answered question under its marking scheme. */
export function marksFor(q, correct, attempted) {
  if (!attempted) return 0;
  if (correct) return q.marking?.correct ?? 0;
  return q.marking?.wrong ?? 0;
}

export function paperTitle(paper) {
  const bits = [paper.exam, paper.year];
  if (paper.paper) bits.push(paper.paper);
  if (paper.session) bits.push(paper.session);
  if (paper.shift) bits.push(paper.shift);
  return bits.join(' · ');
}
