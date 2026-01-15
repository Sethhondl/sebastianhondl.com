---
layout: post
title: "The Staircase Cosine: What a DAC Taught Me About Debugging"
date: 2025-10-09
categories: [development, ai]
tags: [claude-code, git, testing, debugging]
read_time: 3
word_count: 734
---

The oscilloscope trace looked wrong. I'd implemented a straightforward derivative filter, fed it a clean sine wave, and expected a smooth cosine shifted 90 degrees in phase. Instead, I was staring at something that looked like a staircase trying to impersonate a curve.

My first instinct was to check the code. Then the filter coefficients. Then the sampling rate. Everything checked out. The math was correct. The implementation was correct. So why did my "perfect cosine" look like it was built from LEGO bricks?

## The Hardware Constraint Nobody Mentioned

The answer wasn't in my code—it was in the hardware. The lab setup used a 12-bit digital-to-analog converter outputting at 750 Hz. For a 20 Hz signal, that means roughly 37 discrete voltage levels per cycle. Each "step" in my staircase was the DAC jumping to its next available output value.

The DAC can't output voltages between its discrete levels. It's not smoothly tracing a curve—it's hopping from one flat step to the next. The smooth mathematical function exists only in theory; the physical output is fundamentally quantized.

What made the staircase especially pronounced was that differentiation acts as a high-pass filter. Those sharp step transitions contain high-frequency components, and the derivative operation amplifies them. The quantization artifacts barely visible in the original sine wave became the dominant feature of the output.

```
Expected:        Actual:
    ___              _|
   /   \            | |_
  /     \          _|   |
 /       \        |     |_
/         \      _|       |
```

The code was right. The model was right. The constraint was the 12-bit resolution of physical hardware that no amount of clever programming could overcome.

## The Same Pattern, Different Domain

This wasn't an isolated incident. Earlier in the same session, I needed a Google Sheets formula to calculate magnitude from experimental data. The formula itself is trivial: `=SQRT(A2^2 + B2^2)`. Any first-year student knows this.

But the lab instructions referenced values "a" and "b" without explaining what they represented. Were these vector components? Real and imaginary parts of a complex measurement? Separate trials to be averaged? The formula depends entirely on the answer, and that answer was buried in a PDF I hadn't fully read.

When I asked Claude for help, the response was a clarifying question: "What do 'a' and 'b' represent in your experimental context?" Exactly the right question—and one I couldn't answer without going back to the source material.

Both problems shared the same structure. The execution was trivial once you understood the constraints. Understanding the constraints required context that lived outside the code.

## What I Actually Changed

After catching myself asking for help without providing enough background, I started including a brief context dump at the beginning of each task.

Instead of: "Write a formula to calculate magnitude from columns A and B."

I started writing: "This is post-lab analysis for a digital filtering experiment. Columns A and B contain the real and imaginary components of the frequency response measured at each test frequency. I need magnitude in dB for comparison against the theoretical transfer function."

The difference in response quality was immediate. The same capability was always there—I just wasn't activating it properly.

This sounds obvious in retrospect. It's the same principle as writing good documentation or clear commit messages. But when you're deep in a problem, it's easy to forget that your collaborator doesn't share your mental context.

## The Constraint You Can't Code Around

The staircase cosine still bothers me. Not because I couldn't fix it—you can add analog reconstruction filters, increase sampling rate, or use a higher-resolution DAC. What bothers me is how long I spent looking for a bug that didn't exist.

The code was doing exactly what it should. The model accurately predicted the behavior. The limitation was physical, not logical, and no amount of debugging would reveal it because there was nothing broken to find.

Working with AI tools has a similar failure mode. When Claude gives an unhelpful response, my instinct is to rephrase the question or try a different prompt. Sometimes that works. But sometimes the problem isn't the prompt—it's missing context that I've internalized so deeply I forget it needs to be stated explicitly.

The DAC can't output voltages it doesn't have. Claude can't use context it wasn't given. Both are constraints worth remembering the next time your output doesn't match your expectations.