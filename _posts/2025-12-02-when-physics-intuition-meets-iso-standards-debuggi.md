---
layout: post
title: "When Physics Intuition Meets ISO Standards: Debugging My Understanding of Rotor Runout"
date: 2025-12-02
categories: [development, ai]
tags: [claude-code, testing, debugging]
read_time: 5
word_count: 1015
---

Something didn't add up.

I was staring at simulation results for our flywheel energy storage system, watching rotor runout values climb as the state of charge increased. My gut said this was wrong. A well-balanced rotor shouldn't wobble more just because it's spinning faster, right?

Turns out, my gut was confidently incorrect. The path to understanding why taught me more about debugging mental models than any compiler error ever has.

## The Setup: Why Runout Matters

A flywheel energy storage system stores kinetic energy in a spinning rotor—essentially a mechanical battery. Charge it by spinning the rotor up, discharge it by letting it slow down through a generator. The state of charge maps directly to rotational speed: higher RPM means more stored energy.

Rotor runout is the deviation of the rotor's center of mass from its geometric center as it spins. Even precision-manufactured rotors have some residual eccentricity—a tiny offset between where the mass center *is* and where it *should* be. This eccentricity causes vibration, and excessive vibration damages bearings, creates noise, and limits safe operating speeds.

When I saw runout increasing with speed, I assumed our model was broken. The *physical* eccentricity doesn't change just because you spin faster. The metal is the same shape at 10,000 RPM as at 5,000 RPM.

## What I Thought I Knew

My mental model went like this:

- Residual unbalance creates an eccentricity *e* (in millimeters)
- The unbalance force is *F = m × e × ω²*, where *m* is rotor mass and *ω* is angular velocity
- Force grows with the square of speed, but eccentricity stays constant

This suggested that while *force* increases with speed, the geometric displacement should remain fixed. The rotor doesn't physically relocate its center of mass by spinning faster.

Yet our model showed increasing runout. We were using an ISO G2.5 balance grade, which I vaguely knew was "a good balance specification." I hadn't thought through what that specification actually *meant*.

## The ISO Standard That Changes Everything

I finally pulled up ISO 1940-1, the international standard for balance quality of rotating rigid bodies. There it was—the insight I'd been missing.

The ISO balance grade G is defined as:

**G = e × ω**

Where *G* is the balance grade (mm/s), *e* is permissible eccentricity (mm), and *ω* is angular velocity (rad/s).

For G2.5:

**e = 2.5 / ω**

This was the aha moment. The ISO standard doesn't define a constant eccentricity. It defines a *constant product* of eccentricity and speed. As speed increases, permissible eccentricity decreases proportionally.

## Connecting Standard to Physics

When you specify a rotor balanced to G2.5, you're saying the residual unbalance satisfies *e × ω ≤ 2.5* at maximum operating speed. Our model used the G value directly, setting *e = G/ω*. As ω increases, eccentricity *decreases*—correct behavior for a rotor balanced to a given G grade.

What about the unbalance force?

**F = m × e × ω² = m × (G/ω) × ω² = m × G × ω**

The force grows *linearly* with ω, not quadratically. Decreasing eccentricity partially compensates for increasing speed.

And dynamic displacement at the bearing? That depends on both force and the system's dynamic stiffness at the excitation frequency. At synchronous frequency—the rotor's spin speed—we evaluate stiffness at exactly that frequency, not some static value.

Here's where runout increase comes from. As speed climbs:
1. Unbalance force grows linearly (not quadratically, thanks to the G-grade relationship)
2. Dynamic stiffness at synchronous frequency changes with speed
3. Near resonances, stiffness drops dramatically
4. The net effect can be increasing runout, even with decreasing eccentricity

Our model was correct. My understanding wasn't.

## Validation Through Cross-Comparison

Another team had implemented their own rotor dynamics model. Comparing approaches helped validate this insight.

They parameterized differently—inputting the unbalance mass-eccentricity product directly rather than deriving it from ISO grade. When we aligned inputs to represent the same physical rotor, our results converged. Both models showed increasing runout near resonance frequencies.

The comparison confirmed our physics was consistent and highlighted how different-but-equivalent formulations can make the same behavior more or less intuitive.

## The Broader Lesson

When simulation results surprise you, the instinct is to debug code. Check for off-by-one errors, unit mismatches, sign flips. These are real failure modes.

But sometimes the bug isn't in the code. It's in your head.

I spent longer than I'd like to admit hunting for numerical errors before asking: "What if the model is right and I'm wrong?" That question—genuinely entertaining the possibility that my intuition had failed—unlocked the solution.

Mental model bugs don't throw exceptions. They don't highlight line numbers in red. They quietly filter how you interpret everything, making correct output look broken because your expectations are miscalibrated.

## A Better Debugging Process

The specific failure: I assumed eccentricity was a fixed geometric property, independent of speed. I didn't consider that engineering standards might define allowable eccentricity as a function of operating conditions.

Going forward, when results surprise me:

1. **Write down my prediction.** What exactly do I expect, and why?
2. **Surface the assumptions.** What physical relationships am I invoking? What am I treating as constant?
3. **Audit those assumptions.** Are there standards, specifications, or constraints that invalidate my mental model?

Only after that audit do I look for code bugs.

## Takeaways

If you work with rotating machinery or any domain where specifications interact with physics in non-obvious ways:

1. **ISO balance grades define a constant velocity product (G = e × ω), not constant eccentricity.** For G2.5, eccentricity decreases with speed.

2. **Unbalance force under a constant-G spec grows linearly with speed, not quadratically.** The ω² from centripetal acceleration is partially cancelled by 1/ω from decreasing eccentricity.

3. **Dynamic response depends on stiffness at excitation frequency.** For synchronous vibration, that's the spin speed—not static stiffness.

4. **When results surprise you, audit your mental model before your code.** The bug might be in your assumptions.

The flywheel is spinning correctly. It just took my understanding a while to catch up.