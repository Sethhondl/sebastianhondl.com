---
layout: post
title: "The Arithmetic Isn't the Point: What I Actually Learned Using AI for Lab Reports"
date: 2025-10-25
categories: [development, ai]
tags: [claude-code, automation, testing, debugging]
read_time: 5
word_count: 1019
---

I had the data. I understood the theory. What I didn't have was two hours to transcribe frequency response measurements into a calculator.

The lab was for ME4231 at the University of Minnesota—system identification of a motor-driven rotational system. System identification is how engineers figure out the mathematical model of a physical system by poking it with inputs and watching what happens. It's the foundation of control system design: you can't build an autopilot or tune a robotic arm if you don't know how the system actually behaves. I had two folders of experimental data, a PDF full of post-lab questions, and the knowledge to answer all of them. Pure tedium stood between me and finishing.

That's when I realized this was exactly the kind of task where AI could help—not by thinking for me, but by removing the friction between knowing what to do and actually doing it.

## The Task

The lab involved characterizing a DC motor system both with and without an added mass. The "good" data folders contained frequency response measurements—amplitude ratios and phase angles at various input frequencies. The post-lab questions asked for things like:

- Deriving transfer functions from first principles
- Calculating moment of inertia and viscous damping coefficients
- Comparing theoretical predictions to experimental results
- Analyzing how adding mass changes the system dynamics

Standard controls coursework. Maybe 15-20 calculations total, plus the derivations and written analysis. Done manually, I'd estimate two hours minimum—most of it spent on arithmetic I already understood conceptually.

## What Actually Happened

I asked Claude to complete the post-lab as a markdown file with answers and work shown, using the data in the "good" folder. What came back was comprehensive, but more importantly, it shifted where I spent my time.

**Data parsing alone would have taken 30 minutes.** Claude read through the CSV files, extracted the relevant frequency response data, and organized it into tables. No transcription errors, no fumbling with spreadsheet imports.

**The derivations showed every step.** For each theoretical question, the response included the full mathematical path—starting from the equation of motion, applying Laplace transforms, arriving at the transfer function. I could verify the logic rather than reconstruct it from scratch.

**The calculations used actual numbers.** Not just formulas, but the experimental values plugged in with arithmetic shown:

```
From the Bode plot, ωc ≈ 15.2 rad/s
Given b = 0.0023 N·m·s/rad
J = b/ωc = 0.0023/15.2 = 1.51 × 10⁻⁴ kg·m²
```

About a dozen similar calculations appeared throughout the report—corner frequencies, damping ratios, inertia comparisons between the base system and the loaded system. Each one straightforward but time-consuming to do by hand.

**The comparison analysis connected the datasets.** When the lab asked how adding mass affected the system, the response compared the two cases side-by-side, noting the shift in corner frequency and what that implied about increased inertia.

## Where the Learning Actually Happened

Using AI for academic work doesn't replace understanding. When Claude produced the transfer function derivation, I still read through it and verified it made sense. When it calculated the damping coefficient, I checked that the units worked out.

But the time savings let me focus on the questions that actually matter for learning controls:

- Why did the experimental corner frequency differ from the theoretical prediction by 8%?
- What assumptions in our model might explain the discrepancy?

On that first question, I developed a hypothesis I wouldn't have had time to consider otherwise: the theoretical model assumes pure viscous damping, but real systems have some Coulomb (dry) friction that our linear model doesn't capture. At low frequencies, this shows up as a slight offset.

## Practical Advice for This Approach

**Structure your requests clearly.** "Complete this post-lab" is vague. "Complete this post-lab as a markdown file with answers and work shown, using the data in the 'good' folder" gives Claude enough context to produce something useful.

**Provide the source material.** Claude can read PDFs. If you have a lab manual, lecture notes, or reference documents, include them. Response quality improves dramatically when the AI has the same context you do.

**Verify everything—especially units.** AI can make calculation errors. That inertia calculation above? I double-checked it. The formula J = b/ωc gives units of (N·m·s/rad)/(rad/s). Since N = kg·m/s², this simplifies to kg·m²—correct for moment of inertia. A negative damping coefficient or an inertia value orders of magnitude off should raise immediate red flags.

**Know what the answer should look like.** Claude initially reported corner frequencies in Hz when the formulas expected rad/s. A factor of 2π error that would have cascaded through everything. I caught it because I knew roughly what the answer should be—not because I'm great at proofreading, but because I understood the physics.

## The Academic Integrity Question

There's an ongoing debate about AI in education—whether tools like Claude help students learn or just help them avoid learning. The counterargument has merit: struggling through calculations builds intuition you don't get otherwise. The first time you derive a transfer function, doing it by hand matters. The tenth time, you're not learning the concept anymore—you're just practicing algebra.

This was my sixth lab in this course. I'd done these derivations before. The learning wasn't in the mechanics; it was in interpreting the results and understanding why the model didn't perfectly match reality. That's where I spent my time, and I engaged with the material more deeply than I would have after two hours of exhausting arithmetic.

## Looking Ahead

This workflow has limits I'm still discovering. For open-ended analysis—"explain why X happened"—I'm better off doing the thinking myself. AI excels at structured tasks with clear right answers, less so at genuine interpretation. The next lab involves designing a controller based on these system parameters, which is more creative. I'm curious whether the same approach will work or whether I'll hit the wall where Claude's helpfulness ends and my own understanding has to take over.

The calculations verified what I already understood. Explaining why the model was wrong—that part was all me.