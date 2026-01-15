---
layout: post
title: "How Claude Helped Me Learn PLC Ladder Logic in One Session"
date: 2025-11-17
categories: [development, ai]
tags: [claude-code, python, testing, api, debugging]
read_time: 4
word_count: 965
---

I'd never written a line of ladder logic in my life. With a prelab due for ME4231—a motion control course at the University of Minnesota—I had a choice: spend hours parsing dense documentation, or ask Claude to teach me by building working examples. I chose the latter, and in one session went from zero to designing traffic light controllers.

## The Assignment: Traffic Light Controllers

Lab 10 introduced ladder logic programming, the industrial standard for controlling everything from traffic lights to manufacturing equipment. The prelab required designing two ladder logic diagrams:

1. **Alternating red lights** for a four-way stop (2-second intervals)
2. **A full traffic signal controller** for a two-street intersection (60-second cycle)

Ladder logic has an interesting history. It was designed in the 1960s to replace physical relay panels in factories. Rather than inventing a new programming language that electricians would need to learn, engineers created a notation that visually mimics the relay ladder diagrams electricians already knew how to read. Each "rung" of the ladder represents a circuit path, with inputs on the left controlling outputs on the right—just like a schematic of relay contacts and coils.

## A Quick Primer on Notation

Before diving into the diagrams, here's the essential vocabulary: `[ ]` represents a contact (an input condition) and `( )` represents a coil (an output). A slash like `[/ ]` means "normally closed"—the contact is active when the condition is *not* true. Timers have both an instruction (which counts time) and "done bits" that fire when the timer finishes.

## What Claude Actually Built

Rather than just explaining concepts, Claude created a complete document with ASCII ladder logic diagrams. Here's the simpler one—alternating red lights:

```
|--[/T2]-------------------------------------------(T1)---|
|   NC Contact for Timer 2                    Timer 1    |
|   Comment: Start T1 when T2 is not running (2 s)       |

|--[T1]-------------------------------------------(T2)---|
|   Timer 1 Done bit                          Timer 2    |
|   Comment: Start T2 when T1 completes (2 s)            |

|--[/T1]-------------------------------------------(Y001)-|
|   NC Contact for Timer 1                    Red 1 OUT  |
|   Comment: Red 1 ON when T1 not timing                 |

|--[T1]-------------------------------------------(Y004)-|
|   Timer 1 Done bit                          Red 2 OUT  |
|   Comment: Red 2 ON when T1 timing/done                |
```

When I first approached this problem, I expected to need a state machine—a variable tracking which phase we're in, conditional logic checking that variable, maybe a counter. That's how I'd solve this in Python or C. But ladder logic's timer-reset pattern eliminates all of that machinery. Timer 1 starts when Timer 2 isn't running. Timer 2 starts when Timer 1 finishes. The red lights simply follow the timer states. Two timers resetting each other in an infinite loop—no state variables, no conditionals, no counters.

## The Traffic Signal: Scaling Up the Pattern

The second problem required orchestrating six outputs across a 60-second cycle. Claude's solution used four timers working in sequence:

```
|--[T3]-------------------------------------------(T4)---|
|   Timer 3 Done bit                          Timer 4    |
|   Comment: T4 starts when Union green ends (5 s)       |

|--[T4]-------------------------------------------(T1)---|
|   Timer 4 Done bit                          Timer 1    |
|   Comment: Restart cycle when T4 completes             |
```

Timer 4's completion triggers Timer 1 again, creating an infinite loop. The outputs use combinations of timer done bits and running states to achieve this:

| Phase | Duration | Washington Ave | Union Street |
|-------|----------|----------------|--------------|
| 1 | 0-35s | Green | Red |
| 2 | 35-40s | Yellow | Red |
| 3 | 40-55s | Red | Green |
| 4 | 55-60s | Red | Yellow |

Ten rungs plus an END rung—more complex than the two-timer design, but built on the exact same timer-triggering pattern.

## Tomorrow's Challenge: Real Hardware

This prelab prepares me for tomorrow's hands-on lab where I'll program actual CLICK Series Micro PLC hardware. The physical implementation introduces concerns that don't exist in simulation: wiring errors that could illuminate the wrong light, download verification to ensure the logic transferred correctly, and real-time observation of the 60-second cycle to catch timing bugs.

I can test the logic beforehand using plcsimulator.online, but that only validates the logic itself—not my ability to wire the physical connections correctly. Claude can design the logic and explain the concepts, but debugging a loose wire on terminal Y003 requires hands-on work.

## What Made This Approach Work

Claude excelled at translating an unfamiliar notation system into working examples I could reverse-engineer. A few specific tactics helped:

1. **Request examples at multiple difficulty levels.** The two-timer alternating lights gave me the mental model needed to understand the four-timer traffic signal. Jumping straight to the complex case would have been overwhelming.

2. **Ask for timing diagrams alongside the rungs.** Seeing which outputs are active during each timer phase made the logic click in a way that staring at contacts and coils alone wouldn't have.

3. **Include inline comments.** Ladder logic is dense. Plain-English explanations let me verify my understanding rung by rung.

## What Could Go Wrong

These designs assume ideal conditions. Timer drift could accumulate over thousands of cycles. Power interruption mid-cycle leaves recovery behavior undefined. A logic bug could activate conflicting lights with no safety interlock to prevent it.

For a lab exercise, these limitations are acceptable. For industrial deployment, they're exactly the edge cases that separate classroom examples from production systems.

## The Takeaway

Tomorrow I'll find out if my understanding translates to working hardware. But regardless of what happens at the terminal blocks, today proved something useful: when facing an unfamiliar notation system with a deadline, the fastest path to competence isn't reading documentation—it's building progressively complex examples and reverse-engineering how they work. Claude didn't just help me finish a prelab. It compressed what might have been hours of confusion into a single productive session.