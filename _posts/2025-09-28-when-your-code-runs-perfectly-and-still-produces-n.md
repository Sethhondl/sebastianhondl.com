---
layout: post
title: "When Your Code Runs Perfectly and Still Produces Nonsense"
date: 2025-09-28
categories: [development, ai]
tags: [claude-code, python, testing, debugging, refactoring]
read_time: 3
word_count: 728
---

My code executed without errors. All the functions returned values. The plots rendered. And the results were completely wrong.

I spent three hours debugging a Stirling engine simulation in MATLAB, convinced I had a syntax error or an off-by-one bug lurking somewhere. The actual problem? My mental model of the physics was broken. The code did exactly what I told it to do—I just told it to do the wrong thing.

## The Setup

I'm working on a beta-type Stirling engine analysis for a mechanical engineering course. Stirling engines convert temperature differences into mechanical work through a closed cycle—no combustion, no exhaust, just pistons moving gas between hot and cold spaces. In a beta configuration, both the power piston and displacer share a single cylinder, which means their volumes are geometrically coupled.

My codebase had about 15 MATLAB files forming a pipeline: engine parameters → volume calculations → Schmidt thermodynamic analysis → power output → flywheel sizing. The goal was a valid P-V diagram showing the engine's thermodynamic cycle.

But instead of the rounded, roughly elliptical shape you expect from a Stirling cycle, mine produced a flattened figure that barely enclosed any area. Low enclosed area means low work output, which meant the optimizer was chasing its tail trying to find power that didn't exist.

## Right Syntax, Wrong Semantics

This distinction cost me three hours: my code was *syntactically* correct—it ran without errors and did exactly what I told it to do. But it was *semantically* wrong—the equations I implemented didn't match how a beta-type engine actually works.

The implementation was flawless. The specification was broken.

## Finding the Real Bug

The optimizer was faithfully finding the phase angle that maximized power output given the volume and pressure calculations it received. But since those upstream calculations were wrong, it was optimizing garbage—finding the best answer to the wrong question.

A classmate named Peyton had a working implementation, so I compared approaches. The difference was in how we calculated volumes:

```matlab
% The correct approach for beta-type geometry
powerPistonPos = calculatePistonPosition(crankAngle, params.powerCrankLength, params.powerRodLength);
displacerPos = calculatePistonPosition(crankAngle + params.phaseShift, params.displacerCrankLength, params.displacerRodLength);

% Cold volume is the GAP between displacer and power piston
coldVol.height = (displacerPos - powerPistonPos) - params.powerPinToPistonTop - (params.displacerHeight / 2);
coldVol.volume = params.cylinderCrossSectionalArea * coldVol.height;
```

The key insight: in a beta-type engine, the cold volume is the space *between* the displacer and power piston. My code treated these as independent volumes—as if I had an alpha-type engine with separate cylinders—when they're geometrically coupled in a shared cylinder.

## What AI Helped Me See

When I asked Claude to analyze why Peyton's code worked, it didn't just diff the files. It explained the physical meaning:

> "In your `calc_volumes.m`, you're computing `V_comp` based only on the power piston's position. But Peyton's version takes the difference between `displacerPos` and `powerPistonPos`. That subtraction is the physical gap in the cylinder. Your version gives the cold space a fixed displacement pattern; Peyton's captures how the displacer squeezes and expands that gap as both pistons move."

I could have stared at both implementations for hours and noticed the code differences. Having Claude explain *why* one approach matched the physics saved me from a lot of frustrated guessing.

## The Fix

The actual code change took ten minutes:

```matlab
% Hot side: the space above the displacer
hotVol.height = params.totalCylinderHeight - 0.5 * params.displacerHeight - displacerPos;
hotVol.volume = params.cylinderCrossSectionalArea * hotVol.height;
```

After the fix, the P-V diagram finally showed a proper elliptical shape with meaningful enclosed area. The optimizer found real results because it was optimizing against correct physics.

## Takeaways

**Verify your model before debugging your code.** When simulations produce wrong results, the bug might not be in your implementation. Step back and ask whether your mathematical model matches reality.

**Working reference implementations are gold.** Having Peyton's code let me compare behavior rather than just theory. When you're stuck, find something that works and study it.

**AI assistants excel at explaining the "why."** Claude didn't just find the different lines—it explained the physical reasoning that made one approach correct. That conceptual bridge is often what you need when syntax isn't the problem.

Sometimes the bug isn't in how you wrote the code. It's in how you understood the problem. No amount of refactoring will fix a broken mental model.