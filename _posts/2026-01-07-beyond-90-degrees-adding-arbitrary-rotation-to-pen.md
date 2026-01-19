---
layout: post
title: "Beyond 90 Degrees: Adding Arbitrary Rotation to PenguinCAM"
date: 2026-01-07
categories: [development, ai]
tags: [claude-code, javascript, automation, testing, api]
read_time: 4
word_count: 811
---

Every aluminum sheet has a grain. Every CNC setup has constraints. And sometimes the only way to squeeze one more part out of a 12"×12" plate is to tilt it 23 degrees and pray your CAM software can keep up.

Mine couldn't—until today.

I've been building PenguinCAM, a browser-based CAM (Computer-Aided Manufacturing) tool for our FIRST Robotics Competition team. CAM software takes part designs and generates G-code: the line-by-line instructions that tell a CNC machine where to move, how fast to spin, and when to cut. The tool worked fine for parts aligned with the X and Y axes, but real-world material optimization often demands rotating parts to odd angles. A widget that only offered 0°, 90°, 180°, and 270° wasn't cutting it.

So I built arbitrary rotation. Here's how the math works—and what I learned along the way.

## The Bounding Box Problem

When you rotate a rectangular part, its axis-aligned bounding box changes. A 4"×2" rectangle needs exactly 4"×2" of space at 0°, but rotate it 45° and suddenly it occupies a larger square footprint.

The formula looks intimidating at first:

```javascript
const rotatedWidth = Math.abs(width * Math.cos(radians)) + Math.abs(height * Math.sin(radians));
const rotatedHeight = Math.abs(width * Math.sin(radians)) + Math.abs(height * Math.cos(radians));
```

But the intuition is straightforward. Imagine the rectangle's corners tracing circles as it rotates. At 0°, the width contributes fully to horizontal extent and the height to vertical. At 90°, they swap. At 45°, both dimensions contribute to both axes—hence the sum of projections.

The `Math.abs()` calls handle quadrants where sine or cosine go negative. A rotation of 135° shouldn't give you a negative bounding box, even though `cos(135°)` is negative. We care about the physical extent, not the direction.

## The Double-Modulo Trick

Angle normalization sounds trivial until you're debugging why 720° doesn't behave like 0°. The input slider allows values from 0 to 360, but what happens when someone types -45 or 450?

```javascript
const normalizedAngle = ((angle % 360) + 360) % 360;
```

This double-modulo pattern handles both positive and negative overflow. The first `% 360` brings large positives into range but leaves negatives negative. Adding 360 shifts everything positive. The second `% 360` catches the case where the original was already positive. Result: any input maps cleanly to 0–359.

## Rotating the Toolpath

Individual points rotate with standard trigonometry:

```javascript
function rotatePoint(x, y, angleDegrees, centerX, centerY) {
    const radians = angleDegrees * Math.PI / 180;
    const dx = x - centerX;
    const dy = y - centerY;
    return {
        x: centerX + dx * Math.cos(radians) - dy * Math.sin(radians),
        y: centerY + dx * Math.sin(radians) + dy * Math.cos(radians)
    };
}
```

The key detail: rotation happens around a center point, not the origin. For part placement, that center is usually the part's centroid. Get this wrong and your part orbits wildly instead of spinning in place.

Each toolpath operation—contours, pockets, drill points—transforms through this function before G-code generation. The rotation happens in the coordinate space, not by physically rotating the stock material on the machine. Same result, simpler setup.

## The UI Decisions

Small interface choices shape the user experience. The rotation input accepts keyboard entry for precision (23.5°) but also provides increment buttons for quick adjustment. The preview updates live as you drag, showing the rotated bounding box against the stock material.

```html
<input type="number" id="rotation" min="0" max="360" step="1" value="0">
```

I debated whether `max` should be 359 or 360. Mathematically, 360° equals 0°, so allowing both creates redundancy. But users expect to type "360" when they mean "full rotation"—the redundancy is a feature, not a bug. The normalization code handles the equivalence internally.

## What I Learned

Three lessons from this feature:

**Trigonometry is easier to debug than to remember.** I haven't touched rotation matrices since college. Claude Code helped me reconstruct the math, but more importantly, it helped me verify each step with test cases. Coding against a clear spec beats coding from fuzzy memory.

**Physical intuition beats abstract formulas.** The bounding box calculation clicked once I visualized corners tracing arcs. When stuck on math, draw the picture.

**Edge cases are where features break.** 0°, 90°, 180°, 270° all worked immediately. The bugs appeared at 45°, at 360°, at negative angles. The interesting code isn't the happy path—it's the normalization and bounds checking that make the happy path possible.

## Next Steps

The rotation feature ships today. Next up: adding visual feedback for material utilization. If you're rotating a part to fit more pieces on a sheet, you want to see exactly how much aluminum you're saving. Right now that calculation happens in your head. It shouldn't have to.

Building tools for a robotics team means building tools that survive contact with sixteen-year-olds who will absolutely type -999 into any input field. Arbitrary rotation is now one less thing standing between a design and a finished part.
