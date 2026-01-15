---
layout: post
title: "Daily Development Log - January 14, 2026"
date: 2026-01-10
categories: [development, ai]
tags: [claude-code, testing, debugging]
read_time: 4
word_count: 985
---

I've prepared the final polished blog post. Here's the complete version ready for publication:

---

```markdown
---
layout: post
title: "Solving a Projectile Motion Problem with Claude Code"
date: 2026-01-13
categories: [development, ai]
tags: [claude-code, physics, robotics, engineering]
read_time: 4
word_count: 850
---

Picture a mechanism on a robot that needs to loft a foam ring from near ground level into an elevated goal 25 inches away. You know the distance and the height—but what launch angle and velocity will actually get it there? This is the kind of back-of-the-envelope physics problem that shows up constantly in FIRST Robotics (high school robotics competitions), and yesterday I used Claude Code to work through the math.

## Setting Up the Problem

The launcher sits at a fixed position. The target is 25 inches away horizontally and elevated above the launch point. I needed to find two things: the optimal launch angle and the required muzzle velocity.

My first instinct was 20 degrees—a fairly flat trajectory. Claude walked through the projectile motion equations and suggested something much steeper: around 70 degrees.

That felt wrong initially. But the math checked out: with a steep angle, the ring spends more time climbing, giving it the height needed to clear the goal. A shallow angle would send it fast and flat, missing high targets entirely.

## The Physics

Here's the core equation Claude derived for the launch velocity:

```
v = sqrt((g * x²) / (2 * cos²(θ) * (x * tan(θ) - y)))
```

Where:
- `g` = 386.4 (gravitational acceleration in inches per second squared)
- `x` = 25 inches (horizontal distance)
- `y` = target height above launch point
- `θ` = launch angle

At the peak of the arc, vertical velocity is zero, which gives us this constraint. Working through the numbers with a 74.5-degree angle yielded a required velocity of 193.5 inches per second—about 16 feet per second or 11 miles per hour, roughly jogging speed.

That result made physical sense. You're not trying to rifle the ring at the target; you're lobbing it in a high arc that drops neatly into the goal.

## The Iteration

What made this session useful wasn't just getting an answer—it was the back-and-forth refinement.

When I initially proposed 20 degrees, Claude didn't just say "that's wrong." It showed why: at that angle, the projectile wouldn't gain enough height. We walked through several angle values together, comparing trajectories until landing on 74.5 degrees as optimal for this geometry.

This kind of iterative problem-solving is where Claude Code shines. You can propose ideas, get immediate feedback on the physics, and adjust your thinking without hunting through textbooks or hoping your spreadsheet formulas are correct.

## Earlier That Day: CNC Coordinate Documentation

Before diving into launcher math, I spent time documenting work coordinate systems for CNC machining. Different context, but the same underlying theme: precision matters.

In CNC work, getting your coordinate offsets wrong doesn't just produce bad parts—at worst it means a tool embedded in your machine table or a serious injury. I was capturing the workflow for setting G54/G55/G56 offsets, documenting the exact sequence of touches and calculations that translate physical positions into machine coordinates.

Having that precision mindset fresh helped when I switched to the launcher problem. Both tasks require thinking carefully about coordinate systems, reference points, and how small errors compound into big problems.

## What I Learned

A few specific takeaways from this session:

**Trust the math, not intuition.** My gut said 20 degrees; physics said 74.5 degrees. The steep angle makes sense once you understand you're optimizing for height, not speed.

**Units matter more than you think.** Working in inches and inches-per-second kept everything consistent with the robot's coordinate system. Converting to metric mid-calculation is where errors creep in.

**Context carries over.** Having the CNC machining work fresh in mind helped me think about the launcher in terms of precise coordinates and reference points rather than vague approximations.

## The Satisfying Part

The most satisfying moment was realizing why 74.5 degrees works.

At that angle, you're launching the ring almost straight up with just enough horizontal component to drift over to the target as it falls. The ring reaches peak height almost directly above its starting point, then drops into the goal on the way down.

It's counterintuitive if you're thinking about throwing something *at* a target. But we're not throwing at it—we're lobbing over it and letting gravity do the final positioning.

That physical insight is what I'll remember from this session. Not the specific numbers, but the understanding of why steep angles work for elevated targets at short range.

## Summary of Calculated Values

| Parameter | Value |
|-----------|-------|
| Horizontal distance | 25 inches |
| Optimal launch angle | 74.5 degrees |
| Required velocity | 193.5 in/s (16 ft/s, 11 mph) |
| Gravitational constant | 386.4 in/s² |

## What's Next

With the launch parameters calculated, the next step is designing the actual mechanism—choosing between a flywheel launcher and a pneumatic system, then sizing the motors or air reservoir accordingly.

The physics gives you the target specs. Engineering turns those specs into something you can actually build.
```

---

**Polish summary:**

1. **Opening hook**: Starts with a concrete, visual scenario that immediately grounds the reader in the problem
2. **Transitions**: Each section flows naturally—problem setup → physics → iteration → related context → takeaways → insight → next steps
3. **Conclusion**: Ends with a memorable, quotable insight ("The physics gives you the target specs. Engineering turns those specs into something you can actually build")
4. **Title**: Changed to "Solving a Projectile Motion Problem with Claude Code"—more specific and searchable
5. **Tone**: Consistent first-person, conversational voice throughout
6. **Redundancy**: Removed all PR review content, streamlined the CNC section to supporting context
7. **Readability**: Short paragraphs, clear subheadings, technical details explained in plain language

The file needs write permission to save.