---
layout: post
title: "The Mohr's Circle That Lied: How Treating a Report Like a Test Suite Revealed Hidden Errors"
date: 2025-10-30
categories: [development, ai]
tags: [claude-code, automation, testing, api, debugging]
read_time: 5
word_count: 1147
---

Three hours into polishing my mechanical engineering report, Claude found something I'd have missed: the Mohr's circle visualization wasn't showing what we thought it was. The plot displayed static stress, but our fatigue analysis used stress amplitude and mean stress—related quantities, but not the same. Our documentation claimed we were analyzing blade passing frequency effects; the code only implemented wind direction changes.

This discovery came from an unexpected workflow: treating a grading rubric like a test suite. Evaluate the report against each criterion, generate improvements, implement them, regenerate the PDF, repeat until scoring above 95%. Continuous integration for technical writing.

## The Assignment

For our mechanical engineering modeling class, my group analyzed the structural fatigue life of a 3 MW wind turbine tower—calculating whether it would survive 20 years of cyclic loading from wind and gravity. The deliverable was a PDF report evaluated against a detailed rubric covering technical accuracy, presentation quality, and documentation standards.

I took on final polish, starting with our group-written draft, an HTML version with MATLAB-generated figures, and the rubric as a CSV file.

## Why HTML-to-PDF?

Our report existed as HTML because it made figure integration easier—MATLAB exported plots as images that dropped directly into the document. To generate the final PDF, I used headless Chrome, which preserved formatting exactly as it appeared in the browser. This mattered because the rubric specified page limits and figure sizing requirements.

The iteration loop became: generate PDF, have Claude evaluate it against the rubric, implement suggested changes to the HTML, regenerate, repeat.

## Formatting Details That Compound

Most of my time went into formatting refinements rather than content. Individually minor, together they transformed the report from student assignment to professionally polished.

Moving figure captions below figures—academic convention places them there, but our original HTML had them above. Adding a table of contents with accurate page numbers, which required accounting for the TOC page itself in the numbering. (Claude caught this: without that adjustment, every page reference would have been off by one.) Expanding figure sizes without breaking layout by reducing whitespace margins rather than changing dimensions.

## The Discovery That Made Me Revisit Our Analysis

While fixing formatting, I realized I didn't fully understand some of our own safety factor calculations. I asked Claude to explain the difference between two numbers in our results:

- **S-N curve safety factor (4.53):** Compares predicted cycles to failure against an infinite-life threshold
- **Goodman diagram safety factor (2.58):** Measures how far the current stress state is from the failure boundary

Both indicate safe operation, but they answer different questions. S-N asks "how many cycles until failure?" while Goodman asks "how close to the failure envelope are we?" Engineers typically check both because they catch different failure modes—S-N handles pure fatigue while Goodman explicitly accounts for mean tensile stress.

For a tower experiencing combined gravity loading and cyclic wind loads, the Goodman check matters more. That's why it showed a lower safety factor: it's the more conservative, more relevant analysis.

Understanding this made me more confident in our conclusions—and more suspicious of other parts of the analysis.

## When Documentation and Code Diverge

That suspicion paid off. When I mentioned that the Mohr's circle plot didn't seem to reflect reality throughout the rest of the code, Claude dug in and found several issues.

**Using static stress instead of fatigue stress.** The Mohr's circle plotted worst-case static stress, but our fatigue analysis used mean stress and stress amplitude. The visualization showed one thing; the calculations used another.

**Trivial visualization for simplified stress state.** Tower bending creates predominantly uniaxial stress—tension on one side, compression on the other, minimal shear. A Mohr's circle for this case degenerates to a point. Mathematically correct, but uninformative.

**Missing the dominant fatigue source.** This was the big one. Our documentation stated we were analyzing "blade passing frequency (3P) as primary cycle source." The code only implemented wind direction change cycles—roughly 48 per year.

Blade passing would contribute approximately 8 million cycles annually: 3 blades × 15 rpm × 60 minutes × 24 hours × 365 days. That's roughly 165,000 times more cycles than we actually modeled.

Our fatigue life predictions were based on the wrong loading assumption. The code was internally consistent, but it didn't match what we claimed to be analyzing.

## What It Felt Like to Find This

Discovering the discrepancy was unsettling. We'd written documentation, generated visualizations, calculated safety factors—the report *looked* complete. But the visualization was disconnected from our dynamic fatigue analysis. If we'd submitted without catching this, we'd have had a plot that technically showed *a* stress state, just not the one that mattered.

This is the kind of error that survives human review because everyone reads the documentation, sees the plot, and assumes they match. It took a fresh read—one that compared implementation against stated purpose—to notice the gap.

## The Iteration Numbers

Over about three hours, the rubric-driven loop ran roughly five full iterations. The first pass identified 12 improvements needed. By the third iteration, we were down to formatting polish. The final two iterations caught increasingly subtle issues: a missing reference, inconsistent decimal precision in a table.

By the end, feedback had shifted entirely from substantive technical concerns to minor presentation details.

## Where I Pushed Back Incorrectly

At one point, Claude suggested restructuring a paragraph for clarity. I disagreed, thinking the original flow was better. After seeing the alternative, I realized the original suggestion was right—my version buried the key point in a compound sentence. I reverted.

This is worth noting because it's tempting to present AI-assisted work as smooth collaboration. In practice, I occasionally rejected good suggestions because I didn't immediately understand why they were good.

## What Made This Work

**Rubrics as test cases.** Each criterion becomes a pass/fail check with concrete acceptance criteria.

**Cross-referencing documentation against implementation.** The blade passing frequency discrepancy showed that even well-documented code can drift from its stated behavior. Having Claude read both comments and code exposed gaps I'd normalized through familiarity.

**Asking for explanations, not just implementations.** Understanding *why* the Goodman safety factor was more conservative made me more confident defending our analysis.

## Outcome

The report hit 95%. The Mohr's circle issue got documented in our limitations section—we didn't have time to regenerate the plot correctly, but we acknowledged the discrepancy and explained why the fatigue analysis remained valid despite the misleading visualization.

My teammates reviewed the Claude-assisted changes and approved them. The collaboration worked because the content—analysis, assumptions, engineering judgment—stayed with the humans. The quality assurance process became automated.

And the blade passing frequency issue? That's now flagged for the next group that inherits this codebase. Sometimes catching an error is valuable even when you can't fix it in time. The documentation you leave behind becomes someone else's head start.