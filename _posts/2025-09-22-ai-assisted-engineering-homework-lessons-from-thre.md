---
layout: post
title: "AI-Assisted Engineering Homework: Lessons from Three Courses in One Day"
date: 2025-09-22
categories: [development, ai]
tags: [claude-code, automation, testing, api, debugging]
read_time: 5
word_count: 1178
---

Three engineering courses. Three different failure modes. One day to get through all of them.

Today I bounced between Motion Control, Feedback Control Systems, and a Stirling Engine design project, each demanding a different kind of AI-assisted analysis. I also spent twenty minutes migrating some Claude Code configuration to my MacBook, but that was the least interesting part of the day.

## Feedback Control Systems: When Your AI Can't See the Picture

My controls homework hit a wall immediately. The assignment included block diagrams—those flowchart-like representations of feedback systems where boxes represent transfer functions and arrows show signal flow. Claude Code can read assignment PDFs, but interpreting spatial relationships in diagrams? That's where things get unreliable.

I've learned to head this off explicitly. My prompt included:

> "Understand that diagrams are very hard to read and interpret for you. Please ask clarifying questions about the diagram topology before attempting the problem."

This worked. Instead of confidently misreading the diagram, Claude asked: "Is the feedback path connected before or after the G2 block? And is H(s) in the forward path or the feedback path?"

I could answer by looking at the diagram: "The feedback path takes the output C(s), runs it through H(s), and subtracts it from the input R(s) before the first summing junction. G1 and G2 are in series in the forward path."

From that verbal description, Claude correctly derived the closed-loop transfer function. Telling the AI about its own limitations turned a potential hallucination into a productive conversation.

## Motion Control: The Plot That Looked Wrong

My RC circuit simulation plots looked suspicious. The voltage curves were oscillating when they should have been smooth exponential decays.

First, I had Claude read my MATLAB script. The Euler forward method implementation looked correct:

```matlab
v(i+1) = v(i) + dt * (1/tau) * (v_in - v(i));
```

Then I asked Claude to check the relationship between my time step `dt` and the circuit's time constant `tau`. That's when the issue became clear: I was using `dt = 0.1` seconds with `tau = 0.15` seconds. The ratio `dt/tau` was about 0.67—way too high.

The Euler forward method becomes unstable when the time step approaches the system's time constant. You need `dt` to be at least an order of magnitude smaller than `tau` for stable results. I changed `dt` to `0.01` and the oscillations disappeared.

The fix was trivial once diagnosed. The lesson: when your simulation produces unexpected oscillations, check your time step first.

## Stirling Engine: Where Layered Prompting Paid Off

The Stirling Engine project was the most extensive session, and it showed the clearest difference between good and bad prompting strategies.

A Stirling engine operates by cycling gas between hot and cold chambers—no combustion, just temperature differentials driving a piston. My project was designing the flywheel for a beta-type configuration. The flywheel needs to smooth out torque pulses into relatively constant rotational speed.

I started with the wrong approach. My first prompt was essentially: "Write a technical report on this Stirling engine flywheel design based on my code and results."

Claude produced a generic report full of placeholder text like "[insert calculated value]" and vague statements about "optimal performance characteristics." Useless.

The approach that worked was layering:

**First, I generated an outline.** I asked Claude to read `spec.md` (my reformulated assignment requirements) and `givenpar.csv` (the input parameters) and produce a report structure in markdown.

**Second, I asked for content section by section.** For each section, I explicitly pointed Claude to the relevant data file. "Read RESULTS_SUMMARY.md and write the Results section. Use the actual numbers, not placeholders."

**Third, I generated the final HTML separately.** Once the content was solid, I asked for print-optimized HTML with CSS that would render well as a PDF.

The final design met all specs: 3.8 kW power output (target: 3-5 kW), 37% thermal efficiency (target: 35-40%), coefficient of fluctuation of 0.04, and flywheel diameter of 1.8m (constraint: under 2m).

A single monolithic prompt produced garbage. Layered prompts with explicit file references produced a usable report.

## The Friction Points

Not everything went smoothly.

The Stirling Engine outline took three iterations. The first version organized sections by component (flywheel, crank, connecting rod) when the assignment wanted organization by analysis type (kinematics, dynamics, optimization). I had to explicitly say "reorganize around the assignment rubric structure, not the physical components."

In the controls homework, Claude initially tried to simplify a transfer function by canceling a pole-zero pair that wasn't actually present. I caught it because the algebra didn't match what I'd worked out by hand. When I pushed back—"show me where that (s+2) term comes from"—Claude acknowledged the error and recalculated correctly.

The Motion Control debugging took longer than it should have because I initially asked Claude to "check if the code is correct" rather than "check the relationship between dt and tau." Vague questions get vague answers.

## Why I Keep an AI Usage Log

One file that came up today: `ACADEMIC_AI_GUIDE.md`. It's my compliance document for UMN's AI appropriate use policy.

The file contains every prompt I give Claude for coursework, the responses (or summaries), notes on how I verified the output, and what I modified or rejected.

It sounds tedious, but it's useful beyond compliance. When a solution doesn't work, I can trace back through the conversation to see where the reasoning went wrong. It's also made me more intentional about my prompts—if I have to write it down, I think harder about what I'm asking.

For anyone at a university with AI disclosure requirements: build the habit now. It's easier to log as you go than to reconstruct later.

## What Actually Worked

Three courses, one day, three patterns:

**Explicit limitations beat implicit assumptions.** Telling Claude "you're bad at diagrams, ask me questions" produced better results than hoping it would figure things out correctly.

**Specificity compounds.** "Check the code" led nowhere. "Check dt against tau" found the bug. "Write a report" produced fluff. "Write the Results section using RESULTS_SUMMARY.md" produced content.

**Verification needs structure.** Having `spec.md` and `givenpar.csv` as explicit sources of truth made validation mechanical rather than vibes-based.

## Practical Takeaways

For technical coursework with AI assistance:

**Create a spec file, even for assignments that don't come with one.** Restructure the assignment as: Inputs, Outputs, Constraints, and Evaluation Criteria. This gives you a concrete artifact to validate against.

**Separate computation from presentation.** MATLAB scripts for numerical results, markdown for findings, HTML for the final document. Each layer can be checked independently.

**When asking for code review, specify the failure mode you're worried about.** "Check this for off-by-one errors" catches more bugs than "review this code."

**For numerical methods, sanity-check your step size against your system's characteristic times.** If your step is larger than your fastest dynamics, expect instability.

The Stirling Engine report is submitted. The controls homework is done. The Motion Control plots now look correct. Three courses down, and a clearer sense of when to tell the AI what it can't do—so it can actually help with what it can.