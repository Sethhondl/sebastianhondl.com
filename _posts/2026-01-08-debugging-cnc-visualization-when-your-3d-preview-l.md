---
layout: post
title: "Debugging CNC Visualization: When Your 3D Preview Lies to You"
date: 2026-01-08
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 5
word_count: 1142
---

I watched the simulated toolpath arc gracefully through empty space, cutting nothing. My finishing pass was positioned inside my roughing pass—in the space where material had already been removed. If I'd run this on the machine, the tool would have made a beautiful curved motion through air while the actual stock sat untouched, a sixteenth of an inch away.

This is the particular frustration of CNC software bugs. Unlike a web app where mistakes show up immediately, bad toolpath code survives until material is loaded, the spindle is running, and you're committed. Today I spent several hours with Claude Code tracking down visualization and toolpath issues in PenguinCAM, a CAM (Computer-Aided Manufacturing) tool I'm building for our FRC robotics team.

## The Mental Model That Makes Everything Click

Before I describe what went wrong, here's the insight that finally untangled the mess: **in CNC work, you almost never care about where the center of the tool is. You care about where the cutting edge is.**

This distinction is the source of an entire category of bugs. Here's what I mean, visualized for a facing operation where you want the finished surface at Y = 0.0625":

```
                    TOOL (end mill, looking from above)
                         ___________
                        /           \
                       |   CENTER    |    Tool center: Y = -0.0163"
                       |      *      |    (in negative space!)
                        \_____|_____/
                             |
    ═══════════════════════════════════════  ← Cutting edge touches here
                             |                  Final surface: Y = 0.0625"
                             |
    - - - - - - - - - - - - - - - - - - - -  ← Y = 0 (tube wall)

    MATERIAL (box tubing, cross-section)
    ┌─────────────────────────────────────┐
    │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
    │░░░░░░░░░░░ WASTE MATERIAL ░░░░░░░░░░│
    └─────────────────────────────────────┘
```

The math:
```
Desired face location:     Y = 0.0625" (1/16" offset from tube wall)
Tool radius:               0.0787" (4mm end mill)
Tool CENTER must be at:    Y = 0.0625" - 0.0787" = -0.0163"
```

The tool center is actually in *negative* Y space while cutting happens at positive Y. When you're deep in G-code generation, it's easy to lose track of which reference point you're using—and that confusion was the root cause of every bug I found today.

## Three Bugs, One Mistake

With that mental model established, here's what I was seeing in PenguinCAM:

**Bug 1: Stock visualization extended too far.** The 3D preview showed box tubing (hollow rectangular steel stock, commonly used in robotics frames) extending beyond where the actual material would be.

**Bug 2: Finishing pass inside roughing pass.** Roughing should remove bulk material, leaving a thin layer for the finishing pass to clean up. Instead, my finishing pass was positioned *closer* to the final surface than the roughing—meaning the roughing had already cut past where finishing needed to go.

**Bug 3: Cut-to-length operations using wrong reference.** The coordinate calculations were based on tool center position instead of cutting edge position. Everything was off by one tool radius.

All three traced back to mixing up tool center coordinates with cutting edge coordinates.

## The Roughing/Finishing Relationship

For tube facing operations, the passes have a specific geometric relationship:

- **Finishing pass** defines where the final surface will be
- **Roughing pass** must stay *outside* the finishing pass, leaving material for finishing to remove
- A small "finish allowance" (typically 0.005" to 0.010") separates them

My original code had this inverted. The roughing pass was cutting closer to Y=0 than the finishing pass, which meant finishing had nothing left to cut.

## Working Backwards from the Desired Result

The debugging approach that worked: start with where you want to end up, then calculate backwards.

The facing operation needs to leave 1/16" (0.0625") of material on the tube end—a design requirement for our robot frame, providing clearance for welding and assembly. Here's the corrected calculation:

```python
# Tube facing: final surface at Y = 0.0625" (1/16" offset for assembly clearance)
final_face_y = 0.0625
tool_radius = tool_diameter / 2  # 0.0787" for 4mm end mill
finish_allowance = 0.005

# Finishing pass: position tool so cutting edge lands at final surface
finishing_tool_center_y = final_face_y - tool_radius  # = -0.0163"

# Roughing pass: remove material OUTSIDE the finishing zone
roughing_face_y = final_face_y + finish_allowance  # = 0.0675"
roughing_tool_center_y = roughing_face_y - tool_radius  # = -0.0112"
```

The key: roughing_tool_center_y (-0.0112") is more positive than finishing_tool_center_y (-0.0163"). The roughing pass removes material further from Y=0, leaving material for finishing to clean up. Defining the end state first, then computing intermediate positions from cutting edge requirements, eliminated the reference point confusion entirely.

## The Visualization Gap

One thing became clear: there's a disconnect between what the 3D preview shows and what the G-code actually does.

PenguinCAM's workflow starts with DXF files (a standard CAD format) that define part geometry—hole positions, outlines, pocket shapes. The DXF is parsed, toolpaths are generated, G-code is output. The 3D preview is supposed to help verify the setup before running on the machine.

The problem: the preview shows stock material, but what I really need is the *part*—the shape that would remain after cutting.

```javascript
// Current: shows stock bounds only
const stockGeometry = new THREE.BoxGeometry(stockWidth, stockHeight, stockDepth);

// What I need: show actual part geometry from parsed DXF entities
```

The DXF parsing already extracts all the part geometry for toolpath generation. Rendering it in the 3D preview would tighten the feedback loop significantly—you could see the intended part shape overlaid on toolpaths, catching positioning errors before they become wasted aluminum.

## How AI Assistance Changed the Process

Working with Claude Code on this problem had a specific rhythm:

**Describe symptoms precisely.** "The finishing pass is inside the roughing pass" is actionable. "The toolpaths look wrong" isn't.

**Share visual evidence.** I pasted screenshots of the 3D preview. CNC problems are inherently geometric—describing them in words alone loses information.

**Ask about mental models, not just code.** The breakthrough came when I asked Claude to explain the coordinate system and tool compensation relationship, not just to fix the specific calculation. Understanding the *why* prevented the same class of bug from recurring elsewhere.

**Verify against physical reality.** G-code that looks correct in the editor might not survive contact with actual material. We caught this bug in simulation, but I've had near-misses where incorrect toolpaths weren't obvious until material was being cut.

## The Feedback Loop Problem

The meta-lesson from today: CNC bugs are particularly insidious because the feedback loop is so long. You write code, generate G-code, load it on the machine, set up material, run the job—and only *then* discover the tool was 0.0787" off in the wrong direction.

Anything that tightens that loop is worth the investment. Better visualization, simulation, dry runs with a marker instead of a spinning endmill. Today's bug was caught in software review. The bugs that slip through to the machine are expensive lessons in the difference between where a tool *is* and where it *cuts*.