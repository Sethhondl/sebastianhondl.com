---
layout: post
title: "Before You Can Spin a Motor, You Have to Trust Your Current Sensors"
date: 2026-03-25
categories: [development, ai]
tags: [claude-code, python, automation, testing, debugging]
read_time: 5
word_count: 1055
---

Six numbers sit hardcoded at the top of `task_controller.c` — gain and offset pairs for three current sensor channels. Someone measured them once, typed them in, and moved on. Those numbers are the entire basis for converting raw ADC counts into amperes. If they're wrong, every downstream calculation — every PI gain, every torque estimate, every protective current limit — is wrong too.

I'd been assuming those values were close enough. This week I stopped assuming.

## The Platform

We're building a motor drive research platform around a custom inverter board and the AMDC controller. The path forward is closed-loop current control, then torque, then speed. But none of that works until the firmware knows what current is actually flowing through each phase. And right now, there's no way to know whether it does without an independent measurement to compare against.

## The Calibration Approach

The procedure borrows from a reference in the AMDC documentation (labeled BP6 in the lab's internal numbering — "Bring-up Procedure 6," the current sensor calibration protocol). Apply known DC voltages across an RL load wired to one inverter phase, log the raw ADC readings at each voltage, measure the true current with an oscilloscope probe, and fit a line through the points. Three phases, three independent calibrations.

Getting DC voltage from a PWM inverter requires some care. The half-bridge output voltage is proportional to duty cycle: 0.5 means equal time high and low, so the average output is half the DC bus voltage — effectively zero net voltage across the load. To command a specific average voltage V, the duty cycle is `0.5 + V / V_dc`. Push above 0.5 to go positive, below to go negative. The firmware implements this as a calibration mode in the task controller. When active, it ignores normal current references and drives the requested DC voltage on the phase under test while holding the other phases at 50% duty.

## Why the Logging Details Matter

Three logging variables — `LOG_vadc_a`, `LOG_vadc_b`, `LOG_vadc_c` — capture the raw ADC readings for each phase. They come from `_get_Iabc`, which reads each ADC channel once and stores the result in a local variable used twice: once for logging and once for the control loop's current calculation.

This read-once-use-twice pattern is deliberate. The ADC values are sampled at a specific instant within the PWM cycle. Reading again would give a different sample at a different point in the switching period — and in a system switching at tens of kilohertz, even microseconds of skew between the logged value and the control value would mean you're not calibrating what you think you're calibrating.

The AMDC streams these values over Ethernet at the control loop rate of 10 kHz. Dense enough to average out noise, sparse enough to store comfortably for a multi-second voltage sweep.

## The Measurement Campaign

The Jupyter notebook workflow: command a DC voltage on one phase, wait for the current to settle through the RL load, log a few hundred ADC samples, read the true current from the oscilloscope, step to the next voltage, repeat. After sweeping five or six points per phase, `scipy.optimize.curve_fit` finds the best-fit line mapping ADC counts to amperes.

Three phases, three linear fits. Linearity wasn't assumed — it was confirmed. The residuals were small and evenly distributed. No polynomial correction needed, no lookup table. Just a gain and an offset per channel.

What I didn't expect: the offsets were significant. The hardcoded gains were within a few percent of the fitted values, but the offsets were off by enough to shift the zero-current reading by several hundred milliamps. In a system where the current limit might be 5A, a 300mA offset error is the difference between running normally and tripping a protection threshold for no reason. The old numbers weren't wildly wrong. They were wrong at the baseline where every other measurement starts — which is the worst place to be wrong.

## Two CLI Commands and a Safety Invariant

The calibration surfaces through two commands. `ctrl mode curcal` puts the task controller into calibration mode. `ctrl curcal <va> <vb> <vc>` sets the DC voltage for each phase.

A detail that matters: calibration mode resets to idle on deinit. If the task controller is deinitialized — intentionally or from a fault — it doesn't return to closed-loop control with stale references. It goes to idle. Zero duty on all phases. Open switches. No current. That safe state is explicit, not a side effect of whatever mode happened to be active before.

## Meanwhile, in the Pipeline

On the software side, the blog pipeline gained a meaningfulness gate this week. The problem: too many recent posts have been about the pipeline's own failures. The fix is a fast classifier that runs on raw transcript material before the four-pass generation starts. Under 200 characters, it's not meaningful — skip entirely, no expensive Claude calls. Above that threshold, the classifier makes a quick judgment and either proceeds or bails.

It's a heuristic, not a clean filter. The calibration work has ground truth — the linear fit either matches the oscilloscope or it doesn't. "Is this transcript worth a blog post?" has no equivalent. So the gate fails open: if the classifier can't decide, the post gets generated. A `--force` flag bypasses the check entirely. The goal is to catch obvious empties, not to make editorial judgments.

## The Prerequisite Chain

Both projects this week built infrastructure that exists only to enable the next step. The motor won't spin under closed-loop control until the current sensors are calibrated — not approximately, not with someone's old numbers, but with measured gains and offsets verified against an independent instrument. The blog won't stop publishing posts about itself until the pipeline can tell a real transcript from an empty one.

The parallel is real but imperfect, and the imperfection is the honest part. Calibration has a solution: three linear fits, six numbers, done. The meaningfulness problem is a heuristic bolted onto a system that lacks a clean definition of its own success criteria. One is physics. The other is judgment. But both had to be solved before anything downstream could work — and both were, until this week, living as "close enough" in someone's head.