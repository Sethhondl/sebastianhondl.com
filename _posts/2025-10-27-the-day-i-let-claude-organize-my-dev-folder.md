---
layout: post
title: "The Day I Let Claude Organize My Dev Folder"
date: 2025-10-27
categories: [development, ai]
tags: [claude-code, python, git, automation, api]
read_time: 4
word_count: 847
---

There's a particular kind of chaos that builds up in a personal projects directory. You know the one—where `ShapeForge`, `ShapeForge-Clean`, and `ShapeForge-backup-20250621-172754` all coexist peacefully, each one a monument to the moment you thought "I should probably make a backup before I break this."

Today I finally did something about it.

## The Problem With Personal Projects

My `~/dev` folder had accumulated the digital equivalent of a junk drawer. School projects mixed with side projects, loose PDFs floating around, and three versions of the same project because I couldn't remember which one actually worked.

For context: Claude Code is an AI-powered command-line tool that can read, write, and organize files through natural conversation. Instead of writing shell scripts or manually dragging files around in Finder, I describe what I want and Claude executes it—asking clarifying questions along the way.

Here's what Claude found when it took stock:

```
drwxr-xr-x  AutoBlog
drwxr-xr-x  ShapeForge
drwxr-xr-x  ShapeForge-Clean
drwxr-xr-x  ShapeForge-backup-20250621-172754
drwxr-xr-x  ME4031WFinalProject
drwxr-xr-x  umnClasses
drwxr-xr-x  highSpeedTrebuchet
-rw-r--r--  Stirling Engine Mathematical Model.pdf
-rw-r--r--  pep_band_schedule.csv
-rw-r--r--  Keys.rtf
```

The ShapeForge situation alone told the whole story. Three copies, no clear indicator of which was current. Last week this cost me twenty minutes when I made edits to the wrong version and had to manually diff and merge.

And that `Keys.rtf` file? API credentials I'd dumped there "temporarily" six months ago. Not exactly best practices.

## The Conversation That Mattered

What made this session interesting wasn't the mechanics of moving files around. It was the back-and-forth about *how* to organize. Claude didn't just ask "where should I put these files?"—it asked questions that forced me to articulate my own mental model.

**"What should I do with the ShapeForge duplicates?"** This one made me actually investigate. I had Claude check the git status and last modified dates across all three. Turns out `ShapeForge-Clean` was my active version—I'd created it after a messy merge conflict and had been working there ever since. The original `ShapeForge` had uncommitted changes from three months ago that I'd completely forgotten about. The backup was just noise.

**"How should I organize—by project type, by status, or by technology?"** I went with status. The distinction between "things I'm actively working on" and "things I finished for a class" matters more to me than whether something uses Python or MATLAB.

**"What about those loose files?"** This is where most organization attempts fall apart. The temptation is to create a `misc` folder, which just becomes a new junk drawer. Instead, I had Claude trace each file to its related project. The Stirling Engine PDF was reference material for a thermodynamics project. The pep band schedule belonged with an app I'd built to track rehearsals. Everything had a home—I'd just been too lazy to put things away.

For `Keys.rtf`, I didn't just move it—I deleted it entirely after transferring the credentials to my system keychain. Claude walked me through the macOS `security` command to store sensitive values properly. Five minutes of work I'd been putting off for months.

## The First Hiccup

The reorganization wasn't entirely smooth. When Claude moved the ShapeForge projects, it didn't account for the fact that `ShapeForge-Clean` had a git remote still pointing to a repo named `ShapeForge`. After renaming the folder, my next `git push` failed with a cryptic error about the remote not matching.

This would have derailed me for an hour if I'd been doing the reorganization manually at 11 PM. Instead, Claude diagnosed the issue immediately—the remote URL contained the old path—and offered to update the git config. A thirty-second fix, but only because the tool that caused the problem was also the tool that could debug it.

## The Result

The final structure reflects how I actually think about my work:

```
~/dev/
├── active-projects/
│   ├── AutoBlog
│   ├── ShapeForge
│   └── PepBandMusicApp
├── school/
│   ├── umnClasses/
│   └── ME4031WFinalProject
└── archive/
    ├── basicInventoryApp
    └── highSpeedTrebuchet
```

The duplicates are gone. Every loose file found a home. When I need to find something now, I know exactly which folder to check based on one question: "Am I still working on this?"

## What This Session Revealed

The folder organization took maybe ten minutes of actual execution time. But the value wasn't in the file moves—it was in the conversation that preceded them.

Left to my own devices, I would have procrastinated on this forever, or done a half-hearted job that created new problems. The duplicates would have lingered because deleting them felt risky. The loose files would have ended up in `~/dev/misc`. The credentials file would have stayed right where it was.

Having an assistant that asks "what should I do with this?" forced me to make decisions I'd been avoiding. And having that assistant execute immediately—before I could second-guess myself or get distracted—meant the decisions actually stuck.

The chaos in my dev folder wasn't a technical problem. It was a decision-avoidance problem wearing technical clothing. Sometimes the best thing a tool can do is make you finally answer the questions you've been ignoring.