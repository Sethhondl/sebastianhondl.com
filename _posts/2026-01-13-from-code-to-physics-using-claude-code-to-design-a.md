---
layout: post
title: "From Code to Physics: Using Claude Code to Design a Ball Launcher"
date: 2026-01-13
categories: [development, ai]
tags: [claude-code, testing, debugging]
read_time: 3
word_count: 766
---

When I started using Claude Code, I expected it to help me write functions and debug code. I didn't expect it to become my go-to tool for back-of-the-envelope engineering calculations—but here we are.

## The Problem

I'm building ShapeForge, a CAD tool for designing 3D-printable mechanisms and mechanical toys. One component is a ball launcher for a carnival-style target game, and I needed to answer a basic question: how much motor power do I need to launch 120 half-pound balls eight feet into the air within 20 seconds?

The 120-ball count represents full hopper capacity for stress-testing the mechanism at maximum throughput. My motors max out at 1000 watts. Would that be enough?

## How Claude Approached It

Here's roughly what I typed:

> I need to calculate motor power requirements. I want to launch 120 balls, each weighing half a pound, to a height of 8 feet. All 120 need to launch within 20 seconds. My motors are rated for 1000W max—is that enough?

Rather than just returning a number, Claude walked through each step clearly.

**Unit conversion first.** Half a pound becomes 0.227 kg. Eight feet becomes 2.44 meters. This matters because physics formulas expect SI units, and mixing systems is a classic source of errors.

**Then the energy calculation:**
```
E = mgh = 0.227 kg × 9.81 m/s² × 2.44 m = 5.43 J per ball
```

Each ball needs about 5.4 joules of kinetic energy to reach that height. Multiply by 120 balls: roughly 652 joules total.

**Finally, power:**
```
Power = Energy / Time = 651.6 J / 20 s = 32.6 W
```

About 33 watts. But the raw number wasn't the most useful part of the response.

*A note on the physics: this assumes ideal conditions where all kinetic energy converts to gravitational potential energy, ignoring air resistance and ball spin. That's fine for a rough engineering estimate—Claude's efficiency factors account for real-world losses anyway.*

## Beyond the Textbook Answer

What actually helped were the follow-up considerations Claude raised without prompting:

**Mechanism efficiency.** Real launchers have losses. Flywheel mechanisms typically run 60-70% efficient, while pneumatic systems might drop to 40-50%. At 50% efficiency, I'd need around 65W of input power, not 33W.

**Peak vs. average power.** If I'm launching balls in bursts rather than a steady stream, instantaneous power demand spikes higher even if the average stays at 33W.

**Launch velocity.** Each ball needs 6.9 m/s (about 15.5 mph) initial velocity—useful for sizing the actual mechanism.

These details separate a homework answer from something you can actually build.

## Why This Matters

This wasn't a coding task. But it's exactly the kind of quick calculation that shows up constantly in hardware-adjacent projects, game physics, simulations, or any work that touches the physical world.

Before tools like Claude Code, I'd either open a spreadsheet and fumble through unit conversions, search for an online calculator that probably doesn't match my scenario, or dig through forums looking for a similar worked example.

Now I describe the problem in plain English with my actual constraints and get a worked solution I can verify step by step.

## Making It Work for You

**State your constraints upfront.** I mentioned the 1000W motor limit in my initial question. Claude used that to contextualize the answer ("only 3.3% of max output") without me asking.

**Ask about real-world factors.** You can follow up with questions like "what if my mechanism is only 40% efficient?" or "how does this change if I need to launch them in 5 seconds instead of 20?"

**Use it for sanity checks.** Even if you know the physics, having Claude show its work lets you spot errors in your own reasoning.

## Summary of Calculated Values

| Parameter | Value |
|-----------|-------|
| Ball mass | 0.227 kg (0.5 lb) |
| Target height | 2.44 m (8 ft) |
| Energy per ball | 5.43 J |
| Total energy (120 balls) | 651.6 J |
| Theoretical power | 32.6 W |
| Practical power (50% eff.) | ~65 W |
| Required launch velocity | 6.9 m/s (15.5 mph) |

## What's Next

With power requirements sorted—33W theoretical, around 65W practical—I can move forward on motor selection. The 1000W capacity gives me plenty of headroom.

Next up: choosing between a flywheel and pneumatic launcher. The flywheel's higher efficiency is appealing, but the pneumatic option might be simpler to 3D print. Sometimes the best engineering decision isn't the most efficient one—it's the one you can actually build.