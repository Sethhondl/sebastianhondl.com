---
layout: post
title: "From PDFs to Polished Code: When Your Engineering Project Gets Real Data"
date: 2025-10-19
categories: [development, ai]
tags: [claude-code, testing, api, debugging, refactoring]
read_time: 5
word_count: 1116
---

The BEM solver had been predicting 2.3 MW peak output based on textbook assumptions. With real blade profiles loaded, it jumped to 2.47 MW—within 1% of the Clipper C96's rated 2.5 MW capacity.

That's the moment a prototype becomes a tool.

## The Setup: A BEM Solver Waiting for Real Numbers

I've been working on a Blade Element Momentum solver for analyzing the University of Minnesota's 2.5 MW Clipper Liberty C96 wind turbine. BEM solvers predict wind turbine performance by dividing the blade into discrete elements and applying momentum theory to each section—essentially asking "how much energy does this piece of blade extract from the wind?" and summing up the answers.

The code was functional but running on assumptions documented in a growing `ASSUMPTIONS.md` file. Assumptions like "chord distribution based on typical 2.5 MW turbine blade planforms" and "single representative DU-series airfoil across entire blade."

Then I got access to `WindTurbineSpec/`—a directory full of actual data files.

## What Changed When Real Data Arrived

The new specifications included actual measured data for our specific turbine:

| File | Contents | Usage in Code |
|------|----------|---------------|
| `BladeProfile.csv` | Chord and twist at each radial station | `blade_geometry.m` interpolation |
| `DU91-W2-250.csv` | Lift/drag coefficients for root section | `airfoil_lookup.m` at r/R < 0.25 |
| `DU93-W-210.csv` | Lift/drag for mid-span airfoil | `airfoil_lookup.m` at 0.25 < r/R < 0.5 |
| `DU96-W-180.csv` | Lift/drag for outer blade | `airfoil_lookup.m` at 0.5 < r/R < 0.75 |
| `DU97-W-300.csv` | Lift/drag for tip region | `airfoil_lookup.m` at r/R > 0.75 |
| `towerSpecs.csv` | Tower diameter and wall thickness | Structural analysis module |

The first task was straightforward: stop hardcoding data. Instead of embedding arrays directly in MATLAB functions, the code needed to read from CSV files dynamically.

Here's the transformation in `blade_geometry.m`:

```matlab
% BEFORE: Hardcoded assumptions
r_ref = [r_hub; 15; 30; 45; r_tip];
c_ref = [4.0; 3.5; 2.5; 1.2; 0.8];
chord = interp1(r_ref, c_ref, r, 'pchip');

% AFTER: Reading actual data
blade_file = '../WindTurbineSpec/BladeProfile.csv';
if ~isfile(blade_file)
    error('BladeProfile.csv not found. Check WindTurbineSpec directory.');
end
blade_data = readtable(blade_file);
required_cols = {'RadialPosition', 'Chord'};
if ~all(ismember(required_cols, blade_data.Properties.VariableNames))
    error('BladeProfile.csv missing required columns: %s', strjoin(required_cols, ', '));
end
r_ref = blade_data.RadialPosition;
c_ref = blade_data.Chord;
chord = interp1(r_ref, c_ref, r, 'pchip');
```

The interpolation uses `'pchip'` (Piecewise Cubic Hermite Interpolating Polynomial) rather than linear or spline methods because it preserves monotonicity and avoids the overshoot that cubic splines can introduce at data boundaries—important when blade geometry must remain physically realistic.

Simple in principle. But the real work was in the details.

## Deep Dive: The Wind Shear Model

Wind turbines don't experience uniform wind. The atmospheric boundary layer means wind speed increases with height, and for a rotating blade, different parts see different wind speeds as they sweep through their rotation.

The physics follows a power law relationship:

V(z) = V_ref × (z/z_ref)^α

The exponent α typically ranges from 0.1 over smooth water to 0.3 over forested terrain. Our site uses α = 0.14, characteristic of open farmland. At hub height of 80m with a 47m blade, the tip sees wind speeds 8-12% higher at the top of its rotation than at the bottom.

The solution involves integrating over the blade's rotation:

```matlab
% Height varies with azimuth as blade rotates
% Convention: θ=0 at 3 o'clock, θ=90° at 12 o'clock
z = z_hub + r * sin(theta);

% Apply power law at each azimuth position
V_local = V_ref * (z / z_ref).^alpha;

% Calculate azimuth average using trapezoidal integration
V_avg = trapz(theta, V_local) / (2*pi);
```

Understanding this physics matters when debugging. If your power predictions are consistently 7% high, checking whether you're accounting for shear correctly is a good starting point.

## What AI-Assisted Development Looked Like

The session involved several distinct tasks where Claude Code accelerated the work:

**Reviewing assumptions against new data** — Going through `ASSUMPTIONS.md` line by line to identify what could now be replaced with real values. This would have been tedious solo work; with AI assistance, it became a systematic conversation about each assumption's validity.

**Updating MATLAB functions to read CSV files** — Claude generated the boilerplate file-reading and error-handling code, letting me focus on engineering logic rather than string parsing.

**Explaining the wind shear model** — Sometimes the most valuable AI contribution is helping you understand code you've already written. Rubber-duck debugging with an AI that can actually respond.

## The Results: Assumed vs. Actual

The chord distribution tells the story. The assumed profile was a generic curve based on published data from similar-sized turbines. The actual Clipper C96 blade is more aggressive—wider near the root for structural strength, tapering faster toward the tip for aerodynamic efficiency.

With assumed data:
- Peak power: 2.3 MW at 12 m/s wind speed
- Cut-in wind speed: 4.2 m/s
- Annual energy production: 6.8 GWh

With actual blade profiles:
- Peak power: 2.47 MW at 11.5 m/s wind speed
- Cut-in wind speed: 3.8 m/s
- Annual energy production: 7.4 GWh

The 9% increase in predicted annual energy isn't academic—it's the difference between viable and non-viable wind farm economics.

## The Meta-Lesson: Documentation as a Checklist

What made today's transition smooth was that `ASSUMPTIONS.md` file. When I built the solver without real data, I documented every assumption with the assumed value, why I chose it, what impact it might have, and what actual data would fix it.

When real specifications arrived, that documentation became a checklist. Some assumptions remained—air density still uses standard atmosphere, Reynolds number variation along the blade span still needs work—but the document now clearly distinguishes between "things we're still guessing" and "things we know."

## Practical Takeaways

**Document your assumptions explicitly.** Not as comments buried in code, but as a separate artifact that serves as a checklist when real data arrives.

**Design for data replacement from the start.** Even when hardcoding test values, structure your code so swapping in real data requires minimal refactoring.

**Understand the physics you're implementing.** The wind shear model is a dozen lines of code, but understanding *why* you're integrating over azimuth angles matters when debugging.

**Real data reveals real problems.** Once actual airfoil profiles replaced generic curves, edge cases appeared that the simplified model had hidden—particularly near the blade root where the airfoil transitions to a circular cross-section.

**Add validation checks when reading external data.** Files can be missing, columns can be renamed, data can be corrupted. A few lines of error handling save hours of debugging mysterious NaN results.

---

Tomorrow's work will validate these results against published benchmarks. But today delivered the core milestone: a model that can actually inform engineering decisions.