---
layout: post
title: "From Scattered Notes to a Full GitHub Roadmap in Ten Minutes"
date: 2026-02-13
categories: [development, ai]
tags: [claude-code, git, automation, testing]
read_time: 4
word_count: 861
---

Twenty issues. Six project phases. One session with the `gh` CLI and Claude Code. That's what it took to turn a semester-long motor drive project from "I should really organize this" into a fully linked, dependency-mapped GitHub roadmap.

## The Project That Needed a Map

I'm working on BP1, a motor demonstrator project in the Severson-Group research lab at UMN. The platform is AMDC (Advanced Motor Drive Controller)—hardware used for prototyping power electronics and motor control systems. The work spans everything from completing firmware tutorials to running a physical demonstrator with real motor hardware.

The problem wasn't ambition. It was visibility. I had tasks scattered across my notes, a mental model of dependencies that existed only in my head, and a GitHub repository with a handful of unstructured issues. When your project crosses six distinct phases—from learning a platform to operating hardware—you need something better than memory.

## From Phases to Issues in Minutes

The six phases mapped out like this:

- **T1: AMDC Tutorials** — Build foundational firmware knowledge through the platform's official tutorials
- **T2: Timing and Sensors** — Work through sensor integration and timing configuration
- **T3: Current Control** — Build the inner control loop for motor phase currents
- **T4: Hardware Setup** — Physical board assembly, wiring, and power stage configuration
- **T5: System Integration** — Connect firmware to hardware with safety checks
- **T6: Demonstrator Operation** — Run the actual motor and validate performance

Each phase became a roadmap issue. Then came the part that would have eaten an hour manually: creating fourteen linked sub-task issues, breaking each phase into concrete work items, and wiring them all into GitHub project board #51.

The `gh` CLI made this possible without touching a browser. Claude Code handled the mechanics—formatting issue bodies with task lists, adding labels, linking sub-issues to their parent roadmap issues, and assigning everything to the correct project board columns. I stayed focused on whether the technical breakdown was actually right.

## Why CLI Beats the Browser for This

Creating a single GitHub issue in the browser is fine. Creating twenty interlinked issues with consistent formatting, cross-references, and project board assignments is miserable. You end up copying IDs between tabs, reformatting markdown, clicking through dropdown menus, and losing your train of thought every time you switch from "what should this task contain" to "which button do I click."

The `gh issue create` command strips all of that away. Combined with Claude Code composing the issue bodies, the workflow became conversational:

> "Create a roadmap issue for T3: Current Control. It depends on T2 completion. Sub-tasks are: implement Clarke/Park transforms, build the PI current regulators, tune gains with step response, and validate against simulation."

Claude translated that into properly formatted GitHub markdown with task checkboxes, linked it to the T2 roadmap issue, and created each sub-task as its own trackable issue. The entire T3 phase went from verbal description to four linked issues in about ninety seconds.

## Quick State Checks Along the Way

Between creating roadmap issues, I needed to check whether a branch already existed for the timing and sensors tutorial. A quick `gh` query confirmed the branch status and saved me from either duplicating work or starting from scratch when partial progress was already there.

It's a small thing, but it's representative. Half of project management is knowing what state things are in before you start making changes. The CLI turns that into a five-second check instead of a multi-click scavenger hunt through the GitHub UI.

## What Twenty Structured Issues Actually Buy You

With the roadmap in place, three things changed immediately.

**Dependencies became visible.** T4 (hardware setup) doesn't block T1–T3 (firmware work), but T5 (integration) blocks on both. Seeing that on a project board means I can parallel-track firmware tutorials and hardware prep without second-guessing the sequencing.

**Progress became measurable.** Each sub-task issue is a checkbox on its parent roadmap issue. Completing "implement Clarke/Park transforms" automatically updates T3's progress. No manual status updates required.

**Scope became concrete.** "Build a motor demonstrator" is overwhelming. "Complete the ADC current sensing tutorial notebook" is a single afternoon. Fourteen specific sub-tasks turned an intimidating semester-long project into a sequence of manageable sessions.

## What I'd Take Away from This

**Use the CLI for batch GitHub operations.** Anything involving more than three interlinked issues is faster through `gh` than through the web interface. The savings compound fast when you need consistent formatting and cross-references.

**Let AI handle structure while you handle substance.** I described each phase in plain language. Claude turned it into GitHub markdown with task lists, labels, and links. That division of labor kept me thinking about project architecture instead of syntax.

**Front-load your roadmap before writing code.** Ten minutes of structured planning created a project board that will guide weeks of implementation. Those roadmap issues aren't overhead—they're the map that keeps you from wandering when phases start overlapping and the work gets complex.

Tomorrow, T1 begins. The tutorials are queued, the issues are linked, and for the first time this semester, the whole path from here to a running motor is visible.