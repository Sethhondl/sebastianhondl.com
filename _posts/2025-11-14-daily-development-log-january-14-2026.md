---
layout: post
title: "Daily Development Log - January 14, 2026"
date: 2025-11-14
categories: [development, ai]
tags: [claude-code, git, testing, debugging]
read_time: 6
word_count: 1311
---

Looking at this blog post, it's already quite strong. The content is solid, the technical explanations are clear, and the conversational tone works well. Let me apply the final polish with focus on the specific areas mentioned.

---
layout: post
title: "When Your CAD Construction Lands the Pivot 20 Inches Away"
date: 2026-01-14
categories: [development, ai]
tags: [claude-code, matlab, mechanical-engineering]
read_time: 8
word_count: 1850
---

"You may use MATLAB for assistance, but please do not use MATLAB to solve Problem 1."

That line in the assignment rubric set the tone for my afternoon. The task: design a four-bar linkage that guides a rigid body through three specified positions. Problem 1 required CAD screenshots and hand calculations. Problem 2, the optional extra credit, allowed MATLAB. I ended up needing both—and learning why.

## What's a Four-Bar Linkage?

A four-bar linkage has exactly what the name suggests: four rigid links connected by four pin joints.

```
    Ground Pivot A                    Ground Pivot B
         O━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━O
         ┃          (Ground Link)        ┃
         ┃                               ┃
   Crank ┃                               ┃ Follower
         ┃                               ┃
         ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
    Moving Pivot A    (Coupler)    Moving Pivot B
```

The ground link stays fixed. The coupler carries the two moving pivots through space as the mechanism operates. The synthesis problem asks: given three positions I want the coupler to achieve, where should I place those four pivot points?

## The Three Positions

My assignment specified three coupler positions:

| Position | X (inches) | Y (inches) | Angle (degrees) |
|----------|------------|------------|-----------------|
| 1        | 0.0        | 0.0        | 0               |
| 2        | 2.5        | 1.0        | 25              |
| 3        | 4.0        | -0.5       | 45              |

The geometric method involves a beautiful insight. For each potential moving pivot location, you track where that point moves through all three positions, draw a circle through those locations, and the circle's center becomes your ground pivot. Do this twice—once for each moving pivot—and you have a complete linkage.

The catch is the geometry gets dense fast.

## The Arc Midpoint Mistake

Here's where I learned something the hard way. The textbook describes perpendicular bisectors of displacement arcs. I was computing the midpoint of a line segment connecting two positions and calling that my bisector reference point.

Claude flagged this when my ground pivot landed 20 inches away from the mechanism.

**Me:** The intersection point is way outside the expected region. The ground pivot should be somewhere near the mechanism.

**Claude:** You're using the midpoint of the straight line between positions 1 and 2. But for rotational motion, you need the perpendicular bisector of the arc that the point traces. The perpendicular bisector of a chord passes through the circle's center—which is exactly where the ground pivot sits. Your calculation assumes linear interpolation.

The fix required going back to first principles: the moving pivot at position 1 and the moving pivot at position 2 are the same physical point, just at different times. I'd been computing something else entirely.

This wasn't a subtle error. My CAD construction was placing ground pivots in physically impossible locations, and I'd been staring at it wondering why the mechanism wouldn't close.

## Connecting Code to Geometry

Here's the coordinate transformation function we developed:

```matlab
function [x_global, y_global] = transform_point(x_local, y_local, theta, x_ref, y_ref)
    % Transform body-fixed coordinates to global frame
    R = [cos(theta), -sin(theta);
         sin(theta),  cos(theta)];
    
    local = [x_local; y_local];
    ref = [x_ref; y_ref];
    
    global_coords = R * local + ref;
    x_global = global_coords(1);
    y_global = global_coords(2);
end
```

I placed a moving pivot at (1.5, 0.8) inches relative to point P in the coupler's body-fixed frame. The function computed where that pivot appeared in global coordinates at each position:

At position 1: (1.5, 0.8)  
At position 2: (3.42, 1.99)  
At position 3: (4.49, 1.13)  

Three global positions. The circle through all three has its center at the ground pivot. That's the geometric insight the whole method relies on.

## The Sign Error

Beyond the arc midpoint confusion, Claude caught a subtler issue. The textbook used notation like δᵢⱼ for displacement and αᵢⱼ for rotation angle. I'd been computing δ₁₂ correctly but using the wrong sign convention for α₁₂.

When your rotation matrix uses the wrong sign, all your perpendicular bisector calculations rotate the wrong direction. The circle intersections exist, but they're on the wrong side of the construction.

Claude noticed because the MATLAB verification showed the coupler orientation at position 3 as -45 degrees instead of +45 degrees. A single sign error propagating through ten lines of matrix multiplication.

## Grashof or Not?

One required result: does the mechanism satisfy the Grashof condition? This determines whether the shortest link can make a full rotation, or whether the mechanism is limited to rocking.

The criterion: if S is the shortest link, L is the longest, and P and Q are the other two, then S + L ≤ P + Q for full rotatability.

My final linkage dimensions:

| Link | Length (inches) |
|------|-----------------|
| Ground | 5.2 |
| Input crank | 2.1 |
| Coupler | 4.8 |
| Output follower | 3.7 |

S + L = 7.3, P + Q = 8.5. Since 7.3 ≤ 8.5, the input crank can rotate continuously—what you'd want for a motor-driven application.

## When Claude Misunderstood

The collaboration wasn't all smooth. When I asked Claude to verify my mechanism had no branch defects, it started explaining transmission angles—related but not the same concept.

**Me:** Branch defects aren't about transmission angle. They're about whether the mechanism can flip to a different assembly mode while going through the specified positions.

**Claude:** You're right—I conflated two concepts. Branch defects occur when the mechanism crosses a configuration where there are multiple valid assembly positions for the same crank angle. For three-position synthesis, the concern is whether the linkage can trace through positions 1 → 2 → 3 continuously without needing to disassemble. Want me to check whether the moving pivot traces a single arc through all three positions?

That recalibration led to a more useful check: verifying the arc swept by each moving pivot was monotonic rather than reversing direction.

## The Resolution

After the CAD construction for Problem 1 and the MATLAB verification for Problem 2, I had a working four-bar linkage. The ground pivots landed at (-1.2, 3.4) and (4.1, 3.8) inches. The mechanism passes through all three positions, allows continuous rotation, and has no branch defects.

MATLAB found the solution in milliseconds. The CAD construction took about an hour. But that hour taught me something the code couldn't: how sensitive the pivot locations are to small changes in the specified positions. Moving position 2 by half an inch completely changed the linkage proportions. The geometric construction made that sensitivity visible in a way that watching numbers change never could.

## The Uncomfortable Truth About Tool Selection

The constraint that frustrated me—no MATLAB for Problem 1—forced me to engage with the geometry at a level I wouldn't have otherwise. I now understand why certain pivot choices lead to compact mechanisms while others sprawl across the plane. I can look at three positions and estimate roughly where the ground pivots will land before calculating anything.

MATLAB gave me precision and verification. CAD gave me intuition. Claude helped connect the two, catching errors in both my geometric reasoning and my code.

But here's the thing: the errors Claude caught were errors I made. Claude didn't prevent me from making them. The learning happened in the debugging—in understanding *why* a ground pivot 20 inches away was wrong, not just *that* it was wrong.

If you're working through similar synthesis problems, you probably need both approaches. Computational tools verify and explore parameter variations. Manual construction builds the intuition that tells you when the computed answer is nonsense. And when you're stuck, having a collaborator that can check your perpendicular bisectors against first principles is more useful than I expected.