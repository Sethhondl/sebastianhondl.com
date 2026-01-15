---
layout: post
title: "The Ghost in My Stirling Engine: When Code Runs Perfectly But Physics Doesn't"
date: 2025-09-23
categories: [development, ai]
tags: [claude-code, debugging]
read_time: 4
word_count: 858
---

There's a particular flavor of debugging frustration that hits different: when your code runs without errors, produces reasonable-looking output, and yet something is fundamentally wrong. I spent several hours with Claude Code working on a Stirling engine simulation for a mechanical engineering class, and the journey taught me something valuable about the difference between code that works and code that's correct.

## The Setup

The project involves simulating a beta-type Stirling engine—a heat engine that converts thermal energy into mechanical work. The core challenge is calculating how gas volumes change as the power piston and displacer move through their cycles, then using those volumes to determine pressure, torque, and ultimately flywheel sizing.

I had working MATLAB code. It ran without errors. It produced P-V diagrams that looked plausible. The numbers were in reasonable ranges. But the work output was about 30% higher than what the textbook example predicted for similar engine parameters. At first I chalked it up to different assumptions, but the nagging feeling wouldn't go away.

## The Problem Nobody Asked About

The issue surfaced when I asked Claude a simple question about a plotting line:

```matlab
plot(results.V_total*1000, results.P/1e6, 'b-', 'LineWidth', 2);
```

"Where does `results.V_total` and `results.P` come from?"

This innocent question led us through a multi-hour investigation. Tracing the data flow revealed that while the values were being calculated correctly according to the code's logic, the logic itself had a conceptual problem: the displacer volume wasn't being accounted for anywhere.

Here's the thing about a beta-type Stirling engine: the displacer is a solid cylinder that shuttles back and forth inside the main cylinder, pushing gas between the hot end and cold end. It doesn't change the total gas volume—that's the power piston's job. But the displacer itself takes up space. When it moves toward the hot end, it physically displaces gas (hence the name) into the cold region. The displacer in this simulation swept through about 15 cm³, which should reduce the available volume in whichever chamber it currently occupies.

My code calculated *where* the gas should go based on displacer position:

```matlab
volumeSplitFactor = 0.5 * (1 - cos(pi * normalizedDisplacerPosition));
```

But it never subtracted the displacer's physical volume from the total. The displacer was a ghost—influencing gas distribution without taking up any room.

## The HTML Documentation Breakthrough

When I couldn't pinpoint exactly where the physics diverged from the implementation, I asked Claude to create an HTML file explaining every step of the volume calculation with full mathematical expressions. This turned out to be the breakthrough.

The documentation laid out the model clearly:

**Mathematical Model (what should happen):**
$$V_{total}(θ) = V_{clearance} + V_{swept,piston}(θ) - V_{displacer}(θ)$$

**Code Implementation (what actually happened):**
```matlab
V_total = V_clearance + V_swept_piston;  % Where's V_displacer?
```

Seeing these side by side—the formal math saying "subtract the displacer volume" and the code conspicuously not doing that—made the bug impossible to miss. I actually said "oh no" out loud when I saw it. The comment in my code even said "displacer position affects gas distribution," which is true, but the implementation only handled the distribution part, not the volume part.

That missing subtraction meant my simulation had more working gas than a real engine would, explaining the inflated work output. The fix took about ten minutes once I understood the problem. The debugging took most of an afternoon.

## What I Learned

**Tracing data flow reveals assumptions.** When you ask "where does this value come from?" and keep asking until you hit first principles, you find the places where assumptions were made. Some of those assumptions are fine. Some aren't.

**Running without errors isn't the same as being correct.** Engineering simulations are tricky because wrong answers often look plausible. A P-V diagram with the wrong shape is still a closed curve. Work output that's 30% high just looks like an optimistic engine.

**Documentation as debugging.** Writing out the mathematical model in a separate document—not just comments in code—forces you to be explicit about what each equation represents. My intuition that something was off came from years of physics classes drilling in conservation laws. When the numbers felt too good, that physical intuition said "free energy doesn't exist, so where's the leak in your model?"

**AI assistants excel at tracing, less so at questioning.** Claude Code helped me trace values through the codebase efficiently. But when I asked about the displacer volume and got an answer that technically addressed the code but not the physics, I felt a flicker of dissatisfaction—like when someone answers your question grammatically but not substantively. That's when I knew to push harder.

## The Takeaway

Next time, I'll write out the full mathematical model in LaTeX or on paper *before* coding, then compare equation-by-equation. A simple checklist—"Does my code include every term in equation 3?"—would have caught this in minutes instead of hours.

The ratio of ten-minute fix to afternoon-long debug feels about right for conceptual bugs. The hard part is never the correction—it's seeing what you've been looking past. Sometimes your code needs a ghost hunter more than a debugger.