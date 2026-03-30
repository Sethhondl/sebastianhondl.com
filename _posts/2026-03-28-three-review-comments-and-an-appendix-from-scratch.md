---
layout: post
title: "Three Review Comments and an Appendix from Scratch"
date: 2026-03-28
categories: [development, ai]
tags: [claude-code, python, automation, testing, api]
read_time: 3
word_count: 760
---

Every day for the past several weeks, a four-pass editorial pipeline has been generating blog posts from my Claude Code session transcripts. It drafts, reviews, revises, and polishes. In theory, each pass sharpens the writing. In practice, the pipeline spent most of those weeks writing posts about itself — about the fact that it exists, about how interesting it is that an AI can write about AI writing, about the meta-recursive nature of automated blogging. The posts were structurally sound and completely empty.

Then on Tuesday, the pipeline produced something different. Not because I changed the code. Because the input changed.

---

The session that fed Tuesday's post was a MATLAB refactoring day. I was working through a Simulink model for a linear cart system — a 4.3 kg cart on a rail driven by a DC motor, the kind of undergraduate controls lab setup that accumulates cruft across semesters of student modifications. I ran `grep -r 'cart_mass' src/` looking for hardcoded physical parameters scattered across simulation files, and that single command reframed the entire day. Instead of tweaking one model, I was tracing a parameter through six files, finding three places where `cart.mass` was set to zero as a debugging shortcut someone had forgotten to undo.

That transcript — with its specific files, specific bugs, and a grep that changed the day's scope — went into the pipeline. For the first time, the four passes did their actual jobs.

---

The review pass came back with eleven structural critiques. Not the usual "consider tightening the prose" filler. Three of them showed the pipeline doing real editorial work:

**"The `cart.mass = 0` trick is the best moment in the post — don't bury it in the third paragraph."** The draft had mentioned the zeroed-out mass as one item in a list. The review pass recognized it as the narrative pivot: someone's temporary hack becoming an invisible load-bearing assumption across the entire simulation. It told the revision pass to move it up front.

**"Which February abstraction are you referring to? Name it."** The draft had a line about "revisiting an abstraction from earlier this semester." The review pass caught the vagueness and demanded the specific function name and file. This is the kind of edit a human reviewer makes when they can tell the writer is hand-waving — and the pipeline made it unprompted.

**"The closing paragraph restates the opening. Cut it or replace it with something the reader doesn't already know."** The revision pass replaced the summary ending with a forward-looking observation about which other lab scripts probably had the same buried-zero problem.

The revision pass implemented all eleven points. The polish pass cleaned up transitions and — critically — protected that new closing line instead of rewriting it into something blander, which is what it had been doing in previous weeks when it had nothing real to work with.

---

For contrast, here is what the failure mode looked like. When the pipeline ran on a day where the only session was the pipeline debugging itself, the draft pass would produce something like: "Today's work focused on improving the blog generation pipeline. The four-pass system continues to evolve." The review pass would critique the lack of specificity but had nowhere to point for concrete details, because there were none. The revision pass would try to add depth by making the meta-commentary more elaborate. The polish pass would smooth this into something grammatically clean and thematically hollow. Four passes producing four layers of polish on nothing.

---

There was one other thread in Tuesday's session: renaming six functions from `snake_case` to `camelCase` in a RoboDK robotics lab script for a FANUC CRX-30iA pick-and-place program. Fifteen minutes of work. The pipeline handled it in a single sentence, and the review pass correctly identified it as minor connective tissue — not worth featuring, but worth mentioning for completeness. Even that small editorial judgment only works when the pipeline has enough material to establish a hierarchy. When every detail is equally thin, nothing gets subordinated because nothing stands above anything else.

---

For weeks I kept adjusting the pipeline — tuning prompts, reordering passes, adding constraints about self-reference. None of it mattered because the problem was upstream. A revision engine needs raw material with enough texture to grip. A grep that reframes a day. A zeroed-out parameter that tells a story about institutional debugging habits. A specific file in a specific project with a specific bug.

The pipeline didn't get smarter. It got fed.