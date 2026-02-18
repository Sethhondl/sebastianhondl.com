---
layout: post
title: "Daily Development Log - February 18, 2026"
date: 2026-02-17
categories: [development, ai]
tags: [claude-code, python, automation, testing, debugging]
read_time: 3
word_count: 795
---

The refactor plan for a 1,812-line MATLAB monolith looked like a mechanical extraction. Break the file into pieces, move the pieces into folders, wire them together. An afternoon of reading, diagramming dependencies, and deciding on file boundaries produced something thorough. Then execution surfaced every assumption the plan had glossed over — and that gap between planning and implementing is where most refactoring effort actually hides.

## The Plan Looked Clean

Break `optimal_foot_analysis.m` into ten independently runnable scripts. Extract eight helper functions into a `functions/` directory. Wire them together with a `run_all.m` master script. Delete the original after verification. Each script got a specification: which lines it came from, what variables it needed, what it produced, and which prerequisite scripts to call at the top.

The script models structural analysis for foot plate configurations on a mobile robot cart. The dependency graph was neat:

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

Read lines 9–132, paste into `constants.m`. Read lines 134–177, paste into `foot_configurations.m`. Repeat. What could go wrong?

## Three Problems the Plan Missed

**The first was a tooling constraint.** The original script exceeded Claude Code's context window for a single read operation. A plan that says "extract lines 611–893 into `ballast_optimization.m`" doesn't mention that you need three read passes just to see those lines in context. A human refactorer wouldn't hit this wall — they'd open the file in an editor and scroll — but the constraint shaped the execution regardless.

**The second was subtler.** In MATLAB, scripts share a single flat variable workspace. No block scoping, no module isolation. Every variable assigned anywhere is visible everywhere below it. The plan accounted for this: each modular script re-runs its prerequisites to populate the workspace. But the plan didn't catch implicit dependencies — places where a variable defined in section 3 was quietly used in section 6 without appearing in section 6's specification. These only surface when you run the extracted script standalone and MATLAB throws an "undefined variable" error that never existed when everything ran top-to-bottom.

**The third was structural.** The plan specified extracting eight local functions into standalone `.m` files. In the original script, those local functions could reference variables from the script's workspace without declaring them as parameters — MATLAB's nested function semantics handle the access implicitly. Once extracted into separate files, that implicit access disappears. Every variable that was silently inherited now needs to be an explicit parameter. The function signatures in the plan matched the originals, but the originals were incomplete — they relied on workspace leakage that only exists inside a single-file context.

## Why This Matters Beyond MATLAB

The pattern isn't language-specific. Any refactor that moves code from a shared-scope environment into isolated units hits the same class of problems. Consider a 2,000-line Python file with dozens of module-level globals: extracting a function into its own module works fine until you discover it was reading `config` and `db_connection` from module scope without ever declaring them as parameters. The plan says "move `calculate_totals()` to `billing.py`." Execution reveals that `calculate_totals` silently depends on `TAX_RATE`, `DISCOUNT_TIERS`, and `current_user` — none of which appear in its signature.

The plan identifies the *intended* data flow. Execution reveals the *actual* data flow, including every shortcut and implicit coupling the original author never documented.

This is where AI-assisted refactoring earns its keep — not in the extraction itself, which is mechanical, but in the iteration cycle when things break. Each "undefined variable" error is a micro-discovery about a dependency the plan missed. With Claude Code, the cycle becomes: run the script, read the error, trace the variable back to its origin in the monolith, add it as a parameter or prerequisite, run again. Each cycle takes seconds instead of minutes. Without that assist, each cycle means manually searching 1,812 lines for where `plate_span_x` first gets assigned.

## The Takeaway

Planning a refactor is necessary. It sets the file structure, identifies the dependency graph, and gives you a verification checklist. But the plan's value isn't in being right — it's in being a specific, falsifiable hypothesis that execution can test. Every "undefined variable" error, every workspace-leakage surprise, every implicit parameter discovery is the plan colliding with reality.

The 1,812-line monolith is now ten scripts and eight functions. The plan said that would take one session. It took two. The extra session was almost entirely the function signature problem — tracing which variables each extracted helper actually needed versus what the original signatures declared, then updating call sites across the new modular scripts to pass the missing arguments.

That's the work no plan predicts: not the extraction, but the full accounting of what a monolith's flat workspace has been hiding all along.