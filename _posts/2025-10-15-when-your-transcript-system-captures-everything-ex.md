---
layout: post
title: "When Your Transcript System Captures Everything Except What Actually Happened"
date: 2025-10-15
categories: [development, ai]
tags: [claude-code, javascript, git, automation, testing]
read_time: 4
word_count: 975
---

Today was one of those days where I spent hours working with Claude Code across four different engineering courses, and my automated transcript system dutifully recorded approximately nothing useful about any of it.

Looking back at the session logs, I see timestamps. I see tool calls marked as "unknown" with empty JSON parameters—meaning the logging system recorded that *something* happened but failed to capture *what*. I see truncated PDF data where the logger tried to store raw binary content as text, hit a character limit, and chopped it mid-stream. What I don't see is the actual conversation—the debugging, the problem-solving, the moments where things clicked into place.

Here's the irony: this blog post was supposed to be auto-generated from those same broken transcripts. My system reads Claude Code session logs, feeds them to Claude for synthesis, and publishes the result. Today, I'm writing manually because the automation had nothing meaningful to work with. The tool that depends on transcript quality is now documenting transcript failure.

## What the Fragments Reveal

Despite the truncation, patterns emerge from the readable portions. The sessions spanned four mechanical engineering projects, and each reveals something about how the work actually happened—even when the record is incomplete.

**Motion Control Labs**: The fragments show a repeated workflow: reading a lab PDF page by page (I'd explicitly asked Claude to "only read 1 or 2 pages at a time"), then creating markdown and HTML files for submission. This incremental approach to processing large documents is something I've found essential when working with AI on technical assignments. Process too much at once and context gets muddy; process too little and you lose coherence across sections.

**Wind Turbine Analysis**: This snippet survived the truncation:

```
can you go ahead and make a first run at this project. 
please keep these files in a seperate folder. 
please keep track of any assumptions made for this first run 
that were not explicitate given in the insial documation.
```

The typos are verbatim—I was typing fast.

This request shows the value of treating AI-assisted work as iterative prototyping rather than one-shot generation. "First run" implies subsequent runs. "Keep track of assumptions" creates accountability for gaps in source material. The project involved implementing Blade Element Momentum theory for a 2.5 MW wind turbine: coefficient of power, coefficient of thrust, pitch angle optimization, tower structural analysis. Not trivial work.

Did the iterative approach pay off? The file timestamps suggest yes. There's a `wind_turbine_v1/` directory and a `wind_turbine_v2/`, with the second containing significantly more MATLAB files. The assumption-tracking produced a markdown file listing gaps like "hub height not specified, assumed 80m based on similar class turbines." When the second run happened, those assumptions became explicit decision points rather than buried guesses.

**Patent Mechanism Analysis**: The most interesting surviving request:

```
I have uploaded a series of patent images for different mechanisms 
can you try to understant them then make a linkage drawing 
for those linkages?
```

Using Claude Code to analyze patent drawings and reverse-engineer linkage configurations is genuinely creative work—turning visual mechanical information into structured representations. The output files show SVG linkage diagrams with labeled pivot points and link lengths. Whether they're *accurate* reconstructions, I can't verify from the fragments, but the approach feels worth exploring further.

**Feedback Control Systems**: The least survived of the sessions. Fragments mention Bode plots and transfer functions, the creation of HTML files for print-to-PDF submission. Standard homework workflow.

## The Logging Problem, Specifically

So what actually went wrong?

My logging captured tool invocations but not tool parameters or results. When Claude Code reads a PDF, the system saw "Read tool called" and recorded that, but the actual content—the extracted text, the page numbers, the file path—was stored as parameters that somehow became empty objects in the log.

Worse, when PDFs *were* captured, they were base64-encoded and stored inline. A 2MB PDF becomes roughly 2.7MB of base64 text, and my transcript storage truncates files over 500KB. The result: the first 18% of an encoded PDF, which decodes to corrupted garbage, followed by nothing.

This creates a peculiar failure mode. The logs look *busy*. Dozens of tool calls per session. Timestamps showing sustained activity from early morning through late evening. But activity isn't insight. A session with 80 tool calls might contain less useful information than a session with 5, if those 5 are captured completely.

## Four Fixes

1. **Separate binary content from text logs.** PDFs and images get stored as references, not inline data. The transcript points to `artifacts/session_123/assignment.pdf` instead of containing it.

2. **Capture parameters at invocation time.** The current system tries to parse parameters from completed tool calls; it should capture them when the call is made, before any processing that might lose them.

3. **Structure logs for truncation.** The most important information—what was asked, what the key conclusion was—should appear in the first 1KB of any session log. Details can follow, but the summary comes first.

4. **Add a completeness check.** Before the blog generator runs, validate that the transcripts contain actual content. A session with 50 tool calls but no readable parameters should trigger an alert, not silent processing.

## The Meta-Observation

There's something fitting about a logging system that captures the structure of work without the substance. It mirrors a lot of documentation practices: we record that meetings happened, that decisions were made, that code was committed. The *what* and *when* are easy. The *why* and *how* require deliberate effort.

Today's broken transcripts are themselves a form of signal. They tell me that my observability system observes the wrong things.

The work got done across four courses, multiple deliverables, a full day of engineering problem-solving. The record of that work is incomplete. Both facts are true, and the tension between them is exactly what I need to fix.