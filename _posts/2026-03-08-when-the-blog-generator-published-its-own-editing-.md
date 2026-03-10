---
layout: post
title: "When the Blog Generator Published Its Own Editing Notes"
date: 2026-03-08
categories: [development, ai]
tags: [claude-code, python, javascript, git, automation]
read_time: 7
word_count: 1506
---

On March 8th, I checked my blog and found this as the opening of the March 5th post:

> Here's the polished blog post. The key changes I made:
> 
> 1. Added concrete opening with the "polish pass leaked" problem
> 2. Restructured to lead with the bizarre failure mode
> 3. Expanded the recursive failure explanation
> 4. Added technical depth on subprocess validation

That wasn't a blog post. That was Claude's editorial notes explaining what changes it had made. Four consecutive posts (March 3-6) had published this way—not as finished articles, but as the generator's own commentary about what it was trying to write. The automated pipeline that produces daily blog posts had started publishing its development notes instead of the actual posts.

## What the Reader Actually Saw

The March 4th post opened with a numbered list:

> Here's the polished blog post. The key changes I made:
> 
> 1. Removed the meta-commentary about "removing meta-commentary"
> 2. Started with a concrete hook about the actual problem
> 3. Restructured to follow: problem → investigation → root cause → fix
> 4. Added specifics about the error message and file paths

Then it ended. No actual blog post—just editorial decisions that were supposed to happen behind the scenes.

The March 5th post was even more surreal. Claude, given the two previous broken posts as input for its polish pass, diagnosed the bug mid-generation: "Both of these posts contain **only editorial meta-commentary** about revisions that should have been made, without any actual blog post content." That diagnosis—complete with the bolded warning—became the published post. The pipeline that writes about development had published its own bug report.

## The Root Cause

The AutoBlog pipeline uses a four-pass architecture: draft → review → revise → polish. Each pass calls `claude --print -p` via subprocess and captures stdout. The polish pass was trying to write the finished post directly to `_posts/`, which the Claude Code sandbox denied. Instead of returning blog post markdown, Claude returned what it would tell a human operator:

> I've polished the post and improved the structure. Here's what I changed:
> 
> [editorial notes]
> 
> Could you grant write permission to save this to `_posts/2026-03-05-daily-development-log.md`?

The pipeline's subprocess handler does this:

```python
result = subprocess.run(["claude", "--print", "-p", prompt], capture_output=True)
if result.returncode == 0:
    return result.stdout.decode('utf-8')
```

When the file write succeeds, stdout contains the blog post. When the write is denied, stdout contains a conversational response *about* the blog post. The pipeline checks `returncode == 0` and accepts whatever text arrives. There's no validation that the output is the deliverable versus a message about the deliverable.

This isn't hallucination, refusal, or prompt injection. Claude did exactly what it was asked. It polished a blog post, then—unable to save the file—explained what it had done and requested permission. That's correct behavior in a conversational context. It's a pipeline-breaking failure in an automated one.

## What LLMs Don't Give You

A compiler either produces a binary or emits errors on stderr. An API endpoint returns JSON with a defined schema. An LLM produces text, and that text might be:

- The deliverable you asked for
- A description of the deliverable
- An explanation of why the deliverable couldn't be produced
- A diagnosis of the system state that prevented delivery

All arrive on stdout. All pass a `returncode == 0` check. All are valid, coherent, well-structured text. The model has no structural way to signal "this is the thing" versus "this is commentary about the thing."

The model is doing its job. The pipeline's job is to validate that what comes back is what it needs.

## The Fix That Would Have Caught This Immediately

The pipeline already had retry logic, but the retries were silent. When a pass failed, it would retry, fail again, and the caller would receive empty output or fall back to the previous pass. The real problem wasn't missing retries—it was missing observability.

Adding stderr and stdout preview logging would have made this obvious:

```
[2026-03-05 06:23:41] Polish pass attempt 1 failed (exit 0)
[2026-03-05 06:23:41] stdout preview: "Here's the polished blog post. The key changes I made:\n\n1. Added concrete opening with the \"polish pass leaked\" problem\n2. Restructured to lead with the bizarre..."
[2026-03-05 06:23:51] Polish pass attempt 2 failed (exit 0)
[2026-03-05 06:23:51] stdout preview: "Here's the polished blog post. The key changes I made:..."
```

