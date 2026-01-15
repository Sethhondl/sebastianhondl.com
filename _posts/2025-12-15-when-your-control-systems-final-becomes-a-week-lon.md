---
layout: post
title: "When Your Control Systems Final Becomes a Week-Long AI Collaboration"
date: 2025-12-15
categories: [development, ai]
tags: [claude-code, git, testing, api, debugging]
read_time: 4
word_count: 860
---

It's 11 PM the night before a 40%-of-your-grade take-home final is due, and you're watching an AI help you debug why your chemostat controller keeps predicting negative rotifer populations. Welcome to modern engineering education.

## The Problem: Controlling Instability

The exam centered on a predator-prey chemostat system—a continuous-culture bioreactor that maintains a constant chemical environment by continuously adding nutrients and removing waste. In this case, nutrients feed algae, algae feed rotifers, and you're trying to maintain stable rotifer populations. The mathematics involved three coupled nonlinear differential equations, state-space linearization, and multiple controller designs.

The challenge wasn't just understanding the theory. It was implementing it correctly in MATLAB and Simulink, then verifying everything worked on the nonlinear plant. One wrong sign in a Jacobian matrix and your "stable" controller sends the simulation into oscillatory divergence.

## The Collaboration Pattern That Emerged

My observer implementation kept producing physically impossible rotifer concentrations. Here's what we discovered:

```matlab
% The crucial insight: observer works in ERROR coordinates
% Observer receives: (u - u_o) and (y - b_o)
% Observer outputs: estimated ERROR states (deviation from equilibrium)
x_hat_0 = [0 - n_o; 1 - a_o; 1 - b_o_val];  % [-2.1818; -0.4026; 0]
```

The distinction between `x_hat` (the error estimate) and `x_hat + x_o` (the actual state) had caused hours of confusion. My initial implementation fed the observer raw plant outputs, but the math assumed error coordinates—deviations from equilibrium.

This pattern repeated throughout the week: I'd hit a wall with a crashing simulation or impossible results. Claude would systematically diagnose—checking matrix dimensions, sign conventions, coordinate systems. We'd discover something subtle, like the coordinate confusion above.

## The Pole Placement Trap

Here's a principle worth remembering: there's no benefit to placing poles faster than 5-6x your desired settling time.

Faster poles mean the controller must react more aggressively to errors, requiring larger gain values. Very high gains cause numerical instability in simulation, unrealistic control effort, and potential actuator saturation in real systems.

Claude found observer poles ranging from -0.1 to -5.0 being tested systematically in my code. The winning configuration ended up at [-0.9, -0.95, -1.0]—conservative enough for numerical stability, fast enough for reasonable settling time. When I pushed beyond that, gains exceeded 35,000 and the simulation became unreliable.

## The Classical Control Reality Check

Perhaps the most educational moment came with Problem 4: designing a classical transfer-function controller. The plant has a right-half-plane zero at s = +1.2.

An RHP zero acts like a fundamental speed limit imposed by physics—you can approach it, but you can't exceed it without crashing. Claude helped me understand why my "obvious" solution of adding an integrator for zero steady-state error was doomed. Any integrator path inevitably leads to instability with this plant structure.

This is the kind of insight that separates textbook knowledge from engineering intuition. Sometimes the answer to "how do I meet all specs?" is "you can't with this approach—and here's why."

## When I Pushed Back

The collaboration wasn't always smooth agreement. At one point, Claude suggested completely restructuring my Simulink model to separate the linear and nonlinear simulations into different files. I disagreed—maintaining two parallel models would double the chance of introducing inconsistencies, and my single-model approach with switchable plant blocks was already working.

Another time, Claude recommended more aggressive pole placement for faster settling time. I overruled that based on prior experience with numerical precision issues in MATLAB's ode45 solver. The conservative choice proved correct when the aggressive configuration produced high-frequency oscillations in the control signal.

These moments of disagreement were valuable. They forced me to articulate my reasoning and commit to engineering judgment calls that an AI couldn't make for me.

## Practical Takeaways

For anyone tackling control systems coursework with AI assistance:

1. **Be systematic about coordinate systems and signal flow.** Are you working in error coordinates or absolute? Describe your Simulink diagram verbally and verify the math matches the blocks. These checks catch 80% of implementation bugs.

2. **Ask for reviews against requirements.** AI excels at systematic checklist verification—use that capability.

3. **Document the "why."** The best parts of my submission were where Claude helped articulate *why* certain design choices were made, not just what values were used.

## The Outcome

Final score: 93/100. The 7 lost points came from overshoot slightly exceeding specs and the classical controller's inherent limitations from that RHP zero. Those deductions taught me something valuable: sometimes physical constraints trump controller design, and recognizing that boundary is part of engineering maturity.

*A note on academic integrity: ME 5281's take-home exam policy explicitly permits computational tools including AI assistants, with the requirement that students demonstrate understanding of the underlying concepts. All AI-assisted work was disclosed in my submission.*

I now understand why observer poles need to be faster than controller poles, why RHP zeros fundamentally limit classical control, and why your simulation crashing at t=0.3 usually means a sign error in your state-space matrices.

The AI never got tired of checking coordinate systems with me. But the engineering judgment—when to trust the math, when to question it, when to try a different approach entirely—that remained mine throughout.