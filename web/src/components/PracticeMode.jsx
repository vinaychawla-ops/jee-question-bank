import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Tex } from '../lib/tex';
import { SolutionView } from './SolutionView';
import { checkMcq, checkNumerical, imageUrl, isIncomplete, marksFor, subjectLabel } from '../lib/filters';

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function formatTime(totalSeconds) {
  const s = Math.max(0, totalSeconds);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`;
}

function isMcq(q) {
  return q.qtype === 'single_correct' || q.qtype === 'multi_correct' || q.qtype === 'matrix_match';
}

function isMulti(q) {
  return q.qtype === 'multi_correct';
}

function AnswerInput({ q, value, onChange }) {
  if (isMcq(q)) {
    const letters = Object.keys(q.options ?? {});
    if (isMulti(q)) {
      const selected = value ?? [];
      const toggleLetter = (L) =>
        onChange(selected.includes(L) ? selected.filter((x) => x !== L) : [...selected, L]);
      return (
        <div className="space-y-2" role="group" aria-label="Select all correct options">
          {letters.map((L) => (
            <label
              key={L}
              className={`flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2.5 transition ${
                selected.includes(L)
                  ? 'border-indigo-500 bg-indigo-50 dark:border-indigo-400 dark:bg-indigo-950/50'
                  : 'border-slate-200 dark:border-slate-700'
              }`}
            >
              <input
                type="checkbox"
                checked={selected.includes(L)}
                onChange={() => toggleLetter(L)}
                className="mt-1 h-4 w-4 accent-indigo-600"
              />
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                {L}
              </span>
              <span className="min-w-0 flex-1 text-[15px] text-slate-800 dark:text-slate-200">
                <Tex>{q.options[L]}</Tex>
                {q.option_images?.[L] && (
                  <img
                    src={imageUrl(q.option_images[L])}
                    alt={`Option ${L} figure`}
                    loading="lazy"
                    className="mt-2 max-h-64 w-full rounded-md border border-slate-200 bg-white object-contain p-1.5 dark:border-slate-700"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                )}
              </span>
            </label>
          ))}
          <p className="text-xs text-slate-400">Select all that apply.</p>
        </div>
      );
    }
    return (
      <div className="space-y-2" role="radiogroup" aria-label="Select the correct option">
        {letters.map((L) => (
          <label
            key={L}
            className={`flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2.5 transition ${
              value?.[0] === L
                ? 'border-indigo-500 bg-indigo-50 dark:border-indigo-400 dark:bg-indigo-950/50'
                : 'border-slate-200 dark:border-slate-700'
            }`}
          >
            <input
              type="radio"
              name={`mcq-${q.id}`}
              checked={value?.[0] === L}
              onChange={() => onChange([L])}
              className="mt-1 h-4 w-4 accent-indigo-600"
            />
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
              {L}
            </span>
            <span className="min-w-0 flex-1 text-[15px] text-slate-800 dark:text-slate-200">
              <Tex>{q.options[L]}</Tex>
              {q.option_images?.[L] && (
                <img
                  src={imageUrl(q.option_images[L])}
                  alt={`Option ${L} figure`}
                  loading="lazy"
                  className="mt-2 max-h-64 w-full rounded-md border border-slate-200 bg-white object-contain p-1.5 dark:border-slate-700"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              )}
            </span>
          </label>
        ))}
      </div>
    );
  }
  return (
    <div>
      <input
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        inputMode="decimal"
        placeholder="Enter numerical value"
        aria-label="Enter numerical value"
        className="w-full max-w-xs rounded-lg border border-slate-300 bg-white px-3 py-2.5 font-mono text-base text-slate-900 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
      />
      <p className="mt-1 text-xs text-slate-400">Round to two decimal places.</p>
    </div>
  );
}

function Setup({ questions, onStart, onExit }) {
  const max = questions.length;
  const [count, setCount] = useState(Math.min(10, max));
  const [minPerQ, setMinPerQ] = useState(2);
  const [subject, setSubject] = useState('');

  if (max === 0) {
    return (
      <div className="mx-auto max-w-xl rounded-xl border border-slate-200 bg-white p-6 text-center dark:border-slate-800 dark:bg-slate-900">
        <p className="text-slate-600 dark:text-slate-300">No questions available. Add data files first.</p>
        <button onClick={onExit} className="mt-4 text-sm font-medium text-indigo-600 dark:text-indigo-300">
          ← Back to bank
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 sm:p-6">
      <h2 className="text-lg font-bold text-slate-900 dark:text-white">Timed practice session</h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
        Answers stay hidden until you submit. JEE Main marking (+4 / −1) applies.
      </p>

      <div className="mt-5 space-y-4">
        <label className="block">
          <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Subject
          </span>
          <select
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          >
            <option value="">All subjects</option>
            <option value="physics">Physics</option>
            <option value="chemistry">Chemistry</option>
            <option value="mathematics">Maths</option>
          </select>
        </label>

        <label className="block">
          <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Questions: {count}
          </span>
          <input
            type="range"
            min={1}
            max={max}
            value={Math.min(count, max)}
            onChange={(e) => setCount(Number(e.target.value))}
            className="w-full accent-indigo-600"
          />
        </label>

        <div>
          <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Time per question
          </span>
          <div className="flex gap-2">
            {[1, 2, 3].map((m) => (
              <button
                key={m}
                onClick={() => setMinPerQ(m)}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition ${
                  minPerQ === m
                    ? 'border-indigo-600 bg-indigo-600 text-white'
                    : 'border-slate-300 text-slate-600 dark:border-slate-700 dark:text-slate-300'
                }`}
              >
                {m} min
              </button>
            ))}
          </div>
          <p className="mt-1 text-xs text-slate-400">Total time: {count * minPerQ} minutes</p>
        </div>

        <button
          onClick={() => onStart({ count, minPerQ, subject })}
          className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700"
        >
          Start session
        </button>
        <button
          onClick={onExit}
          className="w-full rounded-lg px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-700 dark:text-slate-400"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

