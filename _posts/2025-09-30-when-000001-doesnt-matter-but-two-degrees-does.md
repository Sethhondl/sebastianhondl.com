---
layout: post
title: "When 0.00001 Doesn't Matter (But Two Degrees Does)"
date: 2025-09-30
categories: [development, ai]
tags: [claude-code, git, automation, testing, api]
read_time: 4
word_count: 859
---

I spent an hour debugging code that was working exactly as designed. The culprit? A difference of 0.00001 on a target of 0.003. The lesson wasn't about numerical precision—it was about forgetting my own acceptance criteria.

## The Session: Stirling Engine Analysis

I've been working on a beta-type Stirling engine simulation for my mechanical engineering modeling class. These engines work by cyclically heating and cooling gas between two pistons—a displacer that shuttles gas between hot and cold regions, and a power piston that extracts work. A flywheel smooths out the power pulses into continuous rotation.

My goal: design a flywheel that keeps speed fluctuation at exactly 0.003. The coefficient of fluctuation (Cs) measures how much flywheel speed varies per revolution. Too high and the engine runs rough; too low and you've over-engineered a needlessly massive flywheel.

Simple enough. Except my simulation kept returning 0.00301.

## The Investigation

That 0.00001 difference sent me down a rabbit hole. I asked Claude to help investigate, and it methodically traced how Cs was being calculated:

```matlab
omega_max = max(omega);
omega_min = min(omega);
omega_mean = mean(omega);
Cs_actual = (omega_max - omega_min) / omega_mean;
```

The flywheel inertia is sized analytically to achieve the target Cs, but the actual value comes from numerically integrating the equations of motion. Every timestep introduces small truncation errors. Every interpolation of the pressure-volume data adds noise.

Was my numerical integration scheme too coarse? A bug in the angular velocity computation? Should I switch from ode45 to a stiffer solver?

Claude walked through each possibility. We checked solver tolerances, verified torque calculations, examined the energy balance.

Then Claude pointed me to code I'd written weeks ago:

```matlab
if Cs_actual > params.flywheelCoefficientOfFluctuation * 1.01
    warning('Actual Cs (%.4f) exceeds target (%.4f)', ...
            Cs_actual, params.flywheelCoefficientOfFluctuation);
end
```

I had already decided that 1% tolerance was acceptable. On a 0.003 target, that means anything up to 0.00303 passes. My 0.00301 was well within spec.

Past me had already solved this problem. Present me had forgotten the solution existed.

## The Real Bug: Two Implementations, Different Answers

The more substantive issue emerged when I noticed my "clean code" implementation gave different phase angle optimization results than an earlier version in `StirlingCycle.m`. Same engine parameters, but optimal phase angle differed by nearly two degrees.

For a Stirling engine, phase angle determines how the displacer and power piston motions relate. The optimal angle maximizes work output. Two degrees might not sound significant, but it can mean 5-10% difference in power—enough to affect my design project grade.

I asked Claude to compare the two files and generate an HTML report showing the differences. This is where AI assistance earns its keep: when two implementations of the same physics diverge, it can rapidly isolate where calculations start differing, saving hours of manual code review.

The culprit was cylinder geometry:

```matlab
% Both versions used the same volume formula:
hotVol.height = params.totalCylinderHeight - 0.5 * params.displacerHeight - displacerPos;

% But totalCylinderHeight came from different sources:

% Version 1: Derived from compression ratio and displacement
totalCylinderHeight = Vmax / cylinderArea;

% Version 2: Hard-coded from earlier hand calculations  
totalCylinderHeight = 0.085; % meters
```

Same physics equations, different entry points into the calculation chain. The hard-coded version used a value I'd computed once for a specific compression ratio. When I later changed the compression ratio in my parameter file, the derived version updated automatically—the hard-coded version didn't.

This wasn't numerical precision or solver tolerances. It was a configuration management error: two sources of truth for the same parameter.

To validate the fix, I compared both versions against the analytical expression for ideal Stirling cycle work. The derived version matched within 2%—reasonable given idealized assumptions. The hard-coded version was off by 15%.

I deleted the hard-coded value and added a comment explaining the derivation.

## What I Took Away

**Define "correct" before debugging.** My 0.00301 wasn't a bug—it was within tolerance. But I'd forgotten I'd set that tolerance. Document acceptance criteria where you'll actually see them.

**When physics implementations diverge, let AI narrow the search space.** The issue wasn't floating-point error or numerical instability—it was a stale hard-coded value. Claude found it in minutes; manual inspection would have taken hours.

**Derive, don't duplicate.** Computing `totalCylinderHeight` from compression ratio means one place to update when parameters change. Hard-coding creates silent inconsistency.

**Always have a validation reference.** I couldn't determine which implementation was correct without comparing to the analytical solution. Engineering simulations need benchmarks—analytical, experimental, or published.

## The Pattern

Engineering simulations rarely produce perfect numbers. The skill is knowing which imperfections matter.

Today I chased 0.00001 on a problem I'd already solved, then found a two-degree error that would have cost me points. The first investigation reminded me to check my own tolerance specs before assuming something is broken. The second caught a real bug hiding in plain sight.

Claude Code made both faster—not by providing answers, but by systematically narrowing possibilities until the answers became obvious.

Know your acceptance criteria. Derive parameters from single sources of truth. And when two versions of "the same code" disagree, find out why before trusting either one.