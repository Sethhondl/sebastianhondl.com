---
layout: post
title: "When Your Academic Report Needs a Corporate Scrub"
date: 2025-12-04
categories: [development, ai]
tags: [claude-code, python, git, testing, api]
read_time: 4
word_count: 873
---

A 17-page engineering report on flywheel energy storage sat finished—thermal analysis complete, magnetic bearing controllers modeled, efficiency calculations verified. One problem remained: every section addressed "eXtreme Storage Inc.," a fictional client our instructor had decided wasn't adding pedagogical value anymore. The technical content was solid. The corporate framing had to go without leaving scars.

## The Fictional Client That Overstayed Its Welcome

Our course originally required framing engineering analyses as consulting deliverables—professional engineers write for clients, not professors. So we created eXtreme Storage Inc. and wrote our flywheel report as a feasibility study for them.

Mid-semester, the instructor revised the guidelines. The new direction: focus on demonstrating engineering competency without the roleplay layer. Reports should read as technical analyses, not business proposals. Our 17-page HTML document needed surgery.

## Why Find-and-Replace Wouldn't Cut It

The client references weren't isolated strings. They were load-bearing parts of sentences.

**Simple deletion that required restructuring:**

*Before:*
```html
<p>This report presents our findings to eXtreme Storage Inc. regarding 
the feasibility of the proposed flywheel energy storage system.</p>
```

*After:*
```html
<p>This report presents a feasibility analysis of the proposed flywheel 
energy storage system.</p>
```

The phrase "to eXtreme Storage Inc." couldn't just disappear—"presents our findings regarding" is awkward without a recipient. The sentence needed reshaping.

**Recommendation reframed as assessment:**

*Before:*
```html
<p>Based on our comprehensive analysis, we recommend that XS Company 
proceed with developing the proposed flywheel design as a commercial 
product.</p>
```

*After:*
```html
<p>Based on our comprehensive analysis, the proposed flywheel design 
demonstrates viability for commercial development.</p>
```

Same conclusion, different rhetorical stance—shifting from a recommendation *to a client* to a statement of *design viability*.

**Full paragraph rewrite:**

*Before:*
```html
<p>eXtreme Storage Inc. approached our team seeking an independent 
evaluation of their flywheel concept. XS Company's management expressed 
particular concern about thermal management at high charge states...</p>
```

*After:*
```html
<p>This analysis evaluates a flywheel energy storage concept with 
particular attention to thermal management at high charge states and 
magnetic bearing control system feasibility.</p>
```

The fictional backstory was pure narrative scaffolding. Removing it meant reconceiving the paragraph's purpose: not "why we're writing this" but "what this covers."

## What Stayed Untouched

The report covered substantial technical ground: baseline design analysis with component losses, design space exploration for power and efficiency tradeoffs, active magnetic bearing disturbance response, dynamic stiffness calculations, and rotor runout analysis.

None of this needed modification. The client references lived entirely in the framing—introduction, transitions, conclusions—while the engineering remained intact. This validated our document structure: we'd kept technical content modular rather than interweaving it with narrative elements. The separation made targeted edits possible without risking the analysis itself.

## Where AI Assistance Earned Its Keep

I'll be specific about what Claude Code contributed, because "AI helped me edit" is too vague to be useful.

**Catching references I missed.** After my first pass, I thought I'd found everything. Claude identified three additional instances buried in transition sentences—phrases like "as requested by the client" that I'd read past multiple times.

**Suggesting natural rephrasing.** When I removed "for eXtreme Storage Inc." from a sentence, I initially replaced it with nothing, leaving "We conducted this analysis" hanging. Claude suggested "We conducted this analysis to evaluate commercial viability"—adding purpose back where the client reference had provided it.

**Maintaining voice consistency.** Across 17 pages, it's easy to solve the same problem differently in different sections. Claude flagged inconsistencies like "the analysis demonstrates" versus "this evaluation shows" and helped standardize the phrasing.

**What I still did manually:** Every suggested change went through my judgment. Some of Claude's rephrasing was technically correct but didn't match how engineers write. "Demonstrates viability" sounds right in an engineering report; "proves its worth" sounds like marketing copy. I was the filter.

## Verifying the Surgery

After edits across 17 pages, I needed confidence nothing was broken:

1. **Diff review:** Compared original and edited HTML files side by side, confirming every change was intentional.

2. **Full read-through:** Read the entire document start to finish, checking that transitions still made sense.

3. **PDF generation:** Ran the document through our headless Chrome pipeline to verify formatting survived.

4. **Search verification:** Searched for "XS," "eXtreme," "client," and "company" to catch stragglers. Two "client" references were legitimate technical uses in footnotes, which I verified in context.

## Lessons for Next Time

Starting a report with fictional framing you might remove later is structural debt. If I were beginning this project again:

**Separate framing from analysis in the document structure.** Keep client-specific language isolated to clearly marked sections rather than threading it through technical paragraphs.

**Question whether the framing adds value early.** Our team accepted the fictional client premise without asking whether it strengthened our argument. It didn't—it just added words.

**Use version control on the document itself.** We had our source in Git, which made the diff review possible. For teams using Word or Google Docs, this kind of tracking is harder but worth the effort.

The underlying engineering work was sound. The report is now tighter—focused on demonstrating competency rather than performing a client relationship that never existed. Sometimes the most useful work isn't building something new but recognizing when existing structure has outgrown its purpose and cutting it clean.