---
layout: post
title: "A Day of Yak Shaving: From Mouse Settings to MATLAB Extensions"
date: 2026-01-15
categories: [development, ai]
tags: [claude-code, javascript, git, automation, testing]
read_time: 4
word_count: 886
---

January 15th was one of those days where I set out to do one thing and ended up tumbling down a rabbit hole of configuration debugging, infrastructure setup, and the early stages of an ambitious new project. Classic developer day, really.

## The Great Mouse Mystery

It started innocently enough. My trackpad scrolling and pane selection weren't working in tmux, even though I had `set -g mouse on` in my config. Simple fix, right?

With Claude Code's help, I went on a systematic hunt through every possible configuration layer:

- Checked `~/.tmux.conf` (mouse was enabled)
- Verified tmux runtime settings with `tmux show-options -g mouse`
- Inspected shell configs (`.zshrc`, `.zprofile`)
- Dug through iTerm2's plist settings
- Confirmed DNS... wait, no, that was the other problem

After checking for nested tmux sessions, session-specific overrides, and even the `$TERM` variable, the investigation continued. Sometimes the most frustrating bugs are the ones where everything *looks* correct. The session transcript shows Claude methodically working through each layer of the config stack, which is exactly the kind of systematic debugging that's easy to skip when you're annoyed and just want your mouse to work.

## SSL Certificates and the Joy of DNS

Meanwhile, my blog at sebastianhondl.com was showing that dreaded "Your connection is not private" warning. The diagnosis was quick: GitHub Pages hadn't issued an SSL certificate yet, and the "Enforce HTTPS" checkbox was greyed out with the message "Unavailable for your site because the certificate has not yet been issued."

A quick DNS check confirmed the A records were pointing to the right GitHub Pages IPs:

```
185.199.109.153
185.199.110.153
185.199.111.153
185.199.108.153
```

The fix? Wait. Sometimes the most sophisticated debugging leads to the most anticlimactic solution. GitHub's Let's Encrypt integration just needed time to provision the certificate.

## Making AutoBlog Location-Independent

Here's where the day got more interesting. I realized I'd built a blog automation system that required my Mac to be awake at 6 AM every morning. Not ideal.

The solution Claude and I landed on: sync transcripts to GitHub after each Claude Code session, then let GitHub Actions handle the blog generation on a schedule. The architecture shift looks like this:

**Before:**
```
Mac (always on) → launchd at 6 AM → generate post → push
```

**After:**
```
Mac (whenever) → sync transcripts → GitHub
GitHub Actions (6 AM) → read transcripts → generate post → commit
```

This is the kind of infrastructure thinking that AI assistants excel at—taking a working but fragile system and helping redesign it for resilience. The key insight was recognizing that the transcripts already live locally at `~/transcript/`, so we just need to bridge them to somewhere cloud-accessible.

## The Main Event: Claude Code for MATLAB

The most exciting work of the day was kicking off a new project: a MATLAB add-on that brings Claude Code's capabilities directly into the MATLAB IDE.

The vision is ambitious:
- A side panel in MATLAB with a chat interface
- Backend powered by Claude Code
- Ability to write and execute MATLAB scripts
- GitHub integration
- (The stretch goal) Simulink interaction

Claude did extensive research on MATLAB's extension architecture, uncovering some promising approaches:

1. **ToolGroup Apps** - MATLAB's framework for docked figures with toolstrip interfaces
2. **Custom UI Components** (R2022a+) - Modular, reusable UI elements
3. **LLMs with MATLAB** - MathWorks' official library for LLM integration (already supports OpenAI, Ollama, etc.)

The Simulink question is particularly interesting. I wasn't sure if Simulink had a text representation that Claude could work with. Turns out it does—Simulink models can be exported to XML (`.slx` files are actually ZIP archives containing XML), and there's also SLX API for programmatic model manipulation. Whether this is practical for an AI assistant to work with is another question entirely.

The project is greenfield—the directory had nothing but Claude's session logs—so we spent time planning the architecture rather than writing code. Sometimes the best coding sessions involve zero code.

## Copying GitHub Issues at Scale

In a completely unrelated corner of my day, I needed to copy tutorial issues from one GitHub repository to another. Claude Code made quick work of this with the `gh` CLI:

```bash
# Get issue details from source repo
gh issue view 3 --repo Severson-Group/amdc-tutorial --json title,body

# Create in destination repo
gh issue create --repo Severson-Group/bp1 --title "..." --body "..."
```

17 issues copied, duplicates skipped. What would have been tedious manual work became a simple scripted operation.

## Takeaways

1. **Systematic debugging beats intuition.** When Claude Code checks every config layer methodically, it often finds the issue faster than my "I bet it's this" approach.

2. **Infrastructure fragility is worth addressing early.** Moving from "my laptop must be on" to "GitHub Actions handles it" is the kind of robustness improvement that pays dividends.

3. **Research before coding.** The MATLAB extension project benefited enormously from spending time understanding MATLAB's extension architecture before writing a single line of code.

4. **CLI tools are underrated.** The `gh` CLI for GitHub operations, combined with Claude Code's ability to orchestrate complex command sequences, makes batch operations trivial.

Some days you ship features. Other days you fix your mouse, wait for SSL certificates, and lay groundwork for future projects. Both kinds of days matter.