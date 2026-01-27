---
layout: post
title: "When Your Automation Works Everywhere Except Where It Matters"
date: 2026-01-27
categories: [development, ai]
tags: [claude-code, javascript, git, automation, testing]
read_time: 3
word_count: 612
---

My automated blogging system ran faithfully every morning for ten days straight. It also failed every single time. I only noticed when I realized my website hadn't updated in over a week.

## The Mystery of the Missing Posts

The AutoBlog system was supposed to generate daily posts from my Claude Code session transcripts. I'd built it, tested it, watched it work—then apparently forgot about it.

When I finally checked the logs, I found something maddening: the system *was* running every day. It just couldn't finish the job.

```
Pass 1/4: Generating draft...
Claude CLI not found
...
Generation failed: Failed to generate draft
```

Ten days of this. Every morning at 6 AM, faithfully failing.

## The PATH Problem

The root cause was embarrassingly predictable. My blog generation script calls the Claude CLI to write posts. When I run it manually from my terminal, everything works because my shell knows where to find `claude`—it's installed via npm under my NVM directory.

But launchd jobs don't inherit your shell environment. They run in a minimal, sanitized context with a PATH that looked like this:

```
/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin
```

Meanwhile, the Claude CLI lives here:

```
/Users/sethhondl/.nvm/versions/node/v22.9.0/bin/claude
```

The automation couldn't see the tool it needed. It tried, failed, logged the error, and moved on. Every single day.

## Archaeology of Broken Automation

Digging through the commit history revealed how this fragility developed. The system originally used GitHub Actions, running in a controlled environment where I'd explicitly configured all dependencies. At some point I switched to local launchd scheduling—probably to avoid rate limits or test changes faster.

That transition required the Claude CLI to be accessible from launchd's environment, which I never configured. The GitHub Actions workflow got deleted. The launchd job was modified to run on login. A login trigger script was added to backfill missed days.

Each change made sense in isolation. Together, they created a system that looked healthy from every angle except the one that mattered: actually producing output.

## The Fix

Once I understood the problem, the solution took thirty seconds:

```xml
<key>PATH</key>
<string>/Users/sethhondl/.nvm/versions/node/v22.9.0/bin:/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
```

Add the NVM bin directory to the launchd PATH, reload the job, done.

## Other Work Today

Beyond the AutoBlog debugging, I did some housekeeping on PenguinCAM—a CAM tool for robotics that I contribute to. The local repo had accumulated feature branches from old experiments, so I reset everything to match upstream main and cleared out the cruft. Five branches deleted, back to a clean slate.

I also continued work on a voltage source inverter tutorial for my embedded systems class. The current step involves oscilloscope measurements to verify three-phase current waveforms—checking that the phases are separated by 120 degrees and measuring the delay between voltage and current. It's the kind of hands-on hardware debugging that reminds me why I got into engineering in the first place.

## Making Failure Visible

This experience reinforced something I already knew but apparently needed to relearn: automation should fail loudly or succeed visibly. Silent failure is the worst outcome.

My blog system dutifully logged its errors to `/tmp/autoblog.err`, but nothing prompted me to check those logs. Transcripts kept syncing, commits kept happening, and from the outside everything looked healthy. Only the absence of new posts hinted at a problem—and I wasn't looking closely enough to notice.

The next improvement is obvious: make the system complain when it can't do its job. For personal automation, I don't need enterprise-grade monitoring. Just a notification when a scheduled job fails for multiple consecutive days.

Until then, at least the PATH is fixed. Tomorrow's post should appear on schedule.

We'll see.