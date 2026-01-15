---
layout: post
title: "When Physics Intuition Meets Vacuum Thermal Models: Debugging a Flywheel Energy Storage Simulation"
date: 2025-12-01
categories: [development, ai]
tags: [claude-code, testing, debugging]
read_time: 5
word_count: 1084
---

The rotor temperature read 147°C. At that temperature, the composite material would start to degrade and the magnetic bearings would lose their carefully tuned air gaps. Something was very wrong with my simulation.

## The Setup: A Complex Engineering Project

I'm working on Project 3 for my Mechanical Engineering Modeling course—a comprehensive analysis of a flywheel energy storage system. For those unfamiliar with the technology: flywheels store energy as rotational kinetic energy in a spinning mass. Think of a potter's wheel that keeps spinning after you stop pushing it, except engineered to spin at tens of thousands of RPM in a vacuum chamber to minimize air drag. These systems are used for grid-scale energy storage, spacecraft attitude control, and uninterruptible power supplies.

The project spans three deliverables: baseline system characterization, design optimization, and active magnetic bearing controller design. It's the kind of multi-physics problem where thermal, mechanical, and control systems all interact.

The simulation uses MATLAB with proprietary `.p` files—encrypted, compiled functions that I can call but can't read or modify. They calculate motor losses based on operating conditions, and my job is to wire everything together correctly. After completing a first pass through all three deliverables, I decided to create a "v2"—a single consolidated MATLAB file incorporating all the lessons learned.

## The Bug: Temperatures That Didn't Add Up

When I ran the v2 code, the temperature vs. state-of-charge plot looked wrong. In flywheel systems, "state of charge" refers to rotational speed—higher speed means more stored kinetic energy, analogous to a battery's charge level. At 100% state of charge, my simulation showed temperatures climbing past 140°C when they should have plateaued around 100°C. The stator power losses were also clearly incorrect.

Here's where Claude Code became invaluable—not for writing the physics equations, but for systematically auditing the code against the specification documents.

## Bug #1: Phantom Safety Factors

The first issue Claude helped me identify: arbitrary safety factors scattered throughout the code.

**My prompt:** "Can you go through the v2 code and make sure I don't have any random safety factors or arbitrary multipliers that aren't from the spec documents?"

**What Claude found:** It flagged several lines, including one where I'd estimated the AMB rotor mass as `0.10 * m_shaft` instead of using the actual value from the specifications. It also found a place where I'd added a 1.05 multiplier to account for "uncertainty" that had no basis in the project requirements.

These accumulated errors were masking the real physics and making it impossible to validate my results against expected values.

## Bug #2: Misunderstanding the Thermal Boundaries

The more fundamental issue came from re-examining the thermal model. In this flywheel system, the rotor spins in a vacuum chamber to minimize windage losses. This creates specific thermal constraints:

1. **Only radiation** transfers heat from the rotor to the housing—there's no air for convection, and the magnetic bearings are fully non-contact.
2. **Only rotor losses** heat the rotor—the stator windings are physically located outside the vacuum chamber and are cooled by a separate liquid cooling system.

I had been including the stator losses in the rotor temperature calculation. This is physically wrong—the stator sits outside the vacuum barrier, and its heat goes into the liquid cooling system, not into the vacuum chamber.

Here's what the fix looked like:

```matlab
% Power losses from the motor (from the .p file calculations)
P_rotor = 850;    % Watts dissipated in the rotor (hysteresis, eddy currents)
P_stator = 1200;  % Watts dissipated in the stator windings (I²R losses)

% WRONG: Including all losses in rotor heating
Q_to_rotor = P_rotor + P_stator;
T_rotor = T_ambient + Q_to_rotor / (h_rad * A_surface);

% RIGHT: Only rotor losses heat the rotor in vacuum
Q_to_rotor = P_rotor;
T_rotor = T_ambient + Q_to_rotor / (h_rad * A_surface);
```

## The Value of a Fresh Start

Why did I miss this in the first place? The original code was spread across three directories for the three deliverables, each with slightly different assumptions. When I found an error in one, I'd patch it locally without propagating the fix everywhere. The "v2 from scratch" approach forced me to make every assumption explicit:

- All values trace back to specific sources ("Appendix B, Table A.1")
- No arbitrary safety factors—only values from the specifications
- A companion `ASSUMPTIONS.md` file documenting every modeling choice

Claude helped me build this by exploring what we'd learned from both Homework 3 (which covered similar motor loss calculations) and the Project 3 attempts. The key question I asked: "What from hw 3 needs to be applied to project 3 code?" This surfaced several calculation methods I'd implemented correctly in homework but incorrectly in the project.

## The Outcome

After fixing both the phantom safety factors and the thermal boundary error, the temperature plot finally made physical sense. At rated power and 100% state of charge, rotor temperature reaches approximately 100°C—right at the design limit.

The before/after difference was stark: instead of temperatures continuing to climb past 140°C (indicating a design that couldn't sustain continuous operation), they plateaued at the material limit. The system is designed so that at maximum continuous operation, you're operating right at the thermal boundary—which is good engineering, not a bug.

## Lessons for AI-Assisted Engineering Work

**Claude excels at systematic auditing.** When I asked for a search through the codebase for undocumented multipliers, Claude methodically found them. This kind of tedious verification is exactly where AI assistance shines—I can focus on whether each finding is actually a problem rather than on the searching itself.

**Physics understanding must come from you.** Claude could find that I was adding rotor and stator losses together, but I had to recognize why that was wrong based on understanding the vacuum thermal model. The AI found the code; I had to supply the judgment about what the code should do.

## What I'd Do Differently

If I were starting this project over, I'd create the consolidated `ASSUMPTIONS.md` file from day one, before writing any code. The bugs I encountered weren't primarily coding errors—they were modeling errors that happened because I didn't have a single source of truth for "what physical system am I actually simulating?"

Sometimes debugging is about the code. Sometimes it's about the physics. The best outcomes happen when you can iterate quickly on both—and that's where having an AI assistant that can search, compare, and audit while you focus on the engineering judgment becomes genuinely powerful.