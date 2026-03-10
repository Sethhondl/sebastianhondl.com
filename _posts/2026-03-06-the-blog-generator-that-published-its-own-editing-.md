---
layout: post
title: "The Blog Generator That Published Its Own Editing Notes"
date: 2026-03-06
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 3
word_count: 669
---

I broke the blog pipeline twice in 72 hours. Both times, the symptom was identical: blog posts publishing their own editing instructions instead of content.

## What Broke

Instead of a blog post, this appeared:

```
Here's what I polished and why:
1. Opening — Tightened 'The task was straightforward' to 'The task:'
2. Technical explanation — Added concrete example of the race condition
3. Conclusion — Removed redundant summary paragraph
```

Three consecutive days (March 3, 4, 5) published variations of this. The files also had mismatched dates and generic fallback titles instead of the real titles the pipeline had chosen.

## How the Pipeline Works

The blog generator runs four passes through the Claude CLI:

1. **Draft** — Generate initial post from transcripts
2. **Review** — Critique the draft and identify improvements  
3. **Revise** — Implement the improvements
4. **Polish** — Final readability pass before publication

Each pass feeds into the next. The polish prompt explicitly says: "Output ONLY the blog post markdown, starting with # Title. Do NOT include any preamble, commentary, code fences, or explanatory notes."

## The Bug

The leaked reasoning looked like a permissions error—Claude asking to save files and getting blocked. But the pipeline ran unattended via launchd. If it couldn't write, it would fail completely, not swap content.

The real issue: the polish pass was leaking its internal reasoning into the output. The pipeline captured whatever Claude returned and saved it as the blog post. So the published files contained editorial commentary, not content.

## The Fix That Didn't Fix It

I added regex patterns to catch meta-commentary and reject it:

```python
def _clean_claude_output(text):
    # Strip markdown code fences if present
    if text.startswith('```'):
        lines = text.split('\n')
        text = '\n'.join(lines[1:-1])
    
    # Detect meta-commentary patterns
    meta_patterns = [
        r'^(Here\'s|I need|Would you like|Could you)',
        r'^Changes made:',
        r'write permission'
    ]
    
    if any(re.match(p, text, re.IGNORECASE) for p in meta_patterns):
        return None  # Signal failure, fall back to previous pass
    
    return text.strip()
```

This caught the broken output and rejected it. The pipeline fell back to the previous pass instead of publishing meta-commentary.

I tested the fix on the same broken posts, saw that it worked, and immediately hit the same failure mode again the next day.

## The Part I Missed

The meta-commentary detection only ran on the polish pass. If Claude leaked its reasoning during the **revise** pass instead, the bug would propagate undetected:

1. Draft contains meta-commentary ("I need write permission")
2. Revise polishes the meta-commentary
3. Polish polishes it further
4. Published post is polished garbage

When I read the March 6 post before publication, I saw the same pattern—but different meta-commentary. It wasn't polish-pass commentary. It was revise-pass commentary that had been polished. The pipeline wasn't just failing at one stage. It was carrying the failure forward, refining a request for write permissions as if it were blog content.

## What Actually Fixed It

Two changes:

1. **Detect meta-commentary at every pass**, not just the final polish. If any pass returns reasoning instead of content, reject it and fall back.

2. **Check the input before prompting**. If the draft being revised contains phrases like "I need write permission" or "Could you grant access", the draft is broken. Skip the pass or regenerate from scratch.

The fix wasn't just catching bad output—it was catching bad *input* before it poisoned downstream passes.

## The Lesson

When a system has multiple passes, and each pass depends on the output of the previous pass, a failure in any stage compounds. The clearest version of this is when the failure mode is subtle enough that it looks like valid output. Meta-commentary looks like markdown. A permissions request looks like a blog post if you squint.

Validation can't happen only at the boundaries. Every transformation needs its own integrity check. A broken pass doesn't fail cleanly—it produces plausible-looking garbage that the next pass will dutifully refine.

Three days of posts republished with correct content. Pipeline hasn't leaked since.