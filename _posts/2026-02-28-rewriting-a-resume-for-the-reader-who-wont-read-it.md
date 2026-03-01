---
layout: post
title: "Rewriting a Resume for the Reader Who Won't Read It"
date: 2026-02-28
categories: [development, ai]
tags: [claude-code, python, git, automation, testing]
read_time: 4
word_count: 895
---

---
layout: post
title: "Rewriting a Resume for the Reader Who Won't Read It"
date: 2026-03-01
categories: [development, ai]
tags: [claude-code, writing, career, applications]
read_time: 4
word_count: 950
---

Most of my recent posts are about engineering — [firmware debugging](/2026/02/27/reading-someone-elses-code-to-build-a-hardware-che.html), [robot programming](/2026/02/25/writing-robot-code-before-touching-the-robot.html), [compressing months of analysis into six tables](/2026/02/24/three-review-comments-and-an-appendix-from-scratch.html). Today the subject was different but the task was the same: take a fixed set of facts and reformat them for a reader who will spend seconds on the page.

Two sessions. One was rebuilding a resume. The other was writing a 250-word application for a startup program. Both were exercises in layout as argument — deciding what goes first, what gets cut, and what the reader's eye hits in the three seconds before they decide to keep reading or move on.

## The Most Relevant Experience Was Buried on Page Two

The resume had a structural problem. Work experience was listed chronologically, which meant the most recent role — independent engineering projects, the work I do now — sat at the top. That sounds correct until you consider who's reading it. An HR screener or an applicant tracking system scanning for keywords doesn't parse a resume like a narrative. They scan. Top to bottom, left to right, with diminishing attention at every line.

The role that best matched the jobs I'm targeting — process engineering at Veolia, an environmental services company — was halfway down the page. A hiring manager scanning for industry experience would hit two sections of independent work before finding the role where I'd actually operated in a plant environment, managed capital projects, and worked inside a regulated industry. The most relevant credential was in the least visible position.

Moving Veolia to the top wasn't cosmetic. It reframed the entire document. With industrial experience leading, the independent projects that followed read as "engineer who left industry to build things" rather than "independent developer who once had an industry job." Same facts. Different story. The difference is which sentence the reader constructs in their head during the first pass.

I also added Anderson Labs — a research position I'd undersold on previous versions — and regrouped the skills section. Technical skills had been a flat list: Python, MATLAB, SolidWorks, Git, machine learning. Flat lists are easy to write and hard to scan. Grouping them by domain — programming languages, engineering tools, frameworks — gives the ATS something to match against and gives the human reader a structure that says "this person thinks in categories, not bullet points."

## 250 Words for Someone Who Reads Thousands

The second session was an application for the a16z Speedrun program — a startup accelerator run by Andreessen Horowitz that accepts founders building companies from scratch over a compressed timeline. The application asked for 250 words about what I'm building and why.

The project is ShapeForge, a parametric CAD tool that generates manufacturing-ready 3D models from text descriptions. You describe a part — "a mounting bracket with four M6 bolt holes on a 50mm square pattern, 3mm wall thickness, with a fillet at the base" — and ShapeForge produces a solid model with the geometry, tolerances, and export formats that a machine shop or 3D printer expects. It fills the gap between the engineer who knows exactly what they need and the CAD software that requires thirty minutes of mouse clicks to produce it.

Writing 250 words for a venture audience is a different compression problem than a resume but the same underlying exercise. A partner reviewing thousands of applications will spend less time on my paragraph than an HR screener spends on a resume. Every sentence has to either establish what ShapeForge does, why it matters, or why I'm the person building it. There's no room for a fourth category.

The resume version of my background emphasizes industry experience and technical breadth. The application version emphasizes the specific intersection of mechanical engineering and AI tooling that makes ShapeForge credible from a credible builder. Same career, same projects, different emphasis — because the reader's question is different. A hiring manager asks "can this person do the job?" A startup investor asks "can this person build the thing?"

## Same Facts, Different Reader

The interesting realization wasn't that resumes and applications require different formatting. That's obvious. It's that the formatting *is* the argument.

A chronological resume argues "here's what I've done, in order." A resume with Veolia at the top argues "I'm an industry engineer." Moving one section changed the thesis of the document without changing a single fact. The a16z application makes its argument about builder credibility by selecting three details from a career and omitting everything else. What's absent is as much a choice as what's present.

This is the same problem I hit when [compressing months of analysis into an appendix](/2026/02/24/three-review-comments-and-an-appendix-from-scratch.html). The source material — my career, the engineering analyses, the project history — is fixed. The output format depends entirely on who's reading and what they need to decide. An appendix table, a resume, a 250-word application, and a blog post are four different projections of the same underlying data.

The resume is submitted. The application is submitted. Both will be read in under ten seconds by someone deciding whether to keep reading. The only thing I control is what those ten seconds contain.