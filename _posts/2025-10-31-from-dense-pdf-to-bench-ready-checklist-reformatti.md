---
layout: post
title: "From Dense PDF to Bench-Ready Checklist: Reformatting a Motion Control Lab"
date: 2025-10-31
categories: [development, ai]
tags: [claude-code, git, automation, debugging, refactoring]
read_time: 3
word_count: 642
---

Eight pages of nested procedures, embedded equations, and figure references scattered across a lab PDF. One hand on an oscilloscope probe, the other scrolling to find "Step 3b." This is the reality of academic lab work—and exactly what I wanted to fix before walking into my servo motor characterization lab.

## The Problem with Academic PDFs

Lab 7 for my Motion Control class (ME4231) covers measuring torque constants, back-EMF coefficients, and friction parameters using a dynamometer setup. The documentation is thorough but designed for printing, not for quick reference while you're juggling equipment and trying to remember which motor terminal connects to which DAQ channel.

I wanted a stripped-down markdown checklist—just the procedures for the two main exercises, formatted for quick scanning.

```
Please write a document an md file to walk me through 
how to complete lab 7. This should just be for the lab 
procedure for those two exercises
```

## What Claude Actually Did

Before writing anything, Claude located the source materials in my project directory: the main lab PDF, my prelab submission, and supporting theory documentation. Then it parsed the PDF directly, extracting procedural content from the dense academic formatting.

The transformation was striking:

**Original PDF (paraphrased):**
> "For Exercise 1, students will characterize the torque constant by measuring armature current and output torque at multiple load points. Begin by ensuring the dynamometer brake is fully released, then apply 12V to the motor terminals while recording..."

**Generated walkthrough:**
```markdown
## Exercise 1: Torque Constant Measurement

### Setup
- [ ] Verify dynamometer brake fully released
- [ ] Connect motor terminals to 12V supply
- [ ] Attach current probe to armature lead

### Data Collection
- [ ] Apply brake incrementally (5 positions)
- [ ] At each position, record:
  - Armature current (A)
  - Torque reading (N·m)
  - Motor speed (RPM)
```

Same information, completely different usability.

## The Payoff at the Bench

Two things stood out when I used this walkthrough during the actual lab. The checkbox format let me track progress without losing my place—critical when the TA interrupts to check your setup. And having measurement parameters listed explicitly prevented the "wait, what was I supposed to record?" moment that costs five minutes of backtracking.

The friction characterization in Exercise 2 involves running the motor at multiple speeds and measuring deceleration curves. The original PDF describes this across three paragraphs with equation references. The walkthrough condensed it to six steps with the relevant equations pulled inline.

## A Note on Academic Integrity

I want to be direct: reformatting existing instructions is legitimate study support. The professor wrote the procedures. I reorganized them for usability—the same way I'd rewrite lecture notes by hand, except faster.

What would cross the line: asking Claude to interpret my torque-current data and explain what the slope means. That analysis is the learning. The walkthrough just reduces friction around following instructions.

## Why This Worked

**Colocated source files.** Claude found my prelab and theory documentation automatically because everything lived in the same directory.

**Explicit scope.** Asking for "just the lab procedure for those two exercises" prevented unnecessary background sections or theory reviews.

**PDF parsing capability.** This wouldn't have worked two years ago. Reading academic PDFs directly—with their multi-column layouts, embedded figures, and technical notation—makes Claude genuinely useful for STEM coursework.

## The Work That Remains

The walkthrough saved maybe twenty minutes of reformatting. The lab itself still required three hours of careful measurements and post-lab analysis where I calculate motor parameters from recorded values. Fitting lines to torque-current data, interpreting what friction coefficients mean physically—that's where learning happens.

The most practical AI assistance isn't generating novel content. It's eliminating friction between dense source materials and usable working documents, so more time goes toward the work that actually matters.