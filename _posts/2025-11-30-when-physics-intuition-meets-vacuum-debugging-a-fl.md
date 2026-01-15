---
layout: post
title: "When Physics Intuition Meets Vacuum: Debugging a Flywheel Thermal Model"
date: 2025-11-30
categories: [development, ai]
tags: [claude-code, git, debugging]
read_time: 3
word_count: 755
---

The rotor temperature wasn't changing. According to my MATLAB simulation, a flywheel spinning at 40,000 RPM inside a vacuum chamber—generating electromagnetic losses, rejecting heat only through radiation—sat perfectly at ambient temperature. I stared at the graph for a full minute before the obvious hit me: that's thermodynamically impossible.

## Why Vacuum Changes Everything

In a vacuum, there's no air to carry heat away through convection. The only path for thermal energy to escape is radiation, governed by the Stefan-Boltzmann law. With a rotor emissivity of 0.4 and housing emissivity of 0.9, even modest electromagnetic losses should push temperatures up noticeably. A rotor that stays at 30°C while dissipating power isn't a simulation result—it's a simulation bug.

This project is part of my Mechanical Engineering Modeling course at UMN. We're analyzing a flywheel energy storage system that stores 10 kWh of extractable energy, delivers 100 kW of power, and spins between 20,000 and 40,000 RPM inside a vacuum chamber. Our professor provided protected MATLAB functions (`.p` files) for electromagnetic and thermal behavior. My job was to call them correctly.

I wasn't.

## Tracing Backward from the Impossible

When I brought this to Claude Code, my first instinct was to blame the `.p` files. Maybe they were broken? But Claude pushed back with a principle that proved right: trust official interfaces, question your usage.

"The protected functions are provided by your professor and used by the entire class. If they were broken, you'd have heard about it. Let's trace how you're calling `rotorLosses()` instead."

We started at the symptom—zero losses—and worked backward. The rotor loss function expected angular velocity in rad/s:

```matlab
Q_rotor = rotorLosses(params.shaft_diameter/2, params.flywheel_length, ...
                      omega, params.emissivity_rotor);
```

"Print the actual omega value you're passing," Claude suggested. "Don't trust intermediate variables—verify the final input."

I added a diagnostic line. The omega value was zero.

## The Bug: A Silent Initialization Error

The root cause was embarrassingly simple. In my parameter initialization, I computed `omega_min` before `min_speed_rpm` was defined:

```matlab
% Original (buggy) order:
params.omega_min = params.min_speed_rpm * 2*pi / 60;  % Uses undefined field!
params.min_speed_rpm = params.max_speed_rpm / 2;      % Defined too late
```

MATLAB doesn't always error on accessing an undefined struct field—it can silently return an empty array, which multiplied through to zero. Every downstream calculation inherited this zero. The rotor losses function received `omega = 0`, computed zero losses, and the thermal model correctly predicted no temperature rise from zero heat input.

The fix was reordering two lines:

```matlab
% Fixed order:
params.min_speed_rpm = params.max_speed_rpm / 2;      % Define first
params.omega_min = params.min_speed_rpm * 2*pi / 60;  % Now this works
```

After the fix, the temperature graphs showed exactly what vacuum physics predicts: rotor temperature rising with speed as electromagnetic losses increase, constrained by radiation-limited heat rejection.

## How Claude Code Helped Find It

The debugging approach was methodical. After I described the symptom, Claude suggested adding a diagnostic print before the function call:

```matlab
fprintf('Debug: omega = %.2f rad/s, shaft_r = %.4f m\n', omega, params.shaft_diameter/2);
```

When I saw `omega = 0.00`, Claude immediately asked: "Where is omega computed? Let's trace the assignment chain."

This systematic approach—printing actual values rather than assuming they match expectations—found the bug in under ten minutes. I'd been staring at thermal equations for hours, convinced the physics was wrong. The physics was fine. The initialization order wasn't.

## Practical Takeaways

**Trust official interfaces, question your usage.** When protected code returns unexpected results, the bug is almost always in how you're calling it.

**Physics provides sanity checks.** A temperature that doesn't change when losses are applied violates thermodynamics. Domain knowledge catches bugs that static analysis can't.

**Print actual values, not variable names.** MATLAB's silent handling of undefined struct fields meant my bug produced no errors—only wrong results. Explicit verification catches these.

**Initialization order matters.** In languages that don't enforce declaration-before-use, assignment order in a struct can silently break dependent calculations.

## The Collaboration That Cracked It

The pattern that emerged was clear: Claude Code handled systematic exploration—suggesting diagnostic prints, tracing variable dependencies, questioning assumptions. I provided the physics intuition that recognized "rotor at ambient in a vacuum" as impossible.

Neither approach alone would have found this quickly. Without physics intuition, I might have accepted the output as correct. Without methodical tracing, I'd still be reviewing equations that were never the problem.

The bug was two lines in the wrong order. The lesson was bigger: when your simulation violates physics, trust physics. The code is lying.