---
layout: post
title: "When the Polish Pass Leaked Its Reasoning"
date: 2026-03-07
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 4
word_count: 992
---

If you read this blog between March 3 and 6, you didn't read blog posts. You read Claude's editorial notes — the process commentary that was supposed to be discarded before anything reached the page. Four consecutive posts went live containing lines like this:

> Here's the polished blog post. The key changes I made:

And this, from the March 4 post:

> It looks like I need write permission to `_posts/`. Here's what I polished and why:

The March 5 post is the strangest. Claude, given the two previous broken posts as input for its polish pass, diagnosed the problem mid-output: "Both of these posts contain **only editorial meta-commentary** — they describe changes that *would* be made to a blog post, but never contain the actual blog post content." It identified the pipeline bug, recommended fixing `generate_post.py`, and then *that diagnosis itself* was published as the blog post for the day.

The pipeline that writes about development published its own development notes. If that sounds familiar, the [February 14 post](/2026/02/14/when-your-blog-pipeline-blogs-about-itself.html) was literally titled "When Your Blog Pipeline Blogs About Itself." Same recursion, different failure mode. That post was about the pipeline processing its own transcripts. This time the pipeline didn't just write about itself — it wrote *as* itself, unfiltered.

## What Actually Broke

The pipeline calls `claude --print -p` via subprocess for each of its four passes: draft, review, revise, polish. The polish pass tried to write the finished post to `_posts/` directly — a file write that the Claude Code sandbox denied. Instead of returning the polished text to stdout, Claude returned what it would have said to a human operator: "Here's what I changed and why. Could you grant write permission so I can save the file?"

This is the critical mechanism. The subprocess call captures stdout. When the write succeeds, stdout contains the blog post. When the write is denied, stdout contains Claude's conversational response *about* the blog post — editorial notes, a summary of changes, a permission request. The pipeline's `_call_claude_cli` method checks `returncode == 0` and takes whatever comes back. It has no way to distinguish between "here is the deliverable" and "here is my thinking about the deliverable." Both arrive as text in the same stream.

The pipeline already had retry logic — `max_attempts = 2` with a 10-second sleep. But the retries were silent. A failed pass would retry, fail again, and the caller would receive an empty string or fall back to the previous pass's output. The real problem wasn't the absence of retries. It was the absence of *observability*. Nothing logged what Claude actually returned, so the failure mode — editorial commentary leaking into published output — was invisible until a reader noticed.

## What Was Added

Two fixes mattered most.

**Logging what Claude returns.** The `_call_claude_cli` method now logs stderr and a 200-character stdout preview on non-zero exit codes. This would have caught the original bug immediately. When the polish pass returns "Here's the polished blog post. The key changes I made:" instead of a markdown heading, a 200-character preview makes that obvious in the log. The retries were already there. The missing piece was knowing what was being retried.

**Draft-mode routing.** Posts from certain projects now save to `_drafts/` instead of `_posts/`, and draft posts skip the git push entirely. This doesn't prevent the output-leaking bug, but it prevents the consequence — broken posts going live on the public site. If the pipeline produces garbage, the garbage stays local.

Two other fixes address related failure modes. Front matter deduplication in `_clean_claude_output` handles cases where Claude emits its own `---` YAML block that then gets double-wrapped by `_format_jekyll_post`. A 30-minute global timeout via SIGALRM in the orchestrator catches hung processes. The SIGALRM approach is Unix-specific and won't work on Windows, but for a single-user macOS pipeline running via launchd, it's the right tool. The [kill switch post](/2026/02/22/why-your-content-pipeline-needs-a-kill-switch.html) from February made the same argument: build for the actual deployment environment, not the hypothetical one.

## The Failure Mode That Doesn't Have a Name

The interesting thing about this bug is what category it belongs to. It's not hallucination — Claude didn't invent facts. It's not refusal — Claude didn't decline the task. It's not prompt injection — no adversarial input was involved. Claude did exactly what it was asked to do. It polished a blog post. Then, unable to write the file, it told the operator what it had done and asked for permission. That's correct behavior in a conversational context. It's a pipeline-breaking failure in an automated one.

The deeper problem is that LLMs have no structured separation between the work and the reasoning about the work. An API endpoint returns JSON with a defined schema. A compiler either produces a binary or emits errors on stderr. Claude produces text, and the text might be the deliverable, or it might be a description of the deliverable, or — as the March 5 post demonstrated — a diagnosis of why the deliverable wasn't delivered. All of it arrives on stdout. All of it passes a `returncode == 0` check.

I don't have a standard name for this. "Output category confusion" is the closest I can get — the model produces valid, coherent, well-structured text that answers the wrong question. Any automated pipeline that treats LLM output as a deliverable rather than a conversation turn needs validation that the output is actually *the thing* and not *a message about the thing*.

The broken posts from March 3–6 are still live. They're artifacts of the failure, and leaving them up is more honest than quietly deleting them. This post is the result of the pipeline running with the fixes in place — which means, yes, the polish pass that produced this text could have leaked its own reasoning instead. You'd be reading editorial notes about editorial notes about editorial notes. Turtles all the way down.