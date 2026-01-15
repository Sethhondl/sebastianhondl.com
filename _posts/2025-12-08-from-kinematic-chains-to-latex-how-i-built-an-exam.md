---
layout: post
title: "From Kinematic Chains to LaTeX: How I Built an Exam Cheat Sheet with Claude Code"
date: 2025-12-08
categories: [development, ai]
tags: [claude-code, testing, debugging, refactoring]
read_time: 4
word_count: 941
---

There's a particular kind of panic that sets in when you're staring down a mechanical engineering final covering everything from radiation heat transfer to PID controller tuning—and all your knowledge needs to fit on a single side of paper.

My solution: point Claude Code at my project documentation and let it do the compression.

## The Challenge: Too Much Knowledge, Too Little Paper

The exam topics read like a greatest hits album of mechanical engineering:

- Heat transfer and radiation with view factors
- Rotational dynamics (torque, kinetic energy, moment of inertia)
- Transfer functions, poles, zeros, and Bode plots
- PI/PID controller tuning and stability analysis
- Magnetic bearing systems and dynamic stiffness
- Kinematic chain analysis for the flywheel rotor assembly

All of this had to fit on one side of one sheet. The constraint wasn't just space—it was *useful* space. A cheat sheet crammed with formulas you can't find under pressure is worse than no cheat sheet at all.

## The Approach: Mine the Project Report

Rather than starting from scratch, I pointed Claude at my existing project documentation. The `CLAUDE.md` file in my course repository already contained the essential specifications: baseline system parameters, thermal model equations, state of charge definitions, and controller gains.

The key insight was treating this as a data extraction problem rather than a content creation problem. All the formulas already existed—they just needed reorganizing for quick reference.

Here's the prompt I used:

```
I need to create a one-page cheat sheet for my ME final exam. 
The CLAUDE.md file in this repo has all the key formulas and 
system parameters from my flywheel energy storage project. 
Extract the most important equations and generate an HTML file 
optimized for printing with Chrome headless—three columns, 
8pt font, minimal margins. Group related concepts together.
```

Claude's first draft was too verbose. My follow-up:

```
Strip out all prose—just formulas, variable definitions, and 
the "gotcha" notes about common mistakes. Also, the thermal 
radiation section is missing the view factor formula.
```

That second pass got much closer. The source documentation had formulas with full explanations:

```markdown
## Thermal Model
- Rotor emissivity: 0.4 (LOW - limits heat dissipation!)
- Housing emissivity: 0.9
- Two-surface radiation formula:
  Q = σ × A_rotor × (T_rotor⁴ - T_housing⁴) / F_rad
```

Claude compressed this into three tight lines with the formula and a bolded warning about low rotor emissivity being a design limitation.

## Why HTML Instead of LaTeX?

I considered LaTeX initially—it's the standard for academic documents. But for a cheat sheet, HTML with CSS offered practical advantages:

1. **Faster iteration.** Tweaking column widths in CSS takes seconds; debugging LaTeX layout issues takes longer.
2. **Precise margin control.** Chrome's headless print-to-PDF respects CSS `@page` rules exactly.
3. **No dependency headaches.** HTML works everywhere; LaTeX requires a full TeX distribution.

The CSS that made the density possible:

```css
@page {
  size: letter;
  margin: 0.25in;
}

body {
  font-size: 8pt;
  line-height: 1.2;
  column-count: 3;
}
```

And the command to generate the final PDF:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --print-to-pdf=cheatsheet.pdf --no-margins cheatsheet.html
```

## The Real Value: Context Preservation

What struck me most was how Claude navigated the project context. The `CLAUDE.md` file wasn't just formulas—it contained notes about common mistakes and derived values that wouldn't be obvious from raw specifications.

These annotations made it into the cheat sheet. For example, the state of charge calculation includes a non-obvious gotcha: 50% SoC corresponds to ~34,641 RPM, not 30,000 RPM as you might naively expect from linear interpolation. Why? Because kinetic energy scales with ω² (E = ½Iω²), so state of charge isn't linear with RPM—it's quadratic.

That kind of contextual knowledge is exactly what you need when your brain is running at half capacity from exam stress.

## What Actually Worked

I used the cheat sheet this morning. The three-column density worked well for scanning—related concepts were grouped together, so I could find formulas quickly. The 8pt font was readable but definitely at the lower limit.

The most valuable part turned out to be the gotcha notes. During one problem, I almost used absolute amperes instead of per-unit current in the motor efficiency function—exactly the mistake the cheat sheet warned against in bold.

## Practical Takeaways

**Structure documentation for reuse.** The `CLAUDE.md` file wasn't created for cheat sheet generation—it was created to help Claude understand the project during development. Well-structured documentation serves multiple purposes.

**Specify output constraints early.** Telling Claude "HTML with minimal margins, print via Chrome headless" upfront shaped the entire output.

**Let AI compress, not create.** Asking Claude to reorganize verified content is safer than asking it to generate technical formulas from memory. One caveat: errors in your source docs will propagate faithfully.

**Include the gotchas.** A cheat sheet that just lists equations is barely better than a textbook. Notes about common mistakes are what actually save you during the exam.

**Iterate on density.** My first pass was too verbose by about 40%. Don't expect the first output to be print-ready.

## The Documentation Payoff

There's something fitting about using AI to prepare for an exam on control systems. The flywheel project itself was about modeling complex systems with feedback loops—and that's exactly what happened when iterating on this cheat sheet. Each pass refined the output, rejecting what didn't fit, amplifying what mattered.

But the bigger lesson isn't about AI or control theory. The `CLAUDE.md` file I wrote to help Claude understand my project during development became exam prep material weeks later. Write documentation once for understanding; reuse it for everything else.