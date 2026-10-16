# NTA / JEE official source reconnaissance

Recon date: 2026-10-16. Public sources only; no logins used, no files downloaded.
Correction to the original brief: the most recent JEE Main is **2026** (Sessions 1 & 2),
not 2025. JEE Advanced 2026 (IIT Roorkee) is newer still.

---

## 1. JEE Main 2026 — Paper 1 (B.E./B.Tech), via NTA

### Notices hub
- https://jeemain.nta.nic.in/public-notices/ — contains:
  - **"Final Answer Keys for JEE(Main) – 2026 [Session-II] (B.E. / B. Tech)"** (released ~20 Apr 2026)
  - **"JEE (Main) 2026 Session -1 and Session-2 for Paper-1 (B.E/ B. Tech)"** (question-paper archive)
  - **"Display of Provisional Answer Keys and Recorded Response Sheet for Answer Key Challenge ... Session 2 (April 2026)"** (provisional + challenge window, 11–13 Apr 2026)

### Sessions / shifts (Paper 1, B.E./B.Tech)
- **Session 2 (April 2026):** exam dates Apr 2, 4, 5, 6, 8 — 9 shifts:
  Apr 2 S1, Apr 2 S2, Apr 4 S1, Apr 4 S2, Apr 5 S1, Apr 5 S2, Apr 6 S1, Apr 6 S2, Apr 8 S2.
  (Apr 7 was Paper 2A/2B days; no Apr 8 Shift 1 paper listed.)
- **Session 1 (January 2026):** exam dates Jan 21, 22, 23, 24, 28 — 10 shifts
  (S1+S2 each day).
- Question papers were released publicly on 9 Apr 2026 (Session 2); **no login required**.

### Question-paper PDF — host and structure
- Papers are hosted on the S3 CDN backing jeemain.nta.nic.in (`cdnbbsr.s3waas.gov.in`),
  one PDF per shift. Verified live example (April 2, Shift 1):
  `https://cdnbbsr.s3waas.gov.in/s3f8e59f4b2fe7c5705bf878bbd494ccdf/uploads/2026/04/202604092096865379.pdf`
  (PDF header: "B Tech 2nd Apr 2026 Shift 1"). Aggregators (e.g. Jagran Josh, Careers360)
  link all 9 Session-2 shift PDFs directly to this CDN.
- Paper structure (from rendered PDF): 300 marks, 180 min. Per subject
  (Mathematics / Physics / Chemistry):
  - Section A: 20 × MCQ (single correct), 80 marks
  - Section B: 5 × SA (numeric entry), 20 marks
  - Total: 75 questions.
- Each question row carries machine-parseable metadata: **Question Number, Question Id,
  Question Type (MCQ/SA), and Option Ids** (MCQ). E.g. Q1 Question Id 6911211 with
  Option Ids 6911211–6911214; numeric questions have "Response Type: Numeric".

### Final answer-key format (Main)
- Per-shift tables mapping **Question ID → Correct Option ID** (for MCQ;
  the Option ID is the NTA internal ID of the correct option, e.g. 6911213)
  or **correct numeric value** (for SA questions).
- Format independently corroborated by NTA's own challenge-interface wording
  (as quoted by Shiksha): the interface lists "Question IDs in sequential order"
  with a "Correct Option" column holding the NTA key, plus the four Option IDs.
- **Dropped questions** are published as Question IDs per shift. Confirmed case:
  Session 2, **Apr 4 Shift 1 — 2 Physics questions dropped**, +4 bonus marks each to all
  candidates in that shift. Dropped Question IDs:
  - 695278261 (centres in India)
  - 6952781086 (centres outside India)
  (India vs outside-India variants have different question-ID spaces — note for Phase 2.)

### Barriers
- Provisional answer key + recorded response sheets were behind candidate login
  (application number + password/DOB) during the 11–13 Apr 2026 challenge window.
- **Final answer-key PDF is public — no login.**
- Individual recorded response sheets remain login-gated (not needed for our build;
  official keys suffice).
- One combined key PDF covers all shifts (per-shift tables inside); papers are
  per-shift PDFs.

---

## 2. JEE Advanced 2026 — IIT Roorkee, via jeeadv.ac.in

