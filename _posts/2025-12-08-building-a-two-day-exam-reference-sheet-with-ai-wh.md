---
layout: post
title: "Building a Two-Day Exam Reference Sheet with AI: When Dense Physics Meets Dense PDF"
date: 2025-12-08
categories: [development, ai]
tags: [claude-code, git, automation, testing, debugging]
read_time: 6
word_count: 1387
---

The realization hit at 2:47 PM on a Tuesday: I had two days to compress an entire semester of thermal systems, power electronics, and active magnetic bearing theory onto twenty printable pages. Past attempts at cramming had failed me before—twice I'd walked into exams with "reference sheets" that were really just anxiety printed on paper, too dense to parse under time pressure.

This time would be different. I had Claude Code, and I had a plan: generate HTML, print to PDF via Chrome's headless mode, and iterate until the reference sheet was actually *useful*. What I didn't expect was how much I'd learn about the material itself in the process.

## Why HTML and Chrome Headless?

Word processors fight you on dense layouts. LaTeX requires debugging compilation errors when you should be studying. HTML with CSS Grid, on the other hand, lets you specify exactly what you want: three columns, 6pt fonts, precise margins down to the millimeter.

Chrome's headless mode renders this HTML to PDF identically to how it appears in the browser. The command looks like this:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu --print-to-pdf="reference.pdf" \
  --no-margins reference.html
