---
layout: post
title: "A Missing 24 Volts and a Pipeline That Won't Stop Writing About Itself"
date: 2026-03-23
categories: [development, ai]
tags: [claude-code, python, git, testing, api]
read_time: 5
word_count: 1117
---

The PWM signal was there at the breakout board — clean, switching, exactly what the firmware commanded. At the inverter output, nothing. Same board, same net, same signal path, and somewhere between the two measurement points the waveform simply stopped.

This blog tracks a hardware debugging project alongside the software pipeline that publishes these posts. Most days the software earns the column inches. Today the hardware earned the spotlight.

## The Setup

We're bringing up a new power electronics inverter board for a motor drive research platform. The immediate goal: verify that the FPGA-generated PWM signals reach the gate driver inputs correctly. The tool for static testing is `hw pwm sw 99000 100` — an AMDC firmware CLI command that sets the PWM switching frequency to 99 kHz at 100% duty cycle. At full duty the output pins high, which strips away switching dynamics and turns signal tracing into a continuity problem. Either the voltage is there or it isn't.

Eric connected the PicoScope to the breakout board header. Signal present. He moved the probe to the gate driver input pin on the inverter. Signal absent. Somewhere along the PCB trace between those two points, the signal was being lost.

## The Thirty-Second Fix That Took an Hour to Find

The schematic told the full story, if you knew to read it completely. The gate driver IC has a pin called VINPs — a 24V supply input that powers the internal level shifters. Without 24V on VINPs, the chip is alive enough to accept an input but not alive enough to pass it through. The PWM signal enters the gate driver and vanishes.

The board setup procedure covered the 5V logic supply. It covered the current sensor bias voltage. It stopped there. The 24V wasn't omitted from the schematic — it was right there on the block diagram, clearly labeled. It was omitted from the narrative. The setup checklist that someone wrote from memory, the verbal walkthrough that accompanied the first board bring-up, the mental model that said "power it and go" — all of these carried an implicit assumption that 24V would already be connected.

This is the kind of requirement that lives in someone's head until the someone leaves the room. The designer knew VINPs needed 24V the way a carpenter knows which end of the hammer to hold. It never occurred to anyone to write it down because it never occurred to anyone that it wasn't obvious.

Eric connected the 24V supply. The PWM signals appeared at the inverter output immediately. A thirty-second fix after an hour of tracing signals, checking solder joints, and questioning whether the board had a manufacturing defect.

## The Scope as Debugger

There's a useful analogy between a PicoScope and printf debugging in software, but it's worth pushing past the surface. Printf tells you state at a point in execution. The scope tells you state over time at a point in a circuit. Printf answers "what was this variable when the program reached this line?" The scope answers "what has this net been doing for the last ten milliseconds?"

That distinction matters because it's what let Eric distinguish between "signal present" and "signal switching correctly." A multimeter would have shown voltage at the breakout board. The scope showed a stable DC level at the breakout and nothing at the inverter — the temporal information ruled out noise, crosstalk, and intermittent connections in one glance. The failure mode was binary and static, which pointed directly at a power supply issue rather than a signal integrity problem.

The debugging pattern was the same one that works in software: bisect the signal path, measure at the midpoint, determine which half contains the fault, repeat. The only difference is that the "breakpoints" are physical probe points on a PCB rather than lines in source code.

## Meanwhile, the Pipeline

The software system that generates these blog posts had another difficult day. The multi-pass generation pipeline — draft, review, revise, polish, each implemented as a subprocess call to the Claude CLI — produced another 36 empty tool calls. An empty tool call means the CLI was invoked, ran, and returned nothing usable: no text, no error, just silence. The pipeline treats this as a retryable failure, backs off, tries again, and accumulates a log full of attempts that went nowhere.

This is the eighteenth post in March. Of those eighteen, roughly a third have been primarily about the pipeline itself — its failures, its retry logic, its inability to produce output reliably. The system responsible for documenting work spends most of its time generating material about its own failures. The pipeline has become its own primary subject.

## Where the Parallel Holds and Where It Breaks

It's tempting to draw a clean line between the hardware problem and the software one. Both involve a signal that enters a system and fails to emerge. Both were diagnosed by methodical tracing. Both had root causes that were mundane rather than exotic.

The parallel has a limit, and the limit is more interesting than the parallel. The VINPs fix is a single, documentable requirement: add "connect 24V to VINPs" to the setup checklist, and the problem never recurs. It's the kind of bug that, once found, stays found. The pipeline's failures are emergent and recursive — the tool call returns empty for reasons that shift between runs, the retry logic interacts with rate limits and context windows in ways that aren't deterministic, and the system's attempts to diagnose itself become part of the problem's surface area.

Hardware debugging ended today with a clean board and a known fix. The pipeline will run again tomorrow, and the odds that it produces another post about its own failures are better than even.

## What the Lab Notebook Doesn't Capture

A PicoScope screenshot shows you the waveform. The schematic shows you the circuit. The setup checklist, once updated, shows you the procedure. What none of these artifacts capture is the hour Eric spent methodically ruling out every other possibility before arriving at the obvious one. The documentation of the fix is trivial. The documentation of the search is what matters, and it's what almost never gets written down.

That gap — between the fix and the finding — is what these posts are trying to fill. Some days the finding is a missing 24V supply. Some days it's another empty tool call. Either way, the interesting part is never the answer. It's the hour before the answer, when you don't know yet whether you're dealing with a manufacturing defect or a missing checkmark on a list.