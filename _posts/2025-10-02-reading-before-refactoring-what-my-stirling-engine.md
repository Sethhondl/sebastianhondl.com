---
layout: post
title: "Reading Before Refactoring: What My Stirling Engine Code Actually Taught Me"
date: 2025-10-02
categories: [development, ai]
tags: [claude-code, testing, api, debugging, refactoring]
read_time: 4
word_count: 839
---

There's a moment in every engineering student's semester when you realize your MATLAB code has become sentient—not in the fun AI way, but in the "I have no idea what half of these functions do anymore" way. Today was that moment for my Stirling engine simulation.

The request seemed simple: refactor `StirlingCycle.m` because it had grown unwieldy. But instead of diving straight into surgical code changes, Claude did something that surprised me. It read the entire file first.

## The Code Archaeology Phase

Before suggesting a single change, Claude walked through 400+ lines of thermodynamic calculations, slider-crank kinematics, and Schmidt analysis functions. The file had accumulated layers like sedimentary rock—each representing a different debugging session or feature request.

That reading phase revealed something I'd completely missed: three separate functions were calculating piston displacement using slightly different assumptions. One used full slider-crank kinematics. Another used a simplified sinusoidal approximation I'd added during an early debugging session. A third—buried in the Schmidt analysis section—used the exact kinematic equations but with hardcoded parameters instead of pulling from the config struct.

If Claude had jumped straight to "let's extract this into a separate file," it would have preserved all three approaches. The refactored code would have been just as inconsistent as the original, just spread across more files.

Here's what one of those problematic functions looked like:

```matlab
function vol = schmidtExpansionVolume(theta, params)
    % Simplified sinusoidal - added 10/15 during late-night debug
    stroke = params.powerBore * 0.8;  % Why 0.8? No idea anymore
    vol = params.clearanceVol + (stroke/2) * (1 - cos(theta));
end
```

That `0.8` factor was a mystery even to me. The comment admitted as much. The real slider-crank calculation elsewhere in the file used actual geometry—crank length, connecting rod length, proper kinematic equations. This simplified version was a debugging artifact I'd forgotten to remove, producing subtly different volume curves than the rest of the simulation.

## Test-First Refactoring: Catching What I'd Hidden

What happened next changed how I'll approach refactoring forever. Instead of just rewriting the code to "look cleaner," Claude suggested writing comprehensive tests first—tests that would capture exactly what the current code produces.

The first test compared the output of all three displacement calculations across a full 360-degree cycle:

```matlab
function test_displacement_consistency()
    params = loadDefaultParams();
    angles = linspace(0, 2*pi, 360);
    
    kinematic = arrayfun(@(a) calculatePistonPosition(a, params, true), angles);
    sinusoidal = arrayfun(@(a) simplifiedDisplacement(a, params), angles);
    schmidt = arrayfun(@(a) schmidtExpansionVolume(a, params), angles);
    
    % These should match within tolerance
    assert(max(abs(kinematic - sinusoidal)) < 0.001, 'Kinematic vs sinusoidal mismatch');
end
```

The test failed immediately. Maximum deviation: 0.023 meters. Not huge in absolute terms, but enough to throw off the P-V diagram integration by several percent. The work output calculation used the kinematic version while the Schmidt analysis used the sinusoidal approximation. I'd been comparing apples to oranges for weeks.

That's when I understood what my "clamped volume calculations" were actually doing. During debugging, I'd noticed the P-V diagram wasn't closing properly—the cycle didn't return to its starting point. Instead of finding the root cause (inconsistent displacement functions), I'd added volume clamping at the cycle boundaries:

```matlab
if abs(theta) < 0.01 || abs(theta - 2*pi) < 0.01
    vol = params.clearanceVol;  % Force closure
end
```

This made the diagram look correct while masking the underlying physics violation. A test-first approach would have caught this immediately because I'd have had to articulate: "The P-V diagram should close naturally without forced clamping."

## What the Refactoring Actually Produced

With the tests in place, the refactoring became straightforward. One canonical displacement function. One set of geometric parameters. The Schmidt analysis now calls the same kinematics as everything else.

The refactored piston position function—now the only one—looks like this:

```matlab
function pistonPosition = calculatePistonPosition(crankAngle, params, isPower)
    if isPower
        angle = crankAngle;
        crankLength = params.powerCrankLength;
        rodLength = params.powerRodLength;
    else
        angle = crankAngle + params.phaseShift;
        crankLength = params.displacerCrankLength;
        rodLength = params.displacerRodLength;
    end

    beta = asin(crankLength * sin(angle) / rodLength);
    pistonPosition = rodLength * cos(beta) - crankLength * cos(angle);
end
```

Clean slider-crank kinematics, used everywhere. The mysterious `0.8` factor is gone. The volume clamping is gone too—and the P-V diagram still closes properly, because the physics is now consistent.

## The Broader Lesson

Writing tests before refactoring forced me to articulate what the code *should* do. That articulation revealed my mental model was wrong. I thought I had one displacement calculation with some cleanup code around the edges. I actually had three competing calculations and duct tape hiding the conflicts.

Five minutes of reading—really understanding the existing code—revealed problems I would have preserved if I'd jumped straight to restructuring. The tests gave me confidence that the refactored code actually works, not just that it looks cleaner.

Tomorrow I'll run the full simulation and compare output against theoretical Schmidt analysis predictions. If they don't match within tolerance, at least I'll know exactly which function to examine.

Sometimes the most productive coding session is the one where you write zero new features and just make the existing code honest.