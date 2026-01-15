---
layout: post
title: "When Your Control Systems Final Becomes a Week-Long Engineering Marathon"
date: 2025-12-14
categories: [development, ai]
tags: [claude-code, git, testing, api, debugging]
read_time: 5
word_count: 1190
---

There's something uniquely humbling about a take-home final exam that spans an entire week. In graduate-level control systems courses, these extended exams don't test whether you can recall formulas under pressure—they test whether you can apply theory to messy, realistic problems that resist clean solutions. Seven days instead of three hours sounds easier. It isn't. It just means you have seven days to discover exactly how deep the rabbit hole goes.

This week I've been working through my ME 5281 Feedback Control Systems final, designing a complete control system for a chemostat. Think of it as a carefully controlled petri dish: you pump nutrient solution in at one end, bacteria consume it and multiply, and the mixture flows out the other end. Researchers use them to maintain bacterial populations at precise, steady concentrations—essential for studying how microorganisms behave under controlled conditions. The problem set covers everything from Jacobian linearization to full state feedback with integral action, observers, and classical control comparisons. It's the kind of comprehensive exam that reveals whether you actually understand control theory or just memorized formulas.

## The Challenge: Bridging Theory and Implementation

The exam provides a nonlinear chemostat model with three state variables. The nutrient concentration `n` represents how much food is available for the microorganisms. Species `a` consumes these nutrients and grows, while species `b` feeds on species `a`—and `b` is the population we actually want to control. The input `u` is our nutrient feed rate, the only knob we can turn.

The dynamics look like this:

```
ṅ = u - k₁na
ȧ = αk₁na - k₂ab - k₃a  
ḃ = βk₂ab - k₄nb
y = b
```

Simple enough on paper. The real difficulty emerged when I sat down to implement the controller in Simulink. The control law itself is compact:

```
u = -K*(x - x_o) + Ki*xi + u_o
```

But this single equation hides a maze of signal routing decisions. Where does the equilibrium offset enter? How do you wire up the integrator state `xi`? Which signals need to be subtracted versus added? I spent an embarrassing amount of time staring at Simulink's blank canvas, uncertain how to connect pieces I understood in isolation.

## Where Claude Code Actually Helped

Frustrated with my mental block, I asked Claude to help me visualize the feedback controller structure. The resulting ASCII block diagram mapped out exactly where each signal flows:

```
                              CONTROLLER
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  setpoint ────┐                                                          │
│               ▼                                                          │
│           ┌───────┐      ┌─────────┐      ┌──────┐                       │
│           │   Σ   │      │   1/s   │      │  Ki  │                       │
│           │  + -  │─────▶│Integrator─────▶│ Gain │────┐                  │
│           └───────┘      └─────────┘      └──────┘    │                  │
│               ▲                                       ▼                  │
│               │                                   ┌───────┐    ┌─────┐   │
│               │ y_output                          │   Σ   │───▶│ + u₀│──▶│ u
│               │                                   │+ + + -│    └─────┘   │
│  x_o ─────────────────────────────────────────────────┘▲                 │
│                                                        │                 │
│           ┌───────┐      ┌──────┐                      │                 │
│  x_hat ──▶│   Σ   │─────▶│  -K  │──────────────────────┘                 │
│           │  + -  │      │ Gain │                                        │
│           └───────┘      └──────┘                                        │
│               ▲                                                          │
│               │                                                          │
│  x_o ─────────┘                                                          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

This was exactly what I needed. The diagram made explicit what the equation left implicit: the state error `(x - x_o)` forms one path, the integrated tracking error forms another, and they combine with the equilibrium input `u_o` to produce the final control signal.

## The Verification Loop That Actually Worked

The most useful workflow I discovered wasn't having Claude compute answers—it was using iterative verification as a dialogue. After calculating my controller gains using pole placement, I'd show Claude my work and ask it to trace through the logic step by step.

After placing my closed-loop poles at -3±4j for the system dynamics and -15 for the integrator, I computed the gains and then asked Claude to verify that the resulting closed-loop eigenvalues actually matched these targets. This process caught several errors I would have missed. At one point, Claude flagged that my observer gain matrix had incorrect dimensions—I'd been treating a column vector as a row vector. Another time, it caught a sign error in my Jacobian linearization that would have cascaded through every subsequent calculation.

The speed difference was significant. Computing eigenvalues of a 4×4 matrix by hand takes a solid 15-20 minutes of careful cofactor expansion. Having Claude verify that my closed-loop A matrix had eigenvalues at the expected locations took seconds. This freed me to focus on understanding *why* I was placing poles where I placed them, rather than grinding through arithmetic.

That said, Claude wasn't always helpful. When I asked it to help debug why my Simulink simulation was producing oscillations, it suggested several generic fixes—check your sample time, verify your gain signs, look for algebraic loops—that didn't address the actual problem. I eventually discovered I'd wired the observer incorrectly, feeding back the wrong state estimate. The lesson: AI assistance shines for well-defined mathematical verification but struggles with debugging spatial problems like block diagram wiring.

## The Classical Controller Surprise

The most interesting finding came in Problem 4, where we had to design a classical PID controller for comparison. After computing the transfer function from the state-space model and designing a lead-lag compensator, the analysis revealed something unexpected: the classical controller was unstable.

The loop transfer function had poles in the right half-plane that the compensator couldn't adequately address. This wasn't a calculation error—it was a genuine insight about why modern state-space methods exist.

With state feedback, I could independently place each closed-loop pole by choosing appropriate gain values, effectively reshaping the system dynamics from the inside. The classical approach only sees the input-output relationship and must work through the existing transfer function structure. When that structure contains difficult pole-zero configurations—as this chemostat model does—classical methods hit fundamental limitations.

## What I'll Do Differently Next Time

**Use AI for visualization, not just calculation.** The most valuable help wasn't computing eigenvalues—it was generating clear diagrams that made the signal flow obvious. When you're stuck on implementation, ask for a picture.

**Treat verification as a conversation.** Rather than asking "is this right?", show your work and ask the AI to trace through the logic. This catches errors while keeping you intellectually engaged.

**Verify analytically before touching Simulink.** I learned this one the hard way. My first attempt went straight from equations to block diagrams, and I spent hours debugging wiring issues that were actually math errors in disguise. On my second pass, I verified every gain matrix and equilibrium point analytically first. The implementation went smoothly because I knew exactly what correct behavior should look like.

**Let classical methods fail—then understand why.** When my lead-lag compensator couldn't stabilize the system, my first instinct was to assume I'd made a mistake. Understanding *why* classical control struggled—limited access to internal states, inability to independently place poles—transformed frustration into insight about the field's historical development.

One week, one chemostat, and a concrete demonstration of why state-space methods displaced classical control for complex multivariable systems. The math isn't just an academic exercise. It reveals real engineering limitations—and that's exactly what a good final exam should do.