- Exam: **17 May 2026** (Paper 1: 09:00–12:00; Paper 2: 14:30–17:30). Organizing IIT: Roorkee.
- Announcements page: https://jeeadv.ac.in/

### Official question papers (public, no login; posted 17 May 2026)
- Paper 1 (English): https://jeeadv.ac.in/documents/p1_english.pdf
- Paper 2 (English): https://jeeadv.ac.in/documents/p2_english.pdf
- (Hindi versions linked in the same announcement block.)

### Official FINAL answer keys (public, no login; posted 1 Jun 2026)
- Final Key Paper 1: https://jeeadv.ac.in/documents/p1_solutions_final.pdf
- Final Key Paper 2: https://jeeadv.ac.in/documents/p2_solutions_final.pdf
- (Provisional keys were posted 25 May 2026 with a 25–26 May feedback window;
  final keys reflect post-challenge corrections.)

### Key format (Advanced) — confirmed by reading both key PDFs
The `*_solutions_final.pdf` files are the **full paper with inline answers**:
- Single-correct: `Answer Q1: D`
- Multi-correct: `Answer Q5: AC`
- Numerical value: `Answer Q9: [2520]`; tolerance ranges where applicable, e.g.
  `Answer Q12: [3.9 TO 4.1]`
- Matrix-match: `Answer Q13: C` (letter of the correct option)
- Mapping is **1:1 by displayed question number (Q1, Q2, ...)** — no ID join needed.
  This is the simplest verification target of all sources found.

### Paper 2 section structure (2026)
- Section 1: 4 × single-correct (12 marks)
- Section 2: 5 × multi-correct, partial marking (20 marks)
- Section 3: 5 × numerical value (20 marks)
- Section 4: 2 question stems × 2 numerical-value questions each (8 marks)
- Sections repeat across Physics, Chemistry, Mathematics.

### Barriers
- Candidate response sheets are login-gated (candidate portal at
  cportal.jeeadv.ac.in). Not needed: papers + final keys are fully public.
- No dropped-question handling needed for the 2026 final keys (all questions have
  answers in the final PDFs).

---

## 3. Recommended pilot paper for Phase 1

**JEE Advanced 2026 — Paper 2** (17 May 2026)
- Question paper: https://jeeadv.ac.in/documents/p2_english.pdf
- Final answer key: https://jeeadv.ac.in/documents/p2_solutions_final.pdf

Rationale:
1. **Most recent paper with both artifacts** (newer than any Main 2026 shift).
2. **All four JEE question types in one paper** — single-correct, multi-correct,
   numerical-value, and stem-based — best schema coverage for the Phase 1
   pipeline (extraction, LaTeX normalization, taxonomy tagging).
3. **Simplest verification loop**: the key maps by question number (`Answer Qn: …`),
   so blind-solve → compare needs no Question-ID/Option-ID join (unlike NTA Main).
4. Clean finals: no dropped questions in the 2026 Advanced keys.
5. Both files are on the official domain, no login, stable URLs.

Alternatives:
- **JEE Advanced 2026 Paper 1** — equally clean; pair it with Paper 2 for a natural
  two-paper extension.
- **JEE Main 2026 Session 2, April 8 Shift 2** (paper on cdnbbsr.s3waas.gov.in;
  key in the NTA Session-II final-key PDF) — the most recent *Main* shift;
  75 questions (MCQ + numerical only); verification requires the
  Question-ID → Correct-Option-ID join.
- **JEE Main 2026 Session 2, April 4 Shift 1** — if Phase 1 wants to exercise the
  dropped-question/bonus-marks edge case (2 Physics Qs dropped, +4 bonus each).

## 4. Phase-2 ingestion notes
- Main papers/keys: pattern `cdnbbsr.s3waas.gov.in/.../uploads/<YYYY>/<MM>/<file>.pdf`;
  19 Paper-1 shifts for 2026 (10 Jan + 9 Apr). Watch for India vs outside-India
  question-ID variants.
- Advanced: annual `/documents/p{1,2}_english.pdf` + `/documents/p{1,2}_solutions_final.pdf`
  on the year's jeeadv.ac.in (organizing IIT changes yearly; archive pages live on
  each year's site).
- Never needed: candidate logins, response sheets, challenge portals.
