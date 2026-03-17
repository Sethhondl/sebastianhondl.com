---
layout: post
title: "When the Editors Keep Asking for the Actual Post"
date: 2026-03-16
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 6
word_count: 1382
---

The review pass returned ten points of detailed feedback. Point one: "The title promises template boilerplate but the outline covers four unrelated failures." Point six: "The OAuth expiration needs either more space or no space." Point nine: "Match the voice of the existing posts more precisely."

All of this was earnest, actionable, correct editorial guidance — delivered to a document that was five bullet points and a closing line. The review pass opened with the diagnosis in bold: **"The core problem: I can't review a post that doesn't exist yet."** Then it reviewed the post that didn't exist yet anyway, producing a more thorough editorial analysis than most human editors would bother with for an actual draft.

This happened twice on March 16. Two parallel generation attempts. Two outlines masquerading as posts. Two review passes that correctly identified the problem and then couldn't stop themselves from solving it.

Yes, this is the third consecutive post about the pipeline failing. I'm going to acknowledge that directly and move on.

## Why the Draft Pass Produced an Outline

The transcript that fed the March 16 draft pass opens like this:

```
## User [2026-03-17T12:52:16]
You are writing a blog post about my day coding with Claude Code.

## Today's Claude Code Sessions
### Project: active-projects-AutoBlog

# Claude Conversation Transcript
## User [2026-03-16T14:04:16]
Summarize this Claude Code session for the project "active-projects-AutoBlog" on 2026-03-16.

Session content:
# Claude Conversation Transcript
## User [2026-03-16T13:57:26]
Summarize this Claude Code session for the project "active-projects-AutoBlog" on 2026-03-15.

Session content:
# Claude Conversation Transcript
## User [2026-03-15T10:00:54]
Summarize this Claude Code session for the project "active-projects-AutoBlog" on 2026-03-14.
```

Four layers deep. A transcript of the pipeline summarizing a transcript of the pipeline summarizing a transcript of the pipeline summarizing a transcript. Each layer is a "Summarize this session" prompt wrapping the previous day's version. The actual engineering work — the session content being summarized — is buried under three layers of the pipeline talking to itself.

The draft pass receives this and does exactly what the input suggests: it summarizes. The transcript is *about* summarizing, so the model produces a summary. It outputs a pitch — "here's what the post would cover" — instead of prose, because the dominant pattern in its input is descriptions of content rather than content itself.

This is the recursive loop the [March 12 post](/2026/03/12/when-the-pipeline-publishes-its-own-autopsy.html) predicted. The pipeline runs. Its run generates a transcript. That transcript becomes input for the next run. The next run's draft pass, seeing a transcript about summarizing rather than a transcript about engineering, summarizes instead of narrates. That summary becomes the next transcript. The nesting deepens by one layer per day.

## What the Editor Said to the Outline

The review pass on the first attempt opened with its diagnosis and then delivered all ten points anyway. Here are three, verbatim, applied to five bullet points:

> **1.** "The title promises template boilerplate but the outline covers four unrelated failures. The OAuth expiration (point 2) and recursive nesting (point 3) are separate bugs with separate causes. Cramming them into a post framed around the template heading leak dilutes the central narrative."

> **6.** "The OAuth expiration needs either more space or no space. A 401 that 'silently degraded context without crashing' is a serious infrastructure story, but in ~875 words alongside three other topics, it'll get maybe two paragraphs."

> **10.** "Cut the word count estimate or increase it. At ~875 words covering four distinct failure modes plus fixes plus a thematic thread, you're looking at ~125 words per topic."

The review pass estimated words-per-topic on a document that had no topics. It critiqued the pacing of prose that didn't exist. It suggested the post "match the voice of existing posts more precisely" — pointing to a post that was itself a set of bullet points. Every note was correct in the abstract and inapplicable in practice. The editorial machinery performed a flawless review of nothing.

The second attempt produced the same result. A different pitch, the same five-bullet-point structure, the same review pass opening with the same observation: you gave me an outline, not a post.

## The 401 That Didn't Crash Anything

Before the recursive nesting became the main problem, the pipeline was already running degraded. On March 15, the summary pass hit this:

```
Failed to authenticate. API Error: 401
{"type":"error","error":{"type":"authentication_error",
"message":"OAuth token has expired. Please obtain a new
token or refresh your existing token."}}
```

The pipeline caught the non-zero exit code and moved on. It didn't crash. It didn't retry with a fresh token. It proceeded with whatever context it had accumulated before the auth failure — which, for a summary pass that runs early, meant nearly empty context. The subsequent draft pass received a project history with gaps where the March 14 and 15 summaries should have been, and filled those gaps with the only material available: the recursive transcript nesting.

The 401 didn't cause the outline-instead-of-post failure. But it removed the context that might have prevented it. A summary pass with valid auth would have produced a clean project history. The draft pass would have seen "on March 14, the pipeline published a blank template" as a one-line summary rather than as four layers of nested "Summarize this session" prompts. The OAuth expiration didn't break the pipeline. It degraded the pipeline's immune system right before the infection arrived.

## The Fix That Keeps Getting Proposed

The [March 12 post](/2026/03/12/when-the-pipeline-publishes-its-own-autopsy.html) proposed three defenses: a minimum word count, a structural check for narrative elements, and a classification gate. The [March 15 post](/2026/03/15/when-the-pipeline-published-a-blank-template-as-a-.html) documented the same three fixes — word count, structural check, classification gate — noting that they would have caught the template leak but hadn't been deployed. Now here on March 16, the pipeline produced outlines that all three checks would have rejected.

To make the pattern explicit:

- **March 12**: "A minimum word count. A structural check. A classification gate." Proposed in `_posts/2026-03-12`.
- **March 15**: "A word count floor. A placeholder blocklist. Structural validation." Proposed in `_posts/2026-03-15`.
- **March 16**: The pipeline produces 50-word outlines. All three checks would catch them. None exist in `generate_post.py`.

Three posts. Three identical recommendations. Zero implementations. The fixes live in the blog's archive, not in the codebase. The pipeline publishes its own remediation plan and then ignores it on the next run.

## What Would Actually Break the Cycle

The loop is: pipeline fails, post documents failure, post proposes fixes, fixes remain in `_posts/`, pipeline fails again. The escape isn't a better fix — it's deploying any of the fixes already proposed three times.

But there's a deeper structural problem that no word-count check solves. The recursive transcript nesting means the pipeline's input degrades every day it runs on its own output. A word count gate would reject today's outline. It wouldn't prevent tomorrow's draft pass from receiving a five-layer-deep transcript of the pipeline summarizing itself summarizing itself. The input degradation is upstream of the output validation.

The transcript nesting could be broken by excluding AutoBlog's own sessions from its input — don't let the pipeline read transcripts of itself running. Or the summary pass could produce fixed-length summaries that don't preserve the nested prompt structure. Or the draft pass could receive only summaries, never raw transcripts, eliminating the nesting entirely.

Each of those is a design change, not a heuristic. And each has been, until now, the kind of thing that gets described in a blog post rather than committed to a repository.

This post, like the March 12 and March 15 posts before it, was written manually outside the pipeline. Of the last six posts on this blog, four exist because the pipeline couldn't write them. The pipeline produces the blog's best material by failing — not as a clever observation, but as a literal accounting of the archive. The posts that required manual intervention are the ones with narrative structure, specific detail, and a through-line. The posts the pipeline produced on its own are a 50-word template skeleton and a 62-word skeleton with anchor links to its own empty sections.

The cycle breaks when the fixes move from `_posts/` to `generate_post.py`. Until then, the pipeline and I will keep taking turns.