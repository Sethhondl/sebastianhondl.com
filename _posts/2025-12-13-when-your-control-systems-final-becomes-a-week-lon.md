---
layout: post
title: "When Your Control Systems Final Becomes a Week-Long Coding Sprint"
date: 2025-12-13
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 4
word_count: 836
---

Three days until my Motion Control final. The syllabus stared back at me: "Open-note exam. Maximum 10 double-sided pages." Ten pages to compress an entire semester—transfer functions, Z-transforms, digital filter implementations, stability criteria. Eleven lectures of dense PDFs. A stack of lab reports. And a growing sense of dread.

Then my phone buzzed. A Discord notification from my Minecraft server: "Villager was slain by Zombie." Then another. And another. My death announcement bot had developed an unfortunate enthusiasm for reporting every villager casualty in my automated trading hall.

Both problems landed on my desk the same afternoon. And both, it turned out, were exercises in the same fundamental skill: filtering signal from noise. The cheat sheet needed to compress dense technical content into scannable reference material. The bot needed to stop treating every mob death as breaking news. Even the third task I tackled that day—publishing my control systems coursework to GitHub—fit the theme. It was a day about organization, filtering, and getting the right information to the right audience.

## The Cheat Sheet Challenge

The constraints were non-negotiable: 20 PDF pages maximum when printed through Chrome Headless. The content had to span everything from basic sampling theory to advanced stability analysis.

This wasn't a summarization problem. It was an information architecture problem:

1. Parse dozens of PDF files, some too large to process in one pass
2. Extract technically dense content—transfer functions, Z-transforms, digital filter implementations
3. Organize everything into a printable format with optimal information density
4. Include reference tables (signed byte values from -256 to 256 for motor control commands)

The approach that worked: chunking large PDFs with overlap. For a 10-page document, read pages 1-6, then pages 5-10. That two-page overlap ensures continuity—critical when equations span page boundaries, which happens constantly in control systems coursework.

The final cheat sheet covered the full spectrum: sampling and reconstruction methods (ZOH and FOH), Z-transforms, discrete transfer functions, digital filter implementations (Direct Form I, II, Transposed), PID tuning in the discrete domain, state-space representations, and stability analysis using the Jury test and bilinear transform.

## The Villager Death Problem

The Discord notifications had started innocently enough. I'd built a bot to announce player deaths on our multiplayer server—useful information for the community. But by the fifteenth "Villager was slain by Zombie" notification in an hour, the problem was obvious.

The culprit lived in `minecraft_integration.py`:

```python
DEATH_PATTERN = re.compile(
    r'\[(\d{2}:\d{2}:\d{2})\] \[(?:Server thread|Async Chat Thread[^\]]*)/INFO\]: (\w+) (.+)'
)
```

Too greedy. This pattern matches any log line with a timestamp, thread info, and a single word followed by anything. "Villager was slain by Zombie" fits the pattern just as well as "Steve was slain by Creeper."

The bot already uses DynamoDB to track player sessions—recording joins and leaves. The fix was simple: validate the matched name against known players before broadcasting.

```python
if death_match:
    potential_player = death_match.group(2)
    if self._is_known_player(potential_player):
        # Broadcast to Discord
```

What about a player's first death before they're recorded? Not an issue—the bot watches for join events, so players are tracked the moment they connect, before they encounter anything dangerous.

The villagers now die in obscurity, as nature intended.

## Publishing Course Materials

The third task was straightforward: making my ME 5281 Feedback Control Systems coursework public on GitHub. Nine homework assignments with solutions, final exam materials, MATLAB files, lecture notes, and lab submissions.

Well-organized course materials with working solutions are genuinely valuable. The repository structure matters—clear folder names, a README explaining what each assignment covers, code that actually runs. Somewhere, a future student will find these materials when they're staring at their own syllabus, counting pages and panicking.

## What I Learned

**Chunking strategy matters.** Don't split large documents arbitrarily. Overlap your chunks to maintain context. This applies beyond PDFs—it works for long log files, large codebases, any sequential data where meaning spans boundaries.

**Regex patterns need constraints.** The villager bug is a classic: a pattern that works perfectly in testing, then fails in production. My regex matched exactly what I designed it to match—single-word entity names followed by death messages. I just hadn't considered that "Villager" is also a single word. Test against edge cases you didn't design for.

**Academic projects belong in public repos.** Future students and your future self will thank you.

## The Payoff

The cheat sheet alone would have taken days to compile manually. With Claude Code processing those PDFs and helping organize the content, it was an afternoon—and more comprehensive than anything I could have produced by hand.

Finals week is always about triage: what to study, what to skip, where to focus limited time. This session was about building tools that make that triage easier. A searchable cheat sheet. A bot that only reports what matters. A public repository that might save someone else a few hours of confusion.

That's the through-line for the day: making information accessible to the people who need it, when they need it. Including myself, three days before an exam.