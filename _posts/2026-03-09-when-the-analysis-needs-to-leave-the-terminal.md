---
layout: post
title: "When the Analysis Needs to Leave the Terminal"
date: 2026-03-09
categories: [development, ai]
tags: [claude-code, testing, api, debugging]
read_time: 4
word_count: 902
---

Today had three sessions that looked unrelated until they didn't. An OSHA terminology correction for a presentation slide. Three SVG schematics for a structural analysis report. A single slide summarizing a year of bearingless motor research. Each one was the same problem: I had the right numbers, and now I needed someone else to understand them without running the simulation.

## The Word That Changes the Slide

The presentation included a caption referencing "OSHA guidelines for fall protection." The phrase sounded right. It wasn't. OSHA's fall protection requirements are codified in 29 CFR 1926 Subpart M — they're regulations, not guidelines. Guidelines are non-binding recommendations. Regulations carry the force of law, with specific compliance thresholds and enforceable penalties.

In a technical report, nobody notices the difference. In a slide shown to a room that includes safety professionals, using "guidelines" instead of "regulations" signals that the presenter doesn't understand the regulatory framework they're citing. The decimal point in the load calculation matters less than this one word in the caption. A wrong number looks like a math error. A wrong regulatory term looks like a misunderstanding of the field.

The fix was five characters. The research to confirm which word was correct took twenty minutes of reading OSHA's own documentation hierarchy. That's the ratio for compliance-adjacent work: seconds to implement, minutes to verify.

## One Drawing That Carries the Story

The structural analysis needed SVG schematics — simplified vector drawings that could sit alongside the calculations in the report. Three were on the list: push-out load limits on the anchor assembly, base sliding under lateral force, and a free body diagram of the combined force analysis.

I started building all three in parallel and realized halfway through that the free body diagram was doing the real work. The push-out and base-sliding drawings were essentially labeled arrows on rectangles — they showed individual load paths but didn't connect them. The FBD showed all forces acting on the assembly simultaneously: the lateral push-out load at the anchor point, the sliding friction at the base, the reaction moment at the bolted connection, and gravity through the center of mass.

The design decisions outweighed the code complexity. Where to place the force arrows so they didn't overlap. How to indicate the ground reaction without cluttering the base. Whether to show the bolt pattern as individual fasteners or as a single reaction point. Each choice was about what the reader needs to see first versus what they can infer.

The push-out and base-sliding schematics became supporting references — smaller, simpler, tucked into the appendix. The FBD carried the narrative in the main body. Three drawings planned, one that mattered, two that supported it.

## A Year of Research on One Slide

The 3-minute thesis slide was a different design problem entirely. A year of bearingless motor research — simulation infrastructure, experimental validation, control algorithm development — compressed into a single visual that has to work in 180 seconds of narration.

The visual arc I landed on: four quadrants, reading left to right. Vision — the compact, sensorless motor concept and why it matters for next-generation drives. Infrastructure — the simulation framework and experimental test bench that didn't exist before this project. Validation — predicted versus measured results showing the models actually work. Capability — what the validated platform enables going forward.

An engineering schematic needs to be precise — every force arrow must have the right direction and point of application. A research slide needs to be *sequential*. A viewer scanning left to right should build understanding progressively, each quadrant adding context that makes the next one legible. Precision matters less than narrative flow. The FBD answers "what forces act on this assembly?" The thesis slide answers "why should you care about this work?"

Both are visual communication. But the FBD serves a reader who will study it. The thesis slide serves an audience that will glance at it while listening to someone talk. Same medium, opposite design constraints.

## The Moment That Made It Concrete

I'd finished the push-out calculation and had the numbers: 847 pounds lateral capacity, 1.3 safety factor, anchor bolt spacing of 6 inches. Clear results. Then I tried to put them in the report next to the existing text, and they just sat there. Three values in a sentence. Technically complete, functionally useless for a reader who hadn't stared at the same assembly for two hours.

The FBD changed that. Once the reader could see the lateral force applied at the anchor point, the opposing friction at the base, and the moment arm between them, the 1.3 safety factor stopped being an abstract number and became a visible relationship between two arrows. The drawing didn't add information. It added *orientation* — a way into the numbers that didn't require already knowing what they meant.

That's the gap I kept running into all day. Not between wrong and right, but between having results and making them readable. The OSHA terminology was about matching the audience's regulatory vocabulary. The SVG schematics were about giving spatial intuition for a force balance. The thesis slide was about compressing a year into a visual narrative. Each required understanding who would look at the output and what they'd need to see first.

The analysis was done before any of these sessions started. The translation took the rest of the day.