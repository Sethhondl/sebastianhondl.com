---
layout: post
title: "The Line Between Learning and Formatting: AI in Engineering Education"
date: 2025-11-13
categories: [development, ai]
tags: [claude-code, git, testing, debugging]
read_time: 5
word_count: 1088
---

"Can you make the prelab answers be in paragraphs of text?"

I was staring at a carefully structured markdown document full of equations, bullet points, and step-by-step procedures for my motion control lab. The content was solid—time constant identification methods, spacing error block diagrams, vehicle platoon dynamics. My answers were correct. But the format wasn't what was needed, and something about that request made me want to close my laptop and walk away.

Engineering students know this particular tedium well: you've done the hard work of understanding the concepts and getting the right answers. Then comes the reformatting request that has nothing to do with learning.

## The Hidden Complexity of "Simple" Reformatting

Here's what most people don't realize about reformatting technical content: it's not just moving words around. When you convert bullet points to prose, you need to maintain technical precision while adding transitional language, preserve the logical flow that the structure provided implicitly, ensure equations still make sense in context, and keep the content scannable even without visual hierarchy.

This is where Claude Code became genuinely useful. Rather than mechanically converting each bullet to a sentence, the AI understood the underlying technical concepts and could rewrite them as coherent paragraphs while preserving accuracy.

Take the time constant identification procedure. The original had clean, numbered steps:

```markdown
**Step 1: Apply a Step Input**
- Apply a step input to the desired acceleration (u_des)
- Use a magnitude that is within the vehicle's acceleration limits
- Recommended: Use a step input of 2 m/s² at t = 1 second
```

The paragraph version needed to flow naturally while keeping every piece of information intact:

> To identify the time constant, begin by applying a step input to the desired acceleration. The magnitude should stay within the vehicle's acceleration limits—a step input of 2 m/s² applied at t = 1 second works well for this purpose. Once the system responds, measure the time required for the actual acceleration to reach 63.2% of the commanded value, which corresponds to one time constant τ.

It's the difference between a recipe card and explaining a cooking technique to a friend. The information is identical, but the presentation requires understanding how the pieces connect.

That said, AI doesn't always get these transformations right. In one case, a reformatted paragraph swapped the order of two procedure steps in a way that would have produced incorrect results if followed literally. I caught it because I understood what the procedure was actually doing—which is precisely the point. You can't verify what you don't understand.

## A Note on Audience

This post assumes you know what a transfer function is, why time constants matter, and what it means when theoretical and experimental bandwidths diverge by orders of magnitude. If terms like "Bode plot" or "PID controller" are unfamiliar, the technical examples won't land. That's okay—the core argument about AI assistance applies broadly, but the specifics come from control systems coursework.

## Lab Reports: A Perfect AI Use Case

I've been working through a series of motion control labs this semester—PID controllers, frequency response analysis, vehicle platooning. A pattern has emerged across all of them. The technical work is challenging and requires genuine understanding. But a surprising amount of time goes into presentation: formatting MATLAB plots, structuring markdown documents, converting between answer formats.

Before using AI assistance, reformatting a prelab from bullets to prose meant reading each bullet, mentally constructing a sentence, typing it, checking that I hadn't dropped any technical details, then repeating for dozens of items. With AI, I paste the bulleted content, specify the target format, review the output for accuracy, and make corrections. The actual time difference on my Lab 9 prelab was closer to 25 minutes versus 5 minutes—substantial when multiplied across a semester of lab reports.

This is where AI assistance shines. Not because it does the thinking for you—you still need to understand why τ represents the time constant, and what happens when your theoretical predictions don't match experimental data. But because it handles the mechanical transformation tasks that consume time without building understanding.

## The Question Nobody Wants to Ask

Let me address what's actually on many students' minds: does this feel like cheating?

I've thought about this more than I'd like to admit. There's genuine anxiety around AI tools in academic settings, and it's not irrational. The line between "assistance" and "doing the work for you" isn't always obvious from the outside.

Here's where I've landed: the understanding has to be mine. The analysis has to be mine. When I look at experimental bandwidth results that don't match theoretical predictions, I need to be the one reasoning about why—model parameters that need refinement, actual system dynamics that differ from assumptions, nonlinearities the linear model ignores. AI can help me articulate those gaps clearly, but noticing them in the first place? That's the learning, and no tool can shortcut it.

The transformation from "here's what I know" to "here's that knowledge in the format you requested" is mechanical work. Outsourcing it doesn't skip the education. But if I couldn't explain what my own lab report means, I'd have outsourced too much.

## Working With the Limitations

One thing I've learned: verify everything. When AI reformats equations or procedures, technical accuracy doesn't always survive the transformation. A well-written paragraph that gets the physics wrong is worse than an ugly bullet list that's correct.

I also document my workflow explicitly. When I can articulate "I performed this analysis, derived these results, and used AI to help present them clearly," I'm confident in my approach. When I find myself unable to explain what the content actually means, that's a signal I've let the tool do work I should have done myself.

The line is clear even if it requires honesty to see it: asking AI to reformat your correct answers into paragraphs is different from asking it to derive the transfer function. The first accelerates presentation. The second skips learning.

## The Work That Actually Matters

Tomorrow I'll be back to vehicle motion control—transfer functions, spacing errors, and platoon dynamics. The AI will help me format the deliverables. But understanding why a first-order lag model captures vehicle acceleration dynamics, and what it means when my experimental results diverge from theory?

That's the work no formatting tool can do for me. And honestly, I wouldn't want it to. The struggle to understand is where the education actually happens. Everything else is just presentation.