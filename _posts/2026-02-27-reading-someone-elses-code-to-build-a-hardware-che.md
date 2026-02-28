---
layout: post
title: "Reading Someone Else's Code to Build a Hardware Checklist"
date: 2026-02-27
categories: [development, ai]
tags: [claude-code, automation, testing, debugging, refactoring]
read_time: 4
word_count: 926
---

The only specification for the hardware on my bench is the firmware that runs it. No schematic with part values annotated. No pinout diagram taped to the enclosure. No setup guide that says "connect the current sensor to ADC channel 3." The specification exists — it's just distributed across three source files written by someone who graduated two years ago.

This is a common situation in university research labs. Equipment outlives the students who built it. The documentation, if it ever existed, lives on a laptop that's been reformatted. What survives is the code, because the code had to work.

## Mining Three Files for a Hardware Spec

The AMDC platform — the same board where I've been [debugging Phase A's 20% gain error](/2026/02/23/a-hardware-puzzle-and-six-documents-in-parallel.html) — runs firmware organized into three layers. `machine_bp1.m` is the MATLAB configuration script that defines the physical system: which inverter legs map to which motor phases, which ADC channels read which sensors, what the scaling factors are. `task_cc.c` is the C control task that runs the current regulation loop: it reads ADC values, applies coordinate transforms, computes voltage commands, and writes them to the PWM registers. `inverter.c` sits below both, handling the power stage — dead time, switching frequency, hardware fault detection.

Each file encodes hardware facts as side effects of doing something else. `machine_bp1.m` doesn't say "Phase A current sensor is on ADC channel 3." It says `Iabc_channel_assignments = [3, 4, 5]` inside a function that configures the motor drive. `task_cc.c` doesn't say "the current sensing range is plus or minus 18.75 amps." It says `#define IMAX 18.75` inside a header block that also defines the control loop bandwidth. `inverter.c` doesn't say "the gate driver uses active-high enable logic." It says `set_gpio(INV_EN_PIN, 1)` inside the startup sequence.

None of these are documentation. All of them are specifications. The difference is that a specification written as documentation tells you what the hardware *should* be. A specification written as firmware tells you what the hardware *was* — at least on the day someone got it working.

## The REV E Problem

Halfway through extracting pin assignments from `machine_bp1.m`, I found a comment: `% REV E board configuration`. The board on my bench is labeled REV F.

This is exactly the kind of discrepancy that costs an afternoon. REV E and REV F share the same processor, the same ADC, the same power stage topology. But four GPIO assignments changed between revisions. The enable pin for inverter leg 1 moved from GPIO 12 to GPIO 18. Two of the ADC mux select lines swapped. A diagnostic LED moved from a active-low to active-high output.

The firmware compiles fine for either revision. The control loop doesn't care which GPIO pin it writes to — it writes to whatever `INV_EN_PIN` resolves to. But if `INV_EN_PIN` resolves to GPIO 12 and the hardware expects GPIO 18, the inverter doesn't enable. No fault, no error message. The motor just doesn't move, and you spend an hour probing pins before realizing the enable signal is going to the right register but the wrong physical pad.

I caught it because the comment was there. If it hadn't been — if someone had just defined `INV_EN_PIN = 12` without noting the board revision — the mismatch would have surfaced as a hardware debugging problem instead of a configuration problem. Thirty seconds of reading versus an hour of probing.

## From Code to Checklist

Scattered facts in source files are useful for someone who already understands the system. They're useless for someone standing at a bench with a multimeter trying to verify that a board works before running a control experiment.

So I reorganized. Every hardware fact I extracted went into a categorized checklist: ADC channel assignments, GPIO pin mappings, power stage parameters, timing constants, sensor scaling factors. Each entry traces back to a specific file and line number. `Phase A current → ADC ch 3 → machine_bp1.m:47` is something you can verify at the bench and something you can update if the code changes.

The categories aren't organized by source file — that would just reproduce the code's structure in a less useful format. They're organized by verification method. "Things you check with a multimeter" is one section. "Things you check with an oscilloscope" is another. "Things you check by reading registers" is a third. A student doing board bring-up works through the checklist in order, and each section uses one instrument before switching.

The REV E/REV F discrepancies got their own column. For each pin assignment that changed between revisions, the checklist shows both values and marks which one the current firmware expects. If someone flashes REV E firmware onto a REV F board — or vice versa — the mismatches are visible before power-up, not after.

## Code as Inadvertent Documentation

The useful realization isn't that code can substitute for documentation. It's that code that controls hardware *is* a hardware specification, whether anyone intended it to be. Every pin assignment, every scaling factor, every timing constant in the firmware corresponds to a physical fact about the board. The code has to be right or the hardware doesn't work. That makes it more reliable than a schematic PDF that might be two revisions out of date.

The checklist I built today is a translation layer. Same facts, different format, different audience. The firmware will keep encoding the spec implicitly. The checklist makes it explicit — and makes the REV E assumption visible to the next person who inherits this bench.