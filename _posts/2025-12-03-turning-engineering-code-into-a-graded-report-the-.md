---
layout: post
title: "Turning Engineering Code Into a Graded Report: The Self-Grading Loop"
date: 2025-12-03
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 4
word_count: 834
---

The moment I realized I could treat a grading rubric as a software specification document, everything clicked. I'd been staring at months of MATLAB output—figures, calculations, simulation results—trying to figure out how to wrestle it all into a coherent report. Then it hit me: the rubric wasn't just telling me what to include. It was a requirements document, complete with acceptance criteria.

## The Problem: Technical Analysis Without Communication

The project was a flywheel energy storage system analysis for a mechanical engineering course. I'd spent weeks building MATLAB code that modeled the physics, ran simulations, and optimized parameters. The code worked. The results were solid. But the output was incomprehensible to anyone who hadn't been living inside those scripts.

I was working with Claude to transform this raw technical work into a polished PDF report. The grading rubric specified exactly what needed to appear: specific plots, particular calculations explained, conclusions in a certain format. My task was bridging the gap between "code that runs" and "document that communicates."

## Treating the Rubric as a Spec Document

Before writing anything, I had Claude parse through the grading rubric. It was structured as a CSV with point values:

```csv
"B. design AMB disturbance response (Q1d)","Correct results and complete explanation, including a description of the AMB control system.",2
"Design space for team cycle (Q2a)","Correct results and explanation of design space trends and trade-offs",2
```

Each row became a checklist item. The text descriptions told us *what* to include. The point values indicated *how much attention* each section deserved. A 2-point item with vague criteria needed less elaboration than a 5-point item demanding "complete explanation."

This reframing changed how I approached the writing. Instead of asking "what should I say about the control system?" I asked "what does the spec require for the control system section to pass acceptance?" The rubric answered that question directly.

## The HTML-to-PDF Pipeline

Rather than fight with LaTeX or Word, I chose HTML for the report. The reasoning was practical: I needed programmatic generation, predictable rendering, and clean PDF output without manual formatting.

The key was Chrome's headless mode:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --print-to-pdf=/path/to/output.pdf \
  --no-pdf-header-footer \
  /path/to/report.html
```

Why Chrome over alternatives like wkhtmltopdf or Puppeteer? Chrome's rendering engine handles CSS and embedded images more reliably, and it's already installed on most machines—no additional dependencies. Puppeteer would work too, but it's overkill when a simple command-line flag does the job.

That `--no-pdf-header-footer` flag was essential. Without it, every page gets timestamps and file paths printed in the margins—fine for internal documents, unacceptable for a graded submission.

## The Self-Grading Loop

Here's where the workflow became interesting. After generating the first PDF, I had Claude read the rendered document and grade it against the rubric. This meant evaluating it as a grader would see it—not as I saw it in the source HTML.

The loop worked like this:

1. Generate PDF from HTML
2. Extract and read the PDF content
3. Compare each section against its rubric requirement
4. Identify gaps between what's there and what's needed
5. Edit the HTML source
6. Regenerate and repeat

**A concrete example:** The rubric required "explanation of design space trends and trade-offs" for the optimization section. My first draft showed the plots and stated the optimal values. Claude's self-grade flagged the missing piece: I'd shown *what* the optimal point was, but not *why* moving away from it degraded performance. The revision added a paragraph explaining how efficiency dropped when flywheel speed increased beyond a threshold due to windage losses. That's the kind of gap that's invisible when you're writing but obvious when you're grading.

The self-review also caught rendering issues that looked fine in HTML but rendered poorly in the PDF. One figure that was perfectly legible on screen came out too small to read in print. The rendered output is what graders see, so the rendered output is what needed checking.

## When This Works (and When It Doesn't)

This approach works well for structured academic reports with explicit requirements. When you have a rubric, you have a spec. When you have a spec, you can verify against it systematically.

It's less suited for open-ended writing where the "requirements" are subjective. A research paper with vague guidelines ("demonstrate original contribution") can't be self-graded the same way. The rubric-as-spec model depends on having concrete, checkable criteria.

## The Takeaway

If you're facing a similar transformation—turning technical work into a graded deliverable—consider this mental model: you're not writing a report, you're implementing a specification. The rubric tells you what to build. Your job is meeting those requirements and verifying that you've met them.

The flywheel analysis was solid engineering work. But engineering work that can't be communicated doesn't get graded, doesn't get funded, doesn't get built. Treating that communication challenge with the same rigor I'd applied to the technical analysis—same verification loops, same iterative refinement—turned an overwhelming formatting task into a solvable problem.