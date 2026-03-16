---
layout: post
title: "When the Pipeline Published a Blank Template as a Finished Post"
date: 2026-03-15
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 5
word_count: 1124
---

On March 13, this appeared on the live site:

```yaml
```

Followed by:

> **Brief one sentence mission statement for article.**
>
> ## Table of Contents
>
> ## Purpose of Document
>
> *1 - 3 sentence section describing the purpose of this article.*
>
> ## Related Issues / PRs
>
> *Bullet list of all relevant issues...*

That's the Severson Group contributing template. Section headings, placeholder italics, instructional comments — all published to the live site as a finished blog post. On March 14, it happened again. Same template, same placeholder title, same `<!-- omit from toc -->` HTML comment embedded in the front matter. The only difference: the second version included a table of contents with anchor links to its own empty sections.

If you followed the March 3–6 failures and the postmortems on [March 7](/2026/03/07/when-the-polish-pass-leaked-its-reasoning.html) and [March 8](/2026/03/08/when-the-blog-generator-published-its-own-editing-.html), the shape might look familiar. It's not. Those failures were about the pipeline publishing its own reasoning — editorial notes, permission requests, self-diagnosis. The template leak is a different category entirely.

## What the Pipeline Was Supposed to Write About

The day's actual engineering work was reformatting the Tutorial 6 README for the PAR Mobile Robot Platform, submitted as PR #47 to `Severson-Group/bp1`. The contributing template — `# Article Name <!-- omit from toc -->` followed by `## Purpose of Document`, `## Related Issues / PRs`, and the rest — was part of the project's documentation scaffolding. It existed in the transcript because the session involved working with that template structure.

The pipeline's draft pass received the transcript containing the template as a reference artifact. Instead of writing *about* the work of filling in and reformatting the template, it extracted the template itself and published it as the post. The actual engineering content — how to restructure a README for a hardware tutorial, what sections a contributing guide needs, the PR review process — never surfaced.

## Input Scaffolding vs. Output Content

The [March 12 post](/2026/03/12/when-the-pipeline-publishes-its-own-autopsy.html) identified a failure mode: the pipeline couldn't distinguish between content it was *writing about* and content it was *generating*. That diagnosis was "output category confusion" — the model produces valid text that answers the wrong question.

The template leak is a different failure. The pipeline couldn't distinguish **input scaffolding** from **output content**. The contributing template wasn't something the pipeline wrote or summarized or diagnosed. It was raw material from the transcript — a document structure that existed in the input context, copied through to the output unchanged. No pass rewrote it. No pass summarized it. The template arrived as-is and left as-is, four passes of the pipeline acting as a very expensive `cat`.

The `_clean_claude_output` method in `generate_post.py` strips code fences, duplicate front matter, and preamble text. It looks for a `# ` heading and treats everything after it as the blog post:

```python
for i, line in enumerate(lines):
    if line.strip().startswith('# '):
        content = '\n'.join(lines[i:])
        break
```

The contributing template starts with `# Article Name <!-- omit from toc -->`. That matches. From the pipeline's perspective, a heading is a heading. It has no way to distinguish `Article Name` from a real title.

## Why the March 12 Fixes Didn't Catch This

The March 12 post proposed three defenses: a minimum word count, a structural check for narrative elements, and a classification gate. Here's what happened to each.

**Word count.** Would have caught it. The March 13 post was 50 words. The March 14 post was 62. A floor of 300 rejects both. But the check hadn't been deployed. The March 12 post documented proposed fixes, not implemented ones.

**Structural check.** Would have caught it too. The template contains no prose paragraphs, no developed argument, only placeholder italics and empty section headings. But same problem: proposed, not deployed.

**Classification gate.** A second Claude pass asking "is this a blog post?" Never built.

Three fixes proposed. Zero implemented. The template leaked through the same unguarded pipe.

## What the Title Tells You

The commit log:

```
961c72c Add blog post: Article Name <!-- omit from toc -->
cddf897 Add blog post: Article Name <!-- omit from toc -->
```

The `_extract_title` method pulls the first `# ` heading from the content. The `_generate_filename` method slugifies it. The git commit message interpolates it. At no point does anything ask: is `Article Name <!-- omit from toc -->` a plausible blog post title? The HTML comment is a markup instruction for a table-of-contents generator. It has no business in a title field. A blocklist checking for common placeholder strings — `Article Name`, `Title Here`, `Untitled`, `TODO` — or embedded HTML comments would have stopped both posts before they reached git.

## The Fix

Three changes close the gap that the March 12 post identified but didn't implement:

**A word count floor.** Any output under 300 words triggers a regeneration attempt. Every legitimate post in the archive exceeds 600. A 50-word template skeleton fails immediately.

**A placeholder blocklist for titles.** The `_extract_title` method rejects titles matching common scaffolding patterns: `Article Name`, `Title`, `Untitled`, strings containing HTML comments, and strings that are entirely placeholder text. A rejected title falls through to the date-based fallback, which at least produces an honest label.

**Structural validation before save.** The `save_post` method checks that the content contains at least two `##` headings, at least three prose paragraphs (lines over 40 characters that aren't headings or list items), and no placeholder markers like `*1 - 3 sentence section describing*`. A template skeleton fails all three.

These are heuristics, not guarantees. A sufficiently unusual post might trip the word count. A sufficiently elaborate template might pass the structural check. But the March 13 and 14 failures weren't edge cases — they were a 50-word template with italicized instructions for content that didn't exist. The checks don't need to be clever. They need to catch the obvious.

## The Pattern Across Two Weeks

March 3–6: the pipeline published its own editorial reasoning. March 12: the pipeline published its own diagnostic summary. March 13–14: the pipeline published raw input scaffolding.

Three different failure surfaces, one underlying gap: the pipeline has no validation that its output is actually a blog post. It checks that output *exists*. It checks that it starts with a heading. It wraps it in front matter and pushes to git. Whether the text between the heading and the front matter is a thousand words of narrative or six lines of placeholder italics — same code path, same outcome, same live site.

The proposed fixes keep getting documented in blog posts. The blog posts keep getting published by the unfixed pipeline. That loop breaks when the fixes land in `generate_post.py`, not in `_posts/`.