```

On Windows or Linux, the path changes, but the flags remain the same. The `--no-margins` flag is crucial—you're managing whitespace in CSS, not fighting the browser's defaults.

This setup gave me a tight feedback loop: edit HTML, regenerate PDF, check density, repeat. Claude Code could propose layout changes and I could see results in seconds.

## The State of Charge Deep Dive

The battery management section almost broke me. State of Charge (SoC) estimation sounds simple—track how much energy goes in and out, like monitoring a gas tank. But batteries aren't gas tanks. Their capacity varies with temperature, age, and discharge rate.

The insight that finally clicked: SoC relates to energy through a *quadratic* relationship, not linear. A battery at 50% SoC doesn't have 50% of its energy remaining—it depends on the voltage curve, which drops nonlinearly as charge depletes. The formula that captures this:

$$E_{remaining} = \int_{SoC}^{100\%} V(s) \cdot Q_{max} \, ds$$

Claude helped me trace through why the course emphasized Coulomb counting alongside voltage-based estimation. Neither method works alone. Coulomb counting drifts over time (you're integrating current, and small measurement errors accumulate). Voltage-based methods fail during transients when the battery isn't at equilibrium. The hybrid approach cross-references both—exactly the kind of redundancy you'd want in a system where wrong estimates mean stranded vehicles or damaged cells.

This section of my reference sheet went through three iterations. The first was a formula dump. The second added context but was too wordy. The final version had four equations, one diagram, and two sentences explaining when each estimation method fails.

## Thermal Analysis: Making Emissivity Practical

The thermal section nearly drowned in Greek letters. Emissivity (ε), Stefan-Boltzmann constant (σ), convective heat transfer coefficient (h)—every surface and every mode of heat transfer wanted its own symbol.

Here's what "low emissivity" actually means: a surface that's bad at radiating heat. Polished aluminum has ε ≈ 0.05, meaning it only emits 5% as much thermal radiation as an ideal blackbody at the same temperature. This matters when you're designing heat sinks. A bare aluminum surface relies almost entirely on convection because radiation contributes almost nothing.

On my reference sheet, I grouped formulas by *what question they answer*:
- "How fast is heat leaving this surface?" → Convection and radiation equations
- "What's the steady-state temperature?" → Thermal resistance network
- "How long until this reaches dangerous temperature?" → Transient analysis with time constants

This organization emerged from trying to use my first draft during practice problems. I'd stare at the sheet knowing the formula was *somewhere*, but the alphabet soup of subscripts made scanning impossible. The reorganization added ten minutes to my prep time but probably saved thirty minutes during the actual exam.

## The AMB Debugging Story

Active Magnetic Bearings (AMB) were the exam's wildcard topic—only two lectures, but explicitly "fair game" according to the syllabus. The core concept: suspend a rotating shaft using electromagnets, no physical contact, adjust current in real-time to counteract disturbances.

While building practice problems, Claude and I traced through a controller derivation where the linearized force equation kept producing unstable simulations. The issue turned out to be a sign error in how the magnetic force relates to air gap displacement.

For a magnetic bearing, force increases as the air gap *decreases* (magnet gets closer to the shaft). This means:

$$\frac{\partial F}{\partial x} > 0$$

A positive perturbation in position (shaft moves toward magnet) creates a *larger* attractive force, pulling it further toward the magnet. This is inherently unstable—the "negative stiffness" that makes AMBs require active control.

My initial derivation had flipped this sign, modeling a stable equilibrium that doesn't exist. The simulation ran fine but produced nonsense results. When I corrected the sign, the system showed the expected unstable pole that feedback control must stabilize.

This exact sign convention appeared on the exam. The question asked students to identify whether a given linearized model was correct—and the error they planted was precisely the one I'd debugged a week earlier.

## The Iteration Grind

Getting the layout right took longer than expected. Three columns in CSS Grid sounds straightforward until you're dealing with equations that refuse to wrap cleanly. Some findings:

- 6pt font is readable on printed output but brutal on screen. I developed my sheet at 12pt, then scaled down only for final PDFs.
- Multi-line equations need explicit column breaks or they'll span gutters and become unreadable.
- Page breaks in Chrome's print mode follow CSS rules, but not always predictably. I eventually added explicit `page-break-before: always` tags to section headers.

The information overload problem was real. My first draft had *everything*—every formula from every lecture, every edge case from every homework problem. It was twenty-three pages of unusable density.

The second draft cut content aggressively. If a formula required more than ten seconds to locate, it didn't belong on a reference sheet. If a derivation was "nice to know" but not "need to solve problems," it got cut.

The final version was eighteen pages. Three-column layout throughout. Section headers in bold 8pt. Critical formulas boxed. Worked examples in the margins where space allowed.

## Three Takeaways for Future Reference Sheets

**Organize by question, not by topic.** "Chapter 4: Thermal Analysis" is useless under time pressure. "How do I calculate steady-state temperature?" gets you to the right formula in seconds.

**Build your sheet iteratively, with practice problems.** Every time you can't find something, that's a signal to reorganize. The sheet should be optimized for *retrieval*, not *coverage*.

**Use the preparation as studying.** I learned more about SoC estimation while deciding which formulas to include than I did reading the original lecture notes. The act of compressing forces you to identify what matters.

## The Exam Itself

Ninety minutes. Four problems. Two of them—the SoC estimation question and the AMB stability analysis—mapped directly to sections I'd iterated on heavily while building the sheet.

There's a moment during an exam when you flip to your reference sheet, find exactly the formula you need in under five seconds, and feel the time pressure ease slightly. Traditional studying never produced that feeling. I'd memorize formulas, forget them under stress, and waste precious minutes reconstructing derivations from first principles.

This time, I didn't need to memorize. The sheet was an extension of my understanding, organized the way I actually think about problems. The preparation wasn't separate from studying—it *was* the studying, just with a deliverable at the end.

The grade won't post for another week. But walking out of that exam, I already knew: the two days spent building that reference sheet taught me more than the two weeks of conventional review that preceded it.

---

This polished version:

1. **Opening hook**: Starts with the specific "2:47 PM" realization and immediately establishes stakes (two days, past failures)
2. **Smooth transitions**: Each section flows naturally to the next
3. **Strong conclusion**: Ends with a memorable moment (finding formulas in under 5 seconds) and a clear insight about preparation vs. studying
4. **Engaging title**: SEO-friendly with "AI" and specific enough to attract readers facing similar challenges
5. **Consistent tone**: Conversational throughout, technical but accessible
6. **Redundancy removed**: Consolidated repeated concepts
7. **Readability**: Varied sentence lengths, clear structure, actionable takeaways
