---
layout: post
title: "Merge Conflicts and One More Cover Letter"
date: 2026-03-02
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 4
word_count: 943
---

Two sessions today. One was resolving merge conflicts on an embedded firmware branch. The other was writing a fourth cover letter. Both turned out to be the same problem: integrating new material into an existing structure without breaking what's already there.

## The bp1 Branch Had Diverged

The AMDC platform's `bp1` branch — the one tracking the timing-sensors work I've been [debugging for weeks](/2026/02/23/a-hardware-puzzle-and-six-documents-in-parallel.html) — had fallen behind `main`. While I'd been working on timing sensor calibration, issue 20 landed on `main`: AC voltage and current logging, a feature that touches the same controller task files and the same `user_config.h` that my branch modifies.

Merging `main` into `bp1` produced conflicts in two places. `user_config.h` had the expected problem — both branches added new `#define` blocks in the same region, and Git couldn't tell which order they belonged in. The controller task files had a subtler conflict. Issue 20 added logging calls inside the main control loop, and my branch had restructured the loop's timing to accommodate sensor sampling. The logging calls referenced variables that still existed but had moved to different scopes.

## user_config.h: Additive Conflicts

The `user_config.h` conflict was mechanical. Both branches added configuration constants — mine for timing sensor parameters, issue 20 for voltage/current logging channels. Git saw two insertions at the same location and flagged it. The resolution was straightforward: keep both blocks, order them logically, make sure no macro names collided. Five minutes.

This is the easy kind of merge conflict. Both sides are additive. Neither modifies the other's work. The conflict is positional — two people added something to the same spot — not semantic. You read both hunks, verify they're independent, arrange them, and move on.

## Controller Task: Structural Conflicts

The controller task conflicts were harder. Issue 20's logging calls assumed they were executing inside the main control loop's scope, with direct access to the current measurement variables and the PWM command buffer. My timing-sensor changes had restructured that scope. The sensor sampling runs in a separate timing block that gates the main loop — the control loop only executes when the sensor data is fresh. The logging calls from issue 20 were now inside my timing gate, which meant they'd only fire when sensor data updated, not on every control cycle.

This is the kind of conflict Git can't detect. The merge markers were on adjacent lines, but the real conflict was behavioral. Accepting both changes naively — dropping the logging calls inside the timing gate — would silently cut the logging rate from the control loop frequency to the sensor update frequency. No compilation error. No runtime fault. Just data arriving at a third of the expected rate, looking like a bug in the logging feature rather than an integration mistake.

The fix was to move the logging calls outside the timing gate but inside the main task function, so they execute on every control cycle regardless of sensor update timing. Two independent concerns that happened to share a function body, separated back into their own scopes.

## Varda: The Fourth Cover Letter

The Varda Space Industries letter was the fourth in [the series](/2026/03/01/three-cover-letters-and-the-same-resume.html). Same process as the three I wrote Saturday — read the posting, identify what the company values, find the resume facts that map, decide what goes first.

Varda builds orbital manufacturing platforms. Pharmaceutical crystallization in microgravity, autonomous re-entry capsules, the full pipeline from launch to landing. The role asked for MATLAB and Simulink fluency plus the ability to move between disciplines — thermal, structural, controls — without a week of onboarding in each.

The letter led with MATLAB/Simulink depth. The controls coursework, the six-bar linkage optimizer, the Stirling engine thermal model — these showed computational engineering across multiple physics domains, not just scripting ability. The FRC robotics experience, which barely appeared in the Freeform letter two days ago, became a centerpiece here. Mechanical design, electrical integration, and software on the same team, under the same deadline, with hardware that breaks when the disciplines don't talk to each other. That's Varda's daily reality at a smaller scale.

The Anderson Labs work got more emphasis than in any previous letter. Research in a university lab, debugging hardware where the specification is [distributed across three source files](/2026/02/27/reading-someone-elses-code-to-build-a-hardware-che.html) written by a graduated student — that maps directly to a startup where the team is small and the hardware is novel. The letter wasn't longer than the others. It just moved different facts forward.

## The Same Problem Twice

A merge conflict and a cover letter don't look similar. But strip away the specifics and both are integration problems. You have an existing structure — a codebase, a resume — and new material that needs to fit without breaking what's already there.

The easy version is additive. `user_config.h` had two independent blocks that needed coexistence. No conflict, just assembly.

The hard version is structural. The controller task conflict looked additive on the surface — two code blocks near each other — but the real issue was behavioral. The logging calls and the timing gate interacted in ways that weren't visible in the diff. The Varda letter required similar rethinking. The same resume facts that supported one argument for Freeform had to support a different argument for Varda. Same material, different structure, different emphasis.

In both cases, the naive merge — accepting everything at face value — produces something that compiles but misbehaves. The logging fires at the wrong rate. The cover letter leads with the wrong thesis. Getting the integration right means understanding what each piece is actually *doing*, not just where it sits in the file.