When Claude returns "Here's the polished blog post" instead of a markdown heading, a preview makes that obvious. The retries were there. The missing piece was knowing what was being retried.

I also added draft-mode routing—posts from certain projects now save to `_drafts/` and skip git push entirely. This doesn't prevent the output-leaking bug, but it prevents broken posts from going live. If the pipeline produces garbage, the garbage stays local.

Additional fixes included front matter deduplication (handling cases where Claude emits its own YAML block that gets wrapped inside the pipeline's block) and a 30-minute SIGALRM timeout to prevent the pipeline from hanging indefinitely. As the [kill switch post](/2026/02/22/why-your-content-pipeline-needs-a-kill-switch.html) argued: build for the actual deployment environment, not the hypothetical one.

## The Recursive Failure

The March 5th post deserves special attention. By that point, the pipeline was ingesting the broken March 3rd and 4th posts as "recent context" for what blog posts should look like. Claude's polish pass received two examples that were pure meta-commentary, recognized the pattern, and wrote:

> **Critical Issue Identified**
> 
> Both of these posts contain **only editorial meta-commentary** about revisions that should have been made, without any actual blog post content. This appears to be a systematic failure in the generation pipeline where the "polish pass" instructions are being published instead of the polished output.

That analysis—completely accurate—became the published post. The generator had diagnosed its own bug, and the diagnosis leaked through the same broken pipe that caused the bug in the first place. It's the same recursive failure as the [February 14 post](/2026/02/14/when-your-blog-pipeline-blogs-about-itself.html), but this time the pipeline didn't just write *about* itself—it wrote *as* itself, publishing internal troubleshooting notes that should have stayed in stdout logs.

## The Broader Pattern

Any automated pipeline that treats LLM output as a structured deliverable needs validation that the output is *the thing* and not *a message about the thing*. Consider a test generation system that's supposed to output pytest fixtures. When the file write fails, you might get:

> I would create a fixture that mocks the database connection like this:
> 
> ```python
> @pytest.fixture
> def mock_db():
>     return MagicMock()
> ```
> 
> However, I don't have write access to `tests/conftest.py`. Could you either grant permission or let me know where you'd like this fixture added?

That's valid, helpful text. It's also not a pytest fixture. If your pipeline does `output = run_generator()` and then writes `output` to the test file, you've just committed conversational placeholder text to your test suite.

The validator needs to check: does this start with `@pytest.fixture`? Does it define a function? Is there actual code, or just a description of code?

The same applies to documentation pipelines that extract API specs, code review tools that output diffs, or any system where the LLM is supposed to produce a structured artifact. Without validation—checking for expected structure, required sections, format markers—the pipeline will happily publish meta-commentary.

## What the Pipeline Checks Now

The validation that would have prevented this:

```python
# After capturing stdout, before returning it as a blog post
if output.startswith("Here's the polished blog post"):
    raise ValueError("Generator returned meta-commentary instead of post content")
if not output.startswith("#"):
    raise ValueError("Output doesn't start with markdown heading")
if "I would" in output[:200] or "Could you" in output[:200]:
    raise ValueError("Output contains conversational phrases suggesting failed write")
```

These are crude heuristics, but they catch the actual failure mode. A more robust approach would validate that the output contains expected sections (title, body paragraphs, technical content) and doesn't contain the tell-tale phrases of a permission request or status update.

## The Quiet Failure Mode

I found the broken posts on March 8th during a routine check of the site. Nobody emailed me. Analytics showed normal traffic, which means readers probably skimmed the editorial notes, found them incomprehensible, and moved on. The posts were live for 2-5 days before I caught them.

That's the quiet failure mode of content pipelines: broken output often just looks like "weird content" rather than triggering an obvious error state. The broken posts from March 3-6 are still live. They're artifacts of the failure mode, and leaving them up is more honest than deleting them.

## The Takeaway

If you're building with LLMs in production: log what comes back, validate the output category, and assume the helpful conversational assistant will sometimes return helpful conversation instead of the structured data you need. Because from the model's perspective, both are equally valid responses to your prompt. Your job is to tell the difference before it goes live.