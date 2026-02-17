---
layout: post
title: "Turning Eight Lectures into One Crib Sheet with Claude Code"
date: 2026-02-16
categories: [development, ai]
tags: [claude-code, automation, api, refactoring]
read_time: 4
word_count: 869
---

I had an exam coming up and a semester's worth of robotics material spread across eight lectures, three labs, and PDFs ranging from 60KB sketches to 6MB slide decks. So I did what any reasonable person would do: I handed it all to Claude Code and asked for a single printable crib sheet. A separate project got the same treatment — an 1,812-line monolithic MATLAB script broken into independently runnable modules. Both tasks share the same core problem: taking a large, messy input and decomposing it into something you can actually navigate.

The interesting part wasn't the output. It was how decomposition made the work tractable.

## Eleven Summaries in Parallel

The first step was reading every lecture and lab PDF — eleven files total — and producing structured markdown summaries. Each followed the same template: techniques used, key equations, and problem types. Lecture 1 covers robot fundamentals (joint types, DOF, workspace definitions). Lecture 7 covers the full Denavit-Hartenberg convention with frame assignment rules. Lab 2 is about repeatability and accuracy analysis on a UR5 arm.

Rather than processing them sequentially, I spawned parallel agents — Claude Code's Task tool can launch multiple sub-agents that work concurrently — with one batch handling lectures and another handling labs. Each agent read the relevant PDFs, extracted the structured content, and wrote a markdown file.

The parallel approach matters because each summary is completely independent. Lecture 3's rotation matrices don't depend on Lab 2's repeatability data. When your work decomposes into independent units, there's no reason to serialize it.

## From Topic Summaries to Exam Layout

Here's where the real design work happened. A crib sheet organized by lecture number is useless during an exam. You don't think "this is a Lecture 4 problem" — you think "I need the DH A-matrix formula."

The lectures teach DH parameters in Lecture 5 and revisit them in Lab 3's UR5 exercises; the crib sheet puts both in one block under "DH Convention." Rotation matrices appear in Lectures 2 and 3 with different notation; the crib sheet consolidates them into a single reference. Forward and inverse kinematics span three lectures and two labs — one crib sheet section, with the 2-DOF planar example and the law-of-cosines IK approach side by side. That regrouping — by concept rather than by source — is where the actual study value lives.

The implementation was a single HTML file with CSS for three-column landscape layout, 9-point sans-serif font, and `@page` margins set for printing. Equations went into monospace `<code>` blocks. Chrome's headless print-to-PDF converted it to a clean output file.

No LaTeX compilation chain. No Overleaf. HTML/CSS gives you precise column control and programmatic generation, which matters when the content is being assembled by an AI agent rather than typed by hand. You iterate by refreshing the browser, and the tooling cost is zero.

## The Other Half: Refactoring 1,800 Lines of MATLAB

The exam prep and the MATLAB refactor are different tasks, but they're the same shape: decompose a monolith into navigable parts. In one case the monolith was a semester of lecture PDFs. In the other, it was a single file called `optimal_foot_analysis.m`.

That script swept foot configurations, sizes, plate thicknesses, and materials to find the optimal setup for a mobile robot cart. Seven analysis sections, seven plot figures, eight local functions, one file. The problem wasn't length — it was coupling. To run just the ballast optimization, you had to execute all 1,812 lines and hope nothing in the plate bending section had changed a shared variable. Every analysis run was all-or-nothing.

The refactor broke it into independently runnable scripts with a shared `constants.m` file and a `functions/` directory for the extracted helpers. The key design decision: each script includes its prerequisite scripts at the top (`constants; foot_configurations; plate_bending_analysis;`), so you can run `ballast_optimization.m` directly without remembering the dependency chain. MATLAB scripts share a single workspace, so re-running `constants` just reassigns the same variables — no import overhead or module isolation to manage.

The resulting dependency structure is shallow enough that any script can be run standalone:

```
constants -> foot_configurations -> plate_bending_analysis -> parametric_sweep
                                                                  |
                                          +-----------------------+-----------------+
                                          |                       |                 |
                                   foot_deflection_report  material_shear   ballast_optimization
                                                                  |                 |
                                                           results_summary <--------+
                                                                  |
                                                            plot_results
```

A `run_all.m` master script executes everything in order for full reproducibility. The monolithic file gets deleted after verification.

## The Pattern Worth Keeping

Two lessons kept surfacing across both projects.

**Parallelize what's independent.** When your input decomposes cleanly — separate lectures, separate labs, separate analysis sections — let the pieces be processed concurrently. The summarization step ran in a fraction of the time because no agent needed to wait on another.

**Reorganize by use, not by source.** Lectures are organized by teaching order; a crib sheet should be organized by exam problem type. A monolithic script is organized by authoring history; a refactored codebase should be organized by execution dependency. The decomposition that matters is the one matching how the output gets *used*.

The crib sheet is done. The MATLAB refactor is done. Tomorrow the exam prep shifts from organizing to actually studying — which, unfortunately, no amount of parallel agents can do for me.