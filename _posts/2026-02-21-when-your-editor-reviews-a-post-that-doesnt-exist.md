---
layout: post
title: "When Your Editor Reviews a Post That Doesn't Exist"
date: 2026-02-21
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 5
word_count: 1029
---

*A type mismatch bug that hides in every multi-stage pipeline*

You've seen a build that exits zero but produces an empty artifact. You've seen an API return 200 OK with an error message in the body. Today my blog pipeline produced a new variant: Pass 1 wrote a description of the post it was supposed to write, and Pass 2 — the editorial review stage — correctly refused to review prose that wasn't there.

The interesting part isn't the failure. It's that every stage checked whether the previous stage produced *output* without checking whether it produced the *right kind* of output.

## What Happened

AutoBlog uses a four-pass generation pipeline. Pass 1 drafts the blog post from session transcripts. Pass 2 reviews the draft editorially. Pass 3 revises based on the review. Pass 4 polishes. Each pass reads the output of the previous pass and writes its own.

Today, Pass 1 didn't have write permission to the `_posts/` directory. Instead of failing loudly, it did what language models do when they can't perform the requested action: it described what it *would* write. The output looked like content — it had a title, bullet points, a word count estimate. It just wasn't a blog post. It was a summary of a blog post.

Pass 2 received this output and did exactly the right thing. It identified that no actual draft existed and refused to fabricate a review:

> "The actual blog post doesn't exist yet. What you've provided is a summary/outline of the intended post, not a written draft."

Correct behavior. But the pipeline didn't treat it as a failure. Pass 2 produced output — editorial feedback — so the orchestrator sent it along to Pass 3 for revision.

## The Accidental Recovery

Pass 3's normal job is to take Pass 2's editorial notes and apply them to the draft. But there was no draft to revise. The editorial notes explicitly said so. So Pass 3 pivoted: it read the original transcript context, checked recent posts for tone and formatting, and wrote the entire post from scratch.

This worked. The output was a coherent blog post. But it was accidental resilience, not intentional design. Pass 3 wasn't built to be a fallback writer — it happened to have enough context to improvise one. On a different day, with different transcript content or a slightly different editorial response, it might have produced something incoherent or simply passed along another description of a post that should exist.

Accidental resilience is worse than a clean failure. A clean failure gets logged, investigated, and fixed. Accidental resilience gets silently incorporated into the success path. The pipeline "worked" today, which means without explicit investigation, the underlying permission bug would persist. Each future run would depend on Pass 3 happening to recover gracefully — a bet that gets worse over time.

## The Deeper Bug: Presence vs. Shape

Strip away the blog-specific details and the bug is generic. Each stage validates that the previous stage produced *something* but not that it produced *the expected thing*. The contract between stages is implicit: Pass 1 should produce markdown prose, Pass 2 should produce editorial feedback on that prose, Pass 3 should produce a revised version. But the only check at each boundary is "did the previous stage return non-empty output?"

This is a type mismatch. The pipeline moves strings between stages when it should be moving typed artifacts. A draft is not the same type as a description of a draft, even though both are non-empty strings. Editorial feedback on a nonexistent draft is not the same type as editorial feedback on a real one, even though both contain valid English sentences about writing quality.

The same pattern shows up everywhere:

- An HTTP response with status 200 and `{"error": "unauthorized"}` in the body. Any client that checks only the status code proceeds as if the request worked.
- A CI build that exits 0 because the test runner itself succeeded, even though it found zero test files to run. Green build, zero coverage.
- A data pipeline that ingests a CSV with correct headers and zero data rows. Schema validation passes. Row count validation doesn't exist.

In each case, the handoff between stages checks for *presence* but not *shape*.

## What I'm Adding

The fix has two parts.

First, the permission issue. Pass 1 needs verified write access to `_posts/` before generation begins. A pre-flight check in `daily_blog.py` that creates and deletes a temporary file in the target directory — if it fails, the pipeline aborts with an explicit error instead of silently degrading into description mode.

Second, content-type validation between passes. After Pass 1, a lightweight check that the output contains front matter (the `---` delimited YAML block that Jekyll requires) and a minimum ratio of prose to bullet points. A description of a post is heavy on bullet points and light on paragraphs; an actual post is the reverse. After Pass 2, a check that the editorial feedback references specific passages rather than commenting on the draft's absence. These are heuristics, not proofs — but they catch the exact failure mode that occurred today.

Neither check is complex. Both could have been written in the time it took Pass 3 to improvise its way around the problem. The reason they didn't exist is the usual one: the happy path worked, and the failure mode produced output that *looked* valid at a glance.

## The Takeaway

Pipeline stages that pass strings to each other are pipelines held together by coincidence. The string happens to contain the right thing most of the time, so the absence of validation doesn't surface as a bug — until it does, and the failure mode isn't a crash but a silent degradation that the next stage heroically tries to recover from.

Check the shape of what flows between your pipeline stages, not just whether something flows. A 200 with an error body, a green build with no tests, and a blog editor reviewing a post that doesn't exist are all the same bug. The container looks fine. The contents are wrong.