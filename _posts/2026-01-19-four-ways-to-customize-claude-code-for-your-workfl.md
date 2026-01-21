---
layout: post
title: "Four Ways to Customize Claude Code for Your Workflow"
date: 2026-01-19
categories: [development, ai]
tags: [claude-code, git, automation, testing, debugging]
read_time: 4
word_count: 812
---

Every time you repeat yourself to a tool, that's friction. Today I focused on eliminating that friction—starting with the simplest customizations and building toward more sophisticated ones.

## A Faster Way to Say "I Trust You"

Claude Code asks for permission before running shell commands, editing files, or taking other potentially destructive actions. Sensible behavior. But when I'm working in a sandboxed environment or on a personal project where I've already reviewed Claude's approach, those confirmation prompts slow things down.

The `--dangerously-skip-permissions` flag tells Claude to proceed without asking. The name is intentionally alarming—a reminder that you're taking responsibility for whatever happens next. I created a shell alias to make this faster:

```bash
alias cldyo='claude --dangerously-skip-permissions'
```

The "yo" stands for YOLO, because that's the energy. Use this only in environments where you trust what's happening: personal projects, throwaway branches, containerized setups. Never in production, never with unfamiliar code, never when you haven't reviewed the plan first.

## Teaching Claude Your Standards

I keep running into the same situation: I finish a feature, ask Claude to commit it, and then remember I need to explain our team's commit message conventions. Again. The Severson Group has detailed Git etiquette guidelines in a markdown file, and I was essentially re-teaching them every session.

Claude Code's skill system solves this. Skills are reusable instructions stored in `.claude/skills/` as markdown files with YAML frontmatter specifying when they should activate. They're persistent context that loads itself.

The skill system watches for patterns in what you're doing—certain file types, certain tools, certain topics. For Git workflows, I created a skill that activates whenever commit-related commands come up:

```yaml
---
triggers:
  - git commit
  - commit message
  - git push
---

# Git Etiquette Standards

[The actual guidelines from the team's markdown file]
```

Before: I'd type "commit these changes" and Claude would generate a generic message. I'd explain our format, Claude would regenerate, we'd iterate.

After: The guidelines are already loaded. Claude's first attempt follows the standards because it knows what they are.

If you find yourself explaining the same thing repeatedly, that's a signal to create a skill.

## Grounding Agents in Your Actual Codebase

I've been using a custom agent called feature-interviewer that helps clarify requirements before implementation begins. It asks Socratic questions about edge cases, user needs, and acceptance criteria. The problem: it asked these questions in a vacuum, unaware of existing patterns or infrastructure.

The fix was straightforward. Before the agent starts its interview, it now explores the relevant parts of the codebase. If I say "I want to add authentication," the agent first looks at how routing works, what middleware patterns exist, and whether there's any existing auth code. Then it asks questions informed by that context.

Instead of generic questions like "How should authentication work?", the agent now asks things like "I see you're using Express middleware for rate limiting—should authentication follow the same pattern?" The questions become useful because they're grounded in reality.

## Experimenting with Job Application Workflows

This one is earlier-stage—more exploration than finished workflow. When applying for jobs on Handshake, I want to customize my resume and cover letter for each posting without manually rewriting everything.

The current approach involves copying the job posting into Claude, providing my base resume, and asking for tailored versions that emphasize relevant experience. Claude reads the job requirements and suggests which projects to highlight, which skills to emphasize, and how to frame experience for that specific role.

What I haven't solved: the feedback loop is slow. I can't easily tell whether the customizations improve response rates without running the experiment over many applications. And the tailoring sometimes overreaches—emphasizing a skill I barely have because the job posting mentioned it.

The next step is tracking which versions lead to interviews, but that requires patience and data I don't have yet.

## What This Adds Up To

None of these customizations is revolutionary on its own. An alias saves a few keystrokes. A skill avoids one repeated explanation. A smarter agent asks better questions.

But they compound. Each small friction removed makes the next session smoother. The Git skill means I think about commits less. The faster permissions flag means I context-switch less. The grounded agent means fewer clarifying questions later.

The pattern worth noticing: most of these came from irritation. I got annoyed at repeating something, so I automated it. I got frustrated with generic questions, so I added context. Irritation is signal.

## Try This Yourself

Pick one thing you've explained to Claude more than twice this week. Write it down in a markdown file with clear instructions. Save it to `.claude/skills/` with a frontmatter trigger that matches when you'd need that information. Use it for a few days.

Start with what annoys you. End with one less thing to think about.