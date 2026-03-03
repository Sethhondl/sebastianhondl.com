---
layout: post
title: "Three Cover Letters and the Same Resume"
date: 2026-03-01
categories: [development, ai]
tags: [claude-code, python, testing, api, debugging]
read_time: 4
word_count: 910
---

Three cover letters in one sitting, all built from the same resume. Freeform, Varda, Vast — three companies that build physical things, three different arguments for why the same person belongs there. The resume didn't change between applications. The letter did, completely, every time.

This follows directly from [last week's work on the resume itself](/2026/02/28/rewriting-a-resume-for-the-reader-who-wont-read-it.html) — the idea that formatting is argument, that the same facts tell different stories depending on what you put first and what you cut. A cover letter takes that principle further. The resume decides what facts to show. The letter decides what those facts *mean*.

## Freeform: Software as the Differentiator

Freeform is an AI-native manufacturing company. They use machine learning to control metal 3D printing in real time — monitoring the melt pool, adjusting laser parameters mid-build, catching defects before they propagate. The role was mechanical engineering, but the company's thesis is that software is the manufacturing differentiator.

So the letter led with software. PenguinCAM — the CNC toolpath visualization tool — showed that I build engineering software, not just use it. ShapeForge — the parametric CAD generator — showed that I think about the intersection of AI and physical geometry. Derivux — the symbolic math engine — showed comfort with the computational thinking that backs their real-time control systems.

The Veolia experience and the Anderson Labs research were still there, but as supporting evidence, not the lead. An applicant whose first paragraph is about plant operations reads as "mechanical engineer who codes." An applicant whose first paragraph is about PenguinCAM and ShapeForge reads as "software-minded engineer who understands manufacturing." Same person. Different opening sentence. Different thesis.

## Varda: Depth Over Breadth

Varda builds orbital manufacturing platforms — pharmaceutical crystallization in microgravity, autonomous re-entry capsules, the full pipeline from launch to landing. The role asked for someone comfortable with MATLAB, Simulink, and cross-disciplinary analysis. Not a software company that does hardware. A hardware company that needs engineers who move fluidly between domains.

The letter's argument shifted entirely. Instead of leading with software projects, it led with MATLAB/Simulink depth: the controls coursework, the six-bar linkage optimizer, the Stirling engine thermal model that required iterating between thermodynamic analysis and mechanism design. The FRC robotics experience — which barely appeared in the Freeform letter — became central, because it demonstrated exactly the cross-disciplinary flexibility Varda's posting described: mechanical design, electrical integration, and software all on the same team, all under deadline.

Anderson Labs got more weight here too. Research in a university lab, working with hardware that outlives its documentation, debugging equipment where the spec is [distributed across three source files](/2026/02/27/reading-someone-elses-code-to-build-a-hardware-che.html) — that maps directly to a startup where the team is small and the hardware is novel. The letter wasn't longer than the Freeform version. It just moved different facts to the front.

## Vast: Structural Analysis and Iteration

Vast is building a commercial space station. The role was structures — FEA, structural analysis, load paths, iterative design against mass and volume constraints. Pure mechanical engineering, no AI angle, no software differentiation.

This was the most constrained letter because the role was the most specific. The argument was simple: I do FEA, I understand structural analysis fundamentals, and I iterate. The coursework in machine design and stress analysis led. The ME4054W capstone project — the mobile robot platform with its deflection analysis, shear stress calculations, and [six tables of standards traceability](/2026/02/24/three-review-comments-and-an-appendix-from-scratch.html) — was the centerpiece. The FRC prototyping cycle, where you design a mechanism, build it, break it, and redesign it on a six-week timeline, demonstrated iteration under constraint.

ShapeForge and PenguinCAM didn't appear at all. They're irrelevant to a structures posting. Including them would have diluted the argument — the reader would see "software projects" and wonder if the applicant actually wants to do structural work or is hedging toward a software role. What I cut said as much as what I kept.

## The Third Letter Wrote Itself

The interesting part of writing three letters in one sitting is that the process becomes visible. The General Matter application I'd written earlier in the week was the prototype — the first time I'd mapped resume facts to a company-specific argument. By the time I sat down for these three, the process had a shape: read the posting, identify what the company values, find the resume facts that speak to those values, decide what goes first, cut everything else.

By the third letter, I wasn't thinking about how to write a cover letter. I was running a selection algorithm. Inputs: resume facts, company values. Output: ordered list of claims, each backed by one specific experience. The creative work was in the first letter. The rest were iterations on a pattern.

## Same Source, Different Projection

The resume is a fixed dataset — Veolia, Anderson Labs, FRC, coursework, projects. Every cover letter is a query against that dataset with different selection criteria and a different sort order. Freeform selects for software. Varda selects for cross-disciplinary depth. Vast selects for structural analysis. The facts don't change. The projection does.

This is the same observation from [the resume work, the a16z application, and the appendix tables](/2026/02/28/rewriting-a-resume-for-the-reader-who-wont-read-it.html): the source material is fixed, and the output depends entirely on who's reading and what they need to decide. Three cover letters are three projections of the same underlying data, each optimized for a reader who will spend sixty seconds deciding whether to keep reading.