---
layout: post
title: "When Your Logging System Logs Nothing: Thirteen Empty Tool Calls"
date: 2025-10-14
categories: [development, ai]
tags: [claude-code, javascript, automation, testing, api]
read_time: 3
word_count: 670
---

My transcript system recorded thirteen tool calls today. Every single one came back empty:

```
### Tool Call: unknown [2025-10-14T11:55:27.608324]
**Parameters:**
```json
{}
```
```

The timestamps progressed through my session. The tool calls were being detected. But somewhere between "Claude did something" and "here's what Claude did," the actual content vanished.

## The Work That Disappeared

I spent the morning on a wind turbine modeling project—building a mathematical model of the UMN turbine installation in Rosemount, Minnesota. Claude helped me create two markdown files: one outlining the project approach, one cataloging the questions I'd need to answer before completing the analysis.

The session went well. The markdown files exist on disk. But the transcript captured none of the reasoning that produced them. Those thirteen empty tool calls were Claude reading the PDF assignment, writing the project outline, drafting the questions document, and revising based on my feedback. All the substantive work—gone.

This matters because the whole point of transcript capture is documenting the *process*, not just the artifacts. I can read the markdown files anytime. What I can't recover is the back-and-forth: why Claude structured the questions in a particular order, what considerations shaped the project outline, how we iterated on the scope.

## The Three-Legged Stool

Documenting AI-assisted development requires three things:

1. **The conversation** — real-time iteration between you and the AI
2. **The artifacts** — files that land on disk
3. **The process log** — how the first produced the second

Today I got the artifacts. The markdown files are fine. But the conversation and process log are both compromised—the transcript captured later discussion but missed the tool calls that actually created the documents.

One leg out of three.

## What Were Those Thirteen Calls?

I can only reconstruct from context. The session involved reading a PDF assignment, listing directory contents, writing two markdown files, and possibly revising them. That accounts for maybe seven operations. The remaining calls might have been additional reads or revision passes. The transcript doesn't say—just thirteen identical "unknown" entries with empty parameters.

My hook parses Claude Code's response format to extract tool usage. Either that format changed, or PDF reading triggers an edge case my parser doesn't handle, or there's something specific about write operations that my regex misses.

## Silent Failures Are the Worst Kind

Here's the uncomfortable truth: I remembered everything anyway. The wind turbine questions, the project structure—I can reconstruct it all from memory.

But that's not the point. My documentation system failed silently. It logged timestamps and empty braces, looking like it was working. If I hadn't reviewed the transcript for this blog post, I wouldn't have noticed until the next time I needed to reference a session and found nothing there.

## The Fix

Tomorrow's debugging checklist:

1. Find a transcript that worked and compare the raw format
2. Check for Claude Code schema changes
3. Test PDF reading specifically to see if it's reproducible
4. Add validation so the hook warns on empty parameters instead of silently logging garbage

The backup that saved me was my own memory, which isn't a backup at all. A real backup would be the raw transcript before processing—if I still have that, I can reparse once I fix the bug.

## The Real Lesson

"Validate your capture system" is obvious advice. Here's what would have actually caught this: a test that runs the hook against a known-good transcript and asserts that tool calls have non-empty parameters. I didn't write that test because I assumed the parsing was straightforward.

It wasn't.

If you're building automation around AI tool transcripts, don't just check that your system runs—check that it captures what you think it captures. The transcript format isn't a stable API. It's a convenience feature that can change without warning. And a logging system that logs nothing useful is worse than no logging at all, because it gives you false confidence while you lose data you can't get back.