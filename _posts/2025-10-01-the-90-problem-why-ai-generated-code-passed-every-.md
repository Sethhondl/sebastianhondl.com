---
layout: post
title: "The 90% Problem: Why AI-Generated Code Passed Every Check Except Understanding"
date: 2025-10-01
categories: [development, ai]
tags: [claude-code, automation, testing, debugging]
read_time: 5
word_count: 1097
---

> "The TAs and I noticed you are using AI to generate your lab reports... There has been a lot of incorrect and confusing material in your lab submissions. For example, postlab 2 with your error analysis, I'm not sure where this came from."

That email from Professor Humann arrived while I was in the middle of yet another Claude Code session, asking the AI to generate MATLAB scripts for my Feedback Control Systems homework.

The timing was brutal. These are core courses in my mechanical engineering program—Feedback Control Systems, Motion Control, Advanced Mechanisms. Failing to demonstrate competence here doesn't just mean a bad grade. It means graduating without actually understanding the material I'll need as a working engineer.

## What I Thought I Was Doing Right

I had been diligent about transparency. Every submission included an AI disclaimer. I cited Claude Code as a tool. I thought disclosure was the ethical obligation, and I was meeting it.

The output impressed me too. Claude generated clean HTML reports with MathJax rendering. It derived transfer functions for PD, PI, and PID controllers. It produced C++ code for IIR filters running on embedded hardware. The work looked professional—better formatted than anything I'd submit by hand.

Here's a sample from my Motion Control pre-lab:

```cpp
// First Order IIR Filter
// y(n) = 0.832448·y(n-1) + 0.167552·x(n)
double A = 0.832448;
double B = 0.167552;
double y_prev = 0.0;

// In the main loop:
double x_n = (adc_value / 65535.0) * 20.0 - 10.0;  // Convert to voltage
double y_n = A * y_prev + B * x_n;
y_prev = y_n;
```

The filter coefficients are mathematically correct for a 20 Hz cutoff at 750 Hz sampling. The code compiles. The math checks out.

But the lab provided a specific template with predefined function signatures and a particular structure for interacting with the Sensoray 826 board. My submission ignored all of it. I didn't use the template because I didn't realize it existed—I'd asked Claude to generate a solution from the lab description without carefully reading what infrastructure was already provided.

## What Actually Went Wrong

The errors fell into categories I couldn't see because I hadn't done the underlying work.

**Missing context.** In the Feedback Control homework, I asked Claude to derive transfer functions from block diagrams. Problems B.3 and B.4 came back wrong—I had to return later and ask Claude to fix them. The issue was a misread of the feedback path topology. If I had traced through the block diagram by hand first, I would have caught this in seconds. Instead, I accepted output I couldn't verify.

**Wrong abstraction level.** The Motion Control load cell code "wasn't anything close to what was expected," according to my professor. Claude generated a technically valid approach to reading a load cell, but the lab wanted us to use specific library functions and follow a particular signal flow. The AI optimized for correctness in a vacuum. The assignment required correctness within a constrained framework.

**Plausible nonsense.** The error analysis my professor mentioned? I still don't know exactly what went wrong. Claude generated statistical formulas and uncertainty propagation that looked reasonable. But "looked reasonable" isn't the same as "matched the methodology taught in class." I couldn't catch the error because I didn't know what correct looked like.

## Why AI Couldn't Catch This

AI tools like Claude excel at generation. Given a problem description, they produce syntactically valid, often mathematically sound output. But validation requires context they don't have:

- What template did the instructor provide?
- What methodology was taught in lecture?
- What does "correct" mean for this specific assignment?
- What level of explanation demonstrates understanding versus parroting?

This is the 90% problem. Claude got me most of the way to a complete assignment. The last 10%—verifying against instructor expectations, checking that my approach matched the taught methodology, ensuring I actually understood what I submitted—required judgment I hadn't developed because I'd outsourced the foundational work.

That 10% is where learning happens. It's also where grades get assigned.

## The Uncomfortable Part

With Claude's help, I drafted a response to my professor:

> "Moving forward from Prelab 4 onward, I will complete all lab reports, code, and calculations entirely on my own without AI assistance. I will follow the lab instructions more carefully and make sure my submissions align with what is expected."

Yes, I used AI to help write an apology email about over-using AI. I noticed the irony when I was doing it. I did it anyway.

That choice reveals something I'm still working through. The habit of reaching for AI assistance is deeply ingrained now. Even when composing a two-paragraph email, my instinct was to ask for help with phrasing. That instinct is exactly what my professor's email was pushing back against—not the tool itself, but the dependency that prevents me from developing my own competence.

## What I'm Actually Changing

Intentions are cheap. Here's the concrete workflow I'm implementing:

1. **Hand-first for new concepts.** Before asking Claude anything about a problem, I work through it on paper. Derive the transfer function. Trace the block diagram. Write pseudocode for the algorithm. This creates the mental model I need to evaluate AI output.

2. **Template audit.** Before generating any code, I read all provided materials and identify what infrastructure already exists. Function signatures, expected file structure, required library functions—all documented before I write a single line.

3. **AI for debugging, not drafting.** Once I have my own solution—even a broken one—I can use AI to help identify specific errors. "Why does this integral wind up?" is a different question than "Write me a PID controller."

4. **Explain before submitting.** If I can't explain every line without referring back to Claude's output, it doesn't go in.

## What Happens Next

I don't know if this approach will work.

The habits are strong. The pressure is real—these are difficult courses with significant workloads, and AI makes the impossible feel manageable. There's a reason I reached for these tools in the first place.

Professor Humann hasn't responded yet. There may be consequences beyond the warning.

What I do know is that I've been optimizing for the wrong metric. Completed assignments aren't the goal. Understanding is. And understanding doesn't come from reading AI output—it comes from the struggle I've been avoiding.

The remaining assignments won't be as polished. But they'll be mine, and I'll be able to defend every line.

That uncertainty feels more honest than anything I've submitted this semester.