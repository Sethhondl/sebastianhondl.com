---
layout: post
title: "When Your Blog Pipeline Blogs About Itself"
date: 2026-02-14
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 3
word_count: 757
---

*What recursive processing reveals about content automation*

There's a particular kind of debugging that only happens when you automate content creation: your system produces output about its own failures. Today my automated blog pipeline — which turns Claude Code session transcripts into published posts — spent most of its cycles processing sessions where it was *already generating blog posts*.

## The Pipeline Eating Its Own Tail

AutoBlog's four-pass pipeline — draft, review, revise, polish — ran against transcripts that were mostly the pipeline running its previous cycle. February 14's transcripts captured the system processing an Agent Teams configuration post through all four passes, plus handling a BP1 project roadmap post.

So today's pipeline was reading transcripts of itself generating posts from transcripts. The output you're reading right now is the result.

## What the Recursion Revealed

This isn't just a funny observation. Watching the pipeline process its own output exposed patterns invisible during normal operation.

**The editor pass is the most valuable.** When the pipeline processed the Agent Teams draft, the editor caught seven specific structural issues. The strongest example: the original draft included a forced analogy between structural beam models and agent configuration — something like "just as Derivux assembles beam elements into a structural model, Agent Teams assembles specialized agents into a collaborative system." The editor flagged it as a reach between unrelated domains. The revision pass cut it entirely and replaced it with a takeaway grounded in actual Agent Teams experience. That's exactly the kind of structural call a human editor makes — not fixing grammar, but recognizing when a section is grasping for a connection that isn't there.

When the editor reviewed a post that didn't yet exist on disk (the BP1 roadmap draft), it handled the failure gracefully rather than hallucinating a review: "The draft file doesn't exist yet — it was described in your message but hasn't actually been written to disk." I'll come back to why that matters.

**The summarization pass strips context.** Each transcript gets summarized before the writing pass begins. Here's what one summary produced:

> "Worked on polishing and revising a blog post about configuring Claude Code's experimental Agent Teams feature."

What it compressed away: seven failed `Edit` tool attempts where the agent kept targeting the wrong line ranges, a lesson about `MEMORY.md` line limits that got recorded for future sessions, and a conflict between tmux hooks and the transcript capture system. All of that — the specific, narrative-rich material that makes for interesting reading — flattened into a single generic sentence.

This compression is fine when transcripts contain rich technical content that survives it. It breaks down when the transcripts are mostly the pipeline's own meta-operations — summarization requests, editorial prompts, and JSON responses. There's less signal to begin with, and what signal exists is precisely the kind that generic summarization discards.

## What I'd Change

The recursion highlighted a concrete design gap: **the pipeline doesn't filter out its own operations.** When AutoBlog sessions generate the majority of a day's transcripts, the system spends most of its processing budget on meta-content rather than actual engineering work. Today's transcripts contained a full-state feedback controller design, a Simulink model build, and a twenty-issue GitHub roadmap — all buried under layers of the pipeline processing itself.

The planned fix: add a `source_type` field to the transcript metadata in `project_memory.py`'s indexing step. Sessions launched from the `com.autoblog.daily.plist` launchd job or matching the `AutoBlog` project path get tagged `"source_type": "pipeline"`. Then in `generate_post.py`'s transcript selection, pipeline-tagged sessions receive a 0.3x weight multiplier when ranking which transcripts to feed into the writing pass. They're still available — sometimes the meta-observations are genuinely interesting — but a control systems derivation outranks a JSON summarization request by default.

## The Takeaway

Recursive processing turns out to be a genuinely useful stress test for content pipelines. The editor correctly refusing to review a nonexistent file confirmed that failure handling works. The summarizer predictably losing signal on meta-content pinpointed where compression is too aggressive. The writing pass dutifully padding thin summaries into full sections revealed the absence of input quality gates.

Normal inputs don't expose these behaviors. It took the pipeline looking in a mirror to show that the editor is the strongest pass, the summarizer is the weakest, and there's no mechanism to distinguish primary content from pipeline operations. Now I know where to add the filter — and more importantly, I know that running the system against its own output periodically is worth doing on purpose.