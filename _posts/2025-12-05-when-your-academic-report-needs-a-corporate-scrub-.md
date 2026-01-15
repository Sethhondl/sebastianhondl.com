---
layout: post
title: "When Your Academic Report Needs a Corporate Scrub: AI-Assisted Document Editing"
date: 2025-12-05
categories: [development, ai]
tags: [claude-code, testing, api, debugging, refactoring]
read_time: 2
word_count: 591
---

Three days before my ME 4053W deadline, I found myself staring at an HTML report about flywheel energy storage systems. The technical content was solid—months of research on rotational kinetic energy, material stress analysis, and efficiency calculations. But scattered throughout the document were references to "eXtreme Storage Inc.," a fictional company name that made sense during early drafts but now needed to disappear before submission.

This is exactly the kind of task where AI assistance earns its keep.

## The Flywheel Report Challenge

The report represented a semester's worth of work for my mechanical engineering design class, covering the physics of storing energy in rotating masses—how a spinning flywheel captures excess electricity and releases it on demand. The technical sections included stress calculations for rotor materials, bearing selection rationale, and efficiency projections under various load scenarios.

The "eXtreme Storage Inc." references had crept in during an earlier phase when the assignment suggested we write as if presenting to a company. That framing changed, but the corporate mentions remained embedded throughout the HTML document.

## Why AI Excels at Contextual Find-and-Replace

A simple find-and-replace would have caught the obvious instances, but HTML documents are tricky. The company name appeared in plain text paragraphs, HTML title tags, figure captions with specific formatting, headers at multiple levels, and metadata sections affecting how the document renders.

Each context required different handling. Removing a company name from "eXtreme Storage Inc. specifications indicate..." needs different treatment than removing it from a standalone header. The AI evaluated each instance in context, suggesting not just deletion but appropriate rewording to maintain sentence flow.

A phrase like "The eXtreme Storage Inc. engineering team recommends..." couldn't simply have the company name deleted—it needed restructuring to something like "Engineering best practices recommend..." Claude handled these transformations while preserving the technical meaning.

## The Editing Workflow

Working through the document section by section, I used Claude Code to identify instances and propose revisions. The process revealed patterns I might have missed manually: the company name appeared in slightly different forms ("eXtreme Storage," "eXtreme Storage Inc.," "eXtreme Storage, Inc.") that a basic search would have handled inconsistently.

The HTML structure added another layer of complexity. Some references sat inside `<span>` tags with specific styling. Others appeared in `<figcaption>` elements where the surrounding markup needed to remain intact. With AI assistance, I could focus on approving changes rather than carefully navigating tag boundaries myself.

## Lessons for Academic Document Preparation

This experience reinforced a few principles for technical writing:

**Placeholder names accumulate.** What starts as one fictional company reference multiplies as you copy section templates and reference earlier material. Establishing final naming conventions early saves cleanup time later.

**HTML reports require careful editing.** Unlike Word documents where formatting is somewhat abstracted, HTML files expose every tag. Manual editing risks accidentally deleting a closing `</div>` or breaking a CSS class reference.

**Context matters more than keywords.** The value wasn't just finding target strings—any text editor can do that. It was evaluating whether each removal required additional rewording to maintain readability.

## The Takeaway

The final report contained zero references to fictional corporate entities, with all sentences reading naturally and all HTML formatting intact. What could have been an error-prone afternoon became a systematic review where I maintained control over every change while offloading the pattern-matching work.

Sometimes the most valuable AI use cases aren't flashy code generation. Sometimes it's helping you clean up a report before the deadline—transforming tedious editing into something almost effortless.