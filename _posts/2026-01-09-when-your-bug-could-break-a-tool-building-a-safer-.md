---
layout: post
title: "When Your Bug Could Break a Tool: Building a Safer CNC Postprocessor"
date: 2026-01-09
categories: [development, ai]
tags: [claude-code, python, javascript, testing, api]
read_time: 4
word_count: 959
---

Today's coding session went deeper into the physical constraints of CNC machining than any before. What started as routine G-code debugging became an exploration of manufacturing safety, the physics of cutting metal tubes, and why the order you remove tabs from sheet metal actually matters.

## The Bug That Could Have Crashed a Tool

The day began with a simple question: "Can you take a look at this G-code and see if something looks funny in the first few commands?"

Looking at the output from PenguinCAM—a CAM postprocessor I've been building for an FRC (FIRST Robotics Competition) team—I spotted something concerning. For context, a postprocessor translates toolpath geometry into the specific G-code dialect a particular CNC machine expects. Here's what the output looked like:

```gcode
G0 X1.1285 Y-0.1243
G0 Z1.2500
G0 Z0.7475
G1 F55.0
G3 X1.0885 Y-0.1243 I-0.0200 J0.0458
```

The problem? Line 3 is a `G0` (rapid movement) directly to the cutting depth. The tool would slam into the material at full speed instead of plunging at a controlled feed rate.

To understand why this matters, consider the speeds involved. A typical rapid traverse might move at 200–400 inches per minute, while a safe plunge rate for aluminum might be 20–30 IPM—an order of magnitude slower. That `G0` instead of `G1` means the endmill hits the material at ten times the intended speed. The cutting forces spike, the tool flexes, and you're looking at a snapped endmill, a gouged workpiece, or aluminum flying across the shop.

This is exactly the kind of bug that's easy to miss when generating G-code programmatically. The code "looks" right at a glance, but the physical consequences of that single character difference are dramatic.

## Tab Removal: A Star Pattern for Safety

Later in the day, we tackled a more nuanced machining problem. When cutting parts from sheet material, tabs hold the workpiece in place until the cut is complete. The question was: what's the safest way to remove them?

The answer involves physics. If you cut tabs sequentially around the perimeter, the part gradually loses support on one side, causing it to shift or vibrate. The solution is a "star pattern"—cutting opposite tabs first to maintain balanced support.

Picture tabs at the 12, 3, 6, and 9 o'clock positions around a part. Cutting them sequentially (12→3→6→9) means that by the time you reach 6 o'clock, the part is only supported on one side. Instead, cut opposite tabs first: 12 o'clock, then 6 o'clock (directly across), then 3, then 9. The part stays balanced throughout.

The implementation calculates this dynamically:

```python
def _get_star_pattern_order(self, num_tabs: int) -> list[int]:
    """Calculate star pattern order for balanced tab removal."""
    if num_tabs <= 2:
        return list(range(num_tabs))

    order = []
    opposite_offset = num_tabs // 2

    for i in range(opposite_offset):
        order.append(i)
        order.append(i + opposite_offset)

    # Handle odd number of tabs
    if num_tabs % 2 == 1:
        order.append(num_tabs - 1)

    return order
```

One edge case worth noting: for three tabs, `opposite_offset` equals 1, producing `[0, 1, 2]`—effectively sequential order. This is intentional. With only three tabs arranged in a triangle, there's no true "opposite" to cut first, so sequential removal works as well as any other approach. The star pattern provides meaningful benefit starting at four tabs.

What fascinates me about this problem is how it bridges abstract code and physical reality. The algorithm isn't complex, but understanding *why* it matters requires thinking about forces, vibration, and the behavior of partially-supported sheet metal.

## 3D Preview Coordinate Systems

Debugging the 3D tube preview led me down an unexpected rabbit hole. PenguinCAM includes a Three.js-based visualization that shows the tube and toolpaths in 3D, letting operators verify the setup before running actual code. The preview was showing incorrect dimensions because coordinate systems weren't aligned between the DXF file (source geometry), the G-code output (machine coordinates), and Three.js (screen coordinates).

Each system has its own conventions. The tube lying horizontal in the machine uses X for width, Y for depth into the tube, and Z for height. But Three.js uses Y for vertical by default.

The bug? The code was applying the coordinate transformation twice—once when parsing the DXF geometry and again when setting up the Three.js scene. The fix was simple: remove the redundant transformation in the scene setup and let the geometry parser handle the conversion alone.

## Practical Takeaways

**Test physical outputs before running them on a machine.** When generating code that controls machinery, a bug isn't just wrong output—it's potentially dangerous. Today's `G0` bug was caught in review, but we've had near-misses where incorrect arc directions (G2 vs G3) weren't caught until toolpath simulation showed the cutter going the wrong way. Those experiences inform the careful review process now.

**Domain knowledge improves the code.** Understanding *why* tabs need removal in a star pattern leads to better implementation than just coding "some kind of alternating removal." Working through the physics—not just the syntax—produces code that handles edge cases correctly.

**Coordinate system bugs are subtle.** When multiple systems with different conventions interact, transformations can easily be applied twice or not at all. The fix is usually simple once found, but finding it requires tracing data through each step.

## What's Next

The tube facing and cut-to-length operations still need real-world testing. The G-code simulates correctly, but there's no substitute for running aluminum through the machine. Tomorrow's adventure: taking this code from screen to shop floor.

Working on a project that bridges software and physical manufacturing reminds me that code doesn't exist in a vacuum. Every line eventually becomes motion, forces, and chips flying off a workpiece. And as we saw today, a single wrong character can be the difference between a clean part and a crashed tool.