---
layout: post
title: "Writing Robot Code Before Touching the Robot"
date: 2026-02-25
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 4
word_count: 829
---

Today I wrote a complete assembly sequence for a flashlight — grip the body, insert the battery, thread the cap, test the switch — and every coordinate in the program is `0.0`. The logic is real. The positions are placeholders. And that's the point.

The hard part of programming a robot isn't telling it *where* to go. It's telling it *what to do when it gets there*, in what order, with what error handling, and what happens if a gripper command fails mid-sequence. The coordinates are a measurement you'll take in thirty seconds with a teach pendant. The sequencing logic is the thing you can't debug under time pressure with a TA waiting and a lab group watching.

## The Assignment

The task: program a UR5 collaborative robot arm — a six-axis industrial arm common in university labs — to assemble a flashlight using a Robotiq adaptive gripper and a pneumatic chuck. Pick up the body from a fixture, insert a battery, retrieve and thread the end cap, actuate the switch to test it. Each step demands coordinating the robot's position, gripper state, and chuck state in the right sequence with the right timing.

Four files needed to exist before the lab: a walkthrough document, a prelab helper script, the assembly sequence, and a report template. I focused almost all the real thinking on the assembly script. The rest is structural — useful, but not where the risk lives.

## The Assembly Script

Here's a simplified version of the pattern that repeats throughout:

```python
def open_gripper():
    """Open Robotiq gripper to release position."""
    robot.set_digital_out(GRIPPER_OPEN_PIN, True)
    robot.set_digital_out(GRIPPER_CLOSE_PIN, False)
    time.sleep(GRIPPER_SETTLE_TIME)

def close_chuck():
    """Engage pneumatic chuck to hold workpiece."""
    robot.set_digital_out(CHUCK_ENGAGE_PIN, True)
    time.sleep(CHUCK_SETTLE_TIME)

# Step 3: Place body in chuck for battery insertion
move_to(approach_chuck)         # 0.0, 0.0, 0.0 — placeholder
move_to(chuck_insert_position)  # 0.0, 0.0, 0.0 — placeholder
open_gripper()
move_to(approach_chuck)         # retreat before chuck engages
close_chuck()
```

That `move_to(chuck_insert_position)` with its zeroed-out coordinates is surrounded by real logic: approach from above so the gripper clears the fixture, open the gripper *before* retreating so the part stays in place, retreat *before* engaging the chuck so the gripper isn't trapped. Get that sequence wrong and you crush a part, jam the chuck, or drive the gripper into the fixture at speed. A gripper closing at the wrong moment isn't a failed test. It's a broken part, a snapped fixture, or a safety stop that kills your lab time.

The coordinate itself is just a number you'll record by jogging the robot into position and reading the display. The logic around it — what happens before, what happens after, what state every actuator needs to be in — is the actual work.

## Tests Before the Implementation Exists

This is test-driven development applied to physical hardware.

In TDD, you write a test that calls a function with expected inputs and asserts the output before the function exists. The test captures the *intent* — what should happen — and the implementation fills in the *how*. You're forced to think about interfaces, edge cases, and sequencing before you're deep in the details.

Writing robot code with placeholder coordinates works the same way. The script captures the intent — grip, insert, thread, test — and the teach pendant fills in the coordinates later. The difference is stakes. A failing software test gives you a red line in the terminal. A sequencing error on a robot gives you a physical collision.

In past labs, the groups that skipped pre-writing their sequences spent most of their time debugging *logic* errors while standing at the robot — discovering they'd forgotten a gripper-open command between steps or that the retreat path collided with a fixture. The coordinates took minutes. The logic debugging took the whole session.

Writing the sequence in advance means the lab becomes pure calibration: jog the robot to each position, record the coordinates, paste them in. If the logic is right, the program runs on the first try. If it's wrong, at least you're debugging one variable instead of two.

## What I Don't Know Yet

Every coordinate in this script is `0.0`. The gripper timing constants are estimates. The approach heights might need adjusting once I see the actual clearances. The program is complete and it cannot possibly run correctly.

Next week, I'll find out whether logic written at a desk holds up when a real robot arm is moving real parts at real speed. Some settle times will need tuning. Probably at least one approach path will need reworking because the physical setup doesn't match what I imagined.

But the sequencing — which step follows which, when the gripper opens, when the chuck engages, how the robot retreats before a tool change — that's done. The part of the problem I can solve without hardware is solved. The part that requires hardware will take thirty minutes instead of three hours, because the logic won't be competing with the geometry for debugging time.