---
layout: post
title: "Three Review Comments and an Appendix from Scratch"
date: 2026-02-24
categories: [development, ai]
tags: [claude-code, git, automation, testing, api]
read_time: 5
word_count: 1034
---

---
layout: post
title: "Three Review Comments and an Appendix from Scratch"
date: 2026-02-24
categories: [development, ai]
tags: [claude-code, code-review, documentation, engineering]
read_time: 4
word_count: 870
---

A PR reviewer left three comments on my current-logging report. One asked me to make link text more descriptive. One said a section wasn't necessary. One said the raw CSV files didn't belong in the repository. Three different shapes of feedback — formatting, audience judgment, repository hygiene — each requiring a different kind of thinking despite all being "address review comments."

That turned out to be the pattern for the whole day: figuring out what belongs and what doesn't.

## Three Comments, Three Different Problems

The PR was on the bp1 repository: a report documenting AC voltage application and phase current logging on the AMDC platform. The reviewer, Mohammad Hassan, left three requested changes.

**Descriptive link titles.** The "Relevant Issues" section had bare links — `[Issue #20](url) - Applying AC voltages` and `[PR #25](url) - This implementation`. The reviewer wanted the titles pulled into the link text itself: `[Issue #20: Create a GitHub PR for AC phase voltages and logging phase currents](url)`. Pure formatting. The information was already there; it just needed to move from after the link to inside it.

**Remove the "Files Modified/Created" section.** This one required judgment. The section was a table mapping every modified file to a one-line description. I'd included it thinking it would help readers navigate the PR. The reviewer's take: not necessary. He was right — the information was redundant with the PR's own diff view, and listing filenames in the report body couples the document to the repository structure. If someone renames a file, the report has a stale table.

**Remove the CSV data files.** Two raw data files — `raw_60hz.csv` and `raw_500hz.csv` — were tracked in the repo, about 3,000 lines each. The Jupyter notebook that generated the plots could re-derive everything from them, but they were also reproducible from the hardware. For a research repository where reproducibility matters but storage discipline also matters, the reviewer's call was clear: the notebook is the artifact, the raw data is transient. `git rm`.

Three changes, one commit, one push. Then replies to each inline comment and a longer response to the reviewer's substantive feedback about Phase A calibration gains — a separate technical thread that connected back to the [sensor discrepancy](/2026/02/20/two-hardware-puzzles-and-six-documents-in-parallel/) I'd been debugging the previous week.

A fourth comment arrived thirty minutes later: the PNG plot images were over 300 KB each. Could I reduce them? A quick `sips` resize — 1800x1200 down to 1000x667, RGBA to RGB — brought one from 307 KB to 214 KB and the other from 344 KB to 296 KB. Second commit, second push, second reply with before-and-after sizes.

## Six Tables for an Appendix That Doesn't Exist Yet

The other half of the day was Appendix K of an ME4054W final report — the "Codes, Standards, and Safety" section for a mobile robot platform designed to carry a Fanuc CRX-30iA cobot. The course requires three things: discuss relevant standards and how they informed the design, describe standard tests used to evaluate it, and explicitly address how users could be harmed and what minimizes that risk.

The source material existed. Months of MATLAB analysis had already produced deflection results, shear stress calculations, ballast optimization, push force models, and stability checks — all documented across standalone files from a [parallel documentation sprint](/2026/02/20/two-hardware-puzzles-and-six-documents-in-parallel/) earlier in the month. The standards research was done. The safety analysis was done. What didn't exist was the *compressed version* — the appendix that synthesizes everything into something a course grader can scan in five minutes.

The decision that shaped the whole section was format. Extended narrative prose would have been the default, but an appendix about codes and standards is fundamentally a reference document. People don't read it linearly — they scan for their standard, check the traceability, and move on. So: tables. Six of them.

Table 1 listed eight applicable standards — ANSI/A3 R15.06, ISO 10218-1, ISO/TS 15066, and five others — with a column explaining why each applied. Table 2 listed three standards that *don't* apply, with a note about the NIST-recognized standards gap for manually-pushed carts with collaborative robots. Table 3 traced each standard to the specific design decision it informed — ISO 10218-2 §5.2.4 drove the cart rigidity requirements, OSHA ergonomic guidelines drove the caster selection. Table 4 mapped eight analysis methods to their criteria and results: deflection passing with 6–8x margin, push force passing with 2.1x margin on OSHA limits. Table 5 was a nine-row hazard analysis — tipping, sliding, collaborative robot contact, pinch/crush, ergonomic injury, electrical hazard, E-stop inaccessibility, unintended restart, loss of locking. Table 6 split responsibilities between our team and the integrator.

Each table required reading the full analysis, deciding what a non-specialist needs to see, and cutting everything else. The deflection analysis alone runs pages of methodology — foot compression, plate bending, tilt amplification across 45 parameter combinations. In the appendix, it becomes one row: method, standard, key result, pass/fail.

## The Hard Work Is Subtraction

The review comments and the appendix had more in common than I expected.

The reviewer told me to remove a section and two files. The section felt useful when I wrote it. The files felt like they belonged because they were inputs to the analysis. In both cases, someone with distance from the work saw what I couldn't: the information was either redundant or in the wrong place.

The appendix was the same problem at larger scale. Months of analysis compressed into six tables means most of the work doesn't appear. The parametric sweeps, the sensitivity studies, the 360-degree force sweep that justified the ballast placement — all of it supports the one-line result but doesn't belong in the result itself.

The instinct is always to include more. You did the work, so the work should be visible. But the reader doesn't need to see the work. They need to see what the work produced. A good review comment and a good appendix table share the same property: they contain exactly what's needed and nothing else.