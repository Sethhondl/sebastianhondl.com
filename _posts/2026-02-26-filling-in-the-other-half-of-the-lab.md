---
layout: post
title: "Filling In the Other Half of the Lab"
date: 2026-02-26
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 4
word_count: 922
---

A robot lab has a script problem and a paperwork problem. The script tells the robot what to do. The paperwork tells the student what to do when the robot doesn't. I spent yesterday writing the assembly sequence — gripper commands, chuck timing, placeholder coordinates — and assumed the remaining files were filler. Three documents later, I'd learned that the scaffolding around the logic matters as much as the logic itself.

## The Report Template That Became a Specification

The last file I wrote was supposed to be the easiest. A report template: section headers, formatting guidelines, placeholder text where data goes. Busywork.

Then I opened the rubric.

The grading criteria listed fourteen specific items. Not vague ones like "discuss results" — concrete ones. Record the joint angles for each waypoint. Compare the planned approach heights to the actual clearances. Document any gripper failures and the recovery sequence used. Explain why you chose `INSTRUCTION_CALL_PROGRAM` versus `INSTRUCTION_INSERT_CODE` for each subroutine call.

I started mapping rubric items to template sections, and the template stopped being a formatting exercise. Each rubric line became an `[INSERT]` placeholder at a specific location in the document. "Record the joint angles for each waypoint" became a table with rows for every named position in the assembly script, each cell reading `[INSERT: joint angles from teach pendant]`. "Document any gripper failures" became a subsection with a pre-built table: failure description, step number, recovery action, time lost.

By the time I finished, the template was a specification for what data to collect during the lab. Not "write a report afterward" but "fill in these blanks while you're standing at the robot." The rubric items weren't post-lab writing prompts. They were data collection requirements that happened to also be grading criteria.

I'd built report templates before and they'd always been structural — here's where the introduction goes, here's where the conclusion goes. This one was functional. A lab partner who'd never read the assembly script could pick up the template, see `[INSERT: approach height for chuck station]`, and know exactly what to measure. The template was doing work I'd assumed only the walkthrough could do.

## A Walkthrough Organized by When Things Break

The walkthrough started as a chronological procedure: step 1, step 2, step 3. Then I realized the interesting question wasn't "what do you do at each step" but "what goes wrong at each step and how do you tell."

The gripper not fully closing on the flashlight body is a step-2 problem. You catch it visually — the body wobbles during the lift. The fix is a gripper force adjustment. But the chuck not engaging fully is a step-4 problem that you don't catch until step 6, when the threading operation fails because the body has shifted. By then you've wasted three steps of robot time and need to back up to the chuck station.

Organizing failures by when they *surface* rather than when they *occur* turned the walkthrough into a debugging timeline. A student hitting a threading failure at step 6 can scan backward to find "threading failure: usually caused by incomplete chuck engagement at step 4" without needing to understand the full causal chain first.

## Helper Functions and the Mistake the Test Harness Caught

The helper script was the most technical file. The UR5 programming environment uses a Python API where you define functions that get loaded onto the robot controller. The functions are modular in source — separate definitions, clean interfaces — but they get flattened into a single program at build time. The robot doesn't have an import system. It has a text concatenation step.

This creates a practical problem: how do you test a helper function when the test environment is a 50-pound robot arm? The answer was a separate file that imports the same functions and calls them with mock positions and simulated I/O. Not a test harness in the pytest sense — no assertions, no CI pipeline. Just a script that lets you see "calling `open_gripper()` sets pin 4 high and pin 5 low" without the gripper actually moving.

I'd originally written one of the subroutine calls using `INSTRUCTION_CALL_PROGRAM`, which loads a subprogram and runs it as a separate execution context. The robot pauses the main program, runs the subprogram, and returns. Clean and modular. But the helper function needed access to variables defined in the main program — specifically, the settle times and pin assignments. A called program can't see the caller's variables. I needed `INSTRUCTION_INSERT_CODE`, which pastes the subroutine inline, sharing the caller's variable scope. Same Python API. Same function signature. Completely different execution model on the controller.

The test harness caught this immediately — the called-program version couldn't resolve the pin constants. Standing at the robot, this would have been a five-minute mystery ending in a TA visit.

## Specification Before Implementation

Yesterday I separated logic from coordinates. The assembly script captured *what the robot should do* without encoding *where things physically are*. Today I ended up separating something different: the specification of the lab from the implementation of the lab.

The report template specifies what data to collect. The walkthrough specifies what failures to watch for. The helper script specifies how subroutines interact with the main program. The assembly sequence specifies the logic. Four files, four different kinds of specification, all written before the robot moves.

The coordinates are still `0.0`. The settle times are still estimates. But the spec is complete. Next week, the lab becomes fill-in-the-blank.