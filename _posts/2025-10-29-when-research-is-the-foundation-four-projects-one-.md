---
layout: post
title: "When Research Is the Foundation: Four Projects, One Day, One Pattern"
date: 2025-10-29
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 5
word_count: 1113
---

Some days with Claude Code are about grinding through implementation. Today was different. Today was about research, architecture decisions, and discovering that the hardest part of building something new is figuring out what already exists—and accepting that there are no shortcuts through that discovery process.

## The Google Keep Exodus

The day started with a deceptively simple request: pull all my Google Keep notes down and convert them to markdown files. I've accumulated hundreds of notes over the years—project ideas, meeting notes, random thoughts—and I want them in plain text files I actually control, not locked in Google's ecosystem.

How hard could it be?

Turns out, Google doesn't provide an official API for Keep. At all. This meant diving into the unofficial `gkeepapi` library, which reverse-engineers Google's internal endpoints. Claude laid out the landscape clearly:

```python
# The unofficial but most reliable approach
import gkeepapi
keep = gkeepapi.Keep()
keep.login('your_email@gmail.com', 'app_password')
```

The research phase uncovered critical details I wouldn't have found quickly on my own:
- App Passwords require 2FA to be enabled first
- The library could break anytime Google changes their internal API
- Google Takeout exists as an official (but manual) alternative

Claude structured the options along clear axes: reliability vs. real-time access, official vs. unofficial, automated vs. manual. That framework made my decision straightforward—I'll use `gkeepapi` for the initial bulk export, with Takeout as a fallback if authentication breaks—even though the implementation itself will be complex.

## The Lab Report That Was Already Done

While setting up the Keep authentication, I turned to a different kind of task: polishing a motion control lab report that I thought needed significant work. The Bode plots weren't using logarithmic x-axis scaling, which is standard for frequency response analysis.

But here's what actually happened: Claude analyzed my existing `lab6_postlab_report.md` and found it was already 627 lines with all required sections complete. The Bode plot fix itself was trivial:

```matlab
% Just semilogx instead of plot
semilogx(omega1, mag1_dB, 'o-', 'LineWidth', 2, 'MarkerSize', 8, ...
    'DisplayName', 'Plant 1 (No Mass)', 'Color', [0, 0.4470, 0.7410]);
```

The real value wasn't the two-line fix. It was discovering I was closer to done than I thought. I'd been procrastinating on this report, assuming it needed major work. It didn't. The "10% that takes 90% of the time" turned out to be 2% that took 5 minutes once I actually looked.

This happens more often than I expected in AI-assisted development: the tool identifies that your mental model of "how much work remains" is wrong. Sometimes dramatically wrong.

## The Statbotics Dead End

The most ambitious project of the day was attempting to modify the Statbotics FRC analytics platform. For those unfamiliar, FRC (FIRST Robotics Competition) uses an EPA (Expected Points Added) metric to rate team performance—essentially a power ranking that predicts match outcomes. My goal: instead of using predetermined alliance assignments, dynamically balance teams to create competitive practice matches.

Claude dove deep into the repository structure and returned with a finding that killed the project as I'd conceived it: **Statbotics doesn't create alliance assignments at all.** It's read-only for match schedules, importing everything from The Blue Alliance API.

This meant my modification couldn't be a simple fork. It would require:
1. A new scheduling algorithm layer
2. Custom match generation logic
3. Integration with the existing EPA calculation engine

I spent the rest of the session understanding the EPA architecture—how it sums team ratings, applies opponent-strength adjustments, and calculates win probability. Fascinating, but ultimately not actionable for my use case.

Here's the honest assessment: I probably should have asked "does Statbotics generate match schedules?" before diving into the codebase. That's a five-minute question that would have revealed the fundamental mismatch. Instead, I spent an hour learning how EPA works, which is interesting but doesn't get me closer to balanced practice matches.

The path forward, if I pursue this, is building a standalone tool that consumes EPA data rather than forking Statbotics. That's a much larger project. For now, it's shelved.

## CSV to Calendar: Why Two Formats Create Real Pain

The final project tackled calendar integration, and this one came with the day's clearest motivation. I manage two performance group calendars—Pep Band and RCR Winds—each exported from different scheduling systems with different CSV formats. Every month, I manually transcribe events into Google Calendar. It's tedious and error-prone.

The Pep Band format:
```
Event #,Day,Date,Call Time,Event Time,Type,Event,Location,Group,Conductor,Notes
```

The RCR Winds format uses entirely different column names and date formatting. Without normalization, I'd need separate upload scripts for each, and adding a third calendar later would mean a third script.

Claude's approach was to create an intermediate normalized format:

```python
# Standard format all CSVs convert to before upload
normalized_fields = [
    'summary',      # Event title
    'start_date',   # YYYY-MM-DD
    'start_time',   # HH:MM (24-hour)
    'end_time',     # HH:MM (24-hour)  
    'location',
    'description',
    'calendar_name' # Which calendar to target
]
```

This normalization layer means adding new calendar formats later just requires writing a new parser—the Google Calendar upload logic stays untouched. It's the classic adapter pattern, but seeing it applied to my specific messy data made the abstraction concrete.

## What Research Days Actually Produce

Looking back at these four sessions, I notice a pattern I hadn't articulated before: research days don't just delay implementation, they prevent wasted implementation.

The Google Keep session stopped me from writing code against an API that might not suit my actual needs. The lab report session stopped me from rewriting something that was already complete. The Statbotics session stopped me from forking a project that fundamentally couldn't do what I wanted. Only the calendar project moved toward implementation, and only because the research confirmed the approach was sound.

That's three out of four sessions where the most productive outcome was *not* writing code.

I used to feel guilty about days like this. No commits, no shipped features, nothing to show. But the alternative—charging into implementation without understanding the landscape—leads to the kind of abandoned half-finished projects that litter my `~/projects` folder.

The question I'm still working out: how do I know when research is complete? When does "understanding the system" become "procrastinating on building"? Today, the signals were clear—either I hit a hard blocker (Statbotics), confirmed completion (lab report), or had a concrete architecture (calendars). But I suspect there are days where I research past the point of usefulness.

Tomorrow, I'll implement the calendar normalization layer. The Keep exporter will wait until I've tested the authentication flow. The Statbotics idea might never become code, and that's fine.

Not every research day produces a roadmap. Some produce a "do not enter" sign. That's valuable too.