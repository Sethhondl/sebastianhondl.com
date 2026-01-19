---
layout: post
title: "Three Scales of Verification: What a 22-Degree Discrepancy Taught Me About Trusting My Tools"
date: 2025-11-18
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 5
word_count: 1065
---

My Bode plot showed 55 degrees of phase margin. MATLAB's `margin()` function reported 33. I stared at the screen for a full minute, convinced I'd made a calculation error somewhere.

I hadn't. Both numbers were correct—they just described different crossovers on the same frequency response curve. That 22-degree gap became the thread I pulled for the rest of the day, and it unraveled assumptions I'd been making across three completely different projects.

This post is about verification at three scales: the micro-level of understanding a single function's behavior, the meso-level of trusting infrastructure outputs, and the macro-level of auditing an entire codebase before publication.

## Micro: When Your Tools Are Right But Your Mental Model Is Wrong

### The Six-Bar Linkage Problem

I was optimizing a six-bar mechanical linkage—the kind of mechanism you see in windshield wipers or excavator bucket arms. These systems use connected rigid bars to transform simple input motion into complex output paths. My goal was to find the right bar lengths and pivot positions to make the output follow a specific trajectory.

The optimization code I was reviewing used weighted constraints to penalize designs that violated physical requirements. One constraint caught my attention:

> Penalize angular velocity above threshold by 5,000,000

Five million. For context, a reasonable weight for this type of constraint would be somewhere between 10 and 1,000, depending on how critical the requirement is. A weight of 5M essentially tells the optimizer "avoid this at all costs, even if it means producing a terrible design in every other way."

I asked Claude to analyze the constraint code I'd shared. The response clarified something I should have realized sooner: with weights this extreme, the optimizer wasn't finding good linkage designs—it was finding designs that barely violated the angular velocity constraint while ignoring everything else.

The fix was straightforward: rebalance the weights to something sane. But the lesson was about reading code critically. Just because an optimizer converges doesn't mean it found what you wanted.

### The Phase Margin Mystery

Back to that 22-degree discrepancy. I'd assumed `margin()` reported the phase margin at the gain crossover frequency—the point where the loop gain equals 1. What I'd missed was that my system had *multiple* crossovers, and `margin()` reports the margin at the *first* crossover only.

**What I thought:** Single crossover at ~2 rad/s, phase margin of 55°.

**What the solution showed:** Multiple crossovers, with the first occurring earlier at a frequency where phase margin was only 33°.

**What I now understand:** `margin()` is conservative by design. It reports the worst-case (first) crossover because that's where instability would first appear as you increase gain.

The Bode plot wasn't lying. `margin()` wasn't lying. I just hadn't understood which question each tool was answering.

## Meso: When Your Infrastructure Silently Drops Information

The second project of the day was a Minecraft server running on AWS. I'd built a Discord bot that reports server status: player count, uptime, that kind of thing.

The bot queries a status API that wraps the server's RCON interface. Everything worked in testing. In production, the player count occasionally showed zero when players were clearly online.

The issue: the status endpoint returned stale data when the server was under load. The bot faithfully reported what it received. There was no indication that the data was 45 seconds old—it just looked like nobody was online.

I added a timestamp field to the response and a staleness warning in the Discord embed. Simple fix, but I'd burned an hour chasing phantom bugs in the bot logic when the bug was upstream in data freshness.

This is verification at the infrastructure level: don't just check if you're getting data, check if the data is current.

## Macro: Security Auditing Before You Publish

The third project was this blog itself. AutoBlog automatically publishes posts from my coding sessions. Before pushing the first real post, I realized I should probably check what I was about to publish to the internet.

This is where publishing becomes a forcing function for security hygiene. I wasn't just publishing code—I was publishing transcripts of sessions that might reference credentials, API keys, or internal infrastructure.

I ran a security scan using Claude and found two concrete issues:

1. **Discord bot token** — A test session included the full token in a debug log. Publishing that would let anyone hijack the bot.

2. **RCON password** — The Minecraft server's remote console password appeared in a configuration snippet. Not catastrophic for a game server, but certainly not something to broadcast.

Neither made it into the final post, but only because I looked. The pipeline now includes a pre-publish scan for anything that looks like a secret.

## The Pattern Across Scales

Here's what I noticed looking back at the day:

| Scale | Project | Assumption | Reality |
|-------|---------|------------|---------|
| Micro | Control systems | `margin()` reports the margin I care about | It reports the first crossover, which may not be the one you're analyzing |
| Meso | AWS/Discord | If the API returns data, it's current | Stale data looks identical to fresh data without explicit timestamps |
| Macro | AutoBlog | My transcripts are safe to publish | They contain credentials and internal details that require scrubbing |

In each case, I had a working system that produced outputs I didn't fully understand. The tools weren't broken. My verification was incomplete.

## Takeaways

**Check your tools' assumptions, not just their outputs.** When MATLAB or any tool gives you a number, understand what question it's answering. Documentation exists for a reason.

**Timestamps are metadata, not optional.** Any data flowing between services should carry information about when it was generated. "Trust but verify" requires something to verify against.

**Publishing is the best security audit.** Nothing motivates a thorough review like the prospect of your credentials appearing on a public website. Build the review into the pipeline, not into your memory.

The 22-degree discrepancy that started my day was never a bug. It was a gap between what I asked and what I thought I asked. That same gap appeared in two other projects before dinner. It'll probably appear again tomorrow.

The only reliable fix is to keep asking: what did this tool actually tell me, and is that the same as what I wanted to know?

---

*This post was generated from my Claude Code sessions using [AutoBlog](https://github.com/sethhondl/AutoBlog).*
