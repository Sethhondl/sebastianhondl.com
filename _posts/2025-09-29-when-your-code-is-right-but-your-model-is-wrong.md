---
layout: post
title: "When Your Code Is Right But Your Model Is Wrong"
date: 2025-09-29
categories: [development, ai]
tags: [claude-code, git, testing, api, debugging]
read_time: 5
word_count: 1118
---

I was staring at two P-V diagrams. The one from `PeytonTest.m` showed the classic rounded parallelogram of a working Stirling cycle—compression, heat addition, expansion, heat rejection, all flowing in the right direction. The one from my "clean" refactored version looked more like a crushed ellipse. Same equations. Same parameter values. Nearly identical code. Completely wrong output.

That's when I realized I wasn't debugging code. I was debugging my understanding of the physics.

Today I worked on two very different projects: building a MATLAB plugin to bring Claude Code's functionality into the MATLAB environment, and tracking down why my Stirling engine simulation produced the wrong P-V diagram. The contrast taught me something about how AI assistance works differently depending on whether you're solving a software problem or a modeling problem.

## The Plugin Architecture Problem

The MATLAB plugin project started with a classic software question: how do you integrate an external process into an IDE that wasn't designed for it?

I asked Claude to research MATLAB addon architectures and propose three implementation approaches, iterate on each until they were clear, then merge the best elements into a single plan.

The research uncovered several options:

1. **App Designer GUI** — Build a native MATLAB app with a terminal-like interface using TextArea components
2. **System command bridging** — Use MATLAB's `system()` function to communicate with Claude CLI as a subprocess
3. **Toolbox wrapper** — Create a proper MATLAB toolbox with functions that abstract the Claude interaction

Each approach had tradeoffs. App Designer would feel native but required significant GUI code. System commands were simpler but crude—no streaming output, awkward interaction patterns. The toolbox wrapper was cleanest architecturally but demanded more upfront design.

I chose the toolbox wrapper. The deciding factor was maintainability: a clean function-based API (`claude_query()`, `claude_explain()`, `claude_refactor()`) would be easier to extend and document than a GUI app, and it would integrate better with existing MATLAB workflows.

What made Claude useful here was speed. The toolbox structure recommendations from MathWorks' best practices repo, the App Designer integration patterns, the subprocess communication methods—assembling all that context manually would have taken hours.

With the plugin architecture mapped out, I switched to a problem where documentation couldn't help me.

## The Physics Problem Was Different

The Stirling engine simulation was a completely different beast. I had working code that produced correct P-V diagrams, and a refactored version that didn't. The task was to figure out why.

For those unfamiliar: Stirling engines work by shuttling gas between hot and cold regions, using temperature-dependent volume changes to drive pistons. The pressure at any point depends on how the total gas mass is distributed across regions at different temperatures. Get the volume calculations wrong and the pressure curve will be wrong, which means the P-V diagram—the signature of engine performance—will look completely off.

Here's the cold volume calculation where my bug lived:

```matlab
function coldVol = calculateColdVolume(crankAngle, params)
    % Power piston position from crank geometry
    powerPistonPos = calculatePistonPosition(crankAngle, params.powerCrankLength, params.powerRodLength);
    
    % Displacer position - offset by phase angle (typically 90 degrees)
    displacerPos = calculatePistonPosition(crankAngle + params.phaseShift, params.displacerCrankLength, params.displacerRodLength);
    
    % Cold side is the space between power piston top and displacer bottom
    coldVol.height = (displacerPos - powerPistonPos) - params.powerPinToPistonTop - (params.displacerHeight / 2);
    coldVol.volume = params.cylinderCrossSectionalArea * coldVol.height;
end
```

The 90-degree phase shift between the power piston and displacer is what makes Stirling engines work. The displacer moves gas between hot and cold regions while the power piston extracts work from the pressure changes. Get that phase relationship wrong—even by applying it in the wrong direction—and your P-V diagram will be incorrect even if every calculation is numerically precise.

## The Debugging Process

I had Claude diff the two files to find structural differences. It identified several: the working code had the phase shift applied as `crankAngle - params.phaseShift`, while my refactored version used `crankAngle + params.phaseShift`. It also flagged differences in how the displacer height offset was calculated.

But Claude couldn't tell me which version was *correct*. Both were syntactically valid. Both produced numbers. The question was which one matched the physical engine geometry, and that required understanding what direction the displacer actually moves relative to the power piston.

So I went back to basics. I added logging to print piston positions at 0°, 90°, 180°, and 270° of crank rotation. In a properly phased Stirling engine, when the power piston is at top dead center, the displacer should be 90° behind in its cycle—partway through moving gas from cold to hot.

My refactored code had the phase relationship inverted. The displacer was leading instead of lagging. The sign on `params.phaseShift` needed to flip from addition to subtraction.

One character. The difference between `+` and `-`. The code was right. The model was wrong.

A correct Stirling P-V diagram looks roughly like this:

```
    P (pressure)
    ^
    |    ___----___
    |   /          \      (expansion at high T)
    |  |            |
    |   \          /      (compression at low T)
    |    ---____---
    +-------------------> V (volume)
```

My broken version produced a figure-eight that crossed itself—physically impossible for a real engine, an immediate visual indicator that the phase relationship was backwards.

## What This Taught Me About AI-Assisted Debugging

For the MATLAB plugin, Claude's assistance was straightforward:
- Gathered scattered MathWorks documentation in minutes
- Structured the comparison between implementation approaches
- Generated initial function signatures for the toolbox API
- Caught a typo where I'd written `sytem()` instead of `system()`

For the Stirling engine, Claude helped differently:
- Quickly diffed the files and highlighted structural differences
- Explained the Schmidt equation when I asked for clarification
- Couldn't determine which phase convention was physically correct
- Couldn't look at the P-V diagram and recognize the loop direction was wrong

The debugging required me to understand what the displacer physically does and how that relates to the mathematical model. No amount of code analysis could substitute for that domain knowledge.

## The Takeaway

If you're working on projects that bridge software and physical simulation, partition your debugging accordingly:

**Use AI for code structure, API research, and pattern matching.** It's fast and thorough at gathering documentation, comparing approaches, and spotting syntactic issues.

**Keep the physical validation loop in your own hands.** When the output must match reality, you need to understand what "correct" looks like before you can recognize "wrong."

**When something looks wrong, ask: is this a code bug or a model bug?** Code bugs break execution or produce obviously wrong types. Model bugs produce plausible-looking numbers that don't match physics.

The model bugs are harder to catch. They're also more interesting. And sometimes they come down to a single character that changes which direction a piston moves.