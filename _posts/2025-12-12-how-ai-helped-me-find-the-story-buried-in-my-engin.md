---
layout: post
title: "How AI Helped Me Find the Story Buried in My Engineering Final"
date: 2025-12-12
categories: [development, ai]
tags: [claude-code, python, automation, testing, debugging]
read_time: 5
word_count: 1055
---

Fifty thousand characters of Python. Four folders labeled v0 through v4. A LaTeX document that needs to become a 30-page journal paper by Friday. Somewhere in this mess is my Advanced Mechanisms final—a six-bar linkage mechanism, the kind you'd find in car suspensions or aircraft landing gear, designed to guide a point along a precise path. The synthesis works. The code runs. Now I just need to explain four months of iteration to people who weren't there for any of it.

This is where Claude Code surprised me. Not by writing my paper, but by helping me figure out what the paper even needed to be.

## Surveying the Wreckage

My project deliverables were scattered everywhere: the main synthesis script, multiple design iterations, progress reports from different stages, a half-written LaTeX file. I started by asking Claude to read through everything and tell me what I was looking at.

The prompt was simple: "Read through these files and summarize what's here. I need to write a final paper and I'm not sure where to start."

What came back was more useful than I expected. Claude didn't just list files—it identified relationships between them. The v0 folder contained an early approach that hit a dead end (my initial precision point selection created impossible constraint equations). The v2 folder showed where I'd switched strategies. The v4 design succeeded because I'd changed how I parameterized the dyad linkage lengths.

I'd lived through all these decisions, but I hadn't articulated them as a coherent narrative. Having an outside reader point out the structure helped me see the story I needed to tell.

## The Guidelines I'd Been Skimming

I'd read the assignment requirements before—multiple times. But I'd been reading them as a checklist, not as a structure. When I asked Claude to compare the specific requirements against my existing draft, the gaps became obvious.

One guideline stated: "Do not list generic or unrelated equations. Develop only the new equations required for your work."

My draft had two pages of standard kinematic equations copied from the textbook. That wasn't what they wanted. They wanted the specific constraint equations I'd derived for my six-bar configuration—the ones that came from my choice of precision points and the geometric relationships in my particular design.

Another requirement I'd glossed over: "Figures are discussed before they appear, not after." My draft had figures floating at the end of sections with captions like "Figure 3: Final mechanism design." No interpretation, no discussion of what the reader should notice.

I could have caught these issues by reading more carefully. But having Claude flag them against my actual draft—showing me "here's the requirement, here's what you wrote, here's the mismatch"—made revision concrete instead of abstract.

## Finding the Real Narrative

My first attempt at using Claude for this failed. I dumped all the files and asked for a paper outline. The result was generic: introduction, literature review, methodology, results, conclusion. Useless.

The breakthrough came from a more specific prompt: "Based on the design iterations in v0-v4 and the final synthesis code, what's the actual story of how this design evolved? What decisions did I make and why?"

That's when Claude started identifying what actually mattered. In v0, I'd chosen five precision points distributed evenly along my target curve. The synthesis equations were solvable, but the resulting link lengths were impractical—one link would have needed to be three meters long for a mechanism meant to fit on a desktop. In v2, I'd reselected precision points clustered near the critical region of the path, which produced feasible dimensions but introduced path deviation errors elsewhere. The v4 solution involved a compromise: fewer precision points with tighter tolerance, accepting small deviations in non-critical regions.

That progression—from theoretical correctness to practical feasibility—was the story my paper needed to tell. I knew it implicitly, but I hadn't framed it as the central thread.

## What the AI Actually Did

I want to be specific here because "AI-assisted writing" can mean many things, most of them less useful than they sound.

Claude didn't write my paper. The technical content—the equations, the design parameters, the analysis—came from my actual work. What Claude did was help me organize four months of scattered artifacts into a structure that made sense.

Specifically:
- Surveying 12+ sessions of previous work and identifying which decisions mattered for the narrative
- Cross-referencing my draft against assignment guidelines to find structural gaps
- Articulating the v0→v4 progression in a way I could use as a paper outline

The "12+ sessions" came from transcript files of earlier coding sessions where I'd debugged the synthesis script, tested parameter variations, and documented intermediate results. Having that history available meant Claude could reference decisions I'd made months ago that I'd half-forgotten.

## What I Learned

**Organization beats generation.** Asking an AI to write your paper produces generic text. Asking it to survey your existing work and identify structure produces something you can actually use.

**Specificity matters.** "Write me an outline" gave useless results. "What's the story of how this design evolved based on these files" gave the narrative thread I needed.

**Use AI to check against requirements.** I'd read the guidelines multiple times but still missed structural issues. Cross-referencing my draft against specific requirements caught problems I'd skimmed past.

**Version your iterations intentionally.** Folders v0-v4 weren't just backups. They were documentation of my design process. When I needed to explain why my final solution worked, the earlier failures provided the context.

## The Work That Remains

I should be clear: this session was about organization, not completion. My LaTeX file now has a solid outline and I know what each section needs to contain. The actual prose, equations, and figures still need to come from me.

But that's exactly the point. The hardest part of finishing a large project isn't usually the final work—it's seeing through the accumulated chaos to find the structure that makes sense. For a semester-long engineering project with multiple iterations and scattered documentation, that organizational problem is exactly where AI assistance proved useful.

If you're facing your own final project writeup, start by surveying everything you have, not planning everything you need to write. The story is usually already there in your artifacts. Sometimes you just need help seeing it.