function Session({ questions, totalSeconds, onSubmit, onExit }) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(totalSeconds);
  const [confirming, setConfirming] = useState(false);
  const submittedRef = useRef(false);

  const q = questions[index];
  const answeredCount = questions.filter((qq) => {
    const a = answers[qq.id];
    if (a == null) return false;
    if (typeof a === 'string') return a.trim() !== '';
    return a.length > 0;
  }).length;

  const doSubmit = () => {
    if (submittedRef.current) return;
    submittedRef.current = true;
    onSubmit(answers);
  };

  useEffect(() => {
    if (timeLeft <= 0) {
      doSubmit();
      return;
    }
    const t = setTimeout(() => setTimeLeft((s) => s - 1), 1000);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeLeft]);

  const setAnswer = (qid, val) => setAnswers((a) => ({ ...a, [qid]: val }));
  const urgent = timeLeft <= 60;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="sticky top-[57px] z-30 mb-3 flex items-center justify-between rounded-xl border border-slate-200 bg-white/95 px-3 py-2 backdrop-blur dark:border-slate-800 dark:bg-slate-900/95 sm:px-4">
        <span className="text-sm text-slate-500 dark:text-slate-400">
          Q {index + 1} / {questions.length} · {answeredCount} answered
        </span>
        <span
          className={`rounded-lg px-3 py-1 font-mono text-base font-bold ${
            urgent ? 'bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-300' : 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200'
          }`}
          role="timer"
          aria-label="Time remaining"
        >
          ⏱ {formatTime(timeLeft)}
        </span>
      </div>

      <div className="mb-3 flex flex-wrap gap-1.5" aria-label="Question palette">
        {questions.map((qq, i) => {
          const a = answers[qq.id];
          const answered = a != null && (typeof a === 'string' ? a.trim() !== '' : a.length > 0);
          return (
            <button
              key={qq.id}
              onClick={() => setIndex(i)}
              className={`flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold transition ${
                i === index
                  ? 'bg-indigo-600 text-white'
                  : answered
                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300'
                    : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
              }`}
              aria-label={`Go to question ${i + 1}${answered ? ' (answered)' : ''}`}
            >
              {i + 1}
            </button>
          );
        })}
      </div>

      <article className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 sm:p-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-indigo-600 dark:text-indigo-300">
          {subjectLabel(q.subject)} · Question {index + 1}
        </p>
        {isIncomplete(q) && (
          <p className="mb-3 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-800 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-200">
            ⚠ Figure / passage incomplete — answer with care.
          </p>
        )}
        {q.parent_stem && String(q.parent_stem).trim() && (
          <div className="mb-3 rounded-lg border border-indigo-200 bg-indigo-50/60 px-3 py-2.5 text-[15px] dark:border-indigo-900/60 dark:bg-indigo-950/30">
            <Tex>{q.parent_stem}</Tex>
          </div>
        )}
        <div className="text-[16px] leading-relaxed text-slate-900 dark:text-slate-100">
          <Tex>{q.stem}</Tex>
        </div>
        {(q.stem_images ?? []).filter(Boolean).length > 0 && (
          <div className="mt-3 space-y-2">
            {(q.stem_images ?? []).filter(Boolean).map((src) => (
              <img
                key={src}
                src={imageUrl(src)}
                alt={`Figure ${src}`}
                loading="lazy"
                className="max-h-96 w-full rounded-lg border border-slate-200 bg-white object-contain p-2 dark:border-slate-700"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
            ))}
          </div>
        )}
        <div className="mt-5">
          <AnswerInput q={q} value={answers[q.id]} onChange={(v) => setAnswer(q.id, v)} />
        </div>

        <div className="mt-6 flex items-center justify-between border-t border-slate-200 pt-4 dark:border-slate-800">
          <button
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
            disabled={index === 0}
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 disabled:opacity-40 dark:text-slate-300"
          >
            ← Previous
          </button>
          {index < questions.length - 1 ? (
            <button
              onClick={() => setIndex((i) => i + 1)}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white dark:bg-slate-100 dark:text-slate-900"
            >
              Next →
            </button>
          ) : (
            <button
              onClick={() => setConfirming(true)}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
            >
              Submit
            </button>
          )}
        </div>
      </article>

      <div className="mt-3 flex justify-between">
        <button onClick={onExit} className="text-sm font-medium text-slate-500 hover:text-slate-700 dark:text-slate-400">
          ✕ End session
        </button>
        {index < questions.length - 1 && (
          <button onClick={() => setConfirming(true)} className="text-sm font-medium text-emerald-600 dark:text-emerald-400">
            Submit answers
          </button>
        )}
      </div>

      {confirming && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal="true">
          <div className="w-full max-w-sm rounded-xl bg-white p-5 dark:bg-slate-900">
            <h3 className="font-bold text-slate-900 dark:text-white">Submit answers?</h3>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {answeredCount} of {questions.length} answered.
              {questions.length - answeredCount > 0 && ' Unanswered questions score 0.'}
            </p>
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => setConfirming(false)}
                className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium dark:border-slate-700 dark:text-slate-200"
              >
                Keep solving
              </button>
              <button
                onClick={doSubmit}
                className="flex-1 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-semibold text-white"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Results({ questions, answers, paperOf, onRetry, onExit }) {
  const [openId, setOpenId] = useState(null);

  const rows = useMemo(
    () =>
      questions.map((q) => {
        const raw = answers[q.id];
        const attempted = raw != null && (typeof raw === 'string' ? raw.trim() !== '' : raw.length > 0);
        let correct = false;
        if (attempted) {
          correct = isMcq(q) ? checkMcq(q, raw) : checkNumerical(q, raw).correct;
        }
        return { q, raw, attempted, correct, marks: marksFor(q, correct, attempted) };
      }),
    [questions, answers]
  );

  const total = rows.reduce((s, r) => s + r.marks, 0);
  const maxMarks = questions.reduce((s, q) => s + (q.marking?.correct ?? 0), 0);
  const correctN = rows.filter((r) => r.correct).length;
  const wrongN = rows.filter((r) => r.attempted && !r.correct).length;
  const skipN = rows.filter((r) => !r.attempted).length;

  const yourAnswerText = (r) => {
    if (!r.attempted) return '—';
    if (isMcq(r.q)) return [...r.raw].sort().join(', ');
    return String(r.raw).trim();
  };

  return (
    <div className="mx-auto max-w-3xl">
      <div className="rounded-xl border border-slate-200 bg-white p-5 text-center dark:border-slate-800 dark:bg-slate-900 sm:p-8">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Session complete</h2>
        <p className="mt-2 text-4xl font-extrabold text-indigo-600 dark:text-indigo-300">
          {total} <span className="text-lg font-medium text-slate-400">/ {maxMarks}</span>
        </p>
        <div className="mx-auto mt-4 grid max-w-md grid-cols-3 gap-2 text-sm">
          <div className="rounded-lg bg-emerald-50 p-2.5 dark:bg-emerald-950/50">
            <p className="text-xl font-bold text-emerald-600 dark:text-emerald-300">{correctN}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Correct</p>
          </div>
          <div className="rounded-lg bg-rose-50 p-2.5 dark:bg-rose-950/50">
            <p className="text-xl font-bold text-rose-600 dark:text-rose-300">{wrongN}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Wrong</p>
          </div>
          <div className="rounded-lg bg-slate-100 p-2.5 dark:bg-slate-800">
            <p className="text-xl font-bold text-slate-600 dark:text-slate-300">{skipN}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Skipped</p>
          </div>
        </div>
        <div className="mt-5 flex justify-center gap-2">
          <button
            onClick={onRetry}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
          >
            New session
          </button>
          <button
            onClick={onExit}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 dark:border-slate-700 dark:text-slate-300"
          >
            Back to bank
          </button>
        </div>
      </div>

      <h3 className="mb-2 mt-6 text-sm font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
        Review answers
      </h3>
      <div className="space-y-2.5">
        {rows.map((r, i) => (
          <div
            key={r.q.id}
            className="rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900 sm:p-4"
          >
            <button
              onClick={() => setOpenId(openId === r.q.id ? null : r.q.id)}
              className="flex w-full items-center justify-between gap-2 text-left"
              aria-expanded={openId === r.q.id}
            >
              <span className="min-w-0 flex-1">
                <span className="mr-2 text-xs font-bold text-slate-400">Q{i + 1}</span>
                <span className="line-clamp-1 text-sm text-slate-800 dark:text-slate-200">
                  <Tex>{r.q.stem}</Tex>
                </span>
              </span>
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-bold ${
                  r.correct
                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300'
                    : r.attempted
                      ? 'bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-300'
                      : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                }`}
              >
                {r.correct ? `+${r.marks}` : r.attempted ? `${r.marks}` : '0'}
              </span>
            </button>

            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm">
              <span className="text-slate-500 dark:text-slate-400">
                Your answer: <strong className="font-mono text-slate-800 dark:text-slate-200">{yourAnswerText(r)}</strong>
              </span>
              <span className="text-slate-500 dark:text-slate-400">
                Correct: <strong className="font-mono text-emerald-600 dark:text-emerald-300">{String(r.q.answer.value)}</strong>
              </span>
            </div>

            {openId === r.q.id && (
              <div className="mt-3 border-t border-slate-200 pt-3 dark:border-slate-800">
                <div className="mb-3 text-[15px] text-slate-800 dark:text-slate-200">
                  <Tex>{r.q.stem}</Tex>
                </div>
                <SolutionView q={r.q} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export function PracticeMode({ questions, onExit }) {
  const [phase, setPhase] = useState('setup');
  const [session, setSession] = useState(null);
  const [finalAnswers, setFinalAnswers] = useState(null);

  const start = ({ count, minPerQ, subject }) => {
    const pool = subject ? questions.filter((q) => q.subject === subject) : questions;
    const picked = shuffle(pool).slice(0, Math.min(count, pool.length));
    setSession({ questions: picked, totalSeconds: Math.min(count, pool.length) * minPerQ * 60 });
    setPhase('session');
  };

  if (phase === 'results') {
    return (
      <Results
        questions={session.questions}
        answers={finalAnswers}
        onRetry={() => {
          setPhase('setup');
          setSession(null);
          setFinalAnswers(null);
        }}
        onExit={onExit}
      />
    );
  }

  if (phase === 'session' && session) {
    return (
      <Session
        questions={session.questions}
        totalSeconds={session.totalSeconds}
        onExit={onExit}
        onSubmit={(answers) => {
          setFinalAnswers(answers);
          setPhase('results');
        }}
      />
    );
  }

  return <Setup questions={questions} onStart={start} onExit={onExit} />;
}
