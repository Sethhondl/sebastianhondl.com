---
layout: post
title: "Twenty Inches of Cart and the Grep That Told the Truth"
date: 2026-03-26
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 6
word_count: 1324
---

The design review was supposed to take fifteen minutes. My team lead wanted to see where we stood on the robot cart's structural analysis — steel versus aluminum frame, ballast requirements, whether the thing would slide on a ramp at the specified load. I opened the MATLAB scripts, ready to walk through the numbers, and ran a quick `grep` for the cart length to make sure everything was consistent.

It wasn't. `grep "51"` lit up across half a dozen files like a fuse burning down a wire. The cart had been 51 inches for months. Three weeks ago, the specification changed to 71 inches. I'd updated two scripts and missed the rest. Every ballast calculation, every sliding analysis, every force diagram — half the codebase was still designing a cart that no longer existed.

I expected to be done by lunch. Instead, I spent the day rebuilding the analysis from the inside out.

## The Inconsistency That Was Hiding in Plain Sight

The `grep` results told a more specific story than just stale numbers. Some files used `cartLength = 51`, others `cart_length = 51`, and one used `L_cart = 51`. Three different variable names for the same physical dimension. When I'd updated the cart length in March, I searched for one naming convention and found two of the six files. The other four kept the old value, and because each script ran independently, nothing complained.

This is the quiet version of a bug. No error, no crash, no assertion failure. Just a ballast mass calculated for a cart twenty inches shorter than the one being built — which means less lever arm, less overturning moment, and a minimum-mass estimate that looks safe on paper but wouldn't hold the actual cart on a thirty-degree ramp.

The grep told me the truth: the code didn't have a single source for cart geometry. Every script defined its own reality.

## Before: The Literal That Answered Its Own Question

Here's what the ballast calculation looked like before the fix, representative of all six files:

```matlab
cart.mass = 690;         % steel frame mass [lb]
cart.length = 51;        % cart length [in]
ballast.mass = 200;      % just pick something
ballast.position = 25.5; % middle of cart, why not
```

The hardcoded values encoded the answer inside the question. Asking "what's the minimum ballast mass to prevent sliding?" is meaningless when the ballast mass is a constant typed on line four. The analysis script was structured as a parametric sweep, but every parameter it swept over was pinned to a literal. A for-loop walking through inclination angles, multiplying by numbers that couldn't change.

## The Fix: Six Lines That Earn the Word Parametric

The refactoring had two parts. First, a single geometry definition at the top of each analysis, referenced everywhere else. Second, the material properties and ballast scenarios rebuilt as data structures instead of literals:

```matlab
materials = struct('steel', struct('density', 490, 'E', 29e6), ...
                   'aluminum', struct('density', 169, 'E', 10e6));
for m = fieldnames(materials)'
    mat = materials.(m{1});
    cart.mass = compute_frame_mass(cart.length, cart.width, mat.density);
    [minBallast, ~] = find_min_ballast(cart, ramp, mat);
end
```

This loop only works because the hardcoded values are gone. `compute_frame_mass` takes geometry and density and returns a mass. `find_min_ballast` takes a cart struct and ramp conditions and returns the minimum ballast to prevent sliding. The material loop is the payoff for removing the literals — iterate over steel and aluminum with the same physics, same cart, same ramp, and let the numbers differ where the materials differ.

The refactoring itself wasn't clever. It was the kind of thing you'd do on day one of any parametric study: separate the data from the computation, name things once, reference them everywhere. The reason it happened on day forty instead is that the original scripts were written to answer one question — "does this specific 51-inch steel cart slide?" — and answered it correctly. Making them parametric wasn't necessary until the parameters changed.

## The Trick That Made the Sweep Work

The length-mass tradeoff script needed to find the minimum frame mass that prevents sliding at each cart length. The solver kept choking on the boundary case — zero ballast, minimum frame weight — because the friction model breaks down when normal force approaches zero.

The fix: `cart.mass = 0` at the start of each iteration. Zero out the frame mass, compute the gravitational and friction forces from ballast alone, then walk the frame mass upward until the net force crosses zero. Starting from zero instead of from the previous iteration's answer avoided carrying stale state across the sweep. Each length got a clean solve.

It's a small thing. But it's the kind of small thing that takes an hour to find when the solver returns answers that look plausible but drift systematically — because 52 inches of cart was starting from 51 inches' answer, and 53 from 52's, and the accumulated bias was invisible until the curve started bending wrong at the upper end.

## What the Tradeoff Curve Showed

Minimum mass scales roughly linearly with cart length up to about 70 inches, then steepens. The nonlinearity comes from the lever arm geometry — as the cart gets longer, the overturning moment grows faster than the restoring moment from frame weight, so each additional inch of length demands disproportionately more mass. At 71 inches, the team lead's design sits right at the knee of that curve. Five inches shorter would be significantly lighter. Five inches longer would need a substantially heavier frame or more ballast.

That's the kind of result a design review is supposed to produce. And it's the kind of result that was inaccessible when six scripts each defined the cart's dimensions independently.

## The February Decision That Made This Possible

Back in February, I'd separated the physics calculations from the scenario logic — pulling force computations, friction models, and geometry helpers into small, single-purpose functions. At the time it felt like over-engineering. The scripts worked. The functions were short. Nobody was asking for reusable components in a set of one-off MATLAB analyses.

That decision is the reason today's refactoring took an afternoon instead of a week. When I ripped out the hardcoded values, the functions didn't need to change. `compute_frame_mass` didn't care whether it was called once with a literal or sixty times inside a sweep. The February abstractions weren't premature — they were just early.

## Meanwhile, in the Pipeline

The blog pipeline ran without intervention this morning — the first clean automated run in over a week, after weeks of posts about its own failures. The meaningfulness gate caught two empty transcript clusters before they reached the expensive generation passes. No empty tool calls, no recursive self-description, no meta-commentary published as prose. A quiet success, the kind that's easy to overlook when the previous failures were so loud.

## The Distance Between Writing Parametric Code and Having It

The 51-to-71-inch change exposed something I already knew but hadn't felt. Parametric code isn't code that uses variables instead of literals. It's code where changing one number propagates correctly to every calculation that depends on it. I had variables. I had functions. I had a for-loop that iterated over inclination angles. What I didn't have was a single source of truth for the cart's geometry, and without that, the parametric machinery was decorative.

The six-line material loop at the center of the new analysis doesn't look like the important part. It looks like the easy part — a `for` over a struct, a function call, a result. The hard part was the afternoon spent making that loop possible: the `grep` that found the inconsistency, the variable renaming, the extraction of literals into data structures, the solver trick for the boundary case. The distance between writing a for-loop and having a for-loop that means something is an afternoon of refactoring that nobody will read about in the code.