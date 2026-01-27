---
layout: post
title: "How a Mislabeled Test Point Nearly Derailed My Debugging Session"
date: 2026-01-25
categories: [development, ai]
tags: [claude-code, git, automation, testing, api]
read_time: 4
word_count: 830
---

A mislabeled test point in documentation can cost you an afternoon. A misidentified component can cost you a board. When you're working with power electronics—where currents spike and MOSFETs fail spectacularly—the gap between "close enough" and "exactly right" isn't pedantic. It's the difference between a smooth debugging session and hours spent probing the wrong signal.

Today I learned this lesson firsthand while updating documentation for a uInverter board.

## The Setup

I'm working through a directed study involving the AMDC (Advanced Motor Drive Controller) platform, used for prototyping motor control systems. Part of this work involves documenting hardware components thoroughly—not just for my own reference, but for the graduate students and researchers who'll use these boards after me.

Issue #15 in our repository needed updates after a reviewer caught inaccuracies in my descriptions of integrated circuits and test points. Three errors in one issue body. None of them typos. All of them the kind of mistakes that would have sent someone measuring the wrong signal or misunderstanding the board's architecture.

If terms like PWM and gate drivers are unfamiliar, the specifics here may be dense, but the broader lesson about documentation precision applies universally.

## Three Errors, Three Different Lessons

The reviewer, @mhmokhtarabadi, identified three issues by cross-referencing my descriptions against the board schematics and their hands-on experience—exactly the verification I should have done more carefully myself.

**The easy fix: a broken link.** I replaced a dead datasheet URL with a working DigiKey product page. Nothing to learn here except to check your links.

**The conceptual error: mischaracterizing the half-bridge.** I had written that the gate driver IC converts PWM signals into high-current gate drive signals "for rapidly switching the power MOSFETs." The problem? The uInverter doesn't have separate power MOSFETs. The gate driver IC itself acts as the half-bridge, directly handling the switching rather than driving external transistors. This architectural detail affects how you think about the entire power stage.

**The dangerous error: test point misidentification.** I had described TP1A as the output from the current sense amplifier. It's actually the output from the gate driver, indicating phase voltage. The current sense output is TP3A.

This last one could have cost someone real time. Imagine tuning a current control loop while your oscilloscope probe is on a voltage signal. You'd see switching waveforms that look plausible but don't respond the way current should. You might spend an hour questioning your control gains before realizing you're measuring the wrong thing entirely.

## Making the Corrections

With the fixes identified, I needed to apply them cleanly. I could have edited the issue directly in GitHub's web interface, but the issue body was several hundred words with embedded links and formatting. Making surgical edits while tracking changes and avoiding new errors would have meant a lot of mental overhead.

Instead, Claude Code handled the mechanics. It fetched the full issue context using the GitHub CLI, created a structured plan documenting each change before execution, then applied the corrections precisely while preserving surrounding formatting.

The time savings weren't dramatic—maybe ten minutes. The real value was staying focused on whether the technical content was correct rather than on the mechanics of making edits.

## What This Taught Me About Documentation

**Describe what components do in this design, not what they typically do.** The IXDN614YI is marketed as a gate driver. In most applications, it drives external MOSFETs. In the uInverter, designers used it differently. Copying the datasheet description would have been technically accurate about the part but wrong about the system.

**Peer review catches what self-review misses.** I read my original descriptions multiple times. They seemed accurate because they matched my mental model—which was wrong. Someone with hands-on board experience comparing my documentation to actual schematics caught what I couldn't.

**Documentation is code that runs in human brains.** It needs debugging and testing just like software. The bugs that slip through are the ones where your assumptions don't match reality.

## The Division of Labor

This session clarified how I'll use AI tools for documentation tasks. The tedious parts—API calls, text manipulation, formatting preservation—were handled efficiently. But the part I expected to be straightforward—knowing what the correct technical content was—turned out to be where I made mistakes.

No AI could have caught that TP1A measures phase voltage rather than current sense output. That required a human reviewer with hardware expertise and the schematics in hand.

## Looking Ahead

The uInverter documentation is now accurate. Somewhere down the line, a graduate student will pick up this board for their motor control project. They'll probe TP1A expecting phase voltage, and they'll find it. They'll understand that the gate driver is the power stage. They won't lose an afternoon to my errors.

That student might be me in six months, having forgotten the details. Documentation is a message to your future self as much as to anyone else. Getting it right isn't optional—it's the whole point.