---
layout: post
title: "When My Shading Logic Was Inverted and I Didn't Notice"
date: 2025-09-24
categories: [development, ai]
tags: [claude-code, testing, api, debugging]
read_time: 3
word_count: 773
---

The purple region was wrong. Not wrong in a way that threw an error or failed to render—wrong in a way that would have quietly propagated through my understanding of the problem if I hadn't happened to squint at it.

I was building an interactive HTML document for a feedback control systems class, and one of the s-plane diagrams had shading that looked reasonable at first glance. But it was highlighting regions that met *some* conditions instead of regions that met *all* conditions. The difference between "or" and "and" was hiding in plain sight.

## The Intersection Problem

In control systems, we place poles on the s-plane to achieve specific behaviors. For this problem, I needed to shade the region where poles could live while satisfying three constraints simultaneously:

- A damping ratio greater than 0.5 (restricting poles to a wedge-shaped region)
- A settling time under 2 seconds (keeping poles left of a vertical line)
- A natural frequency above 1 rad/s (pushing poles outside a semicircle)

Each constraint carves out its own allowed zone. The valid region is where all three overlap—typically much smaller than any single constraint alone.

My original diagram had separate shaded patches for each constraint. Visually, it suggested "here are three things to consider." Mathematically, it said the wrong thing entirely.

The fix was a single path element replacing three:

```html
<!-- Before: Three separate regions (implicit OR) -->
<path d="M 50 200 L 150 200 L 150 50 L 50 50 Z" 
      fill="lightblue" opacity="0.3"/>
<path d="M 200 200 L 350 200 L 350 50 L 200 50 Z" 
      fill="lightgreen" opacity="0.3"/>

<!-- After: One intersection region (explicit AND) -->
<path d="M 150 120 L 200 120 L 200 180 L 150 180 Z" 
      fill="purple" opacity="0.4"/>
```

The new coordinates trace the boundary where the damping wedge, settling time limit, and frequency semicircle all agree. Without understanding the geometry, you'd have no way to know those numbers were wrong before or right now.

## Why This Error Survived

The code was clean. The SVG rendered perfectly. The colors were distinct and the legend was accurate. Every quality check I'd normally run—syntax, rendering, visual clarity—passed.

The error lived at a different level: semantic correctness. The diagram accurately represented *what I told it to draw*, which was not *what I meant to draw*.

When I asked Claude to fix the shading, it had to read through almost a hundred lines of SVG—axis labels, grid lines, other curves—before locating the relevant path elements. For a human looking at the rendered output, you'd just point at the purple blob and say "that's wrong." For an AI working from code, there's no equivalent of pointing.

This asymmetry matters. AI assistance excels at translating abstract requirements into concrete geometry. It can hold multiple constraints simultaneously and compute their intersection without the mental juggling that causes human errors. But it can't glance at a rendered diagram and notice that something looks off.

## The Verification Gap

I've been generating more complete solutions lately—working code plus documentation in a single pass, rather than building incrementally. The efficiency gains are real when it works. But this bug made me realize I'd been verifying the wrong things.

I was checking:
- Does the code run?
- Does it render?
- Does it look professional?

I wasn't checking:
- Does this diagram say what the problem requires?
- Would a student looking at this learn the right thing?

The first set of questions are about execution. The second are about meaning. AI-generated code can ace execution while quietly failing meaning—and that failure mode propagates. You build on wrong foundations because they looked solid.

## What I'm Changing

After this, I'm treating visual code differently. Before accepting any generated diagram, I narrate what it shows in plain language and check that narration against the requirements.

For the s-plane diagram, that sounds like: "The shaded region represents where poles can be placed while achieving damping ratio above 0.5, settling time under 2 seconds, and natural frequency above 1 rad/s. It's bounded by the 45-degree damping lines, the σ = -2 vertical, and the ω = 1 semicircle."

If I can't narrate it, I don't understand it. If my narration doesn't match the requirements, the diagram is wrong regardless of how cleanly it renders.

This isn't a revolutionary insight. But I wasn't doing it, and the shading bug is what made me start. Sometimes the small fixes teach more than the big builds—not because the fix is profound, but because it exposes a gap in your process you didn't know existed.