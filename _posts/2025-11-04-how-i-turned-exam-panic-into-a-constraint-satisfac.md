---
layout: post
title: "How I Turned Exam Panic into a Constraint Satisfaction Problem"
date: 2025-11-04
categories: [development, ai]
tags: [claude-code, python, automation, testing]
read_time: 4
word_count: 996
---

Eighteen hours until my mechanical engineering exam. One semester of MATLAB scripts, lecture notes, and project reports spread across my desk. The constraint: compress everything from external flows to fatigue strength analysis onto a single sheet of paper.

The traditional approach—manually copying equations while squinting at subscripts—felt like the wrong tool for the job. So I asked Claude Code to help.

## Twenty Topics, One Page

The exam covered a sprawling list of concepts: angle of attack and relative velocity, coefficient of drag and lift calculations, power and torque from distributed forces, numerical integration methods, beam bending and stress analysis, wind turbine aerodynamics. The Betz limit alone has enough subscripts to fill half a page.

This is fundamentally a constraint satisfaction problem. Maximize information density. Maintain readability. Fit on one page. Keep font size above "needs a magnifying glass." These constraints compete with each other, and balancing them manually is tedious.

Claude, it turns out, is good at holding multiple constraints in mind simultaneously.

## Extracting Equations from My Own Work

Rather than copying from textbooks, I pointed Claude at the project files I'd actually used during the semester—MATLAB scripts from a wind turbine analysis, stress calculation spreadsheets, lab reports. The AI extracted equations I'd already worked with, which meant they were equations I had some intuition about.

Here's what it pulled for the aerodynamics section:

```
### Relative Velocity (V_rel)
V_rel = √[(V_∞(1-a))² + (ωr(1+a'))²]

Where:
- V_∞ = freestream wind speed [m/s]
- a = axial induction factor [-]
- ω = angular velocity [rad/s]
- r = radial position [m]
- a' = tangential induction factor [-]
```

The organization wasn't alphabetical—it was pedagogical. Force coefficients appeared near the equations that used them. Integration methods sat adjacent to where they'd be applied. Claude had inferred the logical groupings from context.

## When Preparation Becomes Learning

The most valuable moments came when I questioned what Claude generated. Take this Reynolds-dependent drag coefficient formula it extracted:

```
Re < 2×10⁵:
  Cd = 11×Re^(-0.75) + 0.9×(1 - exp(-1000/Re)) + 1.2×(1 - exp(-(Re/4500)^0.7))
```

I stopped. "Why are there three separate terms here? What's each one modeling?"

Claude explained: the first term dominates at very low Reynolds numbers where viscous effects control drag. The second captures the wake formation regime. The third handles the transition region approaching the critical Reynolds number where the boundary layer becomes turbulent.

"So the 'drag crisis'—where drag suddenly drops on spheres—happens because..."

"Because turbulent boundary layers stay attached longer. The wake narrows. Golf balls have dimples specifically to trigger this transition at lower speeds."

That exchange taught me more than re-reading my notes would have. The AI became a tutor who happened to also be a typesetter.

## Why HTML Instead of Word

You might wonder why I bothered with an HTML-to-PDF pipeline for a cheat sheet. Here's what goes wrong with Word or Google Docs: you spend twenty minutes adjusting margins, the equations render inconsistently, and when you add one more line, everything reflows unpredictably. You're fighting the tool instead of focusing on content.

HTML with CSS gives sub-millimeter control. What renders on screen matches what prints. When Claude adjusts the layout, I can verify immediately that everything still fits. No surprises at the exam.

## The Iteration That Almost Broke It

Not everything worked smoothly. Claude's first pass extracted equations from my MATLAB comments, but some of those comments were wrong—earlier attempts I'd corrected in the actual code but never updated in the documentation. The cheat sheet briefly contained a torque formula with the radius squared instead of cubed.

I caught it because the units didn't balance. When I pointed this out, Claude re-scanned the functional code (not just comments) and corrected the extraction. This became a useful habit: always check units, even on AI-generated content. *Especially* on AI-generated content.

## The Final Sheet

The output was dense but navigable. Six sections covered fluid dynamics fundamentals, distributed forces, wind turbine theory, numerical methods, stress analysis, and unit conversions. Each used a consistent format: equation first, variable definitions below, one-line usage note where helpful. The font was 8pt—small but legible.

Every formula was something I'd actually used during the semester, which meant I had at least one concrete memory of applying it.

## Constraint Satisfaction Everywhere

What struck me afterward was how similar this process felt to another project I'd been working on: optimizing a six-bar linkage mechanism using genetic algorithms. That problem also involves satisfying multiple competing constraints—find ground pivot locations where a door mechanism stays entirely inside a boundary when closed while tracing a specific path when open.

"Make this fit on one page" really means "minimize whitespace while maintaining readability while including all required topics while keeping font size legible." That's multi-objective optimization. Whether the output is a PDF or a set of coordinates, the process rhymes.

## What Worked, What I'd Change

**What worked:**
- Extracting equations from my own coursework meant I recognized every formula
- Questioning the generated content turned preparation into active review
- The HTML pipeline eliminated formatting frustration
- Treating the cheat sheet as a constraint problem clarified what "good" meant

**What I'd change:**
- Verify equations against functional code immediately, not just comments
- Start earlier—the tutoring conversations were valuable, but I rushed the last hour
- Include more worked examples; equations alone don't jog memory as well as seeing them applied

## The Exam

I sat down with my single-sided page, dense with the semester's content. More importantly, I'd spent the preparation process explaining to Claude what I needed and why—which meant I'd spent it engaging with the concepts themselves.

When I hit a problem on distributed forces over a curved surface, I didn't just look up the formula. I remembered the conversation about why the integral bounds mattered, and that memory carried the context I needed.

The cheat sheet was useful. The process of making it was better.