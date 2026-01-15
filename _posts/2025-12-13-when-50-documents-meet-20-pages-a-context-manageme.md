---
layout: post
title: "When 50 Documents Meet 20 Pages: A Context Management Problem"
date: 2025-12-13
categories: [development, ai]
tags: [claude-code, git, debugging]
read_time: 4
word_count: 815
---

Twenty pages. That was the limit my professor set for our ME4231 Motion Control final—bring anything you want, as long as it fits on ten double-sided sheets. I stared at fifty-plus documents of control theory, from Bode plots to PID tuning to state-space representations, and wondered how any of this would compress down to something I could actually use.

I decided to use Claude Code to help organize this mountain of material. What I learned had less to do with control systems and more to do with how AI tools handle large amounts of context—and how that constraint shapes everything.

## The Scope of the Problem

Motion Control covers the mathematics of how systems respond to inputs over time: transfer functions, frequency response, stability analysis. The material is dense with equations, block diagrams, and interconnected concepts where understanding one topic requires referencing three others.

The course materials included:
- 11 lecture PDFs (some 40+ pages of dense derivations)
- 11 lab assignments with MATLAB implementations
- Board notes, annotated versions, and review materials
- Reference documents totaling over 50 individual files

My plan was straightforward: have Claude Code read through everything and generate a dense HTML file I could print using Chrome's headless mode. HTML gave me precise control over layout, column formatting, and font sizing that Word or LaTeX would have fought me on.

The execution was anything but straightforward.

## What Happens When You Feed an AI Too Much

My first attempt was simple: ask Claude to read a lecture PDF and summarize the key formulas. For a 40-page document on frequency response methods, this failed immediately. The tool returned errors, and responses came back truncated mid-sentence.

The problem is fundamental to how these systems work. Large language models have context windows—limits on how much text they can process at once. Exceed that limit, and things break in unpredictable ways.

I'd ask Claude to extract all transfer function examples from a lecture and get back:

```
The lecture covers several transfer function forms:
1. First-order: G(s) = K/(τs + 1)
2. Second-order: G(s) = Kω_n²/(s² + 2ζω_n·s + ω_n²)
3. [Response truncated]
```

Everything after the cutoff—including the most complex examples I actually needed—vanished.

## The Chunking Solution

The fix came from thinking about how humans handle large documents. We don't read a 50-page technical document in one sitting. We break it into pieces.

I started giving Claude explicit instructions:

```
Read lecture_07_frequency_response.pdf in chunks. For a 40-page document, 
process pages 1-15 first, then pages 12-25, then pages 22-40. Summarize 
each chunk separately, then I'll ask you to combine them.
```

That overlap—going back 3-4 pages when starting a new chunk—turned out to be crucial. Page 14 of one lecture ended with: "The phase margin can be found by..."

Page 15 continued: "...locating where the magnitude plot crosses 0 dB and reading the phase at that frequency."

Without overlapping chunks, the first section would end mid-sentence, and the second would start without context. The overlap kept complete concepts intact.

For my 50+ documents, I settled on roughly 20% overlap—enough to capture any concept spanning a page break without redundantly processing too much content.

## The Technical Implementation

The actual workflow looked like this:

1. List all PDFs in the course materials directory
2. For each PDF, determine page count and calculate chunk boundaries
3. Process each chunk, extracting formulas, definitions, and key concepts
4. Combine chunks into a single document per lecture
5. Generate HTML with a two-column layout optimized for dense information
6. Use `chrome --headless --print-to-pdf` to render the final output

Chrome's headless mode was essential because it renders CSS exactly as a browser would, giving me precise control over margins, column breaks, and font scaling.

## What I'd Do Differently

The "20% overlap" rule worked for lecture notes, but it wasn't universal. Lab assignments with long code blocks needed more overlap because a MATLAB function spanning two pages would get split awkwardly. Reference tables needed less because each row was self-contained.

Context management isn't a formula you can apply mechanically. You need to understand the structure of your source material and adjust accordingly. Dense mathematical derivations require different handling than bullet-pointed summaries.

## The Real Takeaway

Tomorrow I'll print this HTML file and discover whether my digital formatting survives contact with physical paper. Twenty pages of control theory, condensed from material that would stack an inch thick if printed directly.

Whether I pass the final depends on how well I actually learned the material. But the process of building this cheat sheet taught me something the course itself didn't cover: systems of all kinds—whether control loops or language models—need their inputs structured appropriately to produce useful outputs.

The phase margin formula won't help me remember that lesson. But the three failed attempts before I figured out chunking certainly will.