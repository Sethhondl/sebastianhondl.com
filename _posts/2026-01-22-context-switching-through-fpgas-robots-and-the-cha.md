---
layout: post
title: "Context-Switching Through FPGAs, Robots, and the Chaos of a Real Engineering Day"
date: 2026-01-22
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 3
word_count: 767
---

Seventeen browser tabs stared back at me this morning: four Xilinx forum threads, the RoboDK Python API reference, a Stack Overflow question about git merge history, and documentation for a MATLAB tool I'm building. Each tab represented a different engineering discipline, a different mental model, a different set of assumptions. Welcome to a typical Tuesday.

## The Missing Header File Mystery

The day began with a classic embedded systems puzzle. I was building the AMDC (Advanced Motor Drive Controller) firmware in Xilinx SDK when the compiler delivered this unwelcoming message:

```
fatal error: xparameters.h: No such file or directory
```

For anyone unfamiliar with Xilinx toolchains, `xparameters.h` is an auto-generated file containing all the hardware configuration parameters for your FPGA design. It bridges your hardware (defined in Vivado) and your software (running on the ARM cores).

The frustrating part? This system had worked days ago. A simple blink program ran fine. So what changed?

I had pulled new code from git.

Methodically tracing through the project structure revealed the culprit: the Board Support Package (BSP) directories referenced in the project files didn't exist in the repository. They're generated artifacts, not checked-in code.

Understanding the Xilinx build pipeline made the fix obvious:

1. Block diagrams (.bd files) define the hardware
2. Vivado synthesizes and exports a hardware definition (.xsa/.hdf)
3. The BSP is generated from that hardware definition
4. Only then can you build software that references `xparameters.h`

After pulling new code, the BSP needed regeneration—right-click the BSP project, select "Re-generate BSP Sources," wait for the rebuild. This gotcha catches everyone at least once when working with Zynq-based systems.

## The DONE Pin Saga

With one fire extinguished, another flared up:

```
FPGA Configuration: DONE pin is not high on target FPGA.
Do you still want to continue launching the application?
```

The DONE pin is a physical signal on the FPGA chip that goes high only after the configuration bitstream has been fully loaded. If it stays low, something went wrong during programming—corrupted bitstream, connection issues, or power problems.

The answer to that prompt is almost always no. If DONE isn't high, the FPGA fabric hasn't been configured. Running your application would be like executing software on a computer that hasn't finished booting—the hardware your code expects simply doesn't exist yet.

This understanding pointed me toward checking bitstream generation and the JTAG connection rather than chasing phantom software bugs.

## A Brief Detour Into Robot Simulation

With the FPGA sorted, I switched gears entirely: setting up RoboDK simulations for a robotics course. The goal was writing a Python script to make a robot trace a cube.

The RoboDK Python interface uses `robolink` to connect to the application and `robomath` for transformation matrices. Items in the simulation—robots, reference frames, tools—are represented by Item objects manipulated through method calls.

I got as far as understanding the architecture and setting up a dedicated subdirectory for experiments. Actual robot motion waits for tomorrow. Sometimes the first session with a new tool is purely about orientation, and that's fine.

## Building Better Tools

Between debugging sessions, I worked on my MATLAB-based AI assistant tool. Two threads are in progress.

First, I'm adding a safety checkbox for bypass mode. This mode removes all safety restrictions—no approval prompts, dangerous functions allowed. Powerful but risky. The planned implementation requires users to explicitly enable bypass mode cycling in settings, with a warning dialog explaining the consequences. The UI is designed; wiring it up comes next.

Second, I've been brainstorming names. When you've called something by its technical description for weeks, finding a real name matters. Options like Forge, Lumen, and Nexus capture different aspects—building solutions, illuminating problems, connecting AI to engineering workflows. No decision yet.

## What Stuck With Me

Working across such different domains reinforced one lesson: when things break after a git pull, missing generated files should top your debugging checklist. "No such file or directory" sounds definitive, but the real issue lived upstream in the build pipeline. The error message described a symptom, not a cause.

I also confirmed something I keep relearning: methodically searching the codebase, reading relevant files, and tracing dependencies beats random grepping and hoping. It's not glamorous, but it works.

Tomorrow I'll continue the voltage source inverter tutorial and hopefully get actual robot motion happening in RoboDK. Today was about laying groundwork—understanding why the BSP needed regeneration, why the DONE pin matters, how RoboDK structures its API. That foundation work makes the dramatic features possible later. And sometimes, seventeen browser tabs is exactly the right number.