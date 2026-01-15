---
layout: post
title: "When Your Control Systems Final Becomes a Multi-Day Journey with AI"
date: 2025-12-14
categories: [development, ai]
tags: [claude-code, testing, debugging]
read_time: 5
word_count: 1191
---

For non-engineers, here's what makes a controls final exam brutal: you're not just solving equations—you're designing a system that has to actually stabilize something unstable. It's the difference between calculating trajectory and actually landing the rocket.

That was my reality this week as I worked through my ME 5281 Final Exam—a chemostat control system design problem spanning three days of linearization, full state feedback, observer design, and classical control theory. The kind of exam where you're not just plugging numbers into formulas, but actually building something that has to work.

## The Problem: A Bioreactor That Won't Cooperate

The exam centered on controlling a chemostat—essentially a bioreactor where you're trying to maintain stable bacterial populations by controlling nutrient flow. The nonlinear dynamics look deceptively simple:

```
ṅ = u - k₁na
ȧ = αk₁na - k₂ab - k₃a  
ḃ = βk₂ab - k₄nb
```

Where:
- **n** = nutrient concentration
- **a** = concentration of bacteria species A
- **b** = concentration of bacteria species B
- **u** = nutrient flow rate (our control input)
- **k₁, k₂, k₃, k₄, α, β** = reaction rate constants

Three states, one input, one output. I expected this to follow the same pattern as our homework problems—derive the linearization, compute some gains, done in an evening.

Instead, the system had unstable equilibrium points that sent my simulations spiraling to infinity. The linearization involved partial derivatives with interacting terms that didn't simplify cleanly. And the Simulink implementation required carefully tracking what's a deviation variable versus an absolute value. What I thought would take four hours stretched across three days.

## Where Claude Code Actually Helped

I've been using Claude Code throughout this course, and this final pushed our collaboration to its limits. Here's what I learned about working with AI on complex engineering problems.

### The Insight That Matters Most: Tool Boundaries

Claude Code can't run MATLAB or Simulink. It can explain concepts, derive equations, and even write MATLAB code, but when it comes to actually connecting blocks and debugging why your integrator is blowing up, you're on your own.

I spent roughly six hours on what should have been straightforward Simulink work. The exam required screenshots of working simulations, and no amount of AI assistance could replace actually building and testing the model. This is the irreducible core of engineering education: some knowledge only comes from watching your simulation explode and figuring out why.

### The Good: Conceptual Clarity

When I was struggling to understand the feedback structure, Claude Code generated this ASCII diagram that finally made the signal flow click:

```
    setPoint (x_o) ─────────────────────────────────────────────┐
                                                                │
    ┌───────────────────────────────────────────────────────────┼───────────┐
    │                                                           ▼           │
    │   error ──────┐                                       ┌───────┐       │
    │               ▼                                       │  Σ    │       │
    │           ┌───────┐      ┌─────────┐      ┌──────┐    │ + + + │──► u  │
    │           │  Σ    │      │   1/s   │      │  Ki  │───▶│       │       │
    │           │ + -   │─────▶│Integrator────▶│ Gain │    └───────┘       │
    │           └───────┘      └─────────┘      └──────┘        ▲           │
    │               ▲                                           │           │
    │               │ y (output)                         u_o ───┘           │
    │               │                                           ▲           │
    │               │                              -K*(x-x_o) ──┘           │
    │               │                                   ▲                   │
    │               └───────────────────────────────────┼───────────────────┘
    │                                                   │                    
    └───────────────────────────────────────────────────┘                    
                    Full state feedback: x from observer or plant
```

Sometimes you just need someone to draw the picture differently. I'd been staring at the same block diagram in the lecture notes for hours, but seeing it redrawn with explicit signal labels made the `u = -K*(x - x_o) + Ki*xi + u_o` structure suddenly obvious.

My original misconception was that the integral term `Ki*xi` was somehow separate from the feedback loop—I'd been thinking of it as a feedforward term. The diagram made clear that the integrator is processing the *error* between setpoint and output, accumulating over time to eliminate steady-state error. That's when I finally understood why my first Simulink model wasn't tracking the reference: I'd wired the integrator to the wrong signal.

### The Unexpected Insight: Grading My Own Work

At one point, I asked Claude Code to review my submission and "give it a grade." This turned out to be surprisingly useful—not because the grade mattered, but because it forced me to explain my work clearly enough that someone else could evaluate it.

The review confirmed several things I'd done correctly:
- My A matrix had the expected structure (A[2,2]=0, A[3,3]=0 at equilibrium)
- The eigenvalues showed the expected unstable behavior: -0.83, 0.0643±1.5227j

That last point deserves explanation: a system is unstable when any eigenvalue has a positive real part. The complex pair 0.0643±1.5227j has a real part of +0.0643, which means perturbations from equilibrium will grow exponentially rather than decay. This is why the chemostat needs active control—without it, bacteria populations will oscillate with increasing amplitude until the system crashes.

But the review also caught concrete issues I'd missed:
- One of my transfer function derivations had a sign error in the numerator
- I'd stated a controllability result without showing the rank calculation
- My explanation of pole placement referenced equations that weren't in the document

I fixed all three before submitting.

## What I'd Do Differently

These insights aren't afterthoughts—they're hard-won lessons from watching things go wrong.

**Start with the end in mind.** On day one, I dove straight into the analytical work: linearization, eigenvalue calculation, gain derivation. By day two, when I finally opened Simulink, I discovered that my equilibrium point calculation had a subtle error that propagated through everything. If I'd built a simple simulation first—even just the open-loop nonlinear system—I would have caught this immediately by noticing the state trajectories didn't match my predictions.

**Use Claude Code for verification, not just generation.** My most valuable interactions weren't "solve this problem for me" but "here's my solution—does this make sense?" When I asked Claude Code to derive the A matrix independently, its result matched mine, which gave me confidence to move forward. When I asked it to check my observer gain calculation, it found the sign error I mentioned above.

**Accept the tool's limitations.** There were several moments where I tried to describe a Simulink error message to Claude Code, hoping for a diagnosis. The responses were reasonable guesses but ultimately unhelpful—the actual problem was always something about how I'd connected the blocks, which couldn't be diagnosed without seeing the model. I eventually learned to treat Simulink debugging as solo work.

## The Takeaway

If you're using AI tools for engineering coursework, here's my honest assessment: they're excellent for understanding concepts and catching algebraic errors, but they can't replace the hands-on experience of implementation.

The feedback controller equation `u = -K*(x - x_o) + Ki*xi + u_o` looks simple on paper. Understanding why each term exists, how they interact, and what happens when you wire them up wrong—that's where learning actually happens.

Claude Code helped me get there faster, but the final exam still required me to demonstrate that I actually understood it. Which, after this week, I think I finally do.

**Update:** Final grade: 94%. The points I lost were on the observer design section—specifically, I didn't adequately justify my pole placement choices. Another lesson for next time: the *why* matters as much as the *what*.