---
layout: post
title: "The Thirty-Second Edit That Made Me Question Everything"
date: 2025-09-25
categories: [development, ai]
tags: [claude-code, git, automation, testing, debugging]
read_time: 3
word_count: 784
---

I added a single paragraph to a LaTeX document today. The task took Claude Code about thirty seconds. But that small edit forced me to articulate something I'd been avoiding: what exactly is "legitimate" AI assistance in academic work—and where does my answer fall short?

## The Edit Itself

I was finishing a post-lab report for my ME4231 Motion Control class: RC circuit simulation using Euler's method, comparing numerical solutions against analytical results. Before submitting, I asked Claude to add an AI disclaimer.

Here's what got added:

```latex
\section*{AI Assistance Disclosure}
This report was prepared with assistance from Claude (Anthropic), 
an AI assistant. Claude was used for: explaining Euler's method 
derivation, debugging LaTeX formatting, and discussing error 
analysis between numerical and analytical solutions. All 
mathematical work was verified independently and the author can 
explain all concepts presented.
```

That last sentence is the claim I want to examine.

## My Working Framework (And Its Problems)

I've been operating under this heuristic: if AI helped me understand something I can now explain in my own words, that's legitimate assistance. If AI wrote something I couldn't reproduce or explain, that's a problem regardless of disclosure.

This sounds reasonable until you push on it.

When Claude helped me understand why the Euler method produces a 1.09% relative error at t=3s for the RC circuit, I learned something real. I can now explain that each Euler step assumes the derivative stays constant over the interval, but for an exponential approach to steady state, that derivative is continuously decreasing. The numerical method doesn't capture that change within each step, so it slightly overshoots.

But here's the uncomfortable question: would I have figured that out on my own, given enough time? Probably. Would I have invested that time without AI assistance? Almost certainly not. I would have accepted "numerical error accumulates" as sufficient understanding and moved on.

The AI didn't just help me understand—it raised my floor for what counts as understanding. Is that legitimate assistance, or is it creating a dependency on AI to push past my own intellectual laziness?

I don't have a clean answer.

## Why the Technical Details Matter

The simulation implements this recurrence relation:

```latex
V_C^{i+1} = V_C^i + \Delta t \cdot \frac{V_{DC} - V_C^i}{\tau}
```

This is Euler's forward method applied to a first-order ODE. The analytical solution is `V_C(t) = V_DC(1 - e^{-t/τ})`, and comparing the two reveals exactly where numerical approximation introduces error.

I'm including this not because it's particularly novel, but because it's where I have to ask myself: do I actually understand this, or do I just understand Claude's explanation of it?

I think I understand it. I can derive why the error grows over 30 time steps. I can explain why halving the step size would roughly halve the per-step error. But I'm also aware that I'm a biased judge of my own understanding. The disclaimer asserts a competence I can't fully verify in myself.

## What the Disclaimer Doesn't Capture

The disclaimer lists specific uses: "explaining Euler's method derivation, debugging LaTeX formatting, discussing error analysis." Accurate, but incomplete.

What it doesn't capture is how AI assistance changes the *texture* of doing the work. Without Claude, I would have spent more time staring at equations, making more mistakes, consulting the textbook more often. Some of that friction is unproductive. Some of it might be where actual learning happens.

I formatted the disclaimer as a clean list because that's what academic honesty policies seem to want. But AI collaboration is messier than that—it's not a tool you use for discrete tasks, it's an ongoing conversation that shapes how you approach the entire problem.

## One Practical Lesson

My initial request was vague. "Add an AI disclaimer" could mean anything—a footnote, a section, a sentence in the acknowledgments. Claude made reasonable choices, but I got lucky. For anything more complex, I'd want to specify location, tone, and scope upfront.

I've also started treating my Claude Code session transcripts as documentation. This motion control coursework spans 35 sessions now, and being able to trace back through that history helps me distinguish between "I learned this" and "Claude told me this and I wrote it down." The disclaimer format doesn't support that distinction, but it matters for my own intellectual honesty.

## Where This Leaves Me

I added a disclaimer that says I can explain everything in my report. I believe that's true. I also know that my standard for "can explain" has been calibrated in conversation with an AI that's very good at making explanations feel clear.

The disclaimer took thirty seconds to add. Figuring out what it should actually mean? That's ongoing.