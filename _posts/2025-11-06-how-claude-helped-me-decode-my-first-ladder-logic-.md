---
layout: post
title: "How Claude Helped Me Decode My First Ladder Logic Program"
date: 2025-11-06
categories: [development, ai]
tags: [claude-code, python, testing, debugging]
read_time: 5
word_count: 1054
---

I've implemented PID control in Python, MATLAB, and C++ more times than I can count. But ladder logic? That's a completely different visual language designed for electricians thinking about relay circuits, not control engineers thinking about differential equations. When my Motion Control Systems lab required me to modify an existing ladder logic program for PI control, I needed a translator between these two worlds.

The setup: Lab 8, PID position control of a DC servomotor, implemented entirely through ladder logic on a PLC. I'd never written ladder logic before, and the lab manual assumed I already knew my way around it.

## The Translation Problem

The prelab had gone well. I derived closed-loop transfer functions, calculated critical damping gains, and understood why a proportional-only controller would have steady-state error that a PI or PID controller could eliminate. But the actual lab? The manual handed me an existing ladder logic program and said "modify this to implement PI control."

I provided Claude with the 8-page lab PDF, my 3-page prelab derivations, and the existing .L5K ladder logic file from the course materials. Then I asked not for answers, but for mapping: explain how this ladder logic program is structured so I can modify it myself.

## What Ladder Logic Actually Looks Like

In any procedural language, PID control looks roughly like this:

```cpp
error = setpoint - actual_position;
integral += error * dt;
derivative = (error - prev_error) / dt;
output = Kp * error + Ki * integral + Kd * derivative;
```

Ladder logic looks nothing like this. It's a visual representation that reads like an electrical schematic:

```
     |                                                           |
--+--| |------------------[encoder_position SUB setpoint = error]--+--
  |  ENABLE                                                      |
  |                                                              |
--+--| |--+---[error MUL Kp = P_term]--+--[P_term ADD I_term = output]--+--
     RUN |                             |                               |
         +---[error MUL Ki = I_inc]----+                               |
         |                             |                               |
         +---[I_acc ADD I_inc = I_acc]-+--[I_acc assigned to I_term]---+
```

Each horizontal "rung" flows left to right. The symbols that look like `| |` are contacts—they check conditions, like whether a bit is true. The blocks in brackets are operations: subtraction, multiplication, addition. The entire program scans top to bottom continuously, like a PLC checking relay states dozens of times per second.

Claude's explanation mapped directly between representations. "This contact checks if the RUN bit is set—that's your enable condition. This SUB block computes setpoint minus encoder position—that's your error term. This sequence of MUL and ADD blocks? That's accumulating the integral."

## The Three-Rung Structure

The existing program had three main sections, and understanding this structure made modification straightforward:

**Initialization rung:** This configured the encoder resolution (4096 counts per revolution), set the motor voltage limits (±10V), established the sample rate (1ms), and zeroed the position counter. Missing any of these would cause mysterious failures—the motor might saturate, the position might wrap incorrectly, or the control loop might run at the wrong rate.

**Control law rung:** Where the actual computation happens. The original program only had proportional control: one MUL block computing `Kp * error`, feeding directly to the output. To add integral control, I needed to insert three elements: a MUL block for `Ki * error`, an ADD block to accumulate that increment into a running sum, and another ADD block to combine the P and I terms.

**Output rung:** Takes the computed control voltage and sends it to the analog output module that drives the motor amplifier, including saturation limits for the ±10V range.

## The Mental Shift That Made It Click

One mapping caught me off guard. In code, I'd write integral windup protection like this:

```cpp
if (abs(integral) > max_integral) {
    integral = sign(integral) * max_integral;
}
```

In ladder logic, there's no `if` statement. Instead, you use contacts as conditional gates. The anti-windup logic used a comparison block that set a bit if the integral exceeded the limit, and that bit controlled a contact that bypassed the accumulator.

Claude's explanation: "Think of the comparison block as a relay that trips when the integral gets too large. When it trips, current can't flow through the accumulator path anymore."

That electrical metaphor—current flow, not control flow—was the mental shift I needed.

## What Didn't Work

Not everything clicked immediately. Claude's first explanation of the encoder configuration was too abstract—it described quadrature encoding without mapping to the specific parameters in this PLC's function block. I had to ask follow-up questions: "What does the 'Counts per Revolution' field actually control? What happens if I set it wrong?"

The answer: the PLC uses that value to convert counts to engineering units. Set it wrong and your position feedback is scaled incorrectly—a setpoint of 1000 might command 900 or 1100 actual counts, and your steady-state error measurements become meaningless. That kind of specific, consequential detail only came out through back-and-forth.

## The Concrete Modification

Here's the actual change. The original proportional-only control law rung:

```
--[error MUL Kp = P_term]--[P_term copied to output]--
```

After understanding the structure, I modified it to:

```
--[error MUL Kp = P_term]--+--[P_term ADD I_term = output]--
                           |
--[error MUL Ki = I_inc]---+
                           |
--[I_acc ADD I_inc = I_acc]--[I_acc copied to I_term]--
```

Three new blocks, wired to feed the accumulated integral into the output summation. The derivative term for full PID would add two more blocks: a SUB to compute error change and a MUL for the Kd gain.

## Why Asking for Mapping Worked

If I'd asked Claude to "write ladder logic for PI control," I would have gotten something I couldn't debug when it inevitably didn't work with this specific PLC's function blocks and variable naming conventions. Instead, I asked how the existing code was structured, learned the paradigm, and made the modifications myself.

The more context I provided—prelab derivations, the lab PDF, the existing code—the better Claude could identify what I already understood (PID theory, controls math) and focus on what I didn't (ladder logic syntax, PLC scanning behavior, the electrical-metaphor mental model).

## What's Next

Tomorrow I'll run these trials on the physical hardware. The theory is solid, the procedure is clear, and I understand the ladder logic well enough to troubleshoot when something behaves unexpectedly. That's the difference between copying code and learning a paradigm: when the motor does something weird, I'll know which rung to check first.