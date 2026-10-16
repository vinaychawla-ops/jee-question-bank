import React from 'react';
import { Tex } from '../lib/tex';

/** Full step-by-step solution: concepts, formulas, steps, pitfalls, final check. */
export function SolutionView({ q }) {
  const sol = q.solution ?? {};
  return (
    <div className="space-y-4">
      {sol.dispute_note && (
        <section className="rounded-lg border border-red-300 bg-red-50 p-3 dark:border-red-800 dark:bg-red-950/50">
          <h4 className="mb-1 text-xs font-bold uppercase tracking-wide text-red-700 dark:text-red-300">
            ⚠ Our answer differs from the official key
          </h4>
          <p className="text-sm leading-relaxed text-red-800 dark:text-red-100">
            <Tex>{sol.dispute_note}</Tex>
          </p>
        </section>
      )}

      {sol.concepts?.length > 0 && (
        <section>
          <h4 className="mb-1.5 text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Concepts tested
          </h4>
          <ul className="flex flex-wrap gap-1.5">
            {sol.concepts.map((c) => (
              <li
                key={c}
                className="rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-200"
              >
                {c}
              </li>
            ))}
          </ul>
        </section>
      )}

      {sol.formulas?.length > 0 && (
        <section>
          <h4 className="mb-1.5 text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Key formulas
          </h4>
          <ul className="space-y-1.5">
            {sol.formulas.map((f, i) => (
              <li
                key={i}
                className="rounded-lg bg-slate-50 px-3 py-2 text-sm dark:bg-slate-800/70"
              >
                <Tex>{f}</Tex>
              </li>
            ))}
          </ul>
        </section>
      )}

      {sol.steps?.length > 0 && (
        <section>
          <h4 className="mb-1.5 text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Step-by-step solution
          </h4>
          <ol className="space-y-2.5">
            {sol.steps.map((s) => (
              <li key={s.n} className="flex gap-2.5">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
                  {s.n}
                </span>
                <div className="min-w-0 flex-1 pt-0.5 text-[15px] leading-relaxed text-slate-800 dark:text-slate-200">
                  <Tex>{s.text}</Tex>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}

      {sol.pitfalls?.length > 0 && (
        <section className="rounded-lg border border-amber-200 bg-amber-50 p-3 dark:border-amber-900/60 dark:bg-amber-950/40">
          <h4 className="mb-1.5 text-xs font-bold uppercase tracking-wide text-amber-700 dark:text-amber-300">
            ⚠ Common pitfalls
          </h4>
          <ul className="list-disc space-y-1 pl-5 text-sm text-amber-900 dark:text-amber-100">
            {sol.pitfalls.map((p, i) => (
              <li key={i}>
                <Tex>{p}</Tex>
              </li>
            ))}
          </ul>
        </section>
      )}

      {sol.final_check && (
        <section className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 dark:border-emerald-900/60 dark:bg-emerald-950/40">
          <h4 className="mb-1 text-xs font-bold uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
            ✓ Final check
          </h4>
          <p className="text-sm text-emerald-900 dark:text-emerald-100">
            <Tex>{sol.final_check}</Tex>
          </p>
        </section>
      )}
    </div>
  );
}
